from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from orchestrator.adapters.run_state_store import FileRunLock, JsonRunStateStore
from orchestrator.entities import GateResult, PhaseRecord, PhaseStatus, Run, RunMode


@pytest.fixture
def orch_dir(request) -> Path:
    root = (
        Path(__file__).resolve().parent
        / ".scratch"
        / f"{request.node.name}-{os.getpid()}"
    )
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    yield root
    shutil.rmtree(root, ignore_errors=True)


def _sample_run() -> Run:
    return Run(
        run_id="RUN-001",
        branch="orchestrator/run-001",
        chain=["planning", "implementation", "review"],
        current_phase="implementation",
        iteration=2,
        mode=RunMode.PAUSED,
        phases=[
            PhaseRecord(
                name="planning",
                author="planner",
                reviewer="reviewer",
                status=PhaseStatus.COMPLETE,
                iteration=1,
                last_gate=GateResult(
                    passed=True,
                    errored=False,
                    hook="spec-lint",
                    error_count=0,
                    timed_out=False,
                ),
            ),
            PhaseRecord(
                name="implementation",
                author="builder",
                reviewer=None,
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=2,
                last_gate=GateResult(
                    passed=False,
                    errored=False,
                    hook="pre-commit",
                    error_count=3,
                    timed_out=True,
                ),
            ),
        ],
    )


def test_save_load_round_trip_preserves_all_fields(orch_dir: Path):
    store = JsonRunStateStore(orch_dir)
    run = _sample_run()

    store.save(run)

    assert store.load() == run


def test_atomic_write_temp_file_does_not_linger(orch_dir: Path):
    store = JsonRunStateStore(orch_dir)

    store.save(_sample_run())

    assert sorted(path.name for path in orch_dir.iterdir()) == ["run.json"]


def test_load_missing_file_returns_none(orch_dir: Path):
    store = JsonRunStateStore(orch_dir)

    assert store.load() is None


def test_exists_is_correct_before_and_after_save(orch_dir: Path):
    store = JsonRunStateStore(orch_dir)
    assert not store.exists()

    store.save(_sample_run())

    assert store.exists()


def test_lock_acquire_uses_atomic_create(
    orch_dir: Path, monkeypatch: pytest.MonkeyPatch
):
    lock = FileRunLock(orch_dir)
    open_calls: list[tuple[str, int, int]] = []
    real_open = os.open

    def recording_open(path: str, flags: int, mode: int = 0o777) -> int:
        open_calls.append((path, flags, mode))
        return real_open(path, flags, mode)

    monkeypatch.setattr(os, "open", recording_open)

    lock.acquire("RUN-LOCK")

    assert open_calls == [
        (str(lock.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    ]
    payload = json.loads((orch_dir / "run.lock").read_text(encoding="utf-8"))
    assert payload["run_id"] == "RUN-LOCK"
    assert payload["pid"] == os.getpid()
    assert lock.is_held()
    assert sorted(path.name for path in orch_dir.iterdir()) == ["run.lock"]


def test_acquire_replaces_stale_lock(orch_dir: Path):
    lock = FileRunLock(orch_dir)
    (orch_dir / "run.lock").write_text(
        json.dumps(
            {
                "run_id": "RUN-STALE",
                "pid": 0,
                "started_at": "2026-07-06T12:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    lock.acquire("RUN-NEXT")

    payload = json.loads((orch_dir / "run.lock").read_text(encoding="utf-8"))
    assert payload["run_id"] == "RUN-NEXT"
    assert payload["pid"] == os.getpid()
    assert payload["started_at"] != "2026-07-06T12:00:00+00:00"
    assert lock.is_held()


def test_is_held_returns_true_for_live_pid(orch_dir: Path):
    lock = FileRunLock(orch_dir)
    (orch_dir / "run.lock").write_text(
        json.dumps(
            {
                "run_id": "RUN-LIVE",
                "pid": os.getpid(),
                "started_at": "2026-07-06T12:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    assert lock.is_held() is True


def test_stale_lock_returns_false_from_is_held(orch_dir: Path):
    lock = FileRunLock(orch_dir)
    (orch_dir / "run.lock").write_text(
        json.dumps(
            {
                "run_id": "RUN-STALE",
                "pid": 999999,
                "started_at": "2026-07-06T12:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    assert lock.is_held() is False


def test_acquire_when_held_by_live_process_raises_runtime_error(orch_dir: Path):
    lock = FileRunLock(orch_dir)
    (orch_dir / "run.lock").write_text(
        json.dumps(
            {
                "run_id": "RUN-HELD",
                "pid": os.getpid(),
                "started_at": "2026-07-06T12:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        RuntimeError,
        match=r"run\.lock is held by live process \d+ for run RUN-HELD",
    ):
        lock.acquire("RUN-NEXT")


def test_tooling_version_round_trips(orch_dir: Path):
    store = JsonRunStateStore(orch_dir)
    run = _sample_run()
    run.tooling_version = "v0.1.0-3-gabcdef1"

    store.save(run)
    loaded = store.load()

    assert loaded is not None
    assert loaded.tooling_version == "v0.1.0-3-gabcdef1"


def test_tooling_version_none_round_trips(orch_dir: Path):
    store = JsonRunStateStore(orch_dir)
    run = _sample_run()
    assert run.tooling_version is None

    store.save(run)
    loaded = store.load()

    assert loaded is not None
    assert loaded.tooling_version is None
