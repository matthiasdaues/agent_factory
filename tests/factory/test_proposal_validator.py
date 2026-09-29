"""Contract tests for the proposal readiness validator.

Owned contracts:
  - Missing file returns file_exists=False and early exit (standard risk)
  - Valid proposal passes all checks (standard risk)
  - Missing frontmatter fails frontmatter_present (standard risk)
  - Wrong status fails status_accepted (standard risk)
  - Missing required section fails section check (standard risk)
  - assessed_commit is passed through, not resolved internally (standard risk)
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES_DIR = REPO_ROOT / "packages" / "factory"

if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.validators.proposal import validate_proposal

VALID_PROPOSAL = """\
---
title: Test Proposal
status: accepted
---

# Overview

## Problem

Something is wrong.

## Solution

Fix it.

## Scope

Everything.
"""


class TestMissingFile:
    def test_file_not_found(self, tmp_path):
        result = validate_proposal(tmp_path / "nonexistent.md", assessed_commit="abc")
        assert not result.passed
        check_names = {c.name for c in result.checks}
        assert "file_exists" in check_names
        file_check = next(c for c in result.checks if c.name == "file_exists")
        assert not file_check.passed

    def test_warnings_on_missing(self, tmp_path):
        result = validate_proposal(tmp_path / "nonexistent.md", assessed_commit="abc")
        assert any("not found" in w for w in result.warnings)


class TestValidProposal:
    def test_all_checks_pass(self, tmp_path):
        p = tmp_path / "good.md"
        p.write_text(VALID_PROPOSAL)
        result = validate_proposal(p, assessed_commit="abc123")
        assert result.passed
        assert all(c.passed for c in result.checks)

    def test_artifact_type_is_proposal(self, tmp_path):
        p = tmp_path / "good.md"
        p.write_text(VALID_PROPOSAL)
        result = validate_proposal(p, assessed_commit="abc123")
        assert result.artifact_type == "proposal"

    def test_assessed_commit_passed_through(self, tmp_path):
        p = tmp_path / "good.md"
        p.write_text(VALID_PROPOSAL)
        result = validate_proposal(p, assessed_commit="deadbeef")
        assert result.assessed_commit == "deadbeef"


class TestMissingFrontmatter:
    def test_no_frontmatter(self, tmp_path):
        p = tmp_path / "bare.md"
        p.write_text("# Just a heading\n\nNo frontmatter here.\n")
        result = validate_proposal(p, assessed_commit="abc")
        fm_check = next(c for c in result.checks if c.name == "frontmatter_present")
        assert not fm_check.passed


class TestWrongStatus:
    def test_draft_status_fails(self, tmp_path):
        text = VALID_PROPOSAL.replace("status: accepted", "status: draft")
        p = tmp_path / "draft.md"
        p.write_text(text)
        result = validate_proposal(p, assessed_commit="abc")
        status_check = next(c for c in result.checks if c.name == "status_accepted")
        assert not status_check.passed

    def test_warning_on_wrong_status(self, tmp_path):
        text = VALID_PROPOSAL.replace("status: accepted", "status: draft")
        p = tmp_path / "draft.md"
        p.write_text(text)
        result = validate_proposal(p, assessed_commit="abc")
        assert any("draft" in w for w in result.warnings)


class TestMissingSections:
    def test_missing_problem_section(self, tmp_path):
        text = VALID_PROPOSAL.replace("## Problem", "## Background")
        p = tmp_path / "no_problem.md"
        p.write_text(text)
        result = validate_proposal(p, assessed_commit="abc")
        section_check = next(c for c in result.checks if c.name == "section_problem")
        assert not section_check.passed

    def test_missing_solution_section(self, tmp_path):
        text = VALID_PROPOSAL.replace("## Solution", "## Approach")
        p = tmp_path / "no_solution.md"
        p.write_text(text)
        result = validate_proposal(p, assessed_commit="abc")
        section_check = next(c for c in result.checks if c.name == "section_solution")
        assert not section_check.passed

    def test_missing_scope_section(self, tmp_path):
        text = VALID_PROPOSAL.replace("## Scope", "## Boundaries")
        p = tmp_path / "no_scope.md"
        p.write_text(text)
        result = validate_proposal(p, assessed_commit="abc")
        section_check = next(c for c in result.checks if c.name == "section_scope")
        assert not section_check.passed


class TestDefaultCommit:
    def test_default_assessed_commit(self, tmp_path):
        p = tmp_path / "good.md"
        p.write_text(VALID_PROPOSAL)
        result = validate_proposal(p)
        assert result.assessed_commit == "unknown"
