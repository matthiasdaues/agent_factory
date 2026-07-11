"""Tests for `phase retry` — the configurable iteration cap.

Drives retry() against the real greenfield FSM, which already declares
halt_conditions (type: max_iterations, limit: 5) for the three review-loop
states — previously-dead config this command makes load-bearing. Also
covers the default-limit fallback for playbooks/states that declare none.
"""

from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "phase"
_loader = SourceFileLoader("phase", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("phase", _loader)
phase = importlib.util.module_from_spec(_spec)
sys.modules["phase"] = phase
_loader.exec_module(phase)

retry = phase.retry
parse_marker = phase.parse_marker

PLAYBOOKS_DIR = _ROOT / "factory" / "playbooks"


def _marker(tmp_path: Path, state: str, iteration: int = 1) -> Path:
    p = tmp_path / ".agent-factory" / "playbook-state.yml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        f"playbook: greenfield-development\nstate: {state}\niteration: {iteration}\n",
        encoding="utf-8",
    )
    return p


class TestRetryAgainstRealFSMLimit:
    def test_first_retry_at_gate_succeeds_and_records_loop_back_target(self, tmp_path):
        marker = _marker(tmp_path, "PHASE_1_GATE", iteration=1)
        code, msg = retry(tmp_path, marker, PLAYBOOKS_DIR)
        assert code == 0, msg
        assert "PHASE_1_REQUIREMENTS" in msg
        assert "2/5" in msg
        assert parse_marker(marker.read_text())["iteration"] == "2"

    def test_refuses_once_declared_limit_of_5_exceeded(self, tmp_path):
        marker = _marker(tmp_path, "PHASE_1_GATE", iteration=1)
        # Attempts 2, 3, 4, 5 succeed (limit is 5); attempt 6 must refuse.
        for _ in range(4):
            code, msg = retry(tmp_path, marker, PLAYBOOKS_DIR)
            assert code == 0, msg

        code, msg = retry(tmp_path, marker, PLAYBOOKS_DIR)
        assert code != 0
        assert "cap of 5" in msg
        assert "Spec review looped 5 times" in msg

    def test_refusal_leaves_marker_iteration_unchanged(self, tmp_path):
        marker = _marker(tmp_path, "PHASE_1_GATE", iteration=5)
        code, _ = retry(tmp_path, marker, PLAYBOOKS_DIR)
        assert code != 0
        assert parse_marker(marker.read_text())["iteration"] == "5"

    def test_architecture_review_loop_uses_its_own_declared_limit(self, tmp_path):
        marker = _marker(tmp_path, "PHASE_2_GATE", iteration=1)
        code, msg = retry(tmp_path, marker, PLAYBOOKS_DIR)
        assert code == 0, msg
        assert "PHASE_2_ARCHITECTURE" in msg


class TestRetryDefaultLimit:
    def test_state_with_no_halt_condition_uses_default_limit(self, tmp_path):
        # PHASE_3_APPROVAL has no else-branch and no halt_conditions entry
        # of its own — falls back to the configurable default.
        marker = _marker(tmp_path, "PHASE_3_APPROVAL", iteration=1)
        code, msg = retry(tmp_path, marker, PLAYBOOKS_DIR, default_limit=2)
        assert code == 0, msg
        assert "2/2" in msg

        code, msg = retry(tmp_path, marker, PLAYBOOKS_DIR, default_limit=2)
        assert code != 0
        assert "cap of 2" in msg

    def test_default_limit_is_configurable_per_call(self, tmp_path):
        marker = _marker(tmp_path, "PHASE_3_APPROVAL", iteration=1)
        code, msg = retry(tmp_path, marker, PLAYBOOKS_DIR, default_limit=10)
        assert code == 0, msg
        assert "10" in msg


class TestRetryErrors:
    def test_no_marker_refuses(self, tmp_path):
        marker = tmp_path / ".agent-factory" / "playbook-state.yml"
        code, msg = retry(tmp_path, marker, PLAYBOOKS_DIR)
        assert code != 0
        assert "no marker" in msg

    def test_missing_iteration_field_defaults_to_one(self, tmp_path):
        marker = tmp_path / ".agent-factory" / "playbook-state.yml"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            "playbook: greenfield-development\nstate: PHASE_1_GATE\n",
            encoding="utf-8",
        )
        code, msg = retry(tmp_path, marker, PLAYBOOKS_DIR)
        assert code == 0, msg
        assert "2/5" in msg
