"""Evaluation summary — classifies agents by eligibility.

Accepts readiness verdicts, returns which agents are eligible
(all inputs satisfied) and which have unsatisfied inputs.
No cycle or route vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.readiness import AgentReadiness


@dataclass(frozen=True)
class EvaluationSummary:
    eligible_agents: tuple[AgentReadiness, ...] = ()
    blocked_agents: tuple[AgentReadiness, ...] = ()
    warnings: tuple[str, ...] = ()


def summarize(readiness_verdicts: list[AgentReadiness]) -> EvaluationSummary:
    eligible = []
    blocked = []
    all_warnings: list[str] = []

    for v in readiness_verdicts:
        if v.eligible:
            eligible.append(v)
        else:
            blocked.append(v)
        all_warnings.extend(v.warnings)

    return EvaluationSummary(
        eligible_agents=tuple(eligible),
        blocked_agents=tuple(blocked),
        warnings=tuple(all_warnings),
    )
