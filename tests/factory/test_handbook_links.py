"""FH-05-IT-02: every link to the three deleted files points to its new home.

The migration of ST-0454 deleted the guide and repointed every link in one
commit. The checks compare that commit with its parent, or HEAD with the
working tree while the commit is under way. The link check runs on a copy
of the repository with the factory installed by ``init-factory``, so links
into ``.agent-factory/`` resolve against that copy (SPEC-0156).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from _link_rewrite import UnmappedAnchor, read_section_map, rewrite_section_links
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script

GUIDE = "packages/factory/docs/" + "factory" + "-guide.md"
OLD_FILES = {GUIDE, "docs/arc42/concepts.md", "docs/arc42/beginner-intro.md"}
MIGRATION_MAP = "docs/spec/work/factory-handbooks-migration-map.md"
RECORDS = re.compile(
    r"^(backlog|docs/handoffs|docs/findings|docs/reviews|docs/transcripts|docs/research"
    r"|docs/spec/work|docs/proposals/implemented|docs/proposals/superseded|~archive)/"
)
OUTSIDE = re.compile(r"^(poc/|\.agent-factory/)")

pytestmark = pytest.mark.spec("FH-05-IT-02")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, check=True).stdout


def ships(name: str) -> bool:
    """Whether the file ships with the factory, so it keeps installed links (L-62)."""
    return name.startswith("packages/factory/")


def tracked_markdown() -> list[str]:
    return [name for name in git("ls-files", "*.md").splitlines() if not name.startswith(".agent-factory/")]


class Revision:
    """The files of one commit, or of the working tree when ``rev`` is None."""

    def __init__(self, rev: str | None) -> None:
        self.rev = rev

    def text(self, name: str) -> str:
        if self.rev is None:
            return (REPO_ROOT / name).read_text(encoding="utf-8")
        return git("show", f"{self.rev}:{name}")

    def anchors(self, pages: set[str]) -> dict[str, set[str]]:
        link_check = load_script("link-check")
        return {page: {link_check.slugify(t) for t in link_check.heading_titles(self.text(page))} for page in pages}


def migration() -> tuple[Revision, Revision, list[str]]:
    """The revisions before and after the migration, and the Markdown it changed."""
    deleted = git("log", "-1", "--format=%H", "--diff-filter=D", "--", GUIDE).strip()
    before, after = (f"{deleted}^", deleted) if deleted else ("HEAD", None)
    if subprocess.run(["git", "-C", str(REPO_ROOT), "cat-file", "-e", before], capture_output=True).returncode:
        pytest.skip(f"{before} is missing, probably a shallow clone")
    changed = git("diff", "--name-only", "--diff-filter=M", before, *([after] if after else []), "--", "*.md")
    return Revision(before), Revision(after), changed.split()


def unpadded(text: str) -> str:
    """The text without table padding, which the formatter sets to the widest cell."""
    text = re.sub(r"^\|[ :|-]+\|$", "|-|", text, flags=re.MULTILINE)
    return re.sub(r" +", " ", text)


def section_map(revision: Revision) -> tuple[dict[str, dict[str, str]], dict[str, set[str]]]:
    sections = read_section_map(revision.text(MIGRATION_MAP), OLD_FILES)
    return sections, revision.anchors({page for pages in sections.values() for page in pages.values()})


def test_st_0454_fh_05_02_no_markdown_file_links_to_the_three_files() -> None:
    sections, anchors = section_map(Revision(None))
    left = []
    for name in tracked_markdown():
        try:
            text = (REPO_ROOT / name).read_text(encoding="utf-8")
            edits = rewrite_section_links(text, name, sections, anchors, ships(name))[1]
        except UnmappedAnchor as error:
            edits = [(str(error), "")]
        left += [f"{name}: {old}" for old, _ in edits]
    assert left == []


def test_st_0454_fh_05_02_each_rewritten_link_follows_the_map() -> None:
    before, after, changed = migration()
    sections, anchors = section_map(after)
    link_check = load_script("link-check")
    assert changed, "the migration changed no Markdown file"
    for name in changed:
        expected, edits = rewrite_section_links(before.text(name), name, sections, anchors, ships(name))
        if not edits:
            continue
        actual = after.text(name)
        if RECORDS.match(name):
            assert unpadded(actual) == unpadded(expected), name
        else:
            found = set(link_check.destinations(link_check.strip_code(actual)))
            assert {new for _, new in edits} <= found, name


def test_st_0454_fh_05_02_link_check_passes_on_an_installed_copy(tmp_path: Path) -> None:
    project = tmp_path / "repo"
    for name in git("ls-files", "--cached", "--others", "--exclude-standard").splitlines():
        source = REPO_ROOT / name
        if source.is_file() and not source.is_symlink():
            (project / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, project / name)
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)}
    subprocess.run(["git", "init", "-q", str(project)], check=True, env=env)
    init = subprocess.run(
        [sys.executable, str(project / "packages" / "factory" / "scripts" / "init-factory"),
         "--source", str(project), "--target", str(project), "--cli", "claude", "--project-name", "repo"],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, env=env, check=False,
    )
    assert init.returncode == 0, init.stderr
    assert (project / ".agent-factory" / "factory" / "docs" / "handbook" / "index.md").is_file()
    _, _, changed = migration()
    live = [name for name in tracked_markdown() if not OUTSIDE.match(name) and not RECORDS.match(name)]
    files = sorted(set(live) | {name for name in changed if (project / name).is_file()})
    result = subprocess.run(
        [sys.executable, str(SOURCE_SCRIPTS_DIR / "link-check"), *files],
        cwd=project, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
