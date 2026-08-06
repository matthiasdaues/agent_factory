"""Contract tests for the survey playbook and research mode front gate."""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SURVEY_PLAYBOOK = _ROOT / "factory" / "playbooks" / "research-survey.md"
_FALSIFICATION_PLAYBOOK = _ROOT / "factory" / "playbooks" / "research-topic.md"
_ORCHESTRATOR = _ROOT / "factory" / "agents" / "research-orchestrator.md"
_FACTORY_GUIDE = _ROOT / "factory" / "docs" / "factory-guide.md"
_SURVEY_DESIGN = (
    _ROOT / "docs" / "proposals" / "implemented" / "research-survey-mode.md"
)


def _step_headings(path: Path) -> list[str]:
    """Return numbered procedure headings in document order."""
    return re.findall(r"^### Step \d+ — (.+)$", path.read_text(), flags=re.MULTILINE)


class TestST0062SurveyProcedure:
    """The survey sibling exposes the complete five-step public workflow."""

    def test_ST0062_survey_steps_are_complete_and_ordered(self):
        """Validation, planning, gathering, synthesis, and validation stay ordered."""
        assert _step_headings(_SURVEY_PLAYBOOK) == [
            "Validate the Brief",
            "Plan the Survey",
            "Gather Sources",
            "Synthesise the Findings",
            "Validate the Report",
        ]

    def test_ST0062_every_survey_artifact_passes_its_applicable_gate(self):
        """Each artifact blocks progression until deterministic and semantic checks pass."""
        text = _SURVEY_PLAYBOOK.read_text().lower()

        assert text.count("**gate**:") == 5
        for artifact in (
            "research-brief.schema.json",
            "research-survey-plan.schema.json",
            "research-source-record.schema.json",
            "research-survey-report.schema.json",
        ):
            assert artifact in text
        assert "policy where applicable" in text
        assert "semantic review" in text
        assert "blocks progression" in text

    def test_ST0062_report_semantics_resolve_sources_and_reject_status_language(self):
        """The final gate checks citations and excludes claim-verdict vocabulary."""
        text = _SURVEY_PLAYBOOK.read_text().lower()

        for phrase in (
            "every finding",
            "source_record_refs",
            "recorded source",
            "survived refutation",
            "admitted",
            "validated claim",
        ):
            assert phrase in text


class TestST0062ModeFrontGate:
    """The shared entry point selects exactly one sibling playbook."""

    def test_ST0062_omitted_or_survey_mode_routes_to_survey(self):
        """Survey remains the explicit and default lightweight route."""
        for path in (_FALSIFICATION_PLAYBOOK, _ORCHESTRATOR):
            text = path.read_text().lower()
            assert "omitted" in text
            assert "`survey`" in text
            assert "research-survey.md" in text

    def test_ST0062_explicit_falsification_retains_thirteen_step_route(self):
        """Only explicit falsification enters the existing deep workflow."""
        text = _FALSIFICATION_PLAYBOOK.read_text().lower()

        assert "explicit `falsification`" in text
        assert len(_step_headings(_FALSIFICATION_PLAYBOOK)) == 13
        assert _step_headings(_FALSIFICATION_PLAYBOOK)[-1] == "Validate the Report"

    def test_FAGAN0008_orchestrator_contract_can_complete_survey_mode(self):
        """The mode-aware role declares survey outputs, handoff, and completion."""
        text = " ".join(_ORCHESTRATOR.read_text().split())

        for phrase in (
            "research-survey-plan.md (validation result)",
            "survey-report.md (validation result)",
            "- research-synthesizer",
            "In survey mode",
            "report finding resolves to a source record from the run",
            "survey report passes its release gate",
        ):
            assert phrase in text


class TestST0062OperatorGuidance:
    """Factory users can select a mode and escalate findings deliberately."""

    def test_ST0062_guide_explains_modes_and_separate_escalation_brief(self):
        """The guide distinguishes overview work from later claim testing."""
        text = _FACTORY_GUIDE.read_text().lower()

        for phrase in (
            "survey",
            "falsification",
            "research-survey.md",
            "research-topic.md",
            "new research brief",
            "candidates_for_deeper_falsification_study",
        ):
            assert phrase in text

    def test_FAGAN0009_design_records_the_implemented_schema_boundary(self):
        """The design agrees with the dedicated contracts shipped by the stories."""
        text = _SURVEY_DESIGN.read_text()

        assert "Status: implemented by ST-0060 through ST-0064" in text
        assert "dedicated plan and report schemas" in text
        assert "falsification plan and final-report schemas remain" in text
        assert "design, not yet implemented" not in text
        assert "lighter use of the) final-report schema" not in text
