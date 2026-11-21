"""Integration tests: gate-setup-proof as a subprocess on temporary git repositories (ST-0446).

docs/spec/features/crap-gate-setup.feature, Rule "Test-strategy agent checks
with gate-setup-proof that the measuring command reports true coverage"
(BR-138). Each test builds its own repository in `tmp_path` with the
branches `dev` and `feature/login`. As during the setup, docs/testing.yaml
and the measuring command lie uncommitted in the working tree (DEC-32). The
plant folder holds base/ and gap/ in the layout of the project (DEC-30).

The measuring command is a stub that reads the folder it runs in, as the QA
strategy § How the proof is tested defines. One test runs the real Python
template of setup-crap-score instead.
"""

from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR

SCRIPT = SOURCE_SCRIPTS_DIR / "gate-setup-proof"
TEMPLATE = REPO_ROOT / "packages" / "factory" / "skills" / "setup-crap-score" / "crap-measure-python"
COMMAND = "scripts/crap-measure-python"
PLANT_DIR = ".current-work/gate-setup-proof/python"
WORKTREE = ".current-work/gate-setup-proof/worktree"
PLANT_FILE = "packages/factory/scripts/proof-plant"
PLANT_TEST = "packages/factory/tests/test_proof_plant.py"
GAP_TEST = "packages/factory/tests/test_proof_gap.py"
CHECKS = ["Repeatable", "Catches CRAP", "Sees the folder", "Reports a gap"]


def settings_yaml(threshold: int = 8, command: str = COMMAND) -> str:
    return f"""\
test_command: "true"
gates:
  crap-score:
    enabled: false
    threshold: {threshold}
    timeout_minutes: 10
    measures:
      - name: python
        files: "packages/factory/scripts/*"
        command: "{command}"
"""


PROOF_PLANT = '''\
#!/usr/bin/env python3
"""Planted code of gate-setup-proof."""


def proof_untested(value):
    if value > 10:
        return "high"
    if value > 5:
        return "mid"
    return "low"


def proof_tested(value):
    if value > 10:
        return "high"
    if value > 5:
        return "mid"
    return "low"
'''

TEST_PROOF_PLANT = '''\
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

PLANT = Path(__file__).resolve().parents[1] / "scripts" / "proof-plant"
_loader = SourceFileLoader("proof_plant", str(PLANT))
proof_plant = importlib.util.module_from_spec(importlib.util.spec_from_loader("proof_plant", _loader))
_loader.exec_module(proof_plant)


def test_proof_tested():
    assert proof_plant.proof_tested(11) == "high"
    assert proof_plant.proof_tested(6) == "mid"
    assert proof_plant.proof_tested(1) == "low"
'''

TEST_PROOF_GAP = """\
def test_proof_gap():
    assert False
"""

# The stub reads the folder it runs in. MODE selects the honest stub or one
# of the four faulty stubs of the Scenario Outline.
STUB = '''\
#!/usr/bin/env python3
import ast
import json
import os
import subprocess
import sys
from pathlib import Path

MODE = "{mode}"
PLANT = "packages/factory/scripts/proof-plant"
here = Path.cwd()


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout


with open(os.environ["PROOF_LOG"], "a") as log:
    log.write(json.dumps({{
        "cwd": str(here),
        "head": git("rev-parse", "HEAD").strip(),
        "files": sorted(git("ls-tree", "-r", "--name-only", "HEAD").split()),
        "testing_yaml": git("show", "HEAD:docs/testing.yaml"),
        "stub": git("show", "HEAD:scripts/crap-measure-python"),
    }}) + "\\n")

# The faulty stub "other-folder" takes coverage from the primary checkout.
coverage_root = Path(os.environ["PROOF_PRIMARY"]) if MODE == "other-folder" else here
tested = (coverage_root / "packages/factory/tests/test_proof_plant.py").exists()
gap = (here / "packages/factory/tests/test_proof_gap.py").exists()
if gap and MODE != "hides-gap":
    print("the test run failed: test_proof_gap.py", file=sys.stderr)
    sys.exit(1)
coverage = {{"proof_untested": 0.0, "proof_tested": 100.0 if tested else 0.0}}
if MODE == "full":
    coverage = {{name: 100.0 for name in coverage}}
if MODE == "hides-gap" and gap:
    coverage = {{name: 0.0 for name in coverage}}
if MODE == "unstable":
    counter = Path(os.environ["PROOF_COUNTER"])
    start = int(counter.read_text()) + 1 if counter.exists() else 1
    counter.write_text(str(start))
    coverage["proof_untested"] = float(start)
tree = ast.parse((here / PLANT).read_text())
rows = [
    {{"file": PLANT, "function": node.name, "start_line": node.lineno, "end_line": node.end_lineno,
      "complexity": 3, "coverage_pct": coverage[node.name]}}
    for node in tree.body
    if isinstance(node, ast.FunctionDef) and node.name in coverage
]
Path(os.environ["GATE_OUTPUT"]).write_text(json.dumps(rows))
'''


class Repo:
    """A temporary repository with dev and feature/login, the setup files uncommitted."""

    def __init__(self, tmp_path: Path, mode: str = "honest") -> None:
        self.tmp = tmp_path
        home = tmp_path / "home"
        home.mkdir()
        self.log = tmp_path / "stub-log.jsonl"
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.root = (tmp_path / "repo").resolve()
        self.root.mkdir()
        self.env.update(
            HOME=str(home), GIT_CONFIG_NOSYSTEM="1", PROOF_LOG=str(self.log),
            PROOF_PRIMARY=str(self.root), PROOF_COUNTER=str(tmp_path / "counter"),
        )
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "fixture@example.com")
        self.git("config", "user.name", "Fixture")
        self.git("config", "commit.gpgsign", "false")
        self.write(".gitignore", ".current-work/\n")
        self.write("README.md", "# Demo\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        self.git("checkout", "-q", "-b", "dev")
        self.git("checkout", "-q", "-b", "feature/login")
        # Uncommitted, as setup step 4 leaves them (DEC-32).
        self.write("docs/testing.yaml", settings_yaml())
        self.stub(STUB.format(mode=mode))
        self.write(f"{PLANT_DIR}/base/{PLANT_FILE}", PROOF_PLANT)
        self.write(f"{PLANT_DIR}/base/{PLANT_TEST}", TEST_PROOF_PLANT)
        self.write(f"{PLANT_DIR}/gap/{GAP_TEST}", TEST_PROOF_GAP)

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, env=self.env, check=True, capture_output=True, text=True,
        ).stdout.strip()

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def stub(self, text: str) -> None:
        self.write(COMMAND, text)
        path = self.root / COMMAND
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def proof(self, env: dict | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--measure", "python", "--plant", PLANT_DIR],
            cwd=self.root, env=env or self.env, capture_output=True, text=True, check=False,
            timeout=600,
        )

    def starts(self) -> list[dict]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]


def check_lines(stdout: str) -> dict[str, str]:
    """The verdict of each check line of the proof's output."""
    verdicts = {}
    for line in stdout.splitlines():
        match = re.match(r"^(PASS|FAIL) (.+?): ", line)
        assert match, f"a line of the output is no check line: {line!r}"
        verdicts[match.group(2)] = match.group(1)
    return verdicts


@pytest.mark.spec("CG-02-IT-01")
def test_cg_02_the_proof_passes_an_honest_measuring_command(tmp_path: Path) -> None:
    """Scenario: The proof passes for a measuring command that measures the code of its folder.

    Scenario: The proof copies each subfolder of the plant folder onto the root of its worktree.
    """
    repo = Repo(tmp_path)

    result = repo.proof()

    assert result.returncode == 0, result.stdout + result.stderr
    assert check_lines(result.stdout) == dict.fromkeys(CHECKS, "PASS")
    assert "proof_untested scores 12.0" in result.stdout
    first, _, gap = repo.starts()
    assert {PLANT_FILE, PLANT_TEST} <= set(first["files"])
    assert GAP_TEST not in first["files"]
    assert set(gap["files"]) - set(first["files"]) == {GAP_TEST}


@pytest.mark.spec("CG-02-IT-03")
@pytest.mark.parametrize(
    ("mode", "check"),
    [
        ("unstable", "Repeatable"),
        ("full", "Catches CRAP"),
        ("other-folder", "Sees the folder"),
        ("hides-gap", "Reports a gap"),
    ],
    ids=["different rows", "full coverage", "coverage of another folder", "hidden failed test run"],
)
def test_cg_02_a_faulty_measuring_command_fails_exactly_its_check(tmp_path: Path, mode: str, check: str) -> None:
    """Scenario Outline: The proof fails for a measuring command that hides a fault."""
    repo = Repo(tmp_path, mode)

    result = repo.proof()

    assert result.returncode == 1, result.stdout + result.stderr
    expected = dict.fromkeys(CHECKS, "PASS")
    expected[check] = "FAIL"
    assert check_lines(result.stdout) == expected


@pytest.mark.spec("CG-02-IT-05")
def test_cg_02_the_proof_runs_exactly_four_checks(tmp_path: Path) -> None:
    """Scenario: The proof runs exactly four checks."""
    repo = Repo(tmp_path)

    result = repo.proof()

    assert list(check_lines(result.stdout)) == CHECKS
    assert len(result.stdout.splitlines()) == 4


@pytest.mark.spec("CG-02-IT-06")
def test_cg_02_the_measuring_command_starts_without_a_change_on_the_branch(tmp_path: Path) -> None:
    """Scenario: The proof starts the measuring command without changed code on the current branch."""
    repo = Repo(tmp_path)
    assert repo.git("rev-parse", "feature/login") == repo.git("rev-parse", "dev")
    tip = repo.git("rev-parse", "HEAD")

    result = repo.proof()

    assert result.returncode == 0, result.stdout + result.stderr
    heads = [start["head"] for start in repo.starts()]
    assert len(heads) == 3
    assert heads[0] == heads[1] != heads[2]
    assert tip not in heads
    assert all(start["cwd"] == str(repo.root / WORKTREE) for start in repo.starts())


@pytest.mark.spec("CG-02-IT-07")
def test_cg_02_the_proof_leaves_the_branches_unchanged(tmp_path: Path) -> None:
    """Scenario: The proof leaves the project's branches unchanged."""
    repo = Repo(tmp_path)
    branches = repo.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads")
    worktrees = repo.git("worktree", "list", "--porcelain")

    result = repo.proof()

    assert result.returncode == 0, result.stdout + result.stderr
    assert repo.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads") == branches
    assert repo.git("worktree", "list", "--porcelain") == worktrees
    assert not (repo.root / WORKTREE).exists()
    for line in branches.splitlines():
        files = repo.git("ls-tree", "-r", "--name-only", line.split()[0]).split()
        assert not {PLANT_FILE, PLANT_TEST, GAP_TEST} & set(files)


@pytest.mark.spec("CG-02-IT-08")
def test_cg_02_the_proof_passes_the_real_python_template(tmp_path: Path) -> None:
    """Scenario: The proof passes for a measuring command that measures the code of its folder."""
    repo = Repo(tmp_path)
    test_command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "packages/factory/tests"]
    text, count = re.subn(
        r"^TEST_COMMAND: list\[str\] = \[\]$",
        f"TEST_COMMAND: list[str] = {test_command!r}",
        TEMPLATE.read_text(),
        flags=re.MULTILINE,
    )
    assert count == 1, "the template has no empty TEST_COMMAND constant"
    repo.stub(text)
    repo.write("docs/testing.yaml", settings_yaml(command=f"uv run --quiet --script {COMMAND}"))
    # The real template would measure into the coverage run of this suite.
    env = {k: v for k, v in repo.env.items() if not k.startswith("COVERAGE_")}

    result = repo.proof(env)

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.spec("CG-02-IT-10")
def test_cg_02_the_first_commit_holds_the_setup_files_of_the_working_tree(tmp_path: Path) -> None:
    """Scenario: The first commit of the proof holds the setup files of the working tree.

    Scenario: The proof after a changed threshold reads the threshold of the working tree.
    Scenario: The proof reads the threshold from docs/testing.yaml.
    """
    repo = Repo(tmp_path)
    assert repo.git("status", "--porcelain", "--", "docs", "scripts") != ""

    result = repo.proof()

    assert result.returncode == 0, result.stdout + result.stderr
    first = repo.starts()[0]
    assert yaml.safe_load(first["testing_yaml"]) == yaml.safe_load((repo.root / "docs/testing.yaml").read_text())
    assert first["stub"] == (repo.root / COMMAND).read_text()
    assert {"docs/testing.yaml", COMMAND, PLANT_FILE, PLANT_TEST} <= set(first["files"])
    assert "above the threshold 8" in result.stdout

    repo.write("docs/testing.yaml", settings_yaml(threshold=10))
    repo.log.unlink()

    again = repo.proof()

    assert again.returncode == 0, again.stdout + again.stderr
    assert yaml.safe_load(repo.starts()[0]["testing_yaml"])["gates"]["crap-score"]["threshold"] == 10
    assert "above the threshold 10" in again.stdout


@pytest.mark.spec("CG-02-IT-11")
def test_cg_02_the_proof_removes_a_worktree_left_by_a_crashed_run(tmp_path: Path) -> None:
    """Scenario: The proof makes its worktree at a fixed path.

    Scenario: The proof removes a worktree left by a crashed run before it starts.
    """
    repo = Repo(tmp_path)
    worktrees = repo.git("worktree", "list", "--porcelain")
    leftover = repo.root / WORKTREE
    repo.git("worktree", "add", "--detach", str(leftover), "HEAD")
    (leftover / "left-by-a-crash").write_text("")

    result = repo.proof()

    assert result.returncode == 0, result.stdout + result.stderr
    starts = repo.starts()
    assert len(starts) == 3
    assert all(start["cwd"] == str(leftover) for start in starts)
    assert all("left-by-a-crash" not in start["files"] for start in starts)
    assert repo.git("worktree", "list", "--porcelain") == worktrees
    assert not leftover.exists()


TYPESCRIPT_MEASURE = """\
      - name: typescript
        files: "packages/server/**"
        command: "scripts/crap-measure-typescript"
"""


@pytest.mark.spec("CG-02-IT-10")
def test_cg_02_the_proof_of_one_measure_lists_only_that_measure(tmp_path: Path) -> None:
    """DEC-52: the first commit keeps every setting of gates.crap-score but lists only the chosen measure.

    The measure typescript names a command that the working tree does not
    hold, so a gate run that started it would exit 2 in every check.
    """
    repo = Repo(tmp_path)
    repo.write("docs/testing.yaml", settings_yaml() + TYPESCRIPT_MEASURE)

    result = repo.proof()

    assert result.returncode == 0, result.stdout + result.stderr
    assert check_lines(result.stdout) == dict.fromkeys(CHECKS, "PASS")
    working = yaml.safe_load((repo.root / "docs/testing.yaml").read_text())
    working["gates"]["crap-score"]["measures"] = working["gates"]["crap-score"]["measures"][:1]
    for start in repo.starts():
        assert yaml.safe_load(start["testing_yaml"]) == working
