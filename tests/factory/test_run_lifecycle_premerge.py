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


# --- ST-0413: no merge without a review report or with an open blocking finding ---

FINDING = """---
id: {id}
source: code-review-agent
review_class: code
category: {category}
type: function
severity: {severity}
artifact: src/ST-0350.txt:1
status: {status}
owner: developer-agent
story: {story}
run:
traces: [BR-085]
---

# {id}
"""
REGISTER = """{{
  "id": "{id}",
  "source": "code-review-agent",
  "review_class": "code",
  "category": "defect",
  "type": "function",
  "severity": "minor",
  "artifact": "src/ST-0350.txt:1",
  "story": "ST-0350",
  "status": "open"
}}
"""
REPORT_PATH = f"docs/reviews/code-review-ST-0350-{REVIEW_DAY}.md"


def _finding(
    finding_id: str, *, story: str = "ST-0350", status: str = "open",
    category: str = "defect", severity: str = "major",
) -> str:
    return FINDING.format(
        id=finding_id, story=story, status=status, category=category, severity=severity,
    )


def _commit_on_story(repo: Path, files: dict[str, str], message: str = "work") -> str:
    """Commit *files* on story/ST-0350 in its checkout and return the head."""
    story = repo / STORY_DIR
    for rel, text in files.items():
        (story / rel).parent.mkdir(parents=True, exist_ok=True)
        (story / rel).write_text(text)
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", message)
    return _git(story, "rev-parse", "HEAD")


def _review(base: str, head: str, story: str = "ST-0350") -> str:
    return REPORT.format(id=story, day=REVIEW_DAY, base=base, head=head)


@pytest.mark.spec("RL-08-IT-01")
def test_RL_08_IT_01_merge_story_refuses_a_branch_without_a_review_report(wave_repo):
    """Scenario: A story branch without a matching review report is refused."""
    repo, feature, ledger = wave_repo["repo"], wave_repo["feature"], wave_repo["ledger"]
    sha = _commit_on_story(repo, {"src/ST-0350.txt": "work\n"})
    assert _dispatch(repo, ledger, "verify-story", "ST-0350", "--sha", sha).returncode == 0
    tip = _git(feature, "rev-parse", "HEAD")

    result = _dispatch(feature, ledger, "merge-story", "ST-0350")

    assert result.returncode == 1, result.stdout + result.stderr
    assert (
        "BLOCK code-review: no report docs/reviews/code-review-ST-0350-YYYY-MM-DD.md"
        in result.stdout
    )
    assert _git(feature, "rev-parse", "HEAD") == tip


@pytest.mark.spec("RL-08-IT-01")
@pytest.mark.parametrize(
    ("case", "passes"),
    [("other story", False), ("not an ancestor", False), ("older ancestor", True)],
)
def test_RL_08_IT_01_only_a_report_of_the_story_at_an_ancestor_counts(
    wave_repo, case, passes,
):
    """A report of another story or of a commit outside the branch does not
    count; a report of an older ancestor does (BR-122)."""
    repo, base = wave_repo["repo"], wave_repo["base"]
    work = _commit_on_story(repo, {"src/ST-0350.txt": "work\n"})
    if case == "other story":
        report = _review(base, work, story="ST-0351")
    elif case == "not an ancestor":
        report = _review(base, "0" * 40)
    else:
        report = _review(base, base)
    _commit_on_story(repo, {REPORT_PATH: report}, "docs: review")
    _commit_on_story(repo, {"src/ST-0350.txt": "work after the review\n"})

    result = _premerge(repo)

    assert (result.returncode == 0) is passes, result.stdout + result.stderr
    if passes:
        assert f"PASS code-review: {REPORT_PATH}" in result.stdout
    else:
        assert "BLOCK code-review" in result.stdout


@pytest.mark.spec("RL-08-IT-02")
def test_RL_08_IT_02_an_open_blocking_finding_at_the_head_is_refused_and_named(wave_repo):
    """Scenario: An open blocking finding at the branch head is refused and named."""
    repo = wave_repo["repo"]
    _work_and_review(repo, wave_repo["ledger"], wave_repo["base"], "ST-0350")
    _commit_on_story(repo, {"docs/findings/BUG-0091.md": _finding("BUG-0091")})
    # The folder premerge-check runs in holds a resolved copy, which must not count.
    findings = repo / "docs" / "findings"
    findings.mkdir(parents=True, exist_ok=True)
    (findings / "BUG-0091.md").write_text(_finding("BUG-0091", status="resolved"))

    result = _premerge(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "BLOCK open-findings: BUG-0091 of ST-0350 is open and blocking" in result.stdout
    assert not (repo / ".current-work" / "premerge-check-ok").exists()


@pytest.mark.spec("RL-08-IT-02")
def test_RL_08_IT_02_the_check_passes_once_the_finding_is_resolved(wave_repo):
    """Demo step 4: after BUG-0091 is resolved at the head, the check passes,
    also with an open copy in the folder premerge-check runs in."""
    repo = wave_repo["repo"]
    _work_and_review(repo, wave_repo["ledger"], wave_repo["base"], "ST-0350")
    _commit_on_story(repo, {"docs/findings/BUG-0091.md": _finding("BUG-0091")})
    _commit_on_story(
        repo, {"docs/findings/BUG-0091.md": _finding("BUG-0091", status="resolved")}
    )
    findings = repo / "docs" / "findings"
    findings.mkdir(parents=True, exist_ok=True)
    (findings / "BUG-0091.md").write_text(_finding("BUG-0091"))

    result = _premerge(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS open-findings: no open blocking finding of ST-0350" in result.stdout


@pytest.mark.spec("RL-08-IT-03")
def test_RL_08_IT_03_a_finding_that_does_not_block_leaves_the_merge_open(wave_repo):
    """Scenario: A finding that does not block leaves the merge open."""
    repo = wave_repo["repo"]
    _work_and_review(repo, wave_repo["ledger"], wave_repo["base"], "ST-0350")
    _commit_on_story(
        repo,
        {
            "docs/findings/register/code/IMPL-0093.json": REGISTER.format(id="IMPL-0093"),
            "docs/findings/IMPL-0094.md": _finding("IMPL-0094", category="suggestion"),
            "docs/findings/BUG-0095.md": _finding("BUG-0095", story="ST-0351"),
        },
    )

    result = _premerge(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS open-findings: no open blocking finding of ST-0350" in result.stdout


SRC_FOLDER_STORY = STORY.replace(
    '["src/{id}.txt", "src/{id}.py", "docs/reviews/code-review-{id}-*.md"]', '["src/"]'
).format(id="ST-0350")


@pytest.mark.spec("RL-08-IT-07")
def test_RL_08_IT_07_the_storys_reports_and_findings_do_not_count_toward_the_limit(tmp_path):
    """Scenario: The story's review reports and findings do not count toward
    the file limit."""
    run = _build_wave_repo(tmp_path, {"backlog/ST-0350.md": SRC_FOLDER_STORY})
    repo, feature, ledger, base = run["repo"], run["feature"], run["ledger"], run["base"]
    work = {f"src/f{n:02}.txt": "work\n" for n in range(1, 19)}
    head = _commit_on_story(repo, work)
    sha = _commit_on_story(
        repo,
        {
            REPORT_PATH: _review(base, head),
            "docs/findings/BUG-0091.md": _finding("BUG-0091", status="resolved"),
            "docs/findings/BUG-0096.md": _finding("BUG-0096", status="resolved"),
            "docs/findings/register/code/IMPL-0093.json": REGISTER.format(id="IMPL-0093"),
        },
        "docs: review",
    )
    assert _dispatch(repo, ledger, "verify-story", "ST-0350", "--sha", sha).returncode == 0

    result = _dispatch(feature, ledger, "merge-story", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    assert (
        "PASS file-count-blowout: 18 files changed, not counting 4 review or "
        "finding file(s) of the story (limit 20)" in result.stdout
    )
    assert "PASS out-of-scope-paths: all 22 file(s) under declared scope" in result.stdout


@pytest.mark.spec("RL-08-IT-08")
def test_RL_08_IT_08_a_finding_of_another_story_outside_the_scope_blocks(wave_repo):
    """Scenario: A finding of another story outside the scope blocks the merge."""
    repo, feature, ledger = wave_repo["repo"], wave_repo["feature"], wave_repo["ledger"]
    _work_and_review(repo, ledger, wave_repo["base"], "ST-0350")
    sha = _commit_on_story(
        repo,
        {"docs/findings/BUG-0092.md": _finding("BUG-0092", story="ST-0351", status="resolved")},
    )
    assert _dispatch(repo, ledger, "verify-story", "ST-0350", "--sha", sha).returncode == 0
    tip = _git(feature, "rev-parse", "HEAD")

    result = _dispatch(feature, ledger, "merge-story", "ST-0350")

    assert result.returncode == 1, result.stdout + result.stderr
    assert "BLOCK out-of-scope-paths: docs/findings/BUG-0092.md" in result.stdout
    assert _git(feature, "rev-parse", "HEAD") == tip


# --- ST-0424: the review check reads a full SHA from any folder ---


@pytest.mark.spec("RL-08-IT-01")
def test_RL_08_IT_01_a_report_whose_branch_head_is_a_ref_name_is_refused(wave_repo):
    """IMPL-0025: a ref name as branch_head resolves to the current tip, so the
    check accepts only a full SHA and names the report and the value."""
    repo, base = wave_repo["repo"], wave_repo["base"]
    _commit_on_story(repo, {"src/ST-0350.txt": "work\n"})
    _commit_on_story(repo, {REPORT_PATH: _review(base, "story/ST-0350")}, "docs: review")

    result = _premerge(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    block = [line for line in result.stdout.splitlines() if line.startswith("BLOCK code-review")]
    assert len(block) == 1, result.stdout
    assert REPORT_PATH in block[0]
    assert "'story/ST-0350'" in block[0]


@pytest.mark.spec("RL-08-IT-02")
def test_RL_08_IT_02_the_check_reads_the_head_from_a_subfolder(tmp_path):
    """IMPL-0026: run from packages/, premerge-check finds the report and the open
    BUG-0091 at the head, as it does from the project root."""
    run = _build_wave_repo(tmp_path, {"packages/.keep": ""})
    repo = run["repo"]
    _work_and_review(repo, run["ledger"], run["base"], "ST-0350")
    _commit_on_story(repo, {"docs/findings/BUG-0091.md": _finding("BUG-0091")})

    def review_and_findings(cwd: Path) -> list[str]:
        result = _premerge(cwd)
        assert result.returncode == 1, result.stdout + result.stderr
        return [
            line for line in result.stdout.splitlines()
            if line.startswith(("PASS code-review", "BLOCK code-review", "PASS open-findings",
                                "BLOCK open-findings"))
        ]

    from_root = review_and_findings(repo)
    from_packages = review_and_findings(repo / "packages")

    assert from_packages == from_root
    assert from_root[0].startswith(f"PASS code-review: {REPORT_PATH}")
    assert from_root[1].startswith("BLOCK open-findings: BUG-0091 of ST-0350")


# --- ST-0424: premerge-check dev <feature-branch>, the feature merge check ---

FEATURE = "feature/login"
FEATURE_PREMERGE = Path(".current-work") / "feature" / "login" / "premerge" / "feature"
FEATURE_REPORTS = {
    "review": ("code-review", f"docs/reviews/code-review-feature-login-{REVIEW_DAY}.md"),
    "fagan": ("fagan-review", f"docs/reviews/fagan-review-{REVIEW_DAY}.md"),
    "security": ("security-review", f"docs/reviews/security-review-{REVIEW_DAY}.md"),
    "bug-hunt": ("bug-hunt", f"docs/reviews/bug-hunt-{REVIEW_DAY}.md"),
}
FEATURE_REPORT = """---
type: {type}
title: {type} of {run}
date: {day}
status: pass
reviewer: qa-agent
findings_filed: 0
story:
run: {run}
branch: {run}
branch_base: {base}
branch_head: {head}
---

# {type} of {run}
"""
FEATURE_FINDING = """---
id: {id}
source: qa-agent
review_class: runtime
category: defect
type: function
severity: major
artifact: src/login.txt:1
status: {status}
owner: developer-agent
story: {story}
run: {run}
traces: [BR-085]
---

# {id}
"""
SUITE = "#!/bin/sh\necho \"$PWD\" > {log}\nexit {code}\n"


def _ledger_text(
    statuses: dict[str, str],
    waves: list[int],
    mode: str = "orchestrated",
    entries: dict[str, dict] | None = None,
) -> str:
    """The ledger of the run; *entries* overrides fields of a story's entry."""
    import yaml

    stories = {
        sid: {"id": sid, "wave": wave, "status": status, "deps": [], "branch": f"story/{sid}"}
        for wave, (sid, status) in enumerate(statuses.items(), start=1)
    }
    for sid, fields in (entries or {}).items():
        stories[sid].update(fields)
    records = [
        {"number": n, "completed": [], "blocked": [], "failed": [], "next_ready": []}
        for n in waves
    ]
    return yaml.safe_dump(
        {"mode": mode, "feature_branch": FEATURE, "stories": stories, "waves": records},
        sort_keys=False,
    )


def _feature_run(
    tmp_path: Path,
    *,
    statuses: dict[str, str] | None = None,
    waves: tuple[int, ...] = (1, 2),
    reports: dict[str, str] | None = None,
    findings: dict[str, str] | None = None,
    suite_exit: int = 0,
    head_of_report: str | None = None,
    mode: str = "orchestrated",
    entries: dict[str, dict] | None = None,
) -> dict[str, Path | str]:
    """A run on feature/login with ST-0350 in wave 1 and ST-0351 in wave 2.

    *reports* maps a key of FEATURE_REPORTS to the `run` of that report; a key
    left out writes no report. By default all four reports name feature/login.
    """
    repo = tmp_path / "repo"
    log = tmp_path / "suite.log"
    repo.mkdir(parents=True)
    _git(tmp_path, "init", "-q", "-b", "dev", str(repo))
    (repo / ".gitignore").write_text(".current-work/\n.agent-factory/\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "testing.yaml").write_text('test_command: "sh tests/suite.sh"\n')
    (repo / "src").mkdir()
    (repo / "src" / "login.txt").write_text("start\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    base = _git(repo, "rev-parse", "HEAD")
    feature = repo / ".current-work" / "feature" / "login" / "inv"
    _git(repo, "worktree", "add", "-q", "-b", FEATURE, str(feature))
    (feature / "tests").mkdir()
    (feature / "tests" / "suite.sh").write_text(SUITE.format(log=log, code=suite_exit))
    (feature / "src" / "login.txt").write_text("login\n")
    _git(feature, "add", "-A")
    _git(feature, "commit", "-qm", "feat: login")
    head = head_of_report or _git(feature, "rev-parse", "HEAD")
    runs = reports if reports is not None else {key: FEATURE for key in FEATURE_REPORTS}
    for key, report_run in runs.items():
        kind, path = FEATURE_REPORTS[key]
        (feature / path).parent.mkdir(parents=True, exist_ok=True)
        (feature / path).write_text(
            FEATURE_REPORT.format(type=kind, run=report_run, day=REVIEW_DAY, base=base, head=head)
        )
    for rel, text in (findings or {}).items():
        (feature / rel).parent.mkdir(parents=True, exist_ok=True)
        (feature / rel).write_text(text)
    _git(feature, "add", "-A")
    _git(feature, "commit", "-qm", "docs: feature checks")
    ledger = repo / ".current-work" / "feature" / "login" / "dispatch-ledger.yaml"
    ledger.write_text(
        _ledger_text(
            statuses or {"ST-0350": "done", "ST-0351": "done"}, list(waves), mode, entries,
        )
    )
    return {"repo": repo, "feature": feature, "log": log}


def _premerge_dev(cwd: Path, target: str = "dev") -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(PREMERGE), target, FEATURE],
        cwd=cwd, env=_env(), capture_output=True, text=True, check=False,
    )


def _feature_finding(finding_id: str, *, story: str = "", run: str = FEATURE,
                     status: str = "open") -> dict[str, str]:
    return {
        f"docs/findings/{finding_id}.md": FEATURE_FINDING.format(
            id=finding_id, story=story, run=run, status=status,
        )
    }


def _block_lines(result: subprocess.CompletedProcess) -> list[str]:
    return [line for line in result.stdout.splitlines() if line.startswith("BLOCK")]


@pytest.mark.spec("RL-13-IT-01")
@pytest.mark.parametrize(
    ("statuses", "waves", "named"),
    [
        ({"ST-0350": "failed", "ST-0351": "done"}, (1, 2), "ST-0350"),
        ({"ST-0350": "done", "ST-0351": "blocked"}, (1, 2), "ST-0351"),
        ({"ST-0350": "done", "ST-0351": "done"}, (1,), "wave 2"),
    ],
    ids=["failed", "blocked", "open wave"],
)
def test_RL_13_IT_01_a_stopped_story_or_an_open_wave_is_refused(tmp_path, statuses, waves, named):
    """Scenario Outline: premerge-check dev refuses a run that is not ready, rows 1 to 3."""
    run = _feature_run(tmp_path, statuses=statuses, waves=waves)

    result = _premerge_dev(run["repo"])

    assert result.returncode == 1, result.stdout + result.stderr
    blocks = _block_lines(result)
    assert len(blocks) == 1, result.stdout
    assert named in blocks[0]
    assert not (run["repo"] / ".current-work" / "premerge-check-ok").exists()


@pytest.mark.spec("RL-13-IT-01")
def test_RL_13_IT_01_a_story_that_never_started_in_a_run_by_hand_is_refused(tmp_path):
    """IMPL-0050: in a run by hand, a story gets its wave only when it starts, so
    an unstarted story is pending with no wave and must still refuse the merge."""
    run = _feature_run(
        tmp_path,
        statuses={"ST-0350": "done", "ST-0351": "pending"},
        waves=(1,),
        mode="by-hand",
        entries={"ST-0351": {"wave": None}},
    )

    result = _premerge_dev(run["repo"])

    assert result.returncode == 1, result.stdout + result.stderr
    blocks = _block_lines(result)
    assert blocks == ["BLOCK run-state: ST-0351 is pending and has not run"], result.stdout
    assert not (run["repo"] / ".current-work" / "premerge-check-ok").exists()


@pytest.mark.spec("RL-13-IT-01")
@pytest.mark.parametrize(
    ("statuses", "entries"),
    [
        (
            {"ST-0350": "done", "ST-0351": "pending"},
            {"ST-0351": {"returned": True}},
        ),
        (
            {"ST-0350": "pending", "ST-0351": "pending"},
            {"ST-0350": {"returned": True}, "ST-0351": {"wave": None, "deps": ["ST-0350"]}},
        ),
    ],
    ids=["returned", "waits on a returned story"],
)
def test_RL_13_IT_01_a_story_held_back_by_a_return_does_not_block(tmp_path, statuses, entries):
    """A returned story, and a story that waits on one, wait for the end of the run
    and leave the feature merge open (BR-113)."""
    run = _feature_run(tmp_path, statuses=statuses, mode="by-hand", entries=entries)

    result = _premerge_dev(run["repo"])

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.spec("RL-13-IT-01")
@pytest.mark.parametrize("target", ["refs/heads/dev", "sha of dev"])
def test_RL_13_IT_01_every_name_of_dev_gets_the_feature_checks(tmp_path, target):
    """IMPL-0052: the target refs/heads/dev or the SHA of dev is a feature merge too."""
    run = _feature_run(tmp_path)
    ledger = run["repo"] / ".current-work" / "feature" / "login" / "dispatch-ledger.yaml"
    ledger.unlink()
    if target == "sha of dev":
        target = _git(run["repo"], "rev-parse", "dev")

    result = _premerge_dev(run["repo"], target)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "dispatch-ledger.yaml" in _block_lines(result)[0]
    assert not (run["repo"] / ".current-work" / "premerge-check-ok").exists()


@pytest.mark.spec("RL-13-IT-01")
def test_RL_13_IT_01_a_run_without_a_ledger_is_refused(tmp_path):
    """Without the ledger, the check cannot show that no unit of work stopped."""
    run = _feature_run(tmp_path)
    ledger = run["repo"] / ".current-work" / "feature" / "login" / "dispatch-ledger.yaml"
    ledger.unlink()

    result = _premerge_dev(run["repo"])

    assert result.returncode == 1, result.stdout + result.stderr
    assert "dispatch-ledger.yaml" in _block_lines(result)[0]


@pytest.mark.spec("RL-13-IT-02")
@pytest.mark.parametrize(
    ("missing", "named"),
    [
        ("review", "the end-of-feature review"),
        ("fagan", "the Fagan report"),
        ("security", "the security report"),
        ("bug-hunt", "the bug-hunt report"),
    ],
)
def test_RL_13_IT_02_a_missing_feature_report_is_refused(tmp_path, missing, named):
    """Scenario Outline: premerge-check dev refuses a run that is not ready, rows 4 to 7."""
    reports = {key: FEATURE for key in FEATURE_REPORTS if key != missing}
    run = _feature_run(tmp_path, reports=reports)

    result = _premerge_dev(run["repo"])

    assert result.returncode == 1, result.stdout + result.stderr
    blocks = _block_lines(result)
    assert len(blocks) == 1, result.stdout
    assert named in blocks[0]


@pytest.mark.spec("RL-13-IT-02")
def test_RL_13_IT_02_a_qa_report_of_another_run_does_not_count(tmp_path):
    """Scenario: A QA report of another run does not count for the feature merge."""
    reports = {key: FEATURE for key in FEATURE_REPORTS}
    reports["fagan"] = "feature/search"
    run = _feature_run(tmp_path, reports=reports)

    result = _premerge_dev(run["repo"])

    assert result.returncode == 1, result.stdout + result.stderr
    blocks = _block_lines(result)
    assert len(blocks) == 1, result.stdout
    assert "the Fagan report" in blocks[0]


@pytest.mark.spec("RL-13-IT-02")
@pytest.mark.parametrize(
    ("head", "shown"),
    [("0" * 40, None), (FEATURE, f"'{FEATURE}'")],
    ids=["not an ancestor", "ref name"],
)
def test_RL_13_IT_02_a_report_of_other_code_is_refused(tmp_path, head, shown):
    """A branch_head outside the feature branch, or a ref name, does not count (BR-122)."""
    run = _feature_run(tmp_path, head_of_report=head)

    result = _premerge_dev(run["repo"])

    assert result.returncode == 1, result.stdout + result.stderr
    blocks = _block_lines(result)
    assert len(blocks) == 4, result.stdout
    if shown:
        assert all(shown in line for line in blocks)


@pytest.mark.spec("RL-13-IT-03")
@pytest.mark.parametrize(
    ("finding", "named"),
    [
        (_feature_finding("BUG-0090"), "BUG-0090"),
        (_feature_finding("BUG-0091", story="ST-0350", run=""), "BUG-0091"),
    ],
    ids=["run of the branch", "story of the run"],
)
def test_RL_13_IT_03_an_open_blocking_finding_of_the_run_is_refused(tmp_path, finding, named):
    """Scenario Outline: premerge-check dev refuses a run that is not ready, rows 8 and 9."""
    run = _feature_run(tmp_path, findings=finding)

    result = _premerge_dev(run["repo"])

    assert result.returncode == 1, result.stdout + result.stderr
    blocks = _block_lines(result)
    assert len(blocks) == 1, result.stdout
    assert named in blocks[0]


@pytest.mark.spec("RL-13-IT-03")
@pytest.mark.parametrize(
    "finding",
    [_feature_finding("BUG-0092", run="feature/search"), _feature_finding("BUG-0093", run="")],
    ids=["another run", "no run and no story"],
)
def test_RL_13_IT_03_a_finding_of_another_run_does_not_block(tmp_path, finding):
    """Scenario: A finding of another run does not block the feature merge."""
    run = _feature_run(tmp_path, findings=finding)

    result = _premerge_dev(run["repo"])

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.spec("RL-13-IT-03")
def test_RL_13_IT_03_the_check_passes_once_the_finding_is_resolved(tmp_path):
    """Demo steps 2 and 3: the check names BUG-0090, then passes once it is resolved."""
    open_run = _feature_run(tmp_path / "open", findings=_feature_finding("BUG-0090"))
    refused = _premerge_dev(open_run["repo"])
    resolved_run = _feature_run(
        tmp_path / "resolved", findings=_feature_finding("BUG-0090", status="resolved"),
    )

    passed = _premerge_dev(resolved_run["repo"])

    assert refused.returncode == 1
    assert f"BUG-0090 (run {FEATURE})" in refused.stdout
    assert passed.returncode == 0, passed.stdout + passed.stderr
    assert f"premerge-check: PASS — '{FEATURE}' clean to merge into 'dev'" in passed.stdout
    assert (resolved_run["repo"] / ".current-work" / "premerge-check-ok").exists()


@pytest.mark.spec("RL-13-IT-04")
def test_RL_13_IT_04_a_failing_test_suite_is_refused(tmp_path):
    """Scenario Outline: premerge-check dev refuses a run that is not ready, row 10."""
    run = _feature_run(tmp_path, suite_exit=1)

    result = _premerge_dev(run["repo"])

    assert result.returncode == 1, result.stdout + result.stderr
    blocks = _block_lines(result)
    assert len(blocks) == 1, result.stdout
    assert "the test suite" in blocks[0]
    assert run["log"].read_text().strip() == str(run["repo"] / FEATURE_PREMERGE)
    assert not (run["repo"] / FEATURE_PREMERGE).exists()


@pytest.mark.spec("RL-13-IT-04")
def test_RL_13_IT_04_the_suite_runs_in_a_temporary_worktree(tmp_path):
    """Scenario: The feature merge check runs the test suite in a temporary worktree."""
    run = _feature_run(tmp_path)
    repo = run["repo"]
    (repo / "src" / "login.txt").write_text("changed\n")
    (repo / "notes.txt").write_text("untracked\n")
    status = _git(repo, "status", "--porcelain")

    result = _premerge_dev(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert run["log"].read_text().strip() == str(repo / FEATURE_PREMERGE)
    assert (repo / "src" / "login.txt").read_text() == "changed\n"
    assert (repo / "notes.txt").read_text() == "untracked\n"
    assert _git(repo, "status", "--porcelain") == status
    assert _git(repo, "stash", "list") == ""
    assert not (repo / FEATURE_PREMERGE).exists()
    assert str(repo / FEATURE_PREMERGE) not in _worktrees(repo)
