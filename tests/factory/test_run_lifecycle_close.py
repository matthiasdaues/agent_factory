"""The end of a run with returned stories (docs/spec/features/run-lifecycle.feature).

Rule: Implementation agent starts a story only when its dependencies inside
the run are done.

Each test builds its own git repository in tmp_path and runs dispatch as a
subprocess, the way the implementation agent does.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

from conftest import SOURCE_SCRIPTS_DIR

DISPATCH = SOURCE_SCRIPTS_DIR / "dispatch"
STORY = """---
id: {id}
title: {id}
tier: economy
status: pending
deps: [{deps}]
touches: ["src/{id}.txt"]
outputs: ["src/{id}.txt"]
quality-gates: []
---
# {id}
"""
BRANCH = "feature/login"


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


def _dispatch(cwd: Path, ledger: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(DISPATCH), "--ledger", str(ledger), *args],
        cwd=cwd, env=_env(), capture_output=True, text=True, check=False,
    )


def _status_in_backlog(repo: Path, story_id: str) -> str:
    text = (repo / "backlog" / f"{story_id}.md").read_text()
    return yaml.safe_load(text.split("---")[1])["status"]


@pytest.fixture()
def returned_run(tmp_path: Path) -> tuple[Path, Path]:
    """An orchestrated run on feature/login in which the User returned ST-0350
    after a block, and ST-0351 waits on ST-0350."""
    repo = tmp_path / "repo"
    for folder in ("backlog", "docs", "src"):
        (repo / folder).mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    (repo / "backlog" / "ST-0350.md").write_text(STORY.format(id="ST-0350", deps=""))
    (repo / "backlog" / "ST-0351.md").write_text(
        STORY.format(id="ST-0351", deps="ST-0350")
    )
    (repo / "docs" / "testing.yaml").write_text('test_command: "true"\n')
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "src" / ".keep").write_text("")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    ledger = repo / ".current-work" / BRANCH / "dispatch-ledger.yaml"
    for args in (
        ("init", "--base", "dev", "--feature-branch", BRANCH,
         "--stories", "ST-0350,ST-0351"),
        ("plan", "--backlog-dir", "backlog"),
        ("prepare-wave", "1"),
        ("mark-dispatching", "ST-0350"),
        ("mark-dispatched", "ST-0350"),
        ("mark-blocked", "ST-0350", "--reason", "- see the CI log"),
        ("return-story", "ST-0350"),
    ):
        result = _dispatch(repo, ledger, *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)
    return repo, ledger


@pytest.mark.spec("RL-07-IT-01")
def test_RL_07_IT_01_returned_stories_stay_in_the_backlog_at_the_end_of_the_run(
    returned_run,
):
    """Scenario: Returned stories stay in the backlog at the end of the run."""
    repo, ledger = returned_run

    last_wave = _dispatch(repo, ledger, "prepare-wave", "2")

    assert last_wave.returncode == 0, last_wave.stdout + last_wave.stderr
    assert "ST-0351 depends on ST-0350" in last_wave.stdout + last_wave.stderr
    assert "returned" in last_wave.stdout + last_wave.stderr
    assert _git(repo, "branch", "--list", "story/ST-0351") == ""
    stories = yaml.safe_load(ledger.read_text())["stories"]
    assert stories["ST-0350"]["status"] == "pending"
    assert stories["ST-0350"]["returned"] is True
    assert stories["ST-0350"]["reason"] == "- see the CI log"
    assert stories["ST-0351"]["status"] == "pending"
    assert _status_in_backlog(repo, "ST-0350") == "pending"
    assert _status_in_backlog(repo, "ST-0351") == "pending"
