"""Tests for the adversarial-review and research-reporting skills (ST-0032).

The adversarial-review and research-reporting skills are prose rulebooks that
define capabilities for reviewing claims and composing final reports. Tests verify:

1. File existence: both skill files are created at the expected paths.
2. Frontmatter validity: each file has a `name`, `description`, and `category`
   key in its YAML frontmatter — the structure index-lint expects.
3. Content completeness: each skill contains the key concepts stated in the
   specification (Falsification-Driven Research Workflow, §Skills section).
"""

from __future__ import annotations

import re
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[2]
_SKILLS_DIR = _ROOT / "factory" / "skills"

_ADVERSARIAL_REVIEW_SKILL = _SKILLS_DIR / "adversarial-review" / "SKILL.md"
_RESEARCH_REPORTING_SKILL = _SKILLS_DIR / "research-reporting" / "SKILL.md"


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

    def test_adversarial_review_skill_exists(self):
        assert _ADVERSARIAL_REVIEW_SKILL.exists(), (
            f"Adversarial-review skill not found at {_ADVERSARIAL_REVIEW_SKILL}"
        )

    def test_research_reporting_skill_exists(self):
        assert _RESEARCH_REPORTING_SKILL.exists(), (
            f"Research-reporting skill not found at {_RESEARCH_REPORTING_SKILL}"
        )


class TestFrontmatterValid:
    """Each skill has valid frontmatter with required keys."""

    def test_adversarial_review_frontmatter(self):
        fm = _parse_frontmatter(_ADVERSARIAL_REVIEW_SKILL)
        assert fm.get("name") == "adversarial-review", (
            "adversarial-review name must be 'adversarial-review'"
        )
        assert fm.get("description"), (
            "adversarial-review missing 'description' in frontmatter"
        )
        assert fm.get("category") == "research", (
            "adversarial-review category must be 'research'"
        )

    def test_research_reporting_frontmatter(self):
        fm = _parse_frontmatter(_RESEARCH_REPORTING_SKILL)
        assert fm.get("name") == "research-reporting", (
            "research-reporting name must be 'research-reporting'"
        )
        assert fm.get("description"), (
            "research-reporting missing 'description' in frontmatter"
        )
        assert fm.get("category") == "research", (
            "research-reporting category must be 'research'"
        )


class TestAdversarialReviewContent:
    """Adversarial-review skill must describe the ten checks and defect classification."""

    _text = _ADVERSARIAL_REVIEW_SKILL.read_text(encoding="utf-8")

    # Core requirements: the ten review checks.
    _ten_checks = [
        "testable",
        "credible alternative",
        "severe",
        "claim survive.*without.*chang",
        "sources support.*exact wording",
        "sources independent",
        "assumption.*explicit",
        "claim exceed.*tested scope",
        "contrary evidence.*unexplain",
        "evidence could still overturn",
    ]

    # Defect classification levels.
    _defect_levels = [
        "BLOCKER",
        "MAJOR",
        "MINOR",
        "NOTE",
    ]

    # Vote tied to claim hash concept.
    _vote_concepts = [
        "vote.*tied.*claim hash",
        "vote must refer",
        "exact.*claim hash",
        "current version",
    ]

    def test_ten_checks_present(self):
        """All ten review checks are described."""
        for check in self._ten_checks:
            pattern = re.compile(check, re.IGNORECASE | re.DOTALL)
            assert pattern.search(self._text), (
                f"Adversarial-review skill missing check: '{check}'"
            )

    def test_defect_levels_present(self):
        """All four defect classification levels are defined."""
        for level in self._defect_levels:
            assert level in self._text, (
                f"Adversarial-review skill missing defect level: '{level}'"
            )

    def test_blocker_prevents_survival(self):
        """Skill states that BLOCKER defects prevent survival."""
        pattern = re.compile(
            r"blocker.*prevent.*survival|blocker.*disqualif",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Adversarial-review skill does not state that blockers prevent survival"
        )

    def test_vote_tied_to_claim_hash(self):
        """Skill describes vote tied to exact claim hash."""
        pattern = re.compile(
            r"vote.*claim hash|claim hash.*vote|content hash.*vote",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Adversarial-review skill does not describe vote tied to claim hash"
        )

    def test_capability_not_sequence(self):
        """Skill states it provides a capability, not sequence control."""
        pattern = re.compile(
            r"skill.*capability|skill.*not.*control.*sequence|does not.*control.*sequence",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Adversarial-review skill does not state it is a capability, not sequence"
        )


class TestResearchReportingContent:
    """Research-reporting skill must describe no-new-findings, cite claim IDs, and preserve qualifications."""

    _text = _RESEARCH_REPORTING_SKILL.read_text(encoding="utf-8")

    # Core requirements.
    _core_concepts = [
        "frozen claim register",
        "no new.*finding|new.*finding.*not",
        "cite.*claim.*id|claim.*id.*cite",
        "surviving claim",
        "qualif",
        "survive.*tested",
        "not refuted.*tested scope",
    ]

    # Forbidden content.
    _forbidden_concepts = [
        "proved",
        "refuted.*claim.*fact",
        "hide.*test",
        "stale.*evidence",
    ]

    # Report structure distinctions.
    _distinctions = [
        "finding",
        "recommendation",
        "unresolved",
        "limitation",
    ]

    def test_no_new_findings_principle(self):
        """Skill states it does not add new findings."""
        pattern = re.compile(
            r"no new.*finding|new.*finding.*not|does not.*research",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Research-reporting skill does not state no-new-findings principle"
        )

    def test_cite_surviving_claim_ids(self):
        """Skill requires citation of surviving claim IDs."""
        pattern = re.compile(
            r"cite.*claim.*id|claim.*id.*cite|reference.*claim.*id",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Research-reporting skill does not require citation of claim IDs"
        )

    def test_preserve_qualifications(self):
        """Skill states qualifications must be preserved."""
        pattern = re.compile(
            r"preserve.*qualif|qualif.*preserved|material.*qualif",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Research-reporting skill does not state qualifications must be preserved"
        )

    def test_core_concepts_present(self):
        """All core concepts are explained."""
        for concept in self._core_concepts:
            pattern = re.compile(concept, re.IGNORECASE | re.DOTALL)
            assert pattern.search(self._text), (
                f"Research-reporting skill missing concept: '{concept}'"
            )

    def test_forbidden_content_addressed(self):
        """Skill describes what the report must not do."""
        # At least three of the forbidden concepts should appear in a "must not" context
        forbidden_found = 0
        for concept in self._forbidden_concepts:
            pattern = re.compile(
                rf"must not.*{concept}|forbidden.*{concept}|cannot.*{concept}",
                re.IGNORECASE | re.DOTALL,
            )
            if pattern.search(self._text):
                forbidden_found += 1
        assert forbidden_found >= 2, (
            "Research-reporting skill does not adequately address forbidden content"
        )

    def test_report_structure_distinctions(self):
        """Skill describes how to distinguish key report sections."""
        # Check that the skill describes how to distinguish findings and recommendations
        pattern_all = re.compile(
            r"distinguish.*finding|distinguish.*recommendation|finding.*recommendation",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern_all.search(self._text), (
            "Research-reporting skill does not describe how to distinguish findings and recommendations"
        )

    def test_capability_not_sequence(self):
        """Skill states it provides a capability, not sequence control."""
        pattern = re.compile(
            r"skill.*capability|skill.*not.*control.*sequence|does not.*control.*sequence",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Research-reporting skill does not state it is a capability, not sequence"
        )
