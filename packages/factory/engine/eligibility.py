"""Precondition evaluator — checks agent inputs against the repository.

Reads `inputs.required` declarations from agent definitions, resolves
each path pattern against the filesystem, and returns per-agent,
per-requirement evidence marking each input satisfied or unsatisfied.
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
    candidates: list[str], workstream_id: str | None,
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
        script_path = Path("factory/scripts") / validator_name
        if not script_path.exists():
            warnings.append(f"validator '{validator_name}' not found at {script_path}")
            return "fail"
        try:
            result = subprocess.run(
                [str(script_path), "--check", path],
                capture_output=True, text=True, timeout=30,
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
    req: dict, workstream_id: str | None, warnings: list[str],
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


def evaluate_agent(
    agent: dict, workstream_id: str | None = None,
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
        _evaluate_requirement(req, workstream_id, warnings)
        for req in required
    ]
    eligible = all(r["satisfied"] for r in requirements)

    return {
        "agent_name": name,
        "eligible": eligible,
        "requirements": requirements,
        "warnings": warnings,
    }


def evaluate_all(
    agents: list[dict], workstream_id: str | None = None,
) -> list[dict]:
    return [evaluate_agent(a, workstream_id) for a in agents]
