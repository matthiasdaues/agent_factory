"""The runtime requirements match the script lock of usage-capture (BUG-0144).

init-factory installs the usage runtime from usage-runtime-requirements.txt
with --require-hashes. A hand edit that changes a version but keeps the old
hashes makes every install fail, and capture stops without a message. The
file must therefore be exactly what `uv export` makes from the lock.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest

from conftest import REPO_ROOT

SCRIPT = REPO_ROOT / "packages" / "factory" / "scripts" / "usage-capture"
REQUIREMENTS = REPO_ROOT / "packages" / "factory" / "config" / "usage-runtime-requirements.txt"


def _body(text: str) -> list[str]:
    """Drop the comment header, which names the installed paths."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if not line.startswith("#"))
    return lines[start:]


def test_requirements_are_the_export_of_the_script_lock():
    if shutil.which("uv") is None:
        pytest.skip("uv is required to export the lock")
    exported = subprocess.run(
        [
            "uv", "export", "--script", str(SCRIPT), "--frozen", "--quiet",
            "--format", "requirements.txt", "--no-python-downloads",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    ).stdout

    assert _body(REQUIREMENTS.read_text(encoding="utf-8")) == _body(exported), (
        "usage-runtime-requirements.txt differs from the lock; change versions with"
        " `uv lock --script packages/factory/scripts/usage-capture --upgrade-package`"
        " and export again"
    )
