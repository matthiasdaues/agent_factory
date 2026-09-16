"""Pure eligibility resolution — no I/O, no subprocess.

Given the current cycle and a list of agent records (each carrying an
``eligible_cycles`` list), returns those agents eligible for the cycle.
"""

from __future__ import annotations


def resolve_eligible(current_cycle: str, agents: list[dict]) -> list[dict]:
    return [
        a for a in agents
        if current_cycle in a.get("eligible_cycles", ())
    ]
