"""Contract tests: crap-score reads both key forms of its entry (BR-055, BR-128)."""

from __future__ import annotations

import json
import stat
import subprocess
from decimal import Decimal

import pytest
from conftest import load_script

cs = load_script("crap-score")

ENTRY = (
    "    enabled: true\n"
    "    threshold: {threshold}\n"
    "    timeout_minutes: 10\n"
    "    measures:\n"
    "      - name: python\n"
    "        files: \"src/*\"\n"
    "        command: \"scripts/crap-measure-stub\"\n"
)


def _testing_yaml(tmp_path, gates: str) -> None:
    docs = tmp_path / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "testing.yaml").write_text(
        "test_command: pytest\ngates:\n  attempts: 3\n" + gates + "risk_classes:\n  critical: {}\n",
        encoding="utf-8",
    )


def _entry(key: str, threshold: int) -> str:
    return f"  {key}:\n" + ENTRY.format(threshold=threshold)


@pytest.mark.spec("CG-04-CT-05")
class TestCg04ThresholdKeys:
    """CG-04-CT-05: crap-score reads gates.crap-score and the old key crap_score."""

    def test_cg_04_the_key_with_hyphens(self, tmp_path, capsys):
        _testing_yaml(tmp_path, _entry("crap-score", 8))
        assert cs.read_settings(tmp_path).threshold == Decimal(8)
        assert capsys.readouterr().err == ""

    def test_cg_04_crap_score_reads_the_old_key_crap_score(self, tmp_path, capsys):
        """Scenario: crap-score reads the old key crap_score."""
        _testing_yaml(tmp_path, _entry("crap_score", 8))
        assert cs.read_settings(tmp_path).threshold == Decimal(8)
        assert capsys.readouterr().err == ""

    def test_cg_04_with_both_keys_the_key_with_hyphens_wins(self, tmp_path, capsys):
        _testing_yaml(tmp_path, _entry("crap_score", 5) + _entry("crap-score", 8))
        assert cs.read_settings(tmp_path).threshold == Decimal(8)
        assert "gates.crap_score" in capsys.readouterr().err

    def test_cg_04_a_later_entry_lends_no_threshold(self, tmp_path):
        _testing_yaml(
            tmp_path,
            "  crap-score:\n    enabled: true\n  license-check:\n    threshold: 3\n",
        )
        with pytest.raises(cs.GateError, match="has no threshold"):
            cs.read_settings(tmp_path)

    def test_cg_04_the_run_judges_the_changed_functions_against_the_old_threshold(
        self, tmp_path, monkeypatch
    ):
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
        repo = tmp_path / "repo"
        repo.mkdir()
        monkeypatch.chdir(repo)

        def git(*args):
            subprocess.run(["git", *args], check=True, capture_output=True)

        git("init", "-q", "-b", "main")
        git("config", "user.email", "fixture@example.com")
        git("config", "user.name", "Fixture")
        git("config", "commit.gpgsign", "false")
        _testing_yaml(repo, _entry("crap_score", 2))
        stub = repo / "scripts" / "crap-measure-stub"
        stub.parent.mkdir()
        stub.write_text('#!/bin/sh\ncp "$PLANTED_ROWS" "$GATE_OUTPUT"\n')
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        (repo / "src").mkdir()
        (repo / "src" / "module").write_text("".join(f"line {n}\n" for n in range(1, 11)))
        git("add", "-A")
        git("commit", "-q", "-m", "init")
        git("checkout", "-q", "-b", "feature/login")
        git("checkout", "-q", "-b", "story/ST-0350")
        (repo / "src" / "module").write_text(
            "".join(("changed\n" if n == 2 else f"line {n}\n") for n in range(1, 11))
        )
        git("commit", "-q", "-am", "change greet")
        rows = [
            {"file": "src/module", "function": "Greeter.greet", "start_line": 1,
             "end_line": 5, "complexity": 2, "coverage_pct": 50},
            {"file": "src/module", "function": "helper", "start_line": 7,
             "end_line": 10, "complexity": 3, "coverage_pct": 0},
        ]
        planted = tmp_path / "planted.json"
        planted.write_text(json.dumps(rows))
        monkeypatch.setenv("PLANTED_ROWS", str(planted))
        monkeypatch.delenv("STORY_ID", raising=False)

        reports = tmp_path / "reports"
        code = cs.main(["--base", "feature/login", "--report-dir", str(reports)])
        judged = json.loads((reports / "ST-0350.json").read_text(encoding="utf-8"))
        assert code == 1
        assert {r["function"]: r["pass_fail"] for r in judged} == {"Greeter.greet": "fail"}


ENV_STUB = """\
#!/bin/sh
printf '%s' "${GATE_FILES-unset}" > "$ENV_LOG.files"
printf '%s' "${GATE_EXCLUDE-unset}" > "$ENV_LOG.exclude"
echo "[]" > "$GATE_OUTPUT"
"""


@pytest.mark.spec("CG-04-CT-03")
@pytest.mark.parametrize(
    ("exclude", "expected"),
    [(("**/db/**", "scripts/tools/helper"), "**/db/**\nscripts/tools/helper"), ((), "")],
    ids=["two patterns", "no pattern"],
)
def test_cg_04_crap_score_hands_files_and_exclude_to_the_measuring_command(
    tmp_path, monkeypatch, exclude, expected
):
    """IMPL-0090, DEC-65: GATE_FILES holds files, GATE_EXCLUDE one exclude pattern per line."""
    stub = tmp_path / "env-stub"
    stub.write_text(ENV_STUB)
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    log = tmp_path / "env"
    monkeypatch.setenv("ENV_LOG", str(log))
    measure = cs.Measure("python", "src/**", str(stub), exclude)

    assert cs.run_measure(measure, tmp_path, cs.Clock(1)) == []

    assert (tmp_path / "env.files").read_text() == "src/**"
    assert (tmp_path / "env.exclude").read_text() == expected


@pytest.mark.spec("CG-04-CT-05")
@pytest.mark.parametrize("field", ["files", "exclude"])
def test_cg_04_a_pattern_with_a_line_break_cannot_measure(tmp_path, field):
    """DEC-65: GATE_FILES and GATE_EXCLUDE hold one pattern per line, so no pattern holds a line break."""
    files = '"src/**\\nscripts/*"' if field == "files" else '"src/**"'
    exclude = '\n        exclude:\n          - "a/**\\nb/**"' if field == "exclude" else ""
    _testing_yaml(
        tmp_path,
        "  crap-score:\n    enabled: true\n    threshold: 8\n    timeout_minutes: 10\n"
        "    measures:\n      - name: python\n"
        f"        files: {files}{exclude}\n        command: \"true\"\n",
    )
    with pytest.raises(cs.GateError, match=rf"measure python .* {field} .*line break"):
        cs.read_settings(tmp_path)
