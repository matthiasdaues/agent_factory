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
  - any_of entry is met when one alternative exists (standard risk)
  - Malformed any_of is unmet with a warning, never a crash (standard risk)
  - architecture-agent is eligible from a scope map alone (standard risk)
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

PACKAGES_DIR = Path(__file__).resolve().parents[2] / "packages" / "factory"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.agent_loader import load_agent_definitions
from engine.eligibility import evaluate_agent, evaluate_all


def _write_frontmatter(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
    path.write_text(f"---\n{fm}---\n\n# Content\n")


def _agent(
    name: str, required: list | None = None, context: list | None = None
) -> dict:
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

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                }
            ],
        )
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

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                }
            ],
        )
        result = evaluate_agent(agent, workstream_id="ws-1")
        assert result["eligible"] is True
        assert len(result["requirements"][0]["candidates"]) == 1
        assert "a.md" in result["requirements"][0]["candidates"][0]

    def test_global_scope_passes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "a.md", {"scope": "global"})

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                }
            ],
        )
        result = evaluate_agent(agent, workstream_id="ws-1")
        assert result["eligible"] is True

    def test_skipped_in_open_stage(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "a.md", {"scope": "ws-1"})
        _write_frontmatter(proposals / "b.md", {"scope": "ws-2"})

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                }
            ],
        )
        result = evaluate_agent(agent, workstream_id=None)
        assert result["eligible"] is True
        assert len(result["requirements"][0]["candidates"]) == 2

    def test_missing_scope_passes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "a.md", {"status": "draft"})

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                }
            ],
        )
        result = evaluate_agent(agent, workstream_id="ws-1")
        assert result["eligible"] is True


class TestConditionFieldValue:
    def test_pass(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "x.md", {"status": "accepted"})

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                    "conditions": {"field": "status", "value": "accepted"},
                }
            ],
        )
        result = evaluate_agent(agent)
        assert result["eligible"] is True
        assert result["requirements"][0]["condition_result"] == "pass"

    def test_fail(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "x.md", {"status": "draft"})

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                    "conditions": {"field": "status", "value": "accepted"},
                }
            ],
        )
        result = evaluate_agent(agent)
        assert result["eligible"] is False
        assert result["requirements"][0]["condition_result"] == "fail"


class TestConditionFieldOneOf:
    def test_pass(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "x.md", {"status": "accepted"})

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                    "conditions": {"field": "status", "one_of": ["accepted", "open"]},
                }
            ],
        )
        result = evaluate_agent(agent)
        assert result["eligible"] is True

    def test_fail(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "x.md", {"status": "draft"})

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                    "conditions": {"field": "status", "one_of": ["accepted", "open"]},
                }
            ],
        )
        result = evaluate_agent(agent)
        assert result["eligible"] is False


class TestCardinality:
    def test_zero_unsatisfied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                }
            ],
        )
        result = evaluate_agent(agent)
        assert result["eligible"] is False
        assert result["requirements"][0]["satisfied"] is False
        assert result["requirements"][0]["candidates"] == []

    def test_one_satisfied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "x.md", {"status": "draft"})

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                }
            ],
        )
        result = evaluate_agent(agent)
        assert result["eligible"] is True
        assert len(result["requirements"][0]["candidates"]) == 1

    def test_multiple_reported(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        _write_frontmatter(proposals / "a.md", {"status": "draft"})
        _write_frontmatter(proposals / "b.md", {"status": "draft"})

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                }
            ],
        )
        result = evaluate_agent(agent)
        assert result["eligible"] is True
        assert len(result["requirements"][0]["candidates"]) == 2


class TestMalformedFrontmatter:
    def test_unsatisfied_with_warning(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proposals = tmp_path / "docs" / "proposals"
        proposals.mkdir(parents=True)
        (proposals / "bad.md").write_text("not yaml at all\n")

        agent = _agent(
            "test",
            required=[
                {
                    "type": "proposal",
                    "path_pattern": "docs/proposals/{name}.md",
                    "conditions": {"field": "status", "value": "accepted"},
                }
            ],
        )
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
            _agent(
                "blocked",
                required=[
                    {
                        "type": "proposal",
                        "path_pattern": "nonexistent/{name}.md",
                    }
                ],
            ),
        ]
        results = evaluate_all(agents)
        names = {r["agent_name"]: r["eligible"] for r in results}
        assert names["always"] is True
        assert names["blocked"] is False


_FEATURE_OR_SCOPE_MAP = {
    "any_of": [
        {"type": "feature", "path_pattern": "docs/spec/features/*.feature"},
        {"type": "scope-map", "path_pattern": "docs/spec/scope-map.md"},
    ]
}


class TestAnyOf:
    def test_met_by_second_alternative(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "spec").mkdir(parents=True)
        (tmp_path / "docs" / "spec" / "scope-map.md").write_text("# Scope\n")

        result = evaluate_agent(_agent("arch", required=[_FEATURE_OR_SCOPE_MAP]))
        assert result["eligible"] is True
        req = result["requirements"][0]
        assert req["satisfied"] is True
        assert req["candidates"] == ["docs/spec/scope-map.md"]
        assert [a["satisfied"] for a in req["alternatives"]] == [False, True]

    def test_met_by_first_alternative(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "spec" / "features").mkdir(parents=True)
        (tmp_path / "docs" / "spec" / "features" / "a.feature").write_text("Feature: A\n")

        result = evaluate_agent(_agent("arch", required=[_FEATURE_OR_SCOPE_MAP]))
        assert result["eligible"] is True

    def test_unmet_when_no_alternative_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = evaluate_agent(_agent("arch", required=[_FEATURE_OR_SCOPE_MAP]))
        assert result["eligible"] is False
        req = result["requirements"][0]
        assert req["satisfied"] is False
        assert req["candidates"] == []
        assert "docs/spec/features/*.feature" in req["path_pattern"]
        assert "docs/spec/scope-map.md" in req["path_pattern"]

    def test_combines_with_plain_entries(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "spec").mkdir(parents=True)
        (tmp_path / "docs" / "spec" / "scope-map.md").write_text("# Scope\n")
        (tmp_path / "docs" / "spec" / "architecture.dsl").write_text("workspace {}\n")
        agent = _agent(
            "arch",
            required=[
                _FEATURE_OR_SCOPE_MAP,
                {"type": "dsl", "path_pattern": "docs/spec/architecture.dsl"},
            ],
        )
        result = evaluate_agent(agent)
        assert result["eligible"] is True
        assert [r["satisfied"] for r in result["requirements"]] == [True, True]

    def test_plain_entry_still_blocks(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "spec").mkdir(parents=True)
        (tmp_path / "docs" / "spec" / "scope-map.md").write_text("# Scope\n")
        agent = _agent(
            "arch",
            required=[
                _FEATURE_OR_SCOPE_MAP,
                {"type": "dsl", "path_pattern": "docs/spec/architecture.dsl"},
            ],
        )
        assert evaluate_agent(agent)["eligible"] is False


class TestAnyOfMalformed:
    """BUG-0093: a malformed any_of never crashes. The requirement is unmet
    and the result carries a warning."""

    def _assert_unmet_with_warning(self, tmp_path, monkeypatch, any_of) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "spec").mkdir(parents=True)
        (tmp_path / "docs" / "spec" / "scope-map.md").write_text("# Scope\n")
        result = evaluate_agent(_agent("arch", required=[{"any_of": any_of}]))
        assert result["eligible"] is False
        assert result["requirements"][0]["satisfied"] is False
        assert any("any_of" in w for w in result["warnings"])

    def test_not_a_list(self, tmp_path, monkeypatch):
        self._assert_unmet_with_warning(tmp_path, monkeypatch, "docs/spec/scope-map.md")

    def test_null(self, tmp_path, monkeypatch):
        self._assert_unmet_with_warning(tmp_path, monkeypatch, None)

    def test_empty_list(self, tmp_path, monkeypatch):
        self._assert_unmet_with_warning(tmp_path, monkeypatch, [])

    def test_alternative_not_a_mapping(self, tmp_path, monkeypatch):
        self._assert_unmet_with_warning(
            tmp_path, monkeypatch, ["docs/spec/scope-map.md"]
        )

    def test_alternative_without_path_pattern(self, tmp_path, monkeypatch):
        self._assert_unmet_with_warning(
            tmp_path,
            monkeypatch,
            [{"type": "feature"}, {"type": "scope-map", "path_pattern": "docs/spec/scope-map.md"}],
        )


def _architecture_agent() -> dict:
    agents = load_agent_definitions(PACKAGES_DIR / "agents")
    return next(a for a in agents if a["name"] == "architecture-agent")


class TestArchitectureAgentBrownfieldEntry:
    """BUG-0093: run-step reaches the architecture agent from a scope map."""

    def test_eligible_with_scope_map_and_no_feature(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "spec").mkdir(parents=True)
        (tmp_path / "docs" / "spec" / "scope-map.md").write_text("# Scope\n")

        assert evaluate_agent(_architecture_agent())["eligible"] is True

    def test_eligible_with_feature_and_no_scope_map(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "spec").mkdir(parents=True)
        (tmp_path / "docs" / "spec" / "a.feature").write_text("Feature: A\n")

        assert evaluate_agent(_architecture_agent())["eligible"] is True

    def test_not_eligible_with_neither(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert evaluate_agent(_architecture_agent())["eligible"] is False
