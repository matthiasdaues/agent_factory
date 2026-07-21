"""Installed-path executable coverage for Pi usage capture (ST-0044)."""

from __future__ import annotations

import json
import os
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


def _install_pi_stub(target: Path) -> dict[str, str]:
    bin_dir = target / "test-bin"
    bin_dir.mkdir()
    pi = bin_dir / "pi"
    pi.write_text(
        "#!/bin/sh\n"
        'printf \'%s\\n\' \'{"type":"message_end","message":{"role":"assistant",'
        '"content":[{"type":"text","text":"done"}],'
        '"usage":{"input":11,"output":5,"cacheRead":2,"cacheWrite":0}}}\'\n'
    )
    pi.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env.pop("PI_AGENT_FACTORY_SESSION_ID", None)
    env.pop("PI_RUN_AGENT_DEPTH", None)
    return env


def _install_typebox_stub(target: Path) -> None:
    package = target / "node_modules/typebox"
    package.mkdir(parents=True)
    (package / "package.json").write_text(
        json.dumps({"name": "typebox", "type": "module", "exports": "./index.js"})
    )
    (package / "index.js").write_text(
        "export const Type = new Proxy({}, {get: () => (...args) => ({args})});\n"
    )


def _exercise_tool(
    target: Path, extension_name: str, params: dict, env: dict[str, str]
) -> None:
    extension = target / ".pi/extensions" / extension_name
    script = target / f"exercise-{extension_name}.mjs"
    script.write_text(
        f"""
import extension from {json.dumps(extension.as_uri())};
let tool;
extension({{registerTool(value) {{ tool = value; }}}});
const ctx = {{
  cwd: {json.dumps(str(target))},
  sessionManager: {{getSessionFile() {{ return '/sessions/pi-human-parent.jsonl'; }}}}
}};
const result = await tool.execute('call-1', {json.dumps(params)}, undefined, undefined, ctx);
if (result.details?.error) throw new Error(JSON.stringify(result));
"""
    )
    result = subprocess.run(
        ["node", "--experimental-strip-types", str(script)],
        cwd=target,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr


def test_RECON0006_installed_run_agent_persists_human_parent_and_depth(tmp_path):
    _init(tmp_path)
    _install_typebox_stub(tmp_path)
    env = _install_pi_stub(tmp_path)

    _exercise_tool(
        tmp_path,
        "run-agent.ts",
        {"agent": "developer-agent", "task": "test", "model": "test/model"},
        env,
    )

    child_files = list((tmp_path / ".agent-factory/usage").glob("pi-*.jsonl"))
    assert len(child_files) == 1
    record = json.loads(child_files[0].read_text())
    assert record["parent_session_id"] == "pi-human-parent"
    assert record["depth"] == 1


def test_RECON0006_installed_dispatch_wave_persists_human_parent_and_depth(tmp_path):
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "seed").write_text("seed\n")
    subprocess.run(["git", "add", "seed"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "seed"], cwd=tmp_path, check=True, capture_output=True
    )
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    _init(tmp_path)
    _install_typebox_stub(tmp_path)
    env = _install_pi_stub(tmp_path)

    _exercise_tool(
        tmp_path,
        "dispatch-wave.ts",
        {
            "target": "main",
            "merge": False,
            "items": [
                {
                    "task": "test",
                    "branch": "test/recon-0006",
                    "base": base,
                    "agent": "developer-agent",
                    "model": "test/model",
                }
            ],
        },
        env,
    )

    child_files = list((tmp_path / ".agent-factory/usage").glob("pi-*.jsonl"))
    assert len(child_files) == 1
    record = json.loads(child_files[0].read_text())
    assert record["parent_session_id"] == "pi-human-parent"
    assert record["depth"] == 1


def test_ST0044_capture_bridge_is_best_effort():
    bridge = (_ROOT / "factory/config/extensions/pi-usage.ts").read_text()
    assert "catch {" in bridge
    assert 'stdio: "ignore"' in bridge
