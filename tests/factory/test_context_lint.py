"""Contract tests for factory/scripts/context-lint.

Covers ACX-01 through ACX-10 and ACX-13 from
docs/spec/agent-context-qa-strategy.md. ACX-01 through ACX-05 are the six
core CX-* finding codes introduced by ST-0190: CX-FILE, CX-PARSE, CX-KEYS,
CX-NULL, CX-MODE, CX-MODE-INVALID. ACX-06 through ACX-09 are the four codes
ST-0191 added: CX-SRC, CX-SRC-EXIST, CX-SRC-STALE, CX-GUIDE-REF. ACX-10
(CX-FORMAT) and ACX-13 (testing.yaml's CX-PARSE-only carve-out) are ST-0192
additions; ACX-11 (the format-detection chain itself) and ACX-12/ACX-14
(the legacy-charter and testing.yaml-resolution integration scenarios) live
in their own files -- test_format_detection.py,
test_context_lint_legacy.py, and test_testing_yaml_resolution.py.

Each test runs the script as a subprocess with --format json, mirroring the
existing tests/factory/test_backlog_lint.py pattern for a factory script
without a .py extension.
"""

from __future__ import annotations

import json
import os
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
    context_dir: Path, *, planning_gate: bool = False, cwd: Path | None = None
) -> tuple[list[dict], dict]:
    """Run context-lint against context_dir and return (findings, summary).

    cwd, when given, is the directory the process runs from — source:
    pointers resolve relative to it, mirroring how a real invocation from
    the project root resolves a pointer like 'docs/adr/004.md'.
    """
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
    result = subprocess.run(args, capture_output=True, text=True, check=False, cwd=cwd)
    payload = json.loads(result.stderr)
    return payload["findings"], payload["summary"]


def _codes(findings: list[dict]) -> set[str]:
    return {f["code"] for f in findings}


def _findings_with_code(findings: list[dict], code: str) -> list[dict]:
    return [f for f in findings if f["code"] == code]


def _copy_fixture(name: str, dest: Path) -> Path:
    """Copy a named fixture directory (a relative path under FIXTURES, which
    may include subdirectories, e.g. 'guide_ref/docs/agent-context') to dest
    and return dest."""
    shutil.copytree(FIXTURES / name, dest)
    return dest


#: Alias used at CX-SRC* call sites: these fixtures are 'project root'
#: layouts (docs/agent-context/ plus, for some, docs/adr/), needed because
#: source: pointers like 'docs/adr/004.md' resolve against the process's
#: cwd — the tests pass cwd=project to make that resolution real.
_copy_project_fixture = _copy_fixture


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


# --- ACX-06: CX-SRC ---------------------------------------------------------


@pytest.mark.spec("ACX-06")
def test_cx_src_reports_missing_source_pointer_when_mode_is_index(
    tmp_path: Path,
) -> None:
    """ACX-06-CT-01: stack.yaml is mode: index and frameworks.backend has a
    name but no source pointer -> CX-SRC warning."""
    project = _copy_project_fixture("src_missing", tmp_path / "project")
    context_dir = project / "docs" / "agent-context"

    findings, _ = _run_context_lint(context_dir, cwd=project)

    src_findings = _findings_with_code(findings, "CX-SRC")
    assert any(
        f["artifact"] == "stack.yaml" and "frameworks.backend" in f["message"]
        for f in src_findings
    )
    assert all(f["severity"] == "warning" for f in src_findings)


# --- ACX-07: CX-SRC-EXIST ---------------------------------------------------


@pytest.mark.spec("ACX-07")
def test_cx_src_exist_reports_unresolvable_source_path(tmp_path: Path) -> None:
    """ACX-07-CT-01: a source: pointer to a file that does not exist on
    disk is reported as CX-SRC-EXIST."""
    project = _copy_project_fixture("src_exist_missing", tmp_path / "project")
    context_dir = project / "docs" / "agent-context"

    findings, _ = _run_context_lint(context_dir, cwd=project)

    exist_findings = _findings_with_code(findings, "CX-SRC-EXIST")
    assert any(
        f["artifact"] == "stack.yaml" and "docs/adr/nonexistent.md" in f["message"]
        for f in exist_findings
    )
    assert all(f["severity"] == "warning" for f in exist_findings)


# --- ACX-08: CX-SRC-STALE ---------------------------------------------------


@pytest.mark.spec("ACX-08")
def test_cx_src_stale_reports_source_newer_than_index(tmp_path: Path) -> None:
    """ACX-08-CT-01: the source file's mtime is bumped past stack.yaml's
    mtime after the copy, then context-lint reports CX-SRC-STALE."""
    project = _copy_project_fixture("src_stale", tmp_path / "project")
    context_dir = project / "docs" / "agent-context"
    stack_path = context_dir / "stack.yaml"
    source_path = project / "docs" / "adr" / "004.md"

    index_mtime = stack_path.stat().st_mtime
    newer = index_mtime + 5
    os.utime(source_path, (newer, newer))

    findings, _ = _run_context_lint(context_dir, cwd=project)

    stale_findings = _findings_with_code(findings, "CX-SRC-STALE")
    assert any(
        f["artifact"] == "stack.yaml" and "docs/adr/004.md" in f["message"]
        for f in stale_findings
    )
    assert all(f["severity"] == "info" for f in stale_findings)


@pytest.mark.spec("ACX-08")
def test_cx_src_stale_not_reported_when_mtimes_are_equal(tmp_path: Path) -> None:
    """Equal mtimes are treated as not stale (per the story's implementer
    notes) — this is the boundary the '>' comparison must respect."""
    project = _copy_project_fixture("src_stale", tmp_path / "project")
    context_dir = project / "docs" / "agent-context"
    stack_path = context_dir / "stack.yaml"
    source_path = project / "docs" / "adr" / "004.md"

    same = stack_path.stat().st_mtime
    os.utime(source_path, (same, same))

    findings, _ = _run_context_lint(context_dir, cwd=project)

    assert _findings_with_code(findings, "CX-SRC-STALE") == []


# --- ACX-09: CX-GUIDE-REF ----------------------------------------------------


@pytest.mark.spec("ACX-09")
def test_cx_guide_ref_no_finding_when_key_path_resolves(tmp_path: Path) -> None:
    """ACX-09-CT-01: reading-guides.yaml references stack.yaml#frameworks.backend,
    which exists -> no CX-GUIDE-REF finding for that reference."""
    context_dir = _copy_fixture("guide_ref/docs/agent-context", tmp_path / "ctx")

    findings, _ = _run_context_lint(context_dir)

    assert not any(
        "frameworks.backend" in f["message"]
        for f in _findings_with_code(findings, "CX-GUIDE-REF")
    )


@pytest.mark.spec("ACX-09")
def test_cx_guide_ref_reports_unresolvable_key_path(tmp_path: Path) -> None:
    """ACX-09-CT-02: reading-guides.yaml is edited to reference
    stack.yaml#frameworks.nonexistent, which stack.yaml has no such key
    for -> CX-GUIDE-REF warning."""
    context_dir = _copy_fixture("guide_ref/docs/agent-context", tmp_path / "ctx")
    guide = context_dir / "reading-guides.yaml"
    guide.write_text(
        guide.read_text(encoding="utf-8").replace(
            "frameworks.backend", "frameworks.nonexistent"
        )
    )

    findings, _ = _run_context_lint(context_dir)

    ref_findings = _findings_with_code(findings, "CX-GUIDE-REF")
    assert any(
        f["artifact"] == "reading-guides.yaml"
        and "stack.yaml#frameworks.nonexistent" in f["message"]
        for f in ref_findings
    )
    assert all(f["severity"] == "warning" for f in ref_findings)


@pytest.mark.spec("ACX-09")
def test_cx_guide_ref_checks_key_existence_only_not_value(tmp_path: Path) -> None:
    """ACX-09-CT-03: reading-guides.yaml references stack.yaml#licensing.project,
    whose value is null -> no CX-GUIDE-REF finding; the key's presence is
    all that matters."""
    context_dir = _copy_fixture("guide_ref/docs/agent-context", tmp_path / "ctx")

    findings, _ = _run_context_lint(context_dir)

    assert not any(
        "licensing.project" in f["message"]
        for f in _findings_with_code(findings, "CX-GUIDE-REF")
    )


# --- ACX-10: CX-FORMAT ------------------------------------------------------


def _run_context_lint_root(root: Path) -> tuple[list[dict], dict]:
    """Run context-lint against root with neither --context-dir nor
    --charter-dir, so format detection (ST-0192) drives dispatch -- the
    counterpart to _run_context_lint above, which always passes an explicit
    --context-dir and therefore never exercises format detection or the
    testing.yaml carve-out."""
    args = [
        sys.executable,
        str(SCRIPT),
        "--root",
        str(root),
        "--format",
        "json",
    ]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    payload = json.loads(result.stderr)
    return payload["findings"], payload["summary"]


@pytest.mark.spec("ACX-10")
def test_cx_format_reports_mixed_locations() -> None:
    """ACX-10-CT-01: docs/agent-context/stack.yaml and
    docs/charter/tech-stack.md both exist -> a CX-FORMAT error is reported
    (agent-context.feature Rule: context-lint validates, Scenario: CX-FORMAT
    reports mixed locations)."""
    root = FIXTURES / "format_mixed"

    findings, _ = _run_context_lint_root(root)

    format_findings = _findings_with_code(findings, "CX-FORMAT")
    assert format_findings
    assert all(f["severity"] == "error" for f in format_findings)


@pytest.mark.spec("ACX-10")
def test_cx_format_does_not_flag_split_testing_yaml_location() -> None:
    """ACX-10-CT-02: docs/agent-context/stack.yaml exists and testing.yaml
    exists only at docs/charter/testing.yaml -> no CX-FORMAT error, because
    testing.yaml is not one of the three format-detection-chain locations
    (agent-context.feature Rule: context-lint validates, Scenario: CX-FORMAT
    does not flag split testing.yaml location)."""
    root = FIXTURES / "testing_yaml_charter_fallback"

    findings, _ = _run_context_lint_root(root)

    assert _findings_with_code(findings, "CX-FORMAT") == []


# --- ACX-13: testing.yaml CX-PARSE-only carve-out ---------------------------


@pytest.mark.spec("ACX-13")
def test_testing_yaml_gets_cx_parse_only_not_lifecycle_checks() -> None:
    """ACX-13-CT-01: docs/agent-context/testing.yaml exists with a shape
    that would trip CX-MODE-INVALID and CX-NULL if it were validated as a
    Layer 2 index file (mode: bogus, a null leaf) -- context-lint applies
    CX-PARSE only; CX-SRC, CX-MODE, CX-MODE-INVALID, CX-NULL, and CX-KEYS
    never fire for it (agent-context.feature Rule: testing.yaml operates as
    a lifecycle-exempt peer file, Scenario: context-lint validates
    testing.yaml with CX-PARSE only)."""
    root = FIXTURES / "testing_yaml_parse_only"

    findings, _ = _run_context_lint_root(root)

    testing_findings = [f for f in findings if f["artifact"] == "testing.yaml"]
    assert testing_findings == []
    exempt_codes = {"CX-SRC", "CX-MODE", "CX-MODE-INVALID", "CX-NULL", "CX-KEYS"}
    assert not any(
        f["artifact"] == "testing.yaml" and f["code"] in exempt_codes for f in findings
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
