"""Tests for next-id --move-to-origin (ST-0380, ST-0381, counter-ids-fitting.feature).

The move carries the claim commit C of the local counter to `origin` in the
four steps of BR-102. Every remote is a local bare repository in tmp_path.
The made-up URL `https://user:token@host/demo.git` reaches the bare repository
through `url.<bare path>.insteadOf` in the project's own config, so git talks
to the bare repository and next-id sees the made-up URL (QA strategy, Test
setup). Every failing path checks that no token shows.

ST-0381 adds the claims during a move and the move that was cut off after the
marker. The forced race wraps the read of the local counter and runs a real
`next-id ST` right after the first read, so the test needs no timing. A
cut-off test writes the marker itself, because no command stops a move there.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from test_next_id import (  # noqa: F401
    FIXTURE_IDENTITY,
    NEXT_ID,
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


def _write_marker(env: dict[str, str], project: Path) -> str:
    """Put the marker of a move to the made-up origin on the local counter, parent C."""
    tree = _git(env, "-C", str(project), "mktree")
    sha = subprocess.run(
        ["git", "-C", str(project), "commit-tree", tree, "-p", REF],
        input=ni.format_marker(ORIGIN_URL),
        env={**env, **FIXTURE_IDENTITY},
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _git(env, "-C", str(project), "update-ref", REF, sha)
    return sha


def _worktree(env: dict[str, str], project: Path, path: Path) -> Path:
    _git(
        env,
        "-C",
        str(project),
        "worktree",
        "add",
        "--quiet",
        "-b",
        "feature/x",
        str(path),
    )
    return path


def _in_project(monkeypatch, env: dict[str, str], project: Path) -> None:
    """Run the move in this process, inside the project, with the test's git setup."""
    for key in ("HOME", "GIT_CONFIG_NOSYSTEM", "GIT_CEILING_DIRECTORIES"):
        monkeypatch.setenv(key, env[key])
    monkeypatch.chdir(project)


def _st_line(env: dict[str, str], repo: Path) -> int:
    lines = dict(line.split("=", 1) for line in _counter(env, repo))
    return int(lines["ST"])


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

    result = run(env, project, "--move-to-origin")

    _assert_refused(result)
    assert str(project) in result.stderr
    assert SHOWN_URL in result.stderr
    assert "ST=0012" in result.stderr
    assert "ST=0040" in result.stderr
    assert _counter(env, project / ".git") == [f"moved={SHOWN_URL}"]
    assert _git(env, "-C", str(project), "rev-parse", f"{REF}^") == sha
    assert _sha(env, origin) == taken
    assert _setting(env, project) == str(project)


@pytest.mark.spec("CIF-11-IT-02")
def test_dec_16_a_refused_push_keeps_the_marker_and_a_second_move_resumes(env, demo):
    project, sha, origin = demo
    hook = origin / "hooks" / "pre-receive"
    hook.write_text(READ_ONLY_HOOK)
    hook.chmod(0o755)
    before = _refs(env, origin)

    result = run(env, project, "--move-to-origin")

    _assert_refused(result)
    assert "read-only" in result.stderr
    assert "keeps the marker" in result.stderr
    assert _counter(env, project / ".git") == [f"moved={SHOWN_URL}"]
    assert _git(env, "-C", str(project), "rev-parse", f"{REF}^") == sha
    assert _refs(env, origin) == before
    assert _setting(env, project) == str(project)

    hook.unlink()
    resumed = run(env, project, "--move-to-origin")
    assert resumed.returncode == 0, resumed.stderr
    assert _sha(env, origin) == sha
    assert _setting(env, project) is None


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


@pytest.mark.spec("CIF-12-IT-02")
def test_st_0380_a_claim_in_a_worktree_after_the_marker_claims_nothing(
    env, tmp_path, demo
):
    project, _, _ = demo
    worktree = _worktree(env, project, tmp_path / "demo-feature")
    _write_marker(env, project)
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
    assert (
        run(env, tmp_path, "--seed", "0", "ST=40", "--remote", str(taken)).returncode
        == 0
    )
    _git(env, "-C", str(twice), "remote", "add", "origin", str(taken))
    taken_sha = _sha(env, taken)
    result = run(env, twice, "--move-to-origin")
    assert result.returncode != 0
    assert "ST=0012" in result.stderr
    assert "ST=0040" in result.stderr
    assert _git(env, "-C", str(twice), "rev-parse", f"{REF}^") == sha
    assert _sha(env, taken) == taken_sha
    assert _setting(env, twice) == str(twice)


# --- ST-0381: claims during the move ------------------------------------------


class StaleLocalCounter:
    """A mocked local counter: an ID claim raises it after every read."""

    def __init__(self):
        self.reads = 0
        self.marks: list[str] = []

    def read(self) -> tuple[str, str]:
        self.reads += 1
        return f"sha{self.reads}", f"start=0000\nST={12 + self.reads:04d}\ntoken=x\n"

    def parent(self, marker: str) -> tuple[str, str]:
        raise AssertionError("a claim commit has no marker parent")

    def mark(self, lease: str) -> str:
        self.marks.append(lease)
        raise ni.StaleLease("cannot lock ref")


def test_st_0381_ten_stale_leases_on_c_end_the_move_without_a_marker():
    counter = StaleLocalCounter()
    waits: list[float] = []

    with pytest.raises(ni.NextIdError) as failed:
        ni.mark_loop(counter, "/demo", sleep=waits.append)

    assert counter.reads == 10
    assert counter.marks == [f"sha{n}" for n in range(1, 11)]
    assert len(waits) == 9
    assert all(0.1 <= wait <= 1.0 for wait in waits)
    message = str(failed.value)
    assert "the move" in message
    assert "ten stale leases" in message
    assert "/demo" in message


def test_st_0381_nine_stale_leases_still_end_in_a_marker():
    class NineStale(StaleLocalCounter):
        def mark(self, lease: str) -> str:
            self.marks.append(lease)
            if len(self.marks) < 10:
                raise ni.StaleLease("cannot lock ref")
            return "marker"

    counter = NineStale()
    moved = ni.mark_loop(counter, "/demo", sleep=lambda _s: None)
    assert moved == ("sha10", "start=0000\nST=0022\ntoken=x\n", "marker", False)


@pytest.mark.spec("CIF-12-IT-01")
def test_st_0381_a_claim_between_the_read_and_the_marker_reaches_origin(
    env, tmp_path, demo, monkeypatch
):
    project, _, origin = demo
    worktree = _worktree(env, project, tmp_path / "demo-feature")
    _in_project(monkeypatch, env, project)
    real = ni.read_local_counter
    claims: list[subprocess.CompletedProcess] = []

    def read_then_claim(local: str) -> tuple[str, str]:
        found = real(local)
        if not claims:
            claims.append(run(env, worktree, "ST"))
        return found

    monkeypatch.setattr(ni, "read_local_counter", read_then_claim)

    output = ni.move_to_origin()

    assert claims[0].stdout == "ST-0013\n", claims[0].stderr
    assert output.startswith("moved ")
    assert "ST=0013" in _counter(env, origin)
    marker = project / ".git"
    parent = _git(env, "-C", str(marker), "log", "-1", "--format=%P", REF)
    assert parent == _sha(env, origin)
    assert _setting(env, project) is None


def test_st_0381_twenty_moves_with_a_parallel_claim_hand_out_no_number_twice(
    env, tmp_path
):
    """QS-22: a claim that exits 0 holds a number at or below the ST line on origin."""
    for round_number in range(1, 21):
        base = tmp_path / f"round-{round_number}"
        project, _ = _local_project(env, base / "demo", "start=0000", "ST=0012")
        origin = _bare(env, base / "origin.git")
        _git(env, "-C", str(project), "remote", "add", "origin", str(origin))
        worktree = _worktree(env, project, base / "demo-feature")
        move, claim = (
            subprocess.Popen(
                [sys.executable, str(NEXT_ID), *args],
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for cwd, args in ((project, ["--move-to-origin"]), (worktree, ["ST"]))
        )
        _, moved_err = move.communicate(timeout=120)
        claim_out, _ = claim.communicate(timeout=120)

        assert move.returncode == 0, (round_number, moved_err)
        on_origin = _st_line(env, origin)
        if claim.returncode == 0:
            assert int(claim_out.strip().split("-")[1]) <= on_origin, (
                round_number,
                claim_out,
                on_origin,
            )
        else:
            assert claim_out == "", (round_number, claim_out)
        after = run(env, project, "ST")
        assert int(after.stdout.strip().split("-")[1]) == on_origin + 1, (
            round_number,
            after.stderr,
        )


# --- ST-0381: a move that was cut off after the marker -------------------------


def test_st_0381_a_cut_off_move_pushes_c_from_the_marker_parent(env, demo):
    project, sha, origin = demo
    marker = _write_marker(env, project)

    result = run(env, project, "--move-to-origin")

    assert result.returncode == 0, result.stderr
    _assert_no_token(result)
    assert _sha(env, origin) == sha
    assert _sha(env, project / ".git") == marker
    assert _setting(env, project) is None
    claim = run(env, project, "ST")
    assert claim.stdout == "ST-0013\n", claim.stderr


def test_st_0381_a_cut_off_move_whose_push_was_done_only_removes_the_setting(env, demo):
    project, sha, origin = demo
    marker = _write_marker(env, project)
    _git(env, "-C", str(project), "push", "--quiet", str(origin), f"{sha}:{REF}")
    before = _refs(env, project, origin)

    result = run(env, project, "--move-to-origin")

    assert result.returncode == 0, result.stderr
    _assert_no_token(result)
    assert _refs(env, project, origin) == before
    assert _sha(env, origin) == sha
    assert _sha(env, project / ".git") == marker
    assert _setting(env, project) is None


def test_st_0381_a_cut_off_move_meets_another_counter_on_origin(env, demo):
    project, _, origin = demo
    _write_marker(env, project)
    _set_counter(env, origin, "start=0000", "ST=0040")
    before = _refs(env, project, origin)

    result = run(env, project, "--move-to-origin")

    _assert_refused(result)
    assert str(project) in result.stderr
    assert SHOWN_URL in result.stderr
    assert "ST=0012" in result.stderr
    assert "ST=0040" in result.stderr
    assert _refs(env, project, origin) == before
    assert _setting(env, project) == str(project)


# --- IMPL-0008: the move runs no hook of the project ---------------------------

FAILING_HOOK = """#!/bin/sh
echo pre-push refused >&2
exit 1
"""


def test_impl_0008_a_failing_pre_push_hook_of_the_project_does_not_stop_the_move(
    env, demo
):
    project, sha, origin = demo
    hook = project / ".git" / "hooks" / "pre-push"
    hook.write_text(FAILING_HOOK)
    hook.chmod(0o755)

    result = run(env, project, "--move-to-origin")

    assert result.returncode == 0, result.stderr
    _assert_no_token(result)
    assert _sha(env, origin) == sha
    assert _setting(env, project) is None


# --- IMPL-0009: a refused push asks origin again --------------------------------


def _origin_changes_after_the_check(monkeypatch, change) -> None:
    """Run `change` once, right after the first real `ls-remote` of the move."""
    real = ni._origin_counter
    calls: list[str | None] = []

    def check_then_change(target: str, url: str) -> str | None:
        found = real(target, url)
        if not calls:
            change()
        calls.append(found)
        return found

    monkeypatch.setattr(ni, "_origin_counter", check_then_change)


def test_impl_0009_a_resumed_move_keeps_the_marker_when_origin_gains_a_counter(
    env, tmp_path, demo, monkeypatch
):
    project, sha, origin = demo
    marker = _write_marker(env, project)
    _in_project(monkeypatch, env, project)
    claims: list[subprocess.CompletedProcess] = []

    def push_c_and_claim() -> None:
        _git(env, "-C", str(project), "push", "--quiet", str(origin), f"{sha}:{REF}")
        claims.append(run(env, tmp_path, "ST", "--remote", str(origin)))

    _origin_changes_after_the_check(monkeypatch, push_c_and_claim)

    with pytest.raises(ni.NextIdError) as refused:
        ni.move_to_origin()

    assert claims[0].stdout == "ST-0013\n", claims[0].stderr
    assert "two counters" in str(refused.value)
    assert "ST=0013" in str(refused.value)
    assert _sha(env, project / ".git") == marker
    assert _setting(env, project) == str(project)
    again = run(env, project, "ST")
    assert again.returncode != 0
    assert again.stdout == ""


def test_impl_0009_a_refused_push_finishes_when_origin_holds_c(
    env, demo, monkeypatch
):
    project, sha, origin = demo
    marker = _write_marker(env, project)
    _in_project(monkeypatch, env, project)

    def push_c() -> None:
        _git(env, "-C", str(project), "push", "--quiet", str(origin), f"{sha}:{REF}")

    _origin_changes_after_the_check(monkeypatch, push_c)

    output = ni.move_to_origin()

    assert output.startswith("moved ")
    assert _sha(env, origin) == sha
    assert _sha(env, project / ".git") == marker
    assert _setting(env, project) is None


def test_impl_0009_a_resumed_move_keeps_the_marker_after_another_refusal(env, demo):
    project, _, origin = demo
    marker = _write_marker(env, project)
    hook = origin / "hooks" / "pre-receive"
    hook.write_text(READ_ONLY_HOOK)
    hook.chmod(0o755)

    result = run(env, project, "--move-to-origin")

    _assert_refused(result)
    assert "read-only" in result.stderr
    assert _sha(env, project / ".git") == marker
    assert _setting(env, project) == str(project)


# --- DEC-16: a failed push never puts C back ------------------------------------


def test_dec_16_a_first_move_keeps_the_marker_when_origin_gains_a_counter(
    env, tmp_path, demo, monkeypatch
):
    """The reviewer's race: origin gains a counter grown from C before the push."""
    project, sha, origin = demo
    _in_project(monkeypatch, env, project)
    real = ni.push_to_origin
    claims: list[subprocess.CompletedProcess] = []

    def seed_then_push(local: str, url: str, pushed: str) -> None:
        _git(env, "-C", str(project), "push", "--quiet", str(origin), f"{sha}:{REF}")
        claims.append(run(env, tmp_path, "ST", "--remote", str(origin)))
        real(local, url, pushed)

    monkeypatch.setattr(ni, "push_to_origin", seed_then_push)

    with pytest.raises(ni.NextIdError) as refused:
        ni.move_to_origin()

    assert claims[0].stdout == "ST-0013\n", claims[0].stderr
    assert "two counters" in str(refused.value)
    assert _counter(env, project / ".git") == [f"moved={SHOWN_URL}"]
    assert _setting(env, project) == str(project)
    again = run(env, project, "ST")
    assert again.returncode != 0
    assert again.stdout == ""
