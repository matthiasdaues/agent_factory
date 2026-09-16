"""Integration tests for cycle list and the continue-workstream flow.

Owned contracts:
  - cycle list shows workstreams with topic and cycle (standard risk)
  - cycle list with no workstreams shows empty message (standard risk)
  - cycle assess writes a session binding (standard risk)
  - Corrupted state files are skipped during listing (standard risk)
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


def run_cycle(args: list[str], env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ}
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(CYCLE_SCRIPT)] + args,
        capture_output=True,
        text=True,
        env=env,
    )


def _create_workstream(tmp_path: Path, name: str, topic: str, cycle: str = "IDEA") -> Path:
    state_path = tmp_path / "cycles" / f"{name}.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    result = run_cycle([
        "select",
        "--state", str(state_path),
        "--topic", topic,
        cycle,
        "--model", str(DELIVERY_YAML),
    ], env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")})
    assert result.returncode == 0, result.stderr
    return state_path


class TestListWorkstreams:
    def test_lists_existing_workstream(self, tmp_path):
        _create_workstream(tmp_path, "atlas", "Build the Atlas platform")
        result = run_cycle(["list", "--dir", str(tmp_path / "cycles")])
        assert result.returncode == 0
        assert "atlas" in result.stdout
        assert "IDEA" in result.stdout
        assert "Build the Atlas platform" in result.stdout

    def test_lists_multiple_workstreams(self, tmp_path):
        _create_workstream(tmp_path, "atlas", "Build the Atlas platform")
        _create_workstream(tmp_path, "borealis", "Research Borealis protocol", "CONCEPT")
        result = run_cycle(["list", "--dir", str(tmp_path / "cycles")])
        assert result.returncode == 0
        assert "atlas" in result.stdout
        assert "borealis" in result.stdout
        assert "IDEA" in result.stdout
        assert "CONCEPT" in result.stdout

    def test_empty_directory_shows_no_workstreams(self, tmp_path):
        cycles_dir = tmp_path / "cycles"
        cycles_dir.mkdir(parents=True)
        result = run_cycle(["list", "--dir", str(cycles_dir)])
        assert result.returncode == 0
        assert "no workstreams found" in result.stdout

    def test_nonexistent_directory_shows_no_workstreams(self, tmp_path):
        result = run_cycle(["list", "--dir", str(tmp_path / "nonexistent")])
        assert result.returncode == 0
        assert "no workstreams found" in result.stdout

    def test_corrupted_file_skipped(self, tmp_path):
        _create_workstream(tmp_path, "good", "Good workstream")
        bad = tmp_path / "cycles" / "bad.yaml"
        bad.write_text(":::not valid yaml{{{\n")
        result = run_cycle(["list", "--dir", str(tmp_path / "cycles")])
        assert result.returncode == 0
        assert "good" in result.stdout
        assert "bad" not in result.stdout

    def test_non_mapping_file_skipped(self, tmp_path):
        _create_workstream(tmp_path, "good", "Good workstream")
        bare = tmp_path / "cycles" / "bare.yaml"
        bare.write_text("just a string\n")
        result = run_cycle(["list", "--dir", str(tmp_path / "cycles")])
        assert result.returncode == 0
        assert "good" in result.stdout
        assert "bare" not in result.stdout

    def test_output_contains_revision(self, tmp_path):
        _create_workstream(tmp_path, "atlas", "Atlas")
        result = run_cycle(["list", "--dir", str(tmp_path / "cycles")])
        assert "rev 1" in result.stdout


class TestAssessWritesBinding:
    def test_assess_creates_session_binding(self, tmp_path):
        state_path = _create_workstream(tmp_path, "atlas", "Atlas")
        bindings_dir = tmp_path / "bindings"

        result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            env_extra={"CYCLE_BINDINGS_DIR": str(bindings_dir)},
        )
        assert result.returncode == 0

        binding_files = list(bindings_dir.glob("*.yaml"))
        assert len(binding_files) >= 1
        binding = yaml.safe_load(binding_files[-1].read_text())
        assert binding["workstream_id"] == "atlas"
        assert binding["state_path"] == str(state_path)

    def test_assess_binding_has_revision_and_digest(self, tmp_path):
        state_path = _create_workstream(tmp_path, "atlas", "Atlas")
        bindings_dir = tmp_path / "bindings"

        run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            env_extra={"CYCLE_BINDINGS_DIR": str(bindings_dir)},
        )

        binding_files = list(bindings_dir.glob("*.yaml"))
        binding = yaml.safe_load(binding_files[-1].read_text())
        assert "revision" in binding
        assert "digest" in binding
        assert isinstance(binding["digest"], str)
        assert len(binding["digest"]) == 64


class TestContinueFlow:
    def test_list_then_assess_produces_recommendations(self, tmp_path):
        state_path = _create_workstream(tmp_path, "atlas", "Atlas")

        list_result = run_cycle(["list", "--dir", str(tmp_path / "cycles")])
        assert list_result.returncode == 0
        assert "atlas" in list_result.stdout

        assess_result = run_cycle(
            ["assess", "--state", str(state_path), "--model", str(DELIVERY_YAML)],
            env_extra={"CYCLE_BINDINGS_DIR": str(tmp_path / "bindings")},
        )
        assert assess_result.returncode == 0
        assert "Assessment for cycle IDEA" in assess_result.stdout

    def test_factory_never_auto_selects(self, tmp_path):
        _create_workstream(tmp_path, "atlas", "Atlas")
        _create_workstream(tmp_path, "borealis", "Borealis")
        result = run_cycle(["list", "--dir", str(tmp_path / "cycles")])
        assert result.returncode == 0
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        assert len(lines) == 2


class TestExitCodes:
    def test_list_exits_zero_with_workstreams(self, tmp_path):
        _create_workstream(tmp_path, "atlas", "Atlas")
        result = run_cycle(["list", "--dir", str(tmp_path / "cycles")])
        assert result.returncode == 0

    def test_list_exits_zero_without_workstreams(self, tmp_path):
        result = run_cycle(["list", "--dir", str(tmp_path / "nonexistent")])
        assert result.returncode == 0
