"""Transcript chains: each transcript is stored once, each record holds its turn.

ST-0278 added the structured copy next to the plain text. BUG-0142 replaced
the copy per capture with one chain file per transcript: a capture appends
only the new bytes and records the half-open byte range of its turn.
BUG-0139 keeps the session key stable, so the records of a session share one
record file and the sequence counts up.
"""

from __future__ import annotations

import json
import os
import stat
from datetime import datetime, timezone

import pytest
from conftest import load_script

uc = load_script("usage-capture")

PROJECT_ID = "687cf46a-25f6-4e98-9c62-278612aafd9f"


def _record(record_id=None, chain=None, agent=None):
    return uc.UsageRecord(
        record_id=record_id or "placeholder",
        project_id=PROJECT_ID,
        project_name="Test",
        normalized_input=100,
        normalized_output=50,
        session_id="sess-1",
        agent=agent,
        chain=chain,
    )


def _capture(tmp_path, text, source_bytes=None, *, chain="main", retention="full"):
    """Run one capture of session sess-1 the way `_capture` does."""
    storage = uc.UsageStoragePaths(tmp_path, cli="claude-code")
    reservation = storage.reserve_transcript("sess-1", None, chain)
    record = _record(reservation.record_id)
    source = None
    if source_bytes is not None:
        source = tmp_path / f"source-{reservation.record_id}.jsonl"
        source.write_bytes(source_bytes)
    adapter = uc.JsonlLoggingAdapter(tmp_path, retention=retention, cli="claude-code")
    assert adapter.record_reserved(record, text, reservation, source_transcript=source)
    return record.to_dict()


def _records(tmp_path):
    files = sorted((tmp_path / ".agent-factory" / "usage").glob("*.jsonl"))
    return files, [
        json.loads(line) for path in files for line in path.read_text().splitlines()
    ]


def _slice(ref, *, structured=False):
    path = ref["structured_path"] if structured else ref["path"]
    span = ref["structured_byte_range"] if structured else ref["byte_range"]
    with open(path, "rb") as handle:
        return handle.read()[span["start"] : span["end"]]


class TestStableSessionKey:
    def test_BUG_0139_captures_at_different_times_share_one_record_file(
        self, tmp_path, monkeypatch
    ):
        clock = [datetime(2026, 10, 16, 12, 45, 11, tzinfo=timezone.utc)]

        class FakeDatetime(datetime):
            @classmethod
            def now(cls, tz=None):
                return clock[0]

        monkeypatch.setattr(uc, "datetime", FakeDatetime)
        _capture(tmp_path, "first")
        clock[0] = datetime(2026, 10, 16, 13, 1, 33, tzinfo=timezone.utc)
        _capture(tmp_path, "first second")

        files, records = _records(tmp_path)
        assert [path.name for path in files] == [
            "2026-10-16T12-45-11_claude-code_sess-1.jsonl"
        ]
        assert [record["record_id"] for record in records] == [
            "sess-1-0001",
            "sess-1-0002",
        ]

    def test_session_key_of_another_cli_is_not_reused(self, tmp_path):
        copilot = uc.UsageStoragePaths(tmp_path, cli="copilot")
        copilot.ensure_layout()
        copilot.session_path("sess-1").write_text("")
        claude = uc.UsageStoragePaths(tmp_path, cli="claude-code")
        assert "claude-code_sess-1" in claude._session_key("sess-1")


class TestTurnSpans:
    def test_growing_transcript_is_stored_once_with_gapless_spans(self, tmp_path):
        snapshots = ["one\n", "one\ntwo\n", "one\ntwo\nthree\n"]
        refs = [_capture(tmp_path, text)["transcript_ref"] for text in snapshots]

        assert len({ref["path"] for ref in refs}) == 1
        chain_file = refs[0]["path"]
        with open(chain_file, encoding="utf-8") as handle:
            assert handle.read() == snapshots[-1]
        assert [ref["byte_range"] for ref in refs] == [
            {"start": 0, "end": 4},
            {"start": 4, "end": 8},
            {"start": 8, "end": 14},
        ]
        assert [_slice(ref) for ref in refs] == [b"one\n", b"two\n", b"three\n"]
        transcript_dir = os.path.dirname(chain_file)
        assert sorted(os.listdir(transcript_dir)) == [".lock", "main.jsonl"]

    def test_structured_copy_has_its_own_span(self, tmp_path):
        first = b'{"a": 1}\n'
        second = first + b'{"b": 2}\n'
        _capture(tmp_path, "x", first)
        ref = _capture(tmp_path, "x y", second)["transcript_ref"]

        assert ref["structured_path"].endswith("main.structured.jsonl")
        assert ref["structured_byte_range"] == {"start": len(first), "end": len(second)}
        assert _slice(ref, structured=True) == b'{"b": 2}\n'
        with open(ref["structured_path"], "rb") as handle:
            assert handle.read() == second

    def test_rewritten_transcript_starts_a_new_generation(self, tmp_path):
        _capture(tmp_path, "one\ntwo\n")
        ref = _capture(tmp_path, "summary\n")["transcript_ref"]

        assert ref["path"].endswith("main.2.jsonl")
        assert ref["byte_range"] == {"start": 0, "end": 8}
        next_ref = _capture(tmp_path, "summary\nmore\n")["transcript_ref"]
        assert next_ref["path"] == ref["path"]
        assert next_ref["byte_range"] == {"start": 8, "end": 13}

    def test_crashed_tail_is_cut_off_before_the_append(self, tmp_path):
        ref = _capture(tmp_path, "one\n")["transcript_ref"]
        with open(ref["path"], "ab") as handle:
            handle.write(b"half a turn")
        next_ref = _capture(tmp_path, "one\ntwo\n")["transcript_ref"]

        assert next_ref["byte_range"] == {"start": 4, "end": 8}
        with open(ref["path"], encoding="utf-8") as handle:
            assert handle.read() == "one\ntwo\n"

    def test_late_capture_writes_nothing_and_points_into_the_file(self, tmp_path):
        _capture(tmp_path, "one\n")
        _capture(tmp_path, "one\ntwo\nthree\n")
        late = _capture(tmp_path, "one\ntwo\n")["transcript_ref"]

        assert late["byte_range"] == {"start": 4, "end": 8}
        with open(late["path"], encoding="utf-8") as handle:
            assert handle.read() == "one\ntwo\nthree\n"

    def test_chains_of_one_session_have_separate_files(self, tmp_path):
        main = _capture(tmp_path, "root\n", chain="sess-1")
        child = _capture(tmp_path, "child\n", chain="agent-abc")

        assert main["chain"] == "sess-1"
        assert child["chain"] == "agent-abc"
        assert main["transcript_ref"]["path"] != child["transcript_ref"]["path"]
        assert child["transcript_ref"]["byte_range"] == {"start": 0, "end": 6}

    def test_empty_text_stores_nothing(self, tmp_path):
        ref = _capture(tmp_path, "")["transcript_ref"]

        assert ref["byte_range"] is None
        assert not os.path.exists(ref["path"])

    def test_chain_files_are_private(self, tmp_path):
        ref = _capture(tmp_path, "one\n", b"{}\n")["transcript_ref"]

        assert stat.S_IMODE(os.stat(ref["path"]).st_mode) == 0o600
        assert stat.S_IMODE(os.stat(ref["structured_path"]).st_mode) == 0o600


class TestConcurrentCaptures:
    def test_parallel_captures_get_unique_sequences_and_one_file(self, tmp_path):
        from concurrent.futures import ThreadPoolExecutor

        snapshots = ["".join(f"turn {n}\n" for n in range(k + 1)) for k in range(8)]
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda text: _capture(tmp_path, text), snapshots))

        _, records = _records(tmp_path)
        assert sorted(record["record_id"] for record in records) == [
            f"sess-1-{n:04d}" for n in range(1, 9)
        ]
        path = results[0]["transcript_ref"]["path"]
        with open(path, encoding="utf-8") as handle:
            assert handle.read() == snapshots[-1]
        for text, result in zip(snapshots, results):
            assert result["transcript_ref"]["byte_range"]["end"] == len(text)


class TestRetentionAndSafety:
    def test_omit_writes_no_chain_file(self, tmp_path):
        ref = _capture(tmp_path, "secret", b"{}\n", retention="omit")["transcript_ref"]

        assert ref["span"] == "content-omitted"
        assert ref["byte_range"] is None
        assert ref["structured_path"] is None
        assert not os.path.exists(ref["path"])

    @pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks not available")
    def test_symlink_source_is_not_followed(self, tmp_path):
        real = tmp_path / "real.jsonl"
        real.write_bytes(b"{}\n")
        link = tmp_path / "link.jsonl"
        os.symlink(real, link)
        storage = uc.UsageStoragePaths(tmp_path)
        reservation = storage.reserve_transcript("sess-1", None, "main")
        record = _record(reservation.record_id)
        adapter = uc.JsonlLoggingAdapter(tmp_path, retention="full")

        assert adapter.record_reserved(record, "text", reservation, source_transcript=link)
        assert record.transcript_ref.structured_path is None

    def test_discard_releases_the_session_lock(self, tmp_path):
        storage = uc.UsageStoragePaths(tmp_path)
        first = storage.reserve_transcript("sess-1", None, "main")
        first.discard()
        second = uc.UsageStoragePaths(tmp_path).reserve_transcript("sess-1", None, "main")
        assert second.record_id == "sess-1-0001"
        second.discard()
