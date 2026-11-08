"""finding-lint reads the HEAD version through git (ST-0392, FC-10-IT-02).

Each test builds its own repository in tmp_path, commits the findings, and
then changes, stages, or removes them. The lint runs as a subprocess and
compares the working tree, or the index with --staged, with HEAD
(BR-109, BR-110).
"""

from __future__ import annotations

import subprocess

import pytest
from test_finding_lint import (
    BUG_PATH,
    CONFIRMED,
    FAGAN_PATH,
    OVERRIDE,
    REGISTER_PATH,
    _clean_set,
    _commit,
    _critical_fields,
    _finding_fields,
    _finding_text,
    _git,
    _major_bug,
    _register,
    _register_path,
    _repo,
    _run_in,
    _write,
)

pytestmark = pytest.mark.spec("FC-10-IT-02")


@pytest.fixture
def committed(tmp_path):
    """A repository whose HEAD holds the Demo Data of ST-0391."""
    root, env = _repo(tmp_path)
    _clean_set(root)
    _commit(root, env)
    return root, env


def _lower_fagan(root) -> None:
    _write(root, FAGAN_PATH, _finding_text(_finding_fields(severity="minor")))


def test_st_0392_a_lowering_in_the_working_tree_fails_without_staged(committed):
    root, env = committed
    _lower_fagan(root)
    result = _run_in(root, env)
    assert result.returncode == 1
    assert f"{FAGAN_PATH}: BR-109 lowering" in result.stdout


def test_st_0392_an_unstaged_lowering_is_not_seen_with_staged(committed):
    root, env = committed
    _lower_fagan(root)
    result = _run_in(root, env, "--staged")
    assert (result.returncode, result.stdout) == (0, "")


def test_st_0392_a_staged_lowering_fails_with_staged(committed):
    root, env = committed
    _lower_fagan(root)
    _git(root, env, "add", FAGAN_PATH)
    _write(root, FAGAN_PATH, _finding_text(_finding_fields()))
    result = _run_in(root, env, "--staged")
    assert result.returncode == 1
    assert f"{FAGAN_PATH}: BR-109 lowering" in result.stdout
    assert _run_in(root, env).returncode == 0


@pytest.mark.parametrize(
    ("override", "code"), [({}, 1), (OVERRIDE, 0)], ids=["no-keys", "keys"]
)
def test_st_0392_a_staged_move_of_fagan_0042_into_the_register(
    committed, override, code
):
    root, env = committed
    _git(root, env, "rm", "-q", FAGAN_PATH)
    _write(
        root,
        _register_path(name="FAGAN-0042"),
        _register(id="FAGAN-0042", **override),
    )
    _git(root, env, "add", "docs/findings/register")
    result = _run_in(root, env, "--staged")
    assert result.returncode == code, result.stdout
    if code:
        assert f"{FAGAN_PATH}: BR-109 removal" in result.stdout
        assert "FAGAN-0042" in result.stdout


def test_st_0392_a_staged_removal_of_a_register_file_fails(committed):
    root, env = committed
    _git(root, env, "rm", "-q", REGISTER_PATH)
    result = _run_in(root, env, "--staged")
    assert result.returncode == 1
    assert f"{REGISTER_PATH}: BR-110 removal" in result.stdout
    assert "FAGAN-0032" in result.stdout


def test_st_0392_the_staged_migration_of_bug_0067_passes(tmp_path):
    root, env = _repo(tmp_path)
    _write(
        root,
        "docs/findings/BUG-0067.md",
        "---\nid: BUG-0067\nseverity: Minor\nstatus: open\n---\n",
    )
    _commit(root, env)
    _git(root, env, "rm", "-q", "docs/findings/BUG-0067.md")
    _write(root, _register_path(name="BUG-0067"), _register(id="BUG-0067"))
    _git(root, env, "add", "docs/findings/register")
    result = _run_in(root, env, "--staged")
    assert (result.returncode, result.stdout) == (0, "")


def test_st_0392_a_critical_lowering_passes_once_head_holds_the_confirmation(
    tmp_path,
):
    root, env = _repo(tmp_path)
    _write(root, BUG_PATH, _finding_text(_critical_fields(), damage=True))
    _commit(root, env)
    _write(root, BUG_PATH, _finding_text(_major_bug(**OVERRIDE)))
    result = _run_in(root, env)
    assert result.returncode == 1
    assert f"{BUG_PATH}: BR-109 lowering" in result.stdout

    _write(root, BUG_PATH, _finding_text(_critical_fields(**CONFIRMED), damage=True))
    _commit(root, env, "confirm the stop")
    _write(root, BUG_PATH, _finding_text(_major_bug(**OVERRIDE)))
    result = _run_in(root, env)
    assert (result.returncode, result.stdout) == (0, "")


def test_st_0392_a_repository_without_a_commit_checks_every_file_as_new(tmp_path):
    root, env = _repo(tmp_path)
    _clean_set(root)
    assert _run_in(root, env).returncode == 0
    _git(root, env, "add", "-A")
    result = _run_in(root, env, "--staged")
    assert (result.returncode, result.stdout) == (0, "")


def test_st_0392_staged_outside_a_repository_exits_2(tmp_path):
    root = tmp_path / "plain"
    root.mkdir()
    _clean_set(root)
    _, env = _repo(tmp_path)
    result = _run_in(root, env, "--staged")
    assert result.returncode == 2
    assert "finding-lint" in result.stderr


def test_st_0392_a_failed_git_call_exits_2(committed):
    root, env = committed
    blob = subprocess.run(
        ["git", "rev-parse", f"HEAD:{FAGAN_PATH}"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    (root / ".git" / "objects" / blob[:2] / blob[2:]).unlink()
    result = _run_in(root, env)
    assert result.returncode == 2
    assert "finding-lint" in result.stderr


def test_st_0392_the_demo_scenario_of_the_story(committed):
    root, env = committed
    _lower_fagan(root)
    result = _run_in(root, env)
    assert result.returncode == 1
    assert f"{FAGAN_PATH}: BR-109 lowering" in result.stdout

    _git(root, env, "add", FAGAN_PATH)
    result = _run_in(root, env, "--staged")
    assert result.returncode == 1
    assert f"{FAGAN_PATH}: BR-109 lowering" in result.stdout

    _git(root, env, "checkout", "HEAD", "--", FAGAN_PATH)
    (root / REGISTER_PATH).unlink()
    _write(
        root,
        "docs/findings/FAGAN-0032.md",
        _finding_text(_finding_fields(id="FAGAN-0032")),
    )
    result = _run_in(root, env)
    assert (result.returncode, result.stdout) == (0, "")
