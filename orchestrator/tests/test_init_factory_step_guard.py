"""Tests for the step-guard wiring installed by `factory/scripts/init-factory`.

These tests cover the new CLI-specific adapters that normalize tool events
before invoking `factory/scripts/step-guard`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "init-factory"
_loader = SourceFileLoader("init_factory_step_guard", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("init_factory_step_guard", _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules["init_factory_step_guard"] = init_factory
_loader.exec_module(init_factory)


def _run_init(target: Path) -> int:
    return init_factory.main(
        [
            "--target",
            str(target),
            "--source",
            str(_ROOT),
            "--project-name",
            "Test Project",
        ]
    )


def _commands(settings: dict, event: str) -> list[str]:
    return [
        hook.get("command", "")
        for entry in settings.get("hooks", {}).get(event, [])
        for hook in entry.get("hooks", [])
        if isinstance(hook, dict)
    ]


def test_fresh_install_wires_step_guard_for_all_clis(tmp_path: Path) -> None:
    assert _run_init(tmp_path) == 0

    claude_hook = tmp_path / ".claude" / "hooks" / "step-guard.sh"
    assert claude_hook.is_symlink()
    claude_settings = json.loads(
        (tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    assert _commands(claude_settings, "PreToolUse") == [
        '"$CLAUDE_PROJECT_DIR"/.claude/hooks/block-dangerous-git.sh',
        'GUARD_TYPE=read "$CLAUDE_PROJECT_DIR"/.claude/hooks/step-guard.sh',
        'GUARD_TYPE=write "$CLAUDE_PROJECT_DIR"/.claude/hooks/step-guard.sh',
        'GUARD_TYPE=write "$CLAUDE_PROJECT_DIR"/.claude/hooks/step-guard.sh',
        'GUARD_TYPE=bash "$CLAUDE_PROJECT_DIR"/.claude/hooks/step-guard.sh',
    ]

    codex_hook = tmp_path / ".codex" / "hooks" / "step-guard.sh"
    assert codex_hook.is_symlink()
    codex = json.loads((tmp_path / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    assert codex["hooks"]["PreToolUse"]
    codex_commands = _commands(codex, "PreToolUse")
    assert (
        'GUARD_TYPE=read "$(git rev-parse --show-toplevel)"/.codex/hooks/step-guard.sh'
        in codex_commands
    )
    assert (
        'GUARD_TYPE=write "$(git rev-parse --show-toplevel)"/.codex/hooks/step-guard.sh'
        in codex_commands
    )
    assert (
        'GUARD_TYPE=bash "$(git rev-parse --show-toplevel)"/.codex/hooks/step-guard.sh'
        in codex_commands
    )

    copilot_hook = tmp_path / ".github" / "hooks" / "step-guard.sh"
    assert copilot_hook.is_symlink()
    copilot_config = json.loads(
        (tmp_path / ".github" / "hooks" / "step-guard.json").read_text(encoding="utf-8")
    )
    assert copilot_config["version"] == 1
    assert len(copilot_config["hooks"]["preToolUse"]) == 6
    assert (tmp_path / ".pi" / "extensions" / "step-guard.ts").is_symlink()


def test_second_run_leaves_step_guard_assets_unchanged(tmp_path: Path) -> None:
    assert _run_init(tmp_path) == 0
    snapshot = {
        path.relative_to(tmp_path).as_posix(): path.read_text(encoding="utf-8")
        for path in (
            tmp_path / ".claude" / "settings.json",
            tmp_path / ".codex" / "hooks.json",
            tmp_path / ".github" / "hooks" / "step-guard.json",
        )
    }

    assert _run_init(tmp_path) == 0

    for rel, text in snapshot.items():
        assert (tmp_path / rel).read_text(encoding="utf-8") == text
