"""Merges of reviewed stories in the run lifecycle (docs/spec/features/run-lifecycle.feature).

Each test builds its own git repository in tmp_path and runs dispatch as a
subprocess, the way the implementation agent does. merge-story runs
premerge-check before it merges.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR

DISPATCH = SOURCE_SCRIPTS_DIR / "dispatch"
STORIES = ("ST-0350", "ST-0351")
REVIEW_DAY = "2026-11-24"
STORY = """---
id: {id}
title: {id}
tier: economy
status: open
deps: []
touches: ["src/{id}.txt", "docs/reviews/code-review-{id}-*.md"]
outputs: ["src/{id}.txt", "docs/reviews/code-review-{id}-*.md"]
quality-gates: []
---
# {id}
"""
REPORT = """---
type: code-review
title: Code review of {id}
date: {day}
status: pass
reviewer: code-review-agent
findings_filed: 0
story: {id}
branch: story/{id}
branch_base: {base}
branch_head: {head}
---

# Code review of {id}

No finding.
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
def wave_repo(tmp_path: Path) -> dict[str, Path]:
    """A repository with ST-0350 and ST-0351 dispatched in wave 1 of feat/login."""
    repo = tmp_path / "repo"
    for folder in ("backlog", "config", "src", "docs/reviews"):
        (repo / folder).mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    for story_id in STORIES:
        (repo / "backlog" / f"{story_id}.md").write_text(STORY.format(id=story_id))
    (repo / "config" / "project.json").write_text('{"test_command": "true"}')
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "src" / ".keep").write_text("")
    (repo / "docs" / "reviews" / ".keep").write_text("")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    feature = repo / ".current-work" / "feat" / "login" / "inv"
    _git(repo, "worktree", "add", "-q", "-b", "feat/login", str(feature))
    ledger = repo / ".current-work" / "feat" / "login" / "dispatch-ledger.yaml"
    for root in (repo, feature):
        report_dir = root / ".current-work" / "dependency-check"
        report_dir.mkdir(parents=True, exist_ok=True)
        for story_id in STORIES:
            (report_dir / f"{story_id}.json").write_text("[]\n")
    base = _git(repo, "rev-parse", "HEAD")
    steps = [
        ("init", "--base", base, "--stories", ",".join(STORIES),
         "--feature-branch", "feat/login", "--yes"),
        ("plan", "--backlog-dir", "backlog"),
        ("prepare-wave", "1"),
    ]
    for story_id in STORIES:
        steps += [("mark-dispatching", story_id), ("mark-dispatched", story_id)]
    for args in steps:
        result = _dispatch(repo, ledger, *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)
    return {"repo": repo, "feature": feature, "ledger": ledger, "base": base}


def _work_and_review(repo: Path, ledger: Path, base: str, story_id: str) -> str:
    """Commit the work of *story_id*, then its review report, and verify the head."""
    story = repo / ".current-work" / "feat" / "login" / "story" / story_id
    (story / "src" / f"{story_id}.txt").write_text("work\n")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", f"feat: work ({story_id})")
    head = _git(story, "rev-parse", "HEAD")
    report = story / "docs" / "reviews" / f"code-review-{story_id}-{REVIEW_DAY}.md"
    report.write_text(REPORT.format(id=story_id, day=REVIEW_DAY, base=base, head=head))
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", f"docs: review {story_id}")
    sha = _git(story, "rev-parse", "HEAD")
    verified = _dispatch(repo, ledger, "verify-story", story_id, "--sha", sha)
    assert verified.returncode == 0, verified.stdout + verified.stderr
    return sha


@pytest.mark.spec("RL-04-IT-01")
def test_RL_04_IT_01_two_stories_reviewed_on_one_day_merge_without_a_conflict(wave_repo):
    """Scenario: Two stories reviewed on the same day merge without a conflict on
    their reports."""
    repo, feature, ledger, base = (
        wave_repo["repo"], wave_repo["feature"], wave_repo["ledger"], wave_repo["base"],
    )
    heads = {story_id: _work_and_review(repo, ledger, base, story_id) for story_id in STORIES}

    for story_id in STORIES:
        result = _dispatch(feature, ledger, "merge-story", story_id)
        assert result.returncode == 0, (story_id, result.stdout + result.stderr)
        # merge-story refreshes ST-0351 from feat/login first, so the merged
        # head can be a refresh merge on top of the reviewed head.
        _git(feature, "merge-base", "--is-ancestor", heads[story_id], "HEAD")

    reports = sorted(path.name for path in (feature / "docs" / "reviews").glob("code-review-*.md"))
    assert reports == [f"code-review-{story_id}-{REVIEW_DAY}.md" for story_id in STORIES]
    assert _git(feature, "status", "--porcelain") == ""
