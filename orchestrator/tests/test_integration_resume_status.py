from __future__ import annotations

from pathlib import Path

from orchestrator.adapters.findings_store import FilesystemFindingsStore
from orchestrator.adapters.run_state_store import JsonRunStateStore
from orchestrator.approval_service import ApprovalService
from orchestrator.entities import (
    Finding,
    FindingSource,
    FindingStatus,
    GateResult,
    PhaseRecord,
    PhaseStatus,
    Run,
    RunMode,
    Severity,
)
from orchestrator.status_service import StatusService


def _run_store(tmp_path: Path) -> JsonRunStateStore:
    return JsonRunStateStore(tmp_path / ".orchestrator")


def _findings_store(tmp_path: Path) -> FilesystemFindingsStore:
    return FilesystemFindingsStore(tmp_path / "findings")


class _NoChangeStalenessChecker:
    """Integration stub: artifacts never changed."""

    def artifacts_changed(self, artifact_paths: list[str]) -> bool:
        return False


class _IntegrationAgentRegistry:
    """Integration stub: returns dummy agent info for any phase/role."""

    def resolve(self, phase: str, role: str):
        from orchestrator.ports import AgentInfo

        return AgentInfo(
            name=f"{phase}-agent",
            outputs=["docs/spec/"],
            definition_path=Path(f"agents/{phase}-agent.md"),
        )


def _gate(
    *,
    passed: bool = True,
    errored: bool = False,
    hook: str = "pre-commit",
    error_count: int = 0,
    timed_out: bool = False,
) -> GateResult:
    return GateResult(
        passed=passed,
        errored=errored,
        hook=hook,
        error_count=error_count,
        timed_out=timed_out,
    )


def _phase(
    name: str,
    *,
    status: PhaseStatus,
    iteration: int = 1,
    last_gate: GateResult | None = None,
    last_reviewed_cycle: int | None = None,
) -> PhaseRecord:
    return PhaseRecord(
        name=name,
        author=f"{name}-author",
        reviewer=None,
        status=status,
        iteration=iteration,
        last_gate=last_gate,
        last_reviewed_cycle=last_reviewed_cycle,
    )


def _finding(
    finding_id: str,
    *,
    phase: str,
    iteration: int,
    status: FindingStatus = FindingStatus.OPEN,
) -> Finding:
    return Finding(
        id=finding_id,
        phase=phase,
        iteration=iteration,
        source=FindingSource.SPEC_LINT,
        code="SPEC-001",
        severity=Severity.ERROR,
        artifact="docs/spec.md",
        message="Needs attention",
        status=status,
        created_by="spec-lint",
        resolved_by=None,
    )


class _StubPhaseRunner:
    def __init__(self, statuses: dict[str, PhaseStatus]) -> None:
        self._statuses = statuses
        self.calls: list[str] = []

    def run_phase(self, run: Run, phase_record: PhaseRecord) -> PhaseRecord:
        self.calls.append(phase_record.name)
        phase_record.status = self._statuses[phase_record.name]
        return phase_record


def test_status_on_no_run_reports_idle(tmp_path: Path) -> None:
    service = StatusService(_run_store(tmp_path), _findings_store(tmp_path))

    status = service.get_status()

    assert status.mode is None
    assert status.current_phase is None
    assert status.iteration is None
    assert status.open_findings == 0
    assert status.last_gate is None


def test_status_during_paused_run(tmp_path: Path) -> None:
    run_store = _run_store(tmp_path)
    findings_store = _findings_store(tmp_path)
    gate = _gate(passed=True, hook="spec-lint")
    run = Run(
        run_id="RUN-PAUSED",
        branch="orchestrator/run-paused",
        chain=["requirements"],
        current_phase="requirements",
        iteration=2,
        mode=RunMode.PAUSED,
        phases=[
            _phase(
                "requirements",
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=2,
                last_gate=gate,
                # FAGAN-0040: status now counts findings on the persisted review
                # cycle. The reviewer tagged this cycle's findings at cycle 2.
                last_reviewed_cycle=2,
            )
        ],
    )
    run_store.save(run)
    findings_store.ingest(
        [
            _finding("FND-0001", phase="requirements", iteration=2),
            _finding("FND-0002", phase="requirements", iteration=2),
            _finding(
                "FND-0003",
                phase="requirements",
                iteration=2,
                status=FindingStatus.RESOLVED,
            ),
            _finding("FND-0004", phase="planning", iteration=2),
        ]
    )

    status = StatusService(run_store, findings_store).get_status()

    assert status.mode == "paused"
    assert status.current_phase == "requirements"
    assert status.iteration == 2
    assert status.open_findings == 2
    assert status.last_gate == gate


def test_approve_advances_current_phase_and_pauses(tmp_path: Path) -> None:
    run_store = _run_store(tmp_path)
    findings_store = _findings_store(tmp_path)
    run = Run(
        run_id="RUN-RESUME",
        branch="orchestrator/run-resume",
        chain=["requirements", "implementation"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[
            _phase(
                "requirements",
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=1,
                last_gate=_gate(passed=True),
            ),
            _phase("implementation", status=PhaseStatus.PENDING, iteration=1),
        ],
    )
    run_store.save(run)

    ApprovalService(
        run_store,
        findings_store,
        _NoChangeStalenessChecker(),
        _IntegrationAgentRegistry(),
    ).approve()

    approved_run = run_store.load()
    assert approved_run is not None
    # With run-all deferred (NG6), approve completes the phase, advances
    # current_phase, and pauses; the Operator drives the next phase manually.
    assert approved_run.mode == RunMode.PAUSED
    assert approved_run.phases[0].status == PhaseStatus.COMPLETE
    assert approved_run.current_phase == "implementation"
    assert approved_run.phases[1].status == PhaseStatus.PENDING


def test_reject_halts_chain(tmp_path: Path) -> None:
    run_store = _run_store(tmp_path)
    findings_store = _findings_store(tmp_path)
    run = Run(
        run_id="RUN-REJECT",
        branch="orchestrator/run-reject",
        chain=["requirements"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[
            _phase(
                "requirements",
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=1,
                last_gate=_gate(passed=True),
            )
        ],
    )
    run_store.save(run)

    ApprovalService(
        run_store,
        findings_store,
        _NoChangeStalenessChecker(),
        _IntegrationAgentRegistry(),
    ).reject()

    rejected_run = run_store.load()
    assert rejected_run is not None
    assert rejected_run.mode == RunMode.HALTED
    assert rejected_run.phases[0].status == PhaseStatus.HALTED
