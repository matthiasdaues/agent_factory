"""The findings of this repository stay under the classification rules (ST-0406).

Each test reads the real docs/findings/ of this repository, as
test_no_retired_charter.py reads the real tree.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

import pytest
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR

FINDINGS = REPO_ROOT / "docs" / "findings"


def _frontmatter(path) -> str:
    """Return the frontmatter of a finding file, or an empty text without one."""
    parts = path.read_text(encoding="utf-8").split("---\n", 2)
    return parts[1] if len(parts) == 3 and not parts[0] else ""


def _open_findings() -> dict:
    """Return the frontmatter of each open finding file by its file name."""
    found = {path.name: _frontmatter(path) for path in sorted(FINDINGS.glob("*.md"))}
    return {
        name: text
        for name, text in found.items()
        if re.search(r"^status: open\s*$", text, re.MULTILINE)
    }


@pytest.mark.spec("FC-20-IT-01")
def test_st_0406_finding_lint_passes_on_this_repository():
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    result = subprocess.run(
        [sys.executable, str(SOURCE_SCRIPTS_DIR / "finding-lint")],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.spec("FC-20-IT-01")
def test_st_0406_every_open_finding_file_carries_a_review_class():
    missing = [
        name
        for name, text in _open_findings().items()
        if not re.search(r"^review_class:", text, re.MULTILINE)
    ]
    assert missing == []


@pytest.mark.spec("FC-20-IT-01")
def test_st_0406_no_open_finding_file_is_minor_or_note():
    low = [
        name
        for name, text in _open_findings().items()
        if re.search(r"^severity: (minor|note)\s*$", text, re.MULTILINE)
    ]
    assert low == []


@pytest.mark.spec("FC-20-IT-01")
def test_st_0406_the_register_holds_no_jsonl_file():
    assert list((FINDINGS / "register").rglob("*.jsonl")) == []
