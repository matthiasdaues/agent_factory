"""Regression tests for FAGAN-0047 (cli.py exit codes).

FAGAN-0047: halted runs must exit non-zero (exit code 2) instead of 0, and
argparse usage errors must map to exit code 3 (2 is reserved for HALTED).

These tests drive the private CLI handlers directly with fake ports (fake
phase_runner / approval_service / run_store), which lets us assert on exit
codes for terminal-state combinations without needing the full
adapter/model-matrix/agent-registry machinery that `main()` normally builds.

Note: `run-all`, the `--yes` auto-approve flow, and `ChainRunner` were removed
when automated/unattended chain execution was deferred (NG6). Resume now drives
only the current phase through `PhaseRunner`; the Operator advances to the next
phase manually after approval (UC-03).
"""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest

from orchestrator import cli
from orchestrator.entities import PhaseRecord, PhaseStatus, Run, RunMode


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakePhaseRunner:
    """Mimics PhaseRunner.run_phase: sets the phase status (and, if given,
    the run mode) that a real PhaseRunner would have set for a given
    terminal outcome (HALTED / AWAITING_APPROVAL)."""

    def __init__(self, status: PhaseStatus, run_mode: RunMode | None = None) -> None:
        self._status = status
        self._run_mode = run_mode

    def run_phase(self, run: Run, phase_record: PhaseRecord) -> PhaseRecord:
        phase_record.status = self._status
        if self._run_mode is not None:
            run.mode = self._run_mode
        return phase_record


class FakeApprovalService:
    def __init__(self, raise_error: Exception | None = None) -> None:
        self.approve_calls = 0
        self.reject_calls = 0
        self._raise_error = raise_error

    def approve(self) -> None:
        self.approve_calls += 1
        if self._raise_error is not None:
            raise self._raise_error

    def reject(self, note: str | None = None) -> None:
        self.reject_calls += 1


class FakeNoOpPhaseRunner:
    """Mimics PhaseRunner.run_phase's terminal early-return: when
    phase_record.status is already AWAITING_APPROVAL/HALTED/COMPLETE,
    run_phase() returns immediately without touching run.mode or saving.
    Reproduces FAGAN-0047 hole 1: re-invoking on an already-terminal phase."""

    def run_phase(self, run: Run, phase_record: PhaseRecord) -> PhaseRecord:
        return phase_record


class FakeRunStore:
    def __init__(self, run: Run | None = None) -> None:
        self.current = run

    def load(self) -> Run | None:
        return self.current

    def save(self, run: Run) -> None:
        self.current = run


def _make_runtime(
    *, phase_runner=None, approval_service=None, run_store=None
) -> cli._Runtime:
    return cli._Runtime(
        repo_root=Path("/nonexistent-repo-root"),
        orch_dir=Path("/nonexistent-repo-root/.orchestrator"),
        agents_dir=Path("/nonexistent-repo-root/agents"),
        run_store=run_store if run_store is not None else FakeRunStore(),
        run_lock=None,
        approval_service=approval_service
        if approval_service is not None
        else FakeApprovalService(),
        status_service=None,
        phase_runner=phase_runner,
        prompt_composer=None,
        adapter=None,
        agent_registry=None,
        logger=None,
    )


def _make_run(
    *,
    mode: RunMode,
    phase_status: PhaseStatus,
    phase: str = "requirements",
    chain: list[str] | None = None,
) -> Run:
    chain = chain or [phase]
    return Run(
        run_id="RUN-TEST0001",
        branch="orchestrator/run-test0001",
        chain=chain,
        current_phase=phase,
        iteration=0,
        mode=mode,
        phases=[
            PhaseRecord(
                name=phase,
                author="req-agent",
                reviewer="req-review-agent",
                status=phase_status,
            )
        ],
    )


@pytest.fixture(autouse=True)
def _no_git_branch_ops(monkeypatch):
    """_ensure_run_branch shells out to git against runtime.repo_root; the
    exit-code logic under test doesn't depend on it, so stub it out."""
    monkeypatch.setattr(cli, "_ensure_run_branch", lambda repo_root, branch: None)


# ---------------------------------------------------------------------------
# FAGAN-0047: run-phase
# ---------------------------------------------------------------------------


def test_run_phase_halted_returns_2() -> None:
    runtime = _make_runtime(
        phase_runner=FakePhaseRunner(PhaseStatus.HALTED, RunMode.HALTED),
    )
    run = _make_run(mode=RunMode.RUNNING, phase_status=PhaseStatus.PENDING)
    args = Namespace(phase="requirements")

    rc = cli._handle_run_phase(runtime, run, args)

    assert rc == 2


def test_run_phase_awaiting_approval_returns_0() -> None:
    runtime = _make_runtime(
        phase_runner=FakePhaseRunner(PhaseStatus.AWAITING_APPROVAL, RunMode.PAUSED),
    )
    run = _make_run(mode=RunMode.RUNNING, phase_status=PhaseStatus.PENDING)
    args = Namespace(phase="requirements")

    rc = cli._handle_run_phase(runtime, run, args)

    assert rc == 0


def test_run_phase_reinvoked_on_halted_phase_returns_2() -> None:
    """FAGAN-0047 hole 1: re-invoking `run-phase X` on a phase that's
    already HALTED must NOT report success. _handle_run_phase optimistically
    sets run.mode = RUNNING before calling run_phase(); the real PhaseRunner
    early-returns as a no-op for a terminal phase status. The exit code must
    come from the persisted (authoritative) store, not the clobbered value."""
    halted_run = _make_run(mode=RunMode.HALTED, phase_status=PhaseStatus.HALTED)
    runtime = _make_runtime(
        phase_runner=FakeNoOpPhaseRunner(),
        run_store=FakeRunStore(run=halted_run),
    )
    run = _make_run(mode=RunMode.HALTED, phase_status=PhaseStatus.HALTED)
    args = Namespace(phase="requirements")

    rc = cli._handle_run_phase(runtime, run, args)

    assert rc == 2


# ---------------------------------------------------------------------------
# FAGAN-0047: resume (drives the current phase via PhaseRunner; NG6)
# ---------------------------------------------------------------------------


def test_resume_halted_returns_2() -> None:
    runtime = _make_runtime(
        phase_runner=FakePhaseRunner(PhaseStatus.HALTED, RunMode.HALTED),
    )
    run = _make_run(mode=RunMode.RUNNING, phase_status=PhaseStatus.PENDING)
    args = Namespace()

    rc = cli._handle_resume(runtime, run, args)

    assert rc == 2


def test_resume_awaiting_approval_returns_0() -> None:
    runtime = _make_runtime(
        phase_runner=FakePhaseRunner(PhaseStatus.AWAITING_APPROVAL, RunMode.PAUSED),
    )
    run = _make_run(mode=RunMode.RUNNING, phase_status=PhaseStatus.PENDING)
    args = Namespace()

    rc = cli._handle_resume(runtime, run, args)

    assert rc == 0


def test_resume_noop_on_terminal_phase_reads_persisted_mode() -> None:
    """Resuming a phase already awaiting approval is a no-op in PhaseRunner;
    the exit code comes from the persisted store (paused -> 0)."""
    paused_run = _make_run(
        mode=RunMode.PAUSED, phase_status=PhaseStatus.AWAITING_APPROVAL
    )
    runtime = _make_runtime(
        phase_runner=FakeNoOpPhaseRunner(),
        run_store=FakeRunStore(run=paused_run),
    )
    run = _make_run(mode=RunMode.PAUSED, phase_status=PhaseStatus.AWAITING_APPROVAL)
    args = Namespace()

    rc = cli._handle_resume(runtime, run, args)

    assert rc == 0


# ---------------------------------------------------------------------------
# FAGAN-0047: argparse usage errors -> exit code 3
# ---------------------------------------------------------------------------


def test_unknown_subcommand_usage_error_returns_3() -> None:
    rc = cli.main(["not-a-real-command"])

    assert rc == 3


def test_run_all_is_no_longer_a_command_returns_3() -> None:
    """run-all was removed (deferred, NG6); it is now an unknown command."""
    rc = cli.main(["run-all"])

    assert rc == 3


def test_missing_required_positional_usage_error_returns_3() -> None:
    rc = cli.main(["run-phase"])

    assert rc == 3


def test_help_flag_returns_0() -> None:
    rc = cli.main(["--help"])

    assert rc == 0
