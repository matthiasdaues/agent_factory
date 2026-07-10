"""Tests for FAGAN-0032 through FAGAN-0038 fixes."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from orchestrator.approval_service import ApprovalService
from orchestrator.entities import (
    GateResult,
    PhaseRecord,
    PhaseStatus,
    Run,
    RunMode,
)


# ── shared stubs ──


def _gate(
    passed: bool = True, hook: str = "pre-commit", output: str = ""
) -> GateResult:
    return GateResult(
        passed=passed,
        errored=False,
        hook=hook,
        error_count=0 if passed else 1,
        timed_out=False,
        output=output,
    )


class _RunStore:
    def __init__(self, run: Run | None = None):
        self.run = run
        self.saved: Run | None = None

    def load(self) -> Run | None:
        return self.run

    def save(self, run: Run) -> None:
        self.saved = run


class _FindingsStore:
    def __init__(self, open_findings: int = 0):
        self._open = open_findings

    def open_count(self, phase: str, iteration: int) -> int:
        return self._open


class _NoChangeStalenessChecker:
    def artifacts_changed(self, artifact_paths: list[str]) -> bool:
        return False

    def verify(self, cwd, exit_code: int = 0):
        return _gate()

    def clean_tree(self, cwd) -> None:
        pass


class _AgentRegistry:
    def resolve(self, phase: str, role: str):
        @dataclass
        class _Info:
            name: str = "stub-agent"
            outputs: list[str] = field(default_factory=lambda: ["docs/spec/"])
            skills: list[str] = field(default_factory=list)

        return _Info()


# ── FAGAN-0032: _ensure_run_branch ──


def test_ensure_run_branch_creates_branch(tmp_path: Path) -> None:
    """FAGAN-0032: _ensure_run_branch creates the branch if it doesn't exist."""
    from orchestrator.cli import _ensure_run_branch

    subprocess.run(
        ["git", "init", "-b", "main", str(tmp_path)], capture_output=True, check=True
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
        env={
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
            "HOME": str(tmp_path),
            "PATH": "/usr/bin:/bin",
        },
    )

    _ensure_run_branch(tmp_path, "agent/run-1")

    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "agent/run-1"


def test_ensure_run_branch_checks_out_existing(tmp_path: Path) -> None:
    """FAGAN-0032: _ensure_run_branch checks out an existing branch."""
    from orchestrator.cli import _ensure_run_branch

    env = {
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
        "HOME": str(tmp_path),
        "PATH": "/usr/bin:/bin",
    }
    subprocess.run(
        ["git", "init", "-b", "main", str(tmp_path)], capture_output=True, check=True
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
        env=env,
    )
    subprocess.run(
        ["git", "checkout", "-b", "agent/run-1"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )

    _ensure_run_branch(tmp_path, "agent/run-1")

    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "agent/run-1"


# ── FAGAN-0033: clean index in gate_runner ──


def test_gate_result_output_field() -> None:
    """FAGAN-0034: GateResult carries pre-commit output."""
    gr = GateResult(
        passed=False,
        errored=False,
        hook="spec-lint",
        error_count=2,
        timed_out=False,
        output="lint errors here",
    )
    assert gr.output == "lint errors here"


def test_gate_result_output_default_empty() -> None:
    """GateResult.output defaults to empty string."""
    gr = GateResult(
        passed=True, errored=False, hook="pre-commit", error_count=0, timed_out=False
    )
    assert gr.output == ""


# ── FAGAN-0034: gate output is not persisted ──


def test_serialize_gate_strips_output() -> None:
    """FAGAN-0034: _serialize_gate strips the transient 'output' field."""
    from orchestrator.adapters.run_state_store import JsonRunStateStore

    store = JsonRunStateStore.__new__(JsonRunStateStore)
    gate = _gate(output="should be stripped")
    serialized = store._serialize_gate(gate)
    assert "output" not in serialized


# ── FAGAN-0034: ingest_gate_output on DefaultFindingIngestor ──


def test_ingest_gate_output_empty_string(tmp_path: Path) -> None:
    """ingest_gate_output with empty output returns 0."""
    from orchestrator.adapters.finding_ingest import DefaultFindingIngestor

    class _Store:
        def __init__(self):
            self.ingested: list = []
            self._next = 1

        def ingest(self, findings):
            self.ingested.extend(findings)

        def next_id(self):
            fid = f"FND-{self._next:04d}"
            self._next += 1
            return fid

    store = _Store()
    ingestor = DefaultFindingIngestor(store, tmp_path / "findings")
    count = ingestor.ingest_gate_output("", "requirements", 1)
    assert count == 0


# ── FAGAN-0035: approve pauses instead of running ──


def test_approve_sets_paused_not_running() -> None:
    """FAGAN-0035: approval pauses the run so resume is needed."""
    run = Run(
        run_id="r1",
        branch="agent/r1",
        chain=["requirements", "implementation"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[
            PhaseRecord(
                name="requirements",
                author="a",
                reviewer="r",
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=1,
                last_gate=_gate(),
            ),
            PhaseRecord(
                name="implementation",
                author="a",
                reviewer="r",
                status=PhaseStatus.PENDING,
                iteration=1,
            ),
        ],
    )
    store = _RunStore(run)
    svc = ApprovalService(
        store, _FindingsStore(), _NoChangeStalenessChecker(), _AgentRegistry()
    )

    svc.approve()

    assert store.saved is not None
    assert store.saved.mode == RunMode.PAUSED
    assert store.saved.current_phase == "implementation"


def test_approve_last_phase_completes() -> None:
    """FAGAN-0035: approval of the last phase sets COMPLETE, not PAUSED."""
    run = Run(
        run_id="r1",
        branch="agent/r1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[
            PhaseRecord(
                name="requirements",
                author="a",
                reviewer="r",
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=1,
                last_gate=_gate(),
            ),
        ],
    )
    store = _RunStore(run)
    svc = ApprovalService(
        store, _FindingsStore(), _NoChangeStalenessChecker(), _AgentRegistry()
    )

    svc.approve()

    assert store.saved is not None
    assert store.saved.mode == RunMode.COMPLETE


# ── FAGAN-0036: interactive stderr capture ──


def test_interactive_captures_auth_error_from_stderr(monkeypatch, tmp_path) -> None:
    """FAGAN-0036: interactive mode classifies auth errors from stderr."""
    from orchestrator.adapters.copilot import CopilotAdapter

    def fake_run(cmd, **kw):
        @dataclass
        class _Result:
            returncode: int = 1
            stdout: str = ""
            stderr: str = "error: not logged in"

        return _Result()

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter(interactive=True).invoke("x", tmp_path, 30)
    assert r.auth_error is True
    assert r.config_error is False


def test_interactive_captures_config_error_from_stderr(monkeypatch, tmp_path) -> None:
    """FAGAN-0036: interactive mode classifies config errors from stderr."""
    from orchestrator.adapters.copilot import CopilotAdapter

    def fake_run(cmd, **kw):
        @dataclass
        class _Result:
            returncode: int = 1
            stdout: str = ""
            stderr: str = "error: invalid model specified"

        return _Result()

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter(interactive=True).invoke("x", tmp_path, 30)
    assert r.auth_error is False
    assert r.config_error is True


# ── FAGAN-0037: --story option parsing ──


def test_run_phase_story_option_parsed() -> None:
    """FAGAN-0037: run-phase accepts --story ST-NNNN."""
    from orchestrator.cli import build_parser

    args = build_parser().parse_args(
        ["run-phase", "requirements", "--story", "ST-0001"]
    )
    assert args.story == "ST-0001"


def test_run_phase_story_default_none() -> None:
    """FAGAN-0037: --story defaults to None."""
    from orchestrator.cli import build_parser

    args = build_parser().parse_args(["run-phase", "requirements"])
    assert args.story is None


# ── FAGAN-0038: empty-commit approval ──


def test_approve_empty_commit_skips_gate_check() -> None:
    """FAGAN-0038: approve() allows empty-commit phases."""
    run = Run(
        run_id="r1",
        branch="agent/r1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[
            PhaseRecord(
                name="requirements",
                author="a",
                reviewer="r",
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=1,
                last_gate=_gate(passed=False, hook="empty-commit"),
            ),
        ],
    )
    store = _RunStore(run)
    svc = ApprovalService(
        store, _FindingsStore(), _NoChangeStalenessChecker(), _AgentRegistry()
    )

    # Should NOT raise — empty-commit is acceptable
    svc.approve()

    assert store.saved is not None
    assert store.saved.mode == RunMode.COMPLETE
    assert store.saved.phases[0].status == PhaseStatus.COMPLETE


def test_approve_non_empty_commit_fails_without_gate() -> None:
    """FAGAN-0038: approve() still rejects non-empty-commit without passing gate."""
    run = Run(
        run_id="r1",
        branch="agent/r1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[
            PhaseRecord(
                name="requirements",
                author="a",
                reviewer="r",
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=1,
                last_gate=_gate(passed=False, hook="pre-commit"),
            ),
        ],
    )
    store = _RunStore(run)
    svc = ApprovalService(
        store, _FindingsStore(), _NoChangeStalenessChecker(), _AgentRegistry()
    )

    with pytest.raises(ValueError, match="gate has not passed"):
        svc.approve()
