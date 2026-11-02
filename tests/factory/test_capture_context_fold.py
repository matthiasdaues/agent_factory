"""Text check of `capture-context --fold-context-map` (CAL-08-LN-01).

Covers the first four Scenarios of `Rule: Project maintainer folds context
routing into the agent context file` in core-artifact-layout.feature: one
folded domain concern per listed context, the routing-only `CONTEXT.md`, the
link rewrite to `docs/agent-context.md`, and the old files that only the
developer deletes. The fold mark and the review order are settled in ST-0328
(gaps CAL-G03 and CAL-G14).

The skill is prose, so each test reads one mode section of `SKILL.md` and
checks the statements the contract needs. `mode_section()` cuts any mode
section, so a later rule (for example the rescan of `--update --scan`) adds
its own test class here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = (
    REPO_ROOT / "packages" / "factory" / "skills" / "capture-context" / "SKILL.md"
)
TEMPLATE_PATH = (
    REPO_ROOT / "packages" / "factory" / "rulebooks" / "templates" / "context-map.md"
)

FOLD_HEADING = "## `--fold-context-map`"
UPDATE_SCAN_HEADING = "## `--update --scan`"

FOLD_MARK = "Folded: yes"

#: Old-path patterns of the proposal's Completion Criteria greps.
OLD_PATH_PATTERNS = [
    r"supplementary_specs",
    r"docs/arc42/[a-z-]+\.dsl",
    r"docs/spec/[^/]+\.feature",
    r"docs/spec/prd\.md",
    r"docs/spec/[^/]+-(gaps|qa-strategy)\.md",
    r"docs/spec/todos?\.md",
    r"docs/arc42/themes",
    r"arc42/\(architecture",
    r"UC-XX",
    r"use_cases",
    r"actor-goal-list",
]

#: The old routing files. Only the fold section of the skill may name them.
OLD_ROUTING_RE = re.compile(r"CONTEXT(-MAP)?\.md")


def normalize(text: str) -> str:
    """Collapse whitespace runs so phrase checks survive line wrapping."""
    return re.sub(r"\s+", " ", text)


def mode_section(content: str, heading_prefix: str) -> str:
    """Return the `##` section whose heading starts with `heading_prefix`,
    up to the next `##` heading outside a code fence."""
    lines = content.split("\n")
    start = next(
        (i for i, line in enumerate(lines) if line.startswith(heading_prefix)), None
    )
    assert start is not None, f"no section heading starts with {heading_prefix!r}"
    in_fence = False
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("```"):
            in_fence = not in_fence
        if not in_fence and lines[i].startswith("## "):
            return "\n".join(lines[start:i])
    return "\n".join(lines[start:])


def steps(section: str) -> list[str]:
    """Return the `### Step` sections of a mode section, in order."""
    return re.split(r"\n(?=### Step )", section)[1:]


@pytest.fixture(scope="module")
def skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def fold(skill: str) -> str:
    return mode_section(skill, FOLD_HEADING)


class TestFoldModeDefined:
    """CAL-08-LN-01: the skill defines the mode and lists it."""

    def test_invocation_table_lists_the_mode(self, skill: str) -> None:
        invocation = mode_section(skill, "## Invocation")
        assert "| `capture-context --fold-context-map`" in invocation

    def test_section_has_ordered_steps(self, fold: str) -> None:
        numbers = [int(m) for m in re.findall(r"^### Step (\d+)", fold, re.MULTILINE)]
        assert numbers == list(range(len(numbers)))
        assert len(numbers) >= 7


class TestFoldReadsAndWrites:
    """Scenarios: one domain concern per listed context; a routing-only
    `CONTEXT.md` is read."""

    def test_guard_names_init_when_agent_context_is_missing(self, fold: str) -> None:
        guard = normalize(steps(fold)[0])
        assert "docs/agent-context.md" in guard
        assert "does not exist" in guard
        assert "capture-context --init" in guard

    def test_reads_the_context_map(self, fold: str) -> None:
        assert "docs/arc42/CONTEXT-MAP.md" in fold

    def test_reads_routing_only_context_files_and_skips_language(
        self, fold: str
    ) -> None:
        text = normalize(fold)
        assert "routing-only" in text
        assert "`## Language`" in text
        assert "migrate-spec-layout" in text

    def test_one_domain_concern_per_context(self, fold: str) -> None:
        text = normalize(fold)
        assert "one domain concern per context" in text
        assert "## Domain concerns" in text

    def test_each_concern_carries_the_fold_mark(self, fold: str) -> None:
        assert FOLD_MARK in fold
        assert "directly after the description" in normalize(fold)

    def test_concerns_route_to_the_glossary(self, fold: str) -> None:
        assert "docs/spec/glossary.md" in fold

    def test_read_paths_never_name_the_old_routing_files(self, fold: str) -> None:
        assert "never names a `CONTEXT.md` or `CONTEXT-MAP.md`" in normalize(fold)


class TestFoldRewritesLinks:
    """Scenario: the fold points every link at the agent context file."""

    def test_rewrites_links_under_docs_to_agent_context(self, fold: str) -> None:
        text = normalize(fold)
        assert "Markdown link under `docs/`" in text
        assert "points at `docs/agent-context.md`" in text


class TestFoldReviewAndValidation:
    """CAL-G14: the developer confirms before the write; the skill then shows
    the `concern-lint` result."""

    def test_confirmation_comes_before_the_write(self, fold: str) -> None:
        titles = [s.split("\n", 1)[0] for s in steps(fold)]
        review = next(i for i, t in enumerate(titles) if "Review" in t)
        write = next(i for i, t in enumerate(titles) if "Write" in t)
        assert review < write
        assert "Write nothing before the developer confirms" in normalize(
            steps(fold)[review]
        )

    def test_runs_concern_lint_after_the_write(self, fold: str) -> None:
        titles = [s.split("\n", 1)[0] for s in steps(fold)]
        write = next(i for i, t in enumerate(titles) if "Write" in t)
        validate = next(i for i, t in enumerate(titles) if "Validate" in t)
        assert write < validate
        assert "concern-lint" in steps(fold)[validate]


class TestFoldNeverDeletes:
    """Scenario: the old routing files are gone only after the developer
    deletes them."""

    def test_mode_never_deletes_the_old_files(self, fold: str) -> None:
        assert "never deletes" in normalize(fold).lower()

    def test_names_the_deletion_as_the_developers_next_step(self, fold: str) -> None:
        last = normalize(steps(fold)[-2] + steps(fold)[-1])
        assert "developer deletes" in last
        assert "link-check" in last


class TestSkillLayout:
    """The skill names old routing files only in the fold section, and no old
    path of the core layout anywhere (CAL-13-LN-02 for this file)."""

    def test_old_routing_files_named_only_in_fold_section(
        self, skill: str, fold: str
    ) -> None:
        outside = skill.replace(fold, "")
        assert OLD_ROUTING_RE.findall(outside) == []

    @pytest.mark.parametrize("pattern", OLD_PATH_PATTERNS)
    def test_no_old_path(self, skill: str, pattern: str) -> None:
        assert re.findall(pattern, skill) == []

    def test_context_map_template_removed(self) -> None:
        assert not TEMPLATE_PATH.exists()


@pytest.fixture(scope="module")
def rescan(skill: str) -> str:
    return mode_section(skill, UPDATE_SCAN_HEADING)


class TestRescanKeepsFoldedConcerns:
    """CAL-08-LN-01, Scenario: a later rescan keeps every folded concern.
    `--update --scan` reads the fold mark and never offers to remove a concern
    that carries it, also when it is not a scope-map area."""

    def test_parse_step_reads_the_fold_mark(self, rescan: str) -> None:
        assert FOLD_MARK in normalize(steps(rescan)[1])

    def test_diff_step_excludes_folded_concerns_from_removal(
        self, rescan: str
    ) -> None:
        diff = normalize(steps(rescan)[3])
        assert f"A domain concern with the fold mark `{FOLD_MARK}`" in diff
        assert "never flagged for removal, also when it is not a scope-map area" in (
            diff
        )

    @pytest.mark.parametrize("pattern", OLD_PATH_PATTERNS)
    def test_rescan_section_names_no_old_path(self, rescan: str, pattern: str) -> None:
        assert re.findall(pattern, rescan) == []
