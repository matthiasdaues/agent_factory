"""End-to-end test: Claude Code Stop/SubagentStop hook -> capture path (ST-0041).

This smoke suite drives Claude Code payloads through the installed hook path.
It owns only Claude's payload mapping, reported-token accounting, child
transcript selection, and representative malformed-input behavior.

- The Stop/SubagentStop hook script reads JSON from stdin (`transcript_path`
  for Stop; `agent_transcript_path` and `agent_type` for SubagentStop).
- The hook resolves `factory/scripts/usage-capture` from CLAUDE_PROJECT_DIR.
- The adapter maps reported usage and the CLI identifier correctly.
- SubagentStop uses the child transcript and records its agent type.
- A malformed payload remains a silent, best-effort no-op.

Shared persistence, record reservation, transcript-copy, and supervised
lifecycle contracts are owned by `test_usage_capture.py` and
`test_usage_capture_native_lifecycle_e2e.py`.

COVERAGE CHECKLIST: Completion Criteria from the proposal
(docs/proposals/implemented/token-usage-tracking.md) map to the stories below:

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
_HOOK_SCRIPT = _ROOT / "factory" / "config" / "hooks" / "capture-usage.sh"
_INIT = _ROOT / "factory/scripts/init-factory"


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
    """Poll for a record in `.agent-factory/usage/claude-code_<session_id>.jsonl`.

    The hook runs `usage-capture` in the background, so the file may not exist
    immediately. This function polls up to `timeout_secs` to let the background
    process finish writing, then returns the first record dict (or None if
    timeout expires).
    """
    start = time.time()
    session_file = usage_dir / f"claude-code_{session_id}.jsonl"
    while time.time() - start < timeout_secs:
        if session_file.exists():
            lines = session_file.read_text(encoding="utf-8").splitlines()
            if lines:
                # Return the first line as a parsed record.
                return json.loads(lines[0])
        time.sleep(0.1)
    return None


def _hermetic_project(tmp_path: Path) -> tuple[Path, Path]:
    """Build a throwaway git project with Factory installed for hook tests.

    The Stop/SubagentStop hook resolves ``factory/scripts/usage-capture-runtime``
    from ``CLAUDE_PROJECT_DIR`` and runs the project-owned runtime venv, so the
    target must have Factory installed (``init-factory``) and a git repo for the
    hook's branch/commit enrichment. Writing into ``tmp_path`` keeps the test
    hermetic: no records land in the real checkout's ``.agent-factory/usage/``.
    """
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=project, check=True, capture_output=True
    )
    (project / "seed").write_text("seed\n")
    subprocess.run(["git", "add", "seed"], cwd=project, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=test@example.com",
            "-c",
            "user.name=Test",
            "commit",
            "-m",
            "seed",
        ],
        cwd=project,
        check=True,
        capture_output=True,
    )
    result = subprocess.run(
        [
            str(_INIT),
            "--target",
            str(project),
            "--source",
            str(_ROOT),
            "--project-name",
            "Hook Test Project",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return project, project / ".agent-factory" / "usage"


class TestHookE2E:
    """End-to-end hook tests: feed Stop/SubagentStop JSON to the hook script."""

    def test_stop_hook_appends_well_formed_record_and_transcript_copy(self, tmp_path):
        """Drive a transcript through the hook path and assert record + copy."""
        project_dir, usage_dir = _hermetic_project(tmp_path)

        # Create a fixture transcript with per-message usage.
        transcript_path = _make_transcript_with_usage(tmp_path)

        # Prepare the Stop hook payload (use unique session ID).
        session_id = _make_unique_session_id("test-1")
        payload = _make_stop_payload(
            transcript_path, session_id, hook_event_name="Stop"
        )

        # Invoke the hook against the throwaway project so capture writes only
        # into its .agent-factory/usage/, never the real checkout.
        result = subprocess.run(
            [str(_HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
            check=False,
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
        assert uuid.UUID(record["project_id"])
        assert record["project_name"] == "Hook Test Project"
        assert record["session_id"] == session_id
        assert record["cli"] == "claude-code"
        assert record["recorded_at"].endswith("Z")
        expected_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_dir,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        expected_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_dir,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert record["branch"] == expected_branch
        assert record["commit_id"] == expected_commit
        assert {
            "run_start",
            "run_end",
            "loop_id",
            "loop_role",
            "iteration",
            "skill",
            "phase",
            "playbook",
            "story_id",
            "base_commit",
        }.isdisjoint(record)

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
        project_dir, usage_dir = _hermetic_project(tmp_path)

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
            check=False,
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
            check=False,
        )

        # Hook must exit 0 even though capture failed.
        assert result.returncode == 0
        # Hook should have no stdout (best-effort, silent failure on the capture side).
        assert result.stdout == ""
