"""Contract tests for agent eligibility (precondition evaluator API).

Owned contracts:
  - Agent with no required inputs is eligible (standard risk)
  - Agent with satisfied inputs is eligible (standard risk)
  - Agent with unsatisfied inputs is not eligible (standard risk)
  - Evidence includes per-requirement detail (standard risk)
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

PACKAGES_DIR = Path(__file__).resolve().parents[2] / "packages" / "factory"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.eligibility import evaluate_agent, evaluate_all


def _write_frontmatter(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
    path.write_text(f"---\n{fm}---\n\n# Content\n")


class TestEvaluateAgent:
    def test_no_required_always_eligible(self):
        result = evaluate_agent({"name": "coach", "inputs": {"required": []}})
        assert result["eligible"] is True

    def test_satisfied_requirement(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "proposals").mkdir(parents=True)
        _write_frontmatter(
            tmp_path / "docs" / "proposals" / "x.md", {"status": "accepted"}
        )

        agent = {
            "name": "arch",
            "inputs": {
                "required": [
                    {
                        "type": "proposal",
                        "path_pattern": "docs/proposals/{name}.md",
                        "conditions": {"field": "status", "value": "accepted"},
                    }
                ]
            },
        }
        result = evaluate_agent(agent)
        assert result["eligible"] is True
        assert result["requirements"][0]["satisfied"] is True

    def test_unsatisfied_requirement(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agent = {
            "name": "arch",
            "inputs": {
                "required": [
                    {
                        "type": "proposal",
                        "path_pattern": "docs/proposals/{name}.md",
                    }
                ]
            },
        }
        result = evaluate_agent(agent)
        assert result["eligible"] is False
        assert result["requirements"][0]["satisfied"] is False

    def test_preserves_agent_name(self):
        result = evaluate_agent({"name": "dev", "inputs": {}})
        assert result["agent_name"] == "dev"


class TestEvaluateAll:
    def test_returns_results_for_all(self):
        agents = [
            {"name": "a", "inputs": {}},
            {"name": "b", "inputs": {}},
        ]
        results = evaluate_all(agents)
        assert len(results) == 2
        names = {r["agent_name"] for r in results}
        assert names == {"a", "b"}
