"""Tests for next-id: the seed and the ID claim (ST-0368, counter-ids.feature).

Every remote is a local bare repository in tmp_path. Each subprocess runs with
HOME set to an empty directory, GIT_CONFIG_NOSYSTEM=1, and
GIT_TERMINAL_PROMPT=0, so no global identity, URL rewrite, or prompt reaches
a test (QA strategy, Test setup).
"""

from __future__ import annotations

import os
import re
import socket
import subprocess
import sys
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
                ["'XX'", "ST, BUG, SPEC, FAGAN, SEC, RECON, ATAM, IMPL, T, ADR"],
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

    def test_st_0368_prefix_list_holds_the_ten_prefixes(self):
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
        )


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
    "prefix", ["ST", "BUG", "SPEC", "FAGAN", "SEC", "RECON", "ATAM", "IMPL", "T", "ADR"]
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
