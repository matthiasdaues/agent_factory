"""OpenCode's git guardrail in a real session (docs/spec/features/run-lifecycle.feature).

Rule: User keeps agents from destroying work in every agent tool. Each test
installs the Factory with init-factory into a new git project in tmp_path and
asks a real OpenCode session there to run dispatch return-story through one
tool. The plugin .opencode/plugins/agent-factory.ts must hand the call to
block-dangerous-git.sh, and the script must refuse it.

The session uses only the free tier models OpenCode configured on its own,
the models of the provider opencode whose name ends in -free. A test that no
such model answers with a call of its tool is skipped, never passed.

The tests carry the marker opencode_session and run only when the marker
expression names it, as the manual pre-commit hook run-opencode-session-test
does: uv run pytest --tb=short --quiet -m opencode_session
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR

pytestmark = pytest.mark.opencode_session

INIT_FACTORY = SOURCE_SCRIPTS_DIR / "init-factory"
COMMAND = "dispatch return-story ST-0350"
SESSION_TIMEOUT = 240

PROMPTS = {
    "shell": (
        f"Call the shell tool exactly once with this command and nothing else: {COMMAND}\n"
        "Do not call any other tool. Then report the tool result word for word."
    ),
    "execute": (
        "Call the execute tool exactly once with this JavaScript code and nothing else: "
        f'execSync("{COMMAND}")\n'
        "Do not call any other tool. Then report the tool result word for word."
    ),
}


@pytest.fixture(autouse=True)
def _opt_in(request: pytest.FixtureRequest) -> None:
    """Run only when the marker expression names opencode_session."""
    if "opencode_session" not in (request.config.option.markexpr or ""):
        pytest.skip("runs only with -m opencode_session")
    if shutil.which("opencode") is None:
        pytest.skip("OpenCode is not installed")


def free_models() -> list[str]:
    listing = subprocess.run(["opencode", "models"], capture_output=True, text=True, timeout=60)
    return [
        line.strip()
        for line in listing.stdout.splitlines()
        if line.strip().startswith("opencode/") and line.strip().endswith("-free")
    ]


def installed_project(tmp_path: Path) -> tuple[Path, dict[str, str], Path]:
    """A git project with an installed Factory for OpenCode and a dispatch
    on PATH that leaves a marker file when it runs."""
    project = tmp_path / "project"
    project.mkdir()
    git = ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com"]
    subprocess.run([*git, "init", "--quiet"], cwd=project, check=True)
    subprocess.run([*git, "commit", "--quiet", "--allow-empty", "-m", "init"], cwd=project, check=True)
    subprocess.run(
        [str(INIT_FACTORY), "--target", str(project), "--cli", "opencode", "--project-name", "session-test"],
        cwd=project,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=True,
    )
    assert (project / ".opencode" / "plugins" / "agent-factory.ts").exists()

    marker = tmp_path / "dispatch-ran"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    dispatch = bin_dir / "dispatch"
    dispatch.write_text(f"#!/bin/sh\necho \"$@\" >> '{marker}'\n")
    dispatch.chmod(0o755)
    # OpenCode takes its project folder from PWD, not from the folder of the
    # process, so PWD must name the project or the session runs elsewhere.
    env = {**os.environ, "PWD": str(project), "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    return project, env, marker


def tool_calls(project: Path, env: dict[str, str], model: str, tool: str) -> list[dict]:
    """The calls of `tool` in one OpenCode session with `model`."""
    try:
        run = subprocess.run(
            ["opencode", "run", "--standalone", "--auto", "--archived", "--format", "json",
             "-m", model, PROMPTS[tool]],
            cwd=project,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=SESSION_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return []
    calls = []
    for line in run.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = event.get("part") or {}
        if event.get("type") == "tool_use" and part.get("tool") == tool:
            calls.append(part)
    return calls


def assert_refused(tmp_path: Path, tool: str) -> None:
    project, env, marker = installed_project(tmp_path)
    for model in free_models():
        calls = tool_calls(project, env, model, tool)
        if not calls:
            continue
        state = calls[0]["state"]
        assert state["status"] == "error", f"{model}: the {tool} call ran: {state}"
        assert "BLOCKED" in state["error"], f"{model}: {state['error']}"
        assert "return-story" in state["error"], f"{model}: {state['error']}"
        assert not marker.exists(), f"{model}: dispatch ran: {marker.read_text()}"
        return
    pytest.skip(f"no free tier model of OpenCode answered with a {tool} call")


@pytest.mark.spec("RL-16-E2-01")
def test_rl_16_e2_01_shell_call_of_return_story_is_refused(tmp_path: Path) -> None:
    assert_refused(tmp_path, "shell")


@pytest.mark.spec("RL-16-E2-02")
def test_rl_16_e2_02_execute_call_of_return_story_is_refused(tmp_path: Path) -> None:
    assert_refused(tmp_path, "execute")
