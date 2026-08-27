"""Tests for the guardrail's worktree verify-base enforcement (ST-0047).

The worktree-commit check in block-dangerous-git.sh must not merely test that a
`.agent-factory/verify-base-ok` marker exists — the marker's verified base
(`head=`) must be an ancestor of the worktree's current HEAD. A stale or
mismatched marker no longer authorizes a commit; a HEAD advanced by TDD still
does. Each test builds a real linked worktree and drives the hook against a
`git commit` command, asserting the exit code (2 = deny).
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HOOK = _ROOT / "factory" / "config" / "hooks" / "block-dangerous-git.sh"


def _clean_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
        env=_clean_env(),
    )


def _hook(cwd: Path) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_input": {"command": "git commit -m x"}})
    return subprocess.run(
        [str(_HOOK)],
        input=payload,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=_clean_env(),
    )


def _setup_worktree(tmp_path: Path) -> tuple[Path, Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "f.txt").write_text("1\n", encoding="utf-8")
    _git(repo, "add", "f.txt")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    wt = tmp_path / "wt"
    _git(repo, "worktree", "add", "-q", str(wt), "-b", "feat")
    return repo, wt, base


def _write_marker(wt: Path, head: str) -> None:
    d = wt / ".agent-factory"
    d.mkdir(exist_ok=True)
    (d / "verify-base-ok").write_text(
        f"target=main\nexpect_base=\nhead={head}\n", encoding="utf-8"
    )


def test_no_marker_blocks(tmp_path):
    _, wt, _ = _setup_worktree(tmp_path)
    assert _hook(wt).returncode == 2


def test_marker_matching_base_allows(tmp_path):
    _, wt, base = _setup_worktree(tmp_path)
    _write_marker(wt, base)
    r = _hook(wt)
    assert r.returncode == 0, r.stderr


def test_marker_unrelated_head_blocks(tmp_path):
    # A marker whose head is not in the worktree history (stale / reused path).
    _, wt, _ = _setup_worktree(tmp_path)
    _write_marker(wt, "0" * 40)
    assert _hook(wt).returncode == 2


def test_advanced_head_still_allows(tmp_path):
    # TDD: HEAD advances past the verified base; the commit must still pass.
    _, wt, base = _setup_worktree(tmp_path)
    _write_marker(wt, base)
    (wt / "g.txt").write_text("2\n", encoding="utf-8")
    _git(wt, "add", "g.txt")
    _git(wt, "commit", "-q", "-m", "work")
    r = _hook(wt)
    assert r.returncode == 0, r.stderr
