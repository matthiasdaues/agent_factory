"""mark-blocked in the gate-check step, when crap-score exits 2 (docs/spec/features/crap-gate-setup.feature, Rule CG-07),
and the refusal at the merge of a story that names crap-score without an entry (Rule CG-11, DEC-58).

Each test starts from the state of the Scenario: ST-0350 is dispatched with one counted attempt.
The run helpers come from the run-lifecycle tests, as in the other test_crap_gate_ files.
"""

from __future__ import annotations

import pytest

import dispatch_lib as lib
from test_run_lifecycle_dispatch import (
    AU,
    _dispatch,
    _dispatched_by_hand,
    _entry,
    _fail,
    _commit_story_work,
    _git,
    _orchestrated_on_login,
)

GATE_REASON = "gate cannot measure: crap-score"


def _dispatched_with_one_attempt(run):
    """Fail ST-0350 once, then dispatch it again for its retry."""
    _fail(run, AU, 1)
    for step in ("re-dispatch", "mark-dispatching", "mark-dispatched"):
        result = _dispatch(run["repo"], run["ledger"], step, "ST-0350")
        assert result.returncode == 0, (step, result.stdout, result.stderr)
    entry = _entry(run)
    assert entry.status.value == "dispatched"
    assert len(entry.attempts) == 1
    return run


@pytest.mark.spec("CG-07-IT-01")
@pytest.mark.parametrize("way", ["by_hand", "orchestrated"])
def test_cg_07_it_01_mark_blocked_keeps_the_attempts_and_the_branch(tmp_path, way):
    """Scenario Outline: Exit 2 in the gate-check step blocks the story."""
    if way == "by_hand":
        run = _dispatched_by_hand(tmp_path, code="x = 1\n", rules=False)
    else:
        run = _orchestrated_on_login(tmp_path)
    _dispatched_with_one_attempt(run)
    before = _entry(run)
    head = _git(run["repo"], "rev-parse", "story/ST-0350")

    result = _dispatch(
        run["repo"], run["ledger"], "mark-blocked", "ST-0350", "--reason", GATE_REASON
    )

    assert result.returncode == 0, result.stdout + result.stderr
    entry = _entry(run)
    assert entry.status.value == "blocked"
    assert entry.reason == GATE_REASON
    assert len(entry.attempts) == 1
    assert entry.attempts == before.attempts
    assert entry.branch == "story/ST-0350"
    assert _git(run["repo"], "rev-parse", "story/ST-0350") == head
    if way == "orchestrated":
        assert run["story"].is_dir(), "the story worktree must survive the block"
    assert lib.has_stopped(entry, lib.AttemptLimits())


@pytest.mark.spec("CG-11-IT-05")
def test_cg_11_it_05_the_refusal_at_the_merge_leaves_the_attempts_unchanged(tmp_path):
    """Scenario Outline: A story that names crap-score before the setup is refused, row premerge-check (DEC-58)."""
    run = _dispatched_with_one_attempt(_orchestrated_on_login(tmp_path))
    story_file = run["story"] / "backlog" / "ST-0350.md"
    story_file.write_text(
        story_file.read_text().replace("quality-gates: []", "quality-gates: [crap-score]")
    )
    _commit_story_work(run)  # git add -A takes the changed story file
    before = _entry(run)
    tip = _git(run["repo"], "rev-parse", "feature/login")

    result = _dispatch(run["feature"], run["ledger"], "merge-story", "ST-0350")

    assert result.returncode == 1, result.stdout + result.stderr
    assert "setup-crap-score" in result.stdout
    assert "GATE CANNOT MEASURE" not in result.stdout + result.stderr
    entry = _entry(run)
    assert entry.status.value == "dispatched"
    assert entry.attempts == before.attempts
    assert len(entry.attempts) == 1
    assert _git(run["repo"], "rev-parse", "feature/login") == tip
