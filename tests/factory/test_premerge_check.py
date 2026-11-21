"""Contract tests for premerge-check gate script."""

from __future__ import annotations

import json
import stat
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR, load_script, write_review_report

pm = load_script("premerge-check")


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


@pytest.mark.spec("RL-08-CT-01")
class TestExtractStoryId:
    """The branch pattern yields a story ID or a finding ID (ST-0422)."""

    @pytest.mark.parametrize(
        ("branch", "unit_id"),
        [
            ("story/ST-0190", "ST-0190"),
            ("story/BUG-0090", "BUG-0090"),
            ("story/QA-0012", "QA-0012"),
        ],
    )
    def test_story_branch_extracts_id(self, branch, unit_id):
        assert pm.extract_story_id(branch) == unit_id

    @pytest.mark.parametrize("branch", ["feature/agent-context", "feature/BUG-0090"])
    def test_non_story_branch_returns_none(self, branch):
        assert pm.extract_story_id(branch) is None

    @pytest.mark.parametrize(
        "branch", ["story/ST-0190/fix", "story/BUG-0090/fix", "story/bug-0090"]
    )
    def test_nested_story_branch_returns_none(self, branch):
        assert pm.extract_story_id(branch) is None


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
    # A review of the commit before the story's work passes the review check (BR-122).
    write_review_report(repo, STORY_ID)
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
            (None, "", NO_GATES, []),
            (None, "", None, []),
            (None, "", GATES_CRAP_ONLY, ["crap-score"]),
            (
                None,
                PRIOR_TESTS_BODY,
                None,
                ["test-design-verify"],
            ),
            ("[]", "", GATES_BOTH, ["crap-score", "mutation-testing"]),
            ("[]", "", None, []),
            ("[mutation-testing]", "", GATES_CRAP_ONLY, ["crap-score", "mutation-testing"]),
        ],
    )
    def test_st_0359_gate_list(self, tmp_path, field, body, testing_yaml, expected):
        _write(tmp_path, f"backlog/{STORY_ID}.md", _story(field, body))
        if testing_yaml is not None:
            _write(tmp_path, "docs/testing.yaml", testing_yaml)
        gates, warnings = pm.resolve_gates(tmp_path, STORY_ID)
        assert gates == expected
        assert warnings == []

    def test_st_0434_a_field_with_crap_score_without_a_file_is_refused(self, tmp_path):
        """The field names crap-score without an entry, so the gate is refused and
        names setup-crap-score; mutation-testing needs no entry (DEC-21)."""
        _write(
            tmp_path,
            f"backlog/{STORY_ID}.md",
            _story("[crap-score, mutation-testing, dependency-check]"),
        )
        gates, warnings = pm.resolve_gates(tmp_path, STORY_ID)
        assert gates == ["crap-score", "mutation-testing"]
        assert warnings == []
        entries, _ = pm.gate_entries(tmp_path)
        refusal = pm.gate_refusal("crap-score", entries)
        assert refusal is not None
        assert "setup-crap-score" in refusal
        assert pm.gate_refusal("mutation-testing", entries) is None

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


# --- ST-0413: the review check, the finding check, and the story's own files ---


@pytest.mark.spec("RL-08-IT-03")
@pytest.mark.parametrize(
    ("category", "severity", "blocks"),
    [
        ("defect", "critical", True),
        ("defect", "major", True),
        ("risk", "major", True),
        ("defect", "minor", False),
        ("risk", "note", False),
        ("suggestion", "major", False),
        ("question", "critical", False),
        (None, None, False),
    ],
)
def test_st_0413_the_blocking_rule_of_br_085(category, severity, blocks):
    """A finding blocks when its category is defect or risk and its severity
    is critical or major (BR-085, finding-classification.md)."""
    assert pm.is_blocking({"category": category, "severity": severity}) is blocks


def _owned_repo(tmp_path: Path, monkeypatch, files: dict[str, str]) -> Path:
    """A repository whose story branch commits *files*; the test runs in it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "fixture@example.com")
    _git(repo, "config", "user.name", "Fixture")
    (repo / "README.md").write_text("fixture\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    _git(repo, "checkout", "-q", "-b", BRANCH)
    for rel, text in files.items():
        _write(repo, rel, text)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "story")
    monkeypatch.chdir(repo)
    return repo


@pytest.mark.spec("RL-08-IT-07")
def test_st_0413_a_file_belongs_to_the_story_by_its_name_or_its_story_field(
    tmp_path, monkeypatch
):
    files = {
        f"docs/reviews/code-review-{STORY_ID}-2026-11-18.md": "no frontmatter\n",
        "docs/findings/BUG-0091.md": f"---\nid: BUG-0091\nstory: {STORY_ID}\n---\n",
        "docs/findings/BUG-0092.md": "---\nid: BUG-0092\nstory: ST-0002\n---\n",
        "docs/findings/register/code/IMPL-0093.json": json.dumps({"story": STORY_ID}),
        "docs/findings/register/code/IMPL-0094.json": json.dumps({"story": "ST-0002"}),
        f"src/{STORY_ID}.py": "X = 1\n",
    }
    _owned_repo(tmp_path, monkeypatch, files)

    owned = pm.story_owned_files(
        "main", BRANCH, STORY_ID, [*files, "docs/findings/BUG-0099.md"]
    )

    assert owned == [
        f"docs/reviews/code-review-{STORY_ID}-2026-11-18.md",
        "docs/findings/BUG-0091.md",
        "docs/findings/register/code/IMPL-0093.json",
    ]


@pytest.mark.spec("RL-08-IT-08")
def test_st_0422_a_rewritten_story_field_takes_no_file_of_another_story(
    tmp_path, monkeypatch
):
    """IMPL-0027: for a file that exists at the merge base, the `story` field
    counts at the merge base, and a file new on the branch counts at the head."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "fixture@example.com")
    _git(repo, "config", "user.name", "Fixture")
    _write(repo, "docs/findings/BUG-0092.md", "---\nid: BUG-0092\nstory: ST-0002\n---\n")
    _write(repo, "docs/findings/BUG-0093.md", f"---\nid: BUG-0093\nstory: {STORY_ID}\n---\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    _git(repo, "checkout", "-q", "-b", BRANCH)
    _write(repo, "docs/findings/BUG-0092.md", f"---\nid: BUG-0092\nstory: {STORY_ID}\n---\n")
    _write(repo, "docs/findings/BUG-0093.md", "---\nid: BUG-0093\nstory: ST-0002\n---\n")
    _write(repo, "docs/findings/BUG-0094.md", f"---\nid: BUG-0094\nstory: {STORY_ID}\n---\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "story")
    monkeypatch.chdir(repo)
    files = [f"docs/findings/BUG-009{n}.md" for n in (2, 3, 4)]

    owned = pm.story_owned_files("main", BRANCH, STORY_ID, files)

    assert owned == ["docs/findings/BUG-0093.md", "docs/findings/BUG-0094.md"]


@pytest.mark.spec("RL-08-IT-08")
def test_st_0422_a_renamed_finding_of_another_story_keeps_its_old_name_in_the_diff(
    tmp_path, monkeypatch
):
    """IMPL-0057: the branch renames BUG-0092 of ST-0002 and rewrites its story
    field. The diff lists the old name too, and the old name is no file of
    the story, so the scope check sees it."""
    body = "A long body line one.\nA long body line two.\nA long body line three.\n"
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "fixture@example.com")
    _git(repo, "config", "user.name", "Fixture")
    _write(repo, "docs/findings/BUG-0092.md",
           f"---\nid: BUG-0092\nstatus: open\nstory: ST-0002\n---\n\n{body}")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    _git(repo, "checkout", "-q", "-b", BRANCH)
    (repo / "docs/findings/BUG-0092.md").unlink()
    _write(repo, "docs/findings/BUG-0092-fixed.md",
           f"---\nid: BUG-0092\nstatus: resolved\nstory: {STORY_ID}\n---\n\n{body}")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "rename")
    monkeypatch.chdir(repo)

    code, files, _ = pm.changed_files("main", BRANCH)
    owned = pm.story_owned_files("main", BRANCH, STORY_ID, files)

    assert code == 0
    assert sorted(files) == ["docs/findings/BUG-0092-fixed.md", "docs/findings/BUG-0092.md"]
    assert "docs/findings/BUG-0092.md" not in owned
    ok, line = pm.check_out_of_scope(files, owned)
    assert not ok
    assert "docs/findings/BUG-0092.md" in line


@pytest.mark.spec("RL-08-IT-07")
def test_st_0413_the_storys_own_files_do_not_count_toward_the_limit():
    files = [f"src/f{n}.py" for n in range(20)] + ["docs/findings/BUG-0091.md"]
    ok, line = pm.check_blowout(files, 20, ["docs/findings/BUG-0091.md"])
    assert ok, line
    assert "20 files changed, not counting 1 review or finding file(s)" in line
    ok, line = pm.check_blowout(files, 20)
    assert not ok
    assert "21 files changed" in line


@pytest.mark.spec("RL-08-IT-01")
def test_st_0413_a_report_of_the_story_at_an_ancestor_passes(tmp_path, monkeypatch):
    repo = _owned_repo(tmp_path, monkeypatch, {"src/a.py": "X = 1\n"})
    write_review_report(repo, STORY_ID)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "review")

    ok, line = pm.check_code_review(BRANCH, STORY_ID)

    assert ok, line
    assert f"docs/reviews/code-review-{STORY_ID}-2026-11-18.md" in line


@pytest.mark.spec("RL-08-IT-02")
def test_st_0413_open_blocking_findings_of_the_story_are_named(tmp_path, monkeypatch):
    finding = "---\nid: {id}\ncategory: defect\nseverity: major\nstatus: {status}\nstory: {story}\n---\n"
    _owned_repo(
        tmp_path,
        monkeypatch,
        {
            "docs/findings/BUG-0091.md": finding.format(id="BUG-0091", status="open", story=STORY_ID),
            "docs/findings/BUG-0092.md": finding.format(id="BUG-0092", status="open", story=STORY_ID),
            "docs/findings/BUG-0093.md": finding.format(id="BUG-0093", status="waived", story=STORY_ID),
            "docs/findings/BUG-0094.md": finding.format(id="BUG-0094", status="open", story="ST-0002"),
            "docs/findings/BUG-0095.md": f"---\nstory: {STORY_ID}\nnot: [closed\n---\n",
        },
    )

    ok, line = pm.check_open_findings(BRANCH, STORY_ID)

    assert not ok
    assert f"BUG-0091, BUG-0092 of {STORY_ID} are open and blocking" in line


@pytest.mark.spec("RL-08-IT-02")
def test_st_0413_a_path_git_cannot_read_raises_and_names_it(tmp_path, monkeypatch):
    _owned_repo(tmp_path, monkeypatch, {"README.md": "changed\n"})
    with pytest.raises(pm.GitReadError, match="docs/findings/BUG-0099.md missing"):
        pm.read_at_head(BRANCH, ["README.md", "docs/findings/BUG-0099.md"])


# --- ST-0423: the result rule of the mutation gate (BR-066, RL-G25) -------

QA_FILE = "docs/findings/QA-0012.md"
QA_FINDING = (
    "---\nid: QA-0012\ncategory: defect\nseverity: major\nstatus: open\n"
    "owner: planning-agent\nstory:\nrun: feature/login\n---\n"
)


def _mutant(status: str = "survived", action: str = "file-qa-finding", **extra) -> dict:
    return {
        "operator": "+ -> -", "location": "src/login.py:42",
        "status": status, "resolution_action": action, **extra,
    }


FILED = _mutant(finding="QA-0012")
KILLED = _mutant("killed", "none-required")


def _mutation(exit_code=1, timed_out=False, **extra) -> dict:
    return {
        "story_id": STORY_ID, "passed": exit_code == 0 and not timed_out,
        "command": "mutmut run", "timeout_seconds": 1800,
        "exit_code": exit_code, "timed_out": timed_out, "message": "x", **extra,
    }


@pytest.mark.spec("RL-12-CT-03")
@pytest.mark.parametrize(
    ("payload", "ok"),
    [
        (_mutation(0), True),
        (_mutation(0, mutants=[_mutant(action="unresolved")]), True),
        (_mutation(1), False),
        (_mutation(1, mutants=[]), False),
        (_mutation(1, mutants=[KILLED]), False),
        (_mutation(1, mutants=[FILED, KILLED]), True),
        (_mutation(1, mutants=[_mutant(action="add-missing-test"), _mutant(action="remove-dead-code")]), True),
        (_mutation(1, mutants=[FILED, _mutant(action="unresolved")]), False),
        (_mutation(1, mutants=[FILED, _mutant(action="none-required")]), False),
        (_mutation(1, mutants=[_mutant()]), False),
        (_mutation(1, mutants=[_mutant(finding="QA-0013")]), False),
        (_mutation(1, mutants=[_mutant(finding="../../README")]), False),
        (_mutation(None, timed_out=True, mutants=[FILED]), False),
        (_mutation(None, mutants=[FILED]), False),
    ],
    ids=[
        "exit-0", "exit-0-whatever-the-list-holds", "no-list", "empty-list",
        "no-survivor", "filed-survivor", "test-and-dead-code", "one-unresolved",
        "survivor-without-an-action", "file-qa-finding-without-finding",
        "finding-file-missing", "finding-id-outside-the-folder",
        "time-out-with-a-resolved-list", "command-did-not-run",
    ],
)
def test_st_0423_read_gate_result_applies_the_mutation_rule(tmp_path, monkeypatch, payload, ok):
    """RL-12-CT-03: after a non-zero exit, the mutation result passes only with a
    survivor, none unresolved, and every named finding file at the branch head."""
    _owned_repo(tmp_path, monkeypatch, {QA_FILE: QA_FINDING})
    path = tmp_path / "r.json"
    path.write_text(json.dumps(payload))
    passed, detail = pm.read_gate_result(path, BRANCH)
    assert passed is ok, detail


@pytest.mark.spec("RL-12-CT-03")
def test_st_0423_a_failing_mutation_result_names_its_cause(tmp_path, monkeypatch):
    _owned_repo(tmp_path, monkeypatch, {QA_FILE: QA_FINDING})
    cases = {
        "no list mutants": _mutation(1),
        "holds no survivor": _mutation(1, mutants=[]),
        "src/login.py:42 is unresolved": _mutation(1, mutants=[_mutant(action="unresolved")]),
        "QA-0013, which has no file docs/findings/QA-0013.md": _mutation(
            1, mutants=[_mutant(finding="QA-0013")]
        ),
        "time limit": _mutation(None, timed_out=True, mutants=[FILED]),
    }
    for expected, payload in cases.items():
        path = tmp_path / "r.json"
        path.write_text(json.dumps(payload))
        passed, detail = pm.read_gate_result(path, BRANCH)
        assert not passed
        assert expected in detail, (expected, detail)


@pytest.mark.spec("RL-12-CT-03")
def test_st_0423_a_named_finding_with_the_run_joins_the_story_scope(tmp_path, monkeypatch):
    """The scope of the story holds a finding file with `run` set to the target
    when a `file-qa-finding` entry of the stored result names it (BR-066)."""
    other = QA_FINDING.replace("QA-0012", "QA-0014")
    elsewhere = QA_FINDING.replace("QA-0012", "QA-0015").replace("feature/login", "feature/other")
    repo = _owned_repo(
        tmp_path, monkeypatch,
        {QA_FILE: QA_FINDING, "docs/findings/QA-0014.md": other,
         "docs/findings/QA-0015.md": elsewhere},
    )
    _git(repo, "branch", "feature/login", "main")
    stored = _mutation(1, mutants=[FILED, _mutant(finding="QA-0015")])
    _write(repo, f".current-work/mutation-testing/{STORY_ID}.json", json.dumps(stored))
    files = [QA_FILE, "docs/findings/QA-0014.md", "docs/findings/QA-0015.md"]

    owned = pm.story_owned_files("feature/login", BRANCH, STORY_ID, files)

    assert owned == [QA_FILE]
