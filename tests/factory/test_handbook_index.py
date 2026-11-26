"""Checks of handbook-index (ST-0452).

handbook-index writes the page list of every index.md of both handbooks
between its markers (validation-rules.md BR-140, BR-143 to BR-146). The
integration tests run the script as a subprocess on a temporary project that
holds the model chapter `cli-integrations/` of the feature description. The
contract tests call the functions of the script without files.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR, load_script

hi = load_script("handbook-index")

USER = "packages/factory/docs/handbook"
CONTRIBUTOR = "docs/handbook"
START, END = hi.START_MARKER, hi.END_MARKER
INTRO = "# CLI integrations\n\nIntroduction above the list.\n\n"
NOTE = "\nNote below the list.\n"


def page_text(title, type_="concept", status="implemented", order=None, description=None, body=""):
    """The text of a page; a None argument leaves its line out."""
    lines = ["---"]
    for key, value in (
        ("title", title), ("type", type_), ("status", status), ("order", order), ("description", description),
    ):
        if value is not None:
            lines.append(f"{key}: {value}")
    lines += ["---", "", body]
    return "\n".join(lines)


def index_text(title, order=None, intro="", note="", with_markers=True):
    text = page_text(title, order=order) + intro
    if with_markers:
        text += f"{START}\n{END}\n"
    return text + note


def write(base: Path, rel: str, text: str) -> Path:
    path = base / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build_model(base: Path) -> Path:
    """The model of the feature description: both handbooks, no list written yet."""
    write(base, f"{USER}/index.md", index_text("Factory handbook"))
    write(base, f"{USER}/getting-started/index.md", index_text("Getting started", order=10))
    chapter = f"{USER}/cli-integrations"
    write(base, f"{chapter}/index.md", index_text("CLI integrations", order=80, intro=INTRO, note=NOTE))
    write(base, f"{chapter}/add-an-integration.md",
          page_text("Add a CLI integration", "how-to", order=20, description="Add the files of one CLI."))
    write(base, f"{chapter}/remove-an-integration.md",
          page_text("Remove a CLI integration", "how-to", order=10,
                    description="Remove the files of one CLI from a project."))
    write(base, f"{chapter}/how-the-clis-differ.md", page_text("How the CLIs differ", "concept"))
    write(base, f"{chapter}/opencode-desktop.md", page_text("OpenCode Desktop", "how-to", "stub"))
    write(base, f"{CONTRIBUTOR}/index.md", index_text("Contributor handbook"))
    write(base, f"{CONTRIBUTOR}/release/index.md", index_text("Release", order=40))
    write(base, f"{CONTRIBUTOR}/release/ship.md", page_text("Ship a release", "how-to", "stub"))
    write(base, f"{CONTRIBUTOR}/contributing/index.md", index_text("Contributing", order=20))
    return base


def run_script(name: str, base: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SOURCE_SCRIPTS_DIR / name), *args],
        cwd=base, capture_output=True, text=True, check=False,
    )


def snapshot(base: Path) -> dict[str, bytes]:
    return {p.relative_to(base).as_posix(): p.read_bytes() for p in sorted(base.rglob("*")) if p.is_file()}


@pytest.fixture
def model(tmp_path: Path) -> Path:
    return build_model(tmp_path)


@pytest.mark.spec("FH-01-IT-01")
def test_fh_01_01_grouped_sorted_list_between_markers(model):
    result = run_script("handbook-index", model)

    assert result.returncode == 0, result.stdout
    text = (model / USER / "cli-integrations/index.md").read_text(encoding="utf-8")
    assert text.index("## Concepts") < text.index("## How-to guides")
    assert "- [How the CLIs differ](how-the-clis-differ.md)\n" in text
    assert text.index("[Remove a CLI integration]") < text.index("[Add a CLI integration]")
    assert (
        "- [Remove a CLI integration](remove-an-integration.md): "
        "Remove the files of one CLI from a project.\n"
    ) in text


@pytest.mark.spec("FH-01-IT-02")
def test_fh_01_02_stub_and_outside_text(model):
    path = model / USER / "cli-integrations/index.md"
    before = path.read_text(encoding="utf-8")

    result = run_script("handbook-index", model)

    assert result.returncode == 0
    after = path.read_text(encoding="utf-8")
    assert "OpenCode Desktop" not in after
    assert "index.md" not in after.partition(START)[2].partition(END)[0]
    assert after.startswith(before.partition(START)[0] + START)
    assert after.endswith(END + before.partition(END)[2])


@pytest.mark.spec("FH-01-IT-03")
def test_fh_01_03_page_without_type_writes_nothing(model):
    write(model, f"{USER}/cli-integrations/add-an-integration.md",
          page_text("Add a CLI integration", type_=None))
    before = snapshot(model)

    result = run_script("handbook-index", model)

    assert result.returncode != 0
    assert f"{USER}/cli-integrations/add-an-integration.md" in result.stdout
    assert "field type" in result.stdout
    assert snapshot(model) == before


@pytest.mark.spec("FH-01-IT-04")
def test_fh_01_04_top_level_lists_every_chapter(model):
    result = run_script("handbook-index", model)

    assert result.returncode == 0
    user_top = (model / USER / "index.md").read_text(encoding="utf-8")
    assert user_top.index("[Getting started](getting-started/index.md)") < user_top.index(
        "[CLI integrations](cli-integrations/index.md)"
    )
    contributor_top = (model / CONTRIBUTOR / "index.md").read_text(encoding="utf-8")
    assert "[Release](release/index.md)" in contributor_top
    assert "[Contributing](contributing/index.md)" in contributor_top


@pytest.mark.spec("FH-02-IT-01")
def test_fh_02_01_check_names_the_stale_index(model):
    run_script("handbook-index", model)
    write(model, f"{USER}/cli-integrations/cli-differences.md", page_text("CLI differences"))
    before = snapshot(model)

    result = run_script("handbook-index", model, "--check")

    assert result.returncode != 0
    assert f"{USER}/cli-integrations/index.md" in result.stdout
    assert snapshot(model) == before


@pytest.mark.spec("FH-CT-01")
def test_rerun_changes_nothing_and_check_passes(model):
    run_script("handbook-index", model)
    written = snapshot(model)

    assert run_script("handbook-index", model).returncode == 0
    assert snapshot(model) == written
    assert run_script("handbook-index", model, "--check").returncode == 0


@pytest.mark.spec("FH-CT-02")
def test_a_stub_that_becomes_implemented_joins_the_list(model):
    write(model, f"{USER}/cli-integrations/opencode-desktop.md",
          page_text("OpenCode Desktop", "how-to", "implemented"))

    run_script("handbook-index", model)

    text = (model / USER / "cli-integrations/index.md").read_text(encoding="utf-8")
    assert "[OpenCode Desktop](opencode-desktop.md)" in text


@pytest.mark.spec("FH-CT-03")
def test_an_image_in_a_chapter_is_listed_by_no_list(model):
    (model / USER / "cli-integrations/diagram.png").write_bytes(b"\x89PNG")

    result = run_script("handbook-index", model)

    assert result.returncode == 0
    assert "diagram" not in (model / USER / "cli-integrations/index.md").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "title, description",
    [
        ("Add a CLI integration", "Add   the files  of one CLI."),
        ("Add  a CLI integration", "Add the files of one CLI."),
    ],
)
def test_a_run_of_spaces_survives_mdformat(model, title, description):
    """IMPL-0197: the repository mdformat hook runs before handbook-lint and must not change the index."""
    assert_index_survives_mdformat(model, title, description)


def test_a_bracketed_title_survives_mdformat(model):
    """IMPL-0202: a bracket in a title is escaped by the generator and kept by mdformat."""
    assert_index_survives_mdformat(model, "Add [CLI] integration", "Add the files of one CLI.")


def test_inline_code_keeps_its_two_spaces_through_mdformat(model):
    """IMPL-0203: the generator leaves the spaces of inline code as the author wrote them."""
    text = assert_index_survives_mdformat(model, "Add a CLI integration", 'Run `printf "a  b"`.')

    assert '`printf "a  b"`' in text


def assert_index_survives_mdformat(model, title, description) -> str:
    """Generate the index of one page, format it as the hook does, and check it again; return the index text."""
    write(model, f"{USER}/cli-integrations/add-an-integration.md",
          page_text(title, "how-to", order=20, description=description))
    assert run_script("handbook-index", model).returncode == 0

    subprocess.run(
        [str(SOURCE_SCRIPTS_DIR / "mdformat"), "--number", str(model / USER / "cli-integrations/index.md")],
        check=True, capture_output=True,
    )

    result = run_script("handbook-index", model, "--check")
    assert result.returncode == 0, result.stdout
    return (model / USER / "cli-integrations/index.md").read_text(encoding="utf-8")


def _page(path, order=100, title="T", type_="concept", description=""):
    return hi.Page(path, title, type_, "implemented", order, description)


def _chapter(pages):
    return hi.Folder("ch", {p.path: p for p in pages}, "", None, [], [], [])


class TestChapterBody:
    @pytest.mark.spec("FH-CT-04")
    def test_group_headings_follow_the_type_order(self):
        pages = [_page(f"ch/{t}.md", type_=t) for t in reversed(hi.TYPES)]

        body = hi.chapter_body(_chapter(pages))

        headings = [line for line in body.splitlines() if line.startswith("## ")]
        assert headings == ["## Tutorials", "## Concepts", "## How-to guides", "## Reference", "## Learning"]

    @pytest.mark.spec("FH-CT-05")
    def test_a_type_without_a_page_gets_no_heading(self):
        body = hi.chapter_body(_chapter([_page("ch/a.md", type_="reference")]))

        assert "## Reference" in body
        assert "Tutorials" not in body and "Concepts" not in body

    @pytest.mark.spec("FH-CT-06")
    def test_orders_sort_lower_first_with_negative_zero_and_default(self):
        pages = [_page("ch/d.md", 100, "Default"), _page("ch/e.md", 20, "Twenty"), _page("ch/c.md", 1, "One"),
                 _page("ch/b.md", 0, "Zero"), _page("ch/a.md", -5, "Minus")]

        body = hi.chapter_body(_chapter(pages))

        titles = [line.split("]")[0][3:] for line in body.splitlines() if line.startswith("- ")]
        assert titles == ["Minus", "Zero", "One", "Twenty", "Default"]

    @pytest.mark.spec("FH-CT-07")
    def test_ties_sort_by_title_then_by_path(self):
        pages = [_page("ch/z.md", 5, "Same"), _page("ch/y.md", 5, "Same"), _page("ch/x.md", 5, "Alpha")]

        body = hi.chapter_body(_chapter(pages))

        targets = [line.split("(")[1].rstrip(")") for line in body.splitlines() if line.startswith("- ")]
        assert targets == ["x.md", "y.md", "z.md"]

    @pytest.mark.spec("FH-CT-08")
    def test_an_entry_without_a_description_has_no_colon(self):
        body = hi.chapter_body(_chapter([_page("ch/a.md", title="Alone")]))

        assert "- [Alone](a.md)" in body.splitlines()

    @pytest.mark.spec("FH-CT-09")
    def test_a_stub_is_not_listed(self):
        stub = hi.Page("ch/s.md", "Stub", "concept", "stub", 100, "")

        assert hi.chapter_body(_chapter([stub])) == ""


class TestTopBody:
    def _chapters(self, rows):
        chapters = []
        for path, order, title in rows:
            page = hi.Page(f"{path}/index.md", title, "concept", "stub", order, "")
            chapters.append(hi.Folder(path, {}, "", page, [], [], []))
        return chapters

    @pytest.mark.spec("FH-CT-10")
    def test_chapters_sort_by_order_then_title_then_path(self):
        chapters = self._chapters([("c", 5, "Same"), ("b", 5, "Same"), ("a", 5, "Alpha"), ("d", 1, "Zed")])

        body = hi.top_body(chapters)

        assert [line.split("(")[1].rstrip(")") for line in body.splitlines()] == [
            "d/index.md", "a/index.md", "b/index.md", "c/index.md",
        ]

    @pytest.mark.spec("FH-CT-11")
    def test_a_stub_chapter_stays_in_the_list(self):
        assert "[Only stubs](s/index.md)" in hi.top_body(self._chapters([("s", 1, "Only stubs")]))


class TestSplice:
    @pytest.mark.spec("FH-CT-12")
    def test_text_outside_the_markers_keeps_its_bytes(self):
        text = f"head \r\n{START}old{END}\ttail\n"

        assert hi.splice(text, "") == f"head \r\n{START}\n\n{END}\ttail\n"

    @pytest.mark.spec("FH-CT-13")
    def test_a_body_sits_between_blank_lines(self):
        assert hi.splice(f"{START}\n{END}\n", "- x") == f"{START}\n\n- x\n\n{END}\n"


class TestMarkers:
    @pytest.mark.spec("FH-CT-14")
    @pytest.mark.parametrize(
        "text",
        [
            f"{END}\n",
            f"{START}\n",
            f"{START}\n{START}\n{END}\n",
            f"{START}\n{END}\n{END}\n",
            f"{END}\n{START}\n",
        ],
        ids=["missing-start", "missing-end", "start-twice", "end-twice", "end-before-start"],
    )
    def test_each_broken_marker_case_fails(self, text):
        assert hi.marker_failures("x/index.md", text)

    @pytest.mark.spec("FH-CT-15")
    def test_a_correct_pair_passes(self):
        assert hi.marker_failures("x/index.md", f"{START}\n{END}\n") == []

    @pytest.mark.spec("FH-CT-16")
    @pytest.mark.parametrize(
        "mode", [[], ["--check"]], ids=["write", "check"]
    )
    @pytest.mark.parametrize(
        "text",
        [f"{END}\n", f"{START}\n", f"{START}{START}{END}", f"{START}{END}{END}", f"{END}{START}"],
        ids=["missing-start", "missing-end", "start-twice", "end-twice", "end-before-start"],
    )
    def test_a_broken_pair_refuses_in_both_modes(self, model, text, mode):
        path = f"{USER}/cli-integrations/index.md"
        write(model, path, page_text("CLI integrations", order=80) + text)
        before = snapshot(model)

        result = run_script("handbook-index", model, *mode)

        assert result.returncode != 0
        assert path in result.stdout
        assert snapshot(model) == before


class TestFrontmatter:
    def _parse(self, text):
        return hi.parse_page("p.md", text)

    @pytest.mark.spec("FH-CT-17")
    def test_a_full_page_parses(self):
        page, failures = self._parse(page_text("A", "how-to", order=-5, description="One sentence."))

        assert failures == [] and page.order == -5 and page.description == "One sentence."

    @pytest.mark.spec("FH-CT-18")
    def test_order_defaults_to_100(self):
        assert self._parse(page_text("A"))[0].order == 100

    @pytest.mark.spec("FH-CT-19")
    @pytest.mark.parametrize(
        "field,value",
        [("order", "2.5"), ("order", "first"), ("order", "null"), ("title", '""'), ("title", "42"),
         ("title", "null"), ("type", "guide"), ("status", "planned")],
    )
    def test_a_bad_value_names_the_field(self, field, value):
        fields = {"title": "A", "type": "concept", "status": "implemented", field: value}
        text = "---\n" + "\n".join(f"{k}: {v}" for k, v in fields.items()) + "\n---\n"

        page, failures = self._parse(text)

        assert page is None
        assert [str(failure) for failure in failures if f"field {field}" in str(failure)]

    @pytest.mark.spec("FH-CT-20")
    def test_no_frontmatter_and_unparsable_frontmatter_fail(self):
        assert self._parse("# Heading\n")[0] is None
        assert self._parse("---\ntitle: [\n---\n")[0] is None


class TestPagesAtEveryDepth:
    """IMPL-0118: a hidden page and a page in a nested folder face BR-140 too."""

    @pytest.mark.spec("FH-CT-21")
    @pytest.mark.parametrize(
        "rel", ["cli-integrations/.draft.md", "cli-integrations/nested/bad.md", "cli-integrations/a/b/.bad.md"]
    )
    @pytest.mark.parametrize("mode", [[], ["--check"]], ids=["write", "check"])
    def test_a_page_without_frontmatter_refuses(self, model, rel, mode):
        write(model, f"{USER}/{rel}", "# No frontmatter\n")
        before = snapshot(model)

        result = run_script("handbook-index", model, *mode)

        assert result.returncode != 0
        assert f"{USER}/{rel}: field frontmatter" in result.stdout
        assert snapshot(model) == before

    @pytest.mark.spec("FH-CT-22")
    def test_a_marker_in_a_nested_index_is_checked(self, model):
        write(model, f"{USER}/cli-integrations/nested/index.md", page_text("Nested") + f"{START}\n")

        result = run_script("handbook-index", model)

        assert result.returncode != 0
        assert f"{USER}/cli-integrations/nested/index.md: markers" in result.stdout

    @pytest.mark.spec("FH-CT-23")
    def test_a_nested_page_joins_no_list(self, model):
        write(model, f"{USER}/cli-integrations/nested/ok.md", page_text("Nested ok", "how-to"))

        assert run_script("handbook-index", model).returncode == 0
        assert "Nested ok" not in (model / USER / "cli-integrations/index.md").read_text(encoding="utf-8")


class TestUnparsableDates:
    """IMPL-0119: a YAML scalar that cannot convert is a diagnostic, not a traceback."""

    @pytest.mark.spec("FH-CT-24")
    def test_an_invalid_date_is_a_frontmatter_failure(self):
        page, failures = hi.parse_page("p.md", "---\ntitle: 2000-01-99\ntype: concept\nstatus: implemented\n---\n")

        assert page is None
        assert [str(f) for f in failures] == ["p.md: field frontmatter: the frontmatter does not parse as YAML"]

    @pytest.mark.spec("FH-CT-25")
    def test_the_run_goes_on_to_the_other_handbook(self, model):
        write(model, f"{USER}/cli-integrations/add-an-integration.md",
              "---\ntitle: 2000-01-99\ntype: how-to\nstatus: implemented\n---\n")
        write(model, f"{CONTRIBUTOR}/release/ship.md", page_text("Ship a release", type_=None))

        result = run_script("handbook-index", model, "--check")

        assert "Traceback" not in result.stderr
        assert f"{USER}/cli-integrations/add-an-integration.md: field frontmatter" in result.stdout
        assert f"{CONTRIBUTOR}/release/ship.md: field type" in result.stdout


class TestSymlinks:
    """IMPL-0120: a link never leads the reader or the writer out of a handbook."""

    @pytest.mark.spec("FH-CT-26")
    def test_a_chapter_link_to_a_sibling_folder_refuses(self, model):
        outside = model / "elsewhere"
        write(model, "elsewhere/index.md", index_text("Elsewhere"))
        (model / USER / "linked").symlink_to(outside, target_is_directory=True)
        before = snapshot(model)

        result = run_script("handbook-index", model)

        assert result.returncode != 0
        assert f"{USER}/linked: symlink" in result.stdout
        assert snapshot(model) == before

    @pytest.mark.spec("FH-CT-27")
    def test_a_page_link_to_a_file_outside_refuses(self, model):
        write(model, "outside.md", page_text("Outside"))
        (model / USER / "cli-integrations/outside.md").symlink_to(model / "outside.md")

        result = run_script("handbook-index", model, "--check")

        assert result.returncode != 0
        assert f"{USER}/cli-integrations/outside.md: symlink" in result.stdout


class TestEverySymlinkIsRefused:
    """IMPL-0120, IMPL-0125: a link at any level is refused by path, and no read of a page raises."""

    @pytest.mark.spec("FH-CT-28")
    def test_a_linked_handbook_root_refuses_and_writes_nothing(self, model):
        sibling = model / "sibling"
        sibling.mkdir()
        write(model, "sibling/index.md", index_text("Sibling"))
        write(model, "sibling/ch/index.md", index_text("Chapter", order=1))
        write(model, "sibling/ch/page.md", page_text("Page", "how-to"))
        (model / CONTRIBUTOR).rename(model / "moved")
        (model / CONTRIBUTOR).symlink_to(sibling, target_is_directory=True)
        before = snapshot(model)

        result = run_script("handbook-index", model)

        assert result.returncode != 0
        assert f"{CONTRIBUTOR}: symlink" in result.stdout
        assert snapshot(model) == before

    @pytest.mark.spec("FH-CT-29")
    def test_a_linked_parent_of_a_root_is_refused(self, model):
        (model / "docs").rename(model / "docs-real")
        (model / "docs").symlink_to(model / "docs-real", target_is_directory=True)

        result = run_script("handbook-index", model, "--check")

        assert result.returncode != 0
        assert "docs: symlink" in result.stdout

    @pytest.mark.spec("FH-CT-30")
    def test_a_link_to_a_file_inside_the_handbook_is_refused(self, model):
        chapter = model / USER / "cli-integrations"
        (chapter / "alias.md").symlink_to(chapter / "how-the-clis-differ.md")

        result = run_script("handbook-index", model, "--check")

        assert result.returncode != 0
        assert f"{USER}/cli-integrations/alias.md: symlink" in result.stdout

    @pytest.mark.spec("FH-CT-31")
    def test_a_link_to_a_folder_inside_the_handbook_is_refused(self, model):
        (model / USER / "alias").symlink_to(model / USER / "cli-integrations", target_is_directory=True)

        result = run_script("handbook-index", model, "--check")

        assert result.returncode != 0
        assert f"{USER}/alias: symlink" in result.stdout

    @pytest.mark.spec("FH-CT-32")
    def test_a_link_that_is_no_markdown_file_is_refused(self, model):
        (model / USER / "cli-integrations/logo.png").symlink_to(model / "missing.png")

        result = run_script("handbook-index", model, "--check")

        assert f"{USER}/cli-integrations/logo.png: symlink" in result.stdout

    @pytest.mark.spec("FH-CT-33")
    def test_a_dangling_page_link_in_a_nested_folder_is_reported_without_a_traceback(self, model):
        write(model, f"{USER}/cli-integrations/nested/keep.md", page_text("Keep"))
        (model / USER / "cli-integrations/nested/draft.md").symlink_to(model / "missing.md")
        write(model, f"{CONTRIBUTOR}/release/ship.md", page_text("Ship a release", type_=None))

        result = run_script("handbook-index", model, "--check")

        assert "Traceback" not in result.stderr
        assert f"{USER}/cli-integrations/nested/draft.md: symlink" in result.stdout
        assert f"{CONTRIBUTOR}/release/ship.md: field type" in result.stdout

    @pytest.mark.spec("FH-CT-34")
    def test_an_unreadable_page_is_reported_by_path(self, model, monkeypatch):
        page = model / USER / "cli-integrations/add-an-integration.md"
        original = Path.read_bytes

        def read_bytes(self):
            if self == page:
                raise PermissionError(13, "Permission denied")
            return original(self)

        monkeypatch.setattr(Path, "read_bytes", read_bytes)

        _, text, failures = hi._read_page(model, page)

        assert text is None
        assert [str(failure) for failure in failures] == [
            f"{USER}/cli-integrations/add-an-integration.md: read: the page cannot be read (Permission denied)"
        ]


class TestLinkTargets:
    """IMPL-0121: a hash in a name stays part of the path."""

    @pytest.mark.spec("FH-CT-35")
    def test_a_hash_in_a_page_name_is_encoded(self):
        body = hi.chapter_body(_chapter([_page("ch/changes#2.md", title="Example")]))

        assert "- [Example](changes%232.md)" in body

    @pytest.mark.spec("FH-CT-36")
    def test_a_hash_in_a_chapter_name_is_encoded(self):
        page = _page("c#1/index.md", title="C")
        chapter = hi.Folder("h/c#1", {}, "", page, [], [], [])

        assert "- [C](c%231/index.md)" in hi.top_body([chapter])


class TestMarkerLiteralsInMetadata:
    """IMPL-0122: page metadata never adds a marker to a generated list."""

    @pytest.mark.spec("FH-CT-37")
    def test_a_marker_in_a_description_or_title_is_encoded(self, model):
        chapter = f"{USER}/cli-integrations"
        write(model, f"{chapter}/add-an-integration.md",
              page_text(f"Write {START} first", "how-to", description=f"Write {START} then {END} last."))

        assert run_script("handbook-index", model).returncode == 0
        text = (model / chapter / "index.md").read_text(encoding="utf-8")
        assert text.count(START) == 1 and text.count(END) == 1
        assert run_script("handbook-index", model, "--check").returncode == 0
