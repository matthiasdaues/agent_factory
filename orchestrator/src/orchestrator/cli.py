from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from types import SimpleNamespace
from typing import Callable
from uuid import uuid4

from orchestrator.entities import (
    AgentInvocation,
    AgentRole,
    Config,
    InvocationContext,
    MenuNode,
    MenuNodeType,
    Run,
    PhaseRecord,
    PhaseStatus,
    RunMode,
    Tier,
)
from orchestrator.ports import (
    AdapterRegistry,
    AgentInfo,
    ConfigStore,
    Logger,
    ModelMatrix,
    RunStateStore,
    RunLock,
)
from orchestrator.menu_controller import DispatchHook, DispatchOutcome, MenuController
from orchestrator.menu_tree import build_root_menu
from orchestrator.adapters.menu_renderer import TerminalMenuRenderer
from orchestrator.phase_runner import PhaseRunner
from orchestrator.status_service import (
    FindingSummary,
    LogEntry,
    PhaseDetail,
    RunStatus,
    StatusService,
)
from orchestrator.approval_service import ApprovalService
from orchestrator.loop_policy import LoopPolicy
from orchestrator.model_resolver import ConfigError, ModelResolver
from orchestrator.settings_resolver import BUILTIN_DEFAULTS, SettingsResolver
from orchestrator.adapters.copilot import CopilotAdapter
from orchestrator.adapters.finding_ingest import DefaultFindingIngestor
from orchestrator.adapters.findings_store import FilesystemFindingsStore
from orchestrator.adapters.run_state_store import JsonRunStateStore, FileRunLock
from orchestrator.adapters.gate_runner import WorkingTreeGate
from orchestrator.adapters.agent_registry import MarkdownAgentRegistry
from orchestrator.adapters.prompt_composer import (
    FilePromptComposer,
    skill_scoped_call_to_action,
)
from orchestrator.adapters.invocation_log import FileInvocationLog
from orchestrator.adapters.model_matrix import FileModelMatrix
from orchestrator.adapters.backlog_store import MarkdownBacklogStore
from orchestrator.adapters.config_store import ConfigStoreError, TomlConfigStore
from orchestrator.adapters.adapter_registry import TomlAdapterRegistry
from orchestrator.adapters.adapter_detect import DetectedAdapter, detect_candidates

_PHASE_ORDER = ["requirements", "architecture", "planning", "implementation"]


def _tooling_root() -> Path:
    """Resolve the agent_factory repo root from the package location.

    Works with editable installs (uv tool install --editable .) where
    __file__ points into the source tree:
      .../agent_factory/orchestrator/src/orchestrator/cli.py → parents[3] = agent_factory/

    Post-pivot (ADR-0010 superseded by the current factory/-layout — see
    ST-0064), the tooling ingredients live under factory/agents and
    factory/skills, not bare agents/skills at the root.
    """
    root = Path(__file__).resolve().parents[3]
    if (root / "factory" / "agents").is_dir() and (
        root / "factory" / "skills"
    ).is_dir():
        return root
    raise RuntimeError(
        "Cannot locate agent_factory tooling root.\n"
        "Expected factory/agents and factory/skills at: " + str(root) + "\n"
        "Install with: cd agent_factory/orchestrator && uv tool install --editable ."
    )


def _tooling_version() -> str | None:
    """Get the git describe / commit hash of the tooling root."""
    try:
        root = _tooling_root()
    except RuntimeError:
        return None
    for cmd in (
        ["git", "describe", "--tags", "--always", "--dirty"],
        ["git", "rev-parse", "--short", "HEAD"],
    ):
        result = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return None


class _SystemClock:
    def now_ms(self) -> int:
        return int(time.time() * 1000)


class _ExplicitModelResolver:
    def __init__(self, resolver: ModelResolver, explicit_model: str | None) -> None:
        self._resolver = resolver
        self._explicit_model = explicit_model

    def resolve(
        self,
        phase: str,
        classification: str | None = None,
        explicit_model: str | None = None,
    ) -> str | None:
        return self._resolver.resolve(
            phase,
            classification=classification,
            explicit_model=explicit_model or self._explicit_model,
        )


@dataclass(frozen=True)
class _Runtime:
    repo_root: Path
    orch_dir: Path
    agents_dir: Path
    run_store: RunStateStore
    run_lock: RunLock
    approval_service: ApprovalService
    status_service: StatusService
    phase_runner: PhaseRunner
    prompt_composer: FilePromptComposer
    adapter: CopilotAdapter
    agent_registry: MarkdownAgentRegistry
    logger: Logger
    # BR-040/FR-Q3/QS-20: the *resolved* effective settings (SettingsResolver
    # output, not the raw `--timeout`/`--cap`/`--adapter` flags, which may be
    # `None` when the flag was omitted). `_handle_run_step` reads
    # `timeout_s` from here instead of `args.timeout`; `cap`/`adapter_name`
    # are exposed for callers (and tests — see
    # tests/test_integration_menu_mode.py's settings-precedence coverage)
    # that need to observe what was actually resolved, since
    # `phase_runner`/`adapter` only hold that value inside their own private
    # state. Defaulted to the built-in values so the handful of tests that
    # construct a `_Runtime` fake directly, without exercising settings
    # resolution, keep working unchanged.
    timeout_s: int = BUILTIN_DEFAULTS["timeout"]
    cap: int = BUILTIN_DEFAULTS["cap"]
    adapter_name: str = BUILTIN_DEFAULTS["adapter"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orchestrate")
    parser.add_argument("--model")
    parser.add_argument(
        "--no-interactive",
        dest="no_interactive",
        action="store_true",
        help="Force headless invocation, overriding the interactive default",
    )
    # BR-040/FR-Q3/QS-20: `default=None` (not the built-in value) is
    # deliberate — it is what lets `_build_runtime` tell "operator typed
    # this flag" apart from "operator typed nothing" and resolve the
    # effective value through `SettingsResolver`'s
    # `menu selection > CLI flag > config.toml > built-in default` chain
    # instead of a CLI-flag value that always wins by construction (see
    # ST-0058's Analysis for the bug this replaced: these three flags used
    # to default to the built-in values directly, which meant a persisted
    # `configure > defaults` value was *always* shadowed by argparse's own
    # default, never actually read for a real run).
    parser.add_argument("--adapter", default=None)
    parser.add_argument("--cap", type=int, default=None)
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help=(
            "Per-invocation timeout in seconds "
            "(resolved via config.toml/built-in default of 1800 when omitted)"
        ),
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    run_step = subparsers.add_parser("run-step")
    run_step.add_argument("agent")
    run_step.add_argument(
        "--skill",
        default=None,
        help=(
            "Run only this declared skill's workflow step (UC-11). "
            "Omit, or pass 'all skills', for the full-workflow run-step (BR-052)."
        ),
    )

    run_phase = subparsers.add_parser("run-phase")
    run_phase.add_argument("phase", choices=_PHASE_ORDER)
    run_phase.add_argument(
        "--story",
        default=None,
        help="Story ID (ST-NNNN) for classification-based model selection",
    )

    subparsers.add_parser("status")
    subparsers.add_parser("resume")
    subparsers.add_parser("abort")
    subparsers.add_parser("release")
    subparsers.add_parser("approve")
    reject_parser = subparsers.add_parser("reject")
    reject_parser.add_argument("--note", default=None, help="Optional rejection reason")

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument(
        "project",
        nargs="?",
        default=None,
        help="Project directory to create (default: cwd)",
    )
    init_parser.add_argument(
        "--cli",
        dest="cli_name",
        default=None,
        choices=list(_CLI_INSTRUCTION_FILES.keys()),
        help="Target CLI for instruction file",
    )

    return parser


def main(argv=None) -> int:
    # ST-0040/FR-V1/FR-V2/BR-035: resolve the effective argv *before*
    # touching argparse — `build_parser()`'s subparsers are `required=True`,
    # so `parse_args([])` would itself raise a usage SystemExit before any
    # menu-mode decision could run. A bare invocation (no argv at all) is
    # the ONLY thing that ever routes to menu mode; any subcommand — even
    # just flags with no subcommand, which argparse will reject exactly as
    # it does today — falls straight through to the unchanged direct-mode
    # parse below.
    effective_argv = list(sys.argv[1:]) if argv is None else list(argv)
    if not effective_argv:
        return _run_menu_mode()

    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # FAGAN-0047: argparse's own default usage-error code is 2, but this
        # CLI reserves exit code 2 exclusively for HALTED runs. Remap any
        # non-zero argparse exit (usage/argument errors) to 3.
        return 0 if exc.code == 0 else 3

    try:
        if args.command == "init":
            return _handle_init(args)

        # FAGAN-0024: light commands don't need the full runtime
        # (model matrix, adapter, phase runner). Build only what's needed.
        if args.command in ("status", "approve", "reject"):
            return _handle_light_command(args)
        if args.command == "abort":
            return _handle_abort(args)
        if args.command == "release":
            return _handle_release(args)

        # FAGAN-0037: resolve story classification for model selection
        classification: str | None = None
        story_id = getattr(args, "story", None)
        if story_id:
            backlog = MarkdownBacklogStore(Path.cwd() / "backlog")
            try:
                story = backlog.get_story(story_id)
                classification = story.classification.value
            except KeyError:
                print(f"unknown story: {story_id}", file=sys.stderr)
                return 1

        _resolve_interactive(args)
        runtime = _build_runtime(args, classification=classification)

        if args.command == "run-step":
            # BR-040/QS-20: `runtime.timeout_s` is the *resolved* effective
            # timeout (SettingsResolver), not the raw `args.timeout` flag,
            # which is `None` whenever `--timeout` was omitted.
            return _handle_run_step(runtime, args.agent, runtime.timeout_s, args.skill)

        if args.command == "run-phase":
            run = _load_or_create_phase_run(
                runtime.run_store, runtime.agent_registry, args.phase
            )
            return _with_lock(
                runtime.run_lock,
                run.run_id,
                lambda: _handle_run_phase(runtime, run, args),
            )

        if args.command == "resume":
            run = runtime.run_store.load()
            if run is None:
                print("no active run", file=sys.stderr)
                return 1
            return _with_lock(
                runtime.run_lock, run.run_id, lambda: _handle_resume(runtime, run, args)
            )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 1


def _resolve_interactive(args) -> None:
    """Set `args.interactive` per cli_specification.md §Settings resolution.

    `_build_runtime`/`_handle_run_step` read `args.interactive`, but
    `build_parser()` only ever defines `--no-interactive` (`no_interactive`)
    — commit 322d9cc replaced `--interactive` with `--no-interactive` and
    left these two reads unconverted, so any direct-mode `run-step`,
    `run-phase`, or `resume` invocation that got this far raised
    `AttributeError` (found while wiring `manage-run.resume` for ST-0040;
    see ST-0040.md's Analysis for the repro). Built-in default: interactive
    whenever a TTY is attached; `--no-interactive` forces headless
    regardless of the terminal.
    """
    args.interactive = (
        not args.no_interactive and sys.stdin.isatty() and sys.stdout.isatty()
    )


def _handle_light_command(args) -> int:
    """Handle status/approve/reject without building the full runtime.

    These commands only need run_store, findings_store, and (for
    approve/reject) gate_runner + agent_registry. They must not fail
    when model-matrix.conf is absent (FAGAN-0024, VR-008).
    """
    repo_root = Path.cwd()
    orch_dir = repo_root / ".orchestrator"

    run_store = JsonRunStateStore(orch_dir)
    findings_store = FilesystemFindingsStore(orch_dir / "findings")

    if args.command == "status":
        print(
            _format_status_overview(
                StatusService(run_store, findings_store).get_status()
            )
        )
        return 0

    # approve / reject need the lock + approval service
    agents_dir = _resolve_agents_dir(repo_root)
    run_lock = FileRunLock(orch_dir)
    gate_runner = WorkingTreeGate(repo_root)
    agent_registry = MarkdownAgentRegistry(agents_dir)
    approval_service = ApprovalService(
        run_store, findings_store, gate_runner, agent_registry
    )

    run = run_store.load()
    if run is None:
        print("no active run", file=sys.stderr)
        return 1

    def _do_approval():
        if args.command == "approve":
            approval_service.approve()
        else:
            note = getattr(args, "note", None)
            approval_service.reject(note=note)
        return 0

    return _with_lock(run_lock, run.run_id, _do_approval)


# --- Status views (menu mode + direct mode; ST-0055, FR-T1..T6, BR-033) -----
#
# Shared by `orchestrate status` (direct mode, `_handle_light_command` above)
# and the `status` submenu's four display leaves (menu mode), so both modes
# render the identical `overview` projection by construction (FR-T2) — same
# formatter function, not independently maintained copies.


def _format_table(headers: list[str], rows: list[list[str]], empty_message: str) -> str:
    """Render a small column-aligned text table; `empty_message` if `rows` is empty."""
    if not rows:
        return empty_message
    widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def _fmt_row(cells: list[str]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    lines = [_fmt_row(headers), _fmt_row(["-" * w for w in widths])]
    lines.extend(_fmt_row(row) for row in rows)
    return "\n".join(lines)


def _format_gate_result(gate) -> str:
    """Render a `GateResult` (or `None`) as a short readable summary.

    Reuses the `hook=…, errors=…, errored=…` vocabulary `ApprovalService`
    already uses for gate-failure messages, so gate outcomes read
    consistently everywhere in the CLI.
    """
    if gate is None:
        return "(no gate run)"
    return (
        f"passed={gate.passed}, errored={gate.errored}, "
        f"hook={gate.hook}, errors={gate.error_count}"
    )


def _format_status_overview(status: RunStatus) -> str:
    """Render `StatusService.get_status()` (FR-T2).

    The one function both `orchestrate status` (direct mode) and
    `status > overview` (menu mode) call, so the two modes are
    structurally guaranteed to show the same projection.
    """
    return "\n".join(
        [
            f"mode: {status.mode or '(no active run)'}",
            f"current phase: {status.current_phase or '-'}",
            f"iteration: {status.iteration if status.iteration is not None else '-'}",
            f"open findings: {status.open_findings}",
            f"last gate: {_format_gate_result(status.last_gate)}",
        ]
    )


def _format_phase_details(phases: list[PhaseDetail]) -> str:
    """Render `StatusService.get_phase_details()` as a table (FR-T3)."""
    headers = [
        "name",
        "author",
        "reviewer",
        "status",
        "iteration",
        "last_gate",
        "halted_from",
    ]
    rows = [
        [
            phase.name,
            phase.author,
            phase.reviewer or "-",
            phase.status,
            str(phase.iteration),
            _format_gate_result(phase.last_gate),
            phase.halted_from or "-",
        ]
        for phase in phases
    ]
    return _format_table(headers, rows, empty_message="no phases recorded")


def _format_findings(findings: list[FindingSummary]) -> str:
    """Render `StatusService.get_findings()` as a table (FR-T4)."""
    headers = ["id", "severity", "artifact", "message", "status"]
    rows = [
        [
            finding.id,
            finding.severity,
            finding.artifact,
            finding.message,
            finding.status,
        ]
        for finding in findings
    ]
    return _format_table(headers, rows, empty_message="no open findings")


def _format_invocation_log(entries: list[LogEntry]) -> str:
    """Render `StatusService.get_log()` as a table (FR-T5)."""
    headers = ["agent", "role", "model", "exit_code", "duration_ms", "gate"]
    rows = [
        [
            entry.agent,
            entry.role,
            entry.model or "-",
            str(entry.exit_code),
            str(entry.duration_ms),
            _format_gate_result(entry.gate),
        ]
        for entry in entries
    ]
    return _format_table(headers, rows, empty_message="no invocation log entries")


# node.id -> (StatusService getter method name, formatter). Table-driven so
# adding a fifth status view later is one entry, not another branch of an
# if/elif. The getter is looked up by name (not bound at table-definition
# time) so any duck-typed StatusService-like object works, not only the
# concrete class.
_STATUS_VIEW_RENDERERS = {
    "status.overview": ("get_status", _format_status_overview),
    "status.phase-details": ("get_phase_details", _format_phase_details),
    "status.findings": ("get_findings", _format_findings),
    "status.log": ("get_log", _format_invocation_log),
}


def build_status_dispatch(status_service: StatusService) -> DispatchHook:
    """Build the `DispatchHook` for the `status` submenu's four display leaves.

    Each of the four nodes reads its projection through `StatusService` —
    never a mutating store method (BR-033, VR-030) — and renders it as
    read-only text for `MenuRenderer.render_display`. `MenuController` owns
    returning to the parent menu on the next keypress (BR-034); this hook
    only produces `DispatchOutcome.content`.
    """

    def _dispatch(node: MenuNode) -> DispatchOutcome:
        entry = _STATUS_VIEW_RENDERERS.get(node.id)
        if entry is None:
            raise ValueError(f"no status view registered for menu node '{node.id}'")
        method_name, formatter = entry
        getter = getattr(status_service, method_name)
        return DispatchOutcome(content=formatter(getter()))

    return _dispatch


# --- Backlog views (menu mode; ST-0057, FR-U1..U6, BR-056, BR-058) -----------
#
# Read-only projections over `BacklogStore` (ST-0056) for the `backlog`
# submenu's four display nodes: `list`, `by-epic`, `ready`, and the dynamic
# `view story` per-story leaves. Mirrors the `status` block above: formatter
# functions + a table-driven dispatch hook, so adding a view is one entry,
# not another branch. `view story` additionally needs a populated `MenuNode`
# built from the live backlog snapshot (`build_backlog_view_story_menu`),
# because its children — one per story — are runtime data that the pure
# `menu_tree.py` tree builder cannot know (see menu_tree._build_backlog_menu).


def _format_backlog_list(stories: list) -> str:
    """Render `BacklogStore.list_stories()` as a table (FR-U2, BR-059)."""
    headers = ["id", "title", "epic", "classification", "status", "deps"]
    rows = [
        [
            story.id,
            story.title,
            story.epic,
            story.classification.value,
            story.status.value,
            ", ".join(story.deps) if story.deps else "-",
        ]
        for story in stories
    ]
    return _format_table(headers, rows, empty_message="no stories in backlog")


def _format_backlog_by_epic(grouped: dict) -> str:
    """Render `BacklogStore.stories_by_epic()` grouped under epic headings,
    each story retaining a visible status indicator (FR-U3, BR-059)."""
    if not grouped:
        return "no stories in backlog"
    sections = []
    for epic, stories in grouped.items():
        lines = [f"## {epic}"]
        lines.extend(
            f"  [{story.status.value}] {story.id}  {story.title}  ({story.classification.value})"
            for story in stories
        )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def _format_backlog_ready(stories: list) -> str:
    """Render `BacklogStore.ready_stories()` (FR-U4, BR-057).

    An empty result is an explicit empty-state message, never a blank table
    (BR-058).
    """
    return _format_backlog_list(stories) if stories else "no dependency-ready stories"


def _format_story_detail(story) -> str:
    """Render one story's full frontmatter and prose body (FR-U5, BR-060)."""
    lines = [
        f"id: {story.id}",
        f"title: {story.title}",
        f"epic: {story.epic}",
        f"classification: {story.classification.value}",
        f"status: {story.status.value}",
        f"deps: {', '.join(story.deps) if story.deps else '(none)'}",
        f"traces: {', '.join(story.traces) if story.traces else '(none)'}",
        f"outputs: {', '.join(story.outputs) if story.outputs else '(none)'}",
        "",
        story.body,
    ]
    return "\n".join(lines)


# node.id -> (BacklogStore getter method name, formatter) for the three
# static display leaves. `view story`'s per-story leaves are handled
# separately in `build_backlog_dispatch`, keyed by id prefix rather than an
# exact match, since their ids are runtime-generated (one per story).
_BACKLOG_VIEW_RENDERERS = {
    "backlog.list": ("list_stories", _format_backlog_list),
    "backlog.by-epic": ("stories_by_epic", _format_backlog_by_epic),
    "backlog.ready": ("ready_stories", _format_backlog_ready),
}

_VIEW_STORY_PREFIX = "backlog.view-story."


def build_backlog_view_story_menu(backlog_store) -> MenuNode:
    """Build the populated `view story` submenu (FR-U5, cli_specification.md
    "backlog + view story => menu, [list of story ids with titles]").

    One display leaf per story in `backlog_store.list_stories()` order,
    labeled `"{id}: {title}"`. An empty backlog yields `children == []`:
    `MenuController._select_child` already no-ops when a menu has no
    children, so "no selectable story, return safely without mutation"
    (BR-058, UC-12 extension 2a2) requires no new controller branching.
    """
    children = [
        MenuNode(
            id=f"{_VIEW_STORY_PREFIX}{story.id}",
            label=f"{story.id}: {story.title}",
            type=MenuNodeType.DISPLAY,
        )
        for story in backlog_store.list_stories()
    ]
    return MenuNode(
        id="backlog.view-story",
        label="view story",
        type=MenuNodeType.MENU,
        children=children,
    )


def build_backlog_dispatch(backlog_store) -> DispatchHook:
    """Build the `DispatchHook` for the `backlog` submenu's display leaves.

    Handles the three static leaves (`backlog.list`, `backlog.by-epic`,
    `backlog.ready`) via `_BACKLOG_VIEW_RENDERERS`, and the dynamic
    `backlog.view-story.{id}` leaves by loading the story through
    `get_story()` (BR-060). A story that can no longer be retrieved
    (UC-12 extension 5d) is reported as content, not raised — the display
    stays read-only and nothing is mutated either way (BR-056).
    """

    def _dispatch(node: MenuNode) -> DispatchOutcome:
        entry = _BACKLOG_VIEW_RENDERERS.get(node.id)
        if entry is not None:
            method_name, formatter = entry
            getter = getattr(backlog_store, method_name)
            return DispatchOutcome(content=formatter(getter()))

        if node.id.startswith(_VIEW_STORY_PREFIX):
            story_id = node.id[len(_VIEW_STORY_PREFIX) :]
            try:
                story = backlog_store.get_story(story_id)
            except KeyError:
                return DispatchOutcome(content=f"story could not be loaded: {story_id}")
            return DispatchOutcome(content=_format_story_detail(story))

        raise ValueError(f"no backlog view registered for menu node '{node.id}'")

    return _dispatch


# --- Manage-run leaves (menu mode; ST-0040, FR-V3, cli_specification.md ------
# §Manage run) --------------------------------------------------------------
#
# `manage-run`'s five children (`resume`, `approve`, `reject`, `release`,
# `abort`) are direct function leaves per the spec — no further selection —
# and every direct-mode handler already exists and needs no extra input
# beyond what a bare `orchestrate {command}` invocation already passes. Each
# branch below calls the *exact* function `main()` calls for the matching
# direct-mode subcommand — not a reimplementation — so behaviour (exit
# codes, gate handling, run-state mutation, printed output) is identical by
# construction (FR-V3). `resume` is the one long-running leaf here: it needs
# the full `_Runtime` (adapter, model resolver, phase runner), built lazily
# through the injected `build_runtime` factory so entering menu mode, or
# navigating to any other manage-run leaf, never touches that machinery
# (BR-033).


def build_manage_run_dispatch(build_runtime: Callable[[], "_Runtime"]) -> DispatchHook:
    """Build the `DispatchHook` for the `manage-run` submenu's five leaves."""

    def _dispatch(node: MenuNode) -> DispatchOutcome:
        if node.id == "manage-run.resume":
            _dispatch_resume(build_runtime)
            return DispatchOutcome(long_running=True)
        if node.id == "manage-run.approve":
            _handle_light_command(SimpleNamespace(command="approve"))
            return DispatchOutcome(long_running=False)
        if node.id == "manage-run.reject":
            _handle_light_command(SimpleNamespace(command="reject", note=None))
            return DispatchOutcome(long_running=False)
        if node.id == "manage-run.release":
            _handle_release(None)
            return DispatchOutcome(long_running=False)
        if node.id == "manage-run.abort":
            _handle_abort(None)
            return DispatchOutcome(long_running=False)

        raise ValueError(f"no manage-run action registered for menu node '{node.id}'")

    return _dispatch


def _dispatch_resume(build_runtime: Callable[[], "_Runtime"]) -> None:
    """Menu-mode equivalent of `main()`'s `resume` branch (FR-V3, FR-P7).

    Builds the runtime only now (not at menu-mode entry), loads the run, and
    calls `_handle_resume` under the same lock direct mode uses — the exact
    same code path `orchestrate resume` runs, so exit-code/gate/run-state
    behaviour matches by construction. `_handle_resume` ignores its `args`
    parameter (verified: no `args.*` reference in its body), so no synthetic
    argparse Namespace is needed here.
    """
    runtime = build_runtime()
    run = runtime.run_store.load()
    if run is None:
        print("no active run", file=sys.stderr)
        return
    _with_lock(runtime.run_lock, run.run_id, lambda: _handle_resume(runtime, run, None))


# --- Configure > defaults leaves (menu mode; ST-0044, UC-09, FR-Q4, ---------
# BR-037..041) -----------------------------------------------------------
#
# `configure > defaults`'s four leaves — `adapter`, `timeout`, `cap`,
# `auto-approve` — each validate the submitted value BEFORE persistence
# (BR-039), persist atomically through `ConfigStore`, and never crash menu
# mode on a malformed `.orchestrator/config.toml` (BR-041, ADR-0016).
# `adapter` additionally needs a runtime-populated submenu (one function
# leaf per registered adapter, current default marked ★) — built by
# `build_configure_defaults_adapter_menu`, kept out of menu_tree.py for the
# same reason `build_backlog_view_story_menu` is: a store call is runtime
# data, not something the pure tree builder can know.

_CONFIGURE_DEFAULTS_ADAPTER_PREFIX = "configure.defaults.adapter."


def _current_config(config_store: ConfigStore) -> Config:
    """Load the persisted Config, defaulting to an all-``None`` Config when
    `.orchestrator/config.toml` is absent (BR-037) — callers can then freely
    read/replace fields without a second null-check. Raises `ConfigStoreError`
    unchanged when the file exists but is malformed (BR-041); every caller
    here runs under `build_configure_defaults_dispatch`'s single try/except,
    so that error surfaces as a clean refusal, not a crash.
    """
    return config_store.load() or Config()


def _persist_default(config_store: ConfigStore, **changes: object) -> None:
    """Merge ``changes`` into the currently persisted Config and save it.

    `TomlConfigStore.save()` writes the *entire* ``[defaults]`` table
    represented by the `Config` it is given — a field left at `None` is
    simply omitted from the block it renders (see
    `adapters/config_store.py`'s `_render_defaults_block`), and `save()`
    replaces the whole existing ``[defaults]`` block with that rendering.
    Saving a bare ``Config(timeout=900)`` would therefore silently drop any
    other already-persisted key (`adapter`, `cap`, `auto_approve`). Loading
    the current `Config` first and using `dataclasses.replace()` to change
    only the requested field is what makes each of the four defaults leaves
    an independent, non-destructive edit (UC-09 step 7).
    """
    current = _current_config(config_store)
    config_store.save(replace(current, **changes))


def _parse_int_or_none(raw: str) -> int | None:
    try:
        return int(raw.strip())
    except (ValueError, AttributeError):
        return None


def _validate_timeout(raw: str) -> int:
    """BR-039: timeout must be a positive integer number of seconds."""
    value = _parse_int_or_none(raw)
    if value is None or value <= 0:
        raise ValueError(
            f"timeout must be a positive integer number of seconds, got {raw!r}"
        )
    return value


def _validate_cap(raw: str) -> int:
    """BR-039: cap must be an integer greater than or equal to 1."""
    value = _parse_int_or_none(raw)
    if value is None or value < 1:
        raise ValueError(
            f"cap must be an integer greater than or equal to 1, got {raw!r}"
        )
    return value


def _dispatch_configure_timeout(
    config_store: ConfigStore, input_fn: Callable[[str], str]
) -> DispatchOutcome:
    raw = input_fn("timeout in seconds: ")
    try:
        value = _validate_timeout(raw)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return DispatchOutcome(long_running=False)
    _persist_default(config_store, timeout=value)
    print(f"timeout set to {value}")
    return DispatchOutcome(long_running=False)


def _dispatch_configure_cap(
    config_store: ConfigStore, input_fn: Callable[[str], str]
) -> DispatchOutcome:
    raw = input_fn("iteration cap: ")
    try:
        value = _validate_cap(raw)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return DispatchOutcome(long_running=False)
    _persist_default(config_store, cap=value)
    print(f"cap set to {value}")
    return DispatchOutcome(long_running=False)


def _dispatch_configure_auto_approve(config_store: ConfigStore) -> DispatchOutcome:
    """No prompt — selecting this leaf flips the persisted value (BR-039:
    auto_approve is always a boolean by construction, so there is no
    submitted-value validation step here, unlike timeout/cap/adapter).

    Reads the currently *effective* value through `SettingsResolver` (no
    menu/CLI layer applies here — this leaf toggles the config layer
    itself) rather than hand-rolling the same config-or-built-in fallback a
    second time (ST-0058: this used to be a separate, silently divergent
    copy of the same precedence logic `SettingsResolver` already owns).
    """
    current_value = SettingsResolver(config_store).resolve("auto_approve")
    new_value = not current_value
    _persist_default(config_store, auto_approve=new_value)
    print(f"auto-approve set to {'on' if new_value else 'off'}")
    return DispatchOutcome(long_running=False)


def _dispatch_configure_adapter(
    config_store: ConfigStore, adapter_registry: AdapterRegistry, adapter_name: str
) -> DispatchOutcome:
    """BR-039: adapter must name a registered adapter.

    Re-validated here (not just trusted from the submenu's own contents)
    because the submenu was built once, earlier, at menu-tree-construction
    time (`build_configure_defaults_adapter_menu`) — the registry could have
    changed since, e.g. `configure > cli-list > remove adapter` in the same
    session (ST-0047+).
    """
    registered = {entry.name for entry in adapter_registry.list_adapters()}
    if adapter_name not in registered:
        print(
            f"adapter must name a registered adapter; {adapter_name!r} is not "
            "registered",
            file=sys.stderr,
        )
        return DispatchOutcome(long_running=False)
    _persist_default(config_store, adapter=adapter_name)
    print(f"default adapter set to {adapter_name}")
    return DispatchOutcome(long_running=False)


def build_configure_defaults_dispatch(
    config_store: ConfigStore,
    adapter_registry: AdapterRegistry,
    *,
    input_fn: Callable[[str], str] = input,
) -> DispatchHook:
    """Build the `DispatchHook` for the `configure > defaults` submenu's four
    leaves (UC-09, FR-Q4, ST-0044).

    `timeout`/`cap` prompt for an integer through *input_fn* (defaults to
    the builtin `input`, injectable for tests — the same seam
    `_pick_cli()` would use if it needed one); `auto-approve` toggles with
    no prompt; `adapter.{name}` leaves (populated by
    `build_configure_defaults_adapter_menu`) set the default adapter
    directly, no prompt needed since the submenu *is* the picker. Every
    branch validates before persisting (BR-039) and persists atomically
    through `ConfigStore` (BR-038, already atomic by construction in
    `TomlConfigStore`). A malformed `config.toml` raises `ConfigStoreError`
    from `config_store.load()`; caught once here so every leaf refuses
    cleanly with the same offending file/key message `TomlConfigStore`
    already composes (BR-041), instead of crashing menu mode (ADR-0016).
    """

    def _dispatch(node: MenuNode) -> DispatchOutcome:
        try:
            if node.id == "configure.defaults.timeout":
                return _dispatch_configure_timeout(config_store, input_fn)
            if node.id == "configure.defaults.cap":
                return _dispatch_configure_cap(config_store, input_fn)
            if node.id == "configure.defaults.auto-approve":
                return _dispatch_configure_auto_approve(config_store)
            if node.id.startswith(_CONFIGURE_DEFAULTS_ADAPTER_PREFIX):
                adapter_name = node.id[len(_CONFIGURE_DEFAULTS_ADAPTER_PREFIX) :]
                return _dispatch_configure_adapter(
                    config_store, adapter_registry, adapter_name
                )
        except ConfigStoreError as exc:
            print(str(exc), file=sys.stderr)
            return DispatchOutcome(long_running=False)

        raise ValueError(
            f"no configure/defaults action registered for menu node '{node.id}'"
        )

    return _dispatch


def build_configure_defaults_adapter_menu(
    adapter_registry: AdapterRegistry, config_store: ConfigStore
) -> MenuNode:
    """Build the populated `configure > defaults > adapter` submenu (UC-09,
    cli_specification.md "adapter => menu, [list of registered adapters,
    current default marked ★]").

    One function leaf per `adapter_registry.list_adapters()` entry. The
    currently *effective* default adapter — resolved through
    `SettingsResolver` (BR-040; no menu/CLI layer applies at menu-tree
    construction time, so this collapses to "persisted config, falling back
    to the built-in default when unset or the file is absent") — is marked
    `is_default=True` so the renderer paints it with ★ (BR-032). A malformed
    `config.toml` degrades to "no adapter marked" here rather than
    propagating the read error into menu-tree construction (which runs once,
    eagerly, before any operator action, and is not itself a leaf
    `MenuController` can dispatch to) — the mutating action (actually
    selecting an adapter) still refuses cleanly and reports the malformed
    file when it re-reads `config.toml` at persist time
    (`_dispatch_configure_adapter`, BR-041).
    """
    try:
        current_adapter = SettingsResolver(config_store).resolve("adapter")
    except ConfigStoreError:
        current_adapter = None

    children = [
        MenuNode(
            id=f"{_CONFIGURE_DEFAULTS_ADAPTER_PREFIX}{entry.name}",
            label=entry.name,
            type=MenuNodeType.FUNCTION,
            is_default=(entry.name == current_adapter),
        )
        for entry in adapter_registry.list_adapters()
    ]
    return MenuNode(
        id="configure.defaults.adapter",
        label="adapter",
        type=MenuNodeType.MENU,
        children=children,
    )


# --- Configure > cli-list leaves (menu mode; ST-0047, UC-10 steps 1-8, ------
# 23-24, FR-R2, FR-R3, FR-R4, BR-042, BR-048) --------------------------------
#
# `configure > cli-list`'s three leaves — `auto-detect`, `add adapter`,
# `remove adapter` — manage the adapter *registry* itself (not any one
# adapter's model dictionary; that's `configure > cli > {adapter}`, out of
# this story's traces, left for ST-0048 onward). `auto-detect` and
# `add adapter` need no new validation or cascade logic of their own —
# `TomlAdapterRegistry.register()`/`unregister()` (ST-0046) already
# validate and persist atomically (BR-042, BR-043, BR-044, BR-048); these
# dispatch functions call them and surface the result. `remove adapter`
# additionally needs a runtime-populated submenu (one function leaf per
# registered adapter) — built by `build_cli_list_remove_adapter_menu`,
# mirroring `build_configure_defaults_adapter_menu` for the same reason
# (menu_tree.py stays pure; a store call is runtime data the static tree
# builder cannot know).

_CLI_LIST_REMOVE_ADAPTER_PREFIX = "configure.cli-list.remove-adapter."


def _dispatch_cli_list_auto_detect(
    adapter_registry: AdapterRegistry,
    detect_fn: Callable[[], list[DetectedAdapter]],
) -> DispatchOutcome:
    """UC-10 step 4 / extensions 4a, 4b.

    Pre-filters `detect_fn()`'s candidates against already-registered
    *names* — the same candidate re-detected on a later scan isn't a
    validation failure (4b), it's simply not newly discovered, so it's
    skipped silently rather than re-attempted. A candidate whose *path*
    collides with a differently named existing registration is a genuine
    conflict (BR-043) and is not pre-filtered: `register()` raises for it,
    and that failure is reported and skipped, continuing the scan (4b)
    rather than aborting on one bad candidate. No candidates found or newly
    registered leaves the registry unchanged and reports that (4a).
    """
    known_names = {entry.name for entry in adapter_registry.list_adapters()}

    newly_registered: list[str] = []
    for candidate in detect_fn():
        if candidate.name in known_names:
            continue
        try:
            adapter_registry.register(candidate.name, candidate.binary_path)
        except ValueError as exc:
            print(f"skipping {candidate.name!r}: {exc}", file=sys.stderr)
            continue
        newly_registered.append(candidate.name)

    if newly_registered:
        print(f"registered new adapter(s): {', '.join(newly_registered)}")
    else:
        print("no new supported adapters found on $PATH")
    return DispatchOutcome(long_running=False)


def _dispatch_cli_list_add_adapter(
    adapter_registry: AdapterRegistry, input_fn: Callable[[str], str]
) -> DispatchOutcome:
    """UC-10 steps 5-8 / extensions 8a, 8b.

    No new validation: `TomlAdapterRegistry.register()` already checks
    duplicate name, duplicate path, and non-existent/non-executable path,
    raising `ValueError` with a specific reason before any write. That
    message is surfaced verbatim, not swallowed (this story's explicit
    instruction).
    """
    name = input_fn("adapter name: ").strip()
    binary_path = input_fn("binary path: ").strip()
    try:
        adapter_registry.register(name, binary_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return DispatchOutcome(long_running=False)
    print(f"adapter {name!r} registered")
    return DispatchOutcome(long_running=False)


def _dispatch_cli_list_remove_adapter(
    adapter_registry: AdapterRegistry, adapter_name: str
) -> DispatchOutcome:
    """UC-10 step 24, FR-R4, BR-044.

    No new cascade logic: `TomlAdapterRegistry.unregister()` already
    removes the adapter and its model dictionary in one atomic write
    (ST-0046). A `KeyError` (already removed, e.g. in a concurrent session)
    is reported rather than raised (ADR-0016: a leaf's failure never
    crashes menu mode).
    """
    try:
        adapter_registry.unregister(adapter_name)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return DispatchOutcome(long_running=False)
    print(f"adapter {adapter_name!r} removed")
    return DispatchOutcome(long_running=False)


def build_cli_list_dispatch(
    adapter_registry: AdapterRegistry,
    *,
    input_fn: Callable[[str], str] = input,
    detect_fn: Callable[[], list[DetectedAdapter]] = detect_candidates,
) -> DispatchHook:
    """Build the `DispatchHook` for the `configure > cli-list` submenu's
    three leaves (UC-10, FR-R2, FR-R3, FR-R4, ST-0047).

    `input_fn` reuses ST-0044's injectable-prompt seam for `add adapter`'s
    name/binary-path prompts. `detect_fn` is the equivalent seam for
    `auto-detect` — defaults to `adapter_detect.detect_candidates` (a real
    `$PATH` scan), injectable so tests never depend on what's actually
    installed on the machine running them.
    """

    def _dispatch(node: MenuNode) -> DispatchOutcome:
        if node.id == "configure.cli-list.auto-detect":
            return _dispatch_cli_list_auto_detect(adapter_registry, detect_fn)
        if node.id == "configure.cli-list.add-adapter":
            return _dispatch_cli_list_add_adapter(adapter_registry, input_fn)
        if node.id.startswith(_CLI_LIST_REMOVE_ADAPTER_PREFIX):
            adapter_name = node.id[len(_CLI_LIST_REMOVE_ADAPTER_PREFIX) :]
            return _dispatch_cli_list_remove_adapter(adapter_registry, adapter_name)

        raise ValueError(
            f"no configure/cli-list action registered for menu node '{node.id}'"
        )

    return _dispatch


def build_cli_list_remove_adapter_menu(adapter_registry: AdapterRegistry) -> MenuNode:
    """Build the populated `configure > cli-list > remove adapter` submenu
    (UC-10, cli_specification.md "remove adapter => menu, [list of
    registered adapters]").

    One function leaf per `adapter_registry.list_adapters()` entry —
    mirrors `build_configure_defaults_adapter_menu`'s shape exactly, minus
    the ★ marking (cli_specification.md's `remove adapter` listing carries
    no "current default" concept to mark).
    """
    children = [
        MenuNode(
            id=f"{_CLI_LIST_REMOVE_ADAPTER_PREFIX}{entry.name}",
            label=entry.name,
            type=MenuNodeType.FUNCTION,
        )
        for entry in adapter_registry.list_adapters()
    ]
    return MenuNode(
        id="configure.cli-list.remove-adapter",
        label="remove adapter",
        type=MenuNodeType.MENU,
        children=children,
    )


# --- Configure > cli leaves (menu mode; ST-0048, UC-10 steps 9-22, ---------
# FR-R6, FR-R7, FR-R8, BR-045, BR-046, BR-047) -------------------------------
#
# `configure > cli > {adapter}`'s four leaves — `list models`, `auto-detect`,
# `add model`, `remove model` — manage one registered adapter's *model
# dictionary* (the tier-to-model mapping), as opposed to `cli-list`'s
# registry-of-adapters concerns (ST-0047). Because this menu is two runtime
# levels deep (adapter name, then — for `remove model` — the tier of the
# mapping being removed), `node.id` is parsed as
# `configure.cli.{adapter}.{action}` (five segments for
# `configure.cli.{adapter}.remove-model.{tier}`) rather than matched by a
# single `startswith` prefix constant; `TomlAdapterRegistry.register()`
# already constrains adapter names to `^[A-Za-z0-9_-]+$` (no literal `.`),
# so this split is unambiguous. `TomlAdapterRegistry`'s `set_model`/
# `remove_model`/`list_models`/`get_model` (ST-0046) already validate the
# tier vocabulary and adapter existence and persist atomically — no new
# validation logic is added here, only prompting, replace-confirmation, and
# coverage-warning presentation around those calls.

_CONFIGURE_CLI_REMOVE_MODEL_SEGMENT = "remove-model"


def _format_cli_models(pairs: list[tuple[str, str]]) -> str:
    """Render an adapter's `(tier, model_id)` mappings as a table plus a
    tier-coverage status line (FR-R6, UC-10 step 16).

    Rendered in the fixed tier order (`entities.Tier`'s declared order —
    economy, standard, strong) rather than `list_models()`'s own "undefined
    order" (its docstring), so the table reads consistently regardless of
    insertion order.
    """
    by_tier = dict(pairs)
    ordered = [
        (tier.value, by_tier[tier.value]) for tier in Tier if tier.value in by_tier
    ]
    table = _format_table(
        ["model id", "tier"],
        [[model_id, tier] for tier, model_id in ordered],
        empty_message="no models registered",
    )
    missing = [tier.value for tier in Tier if tier.value not in by_tier]
    coverage = (
        "tier coverage: complete"
        if not missing
        else f"tier coverage: incomplete (missing: {', '.join(missing)})"
    )
    return f"{table}\n\n{coverage}"


def _default_cli_model_discovery(adapter_name: str) -> list[str] | None:
    """Default `discover_fn` for `configure > cli > {adapter} > auto-detect`
    (FR-R8, BR-047).

    `ports.py`'s `CLIAdapter` protocol declares only `invoke(...)` — no
    discovery method — and the one concrete adapter this codebase ships
    (`CopilotAdapter`) implements no such method either; there is also no
    factory that turns a registered adapter's `(name, binary_path)` into a
    live `CLIAdapter` instance to even ask. Returning `None` unconditionally
    is therefore the honest answer for every adapter name today: no
    adapter's model discovery is supported. This is a real, capability-
    sensitive seam (not a hardcoded "always unsupported" branch baked into
    the dispatch function) — a future adapter that gains a discovery
    capability is wired by injecting a different `discover_fn`, not by
    editing `_dispatch_cli_auto_detect`.
    """
    return None


def _dispatch_cli_list_models(
    adapter_registry: AdapterRegistry, adapter_name: str
) -> DispatchOutcome:
    try:
        pairs = adapter_registry.list_models(adapter_name)
    except KeyError as exc:
        return DispatchOutcome(content=str(exc))
    return DispatchOutcome(content=_format_cli_models(pairs))


def _dispatch_cli_add_model(
    adapter_registry: AdapterRegistry,
    adapter_name: str,
    input_fn: Callable[[str], str],
) -> DispatchOutcome:
    """UC-10 steps 17-20 / extension 20a, FR-R7, BR-045.

    Reads the tier's current mapping (if any) before prompting for
    replacement confirmation — declining leaves the dictionary untouched
    (20a3). `get_model`/`set_model` validate adapter existence and tier
    membership and raise before any write; those exceptions are surfaced
    verbatim, the same reporting convention `add adapter` (ST-0047) uses.
    """
    model_id = input_fn("model id: ").strip()
    tier = input_fn("tier (economy/standard/strong): ").strip()
    try:
        existing = adapter_registry.get_model(adapter_name, tier)
    except (KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return DispatchOutcome(long_running=False)

    if existing is not None:
        confirm = (
            input_fn(
                f"tier {tier!r} already maps to {existing!r}; "
                f"replace with {model_id!r}? [y/N]: "
            )
            .strip()
            .lower()
        )
        if confirm != "y":
            print("replacement declined; model dictionary unchanged")
            return DispatchOutcome(long_running=False)

    try:
        adapter_registry.set_model(adapter_name, tier, model_id)
    except (KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return DispatchOutcome(long_running=False)
    print(f"model {model_id!r} mapped to tier {tier!r} for adapter {adapter_name!r}")
    return DispatchOutcome(long_running=False)


def _dispatch_cli_remove_model(
    adapter_registry: AdapterRegistry, adapter_name: str, tier: str
) -> DispatchOutcome:
    """UC-10 step 21-22 / extension 22a, BR-046.

    The removal is never blocked by the resulting incompleteness (BR-046:
    "incomplete coverage may be saved") — it always persists, then a
    coverage re-check reports a warning naming the now-missing tier(s).
    """
    try:
        adapter_registry.remove_model(adapter_name, tier)
    except (KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return DispatchOutcome(long_running=False)

    print(f"model mapping removed for tier {tier!r} on adapter {adapter_name!r}")
    mapped_tiers = {
        mapped_tier for mapped_tier, _ in adapter_registry.list_models(adapter_name)
    }
    missing = [t.value for t in Tier if t.value not in mapped_tiers]
    if missing:
        print(
            "warning: model dictionary is incomplete "
            f"(missing tier(s): {', '.join(missing)}); later tier-based "
            "model resolution may halt on the missing tier unless "
            "adapter-default fallback is explicitly enabled",
            file=sys.stderr,
        )
    return DispatchOutcome(long_running=False)


def _dispatch_cli_auto_detect(
    adapter_registry: AdapterRegistry,
    adapter_name: str,
    discover_fn: Callable[[str], list[str] | None],
    input_fn: Callable[[str], str],
) -> DispatchOutcome:
    """UC-10 steps 11-14 / extensions 11a, 13a, FR-R8, BR-047.

    `discover_fn(adapter_name) is None` means discovery is unsupported for
    that adapter (11a): report it and change nothing. A (possibly empty)
    list means supported; the operator assigns a tier per discovered model
    id (blank skips it) and confirms the whole batch before anything is
    persisted (13a: declining discards the proposal, dictionary unchanged).
    Each accepted mapping is written through `set_model` (already atomic
    per call, ST-0046) — there is no cross-mapping transaction primitive in
    `TomlAdapterRegistry`, so a batch of N accepted mappings is N atomic
    writes, consistent with how `add model` and `cli-list auto-detect`
    (ST-0047) already persist one atomic write per accepted item.
    """
    discovered = discover_fn(adapter_name)
    if discovered is None:
        print(f"model auto-detect is unsupported for adapter {adapter_name!r}")
        return DispatchOutcome(long_running=False)
    if not discovered:
        print(f"adapter {adapter_name!r} reported no available models")
        return DispatchOutcome(long_running=False)

    proposed: list[tuple[str, str]] = []
    for model_id in discovered:
        tier = input_fn(
            f"tier for {model_id!r} (economy/standard/strong, blank to skip): "
        ).strip()
        if tier:
            proposed.append((model_id, tier))

    if not proposed:
        print("no models selected; model dictionary unchanged")
        return DispatchOutcome(long_running=False)

    confirm = (
        input_fn(
            f"apply {len(proposed)} discovered mapping(s) to {adapter_name!r}? [y/N]: "
        )
        .strip()
        .lower()
    )
    if confirm != "y":
        print("discovery cancelled; model dictionary unchanged")
        return DispatchOutcome(long_running=False)

    applied = 0
    for model_id, tier in proposed:
        try:
            adapter_registry.set_model(adapter_name, tier, model_id)
        except (KeyError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            continue
        applied += 1
    print(f"applied {applied} discovered model mapping(s) for {adapter_name!r}")
    return DispatchOutcome(long_running=False)


def build_configure_cli_dispatch(
    adapter_registry: AdapterRegistry,
    *,
    input_fn: Callable[[str], str] = input,
    discover_fn: Callable[[str], list[str] | None] = _default_cli_model_discovery,
) -> DispatchHook:
    """Build the `DispatchHook` for the `configure > cli > {adapter}`
    submenu's four leaves (UC-10, FR-R6, FR-R7, FR-R8, ST-0048).

    `input_fn` reuses the injectable-prompt seam ST-0044/47 already
    established. `discover_fn` is the capability-sensitive seam for
    `auto-detect` (see `_default_cli_model_discovery`'s docstring) —
    injectable so tests can exercise the "discovery supported" path without
    depending on a real adapter this codebase does not implement.
    """

    def _dispatch(node: MenuNode) -> DispatchOutcome:
        parts = node.id.split(".")
        if len(parts) < 4 or parts[0] != "configure" or parts[1] != "cli":
            raise ValueError(
                f"no configure/cli action registered for menu node '{node.id}'"
            )
        adapter_name, action = parts[2], parts[3]

        if action == "list-models" and len(parts) == 4:
            return _dispatch_cli_list_models(adapter_registry, adapter_name)
        if action == "auto-detect" and len(parts) == 4:
            return _dispatch_cli_auto_detect(
                adapter_registry, adapter_name, discover_fn, input_fn
            )
        if action == "add-model" and len(parts) == 4:
            return _dispatch_cli_add_model(adapter_registry, adapter_name, input_fn)
        if action == _CONFIGURE_CLI_REMOVE_MODEL_SEGMENT and len(parts) == 5:
            return _dispatch_cli_remove_model(adapter_registry, adapter_name, parts[4])

        raise ValueError(
            f"no configure/cli action registered for menu node '{node.id}'"
        )

    return _dispatch


def build_configure_cli_remove_model_menu(
    adapter_registry: AdapterRegistry, adapter_name: str
) -> MenuNode:
    """Build the populated `configure > cli > {adapter} > remove model`
    submenu (UC-10, cli_specification.md "remove model => menu, [list of
    models registered for this adapter]").

    One function leaf per currently-mapped tier, labeled `"{model_id}
    [{tier}]"` so the operator can tell mappings apart at a glance even
    though the dictionary holds at most one model per tier (BR-045). An
    adapter with no registered mappings yields `children == []`, same
    empty-state precedent as `build_cli_list_remove_adapter_menu`.
    """
    try:
        pairs = adapter_registry.list_models(adapter_name)
    except KeyError:
        pairs = []
    children = [
        MenuNode(
            id=f"configure.cli.{adapter_name}.{_CONFIGURE_CLI_REMOVE_MODEL_SEGMENT}.{tier}",
            label=f"{model_id} [{tier}]",
            type=MenuNodeType.FUNCTION,
        )
        for tier, model_id in sorted(pairs)
    ]
    return MenuNode(
        id=f"configure.cli.{adapter_name}.{_CONFIGURE_CLI_REMOVE_MODEL_SEGMENT}",
        label="remove model",
        type=MenuNodeType.MENU,
        children=children,
    )


def build_configure_cli_adapter_menu(
    adapter_registry: AdapterRegistry, adapter_name: str
) -> MenuNode:
    """Build the populated `configure > cli > {adapter}` submenu: the four
    model-dictionary actions (UC-10 step 10, cli_specification.md lines
    141-145).
    """
    return MenuNode(
        id=f"configure.cli.{adapter_name}",
        label=adapter_name,
        type=MenuNodeType.MENU,
        children=[
            MenuNode(
                id=f"configure.cli.{adapter_name}.list-models",
                label="list models",
                type=MenuNodeType.DISPLAY,
            ),
            MenuNode(
                id=f"configure.cli.{adapter_name}.auto-detect",
                label="auto-detect",
                type=MenuNodeType.FUNCTION,
            ),
            MenuNode(
                id=f"configure.cli.{adapter_name}.add-model",
                label="add model",
                type=MenuNodeType.FUNCTION,
            ),
            build_configure_cli_remove_model_menu(adapter_registry, adapter_name),
        ],
    )


def build_configure_cli_menu(adapter_registry: AdapterRegistry) -> MenuNode:
    """Build the populated `configure > cli` submenu (UC-10, cli_specification.md
    "cli => menu, [list of registered adapters]").

    One `configure.cli.{adapter}` menu child per registered adapter —
    mirrors `build_cli_list_remove_adapter_menu`'s shape, one level deeper.
    """
    children = [
        build_configure_cli_adapter_menu(adapter_registry, entry.name)
        for entry in adapter_registry.list_adapters()
    ]
    return MenuNode(
        id="configure.cli",
        label="cli",
        type=MenuNodeType.MENU,
        children=children,
    )


# --- Configure > model-matrix leaves (menu mode; ST-0050, UC-10, FR-R9, -----
# FR-K5, ADR-0017, ADR-0018) -------------------------------------------------
#
# `show`/`edit`/`validate` never reimplement matrix parsing or the VR-024
# consistency checks: `show` reads through the existing `FileModelMatrix`
# adapter, `validate` shells out to the existing `scripts/matrix-lint` gate.
# `edit` is the one leaf with a side effect beyond the matrix file itself —
# after a successful `$EDITOR` session it repopulates every registered
# adapter's model dictionary from the edited `[facts]`
# (`populate_adapter_dictionaries_from_matrix`), because the adapter
# dictionary — not the matrix file — is what `ModelResolver` reads at run
# time (ADR-0018 point 3; already true from ST-0049, verified by reading
# `model_resolver.py:ModelResolver.resolve_agent_tier`, which only calls
# `self._adapter_registry.get_model(...)`). The same population function is
# also called once at menu-mode startup (`_run_menu_mode`), so a matrix
# edited outside the menu (by hand, or before this session started) still
# reaches the dictionaries the runtime actually reads.


def populate_adapter_dictionaries_from_matrix(
    matrix: ModelMatrix, adapter_registry: AdapterRegistry
) -> None:
    """Idempotently write the matrix's `[facts]` into each registered
    adapter's `ModelDictionary` (ADR-0017 point 5, ADR-0018 point 3).

    Only CLIs that are *both* configured in `matrix.configured_clis()` and
    already registered are written — an unregistered CLI name in the matrix
    has no dictionary to populate (`AdapterRegistry.set_model` would raise
    `KeyError`), so it is silently skipped rather than treated as an error:
    the matrix may legitimately list facts for a CLI the operator has not
    installed locally yet.

    Idempotent by construction, not by any check performed here:
    `TomlAdapterRegistry.set_model` (via `ModelDictionary.set_model`)
    unconditionally overwrites a tier's mapping (BR-045 — at most one model
    per tier), so calling this twice with an unchanged matrix and registry
    reproduces the identical dictionary state and raises nothing either
    time.
    """
    registered = {entry.name for entry in adapter_registry.list_adapters()}
    for cli_name in matrix.configured_clis():
        if cli_name not in registered:
            continue
        for tier in ("economy", "standard", "strong"):
            model_id = matrix.get_model(cli_name, tier)
            if model_id is not None:
                adapter_registry.set_model(cli_name, tier, model_id)


def _format_model_matrix_facts(matrix: FileModelMatrix) -> str:
    """Render `[facts]` as adapter -> tier -> model (FR-R9)."""
    clis = matrix.configured_clis()
    if not clis:
        return "(no facts configured)"
    lines = []
    for cli_name in clis:
        lines.append(f"[{cli_name}]")
        for tier in ("economy", "standard", "strong"):
            model_id = matrix.get_model(cli_name, tier)
            if model_id is not None:
                lines.append(f"  {tier:8} = {model_id}")
    return "\n".join(lines)


def _format_model_matrix_policy(matrix: FileModelMatrix) -> str:
    """Render `[policy]` — classification -> tier, phase -> tier,
    on_missing (FR-R9)."""
    if not matrix.policy:
        return "(no policy configured)"
    return "\n".join(f"{key} = {value}" for key, value in sorted(matrix.policy.items()))


def _format_model_matrix_show(matrix: FileModelMatrix) -> str:
    return (
        "facts (adapter -> tier -> model):\n"
        f"{_format_model_matrix_facts(matrix)}\n\n"
        "policy (classification -> tier, phase -> tier, on_missing):\n"
        f"{_format_model_matrix_policy(matrix)}"
    )


def _dispatch_model_matrix_show(matrix_path: Path) -> DispatchOutcome:
    try:
        matrix = FileModelMatrix(matrix_path)
    except FileNotFoundError:
        return DispatchOutcome(content=f"model-matrix.conf not found at {matrix_path}")
    except ValueError as exc:
        return DispatchOutcome(content=f"model-matrix.conf is invalid: {exc}")
    return DispatchOutcome(content=_format_model_matrix_show(matrix))


def _dispatch_model_matrix_edit(
    matrix_path: Path,
    adapter_registry: AdapterRegistry,
    run_fn: Callable[[list[str]], int],
    get_editor: Callable[[], str | None],
) -> DispatchOutcome:
    editor = get_editor()
    if not editor:
        print(
            "$EDITOR is not set — cannot open model-matrix.conf. "
            "Set $EDITOR and try again.",
            file=sys.stderr,
        )
        return DispatchOutcome(long_running=False)

    returncode = run_fn([editor, str(matrix_path)])
    if returncode != 0:
        print(
            f"editor {editor!r} exited with status {returncode}; "
            "model-matrix.conf left as-is",
            file=sys.stderr,
        )
        return DispatchOutcome(long_running=False)

    try:
        matrix = FileModelMatrix(matrix_path)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"model-matrix.conf is invalid after edit: {exc}. "
            "Adapter dictionaries were not repopulated.",
            file=sys.stderr,
        )
        return DispatchOutcome(long_running=False)

    populate_adapter_dictionaries_from_matrix(matrix, adapter_registry)
    print("model-matrix.conf saved; adapter dictionaries repopulated")
    return DispatchOutcome(long_running=False)


def _default_run_editor(cmd: list[str]) -> int:
    return subprocess.run(cmd).returncode


def _default_get_editor() -> str | None:
    return os.environ.get("EDITOR") or None


def _default_run_matrix_lint(matrix_path: Path) -> tuple[int, str]:
    """Run the existing `scripts/matrix-lint` gate against `matrix_path`
    (FR-K5) — reused, not reimplemented. `scripts/` is copied alongside
    `model-matrix.conf` into every project directory by `orchestrate init`
    (see `_handle_init`), so it is always `matrix_path.parent / "scripts" /
    "matrix-lint"`.
    """
    lint_script = matrix_path.parent / "scripts" / "matrix-lint"
    result = subprocess.run(
        [sys.executable, str(lint_script), "--matrix", str(matrix_path)],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout


def _dispatch_model_matrix_validate(
    matrix_path: Path, lint_fn: Callable[[Path], tuple[int, str]]
) -> DispatchOutcome:
    returncode, output = lint_fn(matrix_path)
    if returncode == 0:
        print("valid")
    else:
        print(output.strip() or "matrix-lint reported errors", file=sys.stderr)
    return DispatchOutcome(long_running=False)


def build_configure_model_matrix_dispatch(
    matrix_path: Path,
    adapter_registry: AdapterRegistry,
    *,
    run_fn: Callable[[list[str]], int] = _default_run_editor,
    get_editor: Callable[[], str | None] = _default_get_editor,
    lint_fn: Callable[[Path], tuple[int, str]] = _default_run_matrix_lint,
) -> DispatchHook:
    """Build the `DispatchHook` for the `configure > model-matrix` submenu's
    three leaves (UC-10, FR-R9, FR-K5, ST-0050).

    `run_fn`/`get_editor` are the injectable subprocess/env seams for
    `edit` — same convention as `input_fn`/`discover_fn` elsewhere in this
    module — so tests never spawn a real `$EDITOR` process. `lint_fn` is the
    equivalent seam for `validate`, so tests never depend on
    `scripts/matrix-lint` being present on disk relative to a tmp-path
    matrix file (its default, `_default_run_matrix_lint`, does exercise the
    real script end to end when a test does provide one).
    """

    def _dispatch(node: MenuNode) -> DispatchOutcome:
        if node.id == "configure.model-matrix.show":
            return _dispatch_model_matrix_show(matrix_path)
        if node.id == "configure.model-matrix.edit":
            return _dispatch_model_matrix_edit(
                matrix_path, adapter_registry, run_fn, get_editor
            )
        if node.id == "configure.model-matrix.validate":
            return _dispatch_model_matrix_validate(matrix_path, lint_fn)

        raise ValueError(
            f"no configure/model-matrix action registered for menu node '{node.id}'"
        )

    return _dispatch


# --- Run-step leaves (menu mode; ST-0053, UC-11, FR-S4, BR-055) -------------
#
# `run-step`'s four runtime-populated levels — agent (with tier shown) ->
# skill scope (`all skills` default plus declared skills, FR-S4) -> adapter
# (default marked ★) -> model (tier-resolved default marked ★, BR-055) —
# follow the same eager nested-construction shape `build_configure_cli_menu`
# already established for `configure > cli` (adapter -> action -> tier), one
# level deeper. `node.id`s are dot-segmented:
# `run-step.{agent}.{skill-or-all-skills}.{adapter}.{tier}` — the leaf
# encodes the *tier*, not the model id, because real model ids contain
# literal dots (e.g. "gpt-5.4", see tests/test_model_dictionary_menu.py) and
# would corrupt a dot-delimited id; the tier is closed vocabulary
# (economy/standard/strong) and never collides. The concrete model id is
# re-resolved from `adapter_registry.get_model(adapter, tier)` at dispatch
# time, the same re-validate-at-dispatch discipline
# `_dispatch_configure_adapter` already documents. The leaf dispatches to the
# exact same `build_parser()` -> `_resolve_interactive()` -> `_build_runtime()`
# -> `_handle_run_step()` chain direct mode's own `run-step` branch in
# `main()` uses — no reimplementation, no new validation (FR-S2/BR-050 skill
# validation still happens exactly once, inside `_handle_run_step`).

_RUN_STEP_ALL_SKILLS_ID_SEGMENT = "all-skills"


def _list_step_agents(agents_dir: Path) -> list[AgentInfo]:
    """List every agent definition in *agents_dir* (UC-11, "list of agents
    from agents/ registry, showing name + tier").

    Unlike `MarkdownAgentRegistry.resolve`, which resolves exactly one agent
    for a given phase+role, `run-step` lists *every* declared agent — the
    spec's own example rendering includes `coaching-agent`, which is never a
    phase author/reviewer. Reuses the same private frontmatter parsers
    `_load_step_agent` already imports; no new parsing logic. Returns `[]`
    for a missing directory rather than raising — an empty `run-step` menu
    is a valid (if unhelpful) state, not a crash (ADR-0016).
    """
    from orchestrator.adapters.agent_registry import _parse_skills, _parse_tier

    if not agents_dir.is_dir():
        return []

    agents = []
    for definition_path in sorted(agents_dir.glob("*.md")):
        agents.append(
            AgentInfo(
                name=definition_path.stem,
                outputs=_parse_outputs(definition_path),
                definition_path=definition_path,
                skills=_parse_skills(definition_path),
                tier=_parse_tier(definition_path),
            )
        )
    return agents


def _run_step_tier_label(agent_info: AgentInfo) -> str:
    """VR-041: a null declared tier resolves as `standard` — reflected in the
    display label, not only in `ModelResolver.resolve_agent_tier`."""
    return agent_info.tier if agent_info.tier is not None else Tier.STANDARD.value


def build_run_step_model_menu(
    agent_info: AgentInfo,
    skill_segment: str,
    adapter_name: str,
    adapter_registry: AdapterRegistry,
) -> MenuNode:
    """Build the populated `run-step > {agent} > {skill-or-all} > {adapter}`
    submenu: one function leaf per tier this adapter's dictionary maps
    (cli_specification.md "[list of models for this adapter, tier-resolved
    default marked ★]"), the tier-resolved default marked ★ (BR-055).

    `ModelResolver(None, ...)`: `resolve_agent_tier` (ST-0049) only ever
    reads `self._adapter_registry`, never `self._matrix` (verified in
    `model_resolver.py`) — the adapter dictionaries it reads are already
    populated from `model-matrix.conf` at menu-mode startup
    (`populate_adapter_dictionaries_from_matrix`, `_run_menu_mode`), so no
    real `ModelMatrix` is needed here. A `ConfigError` (e.g. an incomplete
    dictionary under `on_missing_tier="halt"`) degrades to "no ★ marked"
    rather than raising out of menu-tree construction (ADR-0016) —
    `MenuController._opening_index` already falls back to index 0 when no
    child carries `is_default` (BR-032).
    """
    try:
        pairs = adapter_registry.list_models(adapter_name)
    except KeyError:
        pairs = []

    resolver = ModelResolver(None, adapter_name, adapter_registry)
    try:
        default_model = resolver.resolve_agent_tier(agent_info.tier)
    except ConfigError:
        default_model = None

    children = []
    marked = False
    for tier, model_id in sorted(pairs):
        is_default = not marked and model_id == default_model
        if is_default:
            marked = True
        children.append(
            MenuNode(
                id=(
                    f"run-step.{agent_info.name}.{skill_segment}.{adapter_name}.{tier}"
                ),
                label=f"{model_id} [{tier}]",
                type=MenuNodeType.FUNCTION,
                is_default=is_default,
            )
        )

    return MenuNode(
        id=f"run-step.{agent_info.name}.{skill_segment}.{adapter_name}",
        label=adapter_name,
        type=MenuNodeType.MENU,
        children=children,
    )


def build_run_step_skill_menu(
    agent_info: AgentInfo,
    skill_segment: str,
    skill_label: str,
    adapter_registry: AdapterRegistry,
    config_store: ConfigStore,
) -> MenuNode:
    """Build the populated `run-step > {agent} > {skill-or-all}` submenu: one
    menu node per registered adapter (cli_specification.md "[list of
    registered adapters, default adapter marked ★]"), mirroring
    `build_configure_defaults_adapter_menu`'s read-with-fallback for the
    currently effective default adapter. A malformed `config.toml` degrades
    to "no adapter marked" (same precedent as
    `build_configure_defaults_adapter_menu`) — the mutating leaf (the model
    selection at the bottom of this chain) re-reads and reports a malformed
    file when it actually runs (`_build_runtime` -> `TomlConfigStore`, via
    whatever leaf ultimately touches it).
    """
    try:
        current_adapter = SettingsResolver(config_store).resolve("adapter")
    except ConfigStoreError:
        current_adapter = None

    children = [
        replace(
            build_run_step_model_menu(
                agent_info, skill_segment, entry.name, adapter_registry
            ),
            is_default=(entry.name == current_adapter),
        )
        for entry in adapter_registry.list_adapters()
    ]

    return MenuNode(
        id=f"run-step.{agent_info.name}.{skill_segment}",
        label=skill_label,
        type=MenuNodeType.MENU,
        children=children,
    )


def build_run_step_agent_menu(
    agent_info: AgentInfo,
    adapter_registry: AdapterRegistry,
    config_store: ConfigStore,
) -> MenuNode:
    """Build the populated `run-step > {agent}` submenu: `all skills`
    (default ★, always first, unconditionally — BR-052) plus each of the
    agent's declared skills (FR-S4)."""
    skill_children = [
        replace(
            build_run_step_skill_menu(
                agent_info,
                _RUN_STEP_ALL_SKILLS_ID_SEGMENT,
                _ALL_SKILLS_SENTINEL,
                adapter_registry,
                config_store,
            ),
            is_default=True,
        )
    ]
    skill_children.extend(
        build_run_step_skill_menu(
            agent_info, skill, skill, adapter_registry, config_store
        )
        for skill in agent_info.skills
    )

    return MenuNode(
        id=f"run-step.{agent_info.name}",
        label=f"{agent_info.name} [{_run_step_tier_label(agent_info)}]",
        type=MenuNodeType.MENU,
        children=skill_children,
    )


def build_run_step_menu(
    agents_dir: Path,
    adapter_registry: AdapterRegistry,
    config_store: ConfigStore,
) -> MenuNode:
    """Build the populated `run-step` submenu (UC-11, cli_specification.md
    §Run-step): one menu node per agent, no `★` at this depth (the operator
    must actively choose an agent — the one non-default selection of the
    "four selections deep... three Enter presses on ★ defaults" happy path).
    """
    children = [
        build_run_step_agent_menu(agent_info, adapter_registry, config_store)
        for agent_info in _list_step_agents(agents_dir)
    ]
    return MenuNode(
        id="run-step", label="run-step", type=MenuNodeType.MENU, children=children
    )


def build_run_step_dispatch() -> DispatchHook:
    """Build the `DispatchHook` for the `run-step` submenu's leaves (UC-11,
    FR-V3, ST-0053).

    Composes the identical argv direct mode would parse — `["--adapter", a,
    "--model", m, "run-step", agent]`, plus `["--skill", skill]` only for a
    specific skill, omitted entirely for `all skills` (matching
    cli_specification.md's direct-mode-equivalents table row for row) — and
    feeds it through the same `build_parser()` -> `_resolve_interactive()` ->
    `_build_runtime()` -> `_handle_run_step()` chain `main()`'s own
    `run-step` branch uses, so behaviour (validation, prompt composition,
    gate handling, exit semantics) is identical by construction, not by
    reimplementation. Takes no injected dependencies — every call it makes
    is to an existing module-level function tests already monkeypatch
    (`cli._build_runtime`, `cli._handle_run_step`), the same seam
    `build_manage_run_dispatch`'s `resume` leaf uses.

    Long-running like `manage-run.resume`: there is no async execution seam
    in this codebase, so the invocation runs synchronously inside the hook;
    `DispatchOutcome(long_running=True)` tells `MenuController` to transition
    to `EXITED` once it returns, instead of re-entering the menu
    (cli_specification.md: "Exits TUI, switches to streaming terminal
    output"). Raises (rather than catching) `ValueError` from
    `_handle_run_step`'s pre-launch validation (unknown agent, undeclared
    skill) — `build_root_dispatch`'s single outer `try/except Exception`
    (ADR-0016) already reports it without exiting the TUI, the same
    convention every other dispatch hook in this module follows.
    """

    def _dispatch(node: MenuNode) -> DispatchOutcome:
        parts = node.id.split(".", 4)
        if len(parts) != 5 or parts[0] != "run-step":
            raise ValueError(f"no run-step action registered for menu node '{node.id}'")
        _, agent_name, skill_segment, adapter_name, tier = parts

        repo_root = Path.cwd()
        adapter_registry = TomlAdapterRegistry(repo_root / ".orchestrator")
        model_id = adapter_registry.get_model(adapter_name, tier)
        if model_id is None:
            raise ValueError(
                f"no model configured for adapter {adapter_name!r} and tier {tier!r}"
            )

        skill = (
            None if skill_segment == _RUN_STEP_ALL_SKILLS_ID_SEGMENT else skill_segment
        )

        argv = ["--adapter", adapter_name, "--model", model_id, "run-step", agent_name]
        if skill is not None:
            argv += ["--skill", skill]

        args = build_parser().parse_args(argv)
        _resolve_interactive(args)
        runtime = _build_runtime(args, classification=None)
        # BR-040/QS-20: resolved effective timeout, not the raw (omitted,
        # so `None`) `--timeout` flag — see the `main()` run-step branch's
        # matching comment.
        _handle_run_step(runtime, args.agent, runtime.timeout_s, args.skill)

        return DispatchOutcome(long_running=True)

    return _dispatch


# --- Master dispatch hook (menu mode composition root; ST-0040, ADR-0016) ---
#
# `build_root_dispatch` is the single `DispatchHook` `MenuController`
# receives. It composes the per-submenu hooks by `node.id` prefix — the
# status/backlog hooks ST-0055/ST-0057 already built, plus the manage-run
# (ST-0040), configure-defaults (ST-0044), configure-cli-list (ST-0047),
# configure-cli (ST-0048), configure-model-matrix (ST-0050), and run-step
# (ST-0053) hooks — and falls back to an honest "not yet implemented"
# message for any leaf under a menu no story has populated yet (`init`,
# `run-phase`; see ST-0040.md's Analysis for why). A later story wires a new
# area by adding
# one `build_*_dispatch(...)` call here and one `if node.id.startswith(...)`
# branch — the same shape status/backlog/manage-run/configure already
# follow. `configure.cli-list.`, `configure.cli.`, and
# `configure.model-matrix.` are all checked before the more general
# `configure.` prefix (which routes to `configure_defaults_dispatch`) so
# their own leaves aren't swallowed by that branch.


def build_root_dispatch(
    status_service: StatusService,
    backlog_store,
    build_runtime: Callable[[], "_Runtime"],
    config_store: ConfigStore,
    adapter_registry: AdapterRegistry,
    matrix_path: Path = Path("model-matrix.conf"),
) -> DispatchHook:
    status_dispatch = build_status_dispatch(status_service)
    backlog_dispatch = build_backlog_dispatch(backlog_store)
    manage_run_dispatch = build_manage_run_dispatch(build_runtime)
    configure_defaults_dispatch = build_configure_defaults_dispatch(
        config_store, adapter_registry
    )
    cli_list_dispatch = build_cli_list_dispatch(adapter_registry)
    configure_cli_dispatch = build_configure_cli_dispatch(adapter_registry)
    configure_model_matrix_dispatch = build_configure_model_matrix_dispatch(
        matrix_path, adapter_registry
    )
    run_step_dispatch = build_run_step_dispatch()

    def _dispatch(node: MenuNode) -> DispatchOutcome:
        try:
            if node.id.startswith("status."):
                return status_dispatch(node)
            if node.id.startswith("backlog."):
                return backlog_dispatch(node)
            if node.id.startswith("manage-run."):
                return manage_run_dispatch(node)
            if node.id.startswith("run-step."):
                return run_step_dispatch(node)
            if node.id.startswith("configure.cli-list."):
                return cli_list_dispatch(node)
            if node.id.startswith("configure.cli."):
                return configure_cli_dispatch(node)
            if node.id.startswith("configure.model-matrix."):
                return configure_model_matrix_dispatch(node)
            if node.id.startswith("configure."):
                return configure_defaults_dispatch(node)
        except Exception as exc:
            # ADR-0016: menu mode must never crash on a leaf's failure — a
            # raising handler is reported and control returns to the menu,
            # exactly like direct mode's own top-level `except Exception`
            # in `main()` reports a failure without a traceback.
            print(str(exc), file=sys.stderr)
            return DispatchOutcome(long_running=False)

        # Leaf under a menu no story has populated yet (init, run-phase).
        # Currently unreachable through real navigation (those menus have no
        # children), but this keeps the master hook total and honest if that
        # changes before its owning story lands.
        print(
            f"'{node.label}' is not yet implemented in menu mode. "
            "Use the equivalent direct-mode command — see `orchestrate --help`.",
            file=sys.stderr,
        )
        return DispatchOutcome(long_running=False)

    return _dispatch


# --- Dual-mode entry point (ST-0040, ADR-0016, UC-08) -----------------------
#
# `main()` routes a bare invocation here (see the `effective_argv` check at
# the top of `main()`); every subcommand still goes through the unchanged
# direct-mode `parser.parse_args` path below (FR-V2, BR-035).


def _supports_menu_mode() -> bool:
    """BR-030: menu mode requires stdin *and* stdout attached to a TTY.

    Deeper terminal-capability negotiation (T-29 — arrow-key sequences,
    `TERM` quirks) is explicitly the renderer adapter's problem per
    ADR-0016's own risk list, not this entry-point decision's.
    """
    return sys.stdin.isatty() and sys.stdout.isatty()


def _print_menu_unavailable() -> None:
    """FR-V4/BR-031/T-30: honest diagnostic, no partial/degraded menu."""
    print(
        "orchestrate: no interactive terminal detected — menu mode is unavailable.\n"
        "Use a direct-mode command instead, for example:\n"
        "  orchestrate status\n"
        "  orchestrate run-phase <phase>\n"
        "  orchestrate resume | approve | reject | release | abort\n"
        "  orchestrate --help              # full command reference"
    )


def _build_menu_tree(
    backlog_store,
    adapter_registry: AdapterRegistry,
    config_store: ConfigStore,
    agents_dir: Path,
) -> MenuNode:
    """Merge the pure static tree (`menu_tree.build_root_menu`) with the
    `backlog > view story` (ST-0057), `configure > defaults > adapter`
    (ST-0044), `configure > cli-list > remove adapter` (ST-0047),
    `configure > cli` (ST-0048), and `run-step` (ST-0053) submenus' live,
    runtime-populated children.

    `menu_tree.py` deliberately never touches a store (module docstring:
    "no node embeds a service call"), so the composition root is where the
    static tree and the runtime snapshots meet — same reasoning
    `build_backlog_view_story_menu`'s own docstring already documents.
    """
    populated_view_story = build_backlog_view_story_menu(backlog_store)
    populated_configure_adapter = build_configure_defaults_adapter_menu(
        adapter_registry, config_store
    )
    populated_remove_adapter = build_cli_list_remove_adapter_menu(adapter_registry)
    populated_configure_cli = build_configure_cli_menu(adapter_registry)
    populated_run_step = build_run_step_menu(agents_dir, adapter_registry, config_store)

    def _merge(node: MenuNode) -> MenuNode:
        if node.id == "backlog.view-story":
            return populated_view_story
        if node.id == "configure.defaults.adapter":
            return populated_configure_adapter
        if node.id == "configure.cli-list.remove-adapter":
            return populated_remove_adapter
        if node.id == "configure.cli":
            return populated_configure_cli
        if node.id == "run-step":
            return populated_run_step
        if node.children:
            return replace(node, children=[_merge(child) for child in node.children])
        return node

    root = build_root_menu()
    return replace(root, children=[_merge(child) for child in root.children])


def _run_menu_mode() -> int:
    """FR-V1: bare `orchestrate` on a supported interactive terminal.

    Builds nothing store-backed until `_supports_menu_mode()` has already
    confirmed a TTY (BR-031: no partial menu, no run-state mutation on the
    fallback path).
    """
    if not _supports_menu_mode():
        _print_menu_unavailable()
        return 0

    repo_root = Path.cwd()
    orch_dir = repo_root / ".orchestrator"
    run_store = JsonRunStateStore(orch_dir)
    findings_store = FilesystemFindingsStore(orch_dir / "findings")
    backlog_store = MarkdownBacklogStore(repo_root / "backlog")
    status_service = StatusService(run_store, findings_store)
    config_store = TomlConfigStore(orch_dir)
    adapter_registry = TomlAdapterRegistry(orch_dir)
    matrix_path = repo_root / "model-matrix.conf"
    # ADR-0016: entering menu mode must never crash. An unresolvable agents
    # directory (VR-011-adjacent — see `_resolve_agents_dir`) degrades to an
    # empty `run-step` menu (`_list_step_agents` already returns `[]` for a
    # non-existent directory) rather than blocking entry; the operator
    # discovers the real problem the first time they actually try to run
    # something, same as every other degrade-not-crash precedent here.
    try:
        agents_dir = _resolve_agents_dir(repo_root)
    except ValueError:
        agents_dir = repo_root / "factory" / "agents"

    # ADR-0017 point 5 / ADR-0018 point 3, ST-0050 acceptance criteria: the
    # matrix facts populate every registered adapter's dictionary at
    # startup, not only after an explicit `configure > model-matrix > edit`.
    # A missing or malformed matrix is not fatal to entering menu mode —
    # `configure > model-matrix > validate` is the leaf that surfaces that
    # problem to the operator; entry itself must never crash (ADR-0016).
    if matrix_path.exists():
        try:
            populate_adapter_dictionaries_from_matrix(
                FileModelMatrix(matrix_path), adapter_registry
            )
        except ValueError:
            pass

    def _menu_runtime_factory() -> "_Runtime":
        # Mirrors direct-mode `resume`'s defaults exactly (same parser,
        # same flag defaults) — the only difference is `interactive=True`,
        # which is already an established fact by the time an operator is
        # driving a live menu session (that's how they got here).
        ns = build_parser().parse_args(["resume"])
        ns.interactive = True
        return _build_runtime(ns, classification=None)

    root = _build_menu_tree(backlog_store, adapter_registry, config_store, agents_dir)
    dispatch = build_root_dispatch(
        status_service,
        backlog_store,
        _menu_runtime_factory,
        config_store,
        adapter_registry,
        matrix_path,
    )
    renderer = TerminalMenuRenderer()
    controller = MenuController(root, renderer, dispatch)
    controller.run()
    return 0


def _handle_abort(args) -> int:
    repo_root = Path.cwd()
    orch_dir = repo_root / ".orchestrator"

    run_store = JsonRunStateStore(orch_dir)
    run_lock = FileRunLock(orch_dir)

    run = run_store.load()
    if run is None or run.mode == RunMode.COMPLETE:
        print("no active run", file=sys.stderr)
        return 1

    if run_lock.is_held_by_other():
        print(
            "run lock is held by another process — cannot abort safely", file=sys.stderr
        )
        return 1

    run.mode = RunMode.COMPLETE
    run_store.save(run)
    run_lock.release()

    print("Run aborted.")
    return 0


def _handle_release(args) -> int:
    repo_root = Path.cwd()
    orch_dir = repo_root / ".orchestrator"

    run_store = JsonRunStateStore(orch_dir)
    run_lock = FileRunLock(orch_dir)

    run = run_store.load()
    if run is None:
        print("no active run", file=sys.stderr)
        return 1

    if run.mode != RunMode.HALTED:
        print("Run is not halted.", file=sys.stderr)
        return 1

    if run_lock.is_held_by_other():
        print(
            "run lock is held by another process — cannot release safely",
            file=sys.stderr,
        )
        return 1

    halted_phase = next(
        (phase for phase in run.phases if phase.status == PhaseStatus.HALTED), None
    )
    if halted_phase is None:
        print("Cannot release: no halted phase found.", file=sys.stderr)
        return 1
    if halted_phase.halted_from is None:
        print("Cannot release: no halted_from recorded (VR-029).", file=sys.stderr)
        return 1

    restored_status = halted_phase.halted_from
    halted_phase.status = restored_status
    halted_phase.iteration = 0
    halted_phase.halted_from = None
    run.iteration = 0
    run.mode = RunMode.PAUSED
    run_store.save(run)
    run_lock.release()

    print(
        f"Released phase '{halted_phase.name}' back to {restored_status.value}. "
        "Run `resume` to continue."
    )
    return 0


_SCAFFOLD_DIRS = [
    "docs/spec/use_cases",
    "docs/spec/supplementary_specs",
    "docs/adr",
    "docs/reviews",
    "docs/findings",
    "backlog",
]

_CLI_INSTRUCTION_FILES: dict[str, str] = {
    "copilot": ".github/copilot-instructions.md",
    "claude": "CLAUDE.md",
    "gemini": "GEMINI.md",
    "cursor": ".cursor/rules/dev-workflow.md",
    "codex": "AGENTS.md",
}

_COPY_DIRS = ["agents", "skills", "scripts"]

_GITIGNORE_ENTRIES = ["agents/", "skills/", "scripts/", ".orchestrator/"]

_INSTRUCTION_TEMPLATE = """\
## Active Agent

Follow the instructions in [{agent_name}](agents/{agent_name}.md).

## Scope — Read These Files Only

1. Your agent definition: `agents/{agent_name}.md`
2. Your skills — read the `SKILL.md` in each directory:
{skill_lines}
3. `CONTEXT.md` if it exists — use the project's domain vocabulary throughout.
4. Files listed in your agent's `inputs:` frontmatter.

## Do Not Read

These are orchestrator internals — not agent concerns:

- Other `.md` files in `agents/` — they belong to other workflow phases.
- `scripts/` — gate scripts executed by the orchestrator, not by agents.
- `.orchestrator/` — run state managed by the orchestrator.
- `model-matrix.conf` — orchestrator model configuration.

## Communication Style

This workflow runs in **caveman mode** by default — terse, no filler, full technical accuracy.
See [skills/caveman/](skills/caveman/).

Two exceptions are always written in **Plain English after Strunk & White**:

1. **Specification prose** — everything under `docs/spec/**`.
2. **Documentation prose** — arc42 chapters, ADRs, review reports, READMEs, `CONTEXT.md`.

## Handoff — Orchestrator Managed

You are running inside the agent_factory orchestrator. **Do not** tell the user to
start a new session or manually run another agent. When your work is complete,
tell the user to **exit this session** (Ctrl+C or `/exit`) so the orchestrator
can gate your artifacts and proceed to the next phase automatically.

Ignore any handoff instructions in your agent definition — the orchestrator
handles phase transitions.

## Always Available — Utility Agents

These agents are available in every session regardless of the active phase.
Invoke them when the user asks:

- **Coaching Agent** — [agents/coaching-agent.md](agents/coaching-agent.md).
  Triggers: "retrospective", "retro", "what went well", "session review".
  Runs inline (not a subprocess) — reads the live session history.
"""


def _compose_cta(ctx: InvocationContext, has_findings: bool) -> str:
    """Derive a call-to-action string from invocation context.

    Mirrors ``FilePromptComposer._call_to_action`` but used when embedding the
    CTA into the instruction file for interactive sessions (no ``-p`` flag).
    """
    if ctx.phase == "standalone":
        return "Execute the workflow defined in your Agent Definition above."
    if ctx.role == AgentRole.AUTHOR:
        if ctx.iteration == 0:
            return (
                f"Begin the {ctx.phase} phase. Execute the workflow "
                "defined in your Agent Definition above, starting at Step 1."
            )
        if has_findings:
            return (
                f"This is iteration {ctx.iteration} of the "
                f"{ctx.phase} phase. Address the findings listed above, "
                "then re-execute your workflow."
            )
        return (
            f"This is iteration {ctx.iteration} of the "
            f"{ctx.phase} phase. Your prior attempt failed the gate. "
            "Re-execute your workflow and ensure all changes are committed."
        )
    if ctx.iteration == 0:
        return (
            f"Review the {ctx.phase} artifacts. Follow the review "
            "workflow in your Agent Definition. File findings per the "
            "specified format."
        )
    return (
        f"This is iteration {ctx.iteration} of the "
        f"{ctx.phase} review. The author has addressed prior findings. "
        "Re-review the artifacts and file any remaining issues."
    )


def _render_instruction_file(
    agent_name: str, skills: list[str], call_to_action: str | None = None
) -> str:
    """Render the instruction file content for a specific agent.

    When *call_to_action* is provided (interactive mode), it is appended as a
    ``## Call to Action`` section so the agent begins work immediately.
    """
    if skills:
        skill_lines = "\n".join(f"   - `skills/{s}/`" for s in skills)
    else:
        skill_lines = "   (none declared)"
    content = _INSTRUCTION_TEMPLATE.format(
        agent_name=agent_name,
        skill_lines=skill_lines,
    )
    if call_to_action:
        content += f"\n## Call to Action\n\n{call_to_action}\n"
    return content


def _update_instruction_file(
    cwd: Path, agent_name: str, skills: list[str], call_to_action: str | None = None
) -> None:
    """Rewrite the CLI instruction file to scope the active agent.

    Scans for the first existing instruction file (Copilot, Claude, etc.)
    and overwrites it with the scoped template.
    """
    for _cli_name, rel_path in _CLI_INSTRUCTION_FILES.items():
        path = cwd / rel_path
        if path.exists():
            path.write_text(
                _render_instruction_file(agent_name, skills, call_to_action)
            )
            return


def _handle_init(args) -> int:
    try:
        root = _tooling_root()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    # 1. Resolve project directory
    if args.project:
        project_dir = Path(args.project).resolve()
        project_dir.mkdir(parents=True, exist_ok=True)
    else:
        project_dir = Path.cwd()

    # 2. git init if needed
    if not (project_dir / ".git").is_dir():
        subprocess.run(
            ["git", "init"], cwd=str(project_dir), capture_output=True, check=True
        )

    # 3. Copy tooling dirs (idempotent — overwrite on re-init)
    # Source lives under factory/ in the tooling root (ST-0065); the
    # destination in the target project stays bare (project_dir / name) —
    # that target-side convention is unchanged by this story.
    for name in _COPY_DIRS:
        src = root / "factory" / name
        dst = project_dir / name
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    # 4. Update .gitignore
    gitignore = project_dir / ".gitignore"
    existing = gitignore.read_text().splitlines() if gitignore.exists() else []
    added = [e for e in _GITIGNORE_ENTRIES if e not in existing]
    if added:
        with gitignore.open("a") as f:
            for entry in added:
                f.write(entry + "\n")

    # 5. Scaffold project directories
    for d in _SCAFFOLD_DIRS:
        (project_dir / d).mkdir(parents=True, exist_ok=True)

    # 6. Copy model-matrix.conf template
    src_matrix = root / "orchestrator" / "model-matrix.conf"
    dst_matrix = project_dir / "model-matrix.conf"
    if src_matrix.exists() and not dst_matrix.exists():
        shutil.copy2(src_matrix, dst_matrix)

    # 6b. Copy .pre-commit-config.yaml template
    src_pcfg = root / "orchestrator" / "pre-commit-config.yaml"
    dst_pcfg = project_dir / ".pre-commit-config.yaml"
    if src_pcfg.exists() and not dst_pcfg.exists():
        shutil.copy2(src_pcfg, dst_pcfg)

    # 7. Create instruction file
    cli_name = args.cli_name
    if cli_name is None:
        if sys.stdin.isatty():
            cli_name = _pick_cli()
        else:
            cli_name = "codex"

    rel_path = _CLI_INSTRUCTION_FILES[cli_name]
    instr_path = project_dir / rel_path
    # Parse skills from the requirements agent (first phase default)
    default_agent = "requirements-agent"
    default_agent_path = project_dir / "agents" / f"{default_agent}.md"
    default_skills: list[str] = []
    if default_agent_path.is_file():
        from orchestrator.adapters.agent_registry import _parse_skills

        default_skills = _parse_skills(default_agent_path)
    content = _render_instruction_file(default_agent, default_skills)
    if instr_path.exists():
        print(f"Instruction file already exists: {rel_path}")
        print("Overwriting with scoped template.")
    instr_path.parent.mkdir(parents=True, exist_ok=True)
    instr_path.write_text(content)

    print(f"Project initialized at {project_dir}")
    print(f"Tooling copied from {root}")
    print(f"Update tooling: cd {project_dir} && orchestrate init --cli {cli_name}")
    print()
    print("Next steps:")
    print("  1. Edit model-matrix.conf to set your preferred models")
    print("  2. Run the requirements agent:")
    print()
    print("     orchestrate --interactive run-phase requirements")
    return 0


def _pick_cli() -> str:
    """Interactive CLI picker for init --cli."""
    options = list(_CLI_INSTRUCTION_FILES.items())
    print("Which CLI do you use?")
    for i, (name, path) in enumerate(options, 1):
        print(f"  {i}. {name} ({path})")
    while True:
        try:
            choice = input(f"Choice [1-{len(options)}]: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx][0]
        except (ValueError, EOFError):
            pass
        print(f"Enter a number 1-{len(options)}")


def _ensure_run_branch(repo_root: Path, branch: str) -> None:
    """Create or check out the dedicated run branch (BR-016, BR-017, VR-016).

    If the branch doesn't exist, create it from the current HEAD. If it
    exists, check it out. The orchestrator always works on the run branch
    so gate commits land on the correct ref.
    """
    # Check current branch
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    current = result.stdout.strip()
    if current == branch:
        return  # already on the run branch

    # Check if the branch exists
    check = subprocess.run(
        ["git", "rev-parse", "--verify", branch],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if check.returncode == 0:
        # Branch exists — check it out
        subprocess.run(
            ["git", "checkout", branch],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
    else:
        # Create the branch from HEAD
        subprocess.run(
            ["git", "checkout", "-b", branch],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )


def _build_runtime(args, classification: str | None = None) -> _Runtime:
    repo_root = Path.cwd()
    orch_dir = repo_root / ".orchestrator"
    agents_dir = _resolve_agents_dir(repo_root)

    run_store = JsonRunStateStore(orch_dir)
    run_lock = FileRunLock(orch_dir)
    findings_store = FilesystemFindingsStore(orch_dir / "findings")
    _backlog_store = MarkdownBacklogStore(repo_root / "backlog")
    model_matrix = FileModelMatrix(repo_root / "model-matrix.conf")

    # BR-040/FR-Q3/QS-20: this is the ONE place direct mode and menu mode
    # both funnel through to resolve `adapter`/`timeout`/`cap` — the same
    # `SettingsResolver` `tests/test_settings_resolver.py` already unit-tests
    # in isolation, now actually wired to a live `TomlConfigStore` instead
    # of being dead code. `cli_flag=args.X` is `None` whenever the flag was
    # omitted (see `build_parser()`'s `default=None` on all three) — that
    # `None` is what lets a persisted `configure > defaults` value be seen
    # at all; menu mode's `run-step` leaf already resolves its own
    # menu-selected adapter into an equivalent `--adapter` argv token before
    # this function ever runs (`build_run_step_dispatch`), so from here both
    # entry paths are indistinguishable — one resolver, one code path,
    # exactly what QS-20 requires.
    config_store = TomlConfigStore(orch_dir)
    settings = SettingsResolver(config_store)
    adapter_name = settings.resolve("adapter", cli_flag=args.adapter)
    timeout_s = settings.resolve("timeout", cli_flag=args.timeout)
    cap = settings.resolve("cap", cli_flag=args.cap)

    model_resolver = _ExplicitModelResolver(
        ModelResolver(model_matrix, adapter_name), args.model
    )
    adapter = _build_adapter(adapter_name, args.model, interactive=args.interactive)
    gate_runner = WorkingTreeGate(repo_root)
    agent_registry = MarkdownAgentRegistry(agents_dir)
    logger = FileInvocationLog(orch_dir)
    phase_runner = PhaseRunner(
        adapter=adapter,
        gate_runner=gate_runner,
        findings_store=findings_store,
        finding_ingestor=DefaultFindingIngestor(
            findings_store, repo_root / "docs" / "findings"
        ),
        run_store=run_store,
        agent_registry=agent_registry,
        prompt_composer=FilePromptComposer(),
        logger=logger,
        loop_policy=LoopPolicy(cap=cap),
        model_resolver=model_resolver,
        clock=_SystemClock(),
        cwd=repo_root,
        timeout_s=timeout_s,
        interactive=args.interactive,
        classification=classification,
        on_agent_start=lambda info, ctx, has_findings: _update_instruction_file(
            repo_root,
            info.name,
            info.skills,
            call_to_action=_compose_cta(ctx, has_findings)
            if not args.no_interactive
            else None,
        ),
    )

    return _Runtime(
        repo_root=repo_root,
        orch_dir=orch_dir,
        agents_dir=agents_dir,
        run_store=run_store,
        run_lock=run_lock,
        approval_service=ApprovalService(
            run_store, findings_store, gate_runner, agent_registry
        ),
        status_service=StatusService(run_store, findings_store),
        phase_runner=phase_runner,
        prompt_composer=FilePromptComposer(),
        adapter=adapter,
        agent_registry=agent_registry,
        logger=logger,
        timeout_s=timeout_s,
        cap=cap,
        adapter_name=adapter_name,
    )


def _resolve_agents_dir(repo_root: Path) -> Path:
    """Resolve agents directory: package-relative first, then symlink in cwd."""
    try:
        pkg_agents = _tooling_root() / "factory" / "agents"
        if pkg_agents.is_dir():
            return pkg_agents
    except RuntimeError:
        pass
    cwd_agents = repo_root / "factory" / "agents"
    if cwd_agents.is_dir():
        return cwd_agents
    raise ValueError(
        "Cannot find agents directory.\n"
        "Run 'orchestrate init' to set up the project, or check your agent_factory installation."
    )


def _build_adapter(
    name: str, model: str | None, interactive: bool = False
) -> CopilotAdapter:
    if name != "copilot":
        raise ValueError(f"unsupported adapter: {name}")
    return CopilotAdapter(model=model, interactive=interactive)


_ALL_SKILLS_SENTINEL = "all skills"


def _validate_skill(agent_info: AgentInfo, skill: str | None) -> str | None:
    """Validate `--skill` against the agent's declared skills (BR-050, VR-038).

    Returns the normalized skill name for a skill-scoped run, or ``None`` for
    the full-workflow sentinel (omitted `--skill`, or the literal
    ``"all skills"`` — BR-052, unconditional regardless of the agent's
    declared skills).

    Raises ``ValueError`` — listing the agent's actually declared skills —
    when *skill* is neither the sentinel nor one of ``agent_info.skills``.
    Callers must invoke this before launching any adapter subprocess
    (FR-S2).
    """
    if skill is None or skill == _ALL_SKILLS_SENTINEL:
        return None

    if skill in agent_info.skills:
        return skill

    declared = ", ".join(agent_info.skills) if agent_info.skills else "(none declared)"
    raise ValueError(
        f"unknown skill '{skill}' for agent '{agent_info.name}'; "
        f"declared skills: {declared}"
    )


def _handle_run_step(
    runtime: _Runtime, agent_name: str, timeout_s: int, skill: str | None = None
) -> int:
    agent_info = _load_step_agent(runtime.agents_dir, agent_name)
    # FR-S2/VR-038: validate before composing a prompt or touching the
    # adapter — no subprocess may start for an undeclared skill.
    scoped_skill = _validate_skill(agent_info, skill)

    standalone_ctx = InvocationContext(
        phase="standalone", role=AgentRole.AUTHOR, iteration=0
    )
    prompt = runtime.prompt_composer.compose(
        agent_info,
        [runtime.repo_root / "CONTEXT.md"],
        standalone_ctx,
        skill=scoped_skill,
    )

    # Interactive mode: write CTA into instruction file so copilot reads it on
    # session start (no -p flag → agent enters live chat).
    if runtime.adapter.interactive:
        cta = (
            skill_scoped_call_to_action(scoped_skill)
            if scoped_skill
            else "Execute the workflow defined in your Agent Definition above."
        )
        _update_instruction_file(
            runtime.repo_root, agent_name, agent_info.skills, call_to_action=cta
        )

    clock = _SystemClock()
    start_ms = clock.now_ms()
    result = runtime.adapter.invoke(prompt, runtime.repo_root, timeout_s)
    end_ms = clock.now_ms()

    invocation = AgentInvocation(
        agent=agent_name,
        role=AgentRole.AUTHOR,
        adapter="cli",
        model=None,
        exit_code=result.exit_code,
        duration_ms=end_ms - start_ms,
        timed_out=result.timed_out,
        auth_error=result.auth_error,
        config_error=result.config_error,
    )
    runtime.logger.log(invocation, None)

    # Working-tree gate (ADR-0013): agents commit, orchestrator verifies
    gate = WorkingTreeGate(runtime.repo_root)
    gate_result = gate.verify(runtime.repo_root, result.exit_code)

    if gate_result.passed:
        for output_path in agent_info.outputs:
            print(output_path)
        return 0

    if gate_result.hook == "confabulation":
        print(
            "confabulation: agent exited 0 but left uncommitted changes",
            file=sys.stderr,
        )
        if gate_result.output:
            print(gate_result.output, file=sys.stderr)
        return 2  # VR-025

    # Agent failure
    output = result.stderr or result.stdout or f"agent failed: {agent_name}"
    print(output, file=sys.stderr)
    return 1


def _exit_code_for_mode(mode: RunMode) -> int:
    """FAGAN-0047: derive the process exit code from a run's terminal mode.

    HALTED means the run needs human intervention and must be reported as
    a failure (exit 2) so CI/shell callers don't treat it as success.
    Every other terminal/paused mode (RUNNING, PAUSED-awaiting-approval,
    COMPLETE) is an expected-good state and exits 0.
    """
    return 2 if mode == RunMode.HALTED else 0


def _handle_run_phase(runtime: _Runtime, run: Run, args) -> int:
    _ensure_run_branch(runtime.repo_root, run.branch)
    run.mode = RunMode.RUNNING
    phase_record = _phase_record(run, args.phase)
    runtime.phase_runner.run_phase(run, phase_record)
    # FAGAN-0047 hole 1: run_phase() early-returns as a no-op when
    # phase_record.status is already terminal (AWAITING_APPROVAL/HALTED/
    # COMPLETE) — e.g. re-invoking run-phase on a phase that's already
    # HALTED — without touching run.mode or saving. The RUNNING value
    # assigned above would then be stale. run_store is the only
    # authoritative source of the run's persisted mode; always derive the
    # exit code from a fresh reload rather than the in-memory `run`.
    persisted = runtime.run_store.load()
    return _exit_code_for_mode(persisted.mode if persisted is not None else run.mode)


def _handle_resume(runtime: _Runtime, run: Run, args) -> int:
    _ensure_run_branch(runtime.repo_root, run.branch)
    # Warn if tooling version changed since the run was created
    current_ver = _tooling_version()
    if run.tooling_version and current_ver and run.tooling_version != current_ver:
        print(
            f"warning: tooling version changed since run started "
            f"({run.tooling_version} → {current_ver})",
            file=sys.stderr,
        )
    # With run-all deferred (NG6), resume continues the current phase only;
    # the Operator advances to the next phase manually after approval (UC-03).
    run.mode = RunMode.RUNNING
    phase_record = _current_phase(run)
    runtime.phase_runner.run_phase(run, phase_record)
    # A no-op run_phase (terminal status) leaves the persisted mode as the
    # source of truth; always derive the exit code from a fresh reload.
    persisted = runtime.run_store.load()
    return _exit_code_for_mode(persisted.mode if persisted is not None else run.mode)


def _handle_approval(
    runtime: _Runtime, *, approve: bool, note: str | None = None
) -> int:
    if approve:
        runtime.approval_service.approve()
    else:
        runtime.approval_service.reject(note=note)
    return 0


def _with_lock(lock: RunLock, run_id: str, action) -> int:
    lock.acquire(run_id)
    try:
        return action()
    finally:
        lock.release()


def _load_or_create_phase_run(
    run_store: RunStateStore,
    agent_registry: MarkdownAgentRegistry,
    phase: str,
) -> Run:
    run = run_store.load()
    if run is None:
        run = _new_run([phase], agent_registry, current_phase=phase)
    elif run.mode == RunMode.RUNNING:
        # VR-017: refuse to start while a run is running
        raise ValueError(
            "a run is already in progress (mode=running); "
            "use 'resume' to continue or wait for it to finish"
        )

    if phase not in run.chain:
        run.chain.append(phase)

    phase_record = _existing_phase_record(run, phase)
    if phase_record is None:
        run.phases.append(_new_phase_record(agent_registry, phase))
        phase_record = run.phases[-1]

    run.current_phase = phase
    run.iteration = phase_record.iteration
    return run


def _new_run(
    chain: list[str],
    agent_registry: MarkdownAgentRegistry,
    *,
    current_phase: str,
) -> Run:
    run_id = f"RUN-{uuid4().hex[:8].upper()}"
    return Run(
        run_id=run_id,
        branch=f"orchestrator/{run_id.lower()}",
        chain=list(chain),
        current_phase=current_phase,
        mode=RunMode.RUNNING,
        phases=[_new_phase_record(agent_registry, phase) for phase in chain],
        tooling_version=_tooling_version(),
    )


def _new_phase_record(agent_registry: MarkdownAgentRegistry, phase: str) -> PhaseRecord:
    author = agent_registry.resolve(phase, "author").name
    try:
        reviewer = agent_registry.resolve(phase, "reviewer").name
    except ValueError as exc:
        # Only suppress for phases that legitimately have no reviewer
        # (e.g. planning). Missing agent definitions must fail-fast (VR-011).
        if "Unknown role" in str(exc):
            reviewer = None
        else:
            raise
    return PhaseRecord(name=phase, author=author, reviewer=reviewer)


def _phase_record(run: Run, phase: str) -> PhaseRecord:
    record = _existing_phase_record(run, phase)
    if record is None:
        raise ValueError(f"unknown phase: {phase}")
    return record


def _existing_phase_record(run: Run, phase: str) -> PhaseRecord | None:
    for record in run.phases:
        if record.name == phase:
            return record
    return None


def _current_phase(run: Run) -> PhaseRecord:
    record = _existing_phase_record(run, run.current_phase)
    if record is None:
        raise ValueError(f"unknown current phase: {run.current_phase}")
    return record


def _load_step_agent(agents_dir: Path, agent_name: str) -> AgentInfo:
    from orchestrator.adapters.agent_registry import _parse_skills

    definition_path = agents_dir / f"{agent_name}.md"
    if not definition_path.is_file():
        raise ValueError(f"unknown agent: {agent_name}")
    return AgentInfo(
        name=agent_name,
        outputs=_parse_outputs(definition_path),
        definition_path=definition_path,
        skills=_parse_skills(definition_path),
    )


def _parse_outputs(definition_path: Path) -> list[str]:
    lines = definition_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return []

    outputs: list[str] = []
    in_frontmatter = True
    collecting = False
    for line in lines[1:]:
        stripped = line.strip()
        if in_frontmatter and stripped == "---":
            break
        if stripped == "outputs:":
            collecting = True
            continue
        if collecting and line.startswith("  - "):
            outputs.append(line[4:].strip())
            continue
        if collecting and stripped:
            break
    return outputs


def main_entry() -> None:
    """Console script entry point for `orchestrate`."""
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
