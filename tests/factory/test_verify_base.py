"""Contract tests for verify-base gate script."""

from __future__ import annotations

import subprocess

import pytest
from conftest import load_script

vb = load_script("verify-base")


@pytest.fixture()
def git_repo(tmp_path):
    """Bare git repo with one commit on main."""
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "--allow-empty", "-m", "init"],
        check=True,
        capture_output=True,
    )
    return tmp_path


class TestCheckNotBehindTarget:
    def test_head_on_target_returns_ok(self, git_repo, monkeypatch):
        monkeypatch.chdir(git_repo)
        ok, msg = vb.check_not_behind_target("HEAD")
        assert ok
        assert "BASE_OK" in msg

    def test_unknown_ref_returns_error(self, git_repo, monkeypatch):
        monkeypatch.chdir(git_repo)
        ok, msg = vb.check_not_behind_target("nonexistent-branch")
        assert not ok
        assert "BASE_ERROR" in msg or "BASE_STALE" in msg


class TestCheckDeclaredBase:
    def test_head_matches_declared_base(self, git_repo, monkeypatch):
        monkeypatch.chdir(git_repo)
        sha = subprocess.run(
            ["git", "-C", str(git_repo), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        ok, msg = vb.check_declared_base(sha)
        assert ok
        assert "BASE_OK" in msg


class TestMainEntrypoint:
    def test_exits_2_outside_git_repo(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = vb.main(["some-target"])
        assert rc == 2

    def test_exits_2_with_invalid_expect_base(self, git_repo, monkeypatch):
        monkeypatch.chdir(git_repo)
        rc = vb.main(["HEAD", "--expect-base", "not-a-sha"])
        assert rc == 2

    def test_exits_0_when_on_target(self, git_repo, monkeypatch):
        monkeypatch.chdir(git_repo)
        rc = vb.main(["HEAD"])
        assert rc == 0
        marker = git_repo / ".current-work" / "verify-base-ok"
        assert marker.exists()
