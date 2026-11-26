"""Text checks of the handbook content (factory-handbooks.feature).

The checks read the committed Markdown of this repository and report a page
that breaks a rule of the feature. FH-07-LN-01 covers the entry points of the
contributor handbook (ST-0456).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from conftest import REPO_ROOT

CONTRIBUTOR = REPO_ROOT / "docs" / "handbook"
CHAPTERS = (
    "getting-started",
    "architecture",
    "agents-and-skills",
    "gates-and-hooks",
    "cli-integrations",
    "testing",
    "workflow",
    "release",
    "contributing",
)
CONCERN_TARGETS = {
    "write a skill or agent": "docs/handbook/agents-and-skills/index.md",
    "add a gate": "docs/handbook/gates-and-hooks/index.md",
    "release": "docs/handbook/release/index.md",
}
LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")


def section(text: str, heading: str, level: str = "##") -> str:
    """The body of a section, up to the next heading of the same level."""
    match = re.search(rf"^{level} {re.escape(heading)}\n(.*?)(?=^{level} |\Z)", text, re.DOTALL | re.MULTILINE)
    assert match, f"no section {heading!r}"
    return match.group(1)


def frontmatter(path: Path) -> dict:
    block = re.match(r"\A---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.DOTALL)
    assert block, f"{path}: no frontmatter"
    return dict(line.split(": ", 1) for line in block.group(1).splitlines() if ": " in line)


def linked_tutorials(body: str, repo: Path) -> list[Path]:
    """The pages under getting-started/ that the body links to and that hold an implemented tutorial."""
    found = []
    for target in LINK.findall(body):
        if target.startswith("http"):
            continue
        page = (repo / target).resolve()
        if page.is_relative_to((repo / "docs" / "handbook" / "getting-started").resolve()) and page.is_file():
            meta = frontmatter(page)
            if meta["type"] == "tutorial" and meta["status"] == "implemented":
                found.append(page)
    return found


@pytest.mark.spec("FH-07-LN-01")
class TestFH07LN01ContributorEntryPoints:
    """FH-07-01: the root README and the agent context lead to contributor pages."""

    def test_st_0456_fh_07_01_contributing_section_links_to_the_tutorial(self) -> None:
        body = section((REPO_ROOT / "README.md").read_text(encoding="utf-8"), "Contributing")
        assert linked_tutorials(body, REPO_ROOT), "Contributing links to no implemented tutorial under docs/handbook/getting-started/"

    def test_st_0456_fh_07_01_contributing_link_to_a_stub_tutorial_fails(self, tmp_path: Path) -> None:
        folder = tmp_path / "docs" / "handbook" / "getting-started"
        folder.mkdir(parents=True)
        (folder / "tutorial.md").write_text("---\ntitle: T\ntype: tutorial\nstatus: stub\n---\n\nA stub.\n", encoding="utf-8")
        assert linked_tutorials("[tutorial](docs/handbook/getting-started/tutorial.md)", tmp_path) == []

    @pytest.mark.parametrize(("concern", "target"), sorted(CONCERN_TARGETS.items()))
    def test_st_0456_fh_07_01_agent_context_routes_the_concern(self, concern: str, target: str) -> None:
        text = (REPO_ROOT / "docs" / "agent-context.md").read_text(encoding="utf-8")
        technical = section(text, "Technical concerns")
        names = {m.group(1).lower(): m.group(2) for m in re.finditer(r"^### ([^\n]+)\n(.*?)(?=^### |\Z)", technical, re.DOTALL | re.MULTILINE)}
        assert concern in names, f"no technical concern {concern!r}"
        reads = re.findall(r"^Read: (.+)$", names[concern], re.MULTILINE)
        assert reads == [target]
        assert (REPO_ROOT / target).is_file()


class TestContributorHandbookShape:
    """ST-0456: nine chapters, each with an index, and a stub with a source."""

    def test_st_0456_nine_chapters_each_with_an_index(self) -> None:
        folders = sorted(p.name for p in CONTRIBUTOR.iterdir() if p.is_dir())
        assert folders == sorted(CHAPTERS)
        for chapter in CHAPTERS:
            assert (CONTRIBUTOR / chapter / "index.md").is_file()

    @pytest.mark.parametrize("chapter", [c for c in CHAPTERS if c not in ("getting-started", "contributing")])
    def test_st_0456_stub_chapter_holds_a_stub_with_a_source(self, chapter: str) -> None:
        stubs = [p for p in (CONTRIBUTOR / chapter).glob("*.md") if p.name != "index.md" and frontmatter(p)["status"] == "stub"]
        assert stubs, f"{chapter}/ holds no stub"
        for stub in stubs:
            body = stub.read_text(encoding="utf-8").split("---\n", 2)[2]
            assert LINK.search(body), f"{stub} links to no source"

    def test_st_0456_rule_summary_is_followed_by_a_rulebook_source(self) -> None:
        for page in CONTRIBUTOR.rglob("*.md"):
            lines = page.read_text(encoding="utf-8").splitlines()
            for number, line in enumerate(lines):
                if line.startswith("> Rule summary:"):
                    following = lines[number + 1] if number + 1 < len(lines) else ""
                    assert following.startswith("> Source:"), f"{page}:{number + 1}"
                    assert "packages/factory/rulebooks/" in following, f"{page}:{number + 1}"

    def test_st_0456_tutorial_names_only_existing_scripts(self) -> None:
        tutorial = CONTRIBUTOR / "getting-started" / "from-clone-to-a-passing-test-run.md"
        text = tutorial.read_text(encoding="utf-8")
        for path in re.findall(r"(?<![\w./(])(?:\./|\.agent-factory/factory/scripts/|packages/factory/scripts/|tests/)[\w./-]+", text):
            if path.startswith(".agent-factory/"):
                path = "packages/factory/" + path.removeprefix(".agent-factory/factory/")
            elif path.startswith("./"):
                path = path[2:]
            assert (REPO_ROOT / path).exists(), path
