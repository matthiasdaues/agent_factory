"""Tests for the `status` menu submenu's four read-only display views.

Traces: UC-08, AG-13, FR-T1..T6, BR-033, cli_specification.md §Status
(ST-0055). Covers the dispatch-hook wiring `build_status_dispatch` builds
for the `status.overview` / `status.phase-details` / `status.findings` /
`status.log` display nodes, the formatter functions each renders through,
the read-only guarantee, and the overview parity between direct mode
(`orchestrate status`) and menu mode.
"""

from __future__ import annotations

import pytest

from orchestrator.adapters.findings_store import FilesystemFindingsStore
from orchestrator.adapters.run_state_store import JsonRunStateStore
from orchestrator.cli import (
    _format_findings,
    _format_invocation_log,
    _format_phase_details,
    _format_status_overview,
    build_status_dispatch,
    main,
)
from orchestrator.entities import (
    AgentRole,
    GateResult,
    PhaseRecord,
    PhaseStatus,
    Run,
    RunMode,
)
from orchestrator.menu_controller import DispatchOutcome
from orchestrator.menu_tree import build_root_menu
from orchestrator.status_service import (
    FindingSummary,
    LogEntry,
    PhaseDetail,
    RunStatus,
    StatusService,
)


def _status_node(node_id: str):
    root = build_root_menu()
    status = next(child for child in root.children if child.id == "status")
    return next(child for child in status.children if child.id == node_id)


# --- Formatter unit tests (fixture data) -------------------------------------


class TestFormatStatusOverview:
    def test_idle_run(self) -> None:
        status = RunStatus(
            mode=None,
            current_phase=None,
            iteration=None,
            open_findings=0,
            last_gate=None,
        )
        text = _format_status_overview(status)
        assert "no active run" in text
        assert "open findings: 0" in text

    def test_active_run(self) -> None:
        gate = GateResult(
            passed=True,
            errored=False,
            hook="pre-commit",
            error_count=0,
            timed_out=False,
        )
        status = RunStatus(
            mode="running",
            current_phase="requirements",
            iteration=2,
            open_findings=3,
            last_gate=gate,
        )
        text = _format_status_overview(status)
        assert "running" in text
        assert "requirements" in text
        assert "2" in text
        assert "open findings: 3" in text
        assert "passed=True" in text
        assert "hook=pre-commit" in text


class TestFormatPhaseDetails:
    def test_empty(self) -> None:
        assert "no phases" in _format_phase_details([])

    def test_populated(self) -> None:
        gate = GateResult(
            passed=False,
            errored=False,
            hook="pre-commit",
            error_count=2,
            timed_out=False,
        )
        phases = [
            PhaseDetail(
                name="requirements",
                author="requirements-agent",
                reviewer="spec-review-agent",
                status="complete",
                iteration=2,
                last_gate=gate,
                halted_from=None,
            ),
            PhaseDetail(
                name="architecture",
                author="architecture-agent",
                reviewer=None,
                status="halted",
                iteration=1,
                last_gate=None,
                halted_from="gating",
            ),
        ]
        text = _format_phase_details(phases)
        assert "requirements" in text
        assert "requirements-agent" in text
        assert "spec-review-agent" in text
        assert "complete" in text
        assert "architecture" in text
        assert "halted" in text
        assert "gating" in text
        assert "errors=2" in text


class TestFormatFindings:
    def test_empty(self) -> None:
        assert "no open findings" in _format_findings([])

    def test_populated(self) -> None:
        findings = [
            FindingSummary(
                id="F-0001",
                severity="error",
                artifact="docs/spec/foo.md",
                message="missing section",
                status="open",
            )
        ]
        text = _format_findings(findings)
        assert "F-0001" in text
        assert "error" in text
        assert "docs/spec/foo.md" in text
        assert "missing section" in text
        assert "open" in text


class TestFormatInvocationLog:
    def test_empty(self) -> None:
        assert "no invocation log" in _format_invocation_log([])

    def test_populated(self) -> None:
        gate = GateResult(
            passed=True,
            errored=False,
            hook="pre-commit",
            error_count=0,
            timed_out=False,
        )
        entries = [
            LogEntry(
                agent="requirements-agent",
                role=AgentRole.AUTHOR.value,
                model="gpt-5.4",
                exit_code=0,
                duration_ms=1234,
                gate=gate,
            )
        ]
        text = _format_invocation_log(entries)
        assert "requirements-agent" in text
        assert "author" in text
        assert "gpt-5.4" in text
        assert "1234" in text
        assert "passed=True" in text


# --- Dispatch-hook wiring -----------------------------------------------------


class _StubStatusService:
    """Exposes only the four StatusService getters — no mutating methods exist,
    so any attempt by the dispatch hook to call something else raises
    AttributeError rather than silently mutating anything."""

    def __init__(self, status, phases, findings, log) -> None:
        self._status = status
        self._phases = phases
        self._findings = findings
        self._log = log

    def get_status(self):
        return self._status

    def get_phase_details(self):
        return self._phases

    def get_findings(self):
        return self._findings

    def get_log(self):
        return self._log


def _stub_service() -> _StubStatusService:
    gate = GateResult(
        passed=True, errored=False, hook="pre-commit", error_count=0, timed_out=False
    )
    return _StubStatusService(
        status=RunStatus(
            mode="running",
            current_phase="requirements",
            iteration=1,
            open_findings=0,
            last_gate=gate,
        ),
        phases=[
            PhaseDetail(
                name="requirements",
                author="requirements-agent",
                reviewer="spec-review-agent",
                status="authoring",
                iteration=1,
                last_gate=gate,
                halted_from=None,
            )
        ],
        findings=[
            FindingSummary(
                id="F-0001",
                severity="warning",
                artifact="foo.md",
                message="nit",
                status="open",
            )
        ],
        log=[
            LogEntry(
                agent="requirements-agent",
                role="author",
                model="gpt-5.4",
                exit_code=0,
                duration_ms=42,
                gate=gate,
            )
        ],
    )


class TestBuildStatusDispatch:
    def test_overview_node_renders_get_status(self) -> None:
        dispatch = build_status_dispatch(_stub_service())
        outcome = dispatch(_status_node("status.overview"))
        assert isinstance(outcome, DispatchOutcome)
        assert outcome.long_running is False
        assert "requirements" in outcome.content
        assert "running" in outcome.content

    def test_phase_details_node_renders_get_phase_details(self) -> None:
        dispatch = build_status_dispatch(_stub_service())
        outcome = dispatch(_status_node("status.phase-details"))
        assert "requirements-agent" in outcome.content
        assert "spec-review-agent" in outcome.content
        assert outcome.long_running is False

    def test_findings_node_renders_get_findings(self) -> None:
        dispatch = build_status_dispatch(_stub_service())
        outcome = dispatch(_status_node("status.findings"))
        assert "F-0001" in outcome.content
        assert "nit" in outcome.content
        assert outcome.long_running is False

    def test_log_node_renders_get_log(self) -> None:
        dispatch = build_status_dispatch(_stub_service())
        outcome = dispatch(_status_node("status.log"))
        assert "requirements-agent" in outcome.content
        assert "42" in outcome.content
        assert outcome.long_running is False

    def test_unknown_node_id_raises(self) -> None:
        from orchestrator.entities import MenuNode, MenuNodeType

        dispatch = build_status_dispatch(_stub_service())
        bogus = MenuNode(id="status.bogus", label="bogus", type=MenuNodeType.DISPLAY)
        with pytest.raises(ValueError, match="status.bogus"):
            dispatch(bogus)


# --- Read-only guarantee (BR-033, VR-030) ------------------------------------


class _GuardRunStore:
    def load(self):
        return None

    def exists(self):
        return False

    def save(self, run):  # pragma: no cover - defensive
        raise AssertionError("save must not be called by a status view")


class _GuardFindingsStore:
    def open_count(self, phase, iteration):
        return 0

    def list_open(self, phase, iteration):
        return []

    def ingest(self, findings):  # pragma: no cover - defensive
        raise AssertionError("ingest must not be called by a status view")

    def supersede_prior(self, phase, current_iteration):  # pragma: no cover
        raise AssertionError("supersede_prior must not be called by a status view")


class _GuardInvocationLog:
    def read_entries(self):
        return []


class TestStatusViewsAreReadOnly:
    @pytest.mark.parametrize(
        "node_id",
        ["status.overview", "status.phase-details", "status.findings", "status.log"],
    )
    def test_dispatch_never_mutates(self, node_id: str) -> None:
        service = StatusService(
            _GuardRunStore(), _GuardFindingsStore(), _GuardInvocationLog()
        )
        dispatch = build_status_dispatch(service)
        outcome = dispatch(_status_node(node_id))
        assert isinstance(outcome.content, str)


# --- Overview parity: direct mode vs menu mode (FR-T2) -----------------------


def _make_run() -> Run:
    return Run(
        run_id="RUN-TEST",
        branch="orchestrator/run-test",
        chain=["requirements"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.PAUSED,
        phases=[
            PhaseRecord(
                name="requirements",
                author="requirements-agent",
                reviewer="spec-review-agent",
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=1,
            )
        ],
    )


class TestOverviewParity:
    def test_menu_mode_overview_matches_direct_mode_status(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        JsonRunStateStore(orch_dir).save(_make_run())

        rc = main(["status"])
        assert rc == 0
        direct_mode_output = capsys.readouterr().out.strip()

        run_store = JsonRunStateStore(orch_dir)
        findings_store = FilesystemFindingsStore(orch_dir / "findings")
        service = StatusService(run_store, findings_store)
        dispatch = build_status_dispatch(service)
        outcome = dispatch(_status_node("status.overview"))

        assert outcome.content.strip() == direct_mode_output
