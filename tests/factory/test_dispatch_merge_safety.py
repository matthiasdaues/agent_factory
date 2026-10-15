"""merge-story merges safely (BUG-0036, BUG-0037, BUG-0038).

Each test builds a scratch repository with an invocation branch in its own
worktree, dispatches one story, and drives merge-story the way the
implementation agent does.
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
status: open
deps: []
touches: ["src/{id}.txt"]
outputs: ["src/{id}.txt"]
quality-gates: []
---
# {id}
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


def _dispatch(cwd: Path, ledger: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(DISPATCH), "--ledger", str(ledger), *args],
        cwd=cwd, env=_env(), capture_output=True, text=True, check=False,
    )


@pytest.fixture()
def dispatched(tmp_path: Path) -> dict[str, Path]:
    """A repo with story ST-0001 dispatched from invocation branch feat/x."""
    repo = tmp_path / "repo"
    (repo / "backlog").mkdir(parents=True)
    (repo / "config").mkdir()
    (repo / "src").mkdir()
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    (repo / "backlog" / "ST-0001.md").write_text(STORY.format(id="ST-0001"))
    (repo / "config" / "project.json").write_text('{"test_command": "true"}')
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "src" / ".keep").write_text("")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    inv = repo / ".current-work" / "feat" / "x" / "inv"
    _git(repo, "worktree", "add", "-q", "-b", "feat/x", str(inv))
    ledger = repo / ".current-work" / "feat" / "x" / "dispatch-ledger.yaml"
    base = _git(repo, "rev-parse", "HEAD")
    for args in (
        ("init", "--base", base, "--stories", "ST-0001", "--feature-branch", "feat/x", "--yes"),
        ("plan", "--backlog-dir", "backlog"),
        ("prepare-wave", "1"),
        ("mark-dispatching", "ST-0001"),
        ("mark-dispatched", "ST-0001"),
    ):
        result = _dispatch(repo, ledger, *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)
    story = repo / ".current-work" / "feat" / "x" / "story" / "ST-0001"
    return {"repo": repo, "inv": inv, "story": story, "ledger": ledger}


def _commit_story_work(story: Path) -> str:
    (story / "src" / "ST-0001.txt").write_text("work\n")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", "story work")
    return _git(story, "rev-parse", "HEAD")


def _set_test_command(repo: Path, inv: Path, command: str) -> None:
    for root in (repo, inv):
        (root / "config" / "project.json").write_text(
            '{"test_command": "%s"}' % command
        )


def test_merge_story_refuses_outside_the_invocation_branch(dispatched):
    """BUG-0036: run from the main checkout on dev, nothing is merged."""
    repo, inv, ledger = dispatched["repo"], dispatched["inv"], dispatched["ledger"]
    sha = _commit_story_work(dispatched["story"])
    assert _dispatch(repo, ledger, "verify-story", "ST-0001", "--sha", sha).returncode == 0
    dev_before = _git(repo, "rev-parse", "dev")
    feat_before = _git(repo, "rev-parse", "feat/x")

    result = _dispatch(repo, ledger, "merge-story", "ST-0001")

    assert result.returncode != 0
    assert "feat/x" in result.stderr
    assert _git(repo, "rev-parse", "dev") == dev_before
    assert _git(repo, "rev-parse", "feat/x") == feat_before


def test_merge_story_merges_into_the_invocation_branch(dispatched):
    """BUG-0036 and BUG-0038: from the invocation worktree, the merge lands on
    feat/x and the ledger records the new branch head."""
    repo, inv, ledger = dispatched["repo"], dispatched["inv"], dispatched["ledger"]
    sha = _commit_story_work(dispatched["story"])
    assert _dispatch(repo, ledger, "verify-story", "ST-0001", "--sha", sha).returncode == 0
    dev_before = _git(repo, "rev-parse", "dev")

    result = _dispatch(inv, ledger, "merge-story", "ST-0001")

    assert result.returncode == 0, result.stderr
    head = _git(inv, "rev-parse", "HEAD")
    assert _git(inv, "rev-parse", "HEAD^2") == sha
    assert _git(repo, "rev-parse", "dev") == dev_before
    data = yaml.safe_load(ledger.read_text())
    assert data["branch_head"] == head


def test_verify_story_rejects_a_commit_at_the_base(dispatched):
    """BUG-0037: a story with no commits of its own does not verify."""
    repo, ledger = dispatched["repo"], dispatched["ledger"]
    base = _git(dispatched["story"], "rev-parse", "HEAD")

    result = _dispatch(repo, ledger, "verify-story", "ST-0001", "--sha", base)

    assert result.returncode != 0
    assert "ahead" in result.stderr


def test_merge_story_never_resets_away_earlier_work(dispatched):
    """BUG-0037: an empty story with a red suite leaves the branch intact."""
    repo, inv, ledger = dispatched["repo"], dispatched["inv"], dispatched["ledger"]
    (inv / "src" / "earlier.txt").write_text("earlier merge\n")
    _git(inv, "add", "-A")
    _git(inv, "commit", "-qm", "earlier story")
    _set_test_command(repo, inv, "false")
    head_before = _git(inv, "rev-parse", "HEAD")

    result = _dispatch(inv, ledger, "merge-story", "ST-0001")

    assert result.returncode != 0
    assert _git(inv, "rev-parse", "HEAD") == head_before
    assert (inv / "src" / "earlier.txt").exists()


def test_close_wave_records_branch_head(dispatched):
    """BUG-0038: closing a wave records the head it closed on."""
    import dispatch_lib as lib
    ledger = lib.Ledger.load(dispatched["ledger"])
    ledger.stories["ST-0001"].status = lib.StoryState.BLOCKED
    head = "a" * 40

    ledger.close_wave(1, head)

    assert ledger.branch_head == head


def test_close_wave_from_main_checkout_keeps_the_merged_head(dispatched):
    """BUG-0038: close-wave run from the main checkout records the
    invocation branch's head, not dev."""
    repo, inv, ledger = dispatched["repo"], dispatched["inv"], dispatched["ledger"]
    sha = _commit_story_work(dispatched["story"])
    assert _dispatch(repo, ledger, "verify-story", "ST-0001", "--sha", sha).returncode == 0
    assert _dispatch(inv, ledger, "merge-story", "ST-0001").returncode == 0
    merged_head = _git(inv, "rev-parse", "HEAD")

    _dispatch(repo, ledger, "close-wave", "1")

    data = yaml.safe_load(ledger.read_text())
    assert data["branch_head"] == merged_head


def test_merge_story_completes_an_interrupted_merge(dispatched):
    """BUG-0037: a merge commit made by an interrupted run is recognised and
    the story completes without a second merge."""
    repo, inv, ledger = dispatched["repo"], dispatched["inv"], dispatched["ledger"]
    sha = _commit_story_work(dispatched["story"])
    assert _dispatch(repo, ledger, "verify-story", "ST-0001", "--sha", sha).returncode == 0
    _git(inv, "merge", "--no-ff", "-q", "story/ST-0001", "-m", "interrupted merge")
    merge_commit = _git(inv, "rev-parse", "HEAD")

    result = _dispatch(inv, ledger, "merge-story", "ST-0001")

    assert result.returncode == 0, result.stderr
    assert _git(inv, "rev-parse", "HEAD") == merge_commit
    data = yaml.safe_load(ledger.read_text())
    assert data["stories"]["ST-0001"]["status"] == "done"
