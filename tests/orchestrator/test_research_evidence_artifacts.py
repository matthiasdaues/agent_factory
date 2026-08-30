"""Tests for the source-record and conjecture templates/schemas (ST-0020).

Source-record and conjecture are the evidence and claim-forming artifacts of
the falsification-driven research playbook (Procedure Steps 4 and 5). Both are
validated by `factory/scripts/schema-validate` (ST-0018), the deterministic
schema-only gate — so these tests exercise the same process seam as
`test_schema_validate.py`: writing a throwaway artifact JSON into `tmp_path`
and asserting the CLI's exit code against the real, checked-in schema files.

The load-bearing case (backlog ST-0020, Acceptance Criteria): a conjecture
without `possible_refuting_evidence` must fail validation — an unfalsifiable
claim cannot enter review. A source-record missing any required field must
likewise fail. A structural check ties each template's field labels to its
schema's `required` list so the two artifacts can never name a field
differently.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_VALIDATE = _ROOT / "factory" / "scripts" / "schema-validate"

_SOURCE_SCHEMA = (
    _ROOT / "factory" / "rulebooks" / "schemas" / "research-source-record.schema.json"
)
_CONJECTURE_SCHEMA = (
    _ROOT / "factory" / "rulebooks" / "schemas" / "research-conjecture.schema.json"
)
_SOURCE_TEMPLATE = (
    _ROOT / "factory" / "rulebooks" / "templates" / "research-source-record.md"
)
_CONJECTURE_TEMPLATE = (
    _ROOT / "factory" / "rulebooks" / "templates" / "research-conjecture.md"
)

_VALID_SOURCE_RECORD = {
    "source_identity": "Quarterly infrastructure incident report Q2-2026",
    "author_or_issuing_body": "Regional Grid Operator, Safety Division",
    "publisher": "Regional Grid Operator",
    "publication_date": "2026-07-01T00:00:00Z",
    "relevant_event_date": "2026-06-15",
    "source_family": "primary-operator-filing",
    "precise_evidence_location": "Section 4.2, Table 7, row 3",
    "method": "Post-incident telemetry review by the operator's safety team",
    "limitations": "Self-reported by the party under scrutiny; no external audit",
    "provenance": "Obtained via public regulatory filing portal, filing #2026-Q2-118",
}

_VALID_CONJECTURE = {
    "claim": "The Q2-2026 outage was caused by relay firmware regression, not weather",
    "scope": "Applies only to the Q2-2026 outage on feeder 14; not generalised to other feeders",
    "assumptions": [
        "The relay logs are complete",
        "The timestamp clock was not skewed",
    ],
    "supporting_evidence": [
        "SRC-0001: telemetry shows relay trip before storm arrival"
    ],
    "contrary_evidence": [
        "SRC-0002: weather service logged severe wind at the same minute"
    ],
    "possible_refuting_evidence": (
        "A relay firmware audit showing no regression shipped before the outage, "
        "or a timestamp reconciliation showing the storm preceded the trip"
    ),
    "planned_tests": [
        "Request the relay vendor's firmware changelog for the affected build"
    ],
    "qualifications": ["Confidence is provisional pending the vendor changelog"],
    "content_hash": "a" * 64,
}


def run(artifact_path: Path, schema_path: Path) -> subprocess.CompletedProcess:
    """Invoke the real `schema-validate` CLI, the same process seam production uses."""
    return subprocess.run(
        [sys.executable, str(_VALIDATE), str(artifact_path), str(schema_path)],
        capture_output=True,
        text=True,
    )


def _write_json(tmp_path: Path, name: str, data: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class TestSourceRecordSchema:
    """A well-formed source-record passes; each missing required field fails."""

    def test_wellformed_source_record_passes(self, tmp_path):
        artifact = _write_json(tmp_path, "source-record.json", _VALID_SOURCE_RECORD)
        r = run(artifact, _SOURCE_SCHEMA)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_missing_required_field_fails(self, tmp_path):
        schema = json.loads(_SOURCE_SCHEMA.read_text(encoding="utf-8"))
        required_fields = schema["required"]
        assert required_fields, "source-record schema must declare required fields"

        for field in required_fields:
            incomplete = dict(_VALID_SOURCE_RECORD)
            del incomplete[field]
            artifact = _write_json(tmp_path, f"missing-{field}.json", incomplete)
            r = run(artifact, _SOURCE_SCHEMA)
            assert r.returncode != 0, f"expected failure with '{field}' missing"
            assert field in r.stdout

    def test_source_family_is_required(self):
        # Called out explicitly in the story: source_family is what later lets
        # policy detect that copied sources are not independent.
        schema = json.loads(_SOURCE_SCHEMA.read_text(encoding="utf-8"))
        assert "source_family" in schema["required"]


class TestConjectureSchema:
    """A well-formed conjecture passes; a missing falsification criterion fails."""

    def test_wellformed_conjecture_passes(self, tmp_path):
        artifact = _write_json(tmp_path, "conjecture.json", _VALID_CONJECTURE)
        r = run(artifact, _CONJECTURE_SCHEMA)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_missing_possible_refuting_evidence_fails(self, tmp_path):
        """The load-bearing case: an unfalsifiable claim cannot enter review."""
        incomplete = dict(_VALID_CONJECTURE)
        del incomplete["possible_refuting_evidence"]
        artifact = _write_json(tmp_path, "conjecture-no-refutation.json", incomplete)
        r = run(artifact, _CONJECTURE_SCHEMA)
        assert r.returncode != 0
        assert "possible_refuting_evidence" in r.stdout

    def test_claim_is_a_single_string_not_an_array(self, tmp_path):
        # Exactly one claim per conjecture — an array of claims must be rejected.
        multi_claim = dict(_VALID_CONJECTURE)
        multi_claim["claim"] = ["first claim", "second claim"]
        artifact = _write_json(tmp_path, "conjecture-multi-claim.json", multi_claim)
        r = run(artifact, _CONJECTURE_SCHEMA)
        assert r.returncode != 0

    def test_missing_other_required_fields_fails(self, tmp_path):
        schema = json.loads(_CONJECTURE_SCHEMA.read_text(encoding="utf-8"))
        required_fields = schema["required"]
        assert required_fields, "conjecture schema must declare required fields"

        for field in required_fields:
            incomplete = dict(_VALID_CONJECTURE)
            del incomplete[field]
            artifact = _write_json(tmp_path, f"missing-{field}.json", incomplete)
            r = run(artifact, _CONJECTURE_SCHEMA)
            assert r.returncode != 0, f"expected failure with '{field}' missing"
            assert field in r.stdout


class TestTemplatesMatchSchemas:
    """Field labels in each template must match its schema's property names verbatim."""

    def test_source_record_template_names_every_required_field(self):
        schema = json.loads(_SOURCE_SCHEMA.read_text(encoding="utf-8"))
        template_text = _SOURCE_TEMPLATE.read_text(encoding="utf-8")
        for field in schema["required"]:
            assert field in template_text, (
                f"'{field}' missing from source-record template"
            )

    def test_conjecture_template_names_every_required_field(self):
        schema = json.loads(_CONJECTURE_SCHEMA.read_text(encoding="utf-8"))
        template_text = _CONJECTURE_TEMPLATE.read_text(encoding="utf-8")
        for field in schema["required"]:
            assert field in template_text, f"'{field}' missing from conjecture template"
