"""Tests for the research-report-writer agent (ST-0029).

The research-report-writer agent writes the final report from the frozen
claim register. Tests verify:

1. File existence: the agent file is created at the expected path.
2. Frontmatter validity: `name`, `title`, `tier`, `phase` (== 6), and
   `phase-name` (== Research) are present with the required values, and a
   `description` is present — the structure `index-lint` expects.
3. Content completeness: the body states every permitted action and every
   forbidden action from the specification (Falsification-Driven Research
   Workflow, §Agents → "Research Report Writer"), and references the report
   policy.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AGENT_FILE = _ROOT / "factory" / "agents" / "research-report-writer.md"


class TestBodyContent:
    """The body states every permitted and forbidden action, and references
    the report policy."""

    _text = _AGENT_FILE.read_text(encoding="utf-8")

    _permitted_actions = [
        "arrange surviving claims",
        "summarize",
        "preserve refutations and limitations",
    ]

    _forbidden_actions = [
        "conduct new research",
        "create claims",
        "remove qualifications",
        "present a surviving claim as proved",
        "use rejected or unresolved claims as facts",
    ]

    def test_permitted_actions_present(self):
        for phrase in self._permitted_actions:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            assert pattern.search(self._text), (
                f"research-report-writer missing permitted action: '{phrase}'"
            )

    def test_forbidden_actions_present(self):
        for phrase in self._forbidden_actions:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            assert pattern.search(self._text), (
                f"research-report-writer missing forbidden action: '{phrase}'"
            )

    def test_references_report_policy(self):
        pattern = re.compile(
            r"factory/rulebooks/conventions/research-report-policy\.md|research-report-policy\.md",
            re.IGNORECASE,
        )
        assert pattern.search(self._text), (
            "research-report-writer does not reference the report policy"
        )
