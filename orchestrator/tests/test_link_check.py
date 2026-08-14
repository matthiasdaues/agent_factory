from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "factory" / "scripts" / "link-check"


def run(*files: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), *(str(path) for path in files)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_accepts_existing_relative_path_and_anchor(tmp_path: Path) -> None:
    target = tmp_path / "target.md"
    target.write_text("# A useful heading\n")
    source = tmp_path / "source.md"
    source.write_text("[target](target.md#a-useful-heading)\n")

    result = run(source)

    assert result.returncode == 0


def test_rejects_missing_image(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("![diagram](missing.png)\n")

    result = run(source)

    assert result.returncode == 1


def test_rejects_missing_file(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("[missing](missing.md)\n")

    result = run(source)

    assert result.returncode == 1
    assert "broken link 'missing.md'" in result.stderr


def test_ignores_remote_links(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("[remote](https://example.com/path)\n")

    assert run(source).returncode == 0
