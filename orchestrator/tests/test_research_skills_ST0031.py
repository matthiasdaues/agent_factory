"""Tests for claim-formulation and refutation-design skills (ST-0031).

The claim-formulation and refutation-design skills are capability definitions
that support the falsification-driven research workflow. Tests verify:

1. File existence: both skill files are created at the expected paths.
2. Frontmatter validity: each file has `name`, `description`, `category`, and
   proper YAML frontmatter — the structure index-lint expects.
3. Content completeness: each skill describes its purpose, inputs, outputs,
   and core process, and includes key constraints and principles required
   by the specification.
"""

from __future__ import annotations

import re
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[2]
_SKILLS_DIR = _ROOT / "factory" / "skills"

_CLAIM_FORMULATION = _SKILLS_DIR / "claim-formulation" / "SKILL.md"
_REFUTATION_DESIGN = _SKILLS_DIR / "refutation-design" / "SKILL.md"


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


class TestFilesExist:
    """Deliverables are created at the expected paths."""

    def test_claim_formulation_exists(self):
        assert _CLAIM_FORMULATION.exists(), (
            f"Claim-formulation skill not found at {_CLAIM_FORMULATION}"
        )

    def test_refutation_design_exists(self):
        assert _REFUTATION_DESIGN.exists(), (
            f"Refutation-design skill not found at {_REFUTATION_DESIGN}"
        )


class TestFrontmatterValid:
    """Each skill has valid frontmatter with required keys."""

    def test_claim_formulation_frontmatter(self):
        fm = _parse_frontmatter(_CLAIM_FORMULATION)
        assert fm.get("name") == "claim-formulation", (
            "claim-formulation missing or incorrect 'name' in frontmatter"
        )
        assert fm.get("description"), (
            "claim-formulation missing 'description' in frontmatter"
        )
        assert fm.get("category") == "research", (
            "claim-formulation category must be 'research'"
        )

    def test_refutation_design_frontmatter(self):
        fm = _parse_frontmatter(_REFUTATION_DESIGN)
        assert fm.get("name") == "refutation-design", (
            "refutation-design missing or incorrect 'name' in frontmatter"
        )
        assert fm.get("description"), (
            "refutation-design missing 'description' in frontmatter"
        )
        assert fm.get("category") == "research", (
            "refutation-design category must be 'research'"
        )


class TestClaimFormulationContent:
    """Claim-formulation skill must describe all required elements."""

    _text = _CLAIM_FORMULATION.read_text(encoding="utf-8")

    # Core content elements from the specification and acceptance criteria.
    _required_phrases = [
        "precise.*testable claim",
        "scope",
        "assumption",
        "content hash",
        "refutation.*condition",
    ]

    def test_required_elements_present(self):
        """Every required element from the specification appears in the skill."""
        for phrase in self._required_phrases:
            pattern = re.compile(phrase, re.IGNORECASE | re.DOTALL)
            assert pattern.search(self._text), (
                f"Claim-formulation skill missing required element: '{phrase}'"
            )

    def test_capability_statement(self):
        """Skill states it provides a capability."""
        pattern = re.compile(r"(capability|provides)", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Claim-formulation does not state it provides a capability"
        )

    def test_does_not_control_sequence(self):
        """Skill states it does not control sequence."""
        pattern = re.compile(
            r"does.*not.*control.*sequence|playbook.*control",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Claim-formulation does not state that playbook controls sequence"
        )

    def test_one_precise_testable_claim(self):
        """Skill describes producing one precise testable claim."""
        pattern = re.compile(
            r"one.*claim|atomic.*claim|single.*claim",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Claim-formulation does not emphasize producing one atomic claim"
        )


class TestRefutationDesignContent:
    """Refutation-design skill must describe all required elements."""

    _text = _REFUTATION_DESIGN.read_text(encoding="utf-8")

    # Core content elements from the specification and acceptance criteria.
    _required_phrases = [
        "refuting evidence",
        "severe test",
        "test.*record",
        "refutation.*condition",
    ]

    def test_required_elements_present(self):
        """Every required element from the specification appears in the skill."""
        for phrase in self._required_phrases:
            pattern = re.compile(phrase, re.IGNORECASE | re.DOTALL)
            assert pattern.search(self._text), (
                f"Refutation-design skill missing required element: '{phrase}'"
            )

    def test_capability_statement(self):
        """Skill states it provides a capability."""
        pattern = re.compile(r"(capability|provides)", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Refutation-design does not state it provides a capability"
        )

    def test_does_not_control_sequence(self):
        """Skill states it does not control sequence."""
        pattern = re.compile(
            r"does.*not.*control.*sequence|playbook.*control",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Refutation-design does not state that playbook controls sequence"
        )

    def test_not_ready_without_refutation_condition(self):
        """Skill states claim without refutation condition is not ready for review."""
        pattern = re.compile(
            r"without.*refutation.*not.*ready|cannot.*refuted.*not.*ready|no.*refutation.*not.*ready",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Refutation-design does not state that claim without refutation "
            "condition is not ready for review"
        )

    def test_ask_what_would_refute(self):
        """Skill embodies the guiding principle of falsification."""
        pattern = re.compile(
            r"what.*would.*refut|serious.*attempt.*refutation",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Refutation-design does not emphasize asking what would refute the claim"
        )
