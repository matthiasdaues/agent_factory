"""Tests for trigger — resolves an agent/playbook step from INDEX.yaml's
source data and builds the CLI invocation. subprocess.run is monkeypatched
everywhere: these tests prove command construction and resolution, never
spawn a real `claude`/`copilot` process.
"""

from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "trigger"
_loader = SourceFileLoader("trigger", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("trigger", _loader)
trigger = importlib.util.module_from_spec(_spec)
sys.modules["trigger"] = trigger
_loader.exec_module(trigger)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def tree(tmp_path):
    agents_dir = tmp_path / "agents"
    playbooks_dir = tmp_path / "playbooks"
    model_conf = tmp_path / "model.conf"

    _write(
        agents_dir / "qa-agent.md",
        "---\nname: qa-agent\ntitle: QA Agent\nphase: 5\nphase-name: Quality\n"
        "tier: strong\ndescription: Review code.\n---\n\n# QA Agent\n\nDo QA.\n",
    )
    _write(
        agents_dir / "developer-agent.md",
        "---\nname: developer-agent\ntitle: Developer Agent\n"
        "description: Implement a story.\n---\n\n# Developer Agent\n\nImplement.\n",
    )
    _write(
        playbooks_dir / "bug-fix.md",
        "---\ntitle: Bug Fix Playbook\ncategory: orchestration\n---\n\n"
        "# Bug Fix Playbook\n\nOperational procedure for **fixing defects**.\n\n"
        "**Agent**: `developer-agent`\n\n**Agent**: `qa-agent`\n",
    )
    model_conf.write_text(
        "[facts]\n"
        "claude.strong = claude-opus-4-8\n"
        "claude.standard = claude-sonnet-5\n"
        "copilot.strong = claude-opus-4-6\n"
        "on_missing = halt\n",
        encoding="utf-8",
    )

    return agents_dir, playbooks_dir, model_conf


class TestResolution:
    def test_resolve_agent_found(self, tree):
        agents_dir, _, _ = tree
        agent = trigger.resolve_agent(agents_dir, "qa-agent")
        assert agent["name"] == "qa-agent"
        assert agent["tier"] == "strong"

    def test_resolve_agent_missing_raises(self, tree):
        agents_dir, _, _ = tree
        with pytest.raises(trigger.ResolutionError):
            trigger.resolve_agent(agents_dir, "no-such-agent")

    def test_resolve_playbook_step_by_name(self, tree):
        _, playbooks_dir, _ = tree
        playbook = trigger.resolve_playbook(playbooks_dir, "bug-fix")
        assert trigger.resolve_playbook_step(playbook, "qa-agent") == "qa-agent"

    def test_resolve_playbook_step_by_index(self, tree):
        _, playbooks_dir, _ = tree
        playbook = trigger.resolve_playbook(playbooks_dir, "bug-fix")
        assert trigger.resolve_playbook_step(playbook, "1") == "developer-agent"
        assert trigger.resolve_playbook_step(playbook, "2") == "qa-agent"

    def test_resolve_playbook_step_out_of_range(self, tree):
        _, playbooks_dir, _ = tree
        playbook = trigger.resolve_playbook(playbooks_dir, "bug-fix")
        with pytest.raises(trigger.ResolutionError):
            trigger.resolve_playbook_step(playbook, "99")

    def test_resolve_tier_model(self, tree):
        _, _, model_conf = tree
        assert (
            trigger.resolve_tier_model(model_conf, "claude", "strong")
            == "claude-opus-4-8"
        )

    def test_resolve_tier_model_missing_halts(self, tree):
        _, _, model_conf = tree
        with pytest.raises(trigger.ResolutionError):
            trigger.resolve_tier_model(model_conf, "claude", "economy")


class TestPromptComposition:
    def test_compose_prompt_includes_agent_definition(self, tree):
        agents_dir, _, _ = tree
        prompt = trigger.compose_prompt(agents_dir / "qa-agent.md")
        assert "# Agent Definition" in prompt
        assert "Do QA." in prompt
        assert "# Call to Action" in prompt


class TestCommandConstruction:
    def test_claude_background_uses_scoped_allowlist_not_bypass(self):
        cmd = trigger.build_background_command("claude", "a prompt", "claude-opus-4-8")
        assert cmd[0] == "claude"
        assert "--dangerously-skip-permissions" not in cmd
        assert "--permission-mode" in cmd
        assert cmd[cmd.index("--permission-mode") + 1] == "dontAsk"
        assert "--allowedTools" in cmd
        allowlist = cmd[cmd.index("--allowedTools") + 1]
        assert "Bash(git push" not in allowlist
        assert "Bash(git add" in allowlist
        assert "--model" in cmd
        assert cmd[cmd.index("--model") + 1] == "claude-opus-4-8"

    def test_claude_disallowed_tools_blocks_destructive_git(self):
        cmd = trigger.build_background_command("claude", "a prompt", None)
        disallow = cmd[cmd.index("--disallowedTools") + 1]
        assert "git push" in disallow
        assert "git reset" in disallow
        assert "git branch -D" in disallow

    def test_copilot_background_uses_scoped_allow_deny_not_all_tools(self):
        cmd = trigger.build_background_command("copilot", "a prompt", "claude-opus-4-6")
        assert cmd[0] == "copilot"
        assert "--allow-all-tools" not in cmd
        assert "--allow-tool" in cmd
        allow = cmd[cmd.index("--allow-tool") + 1]
        assert "shell(git add:*)" in allow
        assert "--deny-tool" in cmd
        deny = cmd[cmd.index("--deny-tool") + 1]
        assert "shell(git push:*)" in deny

    def test_unknown_cli_raises(self):
        with pytest.raises(trigger.ResolutionError):
            trigger.build_background_command("codex", "a prompt", None)


class TestMainBackgroundInvocation:
    """Proves main() wires resolution -> command -> subprocess correctly,
    with subprocess.run monkeypatched so nothing is actually spawned."""

    def test_background_agent_run_builds_expected_command(
        self, tree, monkeypatch, tmp_path
    ):
        agents_dir, playbooks_dir, model_conf = tree
        captured = {}

        def fake_run(cmd, cwd=None):
            captured["cmd"] = cmd
            captured["cwd"] = cwd

            class Result:
                returncode = 0

            return Result()

        monkeypatch.setattr(trigger.subprocess, "run", fake_run)

        rc = trigger.main(
            [
                "--agents-dir",
                str(agents_dir),
                "--playbooks-dir",
                str(playbooks_dir),
                "--model-conf",
                str(model_conf),
                "--cli",
                "claude",
                "--cwd",
                str(tmp_path),
                "--background",
                "agent",
                "qa-agent",
            ]
        )

        assert rc == 0
        assert captured["cmd"][0] == "claude"
        assert "--dangerously-skip-permissions" not in captured["cmd"]
        assert captured["cwd"] == str(tmp_path)

    def test_background_playbook_step_resolves_correct_agent(
        self, tree, monkeypatch, tmp_path
    ):
        agents_dir, playbooks_dir, model_conf = tree
        captured = {}

        def fake_run(cmd, cwd=None):
            captured["cmd"] = cmd

            class Result:
                returncode = 0

            return Result()

        monkeypatch.setattr(trigger.subprocess, "run", fake_run)

        rc = trigger.main(
            [
                "--agents-dir",
                str(agents_dir),
                "--playbooks-dir",
                str(playbooks_dir),
                "--model-conf",
                str(model_conf),
                "--cli",
                "claude",
                "--cwd",
                str(tmp_path),
                "--background",
                "playbook",
                "bug-fix",
                "--step",
                "2",
            ]
        )

        assert rc == 0
        prompt_idx = captured["cmd"].index("-p") + 1
        assert "qa-agent" in captured["cmd"][prompt_idx]

    def test_unresolvable_agent_exits_2_without_spawning(
        self, tree, monkeypatch, tmp_path
    ):
        agents_dir, playbooks_dir, model_conf = tree

        def fake_run(cmd, cwd=None):
            raise AssertionError(
                "subprocess.run must not be called on a resolution error"
            )

        monkeypatch.setattr(trigger.subprocess, "run", fake_run)

        rc = trigger.main(
            [
                "--agents-dir",
                str(agents_dir),
                "--playbooks-dir",
                str(playbooks_dir),
                "--model-conf",
                str(model_conf),
                "--cli",
                "claude",
                "--cwd",
                str(tmp_path),
                "--background",
                "agent",
                "no-such-agent",
            ]
        )

        assert rc == 2
