"""Merges of reviewed stories in the run lifecycle (docs/spec/features/run-lifecycle.feature).

Each test builds its own git repository in tmp_path and runs dispatch as a
subprocess, the way the implementation agent does. merge-story runs
premerge-check before it merges.
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR

DISPATCH = SOURCE_SCRIPTS_DIR / "dispatch"
PREMERGE = SOURCE_SCRIPTS_DIR / "premerge-check"
RULES = "docs/spec/dependency-rules.dsl"
RULE = "src must_not_depend_on infra\n"
STORIES = ("ST-0350", "ST-0351")
REVIEW_DAY = "2026-11-24"
STORY = """---
id: {id}
title: {id}
tier: economy
status: open
deps: []
touches: ["src/{id}.txt", "src/{id}.py", "docs/reviews/code-review-{id}-*.md"]
outputs: ["src/{id}.txt", "src/{id}.py", "docs/reviews/code-review-{id}-*.md"]
quality-gates: []
---
# {id}
"""
REPORT = """---
type: code-review
title: Code review of {id}
date: {day}
status: pass
reviewer: code-review-agent
findings_filed: 0
story: {id}
branch: story/{id}
branch_base: {base}
branch_head: {head}
---

# Code review of {id}

No finding.
"""


def _env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
    )
    return env


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, env=_env(), check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _dispatch(cwd: Path, ledger: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(DISPATCH), "--ledger", str(ledger), *args],
        cwd=cwd, env=_env(), capture_output=True, text=True, check=False,
    )


@pytest.fixture()
def wave_repo(tmp_path: Path) -> dict[str, Path]:
    """A repository with ST-0350 and ST-0351 dispatched in wave 1 of feat/login."""
    return _build_wave_repo(tmp_path)


def _build_wave_repo(tmp_path: Path, files: dict[str, str] | None = None) -> dict[str, Path]:
    """Build the wave repository; *files* go into its first commit."""
    repo = tmp_path / "repo"
    for folder in ("backlog", "src", "docs/reviews"):
        (repo / folder).mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    for story_id in STORIES:
        (repo / "backlog" / f"{story_id}.md").write_text(STORY.format(id=story_id))
    (repo / "docs" / "testing.yaml").write_text('test_command: "true"\n')
    (repo / ".gitignore").write_text(".current-work/\n.agent-factory/\n")
    (repo / "src" / ".keep").write_text("")
    for rel, text in (files or {}).items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text)
    (repo / "docs" / "reviews" / ".keep").write_text("")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    feature = repo / ".current-work" / "feat" / "login" / "inv"
    _git(repo, "worktree", "add", "-q", "-b", "feat/login", str(feature))
    ledger = repo / ".current-work" / "feat" / "login" / "dispatch-ledger.yaml"
    for root in (repo, feature):
        report_dir = root / ".current-work" / "dependency-check"
        report_dir.mkdir(parents=True, exist_ok=True)
        for story_id in STORIES:
            (report_dir / f"{story_id}.json").write_text("[]\n")
    base = _git(repo, "rev-parse", "HEAD")
    steps = [
        ("init", "--base", base, "--stories", ",".join(STORIES),
         "--feature-branch", "feat/login", "--yes"),
        ("plan", "--backlog-dir", "backlog"),
        ("prepare-wave", "1"),
    ]
    for story_id in STORIES:
        steps += [("mark-dispatching", story_id), ("mark-dispatched", story_id)]
    for args in steps:
        result = _dispatch(repo, ledger, *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)
    return {"repo": repo, "feature": feature, "ledger": ledger, "base": base}


def _work_and_review(
    repo: Path, ledger: Path, base: str, story_id: str, code: str | None = None,
) -> str:
    """Commit the work of *story_id*, then its review report, and verify the head.

    *code* becomes src/<story_id>.py when given.
    """
    story = repo / ".current-work" / "feat" / "login" / "story" / story_id
    (story / "src" / f"{story_id}.txt").write_text("work\n")
    if code is not None:
        (story / "src" / f"{story_id}.py").write_text(code)
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", f"feat: work ({story_id})")
    head = _git(story, "rev-parse", "HEAD")
    report = story / "docs" / "reviews" / f"code-review-{story_id}-{REVIEW_DAY}.md"
    report.write_text(REPORT.format(id=story_id, day=REVIEW_DAY, base=base, head=head))
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", f"docs: review {story_id}")
    sha = _git(story, "rev-parse", "HEAD")
    verified = _dispatch(repo, ledger, "verify-story", story_id, "--sha", sha)
    assert verified.returncode == 0, verified.stdout + verified.stderr
    return sha


@pytest.mark.spec("RL-04-IT-01")
def test_RL_04_IT_01_two_stories_reviewed_on_one_day_merge_without_a_conflict(wave_repo):
    """Scenario: Two stories reviewed on the same day merge without a conflict on
    their reports."""
    repo, feature, ledger, base = (
        wave_repo["repo"], wave_repo["feature"], wave_repo["ledger"], wave_repo["base"],
    )
    heads = {story_id: _work_and_review(repo, ledger, base, story_id) for story_id in STORIES}

    for story_id in STORIES:
        result = _dispatch(feature, ledger, "merge-story", story_id)
        assert result.returncode == 0, (story_id, result.stdout + result.stderr)
        # merge-story refreshes ST-0351 from feat/login first, so the merged
        # head can be a refresh merge on top of the reviewed head.
        _git(feature, "merge-base", "--is-ancestor", heads[story_id], "HEAD")

    reports = sorted(path.name for path in (feature / "docs" / "reviews").glob("code-review-*.md"))
    assert reports == [f"code-review-{story_id}-{REVIEW_DAY}.md" for story_id in STORIES]
    assert _git(feature, "status", "--porcelain") == ""


# --- ST-0414: the gates rerun at the branch head in a temporary worktree ---

PREMERGE_PATH = Path(".current-work") / "feat" / "login" / "premerge" / "ST-0350"


def _premerge(cwd: Path, branch: str = "story/ST-0350") -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(PREMERGE), "feat/login", branch],
        cwd=cwd, env=_env(), capture_output=True, text=True, check=False,
    )


def _worktrees(repo: Path) -> list[str]:
    porcelain = _git(repo, "worktree", "list", "--porcelain")
    return [line.split(" ", 1)[1] for line in porcelain.splitlines() if line.startswith("worktree ")]


def _install_gate(repo: Path, name: str, body: str) -> Path:
    """Write an executable stub as the installed copy of gate *name*."""
    script = repo / ".agent-factory" / "factory" / "scripts" / name
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(body)
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


@pytest.mark.spec("RL-08-IT-04")
def test_RL_08_IT_04_a_failing_head_is_refused_despite_a_passing_stored_result(tmp_path):
    """Scenario: The gates rerun on the branch head and ignore a stored result."""
    run = _build_wave_repo(tmp_path, {RULES: RULE})
    repo, feature, ledger = run["repo"], run["feature"], run["ledger"]
    _work_and_review(repo, ledger, run["base"], "ST-0350", code="import infra\n")
    stored = repo / ".current-work" / "dependency-check" / "ST-0350.json"
    assert stored.read_text() == "[]\n"
    tip = _git(feature, "rev-parse", "HEAD")

    result = _dispatch(feature, ledger, "merge-story", "ST-0350")

    assert result.returncode == 1, result.stdout + result.stderr
    assert "BLOCK semantic-gates: dependency-check" in result.stdout
    assert _git(feature, "rev-parse", "HEAD") == tip


@pytest.mark.spec("RL-08-IT-04")
def test_RL_08_IT_04_a_passing_head_merges_without_a_stored_result(tmp_path):
    """Scenario: The gates rerun on the branch head and ignore a stored result."""
    run = _build_wave_repo(tmp_path, {RULES: RULE})
    repo, feature, ledger = run["repo"], run["feature"], run["ledger"]
    for root in (repo, feature):
        (root / ".current-work" / "dependency-check" / "ST-0350.json").unlink()
    _work_and_review(repo, ledger, run["base"], "ST-0350", code="import os\n")

    result = _dispatch(feature, ledger, "merge-story", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS semantic-gates: dependency-check passed for ST-0350" in result.stdout


@pytest.mark.spec("RL-08-IT-05")
def test_RL_08_IT_05_the_rerun_leaves_the_primary_checkout_as_it_was(tmp_path):
    """Scenario: The rerun leaves the primary checkout as it was."""
    run = _build_wave_repo(tmp_path, {RULES: RULE})
    repo = run["repo"]
    _work_and_review(repo, run["ledger"], run["base"], "ST-0350", code="import os\n")
    (repo / "src" / ".keep").write_text("changed\n")
    (repo / "notes.txt").write_text("untracked\n")
    status = _git(repo, "status", "--porcelain")

    result = _premerge(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS semantic-gates: dependency-check passed for ST-0350" in result.stdout
    assert (repo / "src" / ".keep").read_text() == "changed\n"
    assert (repo / "notes.txt").read_text() == "untracked\n"
    assert _git(repo, "status", "--porcelain") == status
    assert _git(repo, "stash", "list") == ""
    assert not (repo / PREMERGE_PATH).exists()
    assert str(repo / PREMERGE_PATH) not in _worktrees(repo)


@pytest.mark.spec("RL-08-IT-14")
def test_RL_08_IT_14_a_leftover_worktree_does_not_block_the_next_check(tmp_path):
    """Scenario: A worktree left by a crashed premerge-check does not block the next check."""
    run = _build_wave_repo(tmp_path, {RULES: RULE})
    repo = run["repo"]
    _work_and_review(repo, run["ledger"], run["base"], "ST-0350", code="import os\n")
    leftover = repo / PREMERGE_PATH
    _git(repo, "worktree", "add", "-q", "--detach", str(leftover), "story/ST-0350")
    (leftover / "src" / "ST-0350.txt").write_text("left by a crash\n")

    result = _premerge(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert not leftover.exists()
    assert str(leftover) not in _worktrees(repo)


@pytest.mark.spec("RL-08-IT-06")
def test_RL_08_IT_06_an_untracked_test_file_takes_no_part_in_the_rerun(tmp_path):
    """Scenario: An untracked test file in the story's checkout takes no part in the rerun."""
    run = _build_wave_repo(tmp_path, {RULES: RULE})
    repo = run["repo"]
    _work_and_review(repo, run["ledger"], run["base"], "ST-0350", code="import os\n")
    story = repo / ".current-work" / "feat" / "login" / "story" / "ST-0350"
    untracked = story / "src" / "test_extra.py"
    untracked.write_text("import infra\n")

    result = _premerge(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert untracked.read_text() == "import infra\n"
    assert "?? src/test_extra.py" in _git(story, "status", "--porcelain")


RECORDING_GATE = """#!/usr/bin/env bash
set -e
{{
  echo "script=$0"
  echo "cwd=$PWD"
  echo "args=$*"
  echo "prefix=$(uv run --offline --quiet python -c 'import sys; print(sys.prefix)')"
}} > {log}
report_dir=""
while [ $# -gt 0 ]; do
  if [ "$1" = "--report-dir" ]; then report_dir="$2"; fi
  shift
done
mkdir -p "$report_dir"
echo "[]" > "$report_dir/ST-0350.json"
"""

PYPROJECT = """[project]
name = "fixture"
version = "0"
requires-python = ">=3.10"
dependencies = []
"""


@pytest.mark.spec("RL-08-IT-10")
def test_RL_08_IT_10_the_rerun_takes_the_gate_scripts_from_the_installed_copy(tmp_path):
    """Scenario: The rerun takes the gate scripts from the installed copy of the
    calling checkout."""
    run = _build_wave_repo(tmp_path, {RULES: RULE, "pyproject.toml": PYPROJECT})
    repo = run["repo"]
    _work_and_review(repo, run["ledger"], run["base"], "ST-0350", code="import os\n")
    log = tmp_path / "gate.log"
    script = _install_gate(repo, "dependency-check", RECORDING_GATE.format(log=log))
    worktree = repo / PREMERGE_PATH
    assert _git(repo, "ls-tree", "-r", "--name-only", "story/ST-0350", ".agent-factory") == ""

    result = _premerge(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    record = dict(line.split("=", 1) for line in log.read_text().splitlines())
    assert record["script"] == str(script)
    assert record["cwd"] == str(worktree)
    assert f"--source-root {worktree}" in record["args"]
    assert f"--dsl-path {worktree / RULES}" in record["args"]
    assert record["prefix"] == str(worktree / ".venv")
    assert not worktree.exists()


@pytest.mark.spec("RL-08-IT-13")
def test_RL_08_IT_13_without_dependency_rules_the_check_skips_and_names_it(tmp_path):
    """Scenario: Without dependency rules, premerge-check skips dependency-check and
    names the skip."""
    run = _build_wave_repo(tmp_path)
    repo = run["repo"]
    _work_and_review(repo, run["ledger"], run["base"], "ST-0350")
    ran = tmp_path / "dependency-check-ran"
    _install_gate(repo, "dependency-check", f"#!/usr/bin/env bash\ntouch {ran}\nexit 1\n")

    result = _premerge(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert (
        "SKIP dependency-check: docs/spec/dependency-rules.dsl does not exist"
        in result.stdout
    )
    assert not ran.exists()


# --- ST-0415: every enabled gate and the test suite run at the branch head ---

STORY_DIR = Path(".current-work") / "feat" / "login" / "story" / "ST-0350"
LICENSE_CHECK = """{{
  echo "cwd=$PWD"
  echo "head=$(git rev-parse HEAD)"
}} > {log}
"""
GATES_WITH_LICENSE_CHECK = """test_command: "true"
gates:
  license-check:
    enabled: true
    command: sh scripts/license-check
  crap-score:
    enabled: false
"""


@pytest.mark.spec("RL-09-IT-01")
def test_RL_09_IT_01_premerge_check_runs_a_gate_that_the_script_does_not_name(tmp_path):
    """Scenario: premerge-check runs a gate that the script does not name."""
    log = tmp_path / "license-check.log"
    run = _build_wave_repo(
        tmp_path,
        {
            "docs/testing.yaml": GATES_WITH_LICENSE_CHECK,
            "scripts/license-check": LICENSE_CHECK.format(log=log),
        },
    )
    repo = run["repo"]
    head = _work_and_review(repo, run["ledger"], run["base"], "ST-0350")

    result = _premerge(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS semantic-gates: license-check passed for ST-0350" in result.stdout
    record = dict(line.split("=", 1) for line in log.read_text().splitlines())
    assert record["cwd"] == str(repo / PREMERGE_PATH)
    assert record["head"] == head


RUN_TESTS = """#!/bin/sh
echo "$PWD" > {log}
for test in tests/*.sh; do
  sh "$test" || exit 1
done
"""
TEST_SUITE_YAML = 'test_command: "sh scripts/run-tests.sh"\n'


def _test_suite_repo(tmp_path: Path) -> tuple[dict[str, Path], Path]:
    log = tmp_path / "suite.log"
    run = _build_wave_repo(
        tmp_path,
        {
            "docs/testing.yaml": TEST_SUITE_YAML,
            "scripts/run-tests.sh": RUN_TESTS.format(log=log),
            "tests/test_passes.sh": "exit 0\n",
        },
    )
    return run, log


@pytest.mark.spec("RL-08-IT-17")
def test_RL_08_IT_17_a_head_that_fails_the_test_suite_is_refused(tmp_path):
    """premerge-check runs test_command in the temporary worktree, refuses a
    red suite, and names the test suite."""
    run, log = _test_suite_repo(tmp_path)
    repo = run["repo"]
    (repo / STORY_DIR / "tests" / "test_fails.sh").write_text("exit 1\n")
    _work_and_review(repo, run["ledger"], run["base"], "ST-0350")

    result = _premerge(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "BLOCK test-suite: the test suite 'sh scripts/run-tests.sh' exited 1" in result.stdout
    assert log.read_text().strip() == str(repo / PREMERGE_PATH)
    assert not (repo / ".current-work" / "premerge-check-ok").exists()
    assert not (repo / PREMERGE_PATH).exists()


@pytest.mark.spec("RL-08-IT-17")
def test_RL_08_IT_17_an_untracked_test_file_takes_no_part_in_the_test_suite(tmp_path):
    """An untracked failing test in the story's checkout does not reach the
    test suite in the temporary worktree."""
    run, _ = _test_suite_repo(tmp_path)
    repo = run["repo"]
    _work_and_review(repo, run["ledger"], run["base"], "ST-0350")
    untracked = repo / STORY_DIR / "tests" / "test_untracked.sh"
    untracked.write_text("exit 1\n")

    result = _premerge(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS test-suite: the test suite 'sh scripts/run-tests.sh' passed for ST-0350" in result.stdout
    assert untracked.read_text() == "exit 1\n"
