"""Tests for `factory/scripts/usage-capture` (ST-0035, ST-0036).

This file is grown by later stories (ST-0037 normalizer, ST-0038 CLI
entrypoint); ST-0035 covers the usage record shape, the `record_id` scheme,
and the cl100k_base tokenizer. ST-0036 adds the `LoggingAdapter` seam and
its `JsonlLoggingAdapter` implementation: append-one-line-per-record,
transcript-copy persistence, concurrent-append safety, and the best-effort
failure contract.

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

import concurrent.futures
import dataclasses
import importlib.util
import json
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


# ── LoggingAdapter / JsonlLoggingAdapter (ST-0036) ──────────────────────


def _make_record(record_id: str, session_id: str) -> "usage_capture.UsageRecord":
    return usage_capture.UsageRecord(
        record_id=record_id,
        normalized_input=1,
        normalized_output=1,
        session_id=session_id,
    )


class TestJsonlLoggingAdapterAppendsRecords:
    def test_appends_one_record_line_to_session_file(self, tmp_path):
        adapter = usage_capture.JsonlLoggingAdapter(base_dir=tmp_path)
        record = _make_record("sess-1-0001", "sess-1")

        adapter.record(record, "transcript text")

        session_file = tmp_path / ".agent-factory" / "usage" / "sess-1.jsonl"
        lines = session_file.read_text().splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0])["record_id"] == "sess-1-0001"

    def test_creates_usage_directory_on_demand(self, tmp_path):
        adapter = usage_capture.JsonlLoggingAdapter(base_dir=tmp_path)
        assert not (tmp_path / ".agent-factory").exists()

        adapter.record(_make_record("sess-2-0001", "sess-2"), "x")

        assert (tmp_path / ".agent-factory" / "usage" / "sess-2.jsonl").exists()

    def test_second_record_appends_a_second_line_not_overwrite(self, tmp_path):
        adapter = usage_capture.JsonlLoggingAdapter(base_dir=tmp_path)
        adapter.record(_make_record("sess-3-0001", "sess-3"), "first")
        adapter.record(_make_record("sess-3-0002", "sess-3"), "second")

        session_file = tmp_path / ".agent-factory" / "usage" / "sess-3.jsonl"
        lines = session_file.read_text().splitlines()
        assert len(lines) == 2
        assert [json.loads(line)["record_id"] for line in lines] == [
            "sess-3-0001",
            "sess-3-0002",
        ]


class TestJsonlLoggingAdapterTranscriptPersistence:
    def test_transcript_copy_written_and_ref_points_at_it(self, tmp_path):
        adapter = usage_capture.JsonlLoggingAdapter(base_dir=tmp_path)
        record = _make_record("sess-4-0001", "sess-4")

        adapter.record(record, "the tokenized transcript body")

        expected_path = (
            tmp_path
            / ".agent-factory"
            / "usage"
            / "transcripts"
            / "sess-4"
            / "sess-4-0001.jsonl"
        )
        assert expected_path.exists()
        assert expected_path.read_text() == "the tokenized transcript body"
        assert record.transcript_ref.path == str(expected_path)

    def test_serialized_record_line_carries_the_same_transcript_ref(self, tmp_path):
        adapter = usage_capture.JsonlLoggingAdapter(base_dir=tmp_path)
        record = _make_record("sess-5-0001", "sess-5")

        adapter.record(record, "body")

        session_file = tmp_path / ".agent-factory" / "usage" / "sess-5.jsonl"
        payload = json.loads(session_file.read_text().splitlines()[0])
        assert payload["transcript_ref"]["path"] == record.transcript_ref.path


class TestJsonlLoggingAdapterConcurrency:
    def test_many_concurrent_appends_are_neither_lost_nor_interleaved(self, tmp_path):
        """Fires many threads at one adapter/session simultaneously.

        `os.write` releases the GIL for the duration of the syscall, so
        concurrent threads genuinely race at the OS level here — this
        exercises the same O_APPEND atomicity the adapter relies on for
        real concurrent *processes* (e.g. parallel sub-agent dispatch),
        without the complexity of spawning subprocesses against a
        dynamically-loaded, extensionless module.
        """
        adapter = usage_capture.JsonlLoggingAdapter(base_dir=tmp_path)
        session_id = "sess-concurrent"
        count = 100

        def _write(i: int) -> None:
            record = _make_record(f"{session_id}-{i:04d}", session_id)
            adapter.record(record, f"transcript {i}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
            list(pool.map(_write, range(count)))

        session_file = tmp_path / ".agent-factory" / "usage" / f"{session_id}.jsonl"
        lines = session_file.read_text().splitlines()
        assert len(lines) == count  # no lost writes

        seen_ids = {json.loads(line)["record_id"] for line in lines}
        assert len(seen_ids) == count  # every line parses; none interleaved/corrupted


class TestJsonlLoggingAdapterFailureIsSwallowed:
    def test_unwritable_target_is_swallowed_and_logged_to_stderr(
        self, tmp_path, capsys
    ):
        # Pre-create a plain file where the per-session transcripts
        # directory needs to be a directory, forcing the adapter's own
        # mkdir(parents=True) to raise.
        transcripts_dir = tmp_path / ".agent-factory" / "usage" / "transcripts"
        transcripts_dir.mkdir(parents=True)
        session_id = "sess-broken"
        (transcripts_dir / session_id).write_text("I am a file, not a directory")

        adapter = usage_capture.JsonlLoggingAdapter(base_dir=tmp_path)
        record = _make_record(f"{session_id}-0001", session_id)

        adapter.record(record, "text")  # must not raise

        captured = capsys.readouterr()
        assert "usage-capture" in captured.err
        assert record.record_id in captured.err
        assert record.transcript_ref is None  # failed before transcript_ref was set

    def test_serialization_error_is_swallowed_and_logged_to_stderr(
        self, tmp_path, capsys
    ):
        adapter = usage_capture.JsonlLoggingAdapter(base_dir=tmp_path)
        record = _make_record("sess-bad-0001", "sess-bad")
        # `object()` is not JSON-serializable; poisons json.dumps() inside
        # the adapter's write path without touching the filesystem at all.
        record.branch = object()

        adapter.record(record, "text")  # must not raise

        captured = capsys.readouterr()
        assert "usage-capture" in captured.err
        assert record.record_id in captured.err


# ── Transcript normalizer (ST-0037) ─────────────────────────────────────


def _write_transcript(tmp_path, lines) -> Path:
    """Write *lines* (dicts and/or raw strings) as a `.jsonl` transcript.

    The fixture is built inline into a `tmp_path` file rather than tracked, so
    ST-0037 stays within its two declared outputs. Raw strings pass through
    verbatim (used to inject a malformed line).
    """
    path = tmp_path / "transcript.jsonl"
    rendered = []
    for line in lines:
        rendered.append(line if isinstance(line, str) else json.dumps(line))
    path.write_text("\n".join(rendered) + "\n", encoding="utf-8")
    return path


def _claude_transcript_with_usage():
    """A Claude Code `.jsonl` run carrying per-message `usage`.

    Covers every content-block kind ST-0037 must fold into one stream: a
    system prompt, a user turn, an assistant turn with thinking + text +
    tool_use, and a tool_result fed back in the following user turn.
    """
    return [
        {"type": "system", "message": {"role": "system", "content": "SYSTEM_PROMPT"}},
        {
            "type": "user",
            "message": {"role": "user", "content": "USER_QUESTION"},
        },
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "THINKING_TRACE"},
                    {"type": "text", "text": "ASSISTANT_ANSWER"},
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"file_path": "TOOL_INPUT_PATH"},
                    },
                ],
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 40,
                    "cache_read_input_tokens": 7,
                    "cache_creation_input_tokens": 3,
                },
            },
        },
        {
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": [{"type": "text", "text": "TOOL_RESULT_BODY"}],
                    }
                ],
                "usage": {
                    "input_tokens": 50,
                    "output_tokens": 0,
                    "cache_read_input_tokens": 1,
                    "cache_creation_input_tokens": 0,
                },
            },
        },
    ]


class TestNormalizerInterface:
    def test_selectable_per_cli(self):
        normalizer = usage_capture.get_normalizer("claude-code")
        assert hasattr(normalizer, "parse")

    def test_unsupported_cli_raises_value_error(self):
        # An unknown CLI is a capture-site programming error, distinct from a
        # malformed transcript (which is skipped, not raised on).
        try:
            usage_capture.get_normalizer("no-such-cli")
        except ValueError as exc:
            assert "no-such-cli" in str(exc)
        else:  # pragma: no cover - fail explicitly if no error raised
            raise AssertionError("expected ValueError for unsupported cli")


class TestClaudeCodeNormalizerText:
    def test_full_run_text_includes_every_block_kind(self, tmp_path):
        path = _write_transcript(tmp_path, _claude_transcript_with_usage())
        result = usage_capture.get_normalizer("claude-code").parse(path)

        full = result.text
        # System prompt, user turn, thinking, assistant answer, tool input,
        # and tool result — not just the boundary prompt and final output.
        for fragment in (
            "SYSTEM_PROMPT",
            "USER_QUESTION",
            "THINKING_TRACE",
            "ASSISTANT_ANSWER",
            "TOOL_INPUT_PATH",
            "TOOL_RESULT_BODY",
        ):
            assert fragment in full, f"{fragment} missing from full run text"

    def test_role_split_directs_input_and_output(self, tmp_path):
        path = _write_transcript(tmp_path, _claude_transcript_with_usage())
        result = usage_capture.get_normalizer("claude-code").parse(path)

        # input <- system, user, tool_result
        assert "SYSTEM_PROMPT" in result.input_text
        assert "USER_QUESTION" in result.input_text
        assert "TOOL_RESULT_BODY" in result.input_text
        # output <- assistant text, thinking, tool_use
        assert "ASSISTANT_ANSWER" in result.output_text
        assert "THINKING_TRACE" in result.output_text
        assert "TOOL_INPUT_PATH" in result.output_text
        # and the streams do not bleed into each other
        assert "TOOL_RESULT_BODY" not in result.output_text
        assert "THINKING_TRACE" not in result.input_text


class TestClaudeCodeNormalizerReportedUsage:
    def test_usage_is_summed_across_messages_at_full_granularity(self, tmp_path):
        path = _write_transcript(tmp_path, _claude_transcript_with_usage())
        result = usage_capture.get_normalizer("claude-code").parse(path)

        assert result.reported_input == 150  # 100 + 50
        assert result.reported_output == 40  # 40 + 0
        assert result.reported_cache_read == 8  # 7 + 1
        assert result.reported_cache_write == 3  # 3 + 0
        assert result.usage_granularity == "full"

    def test_usageless_transcript_yields_null_reported_and_no_granularity(
        self, tmp_path
    ):
        lines = [
            {"type": "user", "message": {"role": "user", "content": "ASK"}},
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": "REPLY"},
            },
        ]
        path = _write_transcript(tmp_path, lines)
        result = usage_capture.get_normalizer("claude-code").parse(path)

        assert "ASK" in result.input_text
        assert "REPLY" in result.output_text
        assert result.reported_input is None
        assert result.reported_output is None
        assert result.reported_cache_read is None
        assert result.reported_cache_write is None
        assert result.usage_granularity is None

    def test_malformed_line_is_skipped_not_raised(self, tmp_path):
        lines = [
            {"type": "user", "message": {"role": "user", "content": "GOOD_ONE"}},
            "{ this is not valid json",
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": "GOOD_TWO",
                    "usage": {"input_tokens": 5, "output_tokens": 9},
                },
            },
        ]
        path = _write_transcript(tmp_path, lines)
        result = usage_capture.get_normalizer("claude-code").parse(path)

        assert "GOOD_ONE" in result.input_text
        assert "GOOD_TWO" in result.output_text
        assert result.reported_input == 5
        assert result.usage_granularity == "full"


def _copilot_parent_transcript_with_general_purpose_child():
    """Synthetic Copilot events; never derived from a private transcript."""
    return [
        {"type": "system.message", "data": {"content": "COPILOT_SYSTEM"}},
        {"type": "user.message", "data": {"content": "PARENT_QUESTION"}},
        {
            "type": "assistant.message",
            "data": {
                "content": "PARENT_ANSWER",
                "reasoningText": "PARENT_REASONING",
            },
        },
        {
            "type": "tool.execution_start",
            "data": {
                "toolName": "task",
                "arguments": {"agent": "general-purpose", "prompt": "CHILD_TASK"},
            },
        },
        {
            "type": "assistant.message",
            "data": {
                "content": "GENERAL_PURPOSE_CHILD_ANSWER",
                "parentToolCallId": "general-purpose-call",
            },
        },
        {
            "type": "tool.execution_complete",
            "data": {
                "result": "GENERAL_PURPOSE_CHILD_RESULT",
                "toolCallId": "general-purpose-call",
            },
        },
        {
            "type": "assistant.usage",
            "data": {
                "inputTokens": 100,
                "outputTokens": 20,
                "cacheReadTokens": 5,
                "cacheWriteTokens": 2,
            },
        },
        {
            "type": "assistant.usage",
            "data": {
                "inputTokens": 40,
                "outputTokens": 9,
                "cacheReadTokens": 3,
                "cacheWriteTokens": 1,
                "initiator": "sub-agent",
                "parentToolCallId": "general-purpose-call",
            },
        },
    ]


class TestCopilotNormalizerST0042:
    def test_parent_is_inclusive_of_general_purpose_child_text_and_usage(
        self, tmp_path
    ):
        path = _write_transcript(
            tmp_path, _copilot_parent_transcript_with_general_purpose_child()
        )

        result = usage_capture.get_normalizer("copilot").parse(path)

        assert "PARENT_QUESTION" in result.input_text
        assert "GENERAL_PURPOSE_CHILD_RESULT" in result.input_text
        assert "PARENT_ANSWER" in result.output_text
        assert "PARENT_REASONING" in result.output_text
        assert "GENERAL_PURPOSE_CHILD_ANSWER" in result.output_text
        assert "CHILD_TASK" in result.output_text
        assert result.reported_input == 140
        assert result.reported_output == 29
        assert result.reported_cache_read == 8
        assert result.reported_cache_write == 3
        assert result.usage_granularity == "full"

    def test_unknown_and_malformed_events_are_skipped(self, tmp_path):
        path = _write_transcript(
            tmp_path,
            [
                "not-json",
                {"type": "future.event", "data": {"content": "IGNORE_ME"}},
                {"type": "user.message", "data": {"content": "KEEP_INPUT"}},
                {
                    "type": "assistant.message",
                    "data": {"content": "KEEP_OUTPUT"},
                },
            ],
        )

        result = usage_capture.get_normalizer("copilot").parse(path)

        assert result.input_text == "KEEP_INPUT"
        assert result.output_text == "KEEP_OUTPUT"
        assert "IGNORE_ME" not in result.text


class TestCodexNormalizerST0043:
    def test_ST0043_full_root_transcript_includes_child_activity_and_latest_usage(
        self, tmp_path
    ):
        events = [
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "ROOT ASK"}],
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "spawn_agent",
                    "arguments": '{"task":"inspect"}',
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call_output",
                    "output": "CHILD RESULT",
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "ROOT ANSWER"}],
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": 90,
                            "cached_input_tokens": 15,
                            "output_tokens": 30,
                        }
                    },
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": 120,
                            "cached_input_tokens": 20,
                            "output_tokens": 45,
                        }
                    },
                },
            },
        ]
        path = tmp_path / "rollout.jsonl"
        path.write_text("\n".join(json.dumps(event) for event in events) + "\n")

        result = usage_capture.get_normalizer("codex").parse(path)

        assert result.input_text == "ROOT ASK\nCHILD RESULT"
        assert result.output_text == ('spawn_agent {"task":"inspect"}\nROOT ANSWER')
        assert "CHILD RESULT" in result.text
        assert result.reported_input == 120
        assert result.reported_output == 45
        assert result.reported_cache_read == 20
        assert result.reported_cache_write == 0
        assert result.usage_granularity == "full"


def _normalize_via_subprocess(cli: str, path: Path) -> dict:
    """Run `usage-capture --normalize` through the script's own shebang.

    Same rationale as `_count_via_subprocess`: bare `uvx pytest` has no
    tiktoken, but the script's `uv run --script` shebang does — so the
    `normalized_*` integers below are real cl100k_base counts, proven to come
    from the *same single read* that yields `reported_*`.
    """
    result = subprocess.run(
        [str(_SCRIPT), "--normalize", cli, str(path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class TestNormalizerProducesBothCountsFromOneRead:
    def test_single_read_yields_normalized_and_reported(self, tmp_path):
        path = _write_transcript(tmp_path, _claude_transcript_with_usage())
        bundle = _normalize_via_subprocess("claude-code", path)

        # normalized_* — real cl100k_base counts over the role-split streams.
        assert bundle["normalized_input"] > 0
        assert bundle["normalized_output"] > 0
        assert (
            bundle["normalized_total"]
            == bundle["normalized_input"] + bundle["normalized_output"]
        )
        # reported_* — summed from the very same read.
        assert bundle["reported_input"] == 150
        assert bundle["reported_output"] == 40
        assert bundle["reported_cache_read"] == 8
        assert bundle["reported_cache_write"] == 3
        assert bundle["usage_granularity"] == "full"

    def test_usageless_single_read_still_yields_normalized(self, tmp_path):
        lines = [
            {"type": "user", "message": {"role": "user", "content": "ASK SOMETHING"}},
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": "A REPLY HERE"},
            },
        ]
        path = _write_transcript(tmp_path, lines)
        bundle = _normalize_via_subprocess("claude-code", path)

        assert bundle["normalized_input"] > 0
        assert bundle["normalized_output"] > 0
        assert bundle["reported_input"] is None
        assert bundle["reported_output"] is None
        assert bundle["usage_granularity"] is None


# ── CLI entrypoint (ST-0038) ─────────────────────────────────────────────

# The proposal's example invocation (`usage-capture --cli pi --transcript
# <path> --session <id> --agent <name> --model <m> --loop-role review
# --iteration 2 --commit <sha> ...`), adapted to the one CLI this slice
# actually registers a normalizer for (`claude-code`), exercising every
# context flag ST-0038's acceptance criteria lists.
_FULL_FLAG_SET = [
    "--parent-session",
    "sess-cli-parent",
    "--depth",
    "2",
    "--agent",
    "developer-agent",
    "--skill",
    "tdd",
    "--model",
    "claude-sonnet-5",
    "--phase",
    "implementation",
    "--playbook",
    "feature-addition",
    "--story-id",
    "ST-0038",
    "--loop-role",
    "create",
    "--iteration",
    "1",
    "--branch",
    "story/ST-0038",
    "--base-commit",
    "abc123",
    "--commit",
    "def456",
    "--exit-status",
    "success",
]


def _run_capture(cwd, extra_args) -> subprocess.CompletedProcess:
    """Invoke `usage-capture` as a subprocess through its own shebang, the
    same rationale as `_count_via_subprocess`/`_normalize_via_subprocess`:
    a bare `uvx pytest` interpreter has no `tiktoken`, but the script's own
    `uv run --script` shebang bootstraps it, so the real argparse ->
    normalize -> tokenize -> persist pipeline runs end to end."""
    return subprocess.run(
        [str(_SCRIPT), *extra_args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


class TestCliEntrypointHappyPath:
    def test_example_invocation_appends_well_formed_record(self, tmp_path):
        transcript_path = _write_transcript(tmp_path, _claude_transcript_with_usage())

        result = _run_capture(
            tmp_path,
            [
                "--cli",
                "claude-code",
                "--transcript",
                str(transcript_path),
                "--session",
                "sess-cli-1",
                *_FULL_FLAG_SET,
            ],
        )
        assert result.returncode == 0, result.stderr

        session_file = tmp_path / ".agent-factory" / "usage" / "sess-cli-1.jsonl"
        lines = session_file.read_text().splitlines()
        assert len(lines) == 1  # exactly one record per call
        record = json.loads(lines[0])

        # Every context flag landed on its matching UsageRecord field.
        assert record["cli"] == "claude-code"
        assert record["session_id"] == "sess-cli-1"
        assert record["parent_session_id"] == "sess-cli-parent"
        assert record["depth"] == 2
        assert record["agent"] == "developer-agent"
        assert record["skill"] == "tdd"
        assert record["model"] == "claude-sonnet-5"
        assert record["phase"] == "implementation"
        assert record["playbook"] == "feature-addition"
        assert record["story_id"] == "ST-0038"
        assert record["loop_role"] == "create"
        assert record["iteration"] == 1
        assert record["branch"] == "story/ST-0038"
        assert record["base_commit"] == "abc123"
        assert record["commit_id"] == "def456"
        assert record["exit_status"] == "success"

        # normalized_* real cl100k_base counts; reported_* from the fixture.
        assert record["normalized_input"] > 0
        assert record["normalized_output"] > 0
        assert (
            record["normalized_total"]
            == record["normalized_input"] + record["normalized_output"]
        )
        assert record["reported_input"] == 150
        assert record["reported_output"] == 40
        assert record["reported_cache_read"] == 8
        assert record["reported_cache_write"] == 3
        assert record["usage_granularity"] == "full"

        # The persisted transcript copy exists and transcript_ref points at
        # it. The adapter's default base_dir is "." (relative to the
        # subprocess's own cwd, tmp_path), so resolve it the same way here.
        transcript_ref_path = tmp_path / record["transcript_ref"]["path"]
        assert transcript_ref_path.exists()
        assert transcript_ref_path.read_text() != ""

    def test_repeated_invocations_same_session_do_not_collide_record_ids(
        self, tmp_path
    ):
        """Guards `RecordIdSequencer.seed`: this CLI is a fresh process per
        call, so two captures for one session must still get distinct
        record_ids (and distinct transcript-copy files), not both "-0001"."""
        transcript_path = _write_transcript(tmp_path, _claude_transcript_with_usage())
        args = [
            "--cli",
            "claude-code",
            "--transcript",
            str(transcript_path),
            "--session",
            "sess-repeat",
        ]

        first = _run_capture(tmp_path, args)
        second = _run_capture(tmp_path, args)
        assert first.returncode == 0, first.stderr
        assert second.returncode == 0, second.stderr

        session_file = tmp_path / ".agent-factory" / "usage" / "sess-repeat.jsonl"
        lines = session_file.read_text().splitlines()
        assert len(lines) == 2
        record_ids = [json.loads(line)["record_id"] for line in lines]
        assert record_ids == ["sess-repeat-0001", "sess-repeat-0002"]

        transcripts_dir = (
            tmp_path / ".agent-factory" / "usage" / "transcripts" / "sess-repeat"
        )
        assert len(list(transcripts_dir.iterdir())) == 2  # neither copy overwritten


class TestCliEntrypointBestEffort:
    def test_unknown_cli_is_a_noop_and_exits_zero(self, tmp_path):
        transcript_path = _write_transcript(tmp_path, _claude_transcript_with_usage())

        result = _run_capture(
            tmp_path,
            [
                "--cli",
                "no-such-cli",
                "--transcript",
                str(transcript_path),
                "--session",
                "sess-unknown-cli",
            ],
        )

        assert result.returncode == 0
        assert not (tmp_path / ".agent-factory").exists()  # nothing written
        assert result.stderr != ""  # but the failure is not silent

    def test_bad_transcript_path_still_exits_zero(self, tmp_path):
        missing_path = tmp_path / "does-not-exist.jsonl"

        result = _run_capture(
            tmp_path,
            [
                "--cli",
                "claude-code",
                "--transcript",
                str(missing_path),
                "--session",
                "sess-bad-transcript",
            ],
        )

        assert result.returncode == 0
        assert not (tmp_path / ".agent-factory").exists()
        assert result.stderr != ""

    def test_missing_required_flags_still_exits_zero(self, tmp_path):
        # No --cli/--transcript at all: argparse would normally exit(2).
        result = _run_capture(tmp_path, ["--session", "sess-missing-flags"])

        assert result.returncode == 0
        assert result.stderr != ""
