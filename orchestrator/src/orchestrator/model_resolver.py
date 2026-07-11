from __future__ import annotations

from typing import Optional

from orchestrator.entities import Tier
from orchestrator.ports import ModelMatrix


class ConfigError(Exception):
    """Raised when model resolution cannot satisfy configured policy."""


class ModelResolver:
    """Resolves a tier to a concrete model by reading model.conf directly
    (ADR-0020, ADR-0021). One method, one axis: every caller — a phase
    agent's own declared `tier`, or (post-ADR-0020) a story's own declared
    `tier` — already carries the tier value itself. There is nothing left
    to pivot through."""

    def __init__(
        self,
        matrix: ModelMatrix,
        cli: str,
        on_missing_tier: Optional[str] = None,
    ):
        self._matrix = matrix
        self._cli = cli
        self._on_missing_tier = on_missing_tier

    def resolve_tier(
        self,
        tier: Optional[str],
        explicit_model: Optional[str] = None,
    ) -> Optional[str]:
        """Resolve a model for the given tier, through model.conf's `[facts]`
        (ADR-0020, ADR-0021, FR-R10, FR-R11, FR-R12).

        Args:
            tier: The declared tier — an agent's `AgentInfo.tier`, or a
                story's own `tier` field. `None` resolves as `standard`
                (VR-041).
            explicit_model: An operator-supplied `--model` override. When
                given, it wins outright and no tier lookup happens.

        Returns:
            The resolved model_id, or None if no tier could be resolved and
            adapter-default fallback is enabled (on_missing="auto") — the
            caller omits `--model` and the adapter runs its own default.

        Raises:
            ConfigError: If model.conf has no model for the required tier
                and on_missing is "halt" (the default, FR-K4/BR-020).
        """
        if explicit_model is not None:
            return explicit_model

        effective_tier = tier if tier is not None else Tier.STANDARD.value

        model = self._matrix.get_model(self._cli, effective_tier)
        if model is not None:
            return model

        on_missing = self._on_missing_tier or self._matrix.get_on_missing()
        if on_missing == "halt":
            raise ConfigError(
                f"no model configured for cli={self._cli!r} and "
                f"tier={effective_tier!r} (FR-K4, BR-020)"
            )

        return None
