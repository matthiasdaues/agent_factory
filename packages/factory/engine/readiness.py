"""Readiness Evaluator — determines whether artifact evidence supports a route.

Pure domain logic. Receives validator results and the delivery model.
Returns a readiness verdict per route from the current cycle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RouteReadiness:
    from_cycle: str
    to_cycle: str
    recommend_if: str
    supported: bool
    evidence: tuple[Any, ...]
    warnings: tuple[str, ...] = ()


def evaluate_readiness(
    current_cycle: str,
    routes: list,
    mechanical_results: dict[str, Any],
    semantic_results: dict[str, Any] | None = None,
    code_changed: bool = False,
) -> list[RouteReadiness]:
    """Evaluate readiness for each route leaving the current cycle.

    Each route declares which validators it requires. The evaluator
    checks only those validators, consulting mechanical results always
    and semantic results only when code_changed is True.

    Args:
        current_cycle: The workstream's current cycle name.
        routes: List of Route objects from the delivery model.
        mechanical_results: Validators that always run (file existence,
            format lint, required fields).
        semantic_results: Validators that compare artifacts against each
            other or against code. Only consulted when code_changed is True.
        code_changed: Whether the current cycle changed source code or
            a canonical artifact.

    Returns:
        A RouteReadiness per outgoing route from current_cycle.
    """
    if semantic_results is None:
        semantic_results = {}

    outgoing = [r for r in routes if r.from_cycle == current_cycle]
    results = []

    for route in outgoing:
        evidence = []
        warnings = []
        all_passing = True
        considered = 0

        for vname in route.validators:
            if vname in mechanical_results:
                vresult = mechanical_results[vname]
                evidence.append(vresult)
                considered += 1
                if not vresult.passed:
                    all_passing = False
                    warnings.extend(vresult.warnings)
            elif code_changed and vname in semantic_results:
                vresult = semantic_results[vname]
                evidence.append(vresult)
                considered += 1
                if not vresult.passed:
                    all_passing = False
                    warnings.extend(vresult.warnings)

        results.append(RouteReadiness(
            from_cycle=route.from_cycle,
            to_cycle=route.to_cycle,
            recommend_if=route.recommend_if,
            supported=all_passing and considered > 0,
            evidence=tuple(evidence),
            warnings=tuple(warnings),
        ))

    return results
