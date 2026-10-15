"""Regression tests for conjecture-lint and mermaid-lint (BUG-0049, BUG-0050, BUG-0051)."""

from __future__ import annotations

import stat

from conftest import SOURCE_SCRIPTS_DIR


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
