"""Installed Copilot CLI hook -> canonical usage capture (ST-0042)."""

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
_loader = SourceFileLoader("init_factory_copilot_e2e", str(_INIT))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules[_loader.name] = init_factory
_loader.exec_module(init_factory)


def _install(project: Path) -> Path:
    assert init_factory.main(["--target", str(project), "--source", str(_ROOT)]) == 0
    return project / ".github/hooks/capture-copilot-usage.sh"


def _transcript(path: Path, marker: str) -> Path:
    events = [
        {"type": "user.message", "data": {"content": f"ASK_{marker}"}},
        {"type": "assistant.message", "data": {"content": f"ANSWER_{marker}"}},
        {
            "type": "assistant.usage",
            "data": {"inputTokens": 12, "outputTokens": 4},
        },
    ]
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    return path


def _invoke(hook: Path, payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(hook)], input=json.dumps(payload), text=True, capture_output=True
    )


def _wait_for_record(project: Path, session: str) -> dict:
    path = project / f".agent-factory/usage/{session}.jsonl"
    for _ in range(100):
        if path.exists() and path.stat().st_size:
            return json.loads(path.read_text().splitlines()[-1])
        time.sleep(0.05)
    raise AssertionError(f"capture record not written: {path}")


class TestInstalledCopilotHooksST0042:
    def test_agentstop_and_supported_subagentstop_append_canonical_records(
        self, tmp_path
    ):
        hook = _install(tmp_path)

        main_result = _invoke(
            hook,
            {
                "sessionId": "copilot-main",
                "transcriptPath": str(_transcript(tmp_path / "main.jsonl", "MAIN")),
                "cwd": str(tmp_path),
                "timestamp": 1,
                "stopReason": "end_turn",
            },
        )
        child_result = _invoke(
            hook,
            {
                "sessionId": "copilot-child",
                "transcriptPath": str(_transcript(tmp_path / "child.jsonl", "CHILD")),
                "cwd": str(tmp_path),
                "timestamp": 2,
                "agentName": "code-review",
                "stopReason": "end_turn",
            },
        )

        assert main_result.returncode == child_result.returncode == 0
        assert main_result.stdout == child_result.stdout == ""
        main = _wait_for_record(tmp_path, "copilot-main")
        child = _wait_for_record(tmp_path, "copilot-child")
        assert main["cli"] == child["cli"] == "copilot"
        assert main["agent"] is None
        assert child["agent"] == "code-review"
        assert main["reported_input"] == child["reported_input"] == 12
        assert main["reported_output"] == child["reported_output"] == 4
        assert (tmp_path / main["transcript_ref"]["path"]).is_file()
        assert (tmp_path / child["transcript_ref"]["path"]).is_file()

    def test_hook_failure_is_best_effort(self, tmp_path):
        hook = _install(tmp_path)
        result = _invoke(
            hook,
            {
                "sessionId": "missing-transcript",
                "transcriptPath": str(tmp_path / "does-not-exist.jsonl"),
                "cwd": str(tmp_path),
                "timestamp": 1,
                "stopReason": "end_turn",
            },
        )
        assert result.returncode == 0
        assert result.stdout == ""
