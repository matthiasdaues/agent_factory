"""PhaseRunner — drives one phase through the state machine (ST-0005).

Implements the author → gate → review → loop-or-approve control flow
defined in docs/spec/supplementary_specs/state-machines.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from orchestrator.entities import (
    AgentInvocation,
    AgentRole,
    InvocationContext,
    PhaseRecord,
    PhaseStatus,
    Run,
    RunMode,
)
from orchestrator.loop_policy import LoopPolicy
from orchestrator.model_resolver import ConfigError, ModelResolver
from orchestrator.ports import (
    AgentRegistry,
    CLIAdapter,
    Clock,
    FindingIngestor,
    FindingsStore,
    GateRunner,
    Logger,
    PromptComposer,
    RunStateStore,
)


class PhaseRunner:
    """Drives one phase through the author→gate→review state machine."""

    def __init__(
        self,
        adapter: CLIAdapter,
        gate_runner: GateRunner,
        findings_store: FindingsStore,
        finding_ingestor: FindingIngestor,
        run_store: RunStateStore,
        agent_registry: AgentRegistry,
        prompt_composer: PromptComposer,
        logger: Logger,
        loop_policy: LoopPolicy,
        model_resolver: ModelResolver,
        clock: Clock,
        cwd: Path,
        timeout_s: int = 1800,
        interactive: bool = False,
        on_agent_start=None,
        story_tier: Optional[str] = None,
    ) -> None:
        self._adapter = adapter
        self._gate = gate_runner
        self._findings = findings_store
        self._ingestor = finding_ingestor
        self._run_store = run_store
        self._registry = agent_registry
        self._composer = prompt_composer
        self._logger = logger
        self._loop = loop_policy
        self._model_resolver = model_resolver
        self._clock = clock
        self._cwd = cwd
        self._timeout_s = timeout_s
        self._interactive = interactive
        self._on_agent_start = on_agent_start
        self._story_tier = story_tier

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _set_status(self, run: Run, phase: PhaseRecord, status: PhaseStatus) -> None:
        phase.status = status
        self._run_store.save(run)

    def _halt(self, run: Run, phase: PhaseRecord) -> PhaseRecord:
        phase.halted_from = phase.status
        self._set_status(run, phase, PhaseStatus.HALTED)
        run.mode = RunMode.HALTED
        self._run_store.save(run)
        return phase

    def _clean_tree(self) -> None:
        """Reset working tree before retry (ADR-0013, VR-026)."""
        self._gate.clean_tree(self._cwd)

    # ------------------------------------------------------------------
    # main entry
    # ------------------------------------------------------------------

    def run_phase(self, run: Run, phase_record: PhaseRecord) -> PhaseRecord:
        """Drive *phase_record* through the state machine, returning it
        with an updated status and iteration count.

        Respects persisted sub-state on resume (UC-06, ATAM-R07):
        AWAITING_APPROVAL/HALTED/COMPLETE → return immediately;
        GATING → skip authoring, re-run gate;
        REVIEWING → skip authoring and gating, re-run reviewer.
        """

        # Terminal / paused states → return as-is (UC-06)
        if phase_record.status in (
            PhaseStatus.AWAITING_APPROVAL,
            PhaseStatus.HALTED,
            PhaseStatus.COMPLETE,
        ):
            return phase_record

        # Resume flags: skip earlier stages on first iteration only
        _skip_author = phase_record.status in (
            PhaseStatus.GATING,
            PhaseStatus.REVIEWING,
        )
        _skip_gate = phase_record.status == PhaseStatus.REVIEWING
        # Resume-idempotency flag for REVIEWING (FAGAN-0043: skip re-invoking
        # the reviewer if this cycle already reviewed).
        # GATING no longer needs special resume logic — verify() is idempotent.
        _resume_reviewing = phase_record.status == PhaseStatus.REVIEWING

        while True:
            # Each invoked agent resolves its own model, independently (ADR-0018
            # point 1, ADR-0020). `story_tier` stands in for a tier-less
            # developer agent's absent frontmatter tier (ADR-0018 point 2).
            author_info = self._registry.resolve(phase_record.name, AgentRole.AUTHOR)

            try:
                model = self._model_resolver.resolve_tier(
                    self._story_tier or author_info.tier
                )
            except ConfigError:
                return self._halt(run, phase_record)

            # ---- AUTHORING ----
            _did_author = not _skip_author
            if not _skip_author:
                self._set_status(run, phase_record, PhaseStatus.AUTHORING)

                open_findings = self._findings.list_open(
                    phase_record.name, phase_record.iteration
                )
                invocation_ctx = InvocationContext(
                    phase=phase_record.name,
                    role=AgentRole.AUTHOR,
                    iteration=phase_record.iteration,
                )

                if self._on_agent_start:
                    self._on_agent_start(
                        author_info, invocation_ctx, bool(open_findings)
                    )

                prompt = self._composer.compose(
                    author_info,
                    [],
                    invocation_ctx,
                    open_findings if open_findings else None,
                )

                start_ms = self._clock.now_ms()
                result = self._adapter.invoke(
                    prompt, self._cwd, self._timeout_s, model=model
                )
                end_ms = self._clock.now_ms()

                invocation = AgentInvocation(
                    agent=author_info.name,
                    role=AgentRole.AUTHOR,
                    adapter="cli",
                    model=model,
                    exit_code=result.exit_code,
                    duration_ms=end_ms - start_ms,
                    timed_out=result.timed_out,
                    auth_error=result.auth_error,
                    config_error=result.config_error,
                )

                # BR-018: auth failure → halt immediately (no gating)
                if result.auth_error:
                    self._logger.log(invocation, None)
                    return self._halt(run, phase_record)

                # BR-020: config error → halt immediately (no gating)
                if result.config_error:
                    self._logger.log(invocation, None)
                    return self._halt(run, phase_record)

                # NOTE: author invocation done, but DON'T log yet — gate comes next.
                # Gate must run even on non-zero exit to check tree state.
            _skip_author = False  # only skip on first resume iteration

            # ---- GATING ----
            if not _skip_gate:
                self._set_status(run, phase_record, PhaseStatus.GATING)

                # Gate checks working-tree state after author exit (ADR-0013)
                # On resume from GATING, use exit_code=0 since verify() is
                # idempotent — it only checks current tree state (VR-027).
                exit_code = result.exit_code if _did_author else 0
                gate_result = self._gate.verify(self._cwd, exit_code)
                phase_record.last_gate = gate_result

                if _did_author:
                    # Log the author invocation with the gate result (normal flow)
                    self._logger.log(invocation, gate_result)

                # Confabulation: exit 0 but dirty tree → halt (VR-025)
                if gate_result.hook == "confabulation":
                    return self._halt(run, phase_record)

                # Gate errored or timed out → halt
                if gate_result.errored or gate_result.timed_out:
                    return self._halt(run, phase_record)

                # Gate failed (non-zero exit) → clean tree if dirty, then RetryOrHalt
                if not gate_result.passed:
                    if gate_result.error_count > 0:  # dirty files exist
                        self._clean_tree()
                    if not self._retry_or_halt(run, phase_record):
                        return phase_record
                    continue
            _skip_gate = False  # only skip on first resume iteration

            # Gate passed — check for reviewer
            if phase_record.reviewer is not None:
                # ---- REVIEWING ----
                self._set_status(run, phase_record, PhaseStatus.REVIEWING)

                # FAGAN-0043: on resume into REVIEWING, if this cycle's review
                # has already been ingested (findings already recorded), do not
                # re-invoke the reviewer or re-ingest — that would duplicate
                # semantic findings. Go straight to the open-findings decision.
                if (
                    _resume_reviewing
                    and self._findings.open_count(
                        phase_record.name, phase_record.iteration + 1
                    )
                    > 0
                ):
                    _resume_reviewing = False
                    self._loop.supersede_prior(
                        self._findings, phase_record.name, phase_record.iteration + 1
                    )
                    if not self._retry_or_halt(run, phase_record):
                        return phase_record
                    continue
                _resume_reviewing = False

                reviewer_info = self._registry.resolve(
                    phase_record.name, AgentRole.REVIEWER
                )

                try:
                    model = self._model_resolver.resolve_tier(reviewer_info.tier)
                except ConfigError:
                    return self._halt(run, phase_record)

                reviewer_ctx = InvocationContext(
                    phase=phase_record.name,
                    role=AgentRole.REVIEWER,
                    iteration=phase_record.iteration,
                )

                if self._on_agent_start:
                    self._on_agent_start(reviewer_info, reviewer_ctx, False)

                review_prompt = self._composer.compose(
                    reviewer_info, [], reviewer_ctx, None
                )

                r_start = self._clock.now_ms()
                r_result = self._adapter.invoke(
                    review_prompt,
                    self._cwd,
                    self._timeout_s,
                    model=model,
                )
                r_end = self._clock.now_ms()

                r_invocation = AgentInvocation(
                    agent=reviewer_info.name,
                    role=AgentRole.REVIEWER,
                    adapter="cli",
                    model=model,
                    exit_code=r_result.exit_code,
                    duration_ms=r_end - r_start,
                    timed_out=r_result.timed_out,
                    auth_error=r_result.auth_error,
                    config_error=r_result.config_error,
                )
                self._logger.log(r_invocation, None)

                # FAGAN-0009: reviewer auth/config errors halt immediately
                # (BR-018/BR-020), same as for author invocations.
                if r_result.auth_error:
                    return self._halt(run, phase_record)

                if r_result.config_error:
                    return self._halt(run, phase_record)

                # Reviewer failure (non-auth/config) → RetryOrHalt
                if r_result.exit_code != 0:
                    if not self._retry_or_halt(run, phase_record):
                        return phase_record
                    continue

                # Ingest the reviewer's findings, then count (UC-02 §7 / SF-03).
                cycle = phase_record.iteration + 1
                # FAGAN-0040: record the cycle the reviewer actually reviewed so
                # approval/status read THIS cycle rather than re-deriving
                # ``iteration + 1`` (which the empty-commit pause path would
                # advance past without ingesting). Set whenever the reviewer ran,
                # even on a clean (0-finding) review, so a subsequent empty-commit
                # pause still points approval at the last real review. Persisted
                # by the _set_status/save calls below (or by the next AUTHORING
                # save when the pass loops).
                phase_record.last_reviewed_cycle = cycle
                self._ingestor.ingest_open_findings(phase_record.name, cycle)
                open_count = self._findings.open_count(phase_record.name, cycle)

                if open_count == 0:
                    # Clean — proceed to approval
                    self._set_status(run, phase_record, PhaseStatus.AWAITING_APPROVAL)
                    run.mode = RunMode.PAUSED
                    self._run_store.save(run)
                    return phase_record

                # Open findings remain — supersede prior cycles' findings, loop
                self._loop.supersede_prior(self._findings, phase_record.name, cycle)
                if not self._retry_or_halt(run, phase_record):
                    return phase_record
                continue

            # Gate passed, no reviewer → AwaitingApproval
            self._set_status(run, phase_record, PhaseStatus.AWAITING_APPROVAL)
            run.mode = RunMode.PAUSED
            self._run_store.save(run)
            return phase_record

    # ------------------------------------------------------------------
    # RetryOrHalt decision
    # ------------------------------------------------------------------

    def _retry_or_halt(self, run: Run, phase: PhaseRecord) -> bool:
        """Return True if looping (iteration incremented), False if halted."""
        if self._loop.should_loop(phase.iteration + 1):
            phase.iteration += 1
            run.iteration = phase.iteration
            return True
        return bool(not self._halt(run, phase))  # always False
