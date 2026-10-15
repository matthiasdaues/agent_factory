"""Regression tests for conjecture-lint and mermaid-lint (BUG-0049, BUG-0050, BUG-0051)."""

from __future__ import annotations

import stat

from conftest import SOURCE_SCRIPTS_DIR, load_script

cl = load_script("conjecture-lint")
ml = load_script("mermaid-lint")


class TestConjectureMarkersMatchWholeWords:
    """BUG-0050: a marker inside another word must not count as a marker."""

    def test_marker_inside_other_word_is_not_a_gap(self):
        claim = "The Arduino platform supports the Singapore protocol"
        assert cl.lint_claim(claim) == []

    def test_no_op_is_not_a_gap(self):
        claim = "The adapter supports a no-op shutdown hook"
        assert cl.lint_claim(claim) == []

    def test_no_ff_flag_is_not_a_gap(self):
        claim = "The merge script supports the --no-ff flag"
        assert cl.lint_claim(claim) == []

    def test_not_yet_is_not_a_gap(self):
        claim = "The queue handles not-yet-acknowledged messages"
        assert cl.lint_claim(claim) == []

    def test_must_not_is_a_gap(self):
        claim = "The adapter supports batch writes and must-not retry them"
        findings = cl.lint_claim(claim)
        assert any("near 'must-not'" in finding for finding in findings)

    def test_real_capability_and_gap_bundle_is_still_flagged(self):
        claim = "The adapter supports batch writes and no retry path exists"
        findings = cl.lint_claim(claim)
        assert any("bundles a capability" in finding for finding in findings)


class TestScriptsAreExecutable:
    """BUG-0049: conjecture-lint was committed without the executable bit."""

    def test_conjecture_lint_has_executable_bit(self):
        mode = (SOURCE_SCRIPTS_DIR / "conjecture-lint").stat().st_mode
        assert mode & stat.S_IXUSR

    def test_every_script_with_shebang_is_executable(self):
        offenders = [
            path.name
            for path in sorted(SOURCE_SCRIPTS_DIR.iterdir())
            if path.is_file()
            and path.read_bytes()[:2] == b"#!"
            and not path.stat().st_mode & stat.S_IXUSR
        ]
        assert offenders == []


class TestMermaidFenceForms:
    """BUG-0051: mermaid-lint must check tilde fences and indented fences."""

    def test_tilde_fence_with_raw_semicolon_is_reported(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text(
            "~~~mermaid\nflowchart LR\n  A-->B; B-->C\n~~~\n", encoding="utf-8"
        )
        errors = ml.check(doc)
        assert len(errors) == 1
        assert "MERMAID-SEMICOLON" in errors[0]

    def test_indented_fence_with_raw_semicolon_is_reported(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text(
            "- step one\n\n  ```mermaid\n  flowchart LR\n    A-->B; B-->C\n  ```\n",
            encoding="utf-8",
        )
        errors = ml.check(doc)
        assert len(errors) == 1
        assert "MERMAID-SEMICOLON" in errors[0]

    def test_tilde_fence_is_closed_only_by_tildes(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text(
            "~~~mermaid\n```\nA-->B; B-->C\n~~~\n", encoding="utf-8"
        )
        errors = ml.check(doc)
        assert len(errors) == 1
