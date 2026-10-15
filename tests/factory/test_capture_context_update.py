"""Tests for ST-0272: capture-context --update --scan mode and K lane wiring."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = (
    REPO_ROOT / "packages" / "factory" / "skills" / "capture-context" / "SKILL.md"
)
MENU_PATH = REPO_ROOT / "packages" / "factory" / "config" / "session-menu.md"

SECTION_HEADING = "## `--update --scan` (refresh existing agent-context)"


def _extract_update_scan_section(content: str) -> str:
    """Extract the --update --scan section from the SKILL.md.

    Handles fenced code blocks that may contain ## headings.
    """
    start = content.find(SECTION_HEADING)
    assert start != -1, f"Section heading not found: {SECTION_HEADING}"
    after = content[start + len(SECTION_HEADING) :]
    in_fence = False
    for i, line in enumerate(after.split("\n")):
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and i > 0 and line.startswith("## "):
            return "\n".join(after.split("\n")[:i])
    return after


class TestSkillUpdateScanSection:
    """Verify the SKILL.md contains a well-structured --update --scan section."""

    @pytest.fixture(autouse=True)
    def _load_skill(self) -> None:
        self.content = SKILL_PATH.read_text(encoding="utf-8")
        self.section = _extract_update_scan_section(self.content)

    def test_invocation_table_lists_update_scan(self) -> None:
        assert "--update --scan" in self.content

    def test_section_heading_exists(self) -> None:
        assert SECTION_HEADING in self.content

    def test_guard_step_exists(self) -> None:
        assert "### Step 0" in self.section

    def test_parse_step_exists(self) -> None:
        assert "### Step 1" in self.section

    def test_rescan_step_exists(self) -> None:
        assert "### Step 2" in self.section

    def test_diff_step_exists(self) -> None:
        assert "### Step 3" in self.section

    def test_present_step_exists(self) -> None:
        assert "### Step 4" in self.section

    def test_confirm_step_exists(self) -> None:
        assert "### Step 5" in self.section

    def test_write_step_exists(self) -> None:
        assert "### Step 6" in self.section

    def test_validate_step_exists(self) -> None:
        assert "### Step 7" in self.section

    def test_commit_step_exists(self) -> None:
        assert "### Step 8" in self.section

    def test_guard_requires_existing_file(self) -> None:
        assert "does not exist" in self.section
        assert "--init" in self.section

    def test_diff_classifies_three_types(self) -> None:
        assert "Addition" in self.section
        assert "Removal" in self.section
        assert "Path change" in self.section

    def test_presentation_grouped_by_category(self) -> None:
        assert "Cross-cutting" in self.section
        assert "Technical" in self.section
        assert "Domain" in self.section

    def test_factory_defaults_never_removed(self) -> None:
        assert "never flagged for removal" in self.section

    def test_concern_lint_validation(self) -> None:
        assert "concern-lint" in self.section

    def test_description_mentions_update(self) -> None:
        frontmatter = self.content.split("---")[1]
        assert "--update" in frontmatter


class TestSessionMenuKLane:
    """Verify session-menu.md K lane includes Update agent context."""

    @pytest.fixture(autouse=True)
    def _load_menu(self) -> None:
        self.content = MENU_PATH.read_text(encoding="utf-8")

    def test_k_lane_has_update_agent_context_action(self) -> None:
        assert "Update agent context" in self.content

    def test_k_lane_has_capture_context_reference(self) -> None:
        k_section = self.content.split("## K")[1].split("## P")[0]
        assert "capture-context" in k_section

    def test_k_lane_update_scan_mode(self) -> None:
        k_section = self.content.split("## K")[1].split("## P")[0]
        assert "--update --scan" in k_section

    def test_k_lane_missing_file_fallback(self) -> None:
        k_section = self.content.split("## K")[1].split("## P")[0]
        assert "--init --scan" in k_section

    def test_k_lane_has_five_actions(self) -> None:
        k_section = self.content.split("## K")[1].split("## P")[0]
        assert "**5** — Back to the main menu" in k_section
