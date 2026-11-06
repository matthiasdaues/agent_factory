"""Tests for claims of next-id at the same time (ST-0369, counter-ids.feature).

Every remote is a local bare repository in tmp_path, and every subprocess runs
with HOME set to an empty directory, as in test_next_id.py. So each test has
its own repository and the tests run in parallel under `-n auto`.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import next_id_race as race
import pytest

HARNESS = Path(race.__file__)


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


@pytest.fixture
def remote(tmp_path: Path, env: dict[str, str]) -> Path:
    path = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--quiet", "--bare", str(path)], env=env, check=True)
    return path


# --- contract tests of the harness ---------------------------------------------


class TestHarnessCheck:
    def _result(self, *ids: str, counter: dict[str, int]) -> race.RaceResult:
        calls = [race.Call(1, "a", i.split("-")[0], 0, f"{i}\n", "") for i in ids]
        return race.RaceResult(calls=calls, counter=counter)

    def test_st_0369_round_plan_claims_st_twice_in_odd_rounds(self):
        assert [race.round_plan(n) for n in (1, 2, 3, 4)] == [
            ("ST", "ST"),
            ("ST", "FAGAN"),
            ("ST", "ST"),
            ("ST", "FAGAN"),
        ]

    def test_st_0369_check_passes_contiguous_ids(self):
        result = self._result(
            "ST-1001", "ST-1002", "FAGAN-1001", counter={"ST": 1002, "FAGAN": 1001}
        )
        race.check(result)
        assert result.ok

    def test_st_0369_check_finds_a_skipped_number(self):
        result = self._result("ST-1001", "ST-1003", counter={"ST": 1003})
        race.check(result)
        assert result.problems == ["ST numbers skipped: [1002]"]

    def test_st_0369_check_finds_a_duplicate(self):
        result = self._result("ST-1001", "ST-1001", counter={"ST": 1001})
        race.check(result)
        assert "IDs handed out twice: ST-1001" in result.problems

    def test_st_0369_check_finds_a_failed_call_and_a_wrong_counter(self):
        result = self._result("ST-1001", counter={"ST": 1002})
        result.calls.append(race.Call(1, "b", "ST", 1, "", "next-id: refused\n"))
        race.check(result)
        assert result.problems == [
            "round 1, clone b: ST exited 1: next-id: refused",
            "the counter holds ST=1002, the highest ST printed is 1001",
        ]

    def test_st_0369_usage_says_a_remote_needs_a_free_counter_and_cleanup(self, capsys):
        with pytest.raises(SystemExit):
            race.main(["--help"])
        out = capsys.readouterr().out
        assert "--rounds" in out
        assert "--remote" in out
        assert "without a counter in use" in out
        assert "delete refs/ids/counters" in out


# --- integration tests ----------------------------------------------------------


@pytest.mark.spec("CID-03-IT-01")
def test_st_0369_race_of_20_rounds_hands_out_no_id_twice_and_skips_none(env, remote):
    result = race.run_race(20, str(remote), env)
    assert result.ok, race.report(result)
    assert len(result.calls) == 40
    assert all(call.code == 0 for call in result.calls)
    ids = [call.out.strip() for call in result.calls]
    assert len(set(ids)) == 40
    assert result.counter["ST"] == 1030
    assert result.counter["FAGAN"] == 1010


def test_st_0369_eight_claims_at_once_all_get_their_own_id(env, tmp_path, remote):
    """QS-19: eight parallel claims of mixed prefixes all succeed."""
    seed = subprocess.run(
        [sys.executable, str(race.NEXT_ID), "--seed", "1000", "--remote", str(remote)],
        env=env,
        capture_output=True,
        text=True,
    )
    assert seed.returncode == 0, seed.stderr
    prefixes = ["ST", "ST", "ST", "FAGAN", "FAGAN", "BUG", "BUG", "ADR"]
    procs = [
        subprocess.Popen(
            [sys.executable, str(race.NEXT_ID), prefix, "--remote", str(remote)],
            cwd=tmp_path,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for prefix in prefixes
    ]
    outcomes = [(p.communicate(timeout=120), p.returncode) for p in procs]
    errors = [err for (_, err), _ in outcomes if err]
    assert [code for _, code in outcomes] == [0] * 8, errors
    ids = [out.strip() for (out, _), _ in outcomes]
    assert len(set(ids)) == 8
    assert not any("ten stale leases" in err for err in errors)
    assert sorted(ids) == sorted(
        [
            "ST-1001",
            "ST-1002",
            "ST-1003",
            "FAGAN-1001",
            "FAGAN-1002",
            "BUG-1001",
            "BUG-1002",
            "ADR-1001",
        ]
    )
    counter = race._read_counter(str(remote), tmp_path, env)
    assert counter == {
        "start": 1000,
        "ST": 1003,
        "FAGAN": 1002,
        "BUG": 1002,
        "ADR": 1001,
    }


# --- smoke test -----------------------------------------------------------------


def test_st_0369_harness_runs_on_its_own_bare_repository(env):
    result = subprocess.run(
        [sys.executable, str(HARNESS), "--rounds", "2"],
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Calls with exit 0: 4 of 4" in result.stdout
    assert "Result: OK" in result.stdout
