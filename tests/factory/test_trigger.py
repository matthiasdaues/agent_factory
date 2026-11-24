"""Subprocess tests for packages/factory/scripts/trigger.

Each test executes the script file itself (the `uv run --script` form)
against a temporary project holding agents, playbooks and a model.conf.
A fake `claude` and `copilot` executable on PATH records its arguments, so
no real CLI starts.
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent.parent
    / "packages"
    / "factory"
    / "scripts"
    / "trigger"
)

MODEL_CONF = """[facts]
claude.standard = claude-test-model
copilot.standard = copilot-test-model
on_missing = halt
"""


@pytest.fixture
def project(tmp_path: Path) -> Path:
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "alpha.md").write_text(
        "---\nname: alpha\ntier: standard\n---\n\n# Alpha\nDo alpha work.\n",
        encoding="utf-8",
    )
    (agents / "beta.md").write_text(
        "---\nname: beta\ntier: strong\n---\n\n# Beta\n", encoding="utf-8"
    )
    playbooks = tmp_path / "playbooks"
    playbooks.mkdir()
    (playbooks / "flow.md").write_text(
        "---\ntitle: Flow\n---\n\nSteps\n\n**Agent**: `alpha`\n\n**Agent**: `beta`\n",
        encoding="utf-8",
    )
    (playbooks / "empty.md").write_text(
        "---\ntitle: Empty\n---\n\nNo steps.\n", encoding="utf-8"
    )
    (tmp_path / "model.conf").write_text(MODEL_CONF, encoding="utf-8")
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for cli in ("claude", "copilot"):
        fake = bindir / cli
        fake.write_text(
            "#!/bin/sh\n"
            f'printf "%s\\n" "$@" > "{tmp_path}/{cli}.args"\n'
            "exit ${FAKE_CLI_EXIT:-0}\n",
            encoding="utf-8",
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    return tmp_path


def _run(
    project: Path, *args: str, exit_code: int = 0
) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "PATH": f"{project / 'bin'}{os.pathsep}{os.environ['PATH']}",
        "FAKE_CLI_EXIT": str(exit_code),
    }
    common = [
        "--agents-dir",
        str(project / "agents"),
        "--playbooks-dir",
        str(project / "playbooks"),
        "--model-conf",
        str(project / "model.conf"),
    ]
    return subprocess.run(
        [str(SCRIPT), *common, *args],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


@pytest.mark.spec("CG-13-LN-03")
def test_list_names_agents_and_playbooks(project: Path) -> None:
    result = _run(project, "list")
    assert result.returncode == 0
    assert "agent      alpha" in result.stdout
    assert "playbook   flow  [alpha, beta]" in result.stdout
    assert "playbook   empty  [(no fixed agent sequence)]" in result.stdout


@pytest.mark.spec("CG-13-LN-03")
def test_background_agent_runs_claude_with_prompt_and_model(project: Path) -> None:
    result = _run(project, "agent", "alpha", "--background", "--cli", "claude")
    assert result.returncode == 0
    args = (project / "claude.args").read_text(encoding="utf-8")
    assert "-p" in args.splitlines()
    assert "Do alpha work." in args
    assert "Execute the workflow defined in your Agent Definition above." in args
    assert "--permission-mode\ndontAsk" in args
    assert "--model\nclaude-test-model" in args
    assert "--dangerously-skip-permissions" not in args


@pytest.mark.spec("CG-13-LN-03")
def test_options_before_the_subcommand_parse_the_same(project: Path) -> None:
    result = _run(project, "--background", "--cli", "copilot", "agent", "alpha")
    assert result.returncode == 0
    args = (project / "copilot.args").read_text(encoding="utf-8")
    assert "--deny-tool" in args
    assert "--model\ncopilot-test-model" in args


@pytest.mark.spec("CG-13-LN-03")
def test_background_returns_the_cli_exit_code(project: Path) -> None:
    result = _run(project, "agent", "alpha", "--background", exit_code=7)
    assert result.returncode == 7


@pytest.mark.spec("CG-13-LN-03")
def test_interactive_prints_prompt_and_launches_cli(project: Path) -> None:
    result = _run(project, "agent", "alpha", "--interactive", "--cli", "copilot")
    assert result.returncode == 0
    assert "paste this as your first message" in result.stdout
    assert "Do alpha work." in result.stdout
    assert (
        "launching `copilot --allow-all-tools --model copilot-test-model`"
        in result.stdout
    )


@pytest.mark.spec("CG-13-LN-03")
def test_interactive_claude_launches_plain_session(project: Path) -> None:
    result = _run(project, "agent", "alpha", "--interactive")
    assert result.returncode == 0
    assert "launching `claude --model claude-test-model`" in result.stdout


@pytest.mark.spec("CG-13-LN-03")
@pytest.mark.parametrize("step", ["1", "alpha"])
def test_playbook_step_by_index_or_name_runs_that_agent(
    project: Path, step: str
) -> None:
    result = _run(project, "playbook", "flow", "--step", step, "--background")
    assert result.returncode == 0
    assert "Do alpha work." in (project / "claude.args").read_text(encoding="utf-8")


@pytest.mark.spec("CG-13-LN-03")
@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["agent", "nobody", "--background"], "no agent named 'nobody'"),
        (["playbook", "nope", "--step", "1"], "no playbook named 'nope'"),
        (["playbook", "empty", "--step", "1"], "has no agent sequence"),
        (["playbook", "flow", "--step", "9"], "out of range"),
        (["playbook", "flow", "--step", "gamma"], "is not in playbook 'flow'"),
        (["agent", "beta", "--background"], "no model configured for 'claude.strong'"),
    ],
)
def test_resolution_errors_exit_two_with_message(
    project: Path, args: list[str], message: str
) -> None:
    result = _run(project, *args)
    assert result.returncode == 2
    assert message in result.stderr
    assert not (project / "claude.args").exists()


@pytest.mark.spec("CG-13-LN-03")
def test_missing_model_conf_exits_two(project: Path) -> None:
    (project / "model.conf").unlink()
    result = _run(project, "agent", "alpha", "--background")
    assert result.returncode == 2
    assert "model config not found" in result.stderr


@pytest.mark.spec("CG-13-LN-03")
def test_malformed_model_conf_exits_two(project: Path) -> None:
    (project / "model.conf").write_text("key = value\n", encoding="utf-8")
    result = _run(project, "agent", "alpha", "--background")
    assert result.returncode == 2
    assert "content outside a section" in result.stderr


@pytest.mark.spec("CG-13-LN-03")
def test_on_missing_auto_runs_without_a_model_flag(project: Path) -> None:
    (project / "model.conf").write_text(
        "[facts]\non_missing = auto\n", encoding="utf-8"
    )
    result = _run(project, "agent", "alpha", "--background")
    assert result.returncode == 0
    assert "--model" not in (project / "claude.args").read_text(encoding="utf-8")


@pytest.mark.spec("CG-13-LN-03")
def test_background_and_interactive_are_mutually_exclusive(project: Path) -> None:
    result = _run(project, "agent", "alpha", "--background", "--interactive")
    assert result.returncode == 2
    assert "not allowed with" in result.stderr
