"""Contract tests: the judging of crap-score without git and without a subprocess.

docs/spec/features/crap-gate-setup.feature, Rule "Implementation agent gets one
verdict for the functions a story changed". Each test calls a function of
packages/factory/scripts/crap-score directly.
"""

from __future__ import annotations

import sys
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
def test_cg_04_a_large_complexity_scores_exactly():
    """Complexity 10**13 at 0 % scores 10**26 + 10**13, beyond 28 digits, without a traceback."""
    assert cs.rounded(cs.crap_formula(10**13, 0)) == Decimal(10**26 + 10**13)


@pytest.mark.spec("CG-04-CT-01")
def test_cg_04_the_largest_values_of_the_shape_check_round_without_a_traceback():
    """The largest complexity a float holds, with the smallest float coverage."""
    complexity = int(sys.float_info.max)
    score = cs.rounded(cs.crap_formula(complexity, 5e-324))
    assert cs.verdict(score, Decimal(8)) == "fail"
    assert score > Decimal(complexity) ** 2 * Decimal("0.99")


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


# --- CG-04-CT-10: deletions outside every function (DEC-51) ----------------


@pytest.mark.spec("CG-04-CT-10")
@pytest.mark.parametrize("after", [48, 60])
def test_cg_04_a_deletion_below_the_last_function_counts_for_it(after):
    """A deletion below the last function may cut its end, so it counts for that function (DEC-51)."""
    rows = cs.judged_rows([TREE, BUG_BAR], _changes(deletions=[after]))
    assert _names(rows) == ["bug_bar_level"]


@pytest.mark.spec("CG-04-CT-10")
@pytest.mark.parametrize("after", [0, 9])
def test_cg_04_a_deletion_above_the_first_function_judges_none(after):
    """Lines above the first function lie outside every function (DEC-51)."""
    assert cs.judged_rows([TREE, BUG_BAR], _changes(deletions=[after])) == []


# --- CG-04-CT-07: the shape check of a report -------------------------------

PYTHON = cs.Measure("python", "packages/factory/scripts/*", "true")


def _without(key: str) -> dict:
    row = dict(TREE)
    del row[key]
    return row


@pytest.mark.spec("CG-04-CT-07")
@pytest.mark.parametrize("report", [{"rows": []}, "rows", None, 3])
def test_cg_04_a_report_that_is_no_array_names_the_measure(report):
    """Scenario: A report in the wrong shape cannot measure."""
    with pytest.raises(cs.GateError, match="measure python .*no JSON array"):
        cs.check_report(PYTHON, report)


@pytest.mark.spec("CG-04-CT-07")
def test_cg_04_a_row_that_is_no_object_names_the_measure():
    with pytest.raises(cs.GateError, match=r"measure python .*row 2\b.*no JSON object"):
        cs.check_report(PYTHON, [TREE, ["tree_severity"]])


@pytest.mark.spec("CG-04-CT-07")
@pytest.mark.parametrize("key", cs.FUNCTION_FIELDS)
def test_cg_04_a_row_without_a_field_names_the_measure_and_the_field(key):
    """Scenario: A report in the wrong shape cannot measure, for each of the six fields."""
    with pytest.raises(cs.GateError, match=rf"measure python .*without the field {key}\b"):
        cs.check_report(PYTHON, [BUG_BAR, _without(key)])


@pytest.mark.spec("CG-04-CT-07")
@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("coverage_pct", 120),
        ("coverage_pct", -1),
        ("coverage_pct", "87"),
        ("coverage_pct", float("nan")),
        ("complexity", "9"),
        ("complexity", 0),
        ("complexity", 2.5),
        ("complexity", True),
        ("start_line", 0),
        ("end_line", None),
        ("file", ""),
        ("function", ""),
        ("function", 7),
    ],
)
def test_cg_04_a_value_outside_the_schema_names_the_measure_and_the_field(key, value):
    """BR-130: a value that breaks measure-output-rows.json is a wrong shape (DEC-42)."""
    row = {**TREE, key: value}
    with pytest.raises(cs.GateError, match=rf"measure python .*\b{key}\b"):
        cs.check_report(PYTHON, [row])


@pytest.mark.spec("CG-04-CT-07")
def test_cg_04_start_line_above_end_line_names_the_function_and_the_two_lines():
    """Scenario: A row whose start_line lies above its end_line is in the wrong shape."""
    row = {**TREE, "start_line": 40, "end_line": 12}
    with pytest.raises(cs.GateError) as caught:
        cs.check_report(PYTHON, [row])
    message = str(caught.value)
    for part in ("measure python", "tree_severity", "start_line 40", "end_line 12"):
        assert part in message


@pytest.mark.spec("CG-04-CT-07")
def test_cg_04_valid_rows_pass_the_shape_check():
    """A parse_error row without the six fields is no wrong shape (DEC-34)."""
    parse_error = {"file": FINDING_LINT, "parse_error": "invalid syntax (line 3)"}
    one_line = {**TREE, "start_line": 12, "end_line": 12, "coverage_pct": 87.5}
    rows = [TREE, parse_error, one_line]
    assert cs.check_report(PYTHON, rows) == rows


@pytest.mark.spec("CG-04-CT-07")
@pytest.mark.parametrize("row", [{"file": FINDING_LINT, "parse_error": ""}, {"parse_error": "x"}])
def test_cg_04_a_parse_error_row_in_the_wrong_shape_names_the_measure(row):
    with pytest.raises(cs.GateError, match="measure python"):
        cs.check_report(PYTHON, [row])


@pytest.mark.spec("CG-04-CT-07")
@pytest.mark.parametrize("value", [None, ""])
def test_cg_04_a_function_row_with_an_empty_parse_error_is_a_function_row(value):
    """IMPL-0078: the schema accepts the six fields with parse_error null, so the row is judged."""
    rows = cs.check_report(PYTHON, [{**TREE, "parse_error": value}])
    assert rows == [TREE]
    judged = cs.judged_rows(rows, _changes(lines=[15]))
    assert cs.report_row(judged[0], Decimal(8))["crap_score"] == 9.0


@pytest.mark.spec("CG-04-CT-07")
@pytest.mark.parametrize("key", ["start_line", "end_line", "complexity", "coverage_pct"])
def test_cg_04_a_number_too_large_for_a_float_names_the_field(key):
    """A JSON integer such as 10**400 gives exit 2 and no OverflowError traceback."""
    row = {**TREE, key: 10**400}
    with pytest.raises(cs.GateError, match=rf"measure python .*\b{key}\b"):
        cs.check_report(PYTHON, [row])


@pytest.mark.spec("CG-04-CT-07")
def test_cg_04_a_wrong_shape_writes_no_report(tmp_path, monkeypatch, capsys):
    """BR-133: on exit 2 the earlier report stays and no new report appears."""
    settings = cs.Settings(Decimal(8), 10, (PYTHON,))
    monkeypatch.setattr(cs, "read_settings", lambda root: settings)
    monkeypatch.setattr(cs, "run_measure", lambda measure, root, clock: [_without("end_line")])
    # Outside a git repository, the trusted gate source reads no branch of this repository (ST-0450).
    monkeypatch.chdir(tmp_path)
    report_dir = tmp_path / "reports"
    argv = ["--all", "--story-id", "ST-0350", "--report-dir", str(report_dir)]
    assert cs.main(argv) == 2
    err = capsys.readouterr().err
    assert "python" in err
    assert "end_line" in err
    assert not report_dir.exists()


# --- CG-04-CT-04: the two duplicate checks ----------------------------------

APP = "packages/server/backend/src/app.py"
BACKEND_ONLY = cs.Measure("backend", "packages/server/backend/**", "true")


def _measure_all(monkeypatch, reports: dict[str, list[dict]], *measures):
    monkeypatch.setattr(cs, "run_measure", lambda measure, root, clock: reports[measure.name])
    return cs.measure_all(cs.Settings(Decimal(8), 10, measures), None)


@pytest.mark.spec("CG-04-CT-04")
def test_cg_04_one_qualified_name_twice_in_a_file_names_the_file_and_the_name(monkeypatch):
    """Scenario: A file that holds the same qualified name twice cannot measure."""
    parser = "packages/server/backend/src/orders/parser.py"
    rows = [_row("Parser.parse", 3, 9, parser), _row("Parser.parse", 20, 30, parser)]
    with pytest.raises(cs.GateError) as caught:
        _measure_all(monkeypatch, {"backend": rows}, BACKEND_ONLY)
    message = str(caught.value)
    for part in ("measure backend", parser, "Parser.parse"):
        assert part in message


@pytest.mark.spec("CG-04-CT-04")
def test_cg_04_two_measures_that_keep_one_function_name_both(monkeypatch):
    """Scenario: Two measures that report the same function cannot measure."""
    python = cs.Measure("python", "packages/**/*.py", "true")
    row = _row("create_app", 1, 30, APP)
    with pytest.raises(cs.GateError) as caught:
        _measure_all(monkeypatch, {"backend": [row], "python": [row]}, BACKEND_ONLY, python)
    message = str(caught.value)
    for part in ("create_app", "backend", "python"):
        assert part in message


@pytest.mark.spec("CG-04-CT-04")
def test_cg_04_a_dropped_row_counts_in_no_duplicate_check(monkeypatch):
    """Scenario: A row that the files pattern drops counts in no duplicate check."""
    python = cs.Measure("python", "packages/factory/scripts/*", "true")
    row = _row("create_app", 1, 30, APP)
    kept = _measure_all(monkeypatch, {"backend": [row], "python": [row]}, BACKEND_ONLY, python)
    assert kept == [row]


@pytest.mark.spec("CG-04-CT-04")
def test_cg_04_an_excluded_row_counts_in_no_duplicate_check(monkeypatch):
    """BR-131: a row that exclude drops is no kept row either."""
    backend = cs.Measure("backend", "packages/server/backend/**", "true", ("**/src/*.py",))
    row = _row("create_app", 1, 30, APP)
    kept = _measure_all(monkeypatch, {"backend": [row, dict(row)]}, backend)
    assert kept == []


@pytest.mark.spec("CG-04-CT-04")
def test_cg_04_one_name_in_two_files_is_no_duplicate(monkeypatch):
    other = "packages/server/backend/src/cli.py"
    rows = [_row("main", 1, 9, APP), _row("main", 1, 9, other)]
    assert _measure_all(monkeypatch, {"backend": rows}, BACKEND_ONLY) == rows


# --- CG-05-CT-01: the register parser ----------------------------------------

HEADER = (
    "| File | Function | Accepted score | Reason | Accepted by |\n"
    "| ---- | -------- | -------------- | ------ | ----------- |\n"
)
TREE_ROW = f"| `{FINDING_LINT}` | `tree_severity` | 9 | Each branch handles one finding class | A. Example |\n"


def _register(rows: str, section: str = "## CRAP score") -> str:
    return f"# Exceptions\n\n{section}\n\n{HEADER}{rows}\n## Mutation testing\n\nNo rows.\n"


@pytest.mark.spec("CG-05-CT-01")
def test_cg_05_a_row_names_the_function_its_score_and_its_reason():
    exceptions = cs.parse_register(_register(TREE_ROW))
    row = exceptions[(FINDING_LINT, "tree_severity")]
    assert row.accepted_score == Decimal(9)
    assert row.reason == "Each branch handles one finding class"
    assert row.accepted_by == "A. Example"
    assert list(exceptions) == [(FINDING_LINT, "tree_severity")]


@pytest.mark.spec("CG-05-CT-01")
def test_cg_05_the_parser_reads_only_the_section_for_the_crap_score():
    """Scenario: crap-score reads only the section for the CRAP score."""
    text = (
        "# Exceptions\n\n## Mutation testing\n\n" + HEADER + TREE_ROW
        + "\n## CRAP score\n\nNo function is accepted.\n"
    )
    assert cs.parse_register(text) == {}


@pytest.mark.spec("CG-05-CT-01")
def test_cg_05_a_register_without_the_section_has_no_exceptions():
    assert cs.parse_register("# Exceptions\n\n## Mutation testing\n\n" + HEADER + TREE_ROW) == {}


@pytest.mark.spec("CG-05-CT-01")
@pytest.mark.parametrize(
    ("row", "word"),
    [
        (f"| `{FINDING_LINT}` | `tree_severity` | 9 |  | A. Example |\n", "Reason"),
        (f"| `{FINDING_LINT}` | `tree_severity` | nine | Old code | A. Example |\n", "nine"),
        (f"| `{FINDING_LINT}` | `tree_severity` | 9 | Old code |\n", "cells"),
    ],
)
def test_cg_05_a_broken_row_names_the_row(row, word):
    """Scenario Outline: A broken exceptions-register row cannot measure."""
    with pytest.raises(cs.GateError) as caught:
        cs.parse_register(_register(row))
    message = str(caught.value)
    assert "line 7" in message
    assert word in message
    assert "docs/findings/exceptions.md" in message


@pytest.mark.spec("CG-05-CT-01")
def test_cg_05_two_rows_for_one_function_name_both_rows():
    """Scenario: Two exceptions-register rows for one function cannot measure (DEC-38)."""
    second = TREE_ROW.replace("| 9 |", "| 12 |")
    with pytest.raises(cs.GateError) as caught:
        cs.parse_register(_register(TREE_ROW + second))
    message = str(caught.value)
    for part in ("lines 7 and 8", FINDING_LINT, "tree_severity"):
        assert part in message


@pytest.mark.spec("CG-05-CT-01")
def test_cg_05_a_table_with_other_columns_names_the_columns():
    text = _register(TREE_ROW).replace("| Reason |", "| Why |")
    with pytest.raises(cs.GateError, match="File, Function, Accepted score, Reason, Accepted by"):
        cs.parse_register(text)


# --- CG-05-CT-02: the accept rule --------------------------------------------


def _accepted(score: str) -> cs.ExceptionRow:
    return cs.ExceptionRow(FINDING_LINT, "tree_severity", Decimal(score), "Old code", "A. Example", 8)


@pytest.mark.spec("CG-05-CT-02")
@pytest.mark.parametrize(("score", "result"), [("9.004", "accepted"), ("9.006", "fail"), ("10", "fail")])
def test_cg_05_the_rounded_score_is_compared_with_the_accepted_score(score, result):
    """Scenario Outline: The gate compares the accepted score with the score rounded to two decimals."""
    assert cs.verdict(Decimal(score), Decimal(8), _accepted("9")) == result


@pytest.mark.spec("CG-05-CT-02")
@pytest.mark.parametrize(("accepted", "result"), [("8.13", "accepted"), ("8.12", "fail")])
def test_cg_05_the_rounding_rounds_half_up_against_the_accepted_score(accepted, result):
    """Scenario Outline: The rounding rounds half up (DEC-36)."""
    assert cs.verdict(cs.crap_formula(8, 87.5), Decimal(8), _accepted(accepted)) == result


@pytest.mark.spec("CG-05-CT-02")
def test_cg_05_a_row_names_a_method_by_its_qualified_name():
    """Scenario: An exceptions-register row names a method by its qualified name (DEC-12)."""
    parser = "packages/server/backend/src/orders/parser.py"
    accepted = cs.ExceptionRow(parser, "Parser.parse", Decimal(12), "Old parser", "A. Example", 8)
    exceptions = {(parser, "Parser.parse"): accepted}
    rows = [_row(name, 1, 9, parser) | {"complexity": 12} for name in ("Parser.parse", "Lexer.parse")]
    results = [cs.report_row(row, Decimal(8), exceptions) for row in rows]
    assert [r["pass_fail"] for r in results] == ["accepted", "fail"]


@pytest.mark.spec("CG-05-CT-02")
def test_cg_05_a_function_at_or_below_the_threshold_passes_without_the_reason():
    """Scenario: A function with an exceptions-register row that scores at or below the threshold passes."""
    exceptions = {(FINDING_LINT, "tree_severity"): _accepted("9")}
    result = cs.report_row(TREE | {"complexity": 8}, Decimal(8), exceptions)
    assert result["pass_fail"] == "pass"
    line = cs._describe(result, exceptions)
    assert line == f"PASS {FINDING_LINT} tree_severity 8.00"


@pytest.mark.spec("CG-05-CT-02")
def test_cg_05_an_accepted_function_shows_its_score_and_reason():
    exceptions = {(FINDING_LINT, "tree_severity"): _accepted("9")}
    result = cs.report_row(TREE, Decimal(8), exceptions)
    assert result == {**TREE, "crap_score": 9.0, "pass_fail": "accepted"}
    assert cs._describe(result, exceptions) == f"ACCEPTED {FINDING_LINT} tree_severity 9.00: Old code"


# --- CG-04-CT-11: the shape check covers rows that the filter drops (ST-0445) -


@pytest.mark.spec("CG-04-CT-11")
def test_cg_04_the_shape_check_covers_rows_that_the_filter_drops(monkeypatch):
    """Scenario: The shape check covers rows that the filter drops (DEC-53)."""
    row = _row("mount", 1, 20, "packages/server/frontend/src/main.ts")
    del row["end_line"]
    assert cs.kept_rows(BACKEND_ONLY, [row]) == []
    with pytest.raises(cs.GateError) as caught:
        _measure_all(monkeypatch, {"backend": [row]}, BACKEND_ONLY)
    message = str(caught.value)
    assert "backend" in message
    assert "end_line" in message


# --- CG-04-CT-12: a measure name or a ready value that cannot measure (ST-0445) -

READY_MEASURE = (
    "      - name: {name}\n"
    "        files: \"packages/server/backend/**\"\n"
    "        command: \"scripts/crap-measure-backend\"\n"
    "        ready: {ready}\n"
)


@pytest.mark.spec("CG-04-CT-12")
@pytest.mark.parametrize("name", ["../backend", "back end/x"])
def test_cg_04_a_measure_name_that_is_no_safe_file_name_cannot_measure(tmp_path, name):
    """Scenario Outline: A measure name that is no safe file name cannot measure (DEC-59)."""
    measure = READY_MEASURE.format(name=f'"{name}"', ready='"scripts/crap-ready-backend"')
    with pytest.raises(cs.GateError) as caught:
        _settings(tmp_path, FULL.replace(MEASURE, measure))()
    assert name in str(caught.value)


@pytest.mark.spec("CG-04-CT-12")
@pytest.mark.parametrize("ready", ['""', "5"], ids=["empty", "number"])
def test_cg_04_a_ready_value_that_is_no_command_cannot_measure(tmp_path, ready):
    """Scenario Outline: A wrong ready value cannot measure; the message names the measure and ready (BR-128)."""
    measure = READY_MEASURE.format(name="backend", ready=ready)
    with pytest.raises(cs.GateError) as caught:
        _settings(tmp_path, FULL.replace(MEASURE, measure))()
    message = str(caught.value)
    assert "measure backend" in message
    assert "ready" in message


# --- CG-05-CT-03: only the first table counts, and the score is a plain decimal (ST-0445) -


@pytest.mark.spec("CG-05-CT-03")
def test_cg_05_only_the_first_table_under_the_crap_score_section_counts():
    """Scenario: Only the first table under the CRAP score section counts (DEC-55)."""
    second = TREE_ROW.replace("`tree_severity`", "`bug_bar_level`")
    text = (
        "# Exceptions\n\n## CRAP score\n\n" + HEADER + TREE_ROW
        + "\nA second table follows.\n\n" + HEADER + second
    )
    assert list(cs.parse_register(text)) == [(FINDING_LINT, "tree_severity")]


@pytest.mark.spec("CG-05-CT-03")
@pytest.mark.parametrize("score", ["9e0", "+9"])
def test_cg_05_an_accepted_score_that_is_no_plain_decimal_names_the_row(score):
    """Scenario Outline: A broken exceptions-register row cannot measure, rows "9e0" and "+9" (DEC-55)."""
    with pytest.raises(cs.GateError) as caught:
        cs.parse_register(_register(TREE_ROW.replace("| 9 |", f"| {score} |")))
    message = str(caught.value)
    assert "line 7" in message
    assert score in message
