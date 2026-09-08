"""Contract tests for block-dangerous-git.sh hook — dispatch-ledger gate.

The hook denies `git commit` on story/* branches when no dispatch ledger
exists in the main checkout. Non-story branches and story branches with
a ledger present are unaffected.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_SOURCE = REPO_ROOT / "packages" / "factory" / "config" / "hooks" / "block-dangerous-git.sh"
_INSTALLED = REPO_ROOT / "factory" / "config" / "hooks" / "block-dangerous-git.sh"
HOOK_PATH = _SOURCE if _SOURCE.exists() else _INSTALLED


def _run_hook(command: str, cwd: str | Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_input": {"command": command}})
    run_env = {k: v for k, v in os.environ.items()}
    run_env.pop("GIT_DIR", None)
    run_env.pop("GIT_WORK_TREE", None)
    run_env.pop("GIT_INDEX_FILE", None)
    if env:
        run_env.update(env)
    return subprocess.run(
        ["bash", str(HOOK_PATH)],
        input=payload,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=run_env,
    )


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@test"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], capture_output=True, check=True)
    (path / "README.md").write_text("init\n")
    subprocess.run(["git", "-C", str(path), "add", "."], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "init", "--no-verify"], capture_output=True, check=True)


def _create_worktree(main: Path, branch: str, wt_path: Path) -> None:
    subprocess.run(
        ["git", "-C", str(main), "worktree", "add", "-b", branch, str(wt_path), "HEAD"],
        capture_output=True,
        check=True,
    )


def _place_verify_base_marker(wt_path: Path) -> None:
    marker_dir = wt_path / ".current-work"
    marker_dir.mkdir(parents=True, exist_ok=True)
    head_sha = subprocess.run(
        ["git", "-C", str(wt_path), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    (marker_dir / "verify-base-ok").write_text(f"head={head_sha}\n")


def _place_ledger(main: Path, feature_name: str = "feature-test") -> Path:
    ledger_dir = main / ".current-work" / feature_name
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = ledger_dir / "dispatch-ledger.yaml"
    ledger.write_text("---\nstories: {}\n")
    return ledger


class TestLedgerGateOnStoryBranch:
    """Commits on story/* branches require a dispatch ledger in the main checkout."""

    def test_story_branch_without_ledger_is_denied(self, tmp_path):
        main = tmp_path / "main"
        wt = tmp_path / "wt"
        _init_repo(main)
        _create_worktree(main, "story/ST-9999", wt)
        _place_verify_base_marker(wt)

        result = _run_hook("git commit -m test", cwd=wt)
        assert result.returncode == 2
        assert "dispatch ledger" in result.stderr.lower() or "dispatch" in result.stderr.lower()

    def test_story_branch_with_ledger_is_allowed(self, tmp_path):
        main = tmp_path / "main"
        wt = tmp_path / "wt"
        _init_repo(main)
        _create_worktree(main, "story/ST-9999", wt)
        _place_verify_base_marker(wt)
        _place_ledger(main)

        result = _run_hook("git commit -m test", cwd=wt)
        assert result.returncode == 0

    def test_non_story_branch_without_ledger_is_allowed(self, tmp_path):
        main = tmp_path / "main"
        wt = tmp_path / "wt"
        _init_repo(main)
        _create_worktree(main, "feature/something", wt)
        _place_verify_base_marker(wt)

        result = _run_hook("git commit -m test", cwd=wt)
        assert result.returncode == 0

    def test_denial_message_suggests_dispatch_init(self, tmp_path):
        main = tmp_path / "main"
        wt = tmp_path / "wt"
        _init_repo(main)
        _create_worktree(main, "story/ST-0001", wt)
        _place_verify_base_marker(wt)

        result = _run_hook("git commit -m test", cwd=wt)
        assert result.returncode == 2
        assert "dispatch init" in result.stderr


class TestLedgerGateDoesNotAffectMainCheckout:
    """Commits in the main checkout (not a worktree) skip the ledger check."""

    def test_commit_in_main_checkout_without_ledger_passes(self, tmp_path):
        main = tmp_path / "main"
        _init_repo(main)
        subprocess.run(
            ["git", "-C", str(main), "checkout", "-b", "story/ST-0002"],
            capture_output=True, check=True,
        )

        result = _run_hook("git commit -m test", cwd=main)
        assert result.returncode == 0
