"""Tests for the research-topic playbook and the index-lint nested-playbook
discovery fix (ST-0033).

The research-topic playbook is a prose runbook that wires the thirteen-step
falsification-driven research procedure. Tests verify:

1. File existence and frontmatter: the nested `research-topic.md`
   exists and carries the frontmatter index-lint requires (title, category,
   type, scenario, version).
2. Body wiring: all thirteen steps appear in order, each naming an agent, an
   input, and an output; the schema -> policy -> semantic gate is placed; the
   brief input and the full output set are declared; and the two-researchers,
   three-reviewers, and new-version-on-resolution rules are stated.
3. Integration proof of the index-lint fix: after regeneration the real
   `factory/INDEX.yaml` lists a playbook `name: research-topic` at
   `path: playbooks/research-topic.md`, while still listing the
   existing flat playbooks.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest


_ROOT = Path(__file__).resolve().parents[2]
_PLAYBOOK = _ROOT / "factory" / "playbooks" / "research-topic.md"
_INDEX = _ROOT / "factory" / "INDEX.yaml"
_INDEX_LINT = _ROOT / "factory" / "scripts" / "index-lint"


def _parse_frontmatter(file_path: Path) -> dict:
    """Extract key: value pairs from a markdown file's YAML frontmatter."""
    text = file_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}

    end_index = text.find("---", 3)
    if end_index == -1:
        return {}

    frontmatter_text = text[3:end_index]
    fields = {}
    for match in re.finditer(r"^([\w-]+):\s*(.+?)$", frontmatter_text, re.MULTILINE):
        key, value = match.groups()
        fields[key] = value.strip()

    return fields


class TestPlaybookExistsAndFrontmatter:
    """The nested playbook exists with the frontmatter index-lint requires."""

    def test_playbook_exists(self):
        assert _PLAYBOOK.exists(), f"Playbook not found at {_PLAYBOOK}"

    def test_frontmatter_keys(self):
        fm = _parse_frontmatter(_PLAYBOOK)
        assert fm.get("title") == "Research Topic Playbook"
        assert fm.get("category") == "orchestration"
        assert fm.get("type") == "runbook"
        assert fm.get("scenario") == "research-topic"
        assert fm.get("version"), "playbook missing 'version' in frontmatter"


class TestThirteenStepsInOrder:
    """All thirteen steps appear in order, each with agent, input, output."""

    _text = _PLAYBOOK.read_text(encoding="utf-8")

    # (step number, agent that owns the step).
    _expected_steps = [
        (1, "research-orchestrator"),
        (2, "researcher"),
        (3, "research-orchestrator"),
        (4, "researcher"),
        (5, "researcher"),
        (6, "research-orchestrator"),
        (7, "researcher"),
        (8, "claim-reviewer"),
        (9, "claim-reviewer"),
        (10, "research-orchestrator"),
        (11, "research-orchestrator"),
        (12, "research-report-writer"),
        (13, "research-orchestrator"),
    ]

    def test_all_step_headings_present_in_order(self):
        """Every step heading appears and they appear in ascending order."""
        positions = []
        for num, _ in self._expected_steps:
            match = re.search(rf"^###\s+Step\s+{num}\b", self._text, re.MULTILINE)
            assert match, f"Step {num} heading not found"
            positions.append(match.start())

        assert positions == sorted(positions), "Steps are not in ascending order"

    def test_each_step_names_its_agent(self):
        """Each step declares its owning agent with the `**Agent**: \\`x\\``
        convention, in step order."""
        agent_refs = re.findall(r"\*\*Agent\*\*:\s*`([a-z][a-z0-9-]*)`", self._text)
        expected = [agent for _, agent in self._expected_steps]
        assert agent_refs == expected, (
            f"Agent sequence mismatch: {agent_refs} != {expected}"
        )

    def test_each_step_declares_input_and_output(self):
        """Each step block declares an Input and an Output artifact."""
        for num, _ in self._expected_steps:
            block = self._step_block(num)
            assert "**Input**" in block, f"Step {num} missing Input"
            assert "**Output**" in block, f"Step {num} missing Output"

    def _step_block(self, num: int) -> str:
        start = re.search(rf"^###\s+Step\s+{num}\b", self._text, re.MULTILINE)
        assert start, f"Step {num} not found"
        nxt = re.search(rf"^###\s+Step\s+{num + 1}\b", self._text, re.MULTILINE)
        end = nxt.start() if nxt else len(self._text)
        return self._text[start.start() : end]


class TestValidationGate:
    """The schema -> policy -> semantic gate is placed between steps."""

    _text = _PLAYBOOK.read_text(encoding="utf-8")

    def test_three_stage_scripts_referenced(self):
        assert "factory/scripts/schema-validate" in self._text
        assert "factory/scripts/policy-validate" in self._text
        assert re.search(r"semantic review", self._text, re.IGNORECASE)

    def test_gate_order_schema_then_policy_then_semantic(self):
        """Schema is described before policy, which is before semantic review."""
        schema = self._text.lower().find("schema validation")
        policy = self._text.lower().find("policy validation")
        semantic = self._text.lower().find("semantic review")
        assert -1 < schema < policy < semantic

    def test_progression_blocks_on_failure(self):
        """The playbook states progression blocks when a stage fails."""
        pattern = re.compile(
            r"(block|fail).*(progress|next step)|"
            r"must\s+PASS|before the next step",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), "Gate does not state it blocks progression"


class TestInputAndOutputSet:
    """The brief input and the full output set are declared."""

    _text = _PLAYBOOK.read_text(encoding="utf-8")

    def test_brief_input_declared(self):
        assert "research-brief.md" in self._text

    def test_full_output_set_declared(self):
        for artifact in [
            "research-plan",
            "assignments",
            "sources",
            "conjectures",
            "tests",
            "reviews",
            "votes",
            "claim-register",
            "final-report",
        ]:
            assert artifact in self._text, f"Output artifact '{artifact}' not declared"


class TestEnforcedRules:
    """The 2-researchers, 3-reviewers, new-version rules are stated."""

    _text = _PLAYBOOK.read_text(encoding="utf-8")

    def test_two_independent_researchers(self):
        pattern = re.compile(
            r"(at least )?two researchers.*independ|"
            r"two independent researchers",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), "Two-researchers rule not stated"

    def test_three_reviewers(self):
        pattern = re.compile(r"(at least )?three reviewers", re.IGNORECASE)
        assert pattern.search(self._text), "Three-reviewers rule not stated"

    def test_new_version_on_resolution(self):
        pattern = re.compile(
            r"semantic change.*new claim version|"
            r"any semantic change.*new.*version",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), "New-version-on-resolution rule not stated"

    def test_routes_failed_claims_through_resolution(self):
        pattern = re.compile(
            r"(refuted|unresolved).*(route|resolution)|"
            r"route.*(refuted|unresolved)",
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(self._text), "Resolution routing not stated"


class TestIndexLintIntegration:
    """The regenerated INDEX.yaml lists research-topic and the flat playbooks."""

    def test_index_is_current(self):
        """index-lint --check confirms the committed INDEX.yaml is up to date.

        The script is run through its own shebang (``uv run --script``), which
        provisions tiktoken so the check reproduces the committed token counts;
        running it under a bare interpreter would fall back to chars/4 counts
        and spuriously report the index as stale.
        """
        result = subprocess.run(
            [str(_INDEX_LINT), "--check"],
            cwd=str(_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"INDEX.yaml is stale — regenerate with index-lint:\n{result.stdout}\n{result.stderr}"
        )

    def test_research_topic_listed(self):
        text = _INDEX.read_text(encoding="utf-8")
        assert "name: research-topic" in text, (
            "INDEX.yaml does not list the research-topic playbook"
        )
        assert "path: playbooks/research-topic.md" in text, (
            "research-topic playbook not indexed at its flat path"
        )

    def test_research_topic_agent_sequence(self):
        """The indexed playbook carries its derived agent sequence."""
        text = _INDEX.read_text(encoding="utf-8")
        block = text[text.find("name: research-topic") :]
        for agent in [
            "research-orchestrator",
            "researcher",
            "claim-reviewer",
            "research-report-writer",
        ]:
            assert f"- {agent}" in block, (
                f"research-topic agent sequence missing {agent}"
            )

    @pytest.mark.parametrize("flat", ["feature-addition", "bug-fix"])
    def test_flat_playbooks_still_listed(self, flat):
        text = _INDEX.read_text(encoding="utf-8")
        assert f"name: {flat}" in text, (
            f"flat playbook '{flat}' dropped from INDEX.yaml"
        )
