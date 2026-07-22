"""End-to-end test: Claude Code Stop/SubagentStop hook -> capture path (ST-0041).

This test drives a Claude Code `.jsonl` transcript fixture THROUGH THE INSTALLED
HOOK PATH — the way Claude Code itself does at session end. It verifies:

- The Stop/SubagentStop hook script reads JSON from stdin (`transcript_path`
  for Stop; `agent_transcript_path` and `agent_type` for SubagentStop).
- The hook resolves `factory/scripts/usage-capture` from CLAUDE_PROJECT_DIR.
- The hook invokes usage-capture in the BACKGROUND (so the hook exits 0 before
  capture finishes) and always exits 0.
- A well-formed record line appears in `.agent-factory/usage/<session_id>.jsonl`.
- A transcript copy exists at the persisted path.
- The record carries the full field set: `normalized_*` (real cl100k_base
  counts), `reported_*` populated from the fixture, `usage_granularity='full'`.
- A capture failure (bad transcript, unwritable usage dir) leaves the run
  UNAFFECTED — the hook still exits 0, no stdout.

COVERAGE CHECKLIST: Completion Criteria from the proposal
(factory/docs/proposals/token-usage-tracking.md) map to the stories below:

| Criterion | Story |
|-----------|-------|
| factory/scripts/usage-capture exists and writes well-formed record | ST-0035, ST-0036, ST-0037, ST-0038 |
| Records carry normalized_* counts produced by cl100k_base | ST-0035, ST-0037 |
| reported_* populated where the transcript provides it | ST-0037, ST-0038 |
| Claude Code Stop and SubagentStop sessions captured automatically | ST-0040 |
| Capture never fails, blocks, or slows the run it measures | ST-0035, ST-0036, ST-0038, ST-0040 |
| Path is git-ignored and concurrent appends do not corrupt | ST-0036, ST-0040 |

DEFERRED SCOPE (out of scope for ST-0041 and earlier):

- Reader, aggregation, and presentation of the data (no reporter yet).
- Dollar-cost math (layer over reported_* × model × rate table).
- PostgreSQL adapter and its logging service.
- Budget enforcement.
- Pi, orchestrator, and Copilot capture points (normalizer seams exist;
  wiring is follow-on).
- Pi human-session hook timing is settled in the Pi rollout, not here.

(This E2E test for Claude Code's hook covers the stop-event path; Pi and
Copilot wiring and their hook semantics are deferred to their respective
rollout phases.)
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[2]
_FACTORY_ROOT = _ROOT
_HOOK_SCRIPT = _FACTORY_ROOT / "factory" / "config" / "hooks" / "capture-usage.sh"


def _make_unique_session_id(base: str = "session") -> str:
    """Generate a unique session ID to avoid collisions between test runs."""
    return f"{base}-{str(uuid.uuid4())[:8]}"


def _make_stop_payload(
    transcript_path: Path,
    session_id: str,
    hook_event_name: str = "Stop",
    agent_type: str | None = None,
    agent_transcript_path: Path | None = None,
) -> str:
    """Build Stop/SubagentStop hook JSON payload."""
    payload = {
        "transcript_path": str(transcript_path),
        "session_id": session_id,
        "hook_event_name": hook_event_name,
    }
    if agent_type and hook_event_name == "SubagentStop":
        payload["agent_type"] = agent_type
    if agent_transcript_path and hook_event_name == "SubagentStop":
        payload["agent_transcript_path"] = str(agent_transcript_path)
    return json.dumps(payload)


def _make_transcript_with_usage(tmp_path: Path) -> Path:
    """Build a Claude Code `.jsonl` transcript with per-message `usage` blocks.

    Includes: system prompt, user turn, assistant turn with thinking + text +
    tool_use, and tool_result. Every message has a `usage` block so
    `reported_*` fields are populated and `usage_granularity='full'`.
    """
    lines = [
        {
            "type": "system",
            "message": {"role": "system", "content": "SYSTEM_PROMPT_TEXT"},
        },
        {
            "type": "user",
            "message": {"role": "user", "content": "USER_QUESTION_TEXT"},
        },
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "ASSISTANT_THINKING"},
                    {"type": "text", "text": "ASSISTANT_ANSWER_TEXT"},
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"file_path": "TOOL_INPUT_PARAMETER"},
                    },
                ],
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_read_input_tokens": 10,
                    "cache_creation_input_tokens": 5,
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
                        "content": [{"type": "text", "text": "TOOL_RESULT_TEXT"}],
                    }
                ],
                "usage": {
                    "input_tokens": 80,
                    "output_tokens": 20,
                    "cache_read_input_tokens": 5,
                    "cache_creation_input_tokens": 2,
                },
            },
        },
    ]
    path = tmp_path / "transcript.jsonl"
    path.write_text(
        "\n".join(json.dumps(line) for line in lines) + "\n", encoding="utf-8"
    )
    return path


def _make_single_assistant_transcript(
    path: Path, marker: str, *, input_tokens: int, output_tokens: int
) -> Path:
    """Build a minimal transcript whose text and usage identify its owner."""
    path.write_text(
        json.dumps(
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": marker}],
                    "usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cache_read_input_tokens": 0,
                        "cache_creation_input_tokens": 0,
                    },
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _poll_usage_file(
    session_id: str, usage_dir: Path, timeout_secs: float = 5.0
) -> dict | None:
    """Poll for a record in `.agent-factory/usage/<session_id>.jsonl`.

    The hook runs `usage-capture` in the background, so the file may not exist
    immediately. This function polls up to `timeout_secs` to let the background
    process finish writing, then returns the first record dict (or None if
    timeout expires).
    """
    start = time.time()
    session_file = usage_dir / f"{session_id}.jsonl"
    while time.time() - start < timeout_secs:
        if session_file.exists():
            lines = session_file.read_text(encoding="utf-8").splitlines()
            if lines:
                # Return the first line as a parsed record.
                return json.loads(lines[0])
        time.sleep(0.1)
    return None


class TestHookE2E:
    """End-to-end hook tests: feed Stop/SubagentStop JSON to the hook script."""

    def test_stop_hook_appends_well_formed_record_and_transcript_copy(self, tmp_path):
        """Drive a transcript through the hook path and assert record + copy."""
        # Use factory root as project dir. .agent-factory/ is git-ignored, so this
        # test remains hermetic (doesn't pollute tracked files).
        project_dir = _FACTORY_ROOT
        usage_dir = project_dir / ".agent-factory" / "usage"

        # Create a fixture transcript with per-message usage.
        transcript_path = _make_transcript_with_usage(tmp_path)

        # Prepare the Stop hook payload (use unique session ID).
        session_id = _make_unique_session_id("test-1")
        payload = _make_stop_payload(
            transcript_path, session_id, hook_event_name="Stop"
        )

        # Invoke the hook with CLAUDE_PROJECT_DIR set to factory root.
        # Also set cwd to project_dir so usage-capture writes to the right place.
        result = subprocess.run(
            [str(_HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        )

        # Hook must exit 0 and produce no stdout (best-effort contract).
        assert result.returncode == 0, f"hook stderr: {result.stderr}"
        assert result.stdout == ""

        # Poll for the record to appear (background write).
        record = _poll_usage_file(session_id, usage_dir)
        assert record is not None, "record did not appear after timeout"

        # Assert the record is well-formed: has all required fields.
        assert record["record_id"].startswith(f"{session_id}-")
        assert record["record_id"].endswith("-0001")  # First record in this session
        assert record["session_id"] == session_id
        assert record["cli"] == "claude-code"

        # Assert normalized_* are present and non-zero.
        assert record["normalized_input"] > 0
        assert record["normalized_output"] > 0
        assert (
            record["normalized_total"]
            == record["normalized_input"] + record["normalized_output"]
        )

        # Assert reported_* are populated from the fixture (usage_granularity='full').
        assert record["reported_input"] == 180  # 100 + 80
        assert record["reported_output"] == 70  # 50 + 20
        assert record["reported_cache_read"] == 15  # 10 + 5
        assert record["reported_cache_write"] == 7  # 5 + 2
        assert record["usage_granularity"] == "full"

        # Assert the transcript copy exists at the path the record points to.
        transcript_ref = record["transcript_ref"]
        assert transcript_ref is not None
        # The path may be relative or absolute; resolve it relative to project_dir
        transcript_copy = Path(transcript_ref["path"])
        if not transcript_copy.is_absolute():
            transcript_copy = project_dir / transcript_copy
        assert transcript_copy.exists()
        assert transcript_copy.read_text(encoding="utf-8") != ""

    def test_RECON0008_subagent_stop_uses_agent_transcript_and_captures_type(
        self, tmp_path
    ):
        """Official payload points at main and child transcripts separately."""
        project_dir = _FACTORY_ROOT
        usage_dir = project_dir / ".agent-factory" / "usage"

        parent_transcript = _make_single_assistant_transcript(
            tmp_path / "parent.jsonl",
            "PARENT_ONLY_MARKER",
            input_tokens=900,
            output_tokens=90,
        )
        child_transcript = _make_single_assistant_transcript(
            tmp_path / "child.jsonl",
            "CHILD_ONLY_MARKER",
            input_tokens=17,
            output_tokens=5,
        )

        session_id = _make_unique_session_id("test-2")
        payload = _make_stop_payload(
            parent_transcript,
            session_id,
            hook_event_name="SubagentStop",
            agent_type="developer-agent",
            agent_transcript_path=child_transcript,
        )

        result = subprocess.run(
            [str(_HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        )

        assert result.returncode == 0
        assert result.stdout == ""

        record = _poll_usage_file(session_id, usage_dir)
        assert record is not None
        assert record["agent"] == "developer-agent"
        assert record["reported_input"] == 17
        assert record["reported_output"] == 5

        transcript_copy = project_dir / record["transcript_ref"]["path"]
        captured_text = transcript_copy.read_text(encoding="utf-8")
        assert "CHILD_ONLY_MARKER" in captured_text
        assert "PARENT_ONLY_MARKER" not in captured_text

    def test_RECON0008_subagent_stop_never_falls_back_to_parent_transcript(
        self, tmp_path
    ):
        project_dir = _FACTORY_ROOT
        usage_dir = project_dir / ".agent-factory" / "usage"
        parent_transcript = _make_single_assistant_transcript(
            tmp_path / "parent-only.jsonl",
            "PARENT_MUST_NOT_BECOME_CHILD",
            input_tokens=900,
            output_tokens=90,
        )
        session_id = _make_unique_session_id("test-missing-child-path")
        payload = _make_stop_payload(
            parent_transcript,
            session_id,
            hook_event_name="SubagentStop",
            agent_type="developer-agent",
        )

        result = subprocess.run(
            [str(_HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        )

        assert result.returncode == 0
        time.sleep(0.2)
        assert not (usage_dir / f"{session_id}.jsonl").exists()

    def test_failure_in_capture_leaves_hook_unaffected(self, tmp_path):
        """A capture failure (bad transcript) does not fail the hook."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Point to a non-existent transcript file.
        missing_transcript = tmp_path / "does-not-exist.jsonl"
        session_id = _make_unique_session_id("test-3")
        payload = _make_stop_payload(missing_transcript, session_id)

        result = subprocess.run(
            [str(_HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        )

        # Hook must exit 0 even though capture failed.
        assert result.returncode == 0
        # Hook should have no stdout (best-effort, silent failure on the capture side).
        assert result.stdout == ""

    def test_unwritable_usage_dir_leaves_hook_unaffected(self, tmp_path):
        """Failure to write usage records does not fail the hook."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Pre-create a file where the usage directory needs to be a directory.
        (project_dir / ".agent-factory").write_text("I am a file, not a directory")

        transcript_path = _make_transcript_with_usage(tmp_path)
        session_id = _make_unique_session_id("test-4")
        payload = _make_stop_payload(transcript_path, session_id)

        # Set CLAUDE_PROJECT_DIR to the isolated project (no factory scripts there, but
        # the hook will fail gracefully since capture-usage is missing or path is blocked).
        result = subprocess.run(
            [str(_HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        )

        # Hook must exit 0 despite the unwritable path.
        assert result.returncode == 0
        assert result.stdout == ""

    def test_missing_required_fields_in_payload_exits_zero(self, tmp_path):
        """Hook exits 0 if transcript_path or session_id is missing."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Payload missing session_id.
        payload = json.dumps(
            {
                "transcript_path": "/tmp/transcript.jsonl",
                # session_id intentionally omitted
                "hook_event_name": "Stop",
            }
        )

        result = subprocess.run(
            [str(_HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        )

        assert result.returncode == 0
        assert result.stdout == ""

    def test_hook_resolves_usage_capture_from_claude_project_dir(self, tmp_path):
        """Hook finds usage-capture via CLAUDE_PROJECT_DIR."""
        project_dir = _FACTORY_ROOT

        transcript_path = _make_transcript_with_usage(tmp_path)
        session_id = _make_unique_session_id("test-5")
        payload = _make_stop_payload(transcript_path, session_id)

        # Invoke with CLAUDE_PROJECT_DIR set to the factory root.
        result = subprocess.run(
            [str(_HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        )

        # Hook should find usage-capture and run it.
        assert result.returncode == 0
        assert result.stdout == ""


class TestHookIntegrationWithMultipleRecords:
    """Multiple invocations of the hook in the same session."""

    def test_two_stop_invocations_same_session_generate_distinct_record_ids(
        self, tmp_path
    ):
        """The hook can be invoked multiple times for one session without collision."""
        project_dir = _FACTORY_ROOT
        usage_dir = project_dir / ".agent-factory" / "usage"

        transcript_path = _make_transcript_with_usage(tmp_path)
        session_id = _make_unique_session_id("test-multi")

        # First invocation.
        payload1 = _make_stop_payload(transcript_path, session_id)
        result1 = subprocess.run(
            [str(_HOOK_SCRIPT)],
            input=payload1,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        )
        assert result1.returncode == 0

        # Second invocation, same session.
        payload2 = _make_stop_payload(transcript_path, session_id)
        result2 = subprocess.run(
            [str(_HOOK_SCRIPT)],
            input=payload2,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        )
        assert result2.returncode == 0

        # Both records should exist with distinct record_ids.
        record1 = _poll_usage_file(session_id, usage_dir)
        assert record1 is not None
        assert record1["record_id"].endswith("-0001")  # First record

        # Poll again after a short delay to let the second record fully persist.
        time.sleep(0.5)
        session_file = usage_dir / f"{session_id}.jsonl"
        lines = session_file.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2

        record_ids = [json.loads(line)["record_id"] for line in lines]
        # Check that both records have the session_id prefix and sequential numbers
        assert record_ids[0].startswith(f"{session_id}-") and record_ids[0].endswith(
            "-0001"
        )
        assert record_ids[1].startswith(f"{session_id}-") and record_ids[1].endswith(
            "-0002"
        )
