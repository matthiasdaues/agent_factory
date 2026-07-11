"""Tests for `phase advance` — the gated marker-advance command.

Builds a realistic greenfield project tree in tmp_path (spec files, findings)
and drives advance() against the real greenfield FSM. Proves the loophole the
harness proposal closes: a failing spec gate cannot be hand-advanced past, and
the recorded timestamp comes from the process clock, not an argument.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "phase"
_loader = SourceFileLoader("phase", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("phase", _loader)
phase = importlib.util.module_from_spec(_spec)
sys.modules["phase"] = phase
_loader.exec_module(phase)

advance = phase.advance
parse_marker = phase.parse_marker

PLAYBOOKS_DIR = _ROOT / "factory" / "playbooks"


def _project(tmp_path: Path, finding_status: str) -> Path:
    """A greenfield tree at the spec gate with one SPEC finding."""
    (tmp_path / "docs" / "spec" / "use_cases").mkdir(parents=True)
    (tmp_path / "docs" / "spec" / "prd.md").write_text("# PRD\n", encoding="utf-8")
    (tmp_path / "docs" / "spec" / "actor-goal-list.md").write_text(
        "# AGL\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "spec" / "use_cases" / "uc-01.md").write_text(
        "# UC-01\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "findings").mkdir(parents=True)
    (tmp_path / "docs" / "findings" / "SPEC-0001.md").write_text(
        f"---\nid: SPEC-0001\nstatus: {finding_status}\n---\n\n# Finding\n",
        encoding="utf-8",
    )
    return tmp_path


def _marker(tmp_path: Path, state: str) -> Path:
    p = tmp_path / ".agent-factory" / "playbook-state.yml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        f"playbook: greenfield-development\nstate: {state}\n", encoding="utf-8"
    )
    return p


class TestGateRefusal:
    def test_refuses_while_spec_finding_open(self, tmp_path: Path):
        _project(tmp_path, finding_status="open")
        marker = _marker(tmp_path, "PHASE_1_GATE")
        code, msg = advance(tmp_path, marker, PLAYBOOKS_DIR)
        assert code != 0
        assert "no_open_spec_findings" in msg
        # marker unchanged
        assert parse_marker(marker.read_text())["state"] == "PHASE_1_GATE"

    def test_refuses_when_spec_files_missing(self, tmp_path: Path):
        # No spec tree at all -> spec_exists also unmet.
        (tmp_path / "docs" / "findings").mkdir(parents=True)
        marker = _marker(tmp_path, "PHASE_1_GATE")
        code, msg = advance(tmp_path, marker, PLAYBOOKS_DIR)
        assert code != 0
        assert "spec_exists" in msg


class TestGatePasses:
    def test_advances_once_finding_resolved(self, tmp_path: Path):
        _project(tmp_path, finding_status="resolved")
        marker = _marker(tmp_path, "PHASE_1_GATE")
        before = datetime.now(timezone.utc)
        code, msg = advance(tmp_path, marker, PLAYBOOKS_DIR)
        after = datetime.now(timezone.utc)
        assert code == 0, msg

        fields = parse_marker(marker.read_text())
        assert fields["state"] == "PHASE_2_ARCHITECTURE"
        assert fields["gate"] == "no_open_spec_findings"
        assert fields["result"] == "pass"
        assert fields["open_findings"] == "0"
        assert fields["next"] == "PHASE_2_GATE"
        assert fields["recorded_by"] == "human"

        # recorded_at is the process clock, not agent-supplied.
        recorded = datetime.strptime(
            fields["recorded_at"], "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc)
        assert before.replace(microsecond=0) <= recorded <= after

    def test_recorded_by_flag(self, tmp_path: Path):
        _project(tmp_path, finding_status="resolved")
        marker = _marker(tmp_path, "PHASE_1_GATE")
        code, _ = advance(
            tmp_path, marker, PLAYBOOKS_DIR, recorded_by="spec-review-agent"
        )
        assert code == 0
        assert parse_marker(marker.read_text())["recorded_by"] == "spec-review-agent"
