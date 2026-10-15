"""Regression tests for the validate skill and the link-check script.

BUG-0059 and BUG-0060 cover the gate table in the validate skill.
BUG-0061 covers link-check's answers on valid and broken links.
"""

from __future__ import annotations

import re

import pytest
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR

SKILL = REPO_ROOT / "packages" / "factory" / "skills" / "validate" / "SKILL.md"
LINK_CHECK = SOURCE_SCRIPTS_DIR / "link-check"

UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")


def _gates() -> dict[str, tuple[str, str]]:
    """Map each gate name in the skill's table to its condition and command.

    Cells are split on unescaped pipes, the way a GFM table is read, so a
    command that holds a raw pipe shows up cut off.
    """
    gates: dict[str, tuple[str, str]] = {}
    for line in SKILL.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cells = [c.strip() for c in UNESCAPED_PIPE.split(line.strip().strip("|"))]
        _, name, condition, command = cells
        gates[name] = (condition, command.replace("\\|", "|").strip("`"))
    return gates


# --- BUG-0059: the validate skill has a broken command and changes files ---


def test_link_check_gate_command_is_complete():
    """BUG-0059: the gate 4 command reaches link-check instead of stopping
    after the pathspec."""
    _, command = _gates()["link-check"]

    assert command.endswith("| xargs -0 .agent-factory/factory/scripts/link-check")


@pytest.mark.parametrize(
    ("gate", "check_flag"),
    [("Markdown format", "--check"), ("Ruff format", "--check")],
)
def test_format_gates_only_check(gate, check_flag):
    """BUG-0059: the format gates report drift and leave files alone."""
    _, command = _gates()[gate]

    assert check_flag in command.split()


def test_ruff_check_gate_does_not_fix():
    """BUG-0059: ruff check reports findings without applying fixes."""
    _, command = _gates()["Ruff check"]

    assert "--fix" not in command

