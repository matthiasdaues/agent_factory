"""Tests for next-id --plan-seed (ST-0376, counter-ids-fitting.feature).

The mode checks the remote as an ID claim does, then prints one seed command
from the highest number of each ID prefix on every local branch, every
remote-tracking branch, and the working tree. Every remote is a local bare
repository in tmp_path, and every subprocess runs with the `env` fixture of
test_next_id.py (QA strategy, Test setup).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from test_next_id import (  # noqa: F401
    FIXTURE_IDENTITY,
    NEXT_ID,
    SHOWN_URL,
    _git,
    _moved_project,
    _set_counter,
    clone,
    env,
    ni,
    remote,
    run,
)

ADR_32 = "docs/adr/0032-agents-push-the-claim-ref-through-next-id.md"
ATAM_TITLED = "docs/findings/ATAM-0014-some-title.md"


# --- helpers ------------------------------------------------------------------


def _write(repo: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def _commit(env: dict[str, str], repo: Path, files: dict[str, str]) -> None:
    _write(repo, files)
    _git(env, "-C", str(repo), "add", "--all")
    _git(env, "-C", str(repo), "commit", "--quiet", "-m", "fixture", extra=FIXTURE_IDENTITY)


def _branch(env: dict[str, str], repo: Path, name: str) -> None:
    _git(env, "-C", str(repo), "checkout", "--quiet", "-b", name)


def _refs(env: dict[str, str], *repos: Path) -> list[str]:
    return [_git(env, "-C", str(repo), "for-each-ref") for repo in repos]


def _plan(files: dict[str, str]) -> tuple[str, list[str]]:
    return ni.plan(ni.ids_in_tree(files, files.__getitem__))


# --- contract tests -----------------------------------------------------------


@pytest.mark.spec("CIF-05-CT-01")
class TestCountingRules:
    @pytest.mark.parametrize(
        ("files", "command"),
        [
            pytest.param(
                {"backlog/ST-0214.md": "An example is ST-9999.\n", "backlog/ST-0375.md": ""},
                "next-id --seed 0 ST=375",
                id="body-text-never-counts",
            ),
            pytest.param(
                {"docs/findings/BUG-0003.md": "", "docs/findings/BUG-0012.md": ""},
                "next-id --seed 0 BUG=12",
                id="a-gap-does-not-lower-the-pair",
            ),
            pytest.param(
                {
                    "docs/findings/FAGAN-0004.md": "",
                    "docs/findings/register/code.jsonl": json.dumps({"id": "FAGAN-0007"})
                    + "\n",
                },
                "next-id --seed 0 FAGAN=7",
                id="a-register-line-counts",
            ),
            pytest.param(
                {"docs/spec/work/todo.md": "# Todo\n\n## T-0016\n\n## T-0017 — A title\n"},
                "next-id --seed 0 T=17",
                id="a-todo-heading-counts",
            ),
            pytest.param(
                {"backlog/ST-0375.md": ""},
                "next-id --seed 0 ST=375",
                id="a-prefix-without-an-id-gets-no-pair",
            ),
            pytest.param({}, "next-id --seed 0", id="no-indexed-artifact"),
            pytest.param(
                {
                    "docs/adr/0031-x.md": "",
                    ADR_32: "",
                    "docs/findings/IMPL-0002.md": "",
                    "backlog/ST-0001.md": "",
                    "docs/spec/work/todo.md": "## T-0003\n",
                },
                "next-id --seed 0 ST=1 IMPL=2 T=3 ADR=32",
                id="pairs-follow-the-order-of-PREFIXES",
            ),
        ],
    )
    def test_st_0376_the_command_holds_the_highest_number(self, files, command):
        assert _plan(files)[0] == command

    def test_st_0376_only_registers_and_the_todo_file_are_read(self):
        files = {
            "backlog/ST-0214.md": "ST-9999",
            "docs/findings/BUG-0001.md": "BUG-9999",
            "docs/findings/register/code.jsonl": '{"id": "SEC-0002"}\n',
            "docs/spec/work/todo.md": "## T-0001\n",
            "docs/spec/work/other.md": "## T-9999\n",
            "README.md": "ST-9999",
        }
        read: list[str] = []

        def reader(path: str) -> str:
            read.append(path)
            return files[path]

        command, _ = ni.plan(ni.ids_in_tree(files, reader))
        assert command == "next-id --seed 0 ST=214 BUG=1 SEC=2 T=1"
        assert sorted(read) == ["docs/findings/register/code.jsonl", "docs/spec/work/todo.md"]

    @pytest.mark.parametrize(
        "line",
        ["not json", '["FAGAN-0009"]', '{"title": "FAGAN-0009"}', '{"id": "FAGAN-HUNT"}', ""],
    )
    def test_st_0376_a_register_line_without_an_id_counts_nothing(self, line):
        files = {"docs/findings/register/code.jsonl": line + "\n"}
        assert _plan(files)[0] == "next-id --seed 0"

    def test_st_0376_a_todo_line_that_is_no_heading_counts_nothing(self):
        files = {"docs/spec/work/todo.md": "See ## T-0009.\n### T-0008\n## T-0002\n"}
        assert _plan(files)[0] == "next-id --seed 0 T=2"


@pytest.mark.spec("CIF-06-CT-01")
class TestOldFileNames:
    @pytest.mark.parametrize(
        ("path", "counted"),
        [
            (ATAM_TITLED, ("ATAM", 14, True)),
            ("docs/findings/SPEC-011-title.md", ("SPEC", 11, True)),
            ("backlog/ST-0380A.md", ("ST", 380, False)),
            ("backlog/ST-0375.md", ("ST", 375, False)),
            ("docs/findings/BUG-HUNT.md", None),
            ("docs/findings/RECON-cycle-retirement.md", None),
            ("docs/findings/PROP-0001.md", None),
            (ADR_32, ("ADR", 32, False)),
            ("docs/adr/README.md", None),
            ("docs/adr/032-short.md", None),
            ("backlog/epics.md", None),
            ("docs/findings/register/ST-0999.md", None),
            ("docs/spec/ST-0999.md", None),
        ],
    )
    def test_st_0376_a_name_counts_by_its_number(self, path, counted):
        assert ni.count_name(path) == counted

    def test_st_0376_each_old_name_gets_one_warning(self):
        files = {ATAM_TITLED: "", "backlog/ST-0380A.md": "", "docs/findings/BUG-HUNT.md": ""}
        found = [*ni.ids_in_tree(files, files.__getitem__)] * 2
        assert ni.plan(found) == ("next-id --seed 0 ST=380 ATAM=14", [ATAM_TITLED])


@pytest.mark.spec("CIF-05-CT-01")
class TestRegisterFileNames:
    def test_st_0404_a_register_file_name_counts_and_its_body_is_never_read(self):
        files = {
            "docs/findings/register/security/SEC-0012.json": "SEC-9999",
            "docs/findings/register/code/notes.json": "IMPL-9999",
        }

        def reader(path: str) -> str:
            raise AssertionError(f"read {path}")

        found = list(ni.ids_in_tree(files, reader))
        assert found == [("SEC", 12, None)]

    def test_st_0404_a_jsonl_line_still_counts_beside_a_register_file(self):
        files = {
            "docs/findings/register/security/SEC-0012.json": "{}",
            "docs/findings/register/code.jsonl": json.dumps({"id": "IMPL-0007"}) + "\n",
        }
        assert _plan(files)[0] == "next-id --seed 0 SEC=12 IMPL=7"


# --- integration tests --------------------------------------------------------


@pytest.mark.spec("CIF-05-IT-01")
def test_st_0376_every_branch_counts_and_no_ref_changes(env, remote, clone):
    _branch(env, clone, "dev")
    _commit(env, clone, {"backlog/ST-0375.md": "", "docs/adr/0031-x.md": ""})
    _branch(env, clone, "feature/adr")
    _commit(env, clone, {ADR_32: ""})
    _git(env, "-C", str(clone), "checkout", "--quiet", "dev")
    _branch(env, clone, "feature/fitting")
    _commit(env, clone, {"backlog/ST-0380.md": ""})
    _git(env, "-C", str(clone), "push", "--quiet", "origin", "feature/fitting")
    _git(env, "-C", str(clone), "checkout", "--quiet", "dev")
    _git(env, "-C", str(clone), "branch", "--quiet", "-D", "feature/fitting")
    before = _refs(env, clone, remote)

    result = run(env, clone, "--plan-seed")

    assert result.returncode == 0, result.stderr
    assert result.stdout == "next-id --seed 0 ST=380 ADR=32\n"
    assert _refs(env, clone, remote) == before


@pytest.mark.spec("CIF-05-IT-01")
def test_st_0404_a_register_file_on_a_remote_tracking_branch_counts(env, remote, clone):
    _branch(env, clone, "dev")
    _commit(env, clone, {"docs/findings/SEC-0005.md": ""})
    _branch(env, clone, "feature/register")
    _commit(env, clone, {"docs/findings/register/security/SEC-0012.json": "{}"})
    _git(env, "-C", str(clone), "push", "--quiet", "origin", "feature/register")
    _git(env, "-C", str(clone), "checkout", "--quiet", "dev")
    _git(env, "-C", str(clone), "branch", "--quiet", "-D", "feature/register")
    before = _refs(env, clone, remote)

    result = run(env, clone, "--plan-seed")

    assert result.returncode == 0, result.stderr
    assert result.stdout == "next-id --seed 0 SEC=12\n"
    assert _refs(env, clone, remote) == before


@pytest.mark.spec("CIF-05-IT-01")
def test_st_0404_an_uncommitted_register_file_counts(env, clone):
    _commit(env, clone, {"backlog/ST-0375.md": ""})
    _write(clone, {"docs/findings/register/code/IMPL-0021.json": "{}"})

    result = run(env, clone, "--plan-seed")

    assert result.returncode == 0, result.stderr
    assert result.stdout == "next-id --seed 0 ST=375 IMPL=21\n"


@pytest.mark.spec("CIF-06-IT-01")
def test_st_0376_an_old_name_gets_a_warning_on_standard_error(env, clone):
    _commit(env, clone, {ATAM_TITLED: "", "backlog/ST-0380A.md": "", "docs/findings/BUG-HUNT.md": ""})

    result = run(env, clone, "--plan-seed")

    assert result.returncode == 0, result.stderr
    assert result.stdout == "next-id --seed 0 ST=380 ATAM=14\n"
    warnings = result.stderr.splitlines()
    assert len(warnings) == 1, result.stderr
    assert ATAM_TITLED in warnings[0]
    assert "ST-0380A" not in result.stderr
    assert "BUG-HUNT" not in result.stderr


def test_st_0376_an_uncommitted_story_file_counts(env, clone):
    _commit(env, clone, {"backlog/ST-0375.md": ""})
    _write(clone, {"backlog/ST-0390.md": ""})
    status = _git(env, "-C", str(clone), "status", "--porcelain", "--untracked-files=all")

    result = run(env, clone, "--plan-seed")

    assert result.returncode == 0, result.stderr
    assert result.stdout == "next-id --seed 0 ST=390\n"
    assert _git(env, "-C", str(clone), "status", "--porcelain", "--untracked-files=all") == status


@pytest.mark.spec("CIF-07-IT-01")
def test_st_0376_a_counter_in_use_ends_the_mode_without_a_command(env, remote, clone):
    _set_counter(env, remote, "start=1000", "ST=1012")
    _commit(env, clone, {"backlog/ST-0375.md": ""})

    result = run(env, clone, "--plan-seed")

    assert result.returncode == 0, result.stderr
    assert "in use" in result.stdout
    assert str(remote) in result.stdout
    assert "--seed" not in result.stdout


@pytest.mark.spec("CIF-07-IT-02")
def test_st_0376_a_clone_without_origin_prints_no_command(env, tmp_path):
    repo = tmp_path / "no-origin"
    _git(env, "init", "--quiet", str(repo))

    result = run(env, repo, "--plan-seed")

    assert result.returncode != 0
    assert result.stdout == ""
    assert "origin" in result.stderr
    assert "--remote" in result.stderr


def _run_printed(env: dict[str, str], cwd: Path, command: str) -> None:
    words = command.split()
    assert words[:3] == ["next-id", "--seed", "0"], command
    seeded = run(env, cwd, *words[1:])
    assert seeded.returncode == 0, seeded.stderr


@pytest.mark.spec("CIF-01-IT-01")
def test_st_0376_the_printed_command_seeds_and_the_next_claim_continues(env, clone):
    _commit(env, clone, {"backlog/ST-0380.md": "", ADR_32: ""})
    planned = run(env, clone, "--plan-seed")
    assert planned.returncode == 0, planned.stderr

    _run_printed(env, clone, planned.stdout.strip())

    claims = [run(env, clone, prefix).stdout for prefix in ("ST", "ADR", "BUG")]
    assert claims == ["ST-0381\n", "ADR-0033\n", "BUG-0001\n"]


@pytest.mark.spec("CIF-03-IT-01")
def test_st_0376_an_empty_project_seeds_with_zero_and_starts_at_one(env, clone):
    _commit(env, clone, {"README.md": "A project.\n"})
    planned = run(env, clone, "--plan-seed")
    assert planned.returncode == 0, planned.stderr
    assert planned.stdout == "next-id --seed 0\n"

    _run_printed(env, clone, planned.stdout.strip())

    assert run(env, clone, "ST").stdout == "ST-0001\n"


def test_st_0376_plan_seed_takes_no_prefix(env, clone):
    result = run(env, clone, "--plan-seed", "ST")

    assert result.returncode == 2
    assert result.stdout == ""


def test_st_0376_plan_seed_outside_a_repository_fails(env, tmp_path, remote):
    result = run(env, tmp_path, "--plan-seed", "--remote", str(remote))

    assert result.returncode == 1
    assert result.stdout == ""
    assert "--plan-seed" in result.stderr


def test_st_0376_usage_names_plan_seed():
    help_text = subprocess.run(
        [sys.executable, str(NEXT_ID), "--help"], capture_output=True, text=True, check=False
    ).stdout
    assert "next-id --plan-seed [--remote <url>]" in help_text


@pytest.mark.spec("CIF-07-IT-04")
def test_st_0380_a_moved_counter_names_its_remote_and_advises_no_seed(env, tmp_path):
    project, local_clone = _moved_project(env, tmp_path)
    before = _refs(env, project, local_clone)

    result = run(env, local_clone, "--plan-seed")

    assert result.returncode != 0
    assert result.stdout == ""
    assert SHOWN_URL in result.stderr
    assert "--seed" not in result.stderr
    assert "user:token" not in result.stderr
    assert _refs(env, project, local_clone) == before
