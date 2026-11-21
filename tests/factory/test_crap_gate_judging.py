"""Contract tests: the judging of crap-score without git and without a subprocess.

docs/spec/features/crap-gate-setup.feature, Rule "Implementation agent gets one
verdict for the functions a story changed". Each test calls a function of
packages/factory/scripts/crap-score directly.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from conftest import load_script

cs = load_script("crap-score")

FINDING_LINT = "packages/factory/scripts/finding-lint"


def _row(function: str, start: int, end: int, file: str = FINDING_LINT) -> dict:
    return {
        "file": file, "function": function, "start_line": start, "end_line": end,
        "complexity": 9, "coverage_pct": 100,
    }


TREE = _row("tree_severity", 10, 28)
BUG_BAR = _row("bug_bar_level", 30, 48)


def _names(rows: list[dict]) -> list[str]:
    return [row["function"] for row in rows]


# --- CG-04-CT-01: the formula, the rounding, and the threshold --------------


@pytest.mark.spec("CG-04-CT-01")
@pytest.mark.parametrize(
    ("score", "result"), [("8.004", "pass"), ("8.006", "fail"), ("8.00", "pass")]
)
def test_cg_04_the_rounded_score_decides_the_verdict(score, result):
    """Scenario Outline: The gate compares the threshold with the score rounded to two decimals."""
    assert cs.verdict(Decimal(score), Decimal(8)) == result


@pytest.mark.spec("CG-04-CT-01")
def test_cg_04_the_score_rounds_half_up():
    """Complexity 8 at 87.5 % scores exactly 8.125, and half up gives 8.13 (DEC-36)."""
    score = cs.crap_formula(8, 87.5)
    assert score == Decimal("8.125")
    assert cs.rounded(score) == Decimal("8.13")
    assert cs.verdict(score, Decimal("8.13")) == "pass"
    assert cs.verdict(score, Decimal("8.12")) == "fail"


@pytest.mark.spec("CG-04-CT-01")
@pytest.mark.parametrize(
    ("complexity", "coverage", "score"), [(9, 100, "9.00"), (3, 0, "12.00"), (3, 100, "3.00")]
)
def test_cg_04_the_formula_at_its_ends(complexity, coverage, score):
    assert cs.rounded(cs.crap_formula(complexity, coverage)) == Decimal(score)


@pytest.mark.spec("CG-04-CT-01")
def test_cg_04_the_report_row_holds_the_score_and_the_result():
    """Scenario: A changed function above the threshold fails the gate and is named."""
    row = cs.report_row(TREE, Decimal(8))
    assert row == {**TREE, "crap_score": 9.0, "pass_fail": "fail"}


# --- CG-04-CT-02: the choice of the judged functions -----------------------


def _changes(lines=(), deletions=()) -> dict:
    return {FINDING_LINT: cs.FileChanges(set(lines), list(deletions))}


@pytest.mark.spec("CG-04-CT-02")
def test_cg_04_a_changed_line_judges_only_its_function():
    """Scenario: A function above the threshold that the story does not change passes."""
    assert _names(cs.judged_rows([TREE, BUG_BAR], _changes(lines=[15]))) == ["tree_severity"]


@pytest.mark.spec("CG-04-CT-02")
@pytest.mark.parametrize("line", [10, 28])
def test_cg_04_the_first_and_the_last_line_belong_to_the_function(line):
    assert _names(cs.judged_rows([TREE, BUG_BAR], _changes(lines=[line]))) == ["tree_severity"]


@pytest.mark.spec("CG-04-CT-02")
def test_cg_04_a_deletion_inside_a_function_judges_it():
    """Scenario: A function in which lines were only deleted counts as changed (DEC-15)."""
    assert _names(cs.judged_rows([TREE, BUG_BAR], _changes(deletions=[14]))) == ["tree_severity"]


@pytest.mark.spec("CG-04-CT-02")
@pytest.mark.parametrize("after", [28, 29])
def test_cg_04_a_deletion_between_two_functions_counts_for_both(after):
    """Scenario: A deletion between two functions counts for both neighbours (DEC-37)."""
    rows = cs.judged_rows([TREE, BUG_BAR], _changes(deletions=[after]))
    assert _names(rows) == ["tree_severity", "bug_bar_level"]


@pytest.mark.spec("CG-04-CT-02")
def test_cg_04_a_deletion_between_two_functions_skips_a_farther_function():
    first = _row("first", 1, 5)
    rows = cs.judged_rows([first, TREE, BUG_BAR], _changes(deletions=[29]))
    assert _names(rows) == ["tree_severity", "bug_bar_level"]


@pytest.mark.spec("CG-04-CT-02")
def test_cg_04_a_change_of_another_file_judges_nothing():
    changes = {"packages/factory/scripts/other": cs.FileChanges({15}, [])}
    assert cs.judged_rows([TREE, BUG_BAR], changes) == []


@pytest.mark.spec("CG-04-CT-02")
def test_cg_04_all_judges_every_kept_row():
    """Scenario: crap-score --all judges every measured function."""
    assert _names(cs.judged_rows([TREE, BUG_BAR], None)) == ["tree_severity", "bug_bar_level"]


@pytest.mark.spec("CG-04-CT-02")
def test_cg_04_the_diff_reader_finds_changed_lines_and_deletions():
    diff = (
        "diff --git a/x b/x\n--- a/x\n+++ b/x\n"
        "@@ -15 +15 @@\n-a\n+b\n"
        "@@ -29,2 +28,0 @@\n-c\n-d\n"
        "@@ -40,0 +40,2 @@\n+e\n+f\n"
        "diff --git a/gone b/gone\n--- a/gone\n+++ /dev/null\n@@ -1 +0,0 @@\n-g\n"
    )
    changes = cs.parse_diff(diff)
    assert set(changes) == {"x"}
    assert changes["x"].lines == {15, 40, 41}
    assert changes["x"].deletions == [28]


# --- CG-04-CT-03 and CG-04-CT-09: files, exclude, and the glob dialect -----

BACKEND = cs.Measure(
    "backend", "packages/server/backend/**", "true", ("**/db/alembic/versions/**",)
)


@pytest.mark.spec("CG-04-CT-03")
@pytest.mark.parametrize(
    "file",
    [
        "packages/server/backend/src/db/alembic/versions/0042_orders.py",
        "packages/server/frontend/src/main.ts",
    ],
)
def test_cg_04_a_row_outside_files_or_inside_exclude_is_never_kept(file):
    """Scenario Outline: crap-score applies files and exclude to the rows a measuring command reports."""
    row = {**_row("create_app", 1, 30, file), "complexity": 20, "coverage_pct": 0}
    assert cs.kept_rows(BACKEND, [row]) == []


@pytest.mark.spec("CG-04-CT-03")
def test_cg_04_a_row_inside_files_is_kept():
    row = _row("create_app", 1, 30, "packages/server/backend/src/app.py")
    assert cs.kept_rows(BACKEND, [row]) == [row]


@pytest.mark.spec("CG-04-CT-09")
@pytest.mark.parametrize(
    ("pattern", "path", "kept"),
    [
        ("packages/factory/scripts/*", "packages/factory/scripts/finding-lint", True),
        ("packages/factory/scripts/*", "packages/factory/scripts/lib/report.py", False),
        (
            "**/db/alembic/versions/**",
            "packages/server/backend/src/db/alembic/versions/0042_orders.py",
            True,
        ),
    ],
)
def test_cg_04_files_and_exclude_use_one_glob_dialect(pattern, path, kept):
    """Scenario Outline: files and exclude use one glob dialect (DEC-35)."""
    row = _row("f", 1, 2, path)
    as_files = cs.kept_rows(cs.Measure("m", pattern, "true"), [row])
    as_exclude = cs.kept_rows(cs.Measure("m", "**", "true", (pattern,)), [row])
    assert (as_files == [row]) is kept
    assert (as_exclude == []) is kept


# --- CG-04-CT-05: the reader of gates.crap-score ---------------------------

MEASURE = (
    "      - name: python\n"
    "        files: \"packages/factory/scripts/*\"\n"
    "        command: \"scripts/crap-measure-stub\"\n"
)


def _settings(tmp_path, entry: str, key: str = "crap-score"):
    docs = tmp_path / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "testing.yaml").write_text(
        f'test_command: "true"\ngates:\n  {key}:\n{entry}', encoding="utf-8"
    )
    return lambda: cs.read_settings(tmp_path)


FULL = "    enabled: true\n    threshold: 8\n    timeout_minutes: 10\n    measures:\n" + MEASURE


@pytest.mark.spec("CG-04-CT-05")
def test_cg_04_the_reader_reads_the_three_values(tmp_path):
    settings = _settings(tmp_path, FULL)()
    assert settings.threshold == Decimal(8)
    assert settings.timeout_minutes == 10
    assert settings.measures == (
        cs.Measure("python", "packages/factory/scripts/*", "scripts/crap-measure-stub"),
    )


@pytest.mark.spec("CG-04-CT-05")
def test_cg_04_a_disabled_entry_is_read_in_full(tmp_path):
    """Scenario: A disabled gate that a story names runs in full."""
    settings = _settings(tmp_path, FULL.replace("enabled: true", "enabled: false"))()
    assert settings.threshold == Decimal(8)


@pytest.mark.spec("CG-04-CT-05")
@pytest.mark.parametrize("key", ["threshold", "timeout_minutes", "measures"])
def test_cg_04_a_missing_value_names_the_key(tmp_path, key):
    """Scenario Outline: An enabled gate without a required value cannot measure."""
    lines = FULL.splitlines(keepends=True)
    if key == "measures":
        entry = "".join(lines[:3])
    else:
        entry = "".join(line for line in lines if not line.strip().startswith(f"{key}:"))
    with pytest.raises(cs.GateError, match=rf"has no {key}$"):
        _settings(tmp_path, entry)()


@pytest.mark.spec("CG-04-CT-05")
@pytest.mark.parametrize("field", ["name", "files", "command"])
def test_cg_04_a_measure_without_a_field_names_the_field(tmp_path, field):
    """Scenario Outline: A measure without a required field cannot measure."""
    fields = {"name": "python", "files": "packages/factory/scripts/*", "command": "true"}
    del fields[field]
    items = [f"{key}: \"{value}\"" for key, value in fields.items()]
    measure = "      - " + "\n        ".join(items) + "\n"
    entry = FULL.replace(MEASURE, measure)
    with pytest.raises(cs.GateError, match=rf"has no field {field}$"):
        _settings(tmp_path, entry)()


@pytest.mark.spec("CG-04-CT-05")
def test_cg_04_an_empty_measures_list_names_the_list(tmp_path):
    """Scenario: An empty measures list cannot measure."""
    entry = FULL.replace("    measures:\n" + MEASURE, "    measures: []\n")
    with pytest.raises(cs.GateError, match="measures .* is an empty list"):
        _settings(tmp_path, entry)()


@pytest.mark.spec("CG-04-CT-05")
def test_cg_04_two_measures_with_one_name_name_both(tmp_path):
    """Scenario: Two measures with one name cannot measure."""
    entry = FULL + MEASURE
    with pytest.raises(cs.GateError, match="measures 1 and 2 .* both have the name python"):
        _settings(tmp_path, entry)()


@pytest.mark.spec("CG-04-CT-05")
def test_cg_04_no_entry_names_the_setup_skill(tmp_path):
    with pytest.raises(cs.GateError, match="no entry gates.crap-score.*setup-crap-score"):
        _settings(tmp_path, "    threshold: 8\n", key="license-check")()


# --- CG-04-CT-06: the call -------------------------------------------------


@pytest.mark.spec("CG-04-CT-06")
@pytest.mark.parametrize(
    ("argv", "word"),
    [(["--story-id", "ST-0350"], "neither"), (["--base", "feature/login", "--all"], "both")],
)
def test_cg_04_a_wrong_call_exits_2_before_it_reads_a_setting(monkeypatch, capsys, argv, word):
    """Scenarios: A call without --base or --all, and a call with both, cannot measure."""

    def no_setting(root):
        raise AssertionError("read a setting")

    monkeypatch.setattr(cs, "read_settings", no_setting)
    assert cs.main(argv) == 2
    err = capsys.readouterr().err
    assert "--base" in err
    assert "--all" in err
    assert word in err


# --- CG-04-CT-08: the name of the report -----------------------------------


@pytest.mark.spec("CG-04-CT-08")
@pytest.mark.parametrize(
    ("env", "branch", "name"),
    [
        ("ST-0350", "story/ST-0351", "ST-0350"),
        (None, "story/ST-0350", "ST-0350"),
        (None, "story/BUG-0090", "BUG-0090"),
        (None, None, "adhoc"),
    ],
)
def test_cg_04_the_report_name_follows_the_environment(monkeypatch, env, branch, name):
    """Scenario Outline: Without --story-id the report takes its name from the environment."""
    monkeypatch.delenv("STORY_ID", raising=False)
    if env:
        monkeypatch.setenv("STORY_ID", env)
    monkeypatch.setattr(cs, "current_branch", lambda: branch)
    assert cs.detect_story_id(None) == name


@pytest.mark.spec("CG-04-CT-08")
def test_cg_04_the_story_id_argument_comes_first_and_holds_no_slash(monkeypatch):
    monkeypatch.setenv("STORY_ID", "ST-0351")
    assert cs.detect_story_id("ST-0350") == "ST-0350"
    assert "/" not in cs.detect_story_id("story/ST-0350")
