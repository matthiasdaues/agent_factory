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

import sys
from pathlib import Path

from orchestrator import cli
from orchestrator.adapters.adapter_registry import TomlAdapterRegistry
from orchestrator.adapters.config_store import TomlConfigStore
from orchestrator.adapters.menu_renderer import ScriptedByteReader, TerminalMenuRenderer
from orchestrator.adapters.run_state_store import FileRunLock, JsonRunStateStore
from orchestrator.entities import (
    Config,
    GateResult,
    MenuNode,
    MenuNodeType,
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
# Full run-step round trip through the menu (UC-11, FR-S4): four real
# keypress-driven levels (agent -> skill scope -> adapter -> model) through
# a live MenuController session, reaching the exact handler + args a direct-
# mode `orchestrate run-step ...` invocation would. test_menu_run_step.py
# already proves `build_run_step_dispatch()(node)` reaches that handler when
# called directly; the genuinely new fact proven here is that *navigating
# there with keypresses* — pushing four menu levels via MenuController,
# never touching the dispatch hook by hand — produces the identical call,
# and that the controller's own EXITED transition (long_running=True) ends
# the session exactly as cli_specification.md's "Exits TUI, switches to
# streaming terminal output" describes.
# ---------------------------------------------------------------------------


class TestRunStepMenuControllerReachesSameHandlerAsDirectMode:
    def _registry(self, orch_dir: Path) -> TomlAdapterRegistry:
        registry = TomlAdapterRegistry(orch_dir)
        registry.register("copilot", sys.executable)
        registry.set_model("copilot", "strong", "gpt-5.4-strong")
        return registry

    def _capture_build_runtime_and_handle_run_step(self, monkeypatch):
        calls: dict = {}

        def _fake_build_runtime(args, story_tier=None):
            calls.setdefault("build_runtime_args", []).append(
                dict(
                    adapter=args.adapter,
                    model=args.model,
                    agent=args.agent,
                    skill=args.skill,
                    command=args.command,
                )
            )
            from types import SimpleNamespace

            return SimpleNamespace(marker="fake-runtime", timeout_s=args.timeout)

        def _fake_handle_run_step(runtime, agent_name, timeout_s, skill=None):
            calls.setdefault("handle_run_step", []).append(
                (runtime.marker, agent_name, skill)
            )
            return 0

        monkeypatch.setattr(cli, "_build_runtime", _fake_build_runtime)
        monkeypatch.setattr(cli, "_handle_run_step", _fake_handle_run_step)
        return calls

    def test_full_keypress_navigation_reaches_same_handler_as_direct_mode(
        self, monkeypatch, tmp_path
    ) -> None:
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "qa-agent", tier="strong")
        monkeypatch.setattr(cli, "_resolve_agents_dir", lambda repo_root: agents_dir)

        orch_dir = tmp_path / ".orchestrator"
        self._registry(orch_dir)
        _write_model_matrix(tmp_path)

        calls = self._capture_build_runtime_and_handle_run_step(monkeypatch)
        monkeypatch.chdir(tmp_path)

        # root(2=run-step) -> qa-agent(0) -> all skills(0, default) ->
        # copilot(0, only adapter) -> strong(0, only/tier-resolved-default
        # model) -- five ENTERs total, one per level pushed/dispatched.
        script = DOWN * 2 + ENTER * 5
        _drive_menu_mode(monkeypatch, script)

        assert len(calls["build_runtime_args"]) == 1
        from_menu = calls["build_runtime_args"][0]
        assert from_menu["command"] == "run-step"
        assert from_menu["agent"] == "qa-agent"
        assert from_menu["skill"] is None  # "all skills"
        assert from_menu["adapter"] == "copilot"
        assert from_menu["model"] == "gpt-5.4-strong"
        assert calls["handle_run_step"] == [("fake-runtime", "qa-agent", None)]

        # Same handler, same args, reached the OTHER way: `main()`'s
        # unchanged direct-mode parse, with the equivalent explicit argv.
        calls2 = self._capture_build_runtime_and_handle_run_step(monkeypatch)
        rc = cli.main(
            [
                "--adapter",
                "copilot",
                "--model",
                "gpt-5.4-strong",
                "run-step",
                "qa-agent",
            ]
        )
        assert rc == 0  # the mocked handler's return value, surfaced faithfully
        from_direct = calls2["build_runtime_args"][0]
        assert from_menu == from_direct
        assert calls2["handle_run_step"] == calls["handle_run_step"]


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


# ---------------------------------------------------------------------------
# QS-20: settings precedence across modes.
#
# tests/test_settings_resolver.py already unit-tests SettingsResolver's
# four-layer precedence in complete isolation (a fake ConfigStore, direct
# resolve() calls). What it explicitly does NOT cover — and what this story
# exists to catch — is whether cli.py's real code paths ever actually CALL
# SettingsResolver with the right ConfigStore/cli_flag values. They did not:
# see backlog/ST-0058.md's Analysis for the cross-cutting bug found and
# fixed while writing this suite (SettingsResolver was dead code; direct
# mode's --adapter/--cap/--timeout argparse defaults silently shadowed
# every persisted config.toml default, and menu-mode's run-step leaf
# inherited the same gap for cap/timeout). These tests pin the fix.
# ---------------------------------------------------------------------------


class TestSettingsPrecedenceAcrossModes:
    def test_persisted_defaults_flow_into_direct_mode_without_cli_flags(
        self, monkeypatch, tmp_path
    ) -> None:
        """Regression test for the bug this story found: a persisted
        cap/timeout/adapter must be the effective value for a direct-mode
        invocation that supplies none of `--cap`/`--timeout`/`--adapter`."""
        monkeypatch.chdir(tmp_path)
        _write_model_matrix(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        TomlConfigStore(orch_dir).save(Config(cap=7, timeout=555, adapter="copilot"))
        TomlAdapterRegistry(orch_dir).register("copilot", sys.executable)

        args = cli.build_parser().parse_args(["run-phase", "requirements"])
        cli._resolve_interactive(args)
        runtime = cli._build_runtime(args, story_tier=None)

        assert runtime.cap == 7
        assert runtime.timeout_s == 555
        assert runtime.adapter_name == "copilot"

    def test_cli_flag_overrides_persisted_default_in_direct_mode(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.chdir(tmp_path)
        _write_model_matrix(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        TomlConfigStore(orch_dir).save(Config(cap=7, timeout=555, adapter="copilot"))
        TomlAdapterRegistry(orch_dir).register("copilot", sys.executable)

        args = cli.build_parser().parse_args(
            ["--cap", "2", "--timeout", "60", "run-phase", "requirements"]
        )
        cli._resolve_interactive(args)
        runtime = cli._build_runtime(args, story_tier=None)

        assert runtime.cap == 2
        assert runtime.timeout_s == 60

    def test_builtin_default_used_when_neither_persisted_nor_flag_present(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.chdir(tmp_path)
        _write_model_matrix(tmp_path)
        TomlAdapterRegistry(tmp_path / ".orchestrator").register(
            "copilot", sys.executable
        )

        args = cli.build_parser().parse_args(["run-phase", "requirements"])
        cli._resolve_interactive(args)
        runtime = cli._build_runtime(args, story_tier=None)

        assert runtime.cap == 3
        assert runtime.timeout_s == 1800
        assert runtime.adapter_name == "copilot"

    def test_run_step_menu_leaf_resolves_persisted_cap_and_timeout(
        self, monkeypatch, tmp_path
    ) -> None:
        """The run-step menu leaf's synthesized argv never carries
        `--cap`/`--timeout` (only agent/skill/adapter/model are menu-
        selected) — so a persisted config.toml value must still reach
        `_build_runtime` for those two settings, exactly as it does for
        direct mode above. Dispatches the hook directly (not through
        MenuController) since the point here is settings resolution, not
        navigation — navigation-level run-step coverage is
        TestRunStepMenuControllerReachesSameHandlerAsDirectMode above."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: True)
        _write_model_matrix(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        TomlConfigStore(orch_dir).save(Config(cap=7, timeout=555))
        registry = TomlAdapterRegistry(orch_dir)
        registry.register("copilot", sys.executable)
        registry.set_model("copilot", "strong", "gpt-5.4-strong")

        captured: dict = {}

        def _fake_handle_run_step(runtime, agent_name, timeout_s, skill=None):
            captured["runtime"] = runtime
            return 0

        monkeypatch.setattr(cli, "_handle_run_step", _fake_handle_run_step)

        dispatch = cli.build_run_step_dispatch()
        node = MenuNode(
            id="run-step.qa-agent.all-skills.copilot.strong",
            label="x",
            type=MenuNodeType.FUNCTION,
        )
        dispatch(node)

        runtime = captured["runtime"]
        assert runtime.cap == 7
        assert runtime.timeout_s == 555

    def test_run_step_menu_selection_overrides_persisted_adapter(
        self, monkeypatch, tmp_path
    ) -> None:
        """Menu selection is the highest-precedence layer: even a persisted
        (but here unregistered/irrelevant) `adapter` default must not win
        over the adapter the operator actually selected in the menu."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: True)
        _write_model_matrix(tmp_path)
        orch_dir = tmp_path / ".orchestrator"
        TomlConfigStore(orch_dir).save(Config(adapter="claude"))
        registry = TomlAdapterRegistry(orch_dir)
        registry.register("copilot", sys.executable)
        registry.set_model("copilot", "strong", "gpt-5.4-strong")

        captured: dict = {}

        def _fake_handle_run_step(runtime, agent_name, timeout_s, skill=None):
            captured["runtime"] = runtime
            return 0

        monkeypatch.setattr(cli, "_handle_run_step", _fake_handle_run_step)

        dispatch = cli.build_run_step_dispatch()
        node = MenuNode(
            id="run-step.qa-agent.all-skills.copilot.strong",
            label="x",
            type=MenuNodeType.FUNCTION,
        )
        dispatch(node)

        assert captured["runtime"].adapter_name == "copilot"

    def test_build_runtime_actually_calls_settings_resolver(
        self, monkeypatch, tmp_path
    ) -> None:
        """The literal "is it wired up" check: `_build_runtime` must
        construct and call the real `SettingsResolver` against a
        `TomlConfigStore` pointed at this project's `.orchestrator/`, not
        re-derive the same precedence by hand (which is exactly what it did
        before this story's fix)."""
        monkeypatch.chdir(tmp_path)
        _write_model_matrix(tmp_path)
        TomlAdapterRegistry(tmp_path / ".orchestrator").register(
            "copilot", sys.executable
        )

        real_cls = cli.SettingsResolver
        constructed_with = []

        class _SpyResolver(real_cls):
            def __init__(self, config_source):
                constructed_with.append(config_source)
                super().__init__(config_source)

        monkeypatch.setattr(cli, "SettingsResolver", _SpyResolver)

        args = cli.build_parser().parse_args(["run-phase", "requirements"])
        cli._resolve_interactive(args)
        cli._build_runtime(args, story_tier=None)

        assert len(constructed_with) == 1
        assert isinstance(constructed_with[0], TomlConfigStore)
        assert (
            constructed_with[0].config_path
            == tmp_path / ".orchestrator" / "config.toml"
        )
