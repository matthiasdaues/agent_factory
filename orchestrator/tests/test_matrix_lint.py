"""Tests for matrix-lint — the model matrix consistency gate.

Each test writes a model-matrix.conf in tmp_path and runs check_matrix() or
main() directly. Covers the happy path and every defect class (VR-024, ADR-0009).
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
# Model matrix — operator-curated artifact (ADR-0009)

[facts]
copilot.economy  = gpt-5.4-mini
copilot.standard = gpt-5.4
copilot.strong   = claude-opus-4-6

[policy]
class.trivial  = economy
class.standard = standard
class.hard     = strong
phase.planning       = strong
phase.implementation = by-class
on_missing = halt
"""


# --- Happy path ---------------------------------------------------------------


class TestHappyPath:
    def test_valid_matrix_zero_errors(self, tmp_path: Path):
        f = tmp_path / "model-matrix.conf"
        f.write_text(VALID_MATRIX, encoding="utf-8")
        findings = check_matrix(f)
        errors = [r for r in findings if r.severity == "error"]
        assert errors == [], [r.line() for r in errors]

    def test_main_exit_zero(self, tmp_path: Path):
        f = tmp_path / "model-matrix.conf"
        f.write_text(VALID_MATRIX, encoding="utf-8")
        rc = matrix_lint.main(["--matrix", str(f)])
        assert rc == 0

    def test_json_format(self, tmp_path: Path):
        f = tmp_path / "model-matrix.conf"
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
        [policy]
        class.trivial = economy
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
        [policy]
        class.trivial = economy
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(r.code == "MX-TIER" for r in findings)


# --- Policy validation --------------------------------------------------------


class TestPolicyValidation:
    def test_bad_classification_name(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy = gpt-5-mini
        [policy]
        class.extreme = economy
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(
            r.code == "MX-ENUM" and "classification" in r.message for r in findings
        )

    def test_bad_tier_in_policy(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy = gpt-5-mini
        [policy]
        class.trivial = mega
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(r.code == "MX-TIER" and "policy" in r.message for r in findings)

    def test_bad_on_missing(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy = gpt-5-mini
        [policy]
        class.trivial = economy
        on_missing = crash
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(r.code == "MX-ENUM" and "on_missing" in r.message for r in findings)

    def test_unknown_policy_prefix(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy = gpt-5-mini
        [policy]
        class.trivial = economy
        widget.foo = economy
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(r.code == "MX-KEY" and "widget" in r.message for r in findings)


# --- VR-024: dangling tier (core check) ----------------------------------------


class TestDanglingTier:
    def test_tier_unreachable_for_cli(self, tmp_path: Path):
        """Policy references 'strong' but copilot has no strong fact."""
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy  = gpt-5-mini
        copilot.standard = gpt-5.4

        [policy]
        class.trivial  = economy
        class.standard = standard
        class.hard     = strong
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        resolve_errors = [r for r in findings if r.code == "MX-RESOLVE"]
        assert len(resolve_errors) == 1
        assert "strong" in resolve_errors[0].message
        assert "copilot" in resolve_errors[0].message

    def test_dangling_tier_multiple_clis(self, tmp_path: Path):
        """Two CLIs, one missing a tier."""
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy  = gpt-5-mini
        copilot.standard = gpt-5.4
        copilot.strong   = claude-opus-4-6
        claude.economy   = haiku
        claude.standard  = sonnet

        [policy]
        class.trivial  = economy
        class.standard = standard
        class.hard     = strong
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        resolve_errors = [r for r in findings if r.code == "MX-RESOLVE"]
        assert len(resolve_errors) == 1
        assert "claude" in resolve_errors[0].message
        assert "strong" in resolve_errors[0].message


# --- Unreferenced facts -------------------------------------------------------


class TestUnreferencedFacts:
    def test_unused_tier_info(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy  = gpt-5-mini
        copilot.standard = gpt-5.4
        copilot.strong   = claude-opus-4-6

        [policy]
        class.trivial  = economy
        class.standard = economy
        class.hard     = economy
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        unused = [r for r in findings if r.code == "MX-UNUSED"]
        tier_names = {r.message.split("'")[1] for r in unused}
        assert "standard" in tier_names
        assert "strong" in tier_names


# --- Missing classification coverage ------------------------------------------


class TestCoverage:
    def test_missing_class_policy(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy = gpt-5-mini

        [policy]
        class.trivial = economy
        on_missing = halt
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        coverage = [r for r in findings if r.code == "MX-COVERAGE"]
        missing_classes = {r.message.split("'")[1] for r in coverage}
        assert "standard" in missing_classes
        assert "hard" in missing_classes


# --- on_missing default info --------------------------------------------------


class TestOnMissingDefault:
    def test_no_on_missing_info(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text(
            textwrap.dedent("""\
        [facts]
        copilot.economy = gpt-5-mini

        [policy]
        class.trivial = economy
        """),
            encoding="utf-8",
        )
        findings = check_matrix(f)
        assert any(r.code == "MX-DEFAULT" for r in findings)


# --- report-only exit code -----------------------------------------------------


class TestReportOnly:
    def test_report_only_exits_zero(self, tmp_path: Path):
        f = tmp_path / "m.conf"
        f.write_text("[facts]\n[policy]\n", encoding="utf-8")
        rc = matrix_lint.main(["--matrix", str(f), "--report-only"])
        assert rc == 0
