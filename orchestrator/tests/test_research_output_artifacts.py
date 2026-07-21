"""Tests for the claim-register and final-report templates/schemas (ST-0022).

These are the two output artifacts of the falsification-driven research
playbook: the claim register separates surviving, refuted, unresolved, and
superseded claims; the final report separates surviving findings from
refuted conjectures, unresolved alternatives, recommendations, evidence gaps,
and limitations, and requires every factual finding to cite the surviving
claim(s) it rests on.

Exercised through the same seam as `test_schema_validate.py`: the
`schema-validate` CLI (ST-0018), invoked as a subprocess against throwaway
JSON fixtures written into `tmp_path`. That script is the load-bearing gate
these schemas will be checked against for real, so testing through it (rather
than re-implementing JSON Schema checks in the test) proves the schemas work
against the actual validator, not an assumption about it.

Required cases (ST-0022 acceptance criteria):
1. A well-formed instance of each artifact passes.
2. A final-report factual section (`findings[]`) without a
   `surviving_claim_refs` reference fails.
3. A claim-register surviving claim missing a required field (`failed_tests`
   or `qualifications`) fails.
4. Every schema `required` property name appears verbatim in the matching
   template, so the template never drifts out of step with what the schema
   demands.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_VALIDATE = _ROOT / "factory" / "scripts" / "schema-validate"

_SCHEMAS_DIR = _ROOT / "factory" / "rulebooks" / "schemas"
_TEMPLATES_DIR = _ROOT / "factory" / "rulebooks" / "templates"

_CLAIM_REGISTER_SCHEMA = _SCHEMAS_DIR / "research-claim-register.schema.json"
_FINAL_REPORT_SCHEMA = _SCHEMAS_DIR / "research-final-report.schema.json"
_CLAIM_REGISTER_TEMPLATE = _TEMPLATES_DIR / "research-claim-register.md"
_FINAL_REPORT_TEMPLATE = _TEMPLATES_DIR / "research-final-report.md"


def run(artifact: Path, schema: Path) -> subprocess.CompletedProcess:
    """Invoke `schema-validate` exactly as the research skills/agents do."""
    return subprocess.run(
        [sys.executable, str(_VALIDATE), str(artifact), str(schema)],
        capture_output=True,
        text=True,
    )


def _write_json(tmp_path: Path, name: str, data: Dict[str, Any]) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# A minimal, fully-populated surviving claim satisfying every required field
# from claim-register.schema.json.
def _surviving_claim(**overrides: Any) -> Dict[str, Any]:
    claim = {
        "claim_text": "The validator rejects artifacts missing a required field.",
        "scope": "Applies to any artifact validated with schema-validate.",
        "assumptions": ["schema-validate is invoked with a matching schema"],
        "evidence": ["test_schema_validate.py::TestRequiredTestsItem1"],
        "tests": ["missing-required-field fails validation"],
        "failed_tests": [],
        "reviews": ["ST-0018 developer-agent self-review"],
        "vote_result": "accept",
        "qualifications": ["only covers the supported keyword subset"],
        "remaining_possible_refuters": [
            "a future keyword the validator does not yet implement"
        ],
        "applicable_date": "2026-07-20T00:00:00Z",
    }
    claim.update(overrides)
    return claim


_VALID_CLAIM_REGISTER = {
    "surviving_claims": [_surviving_claim()],
    "refuted_claims": [],
    "unresolved_claims": [],
    "superseded_claims": [],
}


def _finding(**overrides: Any) -> Dict[str, Any]:
    finding = {
        "title": "Missing required fields are rejected",
        "summary": ("schema-validate exits non-zero when a required field is absent."),
        "surviving_claim_refs": ["CLAIM-0001"],
    }
    finding.update(overrides)
    return finding


_VALID_FINAL_REPORT = {
    "findings": [_finding()],
    "refuted_conjectures": [],
    "unresolved_alternatives": [],
    "recommendations": [],
    "evidence_gaps": [],
    "limitations": [],
}


class TestWellFormedArtifactsPass:
    """AC: templates/schemas admit a correctly populated instance."""

    def test_wellformed_claim_register_passes(self, tmp_path):
        artifact = _write_json(tmp_path, "claim-register.json", _VALID_CLAIM_REGISTER)
        result = run(artifact, _CLAIM_REGISTER_SCHEMA)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_wellformed_final_report_passes(self, tmp_path):
        artifact = _write_json(tmp_path, "final-report.json", _VALID_FINAL_REPORT)
        result = run(artifact, _FINAL_REPORT_SCHEMA)
        assert result.returncode == 0, result.stdout + result.stderr


class TestFinalReportRequiresSurvivingClaimRefs:
    """AC: a factual section without a surviving-claim reference fails."""

    def test_finding_missing_surviving_claim_refs_fails(self, tmp_path):
        report = dict(_VALID_FINAL_REPORT)
        finding = _finding()
        del finding["surviving_claim_refs"]
        report["findings"] = [finding]
        artifact = _write_json(tmp_path, "final-report.json", report)

        result = run(artifact, _FINAL_REPORT_SCHEMA)

        assert result.returncode != 0
        assert "surviving_claim_refs" in result.stdout

    def test_finding_with_empty_surviving_claim_refs_fails(self, tmp_path):
        report = dict(_VALID_FINAL_REPORT)
        report["findings"] = [_finding(surviving_claim_refs=[])]
        artifact = _write_json(tmp_path, "final-report.json", report)

        result = run(artifact, _FINAL_REPORT_SCHEMA)

        assert result.returncode != 0


class TestClaimRegisterRequiresFieldsPerSurvivingClaim:
    """AC: a surviving claim missing a required field fails."""

    def test_missing_failed_tests_fails(self, tmp_path):
        register = dict(_VALID_CLAIM_REGISTER)
        claim = _surviving_claim()
        del claim["failed_tests"]
        register["surviving_claims"] = [claim]
        artifact = _write_json(tmp_path, "claim-register.json", register)

        result = run(artifact, _CLAIM_REGISTER_SCHEMA)

        assert result.returncode != 0
        assert "failed_tests" in result.stdout

    def test_missing_qualifications_fails(self, tmp_path):
        register = dict(_VALID_CLAIM_REGISTER)
        claim = _surviving_claim()
        del claim["qualifications"]
        register["surviving_claims"] = [claim]
        artifact = _write_json(tmp_path, "claim-register.json", register)

        result = run(artifact, _CLAIM_REGISTER_SCHEMA)

        assert result.returncode != 0
        assert "qualifications" in result.stdout

    def test_missing_top_level_disposition_array_fails(self, tmp_path):
        register = dict(_VALID_CLAIM_REGISTER)
        del register["superseded_claims"]
        artifact = _write_json(tmp_path, "claim-register.json", register)

        result = run(artifact, _CLAIM_REGISTER_SCHEMA)

        assert result.returncode != 0
        assert "superseded_claims" in result.stdout


class TestTemplatesMatchSchemaFieldNames:
    """Structural check: every schema `required` name is named, verbatim, in
    the matching template — the template can describe a field with more
    prose than the schema does, but it may never rename or drop one.
    """

    @staticmethod
    def _required_names(schema: Dict[str, Any]) -> set:
        """Collect every property name listed in any `required` array,
        walking into array `items` schemas (where the per-claim / per-finding
        required fields actually live).
        """
        names: set = set()

        def _walk(node: Any) -> None:
            if not isinstance(node, dict):
                return
            for required_name in node.get("required", []):
                names.add(required_name)
            if "items" in node:
                _walk(node["items"])
            for prop_schema in node.get("properties", {}).values():
                _walk(prop_schema)

        _walk(schema)
        return names

    def test_claim_register_template_names_every_required_field(self):
        schema = json.loads(_CLAIM_REGISTER_SCHEMA.read_text(encoding="utf-8"))
        template_text = _CLAIM_REGISTER_TEMPLATE.read_text(encoding="utf-8")

        required_names = self._required_names(schema)
        assert required_names, "expected at least one required field"
        missing = [name for name in required_names if name not in template_text]

        assert not missing, f"template is missing field names: {missing}"

    def test_final_report_template_names_every_required_field(self):
        schema = json.loads(_FINAL_REPORT_SCHEMA.read_text(encoding="utf-8"))
        template_text = _FINAL_REPORT_TEMPLATE.read_text(encoding="utf-8")

        required_names = self._required_names(schema)
        assert required_names, "expected at least one required field"
        missing = [name for name in required_names if name not in template_text]

        assert not missing, f"template is missing field names: {missing}"


@pytest.mark.parametrize(
    "schema_path,template_path",
    [
        (_CLAIM_REGISTER_SCHEMA, _CLAIM_REGISTER_TEMPLATE),
        (_FINAL_REPORT_SCHEMA, _FINAL_REPORT_TEMPLATE),
    ],
)
def test_schema_and_template_files_exist(schema_path, template_path):
    """Sanity check on the story's declared outputs before anything else
    is asked of them."""
    assert schema_path.is_file()
    assert template_path.is_file()
