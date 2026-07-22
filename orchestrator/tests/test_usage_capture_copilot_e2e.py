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
    return _wait_for_records(project, session, 1)[-1]


def _wait_for_records(project: Path, session: str, count: int) -> list[dict]:
    path = project / f".agent-factory/usage/{session}.jsonl"
    for _ in range(100):
        if path.exists() and path.stat().st_size:
            records = [json.loads(line) for line in path.read_text().splitlines()]
            if len(records) == count:
                return records
        time.sleep(0.05)
    raise AssertionError(f"expected {count} capture record(s): {path}")


def _write_events(path: Path, events: list[dict]) -> Path:
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    return path


def _latest_copilot_root_total(records: list[dict], session: str) -> dict:
    """Test-local executable form of the deferred reader's conservation rule."""
    roots = [
        record
        for record in records
        if record["cli"] == "copilot"
        and record["session_id"] == session
        and record["agent"] is None
    ]
    latest = max(roots, key=lambda record: int(record["record_id"].rsplit("-", 1)[1]))
    return {
        "normalized": latest["normalized_total"],
        "reported": latest["reported_input"] + latest["reported_output"],
        "record_id": latest["record_id"],
    }


class TestInstalledCopilotHooksST0042:
    def test_RECON0011_repeated_turns_conserve_latest_root_and_exclude_child(
        self, tmp_path
    ):
        hook = _install(tmp_path)
        turn_one = [
            {"type": "user.message", "data": {"content": "FIRST_QUESTION"}},
            {"type": "assistant.message", "data": {"content": "FIRST_ANSWER"}},
            {
                "type": "assistant.usage",
                "data": {"inputTokens": 12, "outputTokens": 4},
            },
        ]
        turn_two = [
            {"type": "user.message", "data": {"content": "SECOND_QUESTION"}},
            {"type": "assistant.message", "data": {"content": "SECOND_ANSWER"}},
            {
                "type": "assistant.usage",
                "data": {"inputTokens": 18, "outputTokens": 6},
            },
        ]

        first_result = _invoke(
            hook,
            {
                "sessionId": "copilot-repeated-root",
                "transcriptPath": str(
                    _write_events(tmp_path / "root-1.jsonl", turn_one)
                ),
                "cwd": str(tmp_path),
                "timestamp": 1,
                "stopReason": "end_turn",
            },
        )
        assert first_result.returncode == 0
        first = _wait_for_records(tmp_path, "copilot-repeated-root", 1)[0]

        second_result = _invoke(
            hook,
            {
                "sessionId": "copilot-repeated-root",
                "transcriptPath": str(
                    _write_events(tmp_path / "root-2.jsonl", [*turn_one, *turn_two])
                ),
                "cwd": str(tmp_path),
                "timestamp": 2,
                "stopReason": "end_turn",
            },
        )
        assert second_result.returncode == 0
        roots = _wait_for_records(tmp_path, "copilot-repeated-root", 2)

        child_result = _invoke(
            hook,
            {
                "sessionId": "copilot-supported-child",
                "transcriptPath": str(
                    _transcript(tmp_path / "child-attribution.jsonl", "CHILD")
                ),
                "cwd": str(tmp_path),
                "timestamp": 3,
                "agentName": "code-review",
                "stopReason": "end_turn",
            },
        )
        assert child_result.returncode == 0
        child = _wait_for_records(tmp_path, "copilot-supported-child", 1)[0]

        assert [record["record_id"] for record in roots] == [
            "copilot-repeated-root-0001",
            "copilot-repeated-root-0002",
        ]
        assert first["reported_input"] == 12
        assert first["reported_output"] == 4
        assert roots[1]["reported_input"] == 30
        assert roots[1]["reported_output"] == 10
        assert roots[1]["normalized_total"] > roots[0]["normalized_total"]
        assert roots[0]["transcript_ref"] != roots[1]["transcript_ref"]
        assert all(
            (tmp_path / record["transcript_ref"]["path"]).is_file()
            for record in [*roots, child]
        )
        assert child["agent"] == "code-review"

        all_records = [*roots, child]
        conserved = _latest_copilot_root_total(all_records, "copilot-repeated-root")
        assert conserved == {
            "normalized": roots[1]["normalized_total"],
            "reported": 40,
            "record_id": "copilot-repeated-root-0002",
        }
        assert conserved["reported"] != sum(
            record["reported_input"] + record["reported_output"]
            for record in all_records
        )
        assert conserved["normalized"] != sum(
            record["normalized_total"] for record in all_records
        )

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
