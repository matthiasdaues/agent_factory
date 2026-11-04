"""Behavior tests for the Factory-to-Miro ETL."""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATE = REPO_ROOT / "poc" / "workflow" / "miro-generator" / "generate.py"


def _write_agent(
    factory_root: Path,
    name: str,
    *,
    required_input: str | None = None,
    context_input: str | None = None,
    output: str | None = None,
    skills: tuple[str, ...] = (),
) -> None:
    agents = factory_root / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    lines = ["---", f"name: {name}", f"title: {name.replace('-', ' ').title()}"]
    if skills:
        lines.append("skills:")
        lines.extend(f"  - {skill}" for skill in skills)
    if required_input:
        lines.extend(
            [
                "inputs:",
                "  required:",
                "    - type: artifact",
                f"      path_pattern: {required_input}",
            ]
        )
    if context_input:
        if not required_input:
            lines.append("inputs:")
        lines.extend(["  context:", f"    - {context_input}"])
    if output:
        lines.extend(
            [
                "outputs:",
                "  minimum_changed: 1",
                "  declarations:",
                f"    - path_pattern: {output}",
                "      required: true",
            ]
        )
    lines.extend(["---", "", f"# {name}", ""])
    (agents / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")


def _write_skill(
    factory_root: Path,
    name: str,
    *,
    context_input: str | None = None,
    output: str | None = None,
) -> None:
    skill_dir = factory_root / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"name: {name}",
        "category: quality",
        f"description: {name}",
    ]
    if context_input:
        lines.extend(["inputs:", "  context:", f"    - {context_input}"])
    if output:
        lines.extend(["outputs:", f"  - {output}"])
    lines.extend(["---", "", f"# {name}", ""])
    (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")


def _write_index_playbook(
    factory_root: Path, name: str, agents: tuple[str, ...]
) -> None:
    playbooks = factory_root / "playbooks"
    playbooks.mkdir(parents=True, exist_ok=True)
    (playbooks / f"{name}.md").write_text(
        f"---\ntitle: {name}\n---\n\n# {name}\n", encoding="utf-8"
    )
    agent_lines = "\n".join(f"      - {agent}" for agent in agents)
    (factory_root / "INDEX.yaml").write_text(
        "\n".join(
            [
                "---",
                "playbooks:",
                f"  - name: {name}",
                f"    path: playbooks/{name}.md",
                "    agents:",
                agent_lines,
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_cli_connects_agent_output_to_matching_required_input(tmp_path: Path) -> None:
    factory_root = tmp_path / "factory"
    _write_agent(
        factory_root,
        "requirements-agent",
        output="docs/spec/features/{name}.feature",
    )
    _write_agent(
        factory_root,
        "architecture-agent",
        required_input="docs/spec/features/*.feature",
    )
    output_dir = tmp_path / "map"

    result = subprocess.run(
        [
            sys.executable,
            str(GENERATE),
            "--factory-root",
            str(factory_root),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    factory_map = json.loads((output_dir / "factory-map.json").read_text())
    assert factory_map["relationships"] == [
        {
            "consumer": "architecture-agent",
            "consumer_source": "agents/architecture-agent.md",
            "input_role": "required",
            "match": "exact",
            "producer": "requirements-agent",
            "producer_source": "agents/requirements-agent.md",
            "via_input": "docs/spec/features/*.feature",
            "via_output": "docs/spec/features/{name}.feature",
        }
    ]


def test_cli_marks_glob_to_glob_context_relationship_as_possible(
    tmp_path: Path,
) -> None:
    factory_root = tmp_path / "factory"
    _write_agent(
        factory_root,
        "reconciliation-agent",
        output="docs/spec/**/*.md",
    )
    _write_agent(
        factory_root,
        "planning-agent",
        context_input="docs/spec/*.md",
    )
    output_dir = tmp_path / "map"

    result = subprocess.run(
        [
            sys.executable,
            str(GENERATE),
            "--factory-root",
            str(factory_root),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    relationships = json.loads((output_dir / "factory-map.json").read_text())[
        "relationships"
    ]
    assert relationships == [
        {
            "consumer": "planning-agent",
            "consumer_source": "agents/planning-agent.md",
            "input_role": "context",
            "match": "possible",
            "producer": "reconciliation-agent",
            "producer_source": "agents/reconciliation-agent.md",
            "via_input": "docs/spec/*.md",
            "via_output": "docs/spec/**/*.md",
        }
    ]


def test_diagnostics_report_broad_patterns_and_possible_relationships(
    tmp_path: Path,
) -> None:
    factory_root = tmp_path / "factory"
    _write_agent(
        factory_root,
        "reconciliation-agent",
        output="docs/spec/**/*.md",
    )
    _write_agent(
        factory_root,
        "planning-agent",
        context_input="docs/spec/*.md",
    )
    output_dir = tmp_path / "map"

    result = subprocess.run(
        [
            sys.executable,
            str(GENERATE),
            "--factory-root",
            str(factory_root),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    diagnostics = json.loads((output_dir / "factory-map-diagnostics.json").read_text())
    assert diagnostics["broad_patterns"] == [
        {
            "component": "reconciliation-agent",
            "kind": "agent",
            "pattern": "docs/spec/**/*.md",
            "role": "output",
            "source": "agents/reconciliation-agent.md",
        }
    ]
    assert diagnostics["possible_relationships"] == [
        {
            "consumer": "planning-agent",
            "consumer_kind": "agent",
            "producer": "reconciliation-agent",
            "producer_kind": "agent",
            "via_input": "docs/spec/*.md",
            "via_output": "docs/spec/**/*.md",
        }
    ]


def test_unmatched_artifact_contracts_remain_visible_and_are_diagnosed(
    tmp_path: Path,
) -> None:
    factory_root = tmp_path / "factory"
    _write_agent(factory_root, "producer-agent", output="docs/orphan-output.md")
    _write_agent(factory_root, "consumer-agent", context_input="docs/missing-input.md")
    output_dir = tmp_path / "map"

    result = subprocess.run(
        [
            sys.executable,
            str(GENERATE),
            "--factory-root",
            str(factory_root),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    artifacts = (output_dir / "artifacts.svg").read_text()
    diagnostics = json.loads((output_dir / "factory-map-diagnostics.json").read_text())
    assert 'data-content="docs/orphan-output.md"' in artifacts
    assert 'data-content="docs/missing-input.md"' in artifacts
    assert diagnostics["unmatched_outputs"] == [
        {
            "component": "producer-agent",
            "kind": "agent",
            "pattern": "docs/orphan-output.md",
            "source": "agents/producer-agent.md",
        }
    ]
    assert diagnostics["unmatched_inputs"] == [
        {
            "component": "consumer-agent",
            "kind": "agent",
            "pattern": "docs/missing-input.md",
            "role": "context",
            "source": "agents/consumer-agent.md",
        }
    ]


def test_cli_binds_skill_and_reports_missing_artifact_contract(tmp_path: Path) -> None:
    factory_root = tmp_path / "factory"
    _write_skill(factory_root, "fagan-review")
    _write_agent(factory_root, "qa-agent", skills=("fagan-review",))
    output_dir = tmp_path / "map"

    result = subprocess.run(
        [
            sys.executable,
            str(GENERATE),
            "--factory-root",
            str(factory_root),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    factory_map = json.loads((output_dir / "factory-map.json").read_text())
    diagnostics = json.loads((output_dir / "factory-map-diagnostics.json").read_text())
    assert factory_map["skill_bindings"] == [
        {
            "agent": "qa-agent",
            "agent_source": "agents/qa-agent.md",
            "skill": "fagan-review",
            "skill_source": "skills/fagan-review/SKILL.md",
        }
    ]
    assert diagnostics["missing_skill_contracts"] == [
        {
            "skill": "fagan-review",
            "source": "skills/fagan-review/SKILL.md",
        }
    ]


def test_skill_artifact_contract_participates_in_data_flow(tmp_path: Path) -> None:
    factory_root = tmp_path / "factory"
    _write_skill(factory_root, "detect-test-regime", output="docs/testing.yaml")
    _write_agent(factory_root, "planning-agent", context_input="docs/testing.yaml")
    output_dir = tmp_path / "map"

    result = subprocess.run(
        [
            sys.executable,
            str(GENERATE),
            "--factory-root",
            str(factory_root),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    factory_map = json.loads((output_dir / "factory-map.json").read_text())
    assert factory_map["skill_relationships"] == [
        {
            "consumer": "planning-agent",
            "consumer_kind": "agent",
            "consumer_source": "agents/planning-agent.md",
            "input_role": "context",
            "match": "exact",
            "producer": "detect-test-regime",
            "producer_kind": "skill",
            "producer_source": "skills/detect-test-regime/SKILL.md",
            "via_input": "docs/testing.yaml",
            "via_output": "docs/testing.yaml",
        }
    ]
    artifacts = (output_dir / "artifacts.svg").read_text()
    assert 'id="skill-detect-test-regime"' in artifacts
    assert 'data-start="skill-detect-test-regime"' in artifacts


def test_playbook_route_contains_only_forward_relationships_between_its_agents(
    tmp_path: Path,
) -> None:
    factory_root = tmp_path / "factory"
    _write_agent(factory_root, "author-agent", output="docs/result.md")
    _write_agent(factory_root, "review-agent", required_input="docs/result.md")
    _write_agent(factory_root, "outside-agent", required_input="docs/result.md")
    _write_index_playbook(
        factory_root, "feature-addition", ("author-agent", "review-agent")
    )
    output_dir = tmp_path / "map"

    result = subprocess.run(
        [
            sys.executable,
            str(GENERATE),
            "--factory-root",
            str(factory_root),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    playbooks = json.loads((output_dir / "factory-map.json").read_text())["playbooks"]
    assert playbooks == [
        {
            "agents": ["author-agent", "review-agent"],
            "name": "feature-addition",
            "relationships": [
                {
                    "consumer": "review-agent",
                    "match": "exact",
                    "producer": "author-agent",
                    "via_input": "docs/result.md",
                    "via_output": "docs/result.md",
                }
            ],
            "source": "playbooks/feature-addition.md",
        }
    ]


def test_playbook_step_contracts_create_step_relationships(tmp_path: Path) -> None:
    factory_root = tmp_path / "factory"
    _write_index_playbook(factory_root, "feature-addition", ())
    (factory_root / "playbooks" / "feature-addition.md").write_text(
        """---
title: Feature Addition
steps:
  - name: author
    inputs: []
    outputs:
      - docs/result.md
  - name: review
    inputs:
      - docs/result.md
    outputs:
      - docs/findings/*.md
---

# Feature Addition
""",
        encoding="utf-8",
    )
    output_dir = tmp_path / "map"

    result = subprocess.run(
        [
            sys.executable,
            str(GENERATE),
            "--factory-root",
            str(factory_root),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    playbook = json.loads((output_dir / "factory-map.json").read_text())["playbooks"][0]
    assert [step["name"] for step in playbook["steps"]] == ["author", "review"]
    assert playbook["step_relationships"] == [
        {
            "consumer": "review",
            "match": "exact",
            "producer": "author",
            "via_input": "docs/result.md",
            "via_output": "docs/result.md",
        }
    ]
    detail = (output_dir / "playbooks" / "feature-addition.svg").read_text()
    assert 'data-content="docs/result.md"' in detail
    assert 'data-start="step-0-author"' in detail
    assert 'data-end="step-1-review"' in detail


def test_cli_renders_miro_overview_artifacts_and_playbook_detail(
    tmp_path: Path,
) -> None:
    factory_root = tmp_path / "factory"
    _write_agent(factory_root, "author-agent", output="docs/result.md")
    _write_agent(factory_root, "review-agent", required_input="docs/result.md")
    _write_agent(factory_root, "outside-agent", required_input="docs/result.md")
    _write_index_playbook(
        factory_root, "feature-addition", ("author-agent", "review-agent")
    )
    output_dir = tmp_path / "map"

    result = subprocess.run(
        [
            sys.executable,
            str(GENERATE),
            "--factory-root",
            str(factory_root),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    overview = (output_dir / "overview.svg").read_text()
    artifacts = (output_dir / "artifacts.svg").read_text()
    detail = (output_dir / "playbooks" / "feature-addition.svg").read_text()
    assert 'data-content="feature-addition"' in overview
    assert 'data-source="playbooks/feature-addition.md"' in overview
    assert 'data-content="docs/result.md"' in artifacts
    assert 'data-start="agent-author-agent"' in artifacts
    assert 'data-end="agent-review-agent"' in artifacts
    assert 'data-content="author-agent"' in detail
    assert 'data-content="review-agent"' in detail
    assert "outside-agent" not in detail


def test_check_detects_source_drift_without_rewriting_outputs(tmp_path: Path) -> None:
    factory_root = tmp_path / "factory"
    _write_agent(factory_root, "author-agent", output="docs/result.md")
    _write_agent(factory_root, "review-agent", required_input="docs/result.md")
    output_dir = tmp_path / "map"
    base_command = [
        sys.executable,
        str(GENERATE),
        "--factory-root",
        str(factory_root),
        "--output-dir",
        str(output_dir),
    ]

    generated = subprocess.run(
        base_command, capture_output=True, text=True, check=False
    )
    assert generated.returncode == 0, generated.stderr
    original = (output_dir / "factory-map.json").read_text()

    current = subprocess.run(
        [*base_command, "--check"], capture_output=True, text=True, check=False
    )
    assert current.returncode == 0, current.stderr

    _write_agent(factory_root, "author-agent", output="docs/changed.md")
    stale = subprocess.run(
        [*base_command, "--check"], capture_output=True, text=True, check=False
    )

    assert stale.returncode == 1
    assert "out of date: factory-map.json" in stale.stderr
    assert (output_dir / "factory-map.json").read_text() == original


def test_real_factory_inventory_is_complete_and_svgs_are_valid(tmp_path: Path) -> None:
    factory_root = REPO_ROOT / "packages" / "factory"
    output_dir = tmp_path / "map"

    result = subprocess.run(
        [
            sys.executable,
            str(GENERATE),
            "--factory-root",
            str(factory_root),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    index = yaml.safe_load((factory_root / "INDEX.yaml").read_text())
    factory_map = json.loads((output_dir / "factory-map.json").read_text())
    for collection in ("agents", "skills", "playbooks"):
        expected = {entry["name"] for entry in index[collection]}
        actual = {entry["name"] for entry in factory_map[collection]}
        assert actual == expected
    agent_names = {agent["name"] for agent in factory_map["agents"]}
    assert all(
        agent in agent_names
        for playbook in factory_map["playbooks"]
        for agent in playbook["agents"]
    )
    for svg_path in output_dir.rglob("*.svg"):
        ET.parse(svg_path)
