"""Codex-specific ``init-factory`` adapter contracts (ST-0057)."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
import tomllib

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "init-factory"
_loader = SourceFileLoader("init_factory_codex", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("init_factory_codex", _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules["init_factory_codex"] = init_factory
_loader.exec_module(init_factory)


@pytest.fixture(autouse=True)
def _isolate_unrelated_installers(monkeypatch):
    monkeypatch.setattr(
        init_factory, "provision_usage_runtime", lambda _target, _report: True
    )
    monkeypatch.setattr(
        init_factory,
        "initialize_usage_lifecycle",
        lambda _target, _report, _retention: None,
    )
    monkeypatch.setattr(
        init_factory, "pre_commit_install", lambda _target, _report: None
    )


def _run_init(target: Path) -> int:
    return init_factory.main(["--target", str(target), "--source", str(_ROOT)])


def _hook_commands(config: dict, event: str) -> list[str]:
    return [
        hook["command"]
        for entry in config["hooks"][event]
        for hook in entry.get("hooks", [])
        if hook.get("type") == "command"
    ]


def test_fresh_install_creates_codex_discovery_layout_and_native_agents(tmp_path):
    assert _run_init(tmp_path) == 0

    skill_names = sorted(
        path.parent.name for path in (_ROOT / "factory/skills").glob("*/SKILL.md")
    )
    installed_skills = tmp_path / ".agents" / "skills"
    assert sorted(path.name for path in installed_skills.iterdir()) == skill_names
    assert all(
        (installed_skills / name).is_symlink()
        and (installed_skills / name).resolve()
        == (tmp_path / "factory" / "skills" / name).resolve()
        for name in skill_names
    )

    agent_names = sorted(path.stem for path in (_ROOT / "factory/agents").glob("*.md"))
    generated = tmp_path / ".codex" / "agents"
    assert sorted(path.stem for path in generated.glob("*.toml")) == agent_names
    assert all(
        set(tomllib.loads(path.read_text()))
        == {
            "name",
            "description",
            "developer_instructions",
        }
        for path in generated.glob("*.toml")
    )

    for name in ("INDEX.yaml", "playbooks", "rulebooks", "scripts"):
        alias = tmp_path / ".codex" / name
        assert alias.is_symlink()
        assert alias.resolve() == (tmp_path / "factory" / name).resolve()
    assert (tmp_path / "AGENTS.md").is_symlink()
    assert (tmp_path / "AGENTS.md").resolve() == (
        tmp_path / "factory/config/AGENTS.md"
    ).resolve()


def test_hooks_merge_guardrail_and_capture_with_git_root_resolution(tmp_path):
    codex = tmp_path / ".codex"
    codex.mkdir()
    project_entry = {
        "matcher": "^Write$",
        "hooks": [{"type": "command", "command": "project-hook"}],
    }
    (codex / "hooks.json").write_text(
        json.dumps(
            {
                "project": True,
                "hooks": {"PreToolUse": [project_entry]},
            }
        )
        + "\n"
    )

    assert _run_init(tmp_path) == 0

    config = json.loads((codex / "hooks.json").read_text())
    assert config["project"] is True
    assert project_entry in config["hooks"]["PreToolUse"]
    guard_entries = [
        entry
        for entry in config["hooks"]["PreToolUse"]
        if init_factory.CODEX_GUARDRAIL_HOOK_COMMAND
        in [hook.get("command") for hook in entry.get("hooks", [])]
    ]
    assert guard_entries == [
        {
            "matcher": "^Bash$",
            "hooks": [
                {
                    "type": "command",
                    "command": init_factory.CODEX_GUARDRAIL_HOOK_COMMAND,
                }
            ],
        }
    ]
    for command in (
        init_factory.CODEX_GUARDRAIL_HOOK_COMMAND,
        init_factory.CODEX_CAPTURE_HOOK_COMMAND,
    ):
        assert "git rev-parse --show-toplevel" in command
        assert not command.startswith(".codex/")
    for event in ("Stop", "SubagentStop"):
        assert _hook_commands(config, event) == [
            init_factory.CODEX_CAPTURE_HOOK_COMMAND
        ]
    manifest = json.loads(
        (tmp_path / ".agent-factory/factory-install.json").read_text()
    )
    assert manifest["codex_hook_handlers"] == [
        {
            "event": "PreToolUse",
            "matcher": "^Bash$",
            "command": init_factory.CODEX_GUARDRAIL_HOOK_COMMAND,
        },
        {
            "event": "Stop",
            "command": init_factory.CODEX_CAPTURE_HOOK_COMMAND,
        },
        {
            "event": "SubagentStop",
            "command": init_factory.CODEX_CAPTURE_HOOK_COMMAND,
        },
    ]

    nested = tmp_path / "one" / "two"
    nested.mkdir(parents=True)
    result = subprocess.run(
        init_factory.CODEX_GUARDRAIL_HOOK_COMMAND,
        cwd=nested,
        shell=True,
        input='{"tool_input":{"cmd":"git status"}}',
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_rerun_is_idempotent_and_refreshes_only_owned_agents(tmp_path):
    assert _run_init(tmp_path) == 0
    worker = tmp_path / "factory/agents/developer-agent.md"
    worker.write_text(
        worker.read_text().replace(
            "Implement a single backlog story",
            "Implement one refreshed backlog story",
            1,
        )
    )
    foreign = tmp_path / ".codex/agents/project-agent.toml"
    foreign.write_text('name = "project-agent"\n')

    assert _run_init(tmp_path) == 0

    generated = tomllib.loads(
        (tmp_path / ".codex/agents/developer-agent.toml").read_text()
    )
    assert "refreshed backlog story" in generated["description"]
    assert foreign.read_text() == 'name = "project-agent"\n'
    config = json.loads((tmp_path / ".codex/hooks.json").read_text())
    assert (
        _hook_commands(config, "Stop").count(init_factory.CODEX_CAPTURE_HOOK_COMMAND)
        == 1
    )
    guard_commands = _hook_commands(config, "PreToolUse")
    assert guard_commands.count(init_factory.CODEX_GUARDRAIL_HOOK_COMMAND) == 1


def test_project_owned_codex_content_and_root_orientation_are_preserved(
    tmp_path, capsys
):
    project_skill = tmp_path / ".agents/skills/project-skill"
    project_skill.mkdir(parents=True)
    (project_skill / "SKILL.md").write_text("project skill\n")
    project_agent = tmp_path / ".codex/agents/project-agent.toml"
    project_agent.parent.mkdir(parents=True)
    project_agent.write_text('name = "project-agent"\n')
    orientation = tmp_path / "AGENTS.md"
    orientation.write_bytes(b"project orientation\n")

    assert _run_init(tmp_path) == 0

    assert (project_skill / "SKILL.md").read_text() == "project skill\n"
    assert project_agent.read_text() == 'name = "project-agent"\n'
    assert orientation.read_bytes() == b"project orientation\n"
    output = capsys.readouterr().out
    assert "Factory orientation was skipped" in output
    assert "incorporate" in output
    assert "open /hooks" in output and "review and trust" in output


@pytest.mark.parametrize("kind", ["skill", "agent", "alias", "hook"])
def test_factory_name_collision_stops_without_overwriting(tmp_path, kind):
    if kind == "skill":
        source = next((_ROOT / "factory/skills").glob("*/SKILL.md"))
        collision = tmp_path / ".agents/skills" / source.parent.name
        collision.mkdir(parents=True)
        collision.joinpath("owned.txt").write_text("project\n")
    elif kind == "agent":
        source = next((_ROOT / "factory/agents").glob("*.md"))
        collision = tmp_path / ".codex/agents" / f"{source.stem}.toml"
        collision.parent.mkdir(parents=True)
        collision.write_text("project agent\n")
    elif kind == "alias":
        collision = tmp_path / ".codex/INDEX.yaml"
        collision.parent.mkdir(parents=True)
        collision.write_text("project index\n")
    else:
        collision = tmp_path / ".codex/hooks/block-dangerous-git.sh"
        collision.parent.mkdir(parents=True)
        collision.write_text("project hook\n")
    before = collision.read_bytes() if collision.is_file() else None

    assert _run_init(tmp_path) == 1
    assert not (tmp_path / "AGENTS.md").exists()
    if kind == "skill":
        assert list((tmp_path / ".agents/skills").iterdir()) == [collision]
        assert not (tmp_path / ".codex").exists()
    else:
        assert not (tmp_path / ".agents").exists()

    if before is None:
        assert collision.is_dir()
        assert collision.joinpath("owned.txt").read_text() == "project\n"
    else:
        assert collision.read_bytes() == before


@pytest.mark.parametrize(
    "unsafe_path",
    [
        ".agents",
        ".agents/skills",
        ".codex",
        ".codex/agents",
        ".codex/hooks",
    ],
)
def test_symlinked_codex_ancestor_is_rejected_before_codex_writes(
    tmp_path, unsafe_path
):
    outside = tmp_path / "outside"
    outside.mkdir()
    link = tmp_path / unsafe_path
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(outside, target_is_directory=True)

    assert _run_init(tmp_path) == 1

    assert list(outside.iterdir()) == []
    assert not (tmp_path / "AGENTS.md").exists()


def test_unsafe_hooks_json_is_rejected_before_codex_writes(tmp_path):
    outside = tmp_path / "outside-hooks.json"
    outside.write_text("{}\n")
    hooks = tmp_path / ".codex/hooks.json"
    hooks.parent.mkdir()
    hooks.symlink_to(outside)

    assert _run_init(tmp_path) == 1

    assert outside.read_text() == "{}\n"
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / ".agents").exists()


def test_hardlinked_hooks_json_is_rejected_before_codex_writes(tmp_path):
    outside = tmp_path / "outside-hooks.json"
    outside.write_text("{}\n")
    hooks = tmp_path / ".codex/hooks.json"
    hooks.parent.mkdir()
    os.link(outside, hooks)

    assert _run_init(tmp_path) == 1

    assert outside.read_text() == "{}\n"
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / ".agents").exists()


def test_spoofed_generated_marker_needs_prior_manifest_evidence(tmp_path):
    agent = next((_ROOT / "factory/agents").glob("*.md"))
    collision = tmp_path / ".codex/agents" / f"{agent.stem}.toml"
    collision.parent.mkdir(parents=True)
    spoof = '# Generated by Agent Factory; do not edit.\nname = "spoof"\n'
    collision.write_text(spoof)

    assert _run_init(tmp_path) == 1

    assert collision.read_text() == spoof
    assert not (tmp_path / "AGENTS.md").exists()


def test_unmanifested_stale_spoof_marker_is_not_pruned(tmp_path):
    stale = tmp_path / ".codex/agents/retired.toml"
    stale.parent.mkdir(parents=True)
    spoof = '# Generated by Agent Factory; do not edit.\nname = "retired"\n'
    stale.write_text(spoof)

    assert _run_init(tmp_path) == 1

    assert stale.read_text() == spoof
    assert not (tmp_path / ".agents").exists()


def test_manifest_claims_only_handlers_the_installer_appended(tmp_path):
    codex = tmp_path / ".codex"
    codex.mkdir()
    existing = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "^Bash$",
                    "hooks": [
                        {
                            "type": "command",
                            "command": init_factory.CODEX_GUARDRAIL_HOOK_COMMAND,
                        }
                    ],
                }
            ],
            **{
                event: [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": init_factory.CODEX_CAPTURE_HOOK_COMMAND,
                            }
                        ]
                    }
                ]
                for event in ("Stop", "SubagentStop")
            },
        }
    }
    (codex / "hooks.json").write_text(json.dumps(existing) + "\n")

    assert _run_init(tmp_path) == 0

    manifest = json.loads(
        (tmp_path / ".agent-factory/factory-install.json").read_text()
    )
    assert manifest["codex_hook_handlers"] == []
