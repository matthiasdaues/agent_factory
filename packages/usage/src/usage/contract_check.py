"""Validate JSONL records against the usage-record contract.

Implements a subset of JSON Schema Draft 2020-12 assertion keywords:
  type, properties, required, additionalProperties, minimum

Fails closed with UNSUPPORTED_SCHEMA_KEYWORD (exit 2) on any
unimplemented keyword.

Cross-field invariant:
  normalized_total == normalized_input + normalized_output

Exit codes:
  0 — all records valid
  1 — at least one validation failure
  2 — operational error
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXIT_OK = 0
EXIT_VALIDATION = 1
EXIT_OPERATIONAL = 2

Diag = tuple[str, int, str, str, str]

# Assertion keywords this validator implements.
_IMPLEMENTED_KEYWORDS: frozenset[str] = frozenset({
    "type",
    "properties",
    "required",
    "additionalProperties",
    "minimum",
})

# Non-assertion keywords that are always allowed in a schema object.
_META_KEYWORDS: frozenset[str] = frozenset({
    "$schema",
    "title",
    "description",
})


# ---------------------------------------------------------------------------
# Schema loading
# ---------------------------------------------------------------------------

def _contracts_dir() -> Path:
    """Return the installed contracts directory next to this package."""
    return Path(__file__).resolve().parent.parent.parent / "contracts"


def _load_contract() -> tuple[dict[str, Any] | None, str | None]:
    """Load contract.yaml and v1.schema.json.

    Returns (schema_dict, error_message).  On success error_message is None.
    """
    contracts = _contracts_dir()
    contract_path = contracts / "contract.yaml"
    if not contract_path.exists():
        return None, f"contract.yaml not found at {contract_path}"

    schema_file: str | None = None
    with open(contract_path, encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.startswith("schema:"):
                schema_file = stripped.split(":", 1)[1].strip()
                break

    if not schema_file:
        return None, "contract.yaml does not declare a schema file"

    schema_path = contracts / schema_file
    if not schema_path.exists():
        return None, f"schema file {schema_file} not found at {schema_path}"

    try:
        with open(schema_path, encoding="utf-8") as fh:
            schema = json.load(fh)
    except json.JSONDecodeError as exc:
        return None, f"schema file {schema_file} is not valid JSON: {exc}"

    return schema, None


# ---------------------------------------------------------------------------
# Schema keyword checking
# ---------------------------------------------------------------------------

def _check_unsupported_keywords(
    schema: dict[str, Any],
    path: str = "<root>",
) -> list[str]:
    """Recursively check for unsupported assertion keywords."""
    diags: list[str] = []
    allowed = _IMPLEMENTED_KEYWORDS | _META_KEYWORDS

    for key in schema:
        if key not in allowed:
            diags.append(
                f"schema uses unsupported keyword '{key}' at {path}"
            )

    props = schema.get("properties")
    if isinstance(props, dict):
        for prop_name, prop_schema in props.items():
            if isinstance(prop_schema, dict):
                diags.extend(
                    _check_unsupported_keywords(
                        prop_schema, f"{path}.properties.{prop_name}"
                    )
                )

    return diags


# ---------------------------------------------------------------------------
# Type checking helpers
# ---------------------------------------------------------------------------

_JSON_TYPE_MAP: dict[str, type | None] = {
    "string": str,
    "integer": int,
    "number": (int, float),  # type: ignore[assignment]
    "boolean": bool,
    "object": dict,
    "array": list,
    "null": type(None),
}


def _check_single_type(value: Any, type_name: str) -> bool:
    """Check whether *value* matches one JSON Schema type name."""
    expected = _JSON_TYPE_MAP.get(type_name)
    if expected is None:
        return False
    if isinstance(value, bool) and type_name in ("integer", "number"):
        return False
    if expected is type(None):
        return value is None
    return isinstance(value, expected)


def _matches_type(value: Any, type_spec: str | list[str]) -> bool:
    """Check whether *value* matches a JSON Schema type specifier."""
    types = [type_spec] if isinstance(type_spec, str) else type_spec
    return any(_check_single_type(value, t) for t in types)


# ---------------------------------------------------------------------------
# Record validation — split into focused checkers
# ---------------------------------------------------------------------------

def _check_required(
    record: dict[str, Any],
    schema: dict[str, Any],
    filepath: str,
    line_no: int,
) -> list[Diag]:
    """Check that all required fields are present."""
    diags: list[Diag] = []
    for field in schema.get("required", []):
        if field not in record:
            diags.append((
                filepath, line_no, field,
                "SCHEMA_REQUIRED",
                f"required field '{field}' is missing",
            ))
    return diags


def _check_additional(
    record: dict[str, Any],
    schema: dict[str, Any],
    filepath: str,
    line_no: int,
) -> list[Diag]:
    """Check for disallowed additional properties."""
    if schema.get("additionalProperties") is not False:
        return []
    allowed_keys = set(schema.get("properties", {}).keys())
    diags: list[Diag] = []
    for key in record:
        if key not in allowed_keys:
            diags.append((
                filepath, line_no, key,
                "SCHEMA_ADDITIONAL",
                f"additional property '{key}' is not allowed",
            ))
    return diags


def _check_type(
    field: str,
    value: Any,
    prop_schema: dict[str, Any],
    filepath: str,
    line_no: int,
) -> Diag | None:
    """Return a diagnostic if *value* doesn't match the declared type."""
    type_spec = prop_schema.get("type")
    if type_spec is None or _matches_type(value, type_spec):
        return None
    expected = type_spec if isinstance(type_spec, str) else " | ".join(type_spec)
    return (
        filepath, line_no, field,
        "SCHEMA_TYPE",
        f"expected type {expected}, got {type(value).__name__}",
    )


def _check_minimum(
    field: str,
    value: Any,
    prop_schema: dict[str, Any],
    filepath: str,
    line_no: int,
) -> Diag | None:
    """Return a diagnostic if *value* violates a minimum constraint."""
    minimum = prop_schema.get("minimum")
    if minimum is None or not _is_non_bool_int(value) or value >= minimum:
        return None
    return (
        filepath, line_no, field,
        "SCHEMA_MINIMUM",
        f"value {value} is below minimum {minimum}",
    )


def _check_nested(
    field: str,
    value: Any,
    prop_schema: dict[str, Any],
    filepath: str,
    line_no: int,
) -> list[Diag]:
    """Recursively validate nested object properties."""
    if not isinstance(value, dict) or "properties" not in prop_schema:
        return []
    return [
        (fp, ln, f"{field}.{fld}", code, msg)
        for fp, ln, fld, code, msg
        in _validate_record(value, prop_schema, filepath, line_no)
    ]


def _check_properties(
    record: dict[str, Any],
    schema: dict[str, Any],
    filepath: str,
    line_no: int,
) -> list[Diag]:
    """Check type, minimum, and nested objects for all properties."""
    diags: list[Diag] = []
    for field, prop_schema in schema.get("properties", {}).items():
        if field not in record:
            continue
        value = record[field]
        type_diag = _check_type(field, value, prop_schema, filepath, line_no)
        if type_diag:
            diags.append(type_diag)
        min_diag = _check_minimum(field, value, prop_schema, filepath, line_no)
        if min_diag:
            diags.append(min_diag)
        diags.extend(_check_nested(field, value, prop_schema, filepath, line_no))
    return diags


def _is_non_bool_int(value: Any) -> bool:
    """Return True if *value* is an int but not a bool."""
    return isinstance(value, int) and not isinstance(value, bool)


def _check_normalized_invariant(
    record: dict[str, Any],
    filepath: str,
    line_no: int,
) -> list[Diag]:
    """Check that normalized_total == normalized_input + normalized_output."""
    ni = record.get("normalized_input")
    no = record.get("normalized_output")
    nt = record.get("normalized_total")
    if not (_is_non_bool_int(ni) and _is_non_bool_int(no) and _is_non_bool_int(nt)):
        return []
    if nt != ni + no:
        return [(
            filepath, line_no, "normalized_total",
            "INVARIANT_NORMALIZED_TOTAL",
            f"normalized_total ({nt}) != normalized_input ({ni}) + normalized_output ({no})",
        )]
    return []


def _validate_record(
    record: dict[str, Any],
    schema: dict[str, Any],
    filepath: str,
    line_no: int,
) -> list[Diag]:
    """Validate one parsed JSON record against the schema."""
    diags: list[Diag] = []
    diags.extend(_check_required(record, schema, filepath, line_no))
    diags.extend(_check_additional(record, schema, filepath, line_no))
    diags.extend(_check_properties(record, schema, filepath, line_no))
    diags.extend(_check_normalized_invariant(record, filepath, line_no))
    return diags


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------

def _validate_file(
    filepath: str,
    schema: dict[str, Any],
) -> list[Diag]:
    """Validate every line of a JSONL file."""
    diags: list[Diag] = []

    try:
        with open(filepath, encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, start=1):
                stripped = line.strip()
                if not stripped:
                    continue

                try:
                    record = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    diags.append((
                        filepath, line_no, "$",
                        "SCHEMA_PARSE",
                        f"invalid JSON: {exc}",
                    ))
                    continue

                if not isinstance(record, dict):
                    diags.append((
                        filepath, line_no, "$",
                        "SCHEMA_TYPE",
                        f"expected object, got {type(record).__name__}",
                    ))
                    continue

                diags.extend(
                    _validate_record(record, schema, filepath, line_no)
                )
    except OSError as exc:
        diags.append((
            filepath, 0, "$",
            "SCHEMA_PARSE",
            f"cannot read file: {exc}",
        ))

    return diags


# ---------------------------------------------------------------------------
# Directory collection
# ---------------------------------------------------------------------------

def _collect_jsonl_files(path: str) -> list[str]:
    """Recursively collect *.jsonl files under *path*, sorted."""
    result: list[str] = []
    for dirpath, _dirnames, filenames in os.walk(path):
        for fname in filenames:
            if fname.endswith(".jsonl"):
                result.append(os.path.join(dirpath, fname))
    result.sort()
    return result


# ---------------------------------------------------------------------------
# Diagnostic formatting
# ---------------------------------------------------------------------------

def _format_diagnostic(
    filepath: str,
    line_no: int,
    field: str,
    code: str,
    message: str,
) -> str:
    return f"{filepath}:{line_no}:{field}: {code}: {message}"


def _sort_diagnostics(
    diags: list[Diag],
) -> list[Diag]:
    """Sort by filepath, line_no, field, code."""
    return sorted(diags, key=lambda d: (d[0], d[1], d[2], d[3]))


# ---------------------------------------------------------------------------
# Input file collection
# ---------------------------------------------------------------------------

def _collect_input_files(args: list[str]) -> tuple[list[str], str | None]:
    """Resolve CLI arguments to a list of JSONL files.

    Returns (files, error_message).  On success error_message is None.
    """
    files: list[str] = []
    for arg in args:
        if os.path.isdir(arg):
            found = _collect_jsonl_files(arg)
            if not found:
                return [], f"no *.jsonl files found under {arg}"
            files.extend(found)
        elif os.path.isfile(arg):
            files.append(arg)
        else:
            return [], f"path not found: {arg}"

    if not files:
        return [], "no input files"
    return files, None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def _load_and_check_schema() -> tuple[dict[str, Any] | None, int]:
    """Load the schema and check for unsupported keywords.

    Returns (schema, exit_code).  exit_code is EXIT_OK on success.
    """
    schema, err = _load_contract()
    if err:
        print(f"$:0:$: SCHEMA_PARSE: {err}", file=sys.stderr)
        return None, EXIT_OPERATIONAL

    assert schema is not None

    unsupported = _check_unsupported_keywords(schema)
    if unsupported:
        for msg in unsupported:
            print(f"$:0:$: UNSUPPORTED_SCHEMA_KEYWORD: {msg}", file=sys.stderr)
        return None, EXIT_OPERATIONAL

    return schema, EXIT_OK


def _run_validation(files: list[str], schema: dict[str, Any]) -> int:
    """Validate *files* and print diagnostics. Returns exit code."""
    all_diags: list[Diag] = []
    for filepath in files:
        all_diags.extend(_validate_file(filepath, schema))

    if not all_diags:
        return EXIT_OK

    for diag in _sort_diagnostics(all_diags):
        print(_format_diagnostic(*diag), file=sys.stderr)

    return EXIT_VALIDATION


def main(argv: list[str] | None = None) -> int:
    """Run the contract check gate.

    Returns an exit code: 0, 1, or 2.
    """
    args = argv if argv is not None else sys.argv[1:]

    if not args:
        print("usage: usage-contract-check <path> [<path> ...]", file=sys.stderr)
        return EXIT_OPERATIONAL

    schema, rc = _load_and_check_schema()
    if schema is None:
        return rc

    files, collect_err = _collect_input_files(args)
    if collect_err:
        print(collect_err, file=sys.stderr)
        return EXIT_OPERATIONAL

    return _run_validation(files, schema)


if __name__ == "__main__":
    sys.exit(main())
