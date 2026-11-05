"""Contract tests for the brownfield entry of derive-feature (BUG-0094).

Owned contracts:
  - The requirements agent is eligible from a scope map alone (standard risk)
  - The requirements agent stays eligible from an accepted proposal alone
    (standard risk)
  - INDEX.yaml carries the requirements agent's any_of input (standard risk)
  - derive-feature documents a brownfield entry that takes the scope map
    (standard risk)
  - Brownfield Step 3.1 names the agent and the skill (standard risk)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
FACTORY = REPO_ROOT / "packages" / "factory"
if str(FACTORY) not in sys.path:
    sys.path.insert(0, str(FACTORY))

from engine.agent_loader import load_agent_definitions
from engine.eligibility import evaluate_agent

SKILL = FACTORY / "skills" / "derive-feature" / "SKILL.md"
AGENT = FACTORY / "agents" / "requirements-agent.md"
PLAYBOOK = FACTORY / "playbooks" / "brownfield-onboarding.md"
INDEX_YAML = FACTORY / "INDEX.yaml"

_PROPOSAL_OR_SCOPE_MAP = [
    {
        "any_of": [
            {
                "type": "proposal",
                "path_pattern": "docs/proposals/{name}.md",
                "conditions": {"field": "status", "value": "accepted"},
            },
            {"type": "scope-map", "path_pattern": "docs/spec/scope-map.md"},
        ]
    }
]


def _requirements_agent() -> dict:
    agents = load_agent_definitions(FACTORY / "agents")
    return next(a for a in agents if a["name"] == "requirements-agent")


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    level = heading.split(" ", 1)[0]
    match = re.compile(rf"^#{{1,{len(level)}}} ", re.M).search(text, start + len(heading))
    return text[start : match.start() if match else len(text)]


class TestRequirementsAgentEligibility:
    def test_eligible_with_scope_map_and_no_proposal(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "spec").mkdir(parents=True)
        (tmp_path / "docs" / "spec" / "scope-map.md").write_text(
            "---\nscope: global\n---\n# Scope map\n"
        )

        assert evaluate_agent(_requirements_agent())["eligible"] is True

    def test_eligible_with_accepted_proposal_and_no_scope_map(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "proposals").mkdir(parents=True)
        (tmp_path / "docs" / "proposals" / "x.md").write_text(
            "---\nstatus: accepted\n---\n# X\n"
        )

        assert evaluate_agent(_requirements_agent())["eligible"] is True

    def test_not_eligible_with_neither(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert evaluate_agent(_requirements_agent())["eligible"] is False

    def test_index_carries_any_of(self):
        index = yaml.safe_load(INDEX_YAML.read_text(encoding="utf-8"))
        agent = next(a for a in index["agents"] if a["name"] == "requirements-agent")
        assert agent["inputs"]["required"] == _PROPOSAL_OR_SCOPE_MAP


class TestDeriveFeatureBrownfieldEntry:
    def _entry(self) -> str:
        return _section(SKILL.read_text(encoding="utf-8"), "## Brownfield Entry")

    def test_entry_takes_scope_map_path(self):
        assert "docs/spec/scope-map.md" in self._entry()

    def test_entry_maps_each_proposal_field(self):
        entry = self._entry()
        for term in ("impact.boundaries", "Sources", "entry points", "<project-name>", "Source:"):
            assert term in entry, term

    def test_entry_states_brownfield_rules(self):
        entry = self._entry()
        for term in ("`implemented`", "Feature Link", "one consolidated", "@-reference"):
            assert term in entry, term


class TestRequirementsAgentWorkflow:
    def test_workflow_names_brownfield_entry(self):
        workflow = _section(AGENT.read_text(encoding="utf-8"), "## Workflow")
        assert "derive-feature docs/spec/scope-map.md" in workflow


class TestPlaybookStep33:
    def test_step_names_agent_and_skill(self):
        step = _section(PLAYBOOK.read_text(encoding="utf-8"), "### Step 3.1")
        assert "**Agent**: `requirements-agent`" in step
        assert "**Skill**: `derive-feature docs/spec/scope-map.md`" in step


class TestRequirementsAgentBranchSelection:
    """BUG-0094 review: the workflow branches overlap; one order decides."""

    def _workflow(self) -> str:
        return _section(AGENT.read_text(encoding="utf-8"), "## Workflow")

    def _selection(self) -> str:
        workflow = self._workflow()
        return workflow[: workflow.index("\n### ")]

    def test_selection_order_stated_before_branches(self):
        selection = self._selection()
        scope_map = selection.index("passes `docs/spec/scope-map.md`")
        accepted = selection.index("accepted proposal", scope_map)
        draft = selection.index("draft proposal", accepted)
        assert scope_map < accepted < draft

    def test_accepted_proposal_wins_over_existing_scope_map(self):
        assert "even when a scope map exists" in self._selection()

    def test_draft_proposal_goes_to_pause_point(self):
        selection = self._selection()
        draft = selection.index("draft proposal")
        assert "proposal-acceptance pause point" in selection[draft:]

    def test_no_branch_matches_on_scope_map_existence(self):
        assert "nor a scope map exists" not in self._workflow()


class TestBrownfieldEntryDraftMapStop:
    """BUG-0094 review: a draft scope map must not reach the brownfield entry."""

    def _entry(self) -> str:
        return _section(SKILL.read_text(encoding="utf-8"), "## Brownfield Entry")

    def test_first_step_stops_on_draft_map(self):
        entry = self._entry()
        first_step = entry[: entry.index("| Proposal field")]
        for term in ("frontmatter", "`status: draft`", "stop", "derive nothing", "Step 2.6"):
            assert term in first_step, term

    def test_entry_drops_unchecked_stage_one_claim(self):
        assert "after\nStage 1 has confirmed" not in self._entry()

    def test_agent_brownfield_branch_refers_to_draft_stop(self):
        branch = _section(AGENT.read_text(encoding="utf-8"), "### From the scope map")
        assert "once Stage 1 has confirmed" not in branch
        assert "`status: draft`" in branch
