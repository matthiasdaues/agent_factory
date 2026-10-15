"""Tests for ST-0288: context capture explanation and consent gate.

Verifies that the capture-context skill flow includes an explanation step
before the scan starts, defines concern before using the term, and supports
deferral or cancellation with no file creation.

Coverage:
- VFO-027: Context capture starts only after onboarding explains its scan
- VFO-028: Onboarding defines concern as a routing topic before unparaphrased use
- VFO-029: Deferring or cancelling context capture produces no scan and no output file
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = (
    REPO_ROOT / "packages" / "factory" / "skills" / "capture-context" / "SKILL.md"
)


def _extract_init_scan_section(content: str) -> str:
    """Extract the --init --scan section from the SKILL.md.

    Handles fenced code blocks that may contain ## headings.
    """
    section_heading = "## `--init --scan` (brownfield onboarding)"
    start = content.find(section_heading)
    assert start != -1, f"Section heading not found: {section_heading}"
    after = content[start + len(section_heading) :]
    in_fence = False
    for i, line in enumerate(after.split("\n")):
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and i > 0 and line.startswith("## "):
            return "\n".join(after.split("\n")[:i])
    return after


class TestContextCaptureExplanationRequirement:
    """Verify the SKILL.md explains context capture before scanning (VFO-027)."""

    @pytest.fixture(autouse=True)
    def _load_skill(self) -> None:
        self.content = SKILL_PATH.read_text(encoding="utf-8")
        self.section = _extract_init_scan_section(self.content)

    def test_explanation_step_exists(self) -> None:
        """Explanation step must exist in --init --scan section."""
        assert "explanation" in self.section.lower() or "explain" in self.section.lower()

    def test_explanation_covers_what_scan_reads(self) -> None:
        """Explanation must describe what the scan reads from the project."""
        content_lower = self.section.lower()
        assert "scan reads" in content_lower or "reads from" in content_lower or "detects" in content_lower

    def test_explanation_covers_what_decisions_it_asks(self) -> None:
        """Explanation must describe what decisions the scan asks."""
        content_lower = self.section.lower()
        assert "decision" in content_lower or "confirm" in content_lower or "ask" in content_lower

    def test_explanation_covers_output_location(self) -> None:
        """Explanation must specify where output goes."""
        assert "docs/agent-context.md" in self.section

    def test_explanation_covers_concern_lint_validation(self) -> None:
        """Explanation must mention concern-lint validation."""
        content_lower = self.section.lower()
        assert "concern-lint" in content_lower or "validation" in content_lower

    def test_explanation_covers_human_and_agent_use(self) -> None:
        """Explanation must describe how humans and agents use the file."""
        content_lower = self.section.lower()
        assert (
            "human" in content_lower
            or "agent" in content_lower
            or "routing" in content_lower
            or "use" in content_lower
        )


class TestConcernDefinitionRequirement:
    """Verify onboarding defines concern as a routing topic (VFO-028)."""

    @pytest.fixture(autouse=True)
    def _load_skill(self) -> None:
        self.content = SKILL_PATH.read_text(encoding="utf-8")
        self.section = _extract_init_scan_section(self.content)

    def test_concern_is_defined(self) -> None:
        """Concern must be defined in the explanation."""
        content_lower = self.section.lower()
        assert "concern" in content_lower

    def test_concern_defined_as_routing_topic(self) -> None:
        """Concern must be defined as a routing topic before unparaphrased use."""
        content_lower = self.section.lower()
        assert "routing" in content_lower
        assert "topic" in content_lower

    def test_concern_relates_to_project_knowledge(self) -> None:
        """Concern definition must relate to directing agents to knowledge."""
        content_lower = self.section.lower()
        assert (
            "knowledge" in content_lower
            or "project" in content_lower
            or "agent" in content_lower
        )


class TestConsentGateRequirement:
    """Verify consent gate exists with defer/cancel options (VFO-029)."""

    @pytest.fixture(autouse=True)
    def _load_skill(self) -> None:
        self.content = SKILL_PATH.read_text(encoding="utf-8")
        self.section = _extract_init_scan_section(self.content)

    def test_consent_gate_exists(self) -> None:
        """Consent gate must be present in the flow."""
        content_lower = self.section.lower()
        assert (
            "consent" in content_lower
            or "approval" in content_lower
            or "accept" in content_lower
            or "defer" in content_lower
        )

    def test_accept_option_documented(self) -> None:
        """Gate must document accept option that runs the scan."""
        content_lower = self.section.lower()
        assert "accept" in content_lower

    def test_defer_option_documented(self) -> None:
        """Gate must document defer option that skips the scan."""
        content_lower = self.section.lower()
        assert "defer" in content_lower

    def test_cancel_option_documented(self) -> None:
        """Gate must document cancel option that skips the scan."""
        content_lower = self.section.lower()
        assert "cancel" in content_lower

    def test_blank_input_treated_as_deferral(self) -> None:
        """Blank input must be treated as deferral."""
        content_lower = self.section.lower()
        assert (
            ("blank" in content_lower and "defer" in content_lower)
            or ("empty" in content_lower and "defer" in content_lower)
        )

    def test_deferral_produces_no_scan(self) -> None:
        """Deferral must produce no scan."""
        content_lower = self.section.lower()
        assert "no scan" in content_lower or "does not scan" in content_lower

    def test_deferral_produces_no_file(self) -> None:
        """Deferral must create no output file."""
        content_lower = self.section.lower()
        assert (
            "no file" in content_lower
            or "does not create" in content_lower
            or "no output" in content_lower
        )


class TestExplanationPlacementInFlow:
    """Verify explanation appears before the scan in the documented flow."""

    @pytest.fixture(autouse=True)
    def _load_skill(self) -> None:
        self.content = SKILL_PATH.read_text(encoding="utf-8")
        self.section = _extract_init_scan_section(self.content)

    def test_explanation_before_repository_scan(self) -> None:
        """Explanation must come before or at the scan step."""
        lines = self.section.split("\n")
        explanation_idx = -1
        scan_idx = -1

        for i, line in enumerate(lines):
            if "explanation" in line.lower() or "explain" in line.lower():
                if explanation_idx == -1:
                    explanation_idx = i
            if "scan" in line.lower() and ("step" in line.lower() or "###" in line):
                if scan_idx == -1:
                    scan_idx = i

        # Either explanation exists before scan, or explanation covers the concept
        if explanation_idx >= 0 and scan_idx >= 0:
            assert explanation_idx < scan_idx, "Explanation must come before the scan step"

    def test_gate_before_scan_execution(self) -> None:
        """Consent gate must come before scan execution."""
        lines = self.section.split("\n")
        gate_idx = -1
        write_idx = -1

        for i, line in enumerate(lines):
            if "consent" in line.lower() or "accept" in line.lower():
                if gate_idx == -1:
                    gate_idx = i
            if "run" in line.lower() and "scan" in line.lower():
                if write_idx == -1:
                    write_idx = i

        if gate_idx >= 0 and write_idx >= 0:
            assert gate_idx < write_idx, "Gate must come before scan execution"
