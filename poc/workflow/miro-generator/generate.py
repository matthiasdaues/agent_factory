#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Generate a source-derived Factory map for Miro renderers."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from itertools import pairwise
from pathlib import Path
from typing import Any

import yaml

PLACEHOLDER = re.compile(r"\{[^{}]+\}")


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    data = yaml.safe_load(text[4:end]) or {}
    if not isinstance(data, dict):
        return {}
    return data


def _inputs(inputs: object) -> list[dict[str, str]]:
    if not isinstance(inputs, dict):
        return []
    result: list[dict[str, str]] = []
    for entry in inputs.get("required") or []:
        if not isinstance(entry, dict):
            continue
        alternatives = entry.get("any_of")
        candidates = alternatives if isinstance(alternatives, list) else [entry]
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("path_pattern"):
                result.append(
                    {
                        "path_pattern": str(candidate["path_pattern"]),
                        "role": "required",
                    }
                )
    for pattern in inputs.get("context") or []:
        result.append({"path_pattern": str(pattern), "role": "context"})
    return result


def _outputs(outputs: object) -> list[str]:
    if isinstance(outputs, list):
        return [str(item) for item in outputs]
    if not isinstance(outputs, dict):
        return []
    return [
        str(entry["path_pattern"])
        for entry in outputs.get("declarations") or []
        if isinstance(entry, dict) and entry.get("path_pattern")
    ]


def _normalise_pattern(pattern: str) -> str:
    return PLACEHOLDER.sub("*", pattern)


def _has_magic(pattern: str) -> bool:
    return any(char in pattern for char in "*?[")


def _glob_regex(pattern: str) -> re.Pattern[str]:
    index = 0
    parts = ["^"]
    while index < len(pattern):
        if pattern.startswith("**/", index):
            parts.append("(?:.*/)?")
            index += 3
        elif pattern.startswith("**", index):
            parts.append(".*")
            index += 2
        elif pattern[index] == "*":
            parts.append("[^/]*")
            index += 1
        elif pattern[index] == "?":
            parts.append("[^/]")
            index += 1
        else:
            parts.append(re.escape(pattern[index]))
            index += 1
    parts.append("$")
    return re.compile("".join(parts))


def _glob_bounds(pattern: str) -> tuple[str, str]:
    first = min((pattern.find(char) for char in "*?[" if char in pattern), default=-1)
    last = max((pattern.rfind(char) for char in "*?]"), default=-1)
    if first < 0:
        return pattern, pattern
    return pattern[:first], pattern[last + 1 :]


def _match_kind(output_pattern: str, input_pattern: str) -> str | None:
    output_pattern = _normalise_pattern(output_pattern)
    input_pattern = _normalise_pattern(input_pattern)
    if output_pattern == input_pattern:
        return "exact"
    output_magic = _has_magic(output_pattern)
    input_magic = _has_magic(input_pattern)
    if not output_magic:
        return "certain" if _glob_regex(input_pattern).match(output_pattern) else None
    if not input_magic:
        return "certain" if _glob_regex(output_pattern).match(input_pattern) else None
    output_prefix, output_suffix = _glob_bounds(output_pattern)
    input_prefix, input_suffix = _glob_bounds(input_pattern)
    prefixes_overlap = output_prefix.startswith(
        input_prefix
    ) or input_prefix.startswith(output_prefix)
    suffixes_overlap = output_suffix.endswith(input_suffix) or input_suffix.endswith(
        output_suffix
    )
    return "possible" if prefixes_overlap and suffixes_overlap else None


def _load_agents(factory_root: Path) -> list[dict[str, object]]:
    agents: list[dict[str, object]] = []
    for path in sorted((factory_root / "agents").glob("*.md")):
        data = _frontmatter(path)
        name = data.get("name")
        if not name:
            continue
        agents.append(
            {
                "name": str(name),
                "source": path.relative_to(factory_root).as_posix(),
                "inputs": _inputs(data.get("inputs")),
                "outputs": _outputs(data.get("outputs")),
                "skills": sorted(str(skill) for skill in data.get("skills") or []),
            }
        )
    return agents


def _load_skills(factory_root: Path) -> list[dict[str, object]]:
    skills: list[dict[str, object]] = []
    for path in sorted((factory_root / "skills").glob("*/SKILL.md")):
        data = _frontmatter(path)
        name = data.get("name")
        if not name:
            continue
        skills.append(
            {
                "name": str(name),
                "source": path.relative_to(factory_root).as_posix(),
                "inputs": _inputs(data.get("inputs")),
                "outputs": _outputs(data.get("outputs")),
            }
        )
    return skills


def _appears_in_order(sequence: list[str], producer: str, consumer: str) -> bool:
    return any(
        left < right
        for left, left_name in enumerate(sequence)
        for right, right_name in enumerate(sequence)
        if left_name == producer and right_name == consumer
    )


def _load_playbooks(
    factory_root: Path, relationships: list[dict[str, str]]
) -> list[dict[str, object]]:
    index_path = factory_root / "INDEX.yaml"
    if not index_path.exists():
        return []
    index = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    playbooks: list[dict[str, object]] = []
    for entry in index.get("playbooks") or []:
        if not isinstance(entry, dict) or not entry.get("name"):
            continue
        sequence = [str(agent) for agent in entry.get("agents") or []]
        route_relationships = []
        for relationship in relationships:
            if not _appears_in_order(
                sequence, relationship["producer"], relationship["consumer"]
            ):
                continue
            route_relationships.append(
                {
                    key: relationship[key]
                    for key in (
                        "consumer",
                        "match",
                        "producer",
                        "via_input",
                        "via_output",
                    )
                }
            )
        source = str(entry.get("path") or f"playbooks/{entry['name']}.md")
        playbook: dict[str, object] = {
            "name": str(entry["name"]),
            "source": source,
            "agents": sequence,
            "relationships": route_relationships,
        }
        source_path = factory_root / source
        raw_steps = (
            _frontmatter(source_path).get("steps") if source_path.exists() else None
        )
        if isinstance(raw_steps, list):
            steps = [
                {
                    "name": str(step["name"]),
                    "inputs": [str(pattern) for pattern in step.get("inputs") or []],
                    "outputs": [str(pattern) for pattern in step.get("outputs") or []],
                }
                for step in raw_steps
                if isinstance(step, dict) and step.get("name")
            ]
            step_relationships = []
            for producer_index, producer in enumerate(steps):
                for consumer in steps[producer_index + 1 :]:
                    for output_pattern in producer["outputs"]:
                        for input_pattern in consumer["inputs"]:
                            match_kind = _match_kind(output_pattern, input_pattern)
                            if match_kind is None:
                                continue
                            step_relationships.append(
                                {
                                    "consumer": consumer["name"],
                                    "match": match_kind,
                                    "producer": producer["name"],
                                    "via_input": input_pattern,
                                    "via_output": output_pattern,
                                }
                            )
            playbook["steps"] = steps
            playbook["step_relationships"] = step_relationships
        playbooks.append(playbook)
    return sorted(playbooks, key=lambda item: item["name"])


def build_factory_map(factory_root: Path) -> dict[str, object]:
    agents = _load_agents(factory_root)
    skills = _load_skills(factory_root)
    skills_by_name = {skill["name"]: skill for skill in skills}
    skill_bindings: list[dict[str, str]] = []
    unresolved_skill_references: list[dict[str, str]] = []
    for agent in agents:
        for skill_name in agent["skills"]:
            skill = skills_by_name.get(skill_name)
            if skill is None:
                unresolved_skill_references.append(
                    {
                        "agent": agent["name"],
                        "agent_source": agent["source"],
                        "skill": skill_name,
                    }
                )
                continue
            skill_bindings.append(
                {
                    "agent": agent["name"],
                    "agent_source": agent["source"],
                    "skill": skill_name,
                    "skill_source": skill["source"],
                }
            )
    relationships: list[dict[str, str]] = []
    for producer in agents:
        for consumer in agents:
            if producer["name"] == consumer["name"]:
                continue
            for output_pattern in producer["outputs"]:
                for input_decl in consumer["inputs"]:
                    input_pattern = input_decl["path_pattern"]
                    match_kind = _match_kind(output_pattern, input_pattern)
                    if match_kind is None:
                        continue
                    relationships.append(
                        {
                            "consumer": consumer["name"],
                            "consumer_source": consumer["source"],
                            "input_role": input_decl["role"],
                            "match": match_kind,
                            "producer": producer["name"],
                            "producer_source": producer["source"],
                            "via_input": input_pattern,
                            "via_output": output_pattern,
                        }
                    )
    relationships.sort(
        key=lambda item: (
            item["producer"],
            item["consumer"],
            item["via_output"],
            item["via_input"],
        )
    )
    components = [{**agent, "kind": "agent"} for agent in agents] + [
        {**skill, "kind": "skill"} for skill in skills
    ]
    skill_relationships: list[dict[str, str]] = []
    for producer in components:
        for consumer in components:
            if producer["kind"] == consumer["kind"] == "agent":
                continue
            if (
                producer["kind"] == consumer["kind"]
                and producer["name"] == consumer["name"]
            ):
                continue
            for output_pattern in producer["outputs"]:
                for input_decl in consumer["inputs"]:
                    input_pattern = input_decl["path_pattern"]
                    match_kind = _match_kind(output_pattern, input_pattern)
                    if match_kind is None:
                        continue
                    skill_relationships.append(
                        {
                            "consumer": consumer["name"],
                            "consumer_kind": consumer["kind"],
                            "consumer_source": consumer["source"],
                            "input_role": input_decl["role"],
                            "match": match_kind,
                            "producer": producer["name"],
                            "producer_kind": producer["kind"],
                            "producer_source": producer["source"],
                            "via_input": input_pattern,
                            "via_output": output_pattern,
                        }
                    )
    skill_relationships.sort(
        key=lambda item: (
            item["producer_kind"],
            item["producer"],
            item["consumer_kind"],
            item["consumer"],
            item["via_output"],
            item["via_input"],
        )
    )
    broad_patterns = []
    for component in components:
        for input_decl in component["inputs"]:
            if "**" in input_decl["path_pattern"]:
                broad_patterns.append(
                    {
                        "component": component["name"],
                        "kind": component["kind"],
                        "pattern": input_decl["path_pattern"],
                        "role": input_decl["role"],
                        "source": component["source"],
                    }
                )
        for output_pattern in component["outputs"]:
            if "**" in output_pattern:
                broad_patterns.append(
                    {
                        "component": component["name"],
                        "kind": component["kind"],
                        "pattern": output_pattern,
                        "role": "output",
                        "source": component["source"],
                    }
                )
    broad_patterns.sort(
        key=lambda item: (
            item["kind"],
            item["component"],
            item["role"],
            item["pattern"],
        )
    )
    possible_relationships = [
        {
            "consumer": relationship["consumer"],
            "consumer_kind": "agent",
            "producer": relationship["producer"],
            "producer_kind": "agent",
            "via_input": relationship["via_input"],
            "via_output": relationship["via_output"],
        }
        for relationship in relationships
        if relationship["match"] == "possible"
    ] + [
        {
            key: relationship[key]
            for key in (
                "consumer",
                "consumer_kind",
                "producer",
                "producer_kind",
                "via_input",
                "via_output",
            )
        }
        for relationship in skill_relationships
        if relationship["match"] == "possible"
    ]
    possible_relationships.sort(
        key=lambda item: (
            item["producer_kind"],
            item["producer"],
            item["consumer_kind"],
            item["consumer"],
            item["via_output"],
            item["via_input"],
        )
    )
    all_relationships = [
        {
            **relationship,
            "producer_kind": "agent",
            "consumer_kind": "agent",
        }
        for relationship in relationships
    ] + skill_relationships
    matched_outputs = {
        (
            relationship["producer_kind"],
            relationship["producer"],
            relationship["via_output"],
        )
        for relationship in all_relationships
    }
    matched_inputs = {
        (
            relationship["consumer_kind"],
            relationship["consumer"],
            relationship["via_input"],
        )
        for relationship in all_relationships
    }
    unmatched_outputs = [
        {
            "component": component["name"],
            "kind": component["kind"],
            "pattern": pattern,
            "source": component["source"],
        }
        for component in components
        for pattern in component["outputs"]
        if (component["kind"], component["name"], pattern) not in matched_outputs
    ]
    unmatched_inputs = [
        {
            "component": component["name"],
            "kind": component["kind"],
            "pattern": input_decl["path_pattern"],
            "role": input_decl["role"],
            "source": component["source"],
        }
        for component in components
        for input_decl in component["inputs"]
        if (
            component["kind"],
            component["name"],
            input_decl["path_pattern"],
        )
        not in matched_inputs
    ]
    unmatched_outputs.sort(
        key=lambda item: (item["kind"], item["component"], item["pattern"])
    )
    unmatched_inputs.sort(
        key=lambda item: (
            item["kind"],
            item["component"],
            item["role"],
            item["pattern"],
        )
    )
    playbooks = _load_playbooks(factory_root, relationships)
    return {
        "schema_version": 1,
        "agents": agents,
        "skills": skills,
        "skill_bindings": skill_bindings,
        "skill_relationships": skill_relationships,
        "relationships": relationships,
        "playbooks": playbooks,
        "diagnostics": {
            "missing_skill_contracts": [
                {"skill": skill["name"], "source": skill["source"]}
                for skill in skills
                if not skill["inputs"] and not skill["outputs"]
            ],
            "unresolved_skill_references": unresolved_skill_references,
            "broad_patterns": broad_patterns,
            "possible_relationships": possible_relationships,
            "unmatched_inputs": unmatched_inputs,
            "unmatched_outputs": unmatched_outputs,
        },
    }


def _attr(value: object) -> str:
    return html.escape(str(value), quote=True)


def _svg(elements: list[str], *, width: int, height: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}">\n' + "\n".join(elements) + "\n</svg>\n"
    )


def _render_overview(factory_map: dict[str, object]) -> str:
    elements = [
        (
            '<text x="40" y="60" font-family="noto_sans" font-size="36" '
            'font-weight="bold">Factory playbooks</text>'
        )
    ]
    for index, playbook in enumerate(factory_map["playbooks"]):
        y = 100 + index * 130
        elements.append(
            f'<rect id="playbook-{_attr(playbook["name"])}" x="40" y="{y}" '
            'width="520" height="90" rx="16" fill="#f4f2fd" '
            'stroke="#6631d7" stroke-width="2" '
            f'data-content="{_attr(playbook["name"])}" '
            f'data-source="{_attr(playbook["source"])}" />'
        )
    height = max(240, 130 * len(factory_map["playbooks"]) + 100)
    return _svg(elements, width=640, height=height)


def _artifact_id(pattern: str) -> str:
    digest = hashlib.sha1(pattern.encode("utf-8")).hexdigest()[:12]
    return f"artifact-{digest}"


def _render_artifacts(factory_map: dict[str, object]) -> str:
    agents = factory_map["agents"]
    contract_skills = [
        skill for skill in factory_map["skills"] if skill["inputs"] or skill["outputs"]
    ]
    relationships = [
        {
            **relationship,
            "producer_kind": "agent",
            "consumer_kind": "agent",
        }
        for relationship in factory_map["relationships"]
    ] + list(factory_map["skill_relationships"])
    elements = [
        (
            '<text x="40" y="60" font-family="noto_sans" font-size="36" '
            'font-weight="bold">Factory artifact flow</text>'
        )
    ]
    node_y = {}
    nodes = [
        {**agent, "kind": "agent", "fill": "#f0f5fd", "stroke": "#305bab"}
        for agent in agents
    ] + [
        {**skill, "kind": "skill", "fill": "#f4f2fd", "stroke": "#6631d7"}
        for skill in contract_skills
    ]
    for index, node in enumerate(nodes):
        y = 100 + index * 110
        node_id = f"{node['kind']}-{node['name']}"
        node_y[node_id] = y
        elements.append(
            f'<rect id="{_attr(node_id)}" x="40" y="{y}" '
            f'width="360" height="76" rx="12" fill="{node["fill"]}" '
            f'stroke="{node["stroke"]}" stroke-width="2" '
            f'data-content="{_attr(node["name"])}" '
            f'data-source="{_attr(node["source"])}" />'
        )
    artifact_patterns = sorted(
        {_normalise_pattern(pattern) for node in nodes for pattern in node["outputs"]}
        | {
            _normalise_pattern(input_decl["path_pattern"])
            for node in nodes
            for input_decl in node["inputs"]
        }
    )
    artifact_y = {}
    for index, pattern in enumerate(artifact_patterns):
        y = 100 + index * 110
        artifact_y[pattern] = y
        elements.append(
            f'<rect id="{_artifact_id(pattern)}" x="620" y="{y}" '
            'width="460" height="76" rx="12" fill="#f7f7f7" '
            'stroke="#595959" stroke-width="2" '
            f'data-content="{_attr(pattern)}" />'
        )
    for relationship in relationships:
        pattern = _normalise_pattern(relationship["via_output"])
        artifact = _artifact_id(pattern)
        producer = f"{relationship['producer_kind']}-{relationship['producer']}"
        consumer = f"{relationship['consumer_kind']}-{relationship['consumer']}"
        elements.append(
            f'<line x1="400" y1="{node_y[producer] + 38}" '
            f'x2="620" y2="{artifact_y[pattern] + 38}" stroke="#313131" '
            'stroke-width="2" data-arrow="end" data-shape="elbowed" '
            f'data-start="{_attr(producer)}" data-end="{artifact}" />'
        )
        dash = ' stroke-dasharray="5,5"' if relationship["match"] == "possible" else ""
        elements.append(
            f'<line x1="620" y1="{artifact_y[pattern] + 38}" '
            f'x2="400" y2="{node_y[consumer] + 38}" '
            'stroke="#313131" stroke-width="2" data-arrow="end" '
            f'data-shape="elbowed" data-start="{artifact}" '
            f'data-end="{_attr(consumer)}"{dash} />'
        )
    height = max(240, 110 * max(len(nodes), len(artifact_patterns)) + 100)
    return _svg(elements, width=1160, height=height)


def _render_playbook(
    playbook: dict[str, object], agents_by_name: dict[str, dict[str, object]]
) -> str:
    elements = [
        (
            f'<text x="40" y="60" font-family="noto_sans" font-size="36" '
            f'font-weight="bold">{_attr(playbook["name"])}</text>'
        )
    ]
    occurrences = [
        (step["name"], playbook["source"]) for step in playbook.get("steps", [])
    ] or [
        (agent_name, agents_by_name.get(agent_name, {}).get("source", ""))
        for agent_name in playbook["agents"]
    ]
    occurrence_ids = []
    for index, (label, source) in enumerate(occurrences):
        node_id = f"step-{index}-{label}"
        occurrence_ids.append(node_id)
        y = 100 + index * 130
        elements.append(
            f'<rect id="{_attr(node_id)}" x="40" y="{y}" width="440" '
            'height="84" rx="12" fill="#f0f5fd" stroke="#305bab" '
            f'stroke-width="2" data-content="{_attr(label)}" '
            f'data-source="{_attr(source)}" />'
        )
    for index, (start, end) in enumerate(pairwise(occurrence_ids)):
        y1 = 184 + index * 130
        y2 = 230 + index * 130
        elements.append(
            f'<line x1="260" y1="{y1}" x2="260" y2="{y2}" '
            'stroke="#313131" stroke-width="2" data-arrow="end" '
            f'data-start="{_attr(start)}" data-end="{_attr(end)}" />'
        )
    occurrence_by_label = {
        label: (occurrence_ids[index], 142 + index * 130)
        for index, (label, _source) in enumerate(occurrences)
    }
    for relationship in playbook.get("step_relationships", []):
        producer = occurrence_by_label.get(relationship["producer"])
        consumer = occurrence_by_label.get(relationship["consumer"])
        if producer is None or consumer is None:
            continue
        dash = ' stroke-dasharray="5,5"' if relationship["match"] == "possible" else ""
        elements.append(
            f'<line x1="480" y1="{producer[1]}" x2="480" y2="{consumer[1]}" '
            'stroke="#6631d7" stroke-width="2" data-arrow="end" '
            f'data-shape="elbowed" data-start="{_attr(producer[0])}" '
            f'data-end="{_attr(consumer[0])}" '
            f'data-content="{_attr(relationship["via_output"])}"{dash} />'
        )
    height = max(240, 130 * len(occurrence_ids) + 100)
    return _svg(elements, width=560, height=height)


def _rendered_files(factory_root: Path) -> dict[str, str]:
    factory_map = build_factory_map(factory_root)
    diagnostics = factory_map.pop("diagnostics")
    files = {
        "factory-map.json": json.dumps(factory_map, indent=2, sort_keys=True) + "\n",
        "factory-map-diagnostics.json": json.dumps(
            diagnostics, indent=2, sort_keys=True
        )
        + "\n",
        "overview.svg": _render_overview(factory_map),
        "artifacts.svg": _render_artifacts(factory_map),
    }
    agents_by_name = {agent["name"]: agent for agent in factory_map["agents"]}
    for playbook in factory_map["playbooks"]:
        files[f"playbooks/{playbook['name']}.svg"] = _render_playbook(
            playbook, agents_by_name
        )
    files["generation-manifest.json"] = (
        json.dumps({"files": sorted(files)}, indent=2, sort_keys=True) + "\n"
    )
    return files


def generate(factory_root: Path, output_dir: Path) -> None:
    files = _rendered_files(factory_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    for relative_path, content in files.items():
        target = output_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def check(factory_root: Path, output_dir: Path) -> list[str]:
    expected = _rendered_files(factory_root)
    stale = [
        relative_path
        for relative_path, content in expected.items()
        if not (output_dir / relative_path).exists()
        or (output_dir / relative_path).read_text(encoding="utf-8") != content
    ]
    manifest_path = output_dir / "generation-manifest.json"
    if manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8"))["files"]
        except (KeyError, TypeError, json.JSONDecodeError):
            previous = []
        stale.extend(path for path in previous if path not in expected)
    return sorted(set(stale))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--factory-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    factory_root = args.factory_root.resolve()
    output_dir = args.output_dir.resolve()
    if args.check:
        stale = check(factory_root, output_dir)
        for path in stale:
            print(f"out of date: {path}", file=sys.stderr)
        return 1 if stale else 0
    generate(factory_root, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
