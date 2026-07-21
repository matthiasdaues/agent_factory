"""Tests for `factory/scripts/usage-capture` (ST-0035 foundation slice).

This file is grown by later stories (ST-0036 JSONL adapter, ST-0037
normalizer, ST-0038 CLI entrypoint); ST-0035 covers only the usage record
shape, the `record_id` scheme, and the cl100k_base tokenizer.

The script is extensionless and, like `openrouter-discover`/`resolve-model`,
loaded via importlib for the record/record_id tests, which touch no
third-party dependency. The tokenizer itself needs `tiktoken`, which the
script's own PEP 723 shebang (`uv run --script`) bootstraps but a bare test
interpreter (this suite runs under plain `uvx pytest`) does not have —
`import tiktoken` is therefore lazy inside `count_tokens()`, never at module
scope, so importing the module for the record tests never requires it.

The tokenizer's own tests exercise it by invoking the script as a
subprocess through its own shebang (`subprocess.run([str(_SCRIPT), ...])`),
the same pattern `test_research_playbook_ST0033.py` already uses to get a
real, non-fallback `tiktoken` count out of `index-lint` from a bare
interpreter.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import subprocess
import sys
import uuid
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "usage-capture"

_loader = SourceFileLoader("usage_capture", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("usage_capture", _loader)
usage_capture = importlib.util.module_from_spec(_spec)
sys.modules["usage_capture"] = usage_capture
_loader.exec_module(usage_capture)


# ── Tokenizer ────────────────────────────────────────────────────────────


def _count_via_subprocess(text: str) -> int:
    """Run the script's own shebang so tiktoken is really bootstrapped.

    Plain `uvx pytest` (the mandated test runner for this suite) has no
    tiktoken in its own interpreter; `uv run --script` (the script's
    shebang) does. Going through the executable, not the imported module,
    is what makes the assertion below a real cl100k_base count rather than
    a stub.
    """
    result = subprocess.run(
        [str(_SCRIPT), "--count-tokens"],
        input=text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return int(result.stdout.strip())


class TestTokenizer:
    def test_known_fixture_has_exact_count(self):
        # cl100k_base encodes "Hello, world!" as 4 tokens: [9906, 11, 1917, 0]
        assert _count_via_subprocess("Hello, world!") == 4

    def test_second_known_fixture_has_exact_count(self):
        text = "The quick brown fox jumps over the lazy dog."
        assert _count_via_subprocess(text) == 10

    def test_same_input_yields_same_count(self):
        text = "deterministic, local, no network, no LLM call"
        first = _count_via_subprocess(text)
        second = _count_via_subprocess(text)
        assert first == second

    def test_count_tokens_importable_without_tiktoken_at_module_scope(self):
        """Importing the module must not itself require tiktoken.

        Guards the design: `import tiktoken` lives inside `count_tokens()`,
        not at module scope, so the record/record_id half of this file
        stays importable (and testable) under a bare interpreter.
        """
        assert callable(usage_capture.count_tokens)


# ── UsageRecord ──────────────────────────────────────────────────────────

_ALL_FIELDS = {
    # correlation
    "cli",
    "session_id",
    "parent_session_id",
    "depth",
    "run_start",
    "run_end",
    # loop
    "loop_id",
    "loop_role",
    "iteration",
    # what-ran
    "agent",
    "skill",
    "phase",
    "playbook",
    "story_id",
    "model",
    # spend
    "normalized_input",
    "normalized_output",
    "normalized_total",
    "reported_input",
    "reported_output",
    "reported_cache_read",
    "reported_cache_write",
    "usage_granularity",
    # outcome
    "exit_status",
    "branch",
    "base_commit",
    "commit_id",
    "transcript_ref",
}

_NULLABLE_BY_DEFAULT = _ALL_FIELDS - {
    "normalized_input",
    "normalized_output",
    "normalized_total",
}


class TestUsageRecordFieldPresence:
    def test_every_proposal_field_is_present(self):
        record = usage_capture.UsageRecord(
            record_id="sess-0001", normalized_input=3, normalized_output=5
        )
        field_names = {f.name for f in dataclasses.fields(record)}
        missing = _ALL_FIELDS - field_names
        assert not missing, f"UsageRecord is missing fields: {missing}"

    def test_record_id_is_also_present(self):
        record = usage_capture.UsageRecord(
            record_id="sess-0001", normalized_input=1, normalized_output=1
        )
        assert record.record_id == "sess-0001"


class TestNullability:
    def test_reported_and_nullable_fields_default_to_none(self):
        record = usage_capture.UsageRecord(
            record_id="sess-0001", normalized_input=1, normalized_output=2
        )
        for name in _NULLABLE_BY_DEFAULT:
            assert getattr(record, name) is None, f"{name} did not default to None"

    def test_normalized_fields_are_never_null(self):
        record = usage_capture.UsageRecord(
            record_id="sess-0001", normalized_input=0, normalized_output=0
        )
        assert record.normalized_input is not None
        assert record.normalized_output is not None
        assert record.normalized_total is not None

    def test_supplied_nullable_field_overrides_default(self):
        record = usage_capture.UsageRecord(
            record_id="sess-0001",
            normalized_input=1,
            normalized_output=1,
            cli="claude-code",
            loop_role="review",
        )
        assert record.cli == "claude-code"
        assert record.loop_role == "review"


class TestNormalizedTotalInvariant:
    def test_total_equals_input_plus_output(self):
        record = usage_capture.UsageRecord(
            record_id="sess-0001", normalized_input=120, normalized_output=45
        )
        assert record.normalized_total == 165

    def test_total_is_derived_not_settable_out_of_sync(self):
        """normalized_total is computed, not caller-supplied — the invariant
        cannot be violated by construction, only by never being asked for."""
        record = usage_capture.UsageRecord(
            record_id="sess-0001", normalized_input=7, normalized_output=3
        )
        assert (
            record.normalized_total
            == record.normalized_input + record.normalized_output
        )


class TestToDict:
    def test_to_dict_is_json_ready(self):
        record = usage_capture.UsageRecord(
            record_id="sess-0001",
            normalized_input=10,
            normalized_output=2,
            transcript_ref=usage_capture.TranscriptRef(path="/tmp/t.jsonl"),
        )
        payload = record.to_dict()
        assert payload["normalized_total"] == 12
        assert payload["transcript_ref"] == {"path": "/tmp/t.jsonl", "span": None}
        assert payload["cli"] is None


# ── record_id ────────────────────────────────────────────────────────────


class TestRecordIdSequencer:
    def test_same_session_increments_sequence(self):
        seq = usage_capture.RecordIdSequencer()
        first = seq.next_id("sess-abc")
        second = seq.next_id("sess-abc")
        third = seq.next_id("sess-abc")
        assert [first, second, third] == [
            "sess-abc-0001",
            "sess-abc-0002",
            "sess-abc-0003",
        ]

    def test_different_sessions_have_independent_sequences(self):
        seq = usage_capture.RecordIdSequencer()
        seq.next_id("sess-a")
        seq.next_id("sess-a")
        first_b = seq.next_id("sess-b")
        assert first_b == "sess-b-0001"

    def test_missing_session_id_falls_back_to_uuid(self):
        seq = usage_capture.RecordIdSequencer()
        record_id = seq.next_id(None)
        # Falls back to a real UUID4 string, not a session-sequence id.
        assert uuid.UUID(record_id).version == 4

    def test_empty_session_id_falls_back_to_uuid(self):
        seq = usage_capture.RecordIdSequencer()
        record_id = seq.next_id("")
        assert uuid.UUID(record_id).version == 4

    def test_uuid_fallback_is_unique_per_call(self):
        seq = usage_capture.RecordIdSequencer()
        assert seq.next_id(None) != seq.next_id(None)
