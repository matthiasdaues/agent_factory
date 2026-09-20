"""Workstream state v2 — immutable identity records.

A workstream state file contains exactly four fields: schema_version,
workstream_id, topic, origin_ref.  The file is immutable after creation.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import yaml

SCHEMA_VERSION = 2
PERMITTED_FIELDS = frozenset({"schema_version", "workstream_id", "topic", "origin_ref"})
DEFAULT_BASE_DIR = ".agent-factory/workstreams"


class WorkstreamError(Exception):
    pass


class WorkstreamExistsError(WorkstreamError):
    pass


class WorkstreamValidationError(WorkstreamError):
    pass


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


def create_workstream(
    workstream_id: str,
    topic: str,
    origin_ref: str | None,
    base_dir: str | Path = DEFAULT_BASE_DIR,
) -> Path:
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)

    state_path = base / f"{workstream_id}.yaml"
    if state_path.exists():
        raise WorkstreamExistsError(
            f"workstream '{workstream_id}' already exists — state file is immutable"
        )

    state = {
        "schema_version": SCHEMA_VERSION,
        "workstream_id": workstream_id,
        "topic": topic,
        "origin_ref": origin_ref,
    }

    _atomic_write(
        state_path,
        yaml.safe_dump(state, default_flow_style=False, sort_keys=False),
    )
    return state_path


def load_workstream(
    workstream_id: str,
    base_dir: str | Path = DEFAULT_BASE_DIR,
) -> dict:
    state_path = Path(base_dir) / f"{workstream_id}.yaml"
    if not state_path.exists():
        raise WorkstreamError(f"workstream '{workstream_id}' not found")

    data = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise WorkstreamValidationError("state file is not a YAML mapping")

    _validate_fields(data)
    return data


def _validate_fields(data: dict) -> None:
    extra = set(data.keys()) - PERMITTED_FIELDS
    if extra:
        raise WorkstreamValidationError(
            f"unexpected fields in workstream state: {sorted(extra)}"
        )

    missing = PERMITTED_FIELDS - set(data.keys())
    if missing:
        raise WorkstreamValidationError(
            f"missing fields in workstream state: {sorted(missing)}"
        )

    if data["schema_version"] != SCHEMA_VERSION:
        raise WorkstreamValidationError(
            f"expected schema_version {SCHEMA_VERSION}, got {data['schema_version']}"
        )


def list_workstreams(base_dir: str | Path = DEFAULT_BASE_DIR) -> list[dict]:
    base = Path(base_dir)
    if not base.exists():
        return []

    results = []
    for path in sorted(base.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                _validate_fields(data)
                results.append(data)
        except (yaml.YAMLError, WorkstreamValidationError):
            continue
    return results
