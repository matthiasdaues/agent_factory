"""Contract tests for init-factory setup script.

Tests focus on the pure/isolable functions that can run without a full
init sequence — filesystem steps, test regime detection, gitignore
assembly, manifest round-trip.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from conftest import load_script

inf = load_script("init-factory")


class TestEnsureTargetDir:
    def test_creates_missing_directory(self, tmp_path):
        target = tmp_path / "new_project"
        report: list[str] = []
        inf.ensure_target_dir(target, {}, report)
        assert target.is_dir()
        assert any("created" in r for r in report)

    def test_existing_directory_is_noop(self, tmp_path):
        report: list[str] = []
        inf.ensure_target_dir(tmp_path, {}, report)
        assert any("exists" in r for r in report)


class TestEnsureGit:
    def test_initializes_new_repo(self, tmp_path):
        install = {"remove_paths": []}
        report: list[str] = []
        inf.ensure_git(tmp_path, install, report)
        assert (tmp_path / ".git").exists()
        assert install["git_initialized_by_us"] is True

    def test_existing_repo_untouched(self, tmp_path):
        subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
        install = {"remove_paths": []}
        report: list[str] = []
        inf.ensure_git(tmp_path, install, report)
        assert install.get("git_initialized_by_us") is False
        assert any("already a repo" in r for r in report)


class TestCopyFactory:
    def test_copies_source_to_target(self, tmp_path):
        source = tmp_path / "source_factory"
        source.mkdir()
        (source / "scripts").mkdir()
        (source / "scripts" / "lint").write_text("#!/bin/bash\n")
        target = tmp_path / "project"
        target.mkdir()
        install = {"remove_paths": []}
        report: list[str] = []
        inf.copy_factory(source, target, install, report)
        assert (target / "factory" / "scripts" / "lint").exists()
        assert "factory" in install["remove_paths"]

    def test_existing_factory_skipped(self, tmp_path):
        source = tmp_path / "source_factory"
        source.mkdir()
        target = tmp_path / "project"
        (target / "factory").mkdir(parents=True)
        install = {"remove_paths": []}
        report: list[str] = []
        inf.copy_factory(source, target, install, report)
        assert any("already present" in r for r in report)


class TestEnsureDotDirs:
    def test_creates_missing_dirs(self, tmp_path):
        install = {"dir_existed": {}, "remove_paths": []}
        report: list[str] = []
        inf.ensure_dot_dirs(tmp_path, install, report)
        for name in inf.DOT_DIRS:
            assert (tmp_path / name).is_dir()
            assert install["dir_existed"][name] is False

    def test_existing_dirs_preserved(self, tmp_path):
        for name in inf.DOT_DIRS:
            (tmp_path / name).mkdir()
        install = {"dir_existed": {}, "remove_paths": []}
        report: list[str] = []
        inf.ensure_dot_dirs(tmp_path, install, report)
        for name in inf.DOT_DIRS:
            assert install["dir_existed"][name] is True


class TestEnsureSymlink:
    def test_creates_new_symlink(self, tmp_path):
        dest = tmp_path / "source_file"
        dest.write_text("content")
        link = tmp_path / "subdir" / "link"
        link.parent.mkdir()
        report: list[str] = []
        created = inf.ensure_symlink(link, dest, report)
        assert created is True
        assert link.is_symlink()
        assert link.read_text() == "content"

    def test_existing_correct_symlink_skips(self, tmp_path):
        dest = tmp_path / "source_file"
        dest.write_text("content")
        link = tmp_path / "link"
        link.symlink_to(dest)
        report: list[str] = []
        created = inf.ensure_symlink(link, dest, report)
        assert created is False


class TestScanTestEntrypoints:
    def test_detects_makefile_test_target(self, tmp_path):
        (tmp_path / "Makefile").write_text("test:\n\tpytest\n")
        result = inf._scan_test_entrypoints(tmp_path)
        assert any("make test" in cmd for _, cmd in result)

    def test_detects_package_json_test_script(self, tmp_path):
        (tmp_path / "package.json").write_text(
            json.dumps({"scripts": {"test": "jest"}})
        )
        result = inf._scan_test_entrypoints(tmp_path)
        assert any("npm test" in cmd for _, cmd in result)

    def test_detects_pytest_in_pyproject(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n")
        result = inf._scan_test_entrypoints(tmp_path)
        assert any("pytest" in cmd for _, cmd in result)

    def test_detects_tox(self, tmp_path):
        (tmp_path / "tox.ini").write_text("[tox]\n")
        result = inf._scan_test_entrypoints(tmp_path)
        assert any("tox" in cmd for _, cmd in result)

    def test_detects_nox(self, tmp_path):
        (tmp_path / "noxfile.py").write_text("import nox\n")
        result = inf._scan_test_entrypoints(tmp_path)
        assert any("nox" in cmd for _, cmd in result)

    def test_detects_justfile(self, tmp_path):
        (tmp_path / "Justfile").write_text("test:\n  pytest\n")
        result = inf._scan_test_entrypoints(tmp_path)
        assert any("just test" in cmd for _, cmd in result)

    def test_no_entrypoints(self, tmp_path):
        assert inf._scan_test_entrypoints(tmp_path) == []


class TestWriteTestingYaml:
    def test_writes_agent_context(self, tmp_path):
        inf._write_testing_yaml(tmp_path, "pytest")
        path = tmp_path / "docs" / "agent-context" / "testing.yaml"
        assert path.exists()
        content = path.read_text()
        assert 'test_command: "pytest"' in content

    def test_writes_to_charter_when_charter_exists(self, tmp_path):
        charter = tmp_path / "docs" / "charter"
        charter.mkdir(parents=True)
        (charter / "testing.yaml").write_text("test_command: old\n")
        inf._write_testing_yaml(tmp_path, "pytest")
        content = (charter / "testing.yaml").read_text()
        assert 'test_command: "pytest"' in content


class TestDetectTestRegime:
    def test_single_entrypoint_writes(self, tmp_path):
        (tmp_path / "Makefile").write_text("test:\n\tpytest\n")
        report: list[str] = []
        inf.detect_test_regime(tmp_path, report)
        path = tmp_path / "docs" / "agent-context" / "testing.yaml"
        assert path.exists()
        assert "make test" in path.read_text()

    def test_existing_testing_yaml_skipped(self, tmp_path):
        charter = tmp_path / "docs" / "charter"
        charter.mkdir(parents=True)
        (charter / "testing.yaml").write_text("test_command: custom\n")
        (tmp_path / "Makefile").write_text("test:\n\tpytest\n")
        report: list[str] = []
        inf.detect_test_regime(tmp_path, report)
        assert "custom" in (charter / "testing.yaml").read_text()

    def test_no_entrypoints_reports_gap(self, tmp_path):
        report: list[str] = []
        inf.detect_test_regime(tmp_path, report)
        assert not (tmp_path / "docs" / "charter" / "testing.yaml").exists()
        assert any("gap" in r for r in report)


class TestWriteGitignoreBlock:
    def test_creates_new_gitignore(self, tmp_path):
        install = {
            "remove_paths": [],
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
        }
        report: list[str] = []
        inf.write_gitignore_block(tmp_path, install, report)
        gi = (tmp_path / ".gitignore").read_text()
        assert inf.GITIGNORE_BEGIN in gi
        assert inf.GITIGNORE_END in gi
        assert "/factory/" in gi

    def test_appends_to_existing_gitignore(self, tmp_path):
        (tmp_path / ".gitignore").write_text("*.pyc\n")
        install = {
            "remove_paths": [],
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
        }
        report: list[str] = []
        inf.write_gitignore_block(tmp_path, install, report)
        gi = (tmp_path / ".gitignore").read_text()
        assert "*.pyc" in gi
        assert inf.GITIGNORE_BEGIN in gi

    def test_refreshes_existing_block(self, tmp_path):
        existing = f"*.pyc\n\n{inf.GITIGNORE_BEGIN}\n/factory/\n{inf.GITIGNORE_END}\n"
        (tmp_path / ".gitignore").write_text(existing)
        install = {
            "remove_paths": [],
            "ignore_model_conf": True,
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
        }
        report: list[str] = []
        inf.write_gitignore_block(tmp_path, install, report)
        gi = (tmp_path / ".gitignore").read_text()
        assert "/config/model.conf" in gi
        assert gi.count(inf.GITIGNORE_BEGIN) == 1


class TestEnsureProjectIdentity:
    def test_creates_identity(self, tmp_path):
        install = {"remove_paths": []}
        report: list[str] = []
        inf.ensure_project_identity(tmp_path, "Test Project", install, report)
        path = tmp_path / inf.PROJECT_IDENTITY
        assert path.exists()
        identity = json.loads(path.read_text())
        assert identity["project_name"] == "Test Project"
        assert len(identity["project_id"]) == 36

    def test_existing_identity_preserved(self, tmp_path):
        import uuid as _uuid

        path = tmp_path / inf.PROJECT_IDENTITY
        path.parent.mkdir(parents=True)
        original = {"project_id": str(_uuid.uuid4()), "project_name": "Original"}
        path.write_text(json.dumps(original))
        install = {"remove_paths": []}
        report: list[str] = []
        inf.ensure_project_identity(tmp_path, "New Name", install, report)
        assert json.loads(path.read_text())["project_name"] == "Original"

    def test_empty_name_raises(self, tmp_path):
        install = {"remove_paths": []}
        with pytest.raises(inf.Collision):
            inf.ensure_project_identity(tmp_path, "", install, [])


class TestWriteManifest:
    def test_writes_valid_json(self, tmp_path):
        install = {
            "remove_paths": ["factory", ".claude"],
            "merged_dirs": [],
            "orientation": {},
            "copilot_generated_agents": set(),
            "codex_generated_agents": set(),
            "codex_hook_handlers": [],
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
        }
        report: list[str] = []
        inf.write_manifest(tmp_path, install, report)
        path = tmp_path / inf.MANIFEST_PATH
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["version"] == 1
        assert "factory" in data["remove_paths"]


class TestLoadPriorManifest:
    def test_loads_existing_manifest(self, tmp_path):
        manifest_dir = tmp_path / ".agent-factory"
        manifest_dir.mkdir()
        (manifest_dir / "factory-install.json").write_text(
            json.dumps(
                {
                    "remove_paths": ["factory", ".claude"],
                    "merged_dirs": [],
                    "orientation": {},
                    "precommit": {"path": ".pre-commit-config.yaml", "existed": True},
                    "git_initialized_by_us": True,
                }
            )
        )
        install = {
            "remove_paths": [],
            "merged_dirs": [],
            "orientation": {},
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
            "copilot_generated_agents": set(),
            "codex_generated_agents": set(),
            "codex_hook_handlers": [],
        }
        report: list[str] = []
        inf.load_prior_manifest(tmp_path, install, report)
        assert "factory" in install["remove_paths"]
        assert install["git_initialized_by_us"] is True

    def test_missing_manifest_is_noop(self, tmp_path):
        install = {"remove_paths": []}
        report: list[str] = []
        inf.load_prior_manifest(tmp_path, install, report)
        assert install["remove_paths"] == []


class TestHandlePrecommit:
    """Integration: pre-commit config creation and merge splice."""

    def _make_template(self, target: Path):
        """Create the factory template that handle_precommit reads."""
        config_dir = target / "factory" / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "pre-commit-config.yaml").write_text(
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: agent_factory_hook-test\n"
            "        name: test\n"
            "        entry: echo ok\n"
            "        language: system\n"
        )
        scripts_dir = target / "factory" / "scripts"
        scripts_dir.mkdir(parents=True)

    def test_creates_from_scratch(self, tmp_path):
        self._make_template(tmp_path)
        install = {"remove_paths": []}
        report: list[str] = []
        inf.handle_precommit(tmp_path, install, report)
        dest = tmp_path / ".pre-commit-config.yaml"
        assert dest.exists()
        content = dest.read_text()
        assert "agent_factory_hook-test" in content
        assert install["precommit"]["existed"] is False

    def test_existing_untouched_gets_splice(self, tmp_path):
        self._make_template(tmp_path)
        # Create the merge-precommit-config script (needed for splicing)
        merge_script = tmp_path / "factory" / "scripts" / "merge-precommit-config"
        merge_script.write_text(
            "#!/usr/bin/env python3\n"
            "import sys, argparse\n"
            "p = argparse.ArgumentParser()\n"
            "p.add_argument('--target')\n"
            "p.add_argument('--template')\n"
            "p.add_argument('--update', action='store_true')\n"
            "args = p.parse_args()\n"
            "from pathlib import Path\n"
            "t = Path(args.target)\n"
            "existing = t.read_text()\n"
            "tpl = Path(args.template).read_text()\n"
            "t.write_text(existing + '\\n' + tpl)\n"
        )
        merge_script.chmod(0o755)
        (tmp_path / ".pre-commit-config.yaml").write_text(
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: my-project-hook\n"
            "        name: my hook\n"
            "        entry: echo mine\n"
            "        language: system\n"
        )
        install = {"remove_paths": []}
        report: list[str] = []
        inf.handle_precommit(tmp_path, install, report)
        content = (tmp_path / ".pre-commit-config.yaml").read_text()
        assert "my-project-hook" in content
        assert install["precommit"]["existed"] is True


class TestSymlinkFactoryContent:
    """Integration: symlinks factory content into dot-dirs."""

    def test_symlinks_created(self, tmp_path):
        factory = tmp_path / "factory"
        for name in inf.FACTORY_CONTENT:
            path = factory / name
            if name == "INDEX.yaml":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("index content")
            else:
                path.mkdir(parents=True)
                (path / "dummy").write_text("content")
        # Also need factory/config/AGENTS.md for orientation
        config = factory / "config"
        config.mkdir(parents=True, exist_ok=True)
        (config / "AGENTS.md").write_text("# Orientation\n")

        for dot_dir in inf.DOT_DIRS:
            (tmp_path / dot_dir).mkdir()

        install = {
            "remove_paths": [],
            "merged_dirs": [],
            "orientation": {},
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
            "_target": tmp_path,
        }
        report: list[str] = []
        inf.symlink_factory_content(tmp_path, install, report)

        for dot_dir in inf.DOT_DIRS:
            for name in inf.FACTORY_CONTENT:
                if dot_dir == ".github" and name == "agents":
                    continue
                if dot_dir == ".codex" and name in ("agents", "skills"):
                    continue
                link = tmp_path / dot_dir / name
                assert link.is_symlink(), f"{link} should be a symlink"

    def test_symlinks_are_idempotent(self, tmp_path):
        factory = tmp_path / "factory"
        for name in inf.FACTORY_CONTENT:
            path = factory / name
            if name == "INDEX.yaml":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("index content")
            else:
                path.mkdir(parents=True)
                (path / "dummy").write_text("content")
        config = factory / "config"
        config.mkdir(parents=True, exist_ok=True)
        (config / "AGENTS.md").write_text("# Orientation\n")

        for dot_dir in inf.DOT_DIRS:
            (tmp_path / dot_dir).mkdir()

        install = {
            "remove_paths": [],
            "merged_dirs": [],
            "orientation": {},
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
            "_target": tmp_path,
        }
        report1: list[str] = []
        inf.symlink_factory_content(tmp_path, install, report1)
        report2: list[str] = []
        inf.symlink_factory_content(tmp_path, install, report2)
        assert not any("created" in r.lower() for r in report2)


class TestManifestRoundTrip:
    """Integration: write manifest, reload it, verify state preserved."""

    def test_write_then_load_preserves_state(self, tmp_path):
        install = {
            "remove_paths": ["factory", ".claude"],
            "merged_dirs": ["merged1"],
            "orientation": {".claude": "injected"},
            "precommit": {"path": ".pre-commit-config.yaml", "existed": True},
            "git_initialized_by_us": True,
            "gitignore_existed": False,
            "copilot_generated_agents": set(),
            "codex_generated_agents": set(),
            "codex_hook_handlers": [],
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
        }
        report: list[str] = []
        inf.write_manifest(tmp_path, install, report)

        reloaded = {
            "remove_paths": [],
            "merged_dirs": [],
            "orientation": {},
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
            "copilot_generated_agents": set(),
            "codex_generated_agents": set(),
            "codex_hook_handlers": [],
        }
        inf.load_prior_manifest(tmp_path, reloaded, [])
        assert "factory" in reloaded["remove_paths"]
        assert ".claude" in reloaded["remove_paths"]
        assert reloaded["git_initialized_by_us"] is True
        assert reloaded["orientation"] == {".claude": "injected"}


class TestGitignoreIdempotency:
    """Integration: gitignore block survives multiple runs."""

    def test_double_write_no_duplicate_block(self, tmp_path):
        base_install = {
            "remove_paths": [],
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
        }
        inf.write_gitignore_block(tmp_path, dict(base_install), [])
        inf.write_gitignore_block(tmp_path, dict(base_install), [])
        gi = (tmp_path / ".gitignore").read_text()
        assert gi.count(inf.GITIGNORE_BEGIN) == 1
        assert gi.count(inf.GITIGNORE_END) == 1
