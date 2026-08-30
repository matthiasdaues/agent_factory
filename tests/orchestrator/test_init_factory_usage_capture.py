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

import errno
import importlib.util
import json
import os
import stat
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

CAPTURE_COMMAND = init_factory.CLAUDE_CAPTURE_HOOK_COMMAND
CAPTURE_EVENTS = init_factory.CLAUDE_CAPTURE_HOOK_EVENTS


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


def _hook_link(target: Path) -> Path:
    return target / ".claude" / "hooks" / "capture-usage.sh"


def _settings(target: Path) -> Path:
    return target / ".claude" / "settings.json"


def _copilot_hook_config(target: Path) -> Path:
    return target / ".github" / "hooks" / "capture-usage.json"


def _codex_hook_config(target: Path) -> Path:
    return target / ".codex" / "hooks.json"


def _has_capture_entry(settings: dict, event: str) -> bool:
    for entry in settings.get("hooks", {}).get(event, []):
        for hook in entry.get("hooks", []):
            if hook.get("command") == CAPTURE_COMMAND:
                return True
    return False


class TestFreshTarget:
    def test_all_installed_pi_modules_export_extension_factories(self):
        for name in (
            "block-dangerous-git.ts",
            "step-guard.ts",
            "capture-usage.ts",
            "dispatch-wave.ts",
            "pi-usage.ts",
            "run-agent.ts",
        ):
            source = (_ROOT / "factory/config/extensions" / name).read_text()
            assert "export default function" in source, (
                f"{name} is installed into Pi's auto-discovered extensions "
                "directory but does not export an extension factory"
            )

    def test_SEC0003_all_cli_capture_sites_use_package_manager_free_launcher(self):
        launcher = (_ROOT / "factory/scripts/usage-capture-runtime").read_text()
        assert not any(
            command in launcher for command in ("uv ", "uvx ", "pip ", "curl ", "wget ")
        )
        for relative in (
            "factory/config/hooks/capture-usage.sh",
            "factory/config/hooks/capture-copilot-usage.sh",
            "factory/config/hooks/capture-codex-usage.sh",
            "factory/config/extensions/pi-usage.ts",
        ):
            text = (_ROOT / relative).read_text()
            assert "usage-capture-runtime" in text
            assert "uv run" not in text and "pip " not in text

    def test_SEC0003_runtime_ignores_poisoned_uv_cache_and_network(self, tmp_path):
        assert _run_init(tmp_path) == 0
        poison = tmp_path / "poison-bin"
        poison.mkdir()
        marker = tmp_path / "UV_WAS_EXECUTED"
        fake_uv = poison / "uv"
        fake_uv.write_text(f"#!/bin/sh\ntouch {marker}\nexit 99\n")
        fake_uv.chmod(0o700)
        env = {
            **os.environ,
            "PATH": f"{poison}{os.pathsep}{os.environ['PATH']}",
            "UV_OFFLINE": "1",
            "UV_CACHE_DIR": str(tmp_path / "absent-cache"),
        }

        result = subprocess.run(
            [str(tmp_path / "factory/scripts/usage-capture-runtime"), "--count-tokens"],
            input="Hello, world!",
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "4"
        assert not marker.exists()

    def test_SEC0003_requirements_are_exact_and_hash_protected(self):
        text = (_ROOT / init_factory.USAGE_REQUIREMENTS).read_text()
        requirements = [
            line
            for line in text.splitlines()
            if line and not line[0].isspace() and not line.startswith("#")
        ]
        assert requirements
        assert any(line.startswith("tiktoken==0.13.0 ") for line in requirements)
        assert all("==" in line and line.endswith("\\") for line in requirements)
        assert text.count("--hash=sha256:") >= len(requirements)

    def test_SEC0003_provisions_hashed_runtime_before_capture_hooks(self, tmp_path):
        assert _run_init(tmp_path) == 0

        runtime = tmp_path / init_factory.USAGE_RUNTIME
        python = runtime / (
            "Scripts/python.exe" if init_factory.os.name == "nt" else "bin/python"
        )
        assert python.exists()
        assert (runtime / ".requirements-sha256").is_file()
        assert _hook_link(tmp_path).is_symlink()
        assert stat.S_IMODE(runtime.stat().st_mode) == 0o700

    def test_SEC0003_provisioning_uses_hashes_disables_builds_and_python_downloads(
        self, tmp_path, monkeypatch
    ):
        requirements = tmp_path / init_factory.USAGE_REQUIREMENTS
        requirements.parent.mkdir(parents=True)
        requirements.write_text("tiktoken==0.13.0 --hash=sha256:abc\n")
        calls = []

        def fake_run(command, **_kwargs):
            calls.append(command)
            if command[1] == "venv":
                python = Path(command[-1]) / (
                    "Scripts/python.exe"
                    if init_factory.os.name == "nt"
                    else "bin/python"
                )
                python.parent.mkdir(parents=True)
                python.write_text("")
                python.chmod(0o700)
            return subprocess.CompletedProcess(command, 0, "", "")

        monkeypatch.setattr(init_factory.subprocess, "run", fake_run)

        assert init_factory.provision_usage_runtime(tmp_path, [])
        sync = next(command for command in calls if command[1:3] == ["pip", "sync"])
        assert "--require-hashes" in sync
        assert "--no-build" in sync
        assert "--no-python-downloads" in sync

    def test_SEC0003_offline_failure_leaves_capture_hooks_inactive(
        self, tmp_path, monkeypatch, capsys
    ):
        real_run = init_factory.subprocess.run

        def fail_uv(command, **kwargs):
            if command[:2] == ["uv", "venv"]:
                assert "--offline" in command
                return subprocess.CompletedProcess(
                    command, 1, "", "verified artifacts unavailable"
                )
            return real_run(command, **kwargs)

        monkeypatch.setenv("UV_OFFLINE", "1")
        monkeypatch.setattr(init_factory.subprocess, "run", fail_uv)

        assert _run_init(tmp_path) == 0
        assert not _hook_link(tmp_path).exists()
        assert not _copilot_hook_config(tmp_path).exists()
        codex = json.loads(_codex_hook_config(tmp_path).read_text())
        assert "Stop" not in codex["hooks"]
        assert "SubagentStop" not in codex["hooks"]
        assert codex["hooks"]["PreToolUse"]
        assert not (tmp_path / ".codex/hooks/capture-codex-usage.sh").exists()
        assert not (tmp_path / ".pi/extensions/capture-usage.ts").exists()
        assert (
            "usage capture unavailable; lifecycle hooks left inactive"
            in capsys.readouterr().out
        )

    def test_SEC0003_hash_or_build_failure_removes_partial_runtime(
        self, tmp_path, monkeypatch
    ):
        requirements = tmp_path / init_factory.USAGE_REQUIREMENTS
        requirements.parent.mkdir(parents=True)
        requirements.write_text("tiktoken==0.13.0 --hash=sha256:bad\n")

        def fail_sync(command, **_kwargs):
            if command[1] == "venv":
                Path(command[-1]).mkdir(parents=True)
                return subprocess.CompletedProcess(command, 0, "", "")
            assert "--require-hashes" in command and "--no-build" in command
            return subprocess.CompletedProcess(command, 1, "", "hash mismatch")

        monkeypatch.setattr(init_factory.subprocess, "run", fail_sync)
        report = []

        assert not init_factory.provision_usage_runtime(tmp_path, report)
        assert not (tmp_path / init_factory.USAGE_RUNTIME).exists()
        assert not list((tmp_path / ".agent-factory").glob("usage-runtime-stage-*"))
        assert any("hash mismatch" in line for line in report)

    def test_SEC0002_init_creates_private_retention_config_and_preserves_override(
        self, tmp_path
    ):
        assert (
            init_factory.main(
                [
                    "--target",
                    str(tmp_path),
                    "--source",
                    str(_ROOT),
                    "--project-name",
                    "Test Project",
                    "--usage-transcript-retention",
                    "omit",
                ]
            )
            == 0
        )
        config = tmp_path / ".agent-factory/usage-control/config.json"
        assert json.loads(config.read_text())["transcript_retention"] == "omit"
        assert stat.S_IMODE(config.stat().st_mode) == 0o600
        assert _run_init(tmp_path) == 0
        assert json.loads(config.read_text())["transcript_retention"] == "omit"

    def test_SEC0002_init_repairs_historical_usage_tree(self, tmp_path):
        historical = tmp_path / ".agent-factory/usage/transcripts/old-session"
        historical.mkdir(parents=True)
        evidence = historical / "old-record.jsonl"
        evidence.write_text("old secret")
        for directory in (
            tmp_path / ".agent-factory/usage",
            tmp_path / ".agent-factory/usage/transcripts",
            historical,
        ):
            directory.chmod(0o755)
        evidence.chmod(0o644)

        assert _run_init(tmp_path) == 0

        assert stat.S_IMODE(evidence.stat().st_mode) == 0o600
        assert stat.S_IMODE(historical.stat().st_mode) == 0o700

    def test_FAGAN0002_hardlink_capability_failure_is_reported_not_fatal(
        self, tmp_path, monkeypatch
    ):
        def unsupported_link(*_args, **_kwargs):
            raise OSError(errno.EOPNOTSUPP, "hard links unsupported")

        monkeypatch.setattr(init_factory.os, "link", unsupported_link)
        report = []

        init_factory.initialize_usage_lifecycle(tmp_path, report)

        assert (tmp_path / ".agent-factory/usage-control/state.json").is_file()
        assert any("Pi usage capture unavailable" in line for line in report)

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

    def test_copilot_native_agentstop_hooks_are_installed(self, tmp_path):
        assert _run_init(tmp_path) == 0

        config_path = _copilot_hook_config(tmp_path)
        assert config_path.is_symlink()
        config = json.loads(config_path.read_text(encoding="utf-8"))
        assert config["version"] == 1
        assert set(config["hooks"]) == {"agentStop", "subagentStop"}
        for event in ("agentStop", "subagentStop"):
            assert config["hooks"][event] == [
                {
                    "type": "command",
                    "bash": "./.github/hooks/capture-copilot-usage.sh",
                    "cwd": ".",
                    "timeoutSec": 10,
                }
            ]
        assert (tmp_path / ".github/hooks/capture-copilot-usage.sh").is_symlink()

    def test_ST0043_codex_native_stop_hooks_are_merge_installed(self, tmp_path):
        codex = tmp_path / ".codex"
        codex.mkdir()
        existing = {
            "hooks": {
                "Stop": [{"hooks": [{"type": "command", "command": "project-stop"}]}],
                "AfterToolUse": [
                    {"hooks": [{"type": "command", "command": "project-tool"}]}
                ],
            },
            "projectSetting": True,
        }
        _codex_hook_config(tmp_path).write_text(json.dumps(existing, indent=2) + "\n")

        assert _run_init(tmp_path) == 0

        config = json.loads(_codex_hook_config(tmp_path).read_text())
        assert config["projectSetting"] is True
        assert config["hooks"]["AfterToolUse"] == existing["hooks"]["AfterToolUse"]
        assert existing["hooks"]["Stop"][0] in config["hooks"]["Stop"]
        for event in ("Stop", "SubagentStop"):
            commands = [
                hook.get("command")
                for entry in config["hooks"][event]
                for hook in entry.get("hooks", [])
            ]
            assert commands.count(init_factory.CODEX_CAPTURE_HOOK_COMMAND) == 1
        assert (tmp_path / ".codex/hooks/capture-codex-usage.sh").is_symlink()

    def test_RECON0007_codex_install_reports_required_hook_trust(
        self, tmp_path, capsys
    ):
        assert _run_init(tmp_path) == 0

        output = capsys.readouterr().out
        assert "Codex usage capture: installed but not active until trusted" in output
        assert "open /hooks" in output
        assert "review and trust the project hooks" in output


class TestReRunIsNoop:
    def test_SEC0003_second_init_rebuilds_exact_runtime(self, tmp_path):
        assert _run_init(tmp_path) == 0
        runtime = tmp_path / init_factory.USAGE_RUNTIME
        digest = (runtime / ".requirements-sha256").read_text()
        foreign = runtime / "foreign-package"
        foreign.write_text("must not survive exact sync")

        assert _run_init(tmp_path) == 0

        assert (runtime / ".requirements-sha256").read_text() == digest
        assert not foreign.exists()

    def test_second_run_leaves_native_hook_assets_unchanged(self, tmp_path):
        assert _run_init(tmp_path) == 0

        link = _hook_link(tmp_path)
        settings_path = _settings(tmp_path)
        copilot_config = _copilot_hook_config(tmp_path)
        copilot_script = tmp_path / ".github/hooks/capture-copilot-usage.sh"
        codex_config = _codex_hook_config(tmp_path)
        codex_script = tmp_path / ".codex/hooks/capture-codex-usage.sh"

        def snapshot():
            return (
                link.resolve(),
                settings_path.read_bytes(),
                copilot_config.resolve(),
                copilot_config.read_bytes(),
                copilot_script.resolve(),
                codex_config.read_bytes(),
                codex_script.resolve(),
            )

        before = snapshot()

        assert _run_init(tmp_path) == 0

        assert link.is_symlink()
        assert snapshot() == before

    def test_RECON0007_codex_rerun_repeats_required_hook_trust(self, tmp_path, capsys):
        assert _run_init(tmp_path) == 0
        capsys.readouterr()

        assert _run_init(tmp_path) == 0

        output = capsys.readouterr().out
        assert "Codex usage capture: installed but not active until trusted" in output
        assert "open /hooks" in output


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
        assert not any(
            entry.startswith("/.agent-factory/usage")
            for entry in manifest["ignored_paths"]
        ), "no new ignore entry should have been added for .agent-factory/usage/"


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
