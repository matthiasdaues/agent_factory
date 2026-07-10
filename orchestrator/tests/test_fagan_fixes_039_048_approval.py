"""Regression tests for FAGAN-0039/0040/0041 in ApprovalService.

- FAGAN-0040: approve() counts open findings on the latest review CYCLE
  (iteration + 1), consistent with PhaseRunner — not the raw iteration.
- FAGAN-0041: advancing current_phase also syncs run.iteration to the phase
  advanced to.
- FAGAN-0039: a FAILED stale re-gate moves the phase out of AWAITING_APPROVAL
  into a resumable execution state (GATING) with run.mode HALTED, so the run
  does not wedge and resume/run-phase can re-drive the loop.
"""

from __future__ import annotations

import pytest

from orchestrator.approval_service import ApprovalService
from orchestrator.entities import GateResult, PhaseRecord, PhaseStatus, Run, RunMode


# --- fakes (mirroring tests/test_approval_service.py) ------------------------


def _gate(passed: bool = True, hook: str = "pre-commit") -> GateResult:
    return GateResult(
        passed=passed,
        errored=False,
        hook=hook,
        error_count=0 if passed else 1,
        timed_out=False,
    )


class _RunStore:
    def __init__(self, run: Run):
        self.run = run
        self.saved = None

    def load(self):
        return self.run

    def save(self, run):
        self.saved = run


class _FindingsStore:
    """Returns open findings only for the cycle keys configured in *by_cycle*."""

    def __init__(self, by_cycle: dict[tuple[str, int], int] | None = None):
        self._by_cycle = by_cycle or {}
        self.calls: list[tuple[str, int]] = []

    def open_count(self, phase: str, cycle: int) -> int:
        self.calls.append((phase, cycle))
        return self._by_cycle.get((phase, cycle), 0)


class _StalenessChecker:
    def __init__(
        self, stale: bool = False, gate_results: list[GateResult] | None = None
    ):
        self._stale = stale
        self._gate_results = list(gate_results or [_gate()])
        self.verify_calls: list[tuple] = []

    def artifacts_changed(self, artifact_paths: list[str]) -> bool:
        return self._stale

    def verify(self, cwd, exit_code: int = 0) -> GateResult:
        self.verify_calls.append((cwd, exit_code))
        return self._gate_results.pop(0)

    def clean_tree(self, cwd) -> None:
        pass


class _AgentRegistry:
    def __init__(self, outputs: list[str] | None = None):
        self._outputs = outputs or ["docs/spec/"]

    def resolve(self, phase: str, role: str):
        from pathlib import Path

        from orchestrator.ports import AgentInfo

        return AgentInfo(
            name=f"{phase}-agent",
            outputs=self._outputs,
            definition_path=Path(f"agents/{phase}-agent.md"),
        )


def _phase(
    name: str,
    status: PhaseStatus,
    iteration: int,
    last_gate=None,
    last_reviewed_cycle: int | None = None,
) -> PhaseRecord:
    return PhaseRecord(
        name=name,
        author="author-agent",
        reviewer="reviewer-agent",
        status=status,
        iteration=iteration,
        last_gate=last_gate,
        last_reviewed_cycle=last_reviewed_cycle,
    )


# --- FAGAN-0040 --------------------------------------------------------------


def test_approve_counts_findings_on_persisted_review_cycle():
    """The open-findings check must query phase.last_reviewed_cycle, not a
    re-derived iteration + 1."""
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=3,
        mode=RunMode.PAUSED,
        phases=[
            _phase(
                "requirements",
                PhaseStatus.AWAITING_APPROVAL,
                3,
                _gate(),
                last_reviewed_cycle=4,
            )
        ],
    )
    findings = _FindingsStore()
    service = ApprovalService(
        _RunStore(run), findings, _StalenessChecker(), _AgentRegistry()
    )

    service.approve()

    # The persisted review cycle (4) is queried — not iteration (3), not any
    # re-derived value.
    assert findings.calls == [("requirements", 4)]


def test_approve_counts_persisted_cycle_even_when_it_differs_from_iteration_plus_one():
    """last_reviewed_cycle is authoritative even if it no longer equals
    iteration + 1 (the empty-commit pause path leaves them out of sync)."""
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=3,
        mode=RunMode.PAUSED,
        # iteration 3 → the old code would query cycle 4; the persisted cycle is 2.
        phases=[
            _phase(
                "requirements",
                PhaseStatus.AWAITING_APPROVAL,
                3,
                _gate(),
                last_reviewed_cycle=2,
            )
        ],
    )
    findings = _FindingsStore()
    service = ApprovalService(
        _RunStore(run), findings, _StalenessChecker(), _AgentRegistry()
    )

    service.approve()

    assert findings.calls == [("requirements", 2)]


def test_approve_blocked_by_open_findings_on_persisted_cycle():
    """Open findings recorded under the persisted review cycle must block."""
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=2,
        mode=RunMode.PAUSED,
        phases=[
            _phase(
                "requirements",
                PhaseStatus.AWAITING_APPROVAL,
                2,
                _gate(),
                last_reviewed_cycle=3,
            )
        ],
    )
    # Open finding lives on the persisted cycle 3.
    findings = _FindingsStore(by_cycle={("requirements", 3): 1})
    run_store = _RunStore(run)
    service = ApprovalService(
        run_store, findings, _StalenessChecker(), _AgentRegistry()
    )

    with pytest.raises(ValueError, match="still has open findings"):
        service.approve()

    assert findings.calls == [("requirements", 3)]
    assert run_store.saved is None


def test_approve_empty_commit_pause_blocks_on_stale_open_findings():
    """FAGAN-0040 regression (the exact re-fix bug): a prior pass tags 2 findings
    at cycle 1 and loops (iteration → 1); the next pass produces an empty commit
    and re-pauses at AWAITING_APPROVAL WITHOUT ingesting or advancing iteration.
    last_reviewed_cycle is still 1, and the 2 findings are still open at cycle 1.
    Approval MUST block. The buggy iteration+1 query (cycle 2) sees 0 and wrongly
    approves."""
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[
            _phase(
                "requirements",
                PhaseStatus.AWAITING_APPROVAL,
                iteration=1,
                # empty-commit gate → approval's FAGAN-0038 carve-out applies,
                # so the open-findings check is still reached.
                last_gate=_gate(passed=False, hook="empty-commit"),
                last_reviewed_cycle=1,
            )
        ],
    )
    findings = _FindingsStore(by_cycle={("requirements", 1): 2})
    run_store = _RunStore(run)
    service = ApprovalService(
        run_store, findings, _StalenessChecker(), _AgentRegistry()
    )

    with pytest.raises(ValueError, match="still has open findings"):
        service.approve()

    # Queried the persisted last-reviewed cycle (1), where the open findings live.
    assert findings.calls == [("requirements", 1)]
    assert run_store.saved is None


# --- FAGAN-0041 --------------------------------------------------------------


def test_advancing_current_phase_syncs_run_iteration():
    """After advancing to the next phase, run.iteration mirrors that phase."""
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements", "implementation"],
        current_phase="requirements",
        iteration=5,
        mode=RunMode.PAUSED,
        phases=[
            _phase("requirements", PhaseStatus.AWAITING_APPROVAL, 5, _gate()),
            _phase("implementation", PhaseStatus.PENDING, 0),
        ],
    )
    run_store = _RunStore(run)
    service = ApprovalService(
        run_store, _FindingsStore(), _StalenessChecker(), _AgentRegistry()
    )

    service.approve()

    saved = run_store.saved
    assert saved.current_phase == "implementation"
    # FAGAN-0041: iteration checkpoint follows the advanced-to phase (0),
    # not the just-approved phase (5).
    assert saved.iteration == 0
    assert saved.phases[0].status == PhaseStatus.COMPLETE


# --- FAGAN-0039 --------------------------------------------------------------


def test_failed_regate_moves_phase_to_resumable_gating_not_wedged():
    """A failed stale re-gate must leave a resumable state, not AWAITING_APPROVAL."""
    failed = _gate(passed=False)
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[_phase("requirements", PhaseStatus.AWAITING_APPROVAL, 1, _gate())],
    )
    run_store = _RunStore(run)
    staleness = _StalenessChecker(stale=True, gate_results=[failed])
    service = ApprovalService(run_store, _FindingsStore(), staleness, _AgentRegistry())

    with pytest.raises(ValueError, match="re-gate failed after artifact changes"):
        service.approve()

    saved = run_store.saved
    assert saved is run
    # Out of AWAITING_APPROVAL (terminal) into GATING (a resume point the state
    # machine re-drives), and out of PAUSED into HALTED (recoverable, non-zero).
    assert saved.phases[0].status == PhaseStatus.GATING
    assert saved.mode == RunMode.HALTED
    assert saved.phases[0].last_gate == failed
    # current_phase stays on the failed phase so resume re-runs it.
    assert saved.current_phase == "requirements"


def test_successful_regate_still_approves():
    """A successful stale re-gate approves as before (regression guard)."""
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[_phase("requirements", PhaseStatus.AWAITING_APPROVAL, 1, _gate())],
    )
    run_store = _RunStore(run)
    staleness = _StalenessChecker(stale=True, gate_results=[_gate(passed=True)])
    service = ApprovalService(run_store, _FindingsStore(), staleness, _AgentRegistry())

    service.approve()

    saved = run_store.saved
    assert saved.mode == RunMode.COMPLETE
    assert saved.phases[0].status == PhaseStatus.COMPLETE
