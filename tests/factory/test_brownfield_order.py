"""Contract tests for the brownfield Stage 1 order (BUG-0093).

Owned contracts:
  - Stage 1 builds the scope map before the architecture DSL (standard risk)
  - Overview and factory guide name the same order (standard risk)
  - index-lint parses and renders an any_of required input (standard risk)
  - INDEX.yaml carries the architecture agent's any_of input (standard risk)
  - The architecture agent archives nothing; playbook Step 2.0 owns the
    archive (standard risk)
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from conftest import load_script

REPO_ROOT = Path(__file__).resolve().parents[2]
FACTORY = REPO_ROOT / "packages" / "factory"
PLAYBOOK = FACTORY / "playbooks" / "brownfield-onboarding.md"
GUIDE = FACTORY / "docs" / "factory-guide.md"
ARCH_AGENT = FACTORY / "agents" / "architecture-agent.md"
INDEX_YAML = FACTORY / "INDEX.yaml"

il = load_script("index-lint")

_STAGE1_ORDER = [
    ("2.0", "Archive"),
    ("2.1", "Reverse-Map"),
    ("2.2", "Infrastructure-as-Code"),
    ("2.3", "architecture.dsl"),
    ("2.4", "Structurizr"),
    ("2.5", "Validate Architecture"),
    ("2.6", "Stage 1 Exit"),
]


def _stage1_text() -> str:
    text = PLAYBOOK.read_text(encoding="utf-8")
    start = text.index("## Stage 1")
    end = text.index("## Stage 2")
    return text[start:end]


class TestPlaybookStage1Order:
    def test_step_headings_follow_decided_order(self):
        headings = re.findall(r"^### Step (2\.\d) — (.+)$", _stage1_text(), re.M)
        assert [n for n, _ in headings] == [n for n, _ in _STAGE1_ORDER]
        for (_, title), (_, keyword) in zip(headings, _STAGE1_ORDER):
            assert keyword in title, f"{title!r} lacks {keyword!r}"

    def test_scope_map_section_precedes_architecture_section(self):
        text = _stage1_text()
        assert text.index("## Scope Map and Domain Vocabulary") < text.index(
            "## Architecture Docs Baseline"
        )

    def test_arch_lint_transition_leads_to_stage1_exit(self):
        text = _stage1_text()
        lint = text.index("### Step 2.5")
        exit_step = text.index("### Step 2.6")
        assert "Step 2.6" in text[lint:exit_step]

    def test_overview_names_scope_map_before_architecture(self):
        text = PLAYBOOK.read_text(encoding="utf-8")
        line = next(ln for ln in text.splitlines() if "Reverse order workflow" in ln)
        assert line.index("Scope map") < line.index("Architecture baseline")

    def test_factory_guide_names_scope_map_before_dsl(self):
        text = GUIDE.read_text(encoding="utf-8")
        para = next(ln for ln in text.splitlines() if ln.startswith("Brownfield has two stages"))
        assert para.index("scope map") < para.index("architecture DSL")


class TestArchitectureAgentWorkflow:
    """The agent runs after reverse-map, so an archive step would sweep away
    the fresh scope map and CONTEXT.md."""

    def _workflow(self) -> str:
        text = ARCH_AGENT.read_text(encoding="utf-8")
        start = text.index("## Workflow")
        end = text.index("\n## ", start + 1)
        return text[start:end]

    def test_workflow_names_no_archive_step(self):
        steps = re.findall(r"^\d+\. .+$", self._workflow(), re.M)
        assert steps
        for step in steps:
            assert "archive" not in step.lower(), step

    def test_workflow_steps_are_numbered_from_one(self):
        numbers = [int(n) for n in re.findall(r"^(\d+)\. ", self._workflow(), re.M)]
        assert numbers == list(range(1, len(numbers) + 1))


_ANY_OF_FRONTMATTER = (
    "---\nname: test\ninputs:\n"
    "  required:\n"
    "    - any_of:\n"
    "        - type: feature\n"
    '          path_pattern: "docs/spec/*.feature"\n'
    "        - type: scope-map\n"
    "          path_pattern: docs/spec/scope-map.md\n"
    "    - type: dsl\n"
    "      path_pattern: docs/arc42/architecture.dsl\n"
    "  context:\n"
    "    - docs/CONTEXT.md\n"
    "---\n"
)

_ANY_OF_REQUIRED = [
    {
        "any_of": [
            {"type": "feature", "path_pattern": "docs/spec/*.feature"},
            {"type": "scope-map", "path_pattern": "docs/spec/scope-map.md"},
        ]
    },
    {"type": "dsl", "path_pattern": "docs/arc42/architecture.dsl"},
]


class TestIndexLintAnyOf:
    def test_parses_any_of_entry(self):
        fm = il.parse_frontmatter(_ANY_OF_FRONTMATTER)
        assert fm["inputs"]["required"] == _ANY_OF_REQUIRED
        assert fm["inputs"]["context"] == ["docs/CONTEXT.md"]

    def test_renders_any_of_entry_as_yaml(self):
        lines = il._render_structured_field(
            "    ", "inputs", {"required": _ANY_OF_REQUIRED}
        )
        rendered = yaml.safe_load("\n".join(lines))
        assert rendered["inputs"]["required"] == _ANY_OF_REQUIRED

    def test_index_carries_architecture_agent_any_of(self):
        index = yaml.safe_load(INDEX_YAML.read_text(encoding="utf-8"))
        arch = next(a for a in index["agents"] if a["name"] == "architecture-agent")
        assert arch["inputs"]["required"] == [
            {
                "any_of": [
                    {"type": "feature", "path_pattern": "docs/spec/*.feature"},
                    {"type": "scope-map", "path_pattern": "docs/spec/scope-map.md"},
                ]
            }
        ]
