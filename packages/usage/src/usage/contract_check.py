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

    # Read schema version from contract.yaml (stdlib, no PyYAML).
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
    """Recursively check for unsupported assertion keywords.

    Returns a list of diagnostic messages (empty if all keywords are
    implemented).
    """
    diags: list[str] = []
    allowed = _IMPLEMENTED_KEYWORDS | _META_KEYWORDS

    for key in schema:
        if key not in allowed:
            diags.append(
                f"schema uses unsupported keyword '{key}' at {path}"
            )

    # Recurse into nested property schemas.
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


def _matches_type(value: Any, type_spec: str | list[str]) -> bool:
    """Check whether *value* matches a JSON Schema type specifier."""
    if isinstance(type_spec, str):
        types = [type_spec]
    else:
        types = list(type_spec)

    for t in types:
        expected = _JSON_TYPE_MAP.get(t)
        if expected is None:
            continue
        if isinstance(expected, tuple):
            if isinstance(value, expected):
                # JSON booleans are a subtype of int in Python — reject.
                if t in ("integer", "number") and isinstance(value, bool):
                    continue
                return True
        else:
            if expected is type(None):
                if value is None:
                    return True
            elif isinstance(value, expected):
                # Reject bool masquerading as int.
                if t == "integer" and isinstance(value, bool):
                    continue
                return True
    return False


# ---------------------------------------------------------------------------
# Record validation
# ---------------------------------------------------------------------------

def _validate_record(
    record: dict[str, Any],
    schema: dict[str, Any],
    filepath: str,
    line_no: int,
) -> list[tuple[str, int, str, str, str]]:
    """Validate one parsed JSON record against the schema.

    Returns a list of (filepath, line_no, field, code, message) tuples.
    """
    diags: list[tuple[str, int, str, str, str]] = []

    # --- required ---
    required_fields: list[str] = schema.get("required", [])
    for field in required_fields:
        if field not in record:
            diags.append((
                filepath, line_no, field,
                "SCHEMA_REQUIRED",
                f"required field '{field}' is missing",
            ))

    # --- additionalProperties ---
    if schema.get("additionalProperties") is False:
        allowed_keys = set(schema.get("properties", {}).keys())
        for key in record:
            if key not in allowed_keys:
                diags.append((
                    filepath, line_no, key,
                    "SCHEMA_ADDITIONAL",
                    f"additional property '{key}' is not allowed",
                ))

    # --- properties: type + minimum ---
    prop_schemas: dict[str, dict[str, Any]] = schema.get("properties", {})
    for field, prop_schema in prop_schemas.items():
        if field not in record:
            continue  # Missing fields handled by 'required' above.

        value = record[field]

        # type
        type_spec = prop_schema.get("type")
        if type_spec is not None:
            if not _matches_type(value, type_spec):
                expected = type_spec if isinstance(type_spec, str) else " | ".join(type_spec)
                diags.append((
                    filepath, line_no, field,
                    "SCHEMA_TYPE",
                    f"expected type {expected}, got {type(value).__name__}",
                ))

        # minimum (applies only when value is an integer, not null)
        minimum = prop_schema.get("minimum")
        if minimum is not None and isinstance(value, int) and not isinstance(value, bool):
            if value < minimum:
                diags.append((
                    filepath, line_no, field,
                    "SCHEMA_MINIMUM",
                    f"value {value} is below minimum {minimum}",
                ))

        # Nested object validation (for transcript_ref).
        if (
            isinstance(value, dict)
            and isinstance(prop_schema, dict)
            and "properties" in prop_schema
        ):
            nested_diags = _validate_record(
                value, prop_schema, filepath, line_no,
            )
            # Prefix nested field names.
            for fp, ln, fld, code, msg in nested_diags:
                diags.append((fp, ln, f"{field}.{fld}", code, msg))

    # --- cross-field invariant: normalized_total ---
    ni = record.get("normalized_input")
    no = record.get("normalized_output")
    nt = record.get("normalized_total")
    if (
        isinstance(ni, int) and not isinstance(ni, bool)
        and isinstance(no, int) and not isinstance(no, bool)
        and isinstance(nt, int) and not isinstance(nt, bool)
    ):
        if nt != ni + no:
            diags.append((
                filepath, line_no, "normalized_total",
                "INVARIANT_NORMALIZED_TOTAL",
                f"normalized_total ({nt}) != normalized_input ({ni}) + normalized_output ({no})",
            ))

    return diags


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------

def _validate_file(
    filepath: str,
    schema: dict[str, Any],
) -> list[tuple[str, int, str, str, str]]:
    """Validate every line of a JSONL file.

    Returns a list of (filepath, line_no, field, code, message) tuples.
    """
    diags: list[tuple[str, int, str, str, str]] = []

    try:
        with open(filepath, encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, start=1):
                stripped = line.strip()
                if not stripped:
                    continue  # skip blank lines

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
    diags: list[tuple[str, int, str, str, str]],
) -> list[tuple[str, int, str, str, str]]:
    """Sort by filepath, line_no, field, code."""
    return sorted(diags, key=lambda d: (d[0], d[1], d[2], d[3]))


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Run the contract check gate.

    Returns an exit code: 0, 1, or 2.
    """
    args = argv if argv is not None else sys.argv[1:]

    if not args:
        print("usage: usage-contract-check <path> [<path> ...]", file=sys.stderr)
        return EXIT_OPERATIONAL

    # Load the installed contract.
    schema, err = _load_contract()
    if err:
        print(f"$:0:$: SCHEMA_PARSE: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL

    assert schema is not None

    # Check for unsupported keywords.
    unsupported = _check_unsupported_keywords(schema)
    if unsupported:
        for msg in unsupported:
            print(
                f"$:0:$: UNSUPPORTED_SCHEMA_KEYWORD: {msg}",
                file=sys.stderr,
            )
        return EXIT_OPERATIONAL

    # Collect input files.
    files: list[str] = []
    for arg in args:
        if os.path.isdir(arg):
            found = _collect_jsonl_files(arg)
            if not found:
                print(
                    f"no *.jsonl files found under {arg}",
                    file=sys.stderr,
                )
                return EXIT_OPERATIONAL
            files.extend(found)
        elif os.path.isfile(arg):
            files.append(arg)
        else:
            print(f"path not found: {arg}", file=sys.stderr)
            return EXIT_OPERATIONAL

    if not files:
        print("no input files", file=sys.stderr)
        return EXIT_OPERATIONAL

    # Validate.
    all_diags: list[tuple[str, int, str, str, str]] = []
    for filepath in files:
        all_diags.extend(_validate_file(filepath, schema))

    if not all_diags:
        return EXIT_OK

    # Print sorted diagnostics to stderr.
    for diag in _sort_diagnostics(all_diags):
        print(_format_diagnostic(*diag), file=sys.stderr)

    return EXIT_VALIDATION


if __name__ == "__main__":
    sys.exit(main())
