"""Contract tests for agent readiness derivation.

Owned contracts:
  - Eligible agent has empty unsatisfied list (standard risk)
  - Ineligible agent lists unsatisfied requirements (standard risk)
  - Warnings propagated from evaluator evidence (standard risk)
"""

from __future__ import annotations

import sys
from pathlib import Path

PACKAGES_DIR = Path(__file__).resolve().parents[2] / "packages" / "factory"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.readiness import AgentReadiness, derive_readiness


class TestDeriveReadiness:
    def test_eligible_agent(self):
        results = derive_readiness([{
            "agent_name": "coach",
            "eligible": True,
            "requirements": [],
            "warnings": [],
        }])
        assert len(results) == 1
        assert results[0].eligible is True
        assert results[0].unsatisfied == ()

    def test_ineligible_agent(self):
        results = derive_readiness([{
            "agent_name": "arch",
            "eligible": False,
            "requirements": [
                {"type": "proposal", "satisfied": False, "candidates": []},
            ],
            "warnings": [],
        }])
        assert len(results) == 1
        assert results[0].eligible is False
        assert len(results[0].unsatisfied) == 1

    def test_warnings_propagated(self):
        results = derive_readiness([{
            "agent_name": "test",
            "eligible": False,
            "requirements": [],
            "warnings": ["validator not found"],
        }])
        assert "validator not found" in results[0].warnings

    def test_multiple_agents(self):
        results = derive_readiness([
            {"agent_name": "a", "eligible": True, "requirements": [], "warnings": []},
            {"agent_name": "b", "eligible": False, "requirements": [
                {"type": "x", "satisfied": False},
            ], "warnings": []},
        ])
        assert len(results) == 2
        assert results[0].eligible is True
        assert results[1].eligible is False


class TestReadinessShape:
    def test_has_required_fields(self):
        results = derive_readiness([{
            "agent_name": "test",
            "eligible": True,
            "requirements": [],
            "warnings": [],
        }])
        r = results[0]
        assert isinstance(r, AgentReadiness)
        assert isinstance(r.agent_name, str)
        assert isinstance(r.eligible, bool)
        assert isinstance(r.unsatisfied, tuple)
        assert isinstance(r.warnings, tuple)
