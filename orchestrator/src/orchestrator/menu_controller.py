"""MenuController — traversal and navigation state machine for the TUI (ST-0039).

Implements the TUI Menu Navigation State Machine from
`docs/spec/supplementary_specs/state-machines.md` verbatim:
`ROOT_MENU -> SUB_MENU -> DISPLAY -> EXECUTING -> EXITED`. The controller
depends only on `MenuNode` (ST-0036) and the `MenuRenderer` port (ST-0037) —
no terminal library, no application service — so it is exercised entirely
against a fake renderer and a stub dispatch hook (ADR-0016, UC-08).

Every method here is pure with respect to anything outside the renderer and
the controller's own in-memory stack: cursor movement, menu entry, back
navigation, and display viewing never call `dispatch` (BR-033). Only a
`SelectChild` on a `display` or `function` leaf calls the injected
`dispatch` hook — the seam later stories (ST-0040, ST-0044, ST-0047/48,
ST-0050, ST-0053, ST-0055, ST-0057) wire real application services into.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional

from .entities import MenuNode, MenuNodeType
from .ports import KeyEvent, MenuItem, MenuRenderer


class ControllerState(str, Enum):
    """Mirrors the five states of the TUI navigation state machine exactly."""

    ROOT_MENU = "root_menu"
    SUB_MENU = "sub_menu"
    DISPLAY = "display"
    EXECUTING = "executing"
    EXITED = "exited"


@dataclass(frozen=True)
class DispatchOutcome:
    """Result of dispatching a `display` or `function` leaf.

    `long_running` gates the `EXECUTING` guard (FR-P7): `True` means the
    controller transitions to `EXITED` so the TUI can hand off to streaming
    terminal output; `False` means the operation completed within menu mode
    and the controller returns to the menu that opened it. Ignored for
    `display` leaves.

    `content` is the read-only text for a `display` leaf (FR-P8), rendered
    once via `MenuRenderer.render_display`. Ignored for `function` leaves.
    """

    long_running: bool = False
    content: str = ""


DispatchHook = Callable[[MenuNode], DispatchOutcome]


def _opening_index(node: MenuNode) -> int:
    """BR-032: the ★ child's index, or 0 (first item) when none is marked."""
    for index, child in enumerate(node.children):
        if child.is_default:
            return index
    return 0


class MenuController:
    """Walks a `MenuNode` tree and holds the TUI navigation state machine.

    Constructor:
        MenuController(root: MenuNode, renderer: MenuRenderer, dispatch: DispatchHook)

    `dispatch` has no default — the composition root must wire something
    (even a deliberate no-op) so that a function or display leaf is never
    silently inert (ADR-0016: menu mode must not become a second, divergent
    orchestration engine).
    """

    def __init__(
        self, root: MenuNode, renderer: MenuRenderer, dispatch: DispatchHook
    ) -> None:
        self._renderer = renderer
        self._dispatch = dispatch
        self._stack: List[MenuNode] = [root]
        self._selected_index: int = 0
        self.state: ControllerState = ControllerState.ROOT_MENU
        self._enter_current_menu()

    # --- Public, read-only view of navigation state -------------------------

    @property
    def current_node(self) -> MenuNode:
        """The menu currently on top of the stack (meaningful in any state)."""
        return self._stack[-1]

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @property
    def selected_child(self) -> Optional[MenuNode]:
        children = self.current_node.children
        if not children:
            return None
        return children[self._selected_index]

    # --- Run loop -------------------------------------------------------------

    def run(self) -> None:
        """Drive the state machine until `EXITED`, reading keys from the renderer."""
        while self.state != ControllerState.EXITED:
            self.step()

    def step(self) -> None:
        """Advance the state machine by exactly one renderer interaction."""
        if self.state in (ControllerState.ROOT_MENU, ControllerState.SUB_MENU):
            self._render_current_menu()
            key = self._renderer.get_keypress()
            self._handle_menu_key(key)
        elif self.state == ControllerState.DISPLAY:
            # Content was already rendered on entry (see _select_child).
            # BR-034: any keypress dismisses — no branching on the key.
            self._renderer.get_keypress()
            self._enter_current_menu()
        # EXECUTING never persists across a step() boundary: SelectChild on a
        # function leaf resolves it synchronously (see _select_child).
        # EXITED: run()'s loop condition stops before calling step() again.

    # --- ROOT_MENU / SUB_MENU: render + key handling ---------------------------

    def _render_current_menu(self) -> None:
        items = [
            MenuItem(label=child.label, is_default=child.is_default)
            for child in self.current_node.children
        ]
        self._renderer.render_menu(items, self._selected_index)

    def _handle_menu_key(self, key: KeyEvent) -> None:
        if key is KeyEvent.UP:
            self._move_selection(-1)
        elif key is KeyEvent.DOWN:
            self._move_selection(1)
        elif key is KeyEvent.ENTER:
            self._select_child()
        elif key is KeyEvent.BACK:
            self._back()
        elif key is KeyEvent.EXIT:
            self.state = ControllerState.EXITED

    def _move_selection(self, delta: int) -> None:
        # FR-P3 / BR-033: cursor movement only — no ChangeState, no dispatch.
        children = self.current_node.children
        if not children:
            return
        self._selected_index = (self._selected_index + delta) % len(children)

    def _select_child(self) -> None:
        child = self.selected_child
        if child is None:
            return
        if child.type == MenuNodeType.MENU:
            self._stack.append(child)
            self._enter_current_menu()
        elif child.type == MenuNodeType.DISPLAY:
            outcome = self._dispatch(child)
            self.state = ControllerState.DISPLAY
            self._renderer.render_display(outcome.content)
        elif child.type == MenuNodeType.FUNCTION:
            self.state = ControllerState.EXECUTING
            outcome = self._dispatch(child)
            self._complete_execution(outcome)

    def _back(self) -> None:
        if len(self._stack) == 1:
            return  # ROOT_MENU On Back: no-op
        self._stack.pop()
        self._enter_current_menu()

    # --- Shared transition target ---------------------------------------------

    def _enter_current_menu(self) -> None:
        """Land on ROOT_MENU or SUB_MENU per stack depth; recompute BR-032 selection.

        Used after construction, a menu push, a Back pop, a DISPLAY dismissal,
        and a short-running EXECUTING completion — every pseudocode edge whose
        target is "the menu that was already active" resolves through this
        one place, keyed off `len(self._stack)`.
        """
        self.state = (
            ControllerState.ROOT_MENU
            if len(self._stack) == 1
            else ControllerState.SUB_MENU
        )
        self._selected_index = _opening_index(self.current_node)

    def _complete_execution(self, outcome: DispatchOutcome) -> None:
        if outcome.long_running:
            self.state = ControllerState.EXITED
        else:
            self._enter_current_menu()
