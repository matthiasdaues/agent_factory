"""Session bindings — attach sessions to workstreams.

A session binding records session_id, workstream_id, and bound_at.
The workstream_id key must always be present: a known identifier means
bound, explicit null means Open Stage, a missing key is invalid.
"""

from __future__ import annotations

import datetime
import os
import tempfile
from pathlib import Path

import yaml

DEFAULT_BASE_DIR = ".agent-factory/workstreams/sessions"


class BindingError(Exception):
    pass


class BindingValidationError(BindingError):
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


def create_binding(
    session_id: str,
    workstream_id: str | None,
    base_dir: str | Path = DEFAULT_BASE_DIR,
) -> Path:
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)

    binding = {
        "session_id": session_id,
        "workstream_id": workstream_id,
        "bound_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    binding_path = base / f"{session_id}.yaml"
    _atomic_write(
        binding_path,
        yaml.safe_dump(
            binding, default_flow_style=False, sort_keys=False, allow_unicode=True
        ),
    )
    return binding_path


def load_binding(
    session_id: str,
    base_dir: str | Path = DEFAULT_BASE_DIR,
) -> dict:
    binding_path = Path(base_dir) / f"{session_id}.yaml"
    if not binding_path.exists():
        raise BindingError(f"binding for session '{session_id}' not found")

    data = yaml.safe_load(binding_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise BindingValidationError("binding file is not a YAML mapping")

    validate_binding(data)
    return data


def validate_binding(data: dict) -> None:
    if "session_id" not in data:
        raise BindingValidationError("missing required field: session_id")

    if "workstream_id" not in data:
        raise BindingValidationError(
            "missing required field: workstream_id "
            "(must be present — use null for Open Stage)"
        )

    if "bound_at" not in data:
        raise BindingValidationError("missing required field: bound_at")
