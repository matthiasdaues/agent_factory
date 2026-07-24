"""Installed native-hook removal races through the shared capture lifecycle."""

from __future__ import annotations

import json
import importlib.util
import os
import subprocess
import sys
import time
from argparse import Namespace
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_INIT = _ROOT / "factory/scripts/init-factory"
_REMOVE = _ROOT / "factory/scripts/remove-factory"
_LIFECYCLE = _ROOT / "factory/scripts/usage-capture-lifecycle"
_loader = SourceFileLoader("usage_capture_lifecycle_test", str(_LIFECYCLE))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
lifecycle = importlib.util.module_from_spec(_spec)
sys.modules[_loader.name] = lifecycle
_loader.exec_module(lifecycle)


def _wait_for(predicate, timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    assert predicate(), "condition did not become true before timeout"


def _install(target: Path) -> None:
    result = subprocess.run(
        [str(_INIT), "--target", str(target), "--source", str(_ROOT)],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr


def _adapter(target: Path, cli: str) -> tuple[Path, dict, dict[str, str]]:
    transcript = target / f"{cli}.jsonl"
    session = f"{cli}-removal-race"
    environment = os.environ.copy()
    if cli == "claude-code":
        transcript.write_text(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "CLAUDE_RACE"}],
                        "usage": {"input_tokens": 7, "output_tokens": 3},
                    },
                }
            )
            + "\n"
        )
        hook = target / ".claude/hooks/capture-usage.sh"
        payload = {
            "hook_event_name": "Stop",
            "session_id": session,
            "transcript_path": str(transcript),
        }
        environment["CLAUDE_PROJECT_DIR"] = str(target)
    elif cli == "codex":
        transcript.write_text(
            json.dumps(
                {
                    "type": "event_msg",
                    "payload": {
                        "type": "token_count",
                        "info": {
                            "total_token_usage": {
                                "input_tokens": 7,
                                "output_tokens": 3,
                            }
                        },
                    },
                }
            )
            + "\n"
        )
        hook = target / ".codex/hooks/capture-codex-usage.sh"
        payload = {
            "session_id": session,
            "transcript_path": str(transcript),
            "cwd": str(target),
        }
        poison = target / "poison-bin"
        poison.mkdir()
        node = poison / "node"
        node.write_text(f"#!/bin/sh\ntouch {target / 'node-was-used'}\nexit 99\n")
        node.chmod(0o755)
        environment["PATH"] = f"{poison}:{environment['PATH']}"
    else:
        transcript.write_text(
            "\n".join(
                json.dumps(event)
                for event in (
                    {"type": "user.message", "data": {"content": "ASK"}},
                    {"type": "assistant.message", "data": {"content": "COPILOT_RACE"}},
                    {
                        "type": "assistant.usage",
                        "data": {"inputTokens": 7, "outputTokens": 3},
                    },
                )
            )
            + "\n"
        )
        hook = target / ".github/hooks/capture-copilot-usage.sh"
        payload = {
            "sessionId": session,
            "transcriptPath": str(transcript),
            "cwd": str(target),
        }
    return hook, payload, environment


def _gate_capture(target: Path, observed: Path) -> Path:
    capture = target / "factory/scripts/usage-capture"
    real = target / "factory/scripts/usage-capture-real"
    capture.rename(real)
    gate = target / "capture-gate"
    capture.write_text(
        """#!/usr/bin/env python3
import os
import pathlib
import shutil
import subprocess
import sys
import time
gate = pathlib.Path(os.environ['FAGAN_CAPTURE_GATE'])
while not gate.exists():
    time.sleep(0.02)
result = subprocess.run([sys.executable, os.environ['FAGAN_REAL_CAPTURE'], *sys.argv[1:]])
usage = pathlib.Path('.agent-factory/usage')
if usage.is_dir():
    destination = pathlib.Path(os.environ['FAGAN_OBSERVED'])
    destination.mkdir(exist_ok=True)
    for record in usage.glob('*.jsonl'):
        shutil.copy2(record, destination / record.name)
raise SystemExit(result.returncode)
"""
    )
    capture.chmod(0o755)
    return gate


@pytest.mark.parametrize(
    ("cli", "disposition"),
    [("claude-code", "drain"), ("codex", "cancel"), ("copilot", "drain")],
)
def test_FAGAN0005_native_hook_removal_reaches_selected_terminal_state(
    tmp_path: Path, cli: str, disposition: str
) -> None:
    _install(tmp_path)
    observed = tmp_path.parent / f"observed-{tmp_path.name}-{cli}-{disposition}"
    gate = _gate_capture(tmp_path, observed)
    hook, payload, environment = _adapter(tmp_path, cli)
    environment.update(
        {
            "FAGAN_CAPTURE_GATE": str(gate),
            "FAGAN_REAL_CAPTURE": str(tmp_path / "factory/scripts/usage-capture-real"),
            "FAGAN_OBSERVED": str(observed),
        }
    )

    hook_result = subprocess.run(
        [str(hook)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env=environment,
        timeout=10,
    )
    assert hook_result.returncode == 0
    pending = tmp_path / ".agent-factory/usage-control/pending"
    _wait_for(lambda: bool(list(pending.glob("*.pending.json"))))
    (tmp_path / f"{cli}.jsonl").unlink()

    removal = subprocess.Popen(
        [str(_REMOVE), "--target", str(tmp_path), "--pending-usage", disposition],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if disposition == "drain":
        _wait_for(
            lambda: (
                json.loads(
                    (tmp_path / ".agent-factory/usage-control/state.json").read_text()
                )["mode"]
                == disposition
            )
        )
        gate.touch()
    stdout, stderr = removal.communicate(timeout=10)
    assert removal.returncode == 0, stderr
    if disposition == "cancel":
        gate.touch()
    time.sleep(0.2)

    session = f"{cli}-removal-race"
    if disposition == "drain":
        record = json.loads((observed / f"{session}.jsonl").read_text())
        assert record["cli"] == cli
    else:
        assert not observed.exists()
        assert "cancelled 1 pending usage capture" in stdout
    assert not (tmp_path / ".agent-factory").exists()
    assert not (tmp_path / "node-was-used").exists()


@pytest.mark.parametrize(
    ("cli", "failure"),
    [("claude-code", "source"), ("codex", "runtime"), ("copilot", "source")],
)
def test_FAGAN0005_native_handoff_failure_leaves_no_registration(
    tmp_path: Path, cli: str, failure: str
) -> None:
    _install(tmp_path)
    hook, payload, environment = _adapter(tmp_path, cli)
    if failure == "source":
        (tmp_path / f"{cli}.jsonl").unlink()
    else:
        (tmp_path / ".agent-factory/usage-runtime/.requirements-sha256").unlink()

    result = subprocess.run(
        [str(hook)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env=environment,
    )

    assert result.returncode == 0
    assert not list((tmp_path / ".agent-factory/usage-control/pending").iterdir())
    assert not list((tmp_path / ".agent-factory/usage/.capture").iterdir())


def test_FAGAN0005_supervisor_spawn_failure_cleans_registered_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install(tmp_path)
    transcript = tmp_path / "source.jsonl"
    transcript.write_text("{}\n")

    def fail_spawn(*_args, **_kwargs):
        raise OSError("spawn unavailable")

    monkeypatch.setattr(lifecycle.subprocess, "Popen", fail_spawn)
    result = lifecycle.register(
        Namespace(
            root=str(tmp_path),
            cli="codex",
            transcript=str(transcript),
            session="handoff-failure",
            parent_session=None,
            agent=None,
            model=None,
            exit_status=None,
            depth=None,
        )
    )

    assert result == 0
    assert not list((tmp_path / ".agent-factory/usage-control/pending").iterdir())
    assert not list((tmp_path / ".agent-factory/usage/.capture").iterdir())
