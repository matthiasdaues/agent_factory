"""WorkingTreeGate-era regressions for FAGAN-0043 and VR-025/026/027.

WorkingTreeGate.verify()'s four quadrants already live in test_gate_runner.py.
This module focuses on PhaseRunner integration and clean-tree recovery.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, Optional

from orchestrator.adapters.gate_runner import WorkingTreeGate
from orchestrator.entities import (
    GateResult,
    InvocationContext,
    PhaseRecord,
    PhaseStatus,
    Run,
    RunMode,
)
from orchestrator.loop_policy import LoopPolicy
from orchestrator.phase_runner import PhaseRunner
from orchestrator.ports import AgentInfo, InvocationResult


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=check,
    )


def _git_status(repo: Path) -> str:
    return _git(repo, "status", "--porcelain").stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "T")
    (tmp_path / "tracked.txt").write_text("base\n")
    _git(tmp_path, "add", "tracked.txt")
    _git(tmp_path, "commit", "-m", "init")
    return tmp_path


class ScriptedCLIAdapter:
    def __init__(
        self,
        results: list[InvocationResult],
        effects: Optional[list[Optional[Callable[[Path], None]]]] = None,
    ) -> None:
        self._results = list(results)
        self._effects = list(effects or [])
        self._idx = 0
        self.calls: list[tuple[str, Path, int, Optional[str]]] = []

    def invoke(
        self,
        prompt: str,
        cwd: Path,
        timeout_s: int,
        model: Optional[str] = None,
    ) -> InvocationResult:
        self.calls.append((prompt, cwd, timeout_s, model))
        effect = self._effects[self._idx] if self._idx < len(self._effects) else None
        if effect is not None:
            effect(cwd)
        result = self._results[self._idx]
        self._idx += 1
        return result


class StubFindingsStore:
    def __init__(self, open_counts: dict[tuple[str, int], int] | None = None) -> None:
        self._open_counts = open_counts or {}
        self.supersede_calls: list[tuple[str, int]] = []

    def ingest(self, findings) -> None:  # pragma: no cover - unused test double
        return None

    def supersede_prior(self, phase: str, current_iteration: int) -> int:
        self.supersede_calls.append((phase, current_iteration))
        return 0

    def open_count(self, phase: str, iteration: int) -> int:
        return self._open_counts.get((phase, iteration), 0)

    def list_open(self, phase: str, iteration: int) -> list:
        return []


class StubFindingIngestor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def ingest_open_findings(self, phase: str, iteration: int) -> int:
        self.calls.append((phase, iteration))
        return 0


class StubRunStateStore:
    def __init__(self) -> None:
        self.saves: list[Run] = []

    def load(self) -> Optional[Run]:
        return None

    def save(self, run: Run) -> None:
        self.saves.append(run)

    def exists(self) -> bool:
        return bool(self.saves)


class StubAgentRegistry:
    def resolve(self, phase: str, role: str) -> AgentInfo:
        return AgentInfo(
            name=f"{phase}-{role}",
            outputs=["tracked.txt"],
            definition_path=Path("."),
        )


class StubPromptComposer:
    def compose(
        self,
        agent_info: AgentInfo,
        context_paths: list[Path],
        invocation: InvocationContext,
        findings=None,
    ) -> str:
        return f"prompt for {agent_info.name}"


class StubLogger:
    def __init__(self) -> None:
        self.logged: list[tuple[str, Optional[GateResult]]] = []

    def log(self, record, gate: Optional[GateResult] = None) -> None:
        self.logged.append((record.agent, gate))


class StubClock:
    def __init__(self) -> None:
        self._now = 0

    def now_ms(self) -> int:
        current = self._now
        self._now += 50
        return current


class StubModelResolver:
    def resolve(
        self,
        phase: str,
        classification: Optional[str] = None,
        explicit_model: Optional[str] = None,
    ) -> str:
        return "gpt-4o"


class RecordingWorkingTreeGate(WorkingTreeGate):
    def __init__(self, repo_root: Path) -> None:
        super().__init__(repo_root)
        self.calls: list[tuple[Path, int]] = []

    def verify(self, cwd: Path, exit_code: int) -> GateResult:
        self.calls.append((cwd, exit_code))
        return super().verify(cwd, exit_code)


class FailIfVerifyCalledGate(WorkingTreeGate):
    def __init__(self, repo_root: Path) -> None:
        super().__init__(repo_root)
        self.calls = 0

    def verify(self, cwd: Path, exit_code: int) -> GateResult:
        self.calls += 1
        raise AssertionError("verify() should not run when resuming REVIEWING")


def _ok() -> InvocationResult:
    return InvocationResult(
        exit_code=0, stdout="ok", stderr="", timed_out=False, auth_error=False
    )


def _fail() -> InvocationResult:
    return InvocationResult(
        exit_code=1, stdout="", stderr="err", timed_out=False, auth_error=False
    )


def _run(phase_name: str = "design") -> Run:
    return Run(
        run_id="run-1", branch="run/run-1", chain=[phase_name], current_phase=phase_name
    )


def _phase(name: str = "design", reviewer: str | None = None) -> PhaseRecord:
    return PhaseRecord(name=name, author="author-agent", reviewer=reviewer)


def _build_runner(
    cwd: Path,
    *,
    adapter: ScriptedCLIAdapter,
    gate: WorkingTreeGate | None = None,
    findings: StubFindingsStore | None = None,
    ingestor: StubFindingIngestor | None = None,
    loop: LoopPolicy | None = None,
) -> PhaseRunner:
    return PhaseRunner(
        adapter=adapter,
        gate_runner=gate or WorkingTreeGate(cwd),
        findings_store=findings or StubFindingsStore(),
        finding_ingestor=ingestor or StubFindingIngestor(),
        run_store=StubRunStateStore(),
        agent_registry=StubAgentRegistry(),
        prompt_composer=StubPromptComposer(),
        logger=StubLogger(),
        loop_policy=loop or LoopPolicy(cap=2),
        model_resolver=StubModelResolver(),
        clock=StubClock(),
        cwd=cwd,
    )


def test_confabulation_halts_run(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    def leave_dirty_tree(cwd: Path) -> None:
        (cwd / "tracked.txt").write_text("changed\n")

    adapter = ScriptedCLIAdapter([_ok()], effects=[leave_dirty_tree])
    runner = _build_runner(repo, adapter=adapter)

    result = runner.run_phase(_run(), _phase())

    assert result.status == PhaseStatus.HALTED
    assert result.last_gate == GateResult(
        passed=False,
        errored=True,
        hook="confabulation",
        error_count=1,
        output="exit 0 but uncommitted changes: tracked.txt",
    )
    assert _git_status(repo) == "M tracked.txt"


def test_gate_failure_cleans_tree_before_retry(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    seen_statuses: list[str] = []

    def fail_with_dirty_tree(cwd: Path) -> None:
        (cwd / "tracked.txt").write_text("changed\n")
        (cwd / "scratch.txt").write_text("temp\n")

    def verify_tree_was_cleaned(cwd: Path) -> None:
        seen_statuses.append(_git_status(cwd))
        assert (cwd / "tracked.txt").read_text() == "base\n"
        assert not (cwd / "scratch.txt").exists()

    adapter = ScriptedCLIAdapter(
        [_fail(), _ok()],
        effects=[fail_with_dirty_tree, verify_tree_was_cleaned],
    )
    runner = _build_runner(repo, adapter=adapter, loop=LoopPolicy(cap=2))

    result = runner.run_phase(_run(), _phase())

    assert seen_statuses == [""]
    assert result.status == PhaseStatus.AWAITING_APPROVAL
    assert result.iteration == 1
    assert result.last_gate == GateResult(
        passed=True,
        errored=False,
        hook="working-tree",
        error_count=0,
    )
    assert _git_status(repo) == ""


def test_gate_pass_proceeds_to_reviewer(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    adapter = ScriptedCLIAdapter([_ok(), _ok()])
    findings = StubFindingsStore(open_counts={("design", 1): 0})
    ingestor = StubFindingIngestor()
    runner = _build_runner(
        repo,
        adapter=adapter,
        findings=findings,
        ingestor=ingestor,
    )

    result = runner.run_phase(_run(), _phase(reviewer="reviewer-agent"))

    assert result.status == PhaseStatus.AWAITING_APPROVAL
    assert result.last_gate == GateResult(
        passed=True,
        errored=False,
        hook="working-tree",
        error_count=0,
    )
    assert result.last_reviewed_cycle == 1
    assert len(adapter.calls) == 2
    assert ingestor.calls == [("design", 1)]


def test_resume_gating_is_idempotent(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    gate = RecordingWorkingTreeGate(repo)
    adapter = ScriptedCLIAdapter([])
    runner = _build_runner(repo, adapter=adapter, gate=gate)
    phase = _phase()
    phase.status = PhaseStatus.GATING

    first = gate.verify(repo, exit_code=0)
    result = runner.run_phase(_run(), phase)

    assert first == GateResult(
        passed=True,
        errored=False,
        hook="working-tree",
        error_count=0,
    )
    assert result.status == PhaseStatus.AWAITING_APPROVAL
    assert result.last_gate == first
    assert adapter.calls == []
    assert gate.calls == [(repo, 0), (repo, 0)]


def test_resume_reviewing_skips_reinvoke(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    adapter = ScriptedCLIAdapter([])
    findings = StubFindingsStore(open_counts={("design", 1): 2})
    ingestor = StubFindingIngestor()
    gate = FailIfVerifyCalledGate(repo)
    runner = _build_runner(
        repo,
        adapter=adapter,
        gate=gate,
        findings=findings,
        ingestor=ingestor,
        loop=LoopPolicy(cap=1),
    )
    phase = _phase(reviewer="reviewer-agent")
    phase.status = PhaseStatus.REVIEWING
    run = _run()

    result = runner.run_phase(run, phase)

    assert result.status == PhaseStatus.HALTED
    assert run.mode == RunMode.HALTED
    assert adapter.calls == []
    assert ingestor.calls == []
    assert findings.supersede_calls == [("design", 1)]
    assert gate.calls == 0


def test_clean_tree_leaves_git_status_empty(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "tracked.txt").write_text("changed\n")
    (repo / "scratch.txt").write_text("temp\n")

    runner = _build_runner(repo, adapter=ScriptedCLIAdapter([_ok()]))

    runner._clean_tree()

    assert _git_status(repo) == ""
    assert (repo / "tracked.txt").read_text() == "base\n"
    assert not (repo / "scratch.txt").exists()
