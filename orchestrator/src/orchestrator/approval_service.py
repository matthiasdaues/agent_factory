"""Approval and rejection at a paused phase gate."""

from __future__ import annotations

from pathlib import Path

from orchestrator.entities import PhaseStatus, Run, RunMode
from orchestrator.ports import AgentRegistry, FindingsStore, GateRunner, RunStateStore


class ApprovalService:
    def __init__(
        self,
        run_store: RunStateStore,
        findings_store: FindingsStore,
        gate_runner: GateRunner,
        agent_registry: AgentRegistry,
        cwd: Path | None = None,
    ):
        self._run_store = run_store
        self._findings_store = findings_store
        self._gate_runner = gate_runner
        self._agent_registry = agent_registry
        self._cwd = cwd or Path.cwd()

    def approve(self) -> None:
        run = self._load_run()
        phase = self._current_phase(run)
        self._require_awaiting_approval(phase)

        # FAGAN-0038: allow approval of empty-commit phases — the operator
        # acknowledges the empty commit is acceptable
        is_empty_commit = (
            phase.last_gate is not None and phase.last_gate.hook == "empty-commit"
        )
        if not is_empty_commit:
            if phase.last_gate is None or not phase.last_gate.passed:
                raise ValueError("current phase gate has not passed")

        # FAGAN-0040 (BR-007 / UC-04): findings are tagged to the review CYCLE,
        # which PhaseRunner persists as ``phase.last_reviewed_cycle`` at the point
        # it ingests/counts them. Approval must count the SAME cycle key.
        # Re-deriving ``iteration + 1`` regresses the empty-commit pause path: a
        # prior pass tags findings at cycle N and loops (iteration advances), then
        # a later pass produces an empty commit and re-pauses at AWAITING_APPROVAL
        # WITHOUT ingesting or advancing iteration. ``iteration + 1`` would then
        # point past the still-open findings and wrongly approve. Reading the
        # persisted last-reviewed cycle keeps approval and the reviewer in sync.
        # ``None`` means no review ever ran (e.g. gate-passed-no-reviewer phase);
        # the gate already passed, so there is nothing to block on.
        if phase.last_reviewed_cycle is not None:
            if (
                self._findings_store.open_count(phase.name, phase.last_reviewed_cycle)
                != 0
            ):
                raise ValueError("current phase still has open findings")

        # VR-012 / UC-04 ext 3a: re-gate if artifacts changed since the gate
        author_info = self._agent_registry.resolve(phase.name, "author")
        if self._gate_runner.artifacts_changed(author_info.outputs):
            gate_result = self._gate_runner.verify(self._cwd, exit_code=0)
            phase.last_gate = gate_result
            if not gate_result.passed:
                # FAGAN-0039 (UC-04 ext 3a / UC-06): a FAILED stale re-gate must
                # NOT leave the phase in AWAITING_APPROVAL. That status is
                # terminal for the state machine (PhaseRunner.run_phase returns
                # immediately on it), so approve keeps failing and resume/
                # run-phase cannot recover — the run wedges. Move the phase back
                # into the executable GATING sub-state so resume/run-phase
                # re-enter the loop: PhaseRunner treats GATING as a resume point,
                # re-gates the existing HEAD, and on failure ingests the
                # deterministic gate findings and loops the author. Drop the run
                # to HALTED (not PAUSED/awaiting — that is the wedge; not RUNNING
                # — that would block run-phase via VR-017); HALTED still permits
                # both resume and run-phase recovery and signals a non-zero exit.
                phase.status = PhaseStatus.GATING
                run.mode = RunMode.HALTED
                self._run_store.save(run)
                raise ValueError(
                    "re-gate failed after artifact changes — "
                    f"hook={gate_result.hook}, "
                    f"errors={gate_result.error_count}, "
                    f"errored={gate_result.errored}, "
                    f"timed_out={gate_result.timed_out}"
                )

        phase.status = PhaseStatus.COMPLETE
        run.mode = self._approved_mode(run)
        # FAGAN-0035: advance current_phase pointer regardless of mode
        # so resume knows which phase to continue with
        if run.mode != RunMode.COMPLETE:
            phase_index = self._phase_index(run)
            if phase_index is not None and phase_index + 1 < len(run.chain):
                next_name = run.chain[phase_index + 1]
                run.current_phase = next_name
                # FAGAN-0041: sync the run.iteration checkpoint to the phase we
                # advanced to, so run.json doesn't retain the previous phase's
                # iteration (which resume/status would otherwise read back).
                next_phase = self._phase_named(run, next_name)
                if next_phase is not None:
                    run.iteration = next_phase.iteration
        self._run_store.save(run)

    def reject(self, note: str | None = None) -> None:
        run = self._load_run()
        phase = self._current_phase(run)
        self._require_awaiting_approval(phase)

        phase.status = PhaseStatus.HALTED
        phase.rejection_note = note
        run.mode = RunMode.HALTED
        self._run_store.save(run)

    def _load_run(self) -> Run:
        run = self._run_store.load()
        if run is None:
            raise ValueError("no active run")
        return run

    def _current_phase(self, run: Run):
        for phase in run.phases:
            if phase.name == run.current_phase and phase.iteration == run.iteration:
                return phase
        for phase in run.phases:
            if phase.name == run.current_phase:
                return phase
        raise ValueError(f"unknown current phase: {run.current_phase}")

    def _phase_named(self, run: Run, name: str):
        for phase in run.phases:
            if phase.name == name:
                return phase
        return None

    def _require_awaiting_approval(self, phase) -> None:
        if phase.status != PhaseStatus.AWAITING_APPROVAL:
            raise ValueError("current phase is not awaiting approval")

    def _approved_mode(self, run: Run) -> RunMode:
        phase_index = self._phase_index(run)
        if phase_index is None or phase_index == len(run.chain) - 1:
            return RunMode.COMPLETE
        # FAGAN-0035: explicit approval pauses rather than setting RUNNING,
        # since no phase is actually executing. The operator runs `resume`
        # to continue the chain.
        return RunMode.PAUSED

    def _phase_index(self, run: Run):
        try:
            return run.chain.index(run.current_phase)
        except ValueError:
            return None
