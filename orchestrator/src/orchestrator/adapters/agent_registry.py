"""Agent registry backed by markdown agent definitions."""

from __future__ import annotations

from pathlib import Path

from orchestrator.ports import AgentInfo

_PHASE_AGENT_MAP: dict[str, dict[str, str | None]] = {
    "requirements": {
        "author": "requirements-agent",
        "reviewer": "spec-review-agent",
    },
    "architecture": {
        "author": "architecture-agent",
        "reviewer": "architecture-review-agent",
    },
    "planning": {
        "author": "planning-agent",
        "reviewer": None,
    },
    "implementation": {
        "author": "implementation-agent",
        "reviewer": "qa-agent",
    },
}


class MarkdownAgentRegistry:
    """Resolves phase agents from markdown front-matter definitions."""

    def __init__(self, agents_dir: Path) -> None:
        self.agents_dir = agents_dir

    def resolve(self, phase: str, role: str) -> AgentInfo:
        phase_agents = _PHASE_AGENT_MAP.get(phase)
        if phase_agents is None:
            raise ValueError(f"Unknown phase: {phase}")

        agent_name = phase_agents.get(role)
        if agent_name is None:
            raise ValueError(f"Unknown role for phase {phase}: {role}")

        definition_path = self.agents_dir / f"{agent_name}.md"
        if not definition_path.is_file():
            raise ValueError(f"Missing agent definition: {definition_path}")

        outputs = _parse_outputs(definition_path)
        if not outputs:
            raise ValueError(
                f"agent {agent_name} has no declared outputs — "
                f"check the frontmatter in {definition_path}"
            )

        return AgentInfo(
            name=agent_name,
            outputs=outputs,
            definition_path=definition_path,
            skills=_parse_skills(definition_path),
            tier=_parse_tier(definition_path),
            interactive=_parse_interactive(definition_path),
        )


def _parse_outputs(definition_path: Path) -> list[str]:
    return _parse_list_field(definition_path, "outputs:")


def _parse_skills(definition_path: Path) -> list[str]:
    return _parse_list_field(definition_path, "skills:")


def _parse_list_field(definition_path: Path, field_name: str) -> list[str]:
    front_matter = _read_front_matter(definition_path)
    values: list[str] = []
    collecting = False

    for line in front_matter:
        stripped = line.strip()
        if not collecting:
            if stripped == field_name:
                collecting = True
            continue

        if line.startswith("  - "):
            values.append(line[4:].strip())
            continue

        if stripped:
            break

    return values


def _parse_tier(definition_path: Path) -> str | None:
    """Parse the optional tier field from frontmatter. Returns None if absent."""
    front_matter = _read_front_matter(definition_path)
    for line in front_matter:
        stripped = line.strip()
        if stripped.startswith("tier:"):
            value = stripped[5:].strip()
            return value if value else None
    return None


def _parse_interactive(definition_path: Path) -> bool:
    """Parse the optional interactive field from frontmatter. Defaults to True."""
    front_matter = _read_front_matter(definition_path)
    for line in front_matter:
        stripped = line.strip()
        if stripped.startswith("interactive:"):
            value = stripped[12:].strip().lower()
            return value == "true"
    return True


def _read_front_matter(definition_path: Path) -> list[str]:
    lines = definition_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return []

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]

    return []
