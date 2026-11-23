"""Tests for move-docs and the full-path rewrite of _link_rewrite.

Every test builds its project at test time in a temporary git repository.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from _link_rewrite import rewrite_paths
from conftest import SOURCE_SCRIPTS_DIR, load_script

SCRIPT = SOURCE_SCRIPTS_DIR / "move-docs"

OLD = "docs/proposals/sample-proposal.md"
NEW = "docs/proposals/implemented/sample-proposal.md"


@pytest.fixture
def move_docs():
    return load_script("move-docs")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
    ).stdout


def make_project(root: Path, files: dict[str, str]) -> Path:
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "start")
    return root


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), "--root", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


PROJECT = {
    OLD: "# Sample proposal\n\nSee [run lifecycle](run-lifecycle.md#scope).\n",
    "docs/proposals/run-lifecycle.md": (
        "---\nrelated:\n  - docs/proposals/sample-proposal.md\n---\n"
        "# Run lifecycle\n\nIt builds on [sample proposal](sample-proposal.md#decisions).\n"
    ),
    "docs/proposals/implemented/.keep": "",
    "backlog/ST-0371.md": (
        'touches: ["docs/proposals/sample-proposal.md"]\n\n'
        "DEC-14 in the [proposal](../docs/proposals/sample-proposal.md#decisions).\n"
    ),
    "docs/research/synthesis.md": (
        "evidence: docs/proposals/sample-proposal.md#decisions (DEC-14)\n"
    ),
    "notes.yaml": "source: docs/proposals/sample-proposal.md\n",
}


class TestRewritePaths:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            pytest.param(f"see {OLD}.", f"see {NEW}.", id="sentence-end"),
            pytest.param(f"`{OLD}#a`", f"`{NEW}#a`", id="code-span-anchor"),
            pytest.param(f'["{OLD}"]', f'["{NEW}"]', id="yaml-list"),
            pytest.param(f"../{OLD}", f"../{OLD}", id="relative-is-not-full"),
            pytest.param(f"x/{OLD}", f"x/{OLD}", id="longer-path"),
            pytest.param(f"{OLD}x", f"{OLD}x", id="longer-name"),
            pytest.param(f"{OLD}.bak", f"{OLD}.bak", id="longer-extension"),
            pytest.param(f"{OLD}/b", f"{OLD}/b", id="folder-prefix"),
        ],
    )
    def test_rewrite_paths_matches_only_the_full_path(self, text, expected):
        rewritten, _ = rewrite_paths(text, {OLD: NEW})
        assert rewritten == expected

    def test_rewrite_paths_names_each_line(self):
        _, rewrites = rewrite_paths(f"a\n{OLD}\nb {OLD}\n", {OLD: NEW})
        assert rewrites == [(2, OLD, NEW), (3, OLD, NEW)]

    def test_rewrite_paths_prefers_the_longest_old_path(self):
        moved = {"docs/a.md": "docs/x/a.md", "docs/a.md.d/b.md": "docs/y/b.md"}
        rewritten, _ = rewrite_paths("docs/a.md.d/b.md docs/a.md", moved)
        assert rewritten == "docs/y/b.md docs/x/a.md"


class TestMoveDocs:
    def test_moves_the_file_and_rewrites_every_reference(self, tmp_path):
        root = make_project(tmp_path, PROJECT)
        result = run(root, OLD, "docs/proposals/implemented/")
        assert result.returncode == 0, result.stderr

        assert not (root / OLD).exists()
        moved = (root / NEW).read_text()
        assert "[run lifecycle](../run-lifecycle.md#scope)" in moved
        lifecycle = (root / "docs/proposals/run-lifecycle.md").read_text()
        assert f"  - {NEW}\n" in lifecycle
        assert "[sample proposal](implemented/sample-proposal.md#decisions)" in lifecycle
        story = (root / "backlog/ST-0371.md").read_text()
        assert f'touches: ["{NEW}"]' in story
        assert f"(../{NEW}#decisions)" in story
        assert f"evidence: {NEW}#decisions" in (root / "docs/research/synthesis.md").read_text()
        assert (root / "notes.yaml").read_text() == f"source: {NEW}\n"

    def test_stages_the_move_as_a_rename(self, tmp_path):
        root = make_project(tmp_path, PROJECT)
        assert run(root, OLD, NEW).returncode == 0
        staged = _git(root, "diff", "--cached", "--name-status", "-M")
        assert f"{OLD}\t{NEW}" in staged

    def test_reports_each_rewrite(self, tmp_path):
        root = make_project(tmp_path, PROJECT)
        out = run(root, OLD, NEW).stdout
        assert f"move: {OLD} -> {NEW}" in out
        assert "link: backlog/ST-0371.md: ../docs/proposals/sample-proposal.md#decisions" in out
        assert f"path: notes.yaml:1: {OLD} -> {NEW}" in out

    def test_moves_an_untracked_file(self, tmp_path):
        root = make_project(tmp_path, PROJECT)
        (root / "docs/proposals/draft.md").write_text("# Draft\n")
        (root / "index.md").write_text("[d](docs/proposals/draft.md)\n")
        assert run(root, "docs/proposals/draft.md", "docs/proposals/implemented/").returncode == 0
        assert (root / "docs/proposals/implemented/draft.md").is_file()
        assert (root / "index.md").read_text() == "[d](docs/proposals/implemented/draft.md)\n"

    def test_dry_run_changes_no_file(self, tmp_path):
        root = make_project(tmp_path, PROJECT)
        result = run(root, "--dry-run", OLD, NEW)
        assert result.returncode == 0
        assert "dry run:" in result.stdout
        assert (root / OLD).is_file()
        assert _git(root, "status", "--porcelain") == ""

    @pytest.mark.parametrize(
        ("args", "reason"),
        [
            pytest.param(("docs/missing.md", "docs/x.md"), "no such file", id="missing"),
            pytest.param((OLD, "docs/proposals/run-lifecycle.md"), "exists already", id="exists"),
            pytest.param((OLD,), "OLD NEW pairs", id="odd-count"),
            pytest.param((OLD, "../outside.md"), "outside the project", id="outside"),
            pytest.param(
                (OLD, "docs/x.md", "docs/proposals/run-lifecycle.md", "docs/x.md"),
                "share the new path",
                id="shared-new",
            ),
        ],
    )
    def test_refuses_before_the_first_change(self, tmp_path, args, reason):
        root = make_project(tmp_path, PROJECT)
        result = run(root, *args)
        assert result.returncode == 2
        assert reason in result.stderr
        assert _git(root, "status", "--porcelain") == ""

    def test_failed_move_undoes_every_change(self, tmp_path, move_docs, monkeypatch):
        root = make_project(tmp_path, PROJECT)
        second = "docs/proposals/run-lifecycle.md"
        real_move = move_docs._move

        def failing_move(root_, git, old, new):
            if old == second:
                raise OSError("disk full")
            real_move(root_, git, old, new)

        monkeypatch.setattr(move_docs, "_move", failing_move)
        code = move_docs.main(["--root", str(root), OLD, NEW, second, "docs/x.md"])
        assert code == 1
        assert _git(root, "status", "--porcelain") == ""
