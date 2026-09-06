"""Contract tests for usage-capture: filesystem_key, UsageStoragePaths, UsageRecord."""

from __future__ import annotations

import re

import pytest
from conftest import load_script

uc = load_script("usage-capture")


# ---------------------------------------------------------------------------
# filesystem_key — safe vs hostile identifiers
# ---------------------------------------------------------------------------


class TestFilesystemKey:
    """One safe component or an opaque digest — never a path escape."""

    def test_simple_alphanumeric_passes_through(self):
        assert uc.filesystem_key("abc-123") == "abc-123"

    def test_mixed_case_with_iso_separators_passes_through(self):
        key = "2026-08-04T07-40-23-289Z_019fcbb7"
        assert uc.filesystem_key(key) == key

    @pytest.mark.parametrize(
        "hostile",
        [
            "../../escaped",
            "/tmp/absolute",
            "slash/name",
            "backslash\\name",
            "CON",
            "café",
        ],
    )
    def test_hostile_inputs_produce_opaque_digest(self, hostile):
        result = uc.filesystem_key(hostile)
        assert result.startswith("opaque-")
        assert "/" not in result and "\\" not in result

    def test_opaque_prefix_input_is_itself_digested(self):
        result = uc.filesystem_key("opaque-deadbeef")
        assert result.startswith("opaque-")
        assert result != "opaque-deadbeef"


# ---------------------------------------------------------------------------
# UsageStoragePaths — layout with timestamp prefix
# ---------------------------------------------------------------------------


class TestUsageStoragePaths:
    """Session key includes timestamp prefix; paths stay under usage root."""

    _TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}_")

    def test_session_key_has_timestamp_prefix(self, tmp_path):
        sp = uc.UsageStoragePaths(tmp_path)
        key = sp._session_key("sess-1")
        assert self._TS_RE.match(key), f"key lacks timestamp prefix: {key}"

    def test_session_key_includes_cli_when_set(self, tmp_path):
        sp = uc.UsageStoragePaths(tmp_path, cli="claude-code")
        key = sp._session_key("sess-1")
        assert "claude-code" in key
        assert "sess-1" in key

    def test_session_path_under_usage_dir(self, tmp_path):
        sp = uc.UsageStoragePaths(tmp_path)
        path = sp.session_path("sess-1")
        assert path.parent == sp.usage_dir
        assert path.suffix == ".jsonl"

    def test_transcript_path_under_transcripts_dir(self, tmp_path):
        sp = uc.UsageStoragePaths(tmp_path)
        path = sp.transcript_path("sess-1", "rec-1")
        assert sp.transcripts_dir in path.parents

    def test_ensure_layout_creates_directories(self, tmp_path):
        sp = uc.UsageStoragePaths(tmp_path)
        sp.ensure_layout()
        assert sp.agent_dir.is_dir()
        assert sp.usage_dir.is_dir()
        assert sp.transcripts_dir.is_dir()


# ---------------------------------------------------------------------------
# UsageRecord — field defaults and serialization
# ---------------------------------------------------------------------------


class TestUsageRecord:
    def _make_record(self, **overrides):
        defaults = {
            "record_id": "rec-001",
            "project_id": "687cf46a-25f6-4e98-9c62-278612aafd9f",
            "project_name": "Test",
            "normalized_input": 100,
            "normalized_output": 50,
        }
        return uc.UsageRecord(**{**defaults, **overrides})

    def test_normalized_total_is_derived(self):
        rec = self._make_record()
        assert rec.normalized_total == 150

    def test_to_dict_round_trips_through_json(self):
        import json

        rec = self._make_record()
        text = json.dumps(rec.to_dict())
        parsed = json.loads(text)
        assert parsed["project_id"] == "687cf46a-25f6-4e98-9c62-278612aafd9f"
        assert parsed["normalized_total"] == 150
