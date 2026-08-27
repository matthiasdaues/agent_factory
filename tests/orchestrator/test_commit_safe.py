"""Test for factory/scripts/commit-safe (ST-0045).

commit-safe wraps the deterministic two-pass commit: stage, commit, and if a
pre-commit hook rewrote a staged file, re-stage and commit once more. The test
builds a throwaway git repo whose pre-commit hook rewrites a staged file on its
first invocation (mimicking mdformat/ruff), then asserts commit-safe lands the
commit in exactly two passes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_COMMIT_SAFE = _ROOT / "factory" / "scripts" / "commit-safe"

_PRE_COMMIT = """#!/bin/bash
# Rewrite the staged file on the first run only, then abort so git reports
# "files were modified by this hook" — mimicking mdformat/ruff.
if [ ! -f .rewrote ]; then
  echo "reformatted" >> tracked.txt
  touch .rewrote
  echo "files were modified by this hook" >&2
  exit 1
fi
exit 0
"""


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def test_two_pass_lands_commit(tmp_path):
    repo = tmp_path
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "tracked.txt").write_text("original\n", encoding="utf-8")

    hook = repo / ".git" / "hooks" / "pre-commit"
    hook.write_text(_PRE_COMMIT, encoding="utf-8")
    hook.chmod(0o755)

    r = subprocess.run(
        [str(_COMMIT_SAFE), "-m", "test: two-pass", "tracked.txt"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr

    # Exactly one commit landed (two passes, one commit).
    log = (
        subprocess.run(
            ["git", "log", "--oneline"], cwd=repo, capture_output=True, text=True
        )
        .stdout.strip()
        .splitlines()
    )
    assert len(log) == 1

    # The hook's rewrite is part of the committed content.
    show = subprocess.run(
        ["git", "show", "HEAD:tracked.txt"], cwd=repo, capture_output=True, text=True
    ).stdout
    assert "reformatted" in show


def test_missing_message_errors(tmp_path):
    _git(tmp_path, "init", "-q")
    r = subprocess.run(
        [str(_COMMIT_SAFE)], cwd=tmp_path, capture_output=True, text=True
    )
    assert r.returncode == 2
    assert "is required" in r.stderr
