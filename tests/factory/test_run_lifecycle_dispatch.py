"""dispatch commands of the run lifecycle (docs/spec/features/run-lifecycle.feature).

Each test builds its own git repository in tmp_path and runs dispatch as a
subprocess, the way the implementation agent does.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from conftest import SOURCE_SCRIPTS_DIR, write_review_report

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
