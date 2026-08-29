"""Tests for factory/scripts/phase advance and retry (playbook-structured-harness PoC).

phase advance reads the run-state marker, finds the forward transition, checks
entry_conditions, and refuses if any is unmet — closing the hand-advance
loophole. phase retry increments the iteration counter and refuses at the cap.

The end-to-end scenario from the harness proposal: the gate refuses to advance
past PHASE_1_GATE while a SPEC-* finding is open, and succeeds once the finding
is resolved.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PHASE = _ROOT / "factory" / "scripts" / "phase"

_loader = importlib.machinery.SourceFileLoader("phase", str(_PHASE))
_spec = importlib.util.spec_from_file_location("phase", str(_PHASE), loader=_loader)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["phase"] = _mod
_spec.loader.exec_module(_mod)

advance = _mod.advance
advance_dry_run = _mod.advance_dry_run
retry = _mod.retry
parse_marker = _mod.parse_marker
render_marker = _mod.render_marker
evaluate_condition = _mod.evaluate_condition

_FSM_PATH = _ROOT / "factory" / "playbooks" / "greenfield-development.fsm.yml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_marker(path: Path, *, playbook: str, state: str, **extra) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = {"playbook": playbook, "state": state}
    fields.update(extra)
    lines = [f"{k}: {v}" for k, v in fields.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _setup_repo(tmp: Path) -> tuple[Path, Path, Path]:
    """Return (marker, playbooks_dir, repo_root) wired to the real FSM."""
    marker = tmp / ".current-work" / "playbook-state.yml"
    pb = tmp / "factory" / "playbooks"
    pb.mkdir(parents=True)
    (pb / "greenfield-development.fsm.yml").symlink_to(_FSM_PATH)
    # Satisfy project_initialized gate
    (tmp / ".git").mkdir()
    (tmp / ".git" / "config").write_text("[core]\n")
    return marker, pb, tmp


def _open_finding(repo: Path, name: str = "SPEC-001.md") -> Path:
    d = repo / "docs" / "findings"
    d.mkdir(parents=True, exist_ok=True)
    f = d / name
    f.write_text("---\nstatus: open\n---\nSome finding.\n", encoding="utf-8")
    return f


def _close_finding(path: Path) -> None:
    path.write_text("---\nstatus: resolved\n---\nFixed.\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Bootstrap: advance from no marker
# ---------------------------------------------------------------------------


class TestBootstrap:
    def test_bootstrap_lands_on_init(self, tmp_path):
        marker, pb, repo = _setup_repo(tmp_path)
        code, msg = advance(repo, marker, pb)
        assert code == 0
        assert "INIT" in msg
        m = parse_marker(marker.read_text(encoding="utf-8"))
        # INIT's forward transition goes to PHASE_1_REQUIREMENTS
        assert m["state"] == "PHASE_1_REQUIREMENTS"

    def test_bootstrap_refuses_without_fsm(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        pb = tmp_path / "empty"
        pb.mkdir()
        code, _msg = advance(tmp_path, marker, pb)
        assert code == 1


# ---------------------------------------------------------------------------
# Advance: entry condition enforcement
# ---------------------------------------------------------------------------


class TestAdvanceConditions:
    def test_advance_refuses_when_entry_conditions_unmet(self, tmp_path):
        """PHASE_2_ARCHITECTURE requires no_open_spec_findings — refuse if one
        is open."""
        marker, pb, repo = _setup_repo(tmp_path)
        _write_marker(marker, playbook="greenfield-development", state="PHASE_1_GATE")
        # Satisfy spec_exists
        spec = repo / "docs" / "spec"
        spec.mkdir(parents=True)
        (spec / "prd.md").write_text("prd")
        (spec / "actor-goal-list.md").write_text("actors")
        uc = spec / "use_cases"
        uc.mkdir()
        (uc / "UC-01.md").write_text("uc")

        _open_finding(repo, "SPEC-001.md")

        code, msg = advance(repo, marker, pb)
        assert code == 1
        assert "no_open_spec_findings" in msg

    def test_advance_succeeds_when_conditions_met(self, tmp_path):
        """Once the finding is resolved, the gate passes."""
        marker, pb, repo = _setup_repo(tmp_path)
        _write_marker(marker, playbook="greenfield-development", state="PHASE_1_GATE")
        spec = repo / "docs" / "spec"
        spec.mkdir(parents=True)
        (spec / "prd.md").write_text("prd")
        (spec / "actor-goal-list.md").write_text("actors")
        uc = spec / "use_cases"
        uc.mkdir()
        (uc / "UC-01.md").write_text("uc")

        f = _open_finding(repo, "SPEC-001.md")
        _close_finding(f)

        code, _msg = advance(repo, marker, pb)
        assert code == 0
        m = parse_marker(marker.read_text(encoding="utf-8"))
        assert m["state"] == "PHASE_2_ARCHITECTURE"

    def test_advance_writes_extended_marker(self, tmp_path):
        marker, pb, repo = _setup_repo(tmp_path)
        _write_marker(marker, playbook="greenfield-development", state="PHASE_1_GATE")
        spec = repo / "docs" / "spec"
        spec.mkdir(parents=True)
        (spec / "prd.md").write_text("prd")
        (spec / "actor-goal-list.md").write_text("actors")
        uc = spec / "use_cases"
        uc.mkdir()
        (uc / "UC-01.md").write_text("uc")

        code, _ = advance(repo, marker, pb)
        assert code == 0
        m = parse_marker(marker.read_text(encoding="utf-8"))
        assert m["playbook"] == "greenfield-development"
        assert m["state"] == "PHASE_2_ARCHITECTURE"
        assert m["result"] == "pass"
        assert m["iteration"] == "1"
        assert "recorded_at" in m

    def test_dry_run_does_not_write_marker(self, tmp_path):
        marker, pb, repo = _setup_repo(tmp_path)
        _write_marker(marker, playbook="greenfield-development", state="PHASE_1_GATE")
        spec = repo / "docs" / "spec"
        spec.mkdir(parents=True)
        (spec / "prd.md").write_text("prd")
        (spec / "actor-goal-list.md").write_text("actors")
        uc = spec / "use_cases"
        uc.mkdir()
        (uc / "UC-01.md").write_text("uc")

        code, msg = advance_dry_run(repo, marker, pb)
        assert code == 0
        assert "dry-run" in msg
        m = parse_marker(marker.read_text(encoding="utf-8"))
        assert m["state"] == "PHASE_1_GATE"


# ---------------------------------------------------------------------------
# End-to-end: finding blocks advance, resolved finding unblocks
# ---------------------------------------------------------------------------


class TestEndToEndFindingGate:
    """The proposal's one rule proven end to end: architecture artifacts are
    blocked while a SPEC-* finding is open, the gate refuses to advance, and
    both lift once the finding is resolved."""

    def _setup_at_phase_1_gate(self, tmp_path):
        marker, pb, repo = _setup_repo(tmp_path)
        _write_marker(marker, playbook="greenfield-development", state="PHASE_1_GATE")
        spec = repo / "docs" / "spec"
        spec.mkdir(parents=True)
        (spec / "prd.md").write_text("prd")
        (spec / "actor-goal-list.md").write_text("actors")
        uc = spec / "use_cases"
        uc.mkdir()
        (uc / "UC-01.md").write_text("uc")
        return marker, pb, repo

    def test_open_finding_blocks_advance(self, tmp_path):
        marker, pb, repo = self._setup_at_phase_1_gate(tmp_path)
        _open_finding(repo, "SPEC-001.md")

        code, msg = advance(repo, marker, pb)
        assert code == 1
        assert "unmet" in msg

    def test_resolved_finding_unblocks_advance(self, tmp_path):
        marker, pb, repo = self._setup_at_phase_1_gate(tmp_path)
        f = _open_finding(repo, "SPEC-001.md")
        _close_finding(f)

        code, _msg = advance(repo, marker, pb)
        assert code == 0
        m = parse_marker(marker.read_text(encoding="utf-8"))
        assert m["state"] == "PHASE_2_ARCHITECTURE"

    def test_multiple_findings_all_must_close(self, tmp_path):
        marker, pb, repo = self._setup_at_phase_1_gate(tmp_path)
        f1 = _open_finding(repo, "SPEC-001.md")
        f2 = _open_finding(repo, "SPEC-002.md")
        _close_finding(f1)

        code, _ = advance(repo, marker, pb)
        assert code == 1

        _close_finding(f2)
        code, _ = advance(repo, marker, pb)
        assert code == 0


# ---------------------------------------------------------------------------
# Retry: iteration cap
# ---------------------------------------------------------------------------


class TestRetry:
    def test_retry_increments_iteration(self, tmp_path):
        marker, pb, repo = _setup_repo(tmp_path)
        _write_marker(
            marker,
            playbook="greenfield-development",
            state="PHASE_1_GATE",
            iteration="1",
        )
        code, _msg = retry(repo, marker, pb)
        assert code == 0
        m = parse_marker(marker.read_text(encoding="utf-8"))
        assert m["iteration"] == "2"

    def test_retry_refuses_at_cap(self, tmp_path):
        marker, pb, repo = _setup_repo(tmp_path)
        # PHASE_1_REQUIREMENTS has a halt_conditions cap of 5 in the FSM.
        # PHASE_1_GATE's else loops back to PHASE_1_REQUIREMENTS, so the
        # lookup resolves against PHASE_1_REQUIREMENTS's cap.
        _write_marker(
            marker,
            playbook="greenfield-development",
            state="PHASE_1_GATE",
            iteration="5",
        )
        code, msg = retry(repo, marker, pb)
        assert code == 2
        assert "cap" in msg.lower() or "refusing" in msg.lower()

    def test_retry_refuses_without_marker(self, tmp_path):
        marker = tmp_path / ".current-work" / "playbook-state.yml"
        pb = tmp_path / "pb"
        pb.mkdir()
        code, _ = retry(tmp_path, marker, pb)
        assert code == 1

    def test_retry_default_cap_applies(self, tmp_path):
        """States without an explicit halt_conditions entry use the default."""
        marker, pb, repo = _setup_repo(tmp_path)
        # PHASE_3_PLANNING has no halt_conditions entry. Its loop back from
        # PHASE_3_PLANNING -> PHASE_3_PLANNING means the lookup state is
        # PHASE_3_PLANNING itself. Default cap = 3 in this test.
        _write_marker(
            marker,
            playbook="greenfield-development",
            state="PHASE_3_PLANNING",
            iteration="3",
        )
        code, _msg = retry(repo, marker, pb, default_limit=3)
        assert code == 2


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


class TestPhaseCLI:
    def test_advance_cli(self, tmp_path):
        marker, pb, repo = _setup_repo(tmp_path)
        code = _mod.main(
            [
                "advance",
                "--repo-root",
                str(repo),
                "--marker",
                str(marker),
                "--playbooks-dir",
                str(pb),
            ]
        )
        assert code == 0

    def test_retry_cli(self, tmp_path):
        marker, pb, repo = _setup_repo(tmp_path)
        _write_marker(
            marker,
            playbook="greenfield-development",
            state="PHASE_1_GATE",
            iteration="1",
        )
        code = _mod.main(
            [
                "retry",
                "--repo-root",
                str(repo),
                "--marker",
                str(marker),
                "--playbooks-dir",
                str(pb),
            ]
        )
        assert code == 0


# ---------------------------------------------------------------------------
# Charter resolution in evaluate_condition
# ---------------------------------------------------------------------------


class TestCharterResolution:
    def test_charter_resolves_test_command(self, tmp_path):
        charter = tmp_path / "docs" / "charter" / "testing.yaml"
        charter.parent.mkdir(parents=True)
        charter.write_text("test_command: echo ok\n")
        cond = {
            "type": "script_exit_zero",
            "script": "charter:test_command",
            "charter_file": "docs/charter/testing.yaml",
        }
        ok, msg = evaluate_condition(tmp_path, cond)
        assert ok, msg
        assert "passed" in msg

    def test_charter_blocks_when_file_absent(self, tmp_path):
        cond = {
            "type": "script_exit_zero",
            "script": "charter:test_command",
            "charter_file": "docs/charter/testing.yaml",
        }
        ok, msg = evaluate_condition(tmp_path, cond)
        assert not ok
        assert "not found" in msg

    def test_charter_blocks_when_field_missing(self, tmp_path):
        charter = tmp_path / "docs" / "charter" / "testing.yaml"
        charter.parent.mkdir(parents=True)
        charter.write_text("other_field: something\n")
        cond = {
            "type": "script_exit_zero",
            "script": "charter:test_command",
            "charter_file": "docs/charter/testing.yaml",
        }
        ok, msg = evaluate_condition(tmp_path, cond)
        assert not ok
        assert "missing" in msg

    def test_charter_blocks_when_no_charter_file_specified(self, tmp_path):
        cond = {
            "type": "script_exit_zero",
            "script": "charter:test_command",
        }
        ok, msg = evaluate_condition(tmp_path, cond)
        assert not ok
        assert "no charter_file" in msg

    def test_charter_handles_quoted_values(self, tmp_path):
        charter = tmp_path / "docs" / "charter" / "testing.yaml"
        charter.parent.mkdir(parents=True)
        charter.write_text('test_command: "echo ok"\n')
        cond = {
            "type": "script_exit_zero",
            "script": "charter:test_command",
            "charter_file": "docs/charter/testing.yaml",
        }
        ok, msg = evaluate_condition(tmp_path, cond)
        assert ok, msg
