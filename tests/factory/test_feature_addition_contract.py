"""Contract tests for the feature-addition playbook."""

from __future__ import annotations

from pathlib import Path

import yaml

PLAYBOOK = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "factory"
    / "playbooks"
    / "feature-addition.md"
)


def _step(name: str) -> dict:
    """Return one declared playbook step from its public frontmatter contract."""
    _, frontmatter, _ = PLAYBOOK.read_text(encoding="utf-8").split("---", 2)
    document = yaml.safe_load(frontmatter)
    return next(step for step in document["steps"] if step["name"] == name)


def test_spec_review_can_read_project_terminology() -> None:
    assert "docs/CONTEXT.md" in _step("spec-review")["inputs"]


def test_spec_review_can_persist_its_mandatory_report() -> None:
    assert "docs/reviews/spec-review-*.md" in _step("spec-review")["outputs"]


def test_requirements_remediation_can_read_spec_findings() -> None:
    assert "docs/findings/SPEC-*.md" in _step("update-specification")["inputs"]


def test_requirements_remediation_can_correct_the_accepted_proposal() -> None:
    assert "docs/proposals/**/*.md" in _step("update-specification")["outputs"]
