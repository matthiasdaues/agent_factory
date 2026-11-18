"""Contract tests for premerge-check gate script."""

from __future__ import annotations

import json
import stat
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR, load_script

pm = load_script("premerge-check")
cs = load_script("crap-score")


class TestCheckBlowout:
    def test_under_limit_passes(self):
        ok, msg = pm.check_blowout(["a.py", "b.py"], max_files=5)
        assert ok
        assert "PASS" in msg

    def test_over_limit_blocks(self):
        files = [f"file_{i}.py" for i in range(25)]
        ok, msg = pm.check_blowout(files, max_files=20)
        assert not ok
        assert "BLOCK" in msg
        assert "25" in msg


class TestCheckOutOfScope:
    def test_no_scope_skips(self):
        ok, msg = pm.check_out_of_scope(["any/file.py"], [], None)
        assert ok
        assert "SKIP" in msg

    def test_in_scope_passes(self):
        ok, msg = pm.check_out_of_scope(
            [".agent-factory/factory/scripts/lint.py"],
            [".agent-factory/factory/scripts/"],
        )
        assert ok
        assert "PASS" in msg

    def test_out_of_scope_blocks(self):
        ok, msg = pm.check_out_of_scope(
            ["docs/README.md", ".agent-factory/factory/scripts/lint.py"],
            [".agent-factory/factory/scripts/"],
        )
        assert not ok
        assert "BLOCK" in msg
        assert "docs/README.md" in msg


class TestExtractStoryId:
    def test_story_branch_extracts_id(self):
        assert pm.extract_story_id("story/ST-0190") == "ST-0190"

    def test_non_story_branch_returns_none(self):
        assert pm.extract_story_id("feature/agent-context") is None

    def test_nested_story_branch_returns_none(self):
        assert pm.extract_story_id("story/ST-0190/fix") is None


# --- ST-0359: gate list from the story, then from testing.yaml ------------

SCRIPT = SOURCE_SCRIPTS_DIR / "premerge-check"
STORY_ID = "ST-0001"
BRANCH = f"story/{STORY_ID}"

GATES_CRAP_ONLY = """\
gates:
  crap_score:
    enabled: true
    threshold: 30
  mutation_testing:
    enabled: false
"""

GATES_BOTH = """\
gates:
  crap_score:
    enabled: true
    threshold: 30
  mutation_testing:
    enabled: true
    command: "uv run mutmut run"
"""

GATES_MUTATION_ONLY = """\
gates:
  crap_score:
    enabled: false
    threshold: 30
  mutation_testing:
    enabled: true
    command: "uv run mutmut run"
"""

NO_GATES = """\
suites:
  default:
    root: tests
"""

CRAP_PASS = [
    {
        "file": "src/planner.py",
        "function": "plan_moves",
        "complexity": 3,
        "coverage_pct": 100.0,
        "crap_score": 3.0,
        "pass_fail": "pass",
    }
]
CRAP_FAIL = [
    {
        "file": "src/planner.py",
        "function": "plan_moves",
        "complexity": 9,
        "coverage_pct": 20.0,
        "crap_score": 42.0,
        "pass_fail": "fail",
    }
]
DEPENDENCY_PASS = [
    {"rule_name": "domain-free-of-io", "pass_fail": "pass", "violating_import": None}
]
DEPENDENCY_RULES = "docs/spec/dependency-rules.dsl"
DEPENDENCY_RULE = "domain must_not_depend_on infra\n"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _story(quality_gates: str | None, body: str = "") -> str:
    field = f"quality-gates: {quality_gates}\n" if quality_gates is not None else ""
    return f"---\nid: {STORY_ID}\ntitle: Fixture story\n{field}---\n\n# Fixture story\n{body}"


GATE_STUB = """#!/bin/sh
report_dir=""
while [ $# -gt 0 ]; do
  if [ "$1" = "--report-dir" ]; then report_dir="$2"; fi
  shift
done
mkdir -p "$report_dir"
cat > "$report_dir/{story}.json" <<'JSON'
{payload}
JSON
exit {code}
"""


def _install_gate(repo: Path, name: str, body: str) -> Path:
    """Write an executable stub as the installed copy of gate *name*."""
    script = repo / ".agent-factory" / "factory" / "scripts" / name
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(body)
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def _install_stub(repo: Path, name: str, payload: object, code: int) -> Path:
    """Install a gate stub that writes *payload* as its result and exits *code*."""
    body = GATE_STUB.format(story=STORY_ID, payload=json.dumps(payload), code=code)
    return _install_gate(repo, name, body)


def _build_repo(
    tmp_path: Path,
    *,
    story: str,
    testing_yaml: str | None,
    stubs: dict[str, tuple[object, int]] | None = None,
    house_rules: str | None = None,
    extra: dict[str, str] | None = None,
) -> Path:
    """A story branch with an installed stub for each gate of *stubs*.

    Each stub writes its payload as the gate's result and exits with its code.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "fixture@example.com")
    _git(repo, "config", "user.name", "Fixture")
    (repo / "README.md").write_text("fixture\n")
    (repo / ".gitignore").write_text(".agent-factory/\n.current-work/\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    _git(repo, "checkout", "-q", "-b", BRANCH)
    (repo / "backlog").mkdir()
    (repo / "backlog" / f"{STORY_ID}.md").write_text(story)
    if testing_yaml is not None:
        (repo / "docs").mkdir(exist_ok=True)
        (repo / "docs" / "testing.yaml").write_text(testing_yaml)
    if house_rules is not None:
        (repo / "docs" / "charter").mkdir(parents=True, exist_ok=True)
        (repo / "docs" / "charter" / "house-rules.md").write_text(house_rules)
    for rel, text in (extra or {}).items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "story")
    for gate, (payload, code) in (stubs or {}).items():
        _install_stub(repo, gate, payload, code)
    return repo


def _run(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "main", BRANCH],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.spec("CAO-11-IT-03")
class TestSt0359DemoFixtures:
    """CAO-11-IT-03: premerge-check on the four Demo fixtures of ST-0359."""

    def test_st_0359_crap_over_blocks_and_names_the_function(self, tmp_path):
        repo = _build_repo(
            tmp_path,
            story=_story("[crap-score]"),
            testing_yaml=GATES_CRAP_ONLY,
            stubs={"crap-score": (CRAP_FAIL, 1)},
            extra={CHANGED_PY: "X = 1\n"},
        )
        proc = _run(repo)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert "plan_moves" in proc.stdout
        assert "42" in proc.stdout
        assert not (repo / ".current-work" / "premerge-check-ok").exists()

    def test_st_0359_testing_yaml_gates_require_crap_and_dependency_only(self, tmp_path):
        repo = _build_repo(
            tmp_path,
            story=_story(None),
            testing_yaml=GATES_CRAP_ONLY,
            stubs={"crap-score": (CRAP_PASS, 0)},
            extra={DEPENDENCY_RULES: DEPENDENCY_RULE},
        )
        proc = _run(repo)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "crap-score, dependency-check" in proc.stdout
        assert "mutation-testing" not in proc.stdout

    def test_st_0359_old_house_rules_warns_and_uses_testing_yaml(self, tmp_path):
        repo = _build_repo(
            tmp_path,
            story=_story(None),
            testing_yaml=GATES_CRAP_ONLY,
            house_rules="# House rules\n\ndefault_quality_gates: [mutation-testing]\n",
            stubs={"crap-score": (CRAP_PASS, 0)},
        )
        proc = _run(repo)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "WARN" in proc.stdout
        assert "docs/charter/house-rules.md" in proc.stdout

    def test_st_0359_no_gates_requires_crap_and_skips_dependency_without_rules(
        self, tmp_path
    ):
        repo = _build_repo(
            tmp_path,
            story=_story(None),
            testing_yaml=None,
            stubs={"crap-score": (CRAP_PASS, 0)},
        )
        proc = _run(repo)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "PASS semantic-gates: crap-score passed" in proc.stdout
        assert f"SKIP dependency-check: {DEPENDENCY_RULES} does not exist" in proc.stdout
        assert "mutation-testing" not in proc.stdout

    def test_st_0359_dependency_check_reruns_without_a_stored_result(self, tmp_path):
        repo = _build_repo(
            tmp_path,
            story=_story("[]"),
            testing_yaml=GATES_CRAP_ONLY,
            stubs={"crap-score": (CRAP_PASS, 0)},
            extra={DEPENDENCY_RULES: DEPENDENCY_RULE, "domain/model.py": "import infra\n"},
        )
        proc = _run(repo)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert "BLOCK semantic-gates: dependency-check" in proc.stdout
        assert "result not found" not in proc.stdout


def _write(top: Path, rel: str, text: str) -> None:
    path = top / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


TEST_DESIGN_BODY = "\n## Test Design\n\n#### Failure scenarios\n\n- one\n"
PRIOR_TESTS_BODY = "\n## Inputs\n\n#### Prior Tests\n\n- tests/test_x.py\n"


@pytest.mark.spec("CAO-11-CT-01")
class TestSt0359ResolveGates:
    """CAO-11-CT-01: which results premerge-check requires for a story."""

    @pytest.mark.parametrize(
        ("field", "body", "testing_yaml", "expected"),
        [
            ("[crap-score]", "", GATES_BOTH, ["crap-score", "mutation-testing"]),
            (
                "[crap-score]",
                TEST_DESIGN_BODY,
                GATES_BOTH,
                ["crap-score", "mutation-testing", "test-design-verify"],
            ),
            (None, "", GATES_BOTH, ["crap-score", "mutation-testing"]),
            (None, "", GATES_MUTATION_ONLY, ["mutation-testing"]),
            (None, "", NO_GATES, ["crap-score"]),
            (None, "", None, ["crap-score"]),
            (None, "", GATES_CRAP_ONLY, ["crap-score"]),
            (
                None,
                PRIOR_TESTS_BODY,
                None,
                ["crap-score", "test-design-verify"],
            ),
            ("[]", "", GATES_BOTH, ["crap-score", "mutation-testing"]),
            ("[]", "", None, []),
            ("[mutation-testing]", "", GATES_CRAP_ONLY, ["crap-score", "mutation-testing"]),
            (
                "[crap-score, mutation-testing, dependency-check]",
                "",
                None,
                ["crap-score", "mutation-testing"],
            ),
        ],
    )
    def test_st_0359_gate_list(self, tmp_path, field, body, testing_yaml, expected):
        _write(tmp_path, f"backlog/{STORY_ID}.md", _story(field, body))
        if testing_yaml is not None:
            _write(tmp_path, "docs/testing.yaml", testing_yaml)
        gates, warnings = pm.resolve_gates(tmp_path, STORY_ID)
        assert gates == expected
        assert warnings == []

    @pytest.mark.parametrize(("field", "expected"), [
        ("[crap-score]", ["crap-score", "dependency-check"]),
        ("[]", ["dependency-check"]),
    ])
    def test_st_0359_gate_list_with_a_rules_file(self, tmp_path, field, expected):
        _write(tmp_path, f"backlog/{STORY_ID}.md", _story(field))
        _write(tmp_path, DEPENDENCY_RULES, DEPENDENCY_RULE)
        gates, warnings = pm.resolve_gates(tmp_path, STORY_ID)
        assert gates == expected
        assert warnings == []

    def test_st_0359_house_rules_line_warns_and_is_not_a_source(self, tmp_path):
        _write(tmp_path, f"backlog/{STORY_ID}.md", _story(None))
        _write(tmp_path, "docs/testing.yaml", GATES_CRAP_ONLY)
        _write(
            tmp_path,
            "docs/charter/house-rules.md",
            "default_quality_gates: [mutation-testing]\n",
        )
        gates, warnings = pm.resolve_gates(tmp_path, STORY_ID)
        assert gates == ["crap-score"]
        assert len(warnings) == 1
        assert "docs/charter/house-rules.md" in warnings[0]


@pytest.mark.spec("CAO-11-CT-01")
class TestSt0359ReadGateResult:
    """CAO-11-CT-01: the reader accepts the list and the object result shapes."""

    @pytest.mark.parametrize(
        ("payload", "ok"),
        [
            (CRAP_PASS, True),
            (CRAP_FAIL, False),
            (DEPENDENCY_PASS, True),
            ([], True),
            ({"passed": True}, True),
            ({"passed": False}, False),
            ({}, False),
        ],
    )
    def test_st_0359_result_shapes(self, tmp_path, payload, ok):
        path = tmp_path / "r.json"
        path.write_text(json.dumps(payload))
        assert pm.read_gate_result(path)[0] is ok

    def test_st_0359_failing_crap_row_names_function_and_score(self, tmp_path):
        path = tmp_path / "r.json"
        path.write_text(json.dumps(CRAP_FAIL))
        ok, detail = pm.read_gate_result(path)
        assert not ok
        assert "plan_moves" in detail
        assert "42" in detail

    def test_st_0359_unreadable_result_fails(self, tmp_path):
        path = tmp_path / "r.json"
        path.write_text("not json")
        assert pm.read_gate_result(path) == (False, "invalid result")


# --- ST-0415: every gate that docs/testing.yaml enables -------------------

CHANGED_PY = "src/changed.py"
BUSY = "def busy(a, b):\n    if a:\n        return 1\n    if b:\n        return 2\n    return 3\n"
SIMPLE = "def simple():\n    return 1\n"

RECORDING_STUB = """#!/bin/sh
echo "$*" > {log}
"""


def _gates(body: str) -> str:
    return "gates:\n  attempts: 3\n  attempts_escalated: 2\n" + body


@pytest.mark.spec("RL-09-CT-01")
class TestSt0415GateList:
    """RL-09-CT-01: the gate list holds every enabled project gate plus the
    gates of the story's quality-gates field (BR-066)."""

    def test_st_0415_the_gate_list_of_a_story(self, tmp_path):
        """Scenario: The gate list of a story."""
        _write(tmp_path, f"backlog/{STORY_ID}.md", _story(None, TEST_DESIGN_BODY))
        _write(tmp_path, "docs/testing.yaml", _gates("  crap-score:\n    enabled: true\n"))
        _write(tmp_path, DEPENDENCY_RULES, DEPENDENCY_RULE)
        gates, warnings = pm.resolve_gates(tmp_path, STORY_ID)
        assert sorted(gates) == ["crap-score", "dependency-check", "test-design-verify"]
        assert warnings == []

    def test_st_0415_quality_gates_adds_a_gate_and_keeps_the_project_gates(self, tmp_path):
        """Scenario: A story's quality-gates field adds a gate and keeps the project's gates."""
        _write(tmp_path, f"backlog/{STORY_ID}.md", _story("[mutation-testing]"))
        _write(
            tmp_path,
            "docs/testing.yaml",
            _gates(
                "  crap-score:\n    enabled: true\n"
                "  mutation-testing:\n    enabled: false\n    command: mutmut run\n"
            ),
        )
        gates, _ = pm.resolve_gates(tmp_path, STORY_ID)
        assert gates == ["crap-score", "mutation-testing"]

    def test_st_0415_enabled_entries_count_and_scalars_are_no_gate(self, tmp_path):
        _write(tmp_path, f"backlog/{STORY_ID}.md", _story(None))
        _write(
            tmp_path,
            "docs/testing.yaml",
            _gates(
                "  license-check:\n    enabled: true\n    command: ./scripts/license-check\n"
                "  spell-check:\n    enabled: false\n    command: ./scripts/spell-check\n"
                "  mutation-testing:\n    enabled: false\n"
            ),
        )
        gates, _ = pm.resolve_gates(tmp_path, STORY_ID)
        assert gates == ["license-check"]

    def test_st_0415_an_old_key_counts_as_the_entry_of_its_gate(self, tmp_path):
        _write(tmp_path, f"backlog/{STORY_ID}.md", _story(None))
        _write(
            tmp_path,
            "docs/testing.yaml",
            _gates("  crap_score:\n    enabled: true\n  mutation_testing:\n    enabled: true\n"),
        )
        gates, warnings = pm.resolve_gates(tmp_path, STORY_ID)
        assert gates == ["crap-score", "mutation-testing"]
        assert warnings == []


@pytest.mark.spec("RL-09-CT-02")
class TestSt0415QualityGatesThatCannotRun:
    """RL-09-CT-02: a quality-gates entry that docs/testing.yaml cannot run is
    refused and named (BR-066, RL-G09)."""

    @pytest.mark.parametrize(
        "testing_yaml",
        [
            _gates(""),
            _gates("  license-check:\n    enabled: false\n"),
        ],
        ids=["no entry", "no command"],
    )
    def test_st_0415_the_merge_is_refused_and_names_the_gate(self, tmp_path, testing_yaml):
        """Scenario Outline: A quality-gates entry that docs/testing.yaml cannot run is refused."""
        repo = _build_repo(tmp_path, story=_story("[license-check]"), testing_yaml=testing_yaml)
        proc = _run(repo)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert "BLOCK semantic-gates: license-check" in proc.stdout
        assert not (repo / ".current-work" / "premerge-check-ok").exists()


@pytest.mark.spec("RL-09-CT-03")
class TestSt0415BuiltCalls:
    """RL-09-CT-03: premerge-check builds the calls of crap-score and
    mutation-testing (BR-066, RL-G17)."""

    def test_st_0415_the_built_call_of_crap_score(self, tmp_path):
        script = tmp_path / "crap-score"
        call = pm.gate_command(script, "crap-score", tmp_path, STORY_ID, {"crap-score": {"threshold": 8}})
        assert call == [
            str(script),
            "--source-root", str(tmp_path),
            "--story-id", STORY_ID,
            "--report-dir", str(tmp_path / ".current-work" / "crap-score"),
            "--threshold", "8",
            "--",
        ]

    def test_st_0415_the_built_call_of_crap_score_without_a_threshold(self, tmp_path):
        call = pm.gate_command(tmp_path / "crap-score", "crap-score", tmp_path, STORY_ID, {})
        assert "--threshold" not in call

    def test_st_0415_the_built_call_of_mutation_testing(self, tmp_path):
        script = tmp_path / "mutation-testing"
        call = pm.gate_command(script, "mutation-testing", tmp_path, STORY_ID, {})
        assert call == [
            str(script),
            "--story-id", STORY_ID,
            "--testing-yaml", str(tmp_path / "docs" / "testing.yaml"),
            "--report-dir", str(tmp_path / ".current-work" / "mutation-testing"),
        ]

    @pytest.mark.parametrize("gate", ["crap-score", "mutation-testing"])
    def test_st_0415_premerge_check_runs_its_built_call(self, tmp_path, gate):
        """Scenario Outline: premerge-check builds the call of a gate that it names."""
        repo = _build_repo(
            tmp_path,
            story=_story("[]"),
            testing_yaml=_gates(f"  {gate}:\n    enabled: true\n"),
            extra={CHANGED_PY: "X = 1\n"},
        )
        log = tmp_path / "gate.log"
        _install_gate(repo, gate, RECORDING_STUB.format(log=log))
        proc = _run(repo)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert f"--story-id {STORY_ID}" in log.read_text()
        assert f"PASS semantic-gates: {gate} passed" in proc.stdout


@pytest.mark.spec("RL-09-CT-03")
class TestSt0415CrapScoreScoresTheDiff:
    """RL-09-CT-03: the built call of crap-score scores only the `.py` files
    of the story's diff (IMPL-0024, BR-066)."""

    def _score(self, top: Path, diff: list[str]) -> tuple[int, list[dict]]:
        py_files = pm.changed_python_files(top, diff)
        call = pm.gate_command(
            top / "crap-score", "crap-score", top, STORY_ID,
            {"crap-score": {"threshold": 8}}, py_files,
        )
        code = cs.main(call[1:])
        report = top / ".current-work" / "crap-score" / f"{STORY_ID}.json"
        return code, json.loads(report.read_text())

    def test_st_0415_a_function_the_story_did_not_touch_never_fails(self, tmp_path):
        _write(tmp_path, "src/untouched.py", BUSY)
        _write(tmp_path, CHANGED_PY, SIMPLE)
        code, rows = self._score(tmp_path, [CHANGED_PY, "README.md", "src/deleted.py"])
        assert code == 0
        assert [r["function"] for r in rows] == ["simple"]

    def test_st_0415_a_changed_function_above_the_threshold_still_fails(self, tmp_path):
        _write(tmp_path, CHANGED_PY, BUSY)
        code, rows = self._score(tmp_path, [CHANGED_PY])
        assert code == 1
        assert [(r["function"], r["pass_fail"]) for r in rows] == [("busy", "fail")]

    def test_st_0415_no_changed_py_file_passes_and_scores_nothing(self, tmp_path):
        repo = _build_repo(
            tmp_path, story=_story("[]"), testing_yaml=_gates("  crap-score:\n    enabled: true\n"),
        )
        _git(repo, "checkout", "-q", "main")
        _write(repo, "src/untouched.py", BUSY)
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "complex code on main")
        _git(repo, "checkout", "-q", BRANCH)
        _git(repo, "merge", "-q", "--no-edit", "main")
        log = tmp_path / "gate.log"
        _install_gate(repo, "crap-score", RECORDING_STUB.format(log=log))
        proc = _run(repo)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert f"PASS crap-score: {STORY_ID} changed no .py file, so it scored nothing" in proc.stdout
        assert not log.exists()


@pytest.mark.spec("RL-09-CT-04")
def test_st_0415_premerge_check_reads_the_old_key_crap_score(tmp_path):
    """Scenario: premerge-check reads the old key crap_score."""
    testing_yaml = _gates("  crap_score:\n    enabled: true\n    threshold: 8\n")
    repo = _build_repo(
        tmp_path, story=_story(None), testing_yaml=testing_yaml, extra={CHANGED_PY: "X = 1\n"}
    )
    log = tmp_path / "gate.log"
    _install_gate(repo, "crap-score", RECORDING_STUB.format(log=log))
    proc = _run(repo)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "--threshold 8" in log.read_text()
    assert (repo / "docs" / "testing.yaml").read_text() == testing_yaml
    assert subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout == ""


@pytest.mark.spec("RL-09-CT-05")
def test_st_0415_with_both_keys_the_key_with_hyphens_wins_with_a_warning(tmp_path):
    _write(tmp_path, f"backlog/{STORY_ID}.md", _story(None))
    _write(
        tmp_path,
        "docs/testing.yaml",
        _gates(
            "  crap_score:\n    enabled: true\n    threshold: 5\n"
            "  crap-score:\n    enabled: true\n    threshold: 8\n"
        ),
    )
    gates, warnings = pm.resolve_gates(tmp_path, STORY_ID)
    assert gates == ["crap-score"]
    assert len(warnings) == 1
    assert "gates.crap_score" in warnings[0]
    entries, _ = pm.gate_entries(tmp_path)
    call = pm.gate_command(tmp_path / "crap-score", "crap-score", tmp_path, STORY_ID, entries)
    assert call[-3:] == ["--threshold", "8", "--"]


@pytest.mark.spec("RL-09-CT-05")
def test_st_0415_the_warning_of_both_keys_reaches_the_output(tmp_path):
    testing_yaml = _gates(
        "  crap_score:\n    enabled: true\n    threshold: 5\n"
        "  crap-score:\n    enabled: true\n    threshold: 8\n"
    )
    repo = _build_repo(
        tmp_path, story=_story(None), testing_yaml=testing_yaml, extra={CHANGED_PY: "X = 1\n"}
    )
    log = tmp_path / "gate.log"
    _install_gate(repo, "crap-score", "#!/bin/sh\necho run >> " + str(log) + "\n")
    proc = _run(repo)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "WARN semantic-gates" in proc.stdout
    assert "gates.crap_score" in proc.stdout
    assert log.read_text() == "run\n"


@pytest.mark.spec("RL-09-CT-07")
class TestSt0415EnabledEntryWithoutCommand:
    """RL-09-CT-07: an enabled entry without a command, for a gate the script
    does not name, is refused and named, also when no story names it (OI-15)."""

    def test_st_0415_an_enabled_entry_without_a_command_is_refused(self, tmp_path):
        repo = _build_repo(
            tmp_path,
            story=_story("[]"),
            testing_yaml=_gates("  license-check:\n    enabled: true\n"),
        )
        proc = _run(repo)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert "BLOCK semantic-gates: license-check" in proc.stdout
        assert "has no command" in proc.stdout

    def test_st_0415_a_disabled_entry_without_a_command_is_no_refusal(self, tmp_path):
        repo = _build_repo(
            tmp_path,
            story=_story("[]"),
            testing_yaml=_gates("  license-check:\n    enabled: false\n"),
        )
        proc = _run(repo)
        assert proc.returncode == 0, proc.stdout + proc.stderr

    @pytest.mark.parametrize("gate", ["crap-score", "mutation-testing"])
    def test_st_0415_a_built_in_gate_needs_no_command(self, gate):
        assert pm.gate_refusal(gate, {gate: {"enabled": True}}) is None

    def test_st_0415_an_unnamed_gate_names_the_missing_command(self):
        refusal = pm.gate_refusal("license-check", {"license-check": {"enabled": True}})
        assert refusal is not None
        assert "license-check" in refusal
