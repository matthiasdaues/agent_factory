"""Shipped instructions name no retired charter tool and no Epic 0 (BUG-0047).

The charter was replaced by docs/agent-context.md, and Epic 0 was dropped:
setup work is a line item inside the first story that needs it.
"""

from __future__ import annotations

import re

from conftest import REPO_ROOT

FACTORY = REPO_ROOT / "packages" / "factory"
RETIRED = re.compile(r"Epic 0|charter-lint|capture-charter|update-charter")


def test_no_shipped_instruction_names_retired_charter_tools_or_epic_zero():
    hits = [
        f"{path.relative_to(REPO_ROOT)}:{n}"
        for path in FACTORY.rglob("*.md")
        if "reports" not in path.relative_to(FACTORY).parts and path.name != "CHANGELOG.md"
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if RETIRED.search(line)
    ]
    assert hits == []
