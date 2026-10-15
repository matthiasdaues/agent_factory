"""Contract tests for ST-0290: outcome-grouped hook presentation and
filtered consumer hook set (`packages/factory/scripts/hook-subset`).

Owned contracts (EPIC 4 Ownership Resolution table,
docs/spec/value-first-onboarding-journey-qa-strategy.md):

  - VFO-07-LN-01 — Consumer hook set omits ignored runtime triggers and
    `index-lint` (`Scenario: Consumer hook set omits source-only
    triggers`, BUG-0029).
  - "Hook choices describe protected outcomes and material trade-offs"
    (`Scenario: Hook choices describe protected outcomes and material
    trade-offs`) — outcome grouping, consent only for auto-fix /
    material-cost, unavailable hooks described rather than erroring.

Real `packages/factory/config/pre-commit-config.yaml` and
`hook-metadata.yaml` are used as fixtures throughout — this is the actual
Factory hook set, not a synthetic stand-in — with explicit `tracked_files`
lists and `tmp_path` repo roots so availability and BUG-0029 checks stay
deterministic and independent of this checkout's own git state.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from conftest import REPO_ROOT, load_script

hs = load_script("hook-subset")

PRE_COMMIT_PATH = REPO_ROOT / "packages" / "factory" / "config" / "pre-commit-config.yaml"
METADATA_PATH = REPO_ROOT / "packages" / "factory" / "config" / "hook-metadata.yaml"

PRE_COMMIT_TEXT = PRE_COMMIT_PATH.read_text(encoding="utf-8")
METADATA_TEXT = METADATA_PATH.read_text(encoding="utf-8")

ALL_HOOK_IDS = [
    "agent_factory_hook-mdformat",
    "agent_factory_hook-link-check",
    "agent_factory_hook-mermaid-lint",
    "agent_factory_hook-spec-lint",
    "agent_factory_hook-arch-lint",
    "agent_factory_hook-backlog-lint",
    "agent_factory_hook-concern-lint",
    "agent_factory_hook-matrix-lint",
    "agent_factory_hook-statemachine-lint",
    "agent_factory_hook-index-lint",
]


@pytest.fixture
def fully_available_root(tmp_path: Path) -> Path:
    """A repo root satisfying every `requires-path:` availability
    condition in the real hook-metadata.yaml."""
    (tmp_path / "docs" / "spec").mkdir(parents=True)
    (tmp_path / "docs" / "arc42").mkdir(parents=True)
    (tmp_path / "backlog").mkdir(parents=True)
    (tmp_path / "docs" / "agent-context.md").write_text("# context\n")
    return tmp_path


class TestParseHookStanzas:
    def test_finds_every_hook_id_in_source_order(self):
        stanzas = hs.parse_hook_stanzas(PRE_COMMIT_TEXT)
        assert [s.id for s in stanzas] == ALL_HOOK_IDS

    def test_matrix_lint_files_pattern_captured(self):
        stanzas = {s.id: s for s in hs.parse_hook_stanzas(PRE_COMMIT_TEXT)}
        assert stanzas["agent_factory_hook-matrix-lint"].files == r"^\.agent-factory/config/model\.conf$"

    def test_mdformat_has_no_files_key(self):
        stanzas = {s.id: s for s in hs.parse_hook_stanzas(PRE_COMMIT_TEXT)}
        assert stanzas["agent_factory_hook-mdformat"].files is None


class TestLoadHookMetadata:
    def test_every_hook_has_metadata(self):
        metadata = hs.load_hook_metadata(METADATA_TEXT)
        assert set(metadata) == set(ALL_HOOK_IDS)

    def test_mdformat_is_auto_fix_and_always_available(self):
        metadata = hs.load_hook_metadata(METADATA_TEXT)
        meta = metadata["agent_factory_hook-mdformat"]
        assert meta.outcome == "Formatting"
        assert meta.trade_off == "auto-fix"
        assert meta.availability == "always"
        assert meta.description

    def test_arch_lint_requires_arc42_path(self):
        metadata = hs.load_hook_metadata(METADATA_TEXT)
        meta = metadata["agent_factory_hook-arch-lint"]
        assert meta.availability == "requires-path:docs/arc42"
        assert meta.trade_off in {"auto-fix", "material-cost"}


class TestAvailability:
    def test_always_available(self):
        meta = hs.HookMeta(outcome="x", trade_off="none", availability="always", description="d")
        available, reason = hs.is_available(meta, Path("/nonexistent"))
        assert available is True
        assert reason is None

    def test_requires_path_present(self, tmp_path: Path):
        (tmp_path / "docs" / "spec").mkdir(parents=True)
        meta = hs.HookMeta(
            outcome="x", trade_off="none", availability="requires-path:docs/spec", description="d"
        )
        available, reason = hs.is_available(meta, tmp_path)
        assert available is True
        assert reason is None

    def test_requires_path_absent_returns_description_not_error(self, tmp_path: Path):
        meta = hs.HookMeta(
            outcome="x",
            trade_off="none",
            availability="requires-path:docs/spec",
            description="Needs docs/spec/ to exist.",
        )
        available, reason = hs.is_available(meta, tmp_path)
        assert available is False
        assert reason == "Needs docs/spec/ to exist."


class TestFactoryInternalOnlyMatch:
    """BUG-0029: a hook whose `files:` trigger can only ever match a
    gitignored `.agent-factory/factory/` path never fires against a real
    commit, tested against a representative `git ls-files` list."""

    def test_pattern_anchored_under_factory_internal_with_no_tracked_match_is_excluded(self):
        pattern = r"^\.agent-factory/factory/agents/.*\.md$"
        tracked = ["README.md", "docs/spec/feature.feature", "backlog/ST-0001.md"]
        assert hs.hook_matches_only_factory_internal(pattern, tracked) is True

    def test_pattern_matching_a_tracked_file_is_not_excluded(self):
        pattern = r"^docs/spec/"
        tracked = ["docs/spec/feature.feature"]
        assert hs.hook_matches_only_factory_internal(pattern, tracked) is False

    def test_pattern_not_mentioning_factory_internal_prefix_is_never_excluded_by_this_rule(self):
        pattern = r"^docs/nonexistent/"
        tracked = ["README.md"]
        assert hs.hook_matches_only_factory_internal(pattern, tracked) is False

    def test_absent_files_pattern_is_not_excluded(self):
        assert hs.hook_matches_only_factory_internal(None, ["README.md"]) is False

    def test_index_lint_pattern_matches_only_factory_internal(self):
        stanzas = {s.id: s for s in hs.parse_hook_stanzas(PRE_COMMIT_TEXT)}
        index_lint_files = stanzas["agent_factory_hook-index-lint"].files
        tracked = ["README.md", "docs/spec/feature.feature", "backlog/ST-0001.md"]
        assert hs.hook_matches_only_factory_internal(index_lint_files, tracked) is True


class TestBuildDecisions:
    def test_index_lint_is_excluded_unconditionally(self, fully_available_root: Path):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=fully_available_root, tracked_files=[]
        )
        by_id = {d.id: d for d in decisions}
        index_lint = by_id["agent_factory_hook-index-lint"]
        assert index_lint.excluded is True
        assert index_lint.included is False
        assert index_lint.exclude_reason is not None

    def test_matrix_lint_is_available_and_included(self, fully_available_root: Path):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=fully_available_root, tracked_files=[]
        )
        by_id = {d.id: d for d in decisions}
        matrix_lint = by_id["agent_factory_hook-matrix-lint"]
        assert matrix_lint.available is True
        assert matrix_lint.excluded is False
        assert matrix_lint.needs_consent is False
        assert matrix_lint.included is True

    def test_mdformat_needs_consent_and_is_not_pre_approved(self, fully_available_root: Path):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=fully_available_root, tracked_files=[]
        )
        by_id = {d.id: d for d in decisions}
        mdformat = by_id["agent_factory_hook-mdformat"]
        assert mdformat.needs_consent is True
        assert mdformat.included is False  # asking has not happened yet

    def test_no_automatic_file_change_no_material_cost_hooks_auto_include(
        self, fully_available_root: Path
    ):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=fully_available_root, tracked_files=[]
        )
        by_id = {d.id: d for d in decisions}
        for hook_id in ("agent_factory_hook-link-check", "agent_factory_hook-mermaid-lint"):
            decision = by_id[hook_id]
            assert decision.needs_consent is False
            assert decision.included is True

    def test_unavailable_hook_has_description_not_error(self, tmp_path: Path):
        """No docs/arc42, docs/spec, backlog, or agent-context.md present."""
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=tmp_path, tracked_files=[]
        )
        by_id = {d.id: d for d in decisions}
        for hook_id in ("agent_factory_hook-arch-lint", "agent_factory_hook-spec-lint"):
            decision = by_id[hook_id]
            assert decision.available is False
            assert decision.unavailable_reason  # a description, not empty/None
            assert decision.excluded is False  # unavailable != excluded-as-error
            assert decision.included is False

    def test_unavailable_hooks_still_appear_in_decisions_not_dropped(self, tmp_path: Path):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=tmp_path, tracked_files=[]
        )
        assert "agent_factory_hook-arch-lint" in {d.id for d in decisions}


class TestGroupByOutcome:
    def test_groups_hooks_under_their_protected_outcome(self, fully_available_root: Path):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=fully_available_root, tracked_files=[]
        )
        grouped = hs.group_by_outcome(decisions)
        assert grouped["Formatting"][0].id == "agent_factory_hook-mdformat"
        spec_consistency_ids = {d.id for d in grouped["Specification consistency"]}
        assert spec_consistency_ids == {
            "agent_factory_hook-link-check",
            "agent_factory_hook-mermaid-lint",
            "agent_factory_hook-spec-lint",
            "agent_factory_hook-statemachine-lint",
        }

    def test_every_decision_appears_in_exactly_one_group(self, fully_available_root: Path):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=fully_available_root, tracked_files=[]
        )
        grouped = hs.group_by_outcome(decisions)
        total_grouped = sum(len(hooks) for hooks in grouped.values())
        assert total_grouped == len(decisions)


class TestApplyApprovals:
    def test_declined_auto_fix_hook_is_absent(self, fully_available_root: Path):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=fully_available_root, tracked_files=[]
        )
        result = hs.apply_approvals(decisions, approved_ids=set())
        assert "agent_factory_hook-mdformat" not in result
        assert "agent_factory_hook-arch-lint" not in result

    def test_approved_auto_fix_hook_is_present(self, fully_available_root: Path):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=fully_available_root, tracked_files=[]
        )
        result = hs.apply_approvals(
            decisions, approved_ids={"agent_factory_hook-mdformat"}
        )
        assert "agent_factory_hook-mdformat" in result
        assert "agent_factory_hook-arch-lint" not in result  # still not approved

    def test_index_lint_absent_regardless_of_approval(self, fully_available_root: Path):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=fully_available_root, tracked_files=[]
        )
        result = hs.apply_approvals(
            decisions, approved_ids={"agent_factory_hook-index-lint"}
        )
        assert "agent_factory_hook-index-lint" not in result

    def test_matrix_lint_is_last(self, fully_available_root: Path):
        decisions = hs.build_decisions(
            PRE_COMMIT_TEXT, METADATA_TEXT, repo_root=fully_available_root, tracked_files=[]
        )
        result = hs.apply_approvals(decisions, approved_ids=set(ALL_HOOK_IDS))
        assert result[-1] == "agent_factory_hook-matrix-lint"
        assert "agent_factory_hook-statemachine-lint" in result[:-1]


class TestBuildConsumerTemplate:
    def test_omits_index_lint(self, fully_available_root: Path):
        template = hs.build_consumer_template(
            PRE_COMMIT_TEXT,
            METADATA_TEXT,
            repo_root=fully_available_root,
            approved_ids=set(ALL_HOOK_IDS),
            tracked_files=[],
        )
        assert "agent_factory_hook-index-lint" not in template

    def test_matrix_lint_stanza_last_and_uses_always_run(self, fully_available_root: Path):
        template = hs.build_consumer_template(
            PRE_COMMIT_TEXT,
            METADATA_TEXT,
            repo_root=fully_available_root,
            approved_ids=set(ALL_HOOK_IDS),
            tracked_files=[],
        )
        ids_in_order = re.findall(r"- id:\s*(\S+)", template)
        assert ids_in_order[-1] == "agent_factory_hook-matrix-lint"
        assert r"files: ^\.agent-factory/config/model\.conf$" not in template
        assert "always_run: true" in template

    def test_no_generated_hook_matches_only_ignored_factory_runtime_paths(
        self, fully_available_root: Path
    ):
        """VFO-07-LN-01 / BUG-0029, end to end through the generator."""
        template = hs.build_consumer_template(
            PRE_COMMIT_TEXT,
            METADATA_TEXT,
            repo_root=fully_available_root,
            approved_ids=set(ALL_HOOK_IDS),
            tracked_files=["README.md", "docs/spec/feature.feature", "backlog/ST-0001.md"],
        )
        for stanza in hs.parse_hook_stanzas("  - repo: local\n    hooks:\n" + template.split("hooks:\n", 1)[1]):
            assert not hs.hook_matches_only_factory_internal(
                stanza.files, ["README.md", "docs/spec/feature.feature", "backlog/ST-0001.md"]
            )

    def test_declining_all_optional_hooks_still_yields_valid_template(
        self, fully_available_root: Path
    ):
        template = hs.build_consumer_template(
            PRE_COMMIT_TEXT,
            METADATA_TEXT,
            repo_root=fully_available_root,
            approved_ids=set(),
            tracked_files=[],
        )
        assert template.startswith("  - repo: local\n    hooks:\n")
        assert "agent_factory_hook-mdformat" not in template
        assert "agent_factory_hook-link-check" in template  # trade_off: none, auto-included


class TestWrapsMergePrecommitConfig:
    """Boundaries: hook-subset wraps merge-precommit-config; it does not
    duplicate its splicing logic."""

    def test_generated_template_splices_cleanly(self, fully_available_root: Path):
        mpc = load_script("merge-precommit-config")
        template = hs.build_consumer_template(
            PRE_COMMIT_TEXT,
            METADATA_TEXT,
            repo_root=fully_available_root,
            approved_ids={"agent_factory_hook-mdformat"},
            tracked_files=[],
        )
        target = "repos:\n  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        result = mpc.merge(target, template)
        assert result is not None
        assert "agent_factory_hook-mdformat" in result
        assert "agent_factory_hook-index-lint" not in result


class TestCLISmoke:
    """One golden-path exercise of the CLI entry point end to end."""

    def test_present_subcommand_prints_grouped_json(
        self, fully_available_root: Path, capsys: pytest.CaptureFixture[str]
    ):
        rc = hs.main(
            [
                "present",
                "--pre-commit",
                str(PRE_COMMIT_PATH),
                "--metadata",
                str(METADATA_PATH),
                "--repo-root",
                str(fully_available_root),
            ]
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "Formatting" in out
        assert "agent_factory_hook-mdformat" in out

    def test_generate_subcommand_prints_consumer_template(
        self, fully_available_root: Path, capsys: pytest.CaptureFixture[str]
    ):
        rc = hs.main(
            [
                "generate",
                "--pre-commit",
                str(PRE_COMMIT_PATH),
                "--metadata",
                str(METADATA_PATH),
                "--repo-root",
                str(fully_available_root),
                "--approve",
                "agent_factory_hook-mdformat",
            ]
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "agent_factory_hook-mdformat" in out
        assert "agent_factory_hook-index-lint" not in out
