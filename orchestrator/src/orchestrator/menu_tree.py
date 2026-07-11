"""Menu tree builder and declarative construction of the navigation model (ST-0036).

Constructs the root menu tree from cli_specification.md v1.2.0.
The tree is pure data — no node embeds a service call or terminal logic.
"""

from __future__ import annotations

from orchestrator.entities import MenuNode, MenuNodeType


def _build_status_menu() -> MenuNode:
    """Build the `status` submenu: four read-only display leaves (ST-0055, FR-T1).

    Order and labels match `cli_specification.md` §Status exactly. No child
    is marked `is_default` — the spec declares no ★ at this menu depth.
    """
    return MenuNode(
        id="status",
        label="status",
        type=MenuNodeType.MENU,
        children=[
            MenuNode(id="status.overview", label="overview", type=MenuNodeType.DISPLAY),
            MenuNode(
                id="status.phase-details",
                label="phase details",
                type=MenuNodeType.DISPLAY,
            ),
            MenuNode(id="status.findings", label="findings", type=MenuNodeType.DISPLAY),
            MenuNode(id="status.log", label="log", type=MenuNodeType.DISPLAY),
        ],
    )


def _build_backlog_menu() -> MenuNode:
    """Build the `backlog` submenu (ST-0057, FR-U1, cli_specification.md §Backlog).

    `list`, `by-epic`, `ready` are ordinary read-only display leaves — same
    shape as the `status` leaves (ST-0055). `view story` is a `menu` node
    whose children are one display leaf per story (`{story}` in the spec);
    that population is runtime backlog data, not something this pure tree
    builder can know, so it is left with no static children here. The
    populated node is built by `cli.py:build_backlog_view_story_menu`, kept
    out of this module so `MenuNode` construction never embeds a store call
    (module docstring: "no node embeds a service call or terminal logic").
    """
    return MenuNode(
        id="backlog",
        label="backlog",
        type=MenuNodeType.MENU,
        children=[
            MenuNode(id="backlog.list", label="list", type=MenuNodeType.DISPLAY),
            MenuNode(id="backlog.by-epic", label="by-epic", type=MenuNodeType.DISPLAY),
            MenuNode(id="backlog.ready", label="ready", type=MenuNodeType.DISPLAY),
            MenuNode(
                id="backlog.view-story", label="view story", type=MenuNodeType.MENU
            ),
        ],
    )


def _build_configure_defaults_menu() -> MenuNode:
    """Build the `configure > defaults` submenu: four setting leaves (ST-0044,
    UC-09, FR-Q4, cli_specification.md §Configure).

    `adapter` is a `menu` node — like `backlog.view-story`, its real children
    (one per registered adapter, current default marked ★) are runtime data
    this pure tree builder cannot know, so it is left with no static
    children here. The populated node is built by
    `cli.py:build_configure_defaults_adapter_menu`. `timeout`, `cap`, and
    `auto-approve` are direct function leaves per the spec: each prompts (or
    toggles) and persists through `ConfigStore`, needing no further
    menu-level selection. No child is marked `is_default` — the spec's
    "(current: ...)" annotations at this depth are display text, not ★
    markers (that marker is reserved for the `adapter` submenu's own
    children, cli_specification.md line 107).
    """
    return MenuNode(
        id="configure.defaults",
        label="defaults",
        type=MenuNodeType.MENU,
        children=[
            MenuNode(
                id="configure.defaults.adapter", label="adapter", type=MenuNodeType.MENU
            ),
            MenuNode(
                id="configure.defaults.timeout",
                label="timeout",
                type=MenuNodeType.FUNCTION,
            ),
            MenuNode(
                id="configure.defaults.cap", label="cap", type=MenuNodeType.FUNCTION
            ),
            MenuNode(
                id="configure.defaults.auto-approve",
                label="auto-approve",
                type=MenuNodeType.FUNCTION,
            ),
        ],
    )


def _build_configure_cli_list_menu() -> MenuNode:
    """Build the `configure > cli-list` submenu: the adapter-registry
    actions (ST-0047, UC-10 Main Success Scenario steps 1-8, 23-24,
    cli_specification.md lines 121-136).

    `auto-detect` and `add adapter` are direct function leaves — each
    scans/prompts and persists through `AdapterRegistry` with no further
    menu-level selection needed. `remove adapter` is a `menu` node — like
    `backlog.view-story` and `configure.defaults.adapter`, its real
    children (one per registered adapter) are runtime data this pure tree
    builder cannot know, so it is left with no static children here; the
    populated node is built by `cli.py:build_cli_list_remove_adapter_menu`.
    No child is marked `is_default` — cli_specification.md declares no ★ at
    this menu depth (unlike `configure.defaults.adapter`'s own children).
    """
    return MenuNode(
        id="configure.cli-list",
        label="cli-list",
        type=MenuNodeType.MENU,
        children=[
            MenuNode(
                id="configure.cli-list.auto-detect",
                label="auto-detect",
                type=MenuNodeType.FUNCTION,
            ),
            MenuNode(
                id="configure.cli-list.add-adapter",
                label="add adapter",
                type=MenuNodeType.FUNCTION,
            ),
            MenuNode(
                id="configure.cli-list.remove-adapter",
                label="remove adapter",
                type=MenuNodeType.MENU,
            ),
        ],
    )


def _build_configure_cli_menu() -> MenuNode:
    """Build the (unpopulated) `configure > cli` submenu (ST-0048, UC-10
    Main Success Scenario steps 9-22, cli_specification.md lines 138-164).

    `cli` is a `menu` node whose real children — one per registered
    adapter, each in turn a menu of `list models` / `auto-detect` /
    `add model` / `remove model` — are runtime data this pure tree
    builder cannot know, exactly like `configure.defaults.adapter` and
    `configure.cli-list.remove-adapter` before it. The populated node is
    built by `cli.py:build_configure_cli_menu`.
    """
    return MenuNode(id="configure.cli", label="cli", type=MenuNodeType.MENU)


def _build_configure_model_matrix_menu() -> MenuNode:
    """Build the `configure > model-matrix` submenu: `show`, `edit`,
    `validate` (ST-0050, UC-10, FR-R9, FR-K5, cli_specification.md lines
    166-179).

    All three children are static and known ahead of time — unlike
    `configure.defaults.adapter`, `configure.cli-list.remove-adapter`, and
    `configure.cli`, this submenu needs no runtime-populated children, so it
    (unlike those three) is fully built here with no composition-root merge
    step. `show` is a `display` leaf (read-only projection of `model.conf`'s
    `[facts]`); `edit` opens `model.conf` in `$EDITOR` and then repopulates
    every registered adapter's model dictionary from the edited facts
    (ADR-0017 point 5 as revised by ADR-0021); `validate` reruns the
    existing `scripts/matrix-lint` gate rather than reimplementing its
    checks (FR-K5). All three dispatch handlers live in
    `cli.py:build_configure_model_matrix_dispatch`.
    """
    return MenuNode(
        id="configure.model-matrix",
        label="model-matrix",
        type=MenuNodeType.MENU,
        children=[
            MenuNode(
                id="configure.model-matrix.show",
                label="show",
                type=MenuNodeType.DISPLAY,
            ),
            MenuNode(
                id="configure.model-matrix.edit",
                label="edit",
                type=MenuNodeType.FUNCTION,
            ),
            MenuNode(
                id="configure.model-matrix.validate",
                label="validate",
                type=MenuNodeType.FUNCTION,
            ),
        ],
    )


def _build_configure_menu() -> MenuNode:
    """Build the `configure` submenu (ST-0044, ST-0047, ST-0048, ST-0050).

    `defaults` (ST-0044), `cli-list` (ST-0047), `cli` (ST-0048), and
    `model-matrix` (ST-0050) are all populated here.
    """
    return MenuNode(
        id="configure",
        label="configure",
        type=MenuNodeType.MENU,
        children=[
            _build_configure_defaults_menu(),
            _build_configure_cli_list_menu(),
            _build_configure_cli_menu(),
            _build_configure_model_matrix_menu(),
        ],
    )


def _build_manage_run_menu() -> MenuNode:
    """Build the `manage-run` submenu: five function leaves (ST-0040, FR-V3,
    cli_specification.md §Manage run).

    Order and labels match the spec exactly. Every leaf maps 1:1 onto an
    existing direct-mode command (`resume`, `approve`, `reject`, `release`,
    `abort`) that needs no further menu-level selection, so — unlike
    `run-step`/`run-phase`, which need an adapter/agent picker that doesn't
    exist yet — these five are safe to wire as direct function leaves now
    (see ST-0040's Analysis). No child is marked `is_default` — the spec
    declares no ★ at this menu depth.
    """
    return MenuNode(
        id="manage-run",
        label="manage-run",
        type=MenuNodeType.MENU,
        children=[
            MenuNode(
                id="manage-run.resume", label="resume", type=MenuNodeType.FUNCTION
            ),
            MenuNode(
                id="manage-run.approve", label="approve", type=MenuNodeType.FUNCTION
            ),
            MenuNode(
                id="manage-run.reject", label="reject", type=MenuNodeType.FUNCTION
            ),
            MenuNode(
                id="manage-run.release", label="release", type=MenuNodeType.FUNCTION
            ),
            MenuNode(id="manage-run.abort", label="abort", type=MenuNodeType.FUNCTION),
        ],
    )


def build_root_menu() -> MenuNode:
    """Build the root menu tree from the spec.

    Returns the root MenuNode with seven children in spec order:
    init, configure, run-step, run-phase, status, manage-run, backlog.

    All children are menu-type nodes. `status` has four display-node
    children (ST-0055); `backlog` has three display-node children plus a
    `view story` menu-node child with no static children of its own
    (ST-0057, see `_build_backlog_menu`); `manage-run` has five function-node
    children (ST-0040, see `_build_manage_run_menu`); `configure` has four
    populated children, `defaults` (ST-0044), `cli-list` (ST-0047), `cli`
    (ST-0048), and `model-matrix` (ST-0050, see `_build_configure_menu`).
    `init`, `run-step`, and `run-phase` have no children of their own yet —
    their real children need either dynamic runtime data (agents, adapters)
    or a not-yet-built adapter-picker, and are populated by later stories
    (ST-0053; see ST-0040's Analysis for why `run-phase` isn't populated
    here despite having a real direct-mode handler already). No root-level
    child has is_default marked (per spec, no ★ at root depth).

    Raises:
        ValueError: if the tree has structural violations (e.g., multiple
            defaults per menu).
    """
    children = [
        MenuNode(id="init", label="init", type=MenuNodeType.MENU),
        _build_configure_menu(),
        MenuNode(id="run-step", label="run-step", type=MenuNodeType.MENU),
        MenuNode(id="run-phase", label="run-phase", type=MenuNodeType.MENU),
        _build_status_menu(),
        _build_manage_run_menu(),
        _build_backlog_menu(),
    ]

    # Validation happens in MenuNode.__post_init__ via _validate_defaults
    root = MenuNode(
        id="orchestrate",
        label="orchestrate",
        type=MenuNodeType.MENU,
        children=children,
    )

    return root
