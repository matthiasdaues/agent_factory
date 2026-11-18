"""Contract tests for crap-score gate script."""

from __future__ import annotations

import json

import pytest
from conftest import load_script

cs = load_script("crap-score")

SOURCE = """\
class Greeter:
    def greet(self, name):
        if name:
            return name
        return "anon"


def helper():
    return 1
"""


def test_each_function_reported_once(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "module.py").write_text(SOURCE, encoding="utf-8")
    reports = tmp_path / "reports"

    cs.main(
        [
            "--source-root",
            str(src),
            "--report-dir",
            str(reports),
            "--story-id",
            "ST-0000",
            "--threshold",
            "1000",
        ]
    )

    results = json.loads((reports / "ST-0000.json").read_text(encoding="utf-8"))
    names = sorted(r["function"] for r in results)
    assert names == ["greet", "helper"]


# --- ST-0415: crap-score reads both key forms (BR-055) ---------------------


def _testing_yaml(tmp_path, gates: str) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "testing.yaml").write_text(
        "test_command: pytest\ngates:\n  attempts: 3\n" + gates + "risk_classes:\n  critical: {}\n",
        encoding="utf-8",
    )


@pytest.mark.spec("RL-09-CT-06")
class TestSt0415ThresholdKeys:
    """RL-09-CT-06: crap-score reads gates.crap-score and the old key gates.crap_score."""

    def test_st_0415_the_key_with_hyphens(self, tmp_path, capsys):
        _testing_yaml(tmp_path, "  crap-score:\n    enabled: true\n    threshold: 8\n")
        assert cs.read_threshold_from_testing_yaml(tmp_path) == 8.0
        assert capsys.readouterr().err == ""

    def test_st_0415_crap_score_reads_the_old_key_crap_score(self, tmp_path, capsys):
        """Scenario: crap-score reads the old key crap_score."""
        _testing_yaml(tmp_path, "  crap_score:\n    enabled: true\n    threshold: 8\n")
        assert cs.read_threshold_from_testing_yaml(tmp_path) == 8.0
        assert capsys.readouterr().err == ""

    def test_st_0415_with_both_keys_the_key_with_hyphens_wins(self, tmp_path, capsys):
        _testing_yaml(
            tmp_path,
            "  crap_score:\n    threshold: 5\n  crap-score:\n    threshold: 8\n",
        )
        assert cs.read_threshold_from_testing_yaml(tmp_path) == 8.0
        assert "gates.crap_score" in capsys.readouterr().err

    def test_st_0415_a_later_entry_lends_no_threshold(self, tmp_path):
        _testing_yaml(
            tmp_path,
            "  crap-score:\n    enabled: true\n  license-check:\n    threshold: 3\n",
        )
        assert cs.read_threshold_from_testing_yaml(tmp_path) is None

    def test_st_0415_the_run_checks_every_function_against_the_old_threshold(self, tmp_path):
        _testing_yaml(tmp_path, "  crap_score:\n    threshold: 2\n")
        (tmp_path / "module.py").write_text(SOURCE, encoding="utf-8")
        reports = tmp_path / "reports"
        code = cs.main(
            ["--source-root", str(tmp_path), "--report-dir", str(reports), "--story-id", "ST-0350"]
        )
        rows = json.loads((reports / "ST-0350.json").read_text(encoding="utf-8"))
        assert code == 1
        assert {r["function"]: r["pass_fail"] for r in rows} == {"greet": "fail", "helper": "pass"}
