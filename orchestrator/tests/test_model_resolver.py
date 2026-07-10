from __future__ import annotations

from typing import Optional

import pytest

from orchestrator.model_resolver import ConfigError, ModelResolver


class StubModelMatrix:
    def __init__(
        self,
        tiers: Optional[dict[str, str]] = None,
        models: Optional[dict[tuple[str, str], str]] = None,
        on_missing: str = "halt",
    ):
        self.tiers = tiers or {}
        self.models = models or {}
        self.on_missing = on_missing

    def get_tier(self, key: str) -> Optional[str]:
        return self.tiers.get(key)

    def get_model(self, cli: str, tier: str) -> Optional[str]:
        return self.models.get((cli, tier))

    def get_on_missing(self) -> str:
        return self.on_missing


def test_explicit_model_always_wins():
    matrix = StubModelMatrix(
        tiers={"class.hard": "strong"},
        models={("copilot", "strong"): "claude-opus-4-6"},
    )

    resolved = ModelResolver(matrix, "copilot").resolve(
        phase="implementation",
        classification="hard",
        explicit_model="gpt-5.4-manual",
    )

    assert resolved == "gpt-5.4-manual"


def test_classification_to_tier_to_model_resolves():
    matrix = StubModelMatrix(
        tiers={"class.standard": "standard"},
        models={("copilot", "standard"): "gpt-5.4"},
    )

    resolved = ModelResolver(matrix, "copilot").resolve(
        phase="implementation",
        classification="standard",
    )

    assert resolved == "gpt-5.4"


def test_phase_to_tier_to_model_resolves_for_non_task_phase():
    matrix = StubModelMatrix(
        tiers={"phase.planning": "strong"},
        models={("copilot", "strong"): "claude-opus-4-6"},
    )

    resolved = ModelResolver(matrix, "copilot").resolve(phase="planning")

    assert resolved == "claude-opus-4-6"


def test_by_class_with_classification_uses_classification_tier():
    matrix = StubModelMatrix(
        tiers={
            "phase.implementation": "by-class",
            "class.trivial": "economy",
        },
        models={("copilot", "economy"): "gpt-5.4-mini"},
    )

    resolved = ModelResolver(matrix, "copilot").resolve(
        phase="implementation",
        classification="trivial",
    )

    assert resolved == "gpt-5.4-mini"


def test_by_class_without_classification_returns_none():
    matrix = StubModelMatrix(tiers={"phase.implementation": "by-class"})

    resolved = ModelResolver(matrix, "copilot").resolve(phase="implementation")

    assert resolved is None


def test_on_missing_halt_raises_config_error_on_unresolvable_tier():
    matrix = StubModelMatrix(
        tiers={"class.hard": "strong"},
        models={},
        on_missing="halt",
    )

    with pytest.raises(ConfigError):
        ModelResolver(matrix, "copilot").resolve(
            phase="implementation",
            classification="hard",
        )


def test_on_missing_auto_returns_none_on_unresolvable_tier():
    matrix = StubModelMatrix(
        tiers={"class.hard": "strong"},
        models={},
        on_missing="auto",
    )

    resolved = ModelResolver(matrix, "copilot").resolve(
        phase="implementation",
        classification="hard",
    )

    assert resolved is None


def test_no_tier_found_returns_none():
    matrix = StubModelMatrix()

    resolved = ModelResolver(matrix, "copilot").resolve(phase="requirements")

    assert resolved is None


# --- resolve_agent_tier() — ADR-0018 agent-tier axis (ST-0049) --------------
#
# Separate mechanism from resolve() above: reads only the adapter's
# ModelDictionary (via an AdapterRegistry), never the ModelMatrix, and never
# accepts a story classification (that axis belongs to ST-0059's dispatcher,
# one level down, and is out of scope for this resolver method).


class StubAdapterRegistry:
    """In-memory fake of the AdapterRegistry port (ports.py) for unit tests.

    Only implements get_model(), the sole method resolve_agent_tier() calls.
    """

    def __init__(self, models: Optional[dict[tuple[str, str], str]] = None):
        self.models = models or {}

    def get_model(self, adapter: str, tier: str) -> Optional[str]:
        return self.models.get((adapter, tier))


def test_run_step_resolves_agent_tier_through_adapter_dictionary():
    registry = StubAdapterRegistry(models={("copilot", "strong"): "claude-opus-4-6"})

    resolved = ModelResolver(
        StubModelMatrix(), "copilot", adapter_registry=registry
    ).resolve_agent_tier(tier="strong")

    assert resolved == "claude-opus-4-6"


def test_explicit_model_override_bypasses_agent_tier_resolution():
    registry = StubAdapterRegistry(models={("copilot", "strong"): "claude-opus-4-6"})

    resolved = ModelResolver(
        StubModelMatrix(), "copilot", adapter_registry=registry
    ).resolve_agent_tier(tier="strong", explicit_model="gpt-5.4-manual")

    assert resolved == "gpt-5.4-manual"


def test_run_phase_resolves_each_agent_independently_from_its_own_tier():
    registry = StubAdapterRegistry(
        models={
            ("copilot", "economy"): "gpt-5.4-mini",
            ("copilot", "strong"): "claude-opus-4-6",
        }
    )
    resolver = ModelResolver(StubModelMatrix(), "copilot", adapter_registry=registry)

    author_model = resolver.resolve_agent_tier(tier="economy")
    reviewer_model = resolver.resolve_agent_tier(tier="strong")

    assert author_model == "gpt-5.4-mini"
    assert reviewer_model == "claude-opus-4-6"


def test_null_tier_defaults_to_standard():
    registry = StubAdapterRegistry(models={("copilot", "standard"): "gpt-5.4"})

    resolved = ModelResolver(
        StubModelMatrix(), "copilot", adapter_registry=registry
    ).resolve_agent_tier(tier=None)

    assert resolved == "gpt-5.4"


def test_missing_required_tier_halts_by_default():
    registry = StubAdapterRegistry(models={})

    with pytest.raises(ConfigError):
        ModelResolver(
            StubModelMatrix(), "copilot", adapter_registry=registry
        ).resolve_agent_tier(tier="strong")


def test_missing_required_tier_returns_none_when_adapter_default_fallback_enabled():
    registry = StubAdapterRegistry(models={})

    resolved = ModelResolver(
        StubModelMatrix(),
        "copilot",
        adapter_registry=registry,
        on_missing_tier="auto",
    ).resolve_agent_tier(tier="strong")

    assert resolved is None


def test_resolve_agent_tier_has_no_classification_parameter():
    """Structural guard for ADR-0018: this method must never accept a story
    classification — that axis belongs to ST-0059's dispatcher, a separate,
    lower-level concern that must never combine with the agent-tier axis.
    """
    import inspect

    params = inspect.signature(ModelResolver.resolve_agent_tier).parameters
    assert "classification" not in params


def test_resolve_agent_tier_without_adapter_registry_raises_config_error():
    with pytest.raises(ConfigError):
        ModelResolver(StubModelMatrix(), "copilot").resolve_agent_tier(tier="strong")
