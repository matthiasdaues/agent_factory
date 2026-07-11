"""Tests for the git-safety guardrail hook wired in by `factory/scripts/init-factory`.

`init-factory` (the standalone project-init script, not the `orchestrate init`
CLI subcommand covered by test_init.py) is an extensionless script, loaded
here the same way test_transition_lint.py loads transition-lint: via
importlib against the real file. Each test drives `init_factory.main()`
against a fresh `tmp_path` target with `--source` pointed at this checkout,
then inspects the resulting `.claude/hooks/`, `.claude/settings.json`,
`.github/hooks/*.sh`, and `.github/hooks/*.json`.

The hook script's own full pattern coverage (8 block cases, 7 allow cases)
was already proven manually elsewhere this session — these tests only prove
the wiring: that init-factory installs the same script for both CLIs, wires
each CLI's own hook-config shape correctly, idempotently, and without
disturbing unrelated hook entries already present.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "init-factory"
_loader = SourceFileLoader("init_factory", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("init_factory", _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules["init_factory"] = init_factory
_loader.exec_module(init_factory)

GUARDRAIL_COMMAND = init_factory.CLAUDE_GUARDRAIL_HOOK_COMMAND


def _run_init(target: Path) -> int:
    return init_factory.main(["--target", str(target), "--source", str(_ROOT)])


def _hook_link(target: Path) -> Path:
    return target / ".claude" / "hooks" / "block-dangerous-git.sh"


def _settings(target: Path) -> Path:
    return target / ".claude" / "settings.json"


def _copilot_hook_link(target: Path) -> Path:
    return target / ".github" / "hooks" / "block-dangerous-git.sh"


def _copilot_config_link(target: Path) -> Path:
    return target / ".github" / "hooks" / "block-dangerous-git.json"


def _has_guardrail_entry(settings: dict) -> bool:
    for entry in settings.get("hooks", {}).get("PreToolUse", []):
        for hook in entry.get("hooks", []):
            if hook.get("command") == GUARDRAIL_COMMAND:
                return True
    return False


class TestFreshTarget:
    def test_hook_symlinked_into_copied_factory_config(self, tmp_path):
        rc = _run_init(tmp_path)
        assert rc == 0

        link = _hook_link(tmp_path)
        assert link.is_symlink()

        resolved = link.resolve()
        expected = (
            tmp_path / "factory" / "config" / "hooks" / "block-dangerous-git.sh"
        ).resolve()
        assert resolved == expected
        assert resolved.is_file()

    def test_settings_json_created_with_guardrail_entry(self, tmp_path):
        rc = _run_init(tmp_path)
        assert rc == 0

        settings_path = _settings(tmp_path)
        assert settings_path.exists()

        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        assert _has_guardrail_entry(settings)

    def test_copilot_hook_and_config_symlinked(self, tmp_path):
        rc = _run_init(tmp_path)
        assert rc == 0

        script_link = _copilot_hook_link(tmp_path)
        assert script_link.is_symlink()
        assert (
            script_link.resolve()
            == (
                tmp_path / "factory" / "config" / "hooks" / "block-dangerous-git.sh"
            ).resolve()
        )

        config_link = _copilot_config_link(tmp_path)
        assert config_link.is_symlink()
        resolved_config = config_link.resolve()
        assert (
            resolved_config
            == (
                tmp_path / "factory" / "config" / "hooks" / "block-dangerous-git.json"
            ).resolve()
        )

        config = json.loads(resolved_config.read_text(encoding="utf-8"))
        assert config["hooks"]["preToolUse"][0]["matcher"] == "bash"


class TestHookWiringWorks:
    def test_blocks_dangerous_command(self, tmp_path):
        _run_init(tmp_path)
        link = _hook_link(tmp_path)

        result = subprocess.run(
            [str(link)],
            input='{"tool_input":{"command":"git commit -m x --no-verify"}}',
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "BLOCKED" in result.stderr

    def test_allows_harmless_command(self, tmp_path):
        _run_init(tmp_path)
        link = _hook_link(tmp_path)

        result = subprocess.run(
            [str(link)],
            input='{"tool_input":{"command":"git status"}}',
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_blocks_dangerous_command_via_copilot_json_shape(self, tmp_path):
        _run_init(tmp_path)
        link = _copilot_hook_link(tmp_path)

        result = subprocess.run(
            [str(link)],
            input='{"toolName":"bash","toolArgs":{"command":"git push origin main"}}',
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "BLOCKED" in result.stderr

        decision = json.loads(result.stdout)
        assert decision["permissionDecision"] == "deny"

    def test_allows_harmless_command_via_copilot_json_shape(self, tmp_path):
        _run_init(tmp_path)
        link = _copilot_hook_link(tmp_path)

        result = subprocess.run(
            [str(link)],
            input='{"toolName":"bash","toolArgs":{"command":"git status"}}',
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestReRunIsNoop:
    def test_second_run_leaves_symlink_and_settings_unchanged(self, tmp_path):
        assert _run_init(tmp_path) == 0

        link = _hook_link(tmp_path)
        settings_path = _settings(tmp_path)
        copilot_link = _copilot_hook_link(tmp_path)
        copilot_config = _copilot_config_link(tmp_path)
        link_target_before = link.resolve()
        settings_before = settings_path.read_text(encoding="utf-8")
        copilot_link_target_before = copilot_link.resolve()
        copilot_config_target_before = copilot_config.resolve()

        assert _run_init(tmp_path) == 0

        assert link.is_symlink()
        assert link.resolve() == link_target_before
        assert settings_path.read_text(encoding="utf-8") == settings_before
        assert copilot_link.resolve() == copilot_link_target_before
        assert copilot_config.resolve() == copilot_config_target_before


class TestPreExistingSettingsPreserved:
    def test_unrelated_hook_entry_kept_alongside_guardrail(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        existing = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Bash",
                        "hooks": [{"type": "command", "command": "echo done"}],
                    }
                ],
                "PreToolUse": [
                    {
                        "matcher": "Write",
                        "hooks": [{"type": "command", "command": "echo write-hook"}],
                    }
                ],
            }
        }
        (claude_dir / "settings.json").write_text(
            json.dumps(existing, indent=2) + "\n", encoding="utf-8"
        )

        rc = _run_init(tmp_path)
        assert rc == 0

        settings = json.loads(_settings(tmp_path).read_text(encoding="utf-8"))

        # unrelated PostToolUse entry untouched
        assert settings["hooks"]["PostToolUse"] == existing["hooks"]["PostToolUse"]

        # unrelated pre-existing PreToolUse/Write entry untouched
        pre_tool_use = settings["hooks"]["PreToolUse"]
        assert {
            "matcher": "Write",
            "hooks": [{"type": "command", "command": "echo write-hook"}],
        } in pre_tool_use

        # guardrail entry added alongside it
        assert _has_guardrail_entry(settings)


class TestModelConfCopied:
    def test_model_conf_copied_to_target_config(self, tmp_path):
        rc = _run_init(tmp_path)
        assert rc == 0

        dest = tmp_path / "config" / "model.conf"
        assert dest.exists()
        assert dest.read_text(encoding="utf-8") == (
            _ROOT / "factory" / "config" / "model.conf"
        ).read_text(encoding="utf-8")
