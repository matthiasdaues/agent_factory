"""Text checks of the run lifecycle (docs/spec/features/run-lifecycle.feature).

These tests read files of this repository and check their text.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from conftest import REPO_ROOT

TEST_ROOTS = (REPO_ROOT / "tests", REPO_ROOT / "packages" / "usage" / "tests")
LAYOUT_GATES = REPO_ROOT / "tests" / "factory" / "test_core_layout_gates.py"

# A path expression that starts at this repository's root and names
# .agent-factory, such as REPO_ROOT / ".agent-factory" / "factory".
REPO_PATH = re.compile(
    r"\b(?:REPO_ROOT|PROJECT_ROOT|ROOT)\s*/\s*"
    r"""["']\.agent-factory(?P<rest>[^"']*)["'](?P<next>\s*/\s*["'][^"']*["'])?"""
)
# The link of this repository's .agent-factory that scope-lint reads
# .agent-factory/workstreams through (OI-08).
SCOPE_LINT_LINK = re.compile(r"""symlink_to\(\s*REPO_ROOT\s*/\s*["']\.agent-factory["']\s*\)""")


def installed_copy_reads(text: str) -> list[str]:
    """Return each expression of text that reads this repository's installed copy."""
    links = {match.start() for match in SCOPE_LINT_LINK.finditer(text)}
    reads = []
    for match in REPO_PATH.finditer(text):
        link_start = text.rfind("symlink_to(", 0, match.start())
        is_link = link_start in links and not match["rest"] and not match["next"]
        if not is_link:
            reads.append(match.group(0))
    return reads


def _test_files() -> list[Path]:
    """Every test file but this one, whose samples name the forms the check finds."""
    return sorted(
        path
        for root in TEST_ROOTS
        if root.is_dir()
        for path in root.rglob("*.py")
        if path != Path(__file__).resolve()
    )


@pytest.mark.spec("RL-18-LN-01")
def test_RL_18_LN_01_no_test_reads_the_installed_copy_of_this_repository() -> None:
    """Scenario: The test suite of this repository reads no installed copy of its own."""
    files = _test_files()
    assert LAYOUT_GATES in files
    reads = {
        str(path.relative_to(REPO_ROOT)): found
        for path in files
        if (found := installed_copy_reads(path.read_text(encoding="utf-8")))
    }
    assert reads == {}


@pytest.mark.spec("RL-18-LN-01")
def test_RL_18_LN_01_a_read_of_the_installed_copy_counts() -> None:
    """The check finds each form of a path under this repository's .agent-factory/factory,
    and leaves a path under a temporary project alone."""
    assert installed_copy_reads('x = REPO_ROOT / ".agent-factory" / "factory"')
    assert installed_copy_reads("x = REPO_ROOT / '.agent-factory/factory/scripts'")
    assert installed_copy_reads('x = PROJECT_ROOT / ".agent-factory"')
    assert installed_copy_reads('p.symlink_to(REPO_ROOT / ".agent-factory" / "factory")')
    assert installed_copy_reads('x = tmp_path / ".agent-factory" / "factory"') == []
    assert installed_copy_reads('x = target / ".agent-factory/factory"') == []


@pytest.mark.spec("RL-18-LN-02")
def test_RL_18_LN_02_the_scope_lint_link_is_no_read_of_the_installed_copy() -> None:
    """Scenario: A link to this repository's .agent-factory for scope-lint is no read
    of the installed copy."""
    text = LAYOUT_GATES.read_text(encoding="utf-8")
    assert SCOPE_LINT_LINK.search(text), "the scope-lint link moved or changed its form"
    assert installed_copy_reads(text) == []
    line = '(baseline / ".agent-factory").symlink_to(REPO_ROOT / ".agent-factory")'
    assert installed_copy_reads(line) == []
