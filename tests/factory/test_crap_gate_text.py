"""Text checks of the CRAP gate setup (docs/spec/features/crap-gate-setup.feature).

These tests read files of this repository and check their text.
"""

from __future__ import annotations

import re

import pytest
import yaml

from conftest import REPO_ROOT

TEMPLATE = REPO_ROOT / "packages" / "factory" / "rulebooks" / "templates" / "charter-testing.yaml"
VALIDATION_RULES = REPO_ROOT / "docs" / "spec" / "validation-rules.md"


def _rule_text(rule: str) -> str:
    """Return the bullet of *rule* in docs/spec/validation-rules.md."""
    match = re.search(
        rf"^- \*\*{re.escape(rule)}\*\*:(.*)$", VALIDATION_RULES.read_text(), re.MULTILINE
    )
    assert match, f"{rule} is missing from {VALIDATION_RULES}"
    return match.group(1)


@pytest.mark.spec("CG-11-LN-02")
def test_cg_11_the_charter_template_has_a_mutation_entry_and_no_crap_entry() -> None:
    """Scenario: Template includes gates section without a CRAP gate."""
    gates = yaml.safe_load(TEMPLATE.read_text())["gates"]
    assert isinstance(gates, dict)
    assert "mutation_testing" in gates
    assert "crap_score" not in gates
    assert "crap-score" not in gates


@pytest.mark.spec("CG-12-LN-05")
@pytest.mark.parametrize(
    ("rule", "statements"),
    [
        # premerge-check runs no gate by default
        ("BR-066", ["No default picks a gate.", "`premerge-check` runs none"]),
        # crap-score reads the report of the measuring command
        ("BR-027", ["`crap-score` reads the rows that the project's measuring commands write"]),
        # only the stakeholder writes docs/findings/exceptions.md
        (
            "BR-092",
            ["Only the stakeholder writes the exceptions register `docs/findings/exceptions.md`"],
        ),
        # a gate that cannot measure is a fourth cause of blocked
        (
            "BR-116",
            [
                "stops as `blocked` when a gate cannot measure",
                "`crap-score` exits `2` in the gate-check step",
                "`premerge-check` exits `3` at the merge",
            ],
        ),
        # merge-story turns exit 3 of premerge-check into blocked
        ("BR-124", ["When `premerge-check` exits `3`", "it sets the entry `blocked`"]),
    ],
)
def test_cg_12_the_business_rules_state_the_gates_behaviour(rule, statements) -> None:
    """Scenario Outline: The business rules state the gate's behaviour."""
    text = _rule_text(rule)
    for statement in statements:
        assert statement in text, f"{rule} does not state: {statement}"


SETUP_SKILL_DIR = REPO_ROOT / "packages" / "factory" / "skills" / "setup-crap-score"
PYTHON_TEMPLATE = SETUP_SKILL_DIR / "crap-measure-python"


@pytest.mark.spec("CG-03-LN-01")
def test_cg_03_the_python_template_holds_the_tool_code_and_names_its_duty() -> None:
    """Scenario: The Python measuring command starts from the Factory template."""
    text = PYTHON_TEMPLATE.read_text()
    header = re.search(r"^# /// script\n(.*?)^# ///$", text, re.MULTILINE | re.DOTALL)
    assert header, "the template has no `uv run --script` header"
    assert text.startswith("#!/usr/bin/env -S uv run --script\n")
    assert '"radon' in header.group(1)
    assert '"coverage' in header.group(1)
    assert "from radon.complexity import cc_visit" in text
    assert re.search(r"^import coverage$", text, re.MULTILINE)
    assert re.search(r"^TEST_COMMAND: list\[str\] = \[\]$", text, re.MULTILINE)
    docstring = " ".join(text.split('"""')[1].split())
    assert "it exits non-zero, names the cause, and writes no rows" in docstring
    assert "never reports such a file as 0 % covered" in docstring


@pytest.mark.spec("CG-03-LN-02")
def test_cg_03_no_file_of_the_setup_skill_names_the_factory_folder() -> None:
    """Scenario: The project's commands refer to nothing under .agent-factory/."""
    files = sorted(p for p in SETUP_SKILL_DIR.rglob("*") if p.is_file())
    assert PYTHON_TEMPLATE in files
    for path in files:
        assert ".agent-factory/" not in path.read_text(), f"{path} names .agent-factory/"


CRAP_SCORE = REPO_ROOT / "packages" / "factory" / "scripts" / "crap-score"
CRAP_SKILL = REPO_ROOT / "packages" / "factory" / "skills" / "crap-score" / "SKILL.md"
ADR_0003 = REPO_ROOT / "docs" / "adr" / "0003-test-execution-via-hooks.md"
ARC42_5 = REPO_ROOT / "docs" / "arc42" / "05_building_block_view.md"
# A file ending of a language, such as `.py` or `*.ts`; `.json` is no language.
LANGUAGE_ENDING = re.compile(r"\.(?:py|pyi|ts|tsx|js|jsx|mjs|go|rs|java|kt|rb|php|cs|c|cpp|h)\b")
TOOLS = ("radon", "lizard", "coverage.py", "ESLint", "Vitest", "Jest")


@pytest.mark.spec("CG-03-LN-03")
def test_cg_03_crap_score_holds_no_language_specific_code() -> None:
    """Scenario: crap-score holds no language-specific code."""
    text = CRAP_SCORE.read_text()
    assert not re.search(r"^\s*(?:import|from)\s+(?:radon|coverage)\b", text, re.MULTILINE)
    assert "radon" not in text
    assert LANGUAGE_ENDING.findall(text) == []


@pytest.mark.spec("CG-03-LN-03")
def test_cg_03_the_check_finds_a_language_ending() -> None:
    assert LANGUAGE_ENDING.findall('rglob("*.py") and main.ts') == [".py", ".ts"]
    assert LANGUAGE_ENDING.findall("report.json") == []


@pytest.mark.spec("CG-12-LN-01")
def test_cg_12_the_crap_score_skill_describes_the_gate_without_a_tool_or_threshold() -> None:
    """Scenario: The skill crap-score describes the gate and names no tool and no threshold."""
    text = CRAP_SKILL.read_text()
    flat = " ".join(text.split())
    for content in (
        "GATE_OUTPUT",
        "`start_line`",
        "`end_line`",
        "`coverage_pct`",
        "`parse_error`",
        "complexity² × (1 − coverage_pct/100)³ + complexity",
        "half up",
        "docs/findings/exceptions.md",
        "`gates.crap-score.threshold`",
    ):
        assert content in flat, f"crap-score/SKILL.md does not describe {content}"
    for code in ("`0`", "`1`", "`2`"):
        assert code in flat
    for folder in ("worktree of the story", "primary checkout", "premerge-check", "gate-setup-proof"):
        assert folder in flat, f"crap-score/SKILL.md does not name the folder of {folder}"
    for tool in TOOLS:
        assert tool.lower() not in text.lower(), f"crap-score/SKILL.md names {tool}"
    assert not re.search(r"default threshold|threshold[^.\n]*default", text, re.IGNORECASE)


@pytest.mark.spec("CG-12-LN-04")
def test_cg_12_the_architecture_names_exit_code_2_of_crap_score() -> None:
    """Scenario: The architecture names exit code 2 of crap-score."""
    adr = " ".join(ADR_0003.read_text().split())
    assert "Decision 5 of the amendment of 2026-08-28 gains one exception: the CRAP gate `crap-score`." in adr
    assert "It exits `2` when it cannot measure" in adr
    rows = [line for line in ARC42_5.read_text().splitlines() if line.startswith("| **crap-score**")]
    assert any("2 (cannot measure)" in row for row in rows)
