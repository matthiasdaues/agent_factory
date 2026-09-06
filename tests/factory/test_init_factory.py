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


# ── Project context scan ──────────────────────────────────────────────


class TestScanProjectContext:
    def test_empty_project(self, tmp_path):
        ctx = inf._scan_project_context(tmp_path)
        assert ctx["languages"] == []
        assert ctx["frameworks"] == []
        assert ctx["fitting"]["status"] == "unfitted"
        assert ctx["fitting"]["fingerprint_confirmed"] is False

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

    def test_fitting_state_initialized(self, tmp_path):
        ctx = inf._scan_project_context(tmp_path)
        fitting = ctx["fitting"]
        assert fitting["status"] == "unfitted"
        assert fitting["fingerprint_confirmed"] is False
        assert fitting["agent_context_populated"] is False
        assert fitting["hooks_decided"] is False


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
