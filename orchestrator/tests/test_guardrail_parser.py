"""Tests for the git-guardrail command parser (ST-0046).

Drives `factory/config/hooks/block-dangerous-git.sh` directly — JSON on stdin,
exit code 2 = deny — proving two parser fixes without weakening real blocking:
compound-line merge-branch isolation, and git-context-scoped `--no-verify`.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HOOK = _ROOT / "factory" / "config" / "hooks" / "block-dangerous-git.sh"


def _run(command: str) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_input": {"command": command}})
    return subprocess.run([str(_HOOK)], input=payload, capture_output=True, text=True)


class TestMergeBranchParse:
    def test_multiline_compound_resolves_real_branch_not_cd(self):
        # The retro scenario: a two-line bash block (cd, then git merge). The
        # merge line is detected; the reason must name the real branch, not the
        # cd from the previous line — proving the segment was isolated first.
        r = _run("cd /tmp/repo\ngit merge feat/y --no-ff -m msg")
        assert r.returncode == 2
        assert "feat/y" in r.stderr
        assert "merge cd" not in r.stderr


class TestNoVerifyScoping:
    def test_non_git_no_verify_allowed(self):
        r = _run("grep -rIl --no-verify foo factory")
        assert r.returncode == 0, r.stderr

    def test_git_commit_no_verify_blocked(self):
        r = _run("git commit -m x --no-verify")
        assert r.returncode == 2
        assert "BLOCKED" in r.stderr

    def test_git_commit_n_shorthand_blocked(self):
        r = _run("git commit -m x -n")
        assert r.returncode == 2


class TestControls:
    def test_git_status_allowed(self):
        r = _run("git status")
        assert r.returncode == 0, r.stderr

    def test_real_dangerous_still_blocked(self):
        r = _run("git push --force origin main")
        assert r.returncode == 2
