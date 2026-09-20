"""Tests for workstream state v2 — immutable identity records."""

from __future__ import annotations

import pytest
import yaml

from engine.workstream import (
    SCHEMA_VERSION,
    WorkstreamExistsError,
    WorkstreamValidationError,
    create_workstream,
    list_workstreams,
    load_workstream,
)


@pytest.fixture()
def ws_dir(tmp_path):
    return tmp_path / "workstreams"


def test_create_workstream_writes_four_fields(ws_dir):
    path = create_workstream(
        "my-stream", "My Topic", "docs/proposals/my-stream.md", base_dir=ws_dir
    )
    assert path.exists()

    data = yaml.safe_load(path.read_text())
    assert set(data.keys()) == {"schema_version", "workstream_id", "topic", "origin_ref"}
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["workstream_id"] == "my-stream"
    assert data["topic"] == "My Topic"
    assert data["origin_ref"] == "docs/proposals/my-stream.md"


def test_create_workstream_raises_on_existing(ws_dir):
    create_workstream("dup", "Topic", None, base_dir=ws_dir)
    with pytest.raises(WorkstreamExistsError, match="immutable"):
        create_workstream("dup", "Topic Changed", None, base_dir=ws_dir)


def test_load_workstream_valid(ws_dir):
    create_workstream("load-me", "Load Topic", "ref.md", base_dir=ws_dir)
    data = load_workstream("load-me", base_dir=ws_dir)
    assert data["workstream_id"] == "load-me"
    assert data["topic"] == "Load Topic"
    assert data["origin_ref"] == "ref.md"
    assert data["schema_version"] == SCHEMA_VERSION


def test_load_workstream_rejects_extra_fields(ws_dir):
    ws_dir.mkdir(parents=True, exist_ok=True)
    state_file = ws_dir / "bad.yaml"
    state_file.write_text(yaml.safe_dump({
        "schema_version": SCHEMA_VERSION,
        "workstream_id": "bad",
        "topic": "Bad",
        "origin_ref": None,
        "extra_field": "not allowed",
    }))

    with pytest.raises(WorkstreamValidationError, match="unexpected fields"):
        load_workstream("bad", base_dir=ws_dir)


def test_list_workstreams_returns_all(ws_dir):
    create_workstream("alpha", "Alpha", None, base_dir=ws_dir)
    create_workstream("beta", "Beta", "ref.md", base_dir=ws_dir)

    results = list_workstreams(base_dir=ws_dir)
    ids = [w["workstream_id"] for w in results]
    assert sorted(ids) == ["alpha", "beta"]


def test_list_workstreams_empty_dir(ws_dir):
    assert list_workstreams(base_dir=ws_dir) == []


def test_load_workstream_not_found(ws_dir):
    ws_dir.mkdir(parents=True, exist_ok=True)
    with pytest.raises(Exception, match="not found"):
        load_workstream("nonexistent", base_dir=ws_dir)
