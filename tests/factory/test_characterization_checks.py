"""Characterization tests: verify check scripts survived layout migration.

Each standard check script must exist, be executable, and load as a
Python module via the conftest load_script helper.
"""

from __future__ import annotations

import os
import stat

import pytest
from conftest import SCRIPTS_DIR, load_script

CHECK_SCRIPTS = [
    "backlog-lint",
    "index-lint",
    "concern-lint",
    "spec-lint",
    "arch-lint",
    "matrix-lint",
    "statemachine-lint",
    "scope-lint",
    "link-check",
]


class TestCheckScriptsExist:
    """Every listed check script exists on disk and is executable."""

    @pytest.mark.parametrize("script", CHECK_SCRIPTS)
    def test_script_file_exists(self, script: str) -> None:
        path = SCRIPTS_DIR / script
        assert path.exists(), f"{script} not found at {path}"

    @pytest.mark.parametrize("script", CHECK_SCRIPTS)
    def test_script_is_executable(self, script: str) -> None:
        path = SCRIPTS_DIR / script
        mode = os.stat(path).st_mode
        assert mode & stat.S_IXUSR, f"{script} is not user-executable"


class TestCheckScriptsLoad:
    """Every check script can be imported as a Python module."""

    @pytest.mark.parametrize("script", CHECK_SCRIPTS)
    def test_script_loads_as_module(self, script: str) -> None:
        mod = load_script(script)
        assert mod is not None


class TestCheckScriptsHaveMainEntrypoint:
    """Each check script exposes a main() callable."""

    @pytest.mark.parametrize("script", CHECK_SCRIPTS)
    def test_script_has_main(self, script: str) -> None:
        mod = load_script(script)
        assert hasattr(mod, "main"), f"{script} has no main() function"
        assert callable(mod.main), f"{script}.main is not callable"


class TestCheckScriptsExitCodes:
    """Invoke each check script with no args and verify exit code contract.

    main([]) should return 0 (pass) or 1 (failures found).  Scripts that
    require positional arguments (spec-lint, statemachine-lint) raise
    SystemExit(2) for usage errors — that is also a valid contract response.
    """

    @pytest.mark.parametrize("script", CHECK_SCRIPTS)
    def test_main_returns_valid_exit_code(self, script: str) -> None:
        mod = load_script(script)
        try:
            rc = mod.main([])
        except SystemExit as exc:
            assert exc.code == 2, (
                f"{script} raised SystemExit({exc.code}); expected 0, 1, or 2"
            )
        else:
            assert isinstance(rc, int) and rc >= 0, (
                f"{script} main([]) returned {rc}; expected a non-negative integer"
            )
