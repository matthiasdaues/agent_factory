"""Tests for tests/select_tests.py, the selector of the run-tests hook.

The hook passes the staged paths. The selector prints the test files those
paths affect, prints `tests` when the change needs the whole suite, and
prints nothing when no test is affected.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELECTOR = REPO_ROOT / "tests" / "select_tests.py"


def _write(root: Path, rel: str, text: str = "") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _select(root: Path, *paths: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(SELECTOR), "--root", str(root), *paths],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.split()


def _layout(root: Path) -> None:
    scripts = "packages/factory/scripts"
    _write(root, f"{scripts}/link-check", "#!/usr/bin/env python3\n")
    _write(root, f"{scripts}/dispatch", "from dispatch_lib import glob_match\n")
    _write(root, f"{scripts}/dispatch_lib.py", "def glob_match(): ...\n")
    _write(root, "tests/conftest.py")
    _write(root, "tests/factory/test_link_check.py", 'SCRIPT = SCRIPTS_DIR / "link-check"\n')
    _write(root, "tests/factory/test_link_checker.py", 'NAME = "link-checker"\n')
    _write(root, "tests/factory/test_dispatch.py", 'run("dispatch", "init")\n')
    _write(root, "tests/factory/test_sweep.py", "for p in SOURCE_SCRIPTS_DIR.iterdir():\n")
    _write(
        root, "tests/factory/test_fixture_user.py",
        'FIXTURES = ROOT / "fixtures" / "agent-context"\n',
    )


def test_a_changed_test_file_selects_itself(tmp_path: Path) -> None:
    _layout(tmp_path)
    assert _select(tmp_path, "tests/factory/test_dispatch.py") == ["tests/factory/test_dispatch.py"]


def test_a_changed_script_selects_the_tests_that_name_it_and_the_sweep_tests(
    tmp_path: Path,
) -> None:
    _layout(tmp_path)
    assert _select(tmp_path, "packages/factory/scripts/link-check") == [
        "tests/factory/test_link_check.py",
        "tests/factory/test_sweep.py",
    ]


def test_a_changed_library_selects_the_tests_of_the_scripts_that_import_it(
    tmp_path: Path,
) -> None:
    _layout(tmp_path)
    assert _select(tmp_path, "packages/factory/scripts/dispatch_lib.py") == [
        "tests/factory/test_dispatch.py",
        "tests/factory/test_sweep.py",
    ]


def test_a_changed_fixture_selects_the_tests_that_name_its_folder(tmp_path: Path) -> None:
    _layout(tmp_path)
    _write(tmp_path, "tests/fixtures/agent-context/valid/agent-context.md")
    assert _select(tmp_path, "tests/fixtures/agent-context/valid/agent-context.md") == [
        "tests/factory/test_fixture_user.py",
    ]


def test_a_changed_test_helper_selects_the_tests_that_name_it(tmp_path: Path) -> None:
    _layout(tmp_path)
    _write(tmp_path, "tests/factory/race_helper.py")
    _write(tmp_path, "tests/factory/test_race.py", "import race_helper\n")
    assert _select(tmp_path, "tests/factory/race_helper.py") == ["tests/factory/test_race.py"]


def test_a_changed_conftest_or_dependency_file_selects_the_whole_suite(tmp_path: Path) -> None:
    _layout(tmp_path)
    for path in ("tests/conftest.py", "pyproject.toml", "uv.lock"):
        assert _select(tmp_path, "tests/factory/test_dispatch.py", path) == ["tests"]


def test_a_script_no_test_names_selects_only_the_sweep_tests(tmp_path: Path) -> None:
    _layout(tmp_path)
    _write(tmp_path, "packages/factory/scripts/orphan", "")
    assert _select(tmp_path, "packages/factory/scripts/orphan") == ["tests/factory/test_sweep.py"]


def test_a_path_outside_scripts_and_tests_selects_nothing(tmp_path: Path) -> None:
    _layout(tmp_path)
    assert _select(tmp_path, "docs/README.md") == []


def test_a_deleted_test_file_is_not_selected(tmp_path: Path) -> None:
    _layout(tmp_path)
    assert _select(tmp_path, "tests/factory/test_gone.py") == []


def test_run_with_no_affected_test_passes_without_running_pytest(tmp_path: Path) -> None:
    _layout(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SELECTOR), "--root", str(tmp_path), "--run", "docs/README.md"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    assert result.stdout == "run-tests: no affected tests\n"
