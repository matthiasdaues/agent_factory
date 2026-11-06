"""Tests for next-id: the seed and the ID claim (ST-0368, counter-ids.feature).

Every remote is a local bare repository in tmp_path. Each subprocess runs with
HOME set to an empty directory, GIT_CONFIG_NOSYSTEM=1, and
GIT_TERMINAL_PROMPT=0, so no global identity, URL rewrite, or prompt reaches
a test (QA strategy, Test setup).
"""

from __future__ import annotations

import contextlib
import http.server
import os
import re
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR, load_script

ni = load_script("next-id")

NEXT_ID = SOURCE_SCRIPTS_DIR / "next-id"
BACKLOG_LINT = SOURCE_SCRIPTS_DIR / "backlog-lint"
REF = "refs/ids/counters"
FIXTURE_IDENTITY = {
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}


# --- fixtures -----------------------------------------------------------------


@pytest.fixture
def env(tmp_path: Path) -> dict[str, str]:
    home = tmp_path / "home"
    home.mkdir()
    base = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    base.update(
        HOME=str(home),
        GIT_CONFIG_NOSYSTEM="1",
        GIT_TERMINAL_PROMPT="0",
        GIT_CEILING_DIRECTORIES=str(tmp_path),
    )
    return base


def _git(env: dict[str, str], *args: str, cwd: Path | None = None, extra=None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env={**env, **(extra or {})},
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _bare(env: dict[str, str], path: Path) -> Path:
    _git(env, "init", "--quiet", "--bare", str(path))
    return path


def _set_counter(env: dict[str, str], bare: Path, *lines: str) -> str:
    """Write a claim commit inside the bare repository; push nothing."""
    tree = _git(env, "-C", str(bare), "mktree")
    message = "\n".join([*lines, "token=fixture0000000000"]) + "\n"
    sha = subprocess.run(
        ["git", "-C", str(bare), "commit-tree", tree],
        input=message,
        env={**env, **FIXTURE_IDENTITY},
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _git(env, "-C", str(bare), "update-ref", REF, sha)
    return sha


def _counter(env: dict[str, str], bare: Path) -> list[str]:
    return _git(
        env, "-C", str(bare), "show", "--no-patch", "--format=%B", REF
    ).splitlines()


def _has_ref(env: dict[str, str], bare: Path) -> bool:
    return bool(_git(env, "-C", str(bare), "for-each-ref", REF))


@pytest.fixture
def remote(tmp_path: Path, env: dict[str, str]) -> Path:
    return _bare(env, tmp_path / "remote.git")


@pytest.fixture
def clone(tmp_path: Path, env: dict[str, str], remote: Path) -> Path:
    path = tmp_path / "clone"
    _git(env, "clone", "--quiet", str(remote), str(path))
    return path


def run(env: dict[str, str], cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(NEXT_ID), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


# --- contract tests -----------------------------------------------------------


@pytest.mark.spec("CID-01-CT-01")
class TestSeedArguments:
    @pytest.mark.parametrize(
        ("arguments", "lines"),
        [
            (["0"], ["start=0000"]),
            (["9998"], ["start=9998"]),
            (["1000"], ["start=1000"]),
            (["1000", "ADR=6"], ["start=1000", "ADR=0006"]),
            (["1000", "ST=0", "ADR=9998"], ["start=1000", "ST=0000", "ADR=9998"]),
        ],
    )
    def test_st_0368_valid_seed_writes_four_digit_lines(self, arguments, lines):
        assert ni.number_lines(ni.parse_seed(arguments)) == lines

    @pytest.mark.parametrize(
        ("arguments", "named"),
        [
            (["10000"], ["'10000'"]),
            (["abc"], ["'abc'"]),
            (["9999"], ["'9999'"]),
            (["-1"], ["'-1'"]),
            (["1000", "ST=x"], ["'ST=x'"]),
            (["1000", "ST=10000"], ["'ST=10000'"]),
            (
                ["1000", "XX=5"],
                ["'XX'", "ST, BUG, SPEC, FAGAN, SEC, RECON, ATAM, IMPL, T, ADR, ARCH, QA"],
            ),
            (["1000", "ST=5", "ST=7"], ["'ST'"]),
        ],
    )
    def test_st_0368_wrong_seed_argument_names_it(self, arguments, named):
        with pytest.raises(ni.NextIdError) as exc:
            ni.parse_seed(arguments)
        for text in named:
            assert text in str(exc.value)

    @pytest.mark.parametrize(
        "arguments", [["10000"], ["1000", "XX=5"], ["1000", "ST=5", "ST=7"]]
    )
    def test_st_0368_wrong_seed_argument_runs_no_git(
        self, monkeypatch, capsys, arguments
    ):
        def no_git(*_a, **_k):
            raise AssertionError("git ran before the arguments were checked")

        monkeypatch.setattr(ni, "git", no_git)
        assert ni.main(["--seed", *arguments]) == 1
        assert capsys.readouterr().out == ""


@pytest.mark.spec("CID-02-CT-01")
class TestRaiseLine:
    def test_st_0368_claim_raises_the_line_and_keeps_every_other_line(self):
        message = "start=1000\nST=1012\nFAGAN=1003\ntoken=old\n"
        new, claimed = ni.raise_line(message, "FAGAN", "new")
        assert claimed == "FAGAN-1004"
        assert new == "start=1000\nST=1012\nFAGAN=1004\ntoken=new\n"

    def test_st_0368_first_claim_of_a_prefix_is_start_plus_one(self):
        new, claimed = ni.raise_line("start=1000\nST=1012\ntoken=old\n", "BUG", "new")
        assert claimed == "BUG-1001"
        assert new == "start=1000\nST=1012\nBUG=1001\ntoken=new\n"

    def test_st_0368_claim_pads_to_four_digits(self):
        new, claimed = ni.raise_line("start=0000\nADR=0006\ntoken=old\n", "ADR", "new")
        assert claimed == "ADR-0007"
        assert new == "start=0000\nADR=0007\ntoken=new\n"


@pytest.mark.spec("CID-04-CT-01")
class TestPrefixOutsideTheList:
    @pytest.mark.parametrize("prefix", ["XX", "PROP", "RETRO"])
    def test_st_0368_unknown_prefix_fails_before_any_remote(
        self, monkeypatch, capsys, prefix
    ):
        def no_git(*_a, **_k):
            raise AssertionError("git ran before the prefix was checked")

        monkeypatch.setattr(ni, "git", no_git)
        assert ni.main([prefix]) == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert f"'{prefix}'" in captured.err
        assert ", ".join(ni.PREFIXES) in captured.err

    def test_st_0368_prefix_list_holds_the_twelve_prefixes(self):
        assert ni.PREFIXES == (
            "ST",
            "BUG",
            "SPEC",
            "FAGAN",
            "SEC",
            "RECON",
            "ATAM",
            "IMPL",
            "T",
            "ADR",
            "ARCH",
            "QA",
        )


class FakeCounter:
    """A mocked port: hands out counter states and records each push."""

    def __init__(self, stale: int, refusal: str | None = None):
        self.stale = stale
        self.refusal = refusal
        self.reads = 0
        self.pushes: list[tuple[str, str]] = []

    def read(self) -> tuple[str, str]:
        self.reads += 1
        # Each read sees the claim of another session: ST rises by one.
        return f"sha{self.reads}", f"start=1000\nST={1000 + self.reads:04d}\ntoken=x\n"

    def push(self, message: str, lease: str) -> None:
        self.pushes.append((message, lease))
        if self.refusal is not None:
            raise ni.NextIdError(self.refusal)
        if len(self.pushes) <= self.stale:
            raise ni.StaleLease("stale info")


@pytest.mark.spec("CID-03-CT-01")
class TestRetryLoop:
    def test_st_0369_stale_lease_waits_reads_again_and_claims_the_next_number(self):
        counter = FakeCounter(stale=1)
        waits: list[float] = []
        assert ni.claim_loop("ST", counter, sleep=waits.append) == "ST-1003"
        assert counter.reads == 2
        assert [lease for _, lease in counter.pushes] == ["sha1", "sha2"]
        assert "ST=1003" in counter.pushes[-1][0].splitlines()
        assert len(waits) == 1
        assert 0.1 <= waits[0] <= 1.0

    def test_st_0369_ten_stale_leases_end_the_claim_and_name_prefix_and_number(self):
        counter = FakeCounter(stale=99)
        waits: list[float] = []
        with pytest.raises(ni.NextIdError) as exc:
            ni.claim_loop("ST", counter, sleep=waits.append)
        assert len(counter.pushes) == 10
        assert len(waits) == 9
        assert all(0.1 <= wait <= 1.0 for wait in waits)
        assert "ST-1011" in str(exc.value)
        assert "ten stale leases" in str(exc.value)

    def test_st_0369_nine_stale_leases_still_end_in_a_claim(self):
        counter = FakeCounter(stale=9)
        waits: list[float] = []
        assert ni.claim_loop("ST", counter, sleep=waits.append) == "ST-1011"
        assert len(counter.pushes) == 10
        assert len(waits) == 9

    def test_st_0369_waits_use_the_whole_range_from_0_1_to_1_second(self, monkeypatch):
        bounds: list[tuple[float, float]] = []
        monkeypatch.setattr(
            ni.random, "uniform", lambda low, high: bounds.append((low, high)) or low
        )
        ni.claim_loop("ST", FakeCounter(stale=2), sleep=lambda _s: None)
        assert bounds == [(0.1, 1.0), (0.1, 1.0)]

    def test_st_0369_other_refusal_ends_the_loop_after_one_push(self):
        counter = FakeCounter(stale=0, refusal="on fake.git failed: read-only")
        waits: list[float] = []
        with pytest.raises(ni.NextIdError, match="read-only"):
            ni.claim_loop("ST", counter, sleep=waits.append)
        assert len(counter.pushes) == 1
        assert waits == []


@pytest.mark.spec("CID-03-CT-02")
class TestStaleLeaseCheck:
    @pytest.mark.parametrize(
        "error",
        [
            " ! [rejected]        abc -> refs/ids/counters (stale info)",
            (
                "remote: error: cannot lock ref 'refs/ids/counters': is at "
                "db8c82cbcbdcf8f2575bf908be93d5e8b872c088 but expected "
                "3559164876a3e91c18b1c5c404ae8f159c563120"
            ),
        ],
    )
    def test_st_0369_stale_lease_messages_count_as_stale(self, error):
        assert ni.is_stale_lease(error)

    @pytest.mark.parametrize(
        "error",
        [
            " ! [remote rejected] abc -> refs/ids/counters (pre-receive hook declined)",
            "remote: read-only",
            "fatal: unable to access 'https://example.invalid/r.git/'",
            "cannot lock ref 'refs/ids/counters': unable to create lock file",
            "",
        ],
    )
    def test_st_0369_other_refusals_count_as_final(self, error):
        assert not ni.is_stale_lease(error)


# --- integration tests: seed ---------------------------------------------------


@pytest.mark.spec("CID-01-IT-01")
class TestSeedCreatesTheCounter:
    def test_st_0368_seed_creates_the_counter_and_claims_continue_above_it(
        self, env, remote, clone
    ):
        result = run(env, clone, "--seed", "1000")
        assert result.returncode == 0, result.stderr
        assert "start=1000" in result.stdout.splitlines()
        assert "start=1000" in _counter(env, remote)
        assert run(env, clone, "ST").stdout == "ST-1001\n"
        assert run(env, clone, "BUG").stdout == "BUG-1001\n"

    def test_st_0368_seed_gives_adr_its_own_start(self, env, remote, clone):
        result = run(env, clone, "--seed", "1000", "ADR=6")
        assert result.returncode == 0, result.stderr
        assert {"start=1000", "ADR=0006"} <= set(result.stdout.splitlines())
        assert {"start=1000", "ADR=0006"} <= set(_counter(env, remote))
        assert run(env, clone, "ADR").stdout == "ADR-0007\n"

    def test_st_0368_seed_with_remote_creates_the_counter_there(
        self, env, tmp_path, remote, clone
    ):
        other = _bare(env, tmp_path / "other.git")
        result = run(env, clone, "--seed", "1000", "--remote", str(other))
        assert result.returncode == 0, result.stderr
        assert "start=1000" in _counter(env, other)
        assert not _has_ref(env, remote)


@pytest.mark.spec("CID-01-IT-02")
def test_st_0368_seed_on_a_counter_in_use_changes_nothing(env, remote, clone):
    before = _set_counter(env, remote, "start=1000", "ST=1012")
    result = run(env, clone, "--seed", "1000")
    assert result.returncode != 0
    assert result.stdout == ""
    assert str(remote) in result.stderr
    assert REF in result.stderr
    assert _git(env, "-C", str(remote), "rev-parse", REF) == before


@pytest.mark.spec("CID-01-IT-03")
@pytest.mark.parametrize(
    "arguments",
    [
        ["10000"],
        ["abc"],
        ["9999"],
        ["-1"],
        ["1000", "XX=5"],
        ["1000", "ST=x"],
        ["1000", "ST=5", "ST=7"],
    ],
)
def test_st_0368_wrong_seed_argument_creates_no_ref(env, remote, clone, arguments):
    result = run(env, clone, "--seed", *arguments)
    assert result.returncode != 0
    assert result.stdout == ""
    assert not _has_ref(env, remote)


@pytest.mark.spec("CID-01-IT-04")
def test_st_0368_two_seeds_at_once_leave_one_claim_commit(env, tmp_path, remote):
    clones = []
    for name in ("a", "b"):
        path = tmp_path / name
        _git(env, "clone", "--quiet", str(remote), str(path))
        clones.append(path)
    procs = [
        subprocess.Popen(
            [sys.executable, str(NEXT_ID), "--seed", "1000"],
            cwd=path,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for path in clones
    ]
    codes = sorted(p.wait(timeout=60) for p in procs)
    for p in procs:
        p.stdout.close()
        p.stderr.close()
    assert codes[0] == 0
    assert codes[1] != 0
    assert _git(env, "-C", str(remote), "rev-list", "--count", REF) == "1"


@pytest.mark.spec("CID-01-IT-05")
class TestSeedWithoutAWorkingRemote:
    def test_st_0368_seed_without_origin_names_origin_and_remote(self, env, tmp_path):
        repo = tmp_path / "no-origin"
        _git(env, "init", "--quiet", str(repo))
        result = run(env, repo, "--seed", "1000")
        assert result.returncode != 0
        assert result.stdout == ""
        assert "`origin`" in result.stderr
        assert "--remote" in result.stderr

    def test_st_0368_seed_on_an_unreachable_remote_names_it(self, env, tmp_path):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        url = f"http://127.0.0.1:{port}/remote.git"
        repo = tmp_path / "unreachable"
        _git(env, "init", "--quiet", str(repo))
        _git(env, "-C", str(repo), "remote", "add", "origin", url)
        result = run(env, repo, "--seed", "1000")
        assert result.returncode != 0
        assert result.stdout == ""
        assert url in result.stderr
        assert "unable to access" in result.stderr


@pytest.mark.spec("CID-01-IT-06")
def test_st_0368_seed_keeps_the_existing_story_file(env, clone):
    story = clone / "backlog" / "ST-0327.md"
    story.parent.mkdir()
    story.write_text("---\nid: ST-0327\n---\nBody.\n")
    before = story.read_bytes()
    assert run(env, clone, "--seed", "1000").returncode == 0
    assert sorted(p.name for p in story.parent.iterdir()) == ["ST-0327.md"]
    assert story.read_bytes() == before


# --- integration tests: claim --------------------------------------------------


@pytest.mark.spec("CID-02-IT-01")
class TestClaimRecordsTheId:
    def test_st_0368_claim_prints_the_next_id_and_records_it(self, env, remote, clone):
        _set_counter(env, remote, "start=1000", "ST=1012")
        result = run(env, clone, "ST")
        assert result.returncode == 0, result.stderr
        assert result.stdout == "ST-1013\n"
        assert "ST=1013" in _counter(env, remote)

    def test_st_0368_first_bug_claim_keeps_the_st_line(self, env, remote, clone):
        _set_counter(env, remote, "start=1000", "ST=1012")
        assert run(env, clone, "BUG").stdout == "BUG-1001\n"
        assert {"BUG=1001", "ST=1012"} <= set(_counter(env, remote))

    def test_st_0368_fagan_claim_keeps_other_lines_and_changes_the_token(
        self, env, remote, clone
    ):
        _set_counter(env, remote, "start=1000", "ST=1012", "FAGAN=1003")
        old_token = [
            line for line in _counter(env, remote) if line.startswith("token=")
        ]
        assert run(env, clone, "FAGAN").stdout == "FAGAN-1004\n"
        lines = _counter(env, remote)
        assert [line for line in lines if not line.startswith("token=")] == [
            "start=1000",
            "ST=1012",
            "FAGAN=1004",
        ]
        new_token = [line for line in lines if line.startswith("token=")]
        assert len(new_token) == 1
        assert new_token != old_token


@pytest.mark.spec("CID-02-IT-02")
@pytest.mark.parametrize(
    "prefix",
    ["ST", "BUG", "SPEC", "FAGAN", "SEC", "RECON", "ATAM", "IMPL", "T", "ADR", "ARCH", "QA"],
)
def test_st_0368_every_prefix_of_the_list_can_be_claimed(env, remote, clone, prefix):
    _set_counter(env, remote, "start=1000")
    result = run(env, clone, prefix)
    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{prefix}-1001\n"
    assert f"{prefix}=1001" in _counter(env, remote)


@pytest.mark.spec("CID-02-IT-03")
def test_st_0368_claim_works_without_a_git_user_name(env, remote, clone):
    _set_counter(env, remote, "start=1000")
    assert (
        subprocess.run(
            ["git", "-C", str(clone), "config", "user.name"],
            env=env,
            capture_output=True,
        ).returncode
        != 0
    )
    result = run(env, clone, "ST")
    assert result.returncode == 0, result.stderr
    people = _git(
        env, "-C", str(remote), "log", "-1", "--format=%an <%ae>|%cn <%ce>", REF
    )
    assert (
        people
        == "next-id <next-id@agent-factory.invalid>|next-id <next-id@agent-factory.invalid>"
    )


@pytest.mark.spec("CID-02-IT-04")
def test_st_0368_claim_uses_origin_after_url_rewrites(env, tmp_path, remote):
    _set_counter(env, remote, "start=1000", "ST=1012")
    repo = tmp_path / "rewritten"
    _git(env, "init", "--quiet", str(repo))
    _git(env, "-C", str(repo), "remote", "add", "origin", "factory-test:remote.git")
    _git(env, "-C", str(repo), "config", f"url.{tmp_path}/.insteadOf", "factory-test:")
    assert _git(env, "-C", str(repo), "remote", "get-url", "origin") == str(remote)
    result = run(env, repo, "ST")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "ST-1013\n"
    assert "ST=1013" in _counter(env, remote)


@pytest.mark.spec("CID-02-IT-05")
def test_st_0368_claimed_id_passes_backlog_lint(env, tmp_path, remote, clone):
    _set_counter(env, remote, "start=1000")
    claimed = run(env, clone, "ST").stdout.strip()
    assert re.fullmatch(r"ST-\d{4}", claimed)
    backlog = tmp_path / "project" / "backlog"
    backlog.mkdir(parents=True)
    (backlog / f"{claimed}.md").write_text(
        f"---\nid: {claimed}\nepic: E1\ntitle: Claimed story\ntier: standard\n"
        "status: pending\ntouches: [src/]\n---\nBody.\n"
    )
    lint = subprocess.run(
        [sys.executable, str(BACKLOG_LINT), "--backlog-dir", str(backlog)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert lint.returncode == 0, lint.stdout + lint.stderr


# --- integration tests: stale lease and refusal --------------------------------

STALE_LEASE_HOOK = """#!/bin/sh
# Moves refs/ids/counters before every push, so every lease is stale.
unset GIT_QUARANTINE_PATH GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
tree=$(git mktree </dev/null)
sha=$(printf 'start=1000\\ntoken=%s\\n' "$(od -An -N8 -tx8 /dev/urandom | tr -d ' ')" |
  GIT_AUTHOR_NAME=hook GIT_AUTHOR_EMAIL=hook@example.invalid \\
  GIT_COMMITTER_NAME=hook GIT_COMMITTER_EMAIL=hook@example.invalid \\
  git commit-tree "$tree")
git update-ref refs/ids/counters "$sha"
echo "$sha" >"$(git rev-parse --git-dir)/hook-last"
exit 0
"""

READ_ONLY_HOOK = """#!/bin/sh
echo push >>"{log}"
echo read-only >&2
exit 1
"""


def _install_hook(remote: Path, text: str) -> None:
    hook = remote / "hooks" / "pre-receive"
    hook.write_text(text)
    hook.chmod(0o755)


@pytest.mark.spec("CID-04-IT-01")
def test_st_0369_ten_stale_leases_end_the_claim(env, remote):
    _set_counter(env, remote, "start=1000")
    _install_hook(remote, STALE_LEASE_HOOK)
    outside = remote.parent / "outside"
    outside.mkdir()
    result = run(env, outside, "ST", "--remote", str(remote))
    assert result.returncode != 0
    assert result.stdout == ""
    assert "ST-1001" in result.stderr
    assert "ten stale leases" in result.stderr
    last = (remote / "hook-last").read_text().strip()
    assert _git(env, "-C", str(remote), "rev-parse", REF) == last


@pytest.mark.spec("CID-04-IT-02")
def test_st_0369_read_only_refusal_ends_the_claim_after_one_push(env, tmp_path, remote):
    before = _set_counter(env, remote, "start=1000", "ST=1012")
    log = tmp_path / "hook.log"
    _install_hook(remote, READ_ONLY_HOOK.format(log=log))
    outside = tmp_path / "outside"
    outside.mkdir()
    result = run(env, outside, "ST", "--remote", str(remote))
    assert result.returncode != 0
    assert result.stdout == ""
    assert "read-only" in result.stderr
    assert str(remote) in result.stderr
    assert log.read_text().splitlines() == ["push"]
    assert _git(env, "-C", str(remote), "rev-parse", REF) == before


@pytest.mark.spec("CID-05-IT-01")
def test_st_0368_claim_with_remote_uses_that_remote_not_origin(
    env, tmp_path, remote, clone
):
    _set_counter(env, remote, "start=1000", "ST=1012")
    other = _bare(env, tmp_path / "other.git")
    _set_counter(env, other, "start=1000", "ST=1040")
    result = run(env, clone, "ST", "--remote", str(other))
    assert result.stdout == "ST-1041\n", result.stderr
    assert "ST=1012" in _counter(env, remote)


@pytest.mark.spec("CID-05-IT-02")
def test_st_0368_claim_with_remote_works_outside_any_clone(env, tmp_path, remote):
    _set_counter(env, remote, "start=1000", "ST=1012")
    outside = tmp_path / "outside"
    outside.mkdir()
    result = run(env, outside, "ST", "--remote", str(remote))
    assert result.returncode == 0, result.stderr
    assert result.stdout == "ST-1013\n"
    assert "ST=1013" in _counter(env, remote)


def _clone_state(env: dict[str, str], clone: Path) -> tuple[str, str]:
    refs = _git(env, "-C", str(clone), "for-each-ref")
    objects = _git(
        env, "-C", str(clone), "cat-file", "--batch-all-objects", "--batch-check"
    )
    return refs, objects


@pytest.mark.spec("CID-06-IT-01")
class TestClaimLeavesTheCloneUnchanged:
    @pytest.fixture
    def committed_clone(self, env, clone):
        (clone / "README.md").write_text("clone\n")
        _git(env, "-C", str(clone), "add", "README.md")
        _git(
            env,
            "-C",
            str(clone),
            "commit",
            "--quiet",
            "-m",
            "init",
            extra=FIXTURE_IDENTITY,
        )
        return clone

    def test_st_0368_successful_claim_adds_no_ref_and_no_object(
        self, env, remote, committed_clone
    ):
        _set_counter(env, remote, "start=1000", "ST=1012")
        before = _clone_state(env, committed_clone)
        assert run(env, committed_clone, "BUG").stdout == "BUG-1001\n"
        assert _clone_state(env, committed_clone) == before

    def test_st_0368_failed_claim_adds_no_ref_and_no_object(self, env, committed_clone):
        before = _clone_state(env, committed_clone)
        result = run(env, committed_clone, "ST")
        assert result.returncode != 0
        assert result.stdout == ""
        assert _clone_state(env, committed_clone) == before


@pytest.mark.spec("CID-06-IT-02")
class TestClaimDeletesItsThrowawayRepository:
    def test_st_0368_tmpdir_empty_after_successful_claim(
        self, env, tmp_path, remote, clone
    ):
        _set_counter(env, remote, "start=1000")
        tmpdir = tmp_path / "tmpdir"
        tmpdir.mkdir()
        result = run({**env, "TMPDIR": str(tmpdir)}, clone, "ST")
        assert result.returncode == 0, result.stderr
        assert list(tmpdir.iterdir()) == []

    def test_st_0368_tmpdir_empty_after_claim_on_missing_counter(
        self, env, tmp_path, clone
    ):
        tmpdir = tmp_path / "tmpdir"
        tmpdir.mkdir()
        result = run({**env, "TMPDIR": str(tmpdir)}, clone, "ST")
        assert result.returncode != 0
        assert result.stdout == ""
        assert list(tmpdir.iterdir()) == []


# --- smoke test ----------------------------------------------------------------


def test_st_0368_demo_scenario_end_to_end(env, remote, clone, tmp_path):
    assert run(env, clone, "--seed", "1000", "ADR=6").returncode == 0
    again = run(env, clone, "--seed", "1000")
    assert again.returncode != 0
    assert str(remote) in again.stderr
    assert [run(env, clone, "ST").stdout, run(env, clone, "ST").stdout] == [
        "ST-1001\n",
        "ST-1002\n",
    ]
    assert run(env, clone, "ADR").stdout == "ADR-0007\n"
    refused = run(env, clone, "PROP")
    assert refused.returncode != 0
    assert refused.stdout == ""
    assert "'PROP'" in refused.stderr
    outside = tmp_path / "outside"
    outside.mkdir()
    assert run(env, outside, "FAGAN", "--remote", str(remote)).stdout == "FAGAN-1001\n"


@pytest.mark.spec("CID-08-IT-01")
def test_st_0373_two_branches_get_different_ids_and_commit_on_their_own(env, tmp_path, remote):
    first = tmp_path / "a"
    second = tmp_path / "b"
    _git(env, "clone", "--quiet", str(remote), str(first))
    _git(env, "checkout", "--quiet", "-b", "dev", cwd=first)
    _git(env, "commit", "--quiet", "--allow-empty", "-m", "init", cwd=first, extra=FIXTURE_IDENTITY)
    _git(env, "push", "--quiet", "origin", "dev", cwd=first)
    assert run(env, first, "--seed", "1000").returncode == 0
    _git(env, "clone", "--quiet", "--branch", "dev", str(remote), str(second))
    _git(env, "checkout", "--quiet", "-b", "feature/counter-ids", cwd=second)

    ids = {}
    for clone_path, branch in ((first, "dev"), (second, "feature/counter-ids")):
        claimed = run(env, clone_path, "IMPL")
        assert claimed.returncode == 0
        claim = claimed.stdout.strip()
        ids[branch] = claim
        finding = clone_path / "docs" / "findings" / f"{claim}.md"
        finding.parent.mkdir(parents=True, exist_ok=True)
        finding.write_text(f"# {claim}\n")
        _git(env, "add", str(finding), cwd=clone_path)
        _git(env, "commit", "--quiet", "-m", f"add {claim}", cwd=clone_path, extra=FIXTURE_IDENTITY)

    assert ids == {"dev": "IMPL-1001", "feature/counter-ids": "IMPL-1002"}
    for clone_path, branch, other in (
        (first, "dev", "IMPL-1002"),
        (second, "feature/counter-ids", "IMPL-1001"),
    ):
        tracked = _git(env, "ls-tree", "-r", "--name-only", branch, cwd=clone_path).splitlines()
        assert f"docs/findings/{ids[branch]}.md" in tracked
        assert f"docs/findings/{other}.md" not in tracked


# --- a failed claim names its cause (ST-0370) ----------------------------------


def _closed_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def _http_server(status: int, headers: dict[str, str] | None = None):
    """Answer every request with one status; yield the base URL."""

    class Handler(http.server.BaseHTTPRequestHandler):
        def _answer(self):
            self.send_response(status)
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.send_header("Content-Length", "0")
            self.end_headers()

        do_GET = do_POST = do_HEAD = _answer

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/remote.git"
    finally:
        server.shutdown()
        server.server_close()


def _assert_failed_claim(result, *names: str) -> None:
    assert result.returncode != 0
    assert result.stdout == ""
    for name in names:
        assert name in result.stderr


@pytest.mark.spec("CID-04-IT-03")
class TestClaimOnARemoteThatCannotAnswer:
    def test_st_0370_remote_without_the_counter_names_the_seed(
        self, env, tmp_path, remote
    ):
        result = run(env, tmp_path, "ST", "--remote", str(remote))
        _assert_failed_claim(result, str(remote), "next-id --seed")
        assert not _has_ref(env, remote)

    def test_st_0370_closed_port_names_the_remote_and_git_error(self, env, tmp_path):
        url = f"http://127.0.0.1:{_closed_port()}/remote.git"
        result = run(env, tmp_path, "ST", "--remote", url)
        _assert_failed_claim(result, url, "unable to access")

    def test_st_0370_clone_without_origin_names_origin_remote_and_seed(
        self, env, tmp_path
    ):
        # Precondition: no origin and no agent-factory.counterRemote (ST-0379).
        repo = tmp_path / "no-origin"
        _git(env, "init", "--quiet", str(repo))
        unset = subprocess.run(
            ["git", "-C", str(repo), "config", "--get", "agent-factory.counterRemote"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert unset.returncode == 1
        result = run(env, repo, "ST")
        _assert_failed_claim(result, "`origin`", "--remote", "next-id --seed")

    def test_st_0370_remote_answering_403_names_the_remote_and_git_error(
        self, env, tmp_path
    ):
        with _http_server(403) as url:
            result = run(env, tmp_path, "ST", "--remote", url)
        _assert_failed_claim(result, url, "403")


@pytest.mark.spec("CID-04-IT-04")
def test_st_0370_password_server_gets_no_prompt(env, tmp_path):
    asking = {**env, "GIT_TERMINAL_PROMPT": "1"}
    with _http_server(401, {"WWW-Authenticate": 'Basic realm="x"'}) as url:
        result = subprocess.run(
            [sys.executable, str(NEXT_ID), "ST", "--remote", url],
            cwd=tmp_path,
            env=asking,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
    _assert_failed_claim(result, url, "terminal prompts disabled")
    assert len(result.stderr.strip().splitlines()) == 1


@pytest.mark.spec("CID-04-IT-05")
class TestEveryGitCallOfAClaimRunsWithoutPromptsAndWithALimit:
    @pytest.fixture
    def calls(self, monkeypatch, remote, env):
        _set_counter(env, remote, "start=1000")
        monkeypatch.setenv("HOME", env["HOME"])
        monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
        seen: list[dict] = []
        real = subprocess.run

        def spy(cmd, **kwargs):
            if cmd[1:2] != ["config"]:
                seen.append(kwargs)
            return real(cmd, **kwargs)

        monkeypatch.setattr(ni.subprocess, "run", spy)
        return seen

    def test_st_0370_claim_calls_carry_the_environment_and_the_limit(
        self, calls, remote, monkeypatch
    ):
        monkeypatch.delenv("GIT_TERMINAL_PROMPT", raising=False)
        monkeypatch.delenv("GIT_SSH_COMMAND", raising=False)
        assert ni.claim("ST", str(remote)) == "ST-1001"
        assert calls
        for kwargs in calls:
            assert kwargs["timeout"] == 30
            assert kwargs["env"]["GIT_TERMINAL_PROMPT"] == "0"
            assert kwargs["env"]["GIT_SSH_COMMAND"] == "ssh -o BatchMode=yes"

    def test_st_0370_seed_keeps_prompts_and_has_no_limit(
        self, calls, tmp_path, env, monkeypatch
    ):
        monkeypatch.delenv("GIT_TERMINAL_PROMPT", raising=False)
        monkeypatch.delenv("GIT_SSH_COMMAND", raising=False)
        fresh = _bare(env, tmp_path / "fresh.git")
        calls.clear()
        ni.seed(["1000"], str(fresh))
        assert calls
        for kwargs in calls:
            assert kwargs.get("timeout") is None
            assert "GIT_TERMINAL_PROMPT" not in kwargs["env"]
            assert "GIT_SSH_COMMAND" not in kwargs["env"]


@pytest.mark.spec("CID-04-IT-05")
class TestAClaimKeepsTheSshCommandOfTheUser:
    """IMPL-0004: BatchMode joins the ssh command git would run; it never replaces it."""

    @pytest.fixture
    def recorded(self, tmp_path, env, monkeypatch):
        log = tmp_path / "ssh-calls.log"
        script = tmp_path / "custom-ssh"
        script.write_text(f'#!/bin/sh\necho "$@" >> {log}\nexit 255\n')
        script.chmod(0o755)
        monkeypatch.setenv("HOME", env["HOME"])
        monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
        monkeypatch.delenv("GIT_SSH_COMMAND", raising=False)
        return script, log

    def test_impl_0004_core_ssh_command_runs_with_batch_mode(self, recorded, env):
        script, log = recorded
        _git(env, "config", "--global", "core.sshCommand", str(script))
        url = "ssh://git@example.invalid/x.git"
        with pytest.raises(ni.NextIdError):
            ni.claim("ST", url)
        assert "-o BatchMode=yes" in log.read_text()

    def test_impl_0004_environment_command_wins_over_core_ssh_command(
        self, recorded, env, monkeypatch, tmp_path
    ):
        script, log = recorded
        _git(env, "config", "--global", "core.sshCommand", "false")
        monkeypatch.setenv("GIT_SSH_COMMAND", str(script))
        with pytest.raises(ni.NextIdError):
            ni.claim("ST", "ssh://git@example.invalid/x.git")
        assert "-o BatchMode=yes" in log.read_text()

    def test_impl_0004_without_any_setting_the_command_is_plain_ssh(self, recorded):
        assert ni.ssh_command_with_batch_mode() == "ssh -o BatchMode=yes"


@pytest.mark.spec("CID-04-IT-06")
def test_st_0370_git_call_over_the_limit_ends_the_claim(
    remote, env, monkeypatch, capsys
):
    _set_counter(env, remote, "start=1000")
    monkeypatch.setenv("HOME", env["HOME"])
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    real = subprocess.run

    def slow_fetch(cmd, **kwargs):
        if "fetch" in cmd:
            raise subprocess.TimeoutExpired(cmd, kwargs["timeout"])
        return real(cmd, **kwargs)

    monkeypatch.setattr(ni.subprocess, "run", slow_fetch)
    assert ni.main(["ST", "--remote", str(remote)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert str(remote) in captured.err
    assert "30 seconds" in captured.err
    assert _counter(env, remote) == ["start=1000", "token=fixture0000000000"]


# --- the local counter without origin (ST-0379, BR-096) ----------------------

SETTING = "agent-factory.counterRemote"


def _project(env: dict[str, str], path: Path) -> Path:
    """A project repository without origin, its main branch holding one commit."""
    _git(env, "init", "--quiet", str(path))
    _git(
        env,
        "-C",
        str(path),
        "commit",
        "--quiet",
        "--allow-empty",
        "-m",
        "root",
        extra=FIXTURE_IDENTITY,
    )
    return path


class StubGit:
    """A stand-in for ni.git that answers the two lookups of resolve_remote."""

    def __init__(self, setting: str | None, origin: str | None):
        self.setting, self.origin, self.calls = setting, origin, []

    def __call__(self, args, **kwargs):
        self.calls.append(list(args))
        answers = {
            ("config", "--get", SETTING): self.setting,
            ("remote", "get-url", "origin"): self.origin,
        }
        answer = answers.get(tuple(args))
        if answer is None:
            raise subprocess.CalledProcessError(1, ["git", *args])
        return answer


@pytest.mark.spec("CIF-08-CT-01")
@pytest.mark.parametrize("for_seed", [False, True])
class TestRemoteResolutionOrder:
    def test_st_0379_remote_option_wins_over_setting_and_origin(
        self, monkeypatch, for_seed
    ):
        stub = StubGit("/work/demo", "/tmp/origin.git")
        monkeypatch.setattr(ni, "git", stub)
        assert ni.resolve_remote("/tmp/remote.git", for_seed=for_seed) == "/tmp/remote.git"

    def test_st_0379_setting_wins_over_origin(self, monkeypatch, for_seed):
        stub = StubGit("/work/demo", "/tmp/origin.git")
        monkeypatch.setattr(ni, "git", stub)
        assert ni.resolve_remote(None, for_seed=for_seed) == "/work/demo"

    def test_st_0379_origin_is_the_last_resort(self, monkeypatch, for_seed):
        stub = StubGit(None, "/tmp/origin.git")
        monkeypatch.setattr(ni, "git", stub)
        assert ni.resolve_remote(None, for_seed=for_seed) == "/tmp/origin.git"

    def test_st_0379_none_of_the_three_names_origin_and_remote(
        self, monkeypatch, for_seed
    ):
        monkeypatch.setattr(ni, "git", StubGit(None, None))
        with pytest.raises(ni.NextIdError) as caught:
            ni.resolve_remote(None, for_seed=for_seed)
        assert "`origin`" in str(caught.value)
        assert "--remote" in str(caught.value)


@pytest.mark.spec("CIF-08-IT-01")
def test_st_0379_claim_from_local_counter_writes_into_the_project_git(env, tmp_path):
    project = _project(env, tmp_path / "demo")
    _set_counter(env, project / ".git", "start=0000", "ST=0012")
    _git(env, "-C", str(project), "config", SETTING, str(project))
    result = run(env, project, "ST")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ST-0013"
    assert "ST=0013" in _counter(env, project / ".git")
    refs = _git(env, "-C", str(project), "for-each-ref", "--format=%(refname)").split()
    assert [r for r in refs if r.startswith("refs/ids")] == [REF]


@pytest.mark.spec("CIF-08-IT-02")
def test_st_0379_three_counters_setting_wins_and_remote_option_wins_over_it(
    env, tmp_path, remote
):
    origin = _bare(env, tmp_path / "origin.git")
    _set_counter(env, origin, "start=0000", "ST=0040")
    _set_counter(env, remote, "start=0000", "ST=0070")
    project = _project(env, tmp_path / "demo")
    _set_counter(env, project / ".git", "start=0000", "ST=0012")
    _git(env, "-C", str(project), "remote", "add", "origin", str(origin))
    _git(env, "-C", str(project), "config", SETTING, str(project))
    first = run(env, project, "ST")
    assert first.stdout.strip() == "ST-0013", first.stderr
    second = run(env, project, "ST", "--remote", str(remote))
    assert second.stdout.strip() == "ST-0071", second.stderr
    assert "ST=0040" in _counter(env, origin)


@pytest.mark.spec("CIF-02-IT-01")
def test_st_0379_seed_and_claim_from_a_second_worktree_use_the_main_git(env, tmp_path):
    project = _project(env, tmp_path / "demo")
    worktree = tmp_path / "demo-feature"
    _git(env, "-C", str(project), "worktree", "add", "--quiet", "-b", "feature/local", str(worktree))
    common = _git(env, "-C", str(worktree), "rev-parse", "--path-format=absolute", "--git-common-dir")
    main = Path(common).parent
    assert main.resolve() == project.resolve()
    _git(env, "-C", str(worktree), "config", SETTING, str(main))
    plan = run(env, worktree, "--plan-seed")
    assert plan.returncode == 0, plan.stderr
    assert "next-id --seed" in plan.stdout
    seeded = run(env, worktree, "--seed", "0", "ST=12")
    assert seeded.returncode == 0, seeded.stderr
    assert _has_ref(env, project / ".git")
    assert run(env, worktree, "ST").stdout.strip() == "ST-0013"
    assert run(env, project, "ST").stdout.strip() == "ST-0014"


# --- the marker of a moved counter (ST-0380, BR-097) --------------------------

MADE_UP_URL = "https://user:token@host/demo.git"
SHOWN_URL = "https://***@host/demo.git"


def _set_marker(env: dict[str, str], repo: Path, remote_url: str) -> str:
    """Put a marker commit, with the counter as its parent, at the repository's counter."""
    tree = _git(env, "-C", str(repo), "mktree")
    sha = subprocess.run(
        ["git", "-C", str(repo), "commit-tree", tree, "-p", REF],
        input=ni.format_marker(remote_url),
        env={**env, **FIXTURE_IDENTITY},
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _git(env, "-C", str(repo), "update-ref", REF, sha)
    return sha


def _moved_project(env: dict[str, str], tmp_path: Path) -> tuple[Path, Path]:
    """The project /work/demo with the marker, and a local clone whose origin it is."""
    project = _project(env, tmp_path / "demo")
    _set_counter(env, project / ".git", "start=0000", "ST=0012")
    _set_marker(env, project, MADE_UP_URL)
    local_clone = tmp_path / "demo-clone"
    _git(env, "clone", "--quiet", str(project), str(local_clone))
    return project, local_clone


@pytest.mark.spec("CIF-10-CT-01")
class TestMarkerMessage:
    def test_st_0380_marker_is_one_redacted_line(self):
        assert ni.format_marker(MADE_UP_URL) == f"moved={SHOWN_URL}\n"

    def test_st_0380_reader_extracts_the_remote_of_a_marker(self):
        assert ni.marker_remote(ni.format_marker(MADE_UP_URL)) == SHOWN_URL

    def test_st_0380_a_claim_commit_is_no_marker(self):
        assert ni.marker_remote("start=0000\nST=0012\ntoken=abc\n") is None

    def test_st_0380_reader_of_a_counter_names_the_remote_of_the_marker(
        self, env, remote, monkeypatch
    ):
        monkeypatch.setenv("HOME", env["HOME"])
        monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
        _set_counter(env, remote, "start=0000", "ST=0012")
        _set_marker(env, remote, MADE_UP_URL)
        with ni.throwaway(guarded=True) as repo, pytest.raises(ni.MovedCounter) as caught:
            ni.RemoteCounter(repo, str(remote)).read()
        assert caught.value.remote == SHOWN_URL
        assert SHOWN_URL in str(caught.value)
        assert "--seed" not in str(caught.value)


@pytest.mark.spec("CIF-08-IT-04")
def test_st_0380_a_claim_in_a_local_clone_names_the_remote_of_the_marker(env, tmp_path):
    project, local_clone = _moved_project(env, tmp_path)
    before = _git(env, "-C", str(project), "rev-parse", REF)

    result = run(env, local_clone, "ST")

    _assert_failed_claim(result, SHOWN_URL)
    assert "--seed" not in result.stderr
    assert "user:token" not in result.stderr
    assert _git(env, "-C", str(project), "rev-parse", REF) == before
