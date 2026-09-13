from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_IMPLEMENTED_ASSERTION_KEYWORDS: frozenset[str] = frozenset({
    "type",
    "properties",
    "required",
    "additionalProperties",
    "minimum",
})

_ANNOTATION_KEYWORDS: frozenset[str] = frozenset({
    "$schema",
    "$id",
    "title",
    "description",
    "enum",
})

_TYPE_MAP: dict[str, type | tuple[type, ...]] = {
    "object": dict,
    "array": list,
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "null": type(None),
}


def _is_type(value: Any, type_name: str) -> bool:
    expected = _TYPE_MAP.get(type_name)
    if expected is None:
        return True
    if type_name in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, expected)


def _check_unsupported_keywords(
    schema: dict[str, Any], path: str
) -> list[str]:
    errors: list[str] = []
    for key in schema:
        if key in _IMPLEMENTED_ASSERTION_KEYWORDS:
            continue
        if key in _ANNOTATION_KEYWORDS:
            continue
        errors.append(
            f"UNSUPPORTED_SCHEMA_KEYWORD: keyword '{key}' at {path} "
            f"is not implemented"
        )
    props = schema.get("properties")
    if isinstance(props, dict):
        for prop_name, prop_schema in props.items():
            if isinstance(prop_schema, dict):
                errors.extend(
                    _check_unsupported_keywords(
                        prop_schema, f"{path}.properties.{prop_name}"
                    )
                )
    return errors


def _validate_object(
    instance: Any,
    schema: dict[str, Any],
    field_prefix: str,
) -> list[tuple[str, str, str]]:
    """Validate *instance* against *schema*, returning (field, code, message) triples."""
    errors: list[tuple[str, str, str]] = []

    type_spec = schema.get("type")
    if type_spec is not None:
        if isinstance(type_spec, list):
            if not any(_is_type(instance, t) for t in type_spec):
                errors.append((
                    field_prefix or "$",
                    "SCHEMA_TYPE",
                    f"expected one of {type_spec}, got {type(instance).__name__}",
                ))
                return errors
        elif isinstance(type_spec, str):
            if not _is_type(instance, type_spec):
                errors.append((
                    field_prefix or "$",
                    "SCHEMA_TYPE",
                    f"expected {type_spec}, got {type(instance).__name__}",
                ))
                return errors

    if instance is None:
        return errors

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append((key, "SCHEMA_REQUIRED", f"missing required field '{key}'"))

        no_additional = schema.get("additionalProperties") is False
        properties = schema.get("properties", {})
        if no_additional:
            for key in instance:
                if key not in properties:
                    errors.append((key, "SCHEMA_ADDITIONAL", f"unexpected field '{key}'"))

        for prop_name, prop_schema in properties.items():
            if prop_name in instance and isinstance(prop_schema, dict):
                sub_prefix = f"{field_prefix}.{prop_name}" if field_prefix else prop_name
                errors.extend(
                    _validate_object(instance[prop_name], prop_schema, sub_prefix)
                )

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            errors.append((
                field_prefix or "$",
                "SCHEMA_MINIMUM",
                f"value {instance} is below minimum {minimum}",
            ))

    return errors


def _check_invariants(
    record: dict[str, Any],
) -> list[tuple[str, str, str]]:
    errors: list[tuple[str, str, str]] = []
    ni = record.get("normalized_input")
    no = record.get("normalized_output")
    nt = record.get("normalized_total")
    if (
        isinstance(ni, int)
        and isinstance(no, int)
        and isinstance(nt, int)
        and not isinstance(ni, bool)
        and not isinstance(no, bool)
        and not isinstance(nt, bool)
    ):
        if nt != ni + no:
            errors.append((
                "normalized_total",
                "INVARIANT_NORMALIZED_TOTAL",
                f"normalized_total ({nt}) != "
                f"normalized_input ({ni}) + normalized_output ({no})",
            ))
    return errors


class Diagnostic:
    __slots__ = ("path", "line", "field", "code", "message")

    def __init__(
        self, path: str, line: int, field: str, code: str, message: str
    ) -> None:
        self.path = path
        self.line = line
        self.field = field
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"{self.path}:{self.line}:{self.field}: {self.code}: {self.message}"

    def sort_key(self) -> tuple[str, int, str, str]:
        return (self.path, self.line, self.field, self.code)


def load_schema(contracts_dir: Path) -> dict[str, Any] | str:
    schema_path = contracts_dir / "v1.schema.json"
    if not schema_path.exists():
        return f"installed contract not found: {schema_path}"
    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return f"cannot read installed contract: {exc}"
    if not isinstance(schema, dict):
        return f"installed contract is not a JSON object: {schema_path}"
    return schema


def check_schema_support(schema: dict[str, Any]) -> list[str]:
    return _check_unsupported_keywords(schema, "$")


def validate_file(
    file_path: Path, schema: dict[str, Any]
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    path_str = str(file_path)
    try:
        with open(file_path) as f:
            lines = f.readlines()
    except OSError as exc:
        diagnostics.append(
            Diagnostic(path_str, 0, "$", "SCHEMA_PARSE", f"cannot read file: {exc}")
        )
        return diagnostics

    for line_num, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as exc:
            diagnostics.append(
                Diagnostic(path_str, line_num, "$", "SCHEMA_PARSE", str(exc))
            )
            continue

        schema_errors = _validate_object(record, schema, "")
        for field, code, message in schema_errors:
            diagnostics.append(Diagnostic(path_str, line_num, field, code, message))

        if isinstance(record, dict):
            invariant_errors = _check_invariants(record)
            for field, code, message in invariant_errors:
                diagnostics.append(
                    Diagnostic(path_str, line_num, field, code, message)
                )

    return diagnostics


def collect_jsonl_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(target.rglob("*.jsonl"))
    return []


def run(targets: list[str], contracts_dir: Path | None = None) -> int:
    if not targets:
        print("usage: usage-contract-check <file-or-directory>...", file=sys.stderr)
        return 2

    if contracts_dir is None:
        contracts_dir = Path(__file__).resolve().parent.parent.parent / "contracts"

    schema = load_schema(contracts_dir)
    if isinstance(schema, str):
        print(schema, file=sys.stderr)
        return 2

    unsupported = check_schema_support(schema)
    if unsupported:
        for msg in unsupported:
            print(msg, file=sys.stderr)
        return 2

    all_diagnostics: list[Diagnostic] = []
    files_found = False

    for target_str in targets:
        target = Path(target_str)
        if not target.exists():
            print(f"error: path does not exist: {target}", file=sys.stderr)
            return 2
        files = collect_jsonl_files(target)
        if files:
            files_found = True
        for jsonl_file in files:
            all_diagnostics.extend(validate_file(jsonl_file, schema))

    if not files_found:
        print("error: no .jsonl files found", file=sys.stderr)
        return 2

    all_diagnostics.sort(key=lambda d: d.sort_key())
    for diag in all_diagnostics:
        print(diag, file=sys.stderr)

    return 1 if all_diagnostics else 0
