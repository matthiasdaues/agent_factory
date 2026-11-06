"""Dispatch finds its ledger among several, and checks waves and SHAs (BUG-0115).

Each test builds a scratch repository under tmp_path and runs dispatch without
--ledger, so the default ledger is the thing under test.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml
from test_dispatch_merge_safety import DISPATCH, _dispatch, _env, _git
from test_dispatch_run_blockers import _init, _repo


def _run(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    """Run dispatch without --ledger."""
    return subprocess.run(
        [str(DISPATCH), *args], cwd=cwd, env=_env(),
        capture_output=True, text=True, check=False,
    )


def _second_ledger(r: dict[str, Path], branch: str, story_id: str) -> Path:
    path = r["repo"] / ".current-work" / branch / "dispatch-ledger.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(yaml.safe_dump({"version": 1, "stories": {story_id: {"id": story_id}}}))
    return path


def test_bug_0115_current_branch_picks_its_ledger_among_several(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    _second_ledger(r, "other", "ST-0009")
    result = _run(r["inv"], "status")
    assert result.returncode == 0, result.stderr
    assert "ST-0001" in result.stdout


def test_bug_0115_story_branch_picks_the_ledger_holding_its_story(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    _second_ledger(r, "other", "ST-0009")
    story_tree = tmp_path / "story-tree"
    _git(r["repo"], "worktree", "add", "-q", "-b", "story/ST-0002", str(story_tree))
    result = _run(story_tree, "status")
    assert result.returncode == 0, result.stderr
    assert "ST-0002" in result.stdout


def test_bug_0115_no_matching_ledger_names_the_ledgers_and_ledger_flag(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    other = _second_ledger(r, "other", "ST-0009")
    result = _run(r["repo"], "status")
    assert result.returncode == 1
    assert str(r["ledger"]) in result.stderr
    assert str(other) in result.stderr
    assert "--ledger" in result.stderr


def test_bug_0115_one_ledger_stays_the_default(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    result = _run(r["repo"], "status")
    assert result.returncode == 0, result.stderr


def test_bug_0115_prepare_wave_fails_when_no_story_carries_the_wave(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    result = _dispatch(r["repo"], r["ledger"], "prepare-wave", "0")
    assert result.returncode != 0
    assert "wave 0" in result.stderr


def test_bug_0115_verify_story_expands_an_abbreviated_sha(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    worktree = r["repo"] / ".current-work" / "feat" / "x" / "story" / "ST-0001"
    (worktree / "src" / "ST-0001.txt").write_text("x")
    _git(worktree, "add", "-A")
    _git(worktree, "commit", "-qm", "work")
    full = _git(worktree, "rev-parse", "HEAD")
    result = _dispatch(r["repo"], r["ledger"], "verify-story", "ST-0001", "--sha", full[:9])
    assert result.returncode == 0, result.stderr
    stories = yaml.safe_load(r["ledger"].read_text())["stories"]
    entry = stories["ST-0001"] if isinstance(stories, dict) else next(
        s for s in stories if s["id"] == "ST-0001")
    assert entry["commit_sha"] == full


def test_bug_0115_verify_story_rejects_an_unknown_abbreviation(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    result = _dispatch(r["repo"], r["ledger"], "verify-story", "ST-0001", "--sha", "dead0000")
    assert result.returncode == 1
    assert "dead0000" in result.stderr


def test_bug_0115_init_needs_no_default_ledger_among_several(tmp_path):
    r = _repo(tmp_path)
    for name in ("a", "b"):
        path = r["repo"] / ".current-work" / name / "dispatch-ledger.yaml"
        path.parent.mkdir(parents=True)
        path.write_text(yaml.safe_dump({"version": 1, "stories": {}}))
    base = _git(r["repo"], "rev-parse", "HEAD")
    result = _run(
        r["repo"], "init", "--base", base, "--stories", "ST-0001,ST-0002",
        "--feature-branch", "feat/x", "--yes",
    )
    assert result.returncode == 0, result.stderr
