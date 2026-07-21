"""Tests for the usage-capture Stop/SubagentStop hooks wired in by
`factory/scripts/init-factory` (ST-0040).

Mirrors test_init_factory_guardrail.py's structure exactly: init-factory is
an extensionless script, loaded here via importlib against the real file (the
same module object is reused across both test files through
`sys.modules["init_factory"]`, so this file's import is a no-op re-attach
when the guardrail test already ran in-process — importlib.util.module_from_spec
plus exec_module here is idempotent enough for pytest's collection order).

Each test drives `init_factory.main()` against a fresh `tmp_path` target with
`--source` pointed at this checkout, then inspects the resulting
`.claude/hooks/capture-usage.sh` symlink and `.claude/settings.json` entries.

The hook script's own payload-parsing behaviour (Stop vs. SubagentStop shape,
best-effort exit-0 contract) is covered by ST-0039's own tests; these tests
only prove init-factory's wiring: that a fresh install adds both hook
entries, that re-running is a no-op, that unrelated hooks survive the merge,
and that no new .gitignore entry was needed for `.agent-factory/usage/`.
"""

from __future__ import annotations

import importlib.util
import json
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

CAPTURE_COMMAND = init_factory.CLAUDE_CAPTURE_HOOK_COMMAND
CAPTURE_EVENTS = init_factory.CLAUDE_CAPTURE_HOOK_EVENTS


def _run_init(target: Path) -> int:
    return init_factory.main(["--target", str(target), "--source", str(_ROOT)])


def _hook_link(target: Path) -> Path:
    return target / ".claude" / "hooks" / "capture-usage.sh"


def _settings(target: Path) -> Path:
    return target / ".claude" / "settings.json"


def _has_capture_entry(settings: dict, event: str) -> bool:
    for entry in settings.get("hooks", {}).get(event, []):
        for hook in entry.get("hooks", []):
            if hook.get("command") == CAPTURE_COMMAND:
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
            tmp_path / "factory" / "config" / "hooks" / "capture-usage.sh"
        ).resolve()
        assert resolved == expected
        assert resolved.is_file()

    def test_settings_json_gets_both_stop_and_subagentstop_entries(self, tmp_path):
        rc = _run_init(tmp_path)
        assert rc == 0

        settings = json.loads(_settings(tmp_path).read_text(encoding="utf-8"))

        assert set(CAPTURE_EVENTS) == {"Stop", "SubagentStop"}
        for event in CAPTURE_EVENTS:
            assert _has_capture_entry(settings, event), f"missing {event} hook entry"


class TestReRunIsNoop:
    def test_second_run_leaves_symlink_and_settings_unchanged(self, tmp_path):
        assert _run_init(tmp_path) == 0

        link = _hook_link(tmp_path)
        settings_path = _settings(tmp_path)
        link_target_before = link.resolve()
        settings_before = settings_path.read_text(encoding="utf-8")

        assert _run_init(tmp_path) == 0

        assert link.is_symlink()
        assert link.resolve() == link_target_before
        assert settings_path.read_text(encoding="utf-8") == settings_before


class TestPreExistingSettingsPreserved:
    def test_unrelated_hook_entry_kept_alongside_capture_hooks(self, tmp_path):
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
                "Stop": [
                    {
                        "hooks": [
                            {"type": "command", "command": "echo project-owned-stop"}
                        ]
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

        # project's own pre-existing Stop entry untouched, sitting alongside ours
        assert {
            "hooks": [{"type": "command", "command": "echo project-owned-stop"}]
        } in settings["hooks"]["Stop"]

        # both capture entries added alongside the project's own hooks
        for event in CAPTURE_EVENTS:
            assert _has_capture_entry(settings, event)


class TestGitignoreNeedsNoNewEntry:
    def test_agent_factory_usage_covered_by_existing_ignore_line(self, tmp_path):
        rc = _run_init(tmp_path)
        assert rc == 0

        gitignore = (tmp_path / ".gitignore").read_text(encoding="utf-8")
        assert "/.agent-factory/" in gitignore
        assert "/.agent-factory/usage" not in gitignore
        assert "usage/" not in gitignore

        manifest = json.loads(
            (tmp_path / ".agent-factory" / "factory-install.json").read_text(
                encoding="utf-8"
            )
        )
        assert "/.agent-factory/" in manifest["ignored_paths"]
        assert not any("usage" in entry for entry in manifest["ignored_paths"]), (
            "no new ignore entry should have been added for .agent-factory/usage/"
        )


class TestRemovalMarker:
    def test_settings_created_fresh_is_recorded_for_removal(self, tmp_path):
        """When settings.json didn't exist before, both the guardrail and the
        capture hooks land in a file init-factory owns outright: it's
        recorded in remove_paths (deleted wholesale by remove-factory) and
        claude_settings_existed is False, mirroring how the guardrail records
        its own from-scratch settings.json. This is the generic manifest path
        that lets remove-factory extricate a from-scratch install without any
        hook-specific removal code."""
        rc = _run_init(tmp_path)
        assert rc == 0

        manifest = json.loads(
            (tmp_path / ".agent-factory" / "factory-install.json").read_text(
                encoding="utf-8"
            )
        )
        assert manifest["claude_settings_existed"] is False
        assert ".claude/settings.json" in manifest["remove_paths"]
