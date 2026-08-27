"""Contract tests: the argv the orchestrator emits must parse as the REAL trigger.

The orchestrator's own demo replaces factory/scripts/trigger with a stub that
reads `sys.argv[2]` and ignores every other argument, so it accepts any order.
That stub hid a dispatch bug — the orchestrator emitted an argument order the
real parser rejected with exit 2 — through every demo run and every mocked unit
test. These tests close that gap: they build the command exactly as
`run_trigger` does and hand it to `factory/scripts/trigger`'s own parser, never
to a stub.
"""

from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch

import pytest

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "orchestrator/src"))
run_playbook = importlib.import_module("agent_factory_orchestrator.cli")

_TRIGGER_SCRIPT = _ROOT / "factory" / "scripts" / "trigger"
_loader = SourceFileLoader("trigger_under_contract", str(_TRIGGER_SCRIPT))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
trigger = importlib.util.module_from_spec(_spec)
sys.modules[_loader.name] = trigger
_loader.exec_module(trigger)


def _emitted_argv(agent: str, cli: str) -> list[str]:
    """Return the command run_trigger hands to subprocess, without running it."""
    captured: dict[str, list[str]] = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = list(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    with patch.object(run_playbook.subprocess, "run", side_effect=fake_run):
        run_playbook.run_trigger(agent, cli)

    return captured["cmd"]


class TestOrchestratorArgvParsesAsRealTrigger:
    @pytest.mark.parametrize("cli", ["claude", "copilot"])
    def test_dispatch_argv_parses(self, cli):
        cmd = _emitted_argv("requirements-agent", cli)

        assert cmd[0] == sys.executable
        assert Path(cmd[1]) == run_playbook.TRIGGER_SCRIPT

        args = trigger.build_parser().parse_args(cmd[2:])

        assert args.kind == "agent"
        assert args.name == "requirements-agent"
        assert args.background is True
        assert args.interactive is False
        assert args.cli == cli

    def test_dispatch_argv_is_not_a_resolution_free_pass(self):
        """A parse failure and a resolution failure both exit 2 — distinguish them.

        The real trigger must reach agent resolution with this argv, i.e. fail
        because the agent does not exist, not because argparse rejected the
        command line.
        """
        cmd = _emitted_argv("no-such-agent-xyz", "claude")

        result = subprocess.run(
            [cmd[0], str(_TRIGGER_SCRIPT), *cmd[2:]],
            capture_output=True,
            text=True,
            check=False,
            cwd=_ROOT,
        )

        assert result.returncode == 2
        assert "no agent named 'no-such-agent-xyz'" in result.stderr
        assert "unrecognized arguments" not in result.stderr


class TestTriggerAcceptsBothArgumentOrders:
    """Both documented orders must parse identically.

    The spec order comes from UC-04's Gherkin, factory/skills/run-step/SKILL.md
    and trigger's own Usage block; the flags-first order is what argparse
    conventionally implies for a subcommand CLI. Callers use both.
    """

    def test_flags_after_subcommand(self):
        args = trigger.build_parser().parse_args(
            ["agent", "requirements-agent", "--background", "--cli", "claude"]
        )
        assert (args.kind, args.name, args.background, args.cli) == (
            "agent",
            "requirements-agent",
            True,
            "claude",
        )

    def test_flags_before_subcommand(self):
        args = trigger.build_parser().parse_args(
            ["--background", "--cli", "claude", "agent", "requirements-agent"]
        )
        assert (args.kind, args.name, args.background, args.cli) == (
            "agent",
            "requirements-agent",
            True,
            "claude",
        )

    def test_subcommand_flags_do_not_clobber_earlier_values(self):
        """A flag set before the subcommand survives a subcommand that omits it."""
        args = trigger.build_parser().parse_args(
            ["--cli", "copilot", "--background", "agent", "qa-agent"]
        )
        assert args.cli == "copilot"
        assert args.background is True

    def test_playbook_step_with_trailing_flags(self):
        args = trigger.build_parser().parse_args(
            [
                "playbook",
                "greenfield-development",
                "--step",
                "spec-review-agent",
                "--background",
                "--cli",
                "claude",
            ]
        )
        assert args.kind == "playbook"
        assert args.step == "spec-review-agent"
        assert args.background is True

    def test_path_options_are_paths_when_defaulted(self):
        args = trigger.build_parser().parse_args(["agent", "qa-agent", "--background"])
        assert isinstance(args.agents_dir, Path)
        assert isinstance(args.playbooks_dir, Path)
        assert isinstance(args.model_conf, Path)
        assert isinstance(args.cwd, Path)
