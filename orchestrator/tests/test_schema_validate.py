"""Tests for `factory/scripts/schema-validate`.

schema-validate is stage 1 of the research validation order (schema → policy →
semantic): a deterministic, stdlib-only JSON Schema validator (ST-0018). It is
the load-bearing gate that ST-0019..0022 invoke via
`subprocess.run([sys.executable, "factory/scripts/schema-validate", artifact,
schema])`, so these tests exercise exactly that process seam — writing throwaway
schema and artifact JSON into `tmp_path` and asserting the CLI's exit code.

The load-bearing case (proposal "Required Tests", item 1): an artifact missing a
required field fails schema validation; a well-formed artifact passes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "schema-validate"


# A small schema exercising the keyword subset the research artifacts rely on:
# required fields, typed fields, an enum (artifact state), a pattern (identifier),
# and a date-time format (timestamp).
_SCHEMA = {
    "type": "object",
    "required": ["id", "state", "created_at", "votes"],
    "properties": {
        "id": {"type": "string", "pattern": "^CLAIM-[0-9]{4}$"},
        "state": {"type": "string", "enum": ["draft", "supported", "refuted"]},
        "created_at": {"type": "string", "format": "date-time"},
        "votes": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "enum": ["yes", "no", "abstain"]},
        },
    },
    "additionalProperties": False,
}

_VALID_ARTIFACT = {
    "id": "CLAIM-0007",
    "state": "supported",
    "created_at": "2026-07-20T12:00:00Z",
    "votes": ["yes", "no", "abstain"],
}


def _run(
    tmp_path: Path, artifact: dict, schema: dict = None
) -> subprocess.CompletedProcess:
    schema = _SCHEMA if schema is None else schema
    artifact_file = tmp_path / "artifact.json"
    schema_file = tmp_path / "schema.json"
    artifact_file.write_text(json.dumps(artifact), encoding="utf-8")
    schema_file.write_text(json.dumps(schema), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(artifact_file), str(schema_file)],
        capture_output=True,
        text=True,
    )


def _run_raw(
    tmp_path: Path, artifact_text: str, schema: dict = None
) -> subprocess.CompletedProcess:
    schema = _SCHEMA if schema is None else schema
    artifact_file = tmp_path / "artifact.json"
    schema_file = tmp_path / "schema.json"
    artifact_file.write_text(artifact_text, encoding="utf-8")
    schema_file.write_text(json.dumps(schema), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(artifact_file), str(schema_file)],
        capture_output=True,
        text=True,
    )


class TestRequiredTestsItem1:
    """The load-bearing proof: missing-required fails, well-formed passes."""

    def test_wellformed_artifact_passes(self, tmp_path):
        r = _run(tmp_path, _VALID_ARTIFACT)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_missing_required_field_fails(self, tmp_path):
        artifact = dict(_VALID_ARTIFACT)
        del artifact["created_at"]
        r = _run(tmp_path, artifact)
        assert r.returncode != 0
        assert "created_at" in r.stdout


class TestViolationClasses:
    def test_wrong_type_fails(self, tmp_path):
        artifact = dict(_VALID_ARTIFACT)
        artifact["votes"] = "yes"  # string where array is required
        r = _run(tmp_path, artifact)
        assert r.returncode != 0
        assert "votes" in r.stdout

    def test_disallowed_enum_fails(self, tmp_path):
        artifact = dict(_VALID_ARTIFACT)
        artifact["state"] = "unknown"
        r = _run(tmp_path, artifact)
        assert r.returncode != 0
        assert "state" in r.stdout

    def test_bad_pattern_fails(self, tmp_path):
        artifact = dict(_VALID_ARTIFACT)
        artifact["id"] = "claim-7"
        r = _run(tmp_path, artifact)
        assert r.returncode != 0
        assert "id" in r.stdout

    def test_bad_date_time_format_fails(self, tmp_path):
        artifact = dict(_VALID_ARTIFACT)
        artifact["created_at"] = "20 July 2026"
        r = _run(tmp_path, artifact)
        assert r.returncode != 0
        assert "created_at" in r.stdout

    def test_disallowed_additional_property_fails(self, tmp_path):
        artifact = dict(_VALID_ARTIFACT)
        artifact["surprise"] = "extra"
        r = _run(tmp_path, artifact)
        assert r.returncode != 0
        assert "surprise" in r.stdout

    def test_min_items_violation_fails(self, tmp_path):
        artifact = dict(_VALID_ARTIFACT)
        artifact["votes"] = []
        r = _run(tmp_path, artifact)
        assert r.returncode != 0

    def test_nested_item_enum_violation_fails(self, tmp_path):
        artifact = dict(_VALID_ARTIFACT)
        artifact["votes"] = ["yes", "maybe"]
        r = _run(tmp_path, artifact)
        assert r.returncode != 0


class TestConstKeyword:
    def test_const_mismatch_fails(self, tmp_path):
        schema = {
            "type": "object",
            "required": ["schema_version"],
            "properties": {"schema_version": {"const": "1.0"}},
        }
        r = _run(tmp_path, {"schema_version": "2.0"}, schema)
        assert r.returncode != 0

    def test_const_match_passes(self, tmp_path):
        schema = {
            "type": "object",
            "required": ["schema_version"],
            "properties": {"schema_version": {"const": "1.0"}},
        }
        r = _run(tmp_path, {"schema_version": "1.0"}, schema)
        assert r.returncode == 0, r.stdout + r.stderr


class TestOperationalErrors:
    def test_unparseable_artifact_json_errors(self, tmp_path):
        r = _run_raw(tmp_path, "{ not valid json ")
        assert r.returncode != 0

    def test_missing_artifact_file_errors(self, tmp_path):
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(_SCHEMA), encoding="utf-8")
        r = subprocess.run(
            [
                sys.executable,
                str(_SCRIPT),
                str(tmp_path / "does-not-exist.json"),
                str(schema_file),
            ],
            capture_output=True,
            text=True,
        )
        assert r.returncode != 0
