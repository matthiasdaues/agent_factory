"""Contract tests for the format-detection chain in factory/scripts/context-lint.

Covers ACX-11 from docs/spec/agent-context-qa-strategy.md: the three-step
chain that resolves whether a project uses the YAML agent-context format,
a legacy YAML charter, or a legacy markdown charter, relative to a project
root -- and reports CX-FORMAT when files exist at more than one of the
three chain locations.

Each test runs context-lint as a subprocess with --print-format and --root,
mirroring the subprocess pattern used by tests/factory/test_context_lint.py
for a factory script without a .py extension. --print-format exercises
detect_format() in isolation from the downstream CX-*/CH-* validators, so
these tests assert the chain's own resolution logic, not what it dispatches
to afterward (that dispatch is covered by test_context_lint_legacy.py and
the CX-FORMAT scenarios in test_context_lint.py).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent.parent
    / "factory"
    / "scripts"
    / "context-lint"
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "agent-context"


def _detected_format(root: Path) -> str:
    """Run context-lint --print-format against root and return the printed
    mode, stripped of the trailing newline."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--print-format", "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


@pytest.mark.spec("ACX-11")
def test_format_detection_selects_yaml_agent_context_mode() -> None:
    """ACX-11-CT-01: docs/agent-context/stack.yaml exists -> agent-context
    mode is selected (agent-context.feature Rule: Factory consumers resolve
    context file paths via format detection, Scenario: Format detection
    selects YAML agent-context mode)."""
    root = FIXTURES / "format_agent_context"

    assert _detected_format(root) == "agent-context"


@pytest.mark.spec("ACX-11")
def test_format_detection_falls_back_to_legacy_yaml_charter() -> None:
    """ACX-11-CT-02: docs/agent-context/stack.yaml does not exist and
    docs/charter/tech-stack.yaml exists -> legacy-yaml mode is selected."""
    root = FIXTURES / "format_legacy_yaml"

    assert _detected_format(root) == "legacy-yaml"


@pytest.mark.spec("ACX-11")
def test_format_detection_falls_back_to_legacy_markdown_charter() -> None:
    """ACX-11-CT-03: neither YAML location exists and
    docs/charter/tech-stack.md exists -> legacy-markdown mode is selected."""
    root = FIXTURES / "format_legacy_markdown"

    assert _detected_format(root) == "legacy-markdown"


@pytest.mark.spec("ACX-11")
def test_format_detection_reports_error_on_mixed_locations() -> None:
    """ACX-11-CT-04: docs/agent-context/stack.yaml and
    docs/charter/tech-stack.md both exist -> a CX-FORMAT error is reported.

    --print-format only prints the resolved mode (still the first chain
    match, per detect_format's contract), so the CX-FORMAT finding itself
    is asserted through the normal validation run instead.
    """
    root = FIXTURES / "format_mixed"

    assert _detected_format(root) == "agent-context"

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
    import json

    payload = json.loads(result.stderr)
    codes = {f["code"] for f in payload["findings"]}
    assert "CX-FORMAT" in codes


def test_format_detection_selects_none_when_no_location_exists() -> None:
    """Implementation-robustness case, not part of ACX-11: an empty project
    (no chain location present) must resolve cleanly to 'none' rather than
    crashing -- main() dispatches this to an empty findings list."""
    root = FIXTURES / "format_none"

    assert _detected_format(root) == "none"
