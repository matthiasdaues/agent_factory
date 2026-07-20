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


def _parse_frontmatter(file_path: Path) -> dict:
    """Extract frontmatter keys from a markdown file using regex.

    Frontmatter is delimited by --- at the start and end of the first block.
    Returns a dictionary of field names and values found in the frontmatter.
    """
    text = file_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}

    end_index = text.find("---", 3)  # Find closing ---
    if end_index == -1:
        return {}

    frontmatter_text = text[3:end_index]
    fields = {}

    # Extract key: value pairs from YAML-like structure.
    for match in re.finditer(r"^([\w-]+):\s*(.+?)$", frontmatter_text, re.MULTILINE):
        key, value = match.groups()
        fields[key] = value.strip()

    return fields


class TestFileExists:
    """The deliverable is created at the expected path."""

    def test_agent_file_exists(self):
        assert _AGENT_FILE.exists(), (
            f"research-report-writer agent not found at {_AGENT_FILE}"
        )


class TestFrontmatterValid:
    """The agent has valid frontmatter with the required keys and values."""

    _fm = _parse_frontmatter(_AGENT_FILE)

    def test_name(self):
        assert self._fm.get("name") == "research-report-writer"

    def test_title(self):
        assert self._fm.get("title") == "Research Report Writer"

    def test_tier(self):
        assert self._fm.get("tier") == "standard"

    def test_phase_is_six(self):
        assert self._fm.get("phase") == "6"

    def test_phase_name_is_research(self):
        assert self._fm.get("phase-name") == "Research"

    def test_description_present(self):
        assert self._fm.get("description"), (
            "research-report-writer missing 'description' in frontmatter"
        )


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
            r"factory/rulebooks/policies/research/report-policy\.md|report-policy\.md",
            re.IGNORECASE,
        )
        assert pattern.search(self._text), (
            "research-report-writer does not reference the report policy"
        )
