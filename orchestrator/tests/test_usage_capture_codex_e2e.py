"""Codex adapter smoke tests: inclusive accounting, wiring, malformed input.

Shared persistence, record reservation, and lifecycle behavior are owned by
``test_usage_capture.py`` and ``test_usage_capture_native_lifecycle_e2e.py``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import time
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_INIT = _ROOT / "factory/scripts/init-factory"
_loader = SourceFileLoader("init_factory_codex_e2e", str(_INIT))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules[_loader.name] = init_factory
_loader.exec_module(init_factory)


def _install(project: Path) -> tuple[Path, dict]:
    assert (
        init_factory.main(
            [
                "--target",
                str(project),
                "--source",
                str(_ROOT),
                "--project-name",
                "Test Project",
            ]
        )
        == 0
    )
    config = json.loads((project / ".codex/hooks.json").read_text())
    return project / ".codex/hooks/capture-codex-usage.sh", config


def _transcript(path: Path, marker: str, include_child: bool = False) -> Path:
    events = [
        {
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": f"ASK_{marker}"}],
            },
        },
    ]
    if include_child:
        events.extend(
            [
                {
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "name": "spawn_agent",
                        "arguments": '{"task":"child"}',
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "function_call_output",
                        "output": "CHILD_SUBSUMED_RESULT",
                    },
                },
            ]
        )
    events.extend(
        [
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": f"ANSWER_{marker}"}],
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": 21 if include_child else 8,
                            "cached_input_tokens": 3,
                            "output_tokens": 9 if include_child else 4,
                        }
                    },
                },
            },
        ]
    )
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    return path


def _invoke(hook: Path, payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(hook)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


def _wait_for_record(project: Path, session: str) -> dict:
    path = project / f".agent-factory/usage/{session}.jsonl"
    for _ in range(100):
        if path.exists() and path.stat().st_size:
            return json.loads(path.read_text().splitlines()[-1])
        time.sleep(0.05)
    raise AssertionError(f"capture record not written: {path}")


class TestInstalledCodexHooksST0043:
    def test_stop_and_subagentstop_capture_inclusive_root_and_child_attribution(
        self, tmp_path
    ):
        hook, config = _install(tmp_path)
        for event in ("Stop", "SubagentStop"):
            assert config["hooks"][event] == [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": init_factory.CODEX_CAPTURE_HOOK_COMMAND,
                        }
                    ]
                }
            ]

        root_result = _invoke(
            hook,
            {
                "hook_event_name": "Stop",
                "session_id": "codex-root",
                "transcript_path": str(
                    _transcript(tmp_path / "root.jsonl", "ROOT", include_child=True)
                ),
                "cwd": str(tmp_path),
            },
        )
        child_result = _invoke(
            hook,
            {
                "hook_event_name": "SubagentStop",
                "session_id": "codex-child",
                "parent_session_id": "codex-root",
                "agent_name": "reviewer",
                "transcript_path": str(_transcript(tmp_path / "child.jsonl", "CHILD")),
                "cwd": str(tmp_path),
            },
        )

        assert root_result.returncode == child_result.returncode == 0
        assert root_result.stdout == child_result.stdout == ""
        root = _wait_for_record(tmp_path, "codex-root")
        child = _wait_for_record(tmp_path, "codex-child")
        assert root["cli"] == child["cli"] == "codex"
        assert root["reported_input"] == 21
        assert root["reported_output"] == 9
        assert child["parent_session_id"] == "codex-root"
        assert child["agent"] == "reviewer"
        assert (tmp_path / root["transcript_ref"]["path"]).read_text().find(
            "CHILD_SUBSUMED_RESULT"
        ) >= 0
        assert (tmp_path / child["transcript_ref"]["path"]).is_file()
        assert (
            len(
                (tmp_path / ".agent-factory/usage/codex-root.jsonl")
                .read_text()
                .splitlines()
            )
            == 1
        )
        assert (
            len(
                (tmp_path / ".agent-factory/usage/codex-child.jsonl")
                .read_text()
                .splitlines()
            )
            == 1
        )

    def test_hook_failure_is_best_effort(self, tmp_path):
        hook, _ = _install(tmp_path)
        result = _invoke(
            hook,
            {
                "hook_event_name": "Stop",
                "session_id": "missing",
                "transcript_path": str(tmp_path / "missing.jsonl"),
                "cwd": str(tmp_path),
            },
        )
        assert result.returncode == 0
        assert result.stdout == ""
