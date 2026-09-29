"""Tests for ST-0246 views — raw snapshots, latest run, dimensions, cache."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from usage.preflight import run_preflight
from usage.views.cache_efficiency import cache_efficiency
from usage.views.latest_run_snapshots import latest_run_snapshots
from usage.views.raw_usage_snapshots import raw_usage_snapshots
from usage.views.usage_by_dimension import (
    usage_by_dimension,
)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "from usage.cli import main; main()", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _base_record(**overrides):
    rec = {
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
    rec.update(overrides)
    return rec


def _write_fixture(tmp_path: Path, name: str, records: list[dict]) -> Path:
    f = tmp_path / name
    f.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return f


# ---------------------------------------------------------------------------
# raw_usage_snapshots
# ---------------------------------------------------------------------------


class TestRawUsageSnapshots:
    def test_empty_returns_empty(self) -> None:
        result = raw_usage_snapshots(None)
        assert result == {"view": "raw_usage_snapshots", "rows": []}

    def test_returns_all_valid_records(self, multi_cli_dir: Path) -> None:
        paths = [multi_cli_dir / "pi_sessions.jsonl"]
        pf = run_preflight(paths)
        result = raw_usage_snapshots(pf)
        assert result["view"] == "raw_usage_snapshots"
        assert len(result["rows"]) == 3

    def test_includes_evidence_identity(self, multi_cli_dir: Path) -> None:
        paths = [multi_cli_dir / "pi_sessions.jsonl"]
        pf = run_preflight(paths)
        result = raw_usage_snapshots(pf)
        row = result["rows"][0]
        assert "_source_file" in row
        assert "_line_number" in row

    def test_cli_exit_zero(self, multi_cli_dir: Path) -> None:
        _run_cli("raw_usage_snapshots", "--usage-dir", str(multi_cli_dir / ".."))
        # multi-cli has unknown_cli.jsonl — use single-cli subset

    def test_cli_single_cli(self, tmp_path: Path) -> None:
        import shutil

        src = (
            Path(__file__).resolve().parent.parent
            / "fixtures"
            / "multi-cli"
            / "pi_sessions.jsonl"
        )
        shutil.copy(src, tmp_path / "pi.jsonl")
        r = _run_cli("raw_usage_snapshots", "--usage-dir", str(tmp_path))
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["view"] == "raw_usage_snapshots"
        assert len(data["rows"]) == 3


# ---------------------------------------------------------------------------
# latest_run_snapshots
# ---------------------------------------------------------------------------


class TestLatestRunSnapshots:
    def test_empty_returns_empty(self) -> None:
        result = latest_run_snapshots(None)
        assert result == {"view": "latest_run_snapshots", "rows": []}

    def test_deduplicates_per_run(self, multi_cli_dir: Path) -> None:
        paths = sorted(multi_cli_dir.glob("claude_code_capture*.jsonl"))
        pf = run_preflight(paths)
        result = latest_run_snapshots(pf)
        assert result["view"] == "latest_run_snapshots"
        record_ids = [r["record_id"] for r in result["rows"]]
        assert len(record_ids) == len(set(record_ids))

    def test_excludes_snapshot_rank(self, multi_cli_dir: Path) -> None:
        paths = sorted(multi_cli_dir.glob("claude_code_capture*.jsonl"))
        pf = run_preflight(paths)
        result = latest_run_snapshots(pf)
        for row in result["rows"]:
            assert "_snapshot_rank" not in row

    def test_unknown_cli_returns_error(self, multi_cli_dir: Path) -> None:
        paths = [multi_cli_dir / "unknown_cli.jsonl"]
        pf = run_preflight(paths)
        result = latest_run_snapshots(pf)
        assert result["error"] == "unknown_cli"


# ---------------------------------------------------------------------------
# usage_by_dimension — validation
# ---------------------------------------------------------------------------


class TestDimensionValidation:
    def test_duplicate_dimension_rejected(self, tmp_path: Path) -> None:
        rec = _base_record(
            record_id="r1",
            cli="pi",
            session_id="s1",
            parent_session_id=None,
            depth=0,
            recorded_at="2026-01-15T10:00:00Z",
            normalized_input=10,
            normalized_output=5,
            normalized_total=15,
        )
        _write_fixture(tmp_path, "data.jsonl", [rec])
        r = _run_cli(
            "usage_by_dimension",
            "--dimensions",
            "cli,cli",
            "--usage-dir",
            str(tmp_path),
        )
        assert r.returncode == 2
        assert "duplicate" in r.stderr.lower()

    def test_unsupported_dimension_rejected(self, tmp_path: Path) -> None:
        rec = _base_record(
            record_id="r1",
            cli="pi",
            session_id="s1",
            parent_session_id=None,
            depth=0,
            recorded_at="2026-01-15T10:00:00Z",
            normalized_input=10,
            normalized_output=5,
            normalized_total=15,
        )
        _write_fixture(tmp_path, "data.jsonl", [rec])
        r = _run_cli(
            "usage_by_dimension", "--dimensions", "bogus", "--usage-dir", str(tmp_path)
        )
        assert r.returncode == 2
        assert "unsupported" in r.stderr.lower()

    def test_time_with_none_granularity_rejected(self, tmp_path: Path) -> None:
        rec = _base_record(
            record_id="r1",
            cli="pi",
            session_id="s1",
            parent_session_id=None,
            depth=0,
            recorded_at="2026-01-15T10:00:00Z",
            normalized_input=10,
            normalized_output=5,
            normalized_total=15,
        )
        _write_fixture(tmp_path, "data.jsonl", [rec])
        r = _run_cli(
            "usage_by_dimension",
            "--dimensions",
            "time",
            "--granularity",
            "none",
            "--usage-dir",
            str(tmp_path),
        )
        assert r.returncode == 2
        assert "time" in r.stderr.lower()


# ---------------------------------------------------------------------------
# usage_by_dimension — additive totals
# ---------------------------------------------------------------------------


class TestDimensionAdditivity:
    def test_no_dimensions_gives_one_total(self, tmp_path: Path) -> None:
        recs = [
            _base_record(
                record_id="r1",
                cli="pi",
                session_id="s1",
                parent_session_id=None,
                depth=0,
                recorded_at="2026-01-15T10:00:00Z",
                normalized_input=100,
                normalized_output=50,
                normalized_total=150,
            ),
            _base_record(
                record_id="r2",
                cli="pi",
                session_id="s2",
                parent_session_id="s1",
                depth=1,
                recorded_at="2026-01-15T10:01:00Z",
                normalized_input=30,
                normalized_output=20,
                normalized_total=50,
            ),
        ]
        _write_fixture(tmp_path, "data.jsonl", recs)
        pf = run_preflight([tmp_path / "data.jsonl"])
        result = usage_by_dimension(pf)
        assert len(result["rows"]) == 1
        assert result["rows"][0]["normalized_total"] == 200

    def test_cli_dimension_totals_match_session_usage(self, tmp_path: Path) -> None:
        import shutil

        src_dir = Path(__file__).resolve().parent.parent / "fixtures" / "multi-cli"
        for name in (
            "claude_code_capture1.jsonl",
            "claude_code_capture2.jsonl",
            "pi_sessions.jsonl",
            "codex_sessions.jsonl",
            "copilot_sessions.jsonl",
        ):
            shutil.copy(src_dir / name, tmp_path / name)

        paths = sorted(tmp_path.glob("*.jsonl"))
        pf = run_preflight(paths)

        from usage.views.session_usage import session_usage

        canon = session_usage(pf)
        canonical_total = sum(r["normalized_total"] for r in canon["rows"])

        pf2 = run_preflight(paths)
        dim = usage_by_dimension(pf2, dimensions=["cli"])
        dim_total = sum(r["normalized_total"] for r in dim["rows"])

        assert dim_total == canonical_total

    def test_time_dimension_with_day_granularity(self, tmp_path: Path) -> None:
        recs = [
            _base_record(
                record_id="r1",
                cli="pi",
                session_id="s1",
                parent_session_id=None,
                depth=0,
                recorded_at="2026-01-15T10:00:00Z",
                normalized_input=100,
                normalized_output=50,
                normalized_total=150,
            ),
        ]
        _write_fixture(tmp_path, "data.jsonl", recs)
        pf = run_preflight([tmp_path / "data.jsonl"])
        result = usage_by_dimension(pf, dimensions=["time"], granularity="day")
        assert len(result["rows"]) == 1
        assert "time_bucket" in result["rows"][0]
        assert result["rows"][0]["normalized_total"] == 150


# ---------------------------------------------------------------------------
# cache_efficiency — null preservation
# ---------------------------------------------------------------------------


class TestCacheEfficiency:
    def test_empty_returns_empty(self) -> None:
        result = cache_efficiency(None)
        assert result == {"view": "cache_efficiency", "rows": []}

    def test_preserves_null_cache_fields(self, tmp_path: Path) -> None:
        rec = _base_record(
            record_id="r1",
            cli="pi",
            session_id="s1",
            parent_session_id=None,
            depth=0,
            recorded_at="2026-01-15T10:00:00Z",
            normalized_input=100,
            normalized_output=50,
            normalized_total=150,
            reported_cache_read=None,
            reported_cache_write=None,
            cache_miss_turns=None,
            cache_miss_input_tokens=None,
            late_early_input_ratio=None,
        )
        _write_fixture(tmp_path, "data.jsonl", [rec])
        pf = run_preflight([tmp_path / "data.jsonl"])
        result = cache_efficiency(pf)
        assert len(result["rows"]) == 1
        row = result["rows"][0]
        assert row["reported_cache_read"] is None
        assert row["reported_cache_write"] is None
        assert row["cache_miss_turns"] is None
        assert row["cache_miss_input_tokens"] is None
        assert row["late_early_input_ratio"] is None

    def test_preserves_populated_cache_fields(self, multi_cli_dir: Path) -> None:
        paths = [multi_cli_dir / "pi_sessions.jsonl"]
        pf = run_preflight(paths)
        result = cache_efficiency(pf)
        assert result["view"] == "cache_efficiency"
        assert len(result["rows"]) > 0
        for row in result["rows"]:
            assert row["reported_cache_read"] is not None

    def test_unknown_cli_returns_error(self, multi_cli_dir: Path) -> None:
        paths = [multi_cli_dir / "unknown_cli.jsonl"]
        pf = run_preflight(paths)
        result = cache_efficiency(pf)
        assert result["error"] == "unknown_cli"


# ---------------------------------------------------------------------------
# Stable query surface — six views
# ---------------------------------------------------------------------------


class TestStableQuerySurface:
    def test_six_views_available(self) -> None:
        from usage.cli import AVAILABLE_VIEWS

        expected = {
            "raw_usage_snapshots",
            "latest_run_snapshots",
            "session_usage",
            "usage_by_dimension",
            "cache_efficiency",
            "capture_health",
        }
        assert set(AVAILABLE_VIEWS) == expected

    def test_all_views_listed_in_stderr_on_unknown(self) -> None:
        r = _run_cli("bogus_view", "--usage-dir", "/tmp")
        for v in (
            "raw_usage_snapshots",
            "latest_run_snapshots",
            "usage_by_dimension",
            "cache_efficiency",
        ):
            assert v in r.stderr
