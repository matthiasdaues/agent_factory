"""Integration test for the legacy markdown charter fallback path in
factory/scripts/context-lint.

Covers ACX-12 from docs/spec/agent-context-qa-strategy.md: a project with no
docs/agent-context/ directory, only docs/charter/*.md, gets validated with
the existing CH-* finding codes when context-lint runs with no explicit
--context-dir or --charter-dir override -- format detection dispatches to
the legacy path automatically, and no migration is forced.
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

REAL_TEMPLATE_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "factory"
    / "rulebooks"
    / "templates"
)


def test_legacy_markdown_charter_passes_context_lint() -> None:
    """ACX-12-IT-01: docs/charter/ contains the three markdown charter files
    (tech-stack.md, development.md, house-rules.md), each populated from the
    real templates -- context-lint, run bare (root-driven format detection,
    no --context-dir/--charter-dir), applies CH-* validation and reports no
    errors, and no CX-* agent-context finding appears (agent-context.feature
    Rule: Legacy projects continue working without migration, Scenario:
    Legacy markdown charter passes context-lint)."""
    root = FIXTURES / "legacy_charter_project"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(root),
            "--template-dir",
            str(REAL_TEMPLATE_DIR),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(result.stderr)
    findings = payload["findings"]
    codes = {f["code"] for f in findings}

    # Every finding, if any, is a CH-* code -- no CX-* code leaks in, and no
    # migration is forced by mixing in agent-context validation.
    assert all(code.startswith("CH-") for code in codes), codes
    assert payload["summary"]["error"] == 0, findings
    assert result.returncode == 0
