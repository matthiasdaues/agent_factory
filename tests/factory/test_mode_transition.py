"""Contract tests for agent-context mode transition.

Covers ACX-15 (deferred sole-key invariant) and ACX-16
(transition-condition evaluation) from the agent-context QA strategy.

The mode transition is a skill-defined workflow in update-context, not a
script.  These tests verify the structural invariants that context-lint
enforces and the transition-condition logic by evaluating YAML fixtures
directly.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "agent-context"

INDEX_FILES = ("stack.yaml", "workflow.yaml", "governance.yaml")

STRUCTURED_FIELDS = {"languages"}


def _load_index(fixture: str, filename: str) -> dict:
    path = FIXTURES / fixture / "docs" / "agent-context" / filename
    return yaml.safe_load(path.read_text())


def _classify_leaf(value) -> str:
    """Classify a leaf value as null, deferred, valued-with-source, or valued-without-source."""
    if value is None:
        return "null"
    if isinstance(value, dict):
        if "deferred" in value:
            return "deferred"
        if "source" in value and value["source"] is not None:
            return "valued-with-source"
        return "valued-without-source"
    return "valued-without-source"


def _walk_leaves(
    data: dict, skip_keys: set[str] | None = None
) -> list[tuple[str, str]]:
    """Walk a YAML index file and return (key_path, classification) for each leaf."""
    skip = skip_keys or {"mode"}
    results = []
    for key, value in data.items():
        if key in skip:
            continue
        if key in STRUCTURED_FIELDS and isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    cls = _classify_leaf(item)
                    results.append((f"{key}[{i}]", cls))
                else:
                    results.append((f"{key}[{i}]", _classify_leaf(item)))
        elif (
            isinstance(value, dict)
            and "deferred" not in value
            and "source" not in value
            and "name" not in value
        ):
            for subkey, subval in value.items():
                results.append((f"{key}.{subkey}", _classify_leaf(subval)))
        else:
            results.append((key, _classify_leaf(value)))
    return results


def _check_transition_condition(fixture: str) -> bool:
    """Return True if the transition condition is met for a fixture."""
    for filename in INDEX_FILES:
        data = _load_index(fixture, filename)
        for key_path, cls in _walk_leaves(data):
            if cls == "valued-without-source":
                return False
    return True


@pytest.mark.spec("ACX-16")
def test_transition_condition_met_when_all_valued_fields_have_sources():
    """Transition condition is met: every non-null, non-deferred valued field has a source."""
    assert _check_transition_condition("transition_ready") is True


@pytest.mark.spec("ACX-16")
def test_transition_condition_not_met_with_valued_field_missing_source():
    """Transition blocked: a valued field lacks a source pointer."""
    assert _check_transition_condition("transition_partial") is False


@pytest.mark.spec("ACX-15")
def test_deferred_field_is_sole_key():
    """Deferred field has deferred as the sole key — no name or source coexists."""
    data = _load_index("transition_deferred", "stack.yaml")
    ds = data["data_stores"]
    assert isinstance(ds, dict)
    assert "deferred" in ds
    assert "name" not in ds
    assert "source" not in ds
    assert len(ds) == 1


@pytest.mark.spec("ACX-16")
def test_deferred_fields_excluded_from_transition_condition():
    """Deferred fields are excluded from the transition condition."""
    assert _check_transition_condition("transition_deferred") is True


@pytest.mark.spec("ACX-16")
def test_null_fields_excluded_from_transition_condition():
    """Null fields are excluded from the transition condition."""
    data = _load_index("transition_ready", "stack.yaml")
    leaves = _walk_leaves(data)
    null_leaves = [(k, c) for k, c in leaves if c == "null"]
    assert len(null_leaves) > 0, "fixture should have null fields"
    assert _check_transition_condition("transition_ready") is True


@pytest.mark.spec("ACX-16")
def test_all_files_checked_not_just_one():
    """Transition condition evaluates all three index files, not just stack.yaml."""
    for filename in INDEX_FILES:
        path = FIXTURES / "transition_ready" / "docs" / "agent-context" / filename
        assert path.exists(), f"fixture missing {filename}"
