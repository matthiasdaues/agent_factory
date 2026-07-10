"""Read-only status projection for the `status` command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from orchestrator.entities import GateResult, Run, RunMode
from orchestrator.ports import FindingsStore, InvocationLogReader, RunStateStore


@dataclass(frozen=True)
class RunStatus:
    mode: Optional[str]
    current_phase: Optional[str]
    iteration: Optional[int]
    open_findings: int
    last_gate: Optional[GateResult]


@dataclass(frozen=True)
class PhaseDetail:
    """Per-phase projection for `status > phase details` (FR-T3)."""

    name: str
    author: str
    reviewer: Optional[str]
    status: str
    iteration: int
    last_gate: Optional[GateResult]
    halted_from: Optional[str]


@dataclass(frozen=True)
class FindingSummary:
    """One open finding for `status > findings` (FR-T4)."""

    id: str
    severity: str
    artifact: str
    message: str
    status: str


@dataclass(frozen=True)
class LogEntry:
    """One invocation-log record for `status > log` (FR-T5)."""

    agent: str
    role: str
    model: Optional[str]
    exit_code: int
    duration_ms: int
    gate: Optional[GateResult]


class StatusService:
    def __init__(
        self,
        run_store: RunStateStore,
        findings_store: FindingsStore,
        invocation_log: Optional[InvocationLogReader] = None,
    ):
        self._run_store = run_store
        self._findings_store = findings_store
        self._invocation_log = invocation_log

    def get_status(self) -> RunStatus:
        run = self._run_store.load()
        if run is None:
            return RunStatus(
                mode=None,
                current_phase=None,
                iteration=None,
                open_findings=0,
                last_gate=None,
            )

        phase = self._current_phase(run)
        # FAGAN-0040: count open findings on the cycle the reviewer actually
        # reviewed (persisted on the phase), matching ApprovalService. Reading
        # ``run.iteration`` here has the same off-by-one as the old approval
        # path. ``None`` (no review ran) → 0 open findings.
        last_reviewed_cycle = phase.last_reviewed_cycle if phase is not None else None
        if last_reviewed_cycle is None:
            open_findings = 0
        else:
            open_findings = self._findings_store.open_count(
                run.current_phase, last_reviewed_cycle
            )

        return RunStatus(
            mode=self._mode_value(run.mode),
            current_phase=run.current_phase,
            iteration=run.iteration,
            open_findings=open_findings,
            last_gate=phase.last_gate if phase is not None else None,
        )

    def get_phase_details(self) -> List[PhaseDetail]:
        """Per-phase projection for `status > phase details` (FR-T3, read-only)."""
        run = self._run_store.load()
        if run is None:
            return []
        return [
            PhaseDetail(
                name=phase.name,
                author=phase.author,
                reviewer=phase.reviewer,
                status=phase.status.value,
                iteration=phase.iteration,
                last_gate=phase.last_gate,
                halted_from=(
                    phase.halted_from.value if phase.halted_from is not None else None
                ),
            )
            for phase in run.phases
        ]

    def get_findings(self) -> List[FindingSummary]:
        """Open findings for the active run's current review cycle (FR-T4, read-only).

        Mirrors the phase/cycle resolution ``get_status`` uses (FAGAN-0040):
        findings are read on the cycle the reviewer actually reviewed
        (``last_reviewed_cycle``), not on ``run.iteration``. When no review has
        run yet, returns `[]` without querying the findings store.
        """
        run = self._run_store.load()
        if run is None:
            return []
        phase = self._current_phase(run)
        last_reviewed_cycle = phase.last_reviewed_cycle if phase is not None else None
        if last_reviewed_cycle is None:
            return []
        findings = self._findings_store.list_open(
            run.current_phase, last_reviewed_cycle
        )
        return [
            FindingSummary(
                id=finding.id,
                severity=finding.severity.value,
                artifact=finding.artifact,
                message=finding.message,
                status=finding.status.value,
            )
            for finding in findings
        ]

    def get_log(self) -> List[LogEntry]:
        """Invocation-log projection for `status > log` (FR-T5, read-only).

        Returns `[]` when no `InvocationLogReader` was configured — reads
        never drive control flow (FR-T6), so a missing reader is not an error.
        """
        if self._invocation_log is None:
            return []
        return [
            LogEntry(
                agent=record.invocation.agent,
                role=record.invocation.role.value,
                model=record.invocation.model,
                exit_code=record.invocation.exit_code,
                duration_ms=record.invocation.duration_ms,
                gate=record.gate,
            )
            for record in self._invocation_log.read_entries()
        ]

    def _current_phase(self, run: Run):
        for phase in run.phases:
            if phase.name == run.current_phase and phase.iteration == run.iteration:
                return phase
        for phase in run.phases:
            if phase.name == run.current_phase:
                return phase
        return None

    def _mode_value(self, mode: RunMode) -> str:
        return mode.value
