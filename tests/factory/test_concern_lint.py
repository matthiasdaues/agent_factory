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
        _findings, summary, rc = _run(root)
        assert rc == 0
        assert summary["error"] == 0

    def test_missing_heading_fires(self, tmp_path: Path) -> None:
        """Missing 'Technical concerns' heading triggers CTX-SECTIONS."""
        root = _copy_fixture("missing_heading", tmp_path / "project")
        findings, _summary, rc = _run(root)
        assert rc != 0
        section_findings = _findings_with_code(findings, "CTX-SECTIONS")
        assert len(section_findings) >= 1
        messages = [f["message"] for f in section_findings]
        assert any("Technical concerns" in m for m in messages)

    def test_missing_description_fires(self, tmp_path: Path) -> None:
        """A concern section with no description line triggers CTX-SECTIONS."""
        root = _copy_fixture("missing_description", tmp_path / "project")
        findings, _summary, rc = _run(root)
        assert rc != 0
        section_findings = _findings_with_code(findings, "CTX-SECTIONS")
        assert len(section_findings) >= 1
        messages = [f["message"] for f in section_findings]
        assert any("description" in m.lower() for m in messages)

    def test_missing_read_fires(self, tmp_path: Path) -> None:
        """A concern section with no Read: path triggers CTX-SECTIONS."""
        root = _copy_fixture("missing_read", tmp_path / "project")
        findings, _summary, rc = _run(root)
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
        findings, _summary, rc = _run(root)
        assert rc != 0
        path_findings = _findings_with_code(findings, "CTX-PATHS")
        assert len(path_findings) >= 1

    def test_nonexistent_boundary_path_fires(self, tmp_path: Path) -> None:
        root = _copy_fixture("bad_boundary", tmp_path / "project")
        findings, _summary, rc = _run(root)
        assert rc != 0
        path_findings = _findings_with_code(findings, "CTX-PATHS")
        assert len(path_findings) >= 1
        messages = [f["message"] for f in path_findings]
        assert any("nonexistent/interface-contracts.md" in m for m in messages)

    def test_glob_path_resolves(self, tmp_path: Path) -> None:
        """A glob pattern that matches at least one file does not fire."""
        root = _copy_fixture("glob_path", tmp_path / "project")
        findings, _summary, rc = _run(root)
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
        findings, _summary, rc = _run(root)
        assert rc != 0
        legacy_findings = _findings_with_code(findings, "CTX-LEGACY")
        assert len(legacy_findings) >= 1

    def test_charter_dir_fires(self, tmp_path: Path) -> None:
        """A docs/charter/ directory alongside docs/agent-context.md
        triggers CTX-LEGACY."""
        root = _copy_fixture("legacy_charter", tmp_path / "project")
        findings, _summary, rc = _run(root)
        assert rc != 0
        legacy_findings = _findings_with_code(findings, "CTX-LEGACY")
        assert len(legacy_findings) >= 1

    def test_testing_yaml_alone_is_ok(self, tmp_path: Path) -> None:
        """testing.yaml under docs/agent-context/ does NOT trigger
        CTX-LEGACY (it is explicitly exempt)."""
        root = _copy_fixture("legacy_testing_yaml_ok", tmp_path / "project")
        findings, _summary, rc = _run(root)
        assert rc == 0
        assert "CTX-LEGACY" not in _codes(findings)


# ---------------------------------------------------------------------------
# CTX-REFS: concern names in story frontmatter vs agent-context.md headings
# ---------------------------------------------------------------------------


class TestCtxRefs:
    """CTX-REFS fires when a concern name in a story's concerns: frontmatter
    does not match a ### heading under Technical or Domain concerns."""

    def test_matching_concerns_pass(self, tmp_path: Path) -> None:
        """Concerns that match headings in agent-context.md produce no CTX-REFS."""
        root = _copy_fixture("ctx_refs_valid", tmp_path / "project")
        findings, _summary, _rc = _run(root)
        refs_findings = _findings_with_code(findings, "CTX-REFS")
        assert refs_findings == []

    def test_unmatched_concerns_fire(self, tmp_path: Path) -> None:
        """Concern names not in agent-context.md trigger CTX-REFS findings."""
        root = _copy_fixture("ctx_refs_unmatched", tmp_path / "project")
        findings, _summary, _rc = _run(root)
        refs_findings = _findings_with_code(findings, "CTX-REFS")
        assert len(refs_findings) >= 2
        messages = " ".join(f["message"] for f in refs_findings)
        assert "invoicing" in messages
        assert "frontend" in messages

    def test_no_concerns_field_passes(self, tmp_path: Path) -> None:
        """Stories without a concerns field produce no CTX-REFS findings."""
        root = _copy_fixture("ctx_refs_no_concerns", tmp_path / "project")
        findings, _summary, _rc = _run(root)
        refs_findings = _findings_with_code(findings, "CTX-REFS")
        assert refs_findings == []

    def test_no_backlog_dir_passes(self, tmp_path: Path) -> None:
        """When no backlog/ exists, CTX-REFS produces no findings."""
        root = _copy_fixture("valid", tmp_path / "project")
        findings, _summary, _rc = _run(root)
        refs_findings = _findings_with_code(findings, "CTX-REFS")
        assert refs_findings == []


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

    def test_exit_code_clamped_to_one(self, tmp_path: Path) -> None:
        """Multiple errors still exit 1, not the raw error count."""
        root = _copy_fixture("bad_path", tmp_path / "project")
        _findings, summary, rc = _run(root)
        # bad_path has 3 nonexistent Read: paths → 3 CTX-PATHS errors
        assert summary["error"] >= 2
        assert rc == 1

    def test_no_agent_context_exits_clean(self, tmp_path: Path) -> None:
        """When docs/agent-context.md does not exist, concern-lint exits 0."""
        root = tmp_path / "empty_project"
        root.mkdir()
        findings, summary, rc = _run(root)
        assert rc == 0
        assert summary["error"] == 0
        assert findings == []


# ---------------------------------------------------------------------------
# Fold mark: `Folded: yes` under a domain concern (ST-0328, CAL-G03)
# ---------------------------------------------------------------------------

_FOLD_TEMPLATE = """\
# Agent Context

## Always (cross-cutting)

### Branching

Branching policy and worktree discipline.
Read: factory/rulebooks/conventions/branching-policy.md

## Technical concerns

### backend

Server-side application code.
{technical_mark}Read: factory/rulebooks/conventions/branching-policy.md

## Domain concerns

### Ledger

Double-entry bookkeeping of every payment.
{domain_mark}Read: docs/handbook/testing/conventions.md
"""


def _fold_project(tmp_path: Path, *, domain_mark: str = "", technical_mark: str = "") -> Path:
    """Copy the `valid` fixture and replace its agent-context.md with one
    domain concern and one technical concern, each with the given mark lines."""
    root = _copy_fixture("valid", tmp_path / "project")
    (root / "docs" / "agent-context.md").write_text(
        _FOLD_TEMPLATE.format(domain_mark=domain_mark, technical_mark=technical_mark),
        encoding="utf-8",
    )
    return root


class TestFoldMark:
    """The fold mark is the line `Folded: yes` directly after the description
    of a domain concern. Any other form or place is a CTX-SECTIONS error."""

    def test_valid_mark_under_domain_concern_passes(self, tmp_path: Path) -> None:
        root = _fold_project(tmp_path, domain_mark="Folded: yes\n")
        findings, summary, rc = _run(root)
        assert rc == 0, findings
        assert summary["error"] == 0

    @pytest.mark.parametrize(
        "mark",
        [
            pytest.param("Folded: no\n", id="value-no"),
            pytest.param("Folded:\n", id="value-missing"),
            pytest.param("Folded: Yes\n", id="value-capitalised"),
            pytest.param("folded: yes\n", id="key-lowercase"),
        ],
    )
    def test_malformed_mark_fires(self, tmp_path: Path, mark: str) -> None:
        root = _fold_project(tmp_path, domain_mark=mark)
        findings, _summary, rc = _run(root)
        assert rc == 1
        messages = [f["message"] for f in _findings_with_code(findings, "CTX-SECTIONS")]
        assert any("Ledger" in m and "fold mark" in m for m in messages), messages

    def test_mark_not_after_description_fires(self, tmp_path: Path) -> None:
        """A mark below the Read: line is not directly after the description."""
        root = _copy_fixture("valid", tmp_path / "project")
        text = _FOLD_TEMPLATE.format(domain_mark="", technical_mark="") + "Folded: yes\n"
        (root / "docs" / "agent-context.md").write_text(text, encoding="utf-8")
        findings, _summary, rc = _run(root)
        assert rc == 1
        messages = [f["message"] for f in _findings_with_code(findings, "CTX-SECTIONS")]
        assert any("Ledger" in m and "description" in m for m in messages), messages

    def test_mark_under_technical_concern_fires(self, tmp_path: Path) -> None:
        root = _fold_project(tmp_path, technical_mark="Folded: yes\n")
        findings, _summary, rc = _run(root)
        assert rc == 1
        messages = [f["message"] for f in _findings_with_code(findings, "CTX-SECTIONS")]
        assert any(
            "backend" in m and "## Domain concerns" in m for m in messages
        ), messages
