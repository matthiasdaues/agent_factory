"""Text checks of the handbook content (factory-handbooks.feature).

The checks read the committed Markdown of this repository and report a page
that breaks a rule of the feature. FH-06-LN-01 covers the entry points of the
user handbook (ST-0455). FH-07-LN-01 covers the entry points of the
contributor handbook (ST-0456). FH-05-IT-01 and FH-05-LN-01 cover the
migration of the three deleted files (ST-0454).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
from _link_rewrite import MAP_ROW
from conftest import REPO_ROOT, load_script

CONTRIBUTOR = REPO_ROOT / "docs" / "handbook"
FACTORY = REPO_ROOT / "packages" / "factory"
USER_HANDBOOK = ".agent-factory/factory/docs/handbook/"
USER_TUTORIAL = USER_HANDBOOK + "getting-started/"
ENTRY_POINTS = (
    FACTORY / "config" / "session-menu.md",
    FACTORY / "agents" / "virgil.md",
    FACTORY / "skills" / "newcomer-tour" / "SKILL.md",
    FACTORY / "skills" / "guided-tour" / "SKILL.md",
    FACTORY / "skills" / "explain-concept" / "SKILL.md",
    FACTORY / "INDEX.yaml",
    FACTORY / "README.md",
)
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


def runnable_commands(text: str) -> set[str]:
    """The factory commands that start a line of a fenced code block."""
    found = set()
    for block in re.findall(r"^```\w*\n(.*?)^```", text, re.DOTALL | re.MULTILINE):
        for line in block.splitlines():
            found.update(re.findall(r"^(?:\./|\.agent-factory/factory/scripts/)?(init-factory|update-factory|remove-factory)(?=\s|$)", line.strip()))
    return found


def tutorial_pages(body: str) -> list[Path]:
    """The implemented tutorial pages of the user handbook that the body names by path."""
    pages = []
    for name in re.findall(re.escape(USER_TUTORIAL) + r"([\w-]+\.md)(?![\w./-])", body):
        page = FACTORY / "docs" / "handbook" / "getting-started" / name
        if page.is_file() and frontmatter(page)["type"] == "tutorial":
            pages.append(page)
    return pages


def virgil_inputs(index_text: str) -> list[str]:
    """The inputs listed for the virgil agent in INDEX.yaml."""
    block = re.search(r"^\s*- name: virgil\n(.*?)(?=^\s*- name: |\Z)", index_text, re.DOTALL | re.MULTILINE)
    assert block, "no virgil entry in INDEX.yaml"
    inputs = re.search(r"inputs:\n\s+context:\n((?:\s+- .+\n)+)", block.group(1))
    assert inputs, "virgil lists no inputs"
    return [line.strip().removeprefix("- ") for line in inputs.group(1).splitlines()]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.spec("FH-06-LN-01")
class TestFH06LN01UserEntryPoints:
    """FH-06-01: every factory entry point leads to the user handbook."""

    def test_st_0455_fh_06_01_menu_routes_a_new_user_to_the_tutorial(self) -> None:
        body = section(read(FACTORY / "config" / "session-menu.md"), "H — Help")
        assert "newcomer-tour" in body
        assert USER_TUTORIAL in body

    def test_st_0455_fh_06_01_tour_reads_the_tutorial_page(self) -> None:
        body = section(read(FACTORY / "skills" / "newcomer-tour" / "SKILL.md"), "Procedure")
        assert tutorial_pages(body), "the procedure names no tutorial page under " + USER_TUTORIAL

    def test_st_0455_fh_06_01_tour_pointed_at_the_chapter_index_fails(self) -> None:
        assert not tutorial_pages(f"Read `{USER_TUTORIAL}index.md`.")

    def test_st_0455_fh_06_01_tour_pointed_at_a_backup_file_fails(self) -> None:
        assert not tutorial_pages(f"Read `{USER_TUTORIAL}first-session.md.bak`.")

    def test_st_0455_fh_06_01_guided_tour_names_the_tutorial_in_option_h(self) -> None:
        lines = [x for x in read(FACTORY / "skills" / "guided-tour" / "SKILL.md").splitlines() if x.startswith("- **H")]
        assert len(lines) == 1
        assert USER_TUTORIAL in lines[0]

    @pytest.mark.parametrize("path", [FACTORY / "skills" / "explain-concept" / "SKILL.md", FACTORY / "agents" / "virgil.md"])
    def test_st_0455_fh_06_01_entry_point_names_the_user_handbook(self, path: Path) -> None:
        assert USER_HANDBOOK in read(path)

    def test_st_0455_fh_06_01_virgil_inputs_name_the_handbook_index(self) -> None:
        inputs = virgil_inputs(read(FACTORY / "INDEX.yaml"))
        assert USER_HANDBOOK + "index.md" in inputs
        assert (FACTORY / "docs" / "handbook" / "index.md").is_file()

    def test_st_0455_fh_06_01_virgil_inputs_without_the_index_fail(self) -> None:
        text = "agents:\n  - name: virgil\n    inputs:\n      context:\n        - other.md\n"
        assert USER_HANDBOOK + "index.md" not in virgil_inputs(text)

    def test_st_0455_fh_06_01_readme_keeps_the_commands_and_links_to_the_handbook(self) -> None:
        text = read(FACTORY / "README.md")
        assert runnable_commands(text) == {"init-factory", "update-factory", "remove-factory"}
        assert "docs/handbook/" in text
        targets = [t for t in LINK.findall(text) if t.startswith("docs/handbook/")]
        assert targets
        assert all((FACTORY / t).is_file() for t in targets), targets

    def test_st_0455_fh_06_01_readme_with_commands_only_in_prose_fails(self) -> None:
        text = "Run init-factory, update-factory and remove-factory. See [handbook](docs/handbook/index.md).\n"
        assert runnable_commands(text) == set()

    def test_st_0455_fh_06_01_readme_with_a_longer_command_name_fails(self) -> None:
        assert runnable_commands("```bash\ninit-factory-missing\n```\n") == set()

    @pytest.mark.parametrize("path", ENTRY_POINTS, ids=lambda p: p.name)
    def test_st_0455_fh_06_01_no_entry_point_names_the_guide(self, path: Path) -> None:
        assert "factory-" + "guide" not in read(path)


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
    """ST-0456: a stub with a source in each stub chapter, and rule summaries with a source."""

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


# The guide's name is built from two parts, so the search of FH-05-LN-01
# does not find this file.
GUIDE_NAME = "factory" + "-guide"
GUIDE = f"packages/factory/docs/{GUIDE_NAME}.md"
CONCEPTS = "docs/arc42/concepts.md"
INTRO = "docs/arc42/beginner-intro.md"
OLD_FILES = (GUIDE, CONCEPTS, INTRO)
MAP_COMMIT = "4ebf5101f70c1540a0d53dcfb3d00cfa977d361a"
MIGRATION_MAP = REPO_ROOT / "docs" / "spec" / "work" / "factory-handbooks-migration-map.md"
USER_PAGES = "packages/factory/docs/handbook/"


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, check=False)


def map_rows() -> dict[tuple[str, str], str]:
    """Each (source, anchor) of the migration map and the page it names."""
    rows = {}
    for line in read(MIGRATION_MAP).splitlines():
        row = MAP_ROW.match(line)
        if row and row.group(1) in OLD_FILES:
            rows[(row.group(1), row.group(2))] = row.group(3)
    return rows


def heading_anchors(text: str) -> list[str]:
    """The anchor of each heading, a repeated one suffixed as link-check does."""
    link_check = load_script("link-check")
    seen: dict[str, int] = {}
    found = []
    for title in link_check.heading_titles(text):
        slug = link_check.slugify(title)
        found.append(slug if slug not in seen else f"{slug}-{seen[slug]}")
        seen[slug] = seen.get(slug, 0) + 1
    return found


@pytest.mark.spec("FH-05-IT-01")
class TestFH05IT01MigrationMap:
    """FH-05-01: every section of the three files has a home in the map."""

    @pytest.mark.parametrize("old", OLD_FILES)
    def test_st_0454_fh_05_01_every_heading_has_a_row_with_a_real_page(self, old: str) -> None:
        if git("cat-file", "-e", f"{MAP_COMMIT}^{{commit}}").returncode != 0:
            pytest.skip(f"commit {MAP_COMMIT} is missing, probably a shallow clone")
        text = git("show", f"{MAP_COMMIT}:{old}").stdout
        rows = map_rows()
        for anchor in heading_anchors(text):
            assert (old, anchor) in rows, f"no map row for {old}#{anchor}"
            assert (REPO_ROOT / rows[(old, anchor)]).is_file(), rows[(old, anchor)]

    def test_st_0454_fh_05_01_rows_name_the_handbook_of_their_reader(self) -> None:
        for (old, anchor), page in map_rows().items():
            if (old, anchor) == (CONCEPTS, "project-directory-tree"):
                assert page.startswith("docs/handbook/architecture/"), page
                assert frontmatter(REPO_ROOT / page)["type"] == "reference"
            elif old != CONCEPTS or anchor in ("the-phase-chain", "key-ideas"):
                assert page.startswith(USER_PAGES), f"{old}#{anchor}: {page}"

    def test_st_0454_fh_05_01_concept_page_holds_both_sections(self) -> None:
        page = map_rows()[(CONCEPTS, "the-phase-chain")]
        assert frontmatter(REPO_ROOT / page)["type"] == "concept"
        assert {"the-phase-chain", "key-ideas"} <= set(heading_anchors(read(REPO_ROOT / page)))

    def test_st_0454_fh_05_01_tree_names_the_source_and_the_installed_copy(self) -> None:
        page = REPO_ROOT / map_rows()[(CONCEPTS, "project-directory-tree")]
        assert frontmatter(page)["status"] == "implemented"
        tree = re.search(r"^```\n(.*?)^```", read(page), re.DOTALL | re.MULTILINE).group(1)
        assert "packages/" in tree and "factory/" in tree and ".agent-factory/factory/" in tree


@pytest.mark.spec("FH-05-LN-01")
class TestFH05LN01OldFilesAreGone:
    """FH-05-03: the three files are deleted, and nothing names the guide."""

    @pytest.mark.parametrize("old", OLD_FILES)
    def test_st_0454_fh_05_03_old_file_is_absent(self, old: str) -> None:
        assert not (REPO_ROOT / old).exists()

    def test_st_0454_fh_05_03_archive_holds_no_copy(self) -> None:
        names = {Path(old).name for old in OLD_FILES}
        tracked = git("ls-files").stdout.splitlines()
        assert [p for p in tracked if "~archive/" in p and Path(p).name in names] == []

    def test_st_0454_fh_05_03_search_finds_no_guide_name(self) -> None:
        tracked = git("ls-files", "packages/", "tests/", "README.md", "docs/spec/features/").stdout.splitlines()
        skipped = {"CHANGELOG.md", "factory-handbooks.feature"}
        hits = [
            name
            for name in tracked
            if Path(name).name not in skipped
            and (REPO_ROOT / name).is_file()
            and GUIDE_NAME in (REPO_ROOT / name).read_bytes().decode("utf-8", "replace")
        ]
        assert hits == []
