"""Contract tests for factory/scripts/concern-lint.

Covers CTX-SECTIONS, CTX-PATHS, and CTX-LEGACY checks against the
concern-oriented agent-context model (docs/agent-context.md).

Each test runs the script as a subprocess with --format json, mirroring
the existing test_context_lint.py pattern.
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
    / "packages"
    / "factory"
    / "scripts"
    / "concern-lint"
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "concern-lint"


def _run(root: Path) -> tuple[list[dict], dict, int]:
    """Run concern-lint against a project root and return (findings, summary, exit_code)."""
    args = [sys.executable, str(SCRIPT), "--root", str(root), "--format", "json"]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    payload = json.loads(result.stderr)
    return payload["findings"], payload["summary"], result.returncode


def _codes(findings: list[dict]) -> set[str]:
    return {f["code"] for f in findings}


def _findings_with_code(findings: list[dict], code: str) -> list[dict]:
    return [f for f in findings if f["code"] == code]


def _copy_fixture(name: str, dest: Path) -> Path:
    """Copy a named fixture directory to dest and return dest."""
    shutil.copytree(FIXTURES / name, dest)
    return dest


# ---------------------------------------------------------------------------
# CTX-SECTIONS: required category headings and concern structure
# ---------------------------------------------------------------------------


class TestCtxSections:
    """CTX-SECTIONS fires when a required category heading is missing or when
    a concern section lacks a description line or at least one Read: path."""

    def test_valid_passes(self, tmp_path: Path) -> None:
        root = _copy_fixture("valid", tmp_path / "project")
        findings, summary, rc = _run(root)
        assert rc == 0
        assert summary["error"] == 0

    def test_missing_heading_fires(self, tmp_path: Path) -> None:
        """Missing 'Technical concerns' heading triggers CTX-SECTIONS."""
        root = _copy_fixture("missing_heading", tmp_path / "project")
        findings, summary, rc = _run(root)
        assert rc != 0
        section_findings = _findings_with_code(findings, "CTX-SECTIONS")
        assert len(section_findings) >= 1
        messages = [f["message"] for f in section_findings]
        assert any("Technical concerns" in m for m in messages)

    def test_missing_description_fires(self, tmp_path: Path) -> None:
        """A concern section with no description line triggers CTX-SECTIONS."""
        root = _copy_fixture("missing_description", tmp_path / "project")
        findings, summary, rc = _run(root)
        assert rc != 0
        section_findings = _findings_with_code(findings, "CTX-SECTIONS")
        assert len(section_findings) >= 1
        messages = [f["message"] for f in section_findings]
        assert any("description" in m.lower() for m in messages)

    def test_missing_read_fires(self, tmp_path: Path) -> None:
        """A concern section with no Read: path triggers CTX-SECTIONS."""
        root = _copy_fixture("missing_read", tmp_path / "project")
        findings, summary, rc = _run(root)
        assert rc != 0
        section_findings = _findings_with_code(findings, "CTX-SECTIONS")
        assert len(section_findings) >= 1
        messages = [f["message"] for f in section_findings]
        assert any("Read:" in m for m in messages)


# ---------------------------------------------------------------------------
# CTX-PATHS: path resolution for Read: and Boundary: lines
# ---------------------------------------------------------------------------


class TestCtxPaths:
    """CTX-PATHS fires when a path in a Read: or Boundary: line does not
    resolve to an existing file or glob match."""

    def test_nonexistent_read_path_fires(self, tmp_path: Path) -> None:
        root = _copy_fixture("bad_path", tmp_path / "project")
        findings, summary, rc = _run(root)
        assert rc != 0
        path_findings = _findings_with_code(findings, "CTX-PATHS")
        assert len(path_findings) >= 1

    def test_nonexistent_boundary_path_fires(self, tmp_path: Path) -> None:
        root = _copy_fixture("bad_boundary", tmp_path / "project")
        findings, summary, rc = _run(root)
        assert rc != 0
        path_findings = _findings_with_code(findings, "CTX-PATHS")
        assert len(path_findings) >= 1
        messages = [f["message"] for f in path_findings]
        assert any("nonexistent/interface-contracts.md" in m for m in messages)

    def test_glob_path_resolves(self, tmp_path: Path) -> None:
        """A glob pattern that matches at least one file does not fire."""
        root = _copy_fixture("glob_path", tmp_path / "project")
        findings, summary, rc = _run(root)
        assert rc == 0
        assert "CTX-PATHS" not in _codes(findings)


# ---------------------------------------------------------------------------
# CTX-LEGACY: no legacy residue alongside concern-format agent-context.md
# ---------------------------------------------------------------------------


class TestCtxLegacy:
    """CTX-LEGACY fires when YAML agent-context files (other than
    testing.yaml) or a docs/charter/ directory exist alongside
    docs/agent-context.md."""

    def test_yaml_file_fires(self, tmp_path: Path) -> None:
        """A .yaml file other than testing.yaml under docs/agent-context/
        triggers CTX-LEGACY."""
        root = _copy_fixture("legacy_yaml", tmp_path / "project")
        findings, summary, rc = _run(root)
        assert rc != 0
        legacy_findings = _findings_with_code(findings, "CTX-LEGACY")
        assert len(legacy_findings) >= 1

    def test_charter_dir_fires(self, tmp_path: Path) -> None:
        """A docs/charter/ directory alongside docs/agent-context.md
        triggers CTX-LEGACY."""
        root = _copy_fixture("legacy_charter", tmp_path / "project")
        findings, summary, rc = _run(root)
        assert rc != 0
        legacy_findings = _findings_with_code(findings, "CTX-LEGACY")
        assert len(legacy_findings) >= 1

    def test_testing_yaml_alone_is_ok(self, tmp_path: Path) -> None:
        """testing.yaml under docs/agent-context/ does NOT trigger
        CTX-LEGACY (it is explicitly exempt)."""
        root = _copy_fixture("legacy_testing_yaml_ok", tmp_path / "project")
        findings, summary, rc = _run(root)
        assert rc == 0
        assert "CTX-LEGACY" not in _codes(findings)


# ---------------------------------------------------------------------------
# Exit code semantics
# ---------------------------------------------------------------------------


class TestExitCode:
    """concern-lint exits 0 when all checks pass, non-zero on any failure."""

    def test_clean_exit_zero(self, tmp_path: Path) -> None:
        root = _copy_fixture("valid", tmp_path / "project")
        _, _, rc = _run(root)
        assert rc == 0

    def test_failure_exit_nonzero(self, tmp_path: Path) -> None:
        root = _copy_fixture("missing_heading", tmp_path / "project")
        _, _, rc = _run(root)
        assert rc != 0
