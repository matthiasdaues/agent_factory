"""Contract tests for init-factory setup script.

Tests focus on the pure/isolable functions that can run without a full
init sequence — filesystem steps, test regime detection, gitignore
assembly, manifest round-trip.
"""

from __future__ import annotations

import json
import os
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
    def test_writes_to_docs(self, tmp_path):
        inf._write_testing_yaml(tmp_path, "pytest")
        path = tmp_path / "docs" / "testing.yaml"
        assert path.exists()
        content = path.read_text()
        assert 'test_command: "pytest"' in content

    def test_overwrites_existing(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir(parents=True)
        (docs / "testing.yaml").write_text("test_command: old\n")
        inf._write_testing_yaml(tmp_path, "pytest")
        content = (docs / "testing.yaml").read_text()
        assert 'test_command: "pytest"' in content


class TestDetectTestRegime:
    def test_single_entrypoint_writes(self, tmp_path):
        (tmp_path / "Makefile").write_text("test:\n\tpytest\n")
        report: list[str] = []
        inf.detect_test_regime(tmp_path, report)
        path = tmp_path / "docs" / "testing.yaml"
        assert path.exists()
        assert "make test" in path.read_text()

    def test_existing_testing_yaml_skipped(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir(parents=True)
        (docs / "testing.yaml").write_text("test_command: custom\n")
        (tmp_path / "Makefile").write_text("test:\n\tpytest\n")
        report: list[str] = []
        inf.detect_test_regime(tmp_path, report)
        assert "custom" in (docs / "testing.yaml").read_text()

    def test_no_entrypoints_reports_gap(self, tmp_path):
        report: list[str] = []
        inf.detect_test_regime(tmp_path, report)
        assert not (tmp_path / "docs" / "testing.yaml").exists()
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

    def test_excludes_cli_dirs_not_in_cli_list(self, tmp_path):
        install = {
            "cli": ["copilot"],
            "remove_paths": [],
            "github_ignored_entries": {".github/copilot-instructions.md"},
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
        }
        report: list[str] = []
        inf.write_gitignore_block(tmp_path, install, report)
        gi = (tmp_path / ".gitignore").read_text()
        assert "/.claude/" not in gi
        assert "/.pi/" not in gi
        assert "/.github/copilot-instructions.md" in gi
        assert "/factory/" in gi

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

    def test_existing_config_deferred_to_fitting(self, tmp_path):
        self._make_template(tmp_path)
        original = (
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: my-project-hook\n"
            "        name: my hook\n"
            "        entry: echo mine\n"
            "        language: system\n"
        )
        (tmp_path / ".pre-commit-config.yaml").write_text(original)
        install = {"remove_paths": []}
        report: list[str] = []
        inf.handle_precommit(tmp_path, install, report)
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == original
        assert install["precommit"]["existed"] is True
        assert any("fitting" in r.lower() for r in report)


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


class TestDetectCli:
    """detect_cli returns a list of detected CLIs from dot-dirs."""

    def test_detects_claude(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        assert inf.detect_cli(tmp_path) == ["claude"]

    def test_detects_copilot(self, tmp_path):
        (tmp_path / ".github").mkdir()
        assert inf.detect_cli(tmp_path) == ["copilot"]

    def test_detects_codex_from_dotcodex(self, tmp_path):
        (tmp_path / ".codex").mkdir()
        assert inf.detect_cli(tmp_path) == ["codex"]

    def test_detects_codex_from_dotagents(self, tmp_path):
        (tmp_path / ".agents").mkdir()
        assert inf.detect_cli(tmp_path) == ["codex"]

    def test_detects_multiple(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".github").mkdir()
        result = inf.detect_cli(tmp_path)
        assert "claude" in result
        assert "copilot" in result
        assert len(result) == 2

    def test_empty_when_nothing(self, tmp_path):
        assert inf.detect_cli(tmp_path) == []


class TestWants:
    """_wants() gating for multi-CLI dispatch."""

    def test_none_means_all(self):
        assert inf._wants(None, "claude")
        assert inf._wants(None, "codex")

    def test_present_in_list(self):
        assert inf._wants(["claude", "copilot"], "claude")

    def test_absent_from_list(self):
        assert not inf._wants(["claude"], "codex")

    def test_empty_list_rejects_all(self):
        assert not inf._wants([], "claude")


class TestActiveDotDirs:
    """_active_dot_dirs() computes the union for selected CLIs."""

    def test_none_returns_all(self):
        assert inf._active_dot_dirs(None) == list(inf.DOT_DIRS)

    def test_single_cli(self):
        assert inf._active_dot_dirs(["claude"]) == [".claude"]

    def test_multiple_clis(self):
        result = inf._active_dot_dirs(["claude", "copilot"])
        assert result == [".claude", ".github"]

    def test_codex_contributes_dotcodex(self):
        result = inf._active_dot_dirs(["codex"])
        assert result == [".codex"]

    def test_no_duplicates(self):
        result = inf._active_dot_dirs(["claude", "claude"])
        assert result == [".claude"]


class TestAskClis:
    """ask_clis() parses interactive input."""

    def test_single_number(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "1")
        monkeypatch.setattr("sys.stdin", type("FakeTTY", (), {"isatty": lambda self: True})())
        assert inf.ask_clis() == ["claude"]

    def test_multiple_numbers_comma(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "1,3")
        monkeypatch.setattr("sys.stdin", type("FakeTTY", (), {"isatty": lambda self: True})())
        assert inf.ask_clis() == ["claude", "pi"]

    def test_multiple_numbers_space(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "2 4")
        monkeypatch.setattr("sys.stdin", type("FakeTTY", (), {"isatty": lambda self: True})())
        assert inf.ask_clis() == ["copilot", "codex"]

    def test_names(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "claude copilot")
        monkeypatch.setattr("sys.stdin", type("FakeTTY", (), {"isatty": lambda self: True})())
        assert inf.ask_clis() == ["claude", "copilot"]

    def test_all(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "a")
        monkeypatch.setattr("sys.stdin", type("FakeTTY", (), {"isatty": lambda self: True})())
        assert inf.ask_clis() is None

    def test_empty_means_all(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "")
        monkeypatch.setattr("sys.stdin", type("FakeTTY", (), {"isatty": lambda self: True})())
        assert inf.ask_clis() is None

    def test_invalid_input_returns_none(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "xyz 99")
        monkeypatch.setattr("sys.stdin", type("FakeTTY", (), {"isatty": lambda self: True})())
        assert inf.ask_clis() is None

    def test_non_tty_returns_none(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", type("FakeNoTTY", (), {"isatty": lambda self: False})())
        assert inf.ask_clis() is None

    def test_no_duplicates(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "1,1,claude")
        monkeypatch.setattr("sys.stdin", type("FakeTTY", (), {"isatty": lambda self: True})())
        assert inf.ask_clis() == ["claude"]


# ── Orientation file handling ─────────────────────────────────────────


class TestLinkOrientation:
    @pytest.fixture
    def setup(self, tmp_path):
        """Set up a minimal target with factory/config/AGENTS.md."""
        factory = tmp_path / "factory"
        factory.mkdir()
        config = factory / "config"
        config.mkdir()
        agents_md = config / "AGENTS.md"
        agents_md.write_text("# Orientation\nFactory content here.\n")
        install = {
            "remove_paths": [],
            "orientation": {},
            "_target": tmp_path,
            "github_ignored_entries": set(),
            "codex_ignored_entries": set(),
            "agents_ignored_entries": set(),
        }
        return tmp_path, factory, install

    def test_creates_symlink_when_absent(self, setup):
        target, factory, install = setup
        claude_dir = target / ".claude"
        claude_dir.mkdir()
        report: list[str] = []
        inf._link_orientation(target, ".claude", factory, install, report)
        link = target / ".claude" / "CLAUDE.md"
        assert link.is_symlink()
        assert install["orientation"][".claude/CLAUDE.md"] == "linked"

    def test_injects_block_into_existing_real_file(self, setup):
        target, factory, install = setup
        claude_dir = target / ".claude"
        claude_dir.mkdir()
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text("# My custom instructions\nDo things my way.\n")
        report: list[str] = []
        inf._link_orientation(target, ".claude", factory, install, report)
        content = claude_md.read_text()
        assert inf.ORIENTATION_BEGIN in content
        assert "My custom instructions" in content
        assert install["orientation"][".claude/CLAUDE.md"] == "injected"

    def test_skips_external_symlink(self, setup):
        target, factory, install = setup
        claude_dir = target / ".claude"
        claude_dir.mkdir()
        external = target / "my-shared-claude.md"
        external.write_text("# External instructions\n")
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.symlink_to(external)
        report: list[str] = []
        inf._link_orientation(target, ".claude", factory, install, report)
        assert claude_md.is_symlink()
        current = (claude_md.parent / os.readlink(claude_md)).resolve()
        assert current == external.resolve()
        assert install["orientation"][".claude/CLAUDE.md"] == "external"
        assert any("left untouched" in r for r in report)

    def test_recognizes_factory_symlink(self, setup):
        target, factory, install = setup
        claude_dir = target / ".claude"
        claude_dir.mkdir()
        claude_md = claude_dir / "CLAUDE.md"
        dest = factory / "config" / "AGENTS.md"
        claude_md.symlink_to(os.path.relpath(dest, claude_dir))
        report: list[str] = []
        inf._link_orientation(target, ".claude", factory, install, report)
        assert install["orientation"][".claude/CLAUDE.md"] == "linked"
        assert any("already linked" in r for r in report)


# ── Project context scan ──────────────────────────────────────────────


class TestScanProjectContext:
    def test_empty_project(self, tmp_path):
        ctx = inf._scan_project_context(tmp_path)
        assert ctx["languages"] == []
        assert ctx["frameworks"] == []
        assert ctx["fitting"]["status"] == "greenfield"
        assert ctx["fitting"]["fingerprint_confirmed"] is True

    def test_detects_python_language(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["languages"]]
        assert "python" in names

    def test_detects_javascript_language(self, tmp_path):
        (tmp_path / "package.json").write_text('{"name": "demo"}')
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["languages"]]
        assert "javascript" in names

    def test_detects_typescript(self, tmp_path):
        (tmp_path / "tsconfig.json").write_text("{}")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["languages"]]
        assert "typescript" in names

    def test_detects_go(self, tmp_path):
        (tmp_path / "go.mod").write_text("module example.com/demo\n\ngo 1.21\n")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["languages"]]
        assert "go" in names

    def test_detects_rust(self, tmp_path):
        (tmp_path / "Cargo.toml").write_text('[package]\nname = "demo"\n')
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["languages"]]
        assert "rust" in names

    def test_detects_package_manager_uv(self, tmp_path):
        (tmp_path / "uv.lock").write_text("")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["package_managers"]]
        assert "uv" in names

    def test_detects_package_manager_npm(self, tmp_path):
        (tmp_path / "package-lock.json").write_text("{}")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["package_managers"]]
        assert "npm" in names

    def test_detects_ci_github_actions(self, tmp_path):
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["ci"]]
        assert "github-actions" in names

    def test_detects_ci_gitlab(self, tmp_path):
        (tmp_path / ".gitlab-ci.yml").write_text("")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["ci"]]
        assert "gitlab-ci" in names

    def test_detects_linter_eslint(self, tmp_path):
        (tmp_path / ".eslintrc.json").write_text("{}")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["linters"]]
        assert "eslint" in names

    def test_detects_linter_ruff_config_file(self, tmp_path):
        (tmp_path / "ruff.toml").write_text("")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["linters"]]
        assert "ruff" in names

    def test_detects_linter_ruff_in_pyproject(self, tmp_path):
        if inf.tomllib is None:
            pytest.skip("tomllib not available")
        (tmp_path / "pyproject.toml").write_text(
            "[project]\nname = 'demo'\n[tool.ruff]\nline-length = 88\n"
        )
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["linters"]]
        assert "ruff" in names

    def test_detects_test_runner_pytest(self, tmp_path):
        (tmp_path / "conftest.py").write_text("")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["test_runners"]]
        assert "pytest" in names

    def test_detects_test_runner_jest(self, tmp_path):
        (tmp_path / "jest.config.js").write_text("")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["test_runners"]]
        assert "jest" in names

    def test_detects_pytest_in_pyproject(self, tmp_path):
        if inf.tomllib is None:
            pytest.skip("tomllib not available")
        (tmp_path / "pyproject.toml").write_text(
            "[project]\nname = 'demo'\n[tool.pytest.ini_options]\naddopts = '-v'\n"
        )
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["test_runners"]]
        assert "pytest" in names

    def test_detects_docs_tooling_mkdocs(self, tmp_path):
        (tmp_path / "mkdocs.yml").write_text("")
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["docs_tooling"]]
        assert "mkdocs" in names

    def test_detects_docs_structure(self, tmp_path):
        (tmp_path / "README.md").write_text("# Hello")
        (tmp_path / "docs").mkdir()
        ctx = inf._scan_project_context(tmp_path)
        names = [e["name"] for e in ctx["docs_structure"]]
        assert "README.md" in names
        assert "docs" in names

    def test_skips_cache_dirs(self, tmp_path):
        cache = tmp_path / "node_modules" / "express"
        cache.mkdir(parents=True)
        (cache / "package.json").write_text('{"name": "express"}')
        ctx = inf._scan_project_context(tmp_path)
        assert ctx["languages"] == []

    def test_skips_factory_dir(self, tmp_path):
        factory = tmp_path / "factory"
        factory.mkdir()
        (factory / "pyproject.toml").write_text("[project]\nname = 'factory'\n")
        ctx = inf._scan_project_context(tmp_path)
        assert ctx["languages"] == []

    def test_evidence_is_relative_path(self, tmp_path):
        sub = tmp_path / "backend"
        sub.mkdir()
        (sub / "pyproject.toml").write_text("[project]\nname = 'api'\n")
        ctx = inf._scan_project_context(tmp_path)
        evidence = ctx["languages"][0]["evidence"]
        assert evidence == "backend/pyproject.toml"

    def test_no_duplicate_languages(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'a'\n")
        sub = tmp_path / "lib"
        sub.mkdir()
        (sub / "setup.py").write_text("")
        ctx = inf._scan_project_context(tmp_path)
        python_entries = [e for e in ctx["languages"] if e["name"] == "python"]
        assert len(python_entries) == 1

    def test_multiple_languages_detected(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'api'\n")
        (tmp_path / "package.json").write_text('{"name": "frontend"}')
        ctx = inf._scan_project_context(tmp_path)
        names = {e["name"] for e in ctx["languages"]}
        assert names == {"python", "javascript"}

    def test_fitting_state_greenfield(self, tmp_path):
        ctx = inf._scan_project_context(tmp_path)
        fitting = ctx["fitting"]
        assert fitting["status"] == "greenfield"
        assert fitting["model_matrix_configured"] is False
        assert fitting["fingerprint_confirmed"] is True
        assert fitting["agent_context_populated"] is True
        assert fitting["hooks_decided"] is True

    def test_fitting_state_brownfield(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        ctx = inf._scan_project_context(tmp_path)
        fitting = ctx["fitting"]
        assert fitting["status"] == "unfitted"
        assert fitting["model_matrix_configured"] is False
        assert fitting["fingerprint_confirmed"] is False
        assert fitting["agent_context_populated"] is False
        assert fitting["hooks_decided"] is False

    def test_brownfield_no_tracked_artifacts_all_keys_false(self, tmp_path):
        """ST-0210 scenario 2: no derivable artifacts -> every key false,
        status unfitted."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        ctx = inf._scan_project_context(tmp_path)
        fitting = ctx["fitting"]
        assert fitting["status"] == "unfitted"
        assert fitting["model_matrix_configured"] is False
        assert fitting["fingerprint_confirmed"] is False
        assert fitting["agent_context_populated"] is False
        assert fitting["test_regime_detected"] is False
        assert fitting["hooks_decided"] is False

    def test_brownfield_partial_artifacts_mixed_status_fitting(self, tmp_path):
        """ST-0210 scenario 3: some but not all artifacts present -> mixed
        keys, status fitting."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "stack.yaml").write_text(
            "mode: index\n\nlanguages:\n  python:\n    name: Python\n    source: pyproject.toml\n"
        )
        ctx = inf._scan_project_context(tmp_path)
        fitting = ctx["fitting"]
        assert fitting["agent_context_populated"] is True
        assert fitting["fingerprint_confirmed"] is False
        assert fitting["test_regime_detected"] is False
        assert fitting["hooks_decided"] is False
        assert fitting["status"] == "fitting"

    def test_model_matrix_configured_never_derived_true_from_scan(self, tmp_path):
        """model_matrix_configured has no artifact to derive from -- a fresh
        scan always reports it false, regardless of what else is present."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "stack.yaml").write_text(
            "mode: index\n\nlanguages:\n  python:\n    name: Python\n    source: pyproject.toml\n"
        )
        (ac_dir / "testing.yaml").write_text("suites: []\n")
        (tmp_path / ".pre-commit-config.yaml").write_text(
            "repos:\n  - repo: local\n    hooks:\n      - id: agent_factory_hook-mdformat\n"
        )
        ctx = inf._scan_project_context(tmp_path)
        assert ctx["fitting"]["model_matrix_configured"] is False


class TestDeriveFittingKeys:
    """Unit coverage for _derive_fitting_keys, one case per rule in the
    ST-0210 derivation table."""

    def test_fingerprint_confirmed_true_when_cache_has_languages(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "project-context.json").write_text(
            json.dumps({"languages": [{"name": "python", "evidence": "pyproject.toml"}]})
        )
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["fingerprint_confirmed"] is True

    def test_fingerprint_confirmed_true_when_cache_has_frameworks(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "project-context.json").write_text(
            json.dumps({"languages": [], "frameworks": [{"name": "django", "evidence": "x"}]})
        )
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["fingerprint_confirmed"] is True

    def test_fingerprint_not_confirmed_without_cache_file(self, tmp_path):
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["fingerprint_confirmed"] is False

    def test_fingerprint_not_confirmed_when_cache_has_no_signals(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "project-context.json").write_text(
            json.dumps({"languages": [], "frameworks": []})
        )
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["fingerprint_confirmed"] is False

    def test_agent_context_populated_true_with_real_leaf(self, tmp_path):
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "stack.yaml").write_text(
            "mode: index\n\nlanguages:\n  python:\n    name: Python\n    source: pyproject.toml\n"
        )
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["agent_context_populated"] is True

    def test_agent_context_not_populated_when_absent(self, tmp_path):
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["agent_context_populated"] is False

    def test_agent_context_not_populated_when_only_deferred(self, tmp_path):
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "stack.yaml").write_text(
            'mode: index\n\nlanguages:\n  deferred: "pending interview"\n'
        )
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["agent_context_populated"] is False

    def test_agent_context_not_populated_when_only_mode_key(self, tmp_path):
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "stack.yaml").write_text("mode: index\n")
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["agent_context_populated"] is False

    def test_test_regime_detected_via_agent_context_testing_yaml(self, tmp_path):
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "testing.yaml").write_text("suites: []\n")
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["test_regime_detected"] is True

    def test_test_regime_detected_via_charter_testing_yaml(self, tmp_path):
        charter_dir = tmp_path / "docs" / "charter"
        charter_dir.mkdir(parents=True)
        (charter_dir / "testing.yaml").write_text("suites: []\n")
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["test_regime_detected"] is True

    def test_test_regime_detected_via_workflow_testing_field(self, tmp_path):
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "workflow.yaml").write_text(
            "mode: index\n\ntesting:\n  name: pytest\n  source: pyproject.toml\n"
        )
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["test_regime_detected"] is True

    def test_test_regime_not_detected_when_workflow_testing_deferred(self, tmp_path):
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "workflow.yaml").write_text(
            'mode: index\n\ntesting:\n  deferred: "not yet decided"\n'
        )
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["test_regime_detected"] is False

    def test_test_regime_not_detected_when_nothing_present(self, tmp_path):
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["test_regime_detected"] is False

    def test_hooks_decided_true_with_factory_marker(self, tmp_path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            "repos:\n  - repo: local\n    hooks:\n      - id: agent_factory_hook-mdformat\n"
        )
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["hooks_decided"] is True

    def test_hooks_not_decided_without_factory_marker(self, tmp_path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            "repos:\n  - repo: local\n    hooks:\n      - id: ruff\n"
        )
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["hooks_decided"] is False

    def test_hooks_not_decided_when_file_absent(self, tmp_path):
        derived = inf._derive_fitting_keys(tmp_path)
        assert derived["hooks_decided"] is False

    def test_derive_fitting_keys_never_returns_model_matrix_configured(self, tmp_path):
        derived = inf._derive_fitting_keys(tmp_path)
        assert "model_matrix_configured" not in derived


class TestFittingStatus:
    def test_all_true_is_fitted(self):
        fitting = {
            "model_matrix_configured": True,
            "fingerprint_confirmed": True,
            "agent_context_populated": True,
            "test_regime_detected": True,
            "hooks_decided": True,
        }
        assert inf._fitting_status(fitting) == "fitted"

    def test_all_false_is_unfitted(self):
        fitting = {
            "model_matrix_configured": False,
            "fingerprint_confirmed": False,
            "agent_context_populated": False,
            "test_regime_detected": False,
            "hooks_decided": False,
        }
        assert inf._fitting_status(fitting) == "unfitted"

    def test_mixed_is_fitting(self):
        fitting = {
            "model_matrix_configured": False,
            "fingerprint_confirmed": True,
            "agent_context_populated": True,
            "test_regime_detected": False,
            "hooks_decided": False,
        }
        assert inf._fitting_status(fitting) == "fitting"


class TestDetectFrameworksPyproject:
    @pytest.fixture
    def pyproject(self, tmp_path):
        def _write(content):
            path = tmp_path / "pyproject.toml"
            path.write_text(content)
            return path
        return _write

    def test_detects_fastapi(self, pyproject):
        path = pyproject(
            '[project]\nname = "demo"\ndependencies = ["fastapi>=0.100"]\n'
        )
        if inf.tomllib is None:
            pytest.skip("tomllib not available")
        found = inf._detect_frameworks_pyproject(path)
        names = [e["name"] for e in found]
        assert "fastapi" in names

    def test_detects_django(self, pyproject):
        path = pyproject(
            '[project]\nname = "demo"\ndependencies = ["Django>=4.2"]\n'
        )
        if inf.tomllib is None:
            pytest.skip("tomllib not available")
        found = inf._detect_frameworks_pyproject(path)
        names = [e["name"] for e in found]
        assert "django" in names

    def test_detects_poetry_deps(self, pyproject):
        path = pyproject(
            '[tool.poetry.dependencies]\npython = "^3.11"\nflask = "^3.0"\n'
        )
        if inf.tomllib is None:
            pytest.skip("tomllib not available")
        found = inf._detect_frameworks_pyproject(path)
        names = [e["name"] for e in found]
        assert "flask" in names

    def test_ignores_unknown_deps(self, pyproject):
        path = pyproject(
            '[project]\nname = "demo"\ndependencies = ["requests", "httpx"]\n'
        )
        if inf.tomllib is None:
            pytest.skip("tomllib not available")
        found = inf._detect_frameworks_pyproject(path)
        framework_names = [e["name"] for e in found if not e["name"].startswith("[")]
        assert framework_names == []

    def test_malformed_toml_returns_empty(self, pyproject):
        path = pyproject("this is not valid toml {{{{")
        if inf.tomllib is None:
            pytest.skip("tomllib not available")
        found = inf._detect_frameworks_pyproject(path)
        assert found == []


class TestDetectFrameworksPackageJson:
    def test_detects_react(self, tmp_path):
        path = tmp_path / "package.json"
        path.write_text('{"dependencies": {"react": "^18.0"}}')
        found = inf._detect_frameworks_package_json(path)
        names = [e["name"] for e in found]
        assert "react" in names

    def test_detects_express_in_deps(self, tmp_path):
        path = tmp_path / "package.json"
        path.write_text('{"dependencies": {"express": "^4.18"}}')
        found = inf._detect_frameworks_package_json(path)
        names = [e["name"] for e in found]
        assert "express" in names

    def test_detects_nestjs(self, tmp_path):
        path = tmp_path / "package.json"
        path.write_text('{"dependencies": {"@nestjs/core": "^10.0"}}')
        found = inf._detect_frameworks_package_json(path)
        names = [e["name"] for e in found]
        assert "nestjs" in names

    def test_detects_from_dev_deps(self, tmp_path):
        path = tmp_path / "package.json"
        path.write_text('{"devDependencies": {"vitest": "^1.0"}}')
        found = inf._detect_frameworks_package_json(path)
        # vitest is not in KNOWN_FRAMEWORKS_JS; it's a test runner detected separately
        # but vite IS in the list
        assert all(e["name"] != "vitest" for e in found)

    def test_malformed_json_returns_empty(self, tmp_path):
        path = tmp_path / "package.json"
        path.write_text("not json at all")
        found = inf._detect_frameworks_package_json(path)
        assert found == []


class TestDetectFrameworksGomod:
    def test_detects_gin(self, tmp_path):
        path = tmp_path / "go.mod"
        path.write_text(
            "module example.com/demo\n\ngo 1.21\n\n"
            "require github.com/gin-gonic/gin v1.9.1\n"
        )
        found = inf._detect_frameworks_gomod(path)
        names = [e["name"] for e in found]
        assert "gin" in names

    def test_no_frameworks(self, tmp_path):
        path = tmp_path / "go.mod"
        path.write_text("module example.com/demo\n\ngo 1.21\n")
        found = inf._detect_frameworks_gomod(path)
        assert found == []


class TestWriteProjectContext:
    def test_writes_json_file(self, tmp_path):
        install = {"remove_paths": []}
        report: list[str] = []
        (tmp_path / "config").mkdir()
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        inf.write_project_context(tmp_path, install, report)
        path = tmp_path / "config" / "project-context.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert "languages" in data
        assert "fitting" in data
        assert data["fitting"]["status"] == "unfitted"

    def test_skips_if_exists(self, tmp_path):
        (tmp_path / "config").mkdir()
        existing = tmp_path / "config" / "project-context.json"
        existing.write_text('{"custom": true}')
        install = {"remove_paths": []}
        report: list[str] = []
        inf.write_project_context(tmp_path, install, report)
        assert json.loads(existing.read_text()) == {"custom": True}

    def test_adds_to_install_manifest(self, tmp_path):
        install = {"remove_paths": []}
        report: list[str] = []
        (tmp_path / "config").mkdir()
        inf.write_project_context(tmp_path, install, report)
        assert "config/project-context.json" in install["remove_paths"]
        assert install.get("ignore_project_context") is True

    def test_creates_config_dir(self, tmp_path):
        install = {"remove_paths": []}
        report: list[str] = []
        inf.write_project_context(tmp_path, install, report)
        assert (tmp_path / "config" / "project-context.json").exists()


class TestReconcileProjectContext:
    """ST-0210 scenario 4: an existing cache is reconciled against tracked
    artifacts on every write_project_context call, and the artifact wins
    when it contradicts the cache."""

    @staticmethod
    def _seed_cache(tmp_path: Path, fitting: dict, **extra) -> Path:
        (tmp_path / "config").mkdir()
        path = tmp_path / "config" / "project-context.json"
        payload = {"languages": [], "frameworks": [], "fitting": fitting, **extra}
        path.write_text(json.dumps(payload))
        return path

    def test_stale_false_cache_flipped_true_by_new_artifact(self, tmp_path):
        cache_path = self._seed_cache(
            tmp_path,
            {
                "status": "unfitted",
                "model_matrix_configured": False,
                "fingerprint_confirmed": False,
                "agent_context_populated": False,
                "test_regime_detected": False,
                "hooks_decided": False,
            },
        )
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "stack.yaml").write_text(
            "mode: index\n\nlanguages:\n  python:\n    name: Python\n    source: pyproject.toml\n"
        )
        install = {"remove_paths": []}
        report: list[str] = []
        inf.write_project_context(tmp_path, install, report)
        data = json.loads(cache_path.read_text())
        assert data["fitting"]["agent_context_populated"] is True
        assert data["fitting"]["status"] == "fitting"

    def test_all_tracked_artifacts_present_yields_four_of_five_and_fitting(self, tmp_path):
        cache_path = self._seed_cache(
            tmp_path,
            {
                "status": "unfitted",
                "model_matrix_configured": False,
                "fingerprint_confirmed": False,
                "agent_context_populated": False,
                "test_regime_detected": False,
                "hooks_decided": False,
            },
            languages=[{"name": "python", "evidence": "pyproject.toml"}],
        )
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "stack.yaml").write_text(
            "mode: index\n\nlanguages:\n  python:\n    name: Python\n    source: pyproject.toml\n"
        )
        (ac_dir / "testing.yaml").write_text("suites: []\n")
        (tmp_path / ".pre-commit-config.yaml").write_text(
            "repos:\n  - repo: local\n    hooks:\n      - id: agent_factory_hook-mdformat\n"
        )
        install = {"remove_paths": []}
        report: list[str] = []
        inf.write_project_context(tmp_path, install, report)
        fitting = json.loads(cache_path.read_text())["fitting"]
        true_count = sum(1 for k in (
            "model_matrix_configured", "fingerprint_confirmed",
            "agent_context_populated", "test_regime_detected", "hooks_decided",
        ) if fitting[k])
        assert true_count == 4
        assert fitting["model_matrix_configured"] is False
        assert fitting["status"] == "fitting"

    def test_true_cache_flipped_false_when_artifact_removed(self, tmp_path):
        cache_path = self._seed_cache(
            tmp_path,
            {
                "status": "fitting",
                "model_matrix_configured": False,
                "fingerprint_confirmed": False,
                "agent_context_populated": True,
                "test_regime_detected": False,
                "hooks_decided": False,
            },
        )
        install = {"remove_paths": []}
        report: list[str] = []
        inf.write_project_context(tmp_path, install, report)
        data = json.loads(cache_path.read_text())
        assert data["fitting"]["agent_context_populated"] is False
        assert data["fitting"]["status"] == "unfitted"

    def test_model_matrix_configured_preserved_from_cache(self, tmp_path):
        cache_path = self._seed_cache(
            tmp_path,
            {
                "status": "fitting",
                "model_matrix_configured": True,
                "fingerprint_confirmed": False,
                "agent_context_populated": False,
                "test_regime_detected": False,
                "hooks_decided": False,
            },
        )
        install = {"remove_paths": []}
        report: list[str] = []
        inf.write_project_context(tmp_path, install, report)
        assert json.loads(cache_path.read_text())["fitting"]["model_matrix_configured"] is True

    def test_all_five_true_yields_fitted_status(self, tmp_path):
        cache_path = self._seed_cache(
            tmp_path,
            {
                "status": "fitting",
                "model_matrix_configured": True,
                "fingerprint_confirmed": False,
                "agent_context_populated": False,
                "test_regime_detected": False,
                "hooks_decided": False,
            },
            languages=[{"name": "python", "evidence": "pyproject.toml"}],
        )
        ac_dir = tmp_path / "docs" / "agent-context"
        ac_dir.mkdir(parents=True)
        (ac_dir / "stack.yaml").write_text(
            "mode: index\n\nlanguages:\n  python:\n    name: Python\n    source: pyproject.toml\n"
        )
        (ac_dir / "testing.yaml").write_text("suites: []\n")
        (tmp_path / ".pre-commit-config.yaml").write_text(
            "repos:\n  - repo: local\n    hooks:\n      - id: agent_factory_hook-mdformat\n"
        )
        install = {"remove_paths": []}
        report: list[str] = []
        inf.write_project_context(tmp_path, install, report)
        assert json.loads(cache_path.read_text())["fitting"]["status"] == "fitted"

    def test_non_fitting_cached_fields_preserved(self, tmp_path):
        cache_path = self._seed_cache(
            tmp_path,
            {
                "status": "unfitted",
                "model_matrix_configured": False,
                "fingerprint_confirmed": False,
                "agent_context_populated": False,
                "test_regime_detected": False,
                "hooks_decided": False,
            },
            docs_structure=[{"name": "README.md", "evidence": "README.md"}],
        )
        install = {"remove_paths": []}
        report: list[str] = []
        inf.write_project_context(tmp_path, install, report)
        data = json.loads(cache_path.read_text())
        assert data["docs_structure"] == [{"name": "README.md", "evidence": "README.md"}]

    def test_greenfield_cache_left_untouched(self, tmp_path):
        greenfield_fitting = {
            "status": "greenfield",
            "model_matrix_configured": False,
            "fingerprint_confirmed": True,
            "agent_context_populated": True,
            "test_regime_detected": True,
            "hooks_decided": True,
        }
        cache_path = self._seed_cache(tmp_path, greenfield_fitting)
        before = cache_path.read_text()
        install = {"remove_paths": []}
        report: list[str] = []
        inf.write_project_context(tmp_path, install, report)
        assert cache_path.read_text() == before

    def test_cache_without_fitting_key_left_untouched(self, tmp_path):
        (tmp_path / "config").mkdir()
        cache_path = tmp_path / "config" / "project-context.json"
        cache_path.write_text(json.dumps({"custom": True}))
        install = {"remove_paths": []}
        report: list[str] = []
        inf.write_project_context(tmp_path, install, report)
        assert json.loads(cache_path.read_text()) == {"custom": True}


class TestExtractDepName:
    def test_simple_name(self):
        assert inf._extract_dep_name("fastapi") == "fastapi"

    def test_versioned(self):
        assert inf._extract_dep_name("fastapi>=0.100") == "fastapi"

    def test_extras(self):
        assert inf._extract_dep_name("fastapi[all]>=0.100") == "fastapi"

    def test_case_normalized(self):
        assert inf._extract_dep_name("Django>=4.2") == "django"

    def test_empty_string(self):
        assert inf._extract_dep_name("") is None

    def test_whitespace(self):
        assert inf._extract_dep_name("  requests >= 2.0  ") == "requests"


class TestPathCli:
    def test_claude_paths(self):
        assert inf._path_cli(".claude/settings.json") == "claude"
        assert inf._path_cli(".claude") == "claude"
        assert inf._path_cli(".claude/hooks/block.sh") == "claude"

    def test_copilot_paths(self):
        assert inf._path_cli(".github/copilot-instructions.md") == "copilot"
        assert inf._path_cli(".github/hooks/guard.sh") == "copilot"

    def test_pi_paths(self):
        assert inf._path_cli(".pi/extensions") == "pi"
        assert inf._path_cli(".pi") == "pi"

    def test_codex_paths(self):
        assert inf._path_cli(".codex/agents/virgil.toml") == "codex"
        assert inf._path_cli(".agents/skills/grilling") == "codex"

    def test_shared_paths(self):
        assert inf._path_cli("factory") is None
        assert inf._path_cli("config/model.conf") is None
        assert inf._path_cli("AGENTS.md") is None
        assert inf._path_cli(".agent-factory/factory-install.json") is None


class TestDoAdd:
    def test_fails_without_manifest(self, tmp_path):
        rc = inf.do_add(tmp_path, tmp_path, ["claude"])
        assert rc == 1

    def test_reports_all_installed(self, tmp_path):
        manifest_path = tmp_path / ".agent-factory" / "factory-install.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps({"cli": None}))
        rc = inf.do_add(tmp_path, tmp_path, ["claude"])
        assert rc == 0


class TestDoRemove:
    def test_fails_without_manifest(self, tmp_path):
        rc = inf.do_remove(tmp_path, ["claude"])
        assert rc == 1

    def test_reports_not_installed(self, tmp_path):
        manifest_path = tmp_path / ".agent-factory" / "factory-install.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps({
            "cli": ["copilot"],
            "remove_paths": [],
            "orientation": {},
        }))
        rc = inf.do_remove(tmp_path, ["claude"])
        assert rc == 0

    def test_preserves_shared_orientation_when_other_cli_remains(self, tmp_path):
        """Removing codex must not strip AGENTS.md orientation when pi remains."""
        agents_md = tmp_path / "AGENTS.md"
        begin = inf.ORIENTATION_BEGIN
        end = inf.ORIENTATION_END
        agents_md.write_text(
            f"# Project\n{begin}\nFactory content\n{end}\nUser content\n"
        )
        manifest_path = tmp_path / ".agent-factory" / "factory-install.json"
        manifest_path.parent.mkdir(parents=True)
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("# project\n")
        manifest_path.write_text(json.dumps({
            "cli": ["pi", "codex"],
            "remove_paths": [],
            "orientation": {"AGENTS.md": "injected"},
            "orientation_markers": {"begin": begin, "end": end},
            "ignored_paths": [],
            "gitignore_existed": True,
            "gitignore_orig_final_newline": True,
        }))
        rc = inf.do_remove(tmp_path, ["codex"])
        assert rc == 0
        text = agents_md.read_text()
        assert begin in text, "orientation block should be preserved for pi"

class TestFactoryChecksums:
    """Per-file checksum recording and modification detection."""

    def _make_factory(self, tmp_path):
        factory = tmp_path / "factory"
        factory.mkdir()
        (factory / "scripts").mkdir()
        (factory / "scripts" / "step-guard").write_text("#!/usr/bin/env python3\npass\n")
        (factory / "skills").mkdir()
        (factory / "skills" / "tdd").mkdir()
        (factory / "skills" / "tdd" / "SKILL.md").write_text("# TDD skill\n")
        (factory / "__pycache__").mkdir()
        (factory / "__pycache__" / "lib.cpython-310.pyc").write_bytes(b"\x00")
        return factory

    def test_compute_checksums_skips_pycache(self, tmp_path):
        factory = self._make_factory(tmp_path)
        checksums = inf.compute_factory_checksums(factory)
        assert "scripts/step-guard" in checksums
        assert "skills/tdd/SKILL.md" in checksums
        assert not any("__pycache__" in k for k in checksums)
        assert not any(k.endswith(".pyc") for k in checksums)

    def test_write_and_read_roundtrip(self, tmp_path):
        factory = self._make_factory(tmp_path)
        inf.write_factory_checksums(tmp_path, factory)
        stored = inf.read_factory_checksums(tmp_path)
        assert stored is not None
        assert "scripts/step-guard" in stored

    def test_detect_no_modifications(self, tmp_path):
        factory = self._make_factory(tmp_path)
        inf.write_factory_checksums(tmp_path, factory)
        result = inf.detect_factory_modifications(tmp_path)
        assert result is not None
        modified, added, removed = result
        assert modified == []
        assert added == []
        assert removed == []

    def test_detect_modified_file(self, tmp_path):
        factory = self._make_factory(tmp_path)
        inf.write_factory_checksums(tmp_path, factory)
        (factory / "skills" / "tdd" / "SKILL.md").write_text("# TDD skill\nCustomized.\n")
        result = inf.detect_factory_modifications(tmp_path)
        modified, added, removed = result
        assert "skills/tdd/SKILL.md" in modified
        assert added == []
        assert removed == []

    def test_detect_added_file(self, tmp_path):
        factory = self._make_factory(tmp_path)
        inf.write_factory_checksums(tmp_path, factory)
        (factory / "skills" / "custom").mkdir()
        (factory / "skills" / "custom" / "SKILL.md").write_text("# Custom\n")
        result = inf.detect_factory_modifications(tmp_path)
        modified, added, removed = result
        assert modified == []
        assert "skills/custom/SKILL.md" in added

    def test_detect_removed_file(self, tmp_path):
        factory = self._make_factory(tmp_path)
        inf.write_factory_checksums(tmp_path, factory)
        (factory / "skills" / "tdd" / "SKILL.md").unlink()
        result = inf.detect_factory_modifications(tmp_path)
        modified, added, removed = result
        assert "skills/tdd/SKILL.md" in removed

    def test_no_baseline_returns_none(self, tmp_path):
        self._make_factory(tmp_path)
        result = inf.detect_factory_modifications(tmp_path)
        assert result is None

    def test_copy_factory_records_checksums(self, tmp_path):
        (tmp_path / "source").mkdir()
        source = self._make_factory(tmp_path / "source")
        target = tmp_path / "project"
        target.mkdir()
        report: list[str] = []
        install = {"remove_paths": []}
        inf.copy_factory(source.parent / "factory", target, install, report)
        assert (target / ".agent-factory" / "factory-checksums.json").exists()
        stored = inf.read_factory_checksums(target)
        assert stored is not None
        assert "scripts/step-guard" in stored


class TestDoRemoveCLIPaths:

    def test_removes_cli_paths(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings = claude_dir / "settings.json"
        settings.write_text("{}")
        manifest_path = tmp_path / ".agent-factory" / "factory-install.json"
        manifest_path.parent.mkdir(parents=True)
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("# project\n")
        manifest_path.write_text(json.dumps({
            "cli": ["claude", "copilot"],
            "remove_paths": [".claude/settings.json", ".claude"],
            "orientation": {},
            "ignored_paths": [],
            "gitignore_existed": True,
            "gitignore_orig_final_newline": True,
        }))
        rc = inf.do_remove(tmp_path, ["claude"])
        assert rc == 0
        assert not settings.exists()
        manifest = json.loads(manifest_path.read_text())
        assert "claude" not in (manifest.get("cli") or [])
        assert "copilot" in (manifest.get("cli") or [])
