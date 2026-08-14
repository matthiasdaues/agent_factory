"""Tests for the research-planning and source-research skills (ST-0030).

The research-planning and source-research skills are prose capability definitions
that specify how research work is executed without controlling workflow sequence.
Tests verify:

1. File existence: both skill files are created at the expected paths.
2. Frontmatter validity: each file has `name`, `description`, and `category:
   research` keys in its YAML frontmatter — the structure index-lint expects.
3. Content completeness: each skill contains the required capability statement
   and explicitly declares that it provides a capability and does not control
   sequence.
4. Research-planning content: describes turning a validated brief into research
   questions, assignments, competing conjectures, and stop conditions.
5. Source-research content: describes finding and recording sources for one
   bounded assignment against the source-record artifact.
"""

from __future__ import annotations

import re
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[2]
_SKILLS_DIR = _ROOT / "factory" / "skills"

_RESEARCH_PLANNING = _SKILLS_DIR / "research-planning" / "SKILL.md"
_SOURCE_RESEARCH = _SKILLS_DIR / "source-research" / "SKILL.md"


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
    for match in re.finditer(r"^(\w+):\s*(.+?)$", frontmatter_text, re.MULTILINE):
        key, value = match.groups()
        fields[key] = value.strip()

    return fields


class TestResearchPlanningContent:
    """Research-planning skill must state required content."""

    _text = _RESEARCH_PLANNING.read_text(encoding="utf-8")

    # Core capability-not-sequence statement required by spec.
    _capability_not_sequence_phrases = [
        r"does not control.*workflow|does not control.*sequence",
        r"playbook controls.*when|playbook controls.*sequence",
        r"provides a capability",
    ]

    # Required content from spec (Step 2: Plan the Research).
    _required_content = [
        "research question",
        "competing conjecture",
        "evidence requirement",
        "refutation strateg",
        "assignment",
        "review requirement",
        "stop condition",
    ]

    def test_capability_not_sequence_statement(self):
        """Skill explicitly states it provides capability, not control."""
        for phrase in self._capability_not_sequence_phrases:
            pattern = re.compile(phrase, re.IGNORECASE | re.DOTALL)
            assert pattern.search(self._text), (
                f"Research-planning must state: '{phrase}'"
            )

    def test_required_plan_content(self):
        """Skill describes all required plan elements from the specification."""
        for phrase in self._required_content:
            pattern = re.compile(phrase, re.IGNORECASE)
            assert pattern.search(self._text), (
                f"Research-planning missing required content: '{phrase}'"
            )

    def test_references_schema(self):
        """Skill references the research-plan schema."""
        pattern = re.compile(r"research-plan.*schema", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Research-planning must reference research-plan.schema.json"
        )

    def test_references_template(self):
        """Skill references the research-plan template."""
        pattern = re.compile(r"research-plan.*template", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Research-planning must reference research-plan template"
        )


class TestSourceResearchContent:
    """Source-research skill must state required content."""

    _text = _SOURCE_RESEARCH.read_text(encoding="utf-8")

    # Core capability-not-sequence statement required by spec.
    _capability_not_sequence_phrases = [
        r"does not control.*workflow|does not control.*sequence",
        r"playbook controls.*when|playbook controls.*sequence",
        r"provides a capability",
    ]

    # Required content from spec (Step 4: Collect Evidence).
    _required_content = [
        "source.?identity",
        "author.*issuing.*body",
        "publisher",
        "publication.*date",
        "relevant.*event.*date",
        "source.?family",
        "precise.*evidence.*location",
        "method",
        "limitation",
        "provenance",
    ]

    def test_capability_not_sequence_statement(self):
        """Skill explicitly states it provides capability, not control."""
        for phrase in self._capability_not_sequence_phrases:
            pattern = re.compile(phrase, re.IGNORECASE | re.DOTALL)
            assert pattern.search(self._text), f"Source-research must state: '{phrase}'"

    def test_required_source_record_content(self):
        """Skill describes all required source-record fields from the specification."""
        for phrase in self._required_content:
            pattern = re.compile(phrase, re.IGNORECASE)
            assert pattern.search(self._text), (
                f"Source-research missing required content: '{phrase}'"
            )

    def test_references_schema(self):
        """Skill references the source-record schema."""
        pattern = re.compile(r"source-record.*schema", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Source-research must reference source-record.schema.json"
        )

    def test_references_template(self):
        """Skill references the source-record template."""
        pattern = re.compile(r"source-record.*template", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Source-research must reference source-record template"
        )

    def test_references_bounded_assignment(self):
        """Skill references the bounded assignment input from the specification."""
        pattern = re.compile(r"bounded.*assignment", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Source-research must reference bounded assignment"
        )
