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


def _run_node(script: Path, *, cwd: Path, env: dict[str, str] | None = None) -> None:
    result = subprocess.run(
        ["node", "--experimental-strip-types", str(script)],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr


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


def test_RECON0009_linked_worktree_capture_uses_primary_checkout(tmp_path):
    primary = tmp_path / "primary"
    primary.mkdir()
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=primary, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=primary, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=primary, check=True)
    (primary / "seed").write_text("seed\n")
    subprocess.run(["git", "add", "seed"], cwd=primary, check=True)
    subprocess.run(
        ["git", "commit", "-m", "seed"], cwd=primary, check=True, capture_output=True
    )
    _init(primary)
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "worktree", "add", "-b", "test/linked", str(linked)],
        cwd=primary,
        check=True,
        capture_output=True,
    )

    extension = primary / ".pi/extensions/capture-usage.ts"
    script = primary / "exercise-linked.mjs"
    script.write_text(
        f"""
import extension from {json.dumps(extension.as_uri())};
let shutdown;
extension({{on(name, handler) {{ if (name === 'session_shutdown') shutdown = handler; }}}});
await shutdown({{type:'session_shutdown'}}, {{cwd:{json.dumps(str(linked))}, sessionManager:{{
  getSessionFile() {{ return '/sessions/pi-linked.jsonl'; }},
  getBranch() {{ return [{{type:'message',message:{{role:'assistant',content:[{{type:'text',text:'ok'}}],usage:{{input:3,output:1}}}}}}]; }}
}}}});
"""
    )
    _run_node(script, cwd=linked)

    assert _records(primary, "pi-linked")[0]["depth"] == 0
    assert not (linked / ".agent-factory/usage/pi-linked.jsonl").exists()


def test_RECON0009_untrusted_inherited_root_is_ignored(tmp_path):
    primary = tmp_path / "primary"
    attacker = tmp_path / "attacker"
    primary.mkdir()
    attacker.mkdir()
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=primary, check=True, capture_output=True
    )
    _init(primary)
    malicious = attacker / "factory/scripts/usage-capture"
    malicious.parent.mkdir(parents=True)
    malicious.write_text("#!/bin/sh\ntouch PWNED\n")
    malicious.chmod(0o755)
    bridge = primary / ".pi/extensions/pi-usage.ts"
    script = primary / "exercise-untrusted.mjs"
    script.write_text(
        f"""
import {{capturePiStream}} from {json.dumps(bridge.as_uri())};
capturePiStream({json.dumps(str(primary))}, '{{"type":"message_end","message":{{"role":"assistant","content":[{{"type":"text","text":"ok"}}],"usage":{{"input":3,"output":1}}}}}}', {{sessionId:'pi-safe'}});
"""
    )
    env = os.environ.copy()
    env["PI_AGENT_FACTORY_USAGE_ROOT"] = str(attacker)
    _run_node(script, cwd=primary, env=env)

    assert (primary / ".agent-factory/usage/pi-safe.jsonl").is_file()
    assert not (attacker / "PWNED").exists()


def test_RECON0009_nested_dispatch_records_survive_merged_worktree_removal(tmp_path):
    primary = tmp_path / "primary"
    primary.mkdir()
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=primary, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=primary, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=primary, check=True)
    (primary / "seed").write_text("seed\n")
    subprocess.run(["git", "add", "seed"], cwd=primary, check=True)
    subprocess.run(
        ["git", "commit", "-m", "seed"], cwd=primary, check=True, capture_output=True
    )
    _init(primary)
    # dispatch worktrees need the installed Factory runtime in their committed base.
    subprocess.run(["git", "add", "-f", "factory"], cwd=primary, check=True)
    subprocess.run(
        ["git", "commit", "-m", "install factory"],
        cwd=primary,
        check=True,
        capture_output=True,
    )
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=primary,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    _install_typebox_stub(primary)

    runner = primary / "fake-pi.mjs"
    runner.write_text(
        """
import {execFileSync} from 'node:child_process';
import {mkdirSync, writeFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import {join} from 'node:path';
const depth = Number.parseInt(process.env.PI_RUN_AGENT_DEPTH || '0', 10);
if (depth === 1) {
  execFileSync('factory/scripts/verify-base', ['main', '--expect-base', process.env.TEST_DISPATCH_BASE], {stdio:'ignore'});
  const pkg = join(process.cwd(), 'node_modules/typebox');
  mkdirSync(pkg, {recursive:true});
  writeFileSync(join(pkg, 'package.json'), JSON.stringify({name:'typebox',type:'module',exports:'./index.js'}));
  writeFileSync(join(pkg, 'index.js'), "export const Type=new Proxy({}, {get:()=> (...args)=>({args})});\\n");
  const {default: extension} = await import(pathToFileURL(join(process.cwd(), 'factory/config/extensions/run-agent.ts')));
  let tool;
  extension({registerTool(value) { tool = value; }});
  const result = await tool.execute('nested', {agent:'developer-agent',task:'nested',model:'test/model'}, undefined, undefined, {cwd:process.cwd()});
  if (result.details?.error) throw new Error(JSON.stringify(result));
  writeFileSync('nested-result.txt', 'done\\n');
  execFileSync('git', ['add', 'nested-result.txt']);
  execFileSync('git', ['-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'fix: nested result (RECON-0009)']);
}
process.stdout.write(JSON.stringify({type:'message_end',message:{role:'assistant',content:[{type:'text',text:'done'}],usage:{input:11,output:5,cacheRead:2,cacheWrite:0}}}) + '\\n');
"""
    )
    bin_dir = primary / "test-bin"
    bin_dir.mkdir()
    pi = bin_dir / "pi"
    pi.write_text(f'#!/bin/sh\nexec node {runner} "$@"\n')
    pi.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env.pop("PI_AGENT_FACTORY_SESSION_ID", None)
    env.pop("PI_RUN_AGENT_DEPTH", None)
    env.pop("PI_AGENT_FACTORY_USAGE_ROOT", None)
    env["TEST_DISPATCH_BASE"] = base

    _exercise_tool(
        primary,
        "dispatch-wave.ts",
        {
            "target": "main",
            "items": [
                {
                    "task": "outer",
                    "branch": "test/recon-0009",
                    "base": base,
                    "agent": "developer-agent",
                    "model": "test/model",
                    "scope": ["nested-result.txt"],
                }
            ],
        },
        env,
    )

    assert not (primary / ".agent-factory/worktrees/test-recon-0009").exists()
    records = [
        json.loads(path.read_text())
        for path in (primary / ".agent-factory/usage").glob("pi-*.jsonl")
    ]
    assert sorted(record["depth"] for record in records) == [1, 2]
    outer = next(record for record in records if record["depth"] == 1)
    nested = next(record for record in records if record["depth"] == 2)
    assert outer["parent_session_id"] == "pi-human-parent"
    assert nested["parent_session_id"] == outer["session_id"]
    for record in records:
        assert (primary / record["transcript_ref"]["path"]).is_file()


def test_ST0044_capture_bridge_is_best_effort():
    bridge = (_ROOT / "factory/config/extensions/pi-usage.ts").read_text()
    assert "catch {" in bridge
    assert 'stdio: "ignore"' in bridge
