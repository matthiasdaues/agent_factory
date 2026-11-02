"""The test session never inherits the git variables of a commit hook.

A hook in a linked worktree sees GIT_DIR and GIT_INDEX_FILE. If a fixture of
module, class, or session scope ran `git init` with them, git would write
core.bare = true into the shared repository config. The conftest clears every
GIT_* variable at import, before any fixture runs.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Captured when pytest imports this module, which happens after conftest.py
# and before any fixture of any scope.
GIT_VARS_AT_IMPORT = sorted(k for k in os.environ if k.startswith("GIT_"))

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_no_git_variable_is_visible_at_module_import() -> None:
    assert GIT_VARS_AT_IMPORT == []


def test_a_session_started_with_hook_variables_sees_none(tmp_path: Path) -> None:
    env = dict(os.environ)
    env["GIT_DIR"] = str(tmp_path / "worktree-gitdir")
    env["GIT_INDEX_FILE"] = str(tmp_path / "worktree-gitdir" / "index")
    target = f"{Path(__file__).resolve()}::test_no_git_variable_is_visible_at_module_import"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
