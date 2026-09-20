"""Contract tests for the intent select command."""

from __future__ import annotations

import os
import textwrap

import pytest

from conftest import load_script

intent = load_script("intent")


def _write_agent(tmp_path, name, inputs_required=None, description=""):
    """Write a minimal agent .md file with structured frontmatter."""
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}" if description else f"name: {name}",
    ]

    if inputs_required is not None:
        lines.append("inputs:")
        lines.append("  required:")
        for req in inputs_required:
            lines.append(f"    - type: {req['type']}")
            lines.append(f"      path_pattern: \"{req['path_pattern']}\"")
            if "conditions" in req:
                cond = req["conditions"]
                lines.append("      conditions:")
                for k, v in cond.items():
                    lines.append(f"        {k}: {v}")
        lines.append("  context: []")
    else:
        lines.append("inputs:")
        lines.append("  context: []")

    lines.append("---")
    lines.append(f"# {name}")

    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(exist_ok=True)
    (agents_dir / f"{name}.md").write_text("\n".join(lines))
    return agents_dir


class TestSelectListsAllAgents:
    def test_lists_all_agents(self, tmp_path, capsys):
        agents_dir = _write_agent(tmp_path, "alpha-agent")
        _write_agent(tmp_path, "beta-agent")

        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "alpha-agent" in out
        assert "beta-agent" in out

    def test_no_agents_found(self, tmp_path, capsys):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "no agent definitions found" in out


class TestSelectSatisfiedEvidence:
    def test_shows_satisfied_input(self, tmp_path, capsys):
        target = tmp_path / "docs"
        target.mkdir()
        proposal = target / "my-proposal.md"
        proposal.write_text("---\nstatus: accepted\n---\n# Proposal\n")

        agents_dir = _write_agent(
            tmp_path, "test-agent",
            inputs_required=[{
                "type": "proposal",
                "path_pattern": str(target / "*.md"),
            }],
        )

        os.chdir(tmp_path)
        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "✓" in out
        assert "proposal" in out


class TestSelectUnsatisfiedEvidence:
    def test_shows_unsatisfied_input(self, tmp_path, capsys):
        agents_dir = _write_agent(
            tmp_path, "test-agent",
            inputs_required=[{
                "type": "story",
                "path_pattern": str(tmp_path / "nonexistent/*.md"),
            }],
        )

        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "✗" in out
        assert "story" in out


class TestSelectNoRequiredInputs:
    def test_no_required_inputs_marked(self, tmp_path, capsys):
        agents_dir = _write_agent(tmp_path, "free-agent")

        result = intent.main(["select", "--agents-dir", str(agents_dir)])

        assert result == 0
        out = capsys.readouterr().out
        assert "○" in out
        assert "always eligible" in out


class TestSelectWorkstreamFlag:
    def test_workstream_flag_accepted(self, tmp_path, capsys):
        agents_dir = _write_agent(tmp_path, "scoped-agent")

        result = intent.main([
            "select",
            "--agents-dir", str(agents_dir),
            "--workstream", "my-workstream",
        ])

        assert result == 0


class TestSelectExitCode:
    def test_exit_code_zero_on_success(self, tmp_path):
        agents_dir = _write_agent(tmp_path, "test-agent")
        result = intent.main(["select", "--agents-dir", str(agents_dir)])
        assert result == 0


class TestSelectReadOnly:
    def test_no_files_written(self, tmp_path):
        agents_dir = _write_agent(tmp_path, "test-agent")
        before = set(tmp_path.rglob("*"))

        intent.main(["select", "--agents-dir", str(agents_dir)])

        after = set(tmp_path.rglob("*"))
        assert before == after
