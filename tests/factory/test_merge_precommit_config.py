"""Tests for merge-precommit-config splice and dedup logic."""

from __future__ import annotations

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
        entry: bash -c '[ -d factory ] || exit 0; exec factory/scripts/mdformat --number "$@"' --
        language: system
        types: [markdown]

      - id: agent_factory_hook-link-check
        name: "agent_factory: link-check"
        entry: bash -c '[ -d factory ] || exit 0; exec factory/scripts/link-check "$@"' --
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
            "        entry: factory/scripts/mdformat --number",
            "        language: system",
        ]
        assert mpc._tools_in_target(lines) == set()

    def test_factory_hook_block_skipped(self):
        lines = [
            "repos:",
            "  - repo: local",
            "    hooks:",
            "      - id: agent_factory_hook-mdformat",
            "        entry: factory/scripts/mdformat --number",
            "        language: system",
        ]
        assert mpc._tools_in_target(lines) == set()

    def test_bash_guard_entry_does_not_trigger_dedup(self):
        lines = [
            "repos:",
            "  - repo: local",
            "    hooks:",
            "      - id: mdformat",
            "        entry: bash -c '[ -d factory ] || exit 0; exec factory/scripts/mdformat --number \"$@\"' --",
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
        """Dev repo case: target has a second section using factory/scripts/mdformat.
        The dedup must NOT drop the factory hook."""
        target = (
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: agent_factory_hook-mdformat\n"
            "        entry: factory/scripts/mdformat --number\n"
            "        language: system\n"
            "      - id: agent_factory_hook-link-check\n"
            "        entry: factory/scripts/link-check\n"
            "        language: system\n"
            "\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: mdformat\n"
            "        entry: factory/scripts/mdformat --number\n"
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
            "        entry: bash -c '[ -d factory ] || exit 0; exec factory/scripts/mdformat --number \"$@\"' --\n"
            "        language: system\n"
            "      - id: agent_factory_hook-link-check\n"
            "        entry: bash -c '[ -d factory ] || exit 0; exec factory/scripts/link-check \"$@\"' --\n"
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

    def test_strip_failure_raises_instead_of_duplicating(self):
        """If _strip_factory_block can't remove the marker, merge must abort
        rather than splice on top and duplicate."""
        target = (
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: agent_factory_hook-mdformat\n"
            "        entry: factory/scripts/mdformat --number\n"
            "        language: system\n"
            "      - id: my-custom-hook\n"
            "        entry: echo hi\n"
            "        language: system\n"
        )
        with pytest.raises(ValueError, match="could not be stripped"):
            mpc.merge(target, TEMPLATE, update=True)
