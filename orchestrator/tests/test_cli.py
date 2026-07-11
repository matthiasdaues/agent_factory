from __future__ import annotations

import pytest
from pathlib import Path

from orchestrator.cli import build_parser, main
from orchestrator.entities import (
    PhaseRecord,
    PhaseStatus,
    Run,
    RunMode,
)


@pytest.mark.parametrize(
    ("argv", "command"),
    [
        (["status"], "status"),
        (["abort"], "abort"),
        (["release"], "release"),
        (["approve"], "approve"),
        (["reject"], "reject"),
    ],
)
def test_parser_recognizes_all_subcommands(argv: list[str], command: str) -> None:
    args = build_parser().parse_args(argv)

    assert args.command == command


def test_unknown_subcommand_fails() -> None:
    with pytest.raises(SystemExit) as excinfo:
        build_parser().parse_args(["unknown-command"])

    assert excinfo.value.code != 0


def test_init_subcommand_accepted() -> None:
    args = build_parser().parse_args(["init"])

    assert args.command == "init"


def test_init_cli_flag() -> None:
    args = build_parser().parse_args(["init", "--cli", "copilot"])

    assert args.cli_name == "copilot"


def test_init_cli_defaults_to_none() -> None:
    args = build_parser().parse_args(["init"])

    assert args.cli_name is None


def test_init_positional_project() -> None:
    args = build_parser().parse_args(["init", "my-project", "--cli", "claude"])

    assert args.project == "my-project"
    assert args.cli_name == "claude"


def test_reject_note_flag_is_captured() -> None:
    args = build_parser().parse_args(["reject", "--note", "needs rework"])

    assert args.note == "needs rework"


def test_reject_note_defaults_to_none() -> None:
    args = build_parser().parse_args(["reject"])

    assert args.note is None


# ---------------------------------------------------------------------------
# FAGAN-0029: Handler-level tests exercising the main() dispatch path
# ---------------------------------------------------------------------------


def _write_run_json(orch_dir: Path, run: Run) -> None:
    """Persist a run.json so the CLI can load it."""
    from orchestrator.adapters.run_state_store import JsonRunStateStore

    store = JsonRunStateStore(orch_dir)
    store.save(run)


def _make_paused_run() -> Run:
    return Run(
        run_id="RUN-TEST",
        branch="orchestrator/run-test",
        chain=["requirements", "architecture"],
        current_phase="requirements",
        iteration=0,
        mode=RunMode.PAUSED,
        phases=[
            PhaseRecord(
                name="requirements",
                author="requirements-agent",
                reviewer="spec-review-agent",
                status=PhaseStatus.AWAITING_APPROVAL,
                iteration=0,
            ),
            PhaseRecord(
                name="architecture",
                author="architecture-agent",
                reviewer="architecture-review-agent",
                status=PhaseStatus.PENDING,
            ),
        ],
    )


def _make_halted_run(*, halted_from: PhaseStatus | None = PhaseStatus.GATING) -> Run:
    return Run(
        run_id="RUN-TEST",
        branch="orchestrator/run-test",
        chain=["requirements", "architecture"],
        current_phase="requirements",
        iteration=3,
        mode=RunMode.HALTED,
        phases=[
            PhaseRecord(
                name="requirements",
                author="requirements-agent",
                reviewer="spec-review-agent",
                status=PhaseStatus.HALTED,
                iteration=3,
                halted_from=halted_from,
            ),
            PhaseRecord(
                name="architecture",
                author="architecture-agent",
                reviewer="architecture-review-agent",
                status=PhaseStatus.PENDING,
            ),
        ],
    )


class TestStatusHandler:
    """FAGAN-0024/0029: status works without model-matrix.conf."""

    def test_status_no_active_run(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        rc = main(["status"])
        assert rc == 0

    def test_status_with_active_run(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        _write_run_json(orch_dir, _make_paused_run())
        rc = main(["status"])
        assert rc == 0


class TestApproveRejectHandler:
    """FAGAN-0024/0029: approve/reject work without model-matrix.conf."""

    def test_approve_no_run_fails(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        rc = main(["approve"])
        assert rc == 1

    def test_reject_no_run_fails(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        rc = main(["reject"])
        assert rc == 1

    def test_approve_paused_run(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        orch_findings = orch_dir / "findings"
        orch_findings.mkdir(parents=True, exist_ok=True)
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        # Need a minimal gate pass for approve to work
        run = _make_paused_run()
        from orchestrator.entities import GateResult

        run.phases[0].last_gate = GateResult(
            passed=True,
            errored=False,
            hook="pre-commit",
            error_count=0,
        )
        _write_run_json(orch_dir, run)
        rc = main(["approve"])
        assert rc == 0

    def test_reject_with_note(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        _write_run_json(orch_dir, _make_paused_run())
        rc = main(["reject", "--note", "not ready"])
        assert rc == 0
        # Verify the run is now halted with the note
        from orchestrator.adapters.run_state_store import JsonRunStateStore

        stored = JsonRunStateStore(orch_dir).load()
        assert stored.mode == RunMode.HALTED
        phase = [p for p in stored.phases if p.name == "requirements"][0]
        assert phase.rejection_note == "not ready"


class TestAbortHandler:
    def test_abort_active_run(self, tmp_path, monkeypatch, capsys) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        from orchestrator.adapters.run_state_store import FileRunLock, JsonRunStateStore

        run = _make_paused_run()
        JsonRunStateStore(orch_dir).save(run)
        FileRunLock(orch_dir).acquire(run.run_id)

        rc = main(["abort"])

        assert rc == 0
        captured = capsys.readouterr()
        assert captured.out.strip() == "Run aborted."
        stored = JsonRunStateStore(orch_dir).load()
        assert stored is not None
        assert stored.mode == RunMode.COMPLETE
        assert not (orch_dir / "run.lock").exists()

    def test_abort_no_active_run_fails(self, tmp_path, monkeypatch, capsys) -> None:
        monkeypatch.chdir(tmp_path)

        rc = main(["abort"])

        assert rc == 1
        captured = capsys.readouterr()
        assert captured.err.strip() == "no active run"

    def test_abort_refuses_when_lock_held_by_other_process(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        from orchestrator.adapters.run_state_store import JsonRunStateStore
        import json

        run = _make_paused_run()
        JsonRunStateStore(orch_dir).save(run)
        # Write a lock file with PID 1 (init — always alive, never us)
        lock_path = orch_dir / "run.lock"
        lock_path.write_text(
            json.dumps({"run_id": run.run_id, "pid": 1, "started_at": "t"})
        )

        rc = main(["abort"])

        assert rc == 1
        captured = capsys.readouterr()
        assert "held by another process" in captured.err

    def test_abort_complete_run_fails(self, tmp_path, monkeypatch, capsys) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        from orchestrator.adapters.run_state_store import JsonRunStateStore

        run = _make_paused_run()
        run.mode = RunMode.COMPLETE
        JsonRunStateStore(orch_dir).save(run)

        rc = main(["abort"])

        assert rc == 1
        captured = capsys.readouterr()
        assert captured.err.strip() == "no active run"


class TestReleaseHandler:
    def test_release_halted_run_restores_phase(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        from orchestrator.adapters.run_state_store import FileRunLock, JsonRunStateStore

        run = _make_halted_run(halted_from=PhaseStatus.GATING)
        JsonRunStateStore(orch_dir).save(run)
        FileRunLock(orch_dir).acquire(run.run_id)

        rc = main(["release"])

        assert rc == 0
        captured = capsys.readouterr()
        assert captured.out.strip() == (
            "Released phase 'requirements' back to gating. "
            "Continue the phase with the factory scripts."
        )
        stored = JsonRunStateStore(orch_dir).load()
        assert stored is not None
        assert stored.mode == RunMode.PAUSED
        assert stored.iteration == 0
        phase = [p for p in stored.phases if p.name == "requirements"][0]
        assert phase.status == PhaseStatus.GATING
        assert phase.iteration == 0
        assert phase.halted_from is None
        assert not (orch_dir / "run.lock").exists()

    def test_release_non_halted_run_refuses(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        from orchestrator.adapters.run_state_store import JsonRunStateStore

        JsonRunStateStore(orch_dir).save(_make_paused_run())

        rc = main(["release"])

        assert rc == 1
        captured = capsys.readouterr()
        assert captured.err.strip() == "Run is not halted."

    def test_release_without_halted_from_refuses(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        from orchestrator.adapters.run_state_store import JsonRunStateStore

        JsonRunStateStore(orch_dir).save(_make_halted_run(halted_from=None))

        rc = main(["release"])

        assert rc == 1
        captured = capsys.readouterr()
        assert (
            captured.err.strip() == "Cannot release: no halted_from recorded (VR-029)."
        )


# run-all removed (deferred, NG6): the FAGAN-0025 run-all active-run guard no
# longer applies — a bare `run-all` is now an unknown command (exit 3), covered
# by test_fagan_fixes_039_048_cli.test_run_all_is_no_longer_a_command_returns_3.
