"""Agent readiness — derives per-agent readiness from evaluator evidence.

Accepts evaluator output and produces readiness verdicts.
No cycle or route vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentReadiness:
    agent_name: str
    eligible: bool
    unsatisfied: tuple = ()
    warnings: tuple[str, ...] = ()


def derive_readiness(evaluation_results: list[dict]) -> list[AgentReadiness]:
    results = []
    for ev in evaluation_results:
        unsatisfied = tuple(
            r for r in ev.get("requirements", []) if not r.get("satisfied")
        )
        results.append(AgentReadiness(
            agent_name=ev["agent_name"],
            eligible=ev.get("eligible", False),
            unsatisfied=unsatisfied,
            warnings=tuple(ev.get("warnings", [])),
        ))
    return results
