"""Dispatch can run a fix wave (BUG-0082, BUG-0083, BUG-0084, BUG-0085).

Each test builds a scratch repository with an invocation branch in its own
worktree and drives dispatch the way the implementation agent does.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from test_dispatch_merge_safety import STORY, _dispatch, _git

DEPENDENT_STORY = STORY.replace("deps: []", "deps: [ST-0001]")


def _repo(tmp_path: Path, *, testing_yaml: bool = False) -> dict[str, Path]:
    """A repo with ST-0001 and ST-0002 (which depends on ST-0001)."""
    repo = tmp_path / "repo"
    (repo / "backlog").mkdir(parents=True)
    (repo / "src").mkdir()
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    (repo / "backlog" / "ST-0001.md").write_text(STORY.format(id="ST-0001"))
    (repo / "backlog" / "ST-0002.md").write_text(
        DEPENDENT_STORY.format(id="ST-0002")
    )
    if testing_yaml:
        (repo / "docs").mkdir()
        (repo / "docs" / "testing.yaml").write_text(
            '# comment\ntest_all: "false"\ntest_command: "true"\n'
        )
    else:
        (repo / "config").mkdir()
        (repo / "config" / "project.json").write_text('{"test_command": "true"}')
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "src" / ".keep").write_text("")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    inv = repo / ".current-work" / "feat" / "x" / "inv"
    _git(repo, "worktree", "add", "-q", "-b", "feat/x", str(inv))
    ledger = repo / ".current-work" / "feat" / "x" / "dispatch-ledger.yaml"
    return {"repo": repo, "inv": inv, "ledger": ledger}


def _init(r: dict[str, Path], stories: str = "ST-0001,ST-0002"):
    base = _git(r["repo"], "rev-parse", "HEAD")
    return _dispatch(
        r["repo"], r["ledger"], "init", "--base", base, "--stories", stories,
        "--feature-branch", "feat/x", "--yes",
    )


def _ledger(r: dict[str, Path]) -> dict:
    return yaml.safe_load(r["ledger"].read_text())


def _story(ledger: dict, story_id: str) -> dict:
    stories = ledger["stories"]
    if isinstance(stories, dict):
        return stories[story_id]
    return next(entry for entry in stories if entry["id"] == story_id)


# -- BUG-0085: the test command lives in docs/testing.yaml ------------------


def test_init_reads_the_test_command_from_testing_yaml(tmp_path):
    r = _repo(tmp_path, testing_yaml=True)

    result = _init(r)

    assert result.returncode == 0, result.stderr


# -- BUG-0082: dependencies reach the ledger and gate the next story --------


def test_init_records_story_dependencies(tmp_path):
    r = _repo(tmp_path)

    assert _init(r).returncode == 0
    assert _story(_ledger(r), "ST-0002")["deps"] == ["ST-0001"]


def test_plan_refreshes_story_dependencies(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    data = _ledger(r)
    _story(data, "ST-0002")["deps"] = []
    r["ledger"].write_text(yaml.safe_dump(data))

    result = _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog")

    assert result.returncode == 0, result.stderr
    assert _story(_ledger(r), "ST-0002")["deps"] == ["ST-0001"]


def _block_story(r: dict[str, Path], story_id: str) -> None:
    result = _dispatch(
        r["repo"], r["ledger"], "mark-blocked", story_id, "--reason", "red suite",
    )
    assert result.returncode == 0, (result.stdout, result.stderr)


def test_close_wave_does_not_list_a_story_whose_dependency_is_blocked(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    _block_story(r, "ST-0001")

    result = _dispatch(r["inv"], r["ledger"], "close-wave", "1")

    assert result.returncode == 0, result.stderr
    assert _ledger(r)["waves"][0]["next_ready"] == []


def test_prepare_wave_skips_a_story_whose_dependency_is_blocked(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    _block_story(r, "ST-0001")

    result = _dispatch(r["repo"], r["ledger"], "prepare-wave", "2")

    assert result.returncode == 0, result.stderr
    assert "ST-0001" in result.stdout + result.stderr
    assert _story(_ledger(r), "ST-0002")["status"] == "pending"
    branches = _git(r["repo"], "branch", "--list", "story/ST-0002")
    assert branches == ""


# -- BUG-0083: the ledger is runtime state, close-wave commits nothing ------


@pytest.mark.parametrize("where", ["repo", "inv"])
def test_close_wave_saves_the_ledger_without_a_commit(tmp_path, where):
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    _block_story(r, "ST-0001")
    heads = {b: _git(r["repo"], "rev-parse", b) for b in ("dev", "feat/x")}

    result = _dispatch(r[where], r["ledger"], "close-wave", "1")

    assert result.returncode == 0, result.stderr
    assert [w["number"] for w in _ledger(r)["waves"]] == [1]
    assert {b: _git(r["repo"], "rev-parse", b) for b in heads} == heads


# -- BUG-0084: a failed prepare-wave leaves nothing that blocks a retry -----


def test_prepare_wave_retry_succeeds_after_verify_base_fails(tmp_path):
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0

    # Make verify-base fail once: move the invocation branch ahead of the
    # ledger's base, so the story worktree would start behind its target.
    (r["inv"] / "src" / "ahead.txt").write_text("ahead\n")
    _git(r["inv"], "add", "-A")
    _git(r["inv"], "commit", "-qm", "ahead")
    failed = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")
    assert failed.returncode != 0
    assert _git(r["repo"], "branch", "--list", "story/ST-0001") == ""

    # Bring the ledger's base up to the branch, then retry.
    data = _ledger(r)
    data["branch_head"] = _git(r["repo"], "rev-parse", "feat/x")
    r["ledger"].write_text(yaml.safe_dump(data))
    retry = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")

    assert retry.returncode == 0, retry.stderr
    assert _story(_ledger(r), "ST-0001")["status"] == "prepared"


def test_prepare_wave_reuses_a_leftover_branch_without_work(tmp_path):
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    base = _git(r["repo"], "rev-parse", "feat/x")
    # A leftover from an older dispatch version that died between the two
    # git calls.
    _git(r["repo"], "branch", "story/ST-0001", base)

    result = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")

    assert result.returncode == 0, result.stderr
    assert _story(_ledger(r), "ST-0001")["status"] == "prepared"


def test_prepare_wave_refuses_a_leftover_branch_with_work(tmp_path):
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    scratch = r["repo"] / ".current-work" / "scratch"
    _git(r["repo"], "worktree", "add", "-q", "-b", "story/ST-0001", str(scratch))
    (scratch / "src" / "work.txt").write_text("work\n")
    _git(scratch, "add", "-A")
    _git(scratch, "commit", "-qm", "work")
    _git(r["repo"], "worktree", "remove", str(scratch))
    tip = _git(r["repo"], "rev-parse", "story/ST-0001")

    result = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")

    assert result.returncode != 0
    assert "story/ST-0001" in result.stderr
    assert _git(r["repo"], "rev-parse", "story/ST-0001") == tip
