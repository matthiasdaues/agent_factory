"""ST-0052 — run-step --skill validation and skill-scoped prompt composition.

Traces: UC-11, FR-S1, FR-S2, FR-S3, BR-050, BR-051, BR-052, VR-038.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator.adapters.prompt_composer import (
    FilePromptComposer,
    skill_scoped_call_to_action,
)
from orchestrator.cli import (
    _handle_run_step,
    _load_step_agent,
    _validate_skill,
    build_parser,
)
from orchestrator.entities import AgentRole, InvocationContext
from orchestrator.ports import AgentInfo


def _agent_info(skills: list[str], definition_path: Path | None = None) -> AgentInfo:
    return AgentInfo(
        name="qa-agent",
        outputs=["docs/findings/*.md"],
        definition_path=definition_path or Path("/nonexistent/qa-agent.md"),
        skills=skills,
    )


# ---------------------------------------------------------------------------
# Seam 1: CLI argument parser — FR-S1
# ---------------------------------------------------------------------------


def test_skill_flag_is_accepted_on_run_step() -> None:
    args = build_parser().parse_args(
        ["run-step", "qa-agent", "--skill", "fagan-review"]
    )

    assert args.command == "run-step"
    assert args.agent == "qa-agent"
    assert args.skill == "fagan-review"


def test_skill_flag_defaults_to_none() -> None:
    args = build_parser().parse_args(["run-step", "qa-agent"])

    assert args.skill is None


# ---------------------------------------------------------------------------
# Seam 2 (pre-launch validation): _validate_skill — BR-050, BR-052, VR-038
# ---------------------------------------------------------------------------


def test_validate_skill_accepts_declared_skill() -> None:
    info = _agent_info(["fagan-review", "security-review"])

    assert _validate_skill(info, "fagan-review") == "fagan-review"


def test_validate_skill_rejects_undeclared_skill_listing_declared_skills() -> None:
    info = _agent_info(["fagan-review", "security-review"])

    with pytest.raises(ValueError) as excinfo:
        _validate_skill(info, "bug-hunt")

    message = str(excinfo.value)
    assert "bug-hunt" in message
    assert "fagan-review" in message
    assert "security-review" in message


def test_validate_skill_omitted_selects_full_workflow() -> None:
    info = _agent_info(["fagan-review"])

    assert _validate_skill(info, None) is None


def test_validate_skill_all_skills_sentinel_selects_full_workflow() -> None:
    info = _agent_info(["fagan-review"])

    assert _validate_skill(info, "all skills") is None


def test_validate_skill_all_skills_sentinel_accepted_even_with_no_declared_skills() -> (
    None
):
    info = _agent_info([])

    assert _validate_skill(info, "all skills") is None


def test_validate_skill_rejects_any_named_skill_when_agent_declares_none() -> None:
    info = _agent_info([])

    with pytest.raises(ValueError) as excinfo:
        _validate_skill(info, "fagan-review")

    assert "fagan-review" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Seam 3: PromptComposer.compose — BR-051, BR-052
# ---------------------------------------------------------------------------


def test_compose_with_skill_appends_skill_scoped_call_to_action(tmp_path: Path) -> None:
    definition_path = tmp_path / "qa-agent.md"
    definition_path.write_text("# Agent\nFull QA workflow.\n", encoding="utf-8")
    info = _agent_info(["fagan-review"], definition_path)
    ctx = InvocationContext(phase="standalone", role=AgentRole.AUTHOR, iteration=0)

    prompt = FilePromptComposer().compose(info, [], ctx, skill="fagan-review")

    # BR-051: agent definition preserved verbatim, not rewritten.
    assert "# Agent\nFull QA workflow." in prompt
    assert 'Execute only the "fagan-review" skill' in prompt
    assert "Execute the workflow defined in your Agent Definition above." not in prompt


def test_compose_without_skill_preserves_full_workflow_prompt(tmp_path: Path) -> None:
    definition_path = tmp_path / "qa-agent.md"
    definition_path.write_text("# Agent\nFull QA workflow.\n", encoding="utf-8")
    info = _agent_info(["fagan-review"], definition_path)
    ctx = InvocationContext(phase="standalone", role=AgentRole.AUTHOR, iteration=0)

    with_none = FilePromptComposer().compose(info, [], ctx, skill=None)
    without_kwarg = FilePromptComposer().compose(info, [], ctx)

    assert with_none == without_kwarg
    assert "Execute the workflow defined in your Agent Definition above." in with_none


def test_compose_all_skills_sentinel_equals_full_workflow_prompt(
    tmp_path: Path,
) -> None:
    # _validate_skill normalizes "all skills" to None before compose() is
    # called — this test locks that equivalence at the composer seam too.
    definition_path = tmp_path / "qa-agent.md"
    definition_path.write_text("# Agent\nFull QA workflow.\n", encoding="utf-8")
    info = _agent_info(["fagan-review"], definition_path)
    ctx = InvocationContext(phase="standalone", role=AgentRole.AUTHOR, iteration=0)

    normalized = _validate_skill(info, "all skills")
    prompt = FilePromptComposer().compose(info, [], ctx, skill=normalized)
    baseline = FilePromptComposer().compose(info, [], ctx)

    assert prompt == baseline


def test_skill_scoped_call_to_action_names_the_skill() -> None:
    text = skill_scoped_call_to_action("fagan-review")

    assert "fagan-review" in text
    assert "only" in text.lower()


# ---------------------------------------------------------------------------
# End-to-end handler: undeclared skill rejected before any subprocess launch
# (FR-S2, VR-038)
# ---------------------------------------------------------------------------


class _NeverInvokedAdapter:
    interactive = False

    def invoke(self, *args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("adapter.invoke() must not be called (VR-038)")


def _write_agent_def(agents_dir: Path, name: str, skills: list[str]) -> None:
    agents_dir.mkdir(parents=True, exist_ok=True)
    skill_lines = "\n".join(f"  - {s}" for s in skills)
    (agents_dir / f"{name}.md").write_text(
        "---\n"
        f"skills:\n{skill_lines}\n"
        "outputs:\n  - docs/findings/*.md\n"
        "---\n"
        "# Agent\nFull QA workflow.\n",
        encoding="utf-8",
    )


def test_handle_run_step_rejects_undeclared_skill_before_any_subprocess(
    tmp_path: Path,
) -> None:
    agents_dir = tmp_path / "agents"
    _write_agent_def(agents_dir, "qa-agent", ["fagan-review", "security-review"])

    runtime = SimpleNamespace(
        agents_dir=agents_dir,
        repo_root=tmp_path,
        prompt_composer=FilePromptComposer(),
        adapter=_NeverInvokedAdapter(),
        logger=SimpleNamespace(log=lambda *a, **k: None),
    )

    with pytest.raises(ValueError) as excinfo:
        _handle_run_step(runtime, "qa-agent", 30, skill="bug-hunt")

    message = str(excinfo.value)
    assert "bug-hunt" in message
    assert "fagan-review" in message
    assert "security-review" in message


def test_load_step_agent_parses_declared_skills(tmp_path: Path) -> None:
    agents_dir = tmp_path / "agents"
    _write_agent_def(agents_dir, "qa-agent", ["fagan-review", "security-review"])

    info = _load_step_agent(agents_dir, "qa-agent")

    assert info.skills == ["fagan-review", "security-review"]
