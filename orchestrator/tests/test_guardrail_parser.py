"""Tests for the shared git-guardrail command parser (ST-0046, ST-0056).

Drives `factory/config/hooks/block-dangerous-git.sh` directly — JSON on stdin,
exit code 2 = deny — proving supported CLI payloads share one policy without
weakening compound-line merge parsing or git-context-scoped `--no-verify`.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_HOOK = _ROOT / "factory" / "config" / "hooks" / "block-dangerous-git.sh"


def _payload(cli: str, command: str) -> dict:
    if cli == "claude":
        return {"tool_name": "Bash", "tool_input": {"command": command}}
    if cli == "copilot":
        return {"toolName": "bash", "toolArgs": {"command": command}}
    if cli == "codex":
        return {
            "session_id": "test-session",
            "turn_id": "test-turn",
            "cwd": str(_ROOT),
            "hook_event_name": "PreToolUse",
            "permission_mode": "default",
            "tool_name": "Bash",
            "tool_input": {"cmd": command},
            "tool_use_id": "test-tool-use",
        }
    raise ValueError(f"unsupported CLI fixture: {cli}")


def _run(command: str, cli: str = "claude") -> subprocess.CompletedProcess:
    payload = json.dumps(_payload(cli, command))
    return subprocess.run(
        [str(_HOOK)], input=payload, capture_output=True, text=True, check=False
    )


@pytest.mark.parametrize("cli", ["claude", "copilot", "codex"])
def test_supported_cli_payload_allows_safe_command(cli):
    result = _run("git status", cli)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("cli", ["claude", "copilot", "codex"])
def test_supported_cli_payload_denies_dangerous_command(cli):
    result = _run("git push origin main", cli)
    assert result.returncode == 2
    assert "BLOCKED" in result.stderr


def test_codex_denial_has_supported_outcome_and_compatible_copilot_json():
    result = _run("git reset --hard HEAD", "codex")

    assert result.returncode == 2
    assert "git reset --hard HEAD" in result.stderr
    assert json.loads(result.stdout) == {
        "permissionDecision": "deny",
        "permissionDecisionReason": result.stderr.strip(),
    }


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


class TestBranchRequiresWorktree:
    @pytest.mark.parametrize(
        "command",
        [
            "git branch feat/x",
            "git branch feat/x main",
            "git branch --track feat/x origin/main",
            "git branch feat/x && git status",
            "git switch -c feat/x",
            "git switch -C feat/x main",
            "git checkout -b feat/x",
            "git checkout -B feat/x main",
        ],
    )
    def test_standalone_branch_creation_is_blocked(self, command):
        result = _run(command)
        assert result.returncode == 2
        assert "git worktree add -b" in result.stderr

    @pytest.mark.parametrize(
        "command",
        [
            "git worktree add -b feat/x /tmp/feat-x main",
            "git branch --list",
            "git branch -d merged-branch",
            "git branch -m old-name new-name",
            "git switch existing-branch",
            "git checkout existing-branch",
        ],
    )
    def test_noncreating_branch_operations_remain_allowed(self, command):
        result = _run(command)
        assert result.returncode == 0, result.stderr
