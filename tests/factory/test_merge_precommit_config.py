"""Tests for merge-precommit-config splice and dedup logic."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import load_script

mpc = load_script("merge-precommit-config")

TEMPLATE = """\
# Agent Factory pre-commit hooks
repos:
  - repo: local
    hooks:
      - id: agent_factory_hook-mdformat
        name: "agent_factory: mdformat"
        entry: bash -c '[ -d .agent-factory ] || exit 0; exec .agent-factory/factory/scripts/mdformat --number "$@"' --
        language: system
        types: [markdown]

      - id: agent_factory_hook-link-check
        name: "agent_factory: link-check"
        entry: bash -c '[ -d .agent-factory ] || exit 0; exec .agent-factory/factory/scripts/link-check "$@"' --
        language: system
        types: [markdown]
"""


class TestToolsInTarget:
    def test_project_mdformat_triggers_dedup(self):
        lines = [
            "repos:",
            "  - repo: local",
            "    hooks:",
            "      - id: mdformat",
            "        entry: mdformat --wrap 80",
            "        language: system",
        ]
        assert mpc._tools_in_target(lines) == {"mdformat"}

    def test_factory_script_entry_does_not_trigger_dedup(self):
        lines = [
            "repos:",
            "  - repo: local",
            "    hooks:",
            "      - id: mdformat",
            "        entry: .agent-factory/factory/scripts/mdformat --number",
            "        language: system",
        ]
        assert mpc._tools_in_target(lines) == set()

    def test_factory_hook_block_skipped(self):
        lines = [
            "repos:",
            "  - repo: local",
            "    hooks:",
            "      - id: agent_factory_hook-mdformat",
            "        entry: .agent-factory/factory/scripts/mdformat --number",
            "        language: system",
        ]
        assert mpc._tools_in_target(lines) == set()

    def test_bash_guard_entry_does_not_trigger_dedup(self):
        lines = [
            "repos:",
            "  - repo: local",
            "    hooks:",
            "      - id: mdformat",
            "        entry: bash -c '[ -d .agent-factory ] || exit 0; exec .agent-factory/factory/scripts/mdformat --number \"$@\"' --",
            "        language: system",
        ]
        assert mpc._tools_in_target(lines) == set()


class TestMerge:
    def test_initial_merge_includes_mdformat(self):
        target = "repos:\n  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        result = mpc.merge(target, TEMPLATE)
        assert result is not None
        assert "agent_factory_hook-mdformat" in result

    def test_already_merged_is_noop(self):
        target = "repos:\n  - repo: local\n    hooks:\n      - id: agent_factory_hook-mdformat\n"
        assert mpc.merge(target, TEMPLATE) is None

    def test_update_preserves_mdformat_with_factory_script_entry(self):
        """Dev repo case: target has a second section using .agent-factory/factory/scripts/mdformat.
        The dedup must NOT drop the factory hook."""
        target = (
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: agent_factory_hook-mdformat\n"
            "        entry: .agent-factory/factory/scripts/mdformat --number\n"
            "        language: system\n"
            "      - id: agent_factory_hook-link-check\n"
            "        entry: .agent-factory/factory/scripts/link-check\n"
            "        language: system\n"
            "\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: mdformat\n"
            "        entry: .agent-factory/factory/scripts/mdformat --number\n"
            "        language: system\n"
        )
        result = mpc.merge(target, TEMPLATE, update=True)
        assert result is not None
        assert "agent_factory_hook-mdformat" in result

    def test_update_dedup_fires_for_independent_mdformat(self):
        """Consumer project with its own mdformat: the factory hook should be
        dropped to avoid running the tool twice."""
        target = (
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: agent_factory_hook-mdformat\n"
            "        entry: bash -c '[ -d .agent-factory ] || exit 0; exec .agent-factory/factory/scripts/mdformat --number \"$@\"' --\n"
            "        language: system\n"
            "      - id: agent_factory_hook-link-check\n"
            "        entry: bash -c '[ -d .agent-factory ] || exit 0; exec .agent-factory/factory/scripts/link-check \"$@\"' --\n"
            "        language: system\n"
            "\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: mdformat\n"
            "        entry: mdformat --wrap 80\n"
            "        language: system\n"
        )
        result = mpc.merge(target, TEMPLATE, update=True)
        assert result is not None
        assert "agent_factory_hook-mdformat" not in result
        assert "agent_factory_hook-link-check" in result

    def test_update_replaces_the_block_in_place(self):
        """BUG-0110: an update keeps the block where it stands and leaves
        each comment above the block it heads."""
        target = (
            "repos:\n"
            "  # Project formatting\n"
            "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
            "    rev: v4.6.0\n"
            "    hooks:\n"
            "      - id: trailing-whitespace\n"
            "\n"
            "  # Factory gates\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: agent_factory_hook-link-check\n"
            "        entry: bash -c '[ -d .agent-factory ] || exit 0; exec .agent-factory/factory/scripts/link-check' --\n"
            "        language: system\n"
            "\n"
            "  # Project tests\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: run-tests\n"
            "        entry: pytest\n"
            "        language: system\n"
        )
        result = mpc.merge(target, TEMPLATE, update=True)
        lines = result.splitlines()

        assert "link-check' --\n" not in result
        assert lines.index("  # Project formatting") == 1
        factory_at = lines.index("  # Factory gates")
        assert lines[factory_at + 1] == "  - repo: local"
        assert "agent_factory_hook-mdformat" in lines[factory_at + 3]
        tests_at = lines.index("  # Project tests")
        assert lines[tests_at - 1] == ""
        assert lines[tests_at + 1] == "  - repo: local"
        assert lines[tests_at + 3] == "      - id: run-tests"
        assert mpc.merge(result, TEMPLATE, update=True) == result

    def test_update_keeps_project_keys_on_factory_hooks(self):
        """BUG-0112: a refresh replaces the keys the factory uses and keeps
        the keys a project added, such as `args:` on backlog-lint."""
        args = '        args: [--exclude, "ST-*-details.md"]'
        verbose = "        verbose: true"
        target = (
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: agent_factory_hook-backlog-lint\n"
            "        name: old name\n"
            "        entry: bash -c '[ -d .agent-factory ] || exit 0; exec .agent-factory/factory/scripts/backlog-lint' --\n"
            f"{args}\n"
            "        language: system\n"
            "      - id: agent_factory_hook-link-check\n"
            "        entry: bash -c 'exec .agent-factory/factory/scripts/link-check' --\n"
            f"{verbose}\n"
            "        additional_dependencies:\n"
            "          - some-package\n"
            "        language: system\n"
        )
        real_template = (
            Path(mpc.__file__).resolve().parent.parent / "config" / "pre-commit-config.yaml"
        ).read_text(encoding="utf-8")

        result = mpc.merge(target, real_template, update=True)
        lines = result.splitlines()

        def stanza(hook_id):
            start = lines.index(f"      - id: {hook_id}")
            end = next(
                (i for i in range(start + 1, len(lines)) if lines[i].startswith("      - id:")),
                len(lines),
            )
            return lines[start:end]

        backlog = stanza("agent_factory_hook-backlog-lint")
        link = stanza("agent_factory_hook-link-check")
        assert args in backlog
        assert "old name" not in result
        assert "[ -d .agent-factory ] || exit 0" not in result
        assert verbose in link
        assert "          - some-package" in link
        assert result.count(args) == 1
        assert mpc.merge(result, real_template, update=True) == result

    def test_strip_failure_raises_instead_of_duplicating(self):
        """If _replace_factory_block can't remove the marker, merge must abort
        rather than splice on top and duplicate."""
        target = (
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: agent_factory_hook-mdformat\n"
            "        entry: .agent-factory/factory/scripts/mdformat --number\n"
            "        language: system\n"
            "      - id: my-custom-hook\n"
            "        entry: echo hi\n"
            "        language: system\n"
        )
        with pytest.raises(ValueError, match="could not be stripped"):
            mpc.merge(target, TEMPLATE, update=True)

    @pytest.mark.spec("CAL-07-IT-04")
    def test_update_gives_every_factory_hook_the_template_files_value(self):
        """An update takes each factory hook's `files:` value from the
        template, whatever value the old block held. The project's own
        hooks keep theirs."""
        import yaml

        real_template = (
            Path(mpc.__file__).resolve().parent.parent / "config" / "pre-commit-config.yaml"
        ).read_text(encoding="utf-8")
        target = (
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: agent_factory_hook-arch-lint\n"
            "        entry: .agent-factory/factory/scripts/arch-lint\n"
            "        language: system\n"
            "        files: >-\n"
            "          ^docs/old/.*\\.dsl$\n"
            "      - id: agent_factory_hook-spec-lint\n"
            "        entry: .agent-factory/factory/scripts/spec-lint\n"
            "        language: system\n"
            "        files: ^docs/old/\n"
            "\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: own-check\n"
            "        entry: scripts/check.sh\n"
            "        language: system\n"
            "        files: ^docs/old/\n"
        )

        def files_values(text):
            return {
                hook["id"]: hook.get("files")
                for repo in yaml.safe_load(text)["repos"]
                for hook in repo["hooks"]
            }

        result = files_values(mpc.merge(target, real_template, update=True))
        template = files_values(real_template)

        for hook_id, value in template.items():
            assert result[hook_id] == value, hook_id
        assert result["own-check"] == "^docs/old/"
