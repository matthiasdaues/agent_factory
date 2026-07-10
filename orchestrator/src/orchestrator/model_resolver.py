from __future__ import annotations

from typing import Optional

from orchestrator.entities import ModelDictionary, Tier
from orchestrator.ports import AdapterRegistry, ModelMatrix


class ConfigError(Exception):
    """Raised when model resolution cannot satisfy configured policy."""


# Story classification -> tier, per ADR-0018 sec 2 / BR-021. This is the ONLY
# table this axis reads; it never reads an agent's `tier` frontmatter value.
_CLASSIFICATION_TIER: dict[str, str] = {
    "trivial": "economy",
    "standard": "standard",
    "hard": "strong",
}


class ModelResolver:
    def __init__(
        self,
        matrix: ModelMatrix,
        cli: str,
        adapter_registry: Optional[AdapterRegistry] = None,
        on_missing_tier: str = "halt",
    ):
        self._matrix = matrix
        self._cli = cli
        self._adapter_registry = adapter_registry
        self._on_missing_tier = on_missing_tier

    def resolve_agent_tier(
        self,
        tier: Optional[str],
        explicit_model: Optional[str] = None,
    ) -> Optional[str]:
        """Resolve a model for an orchestrator-invoked agent from its declared
        tier, through the active adapter's model dictionary (ADR-0018, FR-R10,
        FR-R11, FR-R12).

        Deliberately takes no story-classification parameter: that axis is
        ST-0059's separate, lower-level concern for the implementation
        dispatcher's tier-less developer sub-agents, and the two axes never
        combine on one invocation (ADR-0018).

        For `run-step`, call this once for the named agent. For `run-phase`,
        call this once per orchestrator-invoked agent (author, then reviewer);
        each call resolves independently from that agent's own declared tier.

        Args:
            tier: The agent's declared AgentInfo.tier, or None if the agent
                declares no tier — a null tier resolves as `standard`
                (VR-041).
            explicit_model: An operator-supplied `--model` override. When
                given, it wins outright and no tier lookup happens.

        Returns:
            The resolved model_id, or None if no tier could be resolved and
            adapter-default fallback is enabled (on_missing_tier="auto") —
            the caller omits `--model` and the adapter runs its own default.

        Raises:
            ConfigError: If no AdapterRegistry was configured, or if the
                adapter's dictionary has no model for the required tier and
                on_missing_tier is "halt" (the default, per FR-K4/BR-020).
        """
        if explicit_model is not None:
            return explicit_model

        if self._adapter_registry is None:
            raise ConfigError(
                "ModelResolver has no adapter_registry configured; "
                "agent-tier resolution requires one (ADR-0018)."
            )

        effective_tier = tier if tier is not None else Tier.STANDARD.value

        model = self._adapter_registry.get_model(self._cli, effective_tier)
        if model is not None:
            return model

        if self._on_missing_tier == "halt":
            raise ConfigError(
                f"no model configured for cli={self._cli!r} and "
                f"tier={effective_tier!r} (FR-K4, BR-020)"
            )

        return None

    @staticmethod
    def resolve_story_classification(
        classification: str,
        dictionary: ModelDictionary,
    ) -> Optional[str]:
        """Resolve a story's classification to a concrete model (ADR-0018 sec 2).

        This is the SECOND, separate resolution axis: story `classification`
        (trivial/standard/hard, BR-021) -> tier -> concrete model, for the
        tier-less developer sub-agents the `implementation-agent` dispatcher
        spawns. It happens below the adapter boundary (FR-M) — the orchestrator
        never calls this directly; only the dispatcher does, once per story it
        commissions. `run-step`/`run-phase` never call it.

        Deliberately a `@staticmethod`: it reads neither `self._matrix` nor
        `self._cli` (the ADR-0009/agent-tier axis's instance state), so it is
        structurally incapable of combining the two axes on one call — not
        just by convention, but because it has no access to that state.
        The signature also has no `tier` parameter: the ONLY tier this method
        can ever consult is the one it derives from `classification` via
        `_CLASSIFICATION_TIER`, above.

        Args:
            classification: One of {trivial, standard, hard} (Classification enum).
            dictionary: The active adapter's ModelDictionary (same lookup
                mechanism `resolve_agent_tier` reads, keyed by classification
                instead of an agent's declared tier).

        Returns:
            The concrete model_id, or None if the tier is unmapped in
            `dictionary`.

        Raises:
            ValueError: If `classification` is not one of {trivial, standard, hard}.
        """
        try:
            tier = _CLASSIFICATION_TIER[classification]
        except KeyError as exc:
            raise ValueError(
                f"unknown story classification: {classification!r}; "
                f"must be one of {sorted(_CLASSIFICATION_TIER)}"
            ) from exc

        return dictionary.get_model(tier)

    def resolve(
        self,
        phase: str,
        classification: Optional[str] = None,
        explicit_model: Optional[str] = None,
    ) -> Optional[str]:
        if explicit_model is not None:
            return explicit_model

        tier: Optional[str] = None
        if classification is not None:
            tier = self._matrix.get_tier(f"class.{classification}")
        else:
            tier = self._matrix.get_tier(f"phase.{phase}")
            if tier == "by-class":
                tier = None

        if tier is None:
            return None

        model = self._matrix.get_model(self._cli, tier)
        if model is not None:
            return model

        if self._matrix.get_on_missing() == "halt":
            raise ConfigError(
                f"no model configured for cli={self._cli!r} and tier={tier!r}"
            )

        return None
