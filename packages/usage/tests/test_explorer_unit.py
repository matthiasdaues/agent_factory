"""Unit tests for usage.explorer — _snapshot, _loop, _rebuild, main."""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from usage import explorer
from usage.explorer import _EvidenceWatcher


@pytest.fixture()
def quiet_watcher(monkeypatch):
    """Suppress thread start so _EvidenceWatcher can be constructed safely."""
    monkeypatch.setattr(threading.Thread, "start", lambda self: None)


# ── _snapshot ───────────────────────────────────────────────────────


class TestSnapshot:
    def test_reads_jsonl_files(self, tmp_path, quiet_watcher):
        (tmp_path / "a.jsonl").write_text("{}\n")
        (tmp_path / "b.jsonl").write_text("{}\n{}\n")
        (tmp_path / "c.txt").write_text("ignored")
        w = _EvidenceWatcher(tmp_path, tmp_path / "db.duckdb")
        snap = w._snapshot()
        assert len(snap) == 2
        assert snap[0][0] == "a.jsonl"
        assert snap[1][0] == "b.jsonl"

    def test_empty_dir(self, tmp_path, quiet_watcher):
        w = _EvidenceWatcher(tmp_path, tmp_path / "db.duckdb")
        assert w._snapshot() == ()

    def test_nonexistent_dir_returns_empty(self, quiet_watcher, tmp_path):
        w = _EvidenceWatcher(tmp_path, tmp_path / "db.duckdb")
        w.usage_dir = tmp_path / "no_such_dir"
        assert w._snapshot() == ()


# ── _loop ───────────────────────────────────────────────────────────


class TestLoop:
    def test_calls_rebuild_on_change(self, tmp_path, quiet_watcher):
        (tmp_path / "a.jsonl").write_text("{}\n")
        w = _EvidenceWatcher(tmp_path, tmp_path / "db.duckdb")
        w._rebuild = MagicMock()

        call_count = [0]

        def mock_sleep(_seconds):
            call_count[0] += 1
            if call_count[0] == 1:
                (tmp_path / "new.jsonl").write_text("{}")
            else:
                raise StopIteration("break")

        with (
            patch.object(time, "sleep", side_effect=mock_sleep),
            pytest.raises(StopIteration),
        ):
            w._loop()

        w._rebuild.assert_called_once()

    def test_no_rebuild_when_unchanged(self, tmp_path, quiet_watcher):
        (tmp_path / "a.jsonl").write_text("{}\n")
        w = _EvidenceWatcher(tmp_path, tmp_path / "db.duckdb")
        w._rebuild = MagicMock()

        call_count = [0]

        def mock_sleep(_seconds):
            call_count[0] += 1
            if call_count[0] >= 2:
                raise StopIteration("break")

        with (
            patch.object(time, "sleep", side_effect=mock_sleep),
            pytest.raises(StopIteration),
        ):
            w._loop()

        w._rebuild.assert_not_called()


# ── _rebuild ────────────────────────────────────────────────────────


class TestRebuild:
    def test_successful_rebuild(self, tmp_path, quiet_watcher):
        w = _EvidenceWatcher(tmp_path, tmp_path / "db.duckdb")
        initial_version = w.version

        mock_conn = MagicMock()
        mock_result = SimpleNamespace(conn=mock_conn)

        with (
            patch(
                "usage.input_snapshot.snapshot", return_value=([Path("a.jsonl")], "d")
            ),
            patch("usage.contract_check.main", return_value=0),
            patch("usage.preflight.run_preflight", return_value=mock_result),
            patch("usage.accounting.select_latest_snapshots"),
            patch("usage.accounting.build_session_roots"),
            patch("usage.accounting.build_session_contributions"),
            patch("usage.accounting.compute_session_usage"),
            patch("usage.persist.persist_to_duckdb"),
        ):
            w._rebuild()

        assert w.version == initial_version + 1
        mock_conn.close.assert_called_once()

    def test_empty_paths_skips(self, tmp_path, quiet_watcher):
        w = _EvidenceWatcher(tmp_path, tmp_path / "db.duckdb")
        v = w.version
        with patch("usage.input_snapshot.snapshot", return_value=([], "d")):
            w._rebuild()
        assert w.version == v

    def test_contract_check_failure_skips(self, tmp_path, quiet_watcher):
        w = _EvidenceWatcher(tmp_path, tmp_path / "db.duckdb")
        v = w.version
        with (
            patch(
                "usage.input_snapshot.snapshot", return_value=([Path("a.jsonl")], "d")
            ),
            patch("usage.contract_check.main", return_value=1),
        ):
            w._rebuild()
        assert w.version == v

    def test_exception_during_accounting(self, tmp_path, quiet_watcher):
        w = _EvidenceWatcher(tmp_path, tmp_path / "db.duckdb")
        v = w.version
        mock_conn = MagicMock()
        mock_result = SimpleNamespace(conn=mock_conn)
        with (
            patch(
                "usage.input_snapshot.snapshot", return_value=([Path("a.jsonl")], "d")
            ),
            patch("usage.contract_check.main", return_value=0),
            patch("usage.preflight.run_preflight", return_value=mock_result),
            patch(
                "usage.accounting.select_latest_snapshots",
                side_effect=RuntimeError("boom"),
            ),
        ):
            w._rebuild()
        assert w.version == v
        mock_conn.close.assert_called_once()


# ── main ────────────────────────────────────────────────────────────


class TestMain:
    def test_file_not_found(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["usage-explore", "/no/such/file.duckdb"])
        with pytest.raises(SystemExit) as exc_info:
            explorer.main()
        assert exc_info.value.code == 2

    def test_watch_dir_not_found(self, tmp_path, monkeypatch):
        db = tmp_path / "test.duckdb"
        db.touch()
        monkeypatch.setattr(
            sys,
            "argv",
            ["usage-explore", str(db), "--watch", "/no/such/dir"],
        )
        with pytest.raises(SystemExit) as exc_info:
            explorer.main()
        assert exc_info.value.code == 2

    def test_successful_startup(self, tmp_path, monkeypatch):
        db = tmp_path / "test.duckdb"
        db.touch()

        mock_server = MagicMock()
        mock_server.serve_forever.side_effect = KeyboardInterrupt

        monkeypatch.setattr(
            explorer,
            "_ThreadingHTTPServer",
            lambda addr, handler: mock_server,
        )
        monkeypatch.setattr(explorer.webbrowser, "open", lambda url: None)
        monkeypatch.setattr(sys, "argv", ["usage-explore", str(db)])

        explorer.main()

        mock_server.serve_forever.assert_called_once()
        mock_server.server_close.assert_called_once()

    def test_with_watch_dir(self, tmp_path, monkeypatch):
        db = tmp_path / "test.duckdb"
        db.touch()
        watch_dir = tmp_path / "evidence"
        watch_dir.mkdir()

        mock_server = MagicMock()
        mock_server.serve_forever.side_effect = KeyboardInterrupt

        monkeypatch.setattr(
            explorer,
            "_ThreadingHTTPServer",
            lambda addr, handler: mock_server,
        )
        monkeypatch.setattr(explorer.webbrowser, "open", lambda url: None)
        monkeypatch.setattr(threading.Thread, "start", lambda self: None)
        monkeypatch.setattr(
            sys,
            "argv",
            ["usage-explore", str(db), "--watch", str(watch_dir)],
        )

        explorer.main()

        mock_server.serve_forever.assert_called_once()
