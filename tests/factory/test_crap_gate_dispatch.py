"""mark-blocked in the gate-check step, when crap-score exits 2 (docs/spec/features/crap-gate-setup.feature, Rule CG-07),
the refusal at the merge of a story that names crap-score without an entry (Rule CG-11, DEC-58),
and the ready commands that dispatch init runs before a run starts (Rule CG-10, BR-137).

Each test starts from the state of the Scenario: ST-0350 is dispatched with one counted attempt.
The run helpers come from the run-lifecycle tests, as in the other test_crap_gate_ files.
"""

from __future__ import annotations

import stat
import time
from pathlib import Path

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
    _init,
    _ledger_path,
    _worktree_branches,
    run_repo,  # noqa: F401 - the fixture of the CG-10 tests
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


# --- CG-10: dispatch init runs every ready command of an enabled gate (ST-0445) -

READY = "scripts/crap-ready-backend"
GATED_TESTING_YAML = f"""\
test_command: "true"
gates:
  crap-score:
    enabled: {{enabled}}
    threshold: 8
    timeout_minutes: 10
    measures:
      - name: backend
        files: "packages/server/backend/**"
        command: "scripts/crap-measure-backend"
        ready: "{READY}"
"""
READY_STUB = """\
#!/bin/sh
{{
  echo "start $(pwd)"
  git rev-parse --verify --quiet refs/heads/feature/login >/dev/null && echo "branch exists"
  [ -e .current-work/feature/login/dispatch-ledger.yaml ] && echo "ledger exists"
}} >> "{log}"
echo "the Compose stack is stopped" >&2
exit {code}
"""


def _gate_with_ready(repo: Path, *, enabled: str = "true", code: int = 0) -> Path:
    """Commit an entry gates.crap-score with the measure backend and its ready stub; return the stub's log."""
    log = repo.parent / "ready.log"
    (repo / "docs" / "testing.yaml").write_text(GATED_TESTING_YAML.format(enabled=enabled))
    stub = repo / READY
    stub.parent.mkdir(parents=True, exist_ok=True)
    stub.write_text(READY_STUB.format(log=log, code=code))
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "gate with a ready command")
    return log


@pytest.mark.spec("CG-10-IT-01")
def test_cg_10_it_01_init_runs_the_ready_command_once_in_the_primary_checkout(run_repo):
    """Scenario: dispatch init runs every ready command once in the primary checkout (DEC-23)."""
    log = _gate_with_ready(run_repo)

    result = _init(run_repo, "feature/login", "ST-0350", "--mode", "by-hand")

    assert result.returncode == 0, result.stdout + result.stderr
    assert log.read_text().splitlines() == [f"start {run_repo}"]
    assert _ledger_path(run_repo, "feature/login").is_file()


@pytest.mark.spec("CG-10-IT-02")
@pytest.mark.parametrize("mode", ["by-hand", "orchestrated"])
def test_cg_10_it_02_a_failed_ready_command_leaves_nothing_behind(run_repo, mode):
    """Scenario: A failed ready command stops dispatch init and leaves nothing behind (BR-137)."""
    log = _gate_with_ready(run_repo, code=1)
    worktrees = _git(run_repo, "worktree", "list")

    result = _init(run_repo, "feature/login", "ST-0350", "--mode", mode)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "backend" in result.stderr
    assert READY in result.stderr
    assert log.read_text().splitlines() == [f"start {run_repo}"]
    assert _git(run_repo, "branch", "--list", "feature/login") == ""
    assert _git(run_repo, "worktree", "list") == worktrees
    assert "feature/login" not in _worktree_branches(run_repo)
    assert not _ledger_path(run_repo, "feature/login").exists()


@pytest.mark.spec("CG-10-IT-03")
def test_cg_10_it_03_init_runs_no_ready_command_of_a_disabled_gate(run_repo):
    """Scenario: dispatch init runs no ready command of a gate that is not enabled."""
    log = _gate_with_ready(run_repo, enabled="false", code=1)

    result = _init(run_repo, "feature/login", "ST-0350", "--mode", "by-hand")

    assert result.returncode == 0, result.stdout + result.stderr
    assert not log.exists()


HANGING_STUB = """\
#!/bin/sh
sleep 300 &
echo $! > "{child}"
sleep 300
"""


def _pid_alive(pid: int) -> bool:
    """True while *pid* runs; a zombie that waits for its reaper counts as ended."""
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (FileNotFoundError, IndexError):
        return False
    return state != "Z"


@pytest.mark.spec("CG-10-IT-02")
def test_cg_10_a_ready_command_past_the_limit_stops_its_group_and_leaves_nothing_behind(run_repo):
    """DEC-61: init stops the whole process group of a ready command at timeout_minutes."""
    _gate_with_ready(run_repo)
    child = run_repo.parent / "child.pid"
    testing = run_repo / "docs" / "testing.yaml"
    # 0.05 minutes is 3 seconds: long enough for the stub to start its child under load.
    testing.write_text(testing.read_text().replace("timeout_minutes: 10", "timeout_minutes: 0.05"))
    stub = run_repo / READY
    stub.write_text(HANGING_STUB.format(child=child))
    _git(run_repo, "add", "-A")
    _git(run_repo, "commit", "-qm", "a ready command that outlasts the limit")
    worktrees = _git(run_repo, "worktree", "list")

    result = _init(run_repo, "feature/login", "ST-0350", "--mode", "orchestrated")

    assert result.returncode == 1, result.stdout + result.stderr
    assert "backend" in result.stderr
    assert "timeout_minutes 0.05" in result.stderr
    pid = int(child.read_text())
    deadline = time.monotonic() + 10
    while _pid_alive(pid) and time.monotonic() < deadline:
        time.sleep(0.1)
    assert not _pid_alive(pid), "the child of the ready command must stop with its group"
    assert _git(run_repo, "branch", "--list", "feature/login") == ""
    assert _git(run_repo, "worktree", "list") == worktrees
    assert not _ledger_path(run_repo, "feature/login").exists()


# --- CG-09: resume-gates returns a story blocked by a gate that cannot measure (ST-0444) -

RESUME_REFUSED = [
    ("blocked", "merge conflict"),
    ("blocked", "post-merge test failure"),
    ("blocked", "Gate cannot measure: crap-score"),
    ("blocked", None),
    ("dispatched", None),
    ("failed", None),
    ("prepared", None),
]


@pytest.mark.spec("CG-09-CT-01")
def test_cg_09_the_guard_accepts_only_blocked_with_the_exact_reason():
    """Scenario: resume-gates returns the story to the gate-check step (BR-135)."""
    entry = lib.StoryEntry(id="ST-0350", status=lib.StoryState.BLOCKED, reason=GATE_REASON)
    assert lib.GATE_CANNOT_MEASURE_REASON == GATE_REASON
    assert lib.resume_gates_refusal(entry) is None
    assert lib.StoryState.DISPATCHED in lib.VALID_TRANSITIONS[lib.StoryState.BLOCKED]


@pytest.mark.spec("CG-09-CT-01")
@pytest.mark.parametrize(("state", "reason"), RESUME_REFUSED)
def test_cg_09_the_guard_refuses_every_other_entry_and_names_its_state(state, reason):
    """Scenario Outline: resume-gates refuses any other story (DEC-29)."""
    entry = lib.StoryEntry(id="ST-0350", status=lib.StoryState(state), reason=reason)

    refusal = lib.resume_gates_refusal(entry)

    assert refusal is not None
    assert refusal.startswith(f"ST-0350 is {state}")
    if reason is not None:
        assert f"'{reason}'" in refusal
    assert entry.status.value == state
    assert entry.reason == reason


def _blocked_by_the_gate(tmp_path: Path) -> dict[str, Path]:
    """ST-0350 of an orchestrated run, blocked by exit 2 after one counted attempt."""
    run = _dispatched_with_one_attempt(_orchestrated_on_login(tmp_path))
    result = _dispatch(
        run["repo"], run["ledger"], "mark-blocked", "ST-0350", "--reason", GATE_REASON
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return run


def _story_files(run: dict[str, Path]) -> list[Path]:
    """Every file of the story workspace, the step manifest and the brief included."""
    return sorted(p for p in (run["story"] / ".current-work").rglob("*") if p.is_file())


@pytest.mark.spec("CG-09-IT-01")
def test_cg_09_resume_gates_returns_the_story_to_the_gate_check_step(tmp_path):
    """Scenario: resume-gates returns the story to the gate-check step (BR-135, DEC-07)."""
    run = _blocked_by_the_gate(tmp_path)
    ledger = lib.Ledger.load(run["ledger"])
    ledger.stories["ST-0350"].attempt_grants.append({"tier": "economy", "attempt_count": 1})
    ledger.save(run["ledger"])
    before = _entry(run)
    head = _git(run["repo"], "rev-parse", "story/ST-0350")
    files = {p: p.read_bytes() for p in _story_files(run)}

    result = _dispatch(run["repo"], run["ledger"], "resume-gates", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "gate-check step" in result.stdout
    entry = _entry(run)
    assert entry.status.value == "dispatched"
    assert entry.reason == GATE_REASON
    assert len(entry.attempts) == 1
    assert entry.attempts == before.attempts
    assert entry.attempt_grants == before.attempt_grants == [
        {"tier": "economy", "attempt_count": 1}
    ]
    assert entry.branch == before.branch == "story/ST-0350"
    assert entry.worktree == before.worktree
    assert _git(run["repo"], "rev-parse", "story/ST-0350") == head
    assert run["story"].is_dir()
    assert {p: p.read_bytes() for p in _story_files(run)} == files


@pytest.mark.spec("CG-09-IT-01")
def test_cg_09_resume_gates_returns_a_finding_to_the_gate_check_step(tmp_path):
    """Scenario: resume-gates returns a finding to the gate-check step (DEC-22)."""
    run = _blocked_by_the_gate(tmp_path)
    ledger = lib.Ledger.load(run["ledger"])
    ledger.stories["BUG-0090"] = lib.StoryEntry(
        id="BUG-0090",
        wave=1,
        status=lib.StoryState.BLOCKED,
        branch="story/BUG-0090",
        reason=GATE_REASON,
    )
    ledger.save(run["ledger"])

    result = _dispatch(run["repo"], run["ledger"], "resume-gates", "BUG-0090")

    assert result.returncode == 0, result.stdout + result.stderr
    entry = lib.Ledger.load(run["ledger"]).stories["BUG-0090"]
    assert entry.status.value == "dispatched"
    assert entry.attempts == []
    assert entry.branch == "story/BUG-0090"
    assert _entry(run).status.value == "blocked"


@pytest.mark.spec("CG-09-IT-01")
@pytest.mark.parametrize(
    ("state", "reason"), [("blocked", "merge conflict"), ("dispatched", None), ("failed", None)]
)
def test_cg_09_resume_gates_refuses_any_other_story_and_writes_nothing(tmp_path, state, reason):
    """Scenario Outline: resume-gates refuses any other story (BR-135, DEC-29)."""
    run = _blocked_by_the_gate(tmp_path)
    ledger = lib.Ledger.load(run["ledger"])
    ledger.stories["ST-0350"].status = lib.StoryState(state)
    ledger.stories["ST-0350"].reason = reason
    ledger.save(run["ledger"])
    before = run["ledger"].read_bytes()

    result = _dispatch(run["repo"], run["ledger"], "resume-gates", "ST-0350")

    assert result.returncode == 1, result.stdout + result.stderr
    assert f"ST-0350 is {state}" in result.stderr
    if reason is not None:
        assert reason in result.stderr
    assert run["ledger"].read_bytes() == before


@pytest.mark.spec("CG-09-IT-01")
def test_cg_09_mark_dispatched_takes_no_edge_from_blocked(tmp_path):
    """BR-135: only resume-gates leaves blocked for dispatched."""
    run = _blocked_by_the_gate(tmp_path)
    before = run["ledger"].read_bytes()

    result = _dispatch(run["repo"], run["ledger"], "mark-dispatched", "ST-0350")

    assert result.returncode == 1, result.stdout + result.stderr
    assert "ST-0350 is blocked" in result.stderr
    assert run["ledger"].read_bytes() == before


@pytest.mark.spec("CG-09-IT-02")
def test_cg_09_re_dispatch_stays_the_way_back_for_a_story_whose_code_must_change(tmp_path):
    """Scenario: re-dispatch stays the way back for a story whose code must change."""
    run = _blocked_by_the_gate(tmp_path)

    result = _dispatch(run["repo"], run["ledger"], "re-dispatch", "ST-0350")

    assert result.returncode == 0, result.stdout + result.stderr
    entry = _entry(run)
    assert entry.status.value == "prepared"
    assert len(entry.attempts) == 1
