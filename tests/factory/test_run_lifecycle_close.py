"""The end of a run (docs/spec/features/run-lifecycle.feature).

Rules: Implementation agent starts a story only when its dependencies inside
the run are done; User ends a run and leaves no run state behind.

Each test builds its own git repository in tmp_path and runs dispatch as a
subprocess, the way the implementation agent does.
"""

from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from conftest import SOURCE_SCRIPTS_DIR, write_review_report
from test_finding_stop import finding, write_finding

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


# -- RL-14: User ends a run and leaves no run state behind ---------------------

CLOSE_STORY = STORY.replace("deps: [{deps}]", "deps: []").replace(
    'touches: ["src/{id}.txt"]', 'touches: ["src/{id}.txt", "src/login.py"]'
)


def _run_repo(root: Path, stories: tuple[str, ...] = ("ST-0350", "ST-0351")) -> Path:
    """A repository on dev with a test command and the stories pending."""
    repo = root / "repo"
    for folder in ("backlog", "docs", "src"):
        (repo / folder).mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    for story_id in stories:
        (repo / "backlog" / f"{story_id}.md").write_text(CLOSE_STORY.format(id=story_id))
    (repo / "docs" / "testing.yaml").write_text('test_command: "true"\n')
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "src" / "login.py").write_text("def login():\n    return True\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    return repo


def _ledger_of(repo: Path) -> Path:
    return repo / ".current-work" / BRANCH / "dispatch-ledger.yaml"


def _story_tree(repo: Path, story_id: str) -> Path:
    return repo / ".current-work" / BRANCH / "story" / story_id


def _run(repo: Path, *steps: tuple[str, ...]) -> None:
    for args in steps:
        result = _dispatch(repo, _ledger_of(repo), *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)


def _start(repo: Path, stories: str = "ST-0350,ST-0351") -> None:
    _run(
        repo,
        ("init", "--base", "dev", "--feature-branch", BRANCH, "--stories", stories),
        ("plan", "--backlog-dir", "backlog"),
    )


def _dispatched(repo: Path, *story_ids: str) -> None:
    _run(repo, ("prepare-wave", "1"))
    for story_id in story_ids:
        _run(repo, ("mark-dispatching", story_id), ("mark-dispatched", story_id))


def _commit_work(tree: Path, story_id: str) -> str:
    (tree / "src" / f"{story_id}.txt").write_text("work\n")
    _git(tree, "add", "-A")
    _git(tree, "commit", "-qm", f"feat: work ({story_id})")
    return _git(tree, "rev-parse", "HEAD")


def _worktrees(repo: Path) -> list[str]:
    out = _git(repo, "worktree", "list", "--porcelain")
    return [line[len("worktree "):] for line in out.splitlines() if line.startswith("worktree ")]


def _branches(repo: Path) -> set[str]:
    return set(_git(repo, "branch", "--format=%(refname:short)").splitlines())


def _close(repo: Path, *flags: str) -> subprocess.CompletedProcess:
    return _dispatch(repo, _ledger_of(repo), "close", *flags)


def _place_run_state(repo: Path) -> None:
    """Gate results, markers and a brief of the run, and of another run."""
    current = repo / ".current-work"
    for gate in ("crap-score", "dependency-check"):
        (current / gate).mkdir(parents=True, exist_ok=True)
        (current / gate / "ST-0350.json").write_text("[]\n")
        (current / gate / "ST-0999.json").write_text("[]\n")
    (current / "premerge-check-ok").write_text(f"branch={BRANCH}\nhead=abc\n")
    (current / BRANCH / "briefs").mkdir(parents=True, exist_ok=True)
    (current / BRANCH / "briefs" / "ST-0350.md").write_text("brief\n")


@pytest.fixture(scope="module")
def finished_run(tmp_path_factory) -> dict:
    """A finished run on feature/login, closed once.

    ST-0350 merged through merge-story, but its worktree still holds an
    untracked notes.txt and a change to the tracked src/login.py, so
    merge-story could not remove it. The User returned ST-0351, whose branch
    holds a commit that is not merged. A crash left the premerge worktree of
    ST-0350. The User merged feature/login into dev and ran dispatch close.
    """
    repo = _run_repo(tmp_path_factory.mktemp("finished"))
    _start(repo)
    _dispatched(repo, "ST-0350", "ST-0351")
    _commit_work(_story_tree(repo, "ST-0351"), "ST-0351")
    _run(
        repo,
        ("mark-blocked", "ST-0351", "--reason", "design question"),
        ("return-story", "ST-0351"),
    )
    story = _story_tree(repo, "ST-0350")
    (story / "src" / "ST-0350.txt").write_text("work\n")
    write_review_report(story, "ST-0350")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", "feat: work (ST-0350)")
    sha = _git(story, "rev-parse", "HEAD")
    _run(repo, ("verify-story", "ST-0350", "--sha", sha))
    (story / "notes.txt").write_text("my notes\n")
    (story / "src" / "login.py").write_text("def login():\n    return False\n")
    feature = repo / ".current-work" / BRANCH / "invocation"
    merged = _dispatch(feature, _ledger_of(repo), "merge-story", "ST-0350")
    assert merged.returncode == 0, merged.stdout + merged.stderr
    assert story.is_dir()
    premerge = repo / ".current-work" / BRANCH / "premerge" / "ST-0350"
    _git(repo, "worktree", "add", "-q", "--detach", str(premerge), "story/ST-0350")
    _place_run_state(repo)
    (repo / ".current-work" / "verify-base-ok").write_text("target=dev\n")
    _git(repo, "merge", "-q", "--no-ff", "-m", "merge feature/login", BRANCH)

    result = _close(repo)
    return {
        "repo": repo, "result": result, "story": story, "premerge": premerge,
        "date": datetime.now().astimezone().date().isoformat(),
    }


@pytest.mark.spec("RL-14-IT-01")
def test_RL_14_IT_01_dispatch_close_removes_the_state_of_a_finished_run(finished_run):
    """Scenario: dispatch close removes the state of a finished run."""
    repo, result = finished_run["repo"], finished_run["result"]
    current = repo / ".current-work"

    assert result.returncode == 0, result.stdout + result.stderr
    assert not _ledger_of(repo).exists()
    assert not (current / BRANCH).exists()
    assert _worktrees(repo) == [str(repo.resolve())]
    for gate in ("crap-score", "dependency-check"):
        assert not (current / gate / "ST-0350.json").exists()
        assert (current / gate / "ST-0999.json").exists()
    assert not (current / "premerge-check-ok").exists()
    assert "story/ST-0350" not in _branches(repo)
    assert BRANCH not in _branches(repo)


@pytest.mark.spec("RL-14-IT-01")
def test_RL_14_IT_01_close_keeps_the_verify_base_marker_of_the_primary_checkout(
    finished_run,
):
    """An orchestrated run runs verify-base only in its worktrees, so the
    marker of the primary checkout belongs to no run of it."""
    assert (finished_run["repo"] / ".current-work" / "verify-base-ok").exists()


@pytest.mark.spec("RL-14-IT-01")
def test_RL_14_IT_01_close_keeps_the_premerge_marker_of_another_branch(tmp_path):
    repo = _run_repo(tmp_path)
    _start(repo)
    marker = repo / ".current-work" / "premerge-check-ok"
    marker.write_text("branch=feature/other\nhead=abc\n")

    result = _close(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert marker.read_text() == "branch=feature/other\nhead=abc\n"


@pytest.mark.spec("RL-14-IT-02")
def test_RL_14_IT_02_dispatch_close_lists_what_it_cannot_delete(finished_run):
    """Scenario: dispatch close lists what it cannot delete."""
    repo, result = finished_run["repo"], finished_run["result"]

    assert "unmerged branch: story/ST-0351" in result.stdout
    assert "story/ST-0351" in _branches(repo)


@pytest.mark.spec("RL-14-IT-03")
def test_RL_14_IT_03_dispatch_close_stashes_uncommitted_files_under_a_name(finished_run):
    """Scenario: dispatch close stashes uncommitted files under a name."""
    repo, result = finished_run["repo"], finished_run["result"]
    name = f"run {BRANCH} ST-0350 {finished_run['date']}"
    stashes = _git(repo, "stash", "list", "--format=%H %s").splitlines()
    mine = [line.split()[0] for line in stashes if line.endswith(f": {name}")]

    assert len(mine) == 1, stashes
    assert f"stash: {name}" in result.stdout
    untracked = _git(repo, "show", "--format=", "--name-only", f"{mine[0]}^3")
    assert untracked.splitlines() == ["notes.txt"]
    tracked = _git(repo, "diff", "--name-only", f"{mine[0]}^1", mine[0])
    assert tracked.splitlines() == ["src/login.py"]
    assert not (repo / "notes.txt").exists()
    assert (repo / "src" / "login.py").read_text() == "def login():\n    return True\n"


@pytest.mark.spec("RL-14-IT-03")
def test_RL_14_IT_03_a_clean_worktree_makes_no_stash(finished_run):
    """ST-0351 and the feature worktree were clean, so only ST-0350 has a stash."""
    stashes = _git(finished_run["repo"], "stash", "list", "--format=%s").splitlines()

    assert len(stashes) == 1, stashes


@pytest.mark.spec("RL-14-IT-07")
def test_RL_14_IT_07_a_temporary_premerge_worktree_left_by_a_crash_is_removed(
    finished_run,
):
    """Scenario: A temporary premerge worktree left by a crash is removed."""
    premerge = finished_run["premerge"]

    assert not premerge.exists()
    assert str(premerge) not in _worktrees(finished_run["repo"])


@pytest.mark.spec("RL-14-IT-04")
@pytest.mark.parametrize("flags", [(), ("--drop",)], ids=["close", "drop"])
@pytest.mark.parametrize("stop", ["failed", "blocked"])
def test_RL_14_IT_04_dispatch_close_refuses_a_run_with_a_stopped_story(
    tmp_path, flags, stop,
):
    """Scenario: dispatch close refuses a run with a stopped story."""
    repo = _run_repo(tmp_path)
    _start(repo, "ST-0350")
    _dispatched(repo, "ST-0350")
    mark = (
        ("mark-failed", "ST-0350") if stop == "failed"
        else ("mark-blocked", "ST-0350", "--reason", "waits")
    )
    _run(repo, mark)
    before = _ledger_of(repo).read_text()

    result = _close(repo, *flags)

    assert result.returncode != 0
    assert "ST-0350" in result.stderr
    assert stop in result.stderr
    assert _ledger_of(repo).read_text() == before
    assert _story_tree(repo, "ST-0350").is_dir()


@pytest.mark.spec("RL-14-IT-04")
def test_RL_14_IT_04_dispatch_close_refuses_a_story_still_in_progress(tmp_path):
    """BR-119 accepts only done and pending, so a dispatched story keeps its worktree."""
    repo = _run_repo(tmp_path)
    _start(repo, "ST-0350")
    _dispatched(repo, "ST-0350")

    result = _close(repo)

    assert result.returncode != 0
    assert "ST-0350 is dispatched" in result.stderr
    assert _ledger_of(repo).exists()
    assert _story_tree(repo, "ST-0350").is_dir()


@pytest.mark.spec("RL-14-IT-05")
def test_RL_14_IT_05_dispatch_close_refuses_a_feature_branch_not_merged_into_dev(
    tmp_path,
):
    """Scenario: dispatch close refuses a feature branch that is not merged into dev."""
    repo = _run_repo(tmp_path)
    _start(repo)
    feature = repo / ".current-work" / BRANCH / "invocation"
    (feature / "feature.txt").write_text("feature\n")
    _git(feature, "add", "-A")
    _git(feature, "commit", "-qm", "feature work")
    before = _ledger_of(repo).read_text()

    result = _close(repo)

    assert result.returncode != 0
    assert "dispatch close --drop" in result.stderr
    assert _ledger_of(repo).read_text() == before
    assert feature.is_dir()


@pytest.mark.spec("RL-14-IT-06")
def test_RL_14_IT_06_the_user_drops_a_run(tmp_path):
    """Scenario: The User drops a run."""
    repo = _run_repo(tmp_path)
    _start(repo, "ST-0350")
    _dispatched(repo, "ST-0350")
    _commit_work(_story_tree(repo, "ST-0350"), "ST-0350")
    _run(
        repo,
        ("mark-blocked", "ST-0350", "--reason", "design question"),
        ("return-story", "ST-0350"),
    )
    feature = repo / ".current-work" / BRANCH / "invocation"
    (feature / "feature.txt").write_text("feature\n")
    _git(feature, "add", "-A")
    _git(feature, "commit", "-qm", "feature work")
    _place_run_state(repo)

    result = _close(repo, "--drop")

    assert result.returncode == 0, result.stdout + result.stderr
    current = repo / ".current-work"
    assert not _ledger_of(repo).exists()
    assert not (current / BRANCH).exists()
    assert _worktrees(repo) == [str(repo.resolve())]
    assert not (current / "crap-score" / "ST-0350.json").exists()
    assert not (current / "premerge-check-ok").exists()
    assert "unmerged branch: story/ST-0350" in result.stdout
    assert f"unmerged branch: {BRANCH}" in result.stdout
    assert {"story/ST-0350", BRANCH} <= _branches(repo)


@pytest.mark.spec("RL-14-IT-08")
@pytest.mark.parametrize("flags", [(), ("--drop",)], ids=["close", "drop"])
def test_RL_14_IT_08_a_stop_allows_dispatch_close(tmp_path, flags):
    """Scenario Outline: A stop allows the commands that start and merge nothing."""
    outcomes = []
    for name, stop in (("plain", False), ("stopped", True)):
        repo = _run_repo(tmp_path / name)
        _start(repo)
        if stop:
            write_finding(repo, finding())
        result = _close(repo, *flags)
        outcomes.append((
            result.returncode,
            result.stdout.replace(str(tmp_path / name), "<tmp>"),
            _ledger_of(repo).exists(),
            sorted(_branches(repo)),
        ))

    assert "STOP:" not in outcomes[1][1]
    assert outcomes[1] == outcomes[0]
    assert outcomes[0][0] == 0


@pytest.mark.spec("RL-17-IT-03")
def test_RL_17_IT_03_dispatch_close_closes_a_run_whose_ledger_has_the_old_names(tmp_path):
    """Scenario: dispatch close closes a run whose ledger has the old names."""
    repo = _run_repo(tmp_path, stories=("ST-0350",))
    _start(repo, "ST-0350")
    ledger = _ledger_of(repo)
    data = yaml.safe_load(ledger.read_text())
    data["invocation_branch"] = data.pop("feature_branch")
    data["mode"] = "automated"
    data["stories"]["ST-0350"]["status"] = "done"
    ledger.write_text(yaml.safe_dump(data))

    result = _close(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert not ledger.exists()
    assert BRANCH not in _branches(repo)


# -- The stops and the path guards of the close (IMPL-0040 to IMPL-0044) -------


def _returned(repo: Path) -> Path:
    """A run on feature/login whose only story ST-0350 the User returned.

    Return the worktree of ST-0350, which return-story leaves in place."""
    _start(repo, "ST-0350")
    _dispatched(repo, "ST-0350")
    _run(
        repo,
        ("mark-blocked", "ST-0350", "--reason", "design question"),
        ("return-story", "ST-0350"),
    )
    return _story_tree(repo, "ST-0350")


def _stash_of(repo: Path, label: str) -> str | None:
    name = f"run {BRANCH} {label} {datetime.now().astimezone().date().isoformat()}"
    for line in _git(repo, "stash", "list", "--format=%H %s").splitlines():
        if line.endswith(f": {name}"):
            return line.split()[0]
    return None


@pytest.mark.spec("RL-14-IT-03")
@pytest.mark.parametrize("config", [None, "no", "normal"], ids=["default", "no", "normal"])
def test_RL_14_IT_03_close_stashes_a_worktree_with_only_an_untracked_file(
    tmp_path, config,
):
    """IMPL-0040: the check for changes ignores status.showUntrackedFiles."""
    repo = _run_repo(tmp_path)
    story = _returned(repo)
    (story / "notes.txt").write_text("my notes\n")
    (story / "drafts").mkdir()
    (story / "drafts" / "idea.txt").write_text("idea\n")
    if config:
        _git(repo, "config", "status.showUntrackedFiles", config)

    result = _close(repo, "--drop")

    assert result.returncode == 0, result.stdout + result.stderr
    stash = _stash_of(repo, "ST-0350")
    assert stash, result.stdout
    untracked = _git(repo, "show", "--format=", "--name-only", f"{stash}^3")
    assert sorted(untracked.splitlines()) == ["drafts/idea.txt", "notes.txt"]


@pytest.mark.spec("RL-14-IT-03")
def test_RL_14_IT_03_close_stashes_a_worktree_with_only_a_tracked_change(tmp_path):
    repo = _run_repo(tmp_path)
    story = _returned(repo)
    (story / "src" / "login.py").write_text("def login():\n    return False\n")

    result = _close(repo, "--drop")

    assert result.returncode == 0, result.stdout + result.stderr
    stash = _stash_of(repo, "ST-0350")
    assert stash, result.stdout
    tracked = _git(repo, "diff", "--name-only", f"{stash}^1", stash)
    assert tracked.splitlines() == ["src/login.py"]


@pytest.mark.spec("RL-14-IT-01")
def test_RL_14_IT_01_close_refuses_to_remove_a_worktree_that_holds_one_the_ledger_does_not_name(
    tmp_path,
):
    """IMPL-0041: a worktree of another run inside the ignored .current-work/
    of the feature worktree stops the close."""
    repo = _run_repo(tmp_path)
    _returned(repo)
    feature = repo / ".current-work" / BRANCH / "invocation"
    nested = feature / ".current-work" / "feature" / "other" / "story" / "ST-0900"
    _git(repo, "worktree", "add", "-q", "-b", "story/ST-0900", str(nested), "dev")
    (nested / "work.txt").write_text("work\n")
    before = _ledger_of(repo).read_text()

    result = _close(repo, "--drop")

    assert result.returncode == 1, result.stdout + result.stderr
    assert str(nested) in result.stderr
    assert _ledger_of(repo).read_text() == before
    assert (nested / "work.txt").read_text() == "work\n"
    assert str(nested) in _worktrees(repo)
    assert feature.is_dir()


@pytest.mark.spec("RL-14-IT-01")
@pytest.mark.parametrize(
    "name", ["feature/../feature/other", "feature/./other", "feature//other", "@{-1}"],
)
def test_RL_14_IT_01_close_refuses_a_feature_branch_that_git_rejects(tmp_path, name):
    """IMPL-0042: a feature branch edited by hand cannot point at another run."""
    repo = _run_repo(tmp_path)
    _start(repo, "ST-0350")
    other = repo / ".current-work" / "feature" / "other" / "briefs" / "ST-0901.md"
    other.parent.mkdir(parents=True)
    other.write_text("brief\n")
    ledger = _ledger_of(repo)
    data = yaml.safe_load(ledger.read_text())
    data["feature_branch"] = name
    ledger.write_text(yaml.safe_dump(data))
    before = ledger.read_text()

    result = _close(repo, "--drop")

    assert result.returncode == 1, result.stdout + result.stderr
    assert ledger.read_text() == before
    assert other.read_text() == "brief\n"


@pytest.mark.spec("RL-14-IT-01")
def test_RL_14_IT_01_close_refuses_a_symlinked_run_folder(tmp_path):
    """IMPL-0042: a run folder that is a symlink leads to another run."""
    repo = _run_repo(tmp_path)
    _start(repo, "ST-0350")
    current = repo / ".current-work"
    other = current / "feature" / "other" / "briefs" / "ST-0901.md"
    other.parent.mkdir(parents=True)
    other.write_text("brief\n")
    (current / "feature" / "link").symlink_to("other")
    ledger = _ledger_of(repo)
    data = yaml.safe_load(ledger.read_text())
    data["feature_branch"] = "feature/link"
    ledger.write_text(yaml.safe_dump(data))
    before = ledger.read_text()

    result = _close(repo, "--drop")

    assert result.returncode == 1, result.stdout + result.stderr
    assert "symlink" in result.stderr
    assert ledger.read_text() == before
    assert other.read_text() == "brief\n"


@pytest.mark.spec("RL-14-IT-01")
def test_RL_14_IT_01_close_leaves_a_worktree_outside_current_work(tmp_path):
    """A ledger entry that names a worktree outside .current-work/ keeps it."""
    repo = _run_repo(tmp_path)
    _start(repo, "ST-0350")
    outside = tmp_path / "outside"
    _git(repo, "worktree", "add", "-q", "-b", "story/ST-0350", str(outside), "dev")
    (outside / "notes.txt").write_text("my notes\n")
    ledger = _ledger_of(repo)
    data = yaml.safe_load(ledger.read_text())
    data["stories"]["ST-0350"].update(worktree=str(outside), branch="story/ST-0350")
    ledger.write_text(yaml.safe_dump(data))

    result = _close(repo, "--drop")

    assert result.returncode == 0, result.stdout + result.stderr
    assert (outside / "notes.txt").read_text() == "my notes\n"
    assert str(outside.resolve()) in _worktrees(repo)
    assert _stash_of(repo, "ST-0350") is None


@pytest.mark.spec("RL-14-IT-03")
def test_RL_14_IT_03_a_failed_stash_stops_the_close_and_keeps_the_ledger(tmp_path):
    """IMPL-0044: a lock on refs/stash makes git stash push fail."""
    repo = _run_repo(tmp_path)
    story = _returned(repo)
    (story / "notes.txt").write_text("my notes\n")
    (repo / ".git" / "refs" / "stash.lock").write_text("")
    before = _ledger_of(repo).read_text()

    result = _close(repo, "--drop")

    assert result.returncode == 1, result.stdout + result.stderr
    assert "git stash failed" in result.stderr
    assert _ledger_of(repo).read_text() == before
    assert (story / "notes.txt").read_text() == "my notes\n"


@pytest.mark.spec("RL-14-IT-03")
def test_RL_14_IT_03_a_failed_removal_stops_the_close_and_names_the_stash(tmp_path):
    """IMPL-0044: git worktree remove refuses a locked worktree."""
    repo = _run_repo(tmp_path)
    story = _returned(repo)
    (story / "notes.txt").write_text("my notes\n")
    _git(repo, "worktree", "lock", str(story))
    before = _ledger_of(repo).read_text()

    result = _close(repo, "--drop")

    assert result.returncode == 1, result.stdout + result.stderr
    assert "git worktree remove failed" in result.stderr
    assert _ledger_of(repo).read_text() == before
    assert story.is_dir()
    stash = _stash_of(repo, "ST-0350")
    assert stash
    assert f"stash: run {BRANCH} ST-0350" in result.stdout
    untracked = _git(repo, "show", "--format=", "--name-only", f"{stash}^3")
    assert untracked.splitlines() == ["notes.txt"]


def _git_that_fails_after_prune(tmp_path: Path) -> dict[str, str]:
    """An environment whose git fails git worktree list after git worktree prune."""
    real = subprocess.run(
        ["which", "git"], capture_output=True, text=True, check=True,
    ).stdout.strip()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    flag = tmp_path / "pruned"
    wrapper = bin_dir / "git"
    wrapper.write_text(
        "#!/bin/sh\n"
        'case " $* " in\n'
        f'  *" worktree prune "*) touch "{flag}" ;;\n'
        f'  *" worktree list "*) [ -e "{flag}" ] && exit 128 ;;\n'
        "esac\n"
        f'exec "{real}" "$@"\n'
    )
    wrapper.chmod(0o755)
    env = _env()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    return env


@pytest.mark.spec("RL-14-IT-01")
def test_RL_14_IT_01_a_failed_worktree_list_keeps_the_run_folder(tmp_path):
    """IMPL-0043: the check that keeps the run folder fails closed."""
    repo = _run_repo(tmp_path)
    _returned(repo)
    brief = repo / ".current-work" / BRANCH / "briefs" / "ST-0350.md"
    brief.parent.mkdir(parents=True)
    brief.write_text("brief\n")

    result = subprocess.run(
        [str(DISPATCH), "--ledger", str(_ledger_of(repo)), "close", "--drop"],
        cwd=repo, env=_git_that_fails_after_prune(tmp_path),
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 1, result.stdout + result.stderr
    assert "git worktree list failed" in result.stderr
    assert _ledger_of(repo).exists()
    assert brief.read_text() == "brief\n"


# -- RL-15: User cleans up the runs that no active run owns --------------------


def _orphan_repo(root: Path) -> Path:
    """A repository on dev whose .current-work/ git ignores."""
    repo = root / "repo"
    repo.mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "README.md").write_text("repo\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    return repo


def _tree(repo: Path, rel: str, branch: str | None, base: str = "dev") -> Path:
    """Add a worktree at .current-work/<rel>, on a new branch or detached."""
    path = repo / ".current-work" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if branch is None:
        _git(repo, "worktree", "add", "-q", "--detach", str(path), base)
    else:
        _git(repo, "worktree", "add", "-q", "-b", branch, str(path), base)
    return path


def _unmerged(tree: Path) -> None:
    (tree / "work.txt").write_text("work\n")
    _git(tree, "add", "-A")
    _git(tree, "commit", "-qm", "work")


def _write_ledger(
    path: Path,
    feature_branch: str,
    stories: dict[str, str],
    *,
    old_names: bool = False,
    worktrees: dict[str, str] | None = None,
) -> Path:
    """A ledger naming *feature_branch*, with each story in its state."""
    entries = {}
    for story_id, state in stories.items():
        entries[story_id] = {
            "id": story_id, "wave": 1, "status": state, "deps": [],
            "branch": f"story/{story_id}",
            "worktree": (worktrees or {}).get(story_id),
            "feature_branch": feature_branch,
        }
    data = {
        "mode": "automated" if old_names else "orchestrated",
        ("invocation_branch" if old_names else "feature_branch"): feature_branch,
        "stories": entries,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False))
    return path


def _orphans(repo: Path, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """dispatch close --orphans, without --ledger, as the User runs it."""
    return subprocess.run(
        [str(DISPATCH), "close", "--orphans"],
        cwd=cwd or repo, env=_env(), capture_output=True, text=True, check=False,
    )


def _today() -> str:
    return datetime.now().astimezone().date().isoformat()


@pytest.mark.spec("RL-15-IT-01")
def test_RL_15_IT_01_orphans_removes_a_worktree_whose_branch_is_merged_into_dev(tmp_path):
    """Scenario: --orphans removes a worktree whose branch is merged into dev."""
    repo = _orphan_repo(tmp_path)
    tree = _tree(repo, "feature/old/story/ST-0800", "story/ST-0800")
    (tree / "notes.txt").write_text("draft\n")
    (tree / ".gitignore").write_text("secret.env\n")

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert not tree.exists()
    assert str(tree) not in _worktrees(repo)
    assert f"removed worktree: {tree} (story/ST-0800)" in result.stdout
    name = f"orphan story/ST-0800 {_today()}"
    assert f"stash: {name}" in result.stdout
    stashes = _git(repo, "stash", "list", "--format=%s").splitlines()
    assert any(line.endswith(f": {name}") for line in stashes), stashes
    assert "story/ST-0800" in _branches(repo)


@pytest.mark.spec("RL-15-IT-01")
def test_RL_15_IT_01_orphans_keeps_every_worktree_of_a_live_run(tmp_path):
    """A ledger whose feature branch exists owns its worktrees, its branches and
    its folder, even when every branch is merged into dev."""
    repo = _run_repo(tmp_path)
    _start(repo)
    _dispatched(repo, "ST-0350", "ST-0351")
    story = _story_tree(repo, "ST-0350")
    (story / "notes.txt").write_text("agent at work\n")
    leftover = _tree(repo, f"{BRANCH}/premerge/ST-0351", None)
    before = _ledger_of(repo).read_text()
    trees = _worktrees(repo)

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert _ledger_of(repo).read_text() == before
    assert _worktrees(repo) == trees
    assert (story / "notes.txt").read_text() == "agent at work\n"
    assert leftover.is_dir()
    assert str(repo / ".current-work" / BRANCH) not in result.stdout
    assert _git(repo, "stash", "list") == ""


@pytest.mark.spec("RL-15-IT-02")
@pytest.mark.parametrize("merge_state", ["no branch", "feature/login", "detached"])
def test_RL_15_IT_02_orphans_lists_a_worktree_whose_branch_is_not_merged_into_dev(
    tmp_path, merge_state,
):
    """Scenario Outline: --orphans lists a worktree whose branch is not merged into dev."""
    repo = _orphan_repo(tmp_path)
    branch = None if merge_state == "detached" else "story/ST-0900"
    tree = _tree(repo, "feature/poc/story/ST-0900", branch)
    if merge_state != "detached":
        _unmerged(tree)
    if merge_state == "feature/login":
        _git(repo, "branch", "feature/login", "story/ST-0900")

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert tree.is_dir()
    assert str(tree) in _worktrees(repo)
    assert f"kept worktree: {tree}" in result.stdout
    if branch:
        assert "story/ST-0900 is not merged into dev" in result.stdout
    else:
        assert "detached HEAD" in result.stdout


@pytest.mark.spec("RL-15-IT-03")
def test_RL_15_IT_03_orphans_removes_a_ledger_without_a_branch_whose_stories_are_all_done(
    tmp_path,
):
    """Scenario: --orphans removes a ledger without a branch whose stories are all done.
    Scenario: --orphans handles an old ledger with mode automated."""
    repo = _orphan_repo(tmp_path)
    current = repo / ".current-work"
    old = _write_ledger(
        current / "feature/onboarding/dispatch-ledger.yaml", "feature/onboarding",
        {"ST-0100": "done", "ST-0101": "done"}, old_names=True,
    )
    host = _tree(repo, "feature/fitting", "feature/fitting")
    _unmerged(host)
    nested = _write_ledger(
        host / ".current-work/feature/gone/dispatch-ledger.yaml", "feature/gone",
        {"ST-0200": "done"},
    )
    layout = _write_ledger(
        current / "feature/layout/dispatch-ledger.yaml", "feature/layout",
        {"ST-0343": "done", "ST-0344": "blocked"}, old_names=True,
    )

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert not old.exists()
    assert not nested.exists()
    assert host.is_dir()
    assert f"removed ledger: {old}" in result.stdout
    assert f"removed ledger: {nested}" in result.stdout
    left = sorted(p for p in current.rglob("dispatch-ledger.yaml"))
    assert left == [layout]


@pytest.mark.spec("RL-15-IT-04")
def test_RL_15_IT_04_orphans_lists_a_ledger_without_a_branch_that_holds_an_unfinished_story(
    tmp_path,
):
    """Scenario: --orphans lists a ledger without a branch that holds an unfinished story.
    The ledger still owns its worktree, so the worktree stays too."""
    repo = _orphan_repo(tmp_path)
    tree = _tree(repo, "feature/layout/story/ST-0344", "story/ST-0344")
    ledger = _write_ledger(
        repo / ".current-work/feature/layout/dispatch-ledger.yaml", "feature/layout",
        {"ST-0343": "done", "ST-0344": "blocked"}, old_names=True,
        worktrees={"ST-0344": str(tree)},
    )
    before = ledger.read_text()

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert ledger.read_text() == before
    assert (
        f"kept ledger: {ledger} (feature/layout is gone; ST-0344 is blocked)"
        in result.stdout
    )
    assert tree.is_dir()
    assert str(tree) not in result.stdout


@pytest.mark.spec("RL-15-IT-04")
def test_RL_15_IT_04_orphans_keeps_a_ledger_it_cannot_read_and_what_it_may_own(tmp_path):
    """A ledger that dispatch cannot read stays and is listed. Each worktree whose
    branch or path its text names stays too, wherever it lies."""
    repo = _orphan_repo(tmp_path)
    by_branch = _tree(repo, "elsewhere/one", "story/ST-0700")
    by_path = _tree(repo, "elsewhere/two", "story/ST-0701")
    in_folder = _tree(repo, "feature/broken/story/ST-0702", "story/ST-0702")
    ledger = repo / ".current-work/feature/broken/dispatch-ledger.yaml"
    ledger.write_text(
        "---\nfeature_branch: feature/broken\nstories:\n"
        "  ST-0700:\n    id: ST-0700\n    status: not-a-state\n"
        "    branch: story/ST-0700\n"
        f"  ST-0701:\n    id: ST-0701\n    status: done\n    worktree: {by_path}\n"
    )
    stray = _tree(repo, "elsewhere/three", "story/ST-0703")

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert ledger.exists()
    assert f"kept ledger: {ledger} (dispatch cannot read it" in result.stdout
    for tree in (by_branch, by_path, in_folder):
        assert tree.is_dir()
    assert not stray.exists()


@pytest.mark.spec("RL-15-IT-04")
def test_RL_15_IT_04_orphans_keeps_a_worktree_that_holds_a_ledger_it_keeps(tmp_path):
    """Removing the worktree would delete the nested ledger with it."""
    repo = _orphan_repo(tmp_path)
    host = _tree(repo, "feature/host", "feature/host")
    ledger = _write_ledger(
        host / ".current-work/feature/gone/dispatch-ledger.yaml", "feature/gone",
        {"ST-0344": "blocked"},
    )

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert ledger.exists()
    assert host.is_dir()
    assert f"kept worktree: {host} (feature/host; it holds the ledger {ledger})" in result.stdout


@pytest.mark.spec("RL-15-IT-01")
def test_RL_15_IT_01_orphans_keeps_a_worktree_that_holds_one_it_keeps(tmp_path):
    """git would delete the inner worktree with the outer one."""
    repo = _orphan_repo(tmp_path)
    outer = _tree(repo, "feature/outer", "feature/outer")
    inner = _tree(repo, "feature/outer/.current-work/inner", "story/ST-0901")
    _unmerged(inner)

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert (inner / "work.txt").is_file()
    assert outer.is_dir()
    assert f"kept worktree: {outer} (feature/outer; it holds the worktree {inner})" in result.stdout


@pytest.mark.spec("RL-15-IT-01")
def test_RL_15_IT_01_orphans_removes_nested_merged_worktrees_inner_first(tmp_path):
    repo = _orphan_repo(tmp_path)
    outer = _tree(repo, "feature/outer", "feature/outer")
    inner = _tree(repo, "feature/outer/.current-work/inner", "story/ST-0902")

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert not inner.exists()
    assert not outer.exists()


@pytest.mark.spec("RL-15-IT-01")
def test_RL_15_IT_01_orphans_keeps_the_worktree_it_runs_in(tmp_path):
    repo = _orphan_repo(tmp_path)
    tree = _tree(repo, "feature/here", "feature/here")

    result = _orphans(repo, cwd=tree)

    assert result.returncode == 0, result.stdout + result.stderr
    assert tree.is_dir()
    assert f"kept worktree: {tree} (feature/here; dispatch runs inside it)" in result.stdout


@pytest.mark.spec("RL-15-IT-02")
def test_RL_15_IT_02_orphans_keeps_every_worktree_when_dev_is_missing(tmp_path):
    repo = _orphan_repo(tmp_path)
    tree = _tree(repo, "feature/old", "feature/old")
    _git(repo, "branch", "-m", "dev", "main")

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert tree.is_dir()
    assert "dev does not exist" in result.stdout


@pytest.mark.spec("RL-14-IT-08")
def test_RL_14_IT_08_a_stop_allows_dispatch_close_orphans(tmp_path):
    """BR-091 lets close --orphans run during a stop."""
    repo = _orphan_repo(tmp_path)
    tree = _tree(repo, "feature/old", "feature/old")
    write_finding(repo, finding())

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "STOP:" not in result.stdout
    assert not tree.exists()


@pytest.mark.spec("RL-15-IT-03")
@pytest.mark.parametrize(
    ("branch_state", "stories", "expected"),
    [
        ("exists", {"ST-1": "blocked"}, (False, None)),
        ("gone", {"ST-1": "done", "ST-2": "done"}, (True, None)),
        ("gone", {}, (True, None)),
        ("gone", {"ST-1": "done", "ST-2": "dispatched"},
         (False, "feature/x is gone; ST-2 is dispatched")),
        ("invalid", {"ST-1": "done"},
         (False, "its feature branch 'feature/x' is not a valid branch name")),
        ("none", {"ST-1": "done"}, (False, "it names no feature branch")),
    ],
)
def test_RL_15_IT_03_the_verdict_on_a_ledger_of_no_active_run(
    branch_state, stories, expected,
):
    """BR-120: only a ledger whose valid feature branch is gone and whose
    stories are all done goes. A live ledger stays without a line."""
    import dispatch_lib as lib

    ledger = lib.Ledger()
    ledger.feature_branch = None if branch_state == "none" else "feature/x"
    for story_id, state in stories.items():
        ledger.stories[story_id] = lib.StoryEntry(id=story_id, status=lib.StoryState(state))

    assert lib.orphan_ledger_verdict(ledger, branch_state) == expected


def _stashes(repo: Path) -> list[str]:
    return _git(repo, "stash", "list", "--format=%s").splitlines()


def _nested_run(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    """A live run on feature/x whose ledger cmd_init wrote in the linked
    worktree W, while the run's worktrees lie in the primary checkout."""
    repo = _orphan_repo(tmp_path)
    host = tmp_path / "W"
    _git(repo, "worktree", "add", "-q", "-b", "wbranch", str(host), "dev")
    feature = _tree(repo, "feature/x/invocation", "feature/x")
    story = _tree(repo, "feature/x/story/ST-1", "story/ST-1")
    (story / "wip.txt").write_text("agent at work\n")
    ledger = host / ".current-work/feature/x/dispatch-ledger.yaml"
    ledger.parent.mkdir(parents=True)
    return repo, ledger, feature, story


@pytest.mark.spec("RL-15-IT-01")
def test_RL_15_IT_01_orphans_keeps_a_live_run_whose_ledger_lies_in_a_linked_worktree(
    tmp_path,
):
    """IMPL-0049: a readable ledger in a linked worktree owns the run's
    worktrees in the primary checkout."""
    repo, ledger, feature, story = _nested_run(tmp_path)
    _write_ledger(ledger, "feature/x", {"ST-1": "dispatched"})

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert feature.is_dir()
    assert (story / "wip.txt").read_text() == "agent at work\n"
    assert _stashes(repo) == []


@pytest.mark.spec("RL-15-IT-04")
@pytest.mark.parametrize(
    "text",
    [
        "",
        "---\nmode: orchestrated\nfeature_branch: feature/x\nstories:\n  ST-1:\n    id: ST-1\n    wa",
        "---\nmode: orchestrated\nstories: {}\n",
    ],
    ids=["empty", "truncated", "no feature branch"],
)
def test_RL_15_IT_04_orphans_keeps_the_run_folder_of_a_nested_ledger_without_a_feature_branch(
    tmp_path, text,
):
    """IMPL-0045: a ledger that stays claims the matching folder under the
    primary checkout's .current-work/, also when it yields no feature branch."""
    repo, ledger, feature, story = _nested_run(tmp_path)
    ledger.write_text(text)

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert ledger.read_text() == text
    assert f"kept ledger: {ledger}" in result.stdout
    assert feature.is_dir()
    assert (story / "wip.txt").read_text() == "agent at work\n"
    assert _stashes(repo) == []


@pytest.mark.spec("RL-15-IT-03")
def test_RL_15_IT_03_orphans_keeps_a_project_file_named_like_a_ledger(tmp_path):
    """IMPL-0046: the walk reads only .current-work/ folders, so a tracked
    file named dispatch-ledger.yaml in a worktree's checkout stays."""
    repo = _orphan_repo(tmp_path)
    fixture = _write_ledger(
        repo / "tests/fixtures/dispatch-ledger.yaml", "feature/example", {"ST-1": "done"},
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "fixture")
    feature = _tree(repo, "feature/x/invocation", "feature/x")
    _write_ledger(
        repo / ".current-work/feature/x/dispatch-ledger.yaml", "feature/x",
        {"ST-1": "dispatched"},
    )
    copy = feature / "tests/fixtures/dispatch-ledger.yaml"
    edited = copy.read_text() + "# local edit\n"
    copy.write_text(edited)

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert copy.read_text() == edited
    assert fixture.is_file()
    assert "removed ledger" not in result.stdout


@pytest.mark.spec("RL-15-IT-03")
def test_RL_15_IT_03_orphans_keeps_a_ledger_that_git_tracks(tmp_path):
    """IMPL-0046: --orphans never deletes a file that git tracks."""
    repo = _orphan_repo(tmp_path)
    ledger = _write_ledger(
        repo / ".current-work/feature/example/dispatch-ledger.yaml", "feature/example",
        {"ST-1": "done"},
    )
    _git(repo, "add", "-f", str(ledger))
    _git(repo, "commit", "-qm", "example ledger")

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert ledger.is_file()
    assert f"kept ledger: {ledger} (git tracks it in {repo})" in result.stdout


@pytest.mark.spec("RL-15-IT-02")
def test_RL_15_IT_02_orphans_keeps_a_locked_worktree_before_any_stash(tmp_path):
    """IMPL-0047: a locked worktree stays with its changes, and no stash exists."""
    repo = _orphan_repo(tmp_path)
    locked = _tree(repo, "feature/old/story/ST-1", "story/ST-1")
    (locked / "w.txt").write_text("w\n")
    _git(repo, "worktree", "lock", str(locked))
    free = _tree(repo, "feature/old/story/ST-2", "story/ST-2")

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert (locked / "w.txt").read_text() == "w\n"
    assert f"kept worktree: {locked} (story/ST-1; it is locked)" in result.stdout
    assert not free.exists()
    assert not any("story/ST-1" in line for line in _stashes(repo))


@pytest.mark.spec("RL-15-IT-04")
def test_RL_15_IT_04_orphans_reads_the_ledger_behind_a_symlinked_run_folder(tmp_path):
    """IMPL-0048: a symlinked folder under .current-work/ gets a line, and the
    live ledger behind it keeps its worktrees."""
    repo = _orphan_repo(tmp_path)
    outside = tmp_path / "outside"
    ledger = _write_ledger(outside / "dispatch-ledger.yaml", "feature/x", {"ST-1": "dispatched"})
    link = repo / ".current-work/feature/x"
    link.parent.mkdir(parents=True)
    link.symlink_to(outside)
    story = _tree(repo, "story-x/ST-1", "story/ST-1")
    feature = _tree(repo, "inv-x", "feature/x")
    before = ledger.read_text()

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"kept link: {link}" in result.stdout
    assert ledger.read_text() == before
    assert story.is_dir()
    assert feature.is_dir()


@pytest.mark.spec("RL-15-IT-04")
def test_RL_15_IT_04_orphans_keeps_a_symlinked_ledger_and_its_folder(tmp_path):
    """IMPL-0049: a ledger that is a symlink stays and is listed; it owns its folder."""
    repo = _orphan_repo(tmp_path)
    target = _write_ledger(tmp_path / "elsewhere/dispatch-ledger.yaml", "feature/old", {})
    link = repo / ".current-work/feature/old/dispatch-ledger.yaml"
    link.parent.mkdir(parents=True)
    link.symlink_to(target)
    story = _tree(repo, "feature/old/story/ST-1", "story/ST-1")

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert link.is_symlink()
    assert target.is_file()
    assert f"kept ledger: {link} (dispatch cannot read it: it is a symlink" in result.stdout
    assert story.is_dir()


def _git_that_fails_worktree_remove(tmp_path: Path) -> dict[str, str]:
    """An environment whose git fails every git worktree remove."""
    real = subprocess.run(
        ["which", "git"], capture_output=True, text=True, check=True,
    ).stdout.strip()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    wrapper = bin_dir / "git"
    wrapper.write_text(
        "#!/bin/sh\n"
        'case " $* " in\n'
        '  *" worktree remove "*) echo "fatal: refused" >&2; exit 128 ;;\n'
        "esac\n"
        f'exec "{real}" "$@"\n'
    )
    wrapper.chmod(0o755)
    env = _env()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    return env


@pytest.mark.spec("RL-15-IT-01")
def test_RL_15_IT_01_orphans_stops_after_a_failed_removal_and_names_the_stash(tmp_path):
    """IMPL-0049: a failed git worktree remove stops the run with exit 1,
    after the stash line, and the next orphan stays."""
    repo = _orphan_repo(tmp_path)
    deep = _tree(repo, "feature/old/story/ST-1", "story/ST-1")
    (deep / "notes.txt").write_text("draft\n")
    shallow = _tree(repo, "feature/older", "feature/older")

    result = subprocess.run(
        [str(DISPATCH), "close", "--orphans"],
        cwd=repo, env=_git_that_fails_worktree_remove(tmp_path),
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 1, result.stdout + result.stderr
    name = f"orphan story/ST-1 {_today()}"
    assert f"stash: {name}" in result.stdout
    assert any(line.endswith(f": {name}") for line in _stashes(repo))
    assert f"git worktree remove failed for {deep}" in result.stderr
    assert "dispatch close --orphans: done" not in result.stdout
    assert shallow.is_dir()
    assert deep.is_dir()


@pytest.mark.spec("RL-15-IT-01")
@pytest.mark.parametrize("nested", ["at the root", "deeper"])
def test_RL_15_IT_01_orphans_keeps_a_run_whose_run_folder_is_its_feature_worktree(
    tmp_path, nested,
):
    """IMPL-0053: dispatch init without --feature-branch puts the feature
    worktree at .current-work/<branch> and the ledger at its root. The walk
    still reads that ledger, so the live run keeps its worktrees."""
    repo = _orphan_repo(tmp_path)
    if nested == "at the root":
        feature = _tree(repo, "feature/x", "feature/x")
        ledger = feature / "dispatch-ledger.yaml"
        story_rel = "feature/x/.current-work/story/ST-1"
    else:
        feature = _tree(repo, "feature", "feature/host")
        ledger = feature / "x/dispatch-ledger.yaml"
        _git(repo, "branch", "feature/x", "dev")
        story_rel = "feature/x/story/ST-1"
    _write_ledger(ledger, "feature/x", {"ST-1": "dispatched"})
    story = _tree(repo, story_rel, "story/ST-1")
    (story / "wip.txt").write_text("agent at work\n")
    before = ledger.read_text()

    result = _orphans(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert ledger.read_text() == before
    assert feature.is_dir()
    assert (story / "wip.txt").read_text() == "agent at work\n"
    assert _stashes(repo) == []
