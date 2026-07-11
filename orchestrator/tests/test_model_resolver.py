"""Tests for ModelResolver.resolve_tier (ADR-0020, ADR-0021).

One axis, one method: every caller already carries the tier value itself
(an agent's own frontmatter, or — post-ADR-0020 — a story's own `tier`
field), so resolution is just a model.conf lookup. No classification
translation, no adapter-registry dependency.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Optional

import pytest

from orchestrator.model_resolver import ConfigError, ModelResolver

REPO_ROOT = Path(__file__).resolve().parents[2]
DEVELOPER_AGENT_PATH = REPO_ROOT / "factory" / "agents" / "developer-agent.md"


class StubModelMatrix:
    def __init__(
        self,
        models: Optional[dict[tuple[str, str], str]] = None,
        on_missing: str = "halt",
    ):
        self.models = models or {}
        self.on_missing = on_missing

    def get_model(self, cli: str, tier: str) -> Optional[str]:
        return self.models.get((cli, tier))

    def get_on_missing(self) -> str:
        return self.on_missing


def test_explicit_model_always_wins():
    matrix = StubModelMatrix(models={("copilot", "strong"): "claude-opus-4-6"})

    resolved = ModelResolver(matrix, "copilot").resolve_tier(
        "strong", explicit_model="gpt-5.4-manual"
    )

    assert resolved == "gpt-5.4-manual"


def test_tier_resolves_through_matrix_to_model():
    matrix = StubModelMatrix(models={("copilot", "standard"): "gpt-5.4"})

    resolved = ModelResolver(matrix, "copilot").resolve_tier("standard")

    assert resolved == "gpt-5.4"


def test_each_call_resolves_independently():
    matrix = StubModelMatrix(
        models={
            ("copilot", "economy"): "gpt-5.4-mini",
            ("copilot", "strong"): "claude-opus-4-6",
        }
    )
    resolver = ModelResolver(matrix, "copilot")

    author_model = resolver.resolve_tier("economy")
    reviewer_model = resolver.resolve_tier("strong")

    assert author_model == "gpt-5.4-mini"
    assert reviewer_model == "claude-opus-4-6"


def test_null_tier_defaults_to_standard():
    matrix = StubModelMatrix(models={("copilot", "standard"): "gpt-5.4"})

    resolved = ModelResolver(matrix, "copilot").resolve_tier(None)

    assert resolved == "gpt-5.4"


def test_on_missing_halt_raises_config_error_on_unresolvable_tier():
    matrix = StubModelMatrix(models={}, on_missing="halt")

    with pytest.raises(ConfigError):
        ModelResolver(matrix, "copilot").resolve_tier("strong")


def test_on_missing_auto_returns_none_on_unresolvable_tier():
    matrix = StubModelMatrix(models={}, on_missing="auto")

    resolved = ModelResolver(matrix, "copilot").resolve_tier("strong")

    assert resolved is None


def test_constructor_on_missing_override_wins_over_matrix():
    matrix = StubModelMatrix(models={}, on_missing="halt")

    resolved = ModelResolver(matrix, "copilot", on_missing_tier="auto").resolve_tier(
        "strong"
    )

    assert resolved is None


def test_resolve_tier_has_no_classification_parameter():
    """Structural guard (ADR-0020): the story-classification axis is gone —
    a story's own `tier` is the only value this method ever takes."""
    params = inspect.signature(ModelResolver.resolve_tier).parameters
    assert "classification" not in params
    assert list(params) == ["self", "tier", "explicit_model"]


def _read_frontmatter_lines(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0].strip() == "---", f"no frontmatter opener in {path}"
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    raise AssertionError(f"no frontmatter closer in {path}")


def test_developer_agent_definition_declares_no_tier():
    """Developer sub-agents are tier-less by design (ADR-0018 sec 2, ADR-0020):
    the dispatcher resolves their model from the story's own `tier`, never
    from the agent's frontmatter, because none exists."""
    frontmatter = _read_frontmatter_lines(DEVELOPER_AGENT_PATH)

    assert not any(line.strip().startswith("tier:") for line in frontmatter)
