"""Tests for usage.preflight — line classification and ancestry validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from usage.preflight import (
    CYCLE,
    PARENT_BOUNDARY,
    PARENT_CONFLICT,
    PARENT_MISSING,
    ROOT_COUNT,
    SELF_PARENT,
    run_preflight,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _failure_codes(result, *, session_id: str | None = None) -> list[str]:
    """Extract failure codes from the result, optionally filtered by session."""
    if session_id is not None:
        rows = result.conn.execute(
            "SELECT _failure_code FROM preflight_failure "
            "WHERE session_id = ?",
            [session_id],
        ).fetchall()
    else:
        rows = result.conn.execute(
            "SELECT _failure_code FROM preflight_failure"
        ).fetchall()
    return [r[0] for r in rows]


def _valid_session_ids(result) -> set[str]:
    """Extract distinct session_ids from valid records."""
    rows = result.conn.execute(
        "SELECT DISTINCT session_id FROM preflight_valid"
    ).fetchall()
    return {r[0] for r in rows}


def _total_rows(result) -> int:
    """Count total rows across both relations."""
    return result.valid_count + result.failure_count


# ---------------------------------------------------------------------------
# Valid input — zero failures
# ---------------------------------------------------------------------------

@pytest.mark.spec("LU-05")
class TestValidInput:
    """A well-formed session tree produces zero failures."""

    def test_no_failures(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "valid_tree.jsonl"])
        assert result.has_failures is False

    def test_valid_count_matches_lines(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "valid_tree.jsonl"])
        assert result.valid_count == 3

    def test_failure_count_zero(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "valid_tree.jsonl"])
        assert result.failure_count == 0

    def test_all_sessions_present(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "valid_tree.jsonl"])
        assert _valid_session_ids(result) == {
            "sess-root", "sess-child1", "sess-child2",
        }


# ---------------------------------------------------------------------------
# Exhaustive classification
# ---------------------------------------------------------------------------

@pytest.mark.spec("LU-05")
class TestExhaustiveClassification:
    """Every input line lands in exactly one relation."""

    @pytest.mark.parametrize("fixture", [
        "valid_tree.jsonl",
        "parent_conflict.jsonl",
        "self_parent.jsonl",
        "root_count_zero.jsonl",
        "root_count_multi.jsonl",
        "parent_missing.jsonl",
        "parent_boundary.jsonl",
        "cycle.jsonl",
    ])
    def test_valid_plus_failure_equals_total(
        self, ancestry_dir: Path, fixture: str,
    ) -> None:
        path = ancestry_dir / fixture
        line_count = sum(
            1 for line in path.read_text().splitlines() if line.strip()
        )
        result = run_preflight([path])
        assert _total_rows(result) == line_count

    def test_multi_file_exhaustive(self, ancestry_dir: Path) -> None:
        paths = [
            ancestry_dir / "valid_tree.jsonl",
            ancestry_dir / "self_parent.jsonl",
        ]
        total_lines = sum(
            sum(1 for line in p.read_text().splitlines() if line.strip())
            for p in paths
        )
        result = run_preflight(paths)
        assert _total_rows(result) == total_lines

    def test_empty_input(self) -> None:
        result = run_preflight([])
        assert result.valid_count == 0
        assert result.failure_count == 0
        assert result.has_failures is False


# ---------------------------------------------------------------------------
# PARENT_CONFLICT
# ---------------------------------------------------------------------------

@pytest.mark.spec("LU-05")
class TestParentConflict:
    """Snapshots of one logical run disagreeing on parent_session_id."""

    def test_conflicting_records_flagged(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "parent_conflict.jsonl"])
        codes = _failure_codes(result, session_id="sess-pc01")
        assert all(c == PARENT_CONFLICT for c in codes)
        assert len(codes) == 2

    def test_non_conflicting_root_valid(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "parent_conflict.jsonl"])
        assert "sess-pc-root" in _valid_session_ids(result)

    def test_has_failures_true(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "parent_conflict.jsonl"])
        assert result.has_failures is True


# ---------------------------------------------------------------------------
# SELF_PARENT
# ---------------------------------------------------------------------------

@pytest.mark.spec("LU-05")
class TestSelfParent:
    """A session whose parent_session_id equals its own session_id."""

    def test_self_parent_flagged(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "self_parent.jsonl"])
        codes = _failure_codes(result, session_id="sess-sp01")
        assert codes == [SELF_PARENT]

    def test_root_session_valid(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "self_parent.jsonl"])
        assert "sess-sp-root" in _valid_session_ids(result)


# ---------------------------------------------------------------------------
# ROOT_COUNT
# ---------------------------------------------------------------------------

@pytest.mark.spec("LU-05")
class TestRootCount:
    """CLI with zero or more than one root session."""

    def test_zero_roots_flags_root_count(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "root_count_zero.jsonl"])
        codes = _failure_codes(result, session_id="sess-rz01")
        assert codes == [ROOT_COUNT]

    def test_zero_roots_other_session_parent_missing(
        self, ancestry_dir: Path,
    ) -> None:
        """sess-rz02 points to a missing parent — PARENT_MISSING takes priority."""
        result = run_preflight([ancestry_dir / "root_count_zero.jsonl"])
        codes = _failure_codes(result, session_id="sess-rz02")
        assert codes == [PARENT_MISSING]

    def test_independent_roots_are_valid(self, ancestry_dir: Path) -> None:
        """Independent root sessions form separate single-root components."""
        result = run_preflight([ancestry_dir / "root_count_multi.jsonl"])
        assert result.valid_count == 3
        assert result.failure_count == 0


# ---------------------------------------------------------------------------
# PARENT_MISSING
# ---------------------------------------------------------------------------

@pytest.mark.spec("LU-05")
class TestParentMissing:
    """Parent session not present in the selected input."""

    def test_missing_parent_flagged(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "parent_missing.jsonl"])
        codes = _failure_codes(result, session_id="sess-pm01")
        assert codes == [PARENT_MISSING]

    def test_root_session_valid(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "parent_missing.jsonl"])
        assert "sess-pm-root" in _valid_session_ids(result)


# ---------------------------------------------------------------------------
# PARENT_BOUNDARY
# ---------------------------------------------------------------------------

@pytest.mark.spec("LU-05")
class TestParentBoundary:
    """Parent session exists but under a different CLI."""

    def test_boundary_flagged(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "parent_boundary.jsonl"])
        codes = _failure_codes(result, session_id="sess-pb01")
        assert codes == [PARENT_BOUNDARY]

    def test_root_sessions_valid(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "parent_boundary.jsonl"])
        valid = _valid_session_ids(result)
        assert "sess-pb-root" in valid
        assert "sess-pb-other-root" in valid


# ---------------------------------------------------------------------------
# CYCLE
# ---------------------------------------------------------------------------

@pytest.mark.spec("LU-05")
class TestCycle:
    """Directed cycle in parent_session_id chain."""

    def test_both_sessions_flagged(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "cycle.jsonl"])
        codes = _failure_codes(result)
        assert all(c == CYCLE for c in codes)
        assert len(codes) == 2

    def test_no_valid_records(self, ancestry_dir: Path) -> None:
        result = run_preflight([ancestry_dir / "cycle.jsonl"])
        assert result.valid_count == 0


# ---------------------------------------------------------------------------
# Conflict priority — no cascading
# ---------------------------------------------------------------------------

@pytest.mark.spec("LU-05")
class TestConflictPriority:
    """Parent-conflict lines do not cascade to other failure codes."""

    def test_conflict_does_not_produce_other_codes(
        self, ancestry_dir: Path,
    ) -> None:
        """The two conflicting records both get PARENT_CONFLICT, not
        PARENT_MISSING or ROOT_COUNT even though the root is the only
        non-conflict session."""
        result = run_preflight([ancestry_dir / "parent_conflict.jsonl"])
        codes = _failure_codes(result, session_id="sess-pc01")
        assert set(codes) == {PARENT_CONFLICT}

    def test_conflict_records_excluded_from_session_checks(
        self, ancestry_dir: Path, tmp_path: Path,
    ) -> None:
        """Craft a file where the ONLY records are conflicting.  With
        conflict excluded, no session-level check runs and no other
        failure code appears."""
        import json

        def _rec(record_id, session_id, parent):
            return {
                "record_id": record_id,
                "project_id": "proj-test",
                "project_name": "test",
                "normalized_input": 10,
                "normalized_output": 5,
                "normalized_total": 15,
                "cli": "claude-code",
                "session_id": session_id,
                "parent_session_id": parent,
                "depth": 0,
                "recorded_at": "2026-01-01T00:00:00Z",
                "agent": None,
                "model": None,
                "provider": None,
                "reported_input": None,
                "reported_output": None,
                "reported_cache_read": None,
                "reported_cache_write": None,
                "usage_granularity": None,
                "usage_capability": None,
                "cache_miss_turns": None,
                "cache_miss_input_tokens": None,
                "late_early_input_ratio": None,
                "exit_status": None,
                "branch": None,
                "commit_id": None,
                "transcript_ref": None,
            }

        fixture = tmp_path / "only_conflict.jsonl"
        fixture.write_text(
            json.dumps(_rec("rec-x", "sess-x", "sess-a")) + "\n"
            + json.dumps(_rec("rec-x", "sess-x", "sess-b")) + "\n",
            encoding="utf-8",
        )
        result = run_preflight([fixture])
        codes = _failure_codes(result)
        assert all(c == PARENT_CONFLICT for c in codes)
        assert result.valid_count == 0
        assert result.failure_count == 2
