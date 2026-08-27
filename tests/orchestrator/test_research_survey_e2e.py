"""Offline end-to-end evidence for one portable survey research run (ST-0064)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_DIR = _ROOT / "factory" / "rulebooks" / "schemas"
_VALIDATE = _ROOT / "factory" / "scripts" / "schema-validate"
_INIT_SCRIPT = _ROOT / "factory" / "scripts" / "init-factory"
_loader = SourceFileLoader("init_factory_survey_e2e", str(_INIT_SCRIPT))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules[_loader.name] = init_factory
_loader.exec_module(init_factory)


def _validate(artifact_path: Path, schema_name: str) -> subprocess.CompletedProcess:
    """Run the production schema-validation boundary for one fixture artifact."""
    return subprocess.run(
        [
            sys.executable,
            str(_VALIDATE),
            str(artifact_path),
            str(_SCHEMA_DIR / schema_name),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def _resolve_survey_findings(
    run_dir: Path, report_name: str = "report.json"
) -> set[str]:
    """Resolve every report reference to a recorded source artifact.

    Schema validation proves each finding declares a reference list, while this
    narrowly scoped fixture seam proves the independently stored records exist
    within this survey run.
    """
    report = json.loads((run_dir / report_name).read_text(encoding="utf-8"))
    records_dir = (run_dir / "source-records").resolve()
    resolved_families = set()
    for finding in report["findings"]:
        for reference in finding["source_record_refs"]:
            record_path = (run_dir / reference).resolve()
            if not record_path.is_relative_to(records_dir) or not record_path.is_file():
                raise ValueError(f"unsupported source record reference: {reference}")
            record = json.loads(record_path.read_text(encoding="utf-8"))
            resolved_families.add(record["source_family"])
    return resolved_families


def _assert_survey_run_semantics(run_dir: Path, installed_factory: Path) -> None:
    """Assert the fixture's source linkage, clean boundary, and CLI discovery."""
    assert _resolve_survey_findings(run_dir) == {"alpha-primary", "beta-primary"}

    unsupported_report = json.loads(
        (run_dir / "report.json").read_text(encoding="utf-8")
    )
    unsupported_report["findings"][0]["source_record_refs"] = [
        "source-records/not-recorded.json"
    ]
    (run_dir / "unsupported-report.json").write_text(
        json.dumps(unsupported_report), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="unsupported source record reference"):
        _resolve_survey_findings(run_dir, "unsupported-report.json")

    assert not any(
        path.exists()
        for path in (
            run_dir / "research-conjecture.json",
            run_dir / "research-test.json",
            run_dir / "research-review.json",
            run_dir / "research-vote.json",
            run_dir / "research-claim-register.json",
        )
    )

    for cli_dir in (".claude", ".github", ".pi"):
        installed = installed_factory / cli_dir
        assert (installed / "playbooks" / "research-survey.md").is_file()
        for skill in ("research-planning", "research-synthesis", "source-research"):
            assert (installed / "skills" / skill / "SKILL.md").is_file()
        for agent in ("research-orchestrator", "researcher", "research-synthesizer"):
            assert (installed / "agents" / f"{agent}.md").is_file()

    codex = installed_factory / ".codex"
    assert (codex / "playbooks" / "research-survey.md").is_file()
    for agent in ("research-orchestrator", "researcher", "research-synthesizer"):
        assert (codex / "agents" / f"{agent}.toml").is_file()
    for skill in ("research-planning", "research-synthesis", "source-research"):
        assert (installed_factory / ".agents" / "skills" / skill / "SKILL.md").is_file()


@pytest.mark.parametrize("escape_kind", ("traversal", "absolute", "symlink"))
def test_BUG0001_survey_source_references_cannot_escape_the_run(tmp_path, escape_kind):
    """Only source records canonically contained by this survey may resolve."""
    run_dir = tmp_path / "survey-run"
    records_dir = run_dir / "source-records"
    records_dir.mkdir(parents=True)
    outside_record = tmp_path / "outside.json"
    outside_record.write_text(
        json.dumps({"source_family": "outside-survey"}), encoding="utf-8"
    )

    if escape_kind == "traversal":
        reference = "../outside.json"
    elif escape_kind == "absolute":
        reference = str(outside_record)
    else:
        linked_record = records_dir / "linked.json"
        linked_record.symlink_to(outside_record)
        reference = "source-records/linked.json"

    (run_dir / "report.json").write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "title": "Unsupported",
                        "summary": "The record does not belong to this survey.",
                        "source_record_refs": [reference],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unsupported source record reference"):
        _resolve_survey_findings(run_dir)


@pytest.fixture
def installed_factory(tmp_path, monkeypatch):
    """Install Factory without unrelated runtime or hook provisioning."""
    monkeypatch.setattr(
        init_factory, "provision_usage_runtime", lambda _target, _report: False
    )
    monkeypatch.setattr(
        init_factory, "pre_commit_install", lambda _target, _report: None
    )
    assert (
        init_factory.main(
            [
                "--target",
                str(tmp_path),
                "--source",
                str(_ROOT),
                "--project-name",
                "Test Project",
            ]
        )
        == 0
    )
    return tmp_path


def test_ST0064_mode_defaulted_survey_run_validates_and_stays_outside_falsification(
    tmp_path, installed_factory
):
    """Survey artifacts validate, resolve sources, install portably, and emit no claim machinery."""
    run_dir = tmp_path / "survey-run"
    records_dir = run_dir / "source-records"
    records_dir.mkdir(parents=True)
    artifacts = {
        "brief.json": {
            "research_question": "Which community-maintained automation tools exist?",
            "intended_use": "Choose topics for a lightweight landscape survey.",
            "audience": "Factory maintainers",
            "scope": "Public project documentation",
            "exclusions": ["Ranking products"],
            "freshness_requirements": ["Use current published documentation"],
            "source_requirements": ["Record provenance"],
            "cost_of_error": "Low; findings are exploratory.",
            "completion_criteria": ["Two distinct source families are recorded."],
        },
        "plan.json": {
            "research_questions": [
                "Which community-maintained automation tools exist?"
            ],
            "search_angles": ["Official documentation"],
            "source_targets": ["Project documentation"],
            "assignments": ["Record each source under source-records/"],
            "stop_conditions": ["Two source families are represented."],
        },
        "report.json": {
            "findings": [
                {
                    "title": "Two source families are represented",
                    "summary": "The recorded documentation describes distinct projects.",
                    "source_record_refs": [
                        "source-records/alpha.json",
                        "source-records/beta.json",
                    ],
                }
            ],
            "uncertainties": ["This fixture is intentionally bounded."],
            "evidence_gaps": ["It does not compare feature completeness."],
            "limitations": ["Only recorded documentation is represented."],
            "candidates_for_deeper_falsification_study": [],
        },
    }
    source_records = {
        "alpha.json": {
            "source_identity": "Alpha project documentation",
            "author_or_issuing_body": "Alpha maintainers",
            "publisher": "Alpha project",
            "publication_date": "2026-01-01T00:00:00Z",
            "relevant_event_date": "2026-01-01",
            "source_family": "alpha-primary",
            "precise_evidence_location": "Getting started",
            "method": "Project-maintained documentation",
            "limitations": "Self-published source",
            "provenance": "Recorded from the public project documentation",
        },
        "beta.json": {
            "source_identity": "Beta project documentation",
            "author_or_issuing_body": "Beta maintainers",
            "publisher": "Beta project",
            "publication_date": "2026-01-02T00:00:00Z",
            "relevant_event_date": "2026-01-02",
            "source_family": "beta-primary",
            "precise_evidence_location": "Overview",
            "method": "Project-maintained documentation",
            "limitations": "Self-published source",
            "provenance": "Recorded from the public project documentation",
        },
    }
    for filename, artifact in artifacts.items():
        (run_dir / filename).write_text(json.dumps(artifact), encoding="utf-8")
    for filename, record in source_records.items():
        (records_dir / filename).write_text(json.dumps(record), encoding="utf-8")

    for artifact_path, schema_name in (
        (run_dir / "brief.json", "research-brief.schema.json"),
        (run_dir / "plan.json", "research-survey-plan.schema.json"),
        (records_dir / "alpha.json", "research-source-record.schema.json"),
        (records_dir / "beta.json", "research-source-record.schema.json"),
        (run_dir / "report.json", "research-survey-report.schema.json"),
    ):
        assert _validate(artifact_path, schema_name).returncode == 0

    _assert_survey_run_semantics(run_dir, installed_factory)
