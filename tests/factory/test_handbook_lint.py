"""Checks of handbook-lint (ST-0452).

handbook-lint reports every broken page, folder, marker pair, duplicate
title, and stale page list of both handbooks in one run (validation-rules.md
BR-140 to BR-143, BR-146, BR-147). The integration tests run the script on
the model of test_handbook_index.py. The contract tests call its functions.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from conftest import load_script
from test_handbook_index import (
    CONTRIBUTOR,
    END,
    START,
    USER,
    build_model,
    index_text,
    page_text,
    run_script,
    snapshot,
    write,
)

lint = load_script("handbook-lint")

CHAPTER = f"{USER}/cli-integrations"


@pytest.fixture
def model(tmp_path: Path) -> Path:
    """The model of both handbooks with every page list written: lint passes."""
    build_model(tmp_path)
    assert run_script("handbook-index", tmp_path).returncode == 0
    return tmp_path


def report_lines(result) -> list[str]:
    return [line for line in result.stdout.splitlines() if line.strip()]


@pytest.mark.spec("FH-CT-38")
def test_the_model_passes(model):
    result = run_script("handbook-lint", model)

    assert result.returncode == 0, result.stdout
    assert report_lines(result) == []


def _break_type(base):
    write(base, f"{CHAPTER}/remove-an-integration.md", page_text("Remove a CLI integration", type_=None))


def _break_status(base):
    write(base, f"{CHAPTER}/remove-an-integration.md",
          page_text("Remove a CLI integration", "how-to", "planned", order=10))


def _folder_without_index(base):
    write(base, f"{CONTRIBUTOR}/testing/layers.md", page_text("Test layers", "how-to"))


def _nested_folder(base):
    write(base, f"{CHAPTER}/opencode/readme.txt", "x")


def _root_without_index(base):
    (base / CONTRIBUTOR / "index.md").unlink()


def _duplicate_titles(base):
    write(base, f"{CHAPTER}/add-cli.md", page_text("Add a CLI integration", "how-to", order=30))
    assert run_script("handbook-index", base).returncode == 0


def _reversed_markers(base):
    write(base, f"{CHAPTER}/index.md", page_text("CLI integrations", order=80) + f"{END}\n{START}\n")


@pytest.mark.spec("FH-02-IT-02")
@pytest.mark.parametrize(
    "defect,expected",
    [
        (_break_type, [f"{CHAPTER}/remove-an-integration.md", "field type"]),
        (_break_status, [f"{CHAPTER}/remove-an-integration.md", "field status"]),
        (_folder_without_index, [f"{CONTRIBUTOR}/testing/"]),
        (_nested_folder, [f"{CHAPTER}/opencode/"]),
        (_root_without_index, [f"{CONTRIBUTOR}/"]),
        (_duplicate_titles, [f"{CHAPTER}/add-an-integration.md", f"{CHAPTER}/add-cli.md", "Add a CLI integration"]),
        (_reversed_markers, [f"{CHAPTER}/index.md"]),
    ],
    ids=["no-type", "status-planned", "folder-no-index", "nested-folder", "root-no-index",
         "duplicate-title", "reversed-markers"],
)
def test_fh_02_02_each_failure_kind_is_reported_alone(model, defect, expected):
    defect(model)

    result = run_script("handbook-lint", model)

    assert result.returncode != 0
    lines = report_lines(result)
    assert len(lines) == 1, lines
    assert all(part in lines[0] for part in expected), lines[0]


@pytest.mark.spec("FH-02-IT-03")
def test_fh_02_03_one_run_reports_a_page_a_folder_and_a_stale_list(model):
    write(model, f"{CHAPTER}/add-an-integration.md", page_text("Add a CLI integration", type_=None))
    write(model, f"{CONTRIBUTOR}/testing/layers.md", page_text("Test layers", "how-to"))
    write(model, f"{CONTRIBUTOR}/contributing/new.md", page_text("A new page", "how-to"))
    before = snapshot(model)

    result = run_script("handbook-lint", model)

    assert result.returncode != 0
    out = result.stdout
    assert f"{CHAPTER}/add-an-integration.md" in out and "field type" in out
    assert f"{CONTRIBUTOR}/testing/" in out
    stale = [line for line in report_lines(result) if "out of date" in line]
    assert [line.split(":")[0] for line in stale] == [f"{CONTRIBUTOR}/contributing/index.md"]
    assert snapshot(model) == before


class TestPageRules:
    @pytest.mark.spec("FH-CT-39")
    @pytest.mark.parametrize(
        "kwargs,field",
        [
            ({"type_": None}, "type"),
            ({"status": None}, "status"),
            ({"title": None}, "title"),
            ({"title": 42}, "title"),
            ({"title": '""'}, "title"),
            ({"title": "null"}, "title"),
            ({"type_": "guide"}, "type"),
            ({"status": "planned"}, "status"),
            ({"status": "specified"}, "status"),
            ({"order": "first"}, "order"),
            ({"order": 2.5}, "order"),
        ],
        ids=["no-type", "no-status", "no-title", "title-42", "title-empty", "title-null", "type-guide",
             "status-planned", "status-specified", "order-first", "order-2.5"],
    )
    def test_a_bad_field_fails_and_names_it(self, model, kwargs, field):
        args = {"title": "Add a CLI integration", "type_": "how-to", "order": 20}
        args.update(kwargs)
        write(model, f"{CHAPTER}/add-an-integration.md", page_text(**args))

        result = run_script("handbook-lint", model)

        assert result.returncode != 0
        assert f"{CHAPTER}/add-an-integration.md: field {field}" in result.stdout

    @pytest.mark.spec("FH-CT-40")
    @pytest.mark.parametrize("order", [0, -5, 20])
    def test_an_integer_order_passes(self, model, order):
        write(model, f"{CHAPTER}/remove-an-integration.md",
              page_text("Remove a CLI integration", "how-to", order=order, description="Remove the files of one CLI from a project."))
        run_script("handbook-index", model)

        assert run_script("handbook-lint", model).returncode == 0

    @pytest.mark.spec("FH-CT-41")
    def test_a_page_without_a_frontmatter_block_fails(self, model):
        write(model, f"{CHAPTER}/add-an-integration.md", "# Add a CLI integration\n")

        result = run_script("handbook-lint", model)

        assert f"{CHAPTER}/add-an-integration.md: field frontmatter" in result.stdout

    @pytest.mark.spec("FH-CT-42")
    def test_frontmatter_that_does_not_parse_fails(self, model):
        write(model, f"{CHAPTER}/add-an-integration.md", "---\ntitle: [\n---\n")

        result = run_script("handbook-lint", model)

        assert f"{CHAPTER}/add-an-integration.md: field frontmatter" in result.stdout


class TestTitles:
    @pytest.mark.spec("FH-CT-43")
    def test_titles_that_differ_only_in_case_fail(self, model):
        write(model, f"{CHAPTER}/add-cli.md", page_text("Add a CLI Integration", "how-to", order=30))
        run_script("handbook-index", model)

        result = run_script("handbook-lint", model)

        assert result.returncode != 0
        assert "add-cli.md" in result.stdout and "add-an-integration.md" in result.stdout

    @pytest.mark.spec("FH-CT-44")
    def test_a_stub_may_share_a_title_with_an_implemented_page(self, model):
        write(model, f"{CHAPTER}/add-cli.md", page_text("Add a CLI integration", "how-to", "stub"))
        run_script("handbook-index", model)

        assert run_script("handbook-lint", model).returncode == 0

    @pytest.mark.spec("FH-CT-45")
    def test_two_chapters_may_share_a_title(self, model):
        for root in (USER, CONTRIBUTOR):
            write(model, f"{root}/shared/index.md", index_text("Shared", order=90))
            write(model, f"{root}/shared/one.md", page_text("One title", "how-to"))
        run_script("handbook-index", model)

        assert run_script("handbook-lint", model).returncode == 0


class TestOutOfScope:
    @pytest.mark.spec("FH-CT-46")
    def test_a_broken_link_and_the_word_must_do_not_fail(self, model):
        write(model, f"{CHAPTER}/how-the-clis-differ.md",
              page_text("How the CLIs differ", "concept", body="You must read [this](missing.md)."))

        assert run_script("handbook-lint", model).returncode == 0


class TestFunctions:
    @pytest.mark.spec("FH-CT-47")
    def test_duplicate_failures_group_by_casefolded_title(self):
        def page(path, title, status="implemented"):
            return lint.index.Page(path, title, "concept", status, 100, "")

        chapter = lint.index.Folder(
            "c", {p.path: p for p in (page("c/a.md", "Same"), page("c/b.md", "SAME"), page("c/s.md", "Same", "stub"))},
            "", None, [], [], [],
        )
        handbook = lint.index.Handbook("r", True, None, [chapter])

        failures = lint.duplicate_failures([handbook])

        assert [str(f) for f in failures] == ['c/a.md and c/b.md: implemented pages share the title "Same"']

    @pytest.mark.spec("FH-CT-48")
    def test_a_missing_root_is_a_failure(self, tmp_path):
        failures = lint.lint(tmp_path)

        assert {f.path for f in failures} == {f"{USER}/", f"{CONTRIBUTOR}/"}


class TestEveryDepth:
    @pytest.mark.spec("FH-CT-49")
    def test_a_hidden_page_fails_lint(self, model):
        write(model, f"{CHAPTER}/.draft.md", "# No frontmatter\n")

        result = run_script("handbook-lint", model)

        assert result.returncode != 0
        assert f"{CHAPTER}/.draft.md: field frontmatter" in result.stdout

    @pytest.mark.spec("FH-CT-50")
    def test_a_nested_folder_and_its_bad_page_are_both_named(self, model):
        write(model, f"{CHAPTER}/nested/bad.md", "# No frontmatter\n")

        out = run_script("handbook-lint", model).stdout

        assert f"{CHAPTER}/nested/: a chapter folder holds no folder" in out
        assert f"{CHAPTER}/nested/bad.md: field frontmatter" in out


@pytest.mark.spec("FH-CT-51")
def test_an_invalid_date_is_reported_next_to_a_failure_of_the_other_handbook(model):
    write(model, f"{CHAPTER}/add-an-integration.md", "---\ntitle: 2000-01-99\ntype: how-to\nstatus: implemented\n---\n")
    write(model, f"{CONTRIBUTOR}/release/ship.md", page_text("Ship a release", type_=None))

    result = run_script("handbook-lint", model)

    assert "Traceback" not in result.stderr
    assert f"{CHAPTER}/add-an-integration.md: field frontmatter" in result.stdout
    assert f"{CONTRIBUTOR}/release/ship.md: field type" in result.stdout


@pytest.mark.spec("FH-CT-52")
def test_a_linked_chapter_fails_lint(model):
    write(model, "elsewhere/index.md", index_text("Elsewhere"))
    (model / USER / "linked").symlink_to(model / "elsewhere", target_is_directory=True)

    result = run_script("handbook-lint", model)

    assert result.returncode != 0
    assert f"{USER}/linked: symlink" in result.stdout


@pytest.mark.spec("FH-CT-53")
def test_a_dangling_nested_link_and_an_invalid_page_are_both_reported(model):
    write(model, f"{CHAPTER}/nested/keep.md", page_text("Keep"))
    (model / CHAPTER / "nested/draft.md").symlink_to(model / "missing.md")
    write(model, f"{CONTRIBUTOR}/release/ship.md", "# No frontmatter\n")

    result = run_script("handbook-lint", model)

    assert "Traceback" not in result.stderr
    assert f"{CHAPTER}/nested/draft.md: symlink" in result.stdout
    assert f"{CONTRIBUTOR}/release/ship.md: field frontmatter" in result.stdout


@pytest.mark.spec("FH-CT-54")
def test_a_linked_handbook_root_fails_lint(model):
    (model / CONTRIBUTOR).rename(model / "moved")
    (model / CONTRIBUTOR).symlink_to(model / "moved", target_is_directory=True)

    result = run_script("handbook-lint", model)

    assert result.returncode != 0
    assert f"{CONTRIBUTOR}: symlink" in result.stdout


@pytest.mark.spec("FH-CT-55")
def test_the_cli_writes_no_bytecode_beside_the_scripts(model, tmp_path_factory):
    import os
    import shutil

    from conftest import SOURCE_SCRIPTS_DIR

    scripts = tmp_path_factory.mktemp("scripts")
    for name in ("handbook-index", "handbook-lint"):
        shutil.copy(SOURCE_SCRIPTS_DIR / name, scripts / name)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}

    result = subprocess.run(
        [sys.executable, str(scripts / "handbook-lint")], cwd=model, capture_output=True, text=True, env=env,
    )

    assert result.returncode == 0, result.stdout
    assert sorted(p.name for p in scripts.iterdir()) == ["handbook-index", "handbook-lint"]
