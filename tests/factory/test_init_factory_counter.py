"""init-factory tells the user how to seed the counter (ST-0375, CID-10)."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR

COUNTER_REF = "refs/ids/counters"


def _git(cwd: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, env=env, check=True
    )
    return result.stdout


def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    _git(project, "init", "-q")
    _git(project, "-c", "user.name=t", "-c", "user.email=t@example.com",
         "commit", "-q", "--allow-empty", "-m", "first")
    return project


def _bare_origin(tmp_path: Path, project: Path) -> Path:
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", str(origin))
    _git(project, "remote", "add", "origin", str(origin))
    return origin


def _closed_port_url() -> str:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://127.0.0.1:{port}/remote.git"


def _init(target: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(
        [sys.executable, str(SOURCE_SCRIPTS_DIR / "init-factory"),
         "--source", str(REPO_ROOT), "--target", str(target),
         "--cli", "claude", "--project-name", "demo"],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, env=env,
        check=False, timeout=300,
    )


def test_st_0375_missing_counter_names_the_seed_command(tmp_path):
    project = _project(tmp_path)
    origin = _bare_origin(tmp_path, project)

    result = _init(project)

    assert "next-id --seed <number>" in result.stdout
    assert "above your highest ID" in result.stdout
    assert _git(origin, "for-each-ref", COUNTER_REF) == ""


def test_st_0375_missing_origin_names_the_remote(tmp_path):
    project = _project(tmp_path)

    result = _init(project)

    assert "add the remote `origin`, then run `next-id --seed <number>`" in result.stdout


def test_st_0375_unreachable_origin_warns_and_finishes(tmp_path):
    project = _project(tmp_path)
    url = _closed_port_url()
    _git(project, "remote", "add", "origin", url)

    result = _init(project)

    assert result.returncode == 0, result.stderr
    warning = [ln for ln in result.stdout.splitlines() if "warning" in ln.lower()]
    assert any(url in ln for ln in warning), result.stdout
    record = json.loads((project / ".agent-factory" / "install.json").read_text())
    assert record["cli"] == ["claude"]
