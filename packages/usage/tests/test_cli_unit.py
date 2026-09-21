"""Direct-import unit tests for usage.cli — gives coverage.py visibility."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from usage import cli, preflight

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
PI_FIXTURE = FIXTURES / "multi-cli" / "pi_sessions.jsonl"
SNAPSHOT_DIR = FIXTURES / "snapshot"


# ── _parse_args ──────────────────────────────────────────────────────

class TestParseArgs:
    def test_minimal(self):
        args = cli._parse_args(["capture_health"])
        assert args.view == "capture_health"
        assert args.output_format == "json"
        assert args.diagnostic is False

    def test_all_flags(self):
        args = cli._parse_args([
            "usage_by_dimension",
            "--usage-dir", "/tmp/u",
            "--diagnostic",
            "--dimensions", "cli,model",
            "--granularity", "day",
            "--format", "table",
            "-o", "/tmp/out.parquet",
            "--persist", "/tmp/db.duckdb",
        ])
        assert args.view == "usage_by_dimension"
        assert args.usage_dir == "/tmp/u"
        assert args.diagnostic is True
        assert args.dimensions == "cli,model"
        assert args.granularity == "day"
        assert args.output_format == "table"
        assert args.output == "/tmp/out.parquet"
        assert args.persist == "/tmp/db.duckdb"


# ── _validate_args ───────────────────────────────────────────────────

class TestValidateArgs:
    def _args(self, **overrides):
        defaults = dict(
            view="capture_health",
            output_format="json",
            output=None,
            diagnostic=False,
        )
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_valid_returns_none(self):
        assert cli._validate_args(self._args()) is None

    def test_rejected_format(self):
        err = cli._validate_args(self._args(output_format="pandas"))
        assert "unsupported format" in err

    def test_unknown_view(self):
        err = cli._validate_args(self._args(view="bogus"))
        assert "unknown view" in err
        assert "capture_health" in err

    def test_diagnostic_wrong_view(self):
        err = cli._validate_args(self._args(view="session_usage", diagnostic=True))
        assert "diagnostic" in err


# ── _validate_parquet_args ───────────────────────────────────────────

class TestValidateParquetArgs:
    def _args(self, **overrides):
        defaults = dict(
            view="session_usage",
            output_format="json",
            output=None,
        )
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_non_parquet_passes(self):
        assert cli._validate_parquet_args(self._args()) is None

    def test_parquet_without_output(self):
        err = cli._validate_parquet_args(self._args(output_format="parquet"))
        assert "-o OUTPUT" in err

    def test_parquet_with_capture_health(self):
        err = cli._validate_parquet_args(
            self._args(output_format="parquet", output="/tmp/x", view="capture_health"),
        )
        assert "capture_health" in err

    def test_parquet_valid(self):
        assert cli._validate_parquet_args(
            self._args(output_format="parquet", output="/tmp/x"),
        ) is None


# ── _resolve_usage_dir ───────────────────────────────────────────────

class TestResolveUsageDir:
    def test_existing_dir(self, tmp_path):
        args = SimpleNamespace(usage_dir=str(tmp_path))
        assert cli._resolve_usage_dir(args) == tmp_path

    def test_nonexistent_returns_none(self):
        args = SimpleNamespace(usage_dir="/no/such/path/abc")
        assert cli._resolve_usage_dir(args) is None


# ── _find_project_root ───────────────────────────────────────────────

class TestFindProjectRoot:
    def test_finds_marker(self, tmp_path, monkeypatch):
        (tmp_path / ".agent-factory").mkdir()
        monkeypatch.chdir(tmp_path)
        assert cli._find_project_root() == tmp_path

    def test_none_when_absent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert cli._find_project_root() is None


# ── _route ───────────────────────────────────────────────────────────

def _pi_preflight(tmp_path: Path):
    """Build a real PreflightResult from the pi fixture."""
    dest = tmp_path / "pi_sessions.jsonl"
    shutil.copy(PI_FIXTURE, dest)
    return preflight.run_preflight([dest])


class TestRoute:
    def test_capture_health(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        args = SimpleNamespace(view="capture_health", diagnostic=False)
        result = cli._route(args, pr)
        assert result["view"] == "capture_health"

    def test_session_usage(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        args = SimpleNamespace(view="session_usage")
        result = cli._route(args, pr)
        assert result["view"] == "session_usage"
        assert len(result["rows"]) == 1

    def test_raw_usage_snapshots(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        args = SimpleNamespace(view="raw_usage_snapshots")
        result = cli._route(args, pr)
        assert result["view"] == "raw_usage_snapshots"

    def test_latest_run_snapshots(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        args = SimpleNamespace(view="latest_run_snapshots")
        result = cli._route(args, pr)
        assert result["view"] == "latest_run_snapshots"

    def test_cache_efficiency(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        args = SimpleNamespace(view="cache_efficiency")
        result = cli._route(args, pr)
        assert result["view"] == "cache_efficiency"

    def test_usage_by_dimension(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        args = SimpleNamespace(
            view="usage_by_dimension", dimensions=None, granularity="none",
        )
        result = cli._route(args, pr)
        assert result["view"] == "usage_by_dimension"

    def test_unhandled_raises(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        args = SimpleNamespace(view="no_such_view")
        with pytest.raises(AssertionError, match="unhandled"):
            cli._route(args, pr)

    def test_none_preflight(self):
        args = SimpleNamespace(view="capture_health", diagnostic=False)
        result = cli._route(args, None)
        assert result["view"] == "capture_health"
        assert result["total_lines"] == 0


# ── _exit_on_unknown_cli ─────────────────────────────────────────────

class TestExitOnUnknownCli:
    def test_no_error_noop(self):
        cli._exit_on_unknown_cli({"view": "session_usage", "rows": []})

    def test_exits_on_unknown(self):
        with pytest.raises(SystemExit) as exc_info:
            cli._exit_on_unknown_cli({"error": "unknown_cli", "values": ["mystery"]})
        assert exc_info.value.code == 1


# ── _duckdb_view_name ────────────────────────────────────────────────

class TestDuckdbViewName:
    def test_valid_views(self):
        assert cli._duckdb_view_name("session_usage") == "session_usage"
        assert cli._duckdb_view_name("raw_usage_snapshots") == "preflight_valid"

    def test_capture_health_raises(self):
        with pytest.raises(ValueError, match="Parquet"):
            cli._duckdb_view_name("capture_health")


# ── _ensure_view_materialized ────────────────────────────────────────

class TestEnsureViewMaterialized:
    def test_session_usage_calls_accounting(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        args = SimpleNamespace(view="session_usage")
        cli._ensure_view_materialized(args, pr)
        rows = pr.conn.execute("SELECT count(*) FROM session_usage").fetchone()
        assert rows[0] > 0

    def test_latest_run_snapshots(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        args = SimpleNamespace(view="latest_run_snapshots")
        cli._ensure_view_materialized(args, pr)
        rows = pr.conn.execute("SELECT count(*) FROM latest_run_snapshots").fetchone()
        assert rows[0] > 0


# ── _format_and_output ───────────────────────────────────────────────

class TestFormatAndOutput:
    def test_json_output(self, capsys):
        result = {"view": "test", "rows": [{"a": 1}]}
        args = SimpleNamespace(output_format="json", view="test")
        cli._format_and_output(args, result, None, "")
        captured = capsys.readouterr()
        assert json.loads(captured.out)["view"] == "test"

    def test_table_output(self, capsys):
        result = {"view": "test", "rows": [{"col": "val"}]}
        args = SimpleNamespace(output_format="table", view="test")
        cli._format_and_output(args, result, None, "")
        captured = capsys.readouterr()
        assert "col" in captured.out
        assert "val" in captured.out

    def test_relation_format_warns(self, capsys, tmp_path):
        pr = _pi_preflight(tmp_path)
        result = {"view": "test", "rows": []}
        args = SimpleNamespace(output_format="relation", view="test")
        cli._format_and_output(args, result, pr, "")
        captured = capsys.readouterr()
        assert "programmatic use" in captured.err


# ── _persist_if_requested ────────────────────────────────────────────

class TestPersistIfRequested:
    def test_noop_without_flag(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        args = SimpleNamespace(persist=None)
        cli._persist_if_requested(args, pr)

    def test_noop_without_preflight(self, tmp_path):
        args = SimpleNamespace(persist=str(tmp_path / "out.duckdb"))
        cli._persist_if_requested(args, None)
        assert not (tmp_path / "out.duckdb").exists()

    def test_persists_to_absolute_path(self, tmp_path):
        pr = _pi_preflight(tmp_path)
        dest = tmp_path / "out.duckdb"
        args = SimpleNamespace(persist=str(dest))
        cli._persist_if_requested(args, pr)
        assert dest.exists()

    def test_persists_relative_with_project_root(self, tmp_path, monkeypatch):
        pr = _pi_preflight(tmp_path)
        (tmp_path / ".agent-factory").mkdir()
        monkeypatch.setattr(cli, "_find_project_root", lambda: tmp_path)
        args = SimpleNamespace(persist="out.duckdb")
        cli._persist_if_requested(args, pr)
        assert (tmp_path / "out.duckdb").exists()


# ── _run_preflight ───────────────────────────────────────────────────

class TestRunPreflight:
    def test_empty_paths_returns_none(self):
        assert cli._run_preflight([], "session_usage") is None

    def test_with_pi_fixture(self, tmp_path):
        dest = tmp_path / "pi_sessions.jsonl"
        shutil.copy(PI_FIXTURE, dest)
        result = cli._run_preflight([dest], "session_usage")
        assert result is not None
        assert result.valid_count > 0


# ── main (integration-level, direct import) ──────────────────────────

class TestMainDirect:
    def test_capture_health_json(self, tmp_path, capsys):
        dest = tmp_path / "pi.jsonl"
        shutil.copy(PI_FIXTURE, dest)
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["capture_health", "--usage-dir", str(tmp_path)])
        assert exc_info.value.code == 0
        data = json.loads(capsys.readouterr().out)
        assert data["view"] == "capture_health"

    def test_unknown_view_exits_2(self, tmp_path):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["bogus", "--usage-dir", str(tmp_path)])
        assert exc_info.value.code == 2

    def test_missing_dir_exits_2(self):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["capture_health", "--usage-dir", "/no/such/dir/xyz"])
        assert exc_info.value.code == 2
