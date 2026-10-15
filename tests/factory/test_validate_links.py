"""Regression tests for the validate skill and the link-check script.

BUG-0059 and BUG-0060 cover the gate table in the validate skill.
BUG-0061 covers link-check's answers on valid and broken links.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

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


# --- BUG-0060: the validate skill looks for model.conf in the wrong place ---


def test_matrix_lint_gate_uses_the_installed_model_conf():
    """BUG-0060: init-factory installs model.conf under .agent-factory/config/,
    so the matrix-lint gate checks and passes that path."""
    condition, command = _gates()["matrix-lint"]

    assert "`.agent-factory/config/model.conf` exists" in condition
    assert command.endswith("--matrix .agent-factory/config/model.conf")


def test_skill_names_no_root_level_model_conf():
    """BUG-0060: no sentence in the skill points at a root-level config/model.conf."""
    text = SKILL.read_text(encoding="utf-8")

    assert not re.search(r"(?<![/\w.])config/model\.conf", text)


# --- BUG-0061: link-check gives wrong answers ---


def _link_check(cwd: Path, *names: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(LINK_CHECK), *names], cwd=cwd, capture_output=True, text=True
    )


def _write(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode(encoding))


VALID_LINKS = {
    "anchor in a file with a byte order mark": {
        "doc.md": "﻿# Title\n\n[top](#title)\n",
    },
    "setext heading level 1": {
        "doc.md": "Big Title\n=========\n\n[up](#big-title)\n",
    },
    "setext heading level 2": {
        "doc.md": "Small Title\n-----------\n\n[up](#small-title)\n",
    },
    "html anchor with id": {
        "doc.md": '<a id="custom-spot"></a>\n\n[here](#custom-spot)\n',
    },
    "html anchor with name": {
        "doc.md": "<a name='old-spot'></a>\n\n[here](#old-spot)\n",
    },
    "anchor in another file's html anchor": {
        "doc.md": "[there](other.md#deep)\n",
        "other.md": '# Other\n\n<a id="deep"></a>\n',
    },
    "heading with underscore emphasis": {
        "doc.md": "## The _big_ idea\n\n[idea](#the-big-idea)\n",
    },
    "heading with strong underscore emphasis": {
        "doc.md": "## A __bold__ move\n\n[move](#a-bold-move)\n",
    },
    "heading with an intraword underscore": {
        "doc.md": "## The snake_case name\n\n[name](#the-snake_case-name)\n",
    },
    "heading with angle brackets inside a code span": {
        "doc.md": "#### `dispatch prepare-story <story-id>`\n\n"
        "[cmd](#dispatch-prepare-story-story-id)\n",
    },
    "heading with double underscores inside a code span": {
        "doc.md": "## `__init__` method\n\n[init](#__init__-method)\n",
    },
    "heading with brackets and underscores inside a code span": {
        "doc.md": "# `<cli>_<session_id>` as the name\n\n"
        "[name](#cli_session_id-as-the-name)\n",
    },
    "angle-bracket destination with a space": {
        "doc.md": "[file](<my file.md>)\n",
        "my file.md": "# Mine\n",
    },
    "destination with balanced parentheses": {
        "doc.md": "[file](file(1).md)\n",
        "file(1).md": "# One\n",
    },
    "destination with parentheses and a title": {
        "doc.md": '[file](file(1).md "the first")\n',
        "file(1).md": "# One\n",
    },
    "link example inside a nested code fence": {
        "doc.md": "````markdown\n```\n[example](missing.md)\n````\n",
    },
    "link example inside a fence closed by a longer fence": {
        "doc.md": "```\n[example](missing.md)\n`````\n",
    },
    "reference link to an existing file": {
        "doc.md": "See [the guide][g].\n\n[g]: guide.md\n",
        "guide.md": "# Guide\n",
    },
}


@pytest.mark.parametrize("files", VALID_LINKS.values(), ids=list(VALID_LINKS))
def test_link_check_accepts_valid_links(tmp_path, files):
    """BUG-0061: link-check passes documents whose links all resolve."""
    for name, text in files.items():
        _write(tmp_path / name, text)

    result = _link_check(tmp_path, "doc.md")

    assert result.returncode == 0, result.stderr


BROKEN_LINKS = {
    "reference link to a missing file": {
        "doc.md": "See [the guide][g].\n\n[g]: missing.md\n",
    },
    "reference definition in angle brackets to a missing file": {
        "doc.md": "See [the guide][g].\n\n[g]: <missing file.md> \"Title\"\n",
    },
    "link after a nested fence closes": {
        "doc.md": "````\n```\n````\n\n[gone](missing.md)\n",
    },
    "anchor that only a heading inside a fence offers": {
        "doc.md": "```\n# Hidden\n```\n\n[hidden](#hidden)\n",
    },
}


@pytest.mark.parametrize("files", BROKEN_LINKS.values(), ids=list(BROKEN_LINKS))
def test_link_check_reports_broken_links(tmp_path, files):
    """BUG-0061: link-check fails documents with a link that does not resolve."""
    for name, text in files.items():
        _write(tmp_path / name, text)

    result = _link_check(tmp_path, "doc.md")

    assert result.returncode == 1
    assert "doc.md" in result.stderr


def test_link_check_reports_a_missing_input_file(tmp_path):
    """BUG-0061: a named file that does not exist is a finding, not a pass."""
    result = _link_check(tmp_path, "absent.md")

    assert result.returncode == 1
    assert "absent.md" in result.stderr


def test_link_check_reports_a_latin1_input_file(tmp_path):
    """BUG-0061: a file that is not UTF-8 is reported, not a crash."""
    _write(tmp_path / "doc.md", "# Café\n\n[x](#café)\n", encoding="latin-1")

    result = _link_check(tmp_path, "doc.md")

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "doc.md" in result.stderr


def test_link_check_reports_a_latin1_link_target(tmp_path):
    """BUG-0061: an anchor into a file that is not UTF-8 is reported, not a crash."""
    _write(tmp_path / "doc.md", "[x](other.md#top)\n")
    _write(tmp_path / "other.md", "# Top\n\nCafé\n", encoding="latin-1")

    result = _link_check(tmp_path, "doc.md")

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "other.md" in result.stderr
