"""Tests for the `orchestrate init` command (ADR-0010)."""

from __future__ import annotations

import subprocess

import pytest

from orchestrator.cli import (
    main,
    _tooling_root,
    _CLI_INSTRUCTION_FILES,
)


@pytest.fixture()
def empty_dir(tmp_path, monkeypatch):
    """An empty directory used as cwd."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def git_dir(tmp_path, monkeypatch):
    """An empty directory with a git repo, used as cwd."""
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestToolingRoot:
    def test_resolves_to_repo_with_agents_and_skills(self):
        root = _tooling_root()
        assert (root / "factory" / "agents").is_dir()
        assert (root / "factory" / "skills").is_dir()
        assert (root / "factory" / "scripts").is_dir()


class TestInitScaffolds:
    def test_creates_project_directories(self, git_dir):
        rc = main(["init", "--cli", "codex"])
        assert rc == 0
        assert (git_dir / "docs" / "spec" / "use_cases").is_dir()
        assert (git_dir / "docs" / "spec" / "supplementary_specs").is_dir()
        assert (git_dir / "docs" / "adr").is_dir()
        assert (git_dir / "docs" / "reviews").is_dir()
        assert (git_dir / "docs" / "findings").is_dir()
        assert (git_dir / "backlog").is_dir()

    def test_creates_positional_project_dir(self, empty_dir):
        project = empty_dir / "my-project"
        rc = main(["init", str(project), "--cli", "codex"])
        assert rc == 0
        assert project.is_dir()
        assert (project / ".git").is_dir()
        assert (project / "docs" / "adr").is_dir()

    def test_git_init_if_needed(self, empty_dir):
        assert not (empty_dir / ".git").is_dir()
        main(["init", "--cli", "codex"])
        assert (empty_dir / ".git").is_dir()


class TestInitCopiedDirs:
    def test_copies_tooling_dirs(self, git_dir):
        main(["init", "--cli", "codex"])
        for name in ["agents", "skills", "scripts"]:
            d = git_dir / name
            assert d.is_dir()
            assert not d.is_symlink()

    def test_idempotent_rerun_overwrites(self, git_dir):
        main(["init", "--cli", "codex"])
        marker = git_dir / "agents" / "_marker.txt"
        marker.write_text("stale")
        main(["init", "--cli", "codex"])
        assert not marker.exists()  # overwritten by fresh copy

    def test_agents_contain_requirements_agent(self, git_dir):
        main(["init", "--cli", "codex"])
        assert (git_dir / "agents" / "requirements-agent.md").is_file()


class TestInitGitignore:
    def test_adds_symlink_entries(self, git_dir):
        main(["init", "--cli", "codex"])
        content = (git_dir / ".gitignore").read_text()
        assert "agents/" in content
        assert "skills/" in content
        assert "scripts/" in content
        assert ".orchestrator/" in content

    def test_no_ai_tooling_entry(self, git_dir):
        main(["init", "--cli", "codex"])
        content = (git_dir / ".gitignore").read_text()
        assert ".ai_tooling/" not in content

    def test_idempotent_gitignore(self, git_dir):
        main(["init", "--cli", "codex"])
        main(["init", "--cli", "codex"])
        content = (git_dir / ".gitignore").read_text()
        assert content.count("agents/") == 1


class TestInitModelMatrix:
    def test_copies_template(self, git_dir):
        main(["init", "--cli", "codex"])
        matrix = git_dir / "model.conf"
        assert matrix.exists()
        assert "economy" in matrix.read_text()

    def test_does_not_overwrite_existing(self, git_dir):
        existing = "# my config\n"
        (git_dir / "model.conf").write_text(existing)
        main(["init", "--cli", "codex"])
        assert (git_dir / "model.conf").read_text() == existing


class TestInitPreCommitConfig:
    def test_copies_pre_commit_config(self, git_dir):
        main(["init", "--cli", "codex"])
        cfg = git_dir / ".pre-commit-config.yaml"
        assert cfg.exists()
        content = cfg.read_text()
        assert "spec-lint" in content
        assert "arch-lint" in content
        assert "backlog-lint" in content
        assert "matrix-lint" in content

    def test_does_not_overwrite_existing(self, git_dir):
        existing = "# custom hooks\n"
        (git_dir / ".pre-commit-config.yaml").write_text(existing)
        main(["init", "--cli", "codex"])
        assert (git_dir / ".pre-commit-config.yaml").read_text() == existing


class TestInitPreCommitConfigPathsResolve:
    """BUG-0002: the copied .pre-commit-config.yaml's gate hooks must reference
    paths that `orchestrate init` actually creates (flat scripts/, flat
    model.conf), not agent_factory's own factory/scripts + config/
    layout, which `orchestrate init` never produces for the target project."""

    def test_gate_hook_entries_point_at_files_that_exist(self, git_dir):
        main(["init", "--cli", "codex"])
        cfg = git_dir / ".pre-commit-config.yaml"
        content = cfg.read_text()

        for line in content.splitlines():
            line = line.strip()
            if not line.startswith("entry:"):
                continue
            tokens = line[len("entry:") :].strip().split()
            if tokens[0] != "python3":
                continue
            script_path = git_dir / tokens[1]
            assert script_path.exists(), (
                f"gate hook entry references {tokens[1]!r}, which does not "
                "exist anywhere in the project `orchestrate init` just created"
            )

    def test_matrix_lint_files_pattern_matches_copied_matrix_location(self, git_dir):
        import re

        main(["init", "--cli", "codex"])
        assert (git_dir / "model.conf").exists()
        content = (git_dir / ".pre-commit-config.yaml").read_text()

        m = re.search(r"id: matrix-lint\b.*?files:\s*(\S+)", content, re.S)
        assert m is not None, "no matrix-lint hook with a files: pattern found"
        pattern = m.group(1)
        assert re.match(pattern, "model.conf"), (
            f"matrix-lint's files: pattern {pattern!r} does not match "
            "model.conf, the real location `orchestrate init` copies "
            "the matrix template to"
        )


class TestInitInstructionFile:
    @pytest.mark.parametrize(
        "cli_name,expected_path", list(_CLI_INSTRUCTION_FILES.items())
    )
    def test_creates_instruction_file(self, git_dir, cli_name, expected_path):
        rc = main(["init", "--cli", cli_name])
        assert rc == 0
        path = git_dir / expected_path
        assert path.exists()
        content = path.read_text()
        assert "requirements-agent" in content
        assert "## Scope" in content
        assert "## Do Not Read" in content
        assert "scripts/" in content

    def test_overwrites_existing_on_reinit(self, git_dir, capsys):
        instr = git_dir / "AGENTS.md"
        instr.write_text("# stale content\n")
        main(["init", "--cli", "codex"])
        content = instr.read_text()
        assert "requirements-agent" in content
        assert "## Scope" in content
        captured = capsys.readouterr()
        assert "already exists" in captured.out

    def test_defaults_to_codex_when_not_tty(self, git_dir, monkeypatch):
        monkeypatch.setattr(
            "sys.stdin", type("FakeStdin", (), {"isatty": lambda self: False})()
        )
        main(["init"])
        assert (git_dir / "AGENTS.md").exists()


class TestInitNoContext:
    def test_does_not_create_context_md(self, git_dir):
        main(["init", "--cli", "codex"])
        assert not (git_dir / "CONTEXT.md").exists()


class TestToolingVersion:
    def test_version_is_a_string(self):
        from orchestrator.cli import _tooling_version

        ver = _tooling_version()
        assert ver is None or isinstance(ver, str)

    def test_version_not_empty_in_git_repo(self):
        from orchestrator.cli import _tooling_version

        ver = _tooling_version()
        # We're running inside agent_hq which is a git repo
        assert ver is not None
        assert len(ver) > 0
