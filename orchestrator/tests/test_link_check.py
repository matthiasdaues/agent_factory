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


def test_rejects_broken_cross_file_anchor(tmp_path: Path) -> None:
    (tmp_path / "target.md").write_text("# A useful heading\n")
    source = tmp_path / "source.md"
    source.write_text("[target](target.md#no-such-heading)\n")

    result = run(source)

    assert result.returncode == 1
    assert "broken anchor 'target.md#no-such-heading'" in result.stderr


def test_rejects_broken_same_document_anchor(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("# Present\n\n[jump](#absent)\n")

    result = run(source)

    assert result.returncode == 1
    assert "broken anchor '#absent'" in result.stderr


def test_accepts_same_document_anchor(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("# Present\n\n[jump](#present)\n")

    assert run(source).returncode == 0


def test_accepts_em_dash_heading_with_doubled_hyphen(tmp_path: Path) -> None:
    (tmp_path / "target.md").write_text("## Step 3 — Write the review report\n")
    source = tmp_path / "source.md"
    source.write_text("[step](target.md#step-3--write-the-review-report)\n")

    assert run(source).returncode == 0


def test_keeps_inline_code_and_underscores_in_heading_slug(tmp_path: Path) -> None:
    (tmp_path / "target.md").write_text("### `run_agent` Envelope Error\n")
    source = tmp_path / "source.md"
    source.write_text("[e](target.md#run_agent-envelope-error)\n")

    assert run(source).returncode == 0


def test_suffixes_duplicate_headings(tmp_path: Path) -> None:
    (tmp_path / "target.md").write_text("## Notes\n\n## Notes\n")
    source = tmp_path / "source.md"
    source.write_text("[first](target.md#notes)\n\n[second](target.md#notes-1)\n")

    assert run(source).returncode == 0


def test_ignores_links_inside_fenced_code(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("```markdown\n[example](missing.md#nowhere)\n```\n")

    assert run(source).returncode == 0


def test_ignores_links_inside_inline_code(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("Right: `[T-1](missing.md#t-1)`.\n")

    assert run(source).returncode == 0


def test_headings_inside_fenced_code_are_not_anchors(tmp_path: Path) -> None:
    (tmp_path / "target.md").write_text("# Real\n\n```markdown\n## Fake heading\n```\n")
    source = tmp_path / "source.md"
    source.write_text("[f](target.md#fake-heading)\n")

    assert run(source).returncode == 1


def test_ignores_fragment_on_non_markdown_target(tmp_path: Path) -> None:
    (tmp_path / "diagram.svg").write_text("<svg/>\n")
    source = tmp_path / "source.md"
    source.write_text("[d](diagram.svg#layer1)\n")

    assert run(source).returncode == 0
