"""Integration tests for dispatch prepare-wave (Layer 3b)."""

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


def _init_repo(tmp_path: Path) -> Path:
    """Create a minimal git repository for prepare-wave integration tests."""
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
        json.dumps({"project_name": "test", "test_command": "echo ok"})
    )

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
    ledger_path = repo / ".current-work" / "dispatch-ledger.yaml"
    ledger.save(ledger_path)
    return ledger_path


def _load_ledger(repo: Path) -> Ledger:
    """Load the repository's default dispatch ledger."""
    return Ledger.load(repo / ".current-work" / "dispatch-ledger.yaml")


def _worktree_path(repo: Path, story_id: str) -> Path:
    """Return the expected worktree path for one story branch."""
    return repo / ".current-work" / "worktrees" / f"story-{story_id}"


def test_prepare_wave_blocks_when_prior_wave_not_terminal(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING),
        StoryEntry(id="ST-002", wave=2, status=StoryState.PENDING),
    )

    result = _run_dispatch("prepare-wave", "2", cwd=repo, tmp_path=tmp_path)

    assert result.returncode == 1
    assert "ST-001 (pending)" in result.stderr


def test_prepare_wave_creates_branch_and_worktree_and_leaves_chain_link_pending(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    head_sha = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING),
        StoryEntry(
            id="ST-002",
            wave=1,
            status=StoryState.PENDING,
            deps=["ST-001"],
        ),
    )

    result = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr

    branch_sha = _git(repo, tmp_path, "rev-parse", "story/ST-001").stdout.strip()
    assert branch_sha == head_sha

    worktree = _worktree_path(repo, "ST-001")
    assert worktree.exists()
    porcelain = _git(repo, tmp_path, "worktree", "list", "--porcelain").stdout
    assert f"worktree {worktree.resolve()}" in porcelain
    assert (worktree / ".current-work" / "verify-base-ok").exists()

    ledger = _load_ledger(repo)
    prepared = ledger.stories["ST-001"]
    assert prepared.status == StoryState.PREPARED
    assert prepared.branch == "story/ST-001"
    assert prepared.worktree == str(worktree)
    assert prepared.base_sha == head_sha

    chain_link = ledger.stories["ST-002"]
    assert chain_link.status == StoryState.PENDING
    assert chain_link.branch is None
    assert chain_link.worktree is None


def test_prepare_wave_is_idempotent_after_success(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_ledger(repo, StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING))

    first = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)
    assert first.returncode == 0, first.stderr
    before = (repo / ".current-work" / "dispatch-ledger.yaml").read_text()

    second = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)

    assert second.returncode == 0, second.stderr
    after = (repo / ".current-work" / "dispatch-ledger.yaml").read_text()
    assert after == before

    worktree = _worktree_path(repo, "ST-001")
    porcelain = _git(repo, tmp_path, "worktree", "list", "--porcelain").stdout
    assert porcelain.count(f"worktree {worktree.resolve()}") == 1


def test_prepare_wave_resumes_after_partial_failure(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING),
        StoryEntry(id="ST-002", wave=1, status=StoryState.PENDING),
    )
    conflict = _git(repo, tmp_path, "branch", "story/ST-002", "HEAD")
    assert conflict.returncode == 0, conflict.stderr

    first = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)

    assert first.returncode == 1
    assert "story/ST-002" in first.stderr
    ledger = _load_ledger(repo)
    assert ledger.stories["ST-001"].status == StoryState.PREPARED
    assert ledger.stories["ST-002"].status == StoryState.PENDING

    delete_branch = _git(repo, tmp_path, "branch", "-D", "story/ST-002")
    assert delete_branch.returncode == 0, delete_branch.stderr

    second = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)

    assert second.returncode == 0, second.stderr
    resumed = _load_ledger(repo)
    assert resumed.stories["ST-001"].status == StoryState.PREPARED
    assert resumed.stories["ST-002"].status == StoryState.PREPARED

    first_worktree = _worktree_path(repo, "ST-001")
    second_worktree = _worktree_path(repo, "ST-002")
    porcelain = _git(repo, tmp_path, "worktree", "list", "--porcelain").stdout
    assert porcelain.count(f"worktree {first_worktree.resolve()}") == 1
    assert porcelain.count(f"worktree {second_worktree.resolve()}") == 1


def test_prepare_story_after_predecessor_done(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    merge_sha = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-005",
            wave=1,
            status=StoryState.DONE,
            commit_sha=merge_sha,
        ),
        StoryEntry(
            id="ST-006",
            wave=1,
            status=StoryState.PENDING,
            deps=["ST-005"],
        ),
    )

    result = _run_dispatch("prepare-story", "ST-006", cwd=repo, tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr

    branch_sha = _git(repo, tmp_path, "rev-parse", "story/ST-006").stdout.strip()
    assert branch_sha == merge_sha

    worktree = _worktree_path(repo, "ST-006")
    assert worktree.exists()
    porcelain = _git(repo, tmp_path, "worktree", "list", "--porcelain").stdout
    assert f"worktree {worktree.resolve()}" in porcelain
    assert (worktree / ".current-work" / "verify-base-ok").exists()

    ledger = _load_ledger(repo)
    prepared = ledger.stories["ST-006"]
    assert prepared.status == StoryState.PREPARED
    assert prepared.branch == "story/ST-006"
    assert prepared.worktree == str(worktree)
    assert prepared.base_sha == merge_sha


def test_prepare_story_predecessor_not_done_blocked(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    head_sha = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-005",
            wave=1,
            status=StoryState.DISPATCHED,
            commit_sha=head_sha,
        ),
        StoryEntry(
            id="ST-006",
            wave=1,
            status=StoryState.PENDING,
            deps=["ST-005"],
        ),
    )

    result = _run_dispatch("prepare-story", "ST-006", cwd=repo, tmp_path=tmp_path)

    assert result.returncode != 0
    assert "ST-005" in result.stderr

    ledger = _load_ledger(repo)
    assert ledger.stories["ST-006"].status == StoryState.PENDING


def test_prepare_story_idempotent(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    merge_sha = _git(repo, tmp_path, "rev-parse", "HEAD").stdout.strip()
    _write_ledger(
        repo,
        StoryEntry(
            id="ST-005",
            wave=1,
            status=StoryState.DONE,
            commit_sha=merge_sha,
        ),
        StoryEntry(
            id="ST-006",
            wave=1,
            status=StoryState.PENDING,
            deps=["ST-005"],
        ),
    )

    first = _run_dispatch("prepare-story", "ST-006", cwd=repo, tmp_path=tmp_path)
    assert first.returncode == 0, first.stderr
    before = (repo / ".current-work" / "dispatch-ledger.yaml").read_text()

    second = _run_dispatch("prepare-story", "ST-006", cwd=repo, tmp_path=tmp_path)

    assert second.returncode == 0, second.stderr
    after = (repo / ".current-work" / "dispatch-ledger.yaml").read_text()
    assert after == before

    worktree = _worktree_path(repo, "ST-006")
    porcelain = _git(repo, tmp_path, "worktree", "list", "--porcelain").stdout
    assert porcelain.count(f"worktree {worktree.resolve()}") == 1
