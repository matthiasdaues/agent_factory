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
