"""Regression tests for remove-factory (ST-0305).

Each test builds a small installed tree with a hand-written removal manifest,
runs remove-factory against it, and checks what is left on disk.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import load_script

ORIENTATION_BEGIN = "<!-- >>> agent_factory orientation >>>"
ORIENTATION_END = "<!-- <<< agent_factory orientation <<< -->"
CLAUDE_FRESHNESS = '"$CLAUDE_PROJECT_DIR"/.claude/hooks/check-factory-freshness.sh'


@pytest.fixture(scope="module")
def remove_factory():
    return load_script("remove-factory")


def _install(target: Path, **manifest) -> None:
    """Write a removal manifest and the factory tree it points into."""
    factory = target / ".agent-factory/factory"
    (factory / "config").mkdir(parents=True)
    (factory / "config/AGENTS.md").write_text("factory orientation\n")
    payload = {"version": 1, "remove_paths": [], "orientation": {}}
    payload.update(manifest)
    (target / ".agent-factory/install.json").write_text(json.dumps(payload))


def _run(remove_factory, target: Path) -> int:
    return remove_factory.main(["--target", str(target)])


# --- BUG-0074: headers recorded as dictionaries -----------------------------


@pytest.mark.parametrize(
    ("orig_final_newline", "expected"),
    [(True, "# Project\n"), (False, "# Project")],
)
def test_bug_0074_strips_header_recorded_as_dictionary(
    remove_factory, tmp_path, orig_final_newline, expected
):
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        f"{ORIENTATION_BEGIN}\nread the rules\n{ORIENTATION_END}\n\n# Project\n"
    )
    _install(
        tmp_path,
        orientation={
            "AGENTS.md": {
                "status": "injected",
                "block_digest": "abc",
                "orig_final_newline": orig_final_newline,
            }
        },
    )

    assert _run(remove_factory, tmp_path) == 0

    assert agents.read_text() == expected


def test_bug_0074_keeps_project_link_when_linked_entry_is_dictionary(
    remove_factory, tmp_path
):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/own.md").write_text("project orientation\n")
    agents = tmp_path / "AGENTS.md"
    agents.symlink_to("docs/own.md")
    _install(
        tmp_path,
        orientation={"AGENTS.md": {"status": "linked", "block_digest": ""}},
        remove_paths=["AGENTS.md"],
    )

    assert _run(remove_factory, tmp_path) == 0

    assert agents.is_symlink()
    assert agents.read_text() == "project orientation\n"


# --- BUG-0075: freshness hook stays wired -----------------------------------


def test_bug_0075_unwires_freshness_hook_and_prunes_hooks_dir(
    remove_factory, tmp_path
):
    hooks_dir = tmp_path / ".claude/hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "check-factory-freshness.sh").symlink_to(
        "../../.agent-factory/factory/config/hooks/check-factory-freshness.sh"
    )
    project_hook = {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "./own-check.sh"}],
    }
    settings = tmp_path / ".claude/settings.json"
    settings.write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        project_hook,
                        {
                            "matcher": "Bash",
                            "hooks": [{"type": "command", "command": CLAUDE_FRESHNESS}],
                        },
                    ]
                }
            },
            indent=2,
        )
        + "\n"
    )
    _install(
        tmp_path,
        claude_settings_existed=True,
        remove_paths=[".claude/hooks/check-factory-freshness.sh"],
    )

    assert _run(remove_factory, tmp_path) == 0

    assert CLAUDE_FRESHNESS not in settings.read_text()
    assert json.loads(settings.read_text()) == {"hooks": {"PreToolUse": [project_hook]}}
    assert not hooks_dir.exists()


# --- BUG-0076: a stale owner file blocks removal for good -------------------


def _dead_pid() -> int:
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    return child.pid


def test_bug_0076_owner_file_of_dead_process_does_not_block(
    remove_factory, tmp_path
):
    _install(tmp_path)
    control = tmp_path / ".agent-factory/usage/control"
    control.mkdir(parents=True)
    (control / "state.json").write_text(
        json.dumps({"mode": "active", "generation": "g1"})
    )
    (control / "remove-owner").write_text(str(_dead_pid()))

    assert _run(remove_factory, tmp_path) == 0

    assert not (tmp_path / ".agent-factory").exists()


def test_bug_0076_owner_file_of_live_process_still_blocks(remove_factory, tmp_path):
    _install(tmp_path)
    control = tmp_path / ".agent-factory/usage/control"
    control.mkdir(parents=True)
    (control / "state.json").write_text(
        json.dumps({"mode": "active", "generation": "g1"})
    )
    (control / "remove-owner").write_text(str(os.getpid()))

    assert _run(remove_factory, tmp_path) == 1

    assert (tmp_path / ".agent-factory/install.json").exists()


# --- BUG-0079: a pre-existing .codex/ directory is deleted -------------------


def test_bug_0079_keeps_codex_dir_that_existed_before_install(
    remove_factory, tmp_path
):
    (tmp_path / ".codex").mkdir()
    _install(tmp_path)

    assert _run(remove_factory, tmp_path) == 0

    assert (tmp_path / ".codex").is_dir()


def test_bug_0079_removes_codex_dir_the_install_created(remove_factory, tmp_path):
    (tmp_path / ".codex/hooks").mkdir(parents=True)
    _install(tmp_path, remove_paths=[".codex"])

    assert _run(remove_factory, tmp_path) == 0

    assert not (tmp_path / ".codex").exists()


def test_bug_0076_concurrent_takeover_of_stale_owner_lets_one_removal_win(
    remove_factory, tmp_path, monkeypatch
):
    owner = tmp_path / "remove-owner"
    owner.write_text(str(_dead_pid()))
    real_snapshot = remove_factory._stale_snapshot
    competitor: list[bool] = []
    calls: list[Path] = []

    def snapshot_then_competitor_claims(path):
        snapshot = real_snapshot(path)
        calls.append(path)
        if len(calls) == 1:
            # Removal B runs its whole claim between A's read and A's takeover.
            competitor.append(remove_factory._claim_owner(path))
        return snapshot

    monkeypatch.setattr(
        remove_factory, "_stale_snapshot", snapshot_then_competitor_claims
    )
    first_claim = remove_factory._claim_owner(owner)

    assert competitor == [True]
    assert first_claim is False
    assert [p.name for p in tmp_path.iterdir()] == ["remove-owner"]


@pytest.mark.parametrize(("age", "claimed"), [(60, True), (0, False)])
def test_bug_0076_empty_owner_file_expires_after_grace_period(
    remove_factory, tmp_path, age, claimed
):
    owner = tmp_path / "remove-owner"
    owner.write_text("")
    then = owner.stat().st_mtime - age
    os.utime(owner, (then, then))

    assert age == 0 or age > remove_factory.OWNER_WRITE_GRACE_SECONDS
    assert remove_factory._claim_owner(owner) is claimed
