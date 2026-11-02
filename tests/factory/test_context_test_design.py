"""Regression tests for context-lint and test-design-verify (ST-0300).

BUG-0062: context-lint judged docs/testing.yaml wrong in both directions.
BUG-0063: test-design-verify rejected a `tests:` block list as empty.

Both scripts run as subprocesses, as in test_context_lint.py.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent.parent / "packages" / "factory" / "scripts"
CONTEXT_LINT = SCRIPTS / "context-lint"
TEST_DESIGN_VERIFY = SCRIPTS / "test-design-verify"


# --- BUG-0062: context-lint parses testing.yaml as YAML ---------------------


def _testing_yaml_findings(tmp_path: Path, text: str) -> list[dict]:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "testing.yaml").write_text(text, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(CONTEXT_LINT), "--root", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stderr)
    return [f for f in payload["findings"] if f["artifact"] == "testing.yaml"]


def test_bug_0062_valid_block_scalar_passes(tmp_path: Path) -> None:
    text = (
        "suites:\n"
        "  unit:\n"
        "    root: tests\n"
        "    run_all: |\n"
        "      uv run pytest\n"
        "      --quiet\n"
    )

    assert _testing_yaml_findings(tmp_path, text) == []


def test_bug_0062_unclosed_quote_and_bracket_fails(tmp_path: Path) -> None:
    text = (
        "suites:\n"
        "  unit:\n"
        '    root: "tests\n'
        "    markers: [spec, contract\n"
    )

    findings = _testing_yaml_findings(tmp_path, text)

    assert [f["code"] for f in findings] == ["CX-PARSE"]


def test_bug_0062_missing_pyyaml_exits_2_with_one_line(tmp_path: Path) -> None:
    stubs = tmp_path / "stubs"
    stubs.mkdir()
    (stubs / "yaml.py").write_text(
        'raise ImportError("No module named \'yaml\'")\n', encoding="utf-8"
    )
    project = tmp_path / "project"
    (project / "docs").mkdir(parents=True)
    (project / "docs" / "testing.yaml").write_text("suites: {}\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(CONTEXT_LINT), "--root", str(project)],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(stubs)},
    )

    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert result.stderr.strip().count("\n") == 0
    assert "PyYAML" in result.stderr


# --- BUG-0063: test-design-verify reads a tests: block list -----------------


def _verify_story(tmp_path: Path, frontmatter_tests: str) -> tuple[int, dict]:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("", encoding="utf-8")
    story = tmp_path / "ST-9999.md"
    story.write_text(
        "---\n"
        "id: ST-9999\n"
        "test-design-pass: done\n"
        f"{frontmatter_tests}"
        "---\n"
        "\n"
        "# Story\n",
        encoding="utf-8",
    )
    report_dir = tmp_path / "reports"
    result = subprocess.run(
        [
            sys.executable,
            str(TEST_DESIGN_VERIFY),
            "--story",
            str(story),
            "--repo-root",
            str(tmp_path),
            "--report-dir",
            str(report_dir),
            "--epics",
            str(tmp_path / "epics.md"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    report = json.loads((report_dir / "ST-9999.json").read_text(encoding="utf-8"))
    return result.returncode, report


def test_bug_0063_indented_block_list_passes(tmp_path: Path) -> None:
    code, report = _verify_story(tmp_path, "tests:\n  - tests/test_a.py\n")

    assert report["findings"] == []
    assert code == 0


def test_bug_0063_block_list_checks_each_module(tmp_path: Path) -> None:
    code, report = _verify_story(
        tmp_path, "tests:\n- tests/test_a.py\n- 'tests/test_missing.py'\n"
    )

    assert [f["kind"] for f in report["findings"]] == ["missing_test_module"]
    assert "tests/test_missing.py" in report["findings"][0]["message"]
    assert code == 1


def test_bug_0063_key_without_items_stays_empty(tmp_path: Path) -> None:
    code, report = _verify_story(tmp_path, "tests:\nnext-key: x\n")

    assert [f["kind"] for f in report["findings"]] == ["empty_tests_field"]
    assert code == 1


# --- ST-0340: test-design-verify reads feature files from docs/spec/features/

PAYMENTS_FEATURE = (
    "Feature: Payments\n"
    "\n"
    "  Rule: Merchant receives a payout\n"
    "\n"
    "    Scenario: Payout reaches the merchant\n"
    "      Given a settled payment\n"
    "\n"
    "    Scenario: Payout to a closed account is held\n"
    "      Given a closed account\n"
)


def _verify_traced_rule(tmp_path: Path, feature_location: str) -> tuple[int, dict]:
    spec = tmp_path / "docs" / "spec"
    feature = spec / feature_location
    feature.parent.mkdir(parents=True, exist_ok=True)
    feature.write_text(PAYMENTS_FEATURE, encoding="utf-8")
    (spec / "scope-map.md").write_text(
        "| Rule | Status | Sources |\n"
        "| --- | --- | --- |\n"
        "| Merchant receives a payout | specified | "
        "[payments.feature](features/payments.feature) |\n",
        encoding="utf-8",
    )
    (tmp_path / "backlog").mkdir()
    (tmp_path / "backlog" / "ST-0001.md").write_text(
        "---\n"
        "id: ST-0001\n"
        "traces: [payments.feature/Rule-01]\n"
        "---\n"
        "\n"
        "#### Failure scenarios\n"
        "\n"
        "- Payout reaches the merchant\n"
        "- Payout to a closed account is held\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(TEST_DESIGN_VERIFY), "--story", "backlog/ST-0001.md"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    report_path = tmp_path / ".current-work" / "test-design-verify" / "ST-0001.json"
    return result.returncode, json.loads(report_path.read_text(encoding="utf-8"))


def test_st_0340_resolves_rule_in_features_folder(tmp_path: Path) -> None:
    code, report = _verify_traced_rule(tmp_path, "features/payments.feature")

    assert report["resolved"][0]["feature"].endswith("docs/spec/features/payments.feature")
    assert report["resolved"][0]["scenarios"] == [
        "Payout reaches the merchant",
        "Payout to a closed account is held",
    ]
    assert code == 0


def test_st_0340_feature_at_top_of_spec_is_missing(tmp_path: Path) -> None:
    code, report = _verify_traced_rule(tmp_path, "payments.feature")

    assert len(report["config_errors"]) == 1
    assert "missing .feature file" in report["config_errors"][0]
    assert "docs/spec/features/payments.feature" in report["config_errors"][0]
    assert code == 2
