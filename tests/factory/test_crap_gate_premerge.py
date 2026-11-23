"""Tests of premerge-check and the CRAP gate entry (ST-0433, ST-0434, ST-0439, ST-0443).

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
from test_run_lifecycle_dispatch import (
    AU,
    CRAP_ENABLED,
    _commit_story_work,
    _dispatched_by_hand,
    _entry,
    _fail,
    _install_crap_score_exit_2,
    _orchestrated_on_login,
)
from test_run_lifecycle_dispatch import _dispatch as _lifecycle_dispatch
from test_run_lifecycle_dispatch import _git as _lifecycle_git

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
    tmp_path: Path,
    testing_yaml: str | bytes,
    field: str = "",
    dev_testing: str | None = None,
) -> tuple[Path, dict[str, str], Path]:
    """A story branch whose docs/testing.yaml is *testing_yaml*, with recording stubs.

    *field* is the story's front-matter line `quality-gates`, or empty.
    *dev_testing* is the docs/testing.yaml that dev holds, or None for no file.
    *testing_yaml* is bytes when the file must hold bytes that are not text.
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
    if dev_testing is not None:
        (repo / "docs").mkdir()
        (repo / "docs" / "testing.yaml").write_text(dev_testing)
        _git(repo, env, "add", "-A")
        _git(repo, env, "commit", "-q", "-m", "dev")
    _git(repo, env, "checkout", "-q", "-b", TARGET)
    _git(repo, env, "checkout", "-q", "-b", BRANCH)
    (repo / "backlog").mkdir()
    (repo / "backlog" / f"{STORY_ID}.md").write_text(
        f"---\nid: {STORY_ID}\ntitle: Log in\n{field}---\n\n# Log in\n"
    )
    (repo / "docs").mkdir(exist_ok=True)
    story_testing = repo / "docs" / "testing.yaml"
    if isinstance(testing_yaml, bytes):
        story_testing.write_bytes(testing_yaml)
    else:
        story_testing.write_text(testing_yaml)
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
# With MEASURE_FAILS set, the command fails, so crap-score cannot measure.
MEASURE_BODY = """#!/bin/sh
pwd > "$MEASURE_LOG"
if [ -n "$MEASURE_FAILS" ]; then echo "the test run failed" >&2; exit 1; fi
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
    call = pm.gate_command(script, "crap-score", worktree, STORY_ID, TARGET, primary)
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


@pytest.mark.spec("CG-08-IT-06")
def test_cg_08_a_refusal_after_exit_2_names_no_function_of_an_earlier_report(tmp_path):
    """IMPL-0071: the report of an earlier refused run stays in the primary
    checkout, so a run that cannot measure must not name its functions."""
    repo, env, _ = _build_measured_repo(tmp_path, complexity=9)
    first = _run(repo, env)
    assert first.returncode == 1, first.stdout + first.stderr
    assert "tree_severity" in first.stdout
    env["MEASURE_FAILS"] = "1"
    second = _run(repo, env)
    # Exit 2 with every other check passing gives exit 3 (ST-0443, BR-136).
    assert second.returncode == 3, second.stdout + second.stderr
    refusal = _refusal(second.stdout)
    assert "cannot measure" in refusal
    assert "the test run failed" in refusal
    assert "tree_severity" not in second.stdout


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


# --- ST-0443: exit 3 when the gate cannot measure at the merge -------------

CANNOT_MEASURE = "GATE CANNOT MEASURE: crap-score"
GATE_REASON = "gate cannot measure: crap-score"
BACKEND_READY = "scripts/crap-ready-backend"
READY_FAILS = '#!/bin/sh\necho ready >> "{log}"\necho "the Compose stack is stopped" >&2\nexit 1\n'
READY_PASSES = '#!/bin/sh\necho ready >> "{log}"\n'


def _refusal(stdout: str) -> str:
    """The refusal of exit 3: the output from the line GATE CANNOT MEASURE on."""
    lines = stdout.splitlines()
    assert CANNOT_MEASURE in lines, stdout
    return "\n".join(lines[lines.index(CANNOT_MEASURE):])


def _ready_yaml(marker: Path, enabled: bool, timeout: float = 10) -> str:
    """crap-score with the measure backend, a recorded license-check, and a suite marker."""
    return f"""\
test_command: "touch {marker}"
gates:
  crap-score:
    enabled: {str(enabled).lower()}
    threshold: 8
    timeout_minutes: {timeout}
    measures:
      - name: backend
        files: "src/*"
        command: "true"
        ready: "{BACKEND_READY}"
  license-check:
    enabled: true
    command: "echo license-check >> {marker.parent / 'gate-calls.log'}"
"""


def _build_ready_repo(
    tmp_path: Path,
    ready: str,
    *,
    enabled: bool = True,
    field: str = "",
    review: bool = True,
    timeout: float = 10,
) -> tuple[Path, dict[str, str], Path, Path]:
    """A story branch whose measure backend has the ready command *ready*.

    Returns the repository, the environment, the log of the gate calls, and
    the marker that the test suite writes.
    """
    marker = tmp_path / "suite-ran"
    ready_yaml = _ready_yaml(marker, enabled, timeout)
    repo, env, log = _build_repo(tmp_path, ready_yaml, field, dev_testing=ready_yaml)
    _executable(
        repo / BACKEND_READY,
        ready.format(log=tmp_path / "ready.log", pidfile=tmp_path / "child.pid"),
    )
    if not review:
        _git(repo, env, "rm", "-q", "-r", "docs/reviews")
    _git(repo, env, "add", "-A")
    _git(repo, env, "commit", "-q", "-m", "ready command")
    return repo, env, log, marker


@pytest.mark.spec("CG-08-IT-05")
def test_cg_08_a_failed_ready_command_stops_premerge_check_before_the_test_suite(tmp_path):
    """Scenario: A failed ready command at the merge stops premerge-check before the test suite."""
    repo, env, log, marker = _build_ready_repo(tmp_path, READY_FAILS)
    proc = _run(repo, env)
    assert proc.returncode == 3, proc.stdout + proc.stderr
    refusal = _refusal(proc.stdout)
    assert "backend" in refusal
    assert BACKEND_READY in refusal
    assert "the Compose stack is stopped" in refusal
    assert not marker.exists(), "the test suite must not run"
    assert _called(log) == [], "no gate may run"
    assert (tmp_path / "ready.log").read_text().split() == ["ready"]
    assert not (repo / ".current-work" / "premerge-check-ok").exists()
    assert not _premerge_dir(repo).exists()


@pytest.mark.spec("CG-08-IT-05")
def test_cg_08_a_failed_ready_command_beside_a_failed_check_gives_exit_1(tmp_path):
    """DEC-29: the review report is missing too, so the code must change anyway."""
    repo, env, log, marker = _build_ready_repo(tmp_path, READY_FAILS, review=False)
    proc = _run(repo, env)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert CANNOT_MEASURE not in proc.stdout
    assert BACKEND_READY in proc.stdout
    assert not marker.exists()
    assert _called(log) == []


# The ready command starts a child, records its PID, and outlives its time limit.
READY_HANGS = '#!/bin/sh\nsleep 120 &\necho $! > "{pidfile}"\nsleep 120\n'


def _gone(pid: int) -> bool:
    """True when *pid* has ended; a zombie that waits for its reaper counts as ended."""
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return True
    return state == "Z"


@pytest.mark.spec("CG-08-IT-05")
def test_cg_08_a_ready_command_past_its_time_limit_is_stopped_with_its_group(tmp_path):
    """IMPL-0082: the time-out stops every process of the ready command, as crap-score does."""
    # 0.05 minutes are 3 seconds, enough for the stub to start its child under load.
    repo, env, log, marker = _build_ready_repo(tmp_path, READY_HANGS, timeout=0.05)
    pidfile = tmp_path / "child.pid"
    proc = _run(repo, env)
    pid = int(pidfile.read_text()) if pidfile.exists() else None
    try:
        assert proc.returncode == 3, proc.stdout + proc.stderr
        assert "ran out of timeout_minutes" in _refusal(proc.stdout)
        assert pid is not None, "the ready stub must start its child before the time-out"
        # The reaper may need a moment after the SIGTERM; wait up to 10 seconds.
        for _ in range(100):
            if _gone(pid):
                break
            subprocess.run(["sleep", "0.1"], check=True)
        assert _gone(pid), "the child of the ready command must not outlive premerge-check"
        assert not marker.exists()
        assert _called(log) == []
    finally:
        if pid is not None and not _gone(pid):
            os.kill(pid, 9)


@pytest.mark.spec("CG-08-IT-05")
def test_cg_08_only_the_measures_of_crap_score_have_ready_commands():
    entries = {
        "crap-score": {"measures": [{"name": "backend", "ready": BACKEND_READY}]},
        "license-check": {"measures": [{"name": "other", "ready": "scripts/other-ready"}]},
    }
    found = pm.ready_commands(["license-check", "crap-score"], entries)
    assert found == [("crap-score", "backend", BACKEND_READY)]


@pytest.mark.spec("CG-08-IT-05")
def test_cg_08_a_passing_ready_command_runs_before_the_suite_and_the_gates(tmp_path):
    repo, env, log, marker = _build_ready_repo(tmp_path, READY_PASSES)
    proc = _run(repo, env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert marker.exists()
    assert _called(log) == ["crap-score", "license-check"]
    assert (tmp_path / "ready.log").read_text().split() == ["ready"]


@pytest.mark.spec("CG-08-IT-08")
def test_cg_08_a_disabled_gate_that_the_story_names_runs_its_ready_commands(tmp_path):
    """Scenario: A disabled gate that a story names runs its ready commands at the merge."""
    repo, env, log, marker = _build_ready_repo(
        tmp_path, READY_FAILS, enabled=False, field="quality-gates: [crap-score]\n"
    )
    proc = _run(repo, env)
    assert proc.returncode == 3, proc.stdout + proc.stderr
    assert BACKEND_READY in _refusal(proc.stdout)
    assert (tmp_path / "ready.log").read_text().split() == ["ready"]
    assert not marker.exists()


@pytest.mark.spec("CG-08-IT-08")
def test_cg_08_a_disabled_gate_that_no_story_names_runs_no_ready_command(tmp_path):
    repo, env, log, marker = _build_ready_repo(tmp_path, READY_FAILS, enabled=False)
    proc = _run(repo, env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert not (tmp_path / "ready.log").exists()
    assert marker.exists()


@pytest.mark.spec("CG-08-IT-09")
def test_cg_08_the_refusal_names_the_failing_functions_from_the_report_after_exit_1(tmp_path):
    """Scenario: The refusal names the failing functions from the report after exit 1."""
    repo, env, _ = _build_measured_repo(tmp_path, complexity=9)
    proc = _run(repo, env)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    block = [line for line in proc.stdout.splitlines() if line.startswith("BLOCK semantic-gates:")]
    assert len(block) == 1, proc.stdout
    assert "crap-score (failed: tree_severity" in block[0]
    assert CANNOT_MEASURE not in proc.stdout


@pytest.mark.spec("CG-08-IT-09")
def test_cg_08_the_exit_code_of_crap_score_alone_decides_at_the_merge(tmp_path):
    """Scenario: The exit code of crap-score alone decides at the merge."""
    repo, env, log = _build_repo(tmp_path, CRAP_ENABLED, dev_testing=CRAP_ENABLED)
    earlier = repo / ".current-work" / "crap-score" / f"{STORY_ID}.json"
    earlier.parent.mkdir(parents=True)
    earlier.write_text(json.dumps([
        {"file": FINDING_LINT, "function": "tree_severity", "crap_score": 90, "pass_fail": "fail"}
    ]))
    proc = _run(repo, env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert _called(log) == ["crap-score"]
    assert "PASS semantic-gates: crap-score passed" in proc.stdout


def _one_attempt(run: dict) -> None:
    """Fail ST-0350 once, then dispatch it again for its retry."""
    _fail(run, AU, 1)
    for step in ("re-dispatch", "mark-dispatching", "mark-dispatched"):
        result = _lifecycle_dispatch(run["repo"], run["ledger"], step, STORY_ID)
        assert result.returncode == 0, (step, result.stdout, result.stderr)
    assert len(_entry(run).attempts) == 1


@pytest.mark.spec("CG-08-IT-03")
@pytest.mark.parametrize("way", ["orchestrated", "by_hand"])
def test_cg_08_a_gate_that_cannot_measure_at_the_merge_blocks_the_story(tmp_path, way):
    """Scenario Outline: A gate that cannot measure at the merge blocks the story on both ways."""
    if way == "by_hand":
        run = _dispatched_by_hand(tmp_path, code="x = 1\n", rules=False, testing=CRAP_ENABLED)
        where = run["repo"]
    else:
        run = _orchestrated_on_login(tmp_path, testing=CRAP_ENABLED)
        where = run["feature"]
    _one_attempt(run)
    if way == "orchestrated":
        _commit_story_work(run)
    _install_crap_score_exit_2(run["repo"])
    tip = _lifecycle_git(run["repo"], "rev-parse", TARGET)
    attempts = _entry(run).attempts

    result = _lifecycle_dispatch(where, run["ledger"], "merge-story", STORY_ID)

    assert result.returncode == 1, result.stdout + result.stderr
    refusal = _refusal(result.stdout)
    assert "the measuring command of measure python exited 1" in refusal
    entry = _entry(run)
    assert entry.status.value == "blocked"
    assert entry.reason == GATE_REASON
    assert entry.attempts == attempts
    assert _lifecycle_git(run["repo"], "rev-parse", TARGET) == tip


@pytest.mark.spec("CG-08-IT-03")
def test_cg_08_the_dry_run_of_a_gate_that_cannot_measure_changes_no_entry(tmp_path):
    run = _dispatched_by_hand(tmp_path, code="x = 1\n", rules=False, testing=CRAP_ENABLED)
    _install_crap_score_exit_2(run["repo"])
    result = _lifecycle_dispatch(run["repo"], run["ledger"], "merge-story", STORY_ID, "--dry-run")
    assert result.returncode == 1, result.stdout + result.stderr
    assert CANNOT_MEASURE in result.stdout
    assert f"merge-story would set {STORY_ID} blocked" in result.stderr
    assert "no ledger entry changed" in result.stderr
    assert _entry(run).status.value == "dispatched"


@pytest.mark.spec("CG-08-IT-04")
def test_cg_08_a_gate_that_cannot_measure_beside_another_failed_check_keeps_the_story(tmp_path):
    """Scenario: A gate that cannot measure beside another failed check keeps the story dispatched."""
    run = _dispatched_by_hand(tmp_path, code="import infra\n", rules=True, testing=CRAP_ENABLED)
    _install_crap_score_exit_2(run["repo"])
    tip = _lifecycle_git(run["repo"], "rev-parse", TARGET)

    result = _lifecycle_dispatch(run["repo"], run["ledger"], "merge-story", STORY_ID)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "BLOCK semantic-gates:" in result.stdout
    assert "dependency-check" in result.stdout
    assert CANNOT_MEASURE not in result.stdout
    assert _entry(run).status.value == "dispatched"
    assert _lifecycle_git(run["repo"], "rev-parse", TARGET) == tip


# --- SEC-0011: dev decides whether the CRAP gate runs (DEC-80, DEC-82) ---

CRAP_TRUE = 'test_command: "true"\ngates:\n  crap-score:\n    enabled: true\n'
CRAP_FALSE = 'test_command: "true"\ngates:\n  crap-score:\n    enabled: false\n'
CRAP_PASSED_LINE = "PASS semantic-gates: crap-score passed"


def test_sec_0011_dev_enabled_gate_runs_when_the_story_disables_it(tmp_path):
    repo, env, log = _build_repo(tmp_path, CRAP_ONLY, dev_testing=CRAP_TRUE)
    proc = _run(repo, env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "crap-score" in _called(log)
    assert CRAP_PASSED_LINE in proc.stdout


def test_sec_0011_dev_enabled_gate_runs_when_the_story_removes_its_entry(tmp_path):
    repo, env, log = _build_repo(tmp_path, NO_GATES, dev_testing=CRAP_TRUE)
    proc = _run(repo, env)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    # The gate runs and refuses without the entry at the story head, before it measures.
    assert "crap-score (no entry gates.crap-score" in proc.stdout
    assert _called(log) == []


def test_sec_0011_story_cannot_switch_on_a_gate_that_dev_disables(tmp_path):
    repo, env, log = _build_repo(tmp_path, CRAP_TRUE, dev_testing=CRAP_FALSE)
    proc = _run(repo, env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "crap-score" not in _called(log)


def test_sec_0011_no_dev_with_a_head_entry_cannot_measure(tmp_path):
    repo, env, log = _build_repo(tmp_path, CRAP_TRUE)
    _git(repo, env, "update-ref", "-d", "refs/heads/dev")
    proc = _run(repo, env)
    assert proc.returncode == 3, proc.stdout + proc.stderr
    assert CANNOT_MEASURE in proc.stdout
    assert _called(log) == []


def test_sec_0011_no_dev_without_a_head_entry_runs_no_crap_score(tmp_path):
    repo, env, log = _build_repo(tmp_path, NO_GATES)
    _git(repo, env, "update-ref", "-d", "refs/heads/dev")
    proc = _run(repo, env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "crap-score" not in _called(log)
    assert CANNOT_MEASURE not in proc.stdout


# BUG-0137: a docs/testing.yaml that is not valid YAML, empty, a list, or has a
# gates.crap-score that is no mapping. On dev it cannot measure (BR-136, DEC-83);
# at the story head it refuses with exit 1 and names the file (DEC-83).
CRAP_SCALAR = 'test_command: "true"\ngates:\n  crap-score: true\n'
DEV_BROKEN = [
    pytest.param("gates: [unclosed\n", id="unparseable"),
    pytest.param("", id="empty"),
    pytest.param("- crap-score\n", id="list"),
    pytest.param(CRAP_SCALAR, id="crap-score-not-a-mapping"),
    pytest.param("gates:\n  - crap-score\n", id="gates-list"),
    pytest.param("gates: true\n", id="gates-scalar"),
]
HEAD_BROKEN = [
    pytest.param("gates: [unclosed\n", id="unparseable"),
    pytest.param("", id="empty"),
    pytest.param("- crap-score\n", id="list"),
    pytest.param("gates:\n  - crap-score\n", id="gates-list"),
    pytest.param("gates: true\n", id="gates-scalar"),
    pytest.param(b'gates:\n  crap-score: "\xff"\n', id="not-utf8"),
    pytest.param("gates:\n  crap-score: 5\n", id="crap-score-not-a-mapping"),
    pytest.param('gates:\n  crap_score: "on"\n', id="crap_score-not-a-mapping"),
]


@pytest.mark.parametrize("dev_testing", DEV_BROKEN)
def test_bug_0137_broken_dev_settings_cannot_measure_without_traceback(tmp_path, dev_testing):
    repo, env, log = _build_repo(tmp_path, CRAP_ONLY, dev_testing=dev_testing)
    proc = _run(repo, env)
    assert proc.returncode == 3, proc.stdout + proc.stderr
    assert "Traceback" not in proc.stdout + proc.stderr
    assert CANNOT_MEASURE in proc.stdout
    message = proc.stdout.split(CANNOT_MEASURE, 1)[1].splitlines()[1]
    assert "docs/testing.yaml" in message
    assert "dev" in message
    assert "crap-score" not in _called(log)


@pytest.mark.parametrize("dev_testing", [None, CRAP_ONLY], ids=["no-dev", "dev"])
@pytest.mark.parametrize("head_testing", HEAD_BROKEN)
def test_bug_0137_broken_story_settings_refuse_and_name_the_file(
    tmp_path, head_testing, dev_testing
):
    repo, env, log = _build_repo(tmp_path, head_testing, dev_testing=dev_testing)
    proc = _run(repo, env)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "Traceback" not in proc.stdout + proc.stderr
    assert any(
        line.startswith("BLOCK") and "docs/testing.yaml" in line
        for line in proc.stdout.splitlines()
    ), proc.stdout
    assert _called(log) == []


# BUG-0138: the feature merge reads test_command from the feature branch, so a broken
# docs/testing.yaml of the feature branch must refuse with BLOCK testing-yaml and exit 1
# without a traceback, as DEC-83 requires for the story merge.
FEATURE_BROKEN = [
    pytest.param('test_command: "true"\ngates: []\n', id="gates-list"),
    pytest.param('test_command: "true"\ngates: [unclosed\n', id="unparseable"),
]


def _build_feature_repo(tmp_path: Path, feature_testing: str) -> tuple[Path, dict[str, str]]:
    """A repository whose feature branch holds docs/testing.yaml *feature_testing*."""
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
    (repo / "docs").mkdir()
    (repo / "docs" / "testing.yaml").write_text(feature_testing)
    _git(repo, env, "add", "-A")
    _git(repo, env, "commit", "-q", "-m", "feature")
    _git(repo, env, "checkout", "-q", "dev")
    return repo, env


@pytest.mark.parametrize("feature_testing", FEATURE_BROKEN)
def test_bug_0138_broken_feature_settings_refuse_without_traceback(tmp_path, feature_testing):
    repo, env = _build_feature_repo(tmp_path, feature_testing)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "dev", TARGET],
        cwd=repo, env=env, capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "Traceback" not in proc.stdout + proc.stderr
    assert any(
        line.startswith("BLOCK testing-yaml:") and "docs/testing.yaml" in line and TARGET in line
        for line in proc.stdout.splitlines()
    ), proc.stdout
