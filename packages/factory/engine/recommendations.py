"""Route Recommender — applies the supported-route cardinality table.

Pure domain logic. Receives readiness verdicts, returns one of three
result types. Never ranks and never selects between choices.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from engine.cycle_model import REQUIRED_CYCLES
from engine.readiness import RouteReadiness

ACTIVE_CYCLES = REQUIRED_CYCLES - {"DONE"}


@dataclass(frozen=True)
class NoRecommendation:
    """Zero routes have supporting evidence."""
    kind: str = "none"
    warnings: tuple[str, ...] = ()
    available_cycles: tuple[str, ...] = ()


@dataclass(frozen=True)
class SingleRecommendation:
    """Exactly one route has supporting evidence."""
    kind: str = "single"
    recommended_cycle: str = ""
    from_cycle: str = ""
    evidence: tuple[Any, ...] = ()
    available_cycles: tuple[str, ...] = ()


@dataclass(frozen=True)
class MultipleChoices:
    """More than one route has supporting evidence. Unranked."""
    kind: str = "multiple"
    choices: tuple[RouteReadiness, ...] = ()
    available_cycles: tuple[str, ...] = ()


RecommendationResult = NoRecommendation | SingleRecommendation | MultipleChoices


def recommend(
    current_cycle: str,
    readiness_verdicts: list[RouteReadiness],
) -> RecommendationResult:
    supported = [v for v in readiness_verdicts if v.supported]
    all_warnings = []
    for v in readiness_verdicts:
        all_warnings.extend(v.warnings)

    other_cycles = tuple(sorted(ACTIVE_CYCLES - {current_cycle}))

    if len(supported) == 0:
        return NoRecommendation(
            warnings=tuple(all_warnings),
            available_cycles=other_cycles,
        )

    if len(supported) == 1:
        route = supported[0]
        return SingleRecommendation(
            recommended_cycle=route.to_cycle,
            from_cycle=route.from_cycle,
            evidence=route.evidence,
            available_cycles=tuple(c for c in other_cycles if c != route.to_cycle),
        )

    return MultipleChoices(
        choices=tuple(supported),
        available_cycles=tuple(c for c in other_cycles
                               if c not in {s.to_cycle for s in supported}),
    )
