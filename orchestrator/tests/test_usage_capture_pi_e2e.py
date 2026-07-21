"""Installed-path executable coverage for Pi usage capture (ST-0044)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_INIT = _ROOT / "factory/scripts/init-factory"
_REMOVE = _ROOT / "factory/scripts/remove-factory"


def _init(target: Path) -> None:
    result = subprocess.run(
        [str(_INIT), "--target", str(target), "--source", str(_ROOT)],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr


def _records(target: Path, session: str) -> list[dict]:
    path = target / ".agent-factory/usage" / f"{session}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()]


@pytest.mark.skipif(
    not subprocess.run(["node", "--version"], capture_output=True).returncode == 0,
    reason="node required",
)
def test_ST0044_installed_session_shutdown_captures_once(tmp_path):
    _init(tmp_path)
    extension = tmp_path / ".pi/extensions/capture-usage.ts"
    assert extension.is_symlink()
    script = tmp_path / "exercise.mjs"
    script.write_text(
        f"""
import extension from {json.dumps(extension.as_uri())};
let shutdown;
extension({{on(name, handler) {{ if (name === 'session_shutdown') shutdown = handler; }}}});
const ctx = {{cwd: {json.dumps(str(tmp_path))}, sessionManager: {{
  getSessionFile() {{ return '/sessions/pi-human.jsonl'; }},
  getBranch() {{ return [
    {{type:'message', message:{{role:'user', content:'ASK'}}}},
    {{type:'message', message:{{role:'assistant', content:[{{type:'text',text:'ANSWER'}}], usage:{{input:7,output:3,cacheRead:1,cacheWrite:0}}}}}}
  ];}}
}}}};
await shutdown({{type:'session_shutdown'}}, ctx);
await shutdown({{type:'session_shutdown'}}, ctx);
"""
    )
    result = subprocess.run(
        ["node", "--experimental-strip-types", str(script)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    records = _records(tmp_path, "pi-human")
    assert len(records) == 1
    record = records[0]
    assert record["cli"] == "pi"
    assert record["reported_input"] == 7
    assert record["reported_output"] == 3
    transcript = tmp_path / record["transcript_ref"]["path"]
    assert transcript.is_file()
    assert "ASK" in transcript.read_text()


def test_ST0044_init_remove_preserves_project_pi_content(tmp_path):
    custom = tmp_path / ".pi/extensions/custom.ts"
    custom.parent.mkdir(parents=True)
    custom.write_text("// project owned\n")
    _init(tmp_path)
    for name in ("capture-usage.ts", "pi-usage.ts", "run-agent.ts", "dispatch-wave.ts"):
        assert (tmp_path / ".pi/extensions" / name).is_symlink()

    result = subprocess.run(
        [str(_REMOVE), "--target", str(tmp_path)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert custom.read_text() == "// project owned\n"
    assert list(custom.parent.iterdir()) == [custom]


def test_ST0044_invocation_extensions_capture_each_child_once():
    run_agent = (_ROOT / "factory/config/extensions/run-agent.ts").read_text()
    dispatch = (_ROOT / "factory/config/extensions/dispatch-wave.ts").read_text()
    assert run_agent.count("capturePiStream(cwd, child.stdout") == 1
    assert dispatch.count("capturePiStream(cwd, child.stdout") == 1
    assert "parentSessionId" in run_agent and "depth: depth + 1" in run_agent
    assert "parentSessionId" in dispatch and "depth: depth + 1" in dispatch
    assert '[INLINE_CAPTURE_ENV]: "1"' in run_agent
    assert '[INLINE_CAPTURE_ENV]: "1"' in dispatch


def test_ST0044_capture_bridge_is_best_effort():
    bridge = (_ROOT / "factory/config/extensions/pi-usage.ts").read_text()
    assert "catch {" in bridge
    assert 'stdio: "ignore"' in bridge
