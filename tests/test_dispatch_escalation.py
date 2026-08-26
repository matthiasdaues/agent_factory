"""Contract tests for dispatch escalation and attempt recording."""

from __future__ import annotations

import argparse
import copy
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "factory" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
DISPATCH_PATH = SCRIPT_DIR / "dispatch"

loader = importlib.machinery.SourceFileLoader("dispatch_script", str(DISPATCH_PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
dispatch = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = dispatch
loader.exec_module(dispatch)

from dispatch_lib import (  # noqa: E402
    Ledger,
    StoryEntry,
    StoryState,
    implementation_session_tier,
)


def _story_file(
    project_root: Path,
    story_id: str,
    *,
    tier: str = "economy",
    outputs: list[str] | None = None,
    strategy: str = "direct",
) -> Path:
    backlog_dir = project_root / "backlog"
    backlog_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"id: {story_id}",
        f"tier: {tier}",
        "status: failed",
        f"strategy: {strategy}",
    ]
    if outputs:
        lines.append("outputs:")
        lines.extend(f"  - {output}" for output in outputs)
    lines.append("---")
    lines.append(f"# {story_id}")
    path = backlog_dir / f"{story_id}.md"
    path.write_text("\n".join(lines) + "\n")
    return path


def _story_entry(
    story_id: str = "ST-001",
    *,
    status: StoryState = StoryState.FAILED,
    tier: str | None = "economy",
    wave: int = 1,
    branch: str = "story/ST-001",
    worktree: str = "/tmp/worktree",
    base_sha: str = "a" * 40,
    attempts: list[dict] | None = None,
    escalation_granted: bool = False,
    active_session: str | None = None,
    active_tier: str | None = None,
) -> StoryEntry:
    return StoryEntry(
        id=story_id,
        wave=wave,
        status=status,
        branch=branch,
        worktree=worktree,
        base_sha=base_sha,
        tier=tier,
        attempts=attempts if attempts is not None else [],
        escalation_granted=escalation_granted,
        active_session=active_session,
        active_tier=active_tier,
    )


def _ledger_with(*entries: StoryEntry) -> Ledger:
    ledger = Ledger()
    for entry in entries:
        ledger.stories[entry.id] = entry
    return ledger


def _patch(monkeypatch: pytest.MonkeyPatch, *, ledger: Ledger, project_root: Path):
    saved: dict[str, Ledger] = {}

    def _load_ledger(_path: Path) -> Ledger:
        return ledger

    def _save_ledger(current: Ledger, _path: Path) -> int:
        saved["ledger"] = copy.deepcopy(current)
        return 0

    def _project_root() -> Path:
        return project_root

    monkeypatch.setattr(dispatch, "_load_ledger", _load_ledger)
    monkeypatch.setattr(dispatch, "_save_ledger", _save_ledger)
    monkeypatch.setattr(dispatch, "_project_root", _project_root)
    return saved


def test_ledger_round_trip_preserves_attempts_and_escalation_fields(tmp_path: Path) -> None:
    path = tmp_path / "ledger.yaml"
    original = _ledger_with(
        _story_entry(
            attempts=[
                {
                    "session": "impl",
                    "tier": "economy",
                    "failure_class": "acceptance_unmet",
                    "evidence": "docs/findings/IMPL-0001.md",
                    "commit_sha": "b" * 40,
                    "normalized_total": 17,
                }
            ],
            escalation_granted=True,
        )
    )
    original.save(path)

    loaded = Ledger.load(path)

    assert loaded.stories["ST-001"].attempts == original.stories["ST-001"].attempts
    assert loaded.stories["ST-001"].escalation_granted is True
    assert loaded.stories["ST-001"].tier == "economy"


def test_mark_failed_appends_full_attempt_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _story_file(project_root, "ST-001", tier="economy")
    ledger = _ledger_with(_story_entry(status=StoryState.DISPATCHING, attempts=[]))
    saved = _patch(monkeypatch, ledger=ledger, project_root=project_root)

    result = dispatch.cmd_mark_failed(
        argparse.Namespace(
            ledger=tmp_path / "ledger.yaml",
            story_id="ST-001",
            failure_class="acceptance_unmet",
            evidence=None,
        )
    )

    assert result == 0
    entry = saved["ledger"].stories["ST-001"]
    assert entry.status == StoryState.FAILED
    assert entry.attempts == [
        {
            "session": "impl",
            "tier": "economy",
            "failure_class": "acceptance_unmet",
            "evidence": None,
            "commit_sha": None,
            "normalized_total": 0,
        }
    ]


def test_implementation_session_tier_drops_one_level_and_floors_at_economy() -> None:
    assert implementation_session_tier("strong") == "standard"
    assert implementation_session_tier("standard") == "economy"
    assert implementation_session_tier("economy") == "economy"


def test_mark_failed_records_seam_defect_without_consuming_escalation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _story_file(project_root, "ST-001", tier="standard", strategy="seams-first")
    ledger = _ledger_with(
        _story_entry(
            status=StoryState.DISPATCHING,
            tier="standard",
            active_session="seam",
            active_tier="standard",
        )
    )
    saved = _patch(monkeypatch, ledger=ledger, project_root=project_root)

    result = dispatch.cmd_mark_failed(
        argparse.Namespace(
            ledger=tmp_path / "ledger.yaml",
            story_id="ST-001",
            failure_class="seam_defect",
            evidence=None,
        )
    )

    assert result == 0
    entry = saved["ledger"].stories["ST-001"]
    assert entry.status == StoryState.FAILED
    assert entry.escalation_granted is False
    assert entry.attempts[-1] == {
        "session": "seam",
        "tier": "standard",
        "failure_class": "seam_defect",
        "evidence": None,
        "commit_sha": None,
        "normalized_total": 0,
    }


def test_mark_failed_blocks_repeated_seam_defect_for_human_decision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _story_file(project_root, "ST-001", tier="standard", strategy="seams-first")
    ledger = _ledger_with(
        _story_entry(
            status=StoryState.DISPATCHING,
            tier="standard",
            active_session="seam",
            active_tier="standard",
            attempts=[
                {
                    "session": "seam",
                    "tier": "standard",
                    "failure_class": "seam_defect",
                    "evidence": None,
                    "commit_sha": None,
                    "normalized_total": 0,
                }
            ],
        )
    )
    saved = _patch(monkeypatch, ledger=ledger, project_root=project_root)

    result = dispatch.cmd_mark_failed(
        argparse.Namespace(
            ledger=tmp_path / "ledger.yaml",
            story_id="ST-001",
            failure_class="seam_defect",
            evidence=None,
        )
    )

    assert result == 0
    entry = saved["ledger"].stories["ST-001"]
    assert entry.status == StoryState.BLOCKED
    assert entry.reason == "seam_defect_human_decision"
    assert entry.escalation_granted is False
    assert len(entry.attempts) == 2
    assert entry.attempts[-1]["session"] == "seam"


def test_escalate_happy_path_updates_tier_and_grants_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _story_file(project_root, "ST-001", tier="economy", outputs=["src/foo.py"])
    ledger = _ledger_with(
        _story_entry(
            attempts=[
                {
                    "session": "impl",
                    "tier": "economy",
                    "failure_class": "acceptance_unmet",
                    "evidence": "docs/findings/IMPL-0001.md",
                    "commit_sha": "b" * 40,
                    "normalized_total": 17,
                }
            ]
        )
    )
    saved = _patch(monkeypatch, ledger=ledger, project_root=project_root)
    monkeypatch.setattr(dispatch, "_run_verify_base", lambda *args, **kwargs: (0, ""))
    monkeypatch.setattr(
        dispatch,
        "_git",
        lambda *args: (0, "src/foo.py\n", "") if args[:3] == ("show", "--name-only", "--format=") else (0, "", ""),
    )

    result = dispatch.cmd_escalate(
        argparse.Namespace(ledger=tmp_path / "ledger.yaml", story_id="ST-001")
    )

    assert result == 0
    entry = saved["ledger"].stories["ST-001"]
    assert entry.tier == "standard"
    assert entry.escalation_granted is True


def test_escalate_rejects_nonqualifying_failure_class(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _story_file(project_root, "ST-001", tier="economy", outputs=["src/foo.py"])
    ledger = _ledger_with(
        _story_entry(
            attempts=[
                {
                    "session": "impl",
                    "tier": "economy",
                    "failure_class": "context_missing",
                    "evidence": "docs/findings/IMPL-0001.md",
                    "commit_sha": "b" * 40,
                    "normalized_total": 17,
                }
            ]
        )
    )
    _patch(monkeypatch, ledger=ledger, project_root=project_root)
    monkeypatch.setattr(dispatch, "_run_verify_base", lambda *args, **kwargs: (0, ""))

    result = dispatch.cmd_escalate(
        argparse.Namespace(ledger=tmp_path / "ledger.yaml", story_id="ST-001")
    )

    assert result == 1


def test_escalate_blocks_when_no_prior_impl_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _story_file(project_root, "ST-001", tier="economy", outputs=["src/foo.py"])
    ledger = _ledger_with(_story_entry(attempts=[]))
    _patch(monkeypatch, ledger=ledger, project_root=project_root)
    monkeypatch.setattr(dispatch, "_run_verify_base", lambda *args, **kwargs: (0, ""))

    result = dispatch.cmd_escalate(
        argparse.Namespace(ledger=tmp_path / "ledger.yaml", story_id="ST-001")
    )

    assert result == 1


def test_escalate_blocks_when_already_strong(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _story_file(project_root, "ST-001", tier="strong", outputs=["src/foo.py"])
    ledger = _ledger_with(
        _story_entry(
            tier="strong",
            attempts=[
                {
                    "session": "impl",
                    "tier": "strong",
                    "failure_class": "acceptance_unmet",
                    "evidence": "docs/findings/IMPL-0001.md",
                    "commit_sha": "b" * 40,
                    "normalized_total": 17,
                }
            ],
        )
    )
    _patch(monkeypatch, ledger=ledger, project_root=project_root)
    monkeypatch.setattr(dispatch, "_run_verify_base", lambda *args, **kwargs: (0, ""))

    result = dispatch.cmd_escalate(
        argparse.Namespace(ledger=tmp_path / "ledger.yaml", story_id="ST-001")
    )

    assert result == 1


def test_escalate_blocks_when_wave_slot_taken_and_marks_blocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _story_file(project_root, "ST-001", tier="economy", outputs=["src/foo.py"])
    ledger = _ledger_with(
        _story_entry(
            story_id="ST-001",
            attempts=[
                {
                    "session": "impl",
                    "tier": "economy",
                    "failure_class": "acceptance_unmet",
                    "evidence": "docs/findings/IMPL-0001.md",
                    "commit_sha": "b" * 40,
                    "normalized_total": 17,
                }
            ],
        ),
        _story_entry(
            story_id="ST-002",
            attempts=[
                {
                    "session": "impl",
                    "tier": "economy",
                    "failure_class": "acceptance_unmet",
                    "evidence": "docs/findings/IMPL-0002.md",
                    "commit_sha": "c" * 40,
                    "normalized_total": 11,
                }
            ],
            escalation_granted=True,
            status=StoryState.FAILED,
        ),
    )
    saved = _patch(monkeypatch, ledger=ledger, project_root=project_root)
    monkeypatch.setattr(dispatch, "_run_verify_base", lambda *args, **kwargs: (0, ""))
    monkeypatch.setattr(
        dispatch,
        "_git",
        lambda *args: (0, "src/foo.py\n", "") if args[:3] == ("show", "--name-only", "--format=") else (0, "", ""),
    )

    result = dispatch.cmd_escalate(
        argparse.Namespace(ledger=tmp_path / "ledger.yaml", story_id="ST-001")
    )

    assert result == 1
    entry = saved["ledger"].stories["ST-001"]
    assert entry.status == StoryState.BLOCKED
    assert entry.reason == "wave_escalation_exhausted"


def test_escalate_rejects_verify_base_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _story_file(project_root, "ST-001", tier="economy", outputs=["src/foo.py"])
    ledger = _ledger_with(
        _story_entry(
            attempts=[
                {
                    "session": "impl",
                    "tier": "economy",
                    "failure_class": "acceptance_unmet",
                    "evidence": "docs/findings/IMPL-0001.md",
                    "commit_sha": "b" * 40,
                    "normalized_total": 17,
                }
            ]
        )
    )
    _patch(monkeypatch, ledger=ledger, project_root=project_root)
    monkeypatch.setattr(dispatch, "_run_verify_base", lambda *args, **kwargs: (1, "verify-base failed"))

    result = dispatch.cmd_escalate(
        argparse.Namespace(ledger=tmp_path / "ledger.yaml", story_id="ST-001")
    )

    assert result == 1


def test_escalate_rejects_scope_violation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _story_file(project_root, "ST-001", tier="economy", outputs=["src/foo.py"])
    ledger = _ledger_with(
        _story_entry(
            attempts=[
                {
                    "session": "impl",
                    "tier": "economy",
                    "failure_class": "acceptance_unmet",
                    "evidence": "docs/findings/IMPL-0001.md",
                    "commit_sha": "b" * 40,
                    "normalized_total": 17,
                }
            ]
        )
    )
    _patch(monkeypatch, ledger=ledger, project_root=project_root)
    monkeypatch.setattr(dispatch, "_run_verify_base", lambda *args, **kwargs: (0, ""))
    monkeypatch.setattr(
        dispatch,
        "_git",
        lambda *args: (0, "src/other.py\n", "") if args[:3] == ("show", "--name-only", "--format=") else (0, "", ""),
    )

    result = dispatch.cmd_escalate(
        argparse.Namespace(ledger=tmp_path / "ledger.yaml", story_id="ST-001")
    )

    assert result == 1
