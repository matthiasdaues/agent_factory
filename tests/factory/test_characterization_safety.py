"""Characterization tests: branch safety commands survived layout migration.

verify-base and premerge-check must exist, be executable, and load as
Python modules with the expected callable signatures.
"""

from __future__ import annotations

import os
import stat

import pytest

from conftest import SCRIPTS_DIR, load_script

SAFETY_SCRIPTS = ["verify-base", "premerge-check"]


class TestSafetyScriptsExist:
    """Safety scripts exist and are executable."""

    @pytest.mark.parametrize("script", SAFETY_SCRIPTS)
    def test_script_file_exists(self, script: str) -> None:
        path = SCRIPTS_DIR / script
        assert path.exists(), f"{script} not found at {path}"

    @pytest.mark.parametrize("script", SAFETY_SCRIPTS)
    def test_script_is_executable(self, script: str) -> None:
        path = SCRIPTS_DIR / script
        mode = os.stat(path).st_mode
        assert mode & stat.S_IXUSR, f"{script} is not user-executable"


class TestSafetyScriptsLoad:
    """Safety scripts load as Python modules with main()."""

    @pytest.mark.parametrize("script", SAFETY_SCRIPTS)
    def test_script_loads_as_module(self, script: str) -> None:
        mod = load_script(script)
        assert mod is not None

    @pytest.mark.parametrize("script", SAFETY_SCRIPTS)
    def test_script_has_main(self, script: str) -> None:
        mod = load_script(script)
        assert hasattr(mod, "main"), f"{script} has no main() function"
        assert callable(mod.main)


class TestVerifyBaseContract:
    """verify-base accepts a branch-name argument and returns an int."""

    def test_main_accepts_branch_arg(self) -> None:
        vb = load_script("verify-base")
        rc = vb.main(["feature/activity-graph-orchestration"])
        assert isinstance(rc, int)
        assert rc in (0, 1, 2), f"verify-base returned unexpected code {rc}"


class TestPremergeCheckContract:
    """premerge-check produces output that follows the documented format."""

    def test_main_accepts_required_args(self) -> None:
        """main() with no args raises SystemExit(2) — requires target+branch."""
        pm = load_script("premerge-check")
        try:
            pm.main([])
        except SystemExit as exc:
            assert exc.code == 2, f"expected usage error (2), got {exc.code}"
        else:
            pytest.fail("premerge-check main([]) should require arguments")

    def test_has_check_functions(self) -> None:
        pm = load_script("premerge-check")
        assert hasattr(pm, "check_blowout"), "missing check_blowout"
        assert hasattr(pm, "check_out_of_scope"), "missing check_out_of_scope"
        assert hasattr(pm, "extract_story_id"), "missing extract_story_id"
