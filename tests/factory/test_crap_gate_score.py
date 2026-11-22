"""Integration tests: crap-score as a subprocess on temporary git repositories (ST-0436).

docs/spec/features/crap-gate-setup.feature, Rule "Implementation agent gets one
verdict for the functions a story changed". Each test builds its own
repository in `tmp_path` with the branches `dev`, `feature/login` and
`story/ST-0350`, as the QA strategy of crap-gate-setup defines. The measuring
command is a stub that copies the planted rows of `PLANTED_ROWS` to
`GATE_OUTPUT`.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import time
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR

SCRIPT = SOURCE_SCRIPTS_DIR / "crap-score"
STORY_ID = "ST-0350"
BRANCH = f"story/{STORY_ID}"
TARGET = "feature/login"
FINDING_LINT = "packages/factory/scripts/finding-lint"
STUB = "scripts/crap-measure-stub"

TESTING_YAML = f"""\
test_command: "true"
gates:
  crap-score:
    enabled: true
    threshold: 8
    timeout_minutes: 10
    measures:
      - name: python
        files: "packages/factory/scripts/*"
        command: "{STUB}"
"""

COPY_STUB = '#!/bin/sh\ncp "$PLANTED_ROWS" "$GATE_OUTPUT"\n'
FAILING_STUB = '#!/bin/sh\necho "coverage cannot reach finding-lint" >&2\nexit 1\n'


def _finding_lint(changed: dict[int, str] | None = None, deleted: tuple[int, ...] = ()) -> str:
    """Fifty lines: tree_severity on lines 10 to 30, bug_bar_level on lines 32 to 50."""
    lines = []
    for number in range(1, 51):
        if number == 10:
            text = "def tree_severity():"
        elif number == 32:
            text = "def bug_bar_level():"
        elif number in (31,) or number < 10:
            text = f"# line {number}"
        else:
            text = f"    x{number} = {number}"
        lines.append((changed or {}).get(number, text))
    return "\n".join(line for n, line in enumerate(lines, 1) if n not in deleted) + "\n"


def _row(function: str, start: int, end: int, complexity: int = 9, coverage: float = 100) -> dict:
    return {
        "file": FINDING_LINT, "function": function, "start_line": start, "end_line": end,
        "complexity": complexity, "coverage_pct": coverage,
    }


ROWS = [_row("tree_severity", 10, 30), _row("bug_bar_level", 32, 50)]


class Repo:
    """A temporary repository with dev, feature/login and story/ST-0350."""

    def __init__(self, tmp_path: Path) -> None:
        self.tmp = tmp_path
        home = tmp_path / "home"
        home.mkdir()
        self.env = {
            k: v for k, v in os.environ.items()
            if not k.startswith(("GIT_", "COVERAGE_")) and k != "STORY_ID"
        }
        self.env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1")
        self.root = tmp_path / "repo"
        self.root.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "fixture@example.com")
        self.git("config", "user.name", "Fixture")
        self.git("config", "commit.gpgsign", "false")
        self.write(".gitignore", ".current-work/\n")
        self.write("docs/testing.yaml", TESTING_YAML)
        self.stub(COPY_STUB)
        self.write(FINDING_LINT, _finding_lint())
        self.commit("init")
        self.git("checkout", "-q", "-b", "dev")
        self.git("checkout", "-q", "-b", TARGET)
        self.git("checkout", "-q", "-b", BRANCH)
        self.plant(ROWS)

    def git(self, *args: str, cwd: Path | None = None) -> str:
        return subprocess.run(
            ["git", *args], cwd=cwd or self.root, env=self.env,
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    def write(self, relative: str, text: str, root: Path | None = None) -> None:
        path = (root or self.root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def stub(self, text: str, root: Path | None = None) -> None:
        self.write(STUB, text, root)
        path = (root or self.root) / STUB
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def commit(self, message: str, cwd: Path | None = None) -> None:
        self.git("add", "-A", cwd=cwd)
        self.git("commit", "-q", "-m", message, cwd=cwd)

    def plant(self, rows: list[dict]) -> None:
        planted = self.tmp / "planted.json"
        planted.write_text(json.dumps(rows))
        self.env["PLANTED_ROWS"] = str(planted)

    def change(self, text: str, message: str = "change") -> None:
        self.write(FINDING_LINT, text)
        self.commit(message)

    def run(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], cwd=cwd or self.root, env=self.env,
            capture_output=True, text=True, check=False,
        )

    def report(self, story_id: str = STORY_ID, root: Path | None = None) -> list[dict]:
        path = (root or self.root) / ".current-work" / "crap-score" / f"{story_id}.json"
        return json.loads(path.read_text())


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    return Repo(tmp_path)


def _judged(repo: Repo) -> list[str]:
    return [row["function"] for row in repo.report()]


# --- CG-04-IT-01: a changed function is judged and named -------------------


@pytest.mark.spec("CG-04-IT-01")
def test_cg_04_a_changed_function_above_the_threshold_fails_and_is_named(repo):
    """Scenario: A changed function above the threshold fails the gate and is named."""
    repo.change(_finding_lint({15: "    x15 = 'changed'"}))
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert "bug_bar_level" not in proc.stdout
    assert repo.report() == [{**ROWS[0], "crap_score": 9.0, "pass_fail": "fail"}]


@pytest.mark.spec("CG-04-IT-01")
def test_cg_04_a_function_the_story_does_not_change_passes(repo):
    """Scenario: A function above the threshold that the story does not change passes."""
    repo.change(_finding_lint({5: "# a comment"}))
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert repo.report() == []


# --- CG-04-IT-02: deletions, read from a real git diff ---------------------


@pytest.mark.spec("CG-04-IT-02")
def test_cg_04_a_function_with_only_deleted_lines_counts_as_changed(repo):
    """Scenario: A function in which lines were only deleted counts as changed."""
    repo.change(_finding_lint(deleted=(15, 16)))
    repo.plant([_row("tree_severity", 10, 28), _row("bug_bar_level", 30, 48)])
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert _judged(repo) == ["tree_severity"]


@pytest.mark.spec("CG-04-IT-02")
def test_cg_04_a_deletion_between_two_functions_counts_for_both(repo):
    """Scenario: A deletion between two functions counts for both neighbours."""
    repo.change(_finding_lint(deleted=(29, 30)))
    repo.plant([_row("tree_severity", 10, 28), _row("bug_bar_level", 30, 48)])
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert _judged(repo) == ["tree_severity", "bug_bar_level"]


# --- CG-04-IT-03: only the story's own changes count -----------------------


def _merge_story(repo: Repo, story: str, text: str) -> None:
    """Commit *text* on story/<story> from feature/login and merge it into feature/login."""
    current = repo.git("rev-parse", "--abbrev-ref", "HEAD")
    repo.git("checkout", "-q", TARGET)
    repo.git("checkout", "-q", "-b", f"story/{story}")
    repo.change(text, f"feat: {story}")
    repo.git("checkout", "-q", TARGET)
    repo.git("merge", "-q", "--no-ff", "-m", f"merge {story}", f"story/{story}")
    repo.git("checkout", "-q", current)


@pytest.mark.spec("CG-04-IT-03")
def test_cg_04_a_change_of_an_earlier_story_is_not_judged(repo):
    """Scenario: A function changed only by an earlier story on the feature branch does not fail."""
    repo.git("checkout", "-q", TARGET)
    repo.git("branch", "-q", "-D", BRANCH)
    _merge_story(repo, "ST-0349", _finding_lint({15: "    x15 = 'ST-0349'"}))
    repo.git("checkout", "-q", "-b", BRANCH)
    repo.change(_finding_lint({15: "    x15 = 'ST-0349'", 5: "# ST-0350"}))
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert repo.report() == []


@pytest.mark.spec("CG-04-IT-03")
def test_cg_04_a_change_after_the_story_branched_is_not_judged(repo):
    """Scenario: A change that the feature branch gets after the story branched does not count."""
    repo.change(_finding_lint({5: "# ST-0350"}))
    _merge_story(repo, "ST-0351", _finding_lint({15: "    x15 = 'ST-0351'"}))
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert repo.report() == []


# --- CG-04-IT-04: --all judges every function ------------------------------


@pytest.mark.spec("CG-04-IT-04")
def test_cg_04_all_judges_a_function_no_commit_changed(repo):
    """Scenario: crap-score --all judges every measured function."""
    proc = repo.run("--all", "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert _judged(repo) == ["tree_severity", "bug_bar_level"]
    assert "tree_severity 9.00" in proc.stdout
    assert "bug_bar_level 9.00" in proc.stdout


# --- CG-04-IT-05: one commit gives one verdict -----------------------------


@pytest.mark.spec("CG-04-IT-05")
def test_cg_04_two_runs_on_one_commit_give_the_same_verdict(repo):
    """Scenario: One commit and one state of the exceptions register get the same verdict."""
    repo.change(_finding_lint({15: "    x15 = 'changed'"}))
    first = repo.run("--base", TARGET, "--story-id", STORY_ID)
    first_rows = repo.report()
    second = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert first.returncode == second.returncode == 1
    assert repo.report() == first_rows


# --- CG-04-IT-07 and CG-04-IT-09: a failing measure, and the report --------


@pytest.mark.spec("CG-04-IT-07")
def test_cg_04_a_failing_measuring_command_cannot_measure(repo):
    """Scenario: A run that cannot measure writes no report."""
    later = repo.tmp / "later.log"
    repo.write(
        "docs/testing.yaml",
        TESTING_YAML
        + '      - name: later\n        files: "**"\n'
        + f'        command: "echo started >> {later}"\n',
    )
    repo.stub(FAILING_STUB)
    repo.commit("failing stub")
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "measure python" in proc.stderr
    assert STUB in proc.stderr
    assert "coverage cannot reach finding-lint" in proc.stderr
    assert not later.exists()
    assert not (repo.root / ".current-work" / "crap-score" / f"{STORY_ID}.json").exists()


@pytest.mark.spec("CG-04-IT-09")
def test_cg_04_the_report_holds_a_score_and_a_result_and_replaces_the_earlier_one(repo):
    """Scenarios: The report holds a score and a result for each row; a new report replaces it."""
    report_dir = repo.root / ".current-work" / "crap-score"
    report_dir.mkdir(parents=True)
    (report_dir / f"{STORY_ID}.json").write_text('[{"function": "earlier"}]\n')
    repo.plant([_row("tree_severity", 10, 30, 3, 0), _row("bug_bar_level", 32, 50, 2, 100)])
    proc = repo.run("--all", "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert repo.report() == [
        {**_row("tree_severity", 10, 30, 3, 0), "crap_score": 12.0, "pass_fail": "fail"},
        {**_row("bug_bar_level", 32, 50, 2, 100), "crap_score": 2.0, "pass_fail": "pass"},
    ]


@pytest.mark.spec("CG-04-IT-09")
def test_cg_04_exit_2_keeps_the_earlier_report_byte_for_byte(repo):
    """Scenario: A run that cannot measure writes no report."""
    repo.run("--all", "--story-id", STORY_ID)
    path = repo.root / ".current-work" / "crap-score" / f"{STORY_ID}.json"
    before = path.read_bytes()
    repo.stub(FAILING_STUB)
    repo.commit("failing stub")
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 2
    assert path.read_bytes() == before


@pytest.mark.spec("CG-04-IT-09")
def test_cg_04_report_dir_names_the_folder_of_the_report(repo):
    other = repo.tmp / "reports"
    proc = repo.run("--all", "--story-id", STORY_ID, "--report-dir", str(other))
    assert proc.returncode == 1
    assert len(json.loads((other / f"{STORY_ID}.json").read_text())) == 2
    assert not (repo.root / ".current-work" / "crap-score").exists()


# --- CG-04-IT-10: the folder the gate runs in ------------------------------


@pytest.mark.spec("CG-04-IT-10")
def test_cg_04_a_linked_worktree_reads_its_own_testing_yaml(repo):
    """Scenario Outline: The gate-check step runs crap-score in the folder of the story."""
    repo.git("checkout", "-q", TARGET)
    worktree = repo.tmp / "worktree"
    repo.git("worktree", "add", "-q", str(worktree), BRANCH)
    repo.write("docs/testing.yaml", TESTING_YAML.replace("threshold: 8", "threshold: 9"), worktree)
    repo.commit("threshold 9", cwd=worktree)
    proc = repo.run("--all", "--story-id", STORY_ID, cwd=worktree)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert {row["pass_fail"] for row in repo.report(root=worktree)} == {"pass"}
    assert not (repo.root / ".current-work").exists()


# --- CG-04-IT-11: a parse error of a changed file fails --------------------


@pytest.mark.spec("CG-04-IT-11")
def test_cg_04_a_parse_error_of_a_changed_file_fails_the_gate(repo):
    """Scenario: A file the measuring command cannot parse fails the gate."""
    repo.write("packages/factory/scripts/untouched", "def broken(:\n")
    repo.commit("untouched file", cwd=None)
    repo.git("branch", "-q", "-f", TARGET, "HEAD")
    repo.change(_finding_lint({15: "    x15 = ("}))
    repo.plant([
        {"file": FINDING_LINT, "parse_error": "invalid syntax (line 15)"},
        {"file": "packages/factory/scripts/untouched", "parse_error": "invalid syntax (line 1)"},
    ])
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert FINDING_LINT in proc.stdout
    assert "invalid syntax (line 15)" in proc.stdout
    assert "untouched" not in proc.stdout
    assert repo.report() == [
        {"file": FINDING_LINT, "parse_error": "invalid syntax (line 15)", "pass_fail": "fail"}
    ]


# --- CG-04-IT-12: --base takes any revision --------------------------------


@pytest.mark.spec("CG-04-IT-12")
@pytest.mark.parametrize("by_id", [False, True], ids=["branch", "commit"])
def test_cg_04_base_takes_a_branch_or_a_commit(repo, by_id):
    """Scenario Outline: --base takes any git revision."""
    repo.change(_finding_lint({15: "    x15 = 'changed'"}))
    base = repo.git("rev-parse", TARGET) if by_id else TARGET
    proc = repo.run("--base", base, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert _judged(repo) == ["tree_severity"]


# --- CG-04-IT-01: the diff paths do not depend on git config or quoting ----


def _new_file_is_judged(repo: Repo, relative: str) -> None:
    """Commit a new file at *relative* and assert that its function is judged."""
    repo.write(relative, _finding_lint())
    repo.commit("new file")
    repo.plant([{**_row("tree_severity", 10, 30), "file": relative}])
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert [row["file"] for row in repo.report()] == [relative]


@pytest.mark.spec("CG-04-IT-01")
def test_cg_04_diff_noprefix_in_the_git_config_still_judges_the_change(repo):
    """IMPL-0069: diff.noprefix=true must not change the paths of the diff."""
    repo.git("config", "diff.noprefix", "true")
    repo.change(_finding_lint({15: "    x15 = 'changed'"}))
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert _judged(repo) == ["tree_severity"]


@pytest.mark.spec("CG-04-IT-01")
def test_cg_04_a_path_with_a_space_is_judged(repo):
    """IMPL-0069: git ends a path with a space in a tab, which is no part of the path."""
    _new_file_is_judged(repo, "packages/factory/scripts/my mod")


@pytest.mark.spec("CG-04-IT-01")
def test_cg_04_a_quoted_path_is_judged(repo):
    """IMPL-0069: git quotes a path with a quote or a backslash, also with core.quotePath=false."""
    _new_file_is_judged(repo, 'packages/factory/scripts/a"b\\c')


@pytest.mark.spec("CG-04-IT-01")
def test_cg_04_a_changed_latin_1_source_file_is_judged(repo):
    """A changed line that is not UTF-8 does not stop the diff (ST-0440)."""
    text = _finding_lint({15: "    x15 = 'Gr\xfcnde'"})
    (repo.root / FINDING_LINT).write_bytes(text.encode("latin-1"))
    repo.commit("change in Latin-1")
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert repo.report() == [{**ROWS[0], "crap_score": 9.0, "pass_fail": "fail"}]

@pytest.mark.spec("CG-04-IT-01")
def test_cg_04_an_added_line_that_starts_with_two_pluses_is_no_file_header(repo):
    """IMPL-0069: with --unified=0 the added line "++ x" reads "+++ x" in the diff."""
    repo.change(_finding_lint({15: "++ x", 40: "    x40 = 'changed'"}))
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert _judged(repo) == ["tree_severity", "bug_bar_level"]


# --- CG-04-IT-06 to CG-04-IT-08: the ready command and the time limit -----

READY = "scripts/crap-ready-backend"
BACKEND_STUB = "scripts/crap-measure-backend"


def _log_stub(event: str, then: str = "") -> str:
    """A stub that appends *event* and its GATE_OUTPUT to $STUB_LOG, then runs *then*."""
    return f'#!/bin/sh\necho "{event} $GATE_OUTPUT" >> "$STUB_LOG"\n{then}'


def _with_backend(repo: Repo, enabled: bool = True, timeout: float = 10,
                  ready: str = _log_stub("ready"),
                  backend: str = _log_stub("backend", 'echo "[]" > "$GATE_OUTPUT"\n'),
                  python: str = _log_stub("python", 'cp "$PLANTED_ROWS" "$GATE_OUTPUT"\n')) -> Path:
    """Add the measure backend with a ready command before python; return the stub log."""
    log = repo.tmp / "stub.log"
    repo.env["STUB_LOG"] = str(log)
    repo.write(
        "docs/testing.yaml",
        TESTING_YAML.replace("enabled: true", f"enabled: {str(enabled).lower()}")
        .replace("timeout_minutes: 10", f"timeout_minutes: {timeout}")
        .replace(
            "    measures:\n",
            "    measures:\n      - name: backend\n        files: \"backend/**\"\n"
            f"        command: \"{BACKEND_STUB}\"\n        ready: \"{READY}\"\n",
        ),
    )
    for relative, text in ((READY, ready), (BACKEND_STUB, backend), (STUB, python)):
        repo.write(relative, text)
        path = repo.root / relative
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
    repo.commit("measure backend")
    return log


def _events(log: Path) -> list[str]:
    return [line.split()[0] for line in log.read_text().splitlines()] if log.exists() else []


@pytest.mark.spec("CG-04-IT-06")
@pytest.mark.parametrize("enabled", [True, False], ids=["enabled", "disabled"])
def test_cg_04_the_ready_command_runs_before_the_measures_in_list_order(repo, enabled):
    """Scenarios: The measures run in list order; a disabled gate runs its ready commands."""
    log = _with_backend(repo, enabled=enabled)
    proc = repo.run("--all", "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert _events(log) == ["ready", "backend", "python"]
    outputs = [line.split()[1] for line in log.read_text().splitlines()]
    assert outputs[1] != outputs[2]


@pytest.mark.spec("CG-04-IT-07")
def test_cg_04_a_failing_ready_command_starts_no_measuring_command(repo):
    """Scenario: A run that cannot measure writes no report (the ready command exits 1)."""
    log = _with_backend(
        repo, ready=_log_stub("ready", 'echo "the Compose stack is stopped" >&2\nexit 1\n')
    )
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "measure backend" in proc.stderr
    assert READY in proc.stderr
    assert "the Compose stack is stopped" in proc.stderr
    assert _events(log) == ["ready"]
    assert not (repo.root / ".current-work" / "crap-score" / f"{STORY_ID}.json").exists()


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    status = Path(f"/proc/{pid}/stat")
    return not (status.exists() and status.read_text().split()[2] == "Z")


@pytest.mark.spec("CG-04-IT-08")
@pytest.mark.parametrize("stopped", ["measuring command", "ready command"])
def test_cg_04_the_time_limit_covers_every_command_of_the_run(repo, stopped):
    """Scenario: The time limit covers the whole gate run.

    Measuring command: each command alone fits in 0.1 minutes (6 s), the two
    together do not, so the limit runs out in python. Ready command: the ready
    command of backend sleeps past the limit. In both cases the stopped
    command has started a child process, which must not outlive the gate.
    """
    child = repo.tmp / "child.pid"
    spawn = f'sleep 60 &\necho $! > "{child}"\n'
    if stopped == "measuring command":
        log = _with_backend(
            repo, timeout=0.1,
            backend=_log_stub("backend", 'echo "[]" > "$GATE_OUTPUT"\nsleep 4\n'),
            python=_log_stub("python", f'{spawn}sleep 4\ncp "$PLANTED_ROWS" "$GATE_OUTPUT"\n'),
        )
        measure, events = "python", ["ready", "backend", "python"]
    else:
        log = _with_backend(repo, timeout=0.1, ready=_log_stub("ready", f"{spawn}sleep 60\n"))
        measure, events = "backend", ["ready"]
    started = time.monotonic()
    proc = repo.run("--all", "--story-id", STORY_ID)
    elapsed = time.monotonic() - started
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert f"measure {measure}" in proc.stderr
    assert f"stopped its {stopped}" in proc.stderr
    assert "0.1 minutes" in proc.stderr
    assert _events(log) == events
    assert elapsed < 25
    pid = int(child.read_text())
    deadline = time.monotonic() + 5
    while _alive(pid) and time.monotonic() < deadline:
        time.sleep(0.05)
    assert not _alive(pid)


# --- CG-05-IT-01: the exceptions register on dev ----------------------------

REGISTER = "docs/findings/exceptions.md"
REASON = "Each branch handles one finding class"
REGISTER_TEXT = f"""\
# Exceptions

## CRAP score

| File | Function | Accepted score | Reason | Accepted by |
| ---- | -------- | -------------- | ------ | ----------- |
| `{FINDING_LINT}` | `tree_severity` | 9 | {REASON} | A. Example |
"""
NO_DEV_LINE = "crap-score: read no exceptions register, because no branch dev exists"


def _commit_register(repo: Repo, branch: str, text: str = REGISTER_TEXT) -> None:
    current = repo.git("symbolic-ref", "--short", "HEAD")
    repo.git("checkout", "-q", branch)
    repo.write(REGISTER, text)
    repo.commit(f"register on {branch}")
    repo.git("checkout", "-q", current)


def _change_tree(repo: Repo) -> None:
    repo.change(_finding_lint({15: "    x15 = 'changed'"}))


@pytest.mark.spec("CG-05-IT-01")
def test_cg_05_a_function_accepted_on_dev_passes_and_stays_visible(repo):
    """Scenario: A function accepted on dev passes and stays visible."""
    _commit_register(repo, "dev")
    _change_tree(repo)
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert f"ACCEPTED {FINDING_LINT} tree_severity 9.00: {REASON}" in proc.stdout
    assert repo.report() == [{**ROWS[0], "crap_score": 9.0, "pass_fail": "accepted"}]


@pytest.mark.spec("CG-05-IT-01")
def test_cg_05_a_raised_score_fails_again(repo):
    """Scenario: A change that raises the score above the accepted score fails again."""
    _commit_register(repo, "dev")
    _change_tree(repo)
    repo.plant([_row("tree_severity", 10, 30, complexity=10), ROWS[1]])
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 10.00" in proc.stdout


@pytest.mark.spec("CG-05-IT-01")
def test_cg_05_a_row_only_on_the_story_branch_has_no_effect(repo):
    """Scenario: A row that exists only on the story branch does not change the verdict."""
    repo.write(REGISTER, REGISTER_TEXT)
    _change_tree(repo)
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert repo.report()[0]["pass_fail"] == "fail"
    assert NO_DEV_LINE not in proc.stdout


@pytest.mark.spec("CG-05-IT-01")
def test_cg_05_dev_and_the_story_branch_with_different_rows_use_the_row_on_dev(repo):
    _commit_register(repo, "dev", REGISTER_TEXT.replace("| 9 |", "| 8.5 |"))
    repo.write(REGISTER, REGISTER_TEXT)
    _change_tree(repo)
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr


@pytest.mark.spec("CG-05-IT-01")
def test_cg_05_a_project_without_the_register_has_no_exceptions(repo):
    """Scenario: A project without the exceptions register has no exceptions."""
    _change_tree(repo)
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert {row["pass_fail"] for row in repo.report()} == {"fail"}


@pytest.mark.spec("CG-05-IT-01")
def test_cg_05_a_repository_without_dev_has_no_exceptions(repo):
    """Scenario: A repository without a branch dev has no exceptions (DEC-13, DEC-25)."""
    _commit_register(repo, "dev")
    repo.git("merge", "-q", "--no-edit", "dev")
    repo.git("branch", "-q", "-D", "dev")
    _change_tree(repo)
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert NO_DEV_LINE in proc.stdout
    assert repo.report()[0]["pass_fail"] == "fail"


@pytest.mark.spec("CG-05-IT-01")
def test_cg_05_a_linked_worktree_reads_the_register_from_dev(repo):
    _commit_register(repo, "dev")
    repo.git("checkout", "-q", TARGET)
    worktree = repo.tmp / "worktree"
    repo.git("worktree", "add", "-q", str(worktree), BRANCH)
    repo.write(FINDING_LINT, _finding_lint({15: "    x15 = 'changed'"}), worktree)
    repo.commit("change", cwd=worktree)
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID, cwd=worktree)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert repo.report(root=worktree)[0]["pass_fail"] == "accepted"


@pytest.mark.spec("CG-05-IT-01")
def test_cg_05_a_broken_row_on_dev_exits_2_and_writes_no_report(repo):
    """Scenario Outline: A broken exceptions-register row cannot measure, the score "nine"."""
    _commit_register(repo, "dev", REGISTER_TEXT.replace("| 9 |", "| nine |"))
    _change_tree(repo)
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "line 7" in proc.stderr
    assert "nine" in proc.stderr
    assert not (repo.root / ".current-work" / "crap-score" / f"{STORY_ID}.json").exists()


@pytest.mark.spec("CG-05-IT-01")
def test_cg_05_a_tag_named_dev_does_not_stand_in_for_the_branch_dev(repo):
    """A row on the story branch has no effect, even when a tag dev points at it (IMPL-0079)."""
    repo.write(REGISTER, REGISTER_TEXT)
    _change_tree(repo)
    repo.git("tag", "dev", "HEAD")
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert repo.report()[0]["pass_fail"] == "fail"


@pytest.mark.spec("CG-05-IT-01")
def test_cg_05_a_register_on_dev_that_is_not_utf_8_exits_2_and_names_the_file(repo):
    """A register on dev with the byte 0xE4 cannot be read, so the gate cannot measure (IMPL-0080)."""
    current = repo.git("symbolic-ref", "--short", "HEAD")
    repo.git("checkout", "-q", "dev")
    path = repo.root / REGISTER
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(REGISTER_TEXT.replace(REASON, "Gr\xfcnde").encode("utf-8").replace(b"\xc3\xbc", b"\xe4"))
    repo.commit("register on dev in Latin-1")
    repo.git("checkout", "-q", current)
    _change_tree(repo)
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert REGISTER in proc.stderr
    assert "Traceback" not in proc.stderr
    assert not (repo.root / ".current-work" / "crap-score" / f"{STORY_ID}.json").exists()


# --- CG-05-IT-02: the register only from refs/heads/dev (ST-0445) -----------


@pytest.mark.spec("CG-05-IT-02")
def test_cg_05_only_a_remote_branch_dev_gives_no_register(repo):
    """Scenario Outline: crap-score reads the exceptions register only from refs/heads/dev, row origin/dev (DEC-55)."""
    _commit_register(repo, "dev")
    dev = repo.git("rev-parse", "dev")
    repo.git("update-ref", "refs/remotes/origin/dev", dev)
    repo.git("merge", "-q", "--no-edit", "dev")
    repo.git("branch", "-q", "-D", "dev")
    _change_tree(repo)
    proc = repo.run("--base", TARGET, "--story-id", STORY_ID)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert NO_DEV_LINE in proc.stdout
    assert repo.report()[0]["pass_fail"] == "fail"


@pytest.mark.spec("CG-05-IT-02")
def test_cg_05_outside_a_git_repository_gives_no_register(tmp_path):
    """Scenario Outline: crap-score reads the exceptions register only from refs/heads/dev, row outside git (DEC-55)."""
    folder = tmp_path / "plain"
    folder.mkdir()
    (folder / "docs").mkdir()
    (folder / "docs" / "testing.yaml").write_text(TESTING_YAML)
    stub = folder / STUB
    stub.parent.mkdir(parents=True)
    stub.write_text(COPY_STUB)
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    register = folder / REGISTER
    register.parent.mkdir(parents=True)
    register.write_text(REGISTER_TEXT)
    planted = tmp_path / "planted.json"
    planted.write_text(json.dumps(ROWS))
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "COVERAGE_")) and k != "STORY_ID"}
    env.update(PLANTED_ROWS=str(planted), GIT_CEILING_DIRECTORIES=str(tmp_path))
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--all", "--story-id", STORY_ID], cwd=folder, env=env,
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert NO_DEV_LINE in proc.stdout
    report = json.loads((folder / ".current-work" / "crap-score" / f"{STORY_ID}.json").read_text())
    assert report[0]["pass_fail"] == "fail"
