"""Integration tests for dispatch init (Layer 3a).

Each test creates a temporary git repository, runs dispatch init as a
subprocess, and asserts on filesystem and git state.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

DISPATCH_SCRIPT = (
    Path(__file__).resolve().parent.parent / "factory" / "scripts" / "dispatch"
)


def _git_env(tmp_path: Path) -> dict[str, str]:
    """Environment that disables global hooks and config for test repos."""
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(tmp_path),
    }


def _run_dispatch(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DISPATCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )


def _init_repo(tmp_path: Path, with_test_command: bool = True) -> Path:
    """Create a minimal git repo with config/project.json."""
    repo = tmp_path / "repo"
    repo.mkdir()
    env = _git_env(tmp_path)
    subprocess.run(
        ["git", "init", "--initial-branch=main"],
        cwd=repo,
        capture_output=True,
        check=True,
        env=env,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo,
        capture_output=True,
        check=True,
        env=env,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo,
        capture_output=True,
        check=True,
        env=env,
    )
    subprocess.run(
        ["git", "config", "core.hooksPath", "/dev/null"],
        cwd=repo,
        capture_output=True,
        check=True,
        env=env,
    )

    config_dir = repo / "config"
    config_dir.mkdir()
    config_data: dict = {"project_name": "test"}
    if with_test_command:
        config_data["test_command"] = "echo ok"
    (config_dir / "project.json").write_text(json.dumps(config_data))

    subprocess.run(
        ["git", "add", "-A"], cwd=repo, capture_output=True, check=True, env=env
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "initial"],
        cwd=repo,
        capture_output=True,
        check=True,
        env=env,
    )
    return repo


class TestDispatchInitAtomicCreation:
    def test_creates_branch_worktree_and_ledger(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        result = _run_dispatch(
            "init", "--base", "main", "--stories", "ST-001,ST-002", cwd=repo
        )
        assert result.returncode == 0, result.stderr

        ledger_files = list((repo / ".current_work").rglob("dispatch-ledger.yaml"))
        assert len(ledger_files) == 1

        content = ledger_files[0].read_text()
        assert "ST-001" in content
        assert "ST-002" in content
        assert "pending" in content

    def test_idempotent_rerun(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        _run_dispatch("init", "--base", "main", "--stories", "ST-001", cwd=repo)
        result = _run_dispatch(
            "init", "--base", "main", "--stories", "ST-001", cwd=repo
        )
        assert result.returncode == 0
        assert "no-op" in result.stdout


class TestDispatchInitMissingTestCommand:
    def test_exits_nonzero_without_test_command(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path, with_test_command=False)
        result = _run_dispatch(
            "init", "--base", "main", "--stories", "ST-001", cwd=repo
        )
        assert result.returncode == 1
        assert "test_command" in result.stderr


class TestDispatchInitFeatureBranch:
    def test_adopts_existing_branch(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        env = _git_env(tmp_path)
        subprocess.run(
            ["git", "branch", "feature/my-work"],
            cwd=repo,
            capture_output=True,
            check=True,
            env=env,
        )
        result = _run_dispatch(
            "init",
            "--base", "main",
            "--feature-branch", "feature/my-work",
            "--stories", "ST-001",
            cwd=repo,
        )
        assert result.returncode == 0, result.stderr
        ledger = repo / ".current_work" / "feature/my-work" / "dispatch-ledger.yaml"
        assert ledger.exists()

    def test_nonexistent_branch_rejected(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        result = _run_dispatch(
            "init",
            "--base", "main",
            "--feature-branch", "feature/missing",
            "--stories", "ST-001",
            cwd=repo,
        )
        assert result.returncode == 1
        assert "does not exist" in result.stderr

    def test_unreachable_branch_rejected(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        env = _git_env(tmp_path)
        subprocess.run(
            ["git", "checkout", "--orphan", "feature/orphan"],
            cwd=repo,
            capture_output=True,
            check=True,
            env=env,
        )
        subprocess.run(
            ["git", "commit", "--no-verify", "--allow-empty", "-m", "orphan"],
            cwd=repo,
            capture_output=True,
            check=True,
            env=env,
        )
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=repo,
            capture_output=True,
            check=True,
            env=env,
        )
        result = _run_dispatch(
            "init",
            "--base", "main",
            "--feature-branch", "feature/orphan",
            "--stories", "ST-001",
            cwd=repo,
        )
        assert result.returncode == 1
        assert "not reachable" in result.stderr


class TestDispatchInitMutualExclusion:
    def test_baseline_and_feature_branch_rejected(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        result = _run_dispatch(
            "init",
            "--base", "main",
            "--feature-branch", "feature/x",
            "--baseline-commit",
            "--stories", "ST-001",
            cwd=repo,
        )
        assert result.returncode == 1
        assert "mutually exclusive" in result.stderr
