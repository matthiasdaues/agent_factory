"""Integration tests for the testing.yaml carve-out's independent
resolution chain in factory/scripts/context-lint.

Covers ACX-14 from docs/spec/agent-context-qa-strategy.md: testing.yaml
resolves via its own two-step chain (docs/agent-context/testing.yaml first,
docs/charter/testing.yaml as fallback), independent of the main
format-detection chain (agent-context.feature Rule: testing.yaml operates
as a lifecycle-exempt peer file).

Resolution is observed indirectly through CX-PARSE: each fixture's
docs/charter/testing.yaml is deliberately invalid YAML (tab indentation),
so a CX-PARSE finding for artifact 'testing.yaml' proves that path was the
one actually read.
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


def test_testing_yaml_resolution_walks_both_paths() -> None:
    """ACX-14-IT-01: docs/agent-context/ exists but testing.yaml is only at
    docs/charter/testing.yaml -- the charter path is used as fallback (its
    invalid YAML surfaces as CX-PARSE), and no CX-FORMAT error is raised for
    the split location."""
    root = FIXTURES / "testing_yaml_charter_fallback"

    findings, _ = _run(root)

    testing_findings = _testing_yaml_findings(findings)
    assert any(f["code"] == "CX-PARSE" for f in testing_findings), findings
    assert not any(f["code"] == "CX-FORMAT" for f in findings), findings


def test_testing_yaml_at_new_path_takes_precedence() -> None:
    """ACX-14-IT-02: testing.yaml exists at both
    docs/agent-context/testing.yaml (valid) and docs/charter/testing.yaml
    (invalid) -- the new agent-context path takes precedence, so no
    CX-PARSE finding is reported for testing.yaml."""
    root = FIXTURES / "testing_yaml_precedence"

    findings, _ = _run(root)

    testing_findings = _testing_yaml_findings(findings)
    assert not any(f["code"] == "CX-PARSE" for f in testing_findings), findings
