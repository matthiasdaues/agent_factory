"""Tests for directory-merge behaviour: when a project already owns a directory
at a path the factory would normally symlink (e.g. `.github/scripts`), init
merges individual factory entries into it and remove only takes those entries
back out, leaving the project's own files intact.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    script = _ROOT / "factory" / "scripts" / name
    loader = SourceFileLoader(name.replace("-", "_"), str(script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


init_factory = _load("init-factory")
remove_factory = _load("remove-factory")


@pytest.fixture(autouse=True)
def _isolate_external_installers(monkeypatch):
    monkeypatch.setattr(
        init_factory, "provision_usage_runtime", lambda _target, _report: True
    )
    monkeypatch.setattr(
        init_factory,
        "initialize_usage_lifecycle",
        lambda _target, _report, _retention: None,
    )
    monkeypatch.setattr(
        init_factory, "pre_commit_install", lambda _target, _report: None
    )


def _make_project_with_scripts(root: Path) -> None:
    """Create a minimal project that already has .github/scripts/."""
    (root / ".github" / "scripts" / "tests").mkdir(parents=True)
    (root / ".github" / "scripts" / "detect_packages.py").write_text(
        "# project script\n"
    )
    (root / ".github" / "scripts" / "tests" / "test_detect.py").write_text(
        "# project test\n"
    )
    (root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (root / ".github" / "workflows" / "ci.yml").write_text("name: CI\n")
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "app.py").write_text("print('hi')\n")


def _run_init(target: Path) -> int:
    return init_factory.main(
        [
            "--target",
            str(target),
            "--source",
            str(_ROOT),
            "--project-name",
            "Merge Test",
        ]
    )


def _run_remove(target: Path) -> int:
    return remove_factory.main(["--target", str(target)])


class TestMergeIntoExistingDir:
    def test_init_succeeds_when_project_owns_scripts_dir(self, tmp_path):
        _make_project_with_scripts(tmp_path)
        assert _run_init(tmp_path) == 0

    def test_project_files_survive_init(self, tmp_path):
        _make_project_with_scripts(tmp_path)
        assert _run_init(tmp_path) == 0

        assert (tmp_path / ".github/scripts/detect_packages.py").read_text() == (
            "# project script\n"
        )
        assert (tmp_path / ".github/scripts/tests/test_detect.py").read_text() == (
            "# project test\n"
        )
        assert not (tmp_path / ".github/scripts/detect_packages.py").is_symlink()

    def test_factory_entries_are_symlinked_into_existing_dir(self, tmp_path):
        _make_project_with_scripts(tmp_path)
        assert _run_init(tmp_path) == 0

        factory_scripts = tmp_path / "factory" / "scripts"
        github_scripts = tmp_path / ".github" / "scripts"

        for child in factory_scripts.iterdir():
            merged = github_scripts / child.name
            if merged.name in ("detect_packages.py", "tests", "__pycache__"):
                continue
            assert merged.is_symlink(), f"expected symlink: {merged}"

    def test_manifest_records_merged_dirs(self, tmp_path):
        _make_project_with_scripts(tmp_path)
        assert _run_init(tmp_path) == 0

        manifest = json.loads(
            (tmp_path / ".agent-factory/factory-install.json").read_text()
        )
        assert ".github/scripts" in manifest.get("merged_dirs", [])

    def test_gitignore_ignores_children_not_whole_merged_dir(self, tmp_path):
        _make_project_with_scripts(tmp_path)
        assert _run_init(tmp_path) == 0

        gitignore = (tmp_path / ".gitignore").read_text()
        # The whole dir should NOT be ignored (project owns it)
        assert "/.github/scripts\n" not in gitignore
        # But individual factory entries should be ignored
        assert "/.github/scripts/" in gitignore

    def test_remove_deletes_only_factory_symlinks(self, tmp_path):
        _make_project_with_scripts(tmp_path)
        assert _run_init(tmp_path) == 0
        assert _run_remove(tmp_path) == 0

        assert (tmp_path / ".github/scripts/detect_packages.py").read_text() == (
            "# project script\n"
        )
        assert (tmp_path / ".github/scripts/tests/test_detect.py").read_text() == (
            "# project test\n"
        )
        assert (tmp_path / ".github/scripts").is_dir()

    def test_factory_symlinks_gone_after_remove(self, tmp_path):
        _make_project_with_scripts(tmp_path)
        assert _run_init(tmp_path) == 0

        factory_scripts = tmp_path / "factory" / "scripts"
        merged_names = [
            c.name
            for c in factory_scripts.iterdir()
            if c.name not in ("detect_packages.py", "tests", "__pycache__")
        ]

        assert _run_remove(tmp_path) == 0

        for name in merged_names:
            path = tmp_path / ".github" / "scripts" / name
            assert not path.exists(), f"factory entry should be removed: {path}"

    def test_double_init_then_remove_is_clean(self, tmp_path):
        _make_project_with_scripts(tmp_path)
        assert _run_init(tmp_path) == 0
        assert _run_init(tmp_path) == 0
        assert _run_remove(tmp_path) == 0

        assert (tmp_path / ".github/scripts/detect_packages.py").read_text() == (
            "# project script\n"
        )
        github_scripts = tmp_path / ".github" / "scripts"
        remaining = {p.name for p in github_scripts.rglob("*") if not p.is_dir()}
        assert "detect_packages.py" in remaining
        assert "test_detect.py" in remaining


class TestMergeAllDotDirs:
    """Verify that merge works for all three dot-dirs, not just .github."""

    def test_claude_scripts_merge(self, tmp_path):
        (tmp_path / ".claude" / "scripts").mkdir(parents=True)
        (tmp_path / ".claude" / "scripts" / "my-hook.sh").write_text("#!/bin/sh\n")
        assert _run_init(tmp_path) == 0

        assert (tmp_path / ".claude/scripts/my-hook.sh").read_text() == "#!/bin/sh\n"
        assert not (tmp_path / ".claude/scripts/my-hook.sh").is_symlink()

        manifest = json.loads(
            (tmp_path / ".agent-factory/factory-install.json").read_text()
        )
        assert ".claude/scripts" in manifest.get("merged_dirs", [])

    def test_pi_scripts_merge(self, tmp_path):
        (tmp_path / ".pi" / "scripts").mkdir(parents=True)
        (tmp_path / ".pi" / "scripts" / "custom.py").write_text("# custom\n")
        assert _run_init(tmp_path) == 0

        assert (tmp_path / ".pi/scripts/custom.py").read_text() == "# custom\n"
        assert not (tmp_path / ".pi/scripts/custom.py").is_symlink()
