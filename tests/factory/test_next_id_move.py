"""Tests for next-id --move-to-origin (ST-0380, counter-ids-fitting.feature).

The move carries the claim commit C of the local counter to `origin` in the
four steps of BR-102. Every remote is a local bare repository in tmp_path.
The made-up URL `https://user:token@host/demo.git` reaches the bare repository
through `url.<bare path>.insteadOf` in the project's own config, so git talks
to the bare repository and next-id sees the made-up URL (QA strategy, Test
setup). Every failing path checks that no token shows.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from test_next_id import (  # noqa: F401
    FIXTURE_IDENTITY,
    REF,
    _bare,
    _counter,
    _git,
    _project,
    _set_counter,
    env,
    ni,
    run,
)
from test_next_id_redaction import _assert_no_token

SETTING = "agent-factory.counterRemote"
ORIGIN_URL = "https://user:token@host/demo.git"
SHOWN_URL = "https://***@host/demo.git"

READ_ONLY_HOOK = """#!/bin/sh
echo read-only >&2
exit 1
"""


# --- helpers ------------------------------------------------------------------


def _assert_refused(result: subprocess.CompletedProcess) -> None:
    assert result.returncode != 0, result.stdout
    assert result.stdout == ""
    _assert_no_token(result)
    assert "user:token" not in result.stdout + result.stderr


def _setting(env: dict[str, str], repo: Path) -> str | None:
    found = subprocess.run(
        ["git", "-C", str(repo), "config", "--get", SETTING],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return found.stdout.strip() if found.returncode == 0 else None


def _refs(env: dict[str, str], *repos: Path) -> list[str]:
    return [_git(env, "-C", str(repo), "for-each-ref") for repo in repos]


def _sha(env: dict[str, str], repo: Path) -> str:
    return _git(env, "-C", str(repo), "rev-parse", REF)


def _local_project(env: dict[str, str], path: Path, *lines: str) -> tuple[Path, str]:
    """A project without origin whose local counter is at C; return it and C."""
    project = _project(env, path)
    sha = _set_counter(env, project / ".git", *lines)
    _git(env, "-C", str(project), "config", SETTING, str(project))
    return project, sha


def _add_origin(env: dict[str, str], project: Path, bare: Path) -> None:
    """Give the project the made-up origin URL that git rewrites to the bare path."""
    _git(env, "-C", str(project), "remote", "add", "origin", ORIGIN_URL)
    _git(env, "-C", str(project), "config", f"url.{bare}.insteadOf", ORIGIN_URL)


@pytest.fixture
def demo(tmp_path: Path, env: dict[str, str]) -> tuple[Path, str, Path]:
    """The project at C with ST=0012, and an empty origin behind the made-up URL."""
    project, sha = _local_project(env, tmp_path / "demo", "start=0000", "ST=0012")
    origin = _bare(env, tmp_path / "origin.git")
    _add_origin(env, project, origin)
    return project, sha, origin


# --- contract tests -----------------------------------------------------------


def test_st_0380_every_git_call_of_the_move_runs_without_prompts_and_with_a_limit(
    env, demo, monkeypatch
):
    project, _, _ = demo
    for key in ("HOME", "GIT_CONFIG_NOSYSTEM", "GIT_CEILING_DIRECTORIES"):
        monkeypatch.setenv(key, env[key])
    monkeypatch.delenv("GIT_TERMINAL_PROMPT", raising=False)
    monkeypatch.delenv("GIT_SSH_COMMAND", raising=False)
    monkeypatch.chdir(project)
    seen: list[tuple[list[str], dict]] = []
    real = subprocess.run

    def spy(cmd, **kwargs):
        if cmd[1:] != ["config", "--get", "core.sshCommand"]:
            seen.append((cmd, kwargs))
        return real(cmd, **kwargs)

    monkeypatch.setattr(ni.subprocess, "run", spy)
    ni.move_to_origin()
    assert any("push" in cmd for cmd, _ in seen)
    for cmd, kwargs in seen:
        assert kwargs["timeout"] == 30, cmd
        assert kwargs["env"]["GIT_TERMINAL_PROMPT"] == "0", cmd
        assert kwargs["env"]["GIT_SSH_COMMAND"] == "ssh -o BatchMode=yes", cmd


# --- integration tests --------------------------------------------------------


@pytest.mark.spec("CIF-10-IT-01")
def test_st_0380_the_move_carries_c_to_origin_and_leaves_a_marker(env, demo):
    project, sha, origin = demo

    result = run(env, project, "--move-to-origin")

    assert result.returncode == 0, result.stderr
    _assert_no_token(result)
    assert _sha(env, origin) == sha
    marker = project / ".git"
    assert _counter(env, marker) == [f"moved={SHOWN_URL}"]
    parents = _git(env, "-C", str(marker), "log", "-1", "--format=%P", REF)
    assert parents == sha
    assert _setting(env, project) is None
    claim = run(env, project, "ST")
    assert claim.stdout == "ST-0013\n", claim.stderr
    assert "ST=0013" in _counter(env, origin)


@pytest.mark.spec("CIF-11-IT-01")
def test_st_0380_a_counter_on_origin_refuses_the_move(env, demo):
    project, sha, origin = demo
    taken = _set_counter(env, origin, "start=0000", "ST=0040")
    before = _refs(env, project, origin)

    result = run(env, project, "--move-to-origin")

    _assert_refused(result)
    assert str(project) in result.stderr
    assert SHOWN_URL in result.stderr
    assert "ST=0012" in result.stderr
    assert "ST=0040" in result.stderr
    assert _sha(env, project / ".git") == sha
    assert _sha(env, origin) == taken
    assert _refs(env, project, origin) == before
    assert _setting(env, project) == str(project)


@pytest.mark.spec("CIF-11-IT-02")
def test_st_0380_a_refused_push_puts_c_back(env, demo):
    project, sha, origin = demo
    hook = origin / "hooks" / "pre-receive"
    hook.write_text(READ_ONLY_HOOK)
    hook.chmod(0o755)
    before = _refs(env, project, origin)

    result = run(env, project, "--move-to-origin")

    _assert_refused(result)
    assert "read-only" in result.stderr
    assert _sha(env, project / ".git") == sha
    assert _refs(env, project, origin) == before
    assert _setting(env, project) == str(project)


class TestAMoveWithAMissingPiece:
    """CIFP-C16: the move names the missing piece and changes nothing."""

    def test_st_0380_without_the_setting_the_move_names_it(self, env, tmp_path):
        project = _project(env, tmp_path / "demo")
        _set_counter(env, project / ".git", "start=0000", "ST=0012")
        origin = _bare(env, tmp_path / "origin.git")
        _add_origin(env, project, origin)
        before = _refs(env, project, origin)

        result = run(env, project, "--move-to-origin")

        _assert_refused(result)
        assert SETTING in result.stderr
        assert "no local counter" in result.stderr
        assert _refs(env, project, origin) == before

    def test_st_0380_without_origin_the_move_names_origin(self, env, tmp_path):
        project, _ = _local_project(env, tmp_path / "demo", "start=0000", "ST=0012")
        before = _refs(env, project)

        result = run(env, project, "--move-to-origin")

        _assert_refused(result)
        assert "`origin`" in result.stderr
        assert _refs(env, project) == before
        assert _setting(env, project) == str(project)

    def test_st_0380_without_a_local_counter_the_move_names_step_4(self, env, tmp_path):
        project = _project(env, tmp_path / "demo")
        _git(env, "-C", str(project), "config", SETTING, str(project))
        origin = _bare(env, tmp_path / "origin.git")
        _add_origin(env, project, origin)
        before = _refs(env, project, origin)

        result = run(env, project, "--move-to-origin")

        _assert_refused(result)
        assert REF in result.stderr
        assert str(project) in result.stderr
        assert "fitting step 4" in result.stderr
        assert _refs(env, project, origin) == before
        assert _setting(env, project) == str(project)


def test_st_0380_a_marker_at_the_local_counter_stops_the_move(env, demo):
    """Until ST-0381 resumes a move, a marker at the local counter changes nothing."""
    project, _, _ = demo
    assert run(env, project, "--move-to-origin").returncode == 0
    _git(env, "-C", str(project), "config", SETTING, str(project))
    before = _refs(env, project)

    result = run(env, project, "--move-to-origin")

    _assert_refused(result)
    assert SHOWN_URL in result.stderr
    assert "--seed" not in result.stderr
    assert _refs(env, project) == before


@pytest.mark.spec("CIF-12-IT-02")
def test_st_0380_a_claim_in_a_worktree_after_the_marker_claims_nothing(
    env, tmp_path, demo
):
    project, _, _ = demo
    worktree = tmp_path / "demo-feature"
    _git(env, "-C", str(project), "worktree", "add", "--quiet", "-b", "feature/x", str(worktree))
    marker = ni.format_marker(ORIGIN_URL)
    tree = _git(env, "-C", str(project), "mktree")
    sha = subprocess.run(
        ["git", "-C", str(project), "commit-tree", tree, "-p", REF],
        input=marker,
        env={**env, **FIXTURE_IDENTITY},
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _git(env, "-C", str(project), "update-ref", REF, sha)
    before = _refs(env, project)

    result = run(env, worktree, "ST")

    _assert_refused(result)
    assert SHOWN_URL in result.stderr
    assert "--seed" not in result.stderr
    assert _refs(env, project) == before


def test_st_0380_move_takes_no_argument_and_no_remote(env, demo):
    project, _, _ = demo
    assert run(env, project, "--move-to-origin", "ST").returncode == 2
    assert run(env, project, "--move-to-origin", "--remote", "/x").returncode == 2


def test_st_0380_usage_names_the_move(env, tmp_path):
    result = run(env, tmp_path, "--help")
    assert "next-id --move-to-origin" in result.stdout


def test_st_0380_demo_scenario_end_to_end(env, tmp_path):
    project, _ = _local_project(env, tmp_path / "move-demo", "start=0000", "ST=0012")
    origin = _bare(env, tmp_path / "move-origin.git")
    _git(env, "-C", str(project), "remote", "add", "origin", str(origin))
    local_clone = tmp_path / "move-clone"
    _git(env, "clone", "--quiet", str(project), str(local_clone))

    assert run(env, project, "--move-to-origin").returncode == 0
    assert "ST=0012" in _counter(env, origin)
    assert _counter(env, project / ".git") == [f"moved={origin}"]
    assert _setting(env, project) is None
    assert run(env, project, "ST").stdout == "ST-0013\n"
    for args in (["ST"], ["--plan-seed"]):
        result = run(env, local_clone, *args)
        assert result.returncode != 0
        assert str(origin) in result.stderr
        assert "--seed" not in result.stdout + result.stderr

    twice, sha = _local_project(env, tmp_path / "move-twice", "start=0000", "ST=0012")
    taken = _bare(env, tmp_path / "move-taken.git")
    assert run(env, tmp_path, "--seed", "0", "ST=40", "--remote", str(taken)).returncode == 0
    _git(env, "-C", str(twice), "remote", "add", "origin", str(taken))
    taken_sha = _sha(env, taken)
    result = run(env, twice, "--move-to-origin")
    assert result.returncode != 0
    assert "ST=0012" in result.stderr
    assert "ST=0040" in result.stderr
    assert _sha(env, twice / ".git") == sha
    assert _sha(env, taken) == taken_sha
    assert _setting(env, twice) == str(twice)
