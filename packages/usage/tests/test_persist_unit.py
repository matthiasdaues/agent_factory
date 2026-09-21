"""Unit tests for usage.persist — persist_to_duckdb."""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pytest

from usage.persist import persist_to_duckdb, _escape_path


class TestEscapePath:
    def test_plain(self):
        assert _escape_path(Path("/tmp/foo.duckdb")) == "/tmp/foo.duckdb"

    def test_single_quote(self):
        assert _escape_path(Path("/tmp/it's.duckdb")) == "/tmp/it''s.duckdb"


class TestPersistToDuckdb:
    def _conn_with_table(self):
        conn = duckdb.connect(":memory:")
        conn.execute("CREATE TABLE items (id INTEGER, name VARCHAR)")
        conn.execute("INSERT INTO items VALUES (1, 'a'), (2, 'b')")
        return conn

    def test_basic_export(self, tmp_path):
        conn = self._conn_with_table()
        dest = tmp_path / "out.duckdb"
        count = persist_to_duckdb(conn, dest)
        assert count == 1
        assert dest.exists()
        check = duckdb.connect(str(dest), read_only=True)
        rows = check.execute("SELECT * FROM items ORDER BY id").fetchall()
        check.close()
        assert rows == [(1, "a"), (2, "b")]
        conn.close()

    def test_exclude_columns(self, tmp_path):
        conn = duckdb.connect(":memory:")
        conn.execute(
            "CREATE TABLE latest_run_snapshots "
            "(id INTEGER, _snapshot_rank INTEGER, val VARCHAR)"
        )
        conn.execute("INSERT INTO latest_run_snapshots VALUES (1, 99, 'x')")
        dest = tmp_path / "out.duckdb"
        persist_to_duckdb(conn, dest)
        check = duckdb.connect(str(dest), read_only=True)
        cols = [
            r[0]
            for r in check.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'latest_run_snapshots'"
            ).fetchall()
        ]
        check.close()
        assert "_snapshot_rank" not in cols
        assert "id" in cols
        conn.close()

    def test_skips_underscore_tables(self, tmp_path):
        conn = duckdb.connect(":memory:")
        conn.execute("CREATE TABLE _internal (x INTEGER)")
        conn.execute("CREATE TABLE public_tbl (y INTEGER)")
        conn.execute("INSERT INTO public_tbl VALUES (1)")
        dest = tmp_path / "out.duckdb"
        count = persist_to_duckdb(conn, dest)
        assert count == 1
        check = duckdb.connect(str(dest), read_only=True)
        tables = [
            r[0] for r in check.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'main'"
            ).fetchall()
        ]
        check.close()
        assert "_internal" not in tables
        assert "public_tbl" in tables
        conn.close()

    def test_creates_parent_dirs(self, tmp_path):
        conn = self._conn_with_table()
        dest = tmp_path / "sub" / "dir" / "out.duckdb"
        count = persist_to_duckdb(conn, dest)
        assert count == 1
        assert dest.exists()
        conn.close()

    def test_cleanup_on_error(self, tmp_path, monkeypatch):
        conn = self._conn_with_table()
        dest = tmp_path / "out.duckdb"

        def bad_replace(src, dst):
            raise OSError("injected")

        monkeypatch.setattr(os, "replace", bad_replace)
        with pytest.raises(OSError, match="injected"):
            persist_to_duckdb(conn, dest)
        assert not any(f.suffix == ".tmp" for f in tmp_path.iterdir())
        conn.close()
