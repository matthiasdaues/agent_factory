"""Integration test for the requirements phase — ST-0019.

Exercises the full requirements phase end-to-end using stub CLI adapters
but REAL filesystem stores and core components, to validate wiring.

Walking skeleton: author → gate → loop-back → clean → awaiting-approval.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional


from orchestrator.adapters.finding_ingest import DefaultFindingIngestor
from orchestrator.adapters.findings_store import FilesystemFindingsStore
from orchestrator.adapters.invocation_log import FileInvocationLog
from orchestrator.adapters.run_state_store import JsonRunStateStore
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
from orchestrator.loop_policy import LoopPolicy
from orchestrator.phase_runner import PhaseRunner
from orchestrator.ports import AgentInfo, InvocationResult


# ---------------------------------------------------------------------------
# Stubs — thin fakes for the components we do NOT exercise on disk
# ---------------------------------------------------------------------------


class StubCLIAdapter:
    """Always returns exit_code=0 (author succeeds).

    Simulates agent filing findings inside the subprocess (ADR-0013).
    """

    def __init__(
        self,
        findings_store: FilesystemFindingsStore,
        *,
        always_file_findings: bool = False,
    ) -> None:
        self.call_count = 0
        self._store = findings_store
        self._finding_seq = 0
        self._always_file = always_file_findings

    def _next_id(self) -> str:
        self._finding_seq += 1
        return f"FND-{self._finding_seq:04d}"

    def invoke(
        self, prompt: str, cwd: Path, timeout_s: int, model: str | None = None
    ) -> InvocationResult:
        self.call_count += 1

        # Simulate agent filing findings on first invocation (iteration 0)
        # or on every invocation if always_file_findings is True.
        # In the new model, the agent files findings before committing.
        if self.call_count == 1 or self._always_file:
            findings = [
                Finding(
                    id=self._next_id(),
                    phase="requirements",
                    iteration=self.call_count,  # cycle = iteration + 1, but we use call count
                    source=FindingSource.SPEC_LINT,
                    code="missing-section",
                    severity=Severity.ERROR,
                    artifact="requirements.md",
                    message=f"Required section absent (call {self.call_count})",
                    status=FindingStatus.OPEN,
                    created_by="spec-lint",
                ),
                Finding(
                    id=self._next_id(),
                    phase="requirements",
                    iteration=self.call_count,
                    source=FindingSource.SPEC_LINT,
                    code="bad-format",
                    severity=Severity.ERROR,
                    artifact="requirements.md",
                    message=f"Format violation (call {self.call_count})",
                    status=FindingStatus.OPEN,
                    created_by="spec-lint",
                ),
            ]
            self._store.ingest(findings)

        return InvocationResult(
            exit_code=0,
            stdout="ok",
            stderr="",
            timed_out=False,
            auth_error=False,
        )


class StubGateRunner:
    """First call fails (dirty tree); second call passes.

    When *always_fail* is True every call fails — used for cap-exhaustion.
    Simulates working-tree state checks (ADR-0013).
    """

    def __init__(
        self,
        findings_store: FilesystemFindingsStore,
        *,
        always_fail: bool = False,
    ) -> None:
        self._store = findings_store
        self._always_fail = always_fail
        self._call_count = 0

    def verify(self, cwd: Path, exit_code: int) -> GateResult:
        """Check working-tree state after agent exit (ADR-0013)."""
        self._call_count += 1

        if self._always_fail or self._call_count == 1:
            # Simulate dirty tree (working-tree gate failure)
            # NOTE: In the new model, findings are filed by the agent inside
            # its subprocess, not by the gate. The gate only checks tree state.
            # For testing purposes, we simulate the agent having filed findings
            # before the gate runs (this would happen in the real subprocess).
            return GateResult(
                passed=False,
                errored=False,
                hook="working-tree",
                error_count=2,
                timed_out=False,
            )

        return GateResult(
            passed=True,
            errored=False,
            hook="working-tree",
            error_count=0,
            timed_out=False,
        )

    def clean_tree(self, cwd: Path) -> None:
        pass


class StubAgentRegistry:
    """Returns a fixed AgentInfo for any phase/role."""

    def resolve(self, phase: str, role: str) -> AgentInfo:
        return AgentInfo(
            name=f"{phase}-{role}",
            outputs=["docs/requirements.md"],
            definition_path=Path("agents") / f"{phase}-{role}.md",
        )


class StubPromptComposer:
    """Returns a fixed prompt string."""

    def compose(
        self,
        agent_info: AgentInfo,
        context_paths: List[Path],
        invocation,
        findings: Optional[List[Finding]] = None,
    ) -> str:
        n = len(findings) if findings else 0
        return f"prompt for {agent_info.name} ({n} findings)"


class StubModelResolver:
    """Returns None — let the adapter use its default model."""

    def resolve_tier(
        self,
        tier: Optional[str],
        explicit_model: Optional[str] = None,
    ) -> Optional[str]:
        return None


class StubClock:
    """Returns incrementing timestamps (100 ms apart)."""

    def __init__(self) -> None:
        self._tick = 0

    def now_ms(self) -> int:
        self._tick += 1
        return self._tick * 100


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_run() -> Run:
    return Run(
        run_id="integration-001",
        branch="run/integration-001",
        chain=["requirements"],
        current_phase="requirements",
        iteration=0,
        mode=RunMode.RUNNING,
        phases=[
            PhaseRecord(
                name="requirements",
                author="requirements-author",
                reviewer=None,
                status=PhaseStatus.PENDING,
                iteration=0,
            ),
        ],
    )


def _build_phase_runner(
    tmp_path: Path,
    *,
    always_fail_gate: bool = False,
    loop_cap: int = 3,
) -> tuple[PhaseRunner, FilesystemFindingsStore, JsonRunStateStore, FileInvocationLog]:
    """Wire a PhaseRunner with real stores and stubs, return all components."""

    findings_dir = tmp_path / ".orchestrator" / "findings"
    orch_dir = tmp_path / ".orchestrator"
    log_dir = tmp_path / ".orchestrator" / "log"

    findings_store = FilesystemFindingsStore(findings_dir)
    run_store = JsonRunStateStore(orch_dir)
    logger = FileInvocationLog(log_dir)

    runner = PhaseRunner(
        adapter=StubCLIAdapter(findings_store, always_file_findings=always_fail_gate),
        gate_runner=StubGateRunner(findings_store, always_fail=always_fail_gate),
        findings_store=findings_store,
        finding_ingestor=DefaultFindingIngestor(
            findings_store, tmp_path / "docs" / "findings"
        ),
        run_store=run_store,
        agent_registry=StubAgentRegistry(),
        prompt_composer=StubPromptComposer(),
        logger=logger,
        loop_policy=LoopPolicy(cap=loop_cap),
        model_resolver=StubModelResolver(),
        clock=StubClock(),
        cwd=tmp_path,
    )
    return runner, findings_store, run_store, logger


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRequirementsPhaseLoopsThenApproves:
    """Gate fails on first iteration (2 errors), passes on second →
    phase reaches AWAITING_APPROVAL, run mode is PAUSED."""

    def test_final_status_is_awaiting_approval(self, tmp_path: Path) -> None:
        runner, findings_store, run_store, logger = _build_phase_runner(tmp_path)
        run = _make_run()
        phase = run.phases[0]

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.AWAITING_APPROVAL
        assert run.mode == RunMode.PAUSED

    def test_phase_iterated_once_before_passing(self, tmp_path: Path) -> None:
        runner, *_ = _build_phase_runner(tmp_path)
        run = _make_run()
        phase = run.phases[0]

        result = runner.run_phase(run, phase)

        assert result.iteration == 1

    def test_findings_persisted_on_disk(self, tmp_path: Path) -> None:
        runner, findings_store, *_ = _build_phase_runner(tmp_path)
        run = _make_run()
        phase = run.phases[0]

        runner.run_phase(run, phase)

        # The gate's first (failing) call wrote 2 findings with iteration=1.
        finding_files = list(findings_store.findings_dir.glob("FND-*.json"))
        assert len(finding_files) == 2

        # Findings are still OPEN (no reviewer path → no supersession).
        open_findings = findings_store.list_open("requirements", 1)
        assert len(open_findings) == 2

    def test_findings_can_be_superseded_after_phase(self, tmp_path: Path) -> None:
        """Verify the real FindingsStore supersedes correctly when asked."""
        runner, findings_store, *_ = _build_phase_runner(tmp_path)
        run = _make_run()
        phase = run.phases[0]

        runner.run_phase(run, phase)

        # Manually supersede iteration-1 findings (current_iteration=2).
        count = findings_store.supersede_prior("requirements", current_iteration=2)
        assert count == 2

        superseded = findings_store.list_open("requirements", 1)
        assert len(superseded) == 0  # all moved to superseded status

    def test_log_file_has_entries(self, tmp_path: Path) -> None:
        runner, _, _, inv_log = _build_phase_runner(tmp_path)
        run = _make_run()
        phase = run.phases[0]

        runner.run_phase(run, phase)

        log_lines = inv_log.log_file.read_text().strip().splitlines()
        assert len(log_lines) >= 2  # one per iteration (author invocation + gate)

        for line in log_lines:
            record = json.loads(line)
            assert "agent" in record
            assert "exit_code" in record
            assert record["role"] == "author"

    def test_run_state_persisted(self, tmp_path: Path) -> None:
        runner, _, run_store, _ = _build_phase_runner(tmp_path)
        run = _make_run()
        phase = run.phases[0]

        runner.run_phase(run, phase)

        loaded = run_store.load()
        assert loaded is not None
        assert loaded.run_id == "integration-001"
        assert loaded.mode == RunMode.PAUSED
        assert loaded.phases[0].status == PhaseStatus.AWAITING_APPROVAL


class TestRequirementsPhaseCapExhausted:
    """Gate always fails → after cap iterations the phase halts."""

    def test_halts_after_cap_iterations(self, tmp_path: Path) -> None:
        runner, findings_store, run_store, _ = _build_phase_runner(
            tmp_path,
            always_fail_gate=True,
            loop_cap=3,
        )
        run = _make_run()
        phase = run.phases[0]

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert run.mode == RunMode.HALTED

    def test_ran_exactly_cap_iterations(self, tmp_path: Path) -> None:
        runner, findings_store, *_ = _build_phase_runner(
            tmp_path,
            always_fail_gate=True,
            loop_cap=3,
        )
        run = _make_run()
        phase = run.phases[0]

        result = runner.run_phase(run, phase)

        # Iterations 0, 1, 2 attempted → final iteration counter is 2.
        assert result.iteration == 2

        # 3 gate calls × 2 findings each = 6 finding files on disk.
        finding_files = list(findings_store.findings_dir.glob("FND-*.json"))
        assert len(finding_files) == 6

    def test_log_entries_match_iterations(self, tmp_path: Path) -> None:
        runner, _, _, inv_log = _build_phase_runner(
            tmp_path,
            always_fail_gate=True,
            loop_cap=3,
        )
        run = _make_run()
        phase = run.phases[0]

        runner.run_phase(run, phase)

        log_lines = inv_log.log_file.read_text().strip().splitlines()
        assert len(log_lines) == 3  # one log entry per iteration


_FINDING_OPEN = """---
id: SPEC-0001
source: spec-review
severity: major
category: defect
artifact: docs/spec/prd.md#NFR-01
status: open
traces: [NFR-01]
---

# NFR-01 threshold is not verifiable

**What is wrong:** no measurable bound.
"""

_FINDING_RESOLVED = _FINDING_OPEN.replace("status: open", "status: resolved")


class _FilingReviewerAdapter:
    """Author is a no-op; the reviewer files a docs/findings file on its first
    pass (open) and resolves it on its second, mirroring the real agent's
    lifecycle. This is what the DefaultFindingIngestor reads."""

    def __init__(self, docs_findings_dir: Path) -> None:
        self._dir = docs_findings_dir
        self._n = 0

    def invoke(
        self, prompt: str, cwd: Path, timeout_s: int, model: str | None = None
    ) -> InvocationResult:
        self._n += 1
        if self._n == 2:  # reviewer, pass 0 — file an open finding
            self._dir.mkdir(parents=True, exist_ok=True)
            (self._dir / "SPEC-0001.md").write_text(_FINDING_OPEN, encoding="utf-8")
        elif self._n == 4:  # reviewer, pass 1 — verified fixed, mark resolved
            (self._dir / "SPEC-0001.md").write_text(_FINDING_RESOLVED, encoding="utf-8")
        return InvocationResult(
            exit_code=0,
            stdout="ok",
            stderr="",
            timed_out=False,
            auth_error=False,
        )


class _AlwaysPassGate:
    def verify(self, cwd: Path, exit_code: int) -> GateResult:
        return GateResult(passed=True, errored=False, hook="", error_count=0)

    def clean_tree(self, cwd: Path) -> None:
        pass


class _ReviewerAgentRegistry:
    def resolve(self, phase: str, role: str) -> AgentInfo:
        return AgentInfo(
            name=f"{phase}-{role}",
            outputs=["docs/spec/prd.md"],
            definition_path=Path("agents") / f"{phase}-{role}.md",
        )


class TestReviewerFindingsIngestedEndToEnd:
    """The reviewer path with a real FilesystemFindingsStore + DefaultFindingIngestor
    reading docs/findings/*.md (ADR-0012 ingestion source; ADR-0019 confirms the
    store is the loop's sole source of truth): the reviewer files an open
    finding, the loop reads it and loops back, then the finding is resolved and
    the review reaches approval. Works regardless of stdout capture (ST-0022)."""

    def _run(self, tmp_path: Path):
        docs_findings = tmp_path / "docs" / "findings"
        findings_store = FilesystemFindingsStore(
            tmp_path / ".orchestrator" / "findings"
        )
        run_store = JsonRunStateStore(tmp_path / ".orchestrator")
        logger = FileInvocationLog(tmp_path / ".orchestrator" / "log")

        runner = PhaseRunner(
            adapter=_FilingReviewerAdapter(docs_findings),
            gate_runner=_AlwaysPassGate(),
            findings_store=findings_store,
            finding_ingestor=DefaultFindingIngestor(findings_store, docs_findings),
            run_store=run_store,
            agent_registry=_ReviewerAgentRegistry(),
            prompt_composer=StubPromptComposer(),
            logger=logger,
            loop_policy=LoopPolicy(cap=3),
            model_resolver=StubModelResolver(),
            clock=StubClock(),
            cwd=tmp_path,
        )
        run = Run(
            run_id="rev-001",
            branch="run/rev-001",
            chain=["requirements"],
            current_phase="requirements",
            phases=[
                PhaseRecord(
                    name="requirements",
                    author="requirements-author",
                    reviewer="spec-review-agent",
                    status=PhaseStatus.PENDING,
                )
            ],
        )
        result = runner.run_phase(run, run.phases[0])
        return result, run, findings_store

    def test_loops_then_approves(self, tmp_path: Path) -> None:
        result, run, _ = self._run(tmp_path)
        assert result.status == PhaseStatus.AWAITING_APPROVAL
        assert run.mode == RunMode.PAUSED
        assert result.iteration == 1

    def test_reviewer_finding_persisted_with_mapped_severity(
        self, tmp_path: Path
    ) -> None:
        _, _, findings_store = self._run(tmp_path)
        # The open Major finding from the first review pass was read from
        # docs/findings, tagged cycle 1 (phase.iteration 0 + 1), severity → error.
        cycle1 = findings_store.list_open("requirements", 1)
        assert len(cycle1) == 1
        assert cycle1[0].code == "SPEC-0001"
        assert cycle1[0].severity == Severity.ERROR
        assert cycle1[0].source == FindingSource.SEMANTIC


class TestRunStatePersistedThroughout:
    """After the phase runs, loading run state from disk reproduces it."""

    def test_persisted_state_matches_in_memory(self, tmp_path: Path) -> None:
        runner, _, run_store, _ = _build_phase_runner(tmp_path)
        run = _make_run()
        phase = run.phases[0]

        runner.run_phase(run, phase)

        loaded = run_store.load()
        assert loaded is not None
        assert loaded.run_id == run.run_id
        assert loaded.branch == run.branch
        assert loaded.chain == run.chain
        assert loaded.current_phase == run.current_phase
        assert loaded.mode == run.mode
        assert loaded.iteration == run.iteration

    def test_persisted_phase_record_matches(self, tmp_path: Path) -> None:
        runner, _, run_store, _ = _build_phase_runner(tmp_path)
        run = _make_run()
        phase = run.phases[0]

        runner.run_phase(run, phase)

        loaded = run_store.load()
        assert loaded is not None
        lp = loaded.phases[0]
        assert lp.name == phase.name
        assert lp.author == phase.author
        assert lp.status == phase.status
        assert lp.iteration == phase.iteration

    def test_last_gate_result_persisted(self, tmp_path: Path) -> None:
        runner, _, run_store, _ = _build_phase_runner(tmp_path)
        run = _make_run()
        phase = run.phases[0]

        runner.run_phase(run, phase)

        loaded = run_store.load()
        assert loaded is not None
        gate = loaded.phases[0].last_gate
        assert gate is not None
        assert gate.passed is True
        assert gate.error_count == 0

    def test_halted_state_persisted(self, tmp_path: Path) -> None:
        runner, _, run_store, _ = _build_phase_runner(
            tmp_path,
            always_fail_gate=True,
            loop_cap=3,
        )
        run = _make_run()
        phase = run.phases[0]

        runner.run_phase(run, phase)

        loaded = run_store.load()
        assert loaded is not None
        assert loaded.mode == RunMode.HALTED
        assert loaded.phases[0].status == PhaseStatus.HALTED
