"""Regression tests for the structure gates (ST-0296).

Each test reproduces one finding from the bug-hunt of 2026-10-15 and
fails on the code before the fix.
"""

from __future__ import annotations

import shutil
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


# ---------------------------------------------------------------------------
# BUG-0053: block-style `concerns:` escapes backlog-lint and concern-lint
# ---------------------------------------------------------------------------

bl = load_script("backlog-lint")
cl = load_script("concern-lint")

CONCERN_FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "concern-lint"
    / "ctx_refs_unmatched"
)


def _story(concerns_block: str) -> str:
    return (
        "---\n"
        "id: ST-0001\n"
        "epic: Test EPIC\n"
        "title: Test story\n"
        "tier: standard\n"
        "status: pending\n"
        f"{concerns_block}"
        "touches: [test.py]\n"
        "---\n\n# Test story\n"
    )


class TestBlockStyleConcerns:
    def test_backlog_lint_parses_block_mapping(self) -> None:
        """BUG-0053: a nested block mapping becomes a mapping of lists."""
        fm, _ = bl.parse_frontmatter(
            _story("concerns:\n  domain: [billing]\n  technical:\n    - backend\n")
        )
        assert fm["concerns"] == {"domain": ["billing"], "technical": ["backend"]}
        assert fm["touches"] == ["test.py"]

    def test_backlog_lint_flags_unknown_block_key(self, tmp_path: Path) -> None:
        """BUG-0053: an unknown key in block style is caught like in flow style."""
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        (backlog / "ST-0001.md").write_text(
            _story("concerns:\n  bogus:\n    - billing\n")
        )
        findings, _ = bl.check_backlog(backlog)
        assert any(
            f.code == "BL-TYPE" and "unknown key 'bogus'" in f.message
            for f in findings
        )

    def test_backlog_lint_comment_keeps_block_parent(self, tmp_path: Path) -> None:
        """BUG-0053: a comment line inside the block does not end the block."""
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        (backlog / "ST-0001.md").write_text(
            _story("concerns:\n  # note\n\n  bogus: [billing]\n")
        )
        findings, _ = bl.check_backlog(backlog)
        assert any(
            f.code == "BL-TYPE" and "unknown key 'bogus'" in f.message
            for f in findings
        )

    def test_backlog_lint_accepts_valid_block_mapping(self, tmp_path: Path) -> None:
        """BUG-0053: a valid block mapping passes without error."""
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        (backlog / "ST-0001.md").write_text(
            _story("concerns:\n  domain:\n    - billing\n  technical: [backend]\n")
        )
        findings, _ = bl.check_backlog(backlog)
        assert [f for f in findings if f.severity == "error"] == []

    def test_concern_lint_flags_unmatched_block_names(self, tmp_path: Path) -> None:
        """BUG-0053: concern-lint reads names from a block mapping."""
        root = tmp_path / "proj"
        shutil.copytree(CONCERN_FIXTURE, root)
        (root / "backlog" / "ST-0001.md").write_text(
            _story("concerns:\n  domain: [invoicing]\n  technical:\n    - frontend\n")
        )
        rc = cl.main(["--root", str(root), "--format", "json"])
        assert rc == 1
        text = (root / "docs" / "agent-context.md").read_text()
        _, concerns = cl.parse_agent_context(text)
        refs = cl.check_refs(concerns, root)
        names = sorted(f.message.split("'")[1] for f in refs if f.code == "CTX-REFS")
        assert names == ["frontend", "invoicing"]


# ---------------------------------------------------------------------------
# BUG-0054: gates pass on a directory that does not exist
# ---------------------------------------------------------------------------

al = load_script("arch-lint")
val = load_script("voice-anchor-lint")


class TestMissingInputDirectory:
    def test_arch_lint_missing_docs_dir_exits_2(self, tmp_path: Path) -> None:
        """BUG-0054: a mistyped --docs-dir with nothing else to check exits 2."""
        docs = tmp_path / "docs" / "arch42-typo"
        assert al.main(["--docs-dir", str(docs), "--no-validate"]) == 2

    def test_arch_lint_missing_docs_dir_beside_adr_exits_2(
        self, tmp_path: Path
    ) -> None:
        """BUG-0054: a typo exits 2 without the flag, even when docs/adr/ exists."""
        docs = tmp_path / "docs" / "arch42-typo"
        adr = tmp_path / "docs" / "adr"
        adr.mkdir(parents=True)
        (adr / "adr-0001.md").write_text(
            "---\nstatus: accepted\nevaluation: none\n---\nBody."
        )
        assert al.main(["--docs-dir", str(docs), "--no-validate"]) == 2

    def test_arch_lint_allow_missing_docs_dir_warns(
        self, tmp_path: Path, capsys
    ) -> None:
        """BUG-0054: with the opt-in flag, a missing dir warns and exits 0."""
        docs = tmp_path / "docs" / "arc42"
        args = ["--docs-dir", str(docs), "--no-validate", "--allow-missing-docs-dir"]
        assert al.main(args) == 0
        assert "ARCH-NO-DIR" in capsys.readouterr().out

    def test_arch_lint_allow_missing_docs_dir_runs_adr_check(
        self, tmp_path: Path, capsys
    ) -> None:
        """BUG-0054: with the flag, the ADR check still runs beside a missing dir."""
        docs = tmp_path / "docs" / "arc42"
        adr = tmp_path / "docs" / "adr"
        adr.mkdir(parents=True)
        (adr / "adr-0001.md").write_text("---\nstatus: accepted\n---\nBody.")
        args = ["--docs-dir", str(docs), "--no-validate", "--allow-missing-docs-dir"]
        assert al.main(args) == 1
        assert "ARCH-ADR-EVAL" in capsys.readouterr().out

    def test_arch_lint_image_only_project_with_flag_exits_0(
        self, tmp_path: Path
    ) -> None:
        """BUG-0054: screenshots without arc42 or ADRs pass the hook's call."""
        images = tmp_path / "docs" / "assets" / "images"
        images.mkdir(parents=True)
        (images / "screenshot.png").write_bytes(b"\x89PNG")
        docs = tmp_path / "docs" / "arc42"
        args = ["--docs-dir", str(docs), "--no-validate", "--allow-missing-docs-dir"]
        assert al.main(args) == 0

    def test_statemachine_lint_missing_spec_dir_exits_2(self, tmp_path: Path) -> None:
        """BUG-0054: a missing --spec-dir exits 2."""
        assert sm.main(["--spec-dir", str(tmp_path / "nope")]) == 2

    def test_voice_anchor_lint_missing_factory_dir_exits_2(
        self, tmp_path: Path
    ) -> None:
        """BUG-0054: a missing --factory-dir exits 2."""
        assert val.main(["--factory-dir", str(tmp_path / "nope")]) == 2

    def test_concern_lint_missing_root_exits_2(self, tmp_path: Path) -> None:
        """BUG-0054: a missing --root exits 2."""
        assert cl.main(["--root", str(tmp_path / "nope")]) == 2


# ---------------------------------------------------------------------------
# BUG-0090: arch-lint checks nothing when chapter 5 has plain first columns
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]

PLAIN_CH5 = (
    "# 5. Building Block View\n\n"
    "## 5.2 Level 2: Component View\n\n"
    "| Component  | Responsibility |\n"
    "| ---------- | -------------- |\n"
    "| API routes | Serve requests |\n"
    "| Worker     | Run jobs       |\n"
)

BOLD_CH5 = (
    "# 5. Building Block View\n\n"
    "## 5.2 Level 2: Component View\n\n"
    "| Component      | Responsibility |\n"
    "| -------------- | -------------- |\n"
    "| **API routes** | Serve requests |\n"
    "| **Worker**     | Run jobs       |\n"
)

DSL = (
    "workspace {\n  model {\n    s = softwareSystem \"S\" {\n"
    "      core = container \"Core\" {\n"
    "        api = component \"API routes\"\n"
    "        worker = component \"Worker\"\n"
    "      }\n    }\n  }\n}\n"
)


class TestChapterFiveComponents:
    def test_plain_first_column_is_a_component(self) -> None:
        """BUG-0090: a plain first column under a Component header counts."""
        assert al.ch5_core_components(PLAIN_CH5) == {"API routes", "Worker"}

    def test_bold_first_column_is_a_component(self) -> None:
        """BUG-0090: bold first columns still count."""
        assert al.ch5_core_components(BOLD_CH5) == {"API routes", "Worker"}

    def test_plain_columns_couple_with_dsl(self) -> None:
        """BUG-0090: plain columns take part in the coupling check."""
        rep = al.Report()
        al.check_coupling(rep, DSL, PLAIN_CH5.replace("| Worker ", "| Queue  "))
        couple = sorted(m for _, c, m in rep.items if c == "ARCH-COUPLE")
        assert len(couple) == 2
        assert "'Queue' is in chapter 5" in couple[0]

    def test_zero_components_is_an_error(self) -> None:
        """BUG-0090: chapter 5 without components fails instead of passing."""
        ch5 = "# 5. Building Block View\n\n## 5.2 Level 2\n\nNo table.\n"
        rep = al.Report()
        al.check_coupling(rep, DSL, ch5)
        assert rep.n(al.ERROR) == 1
        assert any(c == "ARCH-CH5-EMPTY" for _, c, _ in rep.items)

    def test_repository_chapter_five_is_unchanged(self) -> None:
        """BUG-0090: this repository's chapter 5 keeps its 41 components."""
        ch5 = (REPO_ROOT / "docs" / "arc42" / "05_building_block_view.md").read_text()
        dsl = (REPO_ROOT / "docs" / "arc42" / "architecture.dsl").read_text()
        assert len(al.ch5_core_components(ch5)) == 41
        rep = al.Report()
        al.check_coupling(rep, dsl, ch5)
        assert rep.n(al.ERROR) == 0
