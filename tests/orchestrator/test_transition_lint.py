"""Tests for factory/scripts/transition-lint (playbook-structured-harness PoC).

transition-lint is the pre-commit phase-ordering gate. It reads the run-state
marker, maps staged files to their owning FSM state via outputs: globs, and
blocks any file that belongs to a state other than the current one.

The end-to-end scenario from the harness proposal: architecture artifacts are
blocked while the run is in PHASE_1_GATE, and unblocked once the marker
advances to PHASE_2_ARCHITECTURE.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_TRANSITION_LINT = _ROOT / "factory" / "scripts" / "transition-lint"

sys.path.insert(0, str(_TRANSITION_LINT.parent))

_loader = importlib.machinery.SourceFileLoader("transition_lint", str(_TRANSITION_LINT))
_spec = importlib.util.spec_from_file_location(
    "transition_lint", str(_TRANSITION_LINT), loader=_loader
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["transition_lint"] = _mod
_spec.loader.exec_module(_mod)

check_transitions = _mod.check_transitions
parse_fsm = _mod.parse_fsm
state_outputs = _mod.state_outputs
states_for_file = _mod.states_for_file

_FSM_PATH = _ROOT / "factory" / "playbooks" / "greenfield-development.fsm.yml"
_FSM = parse_fsm(_FSM_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_marker(path: Path, *, playbook: str, state: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"playbook: {playbook}\nstate: {state}\n", encoding="utf-8")


def _setup_playbooks(tmp: Path) -> Path:
    """Symlink the real FSM into a tmp playbooks dir."""
    pb = tmp / "factory" / "playbooks"
    pb.mkdir(parents=True)
    (pb / "greenfield-development.fsm.yml").symlink_to(_FSM_PATH)
    return pb


# ---------------------------------------------------------------------------
# Unit: glob ownership
# ---------------------------------------------------------------------------


class TestGlobOwnership:
    """state_outputs and states_for_file resolve ownership correctly."""

    _OUTPUTS = state_outputs(_FSM)

    def test_spec_file_owned_by_phase_1_requirements(self):
        owners = states_for_file("docs/spec/prd.md", self._OUTPUTS)
        assert "PHASE_1_REQUIREMENTS" in owners

    def test_use_case_wildcard(self):
        owners = states_for_file(
            "docs/spec/use_cases/UC-01-something.md", self._OUTPUTS
        )
        assert "PHASE_1_REQUIREMENTS" in owners

    def test_adr_owned_by_phase_2_architecture(self):
        owners = states_for_file("docs/adr/0001-some-decision.md", self._OUTPUTS)
        assert "PHASE_2_ARCHITECTURE" in owners

    def test_finding_owned_by_gate(self):
        owners = states_for_file("docs/findings/SPEC-001.md", self._OUTPUTS)
        assert "PHASE_1_GATE" in owners

    def test_backlog_owned_by_phase_3(self):
        owners = states_for_file("backlog/ST-0001.md", self._OUTPUTS)
        assert "PHASE_3_PLANNING" in owners

    def test_source_code_owned_by_implementation(self):
        owners = states_for_file("src/main.py", self._OUTPUTS)
        assert "PHASE_4_IMPLEMENTATION" in owners

    def test_ungoverned_file_has_no_owner(self):
        owners = states_for_file("README.md", self._OUTPUTS)
        assert owners == []


# ---------------------------------------------------------------------------
# Unit: check_transitions core
# ---------------------------------------------------------------------------


class TestCheckTransitionsCore:
    def test_no_marker_is_noop(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        pb = _setup_playbooks(tmp_path)
        findings = check_transitions(["docs/adr/0001.md"], marker, pb)
        assert len(findings) == 1
        assert findings[0].code == "TL-NOMARKER"
        assert findings[0].severity == "info"

    def test_marker_missing_fields(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        marker.parent.mkdir(parents=True)
        marker.write_text("playbook: greenfield-development\n")
        pb = _setup_playbooks(tmp_path)
        findings = check_transitions(["x.py"], marker, pb)
        assert any(f.code == "TL-MARKER" for f in findings)

    def test_unknown_state_is_error(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(marker, playbook="greenfield-development", state="BOGUS")
        pb = _setup_playbooks(tmp_path)
        findings = check_transitions(["x.py"], marker, pb)
        assert any(f.code == "TL-STATE" for f in findings)

    def test_missing_fsm_is_error(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(marker, playbook="nonexistent", state="INIT")
        pb = tmp_path / "factory" / "playbooks"
        pb.mkdir(parents=True)
        findings = check_transitions(["x.py"], marker, pb)
        assert any(f.code == "TL-NOFSM" for f in findings)

    def test_current_state_file_passes(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(
            marker, playbook="greenfield-development", state="PHASE_1_REQUIREMENTS"
        )
        pb = _setup_playbooks(tmp_path)
        findings = check_transitions(["docs/spec/prd.md"], marker, pb)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []

    def test_ungoverned_file_passes(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(
            marker, playbook="greenfield-development", state="PHASE_1_REQUIREMENTS"
        )
        pb = _setup_playbooks(tmp_path)
        findings = check_transitions(["README.md"], marker, pb)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []

    def test_out_of_phase_file_blocked(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(
            marker, playbook="greenfield-development", state="PHASE_1_REQUIREMENTS"
        )
        pb = _setup_playbooks(tmp_path)
        findings = check_transitions(["docs/adr/0001.md"], marker, pb)
        errors = [f for f in findings if f.severity == "error"]
        assert len(errors) == 1
        assert errors[0].code == "TL-ORDER"


# ---------------------------------------------------------------------------
# End-to-end: architecture blocked while in PHASE_1_GATE
# ---------------------------------------------------------------------------


class TestEndToEndArchitectureBlocked:
    """The proposal's one rule: architecture artifacts cannot be committed while
    the spec gate is unpassed."""

    ARCH_FILES = [
        "docs/adr/0001-some-decision.md",
        "docs/arc42/architecture.dsl",
        "docs/assets/images/diagram.png",
    ]

    def test_architecture_files_blocked_in_phase_1_gate(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(marker, playbook="greenfield-development", state="PHASE_1_GATE")
        pb = _setup_playbooks(tmp_path)
        findings = check_transitions(self.ARCH_FILES, marker, pb)
        errors = [f for f in findings if f.severity == "error"]
        assert len(errors) == len(self.ARCH_FILES)
        assert all(e.code == "TL-ORDER" for e in errors)

    def test_spec_review_outputs_pass_in_phase_1_gate(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(marker, playbook="greenfield-development", state="PHASE_1_GATE")
        pb = _setup_playbooks(tmp_path)
        gate_files = [
            "docs/reviews/spec-review-2026-01-01.md",
            "docs/findings/SPEC-001.md",
        ]
        findings = check_transitions(gate_files, marker, pb)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []

    def test_architecture_files_pass_in_phase_2(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(
            marker, playbook="greenfield-development", state="PHASE_2_ARCHITECTURE"
        )
        pb = _setup_playbooks(tmp_path)
        findings = check_transitions(self.ARCH_FILES, marker, pb)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []

    def test_mixed_stage_partially_blocked(self, tmp_path):
        """A commit staging both gate outputs and architecture files: only the
        architecture files are blocked."""
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(marker, playbook="greenfield-development", state="PHASE_1_GATE")
        pb = _setup_playbooks(tmp_path)
        mixed = ["docs/findings/SPEC-001.md", "docs/adr/0001.md"]
        findings = check_transitions(mixed, marker, pb)
        errors = [f for f in findings if f.severity == "error"]
        assert len(errors) == 1
        assert errors[0].artifact == "docs/adr/0001.md"


# ---------------------------------------------------------------------------
# CLI exit code contract
# ---------------------------------------------------------------------------


class TestMainExitCode:
    def test_clean_returns_zero(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(
            marker, playbook="greenfield-development", state="PHASE_1_REQUIREMENTS"
        )
        pb = _setup_playbooks(tmp_path)
        code = _mod.main(
            [
                "--repo-root",
                str(tmp_path),
                "--marker",
                str(marker),
                "--playbooks-dir",
                str(pb),
            ]
        )
        assert code == 0

    def test_report_only_always_returns_zero(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        _write_marker(marker, playbook="greenfield-development", state="PHASE_1_GATE")
        pb = _setup_playbooks(tmp_path)
        code = _mod.main(
            [
                "--repo-root",
                str(tmp_path),
                "--marker",
                str(marker),
                "--playbooks-dir",
                str(pb),
                "--report-only",
            ]
        )
        assert code == 0
