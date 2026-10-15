"""Regression tests for context-lint and test-design-verify (ST-0300).

BUG-0062: context-lint judged docs/testing.yaml wrong in both directions.
BUG-0063: test-design-verify rejected a `tests:` block list as empty.

Both scripts run as subprocesses, as in test_context_lint.py.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent.parent / "packages" / "factory" / "scripts"
CONTEXT_LINT = SCRIPTS / "context-lint"


# --- BUG-0062: context-lint parses testing.yaml as YAML ---------------------


def _testing_yaml_findings(tmp_path: Path, text: str) -> list[dict]:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "testing.yaml").write_text(text, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(CONTEXT_LINT), "--root", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stderr)
    return [f for f in payload["findings"] if f["artifact"] == "testing.yaml"]


def test_bug_0062_valid_block_scalar_passes(tmp_path: Path) -> None:
    text = (
        "suites:\n"
        "  unit:\n"
        "    root: tests\n"
        "    run_all: |\n"
        "      uv run pytest\n"
        "      --quiet\n"
    )

    assert _testing_yaml_findings(tmp_path, text) == []


def test_bug_0062_unclosed_quote_and_bracket_fails(tmp_path: Path) -> None:
    text = (
        "suites:\n"
        "  unit:\n"
        '    root: "tests\n'
        "    markers: [spec, contract\n"
    )

    findings = _testing_yaml_findings(tmp_path, text)

    assert [f["code"] for f in findings] == ["CX-PARSE"]
