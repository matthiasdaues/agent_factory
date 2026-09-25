"""Fence runner — deterministic output validation after agent activity.

Snapshots declared output patterns before an activity, compares against
post-activity filesystem state, runs applicable validators, and stores
evidence at .agent-factory/checks/fences/<session-id>/<invocation-id>.yaml.

Lifecycle: PENDING → CHECKING → PASSED | FAILED (terminal).
Fence failure is evidence, not a gate — it never blocks the developer.
"""

from __future__ import annotations

import datetime
import glob as glob_module
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class DeclarationResult:
    path_pattern: str
    required: bool
    validator: str | None
    pre_snapshot: dict[str, float]
    post_snapshot: dict[str, float]
    changed_files: list[str]
    validator_passed: bool | None
    status: str


@dataclass
class FenceResult:
    agent_name: str
    session_id: str
    invocation_id: str
    timestamp: str
    declarations: list[DeclarationResult]
    declarations_changed: int
    minimum_changed: int
    aggregate: str
    failure_reasons: list[str]
    warnings: list[str] = field(default_factory=list)


def _glob_pattern(path_pattern: str) -> list[str]:
    import re

    expanded = re.sub(r"\{[^}]+\}", "*", path_pattern)
    return sorted(glob_module.glob(expanded, recursive=True))


def _file_mtimes(paths: list[str]) -> dict[str, float]:
    result = {}
    for p in paths:
        try:
            result[p] = os.path.getmtime(p)
        except OSError:
            pass
    return result


def snapshot_outputs(agent_def: dict) -> dict[str, dict[str, float]]:
    """Snapshot current filesystem state for each output declaration."""
    outputs = agent_def.get("outputs", {})
    if not isinstance(outputs, dict):
        return {}

    declarations = outputs.get("declarations", [])
    snapshots: dict[str, dict[str, float]] = {}

    for decl in declarations:
        pattern = decl.get("path_pattern", "")
        if not pattern:
            continue
        matches = _glob_pattern(pattern)
        snapshots[pattern] = _file_mtimes(matches)

    return snapshots


def _find_changed(
    pattern: str,
    pre: dict[str, float],
    post: dict[str, float],
) -> list[str]:
    changed = []
    for path, mtime in post.items():
        if path not in pre or mtime > pre[path]:
            changed.append(path)
    return sorted(changed)


def _run_validator(
    validator_name: str,
    changed_files: list[str],
    warnings: list[str],
) -> bool:
    _fr = (
        Path(".agent-factory/factory/scripts")
        if Path(".agent-factory/factory").is_dir()
        else Path("factory/scripts")
    )
    script_path = _fr / validator_name
    if not script_path.exists():
        warnings.append(f"validator '{validator_name}' not found at {script_path}")
        return True

    for fpath in changed_files:
        try:
            result = subprocess.run(
                [str(script_path), "--check", fpath],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if result.returncode != 0:
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            warnings.append(
                f"validator '{validator_name}' failed to execute on {fpath}"
            )
            return False
    return True


def run_fence(
    agent_def: dict,
    pre_snapshot: dict[str, dict[str, float]],
    session_id: str,
    invocation_id: str,
) -> FenceResult:
    """Compare post-activity state against pre-snapshot, run validators, aggregate."""
    agent_name = agent_def.get("name", "unknown")
    outputs = agent_def.get("outputs", {})
    if not isinstance(outputs, dict):
        outputs = {}

    minimum_changed = outputs.get("minimum_changed", 0)
    declarations = outputs.get("declarations", [])
    warnings: list[str] = []
    failure_reasons: list[str] = []
    results: list[DeclarationResult] = []
    decls_changed = 0

    for decl in declarations:
        pattern = decl.get("path_pattern", "")
        required = decl.get("required", False)
        validator = decl.get("validator") or None

        post_matches = _glob_pattern(pattern)
        post_snap = _file_mtimes(post_matches)
        pre_snap = pre_snapshot.get(pattern, {})

        changed = _find_changed(pattern, pre_snap, post_snap)

        if required and not changed:
            status = "failed"
            failure_reasons.append(
                f"required output '{pattern}' has no created or modified match"
            )
            validator_passed = None
        elif not changed:
            status = "skipped"
            validator_passed = None
        else:
            decls_changed += 1
            if validator:
                validator_passed = _run_validator(validator, changed, warnings)
                if not validator_passed:
                    status = "failed"
                    failure_reasons.append(
                        f"validator '{validator}' failed on '{pattern}'"
                    )
                else:
                    status = "passed"
            else:
                validator_passed = None
                status = "passed"

        results.append(
            DeclarationResult(
                path_pattern=pattern,
                required=required,
                validator=validator,
                pre_snapshot=pre_snap,
                post_snapshot=post_snap,
                changed_files=changed,
                validator_passed=validator_passed,
                status=status,
            )
        )

    if decls_changed < minimum_changed:
        failure_reasons.append(
            f"declarations_changed ({decls_changed}) < minimum_changed ({minimum_changed})"
        )

    aggregate = "failed" if failure_reasons else "passed"

    return FenceResult(
        agent_name=agent_name,
        session_id=session_id,
        invocation_id=invocation_id,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        declarations=results,
        declarations_changed=decls_changed,
        minimum_changed=minimum_changed,
        aggregate=aggregate,
        failure_reasons=failure_reasons,
        warnings=warnings,
    )


def _atomic_write(path: Path, content: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    closed = False
    try:
        os.write(fd, content.encode())
        os.close(fd)
        closed = True
        os.replace(tmp, path)
    except BaseException:
        if not closed:
            os.close(fd)
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _result_to_dict(result: FenceResult) -> dict:
    decls = []
    for d in result.declarations:
        decls.append(
            {
                "path_pattern": d.path_pattern,
                "required": d.required,
                "validator": d.validator,
                "changed_files": d.changed_files,
                "validator_passed": d.validator_passed,
                "status": d.status,
            }
        )

    return {
        "agent_name": result.agent_name,
        "session_id": result.session_id,
        "invocation_id": result.invocation_id,
        "timestamp": result.timestamp,
        "aggregate": result.aggregate,
        "declarations_changed": result.declarations_changed,
        "minimum_changed": result.minimum_changed,
        "failure_reasons": result.failure_reasons,
        "warnings": result.warnings,
        "declarations": decls,
    }


def store_evidence(
    result: FenceResult,
    base_dir: str | Path = ".agent-factory/checks/fences",
) -> Path:
    """Store fence evidence YAML."""
    base = Path(base_dir) / result.session_id
    base.mkdir(parents=True, exist_ok=True)

    evidence_path = base / f"{result.invocation_id}.yaml"
    content = yaml.safe_dump(
        _result_to_dict(result),
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    _atomic_write(evidence_path, content)
    return evidence_path


def load_fence_evidence(
    session_id: str,
    base_dir: str | Path = ".agent-factory/checks/fences",
) -> list[dict]:
    """Load all fence evidence for a session."""
    session_dir = Path(base_dir) / session_id
    if not session_dir.exists():
        return []

    results = []
    for path in sorted(session_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                results.append(data)
        except (yaml.YAMLError, OSError):
            continue
    return results
