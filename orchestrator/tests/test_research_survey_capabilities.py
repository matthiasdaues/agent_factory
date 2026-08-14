"""Contract tests for survey planning and synthesis capabilities (ST-0061)."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PLANNING_SKILL = _ROOT / "factory" / "skills" / "research-planning" / "SKILL.md"
_SYNTHESIS_SKILL = _ROOT / "factory" / "skills" / "research-synthesis" / "SKILL.md"
_SYNTHESIZER_AGENT = _ROOT / "factory" / "agents" / "research-synthesizer.md"
_REPORTING_SKILL = _ROOT / "factory" / "skills" / "research-reporting" / "SKILL.md"
_REPORT_WRITER = _ROOT / "factory" / "agents" / "research-report-writer.md"


class TestSurveyPlanningContract:
    """Planning selects the artifact contract named by the brief mode."""

    def test_ST0061_survey_mode_uses_the_survey_plan_contract(self):
        """An absent mode and ``survey`` use the source-grounded plan."""
        text = _PLANNING_SKILL.read_text(encoding="utf-8").lower()

        assert "omitted" in text
        assert "survey" in text
        assert "research-survey-plan.schema.json" in text
        assert "research-survey-plan.md" in text

    def test_ST0061_falsification_mode_retains_the_existing_plan_contract(self):
        """Falsification continues to use its established planning contract."""
        text = _PLANNING_SKILL.read_text(encoding="utf-8").lower()

        assert "falsification" in text
        assert "research-plan.schema.json" in text
        assert "research-plan.md" in text


class TestSurveySynthesisContract:
    """Survey synthesis remains source-grounded and explicit about its bounds."""

    def test_ST0061_synthesis_requires_cited_source_records_and_all_bounds(self):
        """Every finding is grounded and the report records its uncertainty."""
        text = _SYNTHESIS_SKILL.read_text(encoding="utf-8").lower()

        for phrase in (
            "source record",
            "source_record_refs",
            "uncertainties",
            "evidence gaps",
            "limitations",
            "candidates_for_deeper_falsification_study",
            "research-survey-report.schema.json",
        ):
            assert phrase in text

    def test_ST0061_synthesizer_has_valid_research_agent_frontmatter(self):
        """Discovery can catalog the separate synthesis role."""
        text = _SYNTHESIZER_AGENT.read_text(encoding="utf-8")

        for phrase in (
            "name: research-synthesizer",
            "title: Research Synthesizer",
            "tier: standard",
            "phase: 6",
            "phase-name: Research",
        ):
            assert phrase in text

    def test_ST0061_survey_guidance_avoids_falsification_status_language(self):
        """Survey wording never presents source synthesis as a claim verdict."""
        text = (
            _SYNTHESIS_SKILL.read_text(encoding="utf-8")
            + _SYNTHESIZER_AGENT.read_text(encoding="utf-8")
        ).lower()

        for forbidden in ("claim survival", "claim admission", "refutation", "proved"):
            assert forbidden not in text


class TestFrozenRegisterBoundary:
    """Existing falsification reporting stays separate from survey synthesis."""

    def test_ST0061_report_writer_and_reporting_require_a_frozen_claim_register(self):
        """The pre-existing report path still operates only on frozen input."""
        for file_path in (_REPORTING_SKILL, _REPORT_WRITER):
            text = file_path.read_text(encoding="utf-8").lower()
            assert "frozen claim register" in text
