"""Integration tests for the testing.yaml resolution chain in
factory/scripts/context-lint.

testing.yaml resolves at docs/testing.yaml — a single canonical path,
independent of the main format-detection chain. Resolution is observed
indirectly through CX-PARSE: each fixture's docs/testing.yaml can
contain deliberately invalid YAML (tab indentation), so a CX-PARSE
finding for artifact 'testing.yaml' proves that path was actually read.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent.parent
    / "factory"
    / "scripts"
    / "context-lint"
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "agent-context"


def _run(root: Path) -> tuple[list[dict], dict]:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(root),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stderr)
    return payload["findings"], payload["summary"]


def _testing_yaml_findings(findings: list[dict]) -> list[dict]:
    return [f for f in findings if f["artifact"] == "testing.yaml"]


def test_testing_yaml_at_docs_is_parsed() -> None:
    """docs/testing.yaml with invalid YAML surfaces as CX-PARSE,
    proving the canonical path is resolved."""
    root = FIXTURES / "testing_yaml_canonical"

    findings, _ = _run(root)

    testing_findings = _testing_yaml_findings(findings)
    assert any(f["code"] == "CX-PARSE" for f in testing_findings), findings
    assert not any(f["code"] == "CX-FORMAT" for f in findings), findings


def test_testing_yaml_valid_no_parse_error() -> None:
    """docs/testing.yaml with valid YAML produces no CX-PARSE finding."""
    root = FIXTURES / "testing_yaml_parse_only"

    findings, _ = _run(root)

    testing_findings = _testing_yaml_findings(findings)
    assert not any(f["code"] == "CX-PARSE" for f in testing_findings), findings
