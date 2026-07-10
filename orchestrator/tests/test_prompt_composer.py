from __future__ import annotations

from pathlib import Path

import pytest

from orchestrator.adapters.prompt_composer import FilePromptComposer
from orchestrator.entities import (
    AgentRole,
    Finding,
    FindingSource,
    FindingStatus,
    InvocationContext,
    Severity,
)
from orchestrator.ports import AgentInfo


def _agent_info(definition_path: Path) -> AgentInfo:
    return AgentInfo(
        name="implementation-agent",
        outputs=["src/orchestrator/adapters/prompt_composer.py"],
        definition_path=definition_path,
    )


def _finding() -> Finding:
    return Finding(
        id="FND-0001",
        phase="implementation",
        iteration=1,
        source=FindingSource.SEMANTIC,
        code="SEM-001",
        severity=Severity.WARNING,
        artifact="src/orchestrator/phase_runner.py",
        message="Handle missing approvals before advancing.",
        status=FindingStatus.OPEN,
    )


def _invocation() -> InvocationContext:
    return InvocationContext(phase="implementation", role=AgentRole.AUTHOR, iteration=0)


def test_compose_with_agent_and_context_files_returns_combined_content(tmp_path: Path):
    definition_path = tmp_path / "implementation-agent.md"
    definition_path.write_text("# Agent\nImplement the phase.\n", encoding="utf-8")
    context_path = tmp_path / "CONTEXT.md"
    context_path.write_text("Project context\n", encoding="utf-8")
    activation_path = tmp_path / "ACTIVATION.md"
    activation_path.write_text("Activation steps\n", encoding="utf-8")

    prompt = FilePromptComposer().compose(
        _agent_info(definition_path),
        [context_path, activation_path],
        _invocation(),
    )

    assert "# Agent Definition" in prompt
    assert "# Agent\nImplement the phase." in prompt
    assert "# Project Context" in prompt
    assert "## CONTEXT.md\nProject context" in prompt
    assert "## ACTIVATION.md\nActivation steps" in prompt
    assert "# Call to Action" in prompt
    assert (
        "Begin the implementation phase. Execute the workflow defined in your "
        "Agent Definition above, starting at Step 1."
    ) in prompt


def test_compose_with_findings_appends_findings_section(tmp_path: Path):
    definition_path = tmp_path / "implementation-agent.md"
    definition_path.write_text("# Agent\nImplement the phase.\n", encoding="utf-8")

    prompt = FilePromptComposer().compose(
        _agent_info(definition_path),
        [],
        _invocation(),
        findings=[_finding()],
    )

    assert "# Findings from Prior Iteration" in prompt
    assert (
        "[WARNING] SEM-001 src/orchestrator/phase_runner.py: "
        "Handle missing approvals before advancing."
    ) in prompt
    assert prompt.index("# Findings from Prior Iteration") < prompt.index(
        "# Call to Action"
    )
    assert prompt.rstrip().endswith(
        "Begin the implementation phase. Execute the workflow defined in your "
        "Agent Definition above, starting at Step 1."
    )


def test_compose_without_findings_omits_findings_section(tmp_path: Path):
    definition_path = tmp_path / "implementation-agent.md"
    definition_path.write_text("# Agent\nImplement the phase.\n", encoding="utf-8")

    prompt = FilePromptComposer().compose(
        _agent_info(definition_path),
        [],
        _invocation(),
    )

    assert "# Findings from Prior Iteration" not in prompt


@pytest.mark.parametrize(
    ("invocation", "expected"),
    [
        (
            InvocationContext(
                phase="implementation", role=AgentRole.AUTHOR, iteration=0
            ),
            (
                "Begin the implementation phase. Execute the workflow defined in "
                "your Agent Definition above, starting at Step 1."
            ),
        ),
        (
            InvocationContext(
                phase="implementation", role=AgentRole.AUTHOR, iteration=2
            ),
            (
                "This is iteration 2 of the implementation phase. Your prior "
                "attempt failed the gate. Re-execute your workflow and ensure "
                "all changes are committed."
            ),
        ),
        (
            InvocationContext(
                phase="implementation", role=AgentRole.REVIEWER, iteration=0
            ),
            (
                "Review the implementation artifacts. Follow the review workflow "
                "in your Agent Definition. File findings per the specified format."
            ),
        ),
        (
            InvocationContext(
                phase="implementation", role=AgentRole.REVIEWER, iteration=3
            ),
            (
                "This is iteration 3 of the implementation review. The author "
                "has addressed prior findings. Re-review the artifacts and file "
                "any remaining issues."
            ),
        ),
        (
            InvocationContext(phase="standalone", role=AgentRole.AUTHOR, iteration=4),
            "Execute the workflow defined in your Agent Definition above.",
        ),
    ],
)
def test_call_to_action_selects_correct_template(
    invocation: InvocationContext, expected: str
):
    assert FilePromptComposer()._call_to_action(invocation) == expected


def test_call_to_action_author_loopback_with_findings():
    invocation = InvocationContext(
        phase="implementation", role=AgentRole.AUTHOR, iteration=2
    )
    result = FilePromptComposer()._call_to_action(invocation, has_findings=True)
    assert result == (
        "This is iteration 2 of the implementation phase. Address the "
        "findings listed above, then re-execute your workflow."
    )


def test_missing_agent_file_raises_file_not_found_error(tmp_path: Path):
    definition_path = tmp_path / "missing-agent.md"

    with pytest.raises(FileNotFoundError):
        FilePromptComposer().compose(
            _agent_info(definition_path),
            [],
            _invocation(),
        )


def test_missing_context_file_is_skipped_gracefully(tmp_path: Path):
    definition_path = tmp_path / "implementation-agent.md"
    definition_path.write_text("# Agent\nImplement the phase.\n", encoding="utf-8")
    existing_context = tmp_path / "CONTEXT.md"
    existing_context.write_text("Project context\n", encoding="utf-8")
    missing_context = tmp_path / "MISSING.md"

    prompt = FilePromptComposer().compose(
        _agent_info(definition_path),
        [existing_context, missing_context],
        _invocation(),
    )

    assert "## CONTEXT.md\nProject context" in prompt
    assert "MISSING.md" not in prompt
