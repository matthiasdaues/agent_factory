"""ST-0278: structured JSONL copy alongside text rendering at capture time."""

from __future__ import annotations

import json
import os
import stat

import pytest
from conftest import load_script

uc = load_script("usage-capture")


def _make_source_transcript(path, content=None):
    """Write a realistic source transcript and return its bytes."""
    if content is None:
        content = (
            json.dumps(
                {"type": "init", "message": {"role": "system", "content": "hello"}}
            )
            + "\n"
            + json.dumps(
                {
                    "type": "msg",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "world"}],
                    },
                }
            )
            + "\n"
        )
    raw = content.encode("utf-8")
    path.write_bytes(raw)
    return raw


def _make_record(record_id="rec-001"):
    return uc.UsageRecord(
        record_id=record_id,
        project_id="687cf46a-25f6-4e98-9c62-278612aafd9f",
        project_name="Test",
        normalized_input=100,
        normalized_output=50,
        session_id="sess-1",
    )


class TestStructuredTranscriptFull:
    """When retention=full, .structured.jsonl exists alongside text rendering."""

    def test_structured_file_exists_alongside_text(self, tmp_path):
        source = tmp_path / "source.jsonl"
        _make_source_transcript(source)

        storage = uc.UsageStoragePaths(tmp_path)
        storage.ensure_layout()
        reservation = storage.reserve_transcript("sess-1", "rec-001")
        assert reservation.structured_path is not None
        assert reservation.structured_path.name == "rec-001.structured.jsonl"
        assert reservation.structured_path.parent == reservation.path.parent

        adapter = uc.JsonlLoggingAdapter(tmp_path, retention="full")
        record = _make_record()
        ok = adapter.record_reserved(
            record,
            "normalized text",
            reservation,
            source_transcript=source,
        )
        assert ok is True
        assert reservation.structured_path.exists()

    def test_structured_content_is_byte_identical_to_source(self, tmp_path):
        source = tmp_path / "source.jsonl"
        source_bytes = _make_source_transcript(source)

        storage = uc.UsageStoragePaths(tmp_path)
        storage.ensure_layout()
        reservation = storage.reserve_transcript("sess-1", "rec-001")
        adapter = uc.JsonlLoggingAdapter(tmp_path, retention="full")
        record = _make_record()
        adapter.record_reserved(
            record,
            "normalized text",
            reservation,
            source_transcript=source,
        )
        assert reservation.structured_path.read_bytes() == source_bytes

    def test_text_rendering_contains_normalized_text(self, tmp_path):
        source = tmp_path / "source.jsonl"
        _make_source_transcript(source)

        storage = uc.UsageStoragePaths(tmp_path)
        storage.ensure_layout()
        reservation = storage.reserve_transcript("sess-1", "rec-001")
        text_path = reservation.path
        adapter = uc.JsonlLoggingAdapter(tmp_path, retention="full")
        record = _make_record()
        adapter.record_reserved(
            record,
            "normalized text here",
            reservation,
            source_transcript=source,
        )
        assert text_path.read_text(encoding="utf-8") == "normalized text here"

    def test_structured_copy_without_source_skips_silently(self, tmp_path):
        """No source_transcript provided -- structured file stays empty."""
        storage = uc.UsageStoragePaths(tmp_path)
        storage.ensure_layout()
        reservation = storage.reserve_transcript("sess-1", "rec-001")
        adapter = uc.JsonlLoggingAdapter(tmp_path, retention="full")
        record = _make_record()
        ok = adapter.record_reserved(record, "text", reservation)
        assert ok is True
        # structured file exists (reserved) but empty -- no source to copy
        assert reservation.structured_path.exists()
        assert reservation.structured_path.stat().st_size == 0


class TestStructuredTranscriptOmit:
    """When retention=omit, neither file is written."""

    def test_structured_file_removed_on_omit(self, tmp_path):
        source = tmp_path / "source.jsonl"
        _make_source_transcript(source)

        storage = uc.UsageStoragePaths(tmp_path)
        storage.ensure_layout()
        reservation = storage.reserve_transcript("sess-1", "rec-001")
        structured = reservation.structured_path
        adapter = uc.JsonlLoggingAdapter(tmp_path, retention="omit")
        record = _make_record()
        ok = adapter.record_reserved(
            record,
            "text",
            reservation,
            source_transcript=source,
        )
        assert ok is True
        assert not structured.exists()

    def test_text_rendering_empty_on_omit(self, tmp_path):
        source = tmp_path / "source.jsonl"
        _make_source_transcript(source)

        storage = uc.UsageStoragePaths(tmp_path)
        storage.ensure_layout()
        reservation = storage.reserve_transcript("sess-1", "rec-001")
        text_path = reservation.path
        adapter = uc.JsonlLoggingAdapter(tmp_path, retention="omit")
        record = _make_record()
        adapter.record_reserved(
            record,
            "text",
            reservation,
            source_transcript=source,
        )
        assert text_path.read_text(encoding="utf-8") == ""


class TestStructuredTranscriptSafety:
    """Filesystem safety measures on the structured copy."""

    @pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks not available")
    def test_symlink_source_is_rejected(self, tmp_path):
        """Source transcript that is a symlink must not be followed."""
        real = tmp_path / "real.jsonl"
        _make_source_transcript(real)
        link = tmp_path / "link.jsonl"
        os.symlink(real, link)

        storage = uc.UsageStoragePaths(tmp_path)
        storage.ensure_layout()
        reservation = storage.reserve_transcript("sess-1", "rec-001")
        adapter = uc.JsonlLoggingAdapter(tmp_path, retention="full")
        record = _make_record()
        # Should succeed overall (best-effort) but structured copy fails
        ok = adapter.record_reserved(
            record,
            "text",
            reservation,
            source_transcript=link,
        )
        assert ok is True
        # Structured file exists but is empty (copy failed, logged to stderr)
        assert reservation.structured_path.stat().st_size == 0

    def test_reservation_structured_path_has_correct_mode(self, tmp_path):
        storage = uc.UsageStoragePaths(tmp_path)
        storage.ensure_layout()
        reservation = storage.reserve_transcript("sess-1", "rec-001")
        # Close the fd so we can stat the file
        if reservation.structured_fd >= 0:
            os.close(reservation.structured_fd)
            reservation.structured_fd = -1
        mode = reservation.structured_path.stat().st_mode
        assert stat.S_IMODE(mode) == 0o600

    def test_discard_removes_both_files(self, tmp_path):
        storage = uc.UsageStoragePaths(tmp_path)
        storage.ensure_layout()
        reservation = storage.reserve_transcript("sess-1", "rec-001")
        text_path = reservation.path
        structured_path = reservation.structured_path
        assert text_path.exists()
        assert structured_path.exists()
        reservation.discard()
        assert not text_path.exists()
        assert not structured_path.exists()
