"""Tests for the dual-mode entry point and the master menu-mode dispatch hook.

Traces: UC-08, ADR-0016, FR-V1, FR-V2, FR-V3, FR-V4, BR-030, BR-031, T-30
(ST-0040). Covers:
  - the entry-path decision in `main()`: bare invocation -> menu mode,
    subcommand -> unchanged direct mode, non-interactive/unsupported
    terminal -> diagnostic + clean exit;
  - `build_root_dispatch`'s composition of the per-submenu hooks
    (`build_status_dispatch`/`build_backlog_dispatch` from ST-0055/57, plus
    this story's `build_manage_run_dispatch`) and its "not yet implemented"
    fallback for leaves no sub-hook claims;
  - `manage-run`'s five leaves reaching the *same* handler direct mode uses,
    with the same observable effects (run-state mutation, printed output).
"""

from __future__ import annotations

from pathlib import Path

from orchestrator import cli
from orchestrator.entities import (
    MenuNode,
    MenuNodeType,
    PhaseRecord,
    PhaseStatus,
    Run,
    RunMode,
)
from orchestrator.menu_controller import DispatchOutcome


# ---------------------------------------------------------------------------
# Entry-path decision (FR-V1, FR-V2, BR-035)
# ---------------------------------------------------------------------------


class TestEntryPathDecision:
    def test_bare_invocation_enters_menu_mode(self, monkeypatch) -> None:
        """FR-V1: an empty argv routes to `_run_menu_mode`, not `argparse`."""
        called = []
        monkeypatch.setattr(cli, "_run_menu_mode", lambda: called.append(True) or 0)

        rc = cli.main([])

        assert called == [True]
        assert rc == 0

    def test_subcommand_bypasses_menu_mode(self, monkeypatch, tmp_path) -> None:
        """FR-V2/BR-035: any subcommand never touches `_run_menu_mode`."""
        monkeypatch.chdir(tmp_path)

        def _fail_if_called():
            raise AssertionError(
                "menu mode must not be entered when a subcommand is given"
            )

        monkeypatch.setattr(cli, "_run_menu_mode", _fail_if_called)

        rc = cli.main(["status"])

        assert rc == 0

    def test_none_argv_falls_back_to_sys_argv(self, monkeypatch) -> None:
        """`main(None)` (the real console-script entry) resolves the same way
        `main([])` does when `sys.argv` carries no extra arguments."""
        monkeypatch.setattr(cli.sys, "argv", ["orchestrate"])
        called = []
        monkeypatch.setattr(cli, "_run_menu_mode", lambda: called.append(True) or 0)

        rc = cli.main(None)

        assert called == [True]
        assert rc == 0


# ---------------------------------------------------------------------------
# Non-interactive / unsupported terminal fallback (FR-V4, BR-030, BR-031, T-30)
# ---------------------------------------------------------------------------


class TestNonInteractiveFallback:
    def test_non_interactive_terminal_prints_diagnostic_and_exits_cleanly(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
        monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: True)

        rc = cli._run_menu_mode()

        assert rc == 0
        captured = capsys.readouterr()
        assert "menu mode" in captured.out.lower()
        assert "orchestrate status" in captured.out or "--help" in captured.out
        # BR-031/BR-033: no run state may be created or mutated on this path.
        assert not (tmp_path / ".orchestrator").exists()

    def test_non_interactive_stdout_also_falls_back(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: False)

        rc = cli._run_menu_mode()

        assert rc == 0
        assert not (tmp_path / ".orchestrator").exists()

    def test_supported_terminal_builds_and_runs_the_controller(
        self, monkeypatch, tmp_path
    ) -> None:
        """FR-V1: on a supported terminal, `_run_menu_mode` constructs a real
        `MenuController` (root tree + renderer + master dispatch hook) and
        drives it to completion."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: True)

        calls = {}

        class _FakeController:
            def __init__(self, root, renderer, dispatch):
                calls["root"] = root
                calls["renderer"] = renderer
                calls["dispatch"] = dispatch

            def run(self):
                calls["ran"] = True

        monkeypatch.setattr(cli, "MenuController", _FakeController)
        monkeypatch.setattr(cli, "TerminalMenuRenderer", lambda: object())

        rc = cli._run_menu_mode()

        assert rc == 0
        assert calls["ran"] is True
        assert calls["root"].id == "orchestrate"
        assert callable(calls["dispatch"])


# ---------------------------------------------------------------------------
# build_root_dispatch: composition + fallback (ADR-0016, FR-V3)
# ---------------------------------------------------------------------------


class TestBuildRootDispatch:
    def _hook(self, **overrides):
        defaults = dict(
            status_service=object(),
            backlog_store=object(),
            config_store=object(),
            adapter_registry=object(),
            matrix_path=Path("unused-model-matrix.conf"),
        )
        defaults.update(overrides)
        return defaults

    def test_routes_status_prefixed_nodes_to_status_dispatch(self, monkeypatch) -> None:
        seen = []
        monkeypatch.setattr(
            cli,
            "build_status_dispatch",
            lambda svc: lambda node: seen.append(node) or DispatchOutcome(content="x"),
        )
        monkeypatch.setattr(
            cli, "build_backlog_dispatch", lambda store: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli,
            "build_manage_run_dispatch",
            lambda: lambda node: DispatchOutcome(),
        )
        hook = cli.build_root_dispatch(**self._hook())
        node = MenuNode(
            id="status.overview", label="overview", type=MenuNodeType.DISPLAY
        )

        outcome = hook(node)

        assert seen == [node]
        assert outcome.content == "x"

    def test_routes_backlog_prefixed_nodes_to_backlog_dispatch(
        self, monkeypatch
    ) -> None:
        seen = []
        monkeypatch.setattr(
            cli, "build_status_dispatch", lambda svc: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli,
            "build_backlog_dispatch",
            lambda store: (
                lambda node: seen.append(node) or DispatchOutcome(content="y")
            ),
        )
        monkeypatch.setattr(
            cli,
            "build_manage_run_dispatch",
            lambda: lambda node: DispatchOutcome(),
        )
        hook = cli.build_root_dispatch(**self._hook())
        node = MenuNode(id="backlog.list", label="list", type=MenuNodeType.DISPLAY)

        outcome = hook(node)

        assert seen == [node]
        assert outcome.content == "y"

    def test_routes_manage_run_prefixed_nodes_to_manage_run_dispatch(
        self, monkeypatch
    ) -> None:
        seen = []
        monkeypatch.setattr(
            cli, "build_status_dispatch", lambda svc: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli, "build_backlog_dispatch", lambda store: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli,
            "build_manage_run_dispatch",
            lambda: (
                lambda node: seen.append(node) or DispatchOutcome(long_running=True)
            ),
        )
        hook = cli.build_root_dispatch(**self._hook())
        node = MenuNode(
            id="manage-run.abort", label="abort", type=MenuNodeType.FUNCTION
        )

        outcome = hook(node)

        assert seen == [node]
        assert outcome.long_running is True

    def test_routes_configure_prefixed_nodes_to_configure_defaults_dispatch(
        self, monkeypatch
    ) -> None:
        seen = []
        monkeypatch.setattr(
            cli, "build_status_dispatch", lambda svc: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli, "build_backlog_dispatch", lambda store: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli,
            "build_manage_run_dispatch",
            lambda: lambda node: DispatchOutcome(),
        )
        monkeypatch.setattr(
            cli,
            "build_configure_defaults_dispatch",
            lambda config_store, adapter_registry: (
                lambda node: seen.append(node) or DispatchOutcome(long_running=False)
            ),
        )
        hook = cli.build_root_dispatch(**self._hook())
        node = MenuNode(
            id="configure.defaults.timeout",
            label="timeout",
            type=MenuNodeType.FUNCTION,
        )

        outcome = hook(node)

        assert seen == [node]
        assert outcome.long_running is False

    def test_routes_configure_model_matrix_prefixed_nodes_to_its_own_dispatch(
        self, monkeypatch
    ) -> None:
        """`configure.model-matrix.` must route to
        `build_configure_model_matrix_dispatch`, not fall through to the more
        general `configure.` branch (`configure_defaults_dispatch`) — same
        precedence `configure.cli-list.`/`configure.cli.` already require
        (ST-0050)."""
        seen = []
        monkeypatch.setattr(
            cli, "build_status_dispatch", lambda svc: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli, "build_backlog_dispatch", lambda store: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli,
            "build_manage_run_dispatch",
            lambda: lambda node: DispatchOutcome(),
        )
        monkeypatch.setattr(
            cli,
            "build_configure_defaults_dispatch",
            lambda config_store, adapter_registry: (
                lambda node: (_ for _ in ()).throw(
                    AssertionError("must not reach configure_defaults_dispatch")
                )
            ),
        )
        monkeypatch.setattr(
            cli,
            "build_configure_model_matrix_dispatch",
            lambda matrix_path, adapter_registry: (
                lambda node: seen.append(node) or DispatchOutcome(content="z")
            ),
        )
        hook = cli.build_root_dispatch(**self._hook())
        node = MenuNode(
            id="configure.model-matrix.show", label="show", type=MenuNodeType.DISPLAY
        )

        outcome = hook(node)

        assert seen == [node]
        assert outcome.content == "z"

    def test_unwired_leaf_falls_back_honestly_without_crashing(
        self, monkeypatch, capsys
    ) -> None:
        """A leaf under a not-yet-populated menu (init/run-phase) must never
        crash the menu — just say so (ADR-0016). `run-step` is wired
        (ST-0053) so it no longer exercises this fallback — see
        tests/test_menu_run_step.py instead."""
        monkeypatch.setattr(
            cli, "build_status_dispatch", lambda svc: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli, "build_backlog_dispatch", lambda store: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli,
            "build_manage_run_dispatch",
            lambda: lambda node: DispatchOutcome(),
        )
        hook = cli.build_root_dispatch(**self._hook())
        node = MenuNode(
            id="run-phase.some-phase", label="some-phase", type=MenuNodeType.FUNCTION
        )

        outcome = hook(node)

        assert outcome.long_running is False
        captured = capsys.readouterr()
        assert "not yet implemented" in (captured.out + captured.err).lower()

    def test_dispatch_hook_exceptions_do_not_propagate(self, monkeypatch) -> None:
        """A raising handler must not crash the menu loop — the dispatch hook
        reports the error and lets the controller return to the menu."""
        monkeypatch.setattr(
            cli, "build_status_dispatch", lambda svc: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli, "build_backlog_dispatch", lambda store: lambda node: DispatchOutcome()
        )

        def _raising():
            def _dispatch(node):
                raise RuntimeError("boom")

            return _dispatch

        monkeypatch.setattr(cli, "build_manage_run_dispatch", _raising)
        hook = cli.build_root_dispatch(**self._hook())
        node = MenuNode(
            id="manage-run.abort", label="abort", type=MenuNodeType.FUNCTION
        )

        outcome = hook(node)  # must not raise

        assert outcome.long_running is False


# ---------------------------------------------------------------------------
# manage-run leaves: same handler, same observable effects as direct mode
# (FR-V3) — mirrors test_cli.py's TestAbortHandler / TestReleaseHandler /
# TestApproveRejectHandler fixtures so the assertions are directly comparable.
# ---------------------------------------------------------------------------


def _write_run_json(orch_dir: Path, run: Run) -> None:
    from orchestrator.adapters.run_state_store import JsonRunStateStore

    JsonRunStateStore(orch_dir).save(run)


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


class TestManageRunDispatchAbort:
    def test_abort_matches_direct_mode(self, monkeypatch, tmp_path, capsys) -> None:
        from orchestrator.adapters.run_state_store import FileRunLock, JsonRunStateStore

        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        run = _make_paused_run()
        JsonRunStateStore(orch_dir).save(run)
        FileRunLock(orch_dir).acquire(run.run_id)

        dispatch = cli.build_manage_run_dispatch()
        node = MenuNode(
            id="manage-run.abort", label="abort", type=MenuNodeType.FUNCTION
        )

        outcome = dispatch(node)

        assert outcome.long_running is False
        captured = capsys.readouterr()
        assert captured.out.strip() == "Run aborted."
        stored = JsonRunStateStore(orch_dir).load()
        assert stored.mode == RunMode.COMPLETE
        assert not (orch_dir / "run.lock").exists()


class TestManageRunDispatchRelease:
    def test_release_matches_direct_mode(self, monkeypatch, tmp_path, capsys) -> None:
        from orchestrator.adapters.run_state_store import FileRunLock, JsonRunStateStore

        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        run = _make_halted_run(halted_from=PhaseStatus.GATING)
        JsonRunStateStore(orch_dir).save(run)
        FileRunLock(orch_dir).acquire(run.run_id)

        dispatch = cli.build_manage_run_dispatch()
        node = MenuNode(
            id="manage-run.release", label="release", type=MenuNodeType.FUNCTION
        )

        outcome = dispatch(node)

        assert outcome.long_running is False
        stored = JsonRunStateStore(orch_dir).load()
        assert stored.mode == RunMode.PAUSED
        phase = [p for p in stored.phases if p.name == "requirements"][0]
        assert phase.status == PhaseStatus.GATING
        assert phase.halted_from is None


class TestManageRunDispatchApproveReject:
    def test_approve_paused_run_matches_direct_mode(
        self, monkeypatch, tmp_path
    ) -> None:
        from orchestrator.entities import GateResult

        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        (orch_dir / "findings").mkdir(parents=True, exist_ok=True)
        (tmp_path / "agents").mkdir()
        run = _make_paused_run()
        run.phases[0].last_gate = GateResult(
            passed=True, errored=False, hook="pre-commit", error_count=0
        )
        _write_run_json(orch_dir, run)

        dispatch = cli.build_manage_run_dispatch()
        node = MenuNode(
            id="manage-run.approve", label="approve", type=MenuNodeType.FUNCTION
        )

        outcome = dispatch(node)

        assert outcome.long_running is False
        from orchestrator.adapters.run_state_store import JsonRunStateStore

        stored = JsonRunStateStore(orch_dir).load()
        assert stored.current_phase == "architecture"

    def test_reject_with_no_note_matches_direct_mode_default(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        (tmp_path / "agents").mkdir()
        _write_run_json(orch_dir, _make_paused_run())

        dispatch = cli.build_manage_run_dispatch()
        node = MenuNode(
            id="manage-run.reject", label="reject", type=MenuNodeType.FUNCTION
        )

        outcome = dispatch(node)

        assert outcome.long_running is False
        from orchestrator.adapters.run_state_store import JsonRunStateStore

        stored = JsonRunStateStore(orch_dir).load()
        assert stored.mode == RunMode.HALTED
        phase = [p for p in stored.phases if p.name == "requirements"][0]
        assert phase.rejection_note is None

    def test_no_active_run_does_not_crash(self, monkeypatch, tmp_path) -> None:
        monkeypatch.chdir(tmp_path)
        dispatch = cli.build_manage_run_dispatch()
        node = MenuNode(
            id="manage-run.approve", label="approve", type=MenuNodeType.FUNCTION
        )

        outcome = dispatch(node)  # must not raise

        assert outcome.long_running is False
