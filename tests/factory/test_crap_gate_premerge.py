"""Tests of premerge-check and the CRAP gate entry (ST-0433, ST-0434, ST-0439).

Each test builds its own repository in `tmp_path` with the branches `dev`,
`feature/login`, and `story/ST-0350`, as the QA strategy of crap-gate-setup
defines. A recording stub stands in for each built-in gate, so a test sees
whether premerge-check called it. The test of `dispatch merge-story` builds
the wave repository of the run-lifecycle tests instead. The tests of ST-0439
run the real `crap-score` with a stub as the measuring command.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script, write_review_report
from test_run_lifecycle_premerge import STORY as WAVE_STORY
from test_run_lifecycle_premerge import _build_wave_repo, _dispatch, _work_and_review

SCRIPT = SOURCE_SCRIPTS_DIR / "premerge-check"
pm = load_script("premerge-check")
TEMPLATE = REPO_ROOT / "packages" / "factory" / "rulebooks" / "templates" / "charter-testing.yaml"
STORY_ID = "ST-0350"
BRANCH = f"story/{STORY_ID}"
TARGET = "feature/login"

CRAP_PART = "crap-score (set up by the skill setup-crap-score)"
MUTATION_PART = "mutation-testing (set up by the skill mutation-testing)"
LINE_PREFIX = "SKIP not-set-up gates:"

NO_GATES = 'test_command: "true"\n'
LICENSE_ONLY = 'test_command: "true"\ngates:\n  license-check:\n    enabled: true\n    command: "true"\n'
MUTATION_ONLY = 'test_command: "true"\ngates:\n  mutation-testing:\n    enabled: false\n'
CRAP_ONLY = 'test_command: "true"\ngates:\n  crap-score:\n    enabled: false\n'

RECORDING_STUB = """#!/bin/sh
echo "{name}" >> "{log}"
exit 0
"""


def _git(repo: Path, env: dict[str, str], *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True)


def _env(tmp_path: Path) -> dict[str, str]:
    home = tmp_path / "home"
    home.mkdir()
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("GIT_", "COVERAGE_"))
    }
    env["HOME"] = str(home)
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def _build_repo(
    tmp_path: Path, testing_yaml: str, field: str = ""
) -> tuple[Path, dict[str, str], Path]:
    """A story branch whose docs/testing.yaml is *testing_yaml*, with recording stubs.

    *field* is the story's front-matter line `quality-gates`, or empty.
    """
    env = _env(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, env, "init", "-q", "-b", "main")
    _git(repo, env, "config", "user.email", "fixture@example.com")
    _git(repo, env, "config", "user.name", "Fixture")
    _git(repo, env, "config", "commit.gpgsign", "false")
    (repo / "README.md").write_text("fixture\n")
    (repo / ".gitignore").write_text(".agent-factory/\n.current-work/\n")
    _git(repo, env, "add", "-A")
    _git(repo, env, "commit", "-q", "-m", "init")
    _git(repo, env, "checkout", "-q", "-b", "dev")
    _git(repo, env, "checkout", "-q", "-b", TARGET)
    _git(repo, env, "checkout", "-q", "-b", BRANCH)
    (repo / "backlog").mkdir()
    (repo / "backlog" / f"{STORY_ID}.md").write_text(
        f"---\nid: {STORY_ID}\ntitle: Log in\n{field}---\n\n# Log in\n"
    )
    (repo / "docs").mkdir()
    (repo / "docs" / "testing.yaml").write_text(testing_yaml)
    write_review_report(repo, STORY_ID)
    _git(repo, env, "add", "-A")
    _git(repo, env, "commit", "-q", "-m", "story")
    log = tmp_path / "gate-calls.log"
    for name in ("crap-score", "mutation-testing"):
        script = repo / ".agent-factory" / "factory" / "scripts" / name
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(RECORDING_STUB.format(name=name, log=log))
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return repo, env, log


def _run(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), TARGET, BRANCH],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _lines(stdout: str) -> list[str]:
    return [line for line in stdout.splitlines() if line.startswith(LINE_PREFIX)]


def _called(log: Path) -> list[str]:
    return log.read_text().split() if log.exists() else []


@pytest.mark.spec("CG-11-IT-01")
def test_cg_11_a_project_without_a_gates_section_runs_no_crap_score(tmp_path):
    repo, env, log = _build_repo(tmp_path, NO_GATES)
    proc = _run(repo, env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "crap-score" not in _called(log)
    lines = _lines(proc.stdout)
    assert len(lines) == 1, proc.stdout
    assert CRAP_PART in lines[0]
    assert MUTATION_PART in lines[0]
    assert "SKIP dependency-check: docs/spec/dependency-rules.dsl does not exist" in proc.stdout
    assert "PASS semantic-gates: no gate applies" in proc.stdout
    assert "premerge-check: PASS" in proc.stdout


@pytest.mark.spec("CG-11-IT-02")
@pytest.mark.parametrize(
    ("testing_yaml", "field", "named", "not_named", "called"),
    [
        (LICENSE_ONLY, "", [CRAP_PART, MUTATION_PART], [], []),
        (MUTATION_ONLY, "", [CRAP_PART], ["mutation-testing"], []),
        (CRAP_ONLY, "", [MUTATION_PART], ["crap-score"], []),
        # A gate that the field names runs, so the line leaves it out.
        (
            NO_GATES,
            "quality-gates: [mutation-testing]\n",
            [CRAP_PART],
            ["mutation-testing"],
            ["mutation-testing"],
        ),
    ],
    ids=["license-check-only", "mutation-testing-only", "crap-score-only", "field-names-mutation"],
)
def test_cg_11_the_line_names_every_built_in_gate_without_an_entry(
    tmp_path, testing_yaml, field, named, not_named, called
):
    repo, env, log = _build_repo(tmp_path, testing_yaml, field)
    proc = _run(repo, env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    lines = _lines(proc.stdout)
    assert len(lines) == 1, proc.stdout
    for part in named:
        assert part in lines[0]
    for gate in not_named:
        assert gate not in lines[0]
    assert _called(log) == called


@pytest.mark.spec("CG-11-IT-04")
def test_cg_11_a_project_set_up_from_the_charter_template_has_no_crap_gate(tmp_path):
    repo, env, log = _build_repo(tmp_path, TEMPLATE.read_text())
    # The template's test_command runs pytest; the merge here checks the gates only.
    proc = _run(repo, env)
    assert "crap-score" not in _called(log)
    lines = _lines(proc.stdout)
    assert len(lines) == 1, proc.stdout
    assert CRAP_PART in lines[0]
    assert "mutation-testing" not in lines[0]


@pytest.mark.spec("CG-11-IT-03")
def test_cg_11_a_story_that_names_crap_score_before_the_setup_is_refused(tmp_path):
    """Scenario Outline: A story that names crap-score before the setup is refused,
    row premerge-check."""
    repo, env, log = _build_repo(tmp_path, NO_GATES, "quality-gates: [crap-score]\n")
    proc = _run(repo, env)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    block = [line for line in proc.stdout.splitlines() if line.startswith("BLOCK semantic-gates:")]
    assert len(block) == 1, proc.stdout
    assert "crap-score" in block[0]
    assert "setup-crap-score" in block[0]
    assert "GATE CANNOT MEASURE" not in proc.stdout
    assert _called(log) == []
    # The line of DEC-50 leaves out the gate that the field names.
    lines = _lines(proc.stdout)
    assert len(lines) == 1, proc.stdout
    assert CRAP_PART not in lines[0]
    assert MUTATION_PART in lines[0]


@pytest.mark.spec("CG-11-IT-03")
def test_cg_11_the_refusal_of_a_gate_without_an_entry_keeps_the_story_dispatched(tmp_path):
    """Scenario: The refusal of a gate without an entry is not a gate that cannot measure."""
    story = WAVE_STORY.format(id=STORY_ID).replace(
        "quality-gates: []", "quality-gates: [crap-score]"
    )
    run = _build_wave_repo(tmp_path, files={f"backlog/{STORY_ID}.md": story})
    _work_and_review(run["repo"], run["ledger"], run["base"], STORY_ID, code="X = 1\n")

    result = _dispatch(run["feature"], run["ledger"], "merge-story", STORY_ID)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "setup-crap-score" in result.stdout
    assert "GATE CANNOT MEASURE" not in result.stdout + result.stderr
    ledger = yaml.safe_load(run["ledger"].read_text())
    assert ledger["stories"][STORY_ID]["status"] == "dispatched"


# --- ST-0439: the call of crap-score at the merge --------------------------

FINDING_LINT = "packages/factory/scripts/finding-lint"
MEASURE_STUB = "scripts/crap-measure-stub"
READY_STUB = "scripts/crap-ready-backend"

MEASURED = f"""\
test_command: "true"
gates:
  crap-score:
    enabled: true
    threshold: 8
    timeout_minutes: 10
    measures:
      - name: python
        files: "packages/factory/scripts/*"
        command: "{MEASURE_STUB}"
        ready: "{READY_STUB}"
"""

# The measuring command records its folder and plants one row of tree_severity.
# The row shows 100 % coverage only when the test of tree_severity exists.
MEASURE_BODY = """#!/bin/sh
pwd > "$MEASURE_LOG"
if [ -f tests/test_tree_severity.py ]; then cov=100; else cov=0; fi
printf '[{"file": "%s", "function": "tree_severity", "start_line": 10, "end_line": 30, \
"complexity": '"$COMPLEXITY"', "coverage_pct": %s}, {"file": "%s", "function": "bug_bar_level", \
"start_line": 32, "end_line": 50, "complexity": 9, "coverage_pct": 100}]' \
  "$FINDING_LINT" "$cov" "$FINDING_LINT" > "$GATE_OUTPUT"
"""

# The real crap-score of packages/factory/scripts, run by the test interpreter.
REAL_CRAP_SCORE = '#!/bin/sh\nexec "{python}" "{script}" "$@"\n'


def _finding_lint(changed_line: int | None = None) -> str:
    """Fifty lines: tree_severity on lines 10 to 30, bug_bar_level on lines 32 to 50."""
    lines = []
    for number in range(1, 51):
        if number == 10:
            text = "def tree_severity():"
        elif number == 32:
            text = "def bug_bar_level():"
        elif number < 10 or number == 31:
            text = f"# line {number}"
        else:
            text = f"    x{number} = {number}"
        if number == changed_line:
            text = f"    x{number} = 'changed'"
        lines.append(text)
    return "\n".join(lines) + "\n"


def _executable(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _build_measured_repo(
    tmp_path: Path, complexity: int, with_test: bool = False
) -> tuple[Path, dict[str, str], Path]:
    """story/ST-0350 changes one line inside tree_severity of finding-lint.

    The real crap-score is the installed copy. With *with_test*, the story
    branch adds the test of tree_severity. Returns the repository, the
    environment, and the log of the measuring command.
    """
    env = _env(tmp_path)
    log = tmp_path / "measure.log"
    env.update(
        MEASURE_LOG=str(log),
        COMPLEXITY=str(complexity),
        FINDING_LINT=FINDING_LINT,
        READY_LOG=str(tmp_path / "ready.log"),
    )
    env.pop("STORY_ID", None)
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, env, "init", "-q", "-b", "main")
    _git(repo, env, "config", "user.email", "fixture@example.com")
    _git(repo, env, "config", "user.name", "Fixture")
    _git(repo, env, "config", "commit.gpgsign", "false")
    (repo / ".gitignore").write_text(".agent-factory/\n.current-work/\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "testing.yaml").write_text(MEASURED)
    _executable(repo / MEASURE_STUB, MEASURE_BODY)
    _executable(repo / READY_STUB, '#!/bin/sh\necho ready >> "$READY_LOG"\n')
    (repo / FINDING_LINT).parent.mkdir(parents=True)
    (repo / FINDING_LINT).write_text(_finding_lint())
    _git(repo, env, "add", "-A")
    _git(repo, env, "commit", "-q", "-m", "init")
    _git(repo, env, "checkout", "-q", "-b", "dev")
    _git(repo, env, "checkout", "-q", "-b", TARGET)
    _git(repo, env, "checkout", "-q", "-b", BRANCH)
    (repo / "backlog").mkdir()
    (repo / "backlog" / f"{STORY_ID}.md").write_text(
        f"---\nid: {STORY_ID}\ntitle: Log in\n---\n\n# Log in\n"
    )
    (repo / FINDING_LINT).write_text(_finding_lint(changed_line=15))
    if with_test:
        (repo / "tests").mkdir()
        (repo / "tests" / "test_tree_severity.py").write_text("def test_tree_severity(): pass\n")
    write_review_report(repo, STORY_ID)
    _git(repo, env, "add", "-A")
    _git(repo, env, "commit", "-q", "-m", "story")
    _executable(
        repo / ".agent-factory" / "factory" / "scripts" / "crap-score",
        REAL_CRAP_SCORE.format(python=sys.executable, script=SOURCE_SCRIPTS_DIR / "crap-score"),
    )
    return repo, env, log


def _premerge_dir(repo: Path) -> Path:
    return repo / ".current-work" / TARGET / "premerge" / STORY_ID


def _report(repo: Path) -> list[dict]:
    return json.loads((repo / ".current-work" / "crap-score" / f"{STORY_ID}.json").read_text())


@pytest.mark.spec("CG-08-CT-01")
def test_cg_08_the_built_call_of_crap_score_names_the_merge_target(tmp_path):
    """Scenario: premerge-check passes its merge target to crap-score."""
    script = tmp_path / "crap-score"
    worktree = tmp_path / "primary" / ".current-work" / TARGET / "premerge" / STORY_ID
    primary = tmp_path / "primary"
    entries = {"crap-score": {"enabled": True, "threshold": 8}}
    call = pm.gate_command(
        script, "crap-score", worktree, STORY_ID, entries, target=TARGET, primary=primary
    )
    assert call == [
        str(script),
        "--base", TARGET,
        "--story-id", STORY_ID,
        "--report-dir", str(primary / ".current-work" / "crap-score"),
    ]


@pytest.mark.spec("CG-08-IT-01")
def test_cg_08_a_story_that_changes_only_finding_lint_is_scored_at_the_merge(tmp_path):
    """Scenario: A story that changes only scripts without a file ending is scored at the merge."""
    repo, env, _ = _build_measured_repo(tmp_path, complexity=9)
    proc = _run(repo, env)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    block = [line for line in proc.stdout.splitlines() if line.startswith("BLOCK semantic-gates:")]
    assert len(block) == 1, proc.stdout
    assert "crap-score" in block[0]
    assert "tree_severity" in block[0]
    assert "bug_bar_level" not in block[0]
    assert ".py file" not in proc.stdout
    assert [row["function"] for row in _report(repo)] == ["tree_severity"]


@pytest.mark.spec("CG-08-IT-02")
def test_cg_08_the_measuring_command_measures_the_code_of_the_story_branch(tmp_path):
    """Scenario: The measuring command at the merge measures the code of the story branch."""
    repo, env, log = _build_measured_repo(tmp_path, complexity=3, with_test=True)
    # The primary checkout leaves the story branch, so only the head of
    # story/ST-0350 holds the test of tree_severity.
    _git(repo, env, "checkout", "-q", TARGET)
    proc = _run(repo, env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert Path(log.read_text().strip()).resolve() == _premerge_dir(repo).resolve()
    rows = _report(repo)
    assert [(row["function"], row["coverage_pct"]) for row in rows] == [("tree_severity", 100)]


@pytest.mark.spec("CG-08-IT-06")
def test_cg_08_the_report_of_a_refused_merge_stays_in_the_primary_checkout(tmp_path):
    """Scenario: The report of a refused merge stays in the primary checkout."""
    repo, env, _ = _build_measured_repo(tmp_path, complexity=9)
    proc = _run(repo, env)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    rows = _report(repo)
    assert [(row["function"], row["pass_fail"]) for row in rows] == [("tree_severity", "fail")]
    assert not _premerge_dir(repo).exists()


@pytest.mark.spec("CG-08-IT-07")
def test_cg_08_the_feature_merge_runs_no_crap_score(tmp_path):
    """Scenario: The feature merge runs no crap-score."""
    repo, env, log = _build_measured_repo(tmp_path, complexity=9)
    calls = tmp_path / "gate-calls.log"
    _executable(
        repo / ".agent-factory" / "factory" / "scripts" / "crap-score",
        RECORDING_STUB.format(name="crap-score", log=calls),
    )
    _git(repo, env, "checkout", "-q", TARGET)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "dev", TARGET],
        cwd=repo, env=env, capture_output=True, text=True, check=False,
    )
    assert "semantic-gates" not in proc.stdout, proc.stdout
    assert _called(calls) == []
    assert not log.exists()
    assert not (tmp_path / "ready.log").exists()
