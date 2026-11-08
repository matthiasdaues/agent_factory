"""Contract tests for ST-0290: outcome-grouped hook presentation and
filtered consumer hook set (`packages/factory/scripts/hook-subset`).

Owned contracts (EPIC 4 Ownership Resolution table,
docs/spec/work/value-first-onboarding-journey-qa-strategy.md):

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

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import REPO_ROOT, load_script

hs = load_script("hook-subset")

PRE_COMMIT_PATH = REPO_ROOT / "packages" / "factory" / "config" / "pre-commit-config.yaml"
METADATA_PATH = REPO_ROOT / "packages" / "factory" / "config" / "hook-metadata.yaml"

PRE_COMMIT_TEXT = PRE_COMMIT_PATH.read_text(encoding="utf-8")

# ST-0325: the template's arch-lint hook watches the DSL files in docs/spec/
# and chapter 5 in docs/arc42/.
ARCH_LINT_FILES = (
    r"^docs/(spec/(architecture|dependency-rules)\.dsl"
    r"|arc42/05_building_block_view\.md|assets/images/.*|adr/.*\.md)$"
)
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
    "agent_factory_hook-finding-lint",
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

    def test_folded_files_pattern_captured(self):
        """BUG-0113: a long regex sits on its own line under `files: >-`."""
        stanzas = {s.id: s for s in hs.parse_hook_stanzas(PRE_COMMIT_TEXT)}
        assert stanzas["agent_factory_hook-index-lint"].files.startswith(r"^(\.agent-factory/factory/agents/")
        assert stanzas["agent_factory_hook-arch-lint"].files == ARCH_LINT_FILES

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
        tracked = ["README.md", "docs/spec/features/feature.feature", "backlog/ST-0001.md"]
        assert hs.hook_matches_only_factory_internal(pattern, tracked) is True

    def test_pattern_matching_a_tracked_file_is_not_excluded(self):
        pattern = r"^docs/spec/"
        tracked = ["docs/spec/features/feature.feature"]
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
        tracked = ["README.md", "docs/spec/features/feature.feature", "backlog/ST-0001.md"]
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
            tracked_files=["README.md", "docs/spec/features/feature.feature", "backlog/ST-0001.md"],
        )
        for stanza in hs.parse_hook_stanzas("  - repo: local\n    hooks:\n" + template.split("hooks:\n", 1)[1]):
            assert not hs.hook_matches_only_factory_internal(
                stanza.files, ["README.md", "docs/spec/features/feature.feature", "backlog/ST-0001.md"]
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


# ---------------------------------------------------------------------------
# CAL-09-IT-02: a change to the DSL runs arch-lint in a template-installed
# project (Scenario Outline `A change to the DSL runs the architecture lint
# as a hook`, template row).
# ---------------------------------------------------------------------------


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.mark.skipif(shutil.which("pre-commit") is None, reason="pre-commit not installed")
def test_CAL_09_template_hook_runs_arch_lint_on_dsl_change(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / "docs" / "spec").mkdir(parents=True)
    (project / "docs" / "arc42").mkdir()
    (project / "docs" / "spec" / "architecture.dsl").write_text(
        'workspace "x" {\n  model { }\n}\n'
    )
    (project / ".pre-commit-config.yaml").write_text(PRE_COMMIT_TEXT)
    (project / ".agent-factory").mkdir()
    (project / ".agent-factory" / "factory").symlink_to(
        REPO_ROOT / "packages" / "factory"
    )
    _git(project, "init", "-q")
    _git(project, "add", "docs", ".pre-commit-config.yaml")

    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SKIP"))}
    env["PRE_COMMIT_HOME"] = str(tmp_path / "pre-commit-home")
    result = subprocess.run(
        ["pre-commit", "run", "--files", "docs/spec/architecture.dsl"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )

    lines = [
        line
        for line in result.stdout.splitlines()
        if line.startswith("agent_factory: arch-lint")
    ]
    assert len(lines) == 1, result.stdout + result.stderr
    assert lines[0].endswith("Passed"), result.stdout + result.stderr


# CAL-09-IT-02, factory row: in this repository, a change to the DSL selects
# both the factory hook and the repository's own `arch-lint` hook. The test
# runs a copy of this repository's .pre-commit-config.yaml in a scratch Git
# repository, so pre-commit never touches this checkout's index.


@pytest.mark.skipif(shutil.which("pre-commit") is None, reason="pre-commit not installed")
def test_CAL_09_factory_repository_hooks_run_arch_lint_on_dsl_change(
    tmp_path: Path,
) -> None:
    project = tmp_path / "factory"
    (project / "docs" / "spec").mkdir(parents=True)
    (project / "docs" / "arc42").mkdir()
    (project / "docs" / "spec" / "architecture.dsl").write_text(
        'workspace "x" {\n  model { }\n}\n'
    )
    (project / ".pre-commit-config.yaml").write_text(
        (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    )
    (project / "packages").symlink_to(REPO_ROOT / "packages")
    (project / ".agent-factory").mkdir()
    (project / ".agent-factory" / "factory").symlink_to(
        REPO_ROOT / "packages" / "factory"
    )
    _git(project, "init", "-q")
    _git(project, "add", "docs", ".pre-commit-config.yaml")

    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SKIP"))}
    env["PRE_COMMIT_HOME"] = str(tmp_path / "pre-commit-home")
    result = subprocess.run(
        ["pre-commit", "run", "--files", "docs/spec/architecture.dsl"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )

    output = result.stdout + result.stderr
    arch_lint = [
        line
        for line in result.stdout.splitlines()
        if line.startswith(("agent_factory: arch-lint", "arch-lint ("))
    ]
    assert len(arch_lint) == 2, output
    assert all(line.endswith("Passed") for line in arch_lint), output


# ---------------------------------------------------------------------------
# ST-0396: the finding-lint hook (FC-12-CT-01, FC-12-CT-02, FC-12-IT-01).
# ---------------------------------------------------------------------------

FINDING_LINT_ID = "agent_factory_hook-finding-lint"


def _finding_lint_hook() -> dict:
    import yaml

    hooks = {
        hook["id"]: hook
        for repo in yaml.safe_load(PRE_COMMIT_TEXT)["repos"]
        for hook in repo["hooks"]
    }
    return hooks[FINDING_LINT_ID]


@pytest.mark.spec("FC-12-CT-01")
def test_st_0396_hook_runs_finding_lint_staged_on_docs_findings():
    hook = _finding_lint_hook()

    assert re.search(r'finding-lint --staged\' --$', hook["entry"].strip())
    assert hook["always_run"] is True
    assert "files" not in hook
    assert hook["pass_filenames"] is False
    assert hook["language"] == "system"


@pytest.mark.spec("FC-12-CT-02")
def test_st_0396_metadata_makes_the_hook_part_of_every_fitting():
    meta = hs.load_hook_metadata(METADATA_TEXT)[FINDING_LINT_ID]

    assert meta.trade_off == "none"
    assert meta.availability == "always"
    assert meta.outcome
    assert meta.description


def install_finding_lint_hook(project: Path) -> None:
    """Link the Factory into *project* and write .git/hooks/pre-commit as a
    shell script that runs the hook's entry, so no pre-commit install is needed."""
    (project / ".agent-factory").mkdir(exist_ok=True)
    link = project / ".agent-factory" / "factory"
    if not link.exists():
        link.symlink_to(REPO_ROOT / "packages" / "factory")
    script = project / ".git" / "hooks" / "pre-commit"
    script.parent.mkdir(exist_ok=True)
    script.write_text("#!/bin/sh\n" + _finding_lint_hook()["entry"].strip() + "\n")
    script.chmod(0o755)


def git_commit_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SKIP"))}
    env.update(
        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
    )
    return env


def run_git(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=project, env=git_commit_env(),
        capture_output=True, text=True, check=False,
    )


@pytest.mark.spec("FC-12-IT-01")
def test_st_0396_commit_of_a_broken_finding_exits_1_through_the_hook(tmp_path):
    from test_finding_stop import finding

    project = tmp_path / "project"
    project.mkdir()
    assert run_git(project, "init", "-q", "-b", "dev").returncode == 0
    (project / "README.md").write_text("init\n")
    run_git(project, "add", "README.md")
    assert run_git(project, "commit", "-qm", "init").returncode == 0
    install_finding_lint_hook(project)

    path = project / "docs" / "findings" / "BUG-0037.md"
    path.parent.mkdir(parents=True)
    path.write_text(finding(severity="major"))  # the basis computes critical
    run_git(project, "add", "docs/findings/BUG-0037.md")
    broken = run_git(project, "commit", "-qm", "record BUG-0037")

    assert broken.returncode == 1, broken.stdout + broken.stderr
    assert "BUG-0037" in broken.stdout + broken.stderr

    path.write_text(finding())
    run_git(project, "add", "docs/findings/BUG-0037.md")
    fixed = run_git(project, "commit", "-qm", "record BUG-0037")

    assert fixed.returncode == 0, fixed.stdout + fixed.stderr
