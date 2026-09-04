"""Contract tests for factory/scripts/context-lint.

Covers ACX-01 through ACX-05 from docs/spec/agent-context-qa-strategy.md —
the six core CX-* finding codes introduced by ST-0190: CX-FILE, CX-PARSE,
CX-KEYS, CX-NULL, CX-MODE, CX-MODE-INVALID. CX-SRC, CX-SRC-EXIST,
CX-SRC-STALE, CX-GUIDE-REF, and CX-FORMAT are out of this story's scope
(ST-0191/ST-0192) and are not exercised here.

Each test runs the script as a subprocess with --format json, mirroring the
existing tests/factory/test_backlog_lint.py pattern for a factory script
without a .py extension.
"""

from __future__ import annotations

import json
import shutil
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


def _run_context_lint(
    context_dir: Path, *, planning_gate: bool = False
) -> tuple[list[dict], dict]:
    """Run context-lint against context_dir and return (findings, summary)."""
    args = [
        sys.executable,
        str(SCRIPT),
        "--context-dir",
        str(context_dir),
        "--format",
        "json",
    ]
    if planning_gate:
        args.append("--planning-gate")
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    payload = json.loads(result.stderr)
    return payload["findings"], payload["summary"]


def _codes(findings: list[dict]) -> set[str]:
    return {f["code"] for f in findings}


def _findings_with_code(findings: list[dict], code: str) -> list[dict]:
    return [f for f in findings if f["code"] == code]


def _copy_fixture(name: str, dest: Path) -> Path:
    """Copy a named fixture directory to dest and return dest."""
    shutil.copytree(FIXTURES / name, dest)
    return dest


# --- ACX-01: CX-FILE ------------------------------------------------------


@pytest.mark.spec("ACX-01")
def test_cx_file_reports_missing_required_file(tmp_path: Path) -> None:
    """ACX-01-CT-01: a missing required index file is reported as CX-FILE."""
    context_dir = _copy_fixture("missing_stack", tmp_path / "ctx")

    findings, _ = _run_context_lint(context_dir)

    stack_findings = [f for f in findings if f["artifact"] == "stack.yaml"]
    assert any(
        f["code"] == "CX-FILE" and f["severity"] == "error" for f in stack_findings
    )


@pytest.mark.spec("ACX-01")
def test_cx_file_does_not_require_reading_guides_when_primary(tmp_path: Path) -> None:
    """ACX-01-CT-02: reading-guides.yaml is not required while every index
    file is mode: primary."""
    context_dir = _copy_fixture("valid", tmp_path / "ctx")
    assert not (context_dir / "reading-guides.yaml").exists()

    findings, _ = _run_context_lint(context_dir)

    reading_guide_findings = _findings_with_code(findings, "CX-FILE")
    assert not any(
        f["artifact"] == "reading-guides.yaml" for f in reading_guide_findings
    )


@pytest.mark.spec("ACX-01")
def test_cx_file_requires_reading_guides_when_any_index_is_mode_index(
    tmp_path: Path,
) -> None:
    """Reading-guides.yaml becomes required once any index file transitions
    to mode: index — the converse of the primary-mode carve-out above."""
    context_dir = _copy_fixture("valid", tmp_path / "ctx")
    stack = context_dir / "stack.yaml"
    stack.write_text(
        stack.read_text(encoding="utf-8").replace("mode: primary", "mode: index", 1)
    )

    findings, _ = _run_context_lint(context_dir)

    assert any(
        f["code"] == "CX-FILE" and f["artifact"] == "reading-guides.yaml"
        for f in findings
    )


# --- ACX-02: CX-PARSE ------------------------------------------------------


@pytest.mark.spec("ACX-02")
def test_cx_parse_reports_invalid_yaml(tmp_path: Path) -> None:
    """ACX-02-CT-01: a YAML syntax error (tab indentation) is reported as
    CX-PARSE, and stops further validation of that file (no CX-KEYS/CX-MODE
    findings for stack.yaml alongside it)."""
    context_dir = _copy_fixture("invalid_yaml", tmp_path / "ctx")

    findings, _ = _run_context_lint(context_dir)

    stack_findings = [f for f in findings if f["artifact"] == "stack.yaml"]
    assert len(stack_findings) == 1
    assert stack_findings[0]["code"] == "CX-PARSE"
    assert stack_findings[0]["severity"] == "error"


# --- ACX-03: CX-KEYS --------------------------------------------------------


@pytest.mark.spec("ACX-03")
def test_cx_keys_reports_missing_required_top_level_key(tmp_path: Path) -> None:
    """ACX-03-CT-01: stack.yaml missing 'languages' is reported as CX-KEYS."""
    context_dir = _copy_fixture("missing_key", tmp_path / "ctx")

    findings, _ = _run_context_lint(context_dir)

    keys_findings = _findings_with_code(findings, "CX-KEYS")
    assert any(
        f["artifact"] == "stack.yaml" and "languages" in f["message"]
        for f in keys_findings
    )


@pytest.mark.spec("ACX-03")
def test_cx_keys_reports_deferred_coexisting_with_name_or_source(
    tmp_path: Path,
) -> None:
    """ACX-03-CT-02: 'deferred' coexisting with 'name' at the same field is
    reported as CX-KEYS, not CX-SRC or CX-NULL."""
    context_dir = _copy_fixture("deferred_conflict", tmp_path / "ctx")

    findings, _ = _run_context_lint(context_dir)

    keys_findings = _findings_with_code(findings, "CX-KEYS")
    assert any(
        f["artifact"] == "stack.yaml" and "data_stores" in f["message"]
        for f in keys_findings
    )
    # The deferred field itself must not also be flagged null.
    assert not any(
        f["code"] == "CX-NULL" and "data_stores" in f["message"] for f in findings
    )


# --- ACX-04: CX-NULL --------------------------------------------------------


@pytest.mark.spec("ACX-04")
def test_cx_null_reports_warning_in_default_mode(tmp_path: Path) -> None:
    """ACX-04-CT-01: null leaf values are warnings in default mode."""
    context_dir = _copy_fixture("valid", tmp_path / "ctx")

    findings, _ = _run_context_lint(context_dir)

    null_findings = _findings_with_code(findings, "CX-NULL")
    assert null_findings, "expected CX-NULL findings for the null-placeholder templates"
    assert all(f["severity"] == "warning" for f in null_findings)


@pytest.mark.spec("ACX-04")
def test_cx_null_reports_error_under_planning_gate(tmp_path: Path) -> None:
    """ACX-04-CT-02: the same null leaves become errors under --planning-gate."""
    context_dir = _copy_fixture("valid", tmp_path / "ctx")

    findings, _ = _run_context_lint(context_dir, planning_gate=True)

    null_findings = _findings_with_code(findings, "CX-NULL")
    assert null_findings
    assert all(f["severity"] == "error" for f in null_findings)


# --- ACX-05: CX-MODE / CX-MODE-INVALID --------------------------------------


@pytest.mark.spec("ACX-05")
def test_cx_mode_reports_info_for_valid_mode(tmp_path: Path) -> None:
    """ACX-05-CT-01: a valid mode value produces a CX-MODE info finding."""
    context_dir = _copy_fixture("valid", tmp_path / "ctx")

    findings, _ = _run_context_lint(context_dir)

    mode_findings = _findings_with_code(findings, "CX-MODE")
    assert any(
        f["artifact"] == "stack.yaml" and f["severity"] == "info" for f in mode_findings
    )


@pytest.mark.spec("ACX-05")
def test_cx_mode_invalid_reports_error_for_unrecognized_mode(tmp_path: Path) -> None:
    """ACX-05-CT-02: an unrecognized mode value produces a CX-MODE-INVALID
    error, not a silent pass and not a crash."""
    context_dir = _copy_fixture("invalid_mode", tmp_path / "ctx")

    findings, _ = _run_context_lint(context_dir)

    invalid_findings = _findings_with_code(findings, "CX-MODE-INVALID")
    assert len(invalid_findings) == 1
    assert invalid_findings[0]["artifact"] == "stack.yaml"
    assert invalid_findings[0]["severity"] == "error"
    # A rejected mode value must not also register as a valid CX-MODE info.
    assert not any(
        f["artifact"] == "stack.yaml" for f in _findings_with_code(findings, "CX-MODE")
    )


# --- Exit codes and CLI plumbing -------------------------------------------


def test_exit_code_equals_error_count(tmp_path: Path) -> None:
    """The process exit code equals the number of error-severity findings."""
    context_dir = _copy_fixture("invalid_mode", tmp_path / "ctx")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--context-dir", str(context_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    error_count = sum(
        1 for line in result.stderr.splitlines() if line.startswith("[ERROR")
    )
    assert result.returncode == error_count
    assert error_count >= 1


def test_report_only_always_exits_zero(tmp_path: Path) -> None:
    """--report-only always exits 0, even with error-severity findings."""
    context_dir = _copy_fixture("invalid_mode", tmp_path / "ctx")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--context-dir",
            str(context_dir),
            "--report-only",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0


def test_missing_context_dir_produces_no_findings(tmp_path: Path) -> None:
    """An absent agent-context directory is not an error at this layer —
    format detection (choosing YAML agent-context vs. legacy charter) is
    ST-0192's responsibility, not context-lint's default CX-* path."""
    context_dir = tmp_path / "does-not-exist"

    findings, summary = _run_context_lint(context_dir)

    assert findings == []
    assert summary == {"error": 0, "warning": 0, "info": 0}


def test_legacy_charter_dir_flag_preserves_ch_star_behavior(tmp_path: Path) -> None:
    """--charter-dir still runs the preserved CH-* legacy path (ST-0192 will
    wire format detection on top of this; for now it must remain callable)."""
    charter_dir = tmp_path / "charter"
    charter_dir.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--charter-dir",
            str(charter_dir),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(result.stderr)
    codes = _codes(payload["findings"])
    assert codes and all(code.startswith("CH-") for code in codes)
