"""Integration tests for ST-0247 — result format adapters."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from usage import adapters
from usage.preflight import run_preflight
from usage.views.session_usage import session_usage

_HAS_PYARROW = True
try:
    import pyarrow  # noqa: F401
except ImportError:
    _HAS_PYARROW = False


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "from usage.cli import main; main()", *args],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture()
def pi_dir(tmp_path: Path) -> Path:
    import shutil

    src = (
        Path(__file__).resolve().parent.parent.parent
        / "fixtures"
        / "multi-cli"
        / "pi_sessions.jsonl"
    )
    shutil.copy(src, tmp_path / "pi.jsonl")
    return tmp_path


# ---------------------------------------------------------------------------
# Format validation
# ---------------------------------------------------------------------------


class TestFormatValidation:
    def test_pandas_rejected(self) -> None:
        assert adapters.validate_format("pandas") is not None

    def test_polars_rejected(self) -> None:
        assert adapters.validate_format("polars") is not None

    def test_unknown_rejected(self) -> None:
        assert adapters.validate_format("csv") is not None

    def test_json_accepted(self) -> None:
        assert adapters.validate_format("json") is None

    def test_table_accepted(self) -> None:
        assert adapters.validate_format("table") is None

    def test_relation_accepted(self) -> None:
        assert adapters.validate_format("relation") is None

    def test_arrow_accepted(self) -> None:
        assert adapters.validate_format("arrow") is None


# ---------------------------------------------------------------------------
# CLI --format flag
# ---------------------------------------------------------------------------


class TestCliFormat:
    def test_json_output(self, pi_dir: Path) -> None:
        r = _run_cli("session_usage", "--usage-dir", str(pi_dir), "--format", "json")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["view"] == "session_usage"

    def test_table_output(self, pi_dir: Path) -> None:
        r = _run_cli("session_usage", "--usage-dir", str(pi_dir), "--format", "table")
        assert r.returncode == 0
        assert "session_id" in r.stdout
        assert "sess-pi-root" in r.stdout
        assert "(1 row)" in r.stdout

    def test_pandas_rejected_exit_2(self, pi_dir: Path) -> None:
        r = _run_cli("session_usage", "--usage-dir", str(pi_dir), "--format", "pandas")
        assert r.returncode == 2
        assert "unsupported" in r.stderr.lower()

    def test_polars_rejected_exit_2(self, pi_dir: Path) -> None:
        r = _run_cli("session_usage", "--usage-dir", str(pi_dir), "--format", "polars")
        assert r.returncode == 2
        assert "unsupported" in r.stderr.lower()

    def test_default_format_is_json(self, pi_dir: Path) -> None:
        r = _run_cli("session_usage", "--usage-dir", str(pi_dir))
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "view" in data


# ---------------------------------------------------------------------------
# JSON adapter preserves types and nulls
# ---------------------------------------------------------------------------


class TestJsonAdapter:
    def test_preserves_null(self) -> None:
        result = {"view": "test", "rows": [{"a": 1, "b": None}]}
        output = adapters.to_json(result)
        parsed = json.loads(output)
        assert parsed["rows"][0]["b"] is None

    def test_preserves_types(self) -> None:
        result = {"view": "test", "rows": [{"i": 42, "f": 1.5, "s": "x"}]}
        output = adapters.to_json(result)
        parsed = json.loads(output)
        row = parsed["rows"][0]
        assert isinstance(row["i"], int)
        assert isinstance(row["f"], float)
        assert isinstance(row["s"], str)


# ---------------------------------------------------------------------------
# Table adapter preserves nulls
# ---------------------------------------------------------------------------


class TestTableAdapter:
    def test_null_shows_as_null(self) -> None:
        result = {"view": "test", "rows": [{"a": 1, "b": None}]}
        output = adapters.to_table(result)
        assert "NULL" in output

    def test_empty_rows(self) -> None:
        result = {"view": "test", "rows": []}
        output = adapters.to_table(result)
        assert "0 rows" in output


# ---------------------------------------------------------------------------
# Relation adapter
# ---------------------------------------------------------------------------


class TestRelationAdapter:
    def test_returns_duckdb_relation(self, pi_dir: Path) -> None:
        import duckdb

        paths = sorted(pi_dir.glob("*.jsonl"))
        pf = run_preflight(paths)
        session_usage(pf)
        rel = adapters.to_relation(pf.conn, "session_usage")
        assert isinstance(rel, duckdb.DuckDBPyRelation)
        rows = rel.fetchall()
        assert len(rows) == 1
        assert rows[0][1] == "pi"


# ---------------------------------------------------------------------------
# Arrow adapter
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _HAS_PYARROW, reason="pyarrow not installed")
class TestArrowAdapter:
    def test_returns_pyarrow_table(self, pi_dir: Path) -> None:
        import pyarrow

        paths = sorted(pi_dir.glob("*.jsonl"))
        pf = run_preflight(paths)
        session_usage(pf)
        tbl = adapters.to_arrow(pf.conn, "session_usage")
        assert isinstance(tbl, pyarrow.Table)
        assert tbl.num_rows == 1
        assert "session_id" in tbl.schema.names
        assert "normalized_total" in tbl.schema.names

    def test_preserves_null(self, tmp_path: Path) -> None:
        rec = {
            "record_id": "r1",
            "project_id": "proj-test",
            "project_name": "test",
            "normalized_input": 100,
            "normalized_output": 50,
            "normalized_total": 150,
            "cli": "pi",
            "session_id": "s1",
            "parent_session_id": None,
            "depth": 0,
            "recorded_at": "2026-01-15T10:00:00Z",
            "agent": "a",
            "model": "m",
            "provider": "p",
            "reported_input": 10,
            "reported_output": 5,
            "reported_cache_read": None,
            "reported_cache_write": None,
            "usage_granularity": "turn",
            "usage_capability": "full",
            "cache_miss_turns": None,
            "cache_miss_input_tokens": None,
            "late_early_input_ratio": None,
            "exit_status": "success",
            "branch": "main",
            "commit_id": "x",
            "transcript_ref": {"path": "/t.jsonl", "span": "0:100"},
        }
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps(rec) + "\n")
        pf = run_preflight([f])
        from usage.views.cache_efficiency import cache_efficiency

        cache_efficiency(pf)
        tbl = adapters.to_arrow(pf.conn, "session_contributions")
        col = tbl.column("reported_cache_read")
        assert col[0].as_py() is None

    def test_arrow_import_error_without_pyarrow(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Factory capture isolation
# ---------------------------------------------------------------------------


class TestCaptureIsolation:
    def test_factory_capture_does_not_import_duckdb(self) -> None:
        capture_script = (
            Path(__file__).resolve().parent.parent.parent.parent.parent
            / "factory"
            / "scripts"
            / "usage-capture"
        )
        if not capture_script.exists():
            pytest.skip("usage-capture script not found")
        content = capture_script.read_text()
        assert "import duckdb" not in content
        assert "import pyarrow" not in content
