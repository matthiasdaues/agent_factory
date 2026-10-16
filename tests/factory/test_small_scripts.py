"""Regression tests for the small install, commit, and merge-config faults (ST-0307)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script


def _clean_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True, text=True, env=_clean_env(),
    ).stdout


# --- BUG-0080: commit-safe commits only what was staged ----------------------

# A hook that rewrites a staged file and fails, the way mdformat or ruff do.
REWRITING_HOOK = """#!/bin/sh
if grep -q raw staged.txt; then
  sed -i 's/raw/fixed/' staged.txt
  exit 1
fi
exit 0
"""


def _repo_with_rewriting_hook(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "staged.txt").write_text("start\n")
    (repo / "wip.txt").write_text("start\n")
    _git(repo, "add", "staged.txt", "wip.txt")
    _git(repo, "commit", "-q", "-m", "initial")
    hook = repo / ".git" / "hooks" / "pre-commit"
    hook.write_text(REWRITING_HOOK)
    hook.chmod(0o755)
    return repo


def _commit_safe(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(SOURCE_SCRIPTS_DIR / "commit-safe"), *args],
        cwd=repo, capture_output=True, text=True, env=_clean_env(), check=False,
    )


def test_bug_0080_second_pass_leaves_unstaged_work_out_of_the_commit(tmp_path):
    repo = _repo_with_rewriting_hook(tmp_path)
    (repo / "staged.txt").write_text("raw\n")
    (repo / "wip.txt").write_text("work in progress\n")

    result = _commit_safe(repo, "-m", "fix: change staged (BUG-0080)", "staged.txt")

    assert result.returncode == 0, result.stderr
    assert _git(repo, "show", "--name-only", "--format=", "HEAD").split() == [
        "staged.txt"
    ]
    assert _git(repo, "show", "HEAD:staged.txt") == "fixed\n"
    assert _git(repo, "status", "--porcelain").splitlines() == [" M wip.txt"]


def test_bug_0080_message_flag_without_value_explains_itself(tmp_path):
    repo = _repo_with_rewriting_hook(tmp_path)

    result = _commit_safe(repo, "-m")

    assert result.returncode == 2
    assert "-m <message> is required" in result.stderr


# --- BUG-0081: merge-precommit-config adds no duplicate hooks ----------------

FACTORY_TEMPLATE = (
    REPO_ROOT / "packages/factory/config/pre-commit-config.yaml"
).read_text(encoding="utf-8")

PROJECT_WITH_OWN_MDFORMAT = """\
repos:
  - repo: local
    hooks:
      - id: mdformat
        name: mdformat
        entry: mdformat --wrap 80
        language: system
        types: [markdown]
"""


def test_bug_0081_repeated_merges_and_update_keep_one_copy_of_each_hook():
    mpc = load_script("merge-precommit-config")

    text = mpc.merge(PROJECT_WITH_OWN_MDFORMAT, FACTORY_TEMPLATE)
    again = mpc.merge(text, FACTORY_TEMPLATE)
    text = again if again is not None else text
    text = mpc.merge(text, FACTORY_TEMPLATE, update=True)

    assert again is None
    assert text.count("id: agent_factory_hook-link-check") == 1
    assert "id: agent_factory_hook-mdformat" not in text
    assert text.count("id: mdformat\n") == 1
