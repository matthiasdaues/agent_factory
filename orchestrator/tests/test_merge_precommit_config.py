"""Tests for merge-precommit-config — the two-way pre-commit splicing script.

Covers both directions ADR-0001 documents: factory-into-project (the
script's original, documented use) and subproject-into-root (this ADR's new
use). RECON-0001: the no-op marker used to be hardcoded to `id: index-lint`,
which broke the second direction whenever the root file already contained
that id from a prior factory-into-project splice — the script would report
"already merged" and silently skip splicing the subproject's own hooks in.
The fix derives the marker from `--template`'s own first hook id instead.
"""

from __future__ import annotations

import importlib.util
import sys
import textwrap
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "factory"
    / "scripts"
    / "merge-precommit-config"
)
_loader = SourceFileLoader("merge_precommit_config", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("merge_precommit_config", _loader)
merge_precommit_config = importlib.util.module_from_spec(_spec)
sys.modules["merge_precommit_config"] = merge_precommit_config
_loader.exec_module(merge_precommit_config)

merge = merge_precommit_config.merge
extract_marker_id = merge_precommit_config.extract_marker_id


FACTORY_TEMPLATE = textwrap.dedent("""\
    repos:
      - repo: local
        hooks:
          - id: index-lint
            name: index-lint
            entry: python3 factory/scripts/index-lint
            language: system
    """)

ORCHESTRATOR_TEMPLATE = textwrap.dedent("""\
    repos:
      - repo: local
        hooks:
          - id: arch-lint-orchestrator
            name: arch-lint (orchestrator)
            entry: python3 factory/scripts/arch-lint --docs-dir orchestrator/docs
            language: system
    """)


# --- Factory-into-project direction (existing, documented behaviour) ----------


class TestFactoryIntoProject:
    def test_splices_when_not_yet_merged(self):
        target = textwrap.dedent("""\
            repos:
              - repo: some-other-hook
                rev: v1.0.0
                hooks:
                  - id: some-other-hook
            """)

        result = merge(target, FACTORY_TEMPLATE)

        assert result is not None
        assert "id: index-lint" in result
        assert "id: some-other-hook" in result

    def test_noop_when_already_merged(self):
        target = textwrap.dedent("""\
            repos:
              - repo: local
                hooks:
                  - id: index-lint
                    name: index-lint
            """)

        result = merge(target, FACTORY_TEMPLATE)

        assert result is None


# --- Subproject-into-root direction (RECON-0001 regression coverage) ----------


class TestSubprojectIntoRoot:
    def test_splices_even_though_target_already_has_factorys_marker(self):
        """The bug: target already contains `id: index-lint` from a prior
        factory-into-project splice, but does NOT yet contain the
        orchestrator template's own hook id. A hardcoded `index-lint`
        marker would wrongly no-op here; the fix must still splice."""
        target = textwrap.dedent("""\
            repos:
              - repo: local
                hooks:
                  - id: index-lint
                    name: index-lint
                    entry: python3 factory/scripts/index-lint
                    language: system
            """)

        result = merge(target, ORCHESTRATOR_TEMPLATE)

        assert result is not None
        assert "id: arch-lint-orchestrator" in result

    def test_noop_when_orchestrator_marker_already_present(self):
        target = textwrap.dedent("""\
            repos:
              - repo: local
                hooks:
                  - id: index-lint
                    name: index-lint

                  - id: arch-lint-orchestrator
                    name: arch-lint (orchestrator)
            """)

        result = merge(target, ORCHESTRATOR_TEMPLATE)

        assert result is None


# --- extract_marker_id() -------------------------------------------------------


class TestExtractMarkerId:
    def test_returns_first_hook_id_in_repo_local_block(self):
        lines = ORCHESTRATOR_TEMPLATE.splitlines()

        assert extract_marker_id(lines) == "id: arch-lint-orchestrator"

    def test_raises_rather_than_crossing_into_a_later_repo_block(self):
        """FAGAN-0001: a `repo: local` block with no hook id of its own must
        not fall through into the next top-level `- repo:` entry's id."""
        template = textwrap.dedent("""\
            repos:
              - repo: local
                hooks: []
              - repo: https://github.com/foo/bar
                rev: v1.0
                hooks:
                  - id: some-external-hook
            """)

        with pytest.raises(ValueError, match="can't derive an already-merged marker"):
            extract_marker_id(template.splitlines())
