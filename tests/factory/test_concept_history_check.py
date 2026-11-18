"""Checks of concept-history-check.

concept-history-check validates the concept histories of a survey against
their source records and computes the ranking from recorded facts. Each test
builds a small survey root in a temporary folder and runs the script as a
subprocess, because the exit code and the printed table are its contract.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR

SCRIPT = SOURCE_SCRIPTS_DIR / "concept-history-check"

RECORD = """# {rid} test record

```json
{{
  "source_identity": "{rid}",
  "author_or_issuing_body": "Test author",
  "publisher": "Test publisher",
  "publication_date": "{date}T00:00:00Z",
  "relevant_event_date": "{event}",
  "source_family": "{family}",
  "precise_evidence_location": "Section 1",
  "method": "Fetched",
  "limitations": "None stated",
  "provenance": "Test"
}}
```

## Evidence

- {body}

## What the source does not show

- A reviewer note: "cyclic negation is never defined here at all".
"""

DATES = {
    "A1-SR-01": ("2010-01-01", "2010-01-01"),
    "A1-SR-02": ("2011-01-01", "2011-01-01"),
    "A1-SR-03": ("2012-01-01", "2012-01-01"),
    "A1-SR-04": ("2016-01-01", "2013-01-01"),
    "A1-SR-05": ("2014-01-01", "2014-01-01"),
}

BODIES = {
    "A1-SR-01": "The first formulation “defines shapes as plain constraints” for graphs.",
    "A1-SR-02": 'A critic wrote that "plain constraints cannot express recursion at all."',
    "A1-SR-03": (
        "A note: the second formulation brings a typing context to references. "
        'Section 2: "adds recursive shape references with a typing context."'
    ),
    "A1-SR-04": 'A later paper says "the typing context leaves cyclic negation without meaning."',
    "A1-SR-05": 'The third formulation "defines recursion through stratified negation only."',
}


def _history(concept="Shapes", **changes):
    data = {
        "concept": concept,
        "area": "validation",
        "current_formulation": "Recursion through stratified negation.",
        "steps": [
            {
                "formulation": "Plain constraints.",
                "date": "2010-01-01",
                "record": "A1-SR-01",
                "quote": '"defines shapes as plain constraints"',
                "criticism": {
                    "record": "A1-SR-02",
                    "date": "2011-01-01",
                    "quote": "plain constraints cannot express recursion",
                    "drove_next": True,
                },
            },
            {
                "formulation": "Recursive references.",
                "date": "2012-01-01",
                "record": "A1-SR-03",
                "quote": "adds recursive shape references with a typing context",
                "criticism": {
                    "record": "A1-SR-04",
                    "date": "2013-01-01",
                    "quote": "leaves cyclic negation without meaning",
                    "drove_next": True,
                },
            },
            {
                "formulation": "Stratified negation.",
                "date": "2014-01-01",
                "record": "A1-SR-05",
                "quote": "defines recursion through stratified negation only",
                "criticism": None,
            },
        ],
    }
    data.update(changes)
    return data


def _survey(tmp_path: Path, histories: dict[str, dict], secondary=(), bodies=None) -> Path:
    sources = tmp_path / "sources" / "area-1"
    sources.mkdir(parents=True)
    for rid, body in {**BODIES, **(bodies or {})}.items():
        family = "Secondary survey" if rid in secondary else "Primary specification"
        date, event = DATES[rid]
        (sources / f"{rid}-test.md").write_text(
            RECORD.format(rid=rid, family=family, body=body, date=date, event=event)
        )
    (tmp_path / "sources" / "area-1-index.md").write_text("# Index\n")
    hdir = tmp_path / "histories"
    hdir.mkdir()
    for name, data in histories.items():
        (hdir / f"{name}.json").write_text(json.dumps(data))
    return tmp_path


def _run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True
    )


def test_valid_history_passes_and_prints_ranking(tmp_path):
    root = _survey(tmp_path, {"shapes": _history()})
    result = _run(root)
    assert result.returncode == 0, result.stdout
    assert _row_cells(result.stdout, "Shapes") == [
        "1", "Shapes", "validation", "3", "2", "100%", "100%",
        "A1-SR-01, A1-SR-02, A1-SR-03, A1-SR-04, A1-SR-05",
    ]


def _row_cells(text, concept):
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) > 1 and cells[1] == concept:
            return cells
    return None


def _mutate(path, value):
    data = _history()
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return data


@pytest.mark.parametrize(
    ("path", "value", "expected"),
    [
        (("steps", 1, "quote"), "adds recursive references with a context", "does not occur word for word"),
        (("steps", 1, "quote"), "adds recursive ... typing context", "ellipsis"),
        (("steps", 1, "quote"), "adds recursive", "fewer than 4 words"),
        (("steps", 1, "record"), "A1-SR-99", "matches no file"),
        (("steps", 1, "date"), "2009-01-01", "before step 1"),
        (("steps", 0, "criticism", "date"), "2009-06-01", "before the formulation it criticises"),
        (("steps", 1, "criticism", "date"), "2016-01-01", "after step 3"),
        (("steps", 2, "criticism"), {"record": "A1-SR-04", "date": "2016-01-01",
                                     "quote": "leaves cyclic negation without meaning",
                                     "drove_next": True}, "no later formulation exists"),
        (("steps", 1, "date"), "2012-06-01", "matches neither publication_date"),
        (("steps", 1, "quote"), "brings a typing context to references", "outside every quoted passage"),
        (("steps", 1, "criticism", "quote"), "cyclic negation is never defined here",
         "outside every quoted passage"),
        (("steps", 0, "extra"), "x", "schema"),
    ],
    ids=[
        "paraphrased-quote",
        "ellipsis",
        "short-quote",
        "missing-record",
        "dates-go-backwards",
        "criticism-before-formulation",
        "criticism-after-the-step-it-drove",
        "last-step-drove-nothing",
        "date-not-from-record",
        "researcher-note-not-source-words",
        "quoted-passage-outside-evidence",
        "schema-violation",
    ],
)
def test_each_violation_fails_with_its_reason(tmp_path, path, value, expected):
    root = _survey(tmp_path, {"shapes": _mutate(path, value)})
    result = _run(root)
    assert result.returncode == 1
    assert expected in result.stdout


def test_criticism_marked_as_later_assessment_may_postdate_the_next_step(tmp_path):
    data = _mutate(("steps", 1, "criticism", "date"), "2016-01-01")
    data["steps"][1]["criticism"]["drove_next"] = False
    root = _survey(tmp_path, {"shapes": data})
    assert _run(root).returncode == 0


def test_typographic_quotes_and_line_wraps_are_normalised(tmp_path):
    data = _mutate(("steps", 0, "quote"), "“defines shapes\n   as plain constraints”")
    root = _survey(tmp_path, {"shapes": data})
    assert _run(root).returncode == 0


# A source with quotation marks of its own, such as an RFC grammar rule.
NESTED = 'Section 2: "adds recursive "shape" references with a typing context."'
# A bullet with an odd number of marks; it must not shift the bullets after it.
ODD = (
    'Grammar: "ref = "@ shape" ends.\n'
    "- A note: the second formulation brings a typing context to references.\n"
    '- Section 2: "adds recursive shape references with a typing context."'
)


@pytest.mark.parametrize(
    ("body", "quote"),
    [
        (NESTED, 'adds recursive "shape" references with a typing context'),
        (
            NESTED.replace('"shape"', "“shape”"),
            "adds recursive “shape” references with a typing context",
        ),
        (ODD, "adds recursive shape references with a typing context"),
    ],
    ids=["inner-straight-marks", "inner-curly-marks", "odd-marks-in-an-earlier-bullet"],
)
def test_source_quotation_marks_do_not_hide_a_quote(tmp_path, body, quote):
    data = _mutate(("steps", 1, "quote"), quote)
    root = _survey(tmp_path, {"shapes": data}, bodies={"A1-SR-03": body})
    result = _run(root)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    ("body", "quote"),
    [
        (ODD, "brings a typing context to references"),
        (NESTED, '"shape" references with a typing'),
    ],
    ids=["note-after-odd-marks", "part-of-a-passage-with-inner-marks"],
)
def test_source_quotation_marks_do_not_admit_other_text(tmp_path, body, quote):
    data = _mutate(("steps", 1, "quote"), quote)
    root = _survey(tmp_path, {"shapes": data}, bodies={"A1-SR-03": body})
    result = _run(root)
    assert result.returncode == 1
    assert "outside every quoted passage" in result.stdout


def test_concept_below_entry_rule_is_listed_apart_and_unranked(tmp_path):
    short = _history(concept="Short")
    short["steps"] = short["steps"][:2]
    short["steps"][1]["criticism"] = None
    root = _survey(tmp_path, {"shapes": _history(), "short": short})
    out = _run(root).stdout
    ranked, below = out.split("Below the entry rule")
    assert _row_cells(ranked, "Shapes")[0] == "1"
    assert _row_cells(ranked, "Short") is None
    assert _row_cells(below, "Short")[:5] == ["-", "Short", "validation", "2", "1"]


def test_rank_follows_primary_share_not_length(tmp_path):
    longer = _history(concept="Longer")
    longer["steps"].append(copy.deepcopy(longer["steps"][2]))
    longer["steps"][3]["date"] = "2014-01-01"
    strong = _history(concept="Strong")
    root = _survey(tmp_path, {"longer": longer, "strong": strong}, secondary={"A1-SR-05"})
    # Both share A1-SR-05, so both lose primary share; the longer history
    # cites it twice and so ranks lower despite having more rounds.
    out = _run("--table", root).stdout
    assert _row_cells(out, "Strong")[0] == "1"
    assert _row_cells(out, "Longer")[0] == "2"


def test_table_output_is_identical_across_runs(tmp_path):
    root = _survey(tmp_path, {"b": _history(concept="B"), "a": _history(concept="A")})
    first, second = _run("--table", root).stdout, _run("--table", root).stdout
    assert first == second
    assert _row_cells(first, "A")[0] == "1"
    assert _row_cells(first, "B")[0] == "2"


def test_table_is_padded_so_mdformat_leaves_it_unchanged(tmp_path):
    short = _history(concept="A much longer concept name")
    root = _survey(tmp_path, {"shapes": _history(), "long": short})
    lines = _run("--table", root).stdout.strip().splitlines()
    assert len({len(line) for line in lines}) == 1
    assert set(lines[1].replace("|", "").replace(" ", "")) == {"-"}


def test_table_mode_prints_failures_to_stderr_only(tmp_path):
    root = _survey(tmp_path, {"shapes": _mutate(("steps", 1, "record"), "A1-SR-99")})
    result = _run("--table", root)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "matches no file" in result.stderr


def test_missing_histories_is_an_operational_error(tmp_path):
    (tmp_path / "sources").mkdir()
    assert _run(tmp_path).returncode == 2
