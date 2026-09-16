"""Contract tests for agent eligibility resolution.

Owned contracts:
  - Agent with matching cycle is eligible (standard risk)
  - Agent without matching cycle is excluded (standard risk)
  - Agent with multiple eligible cycles matches each (standard risk)
  - Empty eligible_cycles matches nothing (standard risk)
"""

from __future__ import annotations

import sys
from pathlib import Path

PACKAGES_DIR = Path(__file__).resolve().parents[2] / "packages" / "factory"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.eligibility import resolve_eligible


def _agent(name: str, cycles: list[str]) -> dict:
    return {"name": name, "eligible_cycles": cycles}


class TestResolveEligible:
    def test_matching_cycle_is_eligible(self):
        agents = [_agent("dev", ["REALIZE"])]
        result = resolve_eligible("REALIZE", agents)
        assert len(result) == 1
        assert result[0]["name"] == "dev"

    def test_non_matching_cycle_excluded(self):
        agents = [_agent("dev", ["REALIZE"])]
        result = resolve_eligible("IDEA", agents)
        assert result == []

    def test_multiple_eligible_cycles(self):
        agents = [_agent("recon", ["REFINE", "REALIZE"])]
        assert len(resolve_eligible("REFINE", agents)) == 1
        assert len(resolve_eligible("REALIZE", agents)) == 1
        assert len(resolve_eligible("IDEA", agents)) == 0

    def test_empty_eligible_cycles_matches_nothing(self):
        agents = [_agent("virgil", [])]
        for cycle in ["IDEA", "CONCEPT", "ROADMAP", "REFINE", "REALIZE", "DONE"]:
            assert resolve_eligible(cycle, agents) == []

    def test_multiple_agents_filtered(self):
        agents = [
            _agent("req", ["IDEA", "CONCEPT"]),
            _agent("arch", ["CONCEPT"]),
            _agent("plan", ["ROADMAP"]),
        ]
        result = resolve_eligible("CONCEPT", agents)
        names = [a["name"] for a in result]
        assert "req" in names
        assert "arch" in names
        assert "plan" not in names

    def test_missing_eligible_cycles_key_excluded(self):
        agents = [{"name": "legacy"}]
        result = resolve_eligible("IDEA", agents)
        assert result == []

    def test_preserves_agent_data(self):
        agent = {"name": "dev", "eligible_cycles": ["REALIZE"], "path": "agents/dev.md"}
        result = resolve_eligible("REALIZE", [agent])
        assert result[0]["path"] == "agents/dev.md"
