"""Tests for the evidence and report policies (ST-0024).

The evidence and report policies are prose rulebooks that enforce constraints
on research artifacts. Tests verify:

1. File existence: both policy files are created at the expected paths.
2. Frontmatter validity: each file has a `title`, `category`, `enforcement`,
   and `version` key in its YAML frontmatter — the structure index-lint expects.
3. Content completeness: each policy contains every requirement stated in the
   specification (Falsification-Driven Research Workflow, §Policies sections).
"""

from __future__ import annotations

import re
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[2]
_POLICIES_DIR = _ROOT / "factory" / "rulebooks" / "policies" / "research"

_EVIDENCE_POLICY = _POLICIES_DIR / "evidence-policy.md"
_REPORT_POLICY = _POLICIES_DIR / "report-policy.md"


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

    def test_evidence_policy_exists(self):
        assert _EVIDENCE_POLICY.exists(), (
            f"Evidence policy not found at {_EVIDENCE_POLICY}"
        )

    def test_report_policy_exists(self):
        assert _REPORT_POLICY.exists(), f"Report policy not found at {_REPORT_POLICY}"


class TestFrontmatterValid:
    """Each policy has valid frontmatter with required keys."""

    def test_evidence_policy_frontmatter(self):
        fm = _parse_frontmatter(_EVIDENCE_POLICY)
        assert fm.get("title"), "evidence-policy missing 'title' in frontmatter"
        assert fm.get("category") == "policies", (
            "evidence-policy category must be 'policies'"
        )
        assert fm.get("enforcement"), (
            "evidence-policy missing 'enforcement' in frontmatter"
        )
        assert fm.get("version"), "evidence-policy missing 'version' in frontmatter"

    def test_report_policy_frontmatter(self):
        fm = _parse_frontmatter(_REPORT_POLICY)
        assert fm.get("title"), "report-policy missing 'title' in frontmatter"
        assert fm.get("category") == "policies", (
            "report-policy category must be 'policies'"
        )
        assert fm.get("enforcement"), (
            "report-policy missing 'enforcement' in frontmatter"
        )
        assert fm.get("version"), "report-policy missing 'version' in frontmatter"


class TestEvidencePolicyContent:
    """Evidence policy must state all required evidence criteria."""

    _text = _EVIDENCE_POLICY.read_text(encoding="utf-8")

    # Core requirements from the specification.
    _required_phrases = [
        "precise source reference",
        "source date",
        "source provenance",
        "source-family",
        "source limitation",
        "contrary-evidence search",
        "separation.*evidence.*interpretation",
    ]

    # Key principle about source families and repetition.
    _key_principle = [
        "source family",
        "repetition.*not.*corroboration",
    ]

    def test_evidence_requirements_present(self):
        """Every requirement from the specification appears in the policy."""
        for phrase in self._required_phrases:
            pattern = re.compile(phrase, re.IGNORECASE | re.DOTALL)
            assert pattern.search(self._text), (
                f"Evidence policy missing required phrase: '{phrase}'"
            )

    def test_source_family_principle(self):
        """Policy states that copies of one source form a single family."""
        pattern = re.compile(r"(source family|single source family)", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Evidence policy does not explain source-family concept"
        )

    def test_repetition_not_corroboration(self):
        """Policy states that repetition is not independent corroboration."""
        pattern = re.compile(
            r"repetition.*not.*corroboration|repetition.*not.*independent",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), (
            "Evidence policy does not state that repetition is not corroboration"
        )


class TestReportPolicyContent:
    """Report policy must state all required report criteria and wording."""

    _text = _REPORT_POLICY.read_text(encoding="utf-8")

    # Core requirements from the specification.
    _required_phrases = [
        "surviving claim",
        "cite.*claim.*id",
        "material qualification",
        "failed.*test|inconclusive test",
        "distinction.*finding.*recommendation",
        "unresolved question",
        "proof.*language",
    ]

    # Preferred non-proof wording phrases.
    _preferred_wordings = [
        "survived the defined tests",
        "not refuted within the tested scope",
        "provisionally retained",
        "remains open to refutation",
    ]

    def test_report_requirements_present(self):
        """Every requirement from the specification appears in the policy."""
        for phrase in self._required_phrases:
            pattern = re.compile(phrase, re.IGNORECASE | re.DOTALL)
            assert pattern.search(self._text), (
                f"Report policy missing required phrase: '{phrase}'"
            )

    def test_preferred_wording_present(self):
        """Policy includes all four preferred non-proof wording phrases."""
        for wording in self._preferred_wordings:
            assert wording in self._text, (
                f"Report policy missing preferred wording: '{wording}'"
            )

    def test_claim_id_citation_required(self):
        """Policy requires that statements cite claim IDs."""
        pattern = re.compile(r"claim.*id|id.*claim", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Report policy does not require claim ID citation"
        )
