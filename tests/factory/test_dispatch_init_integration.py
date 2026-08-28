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

DISPATCH_SCRIPT = (
    Path(__file__).resolve().parent.parent.parent / "factory" / "scripts" / "dispatch"
)


def _git_env(tmp_path: Path) -> dict[str, str]:
    """Environment that disables global hooks and config for test repos."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", HOME=str(tmp_path))
    return env


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

        ledger_files = list((repo / ".current-work").rglob("dispatch-ledger.yaml"))
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
            "--base",
            "main",
            "--feature-branch",
            "feature/my-work",
            "--stories",
            "ST-001",
            cwd=repo,
        )
        assert result.returncode == 0, result.stderr
        ledger = repo / ".current-work" / "feature/my-work" / "dispatch-ledger.yaml"
        assert ledger.exists()

    def test_nonexistent_branch_rejected(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        result = _run_dispatch(
            "init",
            "--base",
            "main",
            "--feature-branch",
            "feature/missing",
            "--stories",
            "ST-001",
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
            "--base",
            "main",
            "--feature-branch",
            "feature/orphan",
            "--stories",
            "ST-001",
            cwd=repo,
        )
        assert result.returncode == 1
        assert "not reachable" in result.stderr


class TestDispatchInitMutualExclusion:
    def test_baseline_and_feature_branch_rejected(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        result = _run_dispatch(
            "init",
            "--base",
            "main",
            "--feature-branch",
            "feature/x",
            "--baseline-commit",
            "--stories",
            "ST-001",
            cwd=repo,
        )
        assert result.returncode == 1
        assert "mutually exclusive" in result.stderr


def _add_backlog_story(
    repo: Path,
    story_id: str,
    *,
    tier: str,
    risk_domains: list[str] | None = None,
    outputs: list[str] | None = None,
    deps: list[str] | None = None,
    tests: list[str] | None = None,
) -> None:
    """Write and commit a minimal backlog story file with the given frontmatter."""
    backlog_dir = repo / "backlog"
    backlog_dir.mkdir(exist_ok=True)
    lines = ["---", f"id: {story_id}", f"tier: {tier}", "status: pending"]
    if risk_domains:
        lines.append("risk_domains:")
        lines.extend(f"  - {d}" for d in risk_domains)
    if outputs:
        lines.append("outputs:")
        lines.extend(f"  - {o}" for o in outputs)
    if deps:
        lines.append("deps:")
        lines.extend(f"  - {d}" for d in deps)
    if tests:
        lines.append("tests:")
        lines.extend(f"  - {t}" for t in tests)
    lines.append("---")
    lines.append(f"# {story_id}")
    (backlog_dir / f"{story_id}.md").write_text("\n".join(lines) + "\n")

    env = _git_env(repo.parent)
    subprocess.run(
        ["git", "add", "-A"], cwd=repo, capture_output=True, check=True, env=env
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", f"add {story_id}"],
        cwd=repo,
        capture_output=True,
        check=True,
        env=env,
    )


class TestDispatchInitTierMismatch:
    def test_strong_suggestion_lower_declared_blocks_init(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        _add_backlog_story(
            repo,
            "ST-100",
            tier="economy",
            risk_domains=["security"],
            outputs=["src/a.py"],
        )
        result = _run_dispatch(
            "init", "--base", "main", "--stories", "ST-100", cwd=repo
        )
        assert result.returncode == 1
        assert "ST-100" in result.stderr
        assert "strong" in result.stderr

    def test_nonblocking_mismatch_warns_but_proceeds(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        _add_backlog_story(
            repo,
            "ST-101",
            tier="standard",
            outputs=["src/a.py"],
            tests=["tests/test_a.py"],
        )
        result = _run_dispatch(
            "init", "--base", "main", "--stories", "ST-101", cwd=repo
        )
        assert result.returncode == 0, result.stderr
        assert "ST-101" in result.stderr
        assert "economy" in result.stderr
