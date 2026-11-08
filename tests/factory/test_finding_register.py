"""Checks of the five register schemas (ST-0387).

Each register file under docs/findings/register/<class>/ is one JSON object.
The schema finding-register-<class>.schema.json describes it, and
schema-validate runs it. These tests read the schemas, then run
schema-validate on register files built here.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import REPO_ROOT

FACTORY = REPO_ROOT / "packages" / "factory"
SCHEMAS = FACTORY / "rulebooks" / "schemas"
SCHEMA_VALIDATE = FACTORY / "scripts" / "schema-validate"
BASIS_SCHEMA = REPO_ROOT / "docs" / "spec" / "schemas" / "finding-basis.json"

# The first thirteen keys of the register-file contract in interface-contracts.md.
REQUIRED_KEYS = [
    "id",
    "source",
    "review_class",
    "category",
    "type",
    "severity",
    "artifact",
    "story",
    "finding",
    "basis",
    "why_this_severity",
    "commit",
    "status",
]
# The keywords that the validator of schema-validate checks, plus annotations.
SUPPORTED_KEYWORDS = {
    "$schema",
    "title",
    "description",
    "const",
    "enum",
    "type",
    "pattern",
    "format",
    "minimum",
    "required",
    "properties",
    "additionalProperties",
    "minItems",
    "items",
}

TREE_BASIS = {
    "in_use": True,
    "harms_downstream": False,
    "fails_purpose": False,
    "raises_cost": True,
}
BAR_BASIS = {
    "effect": "leak",
    "second_breach": False,
    "trusted_access": True,
    "non_default": False,
    "user_action": False,
    "confidence": "proven",
    "in_use": True,
}
MATRIX_BASIS = {"importance": "medium", "exposure": "uncertain", "in_use": False}
BASIS_OF_CLASS = {
    "document": TREE_BASIS,
    "code": TREE_BASIS,
    "runtime": TREE_BASIS,
    "security": BAR_BASIS,
    "architecture": MATRIX_BASIS,
}
# Index of the matching shape in the oneOf list of finding-basis.json.
SHAPE_INDEX = {"document": 0, "code": 0, "runtime": 0, "security": 1, "architecture": 2}
CLASSES = tuple(BASIS_OF_CLASS)
OTHER_CLASS = {
    "document": "security",
    "code": "architecture",
    "runtime": "security",
    "security": "code",
    "architecture": "document",
}


def _schema(class_name: str) -> dict:
    path = SCHEMAS / f"finding-register-{class_name}.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _register_file(class_name: str, **overrides) -> dict:
    data = {
        "id": "FAGAN-0050",
        "source": "fagan-review",
        "review_class": class_name,
        "category": "defect",
        "type": "function",
        "severity": "minor",
        "artifact": "packages/factory/scripts/dispatch:120",
        "story": "ST-0370",
        "finding": "What is wrong, and the fix.",
        "basis": dict(BASIS_OF_CLASS[class_name]),
        "why_this_severity": "The artifact works (no to fails_purpose).",
        "commit": "d0a78a5c40327c1f7e4c9a204ab5e766a7e0c44b",
        "status": "open",
    }
    data.update(overrides)
    return data


def _validate(
    tmp_path: Path, class_name: str, data: dict
) -> subprocess.CompletedProcess:
    target = tmp_path / "register-file.json"
    target.write_text(json.dumps(data), encoding="utf-8")
    schema = SCHEMAS / f"finding-register-{class_name}.schema.json"
    return subprocess.run(
        [sys.executable, str(SCHEMA_VALIDATE), str(target), str(schema)],
        capture_output=True,
        text=True,
        check=False,
    )


def _keywords(node) -> set[str]:
    """Collect every schema keyword used under a schema node."""
    found: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            found.add(key)
            if key == "properties":
                for sub in value.values():
                    found |= _keywords(sub)
            elif key in ("additionalProperties", "items"):
                found |= _keywords(value)
    return found


@pytest.mark.spec("FC-07-LN-02")
@pytest.mark.parametrize("class_name", CLASSES)
def test_st_0387_schema_requires_the_first_thirteen_keys(class_name):
    schema = _schema(class_name)
    assert schema["required"] == REQUIRED_KEYS
    assert "status" in schema["required"]
    assert schema["additionalProperties"] is False
    assert schema["properties"]["status"]["enum"] == ["open", "resolved", "waived"]
    for key in ("override_by", "override_reason"):
        assert schema["properties"][key]["type"] == "string"
        assert key not in schema["required"]
    assert schema["properties"]["review_class"]["const"] == class_name
    assert schema["properties"]["severity"]["const"] == "minor"


@pytest.mark.spec("FC-07-LN-02")
@pytest.mark.parametrize("class_name", CLASSES)
def test_st_0387_schema_basis_takes_the_shape_of_its_class(class_name):
    shape = json.loads(BASIS_SCHEMA.read_text(encoding="utf-8"))["oneOf"][
        SHAPE_INDEX[class_name]
    ]
    basis = _schema(class_name)["properties"]["basis"]
    assert basis["required"] == shape["required"]
    assert basis["additionalProperties"] is False
    assert basis["properties"] == shape["properties"]


@pytest.mark.spec("FC-07-LN-02")
@pytest.mark.parametrize("class_name", CLASSES)
def test_st_0387_schema_uses_only_keywords_that_schema_validate_supports(class_name):
    keywords = _keywords(_schema(class_name))
    assert "oneOf" not in keywords
    assert keywords <= SUPPORTED_KEYWORDS, keywords - SUPPORTED_KEYWORDS


@pytest.mark.spec("FC-07-LN-02")
@pytest.mark.parametrize("class_name", CLASSES)
def test_st_0387_schema_validate_accepts_a_register_file_of_the_class(
    tmp_path, class_name
):
    result = _validate(tmp_path, class_name, _register_file(class_name))
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.spec("FC-07-LN-02")
@pytest.mark.parametrize("status", ["open", "resolved", "waived"])
def test_st_0387_schema_validate_accepts_each_status_and_both_override_keys(
    tmp_path, status
):
    data = _register_file(
        "code", status=status, override_by="human", override_reason="Accepted as is."
    )
    result = _validate(tmp_path, "code", data)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.spec("FC-07-LN-02")
@pytest.mark.parametrize("class_name", CLASSES)
def test_st_0387_schema_validate_rejects_the_basis_of_another_class(
    tmp_path, class_name
):
    other = OTHER_CLASS[class_name]
    data = _register_file(class_name, basis=dict(BASIS_OF_CLASS[other]))
    result = _validate(tmp_path, class_name, data)
    assert result.returncode == 1
    assert "$.basis" in result.stdout


@pytest.mark.spec("FC-07-LN-02")
@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ({"status": "deferred"}, "$.status"),
        ({"severity": "major"}, "$.severity"),
        ({"review_class": "document"}, "$.review_class"),
        ({"commit": "abc123"}, "$.commit"),
        ({"extra": "key"}, "additional property 'extra'"),
    ],
    ids=[
        "deferred",
        "severity",
        "class-of-another-folder",
        "short-commit",
        "extra-key",
    ],
)
def test_st_0387_schema_validate_rejects_a_broken_register_file(
    tmp_path, change, expected
):
    result = _validate(tmp_path, "code", _register_file("code", **change))
    assert result.returncode == 1
    assert expected in result.stdout


@pytest.mark.spec("FC-07-LN-02")
def test_st_0387_schema_validate_rejects_a_register_file_without_a_required_key(
    tmp_path,
):
    data = _register_file("code")
    del data["story"]
    result = _validate(tmp_path, "code", data)
    assert result.returncode == 1
    assert "missing required field 'story'" in result.stdout


@pytest.mark.spec("FC-07-LN-02")
def test_st_0387_schema_validate_accepts_a_null_story(tmp_path):
    result = _validate(tmp_path, "code", _register_file("code", story=None))
    assert result.returncode == 0, result.stdout + result.stderr


# --- finding-lint runs schema-validate on each register file (ST-0391) --------

FINDING_LINT = FACTORY / "scripts" / "finding-lint"
# A register basis per class whose severity is minor, so finding-lint passes it.
MINOR_BASIS = {
    "document": TREE_BASIS,
    "code": TREE_BASIS,
    "runtime": TREE_BASIS,
    "security": BAR_BASIS,
    "architecture": MATRIX_BASIS,
}
TYPE_OF_CLASS = {
    "document": "incomplete",
    "code": "function",
    "runtime": "crash",
    "security": "A06",
    "architecture": "risk",
}


def _lint_register(
    tmp_path: Path, class_name: str, data: dict
) -> subprocess.CompletedProcess:
    target = (
        tmp_path / "docs" / "findings" / "register" / class_name / "FAGAN-0050.json"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(FINDING_LINT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )


def _lint_ready(class_name: str, **overrides) -> dict:
    data = _register_file(
        class_name, type=TYPE_OF_CLASS[class_name], basis=dict(MINOR_BASIS[class_name])
    )
    if class_name == "architecture":
        data["category"] = "risk"
    data.update(overrides)
    return data


@pytest.mark.spec("FC-07-IT-01")
@pytest.mark.parametrize("class_name", CLASSES)
@pytest.mark.parametrize("status", ["open", "resolved", "waived"])
def test_st_0391_finding_lint_accepts_a_valid_register_file(
    tmp_path, class_name, status
):
    data = _lint_ready(
        class_name,
        status=status,
        override_by="human",
        override_reason="Accepted as is.",
    )
    result = _lint_register(tmp_path, class_name, data)
    assert (result.returncode, result.stdout) == (0, "")


@pytest.mark.spec("FC-07-IT-01")
@pytest.mark.parametrize("class_name", CLASSES)
def test_st_0391_finding_lint_rejects_the_basis_of_another_class(tmp_path, class_name):
    data = _lint_ready(class_name, basis=dict(BASIS_OF_CLASS[OTHER_CLASS[class_name]]))
    result = _lint_register(tmp_path, class_name, data)
    assert result.returncode == 1
    assert (
        f"docs/findings/register/{class_name}/FAGAN-0050.json: BR-090 schema-validate: $.basis"
        in result.stdout
    )


@pytest.mark.spec("FC-07-IT-01")
@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ({"status": "deferred"}, "$.status"),
        ({"status": None}, "missing required field 'status'"),
        ({"story": None}, "missing required field 'story'"),
        ({"extra": "key"}, "additional property 'extra'"),
    ],
    ids=["deferred", "no-status", "missing-key", "extra-key"],
)
def test_st_0391_finding_lint_rejects_a_register_file_that_fails_its_schema(
    tmp_path, change, expected
):
    data = _lint_ready("code")
    for key, value in change.items():
        if value is None:
            del data[key]
        else:
            data[key] = value
    result = _lint_register(tmp_path, "code", data)
    assert result.returncode == 1
    lines = [line for line in result.stdout.splitlines() if expected in line]
    assert lines, result.stdout
    assert lines[0].startswith(
        "docs/findings/register/code/FAGAN-0050.json: BR-090 schema-validate: "
    )
    assert "finding-register-code.schema.json" in lines[0]
