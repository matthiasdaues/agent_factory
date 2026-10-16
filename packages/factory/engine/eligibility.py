"""Precondition evaluator — checks agent inputs against the repository.

Reads `inputs.required` declarations from agent definitions, resolves
each path pattern against the filesystem, and returns per-agent,
per-requirement evidence marking each input satisfied or unsatisfied.

A required entry is either one input (`type`, `path_pattern`, optional
`conditions`) or an `any_of` list of such inputs. An `any_of` entry is
satisfied when at least one alternative is satisfied. A malformed `any_of`
is unmet, and the result carries a warning that names the problem.
"""

from __future__ import annotations

import glob
import re
import subprocess
from pathlib import Path

import yaml


def _read_frontmatter(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    if not text.startswith("---"):
        return None

    end = text.find("\n---", 3)
    if end == -1:
        return None

    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return None

    return data if isinstance(data, dict) else None


def _expand_pattern(path_pattern: str) -> str:
    return re.sub(r"\{[^}]+\}", "*", path_pattern)


def _extract_scope(path: Path) -> str | None:
    """Extract scope declaration from a file, handling all three formats."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    suffix = path.suffix.lower()

    if suffix == ".feature":
        first_line = text.split("\n", 1)[0].strip()
        m = re.match(r"^#\s*scope:\s*(.+)$", first_line)
        return m.group(1).strip() if m else None

    if suffix == ".dsl":
        first_line = text.split("\n", 1)[0].strip()
        m = re.match(r"^//\s*scope:\s*(.+)$", first_line)
        return m.group(1).strip() if m else None

    if suffix in (".yaml", ".yml") and not text.startswith("---"):
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            return None
        if isinstance(data, dict):
            return data.get("scope")
        return None

    fm = _read_frontmatter(path)
    if fm is not None:
        return fm.get("scope")

    return None


def _scope_filter(
    candidates: list[str],
    workstream_id: str | None,
) -> list[str]:
    if workstream_id is None:
        return candidates

    filtered = []
    for c in candidates:
        scope = _extract_scope(Path(c))
        if scope is None:
            filtered.append(c)
            continue
        if scope == workstream_id or scope == "global":
            filtered.append(c)
    return filtered


def _check_condition(path: str, condition: dict | None, warnings: list[str]) -> str:
    if condition is None:
        return "pass"

    if "check" in condition:
        validator_name = condition["check"]
        _fr = (
            Path(".agent-factory/factory/scripts")
            if Path(".agent-factory/factory").is_dir()
            else Path("factory/scripts")
        )
        script_path = _fr / validator_name
        if not script_path.exists():
            warnings.append(f"validator '{validator_name}' not found at {script_path}")
            return "fail"
        try:
            result = subprocess.run(
                [str(script_path), "--check", path],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            return "pass" if result.returncode == 0 else "fail"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            warnings.append(f"validator '{validator_name}' failed to execute")
            return "fail"

    field = condition.get("field")
    if not field:
        return "pass"

    fm = _read_frontmatter(Path(path))
    if fm is None:
        warnings.append(f"cannot read frontmatter from {path}")
        return "fail"

    actual = fm.get(field)

    if "value" in condition:
        expected = condition["value"]
        return "pass" if str(actual) == str(expected) else "fail"

    if "one_of" in condition:
        allowed = condition["one_of"]
        if isinstance(allowed, list):
            return "pass" if str(actual) in [str(v) for v in allowed] else "fail"
        return "fail"

    return "pass"


def _evaluate_requirement(
    req: dict,
    workstream_id: str | None,
    warnings: list[str],
) -> dict:
    req_type = req.get("type", "unknown")
    path_pattern = req.get("path_pattern", "")
    condition = req.get("conditions")

    glob_pattern = _expand_pattern(path_pattern)
    raw_candidates = sorted(glob.glob(glob_pattern, recursive=True))

    candidates = _scope_filter(raw_candidates, workstream_id)

    passing: list[str] = []
    for c in candidates:
        result = _check_condition(c, condition, warnings)
        if result == "pass":
            passing.append(c)

    evidence: dict = {
        "type": req_type,
        "path_pattern": path_pattern,
        "satisfied": len(passing) > 0,
        "candidates": passing,
    }
    if condition is not None:
        evidence["condition"] = condition
        evidence["condition_result"] = "pass" if passing else "fail"

    return evidence


def _any_of_problem(alternatives: object) -> str | None:
    """Name what is wrong with the shape of an `any_of` list, or None."""
    if not isinstance(alternatives, list) or not alternatives:
        return "is not a non-empty list"
    for alt in alternatives:
        if not isinstance(alt, dict):
            return "has an alternative that is not a mapping"
        path_pattern = alt.get("path_pattern")
        if not isinstance(path_pattern, str) or not path_pattern.strip():
            return "has an alternative without a path_pattern"
    return None


def _evaluate_any_of(
    alternatives: object,
    workstream_id: str | None,
    warnings: list[str],
) -> dict:
    problem = _any_of_problem(alternatives)
    if problem is not None:
        warnings.append(f"any_of {problem}; the requirement is treated as unmet")
        return {
            "type": "any_of",
            "path_pattern": "",
            "satisfied": False,
            "candidates": [],
            "alternatives": [],
        }
    evidence = [
        _evaluate_requirement(alt, workstream_id, warnings) for alt in alternatives
    ]
    candidates: list[str] = []
    for e in evidence:
        candidates.extend(e["candidates"])
    return {
        "type": " | ".join(e["type"] for e in evidence),
        "path_pattern": " | ".join(e["path_pattern"] for e in evidence),
        "satisfied": any(e["satisfied"] for e in evidence),
        "candidates": candidates,
        "alternatives": evidence,
    }


def _evaluate_entry(
    req: dict,
    workstream_id: str | None,
    warnings: list[str],
) -> dict:
    if "any_of" in req:
        return _evaluate_any_of(req["any_of"], workstream_id, warnings)
    return _evaluate_requirement(req, workstream_id, warnings)


def evaluate_agent(
    agent: dict,
    workstream_id: str | None = None,
) -> dict:
    name = agent.get("name", "unknown")
    inputs = agent.get("inputs", {})
    required = inputs.get("required", []) if isinstance(inputs, dict) else []

    if not required:
        return {
            "agent_name": name,
            "eligible": True,
            "requirements": [],
            "warnings": [],
        }

    warnings: list[str] = []
    requirements = [
        _evaluate_entry(req, workstream_id, warnings) for req in required
    ]
    eligible = all(r["satisfied"] for r in requirements)

    return {
        "agent_name": name,
        "eligible": eligible,
        "requirements": requirements,
        "warnings": warnings,
    }


def evaluate_all(
    agents: list[dict],
    workstream_id: str | None = None,
) -> list[dict]:
    return [evaluate_agent(a, workstream_id) for a in agents]
