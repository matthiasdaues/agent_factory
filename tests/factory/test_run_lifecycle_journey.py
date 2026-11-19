"""One run by hand from dispatch init to dispatch close (RL-02-E2-01).

Rules: Implementation agent runs every story through the same story workflow
on both ways; User ends a run and leaves no run state behind.

The test builds its own git repository in tmp_path. Scripted commits stand
in for the developer agent and the code-review agent, and dispatch runs as a
subprocess, the way the User runs it.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml
from conftest import SOURCE_SCRIPTS_DIR, write_review_report

DISPATCH = SOURCE_SCRIPTS_DIR / "dispatch"
BRANCH = "feature/login"
STORY = """---
id: ST-0350
title: ST-0350
tier: economy
status: pending
deps: []
touches: ["src/ST-0350.txt"]
outputs: ["src/ST-0350.txt"]
quality-gates: []
---
# ST-0350
"""


def _env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
    )
    return env


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, env=_env(), check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _dispatch(repo: Path, ledger: Path, *args: str) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [str(DISPATCH), "--ledger", str(ledger), *args],
        cwd=repo, env=_env(), capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    for folder in ("backlog", "docs", "src"):
        (repo / folder).mkdir(parents=True)
    _git(tmp_path, "init", "-q", "-b", "dev", str(repo))
    (repo / "backlog" / "ST-0350.md").write_text(STORY)
    (repo / "docs" / "testing.yaml").write_text('test_command: "true"\n')
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "src" / ".keep").write_text("")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    return repo


@pytest.mark.spec("RL-02-E2-01")
def test_RL_02_E2_01_a_run_by_hand_goes_from_init_to_close(tmp_path):
    """Scenario: The story workflow runs its steps in order on the story branch.
    Scenario: The record of a closed run lives in git and the backlog."""
    repo = _repo(tmp_path)
    ledger = repo / ".current-work" / BRANCH / "dispatch-ledger.yaml"
    _dispatch(
        repo, ledger, "init", "--mode", "by-hand", "--base", "dev",
        "--feature-branch", BRANCH, "--stories", "ST-0350",
    )
    _dispatch(repo, ledger, "prepare-story", "ST-0350")
    _dispatch(repo, ledger, "mark-dispatching", "ST-0350")
    (repo / "src" / "ST-0350.txt").write_text("work\n")
    _git(repo, "add", "src")
    _git(repo, "commit", "-qm", "feat: story work (ST-0350)")
    write_review_report(repo, "ST-0350")
    _git(repo, "add", "docs/reviews")
    _git(repo, "commit", "-qm", "docs: review ST-0350")
    _dispatch(repo, ledger, "mark-dispatched", "ST-0350")
    merged = _dispatch(repo, ledger, "merge-story", "ST-0350")
    assert "premerge-check: PASS" in merged.stdout
    assert "test suite 'true' passed for ST-0350" in merged.stdout
    _git(repo, "checkout", "-q", "dev")
    _git(repo, "merge", "-q", "--no-ff", "-m", f"merge {BRANCH}", BRANCH)

    _dispatch(repo, ledger, "close")

    story = _git(repo, "show", "dev:backlog/ST-0350.md")
    assert yaml.safe_load(story.split("---")[1])["status"] == "done"
    assert _git(repo, "log", "--merges", "--format=%s", "dev").splitlines()[0] == (
        f"merge {BRANCH}"
    )
    current = repo / ".current-work"
    assert not (current / BRANCH).exists()
    assert not (current / "verify-base-ok").exists()
    assert not (current / "premerge-check-ok").exists()
    assert _git(repo, "worktree", "list", "--porcelain").count("worktree ") == 1
    assert _git(repo, "branch", "--format=%(refname:short)").splitlines() == ["dev"]
    assert _git(repo, "stash", "list") == ""
