"""Tests for the adversarial-stage research artifacts (ST-0021).

Covers the paired template + JSON Schema for the three adversarial-stage
artifacts: the test record, the review, and the vote (proposal Procedure
Steps 7-9). Schemas are validated through `schema-validate` (ST-0018), the
stage-1 deterministic gate; these tests exercise exactly that process seam,
same as `test_schema_validate.py`.

Two kinds of proof:

1. Enum/reference discipline (proposal "Required Tests"): a well-formed
   instance of each artifact passes; an out-of-range `outcome`,
   `defect_level`, or `value` fails; a vote missing its `claim_hash` fails
   (this last case is what later lets policy enforce "changed claim
   invalidates prior votes" — a vote with no claim hash cannot be checked
   against the claim's current version).
2. Template/schema field parity: every property name a schema `required`
   lists must appear verbatim in the matching template, so an author filling
   in the template cannot silently omit a field the schema will reject.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_VALIDATE = _ROOT / "factory" / "scripts" / "schema-validate"
_SCHEMA_DIR = _ROOT / "factory" / "rulebooks" / "schemas" / "research"
_TEMPLATE_DIR = _ROOT / "factory" / "rulebooks" / "templates" / "research"

_TEST_RECORD_SCHEMA = _SCHEMA_DIR / "test-record.schema.json"
_REVIEW_SCHEMA = _SCHEMA_DIR / "review.schema.json"
_VOTE_SCHEMA = _SCHEMA_DIR / "vote.schema.json"

_TEST_RECORD_TEMPLATE = _TEMPLATE_DIR / "test-record.md"
_REVIEW_TEMPLATE = _TEMPLATE_DIR / "review.md"
_VOTE_TEMPLATE = _TEMPLATE_DIR / "vote.md"


def run(artifact_path: Path, schema_path: Path) -> subprocess.CompletedProcess:
    """Invoke `schema-validate` as a subprocess, the seam every caller uses."""
    return subprocess.run(
        [sys.executable, str(_VALIDATE), str(artifact_path), str(schema_path)],
        capture_output=True,
        text=True,
    )


def _write(tmp_path: Path, name: str, artifact: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(artifact), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Well-formed fixtures — one valid instance per artifact.
# ---------------------------------------------------------------------------

_VALID_TEST_RECORD = {
    "claim_id": "CLAIM-0007",
    "claim_version": 1,
    "test_question": "Does the claimed effect appear under condition X?",
    "refuting_result": "No measurable effect under condition X.",
    "method": "Controlled comparison against a null condition.",
    "evidence_examined": ["source-record: SRC-0012"],
    "observed_result": "Effect appeared at the predicted magnitude.",
    "limitations": "Single trial; no blinding.",
    "outcome": "SURVIVED",
}

_VALID_REVIEW = {
    "claim_id": "CLAIM-0007",
    "checks": {
        "testable": True,
        "alternatives_considered": True,
        "tests_severe": True,
        "survived_unchanged": True,
        "sources_support_wording": True,
        "sources_independent": True,
        "assumptions_explicit": True,
        "within_tested_scope": True,
        "contrary_evidence_addressed": True,
        "possible_overturning_evidence": True,
    },
    "defect_level": "NOTE",
}

_VALID_VOTE = {
    "review_ref": "REVIEW-CLAIM-0007-01",
    "claim_hash": "a" * 64,
    "reviewer": "reviewer-alice",
    "value": "SURVIVE",
}


class TestWellFormedArtifactsPass:
    """proposal "Required Tests" item 1: well-formed instances validate."""

    def test_test_record_passes(self, tmp_path):
        artifact = _write(tmp_path, "test-record.json", _VALID_TEST_RECORD)
        r = run(artifact, _TEST_RECORD_SCHEMA)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_review_passes(self, tmp_path):
        artifact = _write(tmp_path, "review.json", _VALID_REVIEW)
        r = run(artifact, _REVIEW_SCHEMA)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_vote_passes(self, tmp_path):
        artifact = _write(tmp_path, "vote.json", _VALID_VOTE)
        r = run(artifact, _VOTE_SCHEMA)
        assert r.returncode == 0, r.stdout + r.stderr


class TestEnumDiscipline:
    """Out-of-range enum values fail — the constraint policy later relies on."""

    def test_out_of_range_outcome_fails(self, tmp_path):
        artifact = dict(_VALID_TEST_RECORD)
        artifact["outcome"] = "MAYBE"
        path = _write(tmp_path, "test-record.json", artifact)
        r = run(path, _TEST_RECORD_SCHEMA)
        assert r.returncode != 0
        assert "outcome" in r.stdout

    def test_out_of_range_defect_level_fails(self, tmp_path):
        artifact = json.loads(json.dumps(_VALID_REVIEW))
        artifact["defect_level"] = "CRITICAL"
        path = _write(tmp_path, "review.json", artifact)
        r = run(path, _REVIEW_SCHEMA)
        assert r.returncode != 0
        assert "defect_level" in r.stdout

    def test_out_of_range_value_fails(self, tmp_path):
        artifact = dict(_VALID_VOTE)
        artifact["value"] = "MAYBE"
        path = _write(tmp_path, "vote.json", artifact)
        r = run(path, _VOTE_SCHEMA)
        assert r.returncode != 0
        assert "value" in r.stdout


class TestVoteMissingClaimHashFails:
    """A vote missing `claim_hash` fails — supports "changed claim invalidates
    prior votes": without a hash there is nothing to compare against the
    claim's current version."""

    def test_vote_missing_claim_hash_fails(self, tmp_path):
        artifact = dict(_VALID_VOTE)
        del artifact["claim_hash"]
        path = _write(tmp_path, "vote.json", artifact)
        r = run(path, _VOTE_SCHEMA)
        assert r.returncode != 0
        assert "claim_hash" in r.stdout


class TestTemplateSchemaFieldParity:
    """Every schema `required` property name must appear verbatim in the
    matching template, so filling in the template cannot silently omit a
    field the schema will reject."""

    @pytest.mark.parametrize(
        "schema_path, template_path",
        [
            (_TEST_RECORD_SCHEMA, _TEST_RECORD_TEMPLATE),
            (_REVIEW_SCHEMA, _REVIEW_TEMPLATE),
            (_VOTE_SCHEMA, _VOTE_TEMPLATE),
        ],
    )
    def test_required_fields_appear_in_template(self, schema_path, template_path):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        template_text = template_path.read_text(encoding="utf-8")
        for field in schema["required"]:
            assert field in template_text, (
                f"'{field}' required by {schema_path.name} "
                f"but absent from {template_path.name}"
            )

    def test_review_checks_fields_appear_in_template(self):
        schema = json.loads(_REVIEW_SCHEMA.read_text(encoding="utf-8"))
        template_text = _REVIEW_TEMPLATE.read_text(encoding="utf-8")
        for field in schema["properties"]["checks"]["required"]:
            assert field in template_text, (
                f"review check '{field}' absent from {_REVIEW_TEMPLATE.name}"
            )
