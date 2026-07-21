"""Tests for the claim-reviewer agent definition (ST-0028).

The claim-reviewer agent is a prose agent definition that states the checks
it performs when attempting to refute a claim, and the boundary that keeps it
from editing the claim it reviews. Tests verify:

1. File existence: the agent definition is created at the expected path.
2. Frontmatter validity: `name`, `title`, `tier`, `phase`, `phase-name`, and
   `description` are present and carry the values `index-lint` expects
   (phase 6, phase-name Research) so the agent is discovered and indexed.
3. Content completeness: the body lists every review check from the
   specification (Falsification-Driven Research Workflow, §Agents → Claim
   Reviewer), states the may-not-edit-the-claim boundary, and references the
   role-separation policy.
"""

from __future__ import annotations

import re
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[2]
_AGENT = _ROOT / "factory" / "agents" / "claim-reviewer.md"


def _frontmatter_block(text: str) -> str:
    """Return the raw text between the opening and closing `---` markers.

    Frontmatter values here may be single-line scalars or YAML folded
    scalars (`>-`); this helper returns the raw block so per-key regexes
    can look for each key independently, rather than parsing full YAML.
    """
    assert text.startswith("---"), "file must start with frontmatter"
    end = text.find("\n---", 3)
    assert end != -1, "frontmatter must be closed with a second '---'"
    return text[3:end]


def _frontmatter_scalar(block: str, key: str) -> str:
    """Extract a single-line scalar value for `key` from the frontmatter block."""
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", block, re.MULTILINE)
    assert match, f"frontmatter missing key: '{key}'"
    return match.group(1).strip()


class TestFileExists:
    """The agent definition is created at the expected path."""

    def test_claim_reviewer_exists(self):
        assert _AGENT.exists(), f"claim-reviewer agent not found at {_AGENT}"


class TestFrontmatterValid:
    """Frontmatter carries the keys and values index-lint requires."""

    _text = _AGENT.read_text(encoding="utf-8")
    _block = _frontmatter_block(_text)

    def test_name(self):
        assert _frontmatter_scalar(self._block, "name") == "claim-reviewer"

    def test_title(self):
        assert _frontmatter_scalar(self._block, "title") == "Claim Reviewer"

    def test_tier(self):
        assert _frontmatter_scalar(self._block, "tier") == "standard"

    def test_phase_is_six(self):
        assert _frontmatter_scalar(self._block, "phase") == "6"

    def test_phase_name_is_research(self):
        assert _frontmatter_scalar(self._block, "phase-name") == "Research"

    def test_description_present(self):
        assert re.search(r"^description:\s*\S", self._block, re.MULTILINE), (
            "frontmatter missing 'description'"
        )


class TestReviewChecksPresent:
    """Body must list every review check from the proposal's Claim Reviewer section."""

    _text = _AGENT.read_text(encoding="utf-8")

    _required_checks = [
        "whether the claim can be falsified",
        "whether the sources support its exact wording",
        "whether the sources are independent",
        "whether credible alternatives were considered",
        "whether the tests were severe",
        "whether assumptions were added after a failed test",
        "whether the claim exceeds the tested scope",
    ]

    def test_all_review_checks_present(self):
        for check in self._required_checks:
            assert check in self._text, (
                f"claim-reviewer missing review check: '{check}'"
            )


class TestBoundaryAndPolicyReference:
    """Body states the may-not-edit-the-claim boundary and cites role-separation."""

    _text = _AGENT.read_text(encoding="utf-8")

    def test_may_not_edit_the_claim_boundary(self):
        pattern = re.compile(r"may not edit the claim", re.IGNORECASE)
        assert pattern.search(self._text), (
            "claim-reviewer does not state the may-not-edit-the-claim boundary"
        )

    def test_references_role_separation_policy(self):
        assert "role-separation" in self._text, (
            "claim-reviewer does not reference the role-separation policy"
        )
