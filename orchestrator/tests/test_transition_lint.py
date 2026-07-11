"""Tests for transition-lint — the playbook phase-ordering gate.

Each test builds a marker (and, where relevant, a staged-file list) in tmp_path
and runs check_transitions() directly against the real greenfield FSM. Proves
the smallest-viable slice from the playbook-harness proposal: architecture
artifacts cannot be staged while the marker is still at the spec gate.
"""

from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "transition-lint"
_loader = SourceFileLoader("transition_lint", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("transition_lint", _loader)
transition_lint = importlib.util.module_from_spec(_spec)
sys.modules["transition_lint"] = transition_lint
_loader.exec_module(transition_lint)

check_transitions = transition_lint.check_transitions

PLAYBOOKS_DIR = _ROOT / "factory" / "playbooks"


def _marker(tmp_path: Path, state: str) -> Path:
    p = tmp_path / "playbook-state.yml"
    p.write_text(
        f"playbook: greenfield-development\nstate: {state}\n", encoding="utf-8"
    )
    return p


def _errors(findings):
    return [f for f in findings if f.severity == "error"]


# --- Smallest-viable slice ----------------------------------------------------


class TestSpecGateBlocksArchitecture:
    def test_architecture_blocked_at_spec_gate(self, tmp_path: Path):
        marker = _marker(tmp_path, "PHASE_1_GATE")
        findings = check_transitions(["docs/architecture.dsl"], marker, PLAYBOOKS_DIR)
        errs = _errors(findings)
        assert len(errs) == 1
        assert errs[0].code == "TL-ORDER"
        assert errs[0].artifact == "docs/architecture.dsl"
        assert "PHASE_2_ARCHITECTURE" in errs[0].message

    def test_architecture_allowed_once_marker_at_architecture(self, tmp_path: Path):
        marker = _marker(tmp_path, "PHASE_2_ARCHITECTURE")
        findings = check_transitions(["docs/architecture.dsl"], marker, PLAYBOOKS_DIR)
        assert _errors(findings) == [], [f.line() for f in findings]


# --- Ungoverned / current-state files -----------------------------------------


class TestAllowed:
    def test_ungoverned_file_ignored(self, tmp_path: Path):
        marker = _marker(tmp_path, "PHASE_1_GATE")
        findings = check_transitions(["README.md"], marker, PLAYBOOKS_DIR)
        assert _errors(findings) == []

    def test_current_state_output_allowed(self, tmp_path: Path):
        marker = _marker(tmp_path, "PHASE_1_GATE")
        findings = check_transitions(
            ["docs/findings/SPEC-0001.md"], marker, PLAYBOOKS_DIR
        )
        assert _errors(findings) == []


# --- Marker handling ----------------------------------------------------------


class TestMarker:
    def test_absent_marker_is_noop(self, tmp_path: Path):
        findings = check_transitions(
            ["docs/architecture.dsl"], tmp_path / "nope.yml", PLAYBOOKS_DIR
        )
        assert _errors(findings) == []
        assert any(f.code == "TL-NOMARKER" for f in findings)

    def test_marker_missing_fields_errors(self, tmp_path: Path):
        p = tmp_path / "m.yml"
        p.write_text("playbook: greenfield-development\n", encoding="utf-8")
        findings = check_transitions(["docs/architecture.dsl"], p, PLAYBOOKS_DIR)
        assert any(f.code == "TL-MARKER" for f in _errors(findings))

    def test_unknown_playbook_errors(self, tmp_path: Path):
        p = tmp_path / "m.yml"
        p.write_text("playbook: nope\nstate: INIT\n", encoding="utf-8")
        findings = check_transitions([], p, PLAYBOOKS_DIR)
        assert any(f.code == "TL-NOFSM" for f in _errors(findings))
