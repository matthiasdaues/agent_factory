"""Tests for the research-brief, research-plan, and research-assignment
templates and schemas (ST-0019).

These three artifacts open a research effort: the brief is the playbook
input, the plan breaks it into competing conjectures and assignments, and
each assignment is one bounded piece of work handed out from the plan.

Exercises the same seam as test_schema_validate.py — `factory/scripts/
schema-validate <artifact> <schema>` run as a subprocess — plus a structural
check that each template's headings name its schema's required properties
verbatim, proving template and schema stay in lock-step.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_VALIDATE = _ROOT / "factory" / "scripts" / "schema-validate"
_SCHEMA_DIR = _ROOT / "factory" / "rulebooks" / "schemas"
_TEMPLATE_DIR = _ROOT / "factory" / "rulebooks" / "templates"


def run(artifact_path: Path, schema_path: Path) -> subprocess.CompletedProcess:
    """Invoke schema-validate shebang-agnostically, as a subprocess."""
    return subprocess.run(
        [sys.executable, str(_VALIDATE), str(artifact_path), str(schema_path)],
        capture_output=True,
        text=True,
    )


def _write_json(tmp_path: Path, name: str, data: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Well-formed fixtures, one per artifact.
# ---------------------------------------------------------------------------

_VALID_BRIEF = {
    "research_question": "Does X cause Y?",
    "intended_use": "Feeds the go/no-go decision for project Z.",
    "audience": "Engineering leadership.",
    "scope": "Public sources published in the last five years.",
    "exclusions": ["Paywalled sources", "Anonymous forum posts"],
    "freshness_requirements": ["Published within the last 24 months"],
    "source_requirements": ["Primary sources preferred over secondary"],
    "cost_of_error": "A wrong conclusion delays the project by a quarter.",
    "completion_criteria": ["All competing conjectures tested at least once"],
}

_VALID_PLAN = {
    "research_questions": ["Does X cause Y?"],
    "competing_conjectures": ["X causes Y", "Z causes Y, not X"],
    "evidence_requirements": ["At least two independent sources per claim"],
    "refutation_strategies": ["Seek disconfirming case studies"],
    "assignments": ["ASSIGN-0001", "ASSIGN-0002"],
    "review_requirements": ["Two independent reviewers per claim"],
    "stop_conditions": ["Quorum reached with no unresolved claims"],
}

_VALID_ASSIGNMENT = {
    "bounded_question": "Is there a documented case of X preceding Y?",
    "assignment_type": "direct-evidence",
}


class TestResearchBriefSchema:
    """research-brief.schema.json — the playbook input artifact."""

    _SCHEMA = _SCHEMA_DIR / "research-brief.schema.json"

    def test_wellformed_brief_passes(self, tmp_path):
        artifact = _write_json(tmp_path, "brief.json", _VALID_BRIEF)
        r = run(artifact, self._SCHEMA)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_missing_required_field_fails(self, tmp_path):
        brief = dict(_VALID_BRIEF)
        del brief["cost_of_error"]
        artifact = _write_json(tmp_path, "brief.json", brief)
        r = run(artifact, self._SCHEMA)
        assert r.returncode != 0
        assert "cost_of_error" in r.stdout


class TestResearchPlanSchema:
    """research-plan.schema.json — the plan broken into assignments."""

    _SCHEMA = _SCHEMA_DIR / "research-plan.schema.json"

    def test_wellformed_plan_passes(self, tmp_path):
        artifact = _write_json(tmp_path, "plan.json", _VALID_PLAN)
        r = run(artifact, self._SCHEMA)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_missing_required_field_fails(self, tmp_path):
        plan = dict(_VALID_PLAN)
        del plan["stop_conditions"]
        artifact = _write_json(tmp_path, "plan.json", plan)
        r = run(artifact, self._SCHEMA)
        assert r.returncode != 0
        assert "stop_conditions" in r.stdout


class TestResearchAssignmentSchema:
    """research-assignment.schema.json — one bounded piece of work."""

    _SCHEMA = _SCHEMA_DIR / "research-assignment.schema.json"

    def test_wellformed_assignment_passes(self, tmp_path):
        artifact = _write_json(tmp_path, "assignment.json", _VALID_ASSIGNMENT)
        r = run(artifact, self._SCHEMA)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_missing_required_field_fails(self, tmp_path):
        assignment = dict(_VALID_ASSIGNMENT)
        del assignment["bounded_question"]
        artifact = _write_json(tmp_path, "assignment.json", assignment)
        r = run(artifact, self._SCHEMA)
        assert r.returncode != 0
        assert "bounded_question" in r.stdout

    def test_out_of_enum_assignment_type_fails(self, tmp_path):
        assignment = dict(_VALID_ASSIGNMENT)
        assignment["assignment_type"] = "hearsay"
        artifact = _write_json(tmp_path, "assignment.json", assignment)
        r = run(artifact, self._SCHEMA)
        assert r.returncode != 0
        assert "assignment_type" in r.stdout


@pytest.mark.parametrize(
    "schema_name, template_name",
    [
        ("research-brief.schema.json", "research-brief.md"),
        ("research-plan.schema.json", "research-plan.md"),
        ("research-assignment.schema.json", "research-assignment.md"),
    ],
)
class TestTemplateMatchesSchema:
    """Proves each template's field names match its schema's field names.

    A template that renamed or dropped a field would silently desync from
    the schema it is supposed to mirror; this walks the schema's `required`
    list and asserts every property name appears verbatim in the template.
    """

    def test_every_required_property_named_in_template(
        self, schema_name, template_name
    ):
        schema = json.loads((_SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
        template_text = (_TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
        for field in schema["required"]:
            assert field in template_text, (
                f"'{field}' required by {schema_name} but missing from {template_name}"
            )
