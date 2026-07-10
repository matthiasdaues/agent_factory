from __future__ import annotations

from orchestrator.entities import (
    AgentInvocation,
    AgentRole,
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
from orchestrator.ports import LogRecord
from orchestrator.status_service import (
    FindingSummary,
    LogEntry,
    PhaseDetail,
    RunStatus,
    StatusService,
)


class _IdleRunStore:
    def load(self):
        return None

    def exists(self):
        return False

    def save(self, run):  # pragma: no cover - defensive
        raise AssertionError("save must not be called")


class _IdleFindingsStore:
    def open_count(self, phase, iteration):  # pragma: no cover - defensive
        raise AssertionError("open_count must not be called when idle")

    def ingest(self, findings):  # pragma: no cover - defensive
        raise AssertionError("ingest must not be called")

    def supersede_prior(self, phase, current_iteration):  # pragma: no cover
        raise AssertionError("supersede_prior must not be called")


class _ActiveRunStore:
    def __init__(self, run):
        self.run = run
        self.load_calls = 0
        self.exists_calls = 0

    def load(self):
        self.load_calls += 1
        return self.run

    def exists(self):
        self.exists_calls += 1
        return True

    def save(self, run):  # pragma: no cover - defensive
        raise AssertionError("save must not be called")


class _ActiveFindingsStore:
    def __init__(self, open_findings):
        self.open_findings = open_findings
        self.calls = []

    def open_count(self, phase, iteration):
        self.calls.append((phase, iteration))
        return self.open_findings

    def ingest(self, findings):  # pragma: no cover - defensive
        raise AssertionError("ingest must not be called")

    def supersede_prior(self, phase, current_iteration):  # pragma: no cover
        raise AssertionError("supersede_prior must not be called")


def test_no_run_returns_idle_status():
    service = StatusService(_IdleRunStore(), _IdleFindingsStore())

    assert service.get_status() == RunStatus(
        mode=None,
        current_phase=None,
        iteration=None,
        open_findings=0,
        last_gate=None,
    )


def test_active_run_returns_projection():
    gate = GateResult(
        passed=True,
        errored=False,
        hook="pre-commit",
        error_count=0,
        timed_out=False,
    )
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=2,
        mode=RunMode.RUNNING,
        phases=[
            PhaseRecord(
                name="requirements",
                author="author-agent",
                reviewer="review-agent",
                iteration=2,
                last_gate=gate,
                # FAGAN-0040: status counts open findings on the persisted review
                # cycle, matching approval — not on run.iteration.
                last_reviewed_cycle=2,
            )
        ],
    )
    run_store = _ActiveRunStore(run)
    findings_store = _ActiveFindingsStore(open_findings=3)
    service = StatusService(run_store, findings_store)

    assert service.get_status() == RunStatus(
        mode="running",
        current_phase="requirements",
        iteration=2,
        open_findings=3,
        last_gate=gate,
    )
    assert findings_store.calls == [("requirements", 2)]
    assert run_store.load_calls == 1
    assert run_store.exists_calls == 0


def test_active_run_without_review_reports_zero_open_findings():
    """FAGAN-0040: a phase whose reviewer never ran (last_reviewed_cycle is None,
    e.g. a gate-passed-no-reviewer phase) reports 0 open findings without ever
    querying the findings store."""
    gate = GateResult(
        passed=True,
        errored=False,
        hook="pre-commit",
        error_count=0,
        timed_out=False,
    )
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.RUNNING,
        phases=[
            PhaseRecord(
                name="requirements",
                author="author-agent",
                reviewer=None,
                iteration=1,
                last_gate=gate,
                last_reviewed_cycle=None,
            )
        ],
    )
    run_store = _ActiveRunStore(run)

    class _GuardFindingsStore:
        def open_count(self, phase, iteration):
            raise AssertionError("open_count must not be called when no review ran")

    service = StatusService(run_store, _GuardFindingsStore())

    status = service.get_status()
    assert status.open_findings == 0
    assert status.current_phase == "requirements"


def test_status_service_never_mutates_state():
    class _GuardRunStore:
        def load(self):
            return None

        def exists(self):
            return False

        def save(self, run):
            raise AssertionError("save must not be called")

    class _GuardFindingsStore:
        def open_count(self, phase, iteration):
            raise AssertionError("open_count must not be called")

        def ingest(self, findings):
            raise AssertionError("ingest must not be called")

        def supersede_prior(self, phase, current_iteration):
            raise AssertionError("supersede_prior must not be called")

    service = StatusService(_GuardRunStore(), _GuardFindingsStore())

    assert service.get_status() == RunStatus(
        mode=None,
        current_phase=None,
        iteration=None,
        open_findings=0,
        last_gate=None,
    )


# --- Phase details (FR-T3) ----------------------------------------------------


def test_no_run_returns_empty_phase_details():
    service = StatusService(_IdleRunStore(), _IdleFindingsStore())

    assert service.get_phase_details() == []


def test_active_run_returns_phase_details():
    gate = GateResult(
        passed=True, errored=False, hook="pre-commit", error_count=0, timed_out=False
    )
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements", "design"],
        current_phase="design",
        iteration=1,
        mode=RunMode.RUNNING,
        phases=[
            PhaseRecord(
                name="requirements",
                author="author-agent",
                reviewer="review-agent",
                status=PhaseStatus.COMPLETE,
                iteration=2,
                last_gate=gate,
                last_reviewed_cycle=2,
            ),
            PhaseRecord(
                name="design",
                author="author-agent",
                reviewer=None,
                status=PhaseStatus.HALTED,
                iteration=1,
                last_gate=None,
                last_reviewed_cycle=None,
                halted_from=PhaseStatus.GATING,
            ),
        ],
    )
    service = StatusService(_ActiveRunStore(run), _IdleFindingsStore())

    assert service.get_phase_details() == [
        PhaseDetail(
            name="requirements",
            author="author-agent",
            reviewer="review-agent",
            status="complete",
            iteration=2,
            last_gate=gate,
            halted_from=None,
        ),
        PhaseDetail(
            name="design",
            author="author-agent",
            reviewer=None,
            status="halted",
            iteration=1,
            last_gate=None,
            halted_from="gating",
        ),
    ]


def test_phase_details_never_mutates_state():
    service = StatusService(_IdleRunStore(), _IdleFindingsStore())

    assert service.get_phase_details() == []


# --- Findings (FR-T4) ----------------------------------------------------------


class _OpenFindingsStore:
    def __init__(self, findings):
        self.findings = findings
        self.calls = []

    def open_count(self, phase, iteration):  # pragma: no cover - unused here
        raise AssertionError("open_count must not be called by get_findings")

    def list_open(self, phase, iteration):
        self.calls.append((phase, iteration))
        return self.findings

    def ingest(self, findings):  # pragma: no cover - defensive
        raise AssertionError("ingest must not be called")

    def supersede_prior(self, phase, current_iteration):  # pragma: no cover
        raise AssertionError("supersede_prior must not be called")


def test_no_run_returns_empty_findings():
    service = StatusService(_IdleRunStore(), _IdleFindingsStore())

    assert service.get_findings() == []


def test_active_run_returns_open_findings():
    gate = GateResult(
        passed=True, errored=False, hook="pre-commit", error_count=0, timed_out=False
    )
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=2,
        mode=RunMode.RUNNING,
        phases=[
            PhaseRecord(
                name="requirements",
                author="author-agent",
                reviewer="review-agent",
                iteration=2,
                last_gate=gate,
                last_reviewed_cycle=2,
            )
        ],
    )
    finding = Finding(
        id="FND-0001",
        phase="requirements",
        iteration=2,
        source=FindingSource.SEMANTIC,
        code="FND-0001",
        severity=Severity.ERROR,
        artifact="docs/spec/foo.md",
        message="Missing acceptance criteria",
        status=FindingStatus.OPEN,
        created_by="review-agent",
    )
    findings_store = _OpenFindingsStore([finding])
    service = StatusService(_ActiveRunStore(run), findings_store)

    assert service.get_findings() == [
        FindingSummary(
            id="FND-0001",
            severity="error",
            artifact="docs/spec/foo.md",
            message="Missing acceptance criteria",
            status="open",
        )
    ]
    assert findings_store.calls == [("requirements", 2)]


def test_findings_without_review_returns_empty_without_querying_store():
    run = Run(
        run_id="run-1",
        branch="agent/run-1",
        chain=["requirements"],
        current_phase="requirements",
        iteration=1,
        mode=RunMode.RUNNING,
        phases=[
            PhaseRecord(
                name="requirements",
                author="author-agent",
                reviewer=None,
                iteration=1,
                last_gate=None,
                last_reviewed_cycle=None,
            )
        ],
    )

    class _GuardFindingsStore:
        def list_open(self, phase, iteration):
            raise AssertionError("list_open must not be called when no review ran")

    service = StatusService(_ActiveRunStore(run), _GuardFindingsStore())

    assert service.get_findings() == []


def test_findings_service_never_mutates_state():
    service = StatusService(_IdleRunStore(), _IdleFindingsStore())

    assert service.get_findings() == []


# --- Log (FR-T5) -----------------------------------------------------------------


class _StubLogReader:
    def __init__(self, records):
        self.records = records

    def read_entries(self):
        return self.records


def _invocation(**overrides) -> AgentInvocation:
    data = {
        "agent": "copilot",
        "role": AgentRole.AUTHOR,
        "adapter": "copilot",
        "model": None,
        "exit_code": 0,
        "duration_ms": 123,
        "timed_out": False,
        "auth_error": False,
        "config_error": False,
    }
    data.update(overrides)
    return AgentInvocation(**data)


def test_log_without_reader_returns_empty():
    service = StatusService(_IdleRunStore(), _IdleFindingsStore())

    assert service.get_log() == []


def test_log_returns_entries_from_reader_in_order():
    gate = GateResult(
        passed=True, errored=False, hook="pre-commit", error_count=0, timed_out=False
    )
    records = [
        LogRecord(invocation=_invocation(agent="one", model="gpt-5"), gate=gate),
        LogRecord(
            invocation=_invocation(agent="two", role=AgentRole.REVIEWER), gate=None
        ),
    ]
    service = StatusService(
        _IdleRunStore(), _IdleFindingsStore(), _StubLogReader(records)
    )

    assert service.get_log() == [
        LogEntry(
            agent="one",
            role="author",
            model="gpt-5",
            exit_code=0,
            duration_ms=123,
            gate=gate,
        ),
        LogEntry(
            agent="two",
            role="reviewer",
            model=None,
            exit_code=0,
            duration_ms=123,
            gate=None,
        ),
    ]


def test_log_service_never_mutates_state():
    service = StatusService(_IdleRunStore(), _IdleFindingsStore())

    assert service.get_log() == []
