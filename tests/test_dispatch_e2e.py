"""End-to-end smoke test for the Phase 1 dispatch golden path."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

DISPATCH_SCRIPT = (
    Path(__file__).resolve().parent.parent / "factory" / "scripts" / "dispatch"
)
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "factory" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import dispatch_lib  # noqa: E402

Ledger = dispatch_lib.Ledger


def _git_env(tmp_path: Path) -> dict[str, str]:
    """Return a git environment isolated from user-level configuration."""
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(tmp_path),
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def _run_dispatch(*args: str, cwd: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    """Invoke the dispatch CLI as a subprocess."""
    return subprocess.run(
        [sys.executable, str(DISPATCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
        env=_git_env(tmp_path),
    )


def _run_dispatch_with_ledger(
    ledger: Path, *args: str, cwd: Path, tmp_path: Path
) -> subprocess.CompletedProcess[str]:
    """Invoke dispatch with an explicit ledger path."""
    return _run_dispatch("--ledger", str(ledger), *args, cwd=cwd, tmp_path=tmp_path)


def _git(repo: Path, tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git inside the temporary repository."""
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=repo,
        check=False,
        env=_git_env(tmp_path),
    )


def _init_repo(tmp_path: Path) -> Path:
    """Create a minimal git repository with two backlog stories."""
    repo = tmp_path / "repo"
    repo.mkdir()

    for args in (
        ("init", "--initial-branch=main"),
        ("config", "user.email", "test@test.com"),
        ("config", "user.name", "Test"),
        ("config", "core.hooksPath", "/dev/null"),
    ):
        result = _git(repo, tmp_path, *args)
        assert result.returncode == 0, result.stderr

    config_dir = repo / "config"
    config_dir.mkdir()
    (config_dir / "project.json").write_text(
        json.dumps(
            {"project_name": "test", "test_command": "uv run -- python -m unittest discover -s tests -q"}
        )
    )

    backlog_dir = repo / "backlog"
    backlog_dir.mkdir()
    (backlog_dir / "ST-001.md").write_text(
        """---
id: ST-001
tier: economy
status: pending
deps: []
outputs:
  - src/stories/ST-001.txt
tests:
  - tests/test_smoke.py
traces:
  - Feature: Wave Planning
---

# ST-001
"""
    )
    (backlog_dir / "ST-002.md").write_text(
        """---
id: ST-002
tier: economy
status: pending
deps:
  - ST-001
outputs:
  - src/stories/ST-002.txt
tests:
  - tests/test_smoke.py
traces:
  - Feature: Wave Lifecycle
  - Feature: Story Lifecycle
---

# ST-002
"""
    )

    tests_dir = repo / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_smoke.py").write_text(
        """import unittest\n\n\nclass SmokeTest(unittest.TestCase):\n    def test_smoke(self) -> None:\n        self.assertTrue(True)\n"""
    )

    (repo / "src" / "stories").mkdir(parents=True)

    result = _git(repo, tmp_path, "add", "-A")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "--no-verify", "-m", "initial")
    assert result.returncode == 0, result.stderr
    return repo


def _write_story_commit(
    worktree: Path, repo: Path, tmp_path: Path, story_id: str, content: str
) -> str:
    """Simulate subagent work by committing one story output in a worktree."""
    expected_branch = f"story/{story_id}"
    result = _git(worktree, tmp_path, "checkout", "-B", expected_branch)
    assert result.returncode == 0, result.stderr

    output = worktree / "src" / "stories" / f"{story_id}.txt"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)

    result = _git(worktree, tmp_path, "add", "--", str(output.relative_to(worktree)))
    assert result.returncode == 0, result.stderr
    result = _git(worktree, tmp_path, "commit", "--no-verify", "-m", f"feat: {story_id}")
    assert result.returncode == 0, result.stderr
    sha = _git(worktree, tmp_path, "rev-parse", "HEAD").stdout.strip()
    result = _git(repo, tmp_path, "update-ref", f"refs/heads/story/{story_id}", sha)
    assert result.returncode == 0, result.stderr
    return sha


def _ledger_path(repo: Path) -> Path:
    """Return the dispatch ledger path for the two-story smoke test."""
    return repo / ".current_work" / "impl" / "st-001-st-002" / "dispatch-ledger.yaml"


def _assign_waves(ledger_path: Path) -> None:
    """Persist the planned wave numbers expected by prepare-wave."""
    ledger = Ledger.load(ledger_path)
    ledger.stories["ST-001"].wave = 1
    ledger.stories["ST-002"].wave = 2
    ledger.save(ledger_path)


def _story_worktree(repo: Path, story_id: str) -> Path:
    """Return the per-story worktree path created by prepare-wave."""
    return repo / ".agent-factory" / "worktrees" / f"story-{story_id}"


def _clean_worktree(worktree: Path) -> None:
    """Remove generated step-guard state before merge cleanup."""
    current_work = worktree / ".current_work"
    if current_work.exists():
        shutil.rmtree(current_work)


def _cleanup_story_leftovers(repo: Path, tmp_path: Path, story_id: str, worktree: Path) -> None:
    """Force-remove leftover story worktree or branch state after merge."""
    result = _git(repo, tmp_path, "worktree", "remove", "--force", str(worktree))
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    result = _git(repo, tmp_path, "branch", "-D", f"story/{story_id}")
    if result.returncode != 0 and "not found" not in result.stderr:
        raise AssertionError(result.stderr)


def test_smoke_two_story_two_wave_dispatch_to_completion(tmp_path: Path) -> None:
    """Exercise the full dispatch golden path end to end."""
    started = time.monotonic()
    repo = _init_repo(tmp_path)

    init = _run_dispatch("init", "--base", "main", "--stories", "ST-001,ST-002", cwd=repo, tmp_path=tmp_path)
    assert init.returncode == 0, init.stderr

    plan = _run_dispatch("plan", "--backlog-dir", "backlog", cwd=repo, tmp_path=tmp_path)
    assert plan.returncode == 0, plan.stderr
    assert "wave: 1" in plan.stdout
    assert "ST-001" in plan.stdout
    assert "wave: 2" in plan.stdout
    assert "ST-002" in plan.stdout

    ledger_path = _ledger_path(repo)
    assert ledger_path.exists()
    _assign_waves(ledger_path)

    prepare_1 = _run_dispatch_with_ledger(ledger_path, "prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert prepare_1.returncode == 0, prepare_1.stderr

    story_1_worktree = _story_worktree(repo, "ST-001")
    assert story_1_worktree.exists()

    dispatching_1 = _run_dispatch_with_ledger(
        ledger_path, "mark-dispatching", "ST-001", cwd=repo, tmp_path=tmp_path
    )
    assert dispatching_1.returncode == 0, dispatching_1.stderr

    sha_1 = _write_story_commit(
        story_1_worktree, repo, tmp_path, "ST-001", "print('ST-001 complete')\n"
    )

    dispatched_1 = _run_dispatch_with_ledger(
        ledger_path, "mark-dispatched", "ST-001", cwd=repo, tmp_path=tmp_path
    )
    assert dispatched_1.returncode == 0, dispatched_1.stderr

    verify_1 = _run_dispatch_with_ledger(
        ledger_path,
        "verify-story",
        "ST-001",
        "--sha",
        sha_1,
        cwd=story_1_worktree,
        tmp_path=tmp_path,
    )
    assert verify_1.returncode == 0, verify_1.stderr

    _clean_worktree(story_1_worktree)

    merge_1 = _run_dispatch_with_ledger(
        ledger_path, "merge-story", "ST-001", cwd=repo, tmp_path=tmp_path
    )
    assert merge_1.returncode == 0, merge_1.stderr
    assert "status: done" in (repo / "backlog" / "ST-001.md").read_text()

    close_1 = _run_dispatch_with_ledger(
        ledger_path, "close-wave", "1", cwd=repo, tmp_path=tmp_path
    )
    assert close_1.returncode == 0, close_1.stderr

    prepare_2 = _run_dispatch_with_ledger(
        ledger_path, "prepare-wave", "2", cwd=repo, tmp_path=tmp_path
    )
    assert prepare_2.returncode == 0, prepare_2.stderr

    story_2_worktree = _story_worktree(repo, "ST-002")
    assert story_2_worktree.exists()

    dispatching_2 = _run_dispatch_with_ledger(
        ledger_path, "mark-dispatching", "ST-002", cwd=repo, tmp_path=tmp_path
    )
    assert dispatching_2.returncode == 0, dispatching_2.stderr

    sha_2 = _write_story_commit(
        story_2_worktree, repo, tmp_path, "ST-002", "print('ST-002 complete')\n"
    )

    dispatched_2 = _run_dispatch_with_ledger(
        ledger_path, "mark-dispatched", "ST-002", cwd=repo, tmp_path=tmp_path
    )
    assert dispatched_2.returncode == 0, dispatched_2.stderr

    verify_2 = _run_dispatch_with_ledger(
        ledger_path,
        "verify-story",
        "ST-002",
        "--sha",
        sha_2,
        cwd=story_2_worktree,
        tmp_path=tmp_path,
    )
    assert verify_2.returncode == 0, verify_2.stderr

    _clean_worktree(story_2_worktree)

    merge_2 = _run_dispatch_with_ledger(
        ledger_path, "merge-story", "ST-002", cwd=repo, tmp_path=tmp_path
    )
    assert merge_2.returncode == 0, merge_2.stderr
    assert "status: done" in (repo / "backlog" / "ST-002.md").read_text()

    close_2 = _run_dispatch_with_ledger(
        ledger_path, "close-wave", "2", cwd=repo, tmp_path=tmp_path
    )
    assert close_2.returncode == 0, close_2.stderr

    _cleanup_story_leftovers(repo, tmp_path, "ST-001", story_1_worktree)
    _cleanup_story_leftovers(repo, tmp_path, "ST-002", story_2_worktree)

    ledger_text = ledger_path.read_text()
    assert "ST-001" in ledger_text and "done" in ledger_text
    assert "ST-002" in ledger_text and "done" in ledger_text

    status = _git(repo, tmp_path, "status", "--porcelain").stdout.splitlines()
    tracked_status = [
        line for line in status if ".agent-factory/" not in line and "__pycache__" not in line
    ]
    assert tracked_status == []

    story_worktrees = _git(repo, tmp_path, "worktree", "list", "--porcelain").stdout
    assert ".agent-factory/worktrees/story-ST-001" not in story_worktrees
    assert ".agent-factory/worktrees/story-ST-002" not in story_worktrees
    story_branches = _git(repo, tmp_path, "branch", "--list", "story/*").stdout
    assert story_branches == ""

    assert time.monotonic() - started < 60
