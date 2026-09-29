"""Behavioral verification for activity-graph orchestration model.

ST-0265: Verify unrestricted selection, ceremony-free rework,
research routing, and stageless delivery.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES_DIR = REPO_ROOT / "packages" / "factory"
AGENTS_DIR = PACKAGES_DIR / "agents"
ENGINE_DIR = PACKAGES_DIR / "engine"

import sys

if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.eligibility import evaluate_agent, evaluate_all

# ── 1. Unrestricted selection: no blocking on unsatisfied inputs ────────


class TestUnrestrictedSelection:
    def test_select_unsatisfied_no_blocking(self, tmp_path):
        """Selecting an agent with unsatisfied inputs produces no dialog,
        override flag, or justification field — the evaluator just reports
        evidence and the caller decides."""
        agent = {
            "name": "test-agent",
            "inputs": {
                "required": [
                    {
                        "type": "proposal",
                        "path_pattern": str(tmp_path / "nonexistent" / "{name}.md"),
                    }
                ],
            },
        }
        result = evaluate_agent(agent)
        assert result["eligible"] is False
        assert len(result["requirements"]) == 1
        assert result["requirements"][0]["satisfied"] is False
        # The result is pure data — no "blocked", "override", "confirm",
        # or "justification" key exists.
        assert "blocked" not in result
        assert "override" not in result
        assert "confirmation" not in result
        assert "justification" not in result

    def test_intent_select_has_no_blocking_mechanism(self):
        """The intent select script has no confirmation dialog, override
        flag, or justification prompt in its source."""
        intent_script = PACKAGES_DIR / "scripts" / "intent"
        if not intent_script.exists():
            pytest.skip("intent script not yet created")
        source = intent_script.read_text(encoding="utf-8")
        for forbidden in [
            "confirm",
            "override",
            "justification",
            "block",
            "are you sure",
            "proceed anyway",
        ]:
            assert forbidden not in source.lower(), (
                f"intent select contains blocking mechanism: '{forbidden}'"
            )


# ── 2. Rework without ceremony ─────────────────────────────────────────


class TestReworkWithoutCeremony:
    def test_rework_reflects_in_evaluator(self, tmp_path):
        """Editing an artifact and re-running the evaluator reflects the
        change. No state machine update or reconciliation step needed."""
        proposal = tmp_path / "proposals" / "test.md"
        proposal.parent.mkdir(parents=True)
        proposal.write_text(
            textwrap.dedent("""\
                ---
                status: draft
                ---
                # Test proposal
            """),
            encoding="utf-8",
        )

        agent = {
            "name": "arch-agent",
            "inputs": {
                "required": [
                    {
                        "type": "proposal",
                        "path_pattern": str(tmp_path / "proposals" / "{name}.md"),
                        "conditions": {"field": "status", "value": "accepted"},
                    }
                ],
            },
        }

        result1 = evaluate_agent(agent)
        assert result1["eligible"] is False
        assert result1["requirements"][0]["satisfied"] is False

        # Edit the artifact — no ceremony, no state transition
        proposal.write_text(
            textwrap.dedent("""\
                ---
                status: accepted
                ---
                # Test proposal
            """),
            encoding="utf-8",
        )

        result2 = evaluate_agent(agent)
        assert result2["eligible"] is True
        assert result2["requirements"][0]["satisfied"] is True

    def test_no_state_machine_required_for_rework(self):
        """The evaluator module has no state machine, transition, or
        reconciliation logic."""
        source = (ENGINE_DIR / "eligibility.py").read_text(encoding="utf-8")
        for forbidden in [
            "state_machine",
            "transition",
            "reconcil",
            "ceremony",
            "cycle_entry",
        ]:
            assert forbidden not in source.lower(), (
                f"evaluator contains state management: '{forbidden}'"
            )


# ── 3. Research routing through preconditions ──────────────────────────


class TestResearchRouting:
    def test_research_output_satisfies_downstream(self, tmp_path):
        """A research report satisfies a downstream agent's precondition
        when declared as a required input."""
        report = tmp_path / "research" / "findings.md"
        report.parent.mkdir(parents=True)
        report.write_text(
            textwrap.dedent("""\
                ---
                title: Research findings
                ---
                # Findings
            """),
            encoding="utf-8",
        )

        agent = {
            "name": "downstream-agent",
            "inputs": {
                "required": [
                    {
                        "type": "research-report",
                        "path_pattern": str(tmp_path / "research" / "{name}.md"),
                    }
                ],
            },
        }

        result = evaluate_agent(agent)
        assert result["eligible"] is True
        assert result["requirements"][0]["satisfied"] is True
        assert str(report) in result["requirements"][0]["candidates"]

    def test_no_origin_cycle_in_research_agent(self):
        """The researcher agent definition has no origin_cycle or
        return_cycle fields."""
        researcher = AGENTS_DIR / "researcher.md"
        if not researcher.exists():
            pytest.skip("researcher.md not found")
        text = researcher.read_text(encoding="utf-8")
        assert "origin_cycle" not in text
        assert "return_cycle" not in text


# ── 4. No cycle vocabulary in agent definitions ────────────────────────


class TestNoCycleVocabulary:
    def test_no_cycle_vocabulary_in_agents(self):
        """No agent definition contains eligible_cycles, origin_cycle,
        or return_cycle."""
        if not AGENTS_DIR.exists():
            pytest.skip("agents directory not found")

        agent_files = sorted(AGENTS_DIR.glob("*.md"))
        assert len(agent_files) > 0, "no agent files found"

        violations = []
        forbidden = ["eligible_cycles:", "origin_cycle:", "return_cycle:"]
        for path in agent_files:
            text = path.read_text(encoding="utf-8")
            for term in forbidden:
                if term in text:
                    violations.append(f"{path.name}: contains '{term}'")

        assert violations == [], "cycle vocabulary found:\n" + "\n".join(violations)

    def test_no_cycle_vocabulary_in_engine(self):
        """Engine modules eligibility.py, readiness.py, and
        recommendations.py have no cycle imports or references."""
        modules = ["eligibility.py", "readiness.py", "recommendations.py"]
        forbidden = [
            "cycle_model",
            "from engine.cycles",
            "REQUIRED_CYCLES",
            "eligible_cycles",
            "current_cycle",
        ]

        violations = []
        for mod_name in modules:
            path = ENGINE_DIR / mod_name
            if not path.exists():
                continue
            source = path.read_text(encoding="utf-8")
            for term in forbidden:
                if term in source:
                    violations.append(f"{mod_name}: contains '{term}'")

        assert violations == [], "cycle vocabulary found:\n" + "\n".join(violations)


# ── 5. Stageless delivery sequence ─────────────────────────────────────


class TestStagelessDelivery:
    def test_delivery_sequence_precondition_based(self, tmp_path):
        """A sequence of agent selections works through precondition
        satisfaction, not named stage transitions."""
        # Set up a mini delivery pipeline
        proposals_dir = tmp_path / "proposals"
        specs_dir = tmp_path / "spec"
        backlog_dir = tmp_path / "backlog"

        proposals_dir.mkdir()
        specs_dir.mkdir()
        backlog_dir.mkdir()

        # Define agents with chained preconditions
        req_agent = {
            "name": "requirements-agent",
            "inputs": {
                "required": [
                    {
                        "type": "proposal",
                        "path_pattern": str(proposals_dir / "{name}.md"),
                        "conditions": {"field": "status", "value": "accepted"},
                    }
                ],
            },
        }
        arch_agent = {
            "name": "architecture-agent",
            "inputs": {
                "required": [
                    {
                        "type": "feature",
                        "path_pattern": str(specs_dir / "*.feature"),
                    }
                ],
            },
        }
        plan_agent = {
            "name": "planning-agent",
            "inputs": {
                "required": [
                    {
                        "type": "scope-map",
                        "path_pattern": str(specs_dir / "scope-map.md"),
                    }
                ],
            },
        }
        dev_agent = {
            "name": "developer-agent",
            "inputs": {
                "required": [
                    {
                        "type": "story",
                        "path_pattern": str(backlog_dir / "ST-*.md"),
                        "conditions": {"field": "status", "value": "pending"},
                    }
                ],
            },
        }

        agents = [req_agent, arch_agent, plan_agent, dev_agent]

        # Initially: only req_agent is eligible (proposal exists)
        (proposals_dir / "test.md").write_text(
            "---\nstatus: accepted\n---\n# Test\n",
            encoding="utf-8",
        )

        results = evaluate_all(agents)
        eligible_names = {r["agent_name"] for r in results if r["eligible"]}
        assert "requirements-agent" in eligible_names
        assert "architecture-agent" not in eligible_names

        # After spec work: arch_agent becomes eligible
        (specs_dir / "test.feature").write_text(
            "Feature: Test\n",
            encoding="utf-8",
        )

        results = evaluate_all(agents)
        eligible_names = {r["agent_name"] for r in results if r["eligible"]}
        assert "architecture-agent" in eligible_names
        assert "planning-agent" not in eligible_names

        # After scope map: plan_agent becomes eligible
        (specs_dir / "scope-map.md").write_text(
            "---\ntitle: Scope map\n---\n# Scope\n",
            encoding="utf-8",
        )

        results = evaluate_all(agents)
        eligible_names = {r["agent_name"] for r in results if r["eligible"]}
        assert "planning-agent" in eligible_names
        assert "developer-agent" not in eligible_names

        # After story creation: dev_agent becomes eligible
        (backlog_dir / "ST-0001.md").write_text(
            "---\nstatus: pending\n---\n# Story\n",
            encoding="utf-8",
        )

        results = evaluate_all(agents)
        eligible_names = {r["agent_name"] for r in results if r["eligible"]}
        assert "developer-agent" in eligible_names

        # All four became eligible through preconditions.
        # No named stage, cycle transition, or state machine was involved.
