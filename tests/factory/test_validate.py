"""Subprocess tests for packages/factory/scripts/validate.

The script starts through its first line (`uv run --script`), so each test
executes the file itself against Markdown files in a temporary project.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent.parent
    / "packages"
    / "factory"
    / "scripts"
    / "validate"
)


def _run(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), *args],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.spec("CG-13-LN-03")
def test_clean_markdown_file_exits_zero(tmp_path: Path) -> None:
    doc = tmp_path / "clean.md"
    doc.write_text("# Title\n\nPlain prose.\n", encoding="utf-8")
    result = _run(tmp_path, str(doc))
    assert result.returncode == 0
    assert result.stderr == ""


@pytest.mark.spec("CG-13-LN-03")
def test_at_reference_line_is_reported_with_file_and_line(tmp_path: Path) -> None:
    doc = tmp_path / "bad.md"
    doc.write_text("Prose.\n  # @src/app.py::run\n", encoding="utf-8")
    result = _run(tmp_path, str(doc))
    assert result.returncode == 1
    assert (
        f"{doc}:2: @-reference syntax is scoped to .feature files only"
        in result.stderr
    )


@pytest.mark.spec("CG-13-LN-03")
def test_directory_is_expanded_recursively_and_non_markdown_ignored(
    tmp_path: Path,
) -> None:
    nested = tmp_path / "docs" / "deep"
    nested.mkdir(parents=True)
    (nested / "bad.md").write_text("# @ref\n", encoding="utf-8")
    (tmp_path / "docs" / "notes.txt").write_text("# @ref\n", encoding="utf-8")
    result = _run(tmp_path, str(tmp_path / "docs"))
    assert result.returncode == 1
    assert "bad.md:1" in result.stderr
    assert "notes.txt" not in result.stderr


@pytest.mark.spec("CG-13-LN-03")
def test_non_markdown_file_and_missing_path_are_ignored(tmp_path: Path) -> None:
    txt = tmp_path / "a.txt"
    txt.write_text("# @ref\n", encoding="utf-8")
    result = _run(tmp_path, str(txt), str(tmp_path / "missing.md"))
    assert result.returncode == 0


@pytest.mark.spec("CG-13-LN-03")
def test_no_paths_exits_zero(tmp_path: Path) -> None:
    assert _run(tmp_path).returncode == 0


@pytest.mark.spec("CG-13-LN-03")
def test_help_exits_zero(tmp_path: Path) -> None:
    result = _run(tmp_path, "--help")
    assert result.returncode == 0
    assert "forbidden @-reference" in result.stdout
