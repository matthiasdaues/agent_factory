from __future__ import annotations

from pathlib import Path

import pytest

from orchestrator.adapters.agent_registry import MarkdownAgentRegistry
from orchestrator.ports import AgentInfo


def _write_agent(
    agents_dir: Path,
    name: str,
    outputs: list[str],
    skills: list[str] | None = None,
    tier: str | None = None,
    interactive: bool | None = None,
) -> Path:
    definition_path = agents_dir / f"{name}.md"
    rendered_outputs = "\n".join(f"  - {output}" for output in outputs)
    lines = [
        "---",
        f"name: {name}",
    ]
    if tier:
        lines.append(f"tier: {tier}")
    if interactive is not None:
        lines.append(f"interactive: {str(interactive).lower()}")
    if skills:
        lines.append("skills:")
        lines.extend(f"  - {s}" for s in skills)
    lines.extend(
        [
            "outputs:",
            rendered_outputs,
            "---",
            f"# {name}",
            "...",
            "",
        ]
    )
    definition_path.write_text("\n".join(lines), encoding="utf-8")
    return definition_path


@pytest.fixture
def agents_dir(tmp_path: Path) -> Path:
    agents = tmp_path / "agents"
    agents.mkdir()
    return agents


def test_resolve_happy_path_returns_correct_agent_info(agents_dir: Path):
    definition_path = _write_agent(
        agents_dir,
        "requirements-agent",
        ["docs/spec/prd.md", "docs/spec/actor-goal-list.md"],
        skills=["capture-vision", "clarify-requirements"],
    )

    registry = MarkdownAgentRegistry(agents_dir)

    assert registry.resolve("requirements", "author") == AgentInfo(
        name="requirements-agent",
        outputs=["docs/spec/prd.md", "docs/spec/actor-goal-list.md"],
        definition_path=definition_path,
        skills=["capture-vision", "clarify-requirements"],
    )


def test_unknown_phase_raises_value_error(agents_dir: Path):
    registry = MarkdownAgentRegistry(agents_dir)

    with pytest.raises(ValueError, match="Unknown phase"):
        registry.resolve("discovery", "author")


def test_unknown_role_raises_value_error(agents_dir: Path):
    registry = MarkdownAgentRegistry(agents_dir)

    with pytest.raises(ValueError, match="Unknown role"):
        registry.resolve("requirements", "approver")


def test_missing_agent_file_raises_value_error(agents_dir: Path):
    registry = MarkdownAgentRegistry(agents_dir)

    with pytest.raises(ValueError, match="Missing agent definition"):
        registry.resolve("planning", "author")


def test_outputs_are_parsed_from_front_matter(agents_dir: Path):
    _write_agent(
        agents_dir,
        "implementation-agent",
        [
            "src/orchestrator/phase_runner.py",
            "src/orchestrator/adapters/agent_registry.py",
        ],
    )

    registry = MarkdownAgentRegistry(agents_dir)

    resolved = registry.resolve("implementation", "author")

    assert resolved.outputs == [
        "src/orchestrator/phase_runner.py",
        "src/orchestrator/adapters/agent_registry.py",
    ]


def test_skills_are_parsed_from_front_matter(agents_dir: Path):
    _write_agent(
        agents_dir,
        "requirements-agent",
        ["docs/spec/prd.md"],
        skills=["capture-vision", "write-prd", "derive-spec"],
    )

    registry = MarkdownAgentRegistry(agents_dir)
    resolved = registry.resolve("requirements", "author")

    assert resolved.skills == ["capture-vision", "write-prd", "derive-spec"]


def test_agent_without_skills_returns_empty_list(agents_dir: Path):
    _write_agent(agents_dir, "planning-agent", ["backlog/"])

    registry = MarkdownAgentRegistry(agents_dir)
    resolved = registry.resolve("planning", "author")

    assert resolved.skills == []


def test_agent_without_outputs_raises_value_error(agents_dir: Path):
    definition_path = agents_dir / "planning-agent.md"
    definition_path.write_text(
        "\n".join(
            [
                "---",
                "name: planning-agent",
                "outputs: [backlog/]",
                "---",
                "# planning-agent",
                "",
            ]
        ),
        encoding="utf-8",
    )

    registry = MarkdownAgentRegistry(agents_dir)

    with pytest.raises(ValueError, match="has no declared outputs"):
        registry.resolve("planning", "author")


def test_tier_is_parsed_from_front_matter(agents_dir: Path):
    _write_agent(
        agents_dir,
        "qa-agent",
        ["docs/reviews/fagan-review-*.md"],
        skills=["fagan-review"],
        tier="strong",
    )

    registry = MarkdownAgentRegistry(agents_dir)
    resolved = registry.resolve("implementation", "reviewer")

    assert resolved.tier == "strong"


def test_agent_without_tier_returns_none(agents_dir: Path):
    _write_agent(agents_dir, "planning-agent", ["backlog/"])

    registry = MarkdownAgentRegistry(agents_dir)
    resolved = registry.resolve("planning", "author")

    assert resolved.tier is None


def test_interactive_is_parsed_from_front_matter_when_true(agents_dir: Path):
    _write_agent(
        agents_dir,
        "requirements-agent",
        ["docs/spec/prd.md"],
        interactive=True,
    )

    registry = MarkdownAgentRegistry(agents_dir)
    resolved = registry.resolve("requirements", "author")

    assert resolved.interactive is True


def test_interactive_is_parsed_from_front_matter_when_false(agents_dir: Path):
    _write_agent(
        agents_dir,
        "qa-agent",
        ["docs/reviews/fagan-review-*.md"],
        interactive=False,
    )

    registry = MarkdownAgentRegistry(agents_dir)
    resolved = registry.resolve("implementation", "reviewer")

    assert resolved.interactive is False


def test_agent_without_interactive_defaults_to_true(agents_dir: Path):
    _write_agent(agents_dir, "planning-agent", ["backlog/"])

    registry = MarkdownAgentRegistry(agents_dir)
    resolved = registry.resolve("planning", "author")

    assert resolved.interactive is True


def test_happy_path_with_tier_and_interactive(agents_dir: Path):
    definition_path = _write_agent(
        agents_dir,
        "qa-agent",
        ["docs/reviews/fagan-review-*.md"],
        skills=["fagan-review", "security-review"],
        tier="strong",
        interactive=False,
    )

    registry = MarkdownAgentRegistry(agents_dir)

    assert registry.resolve("implementation", "reviewer") == AgentInfo(
        name="qa-agent",
        outputs=["docs/reviews/fagan-review-*.md"],
        definition_path=definition_path,
        skills=["fagan-review", "security-review"],
        tier="strong",
        interactive=False,
    )
