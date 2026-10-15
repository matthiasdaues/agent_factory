"""Contract tests for usage.accounting — conservation rules and snapshot selection.

Tests exercise the SQL views through the real preflight pipeline
against synthetic JSONL fixtures.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from usage.accounting import (
    CONSERVATION_RULES,
    build_session_roots,
    check_unknown_clis,
    compute_session_usage,
    select_latest_snapshots,
)
from usage.preflight import run_preflight
from usage.registry import KNOWN_CLIS

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _preflight_conn(paths: list[Path]):
    """Run preflight and return the DuckDB connection."""
    result = run_preflight(paths)
    return result.conn


def _session_rows(conn) -> list[dict]:
    """Run the full accounting pipeline and return session usage rows."""
    select_latest_snapshots(conn)
    unknown = check_unknown_clis(conn)
    assert not unknown, f"Unexpected unknown CLIs: {unknown}"
    build_session_roots(conn)
    compute_session_usage(conn)
    rows = conn.execute(
        "SELECT session_id, cli, normalized_input, normalized_output, "
        "normalized_total FROM session_usage ORDER BY cli, session_id"
    ).fetchall()
    return [
        {
            "session_id": r[0],
            "cli": r[1],
            "normalized_input": r[2],
            "normalized_output": r[3],
            "normalized_total": r[4],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Conservation rules registry
# ---------------------------------------------------------------------------


class TestConservationRules:
    """CONSERVATION_RULES maps every KNOWN_CLI to a strategy."""

    def test_keys_match_known_clis(self) -> None:
        assert set(CONSERVATION_RULES.keys()) == KNOWN_CLIS

    def test_claude_code_strategy(self) -> None:
        assert CONSERVATION_RULES["claude-code"] == "root_and_children"

    def test_pi_strategy(self) -> None:
        assert CONSERVATION_RULES["pi"] == "root_and_descendants"

    def test_codex_strategy(self) -> None:
        assert CONSERVATION_RULES["codex"] == "inclusive_root"

    def test_copilot_strategy(self) -> None:
        assert CONSERVATION_RULES["copilot"] == "inclusive_root"


# ---------------------------------------------------------------------------
# Latest snapshot selection
# ---------------------------------------------------------------------------


@pytest.mark.spec("LU-03")
class TestLatestSnapshotSelection:
    """Greatest _source_file then greatest _line_number wins."""

    def test_selects_latest_capture(self, multi_cli_dir: Path) -> None:
        """Two snapshots of same run in different files — later file wins."""
        paths = sorted(multi_cli_dir.glob("claude_code_capture*.jsonl"))
        assert len(paths) == 2, "Need both capture files"
        conn = _preflight_conn(paths)
        select_latest_snapshots(conn)

        rows = conn.execute(
            "SELECT record_id, normalized_total, _source_file "
            "FROM latest_run_snapshots "
            "WHERE record_id = 'run-cc-root' "
            "ORDER BY record_id"
        ).fetchall()
        assert len(rows) == 1, "Should deduplicate to one snapshot"
        # capture2 sorts after capture1, so capture2 values win
        assert rows[0][1] == 180  # normalized_total from capture2

    def test_tiebreak_by_line_number(self, tmp_path: Path) -> None:
        """Two snapshots in same file, different lines — highest line wins."""
        # Build a single file with two snapshots of the same run
        line1 = (
            '{"record_id":"run-dup","project_id":"proj-test",'
            '"project_name":"test","normalized_input":10,'
            '"normalized_output":5,"normalized_total":15,'
            '"cli":"claude-code","session_id":"sess-dup",'
            '"parent_session_id":null,"depth":0,'
            '"recorded_at":"2026-01-15T10:00:00Z","agent":"a",'
            '"model":"m","provider":"p","reported_input":10,'
            '"reported_output":5,"reported_cache_read":0,'
            '"reported_cache_write":0,"usage_granularity":"turn",'
            '"usage_capability":"full","cache_miss_turns":0,'
            '"cache_miss_input_tokens":0,"late_early_input_ratio":1.0,'
            '"exit_status":"success","branch":"main","commit_id":"x",'
            '"transcript_ref":{"path":"/t.jsonl","span":"0:100"}}'
        )
        line2 = (
            '{"record_id":"run-dup","project_id":"proj-test",'
            '"project_name":"test","normalized_input":20,'
            '"normalized_output":10,"normalized_total":30,'
            '"cli":"claude-code","session_id":"sess-dup",'
            '"parent_session_id":null,"depth":0,'
            '"recorded_at":"2026-01-15T10:00:00Z","agent":"a",'
            '"model":"m","provider":"p","reported_input":20,'
            '"reported_output":10,"reported_cache_read":0,'
            '"reported_cache_write":0,"usage_granularity":"turn",'
            '"usage_capability":"full","cache_miss_turns":0,'
            '"cache_miss_input_tokens":0,"late_early_input_ratio":1.0,'
            '"exit_status":"success","branch":"main","commit_id":"x",'
            '"transcript_ref":{"path":"/t.jsonl","span":"0:100"}}'
        )
        f = tmp_path / "dup.jsonl"
        f.write_text(line1 + "\n" + line2 + "\n")

        conn = _preflight_conn([f])
        select_latest_snapshots(conn)

        rows = conn.execute(
            "SELECT normalized_total FROM latest_run_snapshots"
        ).fetchall()
        assert len(rows) == 1
        assert rows[0][0] == 30  # line 2 (higher _line_number) wins


# ---------------------------------------------------------------------------
# Claude-code conservation: root + direct children
# ---------------------------------------------------------------------------


@pytest.mark.spec("LU-03")
class TestClaudeCodeConservation:
    """Root + direct children only."""

    def test_includes_root_and_children(self, multi_cli_dir: Path) -> None:
        """Expected total = latest root (180) + child1 (65) + child2 (37) = 282."""
        paths = sorted(multi_cli_dir.glob("claude_code_capture*.jsonl"))
        conn = _preflight_conn(paths)
        rows = _session_rows(conn)

        cc_rows = [r for r in rows if r["cli"] == "claude-code"]
        assert len(cc_rows) == 1
        assert cc_rows[0]["session_id"] == "sess-cc-root"
        assert cc_rows[0]["normalized_total"] == 282

    def test_excludes_grandchildren(self, tmp_path: Path) -> None:
        """Add a grandchild — it must NOT be included in claude-code total."""
        import json

        base = {
            "project_id": "proj-test",
            "project_name": "test",
            "agent": "a",
            "model": "m",
            "provider": "p",
            "reported_input": 10,
            "reported_output": 5,
            "reported_cache_read": 0,
            "reported_cache_write": 0,
            "usage_granularity": "turn",
            "usage_capability": "full",
            "cache_miss_turns": 0,
            "cache_miss_input_tokens": 0,
            "late_early_input_ratio": 1.0,
            "exit_status": "success",
            "branch": "main",
            "commit_id": "x",
            "transcript_ref": {"path": "/t.jsonl", "span": "0:100"},
        }
        root = {
            **base,
            "record_id": "r1",
            "cli": "claude-code",
            "session_id": "s-root",
            "parent_session_id": None,
            "depth": 0,
            "recorded_at": "2026-01-15T10:00:00Z",
            "normalized_input": 100,
            "normalized_output": 50,
            "normalized_total": 150,
        }
        child = {
            **base,
            "record_id": "r2",
            "cli": "claude-code",
            "session_id": "s-child",
            "parent_session_id": "s-root",
            "depth": 1,
            "recorded_at": "2026-01-15T10:01:00Z",
            "normalized_input": 30,
            "normalized_output": 20,
            "normalized_total": 50,
        }
        grandchild = {
            **base,
            "record_id": "r3",
            "cli": "claude-code",
            "session_id": "s-grand",
            "parent_session_id": "s-child",
            "depth": 2,
            "recorded_at": "2026-01-15T10:02:00Z",
            "normalized_input": 10,
            "normalized_output": 5,
            "normalized_total": 15,
        }

        f = tmp_path / "cc_grand.jsonl"
        f.write_text(
            json.dumps(root)
            + "\n"
            + json.dumps(child)
            + "\n"
            + json.dumps(grandchild)
            + "\n"
        )

        conn = _preflight_conn([f])
        rows = _session_rows(conn)

        cc_rows = [r for r in rows if r["cli"] == "claude-code"]
        assert len(cc_rows) == 1
        # 150 (root) + 50 (child) = 200; grandchild's 15 excluded
        assert cc_rows[0]["normalized_total"] == 200


# ---------------------------------------------------------------------------
# Pi conservation: root + ALL descendants
# ---------------------------------------------------------------------------


@pytest.mark.spec("LU-03")
class TestPiConservation:
    """Root + ALL descendants."""

    def test_includes_all_descendants(self, multi_cli_dir: Path) -> None:
        """Total = root (300) + child (75) + grandchild (15) = 390."""
        paths = [multi_cli_dir / "pi_sessions.jsonl"]
        conn = _preflight_conn(paths)
        rows = _session_rows(conn)

        pi_rows = [r for r in rows if r["cli"] == "pi"]
        assert len(pi_rows) == 1
        assert pi_rows[0]["session_id"] == "sess-pi-root"
        assert pi_rows[0]["normalized_total"] == 390


# ---------------------------------------------------------------------------
# Codex conservation: inclusive root only
# ---------------------------------------------------------------------------


@pytest.mark.spec("LU-03")
class TestCodexConservation:
    """Inclusive root only."""

    def test_root_only(self, multi_cli_dir: Path) -> None:
        """Total = root (700) only; child (150) excluded."""
        paths = [multi_cli_dir / "codex_sessions.jsonl"]
        conn = _preflight_conn(paths)
        rows = _session_rows(conn)

        codex_rows = [r for r in rows if r["cli"] == "codex"]
        assert len(codex_rows) == 1
        assert codex_rows[0]["session_id"] == "sess-codex-root"
        assert codex_rows[0]["normalized_total"] == 700


# ---------------------------------------------------------------------------
# Copilot conservation: same as codex
# ---------------------------------------------------------------------------


@pytest.mark.spec("LU-03")
class TestCopilotConservation:
    """Same as codex — inclusive root only."""

    def test_root_only(self, multi_cli_dir: Path) -> None:
        """Total = root (550) only; child (120) excluded."""
        paths = [multi_cli_dir / "copilot_sessions.jsonl"]
        conn = _preflight_conn(paths)
        rows = _session_rows(conn)

        copilot_rows = [r for r in rows if r["cli"] == "copilot"]
        assert len(copilot_rows) == 1
        assert copilot_rows[0]["session_id"] == "sess-copilot-root"
        assert copilot_rows[0]["normalized_total"] == 550


# ---------------------------------------------------------------------------
# Unknown CLI detection
# ---------------------------------------------------------------------------


@pytest.mark.spec("LU-03")
class TestUnknownCli:
    """Unknown CLI detected before conservation computation."""

    def test_unknown_cli_detected(self, multi_cli_dir: Path) -> None:
        """Record with unknown CLI returns the offending value."""
        paths = [multi_cli_dir / "unknown_cli.jsonl"]
        conn = _preflight_conn(paths)
        select_latest_snapshots(conn)
        unknown = check_unknown_clis(conn)
        assert "mystery-tool" in unknown

    def test_known_clis_pass(self, multi_cli_dir: Path) -> None:
        """All-known CLIs return empty set."""
        paths = [multi_cli_dir / "pi_sessions.jsonl"]
        conn = _preflight_conn(paths)
        select_latest_snapshots(conn)
        unknown = check_unknown_clis(conn)
        assert unknown == set()
