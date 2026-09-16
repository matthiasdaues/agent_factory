"""Integration tests for code-change detection and the reconciliation flag.

Owned contracts:
  - Adapter detects source code changes since cycle entry (standard risk)
  - Adapter detects canonical artifact changes since cycle entry (standard risk)
  - No relevant changes reports reconciliation as not applicable (standard risk)
  - code_changed flag reaches the evaluator via cmd_assess (standard risk)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CYCLE_SCRIPT = REPO_ROOT / "packages" / "factory" / "scripts" / "cycle"
DELIVERY_YAML = REPO_ROOT / "packages" / "factory" / "engine" / "models" / "delivery.yaml"


def run_cycle(args: list[str], cwd: str | Path | None = None,
              env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ}
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(CYCLE_SCRIPT)] + args,
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
    )


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + list(args),
        capture_output=True,
        text=True,
        cwd=repo,
    )


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@test.com")
    _git(repo, "config", "user.name", "Test")
    readme = repo / "README.md"
    readme.write_text("# test\n")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "initial")
    return repo


def _create_workstream(repo: Path, tmp_path: Path, name: str = "ws") -> Path:
    state_path = tmp_path / "cycles" / f"{name}.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    result = run_cycle([
        "select",
        "--state", str(state_path),
        "--topic", "test workstream",
        "IDEA",
        "--model", str(DELIVERY_YAML),
    ], cwd=repo, env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")})
    assert result.returncode == 0, result.stderr
    return state_path


class TestNoChanges:
    def test_same_commit_reports_no_changes(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = _create_workstream(repo, tmp_path)

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "no relevant changes" in result.stdout

    def test_unrelated_file_change_reports_no_changes(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = _create_workstream(repo, tmp_path)

        (repo / "notes.txt").write_text("unrelated\n")
        _git(repo, "add", "notes.txt")
        _git(repo, "commit", "-m", "unrelated change")

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "no relevant changes" in result.stdout


class TestSourceCodeChanges:
    def test_packages_change_detected(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = _create_workstream(repo, tmp_path)

        pkg = repo / "packages" / "mod.py"
        pkg.parent.mkdir(parents=True)
        pkg.write_text("x = 1\n")
        _git(repo, "add", "packages/mod.py")
        _git(repo, "commit", "-m", "add package file")

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "changes detected" in result.stdout

    def test_src_change_detected(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = _create_workstream(repo, tmp_path)

        src = repo / "src" / "main.py"
        src.parent.mkdir(parents=True)
        src.write_text("print('hello')\n")
        _git(repo, "add", "src/main.py")
        _git(repo, "commit", "-m", "add src file")

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "changes detected" in result.stdout

    def test_tests_change_detected(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = _create_workstream(repo, tmp_path)

        t = repo / "tests" / "test_x.py"
        t.parent.mkdir(parents=True)
        t.write_text("def test_x(): pass\n")
        _git(repo, "add", "tests/test_x.py")
        _git(repo, "commit", "-m", "add test file")

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "changes detected" in result.stdout


class TestCanonicalArtifactChanges:
    def test_scope_map_change_detected(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = _create_workstream(repo, tmp_path)

        sm = repo / "docs" / "spec" / "scope-map.md"
        sm.parent.mkdir(parents=True)
        sm.write_text("# Scope Map\n")
        _git(repo, "add", "docs/spec/scope-map.md")
        _git(repo, "commit", "-m", "add scope map")

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "changes detected" in result.stdout

    def test_feature_file_change_detected(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = _create_workstream(repo, tmp_path)

        feat = repo / "docs" / "spec" / "auth.feature"
        feat.parent.mkdir(parents=True)
        feat.write_text("Feature: Auth\n")
        _git(repo, "add", "docs/spec/auth.feature")
        _git(repo, "commit", "-m", "add feature file")

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "changes detected" in result.stdout

    def test_entity_model_change_detected(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = _create_workstream(repo, tmp_path)

        em = repo / "docs" / "spec" / "entity-model.yaml"
        em.parent.mkdir(parents=True)
        em.write_text("entities: []\n")
        _git(repo, "add", "docs/spec/entity-model.yaml")
        _git(repo, "commit", "-m", "add entity model")

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "changes detected" in result.stdout

    def test_architecture_dsl_change_detected(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = _create_workstream(repo, tmp_path)

        dsl = repo / "docs" / "arc42" / "architecture.dsl"
        dsl.parent.mkdir(parents=True)
        dsl.write_text("workspace {}\n")
        _git(repo, "add", "docs/arc42/architecture.dsl")
        _git(repo, "commit", "-m", "add dsl")

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "changes detected" in result.stdout


class TestEdgeCases:
    def test_missing_entry_commit_reports_no_changes(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = tmp_path / "cycles" / "no-entry.yaml"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(yaml.safe_dump({
            "schema_version": 1,
            "workstream_id": "no-entry",
            "topic": "no entry commit",
            "cycle": "IDEA",
            "revision": 1,
            "attempt": 1,
            "origin_ref": None,
            "work": None,
            "delegation": None,
        }))

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "no relevant changes" in result.stdout

    def test_transition_resets_entry_commit(self, tmp_path):
        repo = _init_repo(tmp_path)
        state_path = _create_workstream(repo, tmp_path)

        pkg = repo / "packages" / "mod.py"
        pkg.parent.mkdir(parents=True)
        pkg.write_text("x = 1\n")
        _git(repo, "add", "packages/mod.py")
        _git(repo, "commit", "-m", "add package file")

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert "changes detected" in result.stdout

        run_cycle([
            "select", "--state", str(state_path), "CONCEPT",
            "--model", str(DELIVERY_YAML),
        ], cwd=repo, env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")})

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            cwd=repo,
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert result.returncode == 0
        assert "no relevant changes" in result.stdout
