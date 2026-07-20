"""Tests for the role-separation and claim-admission policies (ST-0023).

The role-separation and claim-admission policies are prose rulebooks that
constrain who may act in which capacity during a research run, and what a
claim must satisfy to survive. Tests verify:

1. File existence: both policy files are created at the expected paths.
2. Frontmatter validity: each file has a `title`, `category`, `enforcement`,
   and `version` key in its YAML frontmatter — the structure index-lint expects.
3. Content completeness: each policy contains every rule stated in the
   specification (Falsification-Driven Research Workflow, §Policies sections).
"""

from __future__ import annotations

import re
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[2]
_POLICIES_DIR = _ROOT / "factory" / "rulebooks" / "policies" / "research"

_ROLE_SEPARATION_POLICY = _POLICIES_DIR / "role-separation.md"
_CLAIM_ADMISSION_POLICY = _POLICIES_DIR / "claim-admission-policy.md"


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

    def test_role_separation_policy_exists(self):
        assert _ROLE_SEPARATION_POLICY.exists(), (
            f"Role-separation policy not found at {_ROLE_SEPARATION_POLICY}"
        )

    def test_claim_admission_policy_exists(self):
        assert _CLAIM_ADMISSION_POLICY.exists(), (
            f"Claim-admission policy not found at {_CLAIM_ADMISSION_POLICY}"
        )


class TestFrontmatterValid:
    """Each policy has valid frontmatter with required keys."""

    def test_role_separation_policy_frontmatter(self):
        fm = _parse_frontmatter(_ROLE_SEPARATION_POLICY)
        assert fm.get("title"), "role-separation missing 'title' in frontmatter"
        assert fm.get("category") == "policies", (
            "role-separation category must be 'policies'"
        )
        assert fm.get("enforcement"), (
            "role-separation missing 'enforcement' in frontmatter"
        )
        assert fm.get("version"), "role-separation missing 'version' in frontmatter"

    def test_claim_admission_policy_frontmatter(self):
        fm = _parse_frontmatter(_CLAIM_ADMISSION_POLICY)
        assert fm.get("title"), "claim-admission-policy missing 'title' in frontmatter"
        assert fm.get("category") == "policies", (
            "claim-admission-policy category must be 'policies'"
        )
        assert fm.get("enforcement"), (
            "claim-admission-policy missing 'enforcement' in frontmatter"
        )
        assert fm.get("version"), (
            "claim-admission-policy missing 'version' in frontmatter"
        )


class TestRoleSeparationContent:
    """Role-separation policy must state all five role-conflict rules."""

    _text = _ROLE_SEPARATION_POLICY.read_text(encoding="utf-8")

    # The five role-conflict rules from the specification, as
    # loosely-matched patterns tolerant of surrounding prose.
    _required_rules = [
        r"claim author.*cannot.*review.*or.*vote",
        r"reviewer.*cannot.*edit.*the claim",
        r"orchestrator.*cannot.*vote",
        r"report writer.*cannot.*create.*findings",
        r"one agent.*cannot.*fill.*conflicting roles",
    ]

    def test_all_five_role_rules_present(self):
        """Every one of the five role-conflict rules appears in the policy."""
        for rule in self._required_rules:
            pattern = re.compile(rule, re.IGNORECASE | re.DOTALL)
            assert pattern.search(self._text), (
                f"Role-separation policy missing required rule: '{rule}'"
            )

    def test_names_governed_roles(self):
        """Policy names the roles it governs, so rules trace to responsibilities."""
        for role in [
            "Researcher",
            "Claim Reviewer",
            "Research Orchestrator",
            "Research Report Writer",
        ]:
            assert role in self._text, (
                f"Role-separation policy does not name role: '{role}'"
            )

    def test_names_governed_artifacts_or_fields(self):
        """Policy traces rules to the fields that carry role identity."""
        for field in ["claim_hash", "reviewer", "surviving_claim_refs"]:
            assert field in self._text, (
                f"Role-separation policy does not reference field: '{field}'"
            )

    def test_no_schema_definitions(self):
        """Policy is prose only — no embedded JSON schema definitions."""
        assert '"$schema"' not in self._text
        assert '"type": "object"' not in self._text

    def test_no_step_ordering(self):
        """Policy states rules, not a numbered procedure with step ordering."""
        assert "Step 1" not in self._text
        assert "### Step" not in self._text


class TestClaimAdmissionContent:
    """Claim-admission policy must state every admission condition."""

    _text = _CLAIM_ADMISSION_POLICY.read_text(encoding="utf-8")

    _required_conditions = [
        "one assertion",
        "clear scope",
        "explicit assumptions",
        "refutation condition",
        "required tests",
        "evidence checks",
        "required reviews",
        "no blocking defect",
        "unanswered material refutation",
    ]

    def test_all_admission_conditions_present(self):
        """Every admission condition from the specification appears in the policy."""
        for condition in self._required_conditions:
            pattern = re.compile(re.escape(condition), re.IGNORECASE)
            assert pattern.search(self._text), (
                f"Claim-admission policy missing required condition: '{condition}'"
            )

    def test_strict_majority_of_decisive_votes(self):
        """Policy states the strict-majority-of-decisive-votes threshold."""
        pattern = re.compile(
            r"strict majority.*decisive votes", re.IGNORECASE | re.DOTALL
        )
        assert pattern.search(self._text), (
            "Claim-admission policy does not state strict majority of decisive votes"
        )

    def test_decisive_votes_excludes_unresolved_and_abstain(self):
        """Policy identifies SURVIVE/REFUTE as decisive, distinct from non-decisive votes."""
        assert "SURVIVE" in self._text
        assert "REFUTE" in self._text
        assert "UNRESOLVED" in self._text
        assert "ABSTAIN" in self._text

    def test_current_claim_version_requirement(self):
        """Policy requires all votes to reference the current claim version."""
        pattern = re.compile(r"current claim version|current version", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Claim-admission policy does not require votes on the current claim version"
        )

    def test_process_standard_not_truth(self):
        """Policy records that a vote decides process standard, not truth."""
        pattern = re.compile(r"process standard", re.IGNORECASE)
        assert pattern.search(self._text), (
            "Claim-admission policy does not mention the process standard"
        )
        pattern_truth = re.compile(
            r"not.{0,40}true|does not decide whether.{0,40}true",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern_truth.search(self._text), (
            "Claim-admission policy does not state that a vote does not decide truth"
        )

    def test_no_schema_definitions(self):
        """Policy is prose only — no embedded JSON schema definitions."""
        assert '"$schema"' not in self._text
        assert '"type": "object"' not in self._text

    def test_no_step_ordering(self):
        """Policy states conditions, not a numbered procedure with step ordering."""
        assert "Step 1" not in self._text
        assert "### Step" not in self._text
