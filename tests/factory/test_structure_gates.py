"""Regression tests for the structure gates (ST-0296).

Each test reproduces one finding from the bug-hunt of 2026-10-15 and
fails on the code before the fix.
"""

from __future__ import annotations

from pathlib import Path

from conftest import load_script

sm = load_script("statemachine-lint")


def _write_machine(path: Path, pseudocode: str, mermaid: str) -> Path:
    path.write_text(
        "# Machine\n\n```text\n"
        + pseudocode
        + "```\n\n```mermaid\nstateDiagram-v2\n"
        + mermaid
        + "```\n"
    )
    return path


# ---------------------------------------------------------------------------
# BUG-0052: statemachine-lint misses edges and one documented check
# ---------------------------------------------------------------------------


class TestStatemachineEdgesAndRestoreCheck:
    PSEUDO = "State: A\nOn Go:\n  ChangeState(B)\n\nState: B\n  # terminal\n"

    def test_edge_without_spaces_is_compared(self, tmp_path: Path) -> None:
        """BUG-0052: `B-->A` is an edge the pseudocode lacks."""
        md = _write_machine(
            tmp_path / "sm.md", self.PSEUDO, "    [*]-->A\n    A --> B\n    B-->A\n"
        )
        rep = sm.Report()
        sm._check_file(rep, md)
        trans = [msg for _, code, msg in rep.items if code == "SM-TRANS"]
        assert len(trans) == 1
        assert "B → A in Mermaid but not in pseudocode" in trans[0]
        assert rep.n(sm.ERROR) == 1

    def test_edge_without_spaces_matches_pseudocode(self, tmp_path: Path) -> None:
        """BUG-0052: `A-->B` counts as the edge the pseudocode declares."""
        md = _write_machine(tmp_path / "sm.md", self.PSEUDO, "    A-->B: Go\n")
        rep = sm.Report()
        sm._check_file(rep, md)
        assert rep.items == []

    def test_restore_without_set_halted_from_warns(self, tmp_path: Path) -> None:
        """BUG-0052: SM-RESTORE-OOB fires when RestoreState has no target."""
        pseudo = (
            "State: RUNNING\nOn Halt:\n  ChangeState(HALTED)\n\n"
            "State: HALTED\nOn Resume:\n  RestoreState(halted_from)\n"
        )
        md = _write_machine(tmp_path / "sm.md", pseudo, "    RUNNING --> HALTED\n")
        rep = sm.Report()
        sm._check_file(rep, md)
        codes = [(sev, code) for sev, code, _ in rep.items]
        assert (sm.WARNING, "SM-RESTORE-OOB") in codes

    def test_restore_with_set_halted_from_is_silent(self, tmp_path: Path) -> None:
        """BUG-0052: a RestoreState with a recorded source raises no warning."""
        pseudo = (
            "State: RUNNING\nOn Halt:\n  SetHaltedFrom(RUNNING)\n"
            "  ChangeState(HALTED)\n\n"
            "State: HALTED\nOn Resume:\n  RestoreState(halted_from)\n"
        )
        md = _write_machine(
            tmp_path / "sm.md", pseudo, "    RUNNING --> HALTED\n    HALTED --> RUNNING\n"
        )
        rep = sm.Report()
        sm._check_file(rep, md)
        assert rep.items == []

