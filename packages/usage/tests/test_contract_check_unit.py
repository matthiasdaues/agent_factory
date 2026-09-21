"""Direct-import unit tests for usage.contract_check.

These tests call contract_check functions through the Python API
so coverage.py can instrument them (unlike subprocess-based tests).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from usage import contract_check
from usage.contract_check import (
    EXIT_OK,
    EXIT_OPERATIONAL,
    EXIT_VALIDATION,
    _check_additional,
    _check_minimum,
    _check_nested,
    _check_normalized_invariant,
    _check_properties,
    _check_required,
    _check_single_type,
    _check_type,
    _check_unsupported_keywords,
    _collect_input_files,
    _collect_jsonl_files,
    _is_non_bool_int,
    _matches_type,
    _validate_file,
    _validate_record,
    _run_validation,
    _load_and_check_schema,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_SCHEMA = {
    "type": "object",
    "required": ["name", "value"],
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "value": {"type": "integer", "minimum": 0},
    },
}

USAGE_SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent / "contracts" / "v1.schema.json"
)


@pytest.fixture()
def usage_schema() -> dict:
    with open(USAGE_SCHEMA_PATH) as fh:
        return json.load(fh)


def _valid_record() -> dict:
    return {
        "record_id": "rec-001",
        "project_id": "proj-001",
        "project_name": "demo",
        "normalized_input": 100,
        "normalized_output": 50,
        "normalized_total": 150,
        "cli": "claude-code",
        "session_id": "sess-001",
        "parent_session_id": None,
        "depth": 0,
        "recorded_at": "2026-01-15T10:00:00Z",
        "agent": None,
        "model": "claude-opus-4-6",
        "provider": "anthropic",
        "reported_input": 120,
        "reported_output": 60,
        "reported_cache_read": 30,
        "reported_cache_write": 10,
        "usage_granularity": "turn",
        "usage_capability": "full",
        "cache_miss_turns": 2,
        "cache_miss_input_tokens": 80,
        "late_early_input_ratio": 1.5,
        "exit_status": "success",
        "branch": "main",
        "commit_id": "abc123",
        "transcript_ref": {"path": "/t.jsonl", "span": None},
    }


# ---------------------------------------------------------------------------
# _check_single_type
# ---------------------------------------------------------------------------

class TestCheckSingleType:
    def test_string(self):
        assert _check_single_type("hello", "string") is True

    def test_integer(self):
        assert _check_single_type(42, "integer") is True

    def test_number_with_int(self):
        assert _check_single_type(42, "number") is True

    def test_number_with_float(self):
        assert _check_single_type(3.14, "number") is True

    def test_boolean(self):
        assert _check_single_type(True, "boolean") is True

    def test_object(self):
        assert _check_single_type({"a": 1}, "object") is True

    def test_array(self):
        assert _check_single_type([1, 2], "array") is True

    def test_null(self):
        assert _check_single_type(None, "null") is True

    def test_bool_rejected_as_integer(self):
        assert _check_single_type(True, "integer") is False

    def test_bool_rejected_as_number(self):
        assert _check_single_type(False, "number") is False

    def test_null_not_string(self):
        assert _check_single_type(None, "string") is False

    def test_string_not_integer(self):
        assert _check_single_type("42", "integer") is False

    def test_unknown_type_returns_false(self):
        assert _check_single_type("x", "unknown_type") is False


# ---------------------------------------------------------------------------
# _matches_type
# ---------------------------------------------------------------------------

class TestMatchesType:
    def test_single_type_string(self):
        assert _matches_type("hi", "string") is True

    def test_single_type_mismatch(self):
        assert _matches_type(42, "string") is False

    def test_type_list_first_match(self):
        assert _matches_type("hi", ["string", "null"]) is True

    def test_type_list_second_match(self):
        assert _matches_type(None, ["string", "null"]) is True

    def test_type_list_no_match(self):
        assert _matches_type(42, ["string", "null"]) is False


# ---------------------------------------------------------------------------
# _is_non_bool_int
# ---------------------------------------------------------------------------

class TestIsNonBoolInt:
    def test_regular_int(self):
        assert _is_non_bool_int(42) is True

    def test_bool_rejected(self):
        assert _is_non_bool_int(True) is False

    def test_float_rejected(self):
        assert _is_non_bool_int(3.14) is False

    def test_string_rejected(self):
        assert _is_non_bool_int("42") is False


# ---------------------------------------------------------------------------
# _check_required
# ---------------------------------------------------------------------------

class TestCheckRequired:
    def test_all_present(self):
        record = {"name": "x", "value": 1}
        assert _check_required(record, MINIMAL_SCHEMA, "f", 1) == []

    def test_missing_field(self):
        diags = _check_required({"name": "x"}, MINIMAL_SCHEMA, "f", 1)
        assert len(diags) == 1
        assert diags[0][3] == "SCHEMA_REQUIRED"
        assert "value" in diags[0][4]


# ---------------------------------------------------------------------------
# _check_additional
# ---------------------------------------------------------------------------

class TestCheckAdditional:
    def test_no_extra(self):
        record = {"name": "x", "value": 1}
        assert _check_additional(record, MINIMAL_SCHEMA, "f", 1) == []

    def test_extra_field(self):
        record = {"name": "x", "value": 1, "extra": True}
        diags = _check_additional(record, MINIMAL_SCHEMA, "f", 1)
        assert len(diags) == 1
        assert diags[0][3] == "SCHEMA_ADDITIONAL"

    def test_no_restriction(self):
        schema = {"properties": {"name": {"type": "string"}}}
        record = {"name": "x", "extra": True}
        assert _check_additional(record, schema, "f", 1) == []


# ---------------------------------------------------------------------------
# _check_type
# ---------------------------------------------------------------------------

class TestCheckType:
    def test_matching_type(self):
        assert _check_type("name", "x", {"type": "string"}, "f", 1) is None

    def test_mismatched_type(self):
        diag = _check_type("name", 42, {"type": "string"}, "f", 1)
        assert diag is not None
        assert diag[3] == "SCHEMA_TYPE"

    def test_no_type_in_schema(self):
        assert _check_type("name", 42, {}, "f", 1) is None

    def test_type_list_format(self):
        diag = _check_type("x", 42, {"type": ["string", "null"]}, "f", 1)
        assert diag is not None
        assert "string | null" in diag[4]


# ---------------------------------------------------------------------------
# _check_minimum
# ---------------------------------------------------------------------------

class TestCheckMinimum:
    def test_above_minimum(self):
        assert _check_minimum("v", 5, {"minimum": 0}, "f", 1) is None

    def test_at_minimum(self):
        assert _check_minimum("v", 0, {"minimum": 0}, "f", 1) is None

    def test_below_minimum(self):
        diag = _check_minimum("v", -1, {"minimum": 0}, "f", 1)
        assert diag is not None
        assert diag[3] == "SCHEMA_MINIMUM"

    def test_no_minimum_in_schema(self):
        assert _check_minimum("v", -1, {}, "f", 1) is None

    def test_non_int_skipped(self):
        assert _check_minimum("v", "x", {"minimum": 0}, "f", 1) is None

    def test_bool_skipped(self):
        assert _check_minimum("v", True, {"minimum": 0}, "f", 1) is None


# ---------------------------------------------------------------------------
# _check_nested
# ---------------------------------------------------------------------------

class TestCheckNested:
    def test_non_dict_skipped(self):
        assert _check_nested("f", "x", {"properties": {}}, "f", 1) == []

    def test_no_properties_skipped(self):
        assert _check_nested("f", {"a": 1}, {"type": "object"}, "f", 1) == []

    def test_nested_validation(self):
        schema = {
            "properties": {
                "inner": {"type": "string"},
            },
            "required": ["inner"],
        }
        diags = _check_nested("outer", {}, schema, "f", 1)
        assert len(diags) == 1
        assert diags[0][2] == "outer.inner"


# ---------------------------------------------------------------------------
# _check_normalized_invariant
# ---------------------------------------------------------------------------

class TestCheckNormalizedInvariant:
    def test_correct_sum(self):
        record = {"normalized_input": 100, "normalized_output": 50, "normalized_total": 150}
        assert _check_normalized_invariant(record, "f", 1) == []

    def test_incorrect_sum(self):
        record = {"normalized_input": 100, "normalized_output": 50, "normalized_total": 200}
        diags = _check_normalized_invariant(record, "f", 1)
        assert len(diags) == 1
        assert diags[0][3] == "INVARIANT_NORMALIZED_TOTAL"

    def test_missing_fields(self):
        assert _check_normalized_invariant({}, "f", 1) == []

    def test_null_fields(self):
        record = {"normalized_input": None, "normalized_output": 50, "normalized_total": 50}
        assert _check_normalized_invariant(record, "f", 1) == []


# ---------------------------------------------------------------------------
# _validate_record
# ---------------------------------------------------------------------------

class TestValidateRecord:
    def test_valid_record(self, usage_schema):
        rec = _valid_record()
        assert _validate_record(rec, usage_schema, "f", 1) == []

    def test_missing_required(self, usage_schema):
        rec = _valid_record()
        del rec["cli"]
        diags = _validate_record(rec, usage_schema, "f", 1)
        codes = {d[3] for d in diags}
        assert "SCHEMA_REQUIRED" in codes

    def test_additional_property(self, usage_schema):
        rec = _valid_record()
        rec["bogus"] = "x"
        diags = _validate_record(rec, usage_schema, "f", 1)
        codes = {d[3] for d in diags}
        assert "SCHEMA_ADDITIONAL" in codes

    def test_type_mismatch(self, usage_schema):
        rec = _valid_record()
        rec["normalized_input"] = "not_an_int"
        diags = _validate_record(rec, usage_schema, "f", 1)
        codes = {d[3] for d in diags}
        assert "SCHEMA_TYPE" in codes

    def test_minimum_violation(self, usage_schema):
        rec = _valid_record()
        rec["normalized_input"] = -1
        rec["normalized_total"] = rec["normalized_output"] - 1
        diags = _validate_record(rec, usage_schema, "f", 1)
        codes = {d[3] for d in diags}
        assert "SCHEMA_MINIMUM" in codes

    def test_invariant_violation(self, usage_schema):
        rec = _valid_record()
        rec["normalized_total"] = 999
        diags = _validate_record(rec, usage_schema, "f", 1)
        codes = {d[3] for d in diags}
        assert "INVARIANT_NORMALIZED_TOTAL" in codes

    def test_nested_object(self, usage_schema):
        rec = _valid_record()
        rec["transcript_ref"] = {"path": 42, "span": None}
        diags = _validate_record(rec, usage_schema, "f", 1)
        fields = {d[2] for d in diags}
        assert any("transcript_ref.path" in f for f in fields)


# ---------------------------------------------------------------------------
# _check_unsupported_keywords
# ---------------------------------------------------------------------------

class TestCheckUnsupportedKeywords:
    def test_clean_schema(self, usage_schema):
        assert _check_unsupported_keywords(usage_schema) == []

    def test_unsupported_keyword(self):
        schema = {"type": "object", "minItems": 1}
        diags = _check_unsupported_keywords(schema)
        assert len(diags) == 1
        assert "minItems" in diags[0]

    def test_nested_unsupported(self):
        schema = {
            "type": "object",
            "properties": {"x": {"type": "string", "pattern": "^a"}},
        }
        diags = _check_unsupported_keywords(schema)
        assert any("pattern" in d for d in diags)


# ---------------------------------------------------------------------------
# _validate_file
# ---------------------------------------------------------------------------

class TestValidateFile:
    def test_valid_file(self, tmp_path, usage_schema):
        f = tmp_path / "valid.jsonl"
        f.write_text(json.dumps(_valid_record()) + "\n")
        assert _validate_file(str(f), usage_schema) == []

    def test_invalid_json(self, tmp_path, usage_schema):
        f = tmp_path / "bad.jsonl"
        f.write_text("{not json\n")
        diags = _validate_file(str(f), usage_schema)
        assert len(diags) == 1
        assert diags[0][3] == "SCHEMA_PARSE"

    def test_non_object_line(self, tmp_path, usage_schema):
        f = tmp_path / "arr.jsonl"
        f.write_text("[1, 2, 3]\n")
        diags = _validate_file(str(f), usage_schema)
        assert len(diags) == 1
        assert diags[0][3] == "SCHEMA_TYPE"

    def test_blank_lines_skipped(self, tmp_path, usage_schema):
        f = tmp_path / "blank.jsonl"
        f.write_text("\n" + json.dumps(_valid_record()) + "\n\n")
        assert _validate_file(str(f), usage_schema) == []

    def test_missing_file(self, usage_schema):
        diags = _validate_file("/no/such/file.jsonl", usage_schema)
        assert len(diags) == 1
        assert diags[0][3] == "SCHEMA_PARSE"
        assert "cannot read file" in diags[0][4]

    def test_mixed_valid_and_invalid(self, tmp_path, usage_schema):
        f = tmp_path / "mixed.jsonl"
        lines = [json.dumps(_valid_record()), '{"bad": true}']
        f.write_text("\n".join(lines) + "\n")
        diags = _validate_file(str(f), usage_schema)
        assert len(diags) > 0


# ---------------------------------------------------------------------------
# _collect_jsonl_files
# ---------------------------------------------------------------------------

class TestCollectJsonlFiles:
    def test_finds_jsonl(self, tmp_path):
        (tmp_path / "a.jsonl").write_text("{}\n")
        (tmp_path / "b.txt").write_text("nope\n")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "c.jsonl").write_text("{}\n")
        result = _collect_jsonl_files(str(tmp_path))
        assert len(result) == 2
        assert all(r.endswith(".jsonl") for r in result)

    def test_empty_dir(self, tmp_path):
        assert _collect_jsonl_files(str(tmp_path)) == []

    def test_sorted_output(self, tmp_path):
        (tmp_path / "z.jsonl").write_text("{}\n")
        (tmp_path / "a.jsonl").write_text("{}\n")
        result = _collect_jsonl_files(str(tmp_path))
        assert result[0] < result[1]


# ---------------------------------------------------------------------------
# _collect_input_files
# ---------------------------------------------------------------------------

class TestCollectInputFiles:
    def test_file_arg(self, tmp_path):
        f = tmp_path / "test.jsonl"
        f.write_text("{}\n")
        files, err = _collect_input_files([str(f)])
        assert err is None
        assert len(files) == 1

    def test_dir_arg(self, tmp_path):
        (tmp_path / "test.jsonl").write_text("{}\n")
        files, err = _collect_input_files([str(tmp_path)])
        assert err is None
        assert len(files) == 1

    def test_empty_dir(self, tmp_path):
        files, err = _collect_input_files([str(tmp_path)])
        assert err is not None
        assert "no *.jsonl" in err

    def test_nonexistent_path(self):
        files, err = _collect_input_files(["/no/such/path"])
        assert err is not None
        assert "not found" in err

    def test_empty_args(self, tmp_path):
        files, err = _collect_input_files([])
        assert err is not None


# ---------------------------------------------------------------------------
# _load_contract / _load_and_check_schema
# ---------------------------------------------------------------------------

class TestLoadContract:
    def test_loads_real_contract(self):
        schema, err = contract_check._load_contract()
        assert err is None
        assert schema is not None
        assert "properties" in schema

    def test_missing_contract_dir(self, monkeypatch, tmp_path):
        monkeypatch.setattr(contract_check, "_contracts_dir", lambda: tmp_path)
        schema, err = contract_check._load_contract()
        assert schema is None
        assert "not found" in err

    def test_no_schema_key(self, monkeypatch, tmp_path):
        monkeypatch.setattr(contract_check, "_contracts_dir", lambda: tmp_path)
        (tmp_path / "contract.yaml").write_text("owner: test\n")
        schema, err = contract_check._load_contract()
        assert schema is None
        assert "does not declare" in err

    def test_missing_schema_file(self, monkeypatch, tmp_path):
        monkeypatch.setattr(contract_check, "_contracts_dir", lambda: tmp_path)
        (tmp_path / "contract.yaml").write_text("schema: missing.json\n")
        schema, err = contract_check._load_contract()
        assert schema is None
        assert "not found" in err

    def test_invalid_json_schema(self, monkeypatch, tmp_path):
        monkeypatch.setattr(contract_check, "_contracts_dir", lambda: tmp_path)
        (tmp_path / "contract.yaml").write_text("schema: bad.json\n")
        (tmp_path / "bad.json").write_text("{not json")
        schema, err = contract_check._load_contract()
        assert schema is None
        assert "not valid JSON" in err


class TestLoadAndCheckSchema:
    def test_success(self):
        schema, rc = _load_and_check_schema()
        assert rc == EXIT_OK
        assert schema is not None

    def test_contract_not_found(self, monkeypatch, tmp_path):
        monkeypatch.setattr(contract_check, "_contracts_dir", lambda: tmp_path)
        schema, rc = _load_and_check_schema()
        assert schema is None
        assert rc == EXIT_OPERATIONAL


# ---------------------------------------------------------------------------
# _run_validation
# ---------------------------------------------------------------------------

class TestRunValidation:
    def test_valid_files(self, tmp_path, usage_schema):
        f = tmp_path / "ok.jsonl"
        f.write_text(json.dumps(_valid_record()) + "\n")
        assert _run_validation([str(f)], usage_schema) == EXIT_OK

    def test_invalid_files(self, tmp_path, usage_schema):
        f = tmp_path / "bad.jsonl"
        f.write_text('{"bad": true}\n')
        assert _run_validation([str(f)], usage_schema) == EXIT_VALIDATION


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

class TestMain:
    def test_no_args(self):
        assert contract_check.main([]) == EXIT_OPERATIONAL

    def test_valid_fixture(self):
        fixture = str(
            Path(__file__).resolve().parent.parent / "fixtures" / "snapshot" / "alpha.jsonl"
        )
        assert contract_check.main([fixture]) == EXIT_OK

    def test_nonexistent_path(self):
        assert contract_check.main(["/no/such/file"]) == EXIT_OPERATIONAL

    def test_dir_with_fixtures(self):
        fixture_dir = str(
            Path(__file__).resolve().parent.parent / "fixtures" / "snapshot"
        )
        assert contract_check.main([fixture_dir]) == EXIT_OK

    def test_empty_dir(self, tmp_path):
        assert contract_check.main([str(tmp_path)]) == EXIT_OPERATIONAL

    def test_contract_not_found(self, monkeypatch, tmp_path):
        monkeypatch.setattr(contract_check, "_contracts_dir", lambda: tmp_path)
        f = tmp_path / "test.jsonl"
        f.write_text("{}\n")
        assert contract_check.main([str(f)]) == EXIT_OPERATIONAL
