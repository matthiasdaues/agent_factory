"""Tests for the research-orchestrator agent definition (ST-0026).

The research-orchestrator agent is a prose rulebook that defines the
Research Orchestrator role for the falsification-driven research playbook.
Tests verify:

1. File existence: the agent file is created at the expected path.
2. Frontmatter validity: `name`, `title`, `tier`, `phase` (== 6), and
   `phase-name` (== Research) are present in the YAML frontmatter — the
   structure index-lint expects, and the phase grouping the four research
   agents (Research Orchestrator, Researcher, Claim Reviewer, Research
   Report Writer) under one phase label.
3. Content completeness: the body lists every permitted action and every
   forbidden action exactly as stated in the proposal's "Research
   Orchestrator" section (Falsification-Driven Research Workflow, §Agents),
   and references the role-separation policy as the source of these
   boundaries.
"""

from __future__ import annotations

import re
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[2]
_AGENT_FILE = _ROOT / "factory" / "agents" / "research-orchestrator.md"
_ROLE_SEPARATION_POLICY = (
    _ROOT / "factory" / "rulebooks" / "conventions" / "research-role-separation.md"
)

# Permitted actions, verbatim from the proposal's Research Orchestrator section.
_PERMITTED_ACTIONS = [
    "start playbook steps",
    "assign agents",
    "run validation",
    "request another research round",
    "tally eligible votes",
    "freeze the claim register",
    "start report generation",
]

# Forbidden actions, verbatim from the proposal's Research Orchestrator section.
_FORBIDDEN_ACTIONS = [
    "write substantive claims",
    "review claims",
    "vote",
    "add findings to the report",
]


def _parse_frontmatter(file_path: Path) -> dict:
    """Extract frontmatter keys from a markdown file using regex.

    Frontmatter is delimited by --- at the start and end of the first block.
    Handles both plain `key: value` lines and YAML block-scalar (`>-`)
    values by joining the indented continuation lines that follow.
    Returns a dictionary of field names and values found in the frontmatter.
    """
    text = file_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}

    end_index = text.find("\n---", 3)
    if end_index == -1:
        return {}

    lines = text[3:end_index].split("\n")
    fields: dict = {}
    i = 0

    while i < len(lines):
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
        if not match:
            i += 1
            continue

        key, rest = match.group(1), match.group(2).strip()

        if rest in (">-", ">", "|-", "|"):
            parts = []
            i += 1
            while i < len(lines) and (
                lines[i].startswith("  ") or lines[i].strip() == ""
            ):
                if lines[i].strip():
                    parts.append(lines[i].strip())
                i += 1
            fields[key] = " ".join(parts)
            continue

        fields[key] = rest.strip('"').strip("'")
        i += 1

    return fields


class TestFileExists:
    """The deliverable is created at the expected path."""

    def test_research_orchestrator_exists(self):
        assert _AGENT_FILE.exists(), (
            f"research-orchestrator agent not found at {_AGENT_FILE}"
        )


class TestFrontmatterValid:
    """The agent has valid frontmatter with the keys index-lint requires."""

    _fm = _parse_frontmatter(_AGENT_FILE)

    def test_name(self):
        assert self._fm.get("name") == "research-orchestrator", (
            "research-orchestrator frontmatter 'name' must be 'research-orchestrator'"
        )

    def test_title(self):
        assert self._fm.get("title"), (
            "research-orchestrator missing 'title' in frontmatter"
        )

    def test_tier(self):
        assert self._fm.get("tier"), (
            "research-orchestrator missing 'tier' in frontmatter"
        )

    def test_phase_is_six(self):
        assert self._fm.get("phase") == "6", (
            "research-orchestrator 'phase' must be 6, so it groups with the "
            "other three research agents"
        )

    def test_phase_name_is_research(self):
        assert self._fm.get("phase-name") == "Research", (
            "research-orchestrator 'phase-name' must be 'Research'"
        )

    def test_description(self):
        assert self._fm.get("description"), (
            "research-orchestrator missing 'description' in frontmatter"
        )


class TestBodyContent:
    """The body states every permitted and forbidden action, and points to
    the role-separation policy as their source."""

    _text = _AGENT_FILE.read_text(encoding="utf-8")

    def test_permitted_actions_present(self):
        for action in _PERMITTED_ACTIONS:
            assert action in self._text, (
                f"research-orchestrator body missing permitted action: '{action}'"
            )

    def test_forbidden_actions_present(self):
        for action in _FORBIDDEN_ACTIONS:
            assert action in self._text, (
                f"research-orchestrator body missing forbidden action: '{action}'"
            )

    def test_references_role_separation_policy(self):
        pattern = re.compile(r"role-separation(\.md)?", re.IGNORECASE)
        assert pattern.search(self._text), (
            "research-orchestrator body does not reference the role-separation policy"
        )


class TestRoleSeparationPolicyExists:
    """The referenced policy file must actually exist for the reference to
    resolve — a broken cross-reference would defeat the traceability the
    story asks for."""

    def test_role_separation_policy_file_exists(self):
        assert _ROLE_SEPARATION_POLICY.exists(), (
            f"role-separation.md not found at {_ROLE_SEPARATION_POLICY}"
        )
