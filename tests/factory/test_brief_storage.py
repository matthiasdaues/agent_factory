"""Regression tests for the brief-storage run.

- Item 18 of the bug-hunt handoff: briefs and scratch files live under
  `.current-work/<branch>/` in the main checkout, never in a scratchpad
  under /tmp, which the system can empty.
- BUG-0092: a brief names factory inputs by absolute path into the main
  checkout, because a linked worktree holds no `.agent-factory/`.
- BUG-0102: Pi dispatch cuts worktrees where `rules.md` says.
- BUG-0103: one shared helper finds the main checkout.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script

CONTRACT = REPO_ROOT / "packages/factory/rulebooks/conventions/dispatch-contract.md"
EXTENSIONS = REPO_ROOT / "packages/factory/config/extensions"


def _section(text: str, heading: str) -> str:
    start = text.index(f"### {heading}\n")
    end = text.find("\n### ", start + 1)
    return text[start:end if end != -1 else None]


BRIEF_FILE = _section(CONTRACT.read_text(encoding="utf-8"), "Brief File")


class TestBriefFileRule:
    def test_briefs_go_under_current_work_in_the_main_checkout(self):
        assert "`.current-work/<branch>/briefs/<task>.md`" in BRIEF_FILE
        assert "main checkout" in BRIEF_FILE

    def test_scratch_files_go_under_current_work(self):
        assert "`.current-work/<branch>/scratch/<agent-or-story>/`" in BRIEF_FILE

    def test_no_scratchpad_location_remains(self):
        assert "<scratchpad>" not in BRIEF_FILE

    def test_prompt_names_the_brief_by_absolute_path(self):
        assert "absolute path" in BRIEF_FILE

    def test_factory_inputs_come_from_the_main_checkout(self):
        """BUG-0092."""
        assert "`<main checkout>/.agent-factory/factory/`" in BRIEF_FILE


class TestPiWorktreePath:
    """BUG-0102: rules.md places worktrees under .current-work/<feature-branch>/."""

    def test_no_extension_names_the_old_path(self):
        for path in EXTENSIONS.glob("*.ts"):
            assert ".current-work/worktrees" not in path.read_text(encoding="utf-8"), path.name
            assert 'join(".current-work", "worktrees")' not in path.read_text(encoding="utf-8"), path.name

    def test_dispatch_wave_cuts_under_the_target_branch(self):
        source = (EXTENSIONS / "dispatch-wave.ts").read_text(encoding="utf-8")
        assert 'return join(cwd, ".current-work", target);' in source
        assert "join(worktreeDir(cwd, params.target), sanitizeBranch(item.branch))" in source

    def test_guard_accepts_any_path_under_current_work(self):
        source = (EXTENSIONS / "block-dangerous-git.ts").read_text(encoding="utf-8")
        assert 'wtPath.startsWith(".current-work/")' in source
        assert ".current-work/<feature-branch>/<branch>" in source


class TestSharedMainCheckout:
    """BUG-0103."""

    @pytest.mark.parametrize("script", ["scope-lint", "concern-lint", "link-check"])
    def test_scripts_hold_no_copy_of_their_own(self, script):
        source = (SOURCE_SCRIPTS_DIR / script).read_text(encoding="utf-8")
        assert "def _main_checkout" not in source
        assert "def _installed_copy_in_main_checkout" not in source
        assert "from _main_checkout import" in source

    @pytest.fixture
    def repo(self, tmp_path: Path) -> tuple[Path, Path]:
        main = tmp_path / "main"
        main.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=main, check=True)
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base"],
            cwd=main, check=True,
        )
        linked = tmp_path / "linked"
        subprocess.run(["git", "worktree", "add", "-q", "-b", "s", str(linked)], cwd=main, check=True)
        return main, linked

    def test_linked_worktree_finds_the_main_checkout(self, repo):
        import _main_checkout as helper
        main, linked = repo
        assert helper.main_checkout(linked) == main.resolve()

    def test_main_checkout_and_subfolder_give_none(self, repo):
        import _main_checkout as helper
        main, linked = repo
        (linked / "sub").mkdir()
        assert helper.main_checkout(main) is None
        assert helper.main_checkout(linked / "sub") is None

    def test_installed_copy_maps_into_the_main_checkout(self, repo):
        import _main_checkout as helper
        main, linked = repo
        target = linked / ".agent-factory" / "factory" / "rulebooks" / "rules.md"
        assert helper.installed_copy_in_main_checkout(target) == (
            main.resolve() / ".agent-factory" / "factory" / "rulebooks" / "rules.md"
        )
        assert helper.installed_copy_in_main_checkout(linked / "docs" / "a.md") is None
