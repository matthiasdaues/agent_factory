"""Contract tests for ST-0287: first-session project insight and
value-first configuration ordering.

Owned contracts (EPIC 4 Ownership Resolution table,
docs/spec/value-first-onboarding-journey-qa-strategy.md):

  - First session reports evidence without changing the project
    (`Scenario: First session reports evidence without changing the
    project`) — checked here as a static content contract: the agent
    definition states the read-only key-value report and its unknown-value
    language. The dynamic, end-to-end version of this scenario (VFO-06-AC-01)
    is owned by `tests/factory/test_onboarding_journey.py`, not yet built.
  - Advanced configuration waits for a dependent action (VFO-06-CT-01,
    `Scenario: Advanced configuration waits for a dependent action`).

`Scenario: Ready-host insight meets the decision and time bounds` has no
automated contract-owner row in the QA strategy (time/decision budgets are
measured by the moderated journey protocol in EPIC 6) — this file states
the documented budget but does not attempt to measure it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VIRGIL_PATH = REPO_ROOT / "packages" / "factory" / "agents" / "virgil.md"
CAPTURE_CONTEXT_PATH = (
    REPO_ROOT / "packages" / "factory" / "skills" / "capture-context" / "SKILL.md"
)

INSIGHT_HEADING = "## First-session insight"
FITTING_HEADING = "## Fitting"


def _normalize(text: str) -> str:
    """Collapse whitespace runs (including line wraps) to single spaces so
    phrase assertions survive Markdown line wrapping."""
    return re.sub(r"\s+", " ", text)


def _section(content: str, start_heading: str, end_heading: str | None) -> str:
    start = content.index(start_heading)
    if end_heading is None:
        return content[start:]
    end = content.index(end_heading, start + len(start_heading))
    return content[start:end]


class TestFirstSessionInsightSection:
    """Static content contract for the read-only insight report."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.content = VIRGIL_PATH.read_text(encoding="utf-8")
        self.normalized = _normalize(self.content)
        self.section = _normalize(
            _section(self.content, INSIGHT_HEADING, FITTING_HEADING)
        )

    def test_insight_section_exists(self) -> None:
        assert INSIGHT_HEADING in self.content

    def test_insight_precedes_fitting(self) -> None:
        assert self.content.index(INSIGHT_HEADING) < self.content.index(
            FITTING_HEADING
        )

    def test_reuses_init_factory_detection_logic(self) -> None:
        # No re-implemented detection: the scan is documented as reusing
        # init-factory's constants rather than duplicating them.
        assert "init-factory" in self.section
        assert "LANGUAGE_MANIFESTS" in self.section
        assert "SCAN_SKIP_DIRS" in self.section

    def test_key_value_fields_named(self) -> None:
        for field in ("Stack", "Test entry", "Safety signal", "Recommended action"):
            assert field in self.section

    def test_unknown_stack_and_test_entry_stated_explicitly(self) -> None:
        assert "not detected" in self.section

    def test_unknown_safety_signal_stated_explicitly(self) -> None:
        assert "none observed" in self.section

    def test_recommended_action_order(self) -> None:
        context_idx = self.section.index("Context capture")
        gate_idx = self.section.index("Gate demonstration")
        hook_idx = self.section.index("Hook configuration")
        assert context_idx < gate_idx < hook_idx

    def test_recommends_exactly_one_action(self) -> None:
        assert "exactly one action" in self.section

    def test_scan_performs_no_writes(self) -> None:
        # VFO-026: the initial scan distinguishes observations, unknowns,
        # and recommendations, and performs no writes.
        assert "VFO-026" in self.section
        assert "changes no project file" in self.section

    def test_time_and_decision_bounds_documented(self) -> None:
        assert "two minutes" in self.section
        assert "three user decisions" in self.section


class TestAdvancedConfigurationDeferred:
    """VFO-06-CT-01: configuration appears only before an action that needs
    it. The newcomer sees no model-tier, hook, or extended-context question
    until they select an action that depends on it."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.content = VIRGIL_PATH.read_text(encoding="utf-8")
        self.normalized = _normalize(self.content)
        self.insight_section = _normalize(
            _section(self.content, INSIGHT_HEADING, FITTING_HEADING)
        )

    def test_insight_defers_model_tiers_hooks_and_context(self) -> None:
        assert (
            "Do not ask about model tiers, hooks, or extended context"
            in self.insight_section
        )

    def test_fitting_intro_gates_on_selected_action(self) -> None:
        fitting_intro_end = self.content.index("### 0.")
        intro = _normalize(self.content[self.content.index(FITTING_HEADING) : fitting_intro_end])
        assert "starts only after the newcomer selects" in intro

    def test_model_matrix_step_still_documented(self) -> None:
        # Step 0 (model matrix) is not deleted, only gated — it still runs
        # once reached via the deferred path.
        assert "### 0. Configure the model matrix" in self.content


class TestCaptureContextInvokedAsRecommendedAction:
    """The capture-context skill is offered as the first-session
    recommended action, not run automatically at session start."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.content = CAPTURE_CONTEXT_PATH.read_text(encoding="utf-8")
        self.normalized = _normalize(self.content)

    def test_invocation_note_references_first_session_insight(self) -> None:
        assert "first-session insight recommends context capture" in self.normalized

    def test_scan_not_automatic_at_session_start(self) -> None:
        assert "does not run automatically at session start" in self.normalized


class TestGreenfieldRoutesToInsight:
    """The CLI orientation files route greenfield projects through the
    first-session insight before showing the session menu."""

    AGENTS_DIR = REPO_ROOT / "packages" / "factory" / "config"

    @pytest.fixture(params=["AGENTS.claude.md", "AGENTS.pi.md",
                            "AGENTS.codex.md", "AGENTS.copilot.md"])
    def agents_content(self, request: pytest.FixtureRequest) -> str:
        return (self.AGENTS_DIR / request.param).read_text(encoding="utf-8")

    def test_greenfield_triggers_first_session_insight(self, agents_content: str) -> None:
        assert '"greenfield"' in agents_content
        assert "First-session insight" in agents_content

    def test_greenfield_checked_before_fallthrough(self, agents_content: str) -> None:
        greenfield_pos = agents_content.index('"greenfield"')
        fallthrough = '`"unfitted"`, `"fitting"`, or `"greenfield"`'
        fallthrough_pos = agents_content.index(fallthrough)
        assert greenfield_pos < fallthrough_pos
