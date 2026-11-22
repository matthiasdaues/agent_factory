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

import json
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
        # dev holds no entry gates.crap-score, so crap-score takes every value
        # from the folder and the measure python of dev is no dropped measure (DEC-69, DEC-70).
        self.repo.git("checkout", "-q", "dev")
        self.repo.write("docs/testing.yaml", 'test_command: "true"\n')
        self.repo.commit("dev without the entry gates.crap-score")
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
    # The first stub waits for the start of the second run, up to 20 s. With a
    # lock, the second run would start only after the first one ended.
    wait = (f'i=0\nwhile ! grep -q "python-start wt-0351" "$STUB_LOG" && [ $i -lt 400 ]; do\n'
            f'  sleep 0.05\n  i=$((i+1))\ndone\n')
    trees.setup("0350", PYTHON_YAML, {PYTHON_STUB: _measuring("python", 0).replace("sleep 0\n", wait)})
    trees.setup("0351", PYTHON_YAML, {PYTHON_STUB: _measuring("python", 0)})
    first = trees.start("0350")
    trees.wait_for("python-start wt-0350")
    second = trees.start("0351")
    assert _finish(first)[0] == 0
    assert _finish(second)[0] == 0
    lines = trees.lines()
    assert lines.index("python-start wt-0351") < lines.index("python-end wt-0350"), lines
    assert not (trees.lock_dir / "python.lock").exists()


@pytest.mark.spec("CG-04-IT-16")
def test_cg_04_a_killed_run_leaves_no_lock_that_makes_the_next_run_wait(trees):
    """Scenario: A killed run leaves no lock that makes the next run wait (DEC-47)."""
    _backend(trees, "0350", seconds=3)
    _backend(trees, "0351", seconds=0)
    first = trees.start("0350")
    trees.wait_for("backend-start wt-0350")
    shell = _children(first.pid)
    os.kill(first.pid, signal.SIGKILL)
    first.communicate(timeout=10)
    assert (trees.lock_dir / "backend.lock").exists()
    code, err = _finish(trees.start("0351"))
    assert code == 0, err
    lines = trees.lines()
    assert "backend-end wt-0350" not in lines[: lines.index("ready wt-0351")]
    if sys.platform.startswith("linux"):
        # PR_SET_PDEATHSIG kills the shell that crap-score started for the
        # command. The stub is a child of that shell, so it may still end.
        assert len(shell) == 1
        _wait_gone(shell[0])
    trees.wait_for("backend-end wt-0350")


def _children(pid: int) -> list[int]:
    """The child processes of *pid*, read from /proc on Linux."""
    path = Path(f"/proc/{pid}/task/{pid}/children")
    return [int(child) for child in path.read_text().split()] if path.exists() else []


def _wait_gone(pid: int, seconds: float = 5) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        status = Path(f"/proc/{pid}/stat")
        if not status.exists() or status.read_text().split()[2] == "Z":
            return
        time.sleep(0.02)
    raise AssertionError(f"process {pid} still runs after {seconds} s")


def _stoppable(event: str, seconds: float) -> str:
    """Set a trap, then log the start; on SIGTERM log '<event>-stopped' and exit; else sleep and log the end.

    The trap comes first, so the start line means that the trap is in place.
    """
    return (
        "#!/bin/sh\n"
        f"trap 'echo \"{event}-stopped $(basename \"$PWD\")\" >> \"$STUB_LOG\"; exit 143' TERM\n"
        f'echo "{event}-start $(basename "$PWD")" >> "$STUB_LOG"\n'
        f'sleep {seconds}\necho "[]" > "$GATE_OUTPUT"\n'
        f'echo "{event}-end $(basename "$PWD")" >> "$STUB_LOG"\n'
    )


@pytest.mark.spec("CG-04-IT-16")
@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGINT, signal.SIGHUP], ids=["TERM", "INT", "HUP"])
def test_cg_04_a_stopped_run_stops_its_command_before_it_frees_the_lock(trees, sig):
    """A run stopped by SIGTERM, Ctrl-C or SIGHUP stops its command, so the next run does not overlap it."""
    trees.setup("0350", BACKEND_YAML.format(timeout=1),
                {READY: _stub("ready"), BACKEND_STUB: _stoppable("backend", 10)})
    _backend(trees, "0351", seconds=0)
    first = trees.start("0350")
    trees.wait_for("backend-start wt-0350")
    second = trees.start("0351")
    os.kill(first.pid, sig)
    code, err = _finish(first)
    assert code == 128 + sig, err
    assert signal.Signals(sig).name in err
    assert "Traceback" not in err
    code, err = _finish(second)
    assert code == 0, err
    assert trees.lines() == [
        "ready wt-0350", "backend-start wt-0350", "backend-stopped wt-0350",
        "ready wt-0351", "backend-start wt-0351", "backend-end wt-0351",
    ]


@pytest.mark.spec("CG-04-IT-13")
@pytest.mark.parametrize("name", ["../hooks/x", "a/b", "..", "."])
def test_cg_04_a_measure_name_that_is_no_file_name_cannot_measure(trees, name):
    """The lock file of a measure stays in crap-score/ under the git common directory."""
    trees.setup("0350", BACKEND_YAML.format(timeout=1).replace("name: backend", f'name: "{name}"'),
                {READY: _stub("ready"), BACKEND_STUB: _measuring("backend", 0)})
    code, err = _finish(trees.start("0350"))
    assert code == 2, err
    assert f"measure {name}" in err
    assert "file name" in err
    assert trees.lines() == []
    assert not (trees.lock_dir.parent / "hooks" / "x.lock").exists()


# The driver runs in its own single-threaded process. pthread_sigmask holds a
# signal back only for the calling thread, and a pytest-xdist worker has more
# than one thread, so in the worker another thread could take the signal.
STOP_DRIVER = """\
import importlib.util
import json
import os
import signal
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

loader = SourceFileLoader("crap_score", sys.argv[1])
cs = importlib.util.module_from_spec(importlib.util.spec_from_loader("crap_score", loader))
sys.modules["crap_score"] = cs
loader.exec_module(cs)

started = []
real_popen = subprocess.Popen


def popen_then_signal(*args, **kwargs):
    proc = real_popen(*args, **kwargs)
    started.append(proc)
    os.kill(os.getpid(), signal.SIGTERM)
    return proc


cs.subprocess.Popen = popen_then_signal
measure = cs.Measure("backend", "backend/**", "sleep 30")
try:
    with cs.stop_signals():
        cs.run_command(measure, "measuring command", "sleep 30", Path(sys.argv[2]), dict(os.environ), cs.Clock(1))
except cs.Stopped as stop:
    signum = stop.signum
else:
    signum = None
group_gone = True
if started:
    try:
        os.killpg(started[0].pid, 0)
        group_gone = False
    except ProcessLookupError:
        pass
print(json.dumps({
    "signum": signum,
    "starts": len(started),
    "returncode": started[0].returncode if started else None,
    "group_gone": group_gone,
}))
"""


@pytest.mark.spec("CG-04-IT-16")
def test_cg_04_a_stop_signal_while_the_command_starts_still_stops_it(tmp_path):
    """A SIGTERM that arrives inside subprocess.Popen, after the fork, still stops the command.

    The driver sends SIGTERM to its own process right after the real Popen has
    started the command and before Popen returns to crap-score. That puts the
    signal into the window deterministically. The driver runs in a fresh
    single-threaded process, as crap-score does.
    """
    driver = tmp_path / "stop-driver.py"
    driver.write_text(STOP_DRIVER)
    result = subprocess.run(
        [sys.executable, str(driver), str(SCRIPT), str(tmp_path)],
        capture_output=True, text=True, check=False, timeout=120,
    )
    assert result.returncode == 0, result.stderr
    outcome = json.loads(result.stdout.strip().splitlines()[-1])
    assert outcome["signum"] == int(signal.SIGTERM)
    assert outcome["starts"] == 1
    assert outcome["returncode"] is not None
    assert outcome["group_gone"] is True
