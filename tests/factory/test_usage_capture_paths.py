"""Usage capture finds its files in an installed project (BUG-0033..0035).

Each test builds the installed layout in a temporary project:
.agent-factory/factory/scripts/ holds the scripts, .agent-factory/usage/
holds the runtime, and .agent-factory/config/project.json holds the
project identity.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import uuid
from pathlib import Path

import pytest

from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script

HOOKS_DIR = REPO_ROOT / "packages" / "factory" / "config" / "hooks"


def _executable(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _installed_project(tmp_path: Path) -> tuple[Path, Path]:
    """Return a project whose runtime launcher is a stub that logs its call."""
    project = tmp_path / "project"
    log = tmp_path / "runtime-calls.log"
    _executable(
        project / ".agent-factory" / "factory" / "scripts" / "usage-capture-runtime",
        f'#!/bin/sh\necho "$@" >> "{log}"\n',
    )
    return project, log


@pytest.mark.parametrize(
    ("hook", "payload", "env_project"),
    [
        (
            "capture-usage.sh",
            {"hook_event_name": "Stop", "session_id": "s1", "transcript_path": "/t.jsonl"},
            True,
        ),
        (
            "capture-codex-usage.sh",
            {"session_id": "s1", "transcript_path": "/t.jsonl", "cwd": None},
            False,
        ),
        (
            "capture-copilot-usage.sh",
            {"sessionId": "s1", "transcriptPath": "/t.jsonl", "cwd": None},
            False,
        ),
    ],
)
def test_capture_hook_calls_installed_runtime(tmp_path, hook, payload, env_project):
    """BUG-0033: each capture hook reaches the installed runtime launcher."""
    if shutil.which("jq") is None:
        pytest.skip("jq is required by the capture hooks")
    project, log = _installed_project(tmp_path)
    if "cwd" in payload:
        payload["cwd"] = str(project)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    if env_project:
        env["CLAUDE_PROJECT_DIR"] = str(project)
    result = subprocess.run(
        ["bash", str(HOOKS_DIR / hook)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        cwd=project,
        check=False,
    )
    assert result.returncode == 0
    assert log.exists(), f"{hook} did not call the installed usage-capture-runtime"
    assert "--lifecycle register" in log.read_text(encoding="utf-8")


def test_runtime_launcher_finds_installed_runtime(tmp_path):
    """BUG-0034: the launcher resolves the project root three levels up."""
    project = tmp_path / "project"
    scripts = project / ".agent-factory" / "factory" / "scripts"
    scripts.mkdir(parents=True)
    launcher = scripts / "usage-capture-runtime"
    shutil.copy2(SOURCE_SCRIPTS_DIR / "usage-capture-runtime", launcher)
    runtime = project / ".agent-factory" / "usage" / "runtime"
    (runtime / "bin").mkdir(parents=True)
    (runtime / ".requirements-sha256").write_text("x\n", encoding="utf-8")
    log = tmp_path / "python-calls.log"
    _executable(runtime / "bin" / "python", f'#!/bin/sh\necho "$@" >> "{log}"\n')

    result = subprocess.run(
        ["sh", str(launcher), "--version"], capture_output=True, text=True, check=False
    )

    assert result.returncode == 0, f"launcher exited {result.returncode}"
    assert log.read_text(encoding="utf-8").strip().endswith("usage-capture --version")


def test_project_identity_is_read_from_agent_factory_config(tmp_path):
    """BUG-0035: usage-capture reads the identity that init-factory writes."""
    capture = load_script("usage-capture")
    identity = tmp_path / ".agent-factory" / "config" / "project.json"
    identity.parent.mkdir(parents=True)
    project_id = str(uuid.uuid4())
    identity.write_text(
        json.dumps({"project_id": project_id, "project_name": "demo"}), encoding="utf-8"
    )

    assert capture._project_identity(tmp_path) == (project_id, "demo")


def _join_segments(text: str, anchor: str) -> list[str]:
    match = re.search(r"join\((\w+),\s*([^)]*\"" + re.escape(anchor) + r"\")\)", text)
    assert match, f"no join(...) ending in {anchor!r}"
    return re.findall(r'"([^"]+)"', match.group(2))


def test_pi_bootstrap_accepts_the_launcher_pi_usage_passes():
    """BUG-0033: the Pi bootstrap expects the launcher path pi-usage.ts sends."""
    bootstrap = (SOURCE_SCRIPTS_DIR / "pi-capture-bootstrap.mjs").read_text(encoding="utf-8")
    extension = (
        REPO_ROOT / "packages" / "factory" / "config" / "extensions" / "pi-usage.ts"
    ).read_text(encoding="utf-8")

    expected = _join_segments(extension, "usage-capture-runtime")
    assert _join_segments(bootstrap, "usage-capture-runtime") == expected
    assert expected[0] == ".agent-factory"
