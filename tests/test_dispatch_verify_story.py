"""Integration tests for dispatch verify-story (ST-0120)."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

DISPATCH_SCRIPT = (
    Path(__file__).resolve().parent.parent / "factory" / "scripts" / "dispatch"
)
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "factory" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
dispatch_lib = importlib.import_module("dispatch_lib")

Ledger = dispatch_lib.Ledger
StoryEntry = dispatch_lib.StoryEntry
StoryState = dispatch_lib.StoryState


def _git_env(tmp_path: Path) -> dict[str, str]:
    """Return a git environment isolated from user-level configuration."""
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(tmp_path),
    }


def _run_dispatch(*args: str, cwd: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
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


def _init_repo(tmp_path: Path) -> Path:
    """Create a minimal git repository for verify-story integration tests."""
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

    (repo / "README.md").write_text("initial\n")
    result = _git(repo, tmp_path, "add", "-A")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "--no-verify", "-m", "initial")
    assert result.returncode == 0, result.stderr
    return repo


def _write_ledger(repo: Path, *entries: StoryEntry) -> Path:
    """Persist a dispatch ledger containing the provided entries."""
    ledger = Ledger()
    for entry in entries:
        ledger.stories[entry.id] = entry
    ledger_path = repo / ".agent-factory" / "dispatch-ledger.yaml"
    ledger.save(ledger_path)
    return ledger_path


def _load_ledger(repo: Path) -> Ledger:
    """Load the repository's default dispatch ledger."""
    return Ledger.load(repo / ".agent-factory" / "dispatch-ledger.yaml")


def _commit_on_branch(repo: Path, tmp_path: Path, branch: str, filename: str) -> str:
    """Create *branch* off HEAD, add a commit on it, and return its SHA."""
    result = _git(repo, tmp_path, "checkout", "-b", branch)
    assert result.returncode == 0, result.stderr
    (repo / filename).write_text("content\n")
    result = _git(repo, tmp_path, "add", "-A")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "--no-verify", "-m", f"commit on {branch}")
    assert result.returncode == 0, result.stderr
    sha = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    checkout_main = _git(repo, tmp_path, "checkout", "main")
    assert checkout_main.returncode == 0, checkout_main.stderr
    return sha


def test_verify_valid_sha_on_correct_branch(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    sha = _commit_on_branch(repo, tmp_path, "story/ST-001", "feature.txt")
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", status=StoryState.DISPATCHED, branch="story/ST-001"),
    )

    result = _run_dispatch(
        "verify-story", "ST-001", "--sha", sha, cwd=repo, tmp_path=tmp_path
    )

    assert result.returncode == 0, result.stderr
    ledger = _load_ledger(repo)
    entry = ledger.stories["ST-001"]
    assert entry.verify_base == "pass"
    assert entry.commit_sha == sha


def test_verify_nonexistent_sha_rejected(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", status=StoryState.DISPATCHED, branch="story/ST-001"),
    )
    fake_sha = "a" * 40

    result = _run_dispatch(
        "verify-story", "ST-001", "--sha", fake_sha, cwd=repo, tmp_path=tmp_path
    )

    assert result.returncode == 1
    assert "does not exist" in result.stderr
    ledger = _load_ledger(repo)
    assert ledger.stories["ST-001"].verify_base is None


def test_verify_sha_on_wrong_branch_rejected(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    sha = _commit_on_branch(repo, tmp_path, "story/ST-002", "other.txt")
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", status=StoryState.DISPATCHED, branch="story/ST-001"),
    )

    result = _run_dispatch(
        "verify-story", "ST-001", "--sha", sha, cwd=repo, tmp_path=tmp_path
    )

    assert result.returncode == 1
    assert "not on branch" in result.stderr
    ledger = _load_ledger(repo)
    assert ledger.stories["ST-001"].verify_base is None


def test_verify_leaves_index_unchanged(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    sha = _commit_on_branch(repo, tmp_path, "story/ST-001", "feature.txt")
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", status=StoryState.DISPATCHED, branch="story/ST-001"),
    )
    before_status = _git(repo, tmp_path, "status", "--porcelain").stdout
    before_index = _git(repo, tmp_path, "ls-files", "--stage").stdout

    result = _run_dispatch(
        "verify-story", "ST-001", "--sha", sha, cwd=repo, tmp_path=tmp_path
    )

    assert result.returncode == 0, result.stderr
    after_index = _git(repo, tmp_path, "ls-files", "--stage").stdout
    # The ledger file itself changes on disk; the tracked git index of the
    # source repository (excluding the untracked ledger file) is unaffected.
    assert after_index == before_index
    after_status_excluding_ledger = [
        line
        for line in _git(repo, tmp_path, "status", "--porcelain").stdout.splitlines()
        if "dispatch-ledger.yaml" not in line
    ]
    before_status_lines = [
        line for line in before_status.splitlines() if "dispatch-ledger.yaml" not in line
    ]
    assert after_status_excluding_ledger == before_status_lines


def test_verify_leaves_working_tree_unchanged(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    sha = _commit_on_branch(repo, tmp_path, "story/ST-001", "feature.txt")
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", status=StoryState.DISPATCHED, branch="story/ST-001"),
    )
    current_branch_before = _git(repo, tmp_path, "rev-parse", "--abbrev-ref", "HEAD").stdout
    head_before = _git(repo, tmp_path, "rev-parse", "HEAD").stdout
    readme_before = (repo / "README.md").read_text()

    result = _run_dispatch(
        "verify-story", "ST-001", "--sha", sha, cwd=repo, tmp_path=tmp_path
    )

    assert result.returncode == 0, result.stderr
    current_branch_after = _git(repo, tmp_path, "rev-parse", "--abbrev-ref", "HEAD").stdout
    head_after = _git(repo, tmp_path, "rev-parse", "HEAD").stdout
    readme_after = (repo / "README.md").read_text()

    assert current_branch_after == current_branch_before
    assert head_after == head_before
    assert readme_after == readme_before
    assert not (repo / "feature.txt").exists()
