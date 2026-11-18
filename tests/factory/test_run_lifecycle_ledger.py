"""The ledger fields of the run lifecycle (docs/spec/features/run-lifecycle.feature).

Rule: Factory maintainer finds in the dispatch contract exactly the fields
the ledger holds.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml
from conftest import SOURCE_SCRIPTS_DIR

import dispatch_lib as lib

DISPATCH = SOURCE_SCRIPTS_DIR / "dispatch"
SHA = "a" * 40

OLD_LEDGER = f"""---
mode: automated
closed: false
invocation_branch: feature/login
branch_root: {SHA}
branch_head: {SHA}
stories:
  ST-0350:
    id: ST-0350
    wave: 1
    status: dispatched
    deps: []
    branch: story/ST-0350
    worktree: null
    feature_branch: feature/login
    base_sha: {SHA}
    tier: economy
    reason: null
    gate_results: {{}}
"""


def full_ledger() -> lib.Ledger:
    """A ledger in which every field the code can write holds a value."""
    ledger = lib.Ledger()
    ledger.mode = "by-hand"
    ledger.feature_branch = "feature/login"
    ledger.branch_root = SHA
    ledger.branch_head = SHA
    ledger.stories["ST-0350"] = lib.StoryEntry(
        id="ST-0350",
        wave=1,
        status=lib.StoryState.DONE,
        deps=["ST-0349"],
        branch="story/ST-0350",
        worktree="/tmp/w",
        feature_branch="feature/login",
        base_sha=SHA,
        tier="economy",
        reason="merged",
        attempts=[{"tier": "economy"}],
        escalation_granted=True,
        verify_base="pass",
        commit_sha=SHA,
        failure_class="acceptance_unmet",
        evidence="report.json",
        manifest_recoveries=[{"at": "now"}],
        active_session="impl",
        active_tier="economy",
    )
    ledger.waves.append(lib.WaveCloseout(number=1, branch_head=SHA))
    return ledger


def written(ledger: lib.Ledger, path: Path) -> dict:
    ledger.save(path)
    return yaml.safe_load(path.read_text())


@pytest.mark.spec("RL-17-CT-01")
@pytest.mark.parametrize("mode", lib.LEDGER_MODES)
def test_RL_17_CT_01_the_ledger_uses_the_names_of_the_run(tmp_path, mode):
    """Scenario: The ledger uses the run's names.
    Scenario: The ledger holds no field that no command reads."""
    ledger = full_ledger()
    ledger.mode = mode

    data = written(ledger, tmp_path / "dispatch-ledger.yaml")

    assert data["mode"] == mode
    assert data["feature_branch"] == "feature/login"
    assert "invocation_branch" not in data
    assert "closed" not in data
    assert all("gate_results" not in entry for entry in data["stories"].values())


@pytest.mark.spec("RL-17-CT-01")
def test_RL_17_CT_01_a_new_ledger_is_orchestrated():
    """dispatch init without --mode writes orchestrated (BR-111)."""
    assert lib.Ledger().mode == "orchestrated"
    assert lib.LEDGER_MODES == ("orchestrated", "by-hand")


@pytest.mark.spec("RL-17-CT-02")
def test_RL_17_CT_02_the_old_names_load_as_the_new_ones(tmp_path):
    path = tmp_path / "dispatch-ledger.yaml"
    path.write_text(OLD_LEDGER)

    ledger = lib.Ledger.load(path)

    assert ledger.mode == "orchestrated"
    assert ledger.feature_branch == "feature/login"


@pytest.mark.spec("RL-17-CT-02")
def test_RL_17_CT_02_mark_blocked_writes_only_the_new_names(tmp_path):
    """Scenario: dispatch reads the old names of a ledger and writes only the new ones."""
    path = tmp_path / "dispatch-ledger.yaml"
    path.write_text(OLD_LEDGER)

    result = subprocess.run(
        [str(DISPATCH), "--ledger", str(path), "mark-blocked", "ST-0350",
         "--reason", "design question"],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )

    assert result.returncode == 0, result.stderr
    data = yaml.safe_load(path.read_text())
    assert data["feature_branch"] == "feature/login"
    assert data["mode"] == "orchestrated"
    assert "invocation_branch" not in data
    assert "closed" not in data
    assert "gate_results" not in data["stories"]["ST-0350"]
    assert data["stories"]["ST-0350"]["status"] == "blocked"
