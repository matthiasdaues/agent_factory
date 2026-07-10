"""Tests for PhaseRunner — the author→gate→review state machine (ST-0005)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from orchestrator.entities import (
    AgentInvocation,
    AgentRole,
    Finding,
    FindingStatus,
    FindingSource,
    GateResult,
    InvocationContext,
    PhaseRecord,
    PhaseStatus,
    Run,
    RunMode,
    Severity,
)
from orchestrator.loop_policy import LoopPolicy
from orchestrator.model_resolver import ConfigError
from orchestrator.phase_runner import PhaseRunner
from orchestrator.ports import AgentInfo, InvocationResult


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------


class StubCLIAdapter:
    """Returns a sequence of InvocationResults, one per call."""

    def __init__(self, results: list[InvocationResult] | None = None) -> None:
        self._results = list(results or [])
        self._idx = 0
        self.calls: list[tuple[str, Path, int]] = []

    def invoke(
        self, prompt: str, cwd: Path, timeout_s: int, model: Optional[str] = None
    ) -> InvocationResult:
        self.calls.append((prompt, cwd, timeout_s, model))
        r = self._results[self._idx]
        self._idx += 1
        return r


class StubGateRunner:
    def __init__(self, results: list[GateResult] | None = None) -> None:
        self._results = list(results or [])
        self._idx = 0
        self.calls: list[tuple[Path, int]] = []
        self.clean_tree_calls: list[Path] = []

    def verify(self, cwd: Path, exit_code: int) -> GateResult:
        self.calls.append((cwd, exit_code))
        r = self._results[self._idx]
        self._idx += 1
        return r

    def clean_tree(self, cwd: Path) -> None:
        self.clean_tree_calls.append(cwd)


class StubFindingsStore:
    def __init__(
        self,
        open_counts: dict[tuple[str, int], int] | None = None,
        open_findings: dict[tuple[str, int], list[Finding]] | None = None,
    ) -> None:
        self._open_counts = open_counts or {}
        self._open_findings = open_findings or {}
        self.ingested: list[list[Finding]] = []
        self.supersede_calls: list[tuple[str, int]] = []

    def ingest(self, findings: list[Finding]) -> None:
        self.ingested.append(findings)

    def supersede_prior(self, phase: str, current_iteration: int) -> int:
        self.supersede_calls.append((phase, current_iteration))
        return 0

    def open_count(self, phase: str, iteration: int) -> int:
        return self._open_counts.get((phase, iteration), 0)

    def list_open(self, phase: str, iteration: int) -> list[Finding]:
        return self._open_findings.get((phase, iteration), [])


class StubFindingIngestor:
    """Records ingest_open_findings calls; a no-op on the (pre-seeded) store."""

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
        # Store a snapshot of mode and phases status
        self.saves.append(run)

    def exists(self) -> bool:
        return bool(self.saves)


class StubAgentRegistry:
    def __init__(self, agents: dict[tuple[str, str], AgentInfo] | None = None) -> None:
        self._agents = agents or {}

    def resolve(self, phase: str, role: str) -> AgentInfo:
        return self._agents.get(
            (phase, role),
            AgentInfo(
                name=f"{phase}-{role}", outputs=["out.txt"], definition_path=Path(".")
            ),
        )


class StubPromptComposer:
    def __init__(self) -> None:
        self.calls: list[
            tuple[AgentInfo, list[Path], InvocationContext, Optional[list[Finding]]]
        ] = []

    def compose(
        self,
        agent_info: AgentInfo,
        context_paths: list[Path],
        invocation: InvocationContext,
        findings: Optional[list[Finding]] = None,
    ) -> str:
        self.calls.append((agent_info, context_paths, invocation, findings))
        return f"prompt for {agent_info.name}"


class StubLogger:
    def __init__(self) -> None:
        self.logged: list[tuple[AgentInvocation, Optional[GateResult]]] = []

    def log(self, record: AgentInvocation, gate: Optional[GateResult] = None) -> None:
        self.logged.append((record, gate))


class StubClock:
    def __init__(self, times: list[int] | None = None) -> None:
        self._times = list(times or [0, 100])
        self._idx = 0

    def now_ms(self) -> int:
        t = self._times[self._idx % len(self._times)]
        self._idx += 1
        return t


class StubModelResolver:
    def __init__(
        self, model: Optional[str] = "gpt-4o", raise_config: bool = False
    ) -> None:
        self._model = model
        self._raise = raise_config

    def resolve(
        self,
        phase: str,
        classification: Optional[str] = None,
        explicit_model: Optional[str] = None,
    ) -> Optional[str]:
        if self._raise:
            raise ConfigError("bad model")
        return self._model


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok_result() -> InvocationResult:
    return InvocationResult(
        exit_code=0, stdout="ok", stderr="", timed_out=False, auth_error=False
    )


def _fail_result() -> InvocationResult:
    return InvocationResult(
        exit_code=1, stdout="", stderr="err", timed_out=False, auth_error=False
    )


def _auth_fail() -> InvocationResult:
    return InvocationResult(
        exit_code=1, stdout="", stderr="auth", timed_out=False, auth_error=True
    )


def _config_fail() -> InvocationResult:
    return InvocationResult(
        exit_code=1,
        stdout="",
        stderr="bad flag",
        timed_out=False,
        auth_error=False,
        config_error=True,
    )


def _gate_pass() -> GateResult:
    return GateResult(passed=True, errored=False, hook="", error_count=0)


def _gate_fail_findings() -> GateResult:
    return GateResult(passed=False, errored=False, hook="lint", error_count=3)


def _gate_error() -> GateResult:
    return GateResult(passed=False, errored=True, hook="", error_count=0)


def _gate_timeout() -> GateResult:
    return GateResult(
        passed=False, errored=False, hook="", error_count=0, timed_out=True
    )


def _gate_confabulation() -> GateResult:
    """Exit 0 but dirty tree (VR-025)."""
    return GateResult(passed=False, errored=False, hook="confabulation", error_count=1)


def _make_run(phase_name: str = "design") -> Run:
    return Run(
        run_id="run-1",
        branch="run/run-1",
        chain=[phase_name],
        current_phase=phase_name,
    )


def _make_phase(name: str = "design", reviewer: Optional[str] = None) -> PhaseRecord:
    return PhaseRecord(name=name, author="author-agent", reviewer=reviewer)


def _build_runner(
    adapter: StubCLIAdapter | None = None,
    gate: StubGateRunner | None = None,
    findings: StubFindingsStore | None = None,
    ingestor: StubFindingIngestor | None = None,
    run_store: StubRunStateStore | None = None,
    registry: StubAgentRegistry | None = None,
    composer: StubPromptComposer | None = None,
    logger: StubLogger | None = None,
    loop: LoopPolicy | None = None,
    model_resolver: StubModelResolver | None = None,
    clock: StubClock | None = None,
    interactive: bool = False,
    classification: str | None = None,
) -> PhaseRunner:
    return PhaseRunner(
        adapter=adapter or StubCLIAdapter([_ok_result()]),
        gate_runner=gate or StubGateRunner([_gate_pass()]),
        findings_store=findings or StubFindingsStore(),
        finding_ingestor=ingestor or StubFindingIngestor(),
        run_store=run_store or StubRunStateStore(),
        agent_registry=registry or StubAgentRegistry(),
        prompt_composer=composer or StubPromptComposer(),
        logger=logger or StubLogger(),
        loop_policy=loop or LoopPolicy(cap=3),
        model_resolver=model_resolver or StubModelResolver(),
        clock=clock or StubClock(),
        cwd=Path("/work"),
        interactive=interactive,
        classification=classification,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestHappyPath:
    """1. Author succeeds → gate passes → no reviewer → AwaitingApproval."""

    def test_author_gate_pass_no_reviewer(self) -> None:
        run = _make_run()
        phase = _make_phase()
        store = StubRunStateStore()

        runner = _build_runner(run_store=store)
        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.AWAITING_APPROVAL
        assert run.mode == RunMode.PAUSED
        assert result.iteration == 0


class TestHappyPathWithReviewer:
    """2. Gate passes → reviewer finds 0 issues → AwaitingApproval."""

    def test_reviewer_clean(self) -> None:
        adapter = StubCLIAdapter([_ok_result(), _ok_result()])  # author + reviewer
        # cycle = phase.iteration + 1, so the first review counts iteration 1
        findings = StubFindingsStore(open_counts={("design", 1): 0})

        runner = _build_runner(adapter=adapter, findings=findings)
        phase = _make_phase(reviewer="reviewer-agent")
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.AWAITING_APPROVAL
        assert run.mode == RunMode.PAUSED


class TestAuthFailure:
    """3. Auth failure → Halted (no iteration counted)."""

    def test_auth_error_halts_immediately(self) -> None:
        adapter = StubCLIAdapter([_auth_fail()])
        logger = StubLogger()

        runner = _build_runner(adapter=adapter, logger=logger)
        phase = _make_phase()
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert run.mode == RunMode.HALTED
        assert result.iteration == 0
        assert result.halted_from == PhaseStatus.AUTHORING
        assert len(logger.logged) == 1
        assert logger.logged[0][0].auth_error is True


class TestConfigError:
    """4. Config error → Halted (no iteration counted)."""

    def test_adapter_config_error_halts(self) -> None:
        adapter = StubCLIAdapter([_config_fail()])
        logger = StubLogger()

        runner = _build_runner(adapter=adapter, logger=logger)
        phase = _make_phase()
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert run.mode == RunMode.HALTED
        assert result.iteration == 0

    def test_model_resolver_config_error_halts(self) -> None:
        resolver = StubModelResolver(raise_config=True)

        runner = _build_runner(model_resolver=resolver)
        phase = _make_phase()
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert run.mode == RunMode.HALTED


class TestGateError:
    """5. Gate error → Halted."""

    def test_gate_error_halts(self) -> None:
        adapter = StubCLIAdapter([_ok_result()])
        gate = StubGateRunner([_gate_error()])

        runner = _build_runner(adapter=adapter, gate=gate)
        phase = _make_phase()
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert run.mode == RunMode.HALTED
        assert result.halted_from == PhaseStatus.GATING


class TestGateTimeout:
    """6. Gate timeout → Halted."""

    def test_gate_timeout_halts(self) -> None:
        adapter = StubCLIAdapter([_ok_result()])
        gate = StubGateRunner([_gate_timeout()])

        runner = _build_runner(adapter=adapter, gate=gate)
        phase = _make_phase()
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert run.mode == RunMode.HALTED


class TestConfabulation:
    """7. Confabulation (exit 0 + dirty tree) → Halt (VR-025)."""

    def test_confabulation_halts(self) -> None:
        adapter = StubCLIAdapter([_ok_result()])
        gate = StubGateRunner([_gate_confabulation()])

        runner = _build_runner(adapter=adapter, gate=gate)
        phase = _make_phase()
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert run.mode == RunMode.HALTED
        assert result.iteration == 0
        assert result.halted_from == PhaseStatus.GATING


class TestGateFailure:
    """8. Gate failure (non-zero exit, dirty tree) → clean tree, retry (VR-026)."""

    def test_gate_failure_cleans_tree_and_retries(self) -> None:
        adapter = StubCLIAdapter([_fail_result(), _ok_result()])
        gate = StubGateRunner(
            [
                GateResult(
                    passed=False, errored=False, hook="working-tree", error_count=2
                ),
                _gate_pass(),
            ]
        )
        clock = StubClock([0, 50, 100, 150])

        runner = _build_runner(adapter=adapter, gate=gate, clock=clock)
        phase = _make_phase()
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.AWAITING_APPROVAL
        assert result.iteration == 1
        assert len(gate.calls) == 2
        assert gate.calls[0][1] == 1  # first call: exit_code=1 (fail)
        assert gate.calls[1][1] == 0  # second call: exit_code=0 (ok)
        assert gate.clean_tree_calls == [Path("/work")]


class TestReviewerFindings:
    """9. Reviewer findings → loop, then clean → AwaitingApproval."""

    def test_reviewer_findings_loop_then_clean(self) -> None:
        # Findings are tagged with the cycle (phase.iteration + 1, 1-based):
        # cycle 1 (phase.iteration 0): 2 open findings → loop
        # cycle 2 (phase.iteration 1): 0 open findings → approval
        adapter = StubCLIAdapter(
            [
                _ok_result(),
                _ok_result(),  # iter 0: author + reviewer
                _ok_result(),
                _ok_result(),  # iter 1: author + reviewer
            ]
        )
        gate = StubGateRunner([_gate_pass(), _gate_pass()])
        findings = StubFindingsStore(
            open_counts={
                ("design", 1): 2,
                ("design", 2): 0,
            },
        )
        clock = StubClock([0, 50, 100, 150, 200, 250, 300, 350])

        runner = _build_runner(
            adapter=adapter,
            gate=gate,
            findings=findings,
            clock=clock,
        )
        phase = _make_phase(reviewer="reviewer-agent")
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.AWAITING_APPROVAL
        assert result.iteration == 1
        assert ("design", 1) in findings.supersede_calls

    def test_reviewer_findings_ingested_before_counting(self) -> None:
        """After the reviewer runs, the ingestor reads the filed findings for the
        current cycle before the loop counts them. Regression for the inert-loop
        bug (findings never ingested) and the interactive-stdout gap (ST-0022)."""
        adapter = StubCLIAdapter([_ok_result(), _ok_result()])  # author + reviewer
        ingestor = StubFindingIngestor()
        findings = StubFindingsStore(open_counts={("design", 1): 0})

        runner = _build_runner(adapter=adapter, ingestor=ingestor, findings=findings)
        phase = _make_phase(reviewer="reviewer-agent")
        run = _make_run()

        runner.run_phase(run, phase)

        assert len(ingestor.calls) == 1
        phase_name, iteration = ingestor.calls[0]
        assert phase_name == "design"
        # first review pass is phase.iteration 0 → cycle 1 (1-based Finding DTO)
        assert iteration == 1


class TestCapExhaustion:
    """10. Cap exhaustion → Halted."""

    def test_author_keeps_failing_until_cap(self) -> None:
        # cap=2: iteration 0 fails, iteration 1 fails, iteration 2 → cap reached
        adapter = StubCLIAdapter([_fail_result(), _fail_result(), _fail_result()])
        # Gate sees failure but returns "not passed" each time to trigger retry
        gate = StubGateRunner(
            [
                GateResult(
                    passed=False, errored=False, hook="working-tree", error_count=0
                ),
                GateResult(
                    passed=False, errored=False, hook="working-tree", error_count=0
                ),
                GateResult(
                    passed=False, errored=False, hook="working-tree", error_count=0
                ),
            ]
        )
        clock = StubClock([0, 50, 100, 150, 200, 250])
        loop = LoopPolicy(cap=2)

        runner = _build_runner(adapter=adapter, gate=gate, loop=loop, clock=clock)
        phase = _make_phase()
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert run.mode == RunMode.HALTED


class TestGateOnlyPhase:
    """11. Gate-only phase (no reviewer) → AwaitingApproval on gate pass."""

    def test_no_reviewer_goes_straight_to_approval(self) -> None:
        runner = _build_runner()
        phase = _make_phase(reviewer=None)
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.AWAITING_APPROVAL
        assert run.mode == RunMode.PAUSED


class TestStatePersistence:
    """Run state is saved after every status transition."""

    def test_state_saved_on_transitions(self) -> None:
        store = StubRunStateStore()

        runner = _build_runner(run_store=store)
        phase = _make_phase()
        run = _make_run()

        runner.run_phase(run, phase)

        # At minimum: AUTHORING save, GATING save, AWAITING_APPROVAL save, PAUSED save
        assert len(store.saves) >= 3


class TestModelReachesAdapter:
    """FAGAN-0001/0031: resolved model must be passed to adapter.invoke()."""

    def test_resolved_model_passed_to_invoke(self) -> None:
        adapter = StubCLIAdapter([_ok_result()])
        resolver = StubModelResolver(model="claude-sonnet-4")

        runner = _build_runner(adapter=adapter, model_resolver=resolver)
        phase = _make_phase()
        run = _make_run()

        runner.run_phase(run, phase)

        assert len(adapter.calls) == 1
        _prompt, _cwd, _timeout, model = adapter.calls[0]
        assert model == "claude-sonnet-4"

    def test_reviewer_also_gets_resolved_model(self) -> None:
        adapter = StubCLIAdapter([_ok_result(), _ok_result()])
        resolver = StubModelResolver(model="gpt-4o")
        findings = StubFindingsStore(open_counts={("design", 1): 0})

        runner = _build_runner(
            adapter=adapter, model_resolver=resolver, findings=findings
        )
        phase = _make_phase(reviewer="reviewer-agent")
        run = _make_run()

        runner.run_phase(run, phase)

        assert len(adapter.calls) == 2
        _p1, _c1, _t1, model1 = adapter.calls[0]  # author
        _p2, _c2, _t2, model2 = adapter.calls[1]  # reviewer
        assert model1 == "gpt-4o"
        assert model2 == "gpt-4o"


class TestInvocationContextThreading:
    """ST-0025: compose() receives the phase/role/iteration context."""

    def test_author_compose_gets_invocation_context(self) -> None:
        composer = StubPromptComposer()
        findings = StubFindingsStore(
            open_findings={
                ("design", 2): [
                    Finding(
                        id="f-1",
                        phase="design",
                        iteration=2,
                        source=FindingSource.SEMANTIC,
                        code="SEM-001",
                        severity=Severity.ERROR,
                        artifact="artifact.txt",
                        message="Fix this",
                        status=FindingStatus.OPEN,
                    )
                ]
            }
        )
        runner = _build_runner(composer=composer, findings=findings)
        phase = _make_phase()
        phase.iteration = 2
        run = _make_run()

        runner.run_phase(run, phase)

        assert len(composer.calls) == 1
        _agent_info, context_paths, invocation, passed_findings = composer.calls[0]
        assert context_paths == []
        assert invocation == InvocationContext(
            phase="design",
            role=AgentRole.AUTHOR,
            iteration=2,
        )
        assert passed_findings == findings.list_open("design", 2)

    def test_reviewer_compose_gets_invocation_context(self) -> None:
        composer = StubPromptComposer()
        adapter = StubCLIAdapter([_ok_result(), _ok_result()])
        findings = StubFindingsStore(open_counts={("design", 1): 0})
        runner = _build_runner(
            adapter=adapter,
            composer=composer,
            findings=findings,
        )
        phase = _make_phase(reviewer="reviewer-agent")
        run = _make_run()

        runner.run_phase(run, phase)

        assert len(composer.calls) == 2
        _author_info, _author_paths, author_invocation, _author_findings = (
            composer.calls[0]
        )
        _reviewer_info, reviewer_paths, reviewer_invocation, reviewer_findings = (
            composer.calls[1]
        )
        assert author_invocation == InvocationContext(
            phase="design",
            role=AgentRole.AUTHOR,
            iteration=0,
        )
        assert reviewer_paths == []
        assert reviewer_invocation == InvocationContext(
            phase="design",
            role=AgentRole.REVIEWER,
            iteration=0,
        )
        assert reviewer_findings is None


class TestClassificationThreading:
    """FAGAN-0007: story classification must reach the model resolver."""

    def test_classification_passed_to_resolver(self) -> None:
        resolved_args: list[tuple] = []

        class TrackingResolver:
            def resolve(self, phase, classification=None, explicit_model=None):
                resolved_args.append((phase, classification, explicit_model))
                return "gpt-4o"

        adapter = StubCLIAdapter([_ok_result()])
        runner = _build_runner(adapter=adapter, model_resolver=TrackingResolver())
        runner._classification = "hard"
        phase = _make_phase()
        run = _make_run()

        runner.run_phase(run, phase)

        assert len(resolved_args) == 1
        assert resolved_args[0][1] == "hard"


class TestResumeSubState:
    """FAGAN-0002: resume must honour the persisted sub-state."""

    def test_resume_awaiting_approval_returns_immediately(self) -> None:
        adapter = StubCLIAdapter([])  # no invocations expected
        runner = _build_runner(adapter=adapter)
        phase = _make_phase()
        phase.status = PhaseStatus.AWAITING_APPROVAL
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.AWAITING_APPROVAL
        assert len(adapter.calls) == 0

    def test_resume_halted_returns_immediately(self) -> None:
        adapter = StubCLIAdapter([])
        runner = _build_runner(adapter=adapter)
        phase = _make_phase()
        phase.status = PhaseStatus.HALTED
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert len(adapter.calls) == 0

    def test_resume_complete_returns_immediately(self) -> None:
        adapter = StubCLIAdapter([])
        runner = _build_runner(adapter=adapter)
        phase = _make_phase()
        phase.status = PhaseStatus.COMPLETE
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.COMPLETE
        assert len(adapter.calls) == 0

    def test_resume_at_gating_skips_authoring(self) -> None:
        """If interrupted at GATING, re-run gate but not the author."""
        adapter = StubCLIAdapter([])  # no author invocation expected
        gate = StubGateRunner([_gate_pass()])
        runner = _build_runner(adapter=adapter, gate=gate)
        phase = _make_phase()
        phase.status = PhaseStatus.GATING
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.AWAITING_APPROVAL
        assert len(adapter.calls) == 0  # author not invoked
        assert len(gate.calls) == 1

    def test_resume_at_reviewing_skips_authoring_and_gating(self) -> None:
        """If interrupted at REVIEWING, re-run reviewer only."""
        adapter = StubCLIAdapter([_ok_result()])  # reviewer only
        gate = StubGateRunner([])  # no gate calls expected
        findings = StubFindingsStore(open_counts={("design", 1): 0})

        runner = _build_runner(adapter=adapter, gate=gate, findings=findings)
        phase = _make_phase(reviewer="reviewer-agent")
        phase.status = PhaseStatus.REVIEWING
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.AWAITING_APPROVAL
        assert len(adapter.calls) == 1  # reviewer only
        assert len(gate.calls) == 0


class TestReviewerAuthConfigHalt:
    """FAGAN-0009: reviewer auth/config errors halt immediately."""

    def test_reviewer_auth_error_halts(self) -> None:
        adapter = StubCLIAdapter([_ok_result(), _auth_fail()])
        findings = StubFindingsStore(open_counts={("design", 1): 0})

        runner = _build_runner(adapter=adapter, findings=findings)
        phase = _make_phase(reviewer="reviewer-agent")
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert run.mode == RunMode.HALTED
        assert result.iteration == 0  # no retry consumed

    def test_reviewer_config_error_halts(self) -> None:
        adapter = StubCLIAdapter([_ok_result(), _config_fail()])
        findings = StubFindingsStore(open_counts={("design", 1): 0})

        runner = _build_runner(adapter=adapter, findings=findings)
        phase = _make_phase(reviewer="reviewer-agent")
        run = _make_run()

        result = runner.run_phase(run, phase)

        assert result.status == PhaseStatus.HALTED
        assert run.mode == RunMode.HALTED
        assert result.iteration == 0
