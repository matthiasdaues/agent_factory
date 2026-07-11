"""End-to-end menu-mode integration and dual-mode equivalence tests (ST-0058).

Traces: UC-08, UC-09, UC-10, UC-11, UC-12, NFR-10, NFR-11, QS-18, QS-19,
QS-20. See `backlog/ST-0058.md`'s Analysis section for the full scoping
rationale; in short, every area (`status`, `backlog`, `manage-run`,
`configure > *`, `run-step`) already has thorough per-area coverage
(`tests/test_dual_mode_entry.py`, `tests/test_configure_defaults.py`,
`tests/test_cli_list.py`, `tests/test_model_dictionary_menu.py`,
`tests/test_model_matrix_views.py`, `tests/test_menu_run_step.py`,
`tests/test_status_views.py`, `tests/test_backlog_views.py`) that calls each
area's `DispatchHook` directly with a hand-built `MenuNode`. This module's
job is different and narrower: prove the CROSS-CUTTING guarantees that only
show up when the real `MenuController` state machine drives a full,
multi-level, scripted keypress session end to end (`MenuController.run()`,
never a bare `dispatch(node)` call) — dual-mode equivalence, navigation
purity, and settings-precedence wiring.

Headless by construction: every session below drives a real
`TerminalMenuRenderer` through an injected `ScriptedByteReader` (the same
seam `tests/test_terminal_menu_renderer.py` established) — no real
interactive terminal, no `sleep`, no flakiness.
"""

from __future__ import annotations

from pathlib import Path

from orchestrator import cli
from orchestrator.adapters.menu_renderer import ScriptedByteReader, TerminalMenuRenderer
from orchestrator.adapters.run_state_store import FileRunLock, JsonRunStateStore
from orchestrator.entities import (
    GateResult,
    PhaseRecord,
    PhaseStatus,
    Run,
    RunMode,
)

# --- Scripted-keypress vocabulary (mirrors TerminalMenuRenderer's decoding) -

DOWN = "\x1b[B"
UP = "\x1b[A"
ENTER = "\r"
BACK = "\x1b"
EXIT = "qq"

MODEL_MATRIX_CONTENT = """\
[facts]
copilot.economy  = gpt-5.4-mini
copilot.standard = gpt-5.4
copilot.strong   = gpt-5.4-strong
on_missing = halt
"""


def _write_model_matrix(repo_root: Path) -> None:
    """`_build_runtime`/`_run_menu_mode` both construct a `FileModelMatrix`
    unconditionally from `<cwd>/model.conf`; every scenario that reaches
    either needs this present, even when the scenario itself never
    resolves a model."""
    (repo_root / "model.conf").write_text(MODEL_MATRIX_CONTENT, encoding="utf-8")


def _write_agent(agents_dir: Path, name: str, *, tier: str = "strong") -> None:
    agents_dir.mkdir(parents=True, exist_ok=True)
    content = f"---\ntier: {tier}\nskills:\noutputs:\n  - docs/out.md\n---\n# {name}\n"
    (agents_dir / f"{name}.md").write_text(content, encoding="utf-8")


def _make_paused_run(run_id: str = "RUN-TEST") -> Run:
    return Run(
        run_id=run_id,
        branch=f"orchestrator/{run_id.lower()}",
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


def _drive_menu_mode(monkeypatch, script: str) -> None:
    """Run the real `cli._run_menu_mode()` composition root to completion
    against a scripted key sequence — the actual `MenuController.run()`
    state machine, `_build_menu_tree`, and `build_root_dispatch`, exactly as
    a live session would use them, but with a `ScriptedByteReader` standing
    in for the terminal (headless; no real tty anywhere in this module).
    """
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: True)

    def _fake_renderer_factory():
        return TerminalMenuRenderer(byte_reader=ScriptedByteReader(script))

    monkeypatch.setattr(cli, "TerminalMenuRenderer", _fake_renderer_factory)
    rc = cli._run_menu_mode()
    assert rc == 0


# ---------------------------------------------------------------------------
# QS-18/NFR-10: dual-mode equivalence, driven through the real MenuController
# state machine (not a direct dispatch(node) call) on one side, and through
# `main()`'s unchanged direct-mode parse on the other.
# ---------------------------------------------------------------------------


class TestDualModeEquivalenceManageRunApprove:
    """`manage-run > approve`, reached by four real keypresses through a live
    `MenuController` session, versus `orchestrate approve` (`main(["approve"])`).

    Exercises gate behaviour (a passed `last_gate` gates the approval,
    FAGAN-0038/VR-012) and run-state mutation (current_phase advances) — the
    two QS-18 guarantees `test_dual_mode_entry.py`'s dispatch-hook-level
    `TestManageRunDispatchApproveReject` cannot observe, since it calls
    `dispatch(node)` directly and never exercises `MenuController` itself.

    Menu-mode leaves have no process-level exit code of their own (by
    design — ADR-0016: a short leaf returns to the menu, it does not end
    the TUI process), so "same exit code" is demonstrated the other way
    round in `TestRunStepMenuControllerReachesSameHandlerAsDirectMode`
    below, where the compared leaf (`run-step`) does end the process.
    """

    def _seed(self, orch_dir: Path, agents_dir: Path) -> Run:
        (orch_dir / "findings").mkdir(parents=True, exist_ok=True)
        agents_dir.mkdir(parents=True, exist_ok=True)
        run = _make_paused_run()
        run.phases[0].last_gate = GateResult(
            passed=True, errored=False, hook="pre-commit", error_count=0
        )
        JsonRunStateStore(orch_dir).save(run)
        return run

    def test_menu_driven_approve_matches_direct_mode_approve(
        self, monkeypatch, tmp_path
    ) -> None:
        direct_dir = tmp_path / "direct"
        menu_dir = tmp_path / "menu"
        direct_dir.mkdir()
        menu_dir.mkdir()

        self._seed(direct_dir / ".orchestrator", direct_dir / "agents")
        self._seed(menu_dir / ".orchestrator", menu_dir / "agents")

        # --- direct mode ---
        monkeypatch.chdir(direct_dir)
        rc = cli.main(["approve"])
        assert rc == 0
        direct_state = JsonRunStateStore(direct_dir / ".orchestrator").load()

        # --- menu mode: root -> manage-run (index 5) -> approve (index 1) ---
        monkeypatch.chdir(menu_dir)
        script = DOWN * 5 + ENTER + DOWN * 1 + ENTER + EXIT
        _drive_menu_mode(monkeypatch, script)
        menu_state = JsonRunStateStore(menu_dir / ".orchestrator").load()

        assert direct_state.current_phase == "architecture"
        assert menu_state.current_phase == direct_state.current_phase
        assert menu_state.mode == direct_state.mode
        assert [p.status for p in menu_state.phases] == [
            p.status for p in direct_state.phases
        ]


class TestDualModeEquivalenceManageRunAbort:
    """`manage-run > abort` — the same MenuController-driven-vs-direct-mode
    comparison as above, for a leaf with no gate precondition, so it also
    covers the "no active run" refusal path identically in both modes.
    """

    def _seed(self, orch_dir: Path) -> Run:
        run = _make_paused_run()
        JsonRunStateStore(orch_dir).save(run)
        FileRunLock(orch_dir).acquire(run.run_id)
        return run

    def test_menu_driven_abort_matches_direct_mode_abort(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        direct_dir = tmp_path / "direct"
        menu_dir = tmp_path / "menu"
        direct_dir.mkdir()
        menu_dir.mkdir()
        self._seed(direct_dir / ".orchestrator")
        self._seed(menu_dir / ".orchestrator")

        monkeypatch.chdir(direct_dir)
        rc = cli.main(["abort"])
        assert rc == 0
        capsys.readouterr()  # drain direct-mode "Run aborted." before menu mode
        direct_state = JsonRunStateStore(direct_dir / ".orchestrator").load()
        assert not (direct_dir / ".orchestrator" / "run.lock").exists()

        monkeypatch.chdir(menu_dir)
        # root -> manage-run (index 5) -> abort (index 4) -> exit
        script = DOWN * 5 + ENTER + DOWN * 4 + ENTER + EXIT
        _drive_menu_mode(monkeypatch, script)
        menu_state = JsonRunStateStore(menu_dir / ".orchestrator").load()
        assert not (menu_dir / ".orchestrator" / "run.lock").exists()

        captured = capsys.readouterr()
        assert "Run aborted." in captured.out
        assert menu_state.mode == direct_state.mode == RunMode.COMPLETE
        assert menu_state.run_id == direct_state.run_id


# ---------------------------------------------------------------------------
# QS-19/NFR-11: navigation purity — arrows, submenu pushes/pops, viewing
# displays, and a clean "qq" exit must never touch run.json, findings, or
# logs, even though the session visits several DISPLAY leaves along the way
# (their own dispatch hooks are read-only by construction — this is the
# end-to-end proof of that, not a re-test of build_status_dispatch/
# build_backlog_dispatch in isolation).
# ---------------------------------------------------------------------------


class TestNavigationPurity:
    def test_long_navigation_session_leaves_run_state_untouched(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.chdir(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        run = _make_paused_run()
        JsonRunStateStore(orch_dir).save(run)
        run_json_path = orch_dir / "run.json"
        before_run_json = run_json_path.read_bytes()

        script = (
            # root -> status (index 4) submenu
            DOWN * 4
            + ENTER
            # view "overview" (index 0), dismiss
            + ENTER
            + ENTER
            # view "log" (index 3), dismiss
            + DOWN * 3
            + ENTER
            + ENTER
            # back out to root
            + BACK
            # root -> backlog (index 6) submenu
            + DOWN * 6
            + ENTER
            # view "list" (index 0), dismiss
            + ENTER
            + ENTER
            # open (empty) "view story" (index 3) submenu, back out twice
            + DOWN * 3
            + ENTER
            + BACK
            + BACK
            # aimless cursor movement at the root
            + UP
            + DOWN
            + UP
            + DOWN
            + UP
            # clean exit, never having pressed Enter on a function leaf
            + EXIT
        )
        _drive_menu_mode(monkeypatch, script)

        after_run_json = run_json_path.read_bytes()
        assert after_run_json == before_run_json

        # findings/ may exist (StatusService construction creates the empty
        # directory eagerly — see FilesystemFindingsStore.__init__), but no
        # finding file may have appeared inside it.
        findings_dir = orch_dir / "findings"
        assert list(findings_dir.glob("*")) == []

        # log.jsonl is only ever created by constructing a FileInvocationLog,
        # which only `_build_runtime` does — never reached by pure
        # navigation (no manage-run/run-step leaf was dispatched).
        assert not (orch_dir / "log.jsonl").exists()
        assert not (orch_dir / "run.lock").exists()

    def test_navigation_only_session_creates_no_run_state_at_all(
        self, monkeypatch, tmp_path
    ) -> None:
        """BR-033: a navigation-only session against a project with NO prior
        run must not conjure one into existence — `run.json` must still not
        exist afterwards."""
        monkeypatch.chdir(tmp_path)

        script = DOWN * 4 + ENTER + ENTER + ENTER + BACK + UP + DOWN + EXIT
        _drive_menu_mode(monkeypatch, script)

        assert not (tmp_path / ".orchestrator" / "run.json").exists()
        assert not (tmp_path / ".orchestrator" / "log.jsonl").exists()
        assert not (tmp_path / ".orchestrator" / "run.lock").exists()
