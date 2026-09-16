"""Integration tests for the cycle select adapter.

Owned contracts:
  - cycle select creates state file on new workstream (standard risk)
  - cycle select transitions existing workstream (standard risk)
  - Attempt resets to 1 on cycle change (standard risk)
  - Revision increments on each transition (standard risk)
  - Undeclared route produces warning and state update (standard risk)
  - Invalid model produces error and no state write (standard risk)
  - Session binding appears after creation (standard risk)
  - origin_ref recorded when proposal path given (standard risk)
  - cycle_entry_commit recorded on create and transition (standard risk)
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


class TestCreateWorkstream:
    def test_creates_state_file(self, tmp_path):
        state = tmp_path / "cycles" / "test-ws.yaml"
        state.parent.mkdir(parents=True)
        result = run_cycle([
            "select",
            "--state", str(state),
            "--topic", "Test workstream",
            "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        assert result.returncode == 0, result.stderr
        assert state.exists()
        data = yaml.safe_load(state.read_text())
        assert data["topic"] == "Test workstream"
        assert data["cycle"] == "IDEA"
        assert data["revision"] == 1
        assert data["attempt"] == 1

    def test_state_has_schema_version(self, tmp_path):
        state = tmp_path / "cycles" / "versioned.yaml"
        state.parent.mkdir(parents=True)
        run_cycle([
            "select", "--state", str(state),
            "--topic", "Versioned", "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        data = yaml.safe_load(state.read_text())
        assert data["schema_version"] == 1

    def test_workstream_id_derived_from_filename(self, tmp_path):
        state = tmp_path / "cycles" / "my-project.yaml"
        state.parent.mkdir(parents=True)
        run_cycle([
            "select", "--state", str(state),
            "--topic", "My project", "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        data = yaml.safe_load(state.read_text())
        assert data["workstream_id"] == "my-project"


class TestSessionBinding:
    def test_binding_created(self, tmp_path, monkeypatch):
        state = tmp_path / "cycles" / "binding-test.yaml"
        state.parent.mkdir(parents=True)
        bindings = tmp_path / "session-bindings"
        monkeypatch.setenv("CYCLE_BINDINGS_DIR", str(bindings))
        result = run_cycle([
            "select", "--state", str(state),
            "--topic", "Binding test", "IDEA",
            "--model", str(DELIVERY_YAML),
        ], env_extra={"CYCLE_BINDINGS_DIR": str(bindings)})
        assert result.returncode == 0, result.stderr
        assert bindings.exists()
        binding_files = list(bindings.glob("*.yaml"))
        assert len(binding_files) >= 1


class TestOriginRef:
    def test_origin_ref_recorded(self, tmp_path):
        state = tmp_path / "cycles" / "with-ref.yaml"
        state.parent.mkdir(parents=True)
        proposal = tmp_path / "proposal.md"
        proposal.write_text("# Proposal")
        result = run_cycle([
            "select", "--state", str(state),
            "--topic", "With ref", "IDEA",
            "--model", str(DELIVERY_YAML),
            "--work", str(proposal),
        ])
        assert result.returncode == 0, result.stderr
        data = yaml.safe_load(state.read_text())
        assert data["origin_ref"] == str(proposal)

    def test_no_origin_ref_when_not_given(self, tmp_path):
        state = tmp_path / "cycles" / "no-ref.yaml"
        state.parent.mkdir(parents=True)
        run_cycle([
            "select", "--state", str(state),
            "--topic", "No ref", "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        data = yaml.safe_load(state.read_text())
        assert data.get("origin_ref") is None


class TestTransition:
    def test_transitions_existing_workstream(self, tmp_path):
        state = tmp_path / "cycles" / "transition.yaml"
        state.parent.mkdir(parents=True)
        run_cycle([
            "select", "--state", str(state),
            "--topic", "Transition test", "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        result = run_cycle([
            "select", "--state", str(state), "CONCEPT",
            "--model", str(DELIVERY_YAML),
        ])
        assert result.returncode == 0, result.stderr
        data = yaml.safe_load(state.read_text())
        assert data["cycle"] == "CONCEPT"

    def test_attempt_resets_on_cycle_change(self, tmp_path):
        state = tmp_path / "cycles" / "attempt-reset.yaml"
        state.parent.mkdir(parents=True)
        run_cycle([
            "select", "--state", str(state),
            "--topic", "Attempt test", "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        # Manually set attempt to 3 to simulate retries
        data = yaml.safe_load(state.read_text())
        data["attempt"] = 3
        state.write_text(yaml.dump(data))

        run_cycle([
            "select", "--state", str(state), "CONCEPT",
            "--model", str(DELIVERY_YAML),
        ])
        data = yaml.safe_load(state.read_text())
        assert data["attempt"] == 1

    def test_revision_increments(self, tmp_path):
        state = tmp_path / "cycles" / "revision.yaml"
        state.parent.mkdir(parents=True)
        run_cycle([
            "select", "--state", str(state),
            "--topic", "Revision test", "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        data = yaml.safe_load(state.read_text())
        assert data["revision"] == 1

        run_cycle([
            "select", "--state", str(state), "CONCEPT",
            "--model", str(DELIVERY_YAML),
        ])
        data = yaml.safe_load(state.read_text())
        assert data["revision"] == 2

        run_cycle([
            "select", "--state", str(state), "ROADMAP",
            "--model", str(DELIVERY_YAML),
        ])
        data = yaml.safe_load(state.read_text())
        assert data["revision"] == 3


class TestUndeclaredRoute:
    def test_undeclared_route_warns_and_records(self, tmp_path):
        state = tmp_path / "cycles" / "undeclared.yaml"
        state.parent.mkdir(parents=True)
        run_cycle([
            "select", "--state", str(state),
            "--topic", "Undeclared test", "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        result = run_cycle([
            "select", "--state", str(state), "REALIZE",
            "--model", str(DELIVERY_YAML),
        ])
        assert result.returncode == 0
        assert "warning" in result.stderr.lower() or "warning" in result.stdout.lower()
        data = yaml.safe_load(state.read_text())
        assert data["cycle"] == "REALIZE"


class TestInvalidModel:
    def test_invalid_model_errors_no_state_write(self, tmp_path):
        bad_model = tmp_path / "bad-delivery.yaml"
        bad_model.write_text("not_a_valid_model: true\n")
        state = tmp_path / "cycles" / "invalid.yaml"
        state.parent.mkdir(parents=True)
        result = run_cycle([
            "select", "--state", str(state),
            "--topic", "Invalid model", "IDEA",
            "--model", str(bad_model),
        ])
        assert result.returncode == 2
        assert not state.exists()


class TestExitCodes:
    def test_success_exits_zero(self, tmp_path):
        state = tmp_path / "cycles" / "exit-zero.yaml"
        state.parent.mkdir(parents=True)
        result = run_cycle([
            "select", "--state", str(state),
            "--topic", "Exit test", "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        assert result.returncode == 0

    def test_invalid_input_exits_two(self, tmp_path):
        state = tmp_path / "cycles" / "exit-two.yaml"
        state.parent.mkdir(parents=True)
        result = run_cycle([
            "select", "--state", str(state),
            "--topic", "Exit test", "INVALID_CYCLE",
            "--model", str(DELIVERY_YAML),
        ])
        assert result.returncode == 2


class TestCycleEntryCommit:
    def test_create_records_cycle_entry_commit(self, tmp_path):
        state = tmp_path / "cycles" / "entry-commit.yaml"
        state.parent.mkdir(parents=True)
        run_cycle([
            "select", "--state", str(state),
            "--topic", "Entry commit test", "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        data = yaml.safe_load(state.read_text())
        assert "cycle_entry_commit" in data
        assert isinstance(data["cycle_entry_commit"], str)
        assert len(data["cycle_entry_commit"]) >= 7

    def test_transition_updates_cycle_entry_commit(self, tmp_path):
        state = tmp_path / "cycles" / "entry-update.yaml"
        state.parent.mkdir(parents=True)
        run_cycle([
            "select", "--state", str(state),
            "--topic", "Entry update test", "IDEA",
            "--model", str(DELIVERY_YAML),
        ])
        data_before = yaml.safe_load(state.read_text())
        commit_before = data_before["cycle_entry_commit"]

        run_cycle([
            "select", "--state", str(state), "CONCEPT",
            "--model", str(DELIVERY_YAML),
        ])
        data_after = yaml.safe_load(state.read_text())
        assert "cycle_entry_commit" in data_after
        assert isinstance(data_after["cycle_entry_commit"], str)
        assert len(data_after["cycle_entry_commit"]) >= 7
