"""Pi lifecycle transition and installed-entry smoke tests."""

# Existing result-inspection tests intentionally assert return codes after
# subprocess completion; new calls state check=False explicitly.
# ruff: noqa: PLW1510

from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import time
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_INIT = _ROOT / "factory/scripts/init-factory"
_REMOVE = _ROOT / "factory/scripts/remove-factory"
_REGISTRATION_ARTIFACT = re.compile(
    r"-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    r"(?:\.(?:pending|committing)\.json|\.completion\.json|\.jsonl)$"
)


def _init(target: Path) -> None:
    result = subprocess.run(
        [str(_INIT), "--target", str(target), "--source", str(_ROOT)],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr


def _records(target: Path, session: str) -> list[dict]:
    path = target / ".agent-factory/usage" / f"{session}.jsonl"
    _wait_for(path.is_file)
    _wait_for_terminal_capture(target)
    return [json.loads(line) for line in path.read_text().splitlines()]


def _init_git_repo(target: Path) -> str:
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=target, check=True, capture_output=True
    )
    (target / "seed").write_text("seed\n")
    subprocess.run(["git", "add", "seed"], cwd=target, check=True)
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
        cwd=target,
        check=True,
        capture_output=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=target,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def _wait_for(predicate, timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    assert predicate(), "condition did not become true before timeout"


def _pid_is_live(pid: int) -> bool:
    """Treat a reaped process or Linux zombie as terminated."""
    try:
        state = Path(f"/proc/{pid}/stat").read_text().split()[2]
        return state != "Z"
    except FileNotFoundError:
        return False


def _wait_for_terminal_capture(target: Path) -> None:
    pending = target / ".agent-factory/usage-control/pending"
    scratch = target / ".agent-factory/usage/.capture"
    control = target / ".agent-factory/usage-control"
    _wait_for(
        lambda: (
            (not pending.exists() or not list(pending.iterdir()))
            and (not scratch.exists() or not list(scratch.iterdir()))
            and not list(control.glob("*.completion.json"))
            and not list(control.glob("*.accepted.json"))
        )
    )


def _wait_for_no_registered_capture(target: Path) -> None:
    """Wait for real UUID registrations, ignoring synthetic fence fixtures."""
    pending = target / ".agent-factory/usage-control/pending"
    scratch = target / ".agent-factory/usage/.capture"
    control = target / ".agent-factory/usage-control"

    def registration_artifacts() -> list[Path]:
        paths = []
        for directory in (pending, scratch, control):
            if directory.is_dir():
                paths.extend(
                    path
                    for path in directory.iterdir()
                    if _REGISTRATION_ARTIFACT.search(path.name)
                )
        return paths

    _wait_for(lambda: not registration_artifacts())


@pytest.fixture(autouse=True)
def _settle_installed_pi_captures(tmp_path: Path):
    """Do not return a Pi E2E tmp tree while its supervisor can mutate it."""
    yield
    controls = [
        path
        for path in tmp_path.rglob("usage-control")
        if path.parent.name == ".agent-factory" and path.is_dir()
    ]
    for control in controls:
        _wait_for_no_registered_capture(control.parent.parent)


def _invoke_direct_pi_capture(target: Path, session: str) -> None:
    bridge = target / ".pi/extensions/pi-usage.ts"
    exercise = target / f"exercise-{session}.mjs"
    exercise.write_text(
        f"""
import {{capturePiStream}} from {json.dumps(bridge.as_uri())};
capturePiStream({json.dumps(str(target))}, '{{"type":"message_end","message":{{"role":"assistant","content":[{{"type":"text","text":"ok"}}],"usage":{{"input":3,"output":1}}}}}}', {{sessionId:{json.dumps(session)}}});
"""
    )
    _run_node(exercise, cwd=target, timeout=3)


def _diagnostics(target: Path) -> list[Path]:
    directory = target / ".agent-factory/usage-control/diagnostics"
    return list(directory.glob("*.json")) if directory.is_dir() else []


def _run_node(
    script: Path,
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: float = 60,
) -> None:
    result = subprocess.run(
        ["node", "--experimental-strip-types", str(script)],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    assert result.returncode == 0, result.stderr


def test_omitted_transcript_keeps_totals_without_persisting_text(tmp_path):
    result = subprocess.run(
        [
            str(_INIT),
            "--target",
            str(tmp_path),
            "--source",
            str(_ROOT),
            "--usage-transcript-retention",
            "omit",
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    bridge = tmp_path / ".pi/extensions/pi-usage.ts"
    exercise = tmp_path / "exercise-pi-omit.mjs"
    secret = "PI_UNIQUE_SECRET_CONTENT"
    exercise.write_text(
        f"""
import {{capturePiStream}} from {json.dumps(bridge.as_uri())};
capturePiStream({json.dumps(str(tmp_path))}, '{{"type":"message_end","message":{{"role":"assistant","content":[{{"type":"text","text":{json.dumps(secret)}}}],"usage":{{"input":9,"output":4}}}}}}', {{sessionId:'pi-omit'}});
"""
    )
    _run_node(exercise, cwd=tmp_path)

    record = _records(tmp_path, "pi-omit")[0]
    evidence = tmp_path / record["transcript_ref"]["path"]
    assert record["reported_input"] == 9
    assert record["reported_output"] == 4
    assert record["normalized_total"] > 0
    assert record["transcript_ref"]["span"] == "content-omitted"
    assert evidence.read_bytes() == b""
    _wait_for(lambda: not list((tmp_path / ".agent-factory/usage/.capture").iterdir()))
    assert all(
        secret not in path.read_text(errors="ignore")
        for path in (tmp_path / ".agent-factory").rglob("*")
        if path.is_file()
    )


def test_install_then_remove_preserves_project_pi_content(tmp_path):
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
    target: Path,
    extension_name: str,
    params: dict,
    env: dict[str, str],
    *,
    timeout: float = 60,
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
        timeout=timeout,
    )
    assert result.returncode == 0, result.stderr


def test_BUG_0004_UC_10_run_agent_streams_more_than_64_mib(tmp_path):
    target = tmp_path / "consumer"
    target.mkdir()
    _init_git_repo(target)
    _init(target)
    _install_typebox_stub(target)
    capture_runtime = target / "factory/scripts/usage-capture-runtime"
    real_capture_runtime = capture_runtime.with_name("usage-capture-runtime-real")
    capture_runtime.rename(real_capture_runtime)
    captured_size = target / "captured-raw-size"
    capture_runtime.write_text(
        "#!/usr/bin/env python3\n"
        "import os, pathlib, sys\n"
        "source = pathlib.Path(sys.argv[sys.argv.index('--transcript') + 1])\n"
        f"pathlib.Path({str(captured_size)!r}).write_text(str(source.stat().st_size))\n"
        f"os.execv({str(real_capture_runtime)!r}, [{str(real_capture_runtime)!r}, *sys.argv[1:]])\n"
    )
    capture_runtime.chmod(0o755)

    bin_dir = target / "test-bin"
    bin_dir.mkdir()
    pi = bin_dir / "pi"
    pi.write_text(
        """#!/usr/bin/env node
import {writeSync} from 'node:fs';
const payload = JSON.stringify({type:'message_update',delta:'x'.repeat(32 * 1024)}) + '\\n';
for (let i = 0; i < 2100; i++) {
  writeSync(1, payload);
}
const final = JSON.stringify({type:'message_end',message:{role:'assistant',content:[{type:'text',text:'streamed result'}],usage:{input:11,output:5}}}) + '\\n';
for (let offset = 0; offset < final.length; offset += 7) {
  writeSync(1, final.slice(offset, offset + 7));
}
"""
    )
    pi.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env.pop("PI_AGENT_FACTORY_SESSION_ID", None)
    env.pop("PI_RUN_AGENT_DEPTH", None)
    env.pop("PI_AGENT_FACTORY_USAGE_ROOT", None)

    extension = target / ".pi/extensions/run-agent.ts"
    script = target / "exercise-large-run-agent.mjs"
    script.write_text(
        f"""
import extension from {json.dumps(extension.as_uri())};
let tool;
extension({{registerTool(value) {{ tool = value; }}}});
let updateCount = 0;
let largestUpdate = 0;
const result = await tool.execute(
  'call-large',
  {{agent:'developer-agent', task:'large', model:'test/model'}},
  undefined,
  update => {{
    updateCount++;
    largestUpdate = Math.max(largestUpdate, JSON.stringify(update).length);
  }},
  {{
    cwd:{json.dumps(str(target))},
    sessionManager:{{getSessionFile() {{ return '/sessions/pi-human-parent.jsonl'; }}}},
  }},
);
if (result.details?.error) throw new Error(JSON.stringify(result));
if (result.content[0].text !== 'streamed result') throw new Error(JSON.stringify(result));
if (updateCount < 2 || largestUpdate > 4096) throw new Error(JSON.stringify({{updateCount, largestUpdate}}));
"""
    )
    result = subprocess.run(
        ["node", "--experimental-strip-types", str(script)],
        cwd=target,
        env=env,
        text=True,
        capture_output=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    usage_dir = target / ".agent-factory/usage"
    runtime = target / ".agent-factory/usage-runtime"
    if not (runtime / ".requirements-sha256").is_file():
        # Usage capture is explicitly best-effort when offline initialization
        # could not provision its runtime; the streamed agent result above
        # must remain successful in that state.
        assert not list(usage_dir.glob("pi-*.jsonl"))
        return
    _wait_for(lambda: len(list(usage_dir.glob("pi-*.jsonl"))) == 1, timeout=30)
    record_path = next(usage_dir.glob("pi-*.jsonl"))
    record = json.loads(record_path.read_text().splitlines()[0])
    assert record["reported_input"] == 11
    _wait_for(captured_size.is_file)
    assert int(captured_size.read_text()) > 64 * 1024 * 1024


def test_BUG_0004_UC_10_run_agent_cancellation_terminates_and_cleans(tmp_path):
    target = tmp_path / "consumer"
    target.mkdir()
    _init_git_repo(target)
    _init(target)
    _install_typebox_stub(target)

    started = target / "child-started"
    child_pid = target / "child-pid"
    descendant_pid = target / "descendant-pid"
    spawn_count = target / "spawn-count"
    bin_dir = target / "test-bin"
    bin_dir.mkdir()
    pi = bin_dir / "pi"
    pi.write_text(
        f"""#!/usr/bin/env node
import {{appendFileSync, writeFileSync}} from 'node:fs';
import {{spawn}} from 'node:child_process';
appendFileSync({json.dumps(str(spawn_count))}, 'spawn\\n');
writeFileSync({json.dumps(str(started))}, '');
writeFileSync({json.dumps(str(child_pid))}, String(process.pid));
const descendant = spawn(process.execPath, ['-e', `
  process.on('SIGTERM', () => {{}});
  setInterval(() => process.stdout.write('held\\\\n'), 10);
`], {{stdio:['ignore', process.stdout, process.stderr]}});
writeFileSync({json.dumps(str(descendant_pid))}, String(descendant.pid));
process.on('SIGTERM', () => {{
  // Deliberately non-cooperative: cancellation must escalate.
}});
setInterval(() => process.stdout.write('{{"type":"message_update"}}\\n'), 10);
"""
    )
    pi.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    extension = target / ".pi/extensions/run-agent.ts"
    script = target / "exercise-cancelled-run-agent.mjs"
    script.write_text(
        f"""
import {{existsSync}} from 'node:fs';
import extension from {json.dumps(extension.as_uri())};
let tool;
extension({{registerTool(value) {{ tool = value; }}}});
const controller = new AbortController();
const startedAt = Date.now();
const timer = setInterval(() => {{
  if (existsSync({json.dumps(str(started))})) {{
    clearInterval(timer);
    controller.abort();
  }}
}}, 10);
const result = await tool.execute(
  'call-cancel',
  {{agent:'developer-agent', task:'cancel', model:'test/model'}},
  controller.signal,
  undefined,
  {{cwd:{json.dumps(str(target))}}},
);
clearInterval(timer);
const elapsedMs = Date.now() - startedAt;
if (!result.details?.error || !String(result.details.reason).includes('cancelled')) {{
  throw new Error(JSON.stringify(result));
}}
if (elapsedMs > 2000) throw new Error(`cancellation took ${{elapsedMs}}ms`);
"""
    )
    try:
        result = subprocess.run(
            ["node", "--experimental-strip-types", str(script)],
            cwd=target,
            env=env,
            text=True,
            capture_output=True,
            timeout=3,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert spawn_count.read_text().splitlines() == ["spawn"]
        pids = [int(pid_file.read_text()) for pid_file in (child_pid, descendant_pid)]
        _wait_for(lambda: not any(_pid_is_live(pid) for pid in pids), timeout=1)
        assert not list((target / ".agent-factory/usage/.capture").iterdir())
        assert not list((target / ".agent-factory/usage").glob("pi-*.jsonl"))
    finally:
        # A red implementation can orphan both deliberately non-cooperative
        # processes. Keep the regression itself bounded and self-cleaning.
        for pid_file in (child_pid, descendant_pid):
            if pid_file.is_file():
                try:
                    os.kill(int(pid_file.read_text()), 9)
                except ProcessLookupError:
                    pass


def test_FAGAN_0010_UC_10_cancellation_destroy_fallback_settles_pipes(tmp_path):
    target = tmp_path / "consumer"
    target.mkdir()
    _init_git_repo(target)
    _init(target)
    _install_typebox_stub(target)

    started = target / "child-started"
    escaped_pid = target / "escaped-descendant-pid"
    bin_dir = target / "test-bin"
    bin_dir.mkdir()
    pi = bin_dir / "pi"
    pi.write_text(
        f"""#!/usr/bin/env node
import {{writeFileSync}} from 'node:fs';
import {{spawn}} from 'node:child_process';
const escaped = spawn(process.execPath, ['-e', `
  process.on('SIGTERM', () => {{}});
  setInterval(() => process.stdout.write('held\\\\n'), 10);
`], {{detached:true, stdio:['ignore', process.stdout, process.stderr]}});
writeFileSync({json.dumps(str(escaped_pid))}, String(escaped.pid));
writeFileSync({json.dumps(str(started))}, '');
process.on('SIGTERM', () => {{}});
setInterval(() => process.stdout.write('{{"type":"message_update"}}\\n'), 10);
"""
    )
    pi.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    extension = target / ".pi/extensions/run-agent.ts"
    script = target / "exercise-destroy-fallback.mjs"
    script.write_text(
        f"""
import {{existsSync}} from 'node:fs';
import extension from {json.dumps(extension.as_uri())};
let tool;
extension({{registerTool(value) {{ tool = value; }}}});
const controller = new AbortController();
const timer = setInterval(() => {{
  if (existsSync({json.dumps(str(started))})) {{
    clearInterval(timer);
    controller.abort();
  }}
}}, 10);
const startedAt = Date.now();
const result = await tool.execute(
  'call-destroy-fallback',
  {{agent:'developer-agent', task:'cancel', model:'test/model'}},
  controller.signal,
  undefined,
  {{cwd:{json.dumps(str(target))}}},
);
clearInterval(timer);
if (!result.details?.cancelled) throw new Error(JSON.stringify(result));
if (Date.now() - startedAt > 1500) throw new Error('pipe fallback exceeded bound');
"""
    )
    try:
        result = subprocess.run(
            ["node", "--experimental-strip-types", str(script)],
            cwd=target,
            env=env,
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert not list((target / ".agent-factory/usage/.capture").iterdir())
    finally:
        if escaped_pid.is_file():
            try:
                os.kill(int(escaped_pid.read_text()), 9)
            except ProcessLookupError:
                pass


def _install_gated_capture(target: Path, env: dict[str, str]) -> tuple[Path, Path]:
    script = target / "factory/scripts/usage-capture-runtime"
    real = script.with_name("usage-capture-real")
    script.rename(real)
    started = target / "capture-started"
    gate = target / "capture-release"
    script.write_text(
        "#!/bin/sh\n"
        'touch "$RECON_CAPTURE_STARTED"\n'
        'while [ ! -e "$RECON_CAPTURE_GATE" ]; do sleep 0.05; done\n'
        f'exec {real} "$@"\n'
    )
    script.chmod(0o755)
    env["RECON_CAPTURE_STARTED"] = str(started)
    env["RECON_CAPTURE_GATE"] = str(gate)
    return started, gate


def _install_registration_barrier(
    target: Path, env: dict[str, str]
) -> tuple[Path, Path]:
    """Pause old state-read fencing or new hard-link fencing at the race."""
    started = target / "registration-started"
    gate = target / "registration-release"
    preload = target / "registration-barrier.cjs"
    preload.write_text(
        f"""
const fs = require('node:fs');
const moduleApi = require('node:module');
const started = {json.dumps(str(started))};
const gate = {json.dumps(str(gate))};
let blocked = false;
function barrier() {{
  if (blocked) return;
  blocked = true;
  fs.writeFileSync(started, '');
  while (!fs.existsSync(gate)) Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 10);
}}
const originalRead = fs.readFileSync;
fs.readFileSync = function(path, ...args) {{
  const value = originalRead.call(fs, path, ...args);
  if (String(path).endsWith('/usage-control/state.json')) {{
    try {{ if (JSON.parse(String(value)).mode === 'active') barrier(); }} catch {{}}
  }}
  return value;
}};
const originalLink = fs.linkSync;
fs.linkSync = function(...args) {{
  const value = originalLink.apply(fs, args);
  barrier();
  return value;
}};
moduleApi.syncBuiltinESMExports();
"""
    )
    prior = env.get("NODE_OPTIONS", "")
    env["NODE_OPTIONS"] = f"{prior} --require={preload}".strip()
    return started, gate


def _release_capture_and_assert_cleanup(target: Path, gate: Path, session: str) -> dict:
    gate.touch()
    records = _records(target, session)
    assert len(records) == 1
    record = records[0]
    scratch = target / ".agent-factory/usage/.capture"
    _wait_for(lambda: not scratch.exists() or not list(scratch.iterdir()))
    assert (target / record["transcript_ref"]["path"]).is_file()
    return record


def _start_stalled_direct_capture(target: Path, session: str):
    env = os.environ.copy()
    started, gate = _install_gated_capture(target, env)
    bridge = target / ".pi/extensions/pi-usage.ts"
    exercise = target / f"exercise-{session}.mjs"
    exercise.write_text(
        f"""
import {{capturePiStream}} from {json.dumps(bridge.as_uri())};
capturePiStream({json.dumps(str(target))}, '{{"type":"message_end","message":{{"role":"assistant","content":[{{"type":"text","text":"ok"}}],"usage":{{"input":3,"output":1}}}}}}', {{sessionId:{json.dumps(session)}}});
"""
    )
    _run_node(exercise, cwd=target, env=env, timeout=3)
    _wait_for(started.is_file)
    pending = target / ".agent-factory/usage-control/pending"
    _wait_for(lambda: len(list(pending.iterdir())) == 1)
    return gate, pending


def test_registered_capture_drains_before_teardown(tmp_path):
    _init(tmp_path)
    gate, _pending = _start_stalled_direct_capture(tmp_path, "pi-remove-drain")
    remover = subprocess.Popen(
        [str(_REMOVE), "--target", str(tmp_path), "--pending-timeout", "5"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    state = tmp_path / ".agent-factory/usage-control/state.json"
    _wait_for(lambda: json.loads(state.read_text())["mode"] == "drain")
    assert remover.poll() is None

    gate.touch()
    stdout, stderr = remover.communicate(timeout=10)
    assert remover.returncode == 0, stderr
    assert "Agent Factory removed" in stdout
    assert not (tmp_path / ".agent-factory").exists()
    time.sleep(0.1)
    assert not (tmp_path / ".agent-factory").exists()


@pytest.mark.skipif(os.name != "posix", reason="POSIX mode bits required")
def test_registered_capture_staging_and_control_paths_are_private(tmp_path):
    _init(tmp_path)
    gate, pending = _start_stalled_direct_capture(tmp_path, "pi-private-modes")
    control = tmp_path / ".agent-factory/usage-control"
    scratch = tmp_path / ".agent-factory/usage/.capture"
    marker = next(pending.iterdir())
    staged = next(scratch.iterdir())

    for directory in (control, pending, scratch):
        assert stat.S_IMODE(directory.stat().st_mode) == 0o700
    for file in (control / "state.json", control / "config.json", marker, staged):
        assert stat.S_IMODE(file.stat().st_mode) == 0o600

    gate.touch()
    _records(tmp_path, "pi-private-modes")
    _wait_for(lambda: not list(scratch.iterdir()))


def test_registration_snapshot_closes_pre_marker_removal_race(tmp_path):
    _init(tmp_path)
    env = os.environ.copy()
    capture_started, capture_gate = _install_gated_capture(tmp_path, env)
    registration_started, registration_gate = _install_registration_barrier(
        tmp_path, env
    )
    bridge = tmp_path / ".pi/extensions/pi-usage.ts"
    exercise = tmp_path / "exercise-registration-race.mjs"
    exercise.write_text(
        f"""
import {{capturePiStream}} from {json.dumps(bridge.as_uri())};
capturePiStream({json.dumps(str(tmp_path))}, '{{"type":"message_end","message":{{"role":"assistant","content":[{{"type":"text","text":"race"}}],"usage":{{"input":3,"output":1}}}}}}', {{sessionId:'pi-registration-race'}});
"""
    )
    capture = subprocess.Popen(
        ["node", "--experimental-strip-types", str(exercise)],
        cwd=tmp_path,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _wait_for(registration_started.is_file)
    remover = subprocess.Popen(
        [str(_REMOVE), "--target", str(tmp_path), "--pending-timeout", "5"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    state = tmp_path / ".agent-factory/usage-control/state.json"
    _wait_for(
        lambda: (
            remover.poll() is not None
            or (state.is_file() and json.loads(state.read_text())["mode"] == "drain")
        )
    )
    pending = tmp_path / ".agent-factory/usage-control/pending"
    _wait_for(
        lambda: (
            remover.poll() is not None
            or (pending.is_dir() and bool(list(pending.iterdir())))
        )
    )
    removal_waited_for_token = (
        remover.poll() is None and pending.is_dir() and bool(list(pending.iterdir()))
    )
    registration_gate.touch()
    if removal_waited_for_token:
        _wait_for(capture_started.is_file)
        assert remover.poll() is None
        capture_gate.touch()
    capture_stdout, capture_stderr = capture.communicate(timeout=10)
    remover_stdout, remover_stderr = remover.communicate(timeout=10)

    assert removal_waited_for_token
    assert capture.returncode == 0, capture_stderr or capture_stdout
    assert remover.returncode == 0, remover_stderr or remover_stdout
    assert not (tmp_path / ".agent-factory").exists()
    time.sleep(0.1)
    assert not (tmp_path / ".agent-factory").exists()


def test_drain_timeout_restores_active_installation(tmp_path):
    _init(tmp_path)
    gate, _pending = _start_stalled_direct_capture(tmp_path, "pi-remove-timeout")
    result = subprocess.run(
        [
            str(_REMOVE),
            "--target",
            str(tmp_path),
            "--pending-timeout",
            "0.1",
        ],
        text=True,
        capture_output=True,
        timeout=3,
    )
    assert result.returncode == 1
    assert (tmp_path / ".agent-factory/factory-install.json").is_file()
    state = json.loads(
        (tmp_path / ".agent-factory/usage-control/state.json").read_text()
    )
    assert state["mode"] == "active"
    assert (tmp_path / ".pi/extensions/capture-usage.ts").is_symlink()

    gate.touch()
    assert _records(tmp_path, "pi-remove-timeout")


def test_stale_active_snapshot_aborts_drain_and_restores_active(tmp_path):
    _init(tmp_path)
    control = tmp_path / ".agent-factory/usage-control"
    token = control / "pending/stale-active.pending.json"
    os.link(control / "state.json", token)

    result = subprocess.run(
        [str(_REMOVE), "--target", str(tmp_path), "--pending-timeout", "0.1"],
        text=True,
        capture_output=True,
        timeout=3,
    )

    assert result.returncode == 1
    assert token.is_file()
    assert json.loads((control / "state.json").read_text())["mode"] == "active"


def test_cancel_discards_active_snapshot_token(tmp_path):
    _init(tmp_path)
    control = tmp_path / ".agent-factory/usage-control"
    token = control / "pending/stale-active.pending.json"
    os.link(control / "state.json", token)

    result = subprocess.run(
        [str(_REMOVE), "--target", str(tmp_path), "--pending-usage", "cancel"],
        text=True,
        capture_output=True,
        timeout=3,
    )

    assert result.returncode == 0, result.stderr
    assert "cancelled 1 pending usage capture" in result.stdout
    assert not (tmp_path / ".agent-factory").exists()


def test_unsupported_hardlinks_report_registration_limitation(tmp_path):
    _init(tmp_path)
    preload = tmp_path / "unsupported-hardlink.cjs"
    preload.write_text(
        """
const fs = require('node:fs');
const moduleApi = require('node:module');
fs.linkSync = function() {
  const error = new Error('hard links unsupported');
  error.code = 'EOPNOTSUPP';
  throw error;
};
moduleApi.syncBuiltinESMExports();
"""
    )
    env = os.environ.copy()
    env["NODE_OPTIONS"] = f"--require={preload}"
    bridge = tmp_path / ".pi/extensions/pi-usage.ts"
    exercise = tmp_path / "exercise-unsupported-hardlink.mjs"
    exercise.write_text(
        f"""
import {{capturePiStream}} from {json.dumps(bridge.as_uri())};
capturePiStream({json.dumps(str(tmp_path))}, '{{"type":"message_end","message":{{"role":"assistant","content":"x"}}}}', {{sessionId:'pi-no-hardlink'}});
"""
    )

    result = subprocess.run(
        ["node", "--experimental-strip-types", str(exercise)],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        timeout=5,
    )

    assert result.returncode == 0
    assert "Pi usage capture unavailable" in result.stderr
    assert not list((tmp_path / ".agent-factory/usage-control/pending").iterdir())


def test_explicit_cancel_prevents_late_resurrection(tmp_path):
    user_file = tmp_path / ".github/workflows/user.yml"
    user_file.parent.mkdir(parents=True, exist_ok=True)
    user_file.write_text("user-owned\n")
    _init(tmp_path)
    gate, _pending = _start_stalled_direct_capture(tmp_path, "pi-remove-cancel")
    result = subprocess.run(
        [
            str(_REMOVE),
            "--target",
            str(tmp_path),
            "--pending-usage",
            "cancel",
            "--pending-timeout",
            "2",
        ],
        text=True,
        capture_output=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert "cancelled 1 pending usage capture" in result.stdout
    assert user_file.read_text() == "user-owned\n"

    gate.touch()
    time.sleep(0.2)
    assert not (tmp_path / ".agent-factory").exists()
    again = subprocess.run(
        [str(_REMOVE), "--target", str(tmp_path)], text=True, capture_output=True
    )
    assert again.returncode == 0


def test_registration_rejects_removal_fence_without_recreation(tmp_path):
    _init(tmp_path)
    state_path = tmp_path / ".agent-factory/usage-control/state.json"
    state = json.loads(state_path.read_text())
    state_path.write_text(json.dumps({**state, "mode": "cancel"}) + "\n")
    bridge = tmp_path / ".pi/extensions/pi-usage.ts"
    exercise = tmp_path / "exercise-fenced.mjs"
    exercise.write_text(
        f"""
import {{capturePiStream}} from {json.dumps(bridge.as_uri())};
capturePiStream({json.dumps(str(tmp_path))}, '{{"type":"message_end","message":{{"role":"assistant","content":[{{"type":"text","text":"ok"}}],"usage":{{"input":3,"output":1}}}}}}', {{sessionId:'pi-fenced'}});
"""
    )
    _run_node(exercise, cwd=tmp_path, timeout=3)
    assert not list((tmp_path / ".agent-factory/usage-control/pending").iterdir())
    assert not list((tmp_path / ".agent-factory/usage/.capture").iterdir())
    assert _diagnostics(tmp_path) == []


def test_cancel_does_not_follow_malformed_registry_paths(tmp_path):
    _init(tmp_path)
    outside = tmp_path / "user-data.txt"
    outside.write_text("keep\n")
    pending = tmp_path / ".agent-factory/usage-control/pending"
    (pending / "stale.pending.json").write_text(
        json.dumps({"staged_source": str(outside), "generation": "stale"})
    )
    (pending / "malformed.pending.json").write_text("not json\n")

    result = subprocess.run(
        [str(_REMOVE), "--target", str(tmp_path), "--pending-usage", "cancel"],
        text=True,
        capture_output=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert outside.read_text() == "keep\n"


def test_committing_marker_causes_bounded_abort(tmp_path):
    _init(tmp_path)
    pending = tmp_path / ".agent-factory/usage-control/pending"
    committing = pending / "stalled.committing.json"
    committing.write_text("{}\n")
    result = subprocess.run(
        [
            str(_REMOVE),
            "--target",
            str(tmp_path),
            "--pending-usage",
            "cancel",
            "--pending-timeout",
            "0.1",
        ],
        text=True,
        capture_output=True,
        timeout=3,
    )
    assert result.returncode == 1
    assert (tmp_path / ".agent-factory/factory-install.json").is_file()
    assert (
        json.loads((tmp_path / ".agent-factory/usage-control/state.json").read_text())[
            "mode"
        ]
        == "active"
    )


def test_human_shutdown_is_idempotent_and_returns_while_capture_is_stalled(tmp_path):
    _init(tmp_path)
    env = os.environ.copy()
    started, gate = _install_gated_capture(tmp_path, env)
    extension = tmp_path / ".pi/extensions/capture-usage.ts"
    exercise = tmp_path / "exercise-stalled-human.mjs"
    exercise.write_text(
        f"""
import extension from {json.dumps(extension.as_uri())};
let shutdown;
extension({{on(name, handler) {{ if (name === 'session_shutdown') shutdown = handler; }}}});
const ctx = {{cwd:{json.dumps(str(tmp_path))},sessionManager:{{
  getSessionFile() {{ return '/sessions/pi-stalled-human.jsonl'; }},
  getBranch() {{ return [
    {{type:'message',message:{{role:'user',content:'ASK'}}}},
    {{type:'message',message:{{role:'assistant',content:[{{type:'text',text:'ANSWER'}}],usage:{{input:7,output:3}}}}}}
  ]; }}
}}}};
await shutdown({{type:'session_shutdown'}}, ctx);
await shutdown({{type:'session_shutdown'}}, ctx);
"""
    )

    _run_node(exercise, cwd=tmp_path, env=env, timeout=3)
    _wait_for(started.is_file)
    assert not (tmp_path / ".agent-factory/usage/pi-stalled-human.jsonl").exists()
    record = _release_capture_and_assert_cleanup(tmp_path, gate, "pi-stalled-human")
    assert record["agent"] == "human"
    assert record["reported_input"] == 7
    assert record["reported_output"] == 3
    assert "ASK" in (tmp_path / record["transcript_ref"]["path"]).read_text()
    assert _diagnostics(tmp_path) == []


def test_BUG_0005_UC_10_human_shutdown_captures_full_session_file_events(tmp_path):
    _init(tmp_path)
    env = os.environ.copy()
    started, gate = _install_gated_capture(tmp_path, env)
    # A real Pi session file carries the full event stream: a session header,
    # a model change, user/assistant/toolResult `type:"message"` events, and
    # assistant messages whose `usage` is the final per-turn usage. The reduced
    # `getBranch()` stream omits thinking, tool calls, and tool results, so a
    # capture that only sees getBranch() tokenizes a tiny fraction of the run.
    session_file = tmp_path / "sessions" / "pi-root-rich.jsonl"
    session_file.parent.mkdir(parents=True)
    session_file.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "session",
                        "version": 3,
                        "id": "pi-root-rich",
                        "cwd": str(tmp_path),
                    }
                ),
                json.dumps(
                    {"type": "model_change", "id": "m1", "modelId": "z-ai/glm-5.2"}
                ),
                json.dumps(
                    {
                        "type": "message",
                        "message": {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "please do the thing"}
                            ],
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "message",
                        "message": {
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "thinking",
                                    "thinking": "PLAN_MARKER_REASONING_DETAILED_TRAIL",
                                },
                                {
                                    "type": "toolCall",
                                    "name": "read",
                                    "arguments": {"path": "x"},
                                },
                            ],
                            "model": "z-ai/glm-5.2",
                            "usage": {
                                "input": 5000,
                                "output": 40,
                                "cacheRead": 0,
                                "cacheWrite": 0,
                            },
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "message",
                        "message": {
                            "role": "toolResult",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "TOOL_RESULT_MARKER_PAYLOAD_TRAIL",
                                }
                            ],
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "message",
                        "message": {
                            "role": "assistant",
                            "content": [{"type": "text", "text": "done"}],
                            "model": "z-ai/glm-5.2",
                            "usage": {
                                "input": 6000,
                                "output": 5,
                                "cacheRead": 0,
                                "cacheWrite": 0,
                            },
                        },
                    }
                ),
            ]
        )
        + "\n"
    )
    extension = tmp_path / ".pi/extensions/capture-usage.ts"
    exercise = tmp_path / "exercise-bug-0005-human.mjs"
    exercise.write_text(
        f"""
import extension from {json.dumps(extension.as_uri())};
let shutdown;
extension({{on(name, handler) {{ if (name === 'session_shutdown') shutdown = handler;}}}});
const ctx = {{cwd:{json.dumps(str(tmp_path))},sessionManager:{{
  getSessionFile() {{ return {json.dumps(str(session_file))}; }},
  getBranch() {{ return [
    {{type:'message',message:{{role:'user',content:'please do the thing'}}}},
    {{type:'message',message:{{role:'assistant',content:[{{type:'text',text:'done'}}],usage:{{input:7,output:3}}}}}}
  ]; }}
}}}};
await shutdown({{type:'session_shutdown'}}, ctx);
"""
    )
    _run_node(exercise, cwd=tmp_path, env=env, timeout=3)
    _wait_for(started.is_file)
    record = _release_capture_and_assert_cleanup(tmp_path, gate, "pi-root-rich")
    # Reported usage sums the assistant `message` turns (5000 + 6000, 40 + 5).
    assert record["agent"] == "human"
    assert record["model"] == "z-ai/glm-5.2"
    assert record["reported_input"] == 11000
    assert record["reported_output"] == 45
    assert record["usage_granularity"] == "full"
    # The normalized yardstick must reflect the full event stream, not the
    # reduced getBranch() rendering: thinking and tool-result text must be
    # tokenized and persisted, so the transcript and normalized totals carry
    # them rather than only the visible "please do the thing" / "done".
    transcript_text = (tmp_path / record["transcript_ref"]["path"]).read_text()
    assert "PLAN_MARKER_REASONING_DETAILED_TRAIL" in transcript_text
    assert "TOOL_RESULT_MARKER_PAYLOAD_TRAIL" in transcript_text
    visible_only = "please do the thing\ndone"
    assert record["normalized_total"] > len(visible_only)
    assert _diagnostics(tmp_path) == []


def test_BUG_0006_UC_10_root_record_uses_model_conf_canonical_id(tmp_path):
    _init(tmp_path)
    env = os.environ.copy()
    started, gate = _install_gated_capture(tmp_path, env)
    # Pi's session file reports the provider-native model id (e.g.
    # `z-ai/glm-5.2`), but model.conf stores the canonical row value with the
    # OpenRouter prefix (`openrouter/z-ai/glm-5.2`). The subagent path passes
    # the model.conf id via --model, so its record carries the canonical id;
    # the root path must attribute the same canonical id so usage can be grouped
    # by `model` across both paths instead of splitting one model in two.
    model_conf = tmp_path / "config" / "model.conf"
    model_conf.parent.mkdir(parents=True, exist_ok=True)
    model_conf.write_text(
        "[facts]\npi.strong = openrouter/z-ai/glm-5.2\non_missing = halt\n"
    )
    session_file = tmp_path / "sessions" / "pi-root-canonical.jsonl"
    session_file.parent.mkdir(parents=True)
    session_file.write_text(
        "\n".join(
            [
                json.dumps(
                    {"type": "session", "version": 3, "id": "pi-root-canonical"}
                ),
                json.dumps(
                    {
                        "type": "message",
                        "message": {
                            "role": "assistant",
                            "content": [{"type": "text", "text": "done"}],
                            # Pi reports the bare provider id, not the
                            # model.conf row value.
                            "model": "z-ai/glm-5.2",
                            "usage": {
                                "input": 10,
                                "output": 2,
                                "cacheRead": 0,
                                "cacheWrite": 0,
                            },
                        },
                    }
                ),
            ]
        )
        + "\n"
    )
    extension = tmp_path / ".pi/extensions/capture-usage.ts"
    exercise = tmp_path / "exercise-bug-0006-human.mjs"
    exercise.write_text(
        f"""
import extension from {json.dumps(extension.as_uri())};
let shutdown;
extension({{on(name, handler) {{ if (name === 'session_shutdown') shutdown = handler;}}}});
const ctx = {{cwd:{json.dumps(str(tmp_path))},sessionManager:{{
  getSessionFile() {{ return {json.dumps(str(session_file))}; }},
  getBranch() {{ return [
    {{type:'message',message:{{role:'assistant',content:[{{type:'text',text:'done'}}],model:'z-ai/glm-5.2',usage:{{input:10,output:2}}}}}}
  ]; }}
}}}};
await shutdown({{type:'session_shutdown'}}, ctx);
"""
    )
    _run_node(exercise, cwd=tmp_path, env=env, timeout=3)
    _wait_for(started.is_file)
    record = _release_capture_and_assert_cleanup(tmp_path, gate, "pi-root-canonical")
    # The root record must carry the model.conf canonical id, matching what a
    # subagent run_agent record would emit for the same pi.strong tier — not
    # the bare provider id Pi reports in the transcript.
    assert record["model"] == "openrouter/z-ai/glm-5.2", record
    assert _diagnostics(tmp_path) == []


def test_run_agent_returns_while_capture_is_stalled(tmp_path):
    _init(tmp_path)
    _install_typebox_stub(tmp_path)
    env = _install_pi_stub(tmp_path)
    started, gate = _install_gated_capture(tmp_path, env)

    _exercise_tool(
        tmp_path,
        "run-agent.ts",
        {"agent": "developer-agent", "task": "test", "model": "test/model"},
        env,
        timeout=3,
    )
    _wait_for(started.is_file)
    assert not list((tmp_path / ".agent-factory/usage").glob("pi-*.jsonl"))
    gate.touch()
    _wait_for(
        lambda: len(list((tmp_path / ".agent-factory/usage").glob("pi-*.jsonl"))) == 1
    )
    record = json.loads(
        next((tmp_path / ".agent-factory/usage").glob("pi-*.jsonl")).read_text()
    )
    _wait_for(lambda: not list((tmp_path / ".agent-factory/usage/.capture").iterdir()))
    assert record["parent_session_id"] == "pi-human-parent"
    assert record["depth"] == 1


def test_dispatch_wave_returns_while_capture_is_stalled(tmp_path):
    base = _init_git_repo(tmp_path)
    _init(tmp_path)
    _install_typebox_stub(tmp_path)
    env = _install_pi_stub(tmp_path)
    started, gate = _install_gated_capture(tmp_path, env)

    _exercise_tool(
        tmp_path,
        "dispatch-wave.ts",
        {
            "target": "main",
            "merge": False,
            "items": [
                {
                    "task": "test",
                    "branch": "test/recon-0010",
                    "base": base,
                    "agent": "developer-agent",
                    "model": "test/model",
                }
            ],
        },
        env,
        timeout=3,
    )
    _wait_for(started.is_file)
    assert not list((tmp_path / ".agent-factory/usage").glob("pi-*.jsonl"))
    gate.touch()
    _wait_for(
        lambda: len(list((tmp_path / ".agent-factory/usage").glob("pi-*.jsonl"))) == 1
    )
    record = json.loads(
        next((tmp_path / ".agent-factory/usage").glob("pi-*.jsonl")).read_text()
    )
    _wait_for(lambda: not list((tmp_path / ".agent-factory/usage/.capture").iterdir()))
    assert record["parent_session_id"] == "pi-human-parent"
    assert record["depth"] == 1


def test_spawn_error_cleans_registered_staged_source(tmp_path):
    _init(tmp_path)
    capture = tmp_path / "factory/scripts/usage-capture-runtime"
    capture.write_text("#!/definitely/missing/interpreter\n")
    capture.chmod(0o755)
    bridge = tmp_path / ".pi/extensions/pi-usage.ts"
    exercise = tmp_path / "exercise-spawn-error.mjs"
    exercise.write_text(
        f"""
import {{capturePiStream}} from {json.dumps(bridge.as_uri())};
capturePiStream({json.dumps(str(tmp_path))}, '{{"type":"message_end","message":{{"role":"assistant","content":[{{"type":"text","text":"ok"}}],"usage":{{"input":3,"output":1}}}}}}', {{sessionId:'pi-spawn-error'}});
await new Promise(resolve => setTimeout(resolve, 100));
"""
    )

    _run_node(exercise, cwd=tmp_path, timeout=3)
    scratch = tmp_path / ".agent-factory/usage/.capture"
    _wait_for(lambda: not scratch.exists() or not list(scratch.iterdir()))
    _wait_for_terminal_capture(tmp_path)
    diagnostic = json.loads(_diagnostics(tmp_path)[0].read_text())
    assert diagnostic["reason"] == "launcher-spawn-enoent"
    assert not (tmp_path / ".agent-factory/usage/pi-spawn-error.jsonl").exists()


def test_interpreter_loss_after_registration_is_cleaned(tmp_path):
    _init(tmp_path)
    launcher = tmp_path / "factory/scripts/usage-capture-runtime"
    real_launcher = tmp_path / "factory/scripts/usage-capture-runtime-real"
    launcher.rename(real_launcher)
    runtime_python = tmp_path / ".agent-factory/usage-runtime/bin/python"
    launcher.write_text(
        f'#!/bin/sh\nrm -f {runtime_python}\nexec {real_launcher} "$@"\n'
    )
    launcher.chmod(0o755)

    _invoke_direct_pi_capture(tmp_path, "pi-post-registration-interpreter-loss")

    _wait_for_terminal_capture(tmp_path)
    assert not list((tmp_path / ".agent-factory/usage/.capture").iterdir())
    assert not list((tmp_path / ".agent-factory/usage-control/pending").iterdir())
    diagnostic_path = _diagnostics(tmp_path)[0]
    diagnostic = json.loads(diagnostic_path.read_text())
    assert diagnostic["reason"] == "launcher-exit-before-acceptance"
    assert diagnostic["exit_code"] == 71
    assert stat.S_IMODE(diagnostic_path.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(diagnostic_path.stat().st_mode) == 0o600
    assert "pi-post-registration-interpreter-loss" not in diagnostic_path.read_text()
    result = subprocess.run(
        [str(_REMOVE), "--target", str(tmp_path), "--pending-timeout", "1"],
        text=True,
        capture_output=True,
        timeout=3,
    )
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / ".agent-factory").exists()


def test_acceptance_transfers_cleanup_to_supervisor(tmp_path):
    _init(tmp_path)

    _invoke_direct_pi_capture(tmp_path, "pi-accepted-supervisor")

    record = _records(tmp_path, "pi-accepted-supervisor")[0]
    assert record["cli"] == "pi"
    control = tmp_path / ".agent-factory/usage-control"
    assert not list(control.glob("*.accepted.json"))
    assert _diagnostics(tmp_path) == []


def test_cancel_before_acceptance_does_not_resurrect(tmp_path):
    _init(tmp_path)
    launcher = tmp_path / "factory/scripts/usage-capture-runtime"
    real_launcher = tmp_path / "factory/scripts/usage-capture-runtime-real"
    launcher.rename(real_launcher)
    gate = tmp_path / "bootstrap-gate"
    launcher.write_text(
        "#!/bin/sh\n"
        f"while [ ! -e {gate} ]; do sleep 0.02; done\n"
        f'exec {real_launcher} "$@"\n'
    )
    launcher.chmod(0o755)

    _invoke_direct_pi_capture(tmp_path, "pi-bootstrap-cancel")
    pending = tmp_path / ".agent-factory/usage-control/pending"
    _wait_for(lambda: bool(list(pending.glob("*.pending.json"))))
    result = subprocess.run(
        [str(_REMOVE), "--target", str(tmp_path), "--pending-usage", "cancel"],
        text=True,
        capture_output=True,
        timeout=3,
    )
    assert result.returncode == 0, result.stderr
    gate.touch()
    time.sleep(0.2)

    assert not (tmp_path / ".agent-factory").exists()
    assert not (tmp_path / "factory").exists()


def test_acceptance_timeout_cleans_and_diagnoses(tmp_path):
    _init(tmp_path)
    control = tmp_path / ".agent-factory/usage-control"
    pending = control / "pending"
    scratch = tmp_path / ".agent-factory/usage/.capture"
    generation = json.loads((control / "state.json").read_text())["generation"]
    source = scratch / "timeout.jsonl"
    source.write_text("staged\n")
    marker = pending / "timeout.pending.json"
    marker.write_text(
        json.dumps({"generation": generation, "staged_source": str(source)}) + "\n"
    )
    handshake = control / "timeout.accepted.json"
    status = control / "timeout.completion.json"
    launcher = tmp_path / "factory/scripts/usage-capture-runtime"
    launcher.write_text("#!/bin/sh\nsleep 0.3\n")
    launcher.chmod(0o755)

    result = subprocess.run(
        [
            "node",
            str(tmp_path / "factory/scripts/pi-capture-bootstrap.mjs"),
            "--root",
            str(tmp_path),
            "--marker",
            str(marker),
            "--source",
            str(source),
            "--status",
            str(status),
            "--handshake",
            str(handshake),
            "--generation",
            generation,
            "--accept-timeout-ms",
            "100",
            "--supervisor-command",
            str(launcher),
        ],
        text=True,
        capture_output=True,
        timeout=2,
    )

    assert result.returncode == 0, result.stderr
    assert not marker.exists()
    assert not source.exists()
    assert not handshake.exists()
    diagnostic = json.loads(_diagnostics(tmp_path)[0].read_text())
    assert diagnostic["reason"] == "acceptance-timeout"


def test_bootstrap_exits_while_accepted_supervisor_continues(tmp_path):
    _init(tmp_path)
    control = tmp_path / ".agent-factory/usage-control"
    pending = control / "pending"
    scratch = tmp_path / ".agent-factory/usage/.capture"
    generation = json.loads((control / "state.json").read_text())["generation"]
    source = scratch / "accepted-live.jsonl"
    source.write_text("staged\n")
    marker = pending / "accepted-live.pending.json"
    marker.write_text(
        json.dumps({"generation": generation, "staged_source": str(source)}) + "\n"
    )
    handshake = control / "accepted-live.accepted.json"
    status = control / "accepted-live.completion.json"
    child_alive = tmp_path / "accepted-child-alive"
    child_finished = tmp_path / "accepted-child-finished"
    launcher = tmp_path / "factory/scripts/usage-capture-runtime"
    launcher.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' '{json.dumps({'accepted': True, 'generation': generation})}' > {handshake}\n"
        f"touch {child_alive}\n"
        "sleep 2\n"
        f"touch {child_finished}\n"
    )
    launcher.chmod(0o755)

    started = time.monotonic()
    result = subprocess.run(
        [
            "node",
            str(tmp_path / "factory/scripts/pi-capture-bootstrap.mjs"),
            "--root",
            str(tmp_path),
            "--marker",
            str(marker),
            "--source",
            str(source),
            "--status",
            str(status),
            "--handshake",
            str(handshake),
            "--generation",
            generation,
            "--supervisor-command",
            str(launcher),
        ],
        text=True,
        capture_output=True,
        timeout=1,
    )

    assert result.returncode == 0, result.stderr
    assert time.monotonic() - started < 1
    assert child_alive.is_file()
    assert not child_finished.exists()
    assert not handshake.exists()
    _wait_for(child_finished.is_file, timeout=3)


def test_missing_runtime_interpreter_reaches_terminal_state(tmp_path):
    _init(tmp_path)
    runtime_python = tmp_path / ".agent-factory/usage-runtime/bin/python"
    runtime_python.unlink()

    _invoke_direct_pi_capture(tmp_path, "pi-missing-interpreter")

    _wait_for_terminal_capture(tmp_path)
    assert not (tmp_path / ".agent-factory/usage/pi-missing-interpreter.jsonl").exists()
    assert _diagnostics(tmp_path) == []
    result = subprocess.run(
        [str(_REMOVE), "--target", str(tmp_path), "--pending-timeout", "1"],
        text=True,
        capture_output=True,
        timeout=3,
    )
    assert result.returncode == 0, result.stderr


def test_capture_process_failure_reaches_terminal_state(tmp_path):
    _init(tmp_path)
    capture = tmp_path / "factory/scripts/usage-capture"
    capture.write_text("import os\nos._exit(42)\n")

    _invoke_direct_pi_capture(tmp_path, "pi-abrupt-python")

    _wait_for_terminal_capture(tmp_path)
    assert not (tmp_path / ".agent-factory/usage/pi-abrupt-python.jsonl").exists()
    diagnostic = json.loads(_diagnostics(tmp_path)[0].read_text())
    assert diagnostic["reason"] == "capture-process-failed"
    assert diagnostic["exit_code"] == 42
    assert diagnostic["signal"] is None


def test_supervisor_rejects_foreign_cleanup_paths(tmp_path):
    _init(tmp_path)
    control = tmp_path / ".agent-factory/usage-control"
    pending = control / "pending"
    scratch = tmp_path / ".agent-factory/usage/.capture"
    generation = json.loads((control / "state.json").read_text())["generation"]
    staged = scratch / "validated.jsonl"
    staged.write_text("staged")
    marker = pending / "validated.pending.json"
    marker.write_text(
        json.dumps({"generation": generation, "staged_source": str(staged)}) + "\n"
    )
    victim = tmp_path / "victim.jsonl"
    victim.write_text("do not delete")
    status = control / "validated.completion.json"

    result = subprocess.run(
        [
            str(tmp_path / "factory/scripts/usage-capture-runtime"),
            "--lifecycle",
            "supervise",
            "--root",
            str(tmp_path),
            "--marker",
            str(marker),
            "--source",
            str(victim),
            "--status",
            str(status),
            "--generation",
            generation,
            "--capture-command",
            str(tmp_path / "factory/scripts/usage-capture-runtime"),
        ],
        text=True,
        capture_output=True,
        timeout=3,
    )

    assert result.returncode == 0
    assert victim.read_text() == "do not delete"
    assert marker.is_file()
    assert staged.is_file()


def test_linked_worktree_capture_uses_primary_checkout(tmp_path):
    primary = tmp_path / "primary"
    primary.mkdir()
    _init_git_repo(primary)
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


def test_untrusted_inherited_root_is_ignored(tmp_path):
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

    _wait_for((primary / ".agent-factory/usage/pi-safe.jsonl").is_file)
    assert not (attacker / "PWNED").exists()


def test_nested_dispatch_records_survive_merged_worktree_removal(tmp_path):
    primary = tmp_path / "primary"
    primary.mkdir()
    _init_git_repo(primary)
    _init(primary)
    # dispatch worktrees need the installed Factory runtime in their committed base.
    subprocess.run(["git", "add", "-f", "factory"], cwd=primary, check=True)
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "install factory"],
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
    usage = primary / ".agent-factory/usage"
    _wait_for(lambda: len(list(usage.glob("pi-*.jsonl"))) == 2)
    records = [json.loads(path.read_text()) for path in usage.glob("pi-*.jsonl")]
    assert sorted(record["depth"] for record in records) == [1, 2]
    outer = next(record for record in records if record["depth"] == 1)
    nested = next(record for record in records if record["depth"] == 2)
    assert outer["parent_session_id"] == "pi-human-parent"
    assert nested["parent_session_id"] == outer["session_id"]
    for record in records:
        assert (primary / record["transcript_ref"]["path"]).is_file()
