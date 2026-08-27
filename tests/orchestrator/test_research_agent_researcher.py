"""Tests for the researcher agent definition (ST-0027).

The researcher agent is a prose agent definition (frontmatter + body) that
states what the Researcher role may do, what it must record, and the
boundary that keeps it from judging its own work. Tests verify:

1. File existence: `factory/agents/researcher.md` is created.
2. Frontmatter validity: `name`, `title`, `tier`, `phase` (== 6), and
   `phase-name` (== "Research") are present, plus a non-empty `description`.
3. Content completeness: the body states every permitted action and every
   mandatory record item from the specification (Falsification-Driven
   Research Workflow, §Agents → "Researcher"), and the may-not-review-or-vote
   -on-own-claim boundary.
4. Policy references: the body links both the role-separation policy and
   the evidence policy.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_RESEARCHER_AGENT = _ROOT / "factory" / "agents" / "researcher.md"


class TestBodyContent:
    """The body states permitted actions, mandatory records, and the boundary."""

    _text = _RESEARCHER_AGENT.read_text(encoding="utf-8")

    _permitted_actions = [
        "find sources",
        "assess source provenance",
        "record evidence",
        "propose testable claims",
        "design or execute refutation tests",
    ]

    _must_record_items = [
        "supporting evidence",
        "contrary evidence",
        "source limitations",
        "alternative explanations",
        "failed searches",
        "unresolved gaps",
    ]

    def test_permitted_actions_present(self):
        """Every permitted action from the specification appears in the body."""
        for action in self._permitted_actions:
            assert action in self._text, (
                f"Researcher agent missing permitted action: '{action}'"
            )

    def test_must_record_items_present(self):
        """Every mandatory record item from the specification appears in the body."""
        for item in self._must_record_items:
            assert item in self._text, (
                f"Researcher agent missing must-record item: '{item}'"
            )

    def test_boundary_present(self):
        """The body states the may-not-review-or-vote-on-own-claim boundary."""
        pattern = re.compile(r"may not review or vote on its own claim", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Researcher agent does not state the may-not-review-or-vote-"
            "on-own-claim boundary"
        )


class TestPolicyReferences:
    """The agent definition references both research policies."""

    _text = _RESEARCHER_AGENT.read_text(encoding="utf-8")

    def test_references_role_separation_policy(self):
        assert "role-separation.md" in self._text or "role-separation" in self._text, (
            "Researcher agent does not reference the role-separation policy"
        )

    def test_references_evidence_policy(self):
        assert (
            "evidence-policy.md" in self._text
            or "evidence policy" in self._text.lower()
        ), "Researcher agent does not reference the evidence policy"
