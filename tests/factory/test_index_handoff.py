"""Regression tests for index-lint (BUG-0057)."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import load_script

il = load_script("index-lint")


# ── index-lint: every skill reaches INDEX.yaml (BUG-0057) ────────────────


def _factory(tmp_path: Path) -> dict[str, Path]:
    dirs = {
        name: tmp_path / name for name in ("agents", "skills", "playbooks", "rulebooks")
    }
    for path in dirs.values():
        path.mkdir()
    return dirs


def _skill(skills_dir: Path, folder: str, text: str, encoding: str = "utf-8") -> None:
    (skills_dir / folder).mkdir()
    (skills_dir / folder / "SKILL.md").write_text(text, encoding=encoding)


def _run_index_lint(dirs: dict[str, Path], out: Path) -> int:
    return il.main(
        [
            "--agents-dir", str(dirs["agents"]),
            "--skills-dir", str(dirs["skills"]),
            "--playbooks-dir", str(dirs["playbooks"]),
            "--rulebooks-dir", str(dirs["rulebooks"]),
            "--out", str(out),
        ]
    )  # fmt: skip


def test_index_lint_keeps_skill_with_byte_order_mark(tmp_path: Path) -> None:
    dirs = _factory(tmp_path)
    _skill(
        dirs["skills"],
        "bom-skill",
        "---\nname: bom-skill\ncategory: utility\ndescription: A skill.\n---\n",
        encoding="utf-8-sig",
    )
    out = tmp_path / "INDEX.yaml"

    assert _run_index_lint(dirs, out) == 0
    assert "name: bom-skill" in out.read_text(encoding="utf-8")


def test_index_lint_warns_on_skill_without_name(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dirs = _factory(tmp_path)
    _skill(dirs["skills"], "nameless", "---\ncategory: utility\n---\n")

    _run_index_lint(dirs, tmp_path / "INDEX.yaml")

    err = capsys.readouterr().err
    assert "nameless" in err
    assert "no 'name'" in err


def test_index_lint_rejects_duplicate_skill_names(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dirs = _factory(tmp_path)
    text = "---\nname: twin\ncategory: utility\ndescription: A skill.\n---\n"
    _skill(dirs["skills"], "twin-a", text)
    _skill(dirs["skills"], "twin-b", text)
    out = tmp_path / "INDEX.yaml"

    assert _run_index_lint(dirs, out) == 1
    assert "duplicate skill name 'twin'" in capsys.readouterr().err
    assert not out.exists()

