"""Regression evidence for scoped background permissions in ``trigger``.

These tests enter through the real public dispatch path and replace only the
subprocess execution seam. The captured value is therefore the exact child
argv that ``trigger`` would launch for Claude or Copilot.
"""

from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_TRIGGER_SCRIPT = _ROOT / "factory" / "scripts" / "trigger"
_loader = SourceFileLoader("trigger_background_permissions", str(_TRIGGER_SCRIPT))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
trigger = importlib.util.module_from_spec(_spec)
sys.modules[_loader.name] = trigger
_loader.exec_module(trigger)


def _background_argv(cli: str, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Capture the real background child argv without launching the CLI."""
    captured: list[str] = []

    def capture_command(command: list[str], cwd: Path) -> int:
        captured.extend(command)
        assert cwd == _ROOT
        return 0

    monkeypatch.setattr(trigger, "run_background", capture_command)

    exit_code = trigger.main(
        [
            "agent",
            "requirements-agent",
            "--background",
            "--cli",
            cli,
            "--cwd",
            str(_ROOT),
        ]
    )

    assert exit_code == 0
    return captured


def _option_value(argv: list[str], option: str) -> str:
    """Return the value immediately following a required argv option."""
    return argv[argv.index(option) + 1]


class TestBackgroundPermissionArgv:
    """UC-04/UC-12 evidence for the shipped background permission policy."""

    def test_UC_04_BR_011_claude_argv_is_scoped(self, monkeypatch):
        argv = _background_argv("claude", monkeypatch)

        assert argv[0] == "claude"
        assert "--dangerously-skip-permissions" not in argv
        assert "--allow-all-tools" not in argv
        assert "--allowedTools" in argv
        assert "--disallowedTools" in argv

        allowed = set(_option_value(argv, "--allowedTools").split(","))
        denied = set(_option_value(argv, "--disallowedTools").split(","))

        assert {
            "Bash(factory/scripts/spec-lint *)",
            "Bash(factory/scripts/arch-lint *)",
            "Bash(factory/scripts/backlog-lint *)",
            "Bash(factory/scripts/matrix-lint *)",
            "Bash(factory/scripts/statemachine-lint *)",
            "Bash(factory/scripts/index-lint *)",
            "Bash(factory/scripts/transition-lint *)",
            "Bash(factory/scripts/mdformat *)",
            "Bash(uvx ruff check *)",
            "Bash(uvx ruff format *)",
            "Bash(uv run mdformat *)",
            "Bash(uv run ruff check *)",
            "Bash(uv run ruff format *)",
            "Bash(uv run pytest *)",
        } <= allowed
        assert {
            "Bash(git push *)",
            "Bash(git reset --hard *)",
            "Bash(git clean -fd *)",
            "Bash(git clean -f *)",
            "Bash(git branch -D *)",
            "Bash(git checkout . *)",
            "Bash(git restore . *)",
        } <= denied
        assert {
            "Bash(python *)",
            "Bash(python3 *)",
            "Bash(uv *)",
            "Bash(uvx *)",
            "Bash(npm *)",
        }.isdisjoint(allowed)

    def test_UC_12_BR_047_copilot_argv_is_scoped(self, monkeypatch):
        argv = _background_argv("copilot", monkeypatch)

        assert argv[0] == "copilot"
        assert "--allow-all-tools" not in argv
        assert "--dangerously-skip-permissions" not in argv
        assert "--allow-tool" in argv
        assert "--deny-tool" in argv

        allowed = set(_option_value(argv, "--allow-tool").split(","))
        denied = set(_option_value(argv, "--deny-tool").split(","))

        assert {
            "shell(factory/scripts/spec-lint:*)",
            "shell(factory/scripts/arch-lint:*)",
            "shell(factory/scripts/backlog-lint:*)",
            "shell(factory/scripts/matrix-lint:*)",
            "shell(factory/scripts/statemachine-lint:*)",
            "shell(factory/scripts/index-lint:*)",
            "shell(factory/scripts/transition-lint:*)",
            "shell(factory/scripts/mdformat:*)",
            "shell(uvx ruff check:*)",
            "shell(uvx ruff format:*)",
            "shell(uv run mdformat:*)",
            "shell(uv run ruff check:*)",
            "shell(uv run ruff format:*)",
            "shell(uv run pytest:*)",
        } <= allowed
        assert {
            "shell(git push:*)",
            "shell(git reset --hard:*)",
            "shell(git clean -fd:*)",
            "shell(git clean -f:*)",
            "shell(git branch -D)",
            "shell(git checkout .)",
            "shell(git restore .)",
        } <= denied
        assert {
            "shell(python:*)",
            "shell(python3:*)",
            "shell(uv:*)",
            "shell(uvx:*)",
            "shell(npm:*)",
        }.isdisjoint(allowed)
