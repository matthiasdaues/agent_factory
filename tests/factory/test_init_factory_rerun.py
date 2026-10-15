"""A rerun of init-factory keeps the tools the user chose (BUG-0044)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR


def _init(target: Path, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(
        [sys.executable, str(SOURCE_SCRIPTS_DIR / "init-factory"),
         "--source", str(REPO_ROOT), "--target", str(target), *args],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, env=env, check=False,
    )


def _recorded_clis(target: Path) -> list[str]:
    return json.loads((target / ".agent-factory" / "install.json").read_text())["cli"]


def test_rerun_without_cli_keeps_the_recorded_tools(tmp_path):
    target = tmp_path / "project"
    target.mkdir()
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    first = _init(target, "--cli", "claude", "--project-name", "demo")
    assert first.returncode == 0, first.stderr
    (target / ".github" / "workflows").mkdir(parents=True)

    rerun = _init(target)

    assert rerun.returncode == 0, rerun.stderr
    assert _recorded_clis(target) == ["claude"]
    assert "copilot" not in rerun.stdout.split("Wiring:", 1)[1].splitlines()[0]


def test_explicit_cli_still_overrides_the_record(tmp_path):
    target = tmp_path / "project"
    target.mkdir()
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    assert _init(target, "--cli", "claude", "--project-name", "demo").returncode == 0

    rerun = _init(target, "--cli", "claude", "codex")

    assert rerun.returncode == 0, rerun.stderr
    assert sorted(_recorded_clis(target)) == ["claude", "codex"]
