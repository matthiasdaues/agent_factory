"""dispatch commands of the run lifecycle (docs/spec/features/run-lifecycle.feature).

Each test builds its own git repository in tmp_path and runs dispatch as a
subprocess, the way the implementation agent does.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from conftest import SOURCE_SCRIPTS_DIR, write_review_report

import dispatch_lib as lib

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
TESTING_YAML = 'test_command: "true"\n'


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


def _write_passing_dependency_results(root: Path, story_id: str) -> None:
    """premerge-check requires a dependency-check result for every story (BR-066)."""
    report_dir = root / ".current-work" / "dependency-check"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f"{story_id}.json").write_text("[]\n")


def _snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    return {
        str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _install_copy(checkout: Path) -> Path:
    """Write an installed copy that differs from packages/factory."""
    installed = checkout / ".agent-factory" / "factory"
    (installed / "scripts").mkdir(parents=True)
    (installed / "scripts" / "tool").write_text("installed\n")
    (installed / "VERSION").write_text("0.1\n")
    return installed


@pytest.fixture()
def factory_repo(tmp_path: Path) -> dict[str, Path]:
    """A repository with packages/factory, an ignored installed copy, and
    story ST-0350 dispatched from feature branch feat/x."""
    repo = tmp_path / "repo"
    for folder in ("backlog", "docs", "src", "packages/factory/scripts"):
        (repo / folder).mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    (repo / "backlog" / "ST-0350.md").write_text(STORY.format(id="ST-0350"))
    (repo / "docs" / "testing.yaml").write_text(TESTING_YAML)
    (repo / ".gitignore").write_text(".current-work/\n/.agent-factory/\n")
    (repo / "src" / ".keep").write_text("")
    (repo / "packages" / "factory" / "scripts" / "tool").write_text("source\n")
    (repo / "packages" / "factory" / "NEW").write_text("only in source\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    feature = repo / ".current-work" / "feat" / "x" / "inv"
    _git(repo, "worktree", "add", "-q", "-b", "feat/x", str(feature))
    ledger = repo / ".current-work" / "feat" / "x" / "dispatch-ledger.yaml"
    for root in (repo, feature):
        _write_passing_dependency_results(root, "ST-0350")
        _install_copy(root)
    base = _git(repo, "rev-parse", "HEAD")
    for args in (
        ("init", "--base", base, "--stories", "ST-0350", "--feature-branch", "feat/x", "--yes"),
        ("plan", "--backlog-dir", "backlog"),
        ("prepare-wave", "1"),
        ("mark-dispatching", "ST-0350"),
        ("mark-dispatched", "ST-0350"),
    ):
        result = _dispatch(repo, ledger, *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)
    story = repo / ".current-work" / "feat" / "x" / "story" / "ST-0350"
    return {"repo": repo, "feature": feature, "story": story, "ledger": ledger}


@pytest.mark.spec("RL-18-IT-01")
def test_RL_18_IT_01_merge_story_copies_nothing_into_the_installed_copy(factory_repo):
    """Scenario: merge-story copies nothing into the installed copy."""
    repo, feature, ledger = (
        factory_repo["repo"], factory_repo["feature"], factory_repo["ledger"],
    )
    story = factory_repo["story"]
    (story / "src" / "ST-0350.txt").write_text("work\n")
    write_review_report(story, "ST-0350")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", "story work")
    sha = _git(story, "rev-parse", "HEAD")
    assert _dispatch(repo, ledger, "verify-story", "ST-0350", "--sha", sha).returncode == 0
    before = {
        root: _snapshot(root / ".agent-factory" / "factory") for root in (repo, feature)
    }

    result = _dispatch(feature, ledger, "merge-story", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    assert _git(feature, "rev-parse", "HEAD^2") == sha
    for root in (repo, feature):
        assert _snapshot(root / ".agent-factory" / "factory") == before[root]


# -- RL-01: User starts a run on a feature branch in either way of driving it --


@pytest.fixture()
def run_repo(tmp_path: Path) -> Path:
    """A repository on dev with a test command and ST-0350 to ST-0353 pending."""
    repo = tmp_path / "repo"
    for folder in ("backlog", "docs", "src"):
        (repo / folder).mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    for story_id in ("ST-0350", "ST-0351", "ST-0352", "ST-0353"):
        (repo / "backlog" / f"{story_id}.md").write_text(
            STORY.format(id=story_id).replace("status: open", "status: pending")
        )
    (repo / "docs" / "testing.yaml").write_text(TESTING_YAML)
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "src" / ".keep").write_text("")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    return repo


def _ledger_path(repo: Path, branch: str) -> Path:
    return repo / ".current-work" / branch / "dispatch-ledger.yaml"


def _init(repo: Path, branch: str, stories: str, *mode: str) -> subprocess.CompletedProcess:
    return _dispatch(
        repo, _ledger_path(repo, branch), "init", *mode, "--base", "dev",
        "--feature-branch", branch, "--stories", stories,
    )


def _ledger(repo: Path, branch: str) -> dict:
    return yaml.safe_load(_ledger_path(repo, branch).read_text())


def _worktree_branches(repo: Path) -> list[str]:
    out = _git(repo, "worktree", "list", "--porcelain")
    return [
        line[len("branch refs/heads/"):]
        for line in out.splitlines()
        if line.startswith("branch refs/heads/")
    ]


def _linked_worktree_of(repo: Path, branch: str) -> Path | None:
    out = _git(repo, "worktree", "list", "--porcelain")
    path = None
    for line in out.splitlines():
        if line.startswith("worktree "):
            path = Path(line[len("worktree "):])
        elif line == f"branch refs/heads/{branch}":
            return path
    return None


@pytest.mark.spec("RL-01-IT-01")
def test_RL_01_IT_01_a_run_by_hand_starts_without_a_worktree(run_repo):
    """Scenario: A run by hand starts without a worktree for the feature branch."""
    dev_tip = _git(run_repo, "rev-parse", "dev")

    result = _init(run_repo, "feature/login", "ST-0350,ST-0351", "--mode", "by-hand")

    assert result.returncode == 0, result.stderr
    assert _git(run_repo, "rev-parse", "feature/login") == dev_tip
    assert "feature/login" not in _worktree_branches(run_repo)
    assert _git(run_repo, "branch", "--show-current") == "dev"
    ledger = _ledger(run_repo, "feature/login")
    assert ledger["mode"] == "by-hand"
    assert {sid: entry["status"] for sid, entry in ledger["stories"].items()} == {
        "ST-0350": "pending", "ST-0351": "pending",
    }
    status = _dispatch(run_repo, _ledger_path(run_repo, "feature/login"), "status")
    assert status.returncode == 0, status.stderr
    assert "mode: by-hand" in status.stdout
    assert "feature_branch: feature/login" in status.stdout


@pytest.mark.spec("RL-01-IT-02")
@pytest.mark.parametrize("mode", [("--mode", "orchestrated"), ()], ids=["orchestrated", "absent"])
def test_RL_01_IT_02_an_orchestrated_run_starts_with_a_worktree(run_repo, mode):
    """Scenario: An orchestrated run starts with a worktree for the feature branch.
    Scenario: dispatch init without --mode starts an orchestrated run."""
    result = _init(run_repo, "feature/login", "ST-0350", *mode)

    assert result.returncode == 0, result.stderr
    worktree = _linked_worktree_of(run_repo, "feature/login")
    assert worktree is not None
    assert worktree.is_relative_to(run_repo / ".current-work")
    assert _ledger(run_repo, "feature/login")["mode"] == "orchestrated"


@pytest.mark.spec("RL-01-IT-03")
def test_RL_01_IT_03_the_branch_root_is_the_tip_of_the_feature_branch(run_repo):
    """Scenario: The branch root is the tip of the feature branch at init."""
    _git(run_repo, "branch", "feature/login", "dev")
    worktree = run_repo.parent / "login"
    _git(run_repo, "worktree", "add", "-q", str(worktree), "feature/login")
    (worktree / "src" / "ahead.txt").write_text("ahead\n")
    _git(worktree, "add", "-A")
    _git(worktree, "commit", "-qm", "ahead of dev")
    tip = _git(run_repo, "rev-parse", "feature/login")
    assert tip != _git(run_repo, "rev-parse", "dev")

    result = _init(run_repo, "feature/login", "ST-0350", "--mode", "orchestrated")

    assert result.returncode == 0, result.stderr
    branch_root = _ledger(run_repo, "feature/login")["branch_root"]
    assert branch_root == tip
    assert len(branch_root) == 40


@pytest.mark.spec("RL-01-IT-04")
@pytest.mark.parametrize("first", ["orchestrated", "by-hand"])
def test_RL_01_IT_04_a_second_orchestrated_run_starts_beside_another(run_repo, first):
    """Scenario: A second orchestrated run starts while another run is active.
    The pair beside an active run by hand is a case of the same class."""
    assert _init(run_repo, "feature/login", "ST-0350", "--mode", first).returncode == 0

    result = _init(run_repo, "feature/search", "ST-0352", "--mode", "orchestrated")

    assert result.returncode == 0, result.stderr
    assert _ledger_path(run_repo, "feature/search").exists()
    assert _linked_worktree_of(run_repo, "feature/search") is not None


@pytest.mark.spec("RL-01-IT-04")
def test_RL_01_IT_04_a_second_run_by_hand_is_refused(run_repo):
    """Scenario: A second run by hand is refused while a run by hand is active."""
    assert _init(run_repo, "feature/login", "ST-0350", "--mode", "by-hand").returncode == 0

    result = _init(run_repo, "feature/search", "ST-0352", "--mode", "by-hand")

    assert result.returncode != 0
    assert "feature/login" in result.stderr
    assert not _ledger_path(run_repo, "feature/search").exists()
    assert _git(run_repo, "branch", "--list", "feature/search") == ""


@pytest.mark.spec("RL-01-IT-05")
def test_RL_01_IT_05_a_ledger_with_other_stories_is_refused(run_repo):
    """Scenario: A feature branch whose ledger lists other stories is refused."""
    assert _init(run_repo, "feature/login", "ST-0350").returncode == 0
    before = _ledger_path(run_repo, "feature/login").read_text()

    result = _init(run_repo, "feature/login", "ST-0351", "--mode", "orchestrated")

    assert result.returncode != 0
    assert str(_ledger_path(run_repo, "feature/login")) in result.stderr
    assert _ledger_path(run_repo, "feature/login").read_text() == before
    assert list(_ledger(run_repo, "feature/login")["stories"]) == ["ST-0350"]


@pytest.mark.spec("RL-01-IT-05")
def test_RL_01_IT_05_the_same_stories_resume_an_interrupted_start(run_repo):
    """Scenario: dispatch init on a ledger with the same stories resumes an
    interrupted start. The stories come in another order."""
    assert _init(run_repo, "feature/login", "ST-0350,ST-0351").returncode == 0
    before = _snapshot(_ledger_path(run_repo, "feature/login").parent)

    result = _init(run_repo, "feature/login", "ST-0351,ST-0350", "--mode", "orchestrated")

    assert result.returncode == 0, result.stderr
    assert _snapshot(_ledger_path(run_repo, "feature/login").parent) == before


@pytest.mark.spec("RL-01-IT-06")
def test_RL_01_IT_06_a_dependency_outside_the_run_that_is_not_done_is_refused(run_repo):
    """Scenario: A story whose dependency outside the run is not done is refused."""
    story = run_repo / "backlog" / "ST-0351.md"
    story.write_text(story.read_text().replace("deps: []", "deps: [ST-0349]"))
    (run_repo / "backlog" / "ST-0349.md").write_text(
        STORY.format(id="ST-0349").replace("status: open", "status: pending")
    )

    result = _init(run_repo, "feature/login", "ST-0351", "--mode", "orchestrated")

    assert result.returncode != 0
    assert "ST-0349" in result.stderr
    assert not _ledger_path(run_repo, "feature/login").exists()


@pytest.mark.spec("RL-01-IT-06")
def test_RL_01_IT_06_a_done_dependency_outside_the_run_passes(run_repo):
    """A dependency outside the run that is done in the backlog lets the run start."""
    story = run_repo / "backlog" / "ST-0351.md"
    story.write_text(story.read_text().replace("deps: []", "deps: [ST-0349, ST-0350]"))
    (run_repo / "backlog" / "ST-0349.md").write_text(
        STORY.format(id="ST-0349").replace("status: open", "status: done")
    )

    result = _init(run_repo, "feature/login", "ST-0350,ST-0351", "--mode", "orchestrated")

    assert result.returncode == 0, result.stderr


# -- RL-17: the ledger is the memory of the run --------------------------------


@pytest.mark.spec("RL-17-IT-02")
def test_RL_17_IT_02_a_new_session_continues_an_interrupted_run(factory_repo):
    """Scenario: A new session continues an interrupted run.

    The fixture stops after mark-dispatched. Each later call is a new process
    that finds the ledger on its own, as a new session does."""
    repo, story = factory_repo["repo"], factory_repo["story"]

    status = subprocess.run(
        [str(DISPATCH), "status"], cwd=repo, env=_env(),
        capture_output=True, text=True, check=False,
    )
    assert status.returncode == 0, status.stderr
    assert re.search(r"ST-0350\s+1\s+dispatched", status.stdout)

    (story / "src" / "ST-0350.txt").write_text("work\n")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", "story work")
    sha = _git(story, "rev-parse", "HEAD")
    verify = subprocess.run(
        [str(DISPATCH), "verify-story", "ST-0350", "--sha", sha], cwd=story,
        env=_env(), capture_output=True, text=True, check=False,
    )

    assert verify.returncode == 0, verify.stderr
    entry = yaml.safe_load(factory_repo["ledger"].read_text())["stories"]["ST-0350"]
    assert entry["commit_sha"] == sha


# -- RL-03: User approves each step that needs a person in a run driven by hand --


def _by_hand_run(repo: Path, stories: str = "ST-0350,ST-0351") -> Path:
    """Start a run by hand on feature/login and return its ledger path."""
    result = _init(repo, "feature/login", stories, "--mode", "by-hand")
    assert result.returncode == 0, result.stderr
    return _ledger_path(repo, "feature/login")


@pytest.mark.spec("RL-03-IT-01")
def test_RL_03_IT_01_prepare_story_checks_out_the_story_branch_by_hand(run_repo):
    """Scenario: prepare-story checks out the story branch in the primary checkout.
    Scenario: By hand, prepare-story writes the manifest and the contract
    without a worktree."""
    ledger = _by_hand_run(run_repo)
    tip = _git(run_repo, "rev-parse", "feature/login")

    result = _dispatch(run_repo, ledger, "prepare-story", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    assert _git(run_repo, "branch", "--show-current") == "story/ST-0350"
    assert _git(run_repo, "rev-parse", "story/ST-0350") == tip
    assert _worktree_branches(run_repo) == ["story/ST-0350"]
    folder = run_repo / ".current-work" / "feature" / "login" / "story" / "ST-0350"
    assert (folder / "current-step.yml").is_file()
    assert (folder / "handoff-contract.md").is_file()
    entry = _ledger(run_repo, "feature/login")["stories"]["ST-0350"]
    assert entry["status"] == "prepared"
    assert entry["branch"] == "story/ST-0350"
    assert entry["worktree"] is None
    assert entry["base_sha"] == tip
    status = _dispatch(run_repo, ledger, "status")
    assert re.search(r"ST-0350\s+1\s+prepared", status.stdout), status.stdout


@pytest.mark.spec("RL-03-IT-01")
def test_RL_03_IT_01_prepare_story_by_hand_refuses_an_open_dependency(run_repo):
    """BR-113: a story starts only when every dependency inside the run is done."""
    story = run_repo / "backlog" / "ST-0351.md"
    story.write_text(story.read_text().replace("deps: []", "deps: [ST-0350]"))
    _git(run_repo, "commit", "-qam", "ST-0351 depends on ST-0350")
    ledger = _by_hand_run(run_repo)

    result = _dispatch(run_repo, ledger, "prepare-story", "ST-0351")

    assert result.returncode != 0
    assert "ST-0350" in result.stderr
    assert _git(run_repo, "branch", "--show-current") == "dev"
    assert _git(run_repo, "branch", "--list", "story/ST-0351") == ""
    assert _ledger(run_repo, "feature/login")["stories"]["ST-0351"]["status"] == "pending"


def _close_wave_one(repo: Path, ledger: Path, *, record: bool) -> None:
    """Record ST-0350 as done in wave 1, with or without a wave record."""
    data = yaml.safe_load(ledger.read_text())
    data["stories"]["ST-0350"].update(status="done", wave=1)
    if record:
        data["waves"] = [{
            "number": 1, "completed": [{"id": "ST-0350", "merge_sha": None}],
            "blocked": [], "failed": [], "next_ready": ["ST-0351"],
            "branch_head": data["branch_root"],
        }]
    ledger.write_text(yaml.safe_dump(data, sort_keys=False))


@pytest.mark.spec("RL-03-IT-02")
def test_RL_03_IT_02_prepare_story_by_hand_records_the_next_free_wave(run_repo):
    """Scenario: By hand, prepare-story records the next free wave number."""
    ledger = _by_hand_run(run_repo)
    _close_wave_one(run_repo, ledger, record=True)

    result = _dispatch(run_repo, ledger, "prepare-story", "ST-0351")

    assert result.returncode == 0, result.stdout + result.stderr
    entry = _ledger(run_repo, "feature/login")["stories"]["ST-0351"]
    assert entry["wave"] == 2
    assert entry["status"] == "prepared"


@pytest.mark.spec("RL-03-IT-02")
def test_RL_03_IT_02_prepare_story_by_hand_waits_for_the_wave_record(run_repo):
    """BR-113: prepare-story refuses until the previous wave has a wave record."""
    ledger = _by_hand_run(run_repo)
    _close_wave_one(run_repo, ledger, record=False)

    result = _dispatch(run_repo, ledger, "prepare-story", "ST-0351")

    assert result.returncode != 0
    assert "close-wave 1" in result.stderr
    assert _git(run_repo, "branch", "--show-current") == "dev"
    entry = _ledger(run_repo, "feature/login")["stories"]["ST-0351"]
    assert entry["status"] == "pending"
    assert entry["wave"] is None


@pytest.mark.spec("RL-02-IT-01")
def test_RL_02_IT_01_a_story_reaches_dispatched_in_a_run_by_hand(run_repo):
    """Scenario: A story reaches dispatched in a run by hand."""
    ledger = _by_hand_run(run_repo)
    assert _dispatch(run_repo, ledger, "prepare-story", "ST-0350").returncode == 0

    dispatching = _dispatch(run_repo, ledger, "mark-dispatching", "ST-0350")
    (run_repo / "src" / "ST-0350.txt").write_text("work\n")
    _git(run_repo, "add", "src/ST-0350.txt")
    _git(run_repo, "commit", "-qm", "feat: story work (ST-0350)")
    dispatched = _dispatch(run_repo, ledger, "mark-dispatched", "ST-0350")

    assert dispatching.returncode == 0, dispatching.stderr
    assert dispatched.returncode == 0, dispatched.stderr
    assert _ledger(run_repo, "feature/login")["stories"]["ST-0350"]["status"] == "dispatched"
    status = _dispatch(run_repo, ledger, "status")
    assert re.search(r"ST-0350\s+1\s+dispatched", status.stdout), status.stdout


@pytest.mark.spec("RL-03-IT-01")
def test_RL_03_IT_01_prepare_story_by_hand_refuses_uncommitted_tracked_changes(run_repo):
    """Decision of 2026-11-18: by hand, prepare-story refuses an uncommitted
    change to a tracked file and names the file. Untracked files do not count."""
    ledger = _by_hand_run(run_repo)
    (run_repo / "src" / ".keep").write_text("edited\n")
    (run_repo / "src" / "draft.txt").write_text("untracked\n")

    result = _dispatch(run_repo, ledger, "prepare-story", "ST-0350")

    assert result.returncode == 1
    assert "src/.keep" in result.stderr
    assert "draft.txt" not in result.stderr
    assert _git(run_repo, "branch", "--show-current") == "dev"
    assert _git(run_repo, "branch", "--list", "story/ST-0350") == ""
    assert (run_repo / "src" / ".keep").read_text() == "edited\n"
    assert _ledger(run_repo, "feature/login")["stories"]["ST-0350"]["status"] == "pending"

    (run_repo / "src" / ".keep").write_text("")
    retry = _dispatch(run_repo, ledger, "prepare-story", "ST-0350")
    assert retry.returncode == 0, retry.stderr


@pytest.mark.spec("RL-03-IT-01")
def test_RL_03_IT_01_prepare_story_by_hand_refuses_a_staged_change_reverted_in_the_tree(
    run_repo,
):
    """Review note N4: a change that is staged and then reverted in the working
    tree is still uncommitted, so prepare-story refuses it and names the file."""
    ledger = _by_hand_run(run_repo)
    (run_repo / "src" / ".keep").write_text("staged\n")
    _git(run_repo, "add", "src/.keep")
    (run_repo / "src" / ".keep").write_text("")

    result = _dispatch(run_repo, ledger, "prepare-story", "ST-0350")

    assert result.returncode == 1
    assert "  src/.keep" in result.stderr
    assert _git(run_repo, "branch", "--show-current") == "dev"
    assert _git(run_repo, "branch", "--list", "story/ST-0350") == ""
    assert _ledger(run_repo, "feature/login")["stories"]["ST-0350"]["status"] == "pending"


@pytest.mark.spec("RL-03-IT-01")
def test_RL_03_IT_01_prepare_story_by_hand_fails_closed_when_git_status_fails(run_repo):
    """Review note N5: when git cannot report the state of the primary
    checkout, prepare-story refuses with exit 1 and names the git error."""
    ledger = _by_hand_run(run_repo)
    (run_repo / ".git" / "index").write_bytes(b"garbage")

    result = _dispatch(run_repo, ledger, "prepare-story", "ST-0350")

    assert result.returncode == 1
    assert "git status failed" in result.stderr
    assert "index file" in result.stderr
    assert _git(run_repo, "branch", "--list", "story/ST-0350") == ""
    assert _ledger(run_repo, "feature/login")["stories"]["ST-0350"]["status"] == "pending"


@pytest.mark.spec("RL-03-IT-01")
def test_RL_03_IT_01_a_failing_post_checkout_hook_restores_the_earlier_branch(run_repo):
    """IMPL-0028: git switches the branch and then returns the hook's exit
    status, so prepare-story checks the earlier branch out again."""
    ledger = _by_hand_run(run_repo)
    hook = run_repo / ".git" / "hooks" / "post-checkout"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)

    result = _dispatch(run_repo, ledger, "prepare-story", "ST-0350")

    assert result.returncode != 0
    assert _git(run_repo, "branch", "--show-current") == "dev"
    assert _git(run_repo, "branch", "--list", "story/ST-0350") == ""
    assert _ledger(run_repo, "feature/login")["stories"]["ST-0350"]["status"] == "pending"


@pytest.mark.spec("RL-03-IT-01")
def test_RL_03_IT_01_prepare_story_by_hand_refuses_a_ledger_of_another_checkout(
    run_repo, tmp_path
):
    """IMPL-0029: the ledger must lie under .current-work of the primary
    checkout the command runs against."""
    ledger = _by_hand_run(run_repo)
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "-q", "-b", "dev", str(run_repo), str(clone))
    _git(clone, "branch", "feature/login", "origin/feature/login")

    result = _dispatch(clone, ledger, "prepare-story", "ST-0350")

    assert result.returncode == 1
    assert ".current-work" in result.stderr
    assert _git(clone, "branch", "--show-current") == "dev"
    assert _git(clone, "branch", "--list", "story/ST-0350") == ""
    assert _git(run_repo, "branch", "--show-current") == "dev"
    assert _ledger(run_repo, "feature/login")["stories"]["ST-0350"]["status"] == "pending"


# -- RL-03 and RL-02: merge-story in a run by hand ------------------------------

RULES = "docs/spec/dependency-rules.dsl"
MERGE_STORY = """---
id: {id}
title: {id}
tier: economy
status: pending
deps: []
touches: ["src/{id}.txt", "src/{id}.py"]
outputs: ["src/{id}.txt", "src/{id}.py"]
quality-gates: []
---
# {id}
"""
RECORDING_GATE = """#!/usr/bin/env bash
git -C {repo} branch --show-current >> {log}
report_dir=""
while [ $# -gt 0 ]; do
  if [ "$1" = "--report-dir" ]; then report_dir="$2"; fi
  shift
done
mkdir -p "$report_dir"
echo "[]" > "$report_dir/ST-0350.json"
"""


def _dispatched_by_hand(
    tmp_path: Path, *, code: str, rules: bool, testing: str = TESTING_YAML
) -> dict[str, Path]:
    """A run by hand on feature/login whose ST-0350 is dispatched and reviewed
    in the primary checkout; *code* becomes src/ST-0350.py, and *testing*
    becomes docs/testing.yaml."""
    repo = tmp_path / "repo"
    for folder in ("backlog", "docs/spec", "src"):
        (repo / folder).mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    for story_id in ("ST-0350", "ST-0351"):
        (repo / "backlog" / f"{story_id}.md").write_text(MERGE_STORY.format(id=story_id))
    (repo / "docs" / "testing.yaml").write_text(testing)
    (repo / ".gitignore").write_text(".current-work/\n/.agent-factory/\n")
    (repo / "src" / ".keep").write_text("")
    if rules:
        (repo / RULES).write_text("src must_not_depend_on infra\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    ledger = _by_hand_run(repo)
    for args in (("prepare-story", "ST-0350"), ("mark-dispatching", "ST-0350")):
        result = _dispatch(repo, ledger, *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)
    (repo / "src" / "ST-0350.txt").write_text("work\n")
    (repo / "src" / "ST-0350.py").write_text(code)
    _git(repo, "add", "src")
    _git(repo, "commit", "-qm", "feat: story work (ST-0350)")
    write_review_report(repo, "ST-0350")
    _git(repo, "add", "docs/reviews")
    _git(repo, "commit", "-qm", "docs: review ST-0350")
    result = _dispatch(repo, ledger, "mark-dispatched", "ST-0350")
    assert result.returncode == 0, result.stdout + result.stderr
    return {"repo": repo, "ledger": ledger}


def _record_gate_branch(repo: Path, log: Path) -> None:
    """Install a passing dependency-check that logs the primary checkout's branch."""
    script = repo / ".agent-factory" / "factory" / "scripts" / "dependency-check"
    script.parent.mkdir(parents=True)
    script.write_text(RECORDING_GATE.format(repo=repo, log=log))
    script.chmod(0o755)


def _tracked_files(repo: Path) -> dict[str, tuple[bytes, int]]:
    return {
        name: ((repo / name).read_bytes(), (repo / name).stat().st_mtime_ns)
        for name in _git(repo, "ls-files").splitlines()
    }


@pytest.mark.spec("RL-03-IT-03")
def test_RL_03_IT_03_merge_story_runs_premerge_check_before_the_checkout(tmp_path):
    """Scenario: merge-story runs premerge-check before it checks out the
    feature branch."""
    run = _dispatched_by_hand(tmp_path, code="import os\n", rules=True)
    repo, ledger = run["repo"], run["ledger"]
    log = tmp_path / "gate.log"
    _record_gate_branch(repo, log)
    story_tip = _git(repo, "rev-parse", "story/ST-0350")

    result = _dispatch(repo, ledger, "merge-story", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    assert log.read_text().splitlines() == ["story/ST-0350"]
    assert _git(repo, "branch", "--show-current") == "feature/login"
    assert _git(repo, "rev-parse", "feature/login^2") == story_tip


@pytest.mark.spec("RL-03-IT-04")
def test_RL_03_IT_04_a_refused_premerge_check_leaves_the_story_branch(tmp_path):
    """Scenario: A refused premerge-check leaves the primary checkout on the
    story branch."""
    run = _dispatched_by_hand(tmp_path, code="import infra\n", rules=True)
    repo, ledger = run["repo"], run["ledger"]
    tip = _git(repo, "rev-parse", "feature/login")
    files = _tracked_files(repo)

    result = _dispatch(repo, ledger, "merge-story", "ST-0350")

    assert result.returncode == 1, result.stdout + result.stderr
    assert "BLOCK semantic-gates: dependency-check" in result.stdout
    assert _git(repo, "branch", "--show-current") == "story/ST-0350"
    assert _tracked_files(repo) == files
    assert _git(repo, "rev-parse", "feature/login") == tip
    assert _ledger(repo, "feature/login")["stories"]["ST-0350"]["status"] == "dispatched"


@pytest.mark.spec("RL-03-IT-04")
def test_RL_03_IT_04_a_changed_tracked_file_does_not_hide_a_failing_gate(tmp_path):
    """Scenario: A changed tracked file in the primary checkout does not hide a
    failing gate."""
    run = _dispatched_by_hand(tmp_path, code="import infra\n", rules=True)
    repo, ledger = run["repo"], run["ledger"]
    tip = _git(repo, "rev-parse", "feature/login")
    changed = repo / "src" / "ST-0350.py"
    changed.write_text("import infra\nchanged = True\n")

    result = _dispatch(repo, ledger, "merge-story", "ST-0350")

    output = result.stdout + result.stderr
    assert result.returncode == 1, output
    assert "BLOCK semantic-gates: dependency-check" in result.stdout
    assert "would be overwritten" not in output
    assert "Your local changes" not in output
    assert _git(repo, "branch", "--show-current") == "story/ST-0350"
    assert changed.read_text() == "import infra\nchanged = True\n"
    assert _git(repo, "rev-parse", "feature/login") == tip


@pytest.mark.spec("RL-03-IT-05")
def test_RL_03_IT_05_a_refused_checkout_stops_merge_story_by_hand(tmp_path):
    """Scenario: A refused checkout of the feature branch stops merge-story in a
    run by hand."""
    run = _dispatched_by_hand(tmp_path, code="import os\n", rules=True)
    repo, ledger = run["repo"], run["ledger"]
    log = tmp_path / "gate.log"
    _record_gate_branch(repo, log)
    tip = _git(repo, "rev-parse", "feature/login")
    changed = repo / "src" / "ST-0350.py"
    changed.write_text("import os\nchanged = True\n")

    refused = _dispatch(repo, ledger, "merge-story", "ST-0350")

    assert refused.returncode == 1, refused.stdout + refused.stderr
    assert "PASS" in refused.stdout
    assert "src/ST-0350.py" in refused.stderr
    assert f"primary checkout {repo}" in refused.stderr
    assert _ledger(repo, "feature/login")["stories"]["ST-0350"]["status"] == "dispatched"
    assert _git(repo, "branch", "--show-current") == "story/ST-0350"
    assert changed.read_text() == "import os\nchanged = True\n"
    assert _git(repo, "rev-parse", "feature/login") == tip
    assert log.read_text().splitlines() == ["story/ST-0350"]

    _git(repo, "checkout", "--", "src/ST-0350.py")
    second = _dispatch(repo, ledger, "merge-story", "ST-0350")

    assert second.returncode == 0, second.stdout + second.stderr
    assert log.read_text().splitlines() == ["story/ST-0350", "story/ST-0350"]
    assert _git(repo, "branch", "--show-current") == "feature/login"


@pytest.mark.spec("RL-02-IT-02")
def test_RL_02_IT_02_only_merge_story_sets_the_story_to_done(tmp_path):
    """Scenario: Only dispatch merge-story sets a story to done."""
    run = _dispatched_by_hand(tmp_path, code="import os\n", rules=False)
    repo, ledger = run["repo"], run["ledger"]
    story_commits = _git(repo, "rev-list", "feature/login..story/ST-0350").splitlines()

    result = _dispatch(repo, ledger, "merge-story", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    merged = _git(repo, "show", "feature/login:backlog/ST-0350.md")
    assert "status: done" in merged.splitlines()
    assert _git(repo, "rev-parse", "feature/login^2") == story_commits[0]
    for sha in story_commits:
        story_file = _git(repo, "show", f"{sha}:backlog/ST-0350.md")
        assert "status: done" not in story_file.splitlines(), sha
    status = _dispatch(repo, ledger, "status")
    assert re.search(r"ST-0350\s+1\s+done", status.stdout), status.stdout


@pytest.mark.spec("RL-17-IT-01")
def test_RL_17_IT_01_commit_sha_holds_the_merge_commit(tmp_path):
    """Scenario: After a merge, commit_sha holds the merge commit."""
    run = _dispatched_by_hand(tmp_path, code="import os\n", rules=False)
    repo, ledger = run["repo"], run["ledger"]

    result = _dispatch(repo, ledger, "merge-story", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    merge_commit = _git(repo, "rev-parse", "feature/login")
    assert _git(repo, "rev-parse", "feature/login^2")
    data = _ledger(repo, "feature/login")
    assert data["stories"]["ST-0350"]["commit_sha"] == merge_commit
    # close-wave by hand belongs to ST-0421, so the test writes the wave record.
    data["waves"] = [{
        "number": 1, "completed": [{"id": "ST-0350", "merge_sha": merge_commit}],
        "blocked": [], "failed": [], "next_ready": ["ST-0351"],
        "branch_head": merge_commit,
    }]
    ledger.write_text(yaml.safe_dump(data, sort_keys=False))

    prepared = _dispatch(repo, ledger, "prepare-story", "ST-0351")

    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    assert _ledger(repo, "feature/login")["stories"]["ST-0351"]["base_sha"] == merge_commit
    assert _git(repo, "rev-parse", "story/ST-0351") == merge_commit


# A suite that fails only with feature/login checked out, so premerge-check
# passes in its temporary worktree and the run after the merge fails.
RED_ON_FEATURE = (
    'test_command: "test \\"$(git branch --show-current)\\" != feature/login"\n'
)


@pytest.mark.spec("RL-06-IT-02")
def test_RL_06_IT_02_a_red_suite_by_hand_keeps_a_change_outside_the_story(tmp_path):
    """Scenario: A red test suite after a merge moves the feature branch back.

    By hand, the rollback keeps an uncommitted change to a file that the story
    did not touch (IMPL-0031)."""
    run = _dispatched_by_hand(
        tmp_path, code="import os\n", rules=False, testing=RED_ON_FEATURE
    )
    repo, ledger = run["repo"], run["ledger"]
    tip = _git(repo, "rev-parse", "feature/login")
    untouched = repo / "src" / ".keep"
    untouched.write_text("my uncommitted work\n")

    result = _dispatch(repo, ledger, "merge-story", "ST-0350")

    assert result.returncode == 1, result.stdout + result.stderr
    assert "test suite failed after merging" in result.stderr
    assert untouched.read_text() == "my uncommitted work\n"
    assert _git(repo, "rev-parse", "feature/login") == tip
    entry = _ledger(repo, "feature/login")["stories"]["ST-0350"]
    assert entry["status"] == "blocked"
    assert entry["reason"] == "post-merge test failure"


# The hook prints no name of its own, so the name in the message comes from
# merge-story.
REFUSING_PRE_COMMIT = "#!/bin/sh\necho 'refused' >&2\nexit 1\n"


def _refuse_commits(repo: Path) -> Path:
    """Install a pre-commit hook that refuses every commit, so also the amend."""
    hook = Path(_git(repo, "rev-parse", "--absolute-git-dir")) / "hooks" / "pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(REFUSING_PRE_COMMIT)
    hook.chmod(0o755)
    return hook


@pytest.mark.spec("RL-02-IT-02")
def test_RL_02_IT_02_a_refused_amend_by_hand_leaves_the_story_not_done(tmp_path):
    """Scenario: Only dispatch merge-story sets a story to done.

    A refused amend of the merge commit exits 1, names the hook, and keeps the
    entry from done; the rerun puts status: done into the merge commit."""
    run = _dispatched_by_hand(tmp_path, code="import os\n", rules=False)
    repo, ledger = run["repo"], run["ledger"]
    hook = _refuse_commits(repo)

    refused = _dispatch(repo, ledger, "merge-story", "ST-0350")

    assert refused.returncode == 1, refused.stdout + refused.stderr
    assert "the pre-commit hook refused" in refused.stderr
    assert _ledger(repo, "feature/login")["stories"]["ST-0350"]["status"] != "done"

    hook.unlink()
    rerun = _dispatch(repo, ledger, "merge-story", "ST-0350")

    assert rerun.returncode == 0, rerun.stdout + rerun.stderr
    merged = _git(repo, "show", "feature/login:backlog/ST-0350.md")
    assert "status: done" in merged.splitlines()
    assert _git(repo, "status", "--porcelain", "--", "backlog") == ""
    assert _ledger(repo, "feature/login")["stories"]["ST-0350"]["status"] == "done"


@pytest.mark.spec("RL-02-IT-02")
def test_RL_02_IT_02_a_refused_amend_in_an_orchestrated_run_leaves_the_story_not_done(
    factory_repo,
):
    """The orchestrated path shares the amend, so it refuses the same way."""
    repo, feature, ledger = (
        factory_repo["repo"], factory_repo["feature"], factory_repo["ledger"],
    )
    story = factory_repo["story"]
    (story / "src" / "ST-0350.txt").write_text("work\n")
    write_review_report(story, "ST-0350")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", "story work")
    sha = _git(story, "rev-parse", "HEAD")
    assert _dispatch(repo, ledger, "verify-story", "ST-0350", "--sha", sha).returncode == 0
    hook = _refuse_commits(repo)

    refused = _dispatch(feature, ledger, "merge-story", "ST-0350")

    assert refused.returncode == 1, refused.stdout + refused.stderr
    assert "the pre-commit hook refused" in refused.stderr
    assert yaml.safe_load(ledger.read_text())["stories"]["ST-0350"]["status"] != "done"

    hook.unlink()
    rerun = _dispatch(feature, ledger, "merge-story", "ST-0350")

    assert rerun.returncode == 0, rerun.stdout + rerun.stderr
    merged = _git(feature, "show", "feat/x:backlog/ST-0350.md")
    assert "status: done" in merged.splitlines()
    assert yaml.safe_load(ledger.read_text())["stories"]["ST-0350"]["status"] == "done"


# -- RL-06: User decides how a stopped story continues (ST-0419) --------------

AU = "acceptance_unmet"
CV = "contract_violation"
GATES_3_3 = 'test_command: "true"\ngates:\n  attempts: 3\n  attempts_escalated: 3\n'


def _orchestrated_on_login(
    tmp_path: Path, *, tier: str = "economy", testing: str = TESTING_YAML
) -> dict[str, Path]:
    """An orchestrated run on feature/login whose ST-0350 is dispatched in its
    own worktree; backlog/ST-0350.md reads status: open."""
    repo = tmp_path / "repo"
    for folder in ("backlog", "docs", "src"):
        (repo / folder).mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    (repo / "backlog" / "ST-0350.md").write_text(
        STORY.format(id="ST-0350").replace("tier: economy", f"tier: {tier}")
    )
    (repo / "docs" / "testing.yaml").write_text(testing)
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "src" / ".keep").write_text("")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    feature = repo / ".current-work" / "feature" / "login" / "inv"
    _git(repo, "worktree", "add", "-q", "-b", "feature/login", str(feature))
    ledger = _ledger_path(repo, "feature/login")
    for root in (repo, feature):
        _write_passing_dependency_results(root, "ST-0350")
    base = _git(repo, "rev-parse", "HEAD")
    for args in (
        ("init", "--base", base, "--stories", "ST-0350",
         "--feature-branch", "feature/login", "--yes"),
        ("plan", "--backlog-dir", "backlog"),
        ("prepare-wave", "1"),
        ("mark-dispatching", "ST-0350"),
        ("mark-dispatched", "ST-0350"),
    ):
        result = _dispatch(repo, ledger, *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)
    story = repo / ".current-work" / "feature" / "login" / "story" / "ST-0350"
    return {"repo": repo, "feature": feature, "story": story, "ledger": ledger}


def _commit_story_work(run: dict[str, Path], *extra: str) -> str:
    """Commit the work and the review of ST-0350, plus each file in *extra*."""
    story = run["story"]
    for name in ("src/ST-0350.txt", *extra):
        (story / name).write_text("work\n")
    write_review_report(story, "ST-0350")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", "feat: story work (ST-0350)")
    sha = _git(story, "rev-parse", "HEAD")
    result = _dispatch(run["repo"], run["ledger"], "verify-story", "ST-0350", "--sha", sha)
    assert result.returncode == 0, result.stdout + result.stderr
    return sha


def _commit_on_feature(run: dict[str, Path], name: str, text: str) -> str:
    (run["feature"] / name).write_text(text)
    _git(run["feature"], "add", name)
    _git(run["feature"], "commit", "-qm", f"chore: change {name}")
    return _git(run["feature"], "rev-parse", "HEAD")


def _fail(run: dict[str, Path], failure_class: str, times: int) -> subprocess.CompletedProcess:
    """Fail ST-0350 *times* times, with a re-dispatch before each retry."""
    repo, ledger = run["repo"], run["ledger"]
    result = None
    for attempt in range(times):
        if attempt:
            for step in ("re-dispatch", "mark-dispatching", "mark-dispatched"):
                done = _dispatch(repo, ledger, step, "ST-0350")
                assert done.returncode == 0, (step, done.stdout, done.stderr)
        result = _dispatch(repo, ledger, "mark-failed", "ST-0350", "--class", failure_class)
        assert result.returncode == 0, result.stdout + result.stderr
    return result


def _entry(run: dict[str, Path]) -> lib.StoryEntry:
    return lib.Ledger.load(run["ledger"]).stories["ST-0350"]


def _merge(run: dict[str, Path]) -> subprocess.CompletedProcess:
    return _dispatch(run["feature"], run["ledger"], "merge-story", "ST-0350")


def _last_attempt_on_strong(tmp_path: Path) -> dict[str, Path]:
    run = _orchestrated_on_login(tmp_path, tier="strong")
    out = _fail(run, AU, 3).stdout
    assert "ST-0350 has stopped as failed and waits for the User" in out, out
    assert _entry(run).tier == "strong"
    return run


def _second_contract_violation(tmp_path: Path) -> dict[str, Path]:
    run = _orchestrated_on_login(tmp_path)
    out = _fail(run, CV, 2).stdout
    assert "ST-0350 has stopped as failed and waits for the User" in out, out
    return run


def _merge_conflict(tmp_path: Path) -> dict[str, Path]:
    """git refuses the merge itself: the feature worktree holds an untracked
    file that the merge would overwrite. A content conflict shows up in the
    refresh first, because the refresh merges the feature branch in."""
    run = _orchestrated_on_login(tmp_path)
    _commit_story_work(run)
    (run["feature"] / "src" / "ST-0350.txt").write_text("not committed\n")
    assert _merge(run).returncode == 1
    return run


def _refresh_conflict(tmp_path: Path) -> dict[str, Path]:
    run = _orchestrated_on_login(tmp_path)
    _commit_story_work(run)
    _commit_on_feature(run, "src/ST-0350.txt", "other\n")
    assert _merge(run).returncode == 1
    return run


def _red_suite_after_the_merge(tmp_path: Path) -> dict[str, Path]:
    run = _orchestrated_on_login(tmp_path)
    _commit_story_work(run)
    run["commit_a"] = _commit_on_feature(run, "docs/testing.yaml", RED_ON_FEATURE)
    result = _merge(run)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "test suite failed after merging" in result.stderr
    return run


STOP_CAUSES = {
    "last-attempt-on-strong": (_last_attempt_on_strong, "failed", None),
    "second-contract-violation": (_second_contract_violation, "failed", None),
    "merge-conflict": (_merge_conflict, "blocked", "merge conflict"),
    "refresh-conflict": (_refresh_conflict, "blocked", "refresh conflict"),
    "red-suite-after-the-merge": (
        _red_suite_after_the_merge, "blocked", "post-merge test failure"
    ),
}


@pytest.mark.spec("RL-06-IT-01")
@pytest.mark.parametrize("cause", list(STOP_CAUSES))
def test_RL_06_IT_01_a_story_stops_in_the_state_that_names_its_cause(tmp_path, cause):
    """Scenario Outline: A story stops in the state that names its cause."""
    build, state, reason = STOP_CAUSES[cause]

    run = build(tmp_path)

    entry = _entry(run)
    assert entry.status.value == state
    if reason is not None:
        assert entry.reason == reason
    assert entry.feature_branch == "feature/login"
    assert lib.has_stopped(entry, lib.AttemptLimits())


@pytest.mark.spec("RL-06-IT-02")
def test_RL_06_IT_02_a_red_suite_moves_the_feature_branch_back(tmp_path):
    """Scenario: A red test suite after a merge moves the feature branch back.

    The orchestrated run merges in the worktree of the feature branch."""
    run = _red_suite_after_the_merge(tmp_path)

    commit_a = run["commit_a"]
    assert _git(run["repo"], "rev-parse", "feature/login") == commit_a
    assert _git(run["repo"], "rev-list", f"{commit_a}..feature/login") == ""
    subjects = _git(run["repo"], "log", "--format=%s", "feature/login").splitlines()
    assert not [s for s in subjects if s.startswith("Revert")]
    entry = _entry(run)
    assert (entry.status.value, entry.reason) == ("blocked", "post-merge test failure")


@pytest.mark.spec("RL-06-IT-03")
def test_RL_06_IT_03_a_fixed_cause_lets_the_story_continue_in_the_same_run(tmp_path):
    """Scenario: A fixed cause lets the story continue in the same run."""
    run = _merge_conflict(tmp_path)
    repo, ledger = run["repo"], run["ledger"]
    before = _entry(run)
    assert (before.status.value, before.reason) == ("blocked", "merge conflict")
    tip = _git(repo, "rev-parse", "story/ST-0350")
    (run["feature"] / "src" / "ST-0350.txt").unlink()

    result = _dispatch(repo, ledger, "re-dispatch", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    entry = _entry(run)
    assert entry.status.value == "prepared"
    assert (entry.branch, entry.worktree) == (before.branch, before.worktree)
    assert entry.feature_branch == "feature/login"
    assert _git(run["story"], "branch", "--show-current") == "story/ST-0350"
    assert _git(repo, "rev-parse", "story/ST-0350") == tip
    for step in ("mark-dispatching", "mark-dispatched"):
        assert _dispatch(repo, ledger, step, "ST-0350").returncode == 0
    merged = _merge(run)
    assert merged.returncode == 0, merged.stdout + merged.stderr
    assert _entry(run).status.value == "done"
    assert _git(repo, "rev-parse", "feature/login^2") == tip


@pytest.mark.spec("RL-06-IT-04")
@pytest.mark.parametrize("state", ["failed", "blocked"])
def test_RL_06_IT_04_return_story_sets_a_stopped_story_back_to_pending(tmp_path, state):
    """Scenario Outline: return-story sets a stopped story back to pending."""
    run = _orchestrated_on_login(tmp_path)
    repo, ledger = run["repo"], run["ledger"]
    if state == "failed":
        _fail(run, AU, 1)
    else:
        assert _dispatch(
            repo, ledger, "mark-blocked", "ST-0350", "--reason", "merge conflict"
        ).returncode == 0
    assert _entry(run).status.value == state

    result = _dispatch(repo, ledger, "return-story", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    entry = _ledger(repo, "feature/login")["stories"]["ST-0350"]
    assert (entry["status"], entry["returned"]) == ("pending", True)
    front = (repo / "backlog" / "ST-0350.md").read_text().split("---")[1]
    assert yaml.safe_load(front)["status"] == "pending"
    status = _dispatch(repo, ledger, "status")
    assert re.search(r"ST-0350\s+1\s+pending", status.stdout), status.stdout


@pytest.mark.spec("RL-06-IT-04")
def test_RL_06_IT_04_return_story_refuses_a_dispatched_story(tmp_path):
    """return-story refuses a story that has not stopped and changes no file."""
    run = _orchestrated_on_login(tmp_path)
    repo, ledger = run["repo"], run["ledger"]
    story_file = (repo / "backlog" / "ST-0350.md").read_text()
    ledger_text = ledger.read_text()

    result = _dispatch(repo, ledger, "return-story", "ST-0350")

    assert result.returncode == 1
    assert "ST-0350 is dispatched" in result.stderr
    assert (repo / "backlog" / "ST-0350.md").read_text() == story_file
    assert ledger.read_text() == ledger_text


def _three_failed_attempts_on_standard(tmp_path: Path, *extra: str) -> dict[str, Path]:
    run = _orchestrated_on_login(tmp_path, tier="standard", testing=GATES_3_3)
    _commit_story_work(run, *extra)
    out = _fail(run, AU, 3).stdout
    assert "run `dispatch escalate ST-0350`" in out, out
    return run


@pytest.mark.spec("RL-06-IT-05")
def test_RL_06_IT_05_a_diff_outside_the_scope_stops_the_story(tmp_path):
    """Scenario: A story whose diff leaves its scope stops when dispatch
    escalate refuses it. Once the User moves the diff back inside the scope,
    escalate grants and clears the record."""
    run = _three_failed_attempts_on_standard(tmp_path, "README.md")
    repo, ledger = run["repo"], run["ledger"]

    refused = _dispatch(repo, ledger, "escalate", "ST-0350")

    assert refused.returncode != 0
    entry = _entry(run)
    assert (entry.status.value, entry.tier) == ("failed", "standard")
    assert entry.reason == "escalate refused: scope"
    assert lib.has_stopped(entry, lib.AttemptLimits())
    assert "waits for the User" in refused.stderr

    _git(run["story"], "rm", "-q", "README.md")
    _git(run["story"], "commit", "-qm", "fix: keep the diff inside the scope (ST-0350)")
    granted = _dispatch(repo, ledger, "escalate", "ST-0350")

    assert granted.returncode == 0, granted.stdout + granted.stderr
    entry = _entry(run)
    assert (entry.tier, entry.reason) == ("strong", None)
    assert not lib.has_stopped(entry, lib.AttemptLimits())


@pytest.mark.spec("RL-06-IT-05")
def test_RL_06_IT_05_a_failing_verify_base_stops_the_story(tmp_path):
    """The same refusal with a failing verify-base writes its own record."""
    run = _three_failed_attempts_on_standard(tmp_path)
    _git(run["story"], "checkout", "-q", "--detach", "HEAD~1")

    refused = _dispatch(run["repo"], run["ledger"], "escalate", "ST-0350")

    assert refused.returncode != 0
    entry = _entry(run)
    assert (entry.status.value, entry.tier) == ("failed", "standard")
    assert entry.reason == "escalate refused: verify-base"
    assert lib.has_stopped(entry, lib.AttemptLimits())


@pytest.mark.spec("RL-06-IT-05")
@pytest.mark.parametrize("case", ["strong", "escalated", "escalation-off"])
def test_RL_06_IT_05_a_refusal_of_the_ledger_writes_no_record(tmp_path, case):
    """A refusal for the tier, an earlier escalation or
    gates.attempts_escalated: 0 writes no record, because the ledger shows it."""
    testing = GATES_3_3.replace("attempts_escalated: 3", "attempts_escalated: 0")
    run = _orchestrated_on_login(
        tmp_path,
        tier="strong" if case == "strong" else "standard",
        testing=testing if case == "escalation-off" else GATES_3_3,
    )
    _commit_story_work(run, "README.md")
    if case == "escalated":
        data = _ledger(run["repo"], "feature/login")
        data["stories"]["ST-0350"]["escalation_granted"] = True
        run["ledger"].write_text(yaml.safe_dump(data, sort_keys=False))
    _fail(run, AU, 3)

    refused = _dispatch(run["repo"], run["ledger"], "escalate", "ST-0350")

    assert refused.returncode != 0
    entry = _entry(run)
    assert entry.status.value == "failed"
    assert entry.reason is None
    assert lib.has_stopped(entry, lib.AttemptLimits(attempts_escalated=0)
                           if case == "escalation-off" else lib.AttemptLimits())


# -- RL-08: merge-story in an orchestrated run refuses before a new merge (ST-0416)

NO_DIRTY_REFUSAL = 'test_command: "true"\ndispatch:\n  refuse_dirty_feature_worktree: false\n'


def _failing_gate_on_feature(run: dict[str, Path]) -> None:
    """Commit dependency rules and a breaking import to the feature branch, so
    the dependency-check gate of premerge-check fails on the story branch."""
    feature = run["feature"]
    (feature / "docs" / "spec").mkdir(parents=True, exist_ok=True)
    (feature / RULES).write_text("src must_not_depend_on infra\n")
    (feature / "src" / "uses_infra.py").write_text("import infra\n")
    _git(feature, "add", RULES, "src/uses_infra.py")
    _git(feature, "commit", "-qm", "chore: add a breaking import")


@pytest.mark.spec("RL-08-IT-15")
def test_RL_08_IT_15_a_refused_premerge_check_merges_nothing(tmp_path):
    """Scenario: A refused premerge-check sends a story in an orchestrated run
    back to the gate-check step."""
    run = _orchestrated_on_login(tmp_path)
    _failing_gate_on_feature(run)
    _commit_story_work(run)
    tip = _git(run["repo"], "rev-parse", "feature/login")

    result = _merge(run)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "BLOCK semantic-gates: dependency-check" in result.stdout
    assert "premerge-check failed for story/ST-0350" in result.stderr
    assert _git(run["repo"], "rev-parse", "feature/login") == tip
    assert _entry(run).status.value == "dispatched"


@pytest.mark.spec("RL-08-IT-15")
def test_RL_08_IT_15_a_changed_tracked_file_does_not_hide_a_failing_gate(tmp_path):
    """BR-124: merge-story checks the feature worktree only after premerge-check
    exits 0, so the message names the gate and not the changed file."""
    run = _orchestrated_on_login(tmp_path)
    _failing_gate_on_feature(run)
    _commit_story_work(run)
    (run["feature"] / "src" / ".keep").write_text("my uncommitted work\n")

    result = _merge(run)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "BLOCK semantic-gates: dependency-check" in result.stdout
    assert "uncommitted" not in result.stderr
    assert _entry(run).status.value == "dispatched"


@pytest.mark.spec("RL-08-IT-16")
def test_RL_08_IT_16_a_changed_tracked_file_in_the_feature_worktree_stops_the_merge(
    tmp_path,
):
    """Scenario: An uncommitted change in the worktree of the feature branch
    stops merge-story in an orchestrated run."""
    run = _orchestrated_on_login(tmp_path)
    _commit_story_work(run)
    tip = _git(run["repo"], "rev-parse", "feature/login")
    changed = run["feature"] / "src" / ".keep"
    changed.write_text("my uncommitted work\n")

    result = _merge(run)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "PASS" in result.stdout
    assert "src/.keep" in result.stderr
    assert str(run["feature"]) in result.stderr
    # IMPL-0039: the message names the docs/testing.yaml that merge-story reads.
    assert f"false in {run['feature'] / 'docs' / 'testing.yaml'}:" in result.stderr
    assert changed.read_text() == "my uncommitted work\n"
    assert _git(run["repo"], "rev-parse", "feature/login") == tip
    assert _entry(run).status.value == "dispatched"


@pytest.mark.spec("RL-08-IT-16")
def test_RL_08_IT_16_a_staged_change_in_the_feature_worktree_stops_the_merge(tmp_path):
    """A staged change counts as an uncommitted change too."""
    run = _orchestrated_on_login(tmp_path)
    _commit_story_work(run)
    (run["feature"] / "src" / ".keep").write_text("staged work\n")
    _git(run["feature"], "add", "src/.keep")

    result = _merge(run)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "src/.keep" in result.stderr
    assert _entry(run).status.value == "dispatched"


@pytest.mark.spec("RL-08-IT-16")
def test_RL_08_IT_16_an_untracked_file_in_the_feature_worktree_does_not_stop_the_merge(
    tmp_path,
):
    """BR-124 names tracked files only; an untracked file the merge does not
    touch leaves the merge open."""
    run = _orchestrated_on_login(tmp_path)
    _commit_story_work(run)
    (run["feature"] / "src" / "notes.txt").write_text("scratch\n")

    result = _merge(run)

    assert result.returncode == 0, result.stdout + result.stderr
    assert _entry(run).status.value == "done"


@pytest.mark.spec("RL-08-IT-16")
def test_RL_08_IT_16_the_key_false_merges_past_a_changed_tracked_file(tmp_path):
    """Scenario: merge-story merges past an uncommitted change when
    dispatch.refuse_dirty_feature_worktree is false."""
    run = _orchestrated_on_login(tmp_path, testing=NO_DIRTY_REFUSAL)
    story_tip = _commit_story_work(run)
    changed = run["feature"] / "src" / ".keep"
    changed.write_text("my uncommitted work\n")

    result = _merge(run)

    assert result.returncode == 0, result.stdout + result.stderr
    assert _git(run["repo"], "rev-parse", "feature/login^2") == story_tip
    assert _entry(run).status.value == "done"
    assert changed.read_text() == "my uncommitted work\n"


@pytest.mark.spec("RL-08-IT-16")
def test_RL_08_IT_16_the_rerun_after_a_refused_amend_passes(tmp_path):
    """BR-124, BR-118, SPEC-0110: the refusal applies only before a new merge.

    The refused amend leaves backlog/ST-0350.md changed in the feature
    worktree; the rerun finds the merge commit at HEAD and passes."""
    run = _orchestrated_on_login(tmp_path)
    _commit_story_work(run)
    hook = _refuse_commits(run["repo"])

    refused = _merge(run)

    assert refused.returncode == 1, refused.stdout + refused.stderr
    assert "the pre-commit hook refused" in refused.stderr
    leftover = _git(run["feature"], "status", "--porcelain", "--untracked-files=no")
    assert "backlog/ST-0350.md" in leftover

    hook.unlink()
    rerun = _merge(run)

    assert rerun.returncode == 0, rerun.stdout + rerun.stderr
    merged = _git(run["feature"], "show", "feature/login:backlog/ST-0350.md")
    assert "status: done" in merged.splitlines()
    assert _entry(run).status.value == "done"


@pytest.mark.spec("RL-08-IT-16")
def test_RL_08_IT_16_a_key_that_is_no_bool_stops_the_merge(tmp_path):
    """The key is a bool (interface-contracts.md, dispatch section schema); any
    other value stops the merge and names the file."""
    run = _orchestrated_on_login(
        tmp_path,
        testing='test_command: "true"\ndispatch:\n  refuse_dirty_feature_worktree: "off"\n',
    )
    _commit_story_work(run)

    result = _merge(run)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "dispatch.refuse_dirty_feature_worktree must be true or false" in result.stderr
    assert "docs/testing.yaml" in result.stderr
    assert _entry(run).status.value == "dispatched"


# -- RL-12: a blocking finding of the feature checks runs as a unit of work (ST-0422)

BUG = "BUG-0090"
FEATURE_FINDING = """---
id: {id}
source: qa-agent
review_class: code
category: defect
type: function
severity: {severity}
artifact: src/ST-0350.txt:1
status: {status}
owner: developer-agent
story:
run: feature/login
---

# {id}
"""


def _commit_feature_finding(
    run: dict[str, Path], finding_id: str = BUG, *, severity: str = "major",
    status: str = "open",
) -> None:
    (run["feature"] / "docs" / "findings").mkdir(parents=True, exist_ok=True)
    _commit_on_feature(
        run, f"docs/findings/{finding_id}.md",
        FEATURE_FINDING.format(id=finding_id, severity=severity, status=status),
    )


def _wave_one_merged(tmp_path: Path, *, testing: str = TESTING_YAML) -> dict[str, Path]:
    """The run on feature/login after ST-0350 merged and wave 1 closed. The
    feature checks committed BUG-0090, open and blocking, on feature/login."""
    run = _orchestrated_on_login(tmp_path, testing=testing)
    _commit_feature_finding(run)
    _commit_story_work(run)
    merged = _merge(run)
    assert merged.returncode == 0, merged.stdout + merged.stderr
    closed = _dispatch(run["repo"], run["ledger"], "close-wave", "1")
    assert closed.returncode == 0, closed.stdout + closed.stderr
    run["finding_story"] = (
        run["repo"] / ".current-work" / "feature" / "login" / "story" / BUG
    )
    return run


def _unit(run: dict[str, Path], unit_id: str = BUG) -> lib.StoryEntry:
    return lib.Ledger.load(run["ledger"]).stories[unit_id]


def _steps(run: dict[str, Path], *steps: tuple[str, ...]) -> None:
    for args in steps:
        result = _dispatch(run["repo"], run["ledger"], *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)


def _dispatched_finding(tmp_path: Path, *, testing: str = TESTING_YAML) -> dict[str, Path]:
    """BUG-0090 added in wave 2 and dispatched on story/BUG-0090."""
    run = _wave_one_merged(tmp_path, testing=testing)
    _steps(
        run, ("add", BUG), ("prepare-wave", "2"),
        ("mark-dispatching", BUG), ("mark-dispatched", BUG),
    )
    return run


def _commit_finding_fix(run: dict[str, Path], *names: str) -> str:
    """Commit each file of *names* and the review of BUG-0090 on its branch."""
    story = run["finding_story"]
    for name in names:
        (story / name).parent.mkdir(parents=True, exist_ok=True)
        (story / name).write_text("fix\n")
    write_review_report(story, BUG)
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", f"fix: {BUG}")
    sha = _git(story, "rev-parse", "HEAD")
    _steps(run, ("verify-story", BUG, "--sha", sha))
    return sha


def _merge_finding(run: dict[str, Path]) -> subprocess.CompletedProcess:
    return _dispatch(run["feature"], run["ledger"], "merge-story", BUG)


def _finding_front(text: str) -> dict:
    return yaml.safe_load(text.split("---")[1])


@pytest.mark.spec("RL-12-IT-01")
def test_RL_12_IT_01_dispatch_add_puts_an_open_finding_into_a_new_wave(tmp_path):
    """Scenario: dispatch add puts an open finding into a new wave."""
    run = _wave_one_merged(tmp_path)
    repo, ledger = run["repo"], run["ledger"]

    result = _dispatch(repo, ledger, "add", BUG)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "BUG-0090 is pending in wave 2 of feature/login" in result.stdout
    entry = _unit(run)
    assert (entry.status.value, entry.wave, entry.deps, entry.tier) == ("pending", 2, [], None)
    assert lib.Ledger.load(ledger).feature_branch == "feature/login"
    status = _dispatch(repo, ledger, "status")
    assert re.search(r"BUG-0090\s+2\s+pending", status.stdout), status.stdout

    _steps(run, ("prepare-wave", "2"))

    entry = _unit(run)
    assert (entry.branch, entry.active_tier) == ("story/BUG-0090", "economy")
    assert _git(run["finding_story"], "branch", "--show-current") == "story/BUG-0090"
    assert not (repo / "backlog" / f"{BUG}.md").exists()


@pytest.mark.spec("RL-12-IT-02")
def test_RL_12_IT_02_the_merge_of_a_finding_sets_it_resolved(tmp_path):
    """Scenario: The merge of a finding sets it resolved."""
    run = _dispatched_finding(tmp_path)
    _commit_finding_fix(run, "src/fix.txt", "tests/test_fix.txt")

    result = _merge_finding(run)

    assert result.returncode == 0, result.stdout + result.stderr
    merged = _git(run["feature"], "show", f"HEAD:docs/findings/{BUG}.md")
    assert _finding_front(merged)["status"] == "resolved"
    assert _git(run["feature"], "log", "-1", "--format=%s") == (
        "merge: story/BUG-0090 into feature/login"
    )
    assert _unit(run).status.value == "done"
    assert _git(run["feature"], "status", "--porcelain") == ""


@pytest.mark.spec("RL-12-IT-02")
def test_RL_12_IT_02_a_refused_amend_leaves_the_finding_dispatched(tmp_path):
    """A hook that refuses the amend stops merge-story, names the hook, and
    leaves the entry dispatched; the rerun writes status: resolved (BR-118)."""
    run = _dispatched_finding(tmp_path)
    _commit_finding_fix(run, "src/fix.txt")
    hook = _refuse_commits(run["repo"])

    refused = _merge_finding(run)

    assert refused.returncode == 1, refused.stdout + refused.stderr
    assert "the pre-commit hook refused the amend that writes status: resolved" in refused.stderr
    assert _unit(run).status.value == "dispatched"
    hook.unlink()
    rerun = _merge_finding(run)
    assert rerun.returncode == 0, rerun.stdout + rerun.stderr
    merged = _git(run["feature"], "show", f"HEAD:docs/findings/{BUG}.md")
    assert _finding_front(merged)["status"] == "resolved"
    assert _unit(run).status.value == "done"


def _returned_finding(tmp_path: Path) -> dict[str, Path]:
    """BUG-0090 returned after a failed attempt that committed src/fix.txt."""
    run = _dispatched_finding(tmp_path)
    run["attempt_one"] = _commit_finding_fix(run, "src/fix.txt")
    _steps(run, ("mark-failed", BUG, "--class", AU), ("return-story", BUG))
    return run


@pytest.mark.spec("RL-12-IT-03")
def test_RL_12_IT_03_returning_a_finding_changes_only_its_ledger_entry(tmp_path):
    """Scenario: Returning a finding changes only its ledger entry."""
    run = _dispatched_finding(tmp_path)
    repo, ledger = run["repo"], run["ledger"]
    _steps(run, ("mark-failed", BUG, "--class", AU))
    decoy = repo / "backlog" / f"{BUG}.md"
    decoy.write_text("---\nstatus: open\n---\n")
    tracked = _git(run["feature"], "status", "--porcelain")
    finding_before = (run["feature"] / "docs" / "findings" / f"{BUG}.md").read_text()

    result = _dispatch(repo, ledger, "return-story", BUG)

    assert result.returncode == 0, result.stdout + result.stderr
    entry = _ledger(repo, "feature/login")["stories"][BUG]
    assert (entry["status"], entry["returned"]) == ("pending", True)
    assert decoy.read_text() == "---\nstatus: open\n---\n"
    finding = (run["feature"] / "docs" / "findings" / f"{BUG}.md").read_text()
    assert finding == finding_before
    front = _finding_front(_git(repo, "show", f"feature/login:docs/findings/{BUG}.md"))
    assert (front["status"], front["run"]) == ("open", "feature/login")
    assert _git(run["feature"], "status", "--porcelain") == tracked
    feature_merge = subprocess.run(
        [str(SOURCE_SCRIPTS_DIR / "premerge-check"), "dev", "feature/login"],
        cwd=repo, env=_env(), capture_output=True, text=True, check=False,
    )
    assert feature_merge.returncode != 0, feature_merge.stdout
    assert BUG in feature_merge.stdout


@pytest.mark.spec("RL-12-IT-04")
def test_RL_12_IT_04_adding_a_returned_finding_again_reuses_its_entry(tmp_path):
    """Scenario: Adding a returned finding again reuses its entry."""
    run = _returned_finding(tmp_path)
    repo, ledger = run["repo"], run["ledger"]
    before = _unit(run)
    assert (before.returned, len(before.attempts)) == (True, 1)
    tip = _git(repo, "rev-parse", "story/BUG-0090")
    _steps(run, ("close-wave", "2"))

    result = _dispatch(repo, ledger, "add", BUG)

    assert result.returncode == 0, result.stdout + result.stderr
    entry = _unit(run)
    assert (entry.status.value, entry.wave, entry.returned) == ("pending", 3, False)
    assert (entry.attempts, entry.attempt_grants, entry.tier) == ([], [], None)
    assert not entry.escalation_granted
    assert lib.counted_tier(entry) == "economy"
    assert lib.counted_attempts_on_tier(entry, "economy") == 0
    assert (entry.branch, entry.worktree) == (before.branch, before.worktree)
    assert _git(repo, "rev-parse", "story/BUG-0090") == tip
    assert list(lib.Ledger.load(ledger).stories) == ["ST-0350", BUG]

    # IMPL-0056: the next attempt starts on the existing branch, brought up
    # to the feature branch by a merge, in the registered worktree.
    feature_tip = _commit_on_feature(run, "docs/notes.md", "moved on\n")
    prepared = _dispatch(repo, ledger, "prepare-wave", "3")

    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    entry = _unit(run)
    assert entry.status.value == "prepared"
    assert (entry.branch, entry.worktree) == (before.branch, before.worktree)
    assert entry.base_sha == feature_tip
    story = run["finding_story"]
    assert _git(story, "branch", "--show-current") == "story/BUG-0090"
    for commit in (run["attempt_one"], feature_tip):
        _git(repo, "merge-base", "--is-ancestor", commit, "story/BUG-0090")
    assert _git(repo, "rev-parse", "story/BUG-0090^1") == tip
    assert (story / "src" / "fix.txt").read_text() == "fix\n"
    for step in ("mark-dispatching", "mark-dispatched"):
        assert _dispatch(repo, ledger, step, BUG).returncode == 0


@pytest.mark.spec("RL-12-IT-04")
def test_RL_12_IT_04_a_conflicting_refresh_blocks_the_reused_finding(tmp_path):
    """IMPL-0056: when the merge of the feature branch into the existing
    branch conflicts, prepare-wave aborts it and blocks the entry, as
    refresh-story does; the branch keeps its commits."""
    run = _returned_finding(tmp_path)
    repo, ledger = run["repo"], run["ledger"]
    tip = _git(repo, "rev-parse", "story/BUG-0090")
    _steps(run, ("close-wave", "2"), ("add", BUG))
    (run["feature"] / "src" / "fix.txt").write_text("other\n")
    _git(run["feature"], "add", "src/fix.txt")
    _git(run["feature"], "commit", "-qm", "chore: conflict")

    result = _dispatch(repo, ledger, "prepare-wave", "3")

    assert result.returncode == 1, result.stdout + result.stderr
    entry = _unit(run)
    assert (entry.status.value, entry.reason) == ("blocked", "refresh conflict")
    assert _git(repo, "rev-parse", "story/BUG-0090") == tip
    assert _git(run["finding_story"], "status", "--porcelain") == ""


@pytest.mark.spec("RL-12-IT-04")
def test_RL_12_IT_04_by_hand_the_next_attempt_runs_on_the_existing_branch(run_repo):
    """IMPL-0056 by hand: prepare-story checks out the existing branch in the
    primary checkout and merges the feature branch into it."""
    repo = run_repo
    ledger = _by_hand_run(repo, "ST-0350")
    _git(repo, "checkout", "-q", "feature/login")
    (repo / "docs" / "findings").mkdir(parents=True)
    (repo / "docs" / "findings" / f"{BUG}.md").write_text(
        FEATURE_FINDING.format(id=BUG, severity="major", status="open")
    )
    _git(repo, "add", "docs/findings")
    _git(repo, "commit", "-qm", "docs: file BUG-0090")
    _git(repo, "checkout", "-q", "dev")
    _close_wave_one(repo, ledger, record=True)
    run = {"repo": repo, "ledger": ledger}
    _steps(run, ("add", BUG), ("prepare-story", BUG), ("mark-dispatching", BUG))
    (repo / "src" / "fix.txt").write_text("fix\n")
    _git(repo, "add", "src/fix.txt")
    _git(repo, "commit", "-qm", "fix: attempt one (BUG-0090)")
    attempt_one = _git(repo, "rev-parse", "HEAD")
    _steps(run, ("mark-dispatched", BUG), ("mark-failed", BUG, "--class", AU),
           ("return-story", BUG))
    _git(repo, "checkout", "-q", "feature/login")
    (repo / "docs" / "notes.md").write_text("moved on\n")
    _git(repo, "add", "docs/notes.md")
    _git(repo, "commit", "-qm", "chore: move on")
    feature_tip = _git(repo, "rev-parse", "HEAD")
    data = yaml.safe_load(ledger.read_text())
    data["waves"].append({**data["waves"][0], "number": 2})
    ledger.write_text(yaml.safe_dump(data, sort_keys=False))
    _steps(run, ("add", BUG))

    result = _dispatch(repo, ledger, "prepare-story", BUG)

    assert result.returncode == 0, result.stdout + result.stderr
    assert _git(repo, "branch", "--show-current") == "story/BUG-0090"
    assert _git(repo, "rev-parse", "HEAD^1") == attempt_one
    _git(repo, "merge-base", "--is-ancestor", feature_tip, "HEAD")
    entry = _ledger(repo, "feature/login")["stories"][BUG]
    assert (entry["status"], entry["wave"], entry["base_sha"]) == ("prepared", 3, feature_tip)


@pytest.mark.spec("RL-06-IT-05")
@pytest.mark.parametrize(("files", "granted"), [(1, True), (21, False)])
def test_RL_06_IT_05_escalate_of_a_finding_checks_only_the_file_limit(
    tmp_path, files, granted
):
    """IMPL-0033: a finding declares no file scope, so escalate refuses its
    diff only beyond the file limit that merge-story passes."""
    run = _dispatched_finding(tmp_path, testing=GATES_3_3)
    _commit_finding_fix(run, "README.md", *(f"src/fix{n:02}.txt" for n in range(files)))
    for attempt in range(3):
        if attempt:
            _steps(run, ("re-dispatch", BUG), ("mark-dispatching", BUG),
                   ("mark-dispatched", BUG))
        _steps(run, ("mark-failed", BUG, "--class", AU))

    result = _dispatch(run["repo"], run["ledger"], "escalate", BUG)

    entry = _unit(run)
    if granted:
        assert result.returncode == 0, result.stdout + result.stderr
        assert (entry.tier, entry.reason) == ("standard", None)
    else:
        assert result.returncode == 1, result.stdout + result.stderr
        assert (entry.tier, entry.reason) == (None, "escalate refused: scope")


# -- ST-0431: the run goes on after a finding is added -------------------------

RE_DISPATCH_REFUSES = ["pending", "prepared", "dispatching", "dispatched", "done"]


def _unit_in_state(tmp_path: Path, state: str) -> tuple[dict[str, Path], str]:
    """Return the run and the ID of its unit of work in *state*: ST-0350 is
    done after wave 1, and BUG-0090 takes each state before it."""
    run = _wave_one_merged(tmp_path)
    if state == "done":
        return run, "ST-0350"
    steps = [("add", BUG), ("prepare-wave", "2"),
             ("mark-dispatching", BUG), ("mark-dispatched", BUG)]
    _steps(run, *steps[: RE_DISPATCH_REFUSES.index(state) + 1])
    assert _unit(run).status.value == state
    return run, BUG


@pytest.mark.spec("RL-06-IT-03")
@pytest.mark.parametrize("state", RE_DISPATCH_REFUSES)
def test_RL_06_IT_03_re_dispatch_refuses_a_unit_of_work_that_has_not_stopped(
    tmp_path, state
):
    """ST-0431: re-dispatch continues only a failed or blocked unit of work
    on its branch (BR-116); every other state is refused, and the ledger
    stays as it was."""
    run, unit_id = _unit_in_state(tmp_path, state)
    before = run["ledger"].read_bytes()

    result = _dispatch(run["repo"], run["ledger"], "re-dispatch", unit_id)

    assert result.returncode != 0
    assert f"{unit_id} is {state}" in result.stderr
    assert "re-dispatch accepts only failed and blocked" in result.stderr
    assert run["ledger"].read_bytes() == before
    if state == "pending":
        assert (_unit(run).branch, _unit(run).worktree) == (None, None)


@pytest.mark.spec("RL-12-IT-01")
def test_RL_12_IT_01_prepare_wave_cuts_the_branch_from_the_tip_of_the_feature_branch(
    tmp_path,
):
    """ST-0431: a commit on the feature branch after the wave record, such as
    a filed finding, is the base of the next story branch, and verify-base
    passes on it. branch_head keeps the wave record's commit."""
    run = _wave_one_merged(tmp_path)
    repo, ledger = run["repo"], run["ledger"]
    recorded = lib.Ledger.load(ledger).branch_head
    tip = _commit_on_feature(run, "docs/notes.md", "filed after the wave record\n")
    assert tip != recorded
    _steps(run, ("add", BUG))

    result = _dispatch(repo, ledger, "prepare-wave", "2")

    assert result.returncode == 0, result.stdout + result.stderr
    assert _unit(run).base_sha == tip
    assert _git(repo, "rev-parse", "story/BUG-0090") == tip
    assert lib.Ledger.load(ledger).branch_head == recorded
    verify = subprocess.run(
        [str(SOURCE_SCRIPTS_DIR / "verify-base"), "feature/login", "--expect-base", tip],
        cwd=run["finding_story"], env=_env(), capture_output=True, text=True, check=False,
    )
    assert verify.returncode == 0, verify.stdout + verify.stderr
    assert "BASE_OK" in verify.stdout


@pytest.mark.spec("RL-11-CT-01")
def test_RL_11_CT_01_close_wave_records_a_wave_whose_only_entry_add_moved(tmp_path):
    """ST-0431: add moves the returned BUG-0090 out of wave 2 before its close.
    close-wave 2 records the empty wave, and prepare-wave 3 finds the record."""
    run = _returned_finding(tmp_path)
    repo, ledger = run["repo"], run["ledger"]
    _steps(run, ("add", BUG))
    assert _unit(run).wave == 3

    result = _dispatch(repo, ledger, "close-wave", "2")

    assert result.returncode == 0, result.stdout + result.stderr
    record = next(r for r in lib.Ledger.load(ledger).waves if r.number == 2)
    assert (record.completed, record.blocked, record.failed) == ([], [], [])
    prepared = _dispatch(repo, ledger, "prepare-wave", "3")
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    assert _unit(run).status.value == "prepared"


# -- RL-12: a filed surviving mutant runs in the next wave (ST-0423) ----------

MUTATION_GATE = (
    'test_command: "true"\n'
    "gates:\n  mutation-testing:\n    enabled: true\n    command: \"exit 1\"\n"
)
QA = "QA-0012"
QA_FINDING = """---
id: {id}
source: mutation-testing
review_class: code
category: defect
type: test
severity: major
artifact: src/login.py:42
status: open
owner: planning-agent
story:
run: feature/login
---

# {id}
"""


def _store_mutants(run: dict[str, Path], *mutants: dict) -> None:
    """Write the result of the gate-check step where merge-story reads it."""
    folder = run["feature"] / ".current-work" / "mutation-testing"
    folder.mkdir(parents=True, exist_ok=True)
    result = {
        "story_id": "ST-0350", "passed": False, "command": "exit 1",
        "timeout_seconds": 1800, "exit_code": 1, "timed_out": False,
        "message": "the mutation command exited 1", "mutants": list(mutants),
    }
    (folder / "ST-0350.json").write_text(json.dumps(result))


def _filed(finding_id: str = QA) -> dict:
    return {
        "operator": "+ -> -", "location": "src/login.py:42", "status": "survived",
        "resolution_action": "file-qa-finding", "finding": finding_id,
    }


def _story_with_findings(tmp_path: Path, *finding_ids: str) -> dict[str, Path]:
    """ST-0350 dispatched with the mutation gate on; its branch commits each
    finding of *finding_ids* with run feature/login."""
    run = _orchestrated_on_login(tmp_path, testing=MUTATION_GATE)
    for finding_id in finding_ids:
        path = run["story"] / "docs" / "findings" / f"{finding_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(QA_FINDING.format(id=finding_id))
    _commit_story_work(run)
    return run


@pytest.mark.spec("RL-12-IT-06")
def test_RL_12_IT_06_a_story_merges_with_its_mutant_filed_and_the_finding_runs_next(tmp_path):
    """Scenario: A story merges with its mutant filed, and the QA finding runs
    in the next wave on the story's code."""
    run = _story_with_findings(tmp_path, QA)
    repo, feature, ledger = run["repo"], run["feature"], run["ledger"]
    _store_mutants(run, _filed())

    merged = _merge(run)

    assert merged.returncode == 0, merged.stdout + merged.stderr
    assert "PASS out-of-scope-paths" in merged.stdout
    assert "PASS semantic-gates: mutation-testing passed for ST-0350" in merged.stdout
    merge_commit = _git(feature, "rev-parse", "HEAD")
    assert (_entry(run).status.value, _entry(run).wave) == ("done", 1)
    _steps(run, ("close-wave", "1"), ("add", QA))
    status = _dispatch(repo, ledger, "status")
    assert re.search(rf"{QA}\s+2\s+pending", status.stdout), status.stdout
    front = _finding_front(_git(repo, "show", f"feature/login:docs/findings/{QA}.md"))
    assert (front["status"], front["run"]) == ("open", "feature/login")

    _steps(run, ("prepare-wave", "2"))

    finding_story = repo / ".current-work" / "feature" / "login" / "story" / QA
    assert _git(finding_story, "branch", "--show-current") == f"story/{QA}"
    _git(finding_story, "merge-base", "--is-ancestor", merge_commit, "HEAD")
    assert (finding_story / "src" / "ST-0350.txt").read_text() == "work\n"
    feature_merge = subprocess.run(
        [str(SOURCE_SCRIPTS_DIR / "premerge-check"), "dev", "feature/login"],
        cwd=repo, env=_env(), capture_output=True, text=True, check=False,
    )
    assert feature_merge.returncode != 0, feature_merge.stdout
    assert QA in feature_merge.stdout


@pytest.mark.spec("RL-12-IT-06")
def test_RL_12_IT_06_a_finding_that_no_entry_names_stays_outside_the_scope(tmp_path):
    """A finding file with run feature/login that no `finding` field names
    stays outside the scope and fails the merge (BR-066)."""
    run = _story_with_findings(tmp_path, QA, "QA-0016")
    _store_mutants(run, _filed())
    tip = _git(run["feature"], "rev-parse", "HEAD")

    result = _merge(run)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "BLOCK out-of-scope-paths: docs/findings/QA-0016.md" in result.stdout
    assert _git(run["feature"], "rev-parse", "HEAD") == tip
