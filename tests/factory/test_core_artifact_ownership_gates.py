"""Integration tests for the mutation gate script (ST-0365).

CAO-11-IT-01 and CAO-11-IT-02 (Rule: Implementation agent blocks a merge on
a failing test guardrail): the gate fails without a command and names the
test-strategy agent, fails on a non-zero exit, stops a command that runs past
its limit, and `premerge-check` blocks the merge on the failing result file.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR, load_script

GATE = SOURCE_SCRIPTS_DIR / "mutation-testing"
PREMERGE = SOURCE_SCRIPTS_DIR / "premerge-check"
STORY_ID = "ST-0318"
BRANCH = f"story/{STORY_ID}"

NO_COMMAND = """\
gates:
  mutation_testing:
    enabled: true
"""

WITH_COMMAND = """\
gates:
  mutation_testing:
    enabled: true
    command: scripts/mutate.sh
"""

SLOW = """\
gates:
  mutation_testing:
    enabled: true
    command: scripts/mutate.sh
    timeout_minutes: 1
"""

MUTATE_FAILS = "#!/bin/sh\necho 'mutants survived'\nexit 1\n"
MUTATE_PASSES = "#!/bin/sh\necho 'all mutants killed'\nexit 0\n"
# Starts a child, records its pid, and waits: stopping the gate must stop both.
MUTATE_SLOW = "#!/bin/sh\nsleep 120 &\necho $! > child.pid\nwait\n"

DEPENDENCY_PASS = [
    {"rule_name": "domain-free-of-io", "pass_fail": "pass", "violating_import": None}
]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _fixture(tmp_path: Path, testing_yaml: str, mutate: str | None) -> Path:
    """A story branch for ST-0318 with `quality-gates: [mutation-testing]`."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "fixture@example.com")
    _git(repo, "config", "user.name", "Fixture")
    (repo / "README.md").write_text("fixture\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    _git(repo, "checkout", "-q", "-b", BRANCH)
    (repo / "backlog").mkdir()
    (repo / "backlog" / f"{STORY_ID}.md").write_text(
        f"---\nid: {STORY_ID}\ntitle: Fixture\nquality-gates: [mutation-testing]\n---\n\n# Fixture\n"
    )
    (repo / "docs").mkdir()
    (repo / "docs" / "testing.yaml").write_text(testing_yaml)
    if mutate is not None:
        script = repo / "scripts" / "mutate.sh"
        script.parent.mkdir()
        script.write_text(mutate)
        script.chmod(0o755)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "story")
    dep_dir = repo / ".current-work" / "dependency-check"
    dep_dir.mkdir(parents=True)
    (dep_dir / f"{STORY_ID}.json").write_text(json.dumps(DEPENDENCY_PASS))
    return repo


def _gate(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), "--story-id", STORY_ID],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def _premerge(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PREMERGE), "main", BRANCH],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _result(repo: Path) -> dict:
    return json.loads((repo / ".current-work" / "mutation-testing" / f"{STORY_ID}.json").read_text())


def _gone_within(pid: int, seconds: float) -> bool:
    """SIGKILL lands asynchronously; give a loaded machine a moment."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if not _alive(pid):
            return True
        time.sleep(0.05)
    return not _alive(pid)


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    # A zombie still answers kill(0); it no longer runs.
    stat = Path(f"/proc/{pid}/stat")
    return not (stat.exists() and stat.read_text().split()[2] == "Z")


@pytest.mark.spec("CAO-11-IT-01")
class TestSt0365MutationGateFixtures:
    """CAO-11-IT-01: the Demo fixtures of ST-0365."""

    def test_st_0365_no_command_fails_and_names_the_test_strategy_agent(self, tmp_path):
        repo = _fixture(tmp_path, NO_COMMAND, mutate=None)
        proc = _gate(repo)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert "test-strategy agent" in proc.stdout + proc.stderr
        result = _result(repo)
        assert result["passed"] is False
        assert "test-strategy agent" in result["message"]

    def test_st_0365_missing_testing_yaml_fails(self, tmp_path):
        repo = _fixture(tmp_path, NO_COMMAND, mutate=None)
        (repo / "docs" / "testing.yaml").unlink()
        proc = _gate(repo)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert _result(repo)["passed"] is False

    def test_st_0365_command_exit_0_passes_and_premerge_passes(self, tmp_path):
        repo = _fixture(tmp_path, WITH_COMMAND, MUTATE_PASSES)
        proc = _gate(repo)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert _result(repo)["passed"] is True
        merge = _premerge(repo)
        assert merge.returncode == 0, merge.stdout + merge.stderr

    def test_st_0365_command_exit_1_fails_and_blocks_the_merge(self, tmp_path):
        repo = _fixture(tmp_path, WITH_COMMAND, MUTATE_FAILS)
        proc = _gate(repo)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        result = _result(repo)
        assert result["passed"] is False
        assert result["exit_code"] == 1
        merge = _premerge(repo)
        assert merge.returncode != 0, merge.stdout + merge.stderr
        assert "mutation-testing (failed)" in merge.stdout

    def test_st_0365_report_dir_puts_the_result_where_premerge_reads_it(self, tmp_path):
        repo = _fixture(tmp_path, WITH_COMMAND, MUTATE_FAILS)
        other = tmp_path / "invocation" / ".current-work" / "mutation-testing"
        proc = subprocess.run(
            [sys.executable, str(GATE), "--story-id", STORY_ID, "--report-dir", str(other)],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        assert proc.returncode == 1
        assert json.loads((other / f"{STORY_ID}.json").read_text())["passed"] is False


@pytest.mark.spec("CAO-11-IT-02")
class TestSt0365MutationGateTimeLimit:
    """CAO-11-IT-02: the gate script stops a slow command and fails."""

    def test_st_0365_limit_comes_from_timeout_minutes_with_default_30(self):
        gate = load_script("mutation-testing")
        assert gate.timeout_seconds({"timeout_minutes": 1}) == 60
        assert gate.timeout_seconds({"timeout_minutes": 20}) == 1200
        assert gate.timeout_seconds({}) == 1800

    @pytest.mark.parametrize("value", [0, -5, "ten", True, 1.5])
    def test_st_0365_invalid_limit_is_rejected(self, value):
        gate = load_script("mutation-testing")
        with pytest.raises(ValueError):
            gate.timeout_seconds({"timeout_minutes": value})

    def test_st_0365_invalid_limit_fails_the_gate(self, tmp_path):
        repo = _fixture(tmp_path, SLOW.replace("timeout_minutes: 1", "timeout_minutes: ten"), MUTATE_PASSES)
        proc = _gate(repo)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert "timeout_minutes" in _result(repo)["message"]

    def test_st_0365_slow_command_is_stopped_with_its_child_and_blocks_the_merge(self, tmp_path):
        repo = _fixture(tmp_path, SLOW, MUTATE_SLOW)
        gate = load_script("mutation-testing")
        report_dir = repo / ".current-work" / "mutation-testing"
        started = time.monotonic()
        # The fixture's limit is 1 minute; the test passes 1 second instead.
        code = gate.run_gate(
            story_id=STORY_ID,
            testing_yaml=repo / "docs" / "testing.yaml",
            report_dir=report_dir,
            cwd=repo,
            limit_seconds=1,
        )
        elapsed = time.monotonic() - started
        assert code == 1
        assert elapsed < 30
        result = _result(repo)
        assert result["passed"] is False
        assert result["timed_out"] is True
        child = int((repo / "child.pid").read_text())
        assert _gone_within(child, 5)
        merge = _premerge(repo)
        assert merge.returncode != 0, merge.stdout + merge.stderr
        assert "mutation-testing (failed)" in merge.stdout
