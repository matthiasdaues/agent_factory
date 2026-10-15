"""Tests for session binding — attaching sessions to workstreams."""

from __future__ import annotations

import pytest
import yaml
from engine.session_binding import (
    BindingValidationError,
    create_binding,
    load_binding,
    validate_binding,
)


@pytest.fixture()
def bind_dir(tmp_path):
    return tmp_path / "sessions"


def test_create_binding_with_workstream_id(bind_dir):
    path = create_binding("sess-001", "my-workstream", base_dir=bind_dir)
    assert path.exists()

    data = yaml.safe_load(path.read_text())
    assert data["session_id"] == "sess-001"
    assert data["workstream_id"] == "my-workstream"
    assert "bound_at" in data


def test_create_binding_with_null_workstream_id(bind_dir):
    path = create_binding("sess-open", None, base_dir=bind_dir)
    data = yaml.safe_load(path.read_text())
    assert data["session_id"] == "sess-open"
    assert data["workstream_id"] is None
    assert "bound_at" in data


def test_create_binding_missing_workstream_id_key_fails():
    with pytest.raises(BindingValidationError, match="workstream_id"):
        validate_binding({"session_id": "sess-bad", "bound_at": "2026-01-01T00:00:00"})


def test_load_binding_valid(bind_dir):
    create_binding("sess-load", "ws-1", base_dir=bind_dir)
    data = load_binding("sess-load", base_dir=bind_dir)
    assert data["session_id"] == "sess-load"
    assert data["workstream_id"] == "ws-1"
    assert "bound_at" in data


def test_validate_binding_missing_key_fails():
    with pytest.raises(BindingValidationError, match="session_id"):
        validate_binding({"workstream_id": "x", "bound_at": "2026-01-01T00:00:00"})

    with pytest.raises(BindingValidationError, match="bound_at"):
        validate_binding({"session_id": "s", "workstream_id": "x"})


def test_load_binding_not_found(bind_dir):
    bind_dir.mkdir(parents=True, exist_ok=True)
    with pytest.raises(Exception, match="not found"):
        load_binding("nonexistent", base_dir=bind_dir)
