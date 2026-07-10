"""Tests for the append-only invocation log adapter."""

from __future__ import annotations

import json
from pathlib import Path

from orchestrator.adapters.invocation_log import FileInvocationLog
from orchestrator.entities import AgentInvocation, AgentRole, GateResult
from orchestrator.ports import LogRecord


def _record(**overrides) -> AgentInvocation:
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


def test_first_write_creates_file(tmp_path: Path):
    log = FileInvocationLog(tmp_path / ".orchestrator")
    assert log.log_file.exists()

    log.log(_record())

    assert log.log_file.exists()
    assert log.log_file.read_text(encoding="utf-8").strip() != ""


def test_multiple_writes_append(tmp_path: Path):
    log = FileInvocationLog(tmp_path / ".orchestrator")

    log.log(_record(agent="one"))
    log.log(_record(agent="two"))

    lines = log.log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2


def test_each_line_is_valid_json_with_expected_fields(tmp_path: Path):
    log = FileInvocationLog(tmp_path / ".orchestrator")

    log.log(_record(model="gpt-5"))

    line = log.log_file.read_text(encoding="utf-8").splitlines()[0]
    data = json.loads(line)

    assert data == {
        "agent": "copilot",
        "role": "author",
        "adapter": "copilot",
        "model": "gpt-5",
        "exit_code": 0,
        "duration_ms": 123,
        "timed_out": False,
        "auth_error": False,
        "config_error": False,
    }


def test_gate_fields_included_when_gate_provided(tmp_path: Path):
    log = FileInvocationLog(tmp_path / ".orchestrator")
    gate = GateResult(passed=True, errored=False, hook="pre-commit", error_count=0)

    log.log(_record(), gate=gate)

    data = json.loads(log.log_file.read_text(encoding="utf-8").splitlines()[0])
    assert data["passed"] is True
    assert data["errored"] is False
    assert data["hook"] == "pre-commit"
    assert data["error_count"] == 0
    assert data["gate_timed_out"] is False


def test_gate_fields_absent_when_gate_is_none(tmp_path: Path):
    log = FileInvocationLog(tmp_path / ".orchestrator")

    log.log(_record())

    data = json.loads(log.log_file.read_text(encoding="utf-8").splitlines()[0])
    assert "passed" not in data
    assert "errored" not in data
    assert "hook" not in data
    assert "error_count" not in data
    assert "gate_timed_out" not in data


# --- read_entries (FR-T5 read API) ---------------------------------------------


def test_read_entries_on_empty_log_returns_empty_list(tmp_path: Path):
    log = FileInvocationLog(tmp_path / ".orchestrator")

    assert log.read_entries() == []


def test_read_entries_round_trips_a_write_without_gate(tmp_path: Path):
    log = FileInvocationLog(tmp_path / ".orchestrator")
    record = _record(agent="copilot", model="gpt-5")

    log.log(record)

    assert log.read_entries() == [LogRecord(invocation=record, gate=None)]


def test_read_entries_round_trips_a_write_with_gate(tmp_path: Path):
    log = FileInvocationLog(tmp_path / ".orchestrator")
    record = _record(agent="copilot")
    gate = GateResult(passed=False, errored=True, hook="pre-commit", error_count=2)

    log.log(record, gate=gate)

    [entry] = log.read_entries()
    assert entry.invocation == record
    assert entry.gate == GateResult(
        passed=False,
        errored=True,
        hook="pre-commit",
        error_count=2,
        timed_out=False,
    )


def test_read_entries_preserves_append_order(tmp_path: Path):
    log = FileInvocationLog(tmp_path / ".orchestrator")

    log.log(_record(agent="one"))
    log.log(_record(agent="two"))
    log.log(_record(agent="three"))

    agents = [entry.invocation.agent for entry in log.read_entries()]
    assert agents == ["one", "two", "three"]
