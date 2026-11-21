"""Integration tests: the lock of a measure with a ready command (ST-0438).

docs/spec/features/crap-gate-setup.feature, Rule "Implementation agent gets one
verdict for the functions a story changed", and DEC-43 and DEC-47. Each test
builds one temporary repository with two linked worktrees, one on
`story/ST-0350` and one on `story/ST-0351`, and starts two `crap-score`
processes with `subprocess.Popen`. The stubs append one line per event to one
log outside the repository. The test holds the lock only through a first
`crap-score` run, never by a file of its own (DEC-47).
"""

from __future__ import annotations

import os
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path

import pytest
from test_crap_gate_score import SCRIPT, TARGET, Repo

READY = "scripts/crap-ready-backend"
BACKEND_STUB = "scripts/crap-measure-backend"
PYTHON_STUB = "scripts/crap-measure-python"

BACKEND_YAML = f"""\
gates:
  crap-score:
    enabled: true
    threshold: 8
    timeout_minutes: {{timeout}}
    measures:
      - name: backend
        files: "backend/**"
        command: "{BACKEND_STUB}"
        ready: "{READY}"
"""

PYTHON_YAML = f"""\
gates:
  crap-score:
    enabled: true
    threshold: 8
    timeout_minutes: 1
    measures:
      - name: python
        files: "packages/factory/scripts/*"
        command: "{PYTHON_STUB}"
"""


def _stub(event: str, then: str = "") -> str:
    """Append '<event> <worktree>' to $STUB_LOG, then run *then*."""
    return f'#!/bin/sh\necho "{event} $(basename "$PWD")" >> "$STUB_LOG"\n{then}'


def _measuring(event: str, seconds: float) -> str:
    """Log the start, sleep *seconds*, write no rows, log the end."""
    return _stub(f"{event}-start", f'sleep {seconds}\necho "[]" > "$GATE_OUTPUT"\n'
                                   f'echo "{event}-end $(basename "$PWD")" >> "$STUB_LOG"\n')


class Worktrees:
    """One repository with the worktrees wt-0350 and wt-0351 and one stub log."""

    def __init__(self, tmp_path: Path) -> None:
        self.repo = Repo(tmp_path)
        self.repo.git("checkout", "-q", TARGET)
        self.repo.git("branch", "-q", "story/ST-0351", TARGET)
        self.log = tmp_path / "stub.log"
        self.repo.env["STUB_LOG"] = str(self.log)
        self.trees = {}
        for story in ("0350", "0351"):
            path = tmp_path / f"wt-{story}"
            self.repo.git("worktree", "add", "-q", str(path), f"story/ST-{story}")
            self.trees[story] = path
        self.lock_dir = Path(self.repo.git("rev-parse", "--path-format=absolute", "--git-common-dir")) / "crap-score"

    def setup(self, story: str, yaml: str, stubs: dict[str, str]) -> None:
        """Write docs/testing.yaml and the stubs into the worktree of *story*."""
        root = self.trees[story]
        self.repo.write("docs/testing.yaml", yaml, root)
        for relative, text in stubs.items():
            self.repo.write(relative, text, root)
            path = root / relative
            path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def start(self, story: str) -> subprocess.Popen[str]:
        return subprocess.Popen(
            [sys.executable, str(SCRIPT), "--all", "--story-id", f"ST-{story}"],
            cwd=self.trees[story], env=self.repo.env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

    def lines(self) -> list[str]:
        return self.log.read_text().splitlines() if self.log.exists() else []

    def wait_for(self, line: str, seconds: float = 20) -> None:
        deadline = time.monotonic() + seconds
        while line not in self.lines():
            assert time.monotonic() < deadline, f"no line {line!r} in {self.lines()}"
            time.sleep(0.02)


@pytest.fixture
def trees(tmp_path: Path) -> Worktrees:
    return Worktrees(tmp_path)


def _finish(proc: subprocess.Popen[str]) -> tuple[int, str]:
    _, err = proc.communicate(timeout=60)
    return proc.returncode, err


def _backend(trees: Worktrees, story: str, timeout: float = 1, seconds: float = 1) -> None:
    trees.setup(story, BACKEND_YAML.format(timeout=timeout),
                {READY: _stub("ready"), BACKEND_STUB: _measuring("backend", seconds)})


@pytest.mark.spec("CG-04-IT-13")
def test_cg_04_two_runs_of_a_measure_with_a_ready_command_do_not_overlap(trees):
    """Scenario: Two runs of a measure with ready commands do not overlap."""
    _backend(trees, "0350")
    _backend(trees, "0351")
    first = trees.start("0350")
    trees.wait_for("backend-start wt-0350")
    assert (trees.lock_dir / "backend.lock").exists()
    second = trees.start("0351")
    assert _finish(first)[0] == 0
    code, err = _finish(second)
    assert code == 0, err
    assert trees.lines() == [
        "ready wt-0350", "backend-start wt-0350", "backend-end wt-0350",
        "ready wt-0351", "backend-start wt-0351", "backend-end wt-0351",
    ]


@pytest.mark.spec("CG-04-IT-14")
def test_cg_04_a_run_whose_time_runs_out_while_it_waits_for_the_lock_cannot_measure(trees):
    """Scenario: A run whose time limit runs out while it waits for the lock cannot measure."""
    _backend(trees, "0350", seconds=4)
    _backend(trees, "0351", timeout=0.02)
    first = trees.start("0350")
    trees.wait_for("backend-start wt-0350")
    code, err = _finish(trees.start("0351"))
    assert code == 2, err
    assert "measure backend" in err
    assert str(trees.lock_dir / "backend.lock") in err
    assert _finish(first)[0] == 0
    assert not [line for line in trees.lines() if line.endswith("wt-0351")]


@pytest.mark.spec("CG-04-IT-15")
def test_cg_04_a_measure_without_a_ready_command_takes_no_lock(trees):
    """Scenario: A measure without ready commands takes no lock."""
    for story in ("0350", "0351"):
        trees.setup(story, PYTHON_YAML, {PYTHON_STUB: _measuring("python", 2)})
    first = trees.start("0350")
    trees.wait_for("python-start wt-0350")
    second = trees.start("0351")
    trees.wait_for("python-start wt-0351")
    assert "python-end wt-0350" not in trees.lines()
    assert _finish(first)[0] == 0
    assert _finish(second)[0] == 0
    assert not (trees.lock_dir / "python.lock").exists()


@pytest.mark.spec("CG-04-IT-16")
def test_cg_04_a_killed_run_leaves_no_lock_that_makes_the_next_run_wait(trees):
    """Scenario: A killed run leaves no lock that makes the next run wait (DEC-47)."""
    _backend(trees, "0350", seconds=3)
    _backend(trees, "0351", seconds=0)
    first = trees.start("0350")
    trees.wait_for("backend-start wt-0350")
    os.kill(first.pid, signal.SIGKILL)
    first.communicate(timeout=10)
    assert (trees.lock_dir / "backend.lock").exists()
    code, err = _finish(trees.start("0351"))
    assert code == 0, err
    lines = trees.lines()
    assert "backend-end wt-0350" not in lines[: lines.index("ready wt-0351")]
    trees.wait_for("backend-end wt-0350")
