"""Tests of the trusted gate source of crap-score (ST-0450).

docs/spec/features/crap-gate-setup.feature, Rule "User judges every story by
the gate settings of the integration branch" (CG-14), and the Scenario "One
commit and one state of the exceptions register get the same verdict".
BR-128, BR-129, BR-131, BR-132, DEC-67 to DEC-76, ADR-0041.

The contract tests CG-14-CT-01 to CG-14-CT-03 call the reader with values
that the test builds. Every integration test builds its own repository in
`tmp_path` and commits the trusted settings on `dev` or `main` before it
judges the story head. No integration test stubs git or the reader.
"""

from __future__ import annotations

import json
import re
import stat
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script, write_review_report
from test_crap_gate_score import BRANCH, FINDING_LINT, ROWS, STORY_ID, STUB, TARGET, Repo, _finding_lint, _row
from test_run_lifecycle_dispatch import _by_hand_run, _dispatch, _entry, _git

cs = load_script("crap-score")

TEMPLATE = REPO_ROOT / "packages" / "factory" / "skills" / "setup-crap-score" / "crap-measure-python"
REGISTER = "docs/findings/exceptions.md"
FACTORY_SETTINGS = "docs/factory-settings.yaml"
BACKEND_STUB = "scripts/crap-measure-backend"
GATE_CALL = ("--base", TARGET, "--story-id", STORY_ID, "--report-dir", ".current-work/crap-score/")
FROM_FOLDER = "took the threshold and the files and exclude patterns of every measure from docs/testing.yaml of the folder"
NOT_TRUSTED = "not yet trusted"


# --- fixtures --------------------------------------------------------------


def gate_yaml(threshold: float = 8, measures: str | None = None, command: str = STUB) -> str:
    """docs/testing.yaml with gates.crap-score; *measures* replaces the measure python."""
    if measures is None:
        measures = python_measure(command=command)
    return (
        'test_command: "true"\ngates:\n  crap-score:\n    enabled: true\n'
        f"    threshold: {threshold}\n    timeout_minutes: 10\n    measures:\n{measures}"
    )


def python_measure(files: str = "packages/factory/scripts/*", exclude: tuple[str, ...] = (), command: str = STUB) -> str:
    text = f'      - name: python\n        files: "{files}"\n        command: "{command}"\n'
    if exclude:
        text += "        exclude:\n" + "".join(f'          - "{p}"\n' for p in exclude)
    return text


def backend_measure(files: str = "backend/**", exclude: tuple[str, ...] = (), command: str = BACKEND_STUB) -> str:
    text = f'      - name: backend\n        files: "{files}"\n        command: "{command}"\n'
    if exclude:
        text += "        exclude:\n" + "".join(f'          - "{p}"\n' for p in exclude)
    return text


def register(*rows: tuple[str, str, str]) -> str:
    lines = "".join(f"| `{file}` | `{function}` | {score} | Old code | A. Example |\n" for file, function, score in rows)
    return (
        "# Exceptions\n\n## CRAP score\n\n| File | Function | Accepted score | Reason | Accepted by |\n"
        "| ---- | -------- | -------------- | ------ | ----------- |\n" + lines
    )


def commit_on(repo: Repo, branch: str, files: dict[str, str | None], message: str = "trusted settings") -> None:
    """Commit *files* on *branch* without a checkout; None removes a file.

    The branch must not be checked out, so the fixture moves no working tree.
    """
    index = repo.tmp / "fixture-index"
    env = {**repo.env, "GIT_INDEX_FILE": str(index)}

    def git(*args: str, data: str | None = None) -> str:
        return subprocess.run(
            ["git", *args], cwd=repo.root, env=env, input=data, check=True, capture_output=True, text=True,
        ).stdout.strip()

    git("read-tree", f"refs/heads/{branch}")
    for path, text in files.items():
        if text is None:
            git("update-index", "--force-remove", path)
        else:
            blob = git("hash-object", "-w", "--stdin", data=text)
            git("update-index", "--add", "--cacheinfo", f"100644,{blob},{path}")
    tree = git("write-tree")
    commit = git("commit-tree", tree, "-p", f"refs/heads/{branch}", "-m", message)
    git("update-ref", f"refs/heads/{branch}", commit)
    index.unlink()


def at_head(repo: Repo, files: dict[str, str], cwd: Path | None = None, message: str = "story change") -> None:
    """Commit *files* at the head of the checked-out story branch."""
    for path, text in files.items():
        repo.write(path, text, cwd)
    repo.commit(message, cwd=cwd)


def executable(repo: Repo, path: str, text: str, root: Path | None = None) -> None:
    repo.write(path, text, root)
    target = (root or repo.root) / path
    target.chmod(target.stat().st_mode | stat.S_IXUSR)


def recording_stub(repo: Repo, path: str = STUB, rows: bool = True) -> Path:
    """A stub that logs its name, GATE_FILES and GATE_EXCLUDE as one JSON line, then copies the rows."""
    log = repo.tmp / "gate-env.log"
    repo.env["GATE_ENV_LOG"] = str(log)
    copy = 'cp "$PLANTED_ROWS" "$GATE_OUTPUT"\n' if rows else 'echo "[]" > "$GATE_OUTPUT"\n'
    executable(repo, path, (
        "#!/bin/sh\n"
        f'python3 -c \'import json, os, sys; print(json.dumps({{"stub": sys.argv[1], '
        '"files": os.environ["GATE_FILES"], "exclude": os.environ["GATE_EXCLUDE"]}))\' '
        f'"{path}" >> "$GATE_ENV_LOG"\n' + copy
    ))
    return log


def logged(log: Path) -> list[dict]:
    return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


def change_tree(repo: Repo, cwd: Path | None = None, **extra: str) -> None:
    """Change one line inside tree_severity, which then scores 9 with the planted rows."""
    at_head(repo, {FINDING_LINT: _finding_lint({15: "    x15 = 'changed'"}), **extra}, cwd)


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    return Repo(tmp_path)


def report_path(repo: Repo, root: Path | None = None) -> Path:
    return (root or repo.root) / ".current-work" / "crap-score" / f"{STORY_ID}.json"


# --- CG-14-CT-01: the join of branch and folder ----------------------------


def _measure(name: str, files: str, exclude: tuple[str, ...] = (), command: str = "", ready: str | None = None):
    return cs.Measure(name, files, command or f"scripts/measure-{name}", exclude, ready)


FOLDER = cs.Settings(
    Decimal(10), 10,
    (
        _measure("python", "packages/factory/scripts/dispatch*", ("packages/factory/scripts/finding-lint",)),
        _measure("backend", "backend/**", ready="scripts/ready-backend"),
        _measure("frontend", "packages/server/frontend/**", ("**/*.spec.ts",)),
    ),
)
BRANCH_ENTRY = {
    "threshold": 8,
    "timeout_minutes": 30,
    "measures": [
        {"name": "python", "files": "packages/factory/scripts/*", "command": "scripts/other-command"},
        {"name": "backend", "files": "backend/**", "exclude": ["**/db/alembic/versions/**"], "command": "x", "ready": "y"},
    ],
}
WHERE = "docs/testing.yaml on the branch dev"


@pytest.mark.spec("CG-14-CT-01")
def test_cg_14_the_branch_values_win_and_a_new_measure_keeps_its_own():
    """Scenarios: threshold raised, exclude added, files narrowed, new measure at the story head."""
    values = cs.join_values(FOLDER, BRANCH_ENTRY, WHERE)
    settings = cs.apply_trusted(FOLDER, values)
    assert settings.threshold == Decimal(8)
    assert settings.timeout_minutes == 10
    python, backend, frontend = settings.measures
    assert (python.files, python.exclude) == ("packages/factory/scripts/*", ())
    assert (backend.files, backend.exclude) == ("backend/**", ("**/db/alembic/versions/**",))
    assert (frontend.files, frontend.exclude) == ("packages/server/frontend/**", ("**/*.spec.ts",))
    assert [m.command for m in settings.measures] == [m.command for m in FOLDER.measures]
    assert backend.ready == "scripts/ready-backend"
    assert len(values.notices) == 1
    assert "measure frontend" in values.notices[0]
    assert NOT_TRUSTED in values.notices[0]


@pytest.mark.spec("CG-14-CT-01")
def test_cg_14_a_lower_threshold_at_the_head_still_gives_the_branch_threshold():
    """A reader that took the lower value would let a story loosen the gate in two steps."""
    folder = cs.Settings(Decimal(5), 10, FOLDER.measures)
    assert cs.join_values(folder, BRANCH_ENTRY, WHERE).threshold == Decimal(8)


@pytest.mark.spec("CG-14-CT-01")
@pytest.mark.parametrize(
    ("measures", "named"),
    [
        ((FOLDER.measures[0], FOLDER.measures[2]), "backend"),
        ((_measure("py", "packages/factory/scripts/*"), *FOLDER.measures[1:]), "python"),
    ],
    ids=["dropped", "renamed"],
)
def test_cg_14_a_measure_the_head_drops_or_renames_names_the_measure(measures, named):
    """Scenario: A measure that the story head drops cannot measure (DEC-70).

    A renamed measure is new at the head, and the old name is a dropped measure.
    """
    folder = cs.Settings(Decimal(10), 10, measures)
    with pytest.raises(cs.GateError, match=rf"measure {named} is in {WHERE}"):
        cs.join_values(folder, BRANCH_ENTRY, WHERE)


class FakeGit:
    """The git calls of the reader, answered from values that the test builds."""

    def __init__(self, files: dict[str, str]) -> None:
        self.files = files
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, root, *args, errors="strict"):
        self.calls.append(args)
        if args[0] == "ls-tree":
            return args[-1] + "\n" if args[-1] in self.files else ""
        if args[0] == "show":
            return self.files[args[1].split(":", 1)[1]]
        raise AssertionError(f"unexpected git call {args}")


def _source(monkeypatch, tip: str | None, files: dict[str, str], option: bool = False):
    monkeypatch.setattr(cs, "_resolve", lambda root, revision: "head")
    monkeypatch.setattr(cs, "_branch_tip", lambda root, branch: tip)
    fake = FakeGit(files)
    monkeypatch.setattr(cs, "git", fake)
    return cs.GitRefSource(Path("/nowhere"), "dev", named=False, settings_from_folder=option), fake


@pytest.mark.spec("CG-14-CT-01")
@pytest.mark.parametrize(
    ("tip", "files", "cause"),
    [
        (None, {}, "no branch dev exists"),
        ("tip", {}, "the branch dev holds no docs/testing.yaml"),
        ("tip", {"docs/testing.yaml": 'test_command: "true"\n'}, "docs/testing.yaml on the branch dev has no entry gates.crap-score"),
    ],
    ids=["no ref", "no docs/testing.yaml", "no entry gates.crap-score"],
)
def test_cg_14_a_missing_branch_entry_gives_the_folder_values_and_names_the_cause(monkeypatch, tip, files, cause):
    """Scenario Outline: Without gate settings on the integration branch the settings come from the folder."""
    source, _ = _source(monkeypatch, tip, files)
    values = source.gate_values(FOLDER)
    assert values.threshold == Decimal(10)
    assert values.patterns == {m.name: cs.Patterns(m.files, m.exclude) for m in FOLDER.measures}
    assert values.notices == (f"crap-score: {FROM_FOLDER}, because {cause}",)


@pytest.mark.spec("CG-14-CT-01")
def test_cg_14_settings_from_folder_reads_no_branch_settings_and_skips_the_dropped_measure_check(monkeypatch):
    """DEC-71, DEC-73: the option takes every value from the folder and reads no docs/testing.yaml of the branch."""
    branch_yaml = "gates:\n  crap-score:\n    threshold: 8\n    measures:\n      - {name: gone, files: x}\n"
    source, fake = _source(monkeypatch, "tip", {"docs/testing.yaml": branch_yaml}, option=True)
    values = source.gate_values(FOLDER)
    assert values.threshold == Decimal(10)
    assert values.notices == (f"crap-score: {FROM_FOLDER}, because the call passes --settings-from-folder",)
    assert fake.calls == []
    without, _ = _source(monkeypatch, "tip", {"docs/testing.yaml": branch_yaml})
    with pytest.raises(cs.GateError, match="measure gone"):
        without.gate_values(FOLDER)


# --- CG-14-CT-02: the seam for a second backend ----------------------------


class TestBackend(cs.TrustedGateSource):
    """A second backend behind the interface, as a knowledge-graph store would be (DEC-72)."""

    __test__ = False

    def gate_values(self, folder):
        patterns = {m.name: cs.Patterns(m.files, ("**/bug_bar*",)) for m in folder.measures}
        return cs.TrustedValues(Decimal(5), patterns, ("crap-score: test backend",))

    def exceptions(self):
        row = cs.ExceptionRow(FINDING_LINT, "tree_severity", Decimal(9), "Accepted in the test backend", "T", 1)
        return {(FINDING_LINT, "tree_severity"): row}, ()


def no_git(*args, **kwargs):
    raise AssertionError(f"crap-score ran git {args[1:]}")


class NoSubprocess:
    def __getattr__(self, name):
        raise AssertionError(f"crap-score used subprocess.{name}")


@pytest.mark.spec("CG-14-CT-02")
def test_cg_14_the_gate_judges_with_exactly_the_values_of_the_backend(tmp_path, monkeypatch, capsys):
    """DEC-72, ADR-0041: the gate logic reaches no trusted value past the interface, and no git command runs."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "testing.yaml").write_text(gate_yaml(8))
    bug_bar = "packages/factory/scripts/bug_bar_level"
    rows = [_row("tree_severity", 10, 30), {**_row("bug_bar_level", 1, 20), "file": bug_bar}]
    measured = []

    def run_measure(measure, root, clock):
        measured.append(measure)
        return rows

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cs, "run_measure", run_measure)
    monkeypatch.setattr(cs, "git", no_git)
    monkeypatch.setattr(cs, "subprocess", NoSubprocess())
    report_dir = tmp_path / "reports"
    code = cs.main(["--all", "--story-id", STORY_ID, "--report-dir", str(report_dir)], source=TestBackend())
    out = capsys.readouterr()
    assert code == 0, out.out + out.err
    assert [(m.files, m.exclude) for m in measured] == [("packages/factory/scripts/*", ("**/bug_bar*",))]
    assert f"ACCEPTED {FINDING_LINT} tree_severity 9.00: Accepted in the test backend" in out.out
    assert "above the threshold 5" in out.err
    report = json.loads((report_dir / f"{STORY_ID}.json").read_text())
    assert [(row["function"], row["pass_fail"]) for row in report] == [("tree_severity", "accepted")]


# --- CG-14-CT-03: the key integration_branch -------------------------------


@pytest.mark.spec("CG-14-CT-03")
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("integration_branch: main\n", ("main", True)),
        ('release_tag_patterns: ["v[0-9]*"]\n', ("dev", False)),
        (None, ("dev", False)),
    ],
    ids=["main", "no key", "no file"],
)
def test_cg_14_integration_branch_names_the_branch_and_defaults_to_dev(tmp_path, text, expected):
    """Scenario Outline: The key integration_branch names the branch that the gate reads (DEC-68)."""
    if text is not None:
        (tmp_path / "docs").mkdir()
        (tmp_path / FACTORY_SETTINGS).write_text(text)
    assert cs.integration_branch(tmp_path) == expected


@pytest.mark.spec("CG-14-CT-03")
@pytest.mark.parametrize("value", ['""', "5"])
def test_cg_14_an_integration_branch_that_is_no_text_names_the_file_and_the_key(tmp_path, value):
    """Scenario Outline: Broken gate settings on the integration branch cannot measure, rows 3 and 4 (DEC-74)."""
    (tmp_path / "docs").mkdir()
    (tmp_path / FACTORY_SETTINGS).write_text(f"integration_branch: {value}\n")
    with pytest.raises(cs.GateError, match=r"the key integration_branch in docs/factory-settings\.yaml"):
        cs.integration_branch(tmp_path)


@pytest.mark.spec("CG-14-CT-03")
@pytest.mark.parametrize("value", ["story/ST-1~1", "story/ST-1^", "@{-1}"], ids=["tilde", "caret", "previous branch"])
def test_cg_14_an_integration_branch_that_is_no_branch_name_names_the_key_and_the_value(tmp_path, value):
    """IMPL-0094, DEC-77: a revision expression would let a story name a commit of its own."""
    (tmp_path / "docs").mkdir()
    (tmp_path / FACTORY_SETTINGS).write_text(f'integration_branch: "{value}"\n')
    with pytest.raises(cs.GateError, match=r"the key integration_branch in docs/factory-settings\.yaml") as raised:
        cs.integration_branch(tmp_path)
    assert value in str(raised.value)


# --- CG-14-IT-01: a threshold raised at the head ---------------------------


@pytest.mark.spec("CG-14-IT-01")
@pytest.mark.parametrize("folder", ["linked worktree", "primary checkout"])
def test_cg_14_a_threshold_raised_at_the_head_fails_tree_severity_at_the_gate_check(repo, folder):
    """Scenario: A threshold raised at the story head does not change the verdict; the gate-check call."""
    root = None
    if folder == "linked worktree":
        repo.git("checkout", "-q", TARGET)
        root = repo.tmp / "worktree"
        repo.git("worktree", "add", "-q", str(root), BRANCH)
    change_tree(repo, root, **{"docs/testing.yaml": gate_yaml(10)})
    proc = repo.run(*GATE_CALL, cwd=root)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert "above the threshold 8" in proc.stderr
    assert json.loads(report_path(repo, root).read_text()) == [{**ROWS[0], "crap_score": 9.0, "pass_fail": "fail"}]


# --- CG-14-IT-02: an exclude pattern added at the head ---------------------

PLANTED_FINDING_LINT = '''\
#!/usr/bin/env python3
"""Planted finding-lint."""


def tree_severity(value):
    if value > 10:
        return "high"
    if value > 5:
        return "mid"
    return "low"
'''

LOADS_FINDING_LINT = '''\
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "packages" / "factory" / "scripts" / "finding-lint"
_loader = SourceFileLoader("finding_lint", str(PATH))
module = importlib.util.module_from_spec(importlib.util.spec_from_loader("finding_lint", _loader))
_loader.exec_module(module)


def test_loads():
    assert module.tree_severity
'''


def _template(test_command: list[str]) -> str:
    text, count = re.subn(
        r"^TEST_COMMAND: list\[str\] = \[\]$", f"TEST_COMMAND: list[str] = {test_command!r}",
        TEMPLATE.read_text(), flags=re.MULTILINE,
    )
    assert count == 1
    return text


@pytest.mark.spec("CG-14-IT-02")
def test_cg_14_an_exclude_pattern_added_at_the_head_drops_no_row_with_the_real_template(tmp_path):
    """Scenario: An exclude pattern added at the story head does not change the verdict (real template).

    The template measures only what GATE_FILES and GATE_EXCLUDE keep, so a head
    exclude pattern passed to it would drop the row before crap-score sees it.
    """
    repo = Repo(tmp_path)
    command = "scripts/crap-measure-python"
    test_command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"]
    files = {
        "docs/testing.yaml": gate_yaml(8, command=command),
        command: _template(test_command),
        FINDING_LINT: PLANTED_FINDING_LINT,
        "tests/test_finding_lint.py": LOADS_FINDING_LINT,
    }
    commit_on(repo, "dev", files)
    repo.git("branch", "-q", "-f", TARGET, "dev")
    repo.git("reset", "-q", "--hard", "dev")
    (repo.root / command).chmod(0o755)
    at_head(repo, {
        "docs/testing.yaml": gate_yaml(8, python_measure(exclude=(FINDING_LINT,), command=command)),
        FINDING_LINT: PLANTED_FINDING_LINT.replace('return "low"', 'return "lowest"'),
    })
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 12.00" in proc.stdout


@pytest.mark.spec("CG-14-IT-02")
def test_cg_14_an_exclude_pattern_added_at_the_head_is_not_passed_to_the_command(repo):
    """Scenario: An exclude pattern added at the story head does not change the verdict (recording stub)."""
    log = recording_stub(repo)
    repo.commit("recording stub")
    commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(8)})
    change_tree(repo, **{"docs/testing.yaml": gate_yaml(8, python_measure(exclude=(FINDING_LINT,)))})
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert logged(log) == [{"stub": STUB, "files": "packages/factory/scripts/*", "exclude": ""}]


# --- CG-14-IT-03: a measure new at the head --------------------------------

FRONTEND_STUB = "scripts/crap-measure-frontend"
CART = "packages/server/frontend/src/cart.ts"
CART_SPEC = "packages/server/frontend/src/cart.spec.ts"


@pytest.mark.spec("CG-14-IT-03")
def test_cg_14_a_measure_new_at_the_head_runs_with_its_head_patterns_and_is_not_trusted(repo):
    """Scenario: A measure new at the story head takes its exclude patterns from the head and is named as not trusted."""
    trusted = backend_measure() + python_measure()
    commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(8, trusted)})
    frontend_rows = repo.tmp / "frontend.json"
    frontend_rows.write_text(json.dumps([
        {"file": path, "function": "total", "start_line": 1, "end_line": 3, "complexity": 2, "coverage_pct": 100}
        for path in (CART, CART_SPEC)
    ]))
    frontend = (
        '      - name: frontend\n        files: "packages/server/frontend/**"\n'
        f'        command: "{FRONTEND_STUB}"\n        exclude:\n          - "**/*.spec.ts"\n'
    )
    executable(repo, BACKEND_STUB, '#!/bin/sh\necho "[]" > "$GATE_OUTPUT"\n')
    executable(repo, FRONTEND_STUB, f'#!/bin/sh\ncp "{frontend_rows}" "$GATE_OUTPUT"\n')
    at_head(repo, {
        "docs/testing.yaml": gate_yaml(8, trusted + frontend),
        CART: "export function total() {\n  return 1;\n}\n",
        CART_SPEC: "total();\n\n\n",
    })
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert [row["file"] for row in repo.report()] == [CART]
    notices = [line for line in proc.stdout.splitlines() if NOT_TRUSTED in line]
    assert len(notices) == 1 and "measure frontend" in notices[0]


# --- CG-14-IT-04: a files pattern narrowed at the head ---------------------


@pytest.mark.spec("CG-14-IT-04")
def test_cg_14_a_files_pattern_narrowed_at_the_head_does_not_change_the_verdict(repo):
    """Scenario: A files pattern narrowed at the story head does not change the verdict."""
    log = recording_stub(repo)
    repo.commit("recording stub")
    commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(8)})
    change_tree(repo, **{"docs/testing.yaml": gate_yaml(8, python_measure("packages/factory/scripts/dispatch*"))})
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert [entry["files"] for entry in logged(log)] == ["packages/factory/scripts/*"]


# --- CG-14-IT-05: a measure dropped at the head ----------------------------


@pytest.mark.spec("CG-14-IT-05")
def test_cg_14_a_measure_dropped_at_the_head_cannot_measure(repo):
    """Scenario: A measure that the story head drops cannot measure (DEC-70, BR-133)."""
    commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(8, backend_measure() + python_measure())})
    log = recording_stub(repo, BACKEND_STUB, rows=False)
    change_tree(repo, **{"docs/testing.yaml": gate_yaml(8, backend_measure())})
    earlier = report_path(repo)
    earlier.parent.mkdir(parents=True)
    earlier.write_bytes(b'[{"function": "earlier"}]\n')
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "measure python is in docs/testing.yaml on the branch dev" in proc.stderr
    assert logged(log) == []
    assert earlier.read_bytes() == b'[{"function": "earlier"}]\n'


# --- CG-14-IT-06: the four fallback cases ----------------------------------

ALEMBIC = "packages/server/backend/src/db/alembic/versions/0042_orders.py"
APP = "packages/server/backend/src/app.py"


def _without_dev(repo: Repo) -> None:
    repo.git("branch", "-q", "-D", "dev")


def _only_origin_dev(repo: Repo) -> None:
    repo.git("update-ref", "refs/remotes/origin/dev", repo.git("rev-parse", "dev"))
    repo.git("branch", "-q", "-D", "dev")


def _plant_and_commit_folder_settings(repo: Repo) -> None:
    """Plant an alembic function of complexity 9 and an app function of complexity 2, then commit the story head.

    The folder settings exclude the alembic file, so only the app function is judged (CG-14-IT-06).
    """
    folder = gate_yaml(8, backend_measure("packages/server/backend/**", ("**/db/alembic/versions/**",), STUB))
    repo.plant([
        {"file": ALEMBIC, "function": "upgrade", "start_line": 1, "end_line": 3, "complexity": 9, "coverage_pct": 0},
        {"file": APP, "function": "run", "start_line": 1, "end_line": 3, "complexity": 2, "coverage_pct": 100},
    ])
    at_head(repo, {"docs/testing.yaml": folder, ALEMBIC: "a\nb\nc\n", APP: "a\nb\nc\n"})


@pytest.mark.spec("CG-14-IT-06")
@pytest.mark.parametrize(
    ("case", "cause"),
    [
        (lambda repo: commit_on(repo, "dev", {"docs/testing.yaml": None}), "the branch dev holds no docs/testing.yaml"),
        (lambda repo: commit_on(repo, "dev", {"docs/testing.yaml": 'test_command: "true"\n'}),
         "docs/testing.yaml on the branch dev has no entry gates.crap-score"),
    ],
    ids=["no docs/testing.yaml on dev", "no entry on dev"],
)
def test_cg_14_without_settings_on_the_branch_the_folder_settings_judge(repo, case, cause):
    """Scenario Outline: Without gate settings on the integration branch the settings come from the folder (DEC-69)."""
    case(repo)
    _plant_and_commit_folder_settings(repo)
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert [row["file"] for row in repo.report()] == [APP]
    assert f"crap-score: {FROM_FOLDER}, because {cause}" in proc.stdout.splitlines()


@pytest.mark.spec("CG-14-IT-06")
def test_cg_14_all_without_dev_judges_with_the_folder_settings(repo):
    """Scenario Outline: Without gate settings on the integration branch the settings come from the folder (--all, DEC-81).

    The setup path --all keeps the fallback to the folder when the ref dev is missing.
    """
    _without_dev(repo)
    _plant_and_commit_folder_settings(repo)
    proc = repo.run("--all", "--story-id", STORY_ID, "--report-dir", ".current-work/crap-score/")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert [row["file"] for row in repo.report()] == [APP]
    assert f"crap-score: {FROM_FOLDER}, because no branch dev exists" in proc.stdout.splitlines()
    assert "crap-score: read no exceptions register, because no branch dev exists" in proc.stdout.splitlines()


@pytest.mark.spec("CG-14-IT-06")
def test_cg_14_settings_from_folder_without_dev_judges_with_the_folder_settings(repo):
    """Scenario Outline: Without gate settings on the integration branch the settings come from the folder (--settings-from-folder, DEC-81).

    gate-setup-proof passes this option, so the proof works without a local dev.
    """
    _without_dev(repo)
    _plant_and_commit_folder_settings(repo)
    proc = repo.run(*GATE_CALL, "--settings-from-folder")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert [row["file"] for row in repo.report()] == [APP]
    assert f"crap-score: {FROM_FOLDER}, because the call passes --settings-from-folder" in proc.stdout.splitlines()


# --- CG-14-IT-07: broken settings take no value from the folder ------------


def _settings_at_base(text: str):
    """Commit docs/factory-settings.yaml on the revision that --base names (DEC-77)."""
    return lambda repo: commit_on(repo, TARGET, {FACTORY_SETTINGS: text})


def _only_tag_main(repo: Repo) -> None:
    """Replace the branch main with the tag refs/tags/refs/heads/main (IMPL-0094)."""
    repo.git("branch", "-q", "-D", "main")
    repo.git("update-ref", "refs/tags/refs/heads/main", repo.git("rev-parse", "dev"))
    _settings_at_base("integration_branch: main\n")(repo)


def _tag_v1_10_0_and_no_branch(repo: Repo) -> None:
    """Tag the revision dev, at a threshold of 30, as v1.10.0 and name no local branch of that name (DEC-77)."""
    commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(30)})
    repo.git("update-ref", "refs/tags/v1.10.0", repo.git("rev-parse", "dev"))
    _settings_at_base("integration_branch: v1.10.0\n")(repo)


def _remote_ref_origin_main_and_no_branch(repo: Repo) -> None:
    """Replace the branch main with the remote ref refs/remotes/origin/main at a threshold of 30 (DEC-77)."""
    repo.git("branch", "-q", "-D", "main")
    commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(30)})
    repo.git("update-ref", "refs/remotes/origin/main", repo.git("rev-parse", "dev"))
    _settings_at_base("integration_branch: origin/main\n")(repo)


@pytest.mark.spec("CG-14-IT-07")
@pytest.mark.parametrize(
    ("case", "named"),
    [
        (lambda repo: commit_on(repo, "dev", {"docs/testing.yaml": "gates: [crap-score\n"}),
         ["docs/testing.yaml on the branch dev cannot be parsed"]),
        (lambda repo: commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(8).replace("    threshold: 8\n", "")}),
         ["docs/testing.yaml on the branch dev has no threshold"]),
        (_settings_at_base('integration_branch: ""\n'), ["the key integration_branch in docs/factory-settings.yaml"]),
        (_settings_at_base("integration_branch: 5\n"), ["the key integration_branch in docs/factory-settings.yaml"]),
        (lambda repo: (repo.git("branch", "-q", "-D", "main"), _settings_at_base("integration_branch: main\n")(repo)),
         ["key integration_branch", "names the branch main", "git holds no branch main"]),
        (_settings_at_base(f"integration_branch: {BRANCH}\n"),
         ["key integration_branch", f"names the branch {BRANCH}, whose tip is HEAD"]),
        (_settings_at_base(f'integration_branch: "{BRANCH}~1"\n'), ["key integration_branch", f"{BRANCH}~1"]),
        (_settings_at_base(f'integration_branch: "{BRANCH}^"\n'), ["key integration_branch", f"{BRANCH}^"]),
        (_only_tag_main, ["key integration_branch", "names the branch main", "git holds no branch main"]),
        (_tag_v1_10_0_and_no_branch,
         ["key integration_branch", "names the branch v1.10.0", "git holds no branch v1.10.0"]),
        (_remote_ref_origin_main_and_no_branch,
         ["key integration_branch", "names the branch origin/main", "git holds no branch origin/main"]),
        (_without_dev, ["git holds no branch dev", "the default integration branch"]),
        (_only_origin_dev, ["git holds no branch dev", "the default integration branch"]),
    ],
    ids=["unparseable", "no threshold", "empty branch name", "number", "no branch main", "own branch",
         "parent of the own branch", "caret of the own branch", "only a tag refs/heads/main",
         "tag v1.10.0 and no branch", "remote ref origin/main and no branch",
         "no branch dev deleted after the cut", "only origin/dev"],
)
def test_cg_14_broken_settings_on_the_branch_cannot_measure(repo, case, named):
    """Scenario Outline: Broken gate settings on the integration branch cannot measure (DEC-74, DEC-76)."""
    log = recording_stub(repo)
    change_tree(repo, **{"docs/testing.yaml": gate_yaml(30)})
    case(repo)
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    for part in named:
        assert part in proc.stderr
    assert logged(log) == []
    assert not report_path(repo).exists()


# --- CG-14-IT-08: integration_branch names the branch ----------------------

OTHER_SCRIPT = "packages/factory/scripts/other-script"


@pytest.mark.spec("CG-14-IT-08")
@pytest.mark.parametrize("setting", ["integration_branch: main\n", 'release_tag_patterns: ["v[0-9]*"]\n', None],
                         ids=["main", "no key", "no file"])
def test_cg_14_integration_branch_names_the_branch_of_every_trusted_value(repo, setting):
    """Scenario Outline: The key integration_branch names the branch that the gate reads (DEC-68)."""
    commit_on(repo, "main", {
        "docs/testing.yaml": gate_yaml(8),
        REGISTER: register((FINDING_LINT, "tree_severity", "9")),
    })
    commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(10, python_measure(exclude=(OTHER_SCRIPT,)))})
    repo.plant([*ROWS, {"file": OTHER_SCRIPT, "function": "other", "start_line": 1, "end_line": 3,
                        "complexity": 3, "coverage_pct": 0}])
    if setting is not None:
        commit_on(repo, TARGET, {FACTORY_SETTINGS: setting})
    change_tree(repo, **{OTHER_SCRIPT: "a\nb\nc\n"})
    proc = repo.run(*GATE_CALL)
    verdicts = {row["function"]: row["pass_fail"] for row in repo.report()}
    if setting == "integration_branch: main\n":
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert verdicts == {"tree_severity": "accepted", "other": "fail"}
    else:
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert verdicts == {"tree_severity": "pass"}


@pytest.mark.spec("CG-14-IT-08")
def test_cg_14_all_on_the_checked_out_integration_branch_judges_with_its_values(repo):
    """Scenario Outline: The key integration_branch names the branch that the gate reads, row
    "in the folder of crap-score | has integration_branch: main | --all | main" (DEC-68, DEC-77, DEC-79).

    The checkout is main, so the tip of main is HEAD, and setup step 6 runs there. main holds
    a threshold of 8, and the uncommitted folder holds 30, as setup step 4 writes it. Both
    functions score 9, so the gate judges with 8 and both fail. A gate that read the folder
    would pass them.
    """
    repo.git("checkout", "-q", "main")
    repo.write(FACTORY_SETTINGS, "integration_branch: main\n")
    repo.write("docs/testing.yaml", gate_yaml(8))
    repo.commit("trusted settings on main")
    repo.write("docs/testing.yaml", gate_yaml(30))
    proc = repo.run("--all", "--story-id", STORY_ID, "--report-dir", ".current-work/crap-score/")
    assert "whose tip is HEAD" not in proc.stderr, proc.stderr
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert {row["function"]: row["pass_fail"] for row in repo.report()} == {
        "tree_severity": "fail", "bug_bar_level": "fail",
    }


@pytest.mark.spec("CG-14-IT-08")
@pytest.mark.parametrize("value", ["main", f"{BRANCH}~1"], ids=["main", "parent of the own branch"])
def test_cg_14_a_key_changed_at_the_head_does_not_change_the_branch(repo, value):
    """DEC-77, IMPL-0094: with --base, the key comes from the revision that --base names, here dev.

    main holds a threshold of 30, and the parent of the story head holds the
    default threshold. Either value at the head would pass tree_severity.
    """
    commit_on(repo, "main", {"docs/testing.yaml": gate_yaml(30)})
    commit_on(repo, TARGET, {FACTORY_SETTINGS: "integration_branch: dev\n"})
    at_head(repo, {"docs/testing.yaml": gate_yaml(30)}, message="raise the threshold")
    change_tree(repo, **{FACTORY_SETTINGS: f'integration_branch: "{value}"\n'})
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert "above the threshold 8" in proc.stderr


@pytest.mark.spec("CG-14-IT-08")
def test_cg_14_a_tag_named_like_the_base_does_not_change_the_settings(repo):
    """DEC-78: --base takes the branch feature/login, not a tag of the same name at a story commit.

    The tag points at a story commit whose key names the branch loose, and
    loose holds a threshold of 30. The branch feature/login names no key, so
    the gate takes the threshold 8 of dev.
    """
    at_head(repo, {FACTORY_SETTINGS: 'integration_branch: "loose"\n', "docs/testing.yaml": gate_yaml(30)},
            message="name the branch loose")
    repo.git("branch", "loose")
    repo.git("update-ref", f"refs/tags/{TARGET}", "HEAD")
    change_tree(repo)
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert "above the threshold 8" in proc.stderr


@pytest.mark.spec("CG-14-IT-08")
def test_cg_14_a_tag_named_like_the_base_at_the_head_does_not_hide_the_changed_lines(repo):
    """DEC-78: a tag feature/login at the story head leaves the diff from the branch feature/login."""
    change_tree(repo)
    repo.git("update-ref", f"refs/tags/{TARGET}", "HEAD")
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert [row["function"] for row in repo.report()] == ["tree_severity"]


# --- CG-14-IT-09: dispatch merge-story with the real premerge-check ---------

WAVE_STORY = f"""---
id: {STORY_ID}
title: {STORY_ID}
tier: economy
status: pending
deps: []
touches: ["docs/testing.yaml", "{FINDING_LINT}"]
outputs: ["docs/testing.yaml", "{FINDING_LINT}"]
quality-gates: []
---
# {STORY_ID}
"""
REAL_CRAP_SCORE = '#!/bin/sh\nexec "{python}" "{script}" "$@"\n'


@pytest.mark.spec("CG-14-IT-09")
def test_cg_14_merge_story_refuses_a_story_that_raised_its_threshold(tmp_path):
    """Scenario Outline: The gate-check step and the merge never take the settings from the folder,
    row "dispatch merge-story ST-0350 with premerge-check".

    A wave repository with the real dispatch, premerge-check and crap-score.
    dispatch takes the scope of the story from `outputs`, so `outputs` names
    docs/testing.yaml too, and the refusal comes from crap-score alone.
    """
    planted = tmp_path / "planted.json"
    planted.write_text(json.dumps(ROWS))
    stub = tmp_path / "crap-measure-stub"
    stub.write_text(f'#!/bin/sh\ncp "{planted}" "$GATE_OUTPUT"\n')
    stub.chmod(0o755)
    repo = tmp_path / "repo"
    (repo / "backlog").mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    (repo / "backlog" / f"{STORY_ID}.md").write_text(WAVE_STORY)
    (repo / "docs").mkdir()
    (repo / "docs" / "testing.yaml").write_text(gate_yaml(8, command=str(stub)))
    (repo / ".gitignore").write_text(".current-work/\n/.agent-factory/\n")
    (repo / FINDING_LINT).parent.mkdir(parents=True)
    (repo / FINDING_LINT).write_text(_finding_lint())
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    ledger = _by_hand_run(repo, STORY_ID)
    for step in ("prepare-story", "mark-dispatching"):
        result = _dispatch(repo, ledger, step, STORY_ID)
        assert result.returncode == 0, (step, result.stdout, result.stderr)
    (repo / "docs" / "testing.yaml").write_text(gate_yaml(10, command=str(stub)))
    (repo / FINDING_LINT).write_text(_finding_lint({15: "    x15 = 'changed'"}))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", f"feat: raise the threshold ({STORY_ID})")
    write_review_report(repo, STORY_ID)
    _git(repo, "add", "docs/reviews")
    _git(repo, "commit", "-qm", f"docs: review {STORY_ID}")
    result = _dispatch(repo, ledger, "mark-dispatched", STORY_ID)
    assert result.returncode == 0, result.stdout + result.stderr
    installed = repo / ".agent-factory" / "factory" / "scripts" / "crap-score"
    installed.parent.mkdir(parents=True)
    installed.write_text(REAL_CRAP_SCORE.format(python=sys.executable, script=SOURCE_SCRIPTS_DIR / "crap-score"))
    installed.chmod(0o755)
    tip = _git(repo, "rev-parse", TARGET)

    refused = _dispatch(repo, ledger, "merge-story", STORY_ID)

    assert refused.returncode == 1, refused.stdout + refused.stderr
    # premerge-check names the failing function with the score of the report row.
    assert "BLOCK semantic-gates: crap-score (failed: tree_severity 9.0)" in refused.stdout, refused.stdout
    assert "out-of-scope-paths: all" in refused.stdout, refused.stdout
    assert _entry({"repo": repo, "ledger": ledger}).status.value == "dispatched"
    assert _git(repo, "rev-parse", TARGET) == tip


# --- CG-14-IT-10: --settings-from-folder -----------------------------------


@pytest.mark.spec("CG-14-IT-10")
def test_cg_14_settings_from_folder_judges_with_the_folder_and_the_register_of_dev(repo):
    """The row --settings-from-folder of interface § crap-score; DEC-71, DEC-73."""
    commit_on(repo, "dev", {
        "docs/testing.yaml": gate_yaml(8, backend_measure() + python_measure()),
        REGISTER: register((FINDING_LINT, "bug_bar_level", "12")),
    })
    repo.plant([_row("tree_severity", 10, 30), _row("bug_bar_level", 32, 50, complexity=3, coverage=0)])
    at_head(repo, {"docs/testing.yaml": gate_yaml(10)})
    repo.write(REGISTER, register())
    proc = repo.run("--all", "--story-id", STORY_ID, "--settings-from-folder")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    verdicts = {row["function"]: row["pass_fail"] for row in repo.report()}
    assert verdicts == {"tree_severity": "pass", "bug_bar_level": "accepted"}
    assert "backend" not in proc.stdout + proc.stderr
    assert f"crap-score: {FROM_FOLDER}, because the call passes --settings-from-folder" in proc.stdout


# --- CG-04-IT-17: one commit and one state of dev --------------------------


@pytest.mark.spec("CG-04-IT-17")
def test_cg_04_two_runs_on_one_head_with_dev_fixed_give_the_same_verdict(repo):
    """Scenario: One commit and one state of the exceptions register get the same verdict."""
    commit_on(repo, "dev", {REGISTER: register((FINDING_LINT, "bug_bar_level", "9"))})
    change_tree(repo, **{"docs/testing.yaml": gate_yaml(10)})
    first = repo.run(*GATE_CALL)
    first_rows = repo.report()
    second = repo.run(*GATE_CALL)
    assert first.returncode == second.returncode == 1, first.stdout + first.stderr
    assert repo.report() == first_rows
    assert first.stdout == second.stdout


# --- SEC-0009: replace refs on dev do not change what the gate reads -------


def _git_raw(repo: Repo, *args: str, data: str | None = None, index: Path | None = None) -> str:
    """Run git on the fixture repository, with its environment and, for a tree, a private index."""
    env = {**repo.env, "GIT_INDEX_FILE": str(index)} if index else repo.env
    return subprocess.run(
        ["git", *args], cwd=repo.root, env=env, input=data, check=True, capture_output=True, text=True,
    ).stdout.strip()


def _forged_docs_tree(repo: Repo, docs: str, register_text: str) -> str:
    """The tree of docs at dev with a register added, written as a new tree object."""
    index = repo.tmp / "forged-docs-index"
    _git_raw(repo, "read-tree", docs, index=index)
    blob = _git_raw(repo, "hash-object", "-w", "--stdin", data=register_text, index=index)
    _git_raw(repo, "update-index", "--add", "--cacheinfo", f"100644,{blob},findings/exceptions.md", index=index)
    return _git_raw(repo, "write-tree", index=index)


@pytest.mark.spec("CG-14-IT-01")
def test_cg_14_a_replace_ref_on_the_settings_blob_of_dev_does_not_raise_the_threshold(repo):
    """SEC-0009: git replace of docs/testing.yaml on dev with a raised threshold; the gate reads dev's true value."""
    commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(8)})
    change_tree(repo)
    real = _git_raw(repo, "rev-parse", "dev:docs/testing.yaml")
    forged = _git_raw(repo, "hash-object", "-w", "--stdin", data=gate_yaml(30))
    _git_raw(repo, "replace", real, forged)
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert "above the threshold 8" in proc.stderr


@pytest.mark.spec("CG-14-IT-01")
def test_cg_14_a_repository_setting_use_replace_refs_does_not_raise_the_threshold(repo):
    """SEC-0009: core.useReplaceRefs=true in the shared config must not turn the replace ref back on."""
    commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(8)})
    change_tree(repo)
    _git_raw(repo, "config", "core.useReplaceRefs", "true")
    real = _git_raw(repo, "rev-parse", "dev:docs/testing.yaml")
    forged = _git_raw(repo, "hash-object", "-w", "--stdin", data=gate_yaml(30))
    _git_raw(repo, "replace", real, forged)
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert "above the threshold 8" in proc.stderr


@pytest.mark.spec("CG-04-IT-17")
def test_cg_04_a_replace_ref_on_the_docs_tree_of_dev_adds_no_register_row(repo):
    """SEC-0009: git replace of the docs tree of dev with a forged register row; the gate reads dev's true register."""
    commit_on(repo, "dev", {"docs/testing.yaml": gate_yaml(8)})
    change_tree(repo)
    docs = _git_raw(repo, "rev-parse", "dev:docs")
    forged = _forged_docs_tree(repo, docs, register((FINDING_LINT, "tree_severity", "9")))
    _git_raw(repo, "replace", docs, forged)
    proc = repo.run(*GATE_CALL)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"FAIL {FINDING_LINT} tree_severity 9.00" in proc.stdout
    assert "ACCEPTED" not in proc.stdout


# --- CG-14-LN-01: the texts of the caller and the skill --------------------

FACTORY = REPO_ROOT / "packages" / "factory"


@pytest.mark.spec("CG-14-LN-01")
def test_cg_14_the_gate_check_step_calls_crap_score_without_the_option():
    """Scenario Outline: The gate-check step and the merge never take the settings from the folder."""
    text = (FACTORY / "agents" / "implementation-agent.md").read_text()
    calls = [line for line in text.splitlines() if "scripts/crap-score" in line and "--base" in line]
    assert calls, "implementation-agent.md calls crap-score nowhere"
    assert "--settings-from-folder" not in text


@pytest.mark.spec("CG-14-LN-01")
def test_cg_14_the_skill_names_the_option_and_the_source_of_each_trusted_value():
    """Finding 17 of the QA strategy's Gap Findings."""
    text = " ".join((FACTORY / "skills" / "crap-score" / "SKILL.md").read_text().split())
    assert "[--settings-from-folder]" in text
    assert "Only `gate-setup-proof` passes it" in text
    assert "`integration_branch`" in text
    assert "`dev` by default" in text
    for value in ("`threshold`", "`files`", "`exclude`", "exceptions register"):
        assert value in text
    assert "from the integration branch" in text
