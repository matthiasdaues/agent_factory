"""Integration tests for dispatch merge-story (Layer 3c)."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

DISPATCH_SCRIPT = (
    Path(__file__).resolve().parent.parent.parent / "factory" / "scripts" / "dispatch"
)
SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent / "factory" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
dispatch_lib = importlib.import_module("dispatch_lib")

Ledger = dispatch_lib.Ledger
StoryEntry = dispatch_lib.StoryEntry
StoryState = dispatch_lib.StoryState


def _git_env(tmp_path: Path) -> dict[str, str]:
    """Return a git environment isolated from user-level configuration."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", HOME=str(tmp_path))
    return env


def _run_dispatch(
    *args: str, cwd: Path, tmp_path: Path
) -> subprocess.CompletedProcess[str]:
    """Invoke the dispatch CLI as a subprocess."""
    return subprocess.run(
        [sys.executable, str(DISPATCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
        env=_git_env(tmp_path),
    )


def _git(repo: Path, tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command inside the temporary repository."""
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=repo,
        check=False,
        env=_git_env(tmp_path),
    )


def _init_repo(tmp_path: Path, test_command: str = "true") -> Path:
    """Create a minimal git repository with a passing/failing test_command."""
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
        json.dumps({"project_name": "test", "test_command": test_command})
    )

    backlog_dir = repo / "backlog"
    backlog_dir.mkdir()

    result = _git(repo, tmp_path, "add", "-A")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "--no-verify", "-m", "initial")
    assert result.returncode == 0, result.stderr
    return repo


def _write_story_file(
    repo: Path, story_id: str, outputs: list[str], status: str = "dispatched"
) -> Path:
    """Write a minimal backlog story file with the given outputs frontmatter."""
    outputs_yaml = "\n".join(f'  - "{o}"' for o in outputs)
    text = (
        "---\n"
        f"id: {story_id}\n"
        f"status: {status}\n"
        "quality-gates: []\n"
        "outputs:\n"
        f"{outputs_yaml}\n"
        "---\n\n"
        f"# {story_id}\n"
    )
    path = repo / "backlog" / f"{story_id}.md"
    path.write_text(text)
    return path


def _commit_story_file(repo: Path, tmp_path: Path, story_id: str) -> None:
    """Commit the story's backlog file to the current branch (main)."""
    result = _git(repo, tmp_path, "add", "--", f"backlog/{story_id}.md")
    assert result.returncode == 0, result.stderr
    result = _git(
        repo, tmp_path, "commit", "--no-verify", "-m", f"backlog: add {story_id}"
    )
    assert result.returncode == 0, result.stderr


def _write_ledger(repo: Path, *entries: StoryEntry) -> Path:
    """Persist a dispatch ledger containing the provided entries."""
    ledger = Ledger()
    for entry in entries:
        ledger.stories[entry.id] = entry
    ledger_path = repo / ".current-work" / "dispatch-ledger.yaml"
    ledger.save(ledger_path)
    return ledger_path


def _load_ledger(repo: Path) -> Ledger:
    """Load the repository's default dispatch ledger."""
    return Ledger.load(repo / ".current-work" / "dispatch-ledger.yaml")


def _make_story_branch(
    repo: Path, tmp_path: Path, story_id: str, filename: str, content: str
) -> None:
    """Create story branch off HEAD with one commit touching *filename*."""
    branch = f"story/{story_id}"
    result = _git(repo, tmp_path, "branch", branch, "HEAD")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "checkout", branch)
    assert result.returncode == 0, result.stderr
    (repo / filename).parent.mkdir(parents=True, exist_ok=True)
    (repo / filename).write_text(content)
    result = _git(repo, tmp_path, "add", "-A")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "--no-verify", "-m", f"feat: {story_id}")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "checkout", "main")
    assert result.returncode == 0, result.stderr


def _make_story_worktree(repo: Path, tmp_path: Path, story_id: str) -> Path:
    """Register a worktree for the story branch, as prepare-story would."""
    worktree = repo / ".current-work" / "worktrees" / f"story-{story_id}"
    result = _git(repo, tmp_path, "worktree", "add", str(worktree), f"story/{story_id}")
    assert result.returncode == 0, result.stderr
    return worktree


def test_successful_merge_green_suite(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path, test_command="true")
    _write_story_file(repo, "ST-777", outputs=["src/foo.py"])
    _commit_story_file(repo, tmp_path, "ST-777")
    _make_story_branch(repo, tmp_path, "ST-777", "src/foo.py", "print('hi')\n")
    worktree = _make_story_worktree(repo, tmp_path, "ST-777")
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-777",
            wave=1,
            status=StoryState.DISPATCHED,
            branch="story/ST-777",
            worktree=str(worktree),
            feature_branch="main",
        ),
    )

    result = _run_dispatch("merge-story", "ST-777", cwd=repo, tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr

    log = _git(repo, tmp_path, "log", "--oneline", "-1").stdout
    assert "merge" in log.lower()

    story_text = (repo / "backlog" / "ST-777.md").read_text()
    assert "status: done" in story_text

    ledger = _load_ledger(repo)
    entry = ledger.stories["ST-777"]
    assert entry.status == StoryState.DONE
    assert entry.commit_sha

    assert not worktree.exists()
    branches = _git(repo, tmp_path, "branch", "--list", "story/ST-777").stdout
    assert branches.strip() == ""


def test_merge_conflict_aborts_marks_blocked(tmp_path: Path) -> None:
    """A dirty working tree that git refuses to overwrite is treated the same
    as a textual merge conflict: `git merge` exits non-zero, dispatch aborts
    the merge and marks the story blocked, and the target branch tip is
    unchanged."""
    repo = _init_repo(tmp_path, test_command="true")
    _write_story_file(repo, "ST-778", outputs=["src/foo.py"])
    _commit_story_file(repo, tmp_path, "ST-778")

    (repo / "src").mkdir()
    (repo / "src" / "foo.py").write_text("base version\n")
    _git(repo, tmp_path, "add", "-A")
    _git(repo, tmp_path, "commit", "--no-verify", "-m", "base touches foo.py")
    main_head = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()

    _make_story_branch(repo, tmp_path, "ST-778", "src/foo.py", "story version\n")

    # Leave an uncommitted, conflicting local edit on main: git will refuse
    # to merge because the merge would overwrite it.
    (repo / "src" / "foo.py").write_text("dirty local edit\n")

    worktree = _make_story_worktree(repo, tmp_path, "ST-778")
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-778",
            wave=1,
            status=StoryState.DISPATCHED,
            branch="story/ST-778",
            worktree=str(worktree),
            feature_branch="main",
        ),
    )

    result = _run_dispatch("merge-story", "ST-778", cwd=repo, tmp_path=tmp_path)

    assert result.returncode != 0

    status = _git(repo, tmp_path, "status", "--porcelain").stdout
    assert "src/foo.py" in status
    head_after = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    assert head_after == main_head

    ledger = _load_ledger(repo)
    entry = ledger.stories["ST-778"]
    assert entry.status == StoryState.BLOCKED
    assert entry.reason == "merge conflict"


def test_red_suite_reverts_marks_blocked(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path, test_command="false")
    _write_story_file(repo, "ST-779", outputs=["src/foo.py"])
    _commit_story_file(repo, tmp_path, "ST-779")
    _make_story_branch(repo, tmp_path, "ST-779", "src/foo.py", "print('hi')\n")
    worktree = _make_story_worktree(repo, tmp_path, "ST-779")
    pre_merge_sha = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-779",
            wave=1,
            status=StoryState.DISPATCHED,
            branch="story/ST-779",
            worktree=str(worktree),
            feature_branch="main",
        ),
    )

    result = _run_dispatch("merge-story", "ST-779", cwd=repo, tmp_path=tmp_path)

    assert result.returncode != 0

    head_after = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    assert head_after == pre_merge_sha

    story_text = (repo / "backlog" / "ST-779.md").read_text()
    assert "status: dispatched" in story_text

    ledger = _load_ledger(repo)
    entry = ledger.stories["ST-779"]
    assert entry.status == StoryState.BLOCKED
    assert entry.reason == "post-merge test failure"


def test_dry_run_reports_without_merging(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path, test_command="true")
    _write_story_file(repo, "ST-780", outputs=["src/foo.py"])
    _commit_story_file(repo, tmp_path, "ST-780")
    _make_story_branch(repo, tmp_path, "ST-780", "src/foo.py", "print('hi')\n")
    worktree = _make_story_worktree(repo, tmp_path, "ST-780")
    pre_merge_sha = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-780",
            wave=1,
            status=StoryState.DISPATCHED,
            branch="story/ST-780",
            worktree=str(worktree),
            feature_branch="main",
        ),
    )

    result = _run_dispatch(
        "merge-story", "ST-780", "--dry-run", cwd=repo, tmp_path=tmp_path
    )

    assert result.returncode == 0, result.stderr

    head_after = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    assert head_after == pre_merge_sha

    story_text = (repo / "backlog" / "ST-780.md").read_text()
    assert "status: dispatched" in story_text

    ledger = _load_ledger(repo)
    entry = ledger.stories["ST-780"]
    assert entry.status == StoryState.DISPATCHED

    assert worktree.exists()
    branches = _git(repo, tmp_path, "branch", "--list", "story/ST-780").stdout
    assert "story/ST-780" in branches


def test_premerge_check_receives_scope_globs(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path, test_command="true")
    _write_story_file(repo, "ST-781", outputs=["src/foo.py", "tests/test_foo.py"])
    _commit_story_file(repo, tmp_path, "ST-781")
    _make_story_branch(repo, tmp_path, "ST-781", "src/foo.py", "print('hi')\n")
    worktree = _make_story_worktree(repo, tmp_path, "ST-781")
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-781",
            wave=1,
            status=StoryState.DISPATCHED,
            branch="story/ST-781",
            worktree=str(worktree),
            feature_branch="main",
        ),
    )

    real_premerge = SCRIPT_DIR / "premerge-check"

    # Invoke premerge-check directly with the same args merge-story would
    # use, to verify the --scope-glob contract independent of dispatch
    # internals already exercised by the other scenarios.
    result = subprocess.run(
        [
            str(real_premerge),
            "main",
            "story/ST-781",
            "--scope-glob",
            "src/foo.py",
            "--scope-glob",
            "tests/test_foo.py",
        ],
        capture_output=True,
        text=True,
        cwd=repo,
        check=False,
        env=_git_env(tmp_path),
    )
    assert result.returncode == 0, result.stderr
    assert "out-of-scope-paths: all" in result.stdout

    # Now drive it through dispatch merge-story --dry-run and confirm the
    # same scope-glob-scoped pass is what gates the merge decision.
    dry_run = _run_dispatch(
        "merge-story", "ST-781", "--dry-run", cwd=repo, tmp_path=tmp_path
    )
    assert dry_run.returncode == 0, dry_run.stderr
    assert "out-of-scope-paths: all" in dry_run.stdout


def test_interrupted_merge_resumes_without_duplicating(tmp_path: Path) -> None:
    """If a prior run created the merge commit but was interrupted before the
    test suite finished, re-running merge-story must detect the existing
    merge commit (via ancestry) rather than merging again, and drive the
    story to completion from there."""
    repo = _init_repo(tmp_path, test_command="true")
    _write_story_file(repo, "ST-782", outputs=["src/foo.py"])
    _commit_story_file(repo, tmp_path, "ST-782")
    _make_story_branch(repo, tmp_path, "ST-782", "src/foo.py", "print('hi')\n")
    worktree = _make_story_worktree(repo, tmp_path, "ST-782")

    # Simulate a merge-story run that got as far as creating (and
    # status-amending) the merge commit, then was interrupted before the
    # test suite ran: the ledger is still "dispatched".
    result = _git(
        repo,
        tmp_path,
        "merge",
        "--no-ff",
        "story/ST-782",
        "-m",
        "merge: story/ST-782 into main",
    )
    assert result.returncode == 0, result.stderr
    story_path = repo / "backlog" / "ST-782.md"
    story_path.write_text(
        story_path.read_text().replace("status: dispatched", "status: done")
    )
    _git(repo, tmp_path, "add", "--", "backlog/ST-782.md")
    _git(repo, tmp_path, "commit", "--amend", "--no-edit")

    commit_count_before = _git(
        repo, tmp_path, "rev-list", "--count", "HEAD"
    ).stdout.strip()

    _write_ledger(
        repo,
        StoryEntry(
            id="ST-782",
            wave=1,
            status=StoryState.DISPATCHED,
            branch="story/ST-782",
            worktree=str(worktree),
            feature_branch="main",
        ),
    )

    result = _run_dispatch("merge-story", "ST-782", cwd=repo, tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr

    commit_count_after = _git(
        repo, tmp_path, "rev-list", "--count", "HEAD"
    ).stdout.strip()
    assert commit_count_after == commit_count_before

    ledger = _load_ledger(repo)
    entry = ledger.stories["ST-782"]
    assert entry.status == StoryState.DONE
    assert entry.commit_sha

    assert not worktree.exists()
    branches = _git(repo, tmp_path, "branch", "--list", "story/ST-782").stdout
    assert branches.strip() == ""
