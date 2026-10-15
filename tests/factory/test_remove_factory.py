"""Regression tests for remove-factory (ST-0305).

Each test builds a small installed tree with a hand-written removal manifest,
runs remove-factory against it, and checks what is left on disk.
"""

from __future__ import annotations

import json
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
