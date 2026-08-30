"""Acceptance tests for fresh Factory phase sessions (ST-0066).

The tests inspect the canonical playbook and agent surfaces that every
supported CLI installs. They trace UC-11 and BR-039--BR-041 without coupling to
one CLI adapter or replaying a prior transcript.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_PLAYBOOKS = {
    "greenfield-development": _ROOT / "factory/playbooks/greenfield-development.md",
    "feature-addition": _ROOT / "factory/playbooks/feature-addition.md",
}
_AGENTS = tuple(
    _ROOT / "factory/agents" / name
    for name in (
        "requirements-agent.md",
        "architecture-agent.md",
        "spec-review-agent.md",
        "architecture-review-agent.md",
        "qa-agent.md",
        "reconciliation-agent.md",
        "implementation-agent.md",
        "developer-agent.md",
    )
)

_GREENFIELD_TRANSITIONS = (
    "requirements-agent → spec-review-agent",
    "spec-review-agent → requirements-agent",
    "spec-review-agent → architecture-agent",
    "architecture-agent → architecture-review-agent",
    "architecture-review-agent → architecture-agent",
    "architecture-review-agent → planning-agent",
    "planning-agent → implementation-agent",
    "implementation-agent → reconciliation-agent",
    "reconciliation-agent → implementation-agent",
    "reconciliation-agent → qa-agent",
    "qa-agent → implementation-agent",
    "implementation-agent → qa-agent",
)
_FEATURE_TRANSITIONS = (
    "proposal intake → requirements-agent",
    "proposal intake → architecture-agent",
    "proposal intake → planning-agent",
    "requirements-agent → spec-review-agent",
    "spec-review-agent → requirements-agent",
    "spec-review-agent → architecture-agent",
    "spec-review-agent → planning-agent",
    "architecture-agent → architecture-review-agent",
    "architecture-review-agent → architecture-agent",
    "architecture-review-agent → planning-agent",
    "planning-agent → implementation-agent",
    "implementation-agent → reconciliation-agent",
    "reconciliation-agent → implementation-agent",
    "reconciliation-agent → qa-agent",
    "qa-agent → implementation-agent",
    "implementation-agent → qa-agent",
)


def _normalized(path: Path) -> str:
    """Return case-insensitive prose with Markdown wrapping made irrelevant."""
    return re.sub(r"\s+", " ", path.read_text().lower())


@pytest.mark.parametrize("playbook", _PLAYBOOKS.values(), ids=_PLAYBOOKS)
def test_UC_11_playbook_phase_boundary_is_reviewed_hard_stop(playbook: Path):
    """Every multi-phase playbook defines one non-negotiable restart gate."""
    contract = _normalized(playbook)

    for required in (
        "phase boundary contract",
        "invoke `handoff`",
        "handoff-lint",
        "semantic review",
        "hard stop",
        "fresh session",
        "read the handoff first",
        "bounded chunk",
        "on demand",
        "prior transcript",
    ):
        assert required in contract


@pytest.mark.parametrize(
    ("playbook", "transitions"),
    (
        (_PLAYBOOKS["greenfield-development"], _GREENFIELD_TRANSITIONS),
        (_PLAYBOOKS["feature-addition"], _FEATURE_TRANSITIONS),
    ),
    ids=("greenfield-development", "feature-addition"),
)
def test_UC_11_playbook_marks_every_routed_transition(
    playbook: Path, transitions: tuple[str, ...]
):
    """Forward, skip, review, remedy, reconciliation, and QA routes are named."""
    contract = _normalized(playbook)

    for transition in transitions:
        assert transition in contract


@pytest.mark.parametrize("agent", _AGENTS, ids=lambda path: path.stem)
def test_UC_11_agent_declares_handoff_skill(agent: Path):
    """Every participating agent can invoke the canonical handoff operation."""
    contract = agent.read_text()
    skills = re.search(r"^skills:(?: \[\])?\n((?:  - .+\n)*)", contract, re.MULTILINE)

    assert skills is not None
    assert "  - handoff\n" in skills.group(1)


@pytest.mark.parametrize("agent", _AGENTS, ids=lambda path: path.stem)
def test_UC_11_agent_enters_fresh_session_from_bounded_durable_context(agent: Path):
    """BR-039/041 prohibit transcript replay and eager large-file injection."""
    contract = _normalized(agent)

    for required in (
        "## phase entry",
        "fresh session",
        "read the handoff first",
        "referenced artifacts",
        "bounded chunk",
        "on demand",
        "prior transcript",
    ):
        assert required in contract


@pytest.mark.parametrize("agent", _AGENTS, ids=lambda path: path.stem)
def test_UC_11_agent_exits_through_reviewed_handoff_and_stops(agent: Path):
    """Cross-phase work cannot continue in the outgoing agent session."""
    contract = _normalized(agent)

    for required in (
        "## phase exit",
        "invoke `handoff`",
        "handoff-lint",
        "semantic review",
        "stop",
        "same phase",
    ):
        assert required in contract


@pytest.mark.parametrize("agent", _AGENTS, ids=lambda path: path.stem)
def test_UC_11_child_return_persists_detail_and_bounds_parent_envelope(agent: Path):
    """BR-040 stores complete child work while keeping parent context bounded."""
    contract = _normalized(agent)

    for required in (
        "## child return",
        "canonical tracked",
        "disposition",
        "severity counts",
        "every artifact path",
        "one-to-three-sentence next action",
        "verbatim finding detail",
        "full reasoning",
    ):
        assert required in contract


@pytest.mark.parametrize("agent", _AGENTS, ids=lambda path: path.stem)
def test_UC_11_agent_preserves_cache_and_compaction_exclusions(agent: Path):
    """The accepted proposal adds no in-session compaction or cache ritual."""
    contract = _normalized(agent)

    assert "no in-place transcript compaction" in contract
    assert "no prose-only cache-restabilisation" in contract
