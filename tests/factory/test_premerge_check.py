"""Contract tests for premerge-check gate script."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR, load_script

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


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _story(quality_gates: str | None, body: str = "") -> str:
    field = f"quality-gates: {quality_gates}\n" if quality_gates is not None else ""
    return f"---\nid: {STORY_ID}\ntitle: Fixture story\n{field}---\n\n# Fixture story\n{body}"


def _build_repo(
    tmp_path: Path,
    *,
    story: str,
    testing_yaml: str | None,
    results: dict[str, object],
    house_rules: str | None = None,
) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "fixture@example.com")
    _git(repo, "config", "user.name", "Fixture")
    (repo / "README.md").write_text("fixture\n")
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
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "story")
    for gate, payload in results.items():
        gate_dir = repo / ".current-work" / gate
        gate_dir.mkdir(parents=True, exist_ok=True)
        (gate_dir / f"{STORY_ID}.json").write_text(json.dumps(payload))
    return repo


def _run(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "main", BRANCH],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


class TestSt0359DemoFixtures:
    """CAO-11-IT-03: premerge-check on the four Demo fixtures of ST-0359."""

    def test_st_0359_crap_over_blocks_and_names_the_function(self, tmp_path):
        repo = _build_repo(
            tmp_path,
            story=_story("[crap-score]"),
            testing_yaml=GATES_CRAP_ONLY,
            results={"crap-score": CRAP_FAIL, "dependency-check": DEPENDENCY_PASS},
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
            results={"crap-score": CRAP_PASS, "dependency-check": DEPENDENCY_PASS},
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
            results={"crap-score": CRAP_PASS, "dependency-check": DEPENDENCY_PASS},
        )
        proc = _run(repo)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "WARN" in proc.stdout
        assert "docs/charter/house-rules.md" in proc.stdout

    def test_st_0359_no_gates_requires_crap_and_dependency_without_mutation(self, tmp_path):
        repo = _build_repo(
            tmp_path,
            story=_story(None),
            testing_yaml=None,
            results={"crap-score": CRAP_PASS, "dependency-check": DEPENDENCY_PASS},
        )
        proc = _run(repo)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "crap-score, dependency-check" in proc.stdout
        assert "mutation-testing" not in proc.stdout

    def test_st_0359_missing_dependency_result_blocks(self, tmp_path):
        repo = _build_repo(
            tmp_path,
            story=_story("[]"),
            testing_yaml=GATES_CRAP_ONLY,
            results={},
        )
        proc = _run(repo)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert "dependency-check (result not found)" in proc.stdout


def _write(top: Path, rel: str, text: str) -> None:
    path = top / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


TEST_DESIGN_BODY = "\n## Test Design\n\n#### Failure scenarios\n\n- one\n"
PRIOR_TESTS_BODY = "\n## Inputs\n\n#### Prior Tests\n\n- tests/test_x.py\n"


class TestSt0359ResolveGates:
    """CAO-11-CT-01: which results premerge-check requires for a story."""

    @pytest.mark.parametrize(
        ("field", "body", "testing_yaml", "expected"),
        [
            ("[crap-score]", "", GATES_BOTH, ["crap-score", "dependency-check"]),
            (
                "[crap-score]",
                TEST_DESIGN_BODY,
                GATES_BOTH,
                ["crap-score", "test-design-verify", "dependency-check"],
            ),
            (None, "", GATES_BOTH, ["crap-score", "mutation-testing", "dependency-check"]),
            (None, "", GATES_MUTATION_ONLY, ["mutation-testing", "dependency-check"]),
            (None, "", NO_GATES, ["crap-score", "dependency-check"]),
            (None, "", None, ["crap-score", "dependency-check"]),
            (None, "", GATES_CRAP_ONLY, ["crap-score", "dependency-check"]),
            (
                None,
                PRIOR_TESTS_BODY,
                None,
                ["crap-score", "test-design-verify", "dependency-check"],
            ),
            ("[]", "", GATES_BOTH, ["dependency-check"]),
            (
                "[crap-score, mutation-testing, dependency-check]",
                "",
                None,
                ["crap-score", "mutation-testing", "dependency-check"],
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

    def test_st_0359_house_rules_line_warns_and_is_not_a_source(self, tmp_path):
        _write(tmp_path, f"backlog/{STORY_ID}.md", _story(None))
        _write(tmp_path, "docs/testing.yaml", GATES_CRAP_ONLY)
        _write(
            tmp_path,
            "docs/charter/house-rules.md",
            "default_quality_gates: [mutation-testing]\n",
        )
        gates, warnings = pm.resolve_gates(tmp_path, STORY_ID)
        assert gates == ["crap-score", "dependency-check"]
        assert len(warnings) == 1
        assert "docs/charter/house-rules.md" in warnings[0]


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
