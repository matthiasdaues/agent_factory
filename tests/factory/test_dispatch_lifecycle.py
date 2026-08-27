"""Contract tests for the dispatch ledger model and story lifecycle state machine.

QA strategy Layer 2b — pure logic, no git repos, no subprocess calls.
Owner of: Story Lifecycle State Machine, Ledger Integrity (SHA format),
Subcommand Idempotency (state-transition aspect).
"""

from __future__ import annotations

# Import will work once the dispatch script exposes its internals
# via a companion module or inline importability.
# For now, we insert the script's directory and import the module.
import argparse
import copy
import importlib
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent / "factory" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
dispatch_mod = importlib.import_module("dispatch_lib")
DISPATCH_SCRIPT = SCRIPT_DIR / "dispatch"

loader = importlib.machinery.SourceFileLoader("dispatch_script", str(DISPATCH_SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
dispatch = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = dispatch
loader.exec_module(dispatch)

StoryState = dispatch_mod.StoryState
StoryEntry = dispatch_mod.StoryEntry
Ledger = dispatch_mod.Ledger
TransitionError = dispatch_mod.TransitionError
ShaFormatError = dispatch_mod.ShaFormatError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def story_factory(
    story_id: str = "ST-001",
    status: StoryState = StoryState.PENDING,
    wave: int | None = None,
    branch: str | None = None,
    worktree: str | None = None,
    base_sha: str | None = None,
    reason: str | None = None,
    attempts: list | None = None,
    failure_class: str | None = None,
    escalation_granted: bool = False,
    active_session: str | None = None,
    active_tier: str | None = None,
    tier: str | None = None,
) -> StoryEntry:
    """Generate a StoryEntry with configurable fields for reuse by later stories."""
    return StoryEntry(
        id=story_id,
        wave=wave,
        status=status,
        branch=branch,
        worktree=worktree,
        base_sha=base_sha,
        tier=tier,
        reason=reason,
        gate_results={},
        attempts=attempts if attempts is not None else [],
        escalation_granted=escalation_granted,
        failure_class=failure_class,
        active_session=active_session,
        active_tier=active_tier,
    )


def ledger_with(*stories: StoryEntry) -> Ledger:
    """Build a Ledger pre-loaded with the given story entries."""
    ledger = Ledger()
    for s in stories:
        ledger.stories[s.id] = s
    return ledger


def _patch_ledger_io(
    monkeypatch: pytest.MonkeyPatch, *, ledger: Ledger, project_root: Path
) -> dict[str, Ledger]:
    """Stub ledger persistence for command-level lifecycle tests."""
    saved: dict[str, Ledger] = {}

    monkeypatch.setattr(dispatch, "_load_ledger", lambda _path: ledger)
    monkeypatch.setattr(
        dispatch,
        "_save_ledger",
        lambda current, _path: (saved.setdefault("ledger", copy.deepcopy(current)), 0)[
            1
        ],
    )
    monkeypatch.setattr(dispatch, "_project_root", lambda: project_root)
    return saved


# ---------------------------------------------------------------------------
# Valid transitions
# ---------------------------------------------------------------------------

VALID_TRANSITIONS = [
    (StoryState.PENDING, StoryState.PREPARED),
    (StoryState.PENDING, StoryState.BLOCKED),
    (StoryState.PREPARED, StoryState.DISPATCHING),
    (StoryState.PREPARED, StoryState.BLOCKED),
    (StoryState.DISPATCHING, StoryState.DISPATCHED),
    (StoryState.DISPATCHING, StoryState.FAILED),
    (StoryState.DISPATCHING, StoryState.BLOCKED),
    (StoryState.DISPATCHED, StoryState.DONE),
    (StoryState.DISPATCHED, StoryState.BLOCKED),
    (StoryState.DISPATCHED, StoryState.FAILED),
    (StoryState.FAILED, StoryState.PREPARED),
    (StoryState.BLOCKED, StoryState.PREPARED),
]


@pytest.mark.parametrize("from_state,to_state", VALID_TRANSITIONS)
def test_valid_transition(from_state, to_state):
    entry = story_factory(status=from_state)
    ledger = ledger_with(entry)
    ledger.transition("ST-001", to_state)
    assert ledger.stories["ST-001"].status == to_state


# ---------------------------------------------------------------------------
# Invalid transitions
# ---------------------------------------------------------------------------

ALL_CROSS_PAIRS = [(a, b) for a in StoryState for b in StoryState if a != b]
INVALID_TRANSITIONS = [
    (a, b) for a, b in ALL_CROSS_PAIRS if (a, b) not in set(VALID_TRANSITIONS)
]


@pytest.mark.parametrize("from_state,to_state", INVALID_TRANSITIONS)
def test_invalid_transition(from_state, to_state):
    entry = story_factory(status=from_state)
    ledger = ledger_with(entry)
    with pytest.raises(TransitionError) as exc_info:
        ledger.transition("ST-001", to_state)
    assert from_state.value in str(exc_info.value)
    assert to_state.value in str(exc_info.value)


# ---------------------------------------------------------------------------
# DONE is terminal
# ---------------------------------------------------------------------------


def test_done_has_no_outbound_transitions():
    entry = story_factory(status=StoryState.DONE)
    ledger = ledger_with(entry)
    for target in StoryState:
        if target == StoryState.DONE:
            continue
        with pytest.raises(TransitionError):
            ledger.transition("ST-001", target)


# ---------------------------------------------------------------------------
# Idempotency — same-state transition is no-op
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("state", list(StoryState))
def test_same_state_transition_is_noop(state):
    entry = story_factory(status=state)
    ledger = ledger_with(entry)
    ledger.transition("ST-001", state)
    assert ledger.stories["ST-001"].status == state


# ---------------------------------------------------------------------------
# Unknown story ID
# ---------------------------------------------------------------------------


def test_transition_unknown_story_raises():
    ledger = Ledger()
    with pytest.raises(KeyError):
        ledger.transition("ST-999", StoryState.PREPARED)


# ---------------------------------------------------------------------------
# SHA format validation
# ---------------------------------------------------------------------------

VALID_SHAS = [
    "a" * 40,
    "0123456789abcdef" * 2 + "01234567",
    "bb6849e7600dc7974031128cdcc7f0a343fc082f",
]

INVALID_SHAS = [
    "abc123",
    "a" * 39,
    "a" * 41,
    "g" * 40,
    "ABCDEF" * 6 + "ABCD",
    "",
]


@pytest.mark.parametrize("sha", VALID_SHAS)
def test_valid_sha_accepted(sha):
    entry = story_factory()
    entry.set_sha(sha)
    assert entry.base_sha == sha


@pytest.mark.parametrize("sha", INVALID_SHAS)
def test_invalid_sha_rejected(sha):
    entry = story_factory()
    with pytest.raises(ShaFormatError):
        entry.set_sha(sha)


# ---------------------------------------------------------------------------
# SHA boundary enforcement — constructor, from_dict, load, save
# ---------------------------------------------------------------------------


def test_constructor_rejects_invalid_sha():
    with pytest.raises(ShaFormatError):
        StoryEntry(id="ST-X", base_sha="abc123")


def test_from_dict_rejects_invalid_sha():
    with pytest.raises(ShaFormatError):
        StoryEntry.from_dict({"id": "ST-X", "status": "pending", "base_sha": "abc123"})


def test_load_rejects_invalid_sha(tmp_path):
    path = tmp_path / "bad-sha.yaml"
    path.write_text(
        textwrap.dedent("""\
        stories:
          ST-X:
            id: ST-X
            wave: null
            status: pending
            branch: null
            worktree: null
            base_sha: abc123
            gate_results: {}
    """)
    )
    with pytest.raises(ShaFormatError):
        Ledger.load(path)


def test_save_rejects_invalid_sha(tmp_path):
    path = tmp_path / "ledger.yaml"
    entry = story_factory("ST-X")
    ledger = ledger_with(entry)
    # Bypass __post_init__ by using object.__setattr__ on an existing entry
    object.__setattr__(entry, "base_sha", "abc123")
    with pytest.raises(ShaFormatError):
        ledger.save(path)


# ---------------------------------------------------------------------------
# Ledger YAML round-trip
# ---------------------------------------------------------------------------


def test_ledger_round_trip(tmp_path):
    path = tmp_path / "dispatch-ledger.yaml"
    original = ledger_with(
        story_factory(
            "ST-001",
            StoryState.PREPARED,
            wave=1,
            branch="feat/ST-001",
            reason="awaiting review",
        ),
        story_factory("ST-002", StoryState.DISPATCHED, wave=1, branch="feat/ST-002"),
    )
    original.stories["ST-002"].base_sha = "a" * 40
    original.save(path)
    loaded = Ledger.load(path)
    for sid in ("ST-001", "ST-002"):
        assert loaded.stories[sid].status == original.stories[sid].status
        assert loaded.stories[sid].wave == original.stories[sid].wave
        assert loaded.stories[sid].branch == original.stories[sid].branch
        assert loaded.stories[sid].base_sha == original.stories[sid].base_sha
    assert loaded.stories["ST-001"].reason == "awaiting review"


def test_ledger_round_trip_preserves_attempts(tmp_path):
    path = tmp_path / "dispatch-ledger.yaml"
    entry = story_factory("ST-001", StoryState.FAILED)
    entry.attempts = [{"class": "acceptance_unmet", "tier": "economy"}]
    original = ledger_with(entry)
    original.save(path)
    loaded = Ledger.load(path)
    assert loaded.stories["ST-001"].attempts == [
        {"class": "acceptance_unmet", "tier": "economy"}
    ]


def test_ledger_without_attempts_key_treated_as_empty(tmp_path):
    path = tmp_path / "dispatch-ledger.yaml"
    path.write_text(
        textwrap.dedent("""\
        stories:
          ST-001:
            id: ST-001
            wave: 1
            status: prepared
            branch: feat/ST-001
            worktree: null
            base_sha: null
            gate_results: {}
    """)
    )
    loaded = Ledger.load(path)
    assert loaded.stories["ST-001"].attempts == []


# ---------------------------------------------------------------------------
# Ledger load edge cases
# ---------------------------------------------------------------------------


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        Ledger.load(tmp_path / "nonexistent.yaml")


def test_save_creates_parent_directories(tmp_path):
    path = tmp_path / "sub" / "dir" / "ledger.yaml"
    ledger = ledger_with(story_factory())
    ledger.save(path)
    assert path.exists()
    loaded = Ledger.load(path)
    assert "ST-001" in loaded.stories


# ---------------------------------------------------------------------------
# CLI lifecycle subcommands
# ---------------------------------------------------------------------------


def _run_dispatch(
    *args: str, cwd: Path, ledger: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DISPATCH_SCRIPT), "--ledger", str(ledger), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )


def _write_ledger(path: Path, ledger: Ledger) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ledger.save(path)


def _loaded_status(path: Path, story_id: str) -> StoryState:
    return Ledger.load(path).stories[story_id].status


def test_mark_dispatching_happy_path_and_idempotency(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _write_ledger(ledger_path, ledger_with(story_factory(status=StoryState.PREPARED)))

    first = _run_dispatch(
        "mark-dispatching", "ST-001", cwd=tmp_path, ledger=ledger_path
    )
    second = _run_dispatch(
        "mark-dispatching", "ST-001", cwd=tmp_path, ledger=ledger_path
    )

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0
    assert _loaded_status(ledger_path, "ST-001") == StoryState.DISPATCHING


def test_mark_dispatching_rejects_wrong_source_state(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _write_ledger(ledger_path, ledger_with(story_factory(status=StoryState.DONE)))

    result = _run_dispatch(
        "mark-dispatching", "ST-001", cwd=tmp_path, ledger=ledger_path
    )

    assert result.returncode == 1
    assert "invalid transition" in result.stderr


def test_mark_dispatched_happy_path_and_idempotency(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _write_ledger(
        ledger_path,
        ledger_with(story_factory(status=StoryState.DISPATCHING)),
    )

    first = _run_dispatch("mark-dispatched", "ST-001", cwd=tmp_path, ledger=ledger_path)
    second = _run_dispatch(
        "mark-dispatched", "ST-001", cwd=tmp_path, ledger=ledger_path
    )

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0
    assert _loaded_status(ledger_path, "ST-001") == StoryState.DISPATCHED


def test_mark_dispatched_rejects_wrong_source_state(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _write_ledger(ledger_path, ledger_with(story_factory(status=StoryState.PREPARED)))

    result = _run_dispatch(
        "mark-dispatched", "ST-001", cwd=tmp_path, ledger=ledger_path
    )

    assert result.returncode == 1
    assert "invalid transition" in result.stderr


def test_mark_blocked_records_reason_and_allows_rerun(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _write_ledger(ledger_path, ledger_with(story_factory(status=StoryState.PREPARED)))

    first = _run_dispatch(
        "mark-blocked",
        "ST-001",
        "--reason",
        "awaiting design decision",
        cwd=tmp_path,
        ledger=ledger_path,
    )
    second = _run_dispatch(
        "mark-blocked",
        "ST-001",
        "--reason",
        "ignored on rerun",
        cwd=tmp_path,
        ledger=ledger_path,
    )

    ledger = Ledger.load(ledger_path)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0
    assert ledger.stories["ST-001"].status == StoryState.BLOCKED
    assert ledger.stories["ST-001"].reason == "awaiting design decision"


def test_mark_blocked_rejects_terminal_story(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _write_ledger(ledger_path, ledger_with(story_factory(status=StoryState.DONE)))

    result = _run_dispatch(
        "mark-blocked",
        "ST-001",
        "--reason",
        "should fail",
        cwd=tmp_path,
        ledger=ledger_path,
    )

    assert result.returncode == 1


def _init_git_repo_with_tracked_file(
    repo_path: Path, file_name: str = "evidence.txt"
) -> Path:
    """Initialize a git repo at *repo_path* with one tracked file, return its path."""
    subprocess.run(["git", "init", "-q"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_path, check=True)
    evidence_path = repo_path / file_name
    evidence_path.write_text("evidence contents\n")
    subprocess.run(["git", "add", file_name], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "add evidence"], cwd=repo_path, check=True
    )
    return evidence_path


def _git_head(repo_path: Path) -> str:
    """Return HEAD SHA for a git repository rooted at *repo_path*."""
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def test_mark_failed_happy_path_and_idempotency(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _init_git_repo_with_tracked_file(tmp_path)
    _write_ledger(
        ledger_path,
        ledger_with(story_factory(status=StoryState.DISPATCHING)),
    )

    first = _run_dispatch("mark-failed", "ST-001", cwd=tmp_path, ledger=ledger_path)
    second = _run_dispatch("mark-failed", "ST-001", cwd=tmp_path, ledger=ledger_path)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0
    assert _loaded_status(ledger_path, "ST-001") == StoryState.FAILED
    loaded = Ledger.load(ledger_path)
    assert loaded.stories["ST-001"].failure_class is None
    assert loaded.stories["ST-001"].evidence is None


def test_mark_failed_rejects_wrong_source_state(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _init_git_repo_with_tracked_file(tmp_path)
    _write_ledger(ledger_path, ledger_with(story_factory(status=StoryState.PREPARED)))

    result = _run_dispatch(
        "mark-failed",
        "ST-001",
        "--class",
        "environment",
        "--evidence",
        "evidence.txt",
        cwd=tmp_path,
        ledger=ledger_path,
    )

    assert result.returncode == 1


def test_valid_failure_class_and_tracked_evidence_recorded(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _init_git_repo_with_tracked_file(tmp_path, "proof.log")
    _write_ledger(
        ledger_path,
        ledger_with(story_factory(status=StoryState.DISPATCHING)),
    )

    result = _run_dispatch(
        "mark-failed",
        "ST-001",
        "--class",
        "seam_defect",
        "--evidence",
        "proof.log",
        cwd=tmp_path,
        ledger=ledger_path,
    )

    assert result.returncode == 0, result.stderr
    loaded = Ledger.load(ledger_path)
    assert loaded.stories["ST-001"].status == StoryState.FAILED
    assert loaded.stories["ST-001"].failure_class == "seam_defect"
    assert loaded.stories["ST-001"].evidence == "proof.log"


@pytest.mark.parametrize(
    "failure_class",
    [
        "context_missing",
        "contract_violation",
        "environment",
        "spend_death",
        "seam_defect",
        "acceptance_unmet",
        "contradictory_evidence",
    ],
)
def test_all_seven_classes_accepted(tmp_path, failure_class):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _init_git_repo_with_tracked_file(tmp_path)
    _write_ledger(
        ledger_path,
        ledger_with(story_factory(status=StoryState.DISPATCHING)),
    )

    result = _run_dispatch(
        "mark-failed",
        "ST-001",
        "--class",
        failure_class,
        "--evidence",
        "evidence.txt",
        cwd=tmp_path,
        ledger=ledger_path,
    )

    assert result.returncode == 0, result.stderr
    loaded = Ledger.load(ledger_path)
    assert loaded.stories["ST-001"].failure_class == failure_class


def test_unknown_class_rejected(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _init_git_repo_with_tracked_file(tmp_path)
    _write_ledger(
        ledger_path,
        ledger_with(story_factory(status=StoryState.DISPATCHING)),
    )

    result = _run_dispatch(
        "mark-failed",
        "ST-001",
        "--class",
        "not_a_real_class",
        "--evidence",
        "evidence.txt",
        cwd=tmp_path,
        ledger=ledger_path,
    )

    assert result.returncode != 0
    assert _loaded_status(ledger_path, "ST-001") == StoryState.DISPATCHING


def test_untracked_evidence_rejected(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _init_git_repo_with_tracked_file(tmp_path)
    untracked = tmp_path / "untracked.txt"
    untracked.write_text("not tracked\n")
    _write_ledger(
        ledger_path,
        ledger_with(story_factory(status=StoryState.DISPATCHING)),
    )

    result = _run_dispatch(
        "mark-failed",
        "ST-001",
        "--class",
        "environment",
        "--evidence",
        "untracked.txt",
        cwd=tmp_path,
        ledger=ledger_path,
    )

    assert result.returncode != 0
    assert "not tracked" in result.stderr
    assert _loaded_status(ledger_path, "ST-001") == StoryState.DISPATCHING


def test_basic_failure_transition_does_not_require_metadata(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _init_git_repo_with_tracked_file(tmp_path)
    _write_ledger(
        ledger_path,
        ledger_with(story_factory(status=StoryState.DISPATCHING)),
    )

    result = _run_dispatch("mark-failed", "ST-001", cwd=tmp_path, ledger=ledger_path)

    assert result.returncode == 0, result.stderr
    assert _loaded_status(ledger_path, "ST-001") == StoryState.FAILED


def test_re_dispatch_happy_path_and_idempotency(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _write_ledger(ledger_path, ledger_with(story_factory(status=StoryState.FAILED)))

    first = _run_dispatch("re-dispatch", "ST-001", cwd=tmp_path, ledger=ledger_path)
    second = _run_dispatch("re-dispatch", "ST-001", cwd=tmp_path, ledger=ledger_path)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0
    assert _loaded_status(ledger_path, "ST-001") == StoryState.PREPARED


@pytest.mark.parametrize(
    "failure_class,attempts,escalation_granted,active_session,expected_status,expected_returncode",
    [
        (
            "context_missing",
            [{"failure_class": "context_missing", "session": "impl"}],
            False,
            "impl",
            StoryState.PREPARED,
            0,
        ),
        (
            "environment",
            [{"failure_class": "environment", "session": "impl"}],
            False,
            "impl",
            StoryState.PREPARED,
            0,
        ),
        (
            "spend_death",
            [{"failure_class": "spend_death", "session": "impl"}],
            False,
            "impl",
            StoryState.PREPARED,
            0,
        ),
        (
            "seam_defect",
            [{"failure_class": "seam_defect", "session": "seam"}],
            False,
            "seam",
            StoryState.PREPARED,
            0,
        ),
        (
            "contract_violation",
            [{"failure_class": "contract_violation", "session": "impl"}],
            False,
            "impl",
            StoryState.PREPARED,
            0,
        ),
        (
            "contract_violation",
            [
                {"failure_class": "contract_violation", "session": "impl"},
                {"failure_class": "contract_violation", "session": "impl"},
            ],
            False,
            "impl",
            StoryState.FAILED,
            1,
        ),
        (
            "acceptance_unmet",
            [{"failure_class": "acceptance_unmet", "session": "impl"}],
            False,
            "impl",
            StoryState.FAILED,
            1,
        ),
        (
            "contradictory_evidence",
            [{"failure_class": "contradictory_evidence", "session": "impl"}],
            False,
            "impl",
            StoryState.FAILED,
            1,
        ),
        (
            "acceptance_unmet",
            [{"failure_class": "acceptance_unmet", "session": "impl"}],
            True,
            "impl",
            StoryState.PREPARED,
            0,
        ),
    ],
)
def test_re_dispatch_disposition_by_failure_class(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_class: str,
    attempts: list[dict],
    escalation_granted: bool,
    active_session: str,
    expected_status: StoryState,
    expected_returncode: int,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    ledger = Ledger()
    ledger.stories["ST-001"] = StoryEntry(
        id="ST-001",
        status=StoryState.FAILED,
        tier="economy",
        attempts=attempts,
        escalation_granted=escalation_granted,
        active_session=active_session,
        active_tier="economy",
        failure_class=failure_class,
    )
    saved = _patch_ledger_io(monkeypatch, ledger=ledger, project_root=project_root)

    result = dispatch.cmd_re_dispatch(
        argparse.Namespace(ledger=tmp_path / "ledger.yaml", story_id="ST-001")
    )

    assert result == expected_returncode
    if expected_returncode == 0:
        assert saved["ledger"].stories["ST-001"].status == expected_status
        assert saved["ledger"].stories["ST-001"].active_session == active_session
    else:
        assert "ledger" not in saved
        assert ledger.stories["ST-001"].status == StoryState.FAILED


def test_re_dispatch_rejects_wrong_source_state(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _write_ledger(ledger_path, ledger_with(story_factory(status=StoryState.DISPATCHED)))

    result = _run_dispatch("re-dispatch", "ST-001", cwd=tmp_path, ledger=ledger_path)

    assert result.returncode == 1


def test_close_wave_records_summary_and_commits(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _init_git_repo_with_tracked_file(tmp_path, "placeholder.txt")
    branch_head = _git_head(tmp_path)
    _write_ledger(
        ledger_path,
        ledger_with(
            story_factory("ST-001", status=StoryState.DONE, wave=2),
            story_factory(
                "ST-002", status=StoryState.BLOCKED, wave=2, reason="blocked"
            ),
            story_factory("ST-003", status=StoryState.FAILED, wave=2, reason="failed"),
            story_factory("ST-004", status=StoryState.PENDING, wave=3),
        ),
    )
    ledger = Ledger.load(ledger_path)
    ledger.stories["ST-001"].commit_sha = "a" * 40
    ledger.save(ledger_path)

    before = _git_head(tmp_path)
    result = _run_dispatch("close-wave", "2", cwd=tmp_path, ledger=ledger_path)
    after = _git_head(tmp_path)

    assert result.returncode == 0, result.stderr
    assert before != after
    assert after != branch_head

    loaded = Ledger.load(ledger_path)
    assert len(loaded.waves) == 1
    record = loaded.waves[0]
    assert record.number == 2
    assert record.branch_head == before
    assert record.completed == [{"id": "ST-001", "merge_sha": "a" * 40}]
    assert record.blocked == [{"id": "ST-002", "reason": "blocked"}]
    assert record.failed == [{"id": "ST-003", "reason": "failed"}]
    assert record.next_ready == ["ST-004"]


def test_close_wave_is_idempotent(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _init_git_repo_with_tracked_file(tmp_path, "placeholder.txt")
    _write_ledger(
        ledger_path,
        ledger_with(
            story_factory("ST-001", status=StoryState.DONE, wave=2),
        ),
    )
    ledger = Ledger.load(ledger_path)
    ledger.stories["ST-001"].commit_sha = "b" * 40
    ledger.save(ledger_path)

    first = _run_dispatch("close-wave", "2", cwd=tmp_path, ledger=ledger_path)
    head_after_first = _git_head(tmp_path)
    second = _run_dispatch("close-wave", "2", cwd=tmp_path, ledger=ledger_path)
    head_after_second = _git_head(tmp_path)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0
    assert head_after_first == head_after_second
    assert len(Ledger.load(ledger_path).waves) == 1


def test_close_wave_rejects_non_terminal_story(tmp_path):
    ledger_path = tmp_path / ".agent-factory" / "dispatch-ledger.yaml"
    _write_ledger(
        ledger_path,
        ledger_with(
            story_factory("ST-001", status=StoryState.DONE, wave=2),
            story_factory("ST-002", status=StoryState.PREPARED, wave=2),
        ),
    )

    result = _run_dispatch("close-wave", "2", cwd=tmp_path, ledger=ledger_path)

    assert result.returncode == 1
