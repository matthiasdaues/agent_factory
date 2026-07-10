from __future__ import annotations

import pytest

from orchestrator.approval_service import ApprovalService
from orchestrator.entities import GateResult, PhaseRecord, PhaseStatus, Run, RunMode


def _gate(passed: bool = True) -> GateResult:
    return GateResult(
        passed=passed,
        errored=False,
        hook="pre-commit",
        error_count=0 if passed else 1,
        timed_out=False,
    )


def _run(
    *,
    phase_status: PhaseStatus = PhaseStatus.AWAITING_APPROVAL,
    mode: RunMode = RunMode.PAUSED,
    chain: list[str] | None = None,
) -> Run:
    chain = chain or ["requirements"]
    phase = PhaseRecord(
        name="requirements",
        author="author-agent",
        reviewer="reviewer-agent",
        status=phase_status,
        iteration=1,
        last_gate=_gate(),
        # FAGAN-0040: the reviewer persisted its review cycle here; approval
        # counts open findings on THIS cycle (not a re-derived iteration + 1).
        last_reviewed_cycle=2,
    )
    return Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=chain,
        current_phase="requirements",
        iteration=1,
        mode=mode,
        phases=[phase],
    )


class _RunStore:
    def __init__(self, run: Run):
        self.run = run
        self.saved = None
        self.load_calls = 0

    def load(self):
        self.load_calls += 1
        return self.run

    def save(self, run):
        self.saved = run


class _FindingsStore:
    def __init__(self, open_findings: int):
        self.open_findings = open_findings
        self.calls: list[tuple[str, int]] = []

    def open_count(self, phase: str, iteration: int) -> int:
        self.calls.append((phase, iteration))
        return self.open_findings


class _GuardFindingsStore:
    def open_count(self, phase: str, iteration: int) -> int:  # pragma: no cover
        raise AssertionError("open_count must not be called")


class _StalenessChecker:
    """Stub gate runner with a pre-configured staleness answer."""

    def __init__(
        self,
        stale: bool = False,
        gate_results: list[GateResult] | None = None,
    ):
        self._stale = stale
        self._gate_results = list(gate_results or [_gate()])
        self.checked_paths: list[str] | None = None
        self.verify_calls: list[tuple] = []

    def artifacts_changed(self, artifact_paths: list[str]) -> bool:
        self.checked_paths = artifact_paths
        return self._stale

    def verify(self, cwd, exit_code: int = 0) -> GateResult:
        self.verify_calls.append((cwd, exit_code))
        if not self._gate_results:  # pragma: no cover
            raise AssertionError("verify() was not expected")
        return self._gate_results.pop(0)

    def clean_tree(self, cwd) -> None:
        pass


class _AgentRegistry:
    """Stub: returns pre-configured outputs for a phase/role."""

    def __init__(self, outputs: list[str] | None = None):
        self._outputs = outputs or ["docs/spec/"]

    def resolve(self, phase: str, role: str):
        from orchestrator.ports import AgentInfo
        from pathlib import Path

        return AgentInfo(
            name=f"{phase}-agent",
            outputs=self._outputs,
            definition_path=Path(f"agents/{phase}-agent.md"),
        )


def test_approve_transitions_to_complete():
    run = _run()
    run_store = _RunStore(run)
    findings_store = _FindingsStore(open_findings=0)
    staleness = _StalenessChecker(stale=False)
    registry = _AgentRegistry()
    service = ApprovalService(run_store, findings_store, staleness, registry)

    service.approve()

    saved = run_store.saved
    assert saved is run
    assert saved.mode == RunMode.COMPLETE
    assert saved.phases[0].status == PhaseStatus.COMPLETE
    # FAGAN-0040: approval counts open findings on the PERSISTED review cycle
    # (phase.last_reviewed_cycle == 2), matching how PhaseRunner tags/counts them.
    assert findings_store.calls == [("requirements", 2)]


def test_reject_transitions_to_halted():
    run = _run()
    run_store = _RunStore(run)
    service = ApprovalService(
        run_store, _GuardFindingsStore(), _StalenessChecker(), _AgentRegistry()
    )

    service.reject()

    saved = run_store.saved
    assert saved is run
    assert saved.mode == RunMode.HALTED
    assert saved.phases[0].status == PhaseStatus.HALTED


def test_approve_on_non_awaiting_phase_raises_error():
    run = _run(phase_status=PhaseStatus.GATING)
    run_store = _RunStore(run)
    service = ApprovalService(
        run_store, _GuardFindingsStore(), _StalenessChecker(), _AgentRegistry()
    )

    with pytest.raises(ValueError, match="not awaiting approval"):
        service.approve()

    assert run_store.saved is None


def test_reject_on_non_awaiting_phase_raises_error():
    run = _run(phase_status=PhaseStatus.PENDING)
    run_store = _RunStore(run)
    service = ApprovalService(
        run_store, _GuardFindingsStore(), _StalenessChecker(), _AgentRegistry()
    )

    with pytest.raises(ValueError, match="not awaiting approval"):
        service.reject()

    assert run_store.saved is None


# --- RECON-0001: artifact staleness check / re-gate (VR-012, UC-04 ext 3a) ---


def test_approve_regates_when_artifacts_changed():
    """UC-04 ext 3a: artifacts changed since gate → re-gate, then approve."""
    run = _run()
    run_store = _RunStore(run)
    findings_store = _FindingsStore(open_findings=0)
    staleness = _StalenessChecker(stale=True, gate_results=[_gate(passed=True)])
    registry = _AgentRegistry(outputs=["docs/spec/"])
    service = ApprovalService(run_store, findings_store, staleness, registry)

    service.approve()

    saved = run_store.saved
    assert saved is run
    assert saved.mode == RunMode.COMPLETE
    assert saved.phases[0].status == PhaseStatus.COMPLETE
    assert len(staleness.verify_calls) == 1


def test_approve_raises_when_regate_fails_after_artifact_changes():
    failed_gate = _gate(passed=False)
    run = _run()
    run_store = _RunStore(run)
    findings_store = _FindingsStore(open_findings=0)
    staleness = _StalenessChecker(stale=True, gate_results=[failed_gate])
    registry = _AgentRegistry(outputs=["docs/spec/"])
    service = ApprovalService(run_store, findings_store, staleness, registry)

    with pytest.raises(
        ValueError, match="re-gate failed after artifact changes"
    ) as exc_info:
        service.approve()

    assert "hook=pre-commit" in str(exc_info.value)
    assert "errors=1" in str(exc_info.value)
    assert run_store.saved is run
    # FAGAN-0039: a failed stale re-gate moves the phase OUT of
    # AWAITING_APPROVAL into the resumable GATING sub-state (and drops the run
    # to HALTED) so resume/run-phase can re-drive the loop instead of wedging.
    assert run.phases[0].status == PhaseStatus.GATING
    assert run.mode == RunMode.HALTED
    assert run.phases[0].last_gate == failed_gate


def test_approve_checks_staleness_with_phase_outputs():
    """The staleness check should use the phase's declared artifact paths."""
    run = _run()
    run_store = _RunStore(run)
    findings_store = _FindingsStore(open_findings=0)
    staleness = _StalenessChecker(stale=False)
    registry = _AgentRegistry(outputs=["docs/spec/", "CONTEXT.md"])
    service = ApprovalService(run_store, findings_store, staleness, registry)

    service.approve()

    assert staleness.checked_paths == ["docs/spec/", "CONTEXT.md"]


def test_approve_advances_current_phase():
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements", "implementation"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[
            PhaseRecord(
                name="requirements",
                author="author-agent",
                reviewer="reviewer-agent",
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=1,
                last_gate=_gate(),
            ),
            PhaseRecord(
                name="implementation",
                author="author-agent",
                reviewer="reviewer-agent",
                status=PhaseStatus.PENDING,
                iteration=1,
            ),
        ],
    )
    run_store = _RunStore(run)
    findings_store = _FindingsStore(open_findings=0)
    staleness = _StalenessChecker(stale=False)
    service = ApprovalService(run_store, findings_store, staleness, _AgentRegistry())

    service.approve()

    saved = run_store.saved
    assert saved is run
    assert saved.mode == RunMode.PAUSED
    assert saved.current_phase == "implementation"
    assert saved.phases[0].status == PhaseStatus.COMPLETE


# --- RECON-0002: reject note (UC-04 ext 2a) ---


def test_reject_with_note_persists_note():
    """UC-04 ext 2a: reject with optional note."""
    run = _run()
    run_store = _RunStore(run)
    service = ApprovalService(
        run_store, _GuardFindingsStore(), _StalenessChecker(), _AgentRegistry()
    )

    service.reject(note="needs rework on use-case coverage")

    saved = run_store.saved
    assert saved.phases[0].rejection_note == "needs rework on use-case coverage"


def test_reject_without_note_leaves_none():
    run = _run()
    run_store = _RunStore(run)
    service = ApprovalService(
        run_store, _GuardFindingsStore(), _StalenessChecker(), _AgentRegistry()
    )

    service.reject()

    saved = run_store.saved
    assert saved.phases[0].rejection_note is None
