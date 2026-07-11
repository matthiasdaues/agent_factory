"""Tests for matrix-lint — the model.conf consistency gate.

Each test writes a model.conf in tmp_path and runs check_matrix() or
main() directly. Covers the happy path and every defect class
(VR-024, ADR-0020, ADR-0021) for the flat, policy-less [facts] router.
"""

from __future__ import annotations

import textwrap
from pathlib import Path


import importlib.util
import sys
from importlib.machinery import SourceFileLoader

_SCRIPT = Path(__file__).resolve().parents[2] / "factory" / "scripts" / "matrix-lint"
_loader = SourceFileLoader("matrix_lint", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("matrix_lint", _loader)
matrix_lint = importlib.util.module_from_spec(_spec)
sys.modules["matrix_lint"] = matrix_lint
_loader.exec_module(matrix_lint)

check_matrix = matrix_lint.check_matrix
parse_matrix = matrix_lint.parse_matrix


VALID_MATRIX = """\
# Model config — operator-curated artifact (ADR-0020, ADR-0021)

[facts]
copilot.economy  = gpt-5.4-mini
copilot.standard = gpt-5.4
copilot.strong   = claude-opus-4-6
on_missing = halt
"""


# --- Happy path ---------------------------------------------------------------


class TestHappyPath:
    def test_valid_matrix_zero_errors(self, tmp_path: Path):
        f = tmp_path / "model.conf"
        f.write_text(VALID_MATRIX, encoding="utf-8")
        findings = check_matrix(f)
        errors = [r for r in findings if r.severity == "error"]
        assert errors == [], [r.line() for r in errors]

    def test_main_exit_zero(self, tmp_path: Path):
        f = tmp_path / "model.conf"
        f.write_text(VALID_MATRIX, encoding="utf-8")
        rc = matrix_lint.main(["--matrix", str(f)])
        assert rc == 0

    def test_json_format(self, tmp_path: Path):
        f = tmp_path / "model.conf"
        f.write_text(VALID_MATRIX, encoding="utf-8")
        rc = matrix_lint.main(["--matrix", str(f), "--format", "json"])
        assert rc == 0


# --- Missing file -------------------------------------------------------------


class TestMissingFile:
    def test_nonexistent_file(self, tmp_path: Path):
        findings = check_matrix(tmp_path / "nope.conf")
        assert any(r.code == "MX-MISSING" for r in findings)


# --- Parse errors -------------------------------------------------------------


class TestParseErrors:
    def test_unknown_section(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text("[bogus]\nfoo = bar\n", encoding="utf-8")
        findings = check_matrix(f)
        assert any(r.code == "MX-PARSE" for r in findings)

    def test_content_outside_section(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text("foo = bar\n[facts]\n", encoding="utf-8")
        findings = check_matrix(f)
        assert any(r.code == "MX-PARSE" for r in findings)

    def test_malformed_entry(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text("[facts]\nthis is not a key value pair\n", encoding="utf-8")
        findings = check_matrix(f)
        assert any(r.code == "MX-PARSE" for r in findings)


# --- Facts validation ---------------------------------------------------------


class TestFactsValidation:
    def test_bad_facts_key_format(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        notierhere = gpt-5
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(r.code == "MX-KEY" for r in findings)

    def test_invalid_tier_in_facts(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.mega = gpt-99
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(r.code == "MX-TIER" for r in findings)

    def test_bad_on_missing(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy = gpt-5-mini
        on_missing = crash
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(r.code == "MX-ENUM" and "on_missing" in r.message for r in findings)

    def test_no_clis_configured(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(r.code == "MX-EMPTY" for r in findings)


# --- Coverage: a CLI missing a tier -------------------------------------------


class TestCoverage:
    def test_cli_missing_a_tier_warns(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy  = gpt-5-mini
        copilot.standard = gpt-5.4

        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        coverage = [r for r in findings if r.code == "MX-COVERAGE"]
        assert len(coverage) == 1
        assert "strong" in coverage[0].message
        assert "copilot" in coverage[0].message

    def test_multiple_clis_each_report_their_own_gaps(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy  = gpt-5-mini
        copilot.standard = gpt-5.4
        copilot.strong   = claude-opus-4-6
        claude.economy   = haiku
        claude.standard  = sonnet

        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        coverage = [r for r in findings if r.code == "MX-COVERAGE"]
        assert len(coverage) == 1
        assert "claude" in coverage[0].message
        assert "strong" in coverage[0].message


# --- on_missing default info --------------------------------------------------


class TestOnMissingDefault:
    def test_no_on_missing_info(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy = gpt-5-mini
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(r.code == "MX-DEFAULT" for r in findings)


# --- report-only exit code -----------------------------------------------------


class TestReportOnly:
    def test_report_only_exits_zero(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text("[facts]\n", encoding="utf-8")
        rc = matrix_lint.main(["--matrix", str(f), "--report-only"])
        assert rc == 0
