"""Tests for the classification-driven model resolution axis (ST-0059, ADR-0018 sec 2).

Covers ``ModelResolver.resolve_story_classification`` — the dispatcher's
classification -> tier -> model path for tier-less developer sub-agents.
Structurally distinct from the agent-tier axis (ST-0049's
``resolve_agent_tier``, not yet landed in this worktree — see ST-0059's
Analysis section for the stale-base note): the two axes never combine.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from orchestrator.entities import ModelDictionary
from orchestrator.model_resolver import ModelResolver

# orchestrator/tests/test_classification_resolution.py -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
DEVELOPER_AGENT_PATH = REPO_ROOT / "agents" / "developer-agent.md"


class PoisonedModelMatrix:
    """A ModelMatrix stub that fails the test if the classification axis ever
    reads it. Stands in for the agent-tier / ADR-0009 axis's state."""

    def get_tier(self, key: str):
        raise AssertionError(
            "resolve_story_classification must never read the agent-tier matrix"
        )

    def get_model(self, cli: str, tier: str):
        raise AssertionError(
            "resolve_story_classification must never read the agent-tier matrix"
        )

    def get_on_missing(self):
        raise AssertionError(
            "resolve_story_classification must never read the agent-tier matrix"
        )


def _read_frontmatter_lines(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0].strip() == "---", f"no frontmatter opener in {path}"
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    raise AssertionError(f"no frontmatter closer in {path}")


@pytest.mark.parametrize(
    "classification,tier,model_id",
    [
        ("trivial", "economy", "gpt-5.4-mini"),
        ("standard", "standard", "gpt-5.4"),
        ("hard", "strong", "claude-opus-4-6"),
    ],
)
def test_classification_band_resolves_through_tier_to_model(
    classification, tier, model_id
):
    dictionary = ModelDictionary()
    dictionary.set_model(tier, model_id)

    resolved = ModelResolver.resolve_story_classification(classification, dictionary)

    assert resolved == model_id


def test_unmapped_tier_returns_none():
    dictionary = ModelDictionary()  # no entries set

    resolved = ModelResolver.resolve_story_classification("hard", dictionary)

    assert resolved is None


def test_unknown_classification_raises_value_error():
    dictionary = ModelDictionary()
    dictionary.set_model("strong", "claude-opus-4-6")

    with pytest.raises(ValueError):
        ModelResolver.resolve_story_classification("epic", dictionary)


def test_resolve_story_classification_signature_has_no_tier_parameter():
    """Structural enforcement (ADR-0018 sec 2): the classification axis must be
    incapable of accepting an agent tier. No parameter may be named/shaped like
    one; mirrors the intent of ST-0049's (not-yet-landed) precedent test."""
    sig = inspect.signature(ModelResolver.resolve_story_classification)
    param_names = list(sig.parameters)

    assert param_names == ["classification", "dictionary"]
    assert all("tier" not in name.lower() for name in param_names)


def test_resolve_story_classification_never_touches_agent_tier_axis_state():
    """Even a ModelResolver instance wired to a matrix that raises on any read
    resolves classification correctly — proving the two axes are structurally
    independent at runtime, not merely untested together."""
    resolver = ModelResolver(PoisonedModelMatrix(), "copilot")
    dictionary = ModelDictionary()
    dictionary.set_model("standard", "gpt-5.4")

    # Callable via an instance too (staticmethod), but touches no instance state.
    resolved = resolver.resolve_story_classification("standard", dictionary)

    assert resolved == "gpt-5.4"


def test_developer_agent_definition_declares_no_tier():
    """Developer sub-agents are tier-less by design (ADR-0018 sec 2); the
    dispatcher never reads a developer-agent tier because none exists."""
    frontmatter = _read_frontmatter_lines(DEVELOPER_AGENT_PATH)

    assert not any(line.strip().startswith("tier:") for line in frontmatter)
