"""Contract tests for evaluation summary.

Owned contracts:
  - Eligible agents separated from blocked agents (standard risk)
  - All warnings collected (standard risk)
  - Empty input returns empty summary (standard risk)
"""

from __future__ import annotations

import sys
from pathlib import Path

PACKAGES_DIR = Path(__file__).resolve().parents[2] / "packages" / "factory"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.readiness import AgentReadiness
from engine.recommendations import EvaluationSummary, summarize


class TestSummarize:
    def test_eligible_separated(self):
        verdicts = [
            AgentReadiness("a", eligible=True),
            AgentReadiness("b", eligible=False, unsatisfied=({"type": "x"},)),
        ]
        result = summarize(verdicts)
        assert len(result.eligible_agents) == 1
        assert len(result.blocked_agents) == 1
        assert result.eligible_agents[0].agent_name == "a"
        assert result.blocked_agents[0].agent_name == "b"

    def test_all_eligible(self):
        verdicts = [
            AgentReadiness("a", eligible=True),
            AgentReadiness("b", eligible=True),
        ]
        result = summarize(verdicts)
        assert len(result.eligible_agents) == 2
        assert len(result.blocked_agents) == 0

    def test_all_blocked(self):
        verdicts = [
            AgentReadiness("a", eligible=False),
            AgentReadiness("b", eligible=False),
        ]
        result = summarize(verdicts)
        assert len(result.eligible_agents) == 0
        assert len(result.blocked_agents) == 2

    def test_warnings_collected(self):
        verdicts = [
            AgentReadiness("a", eligible=True, warnings=("w1",)),
            AgentReadiness("b", eligible=False, warnings=("w2",)),
        ]
        result = summarize(verdicts)
        assert "w1" in result.warnings
        assert "w2" in result.warnings

    def test_empty_input(self):
        result = summarize([])
        assert isinstance(result, EvaluationSummary)
        assert result.eligible_agents == ()
        assert result.blocked_agents == ()
        assert result.warnings == ()
