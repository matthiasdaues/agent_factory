"""Contract tests for the precondition evaluator.

Owned contracts:
  - Glob expansion replaces {name} with * (standard risk)
  - Scope filtering narrows to workstream or global (standard risk)
  - Scope filtering skipped in Open Stage (standard risk)
  - Condition field/value checks frontmatter (standard risk)
  - Condition field/one_of accepts any listed value (standard risk)
  - Agent with no inputs.required is always eligible (standard risk)
  - Zero survivors means unsatisfied (standard risk)
  - One survivor means satisfied (standard risk)
  - Multiple survivors reported for selection (standard risk)
  - Missing file means unsatisfied (standard risk)
  - Malformed frontmatter means unsatisfied with warning (standard risk)
  - Missing scope passes all candidates (standard risk)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

PACKAGES_DIR = Path(__file__).resolve().parents[2] / "packages" / "factory"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.eligibility import evaluate_agent, evaluate_all


def _write_frontmatter(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
    path.write_text(f"---\n{fm}---\n\n# Content\n")


def _agent(name: str, required: list | None = None, context: list | None = None) -> dict:
    inputs: dict = {}
    if required is not None:
        inputs["required"] = required
    if context is not None:
        inputs["context"] = context
    return {"name": name, "inputs": inputs}


class TestNoRequiredInputs:
    def test_always_eligible(self):
        result = evaluate_agent(_agent("coaching", required=[]))
        assert result["eligible"] is True
        assert result["requirements"] == []

    def test_no_inputs_key_eligible(self):
        result = evaluate_agent({"name": "virgil"})
        assert result["eligible"] is True


class TestGlobExpansion:
    def test_replaces_name_placeholder(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "my-idea.md", {"status": "draft"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
        }])
        result = evaluate_agent(agent)
        assert result["eligible"] is True
        assert len(result["requirements"]) == 1
        assert len(result["requirements"][0]["candidates"]) == 1


class TestScopeFiltering:
    def test_filters_to_workstream(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "a.md", {"scope": "ws-1"})
        _write_frontmatter(proposals / "b.md", {"scope": "ws-2"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
        }])
        result = evaluate_agent(agent, workstream_id="ws-1")
        assert result["eligible"] is True
        assert len(result["requirements"][0]["candidates"]) == 1
        assert "a.md" in result["requirements"][0]["candidates"][0]

    def test_global_scope_passes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "a.md", {"scope": "global"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
        }])
        result = evaluate_agent(agent, workstream_id="ws-1")
        assert result["eligible"] is True

    def test_skipped_in_open_stage(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "a.md", {"scope": "ws-1"})
        _write_frontmatter(proposals / "b.md", {"scope": "ws-2"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
        }])
        result = evaluate_agent(agent, workstream_id=None)
        assert result["eligible"] is True
        assert len(result["requirements"][0]["candidates"]) == 2

    def test_missing_scope_passes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "a.md", {"status": "draft"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
        }])
        result = evaluate_agent(agent, workstream_id="ws-1")
        assert result["eligible"] is True


class TestConditionFieldValue:
    def test_pass(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "x.md", {"status": "accepted"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
            "conditions": {"field": "status", "value": "accepted"},
        }])
        result = evaluate_agent(agent)
        assert result["eligible"] is True
        assert result["requirements"][0]["condition_result"] == "pass"

    def test_fail(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "x.md", {"status": "draft"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
            "conditions": {"field": "status", "value": "accepted"},
        }])
        result = evaluate_agent(agent)
        assert result["eligible"] is False
        assert result["requirements"][0]["condition_result"] == "fail"


class TestConditionFieldOneOf:
    def test_pass(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "x.md", {"status": "accepted"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
            "conditions": {"field": "status", "one_of": ["accepted", "open"]},
        }])
        result = evaluate_agent(agent)
        assert result["eligible"] is True

    def test_fail(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "x.md", {"status": "draft"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
            "conditions": {"field": "status", "one_of": ["accepted", "open"]},
        }])
        result = evaluate_agent(agent)
        assert result["eligible"] is False


class TestCardinality:
    def test_zero_unsatisfied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
        }])
        result = evaluate_agent(agent)
        assert result["eligible"] is False
        assert result["requirements"][0]["satisfied"] is False
        assert result["requirements"][0]["candidates"] == []

    def test_one_satisfied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "x.md", {"status": "draft"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
        }])
        result = evaluate_agent(agent)
        assert result["eligible"] is True
        assert len(result["requirements"][0]["candidates"]) == 1

    def test_multiple_reported(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "a.md", {"status": "draft"})
        _write_frontmatter(proposals / "b.md", {"status": "draft"})

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
        }])
        result = evaluate_agent(agent)
        assert result["eligible"] is True
        assert len(result["requirements"][0]["candidates"]) == 2


class TestMalformedFrontmatter:
    def test_unsatisfied_with_warning(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        (proposals / "bad.md").write_text("not yaml at all\n")

        agent = _agent("test", required=[{
            "type": "proposal",
            "path_pattern": "docs/proposals/{name}.md",
            "conditions": {"field": "status", "value": "accepted"},
        }])
        result = evaluate_agent(agent)
        assert result["eligible"] is False
        assert len(result["warnings"]) > 0


class TestEvaluateAll:
    def test_returns_all_agents(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agents = [
            _agent("a", required=[]),
            _agent("b", required=[]),
        ]
        results = evaluate_all(agents)
        assert len(results) == 2
        assert all(r["eligible"] for r in results)

    def test_mixed_eligibility(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agents = [
            _agent("always", required=[]),
            _agent("blocked", required=[{
                "type": "proposal",
                "path_pattern": "nonexistent/{name}.md",
            }]),
        ]
        results = evaluate_all(agents)
        names = {r["agent_name"]: r["eligible"] for r in results}
        assert names["always"] is True
        assert names["blocked"] is False
