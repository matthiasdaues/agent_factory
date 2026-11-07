"""Text checks of the finding-classification rulebook (ST-0386).

The rulebook packages/factory/rulebooks/conventions/finding-classification.md
holds the one set of classification rules. These tests read it, the older
rulebooks that link it, and the envelope examples.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from conftest import REPO_ROOT

RULEBOOKS = REPO_ROOT / "packages" / "factory" / "rulebooks"
RULEBOOK = RULEBOOKS / "conventions" / "finding-classification.md"
REPORT_FORMAT = RULEBOOKS / "conventions" / "report-format.md"
FINDING_FORMAT = RULEBOOKS / "conventions" / "finding-format.md"
OWASP = RULEBOOKS / "principles" / "owasp-top-10.md"
RULES = RULEBOOKS / "rules.md"
INTERFACE_CONTRACTS = REPO_ROOT / "docs" / "spec" / "interface-contracts.md"
FINDINGS = REPO_ROOT / "docs" / "findings"

CLASSES = ("document", "code", "security", "architecture", "runtime")
LEVELS = ("critical", "major", "minor", "note")
# The agreement check of ST-0390 uses these three, so no example may name them.
AGREEMENT_SET = ("FAGAN-0021", "SEC-0005", "SEC-0006")
FINDING_ID = re.compile(r"\b[A-Z]+-\d{4}\b")
PATH_SPAN = re.compile(r"`((?:packages|docs)/[^`\s:#]+)")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(text: str) -> str:
    """Join wrapped lines so a phrase can be found across a line break."""
    return re.sub(r"\s+", " ", text)


def _section(text: str, heading: str) -> str:
    """Return the body under a heading, up to the next heading of its level."""
    match = re.search(rf"^(#+) {re.escape(heading)}\s*$", text, re.MULTILINE)
    assert match, f"heading {heading!r} is missing"
    level = len(match.group(1))
    rest = text[match.end() :]
    end = re.search(rf"^#{{1,{level}}} ", rest, re.MULTILINE)
    return rest[: end.start()] if end else rest


def _register_ids() -> set[str]:
    ids: set[str] = set()
    register = FINDINGS / "register"
    for path in register.glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                ids.add(json.loads(line)["id"])
    ids.update(path.stem for path in register.glob("*/*.json"))
    return ids


def _example_rows(class_name: str) -> list[list[str]]:
    """Return the cells of each row of the calibration table of a class."""
    body = _section(_text(RULEBOOK), f"Class: {class_name}")
    table = _section(body, "Calibration examples")
    rows = []
    for line in table.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0].strip("`") in LEVELS:
            rows.append(cells)
    return rows


@pytest.mark.spec("FC-01-LN-01")
def test_st_0386_rulebook_holds_values_scale_tree_and_class_sections():
    text = _text(RULEBOOK)
    for heading in (
        "The values of a finding",
        "Shared severity scale and blocking rule",
        "In use",
        "The consequence tree",
        "Type from the fix",
    ):
        _section(text, heading)
    for class_name in CLASSES:
        _section(text, f"Class: {class_name}")
    values = _flat(_section(text, "The values of a finding"))
    for value in ("Category", "Type", "Severity", "Blocking"):
        assert f"| {value} " in values
    scale = _section(text, "Shared severity scale and blocking rule")
    for level in LEVELS:
        assert f"`{level}`" in scale
    tree = _flat(_section(text, "The consequence tree"))
    order = [tree.index(f"`{q}`") for q in ("harms_downstream", "fails_purpose", "raises_cost")]
    assert order == sorted(order)


@pytest.mark.spec("FC-01-LN-02")
@pytest.mark.parametrize("class_name", CLASSES)
def test_st_0386_each_level_has_two_or_three_real_examples_or_one_invented(class_name):
    known = {path.stem for path in FINDINGS.glob("*.md")} | _register_ids()
    rows = _example_rows(class_name)
    for level in LEVELS:
        level_rows = [row for row in rows if row[0].strip("`") == level]
        real = [row for row in level_rows if "Invented" not in row[1]]
        invented = [row for row in level_rows if "Invented" in row[1]]
        if real:
            assert 2 <= len(real) <= 3, f"{class_name}/{level}: {len(real)} real examples"
            assert not invented, f"{class_name}/{level} mixes real and invented examples"
        else:
            assert len(invented) == 1, f"{class_name}/{level}: needs one invented example"
        for row in real:
            ids = FINDING_ID.findall(row[1])
            assert ids, f"{class_name}/{level}: a real example names no ID"
            for finding_id in ids:
                assert finding_id in known, f"{finding_id} is not in docs/findings/"
            assert row[2], f"{class_name}/{level}: {ids[0]} has no basis"
        for row in invented:
            paths = PATH_SPAN.findall(" ".join(row))
            assert paths, f"{class_name}/{level}: the invented example names no file"
            for path in paths:
                assert (REPO_ROOT / path).exists(), f"{path} does not exist"


@pytest.mark.spec("FC-01-LN-02")
def test_st_0386_no_example_names_a_finding_of_the_agreement_check():
    text = _text(RULEBOOK)
    for finding_id in AGREEMENT_SET:
        assert finding_id not in text


@pytest.mark.spec("FC-02-LN-01")
def test_st_0386_rulebook_states_the_class_and_filing_rules():
    text = _flat(_text(RULEBOOK))
    for phrase in (
        "The reviewed material decides the class",
        "playbooks, skills, agent definitions, rulebooks, and hook configuration",
        "the change that the `**Fix:**` line demands",
        "`docs/spec/work/todo.md`",
        "An observation that names no artifact is not a finding",
        "A `suggestion` of the document, code, or runtime class describes material that works",
        "`nitpick` always gives `note`",
        "its category is `defect` or `risk` and its severity is `critical` or `major`",
    ):
        assert phrase in text, phrase


@pytest.mark.spec("FC-04-LN-01")
def test_st_0386_an_attack_that_needs_the_capability_it_gains_is_not_a_finding():
    security = _flat(_section(_text(RULEBOOK), "Class: security"))
    assert "An attack that needs the capability it gains is not a finding" in security


@pytest.mark.spec("FC-09-LN-01")
@pytest.mark.parametrize("path", [REPORT_FORMAT, INTERFACE_CONTRACTS], ids=["report-format", "interface-contracts"])
def test_st_0386_envelope_example_carries_four_keys(path):
    counts = re.findall(r'"finding_counts":\s*(\{[^}]*\})', _text(path))
    assert counts, f"{path.name} has no finding_counts example"
    for raw in counts:
        assert set(json.loads(raw)) == set(LEVELS)


@pytest.mark.spec("FC-09-LN-01")
def test_st_0386_claim_review_counts_a_blocker_under_major():
    text = _flat(_text(RULEBOOK))
    assert "A BLOCKER counts under `major`" in text
    assert "nothing under `critical`" in text


@pytest.mark.spec("FC-17-LN-01")
def test_st_0386_rulebook_states_the_waiver_rules():
    waiver = _flat(_section(_text(RULEBOOK), "Waiver and confirmation"))
    for phrase in (
        "keeps its computed severity",
        "only after the stakeholder has confirmed its stop",
        "No override raises a `minor` finding",
        "never with `deferred`",
        "never by a lowering to a `note`",
        "the register file stays",
        "`override_by` and `override_reason`",
        "`stop_confirmed_by` and `stop_confirmed_reason`",
    ):
        assert phrase in waiver, phrase


LEVEL_DEFINITION = re.compile(
    r"\*\*(Critical|Major|Minor|High|Medium|Low)\*\*\s*[—:-]"
    r"|Critical\s*/\s*High"
    r"|Medium or higher"
    r"|blocking severity is",
)


@pytest.mark.parametrize(
    ("path", "heading"),
    [
        (REPORT_FORMAT, "Category rules"),
        (REPORT_FORMAT, "Severity"),
        (FINDING_FORMAT, "When to file"),
        (OWASP, None),
        (RULES, "Findings"),
    ],
    ids=["report-format-category", "report-format-severity", "finding-format", "owasp", "rules"],
)
def test_st_0386_older_rulebooks_link_the_rulebook_and_define_no_level(path, heading):
    text = _text(path)
    body = _section(text, heading) if heading else text
    assert "finding-classification.md" in body
    assert not LEVEL_DEFINITION.search(body), LEVEL_DEFINITION.search(body)
