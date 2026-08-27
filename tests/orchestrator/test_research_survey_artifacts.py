"""Contract tests for source-grounded survey research artifacts (ST-0060)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
_VALIDATE = _ROOT / "factory" / "scripts" / "schema-validate"
_SCHEMAS = _ROOT / "factory" / "rulebooks" / "schemas"
_TEMPLATES = _ROOT / "factory" / "rulebooks" / "templates"

_BRIEF_SCHEMA = _SCHEMAS / "research-brief.schema.json"
_FALSIFICATION_PLAN_SCHEMA = _SCHEMAS / "research-plan.schema.json"
_FALSIFICATION_REPORT_SCHEMA = _SCHEMAS / "research-final-report.schema.json"
_SURVEY_PLAN_SCHEMA = _SCHEMAS / "research-survey-plan.schema.json"
_SURVEY_REPORT_SCHEMA = _SCHEMAS / "research-survey-report.schema.json"

_VALID_BRIEF = {
    "research_question": "Which public tools support a given workflow?",
    "intended_use": "Choose tools to evaluate in a later study.",
    "audience": "Engineering leadership.",
    "scope": "Publicly documented tools.",
    "exclusions": ["Undocumented tools"],
    "freshness_requirements": ["Documentation current this year"],
    "source_requirements": ["Official documentation preferred"],
    "cost_of_error": "A short, recoverable evaluation delay.",
    "completion_criteria": ["Each question has sourced findings."],
}

_VALID_SURVEY_PLAN = {
    "research_questions": ["Which public tools support the workflow?"],
    "search_angles": ["Official documentation", "Maintainer release notes"],
    "source_targets": ["Official project documentation", "Primary maintainers"],
    "assignments": ["Survey one bounded tool category."],
    "stop_conditions": ["All planned source targets are examined."],
}

_VALID_SURVEY_REPORT = {
    "findings": [
        {
            "title": "Several tools document workflow support",
            "summary": "The cited project documentation describes the workflow.",
            "source_record_refs": ["source-records/tool-a.json"],
        }
    ],
    "uncertainties": ["Documentation may not reflect current operational use."],
    "evidence_gaps": ["No independent operational comparison was found."],
    "limitations": ["Only public documentation was surveyed."],
    "candidates_for_deeper_falsification_study": [
        "Whether one tool improves delivery time in this environment."
    ],
}


def _write_json(tmp_path: Path, name: str, data: dict[str, Any]) -> Path:
    """Write one disposable JSON artifact for the production validation seam."""
    artifact = tmp_path / name
    artifact.write_text(json.dumps(data), encoding="utf-8")
    return artifact


def _validate(artifact: Path, schema: Path) -> subprocess.CompletedProcess[str]:
    """Invoke the schema gate exactly as research artifact consumers do."""
    return subprocess.run(
        [sys.executable, str(_VALIDATE), str(artifact), str(schema)],
        capture_output=True,
        check=False,
        text=True,
    )


class TestResearchBriefMode:
    """The shared brief defaults to survey and limits its explicit modes."""

    def test_ST0060_omitted_mode_is_valid_and_declares_survey_default(self, tmp_path):
        result = _validate(
            _write_json(tmp_path, "brief.json", _VALID_BRIEF), _BRIEF_SCHEMA
        )

        assert result.returncode == 0, result.stdout + result.stderr
        schema = json.loads(_BRIEF_SCHEMA.read_text(encoding="utf-8"))
        assert schema["properties"]["mode"]["default"] == "survey"

    def test_ST0060_accepts_each_supported_explicit_mode(self, tmp_path):
        for mode in ("survey", "falsification"):
            brief = {**_VALID_BRIEF, "mode": mode}
            result = _validate(
                _write_json(tmp_path, f"{mode}-brief.json", brief), _BRIEF_SCHEMA
            )

            assert result.returncode == 0, result.stdout + result.stderr

    def test_ST0060_rejects_an_unknown_mode(self, tmp_path):
        result = _validate(
            _write_json(tmp_path, "brief.json", {**_VALID_BRIEF, "mode": "hybrid"}),
            _BRIEF_SCHEMA,
        )

        assert result.returncode != 0
        assert "mode" in result.stdout


class TestSurveyPlanContract:
    """Survey planning records bounded source-search work without conjectures."""

    def test_ST0060_well_formed_survey_plan_passes(self, tmp_path):
        result = _validate(
            _write_json(tmp_path, "survey-plan.json", _VALID_SURVEY_PLAN),
            _SURVEY_PLAN_SCHEMA,
        )

        assert result.returncode == 0, result.stdout + result.stderr

    def test_ST0060_missing_required_survey_plan_field_fails(self, tmp_path):
        plan = dict(_VALID_SURVEY_PLAN)
        del plan["search_angles"]

        result = _validate(
            _write_json(tmp_path, "survey-plan.json", plan), _SURVEY_PLAN_SCHEMA
        )

        assert result.returncode != 0
        assert "search_angles" in result.stdout

    def test_ST0060_malformed_survey_plan_assignment_fails(self, tmp_path):
        result = _validate(
            _write_json(
                tmp_path,
                "survey-plan.json",
                {**_VALID_SURVEY_PLAN, "assignments": "not a bounded assignment list"},
            ),
            _SURVEY_PLAN_SCHEMA,
        )

        assert result.returncode != 0
        assert "assignments" in result.stdout


class TestSurveyReportContract:
    """Survey findings remain directly grounded in recorded sources."""

    def test_ST0060_well_formed_survey_report_passes(self, tmp_path):
        result = _validate(
            _write_json(tmp_path, "survey-report.json", _VALID_SURVEY_REPORT),
            _SURVEY_REPORT_SCHEMA,
        )

        assert result.returncode == 0, result.stdout + result.stderr

    def test_ST0060_finding_without_source_record_reference_fails(self, tmp_path):
        report = dict(_VALID_SURVEY_REPORT)
        report["findings"] = [{"title": "Unsupported", "summary": "No source."}]

        result = _validate(
            _write_json(tmp_path, "survey-report.json", report), _SURVEY_REPORT_SCHEMA
        )

        assert result.returncode != 0
        assert "source_record_refs" in result.stdout

    def test_ST0060_empty_source_record_references_fail(self, tmp_path):
        report = dict(_VALID_SURVEY_REPORT)
        report["findings"] = [
            {"title": "Unsupported", "summary": "No source.", "source_record_refs": []}
        ]

        result = _validate(
            _write_json(tmp_path, "survey-report.json", report), _SURVEY_REPORT_SCHEMA
        )

        assert result.returncode != 0
        assert "source_record_refs" in result.stdout

    def test_ST0060_falsification_finding_fields_are_rejected_by_survey_report(
        self, tmp_path
    ):
        report = dict(_VALID_SURVEY_REPORT)
        report["findings"] = [
            {
                **_VALID_SURVEY_REPORT["findings"][0],
                "surviving_claim_refs": ["CLAIM-0001"],
            }
        ]

        result = _validate(
            _write_json(tmp_path, "survey-report.json", report), _SURVEY_REPORT_SCHEMA
        )

        assert result.returncode != 0
        assert "surviving_claim_refs" in result.stdout

    def test_ST0060_missing_required_report_section_fails(self, tmp_path):
        report = dict(_VALID_SURVEY_REPORT)
        del report["candidates_for_deeper_falsification_study"]

        result = _validate(
            _write_json(tmp_path, "survey-report.json", report), _SURVEY_REPORT_SCHEMA
        )

        assert result.returncode != 0
        assert "candidates_for_deeper_falsification_study" in result.stdout


class TestCrossModeRegression:
    """Existing falsification contracts stay independent and valid."""

    def test_ST0060_existing_falsification_plan_remains_valid(self, tmp_path):
        plan = {
            "research_questions": ["Does X cause Y?"],
            "competing_conjectures": ["X causes Y"],
            "evidence_requirements": ["Direct evidence"],
            "refutation_strategies": ["Seek contrary evidence"],
            "assignments": ["ASSIGN-0001"],
            "review_requirements": ["Independent review"],
            "stop_conditions": ["Review is complete"],
        }

        result = _validate(
            _write_json(tmp_path, "plan.json", plan), _FALSIFICATION_PLAN_SCHEMA
        )

        assert result.returncode == 0, result.stdout + result.stderr

    def test_ST0060_existing_falsification_report_remains_valid(self, tmp_path):
        report = {
            "findings": [{"surviving_claim_refs": ["CLAIM-0001"]}],
            "refuted_conjectures": [],
            "unresolved_alternatives": [],
            "recommendations": [],
            "evidence_gaps": [],
            "limitations": [],
        }

        result = _validate(
            _write_json(tmp_path, "final-report.json", report),
            _FALSIFICATION_REPORT_SCHEMA,
        )

        assert result.returncode == 0, result.stdout + result.stderr


def test_ST0060_templates_name_every_required_contract_field():
    """Keep the survey authoring guidance synchronized with required fields."""
    for schema_name, template_name in (
        ("research-survey-plan.schema.json", "research-survey-plan.md"),
        ("research-survey-report.schema.json", "research-survey-report.md"),
    ):
        schema = json.loads((_SCHEMAS / schema_name).read_text(encoding="utf-8"))
        template = (_TEMPLATES / template_name).read_text(encoding="utf-8")

        for field in schema["required"]:
            assert field in template
