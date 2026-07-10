"""Prompt composer backed by agent and context files."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from orchestrator.entities import AgentRole, Finding, InvocationContext
from orchestrator.ports import AgentInfo


def skill_scoped_call_to_action(skill: str) -> str:
    """Call-to-action text for a skill-scoped ``run-step`` invocation (BR-051).

    Skill scoping is a prompt-composition rule, not an agent-definition
    rewrite: the full agent definition is preserved unchanged, and this text
    is the only thing that narrows the invocation to one declared skill's
    workflow step instead of the agent's full workflow.
    """
    return (
        f'Execute only the "{skill}" skill\'s workflow step, as defined in '
        "your Agent Definition above. Do not execute the full workflow or "
        "any other skill."
    )


class FilePromptComposer:
    """Compose prompts from agent definitions, context files, and findings."""

    def __init__(self) -> None:
        pass

    def compose(
        self,
        agent_info: AgentInfo,
        context_paths: List[Path],
        invocation: InvocationContext,
        findings: Optional[List[Finding]] = None,
        skill: Optional[str] = None,
    ) -> str:
        if not agent_info.definition_path.is_file():
            raise FileNotFoundError(agent_info.definition_path)

        sections = [
            "# Agent Definition",
            agent_info.definition_path.read_text(encoding="utf-8").rstrip(),
            "# Project Context",
            self._render_context(context_paths),
        ]

        if findings:
            sections.extend(
                [
                    "# Findings from Prior Iteration",
                    "\n".join(self._format_finding(finding) for finding in findings),
                ]
            )

        sections.extend(
            [
                "# Call to Action",
                self._call_to_action(
                    invocation, has_findings=bool(findings), skill=skill
                ),
            ]
        )

        return "\n\n".join(section for section in sections if section)

    def _call_to_action(
        self,
        invocation: InvocationContext,
        *,
        has_findings: bool = False,
        skill: Optional[str] = None,
    ) -> str:
        if skill:
            return skill_scoped_call_to_action(skill)

        if invocation.phase == "standalone":
            return "Execute the workflow defined in your Agent Definition above."

        if invocation.role == AgentRole.AUTHOR:
            if invocation.iteration == 0:
                return (
                    f"Begin the {invocation.phase} phase. Execute the workflow "
                    "defined in your Agent Definition above, starting at Step 1."
                )
            if has_findings:
                return (
                    f"This is iteration {invocation.iteration} of the "
                    f"{invocation.phase} phase. Address the findings listed above, "
                    "then re-execute your workflow."
                )
            return (
                f"This is iteration {invocation.iteration} of the "
                f"{invocation.phase} phase. Your prior attempt failed the gate. "
                "Re-execute your workflow and ensure all changes are committed."
            )

        if invocation.iteration == 0:
            return (
                f"Review the {invocation.phase} artifacts. Follow the review "
                "workflow in your Agent Definition. File findings per the "
                "specified format."
            )
        return (
            f"This is iteration {invocation.iteration} of the "
            f"{invocation.phase} review. The author has addressed prior findings. "
            "Re-review the artifacts and file any remaining issues."
        )

    def _render_context(self, context_paths: List[Path]) -> str:
        rendered_contexts: list[str] = []
        for path in context_paths:
            if not path.is_file():
                continue
            rendered_contexts.append(
                f"## {path.name}\n{path.read_text(encoding='utf-8').rstrip()}"
            )
        return "\n\n".join(rendered_contexts)

    def _format_finding(self, finding: Finding) -> str:
        return (
            f"[{finding.severity.value.upper()}] "
            f"{finding.code} {finding.artifact}: {finding.message}"
        )
