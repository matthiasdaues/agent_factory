"""Tests for MenuController traversal and the TUI navigation state machine.

Traces: UC-08, ADR-0016, FR-P3, FR-P4, FR-P6, BR-032, BR-033, BR-034,
state-machines.md §"TUI Menu Navigation State Machine" (ST-0039).
"""

from __future__ import annotations

from orchestrator.entities import MenuNode, MenuNodeType
from orchestrator.menu_controller import (
    ControllerState,
    DispatchOutcome,
    MenuController,
)
from orchestrator.ports import KeyEvent, MenuItem


# --- Test fixtures: a small, hand-built tree exercising every node type ------
#
# root (menu)
#   ├─ alpha (menu, ★)
#   │    ├─ alpha-one (function)
#   │    └─ alpha-two (menu)
#   │         └─ alpha-two-deep (display)
#   ├─ beta (display)
#   └─ gamma (function)


def _build_tree() -> MenuNode:
    alpha_two_deep = MenuNode(
        id="root.alpha.alpha-two.deep",
        label="alpha-two-deep",
        type=MenuNodeType.DISPLAY,
    )
    alpha_two = MenuNode(
        id="root.alpha.alpha-two",
        label="alpha-two",
        type=MenuNodeType.MENU,
        children=[alpha_two_deep],
    )
    alpha_one = MenuNode(
        id="root.alpha.alpha-one", label="alpha-one", type=MenuNodeType.FUNCTION
    )
    alpha = MenuNode(
        id="root.alpha",
        label="alpha",
        type=MenuNodeType.MENU,
        is_default=True,
        children=[alpha_one, alpha_two],
    )
    beta = MenuNode(id="root.beta", label="beta", type=MenuNodeType.DISPLAY)
    gamma = MenuNode(id="root.gamma", label="gamma", type=MenuNodeType.FUNCTION)
    return MenuNode(
        id="root", label="root", type=MenuNodeType.MENU, children=[alpha, beta, gamma]
    )


class FakeRenderer:
    """Scripted MenuRenderer double — no terminal library involved."""

    def __init__(self, keys: list[KeyEvent]) -> None:
        self._keys = list(keys)
        self.rendered_menus: list[tuple[list[MenuItem], int]] = []
        self.rendered_displays: list[str] = []

    def render_menu(self, items: list[MenuItem], selected_index: int) -> None:
        self.rendered_menus.append((list(items), selected_index))

    def render_display(self, content: str) -> None:
        self.rendered_displays.append(content)

    def get_keypress(self) -> KeyEvent:
        return self._keys.pop(0)


class SpyDispatch:
    """Records every node it is called with; returns a scripted outcome."""

    def __init__(self, outcome: DispatchOutcome | None = None) -> None:
        self.outcome = outcome or DispatchOutcome()
        self.calls: list[MenuNode] = []
        self.states_at_call: list[ControllerState] = []
        self._controller: MenuController | None = None

    def bind(self, controller: MenuController) -> None:
        self._controller = controller

    def __call__(self, node: MenuNode) -> DispatchOutcome:
        self.calls.append(node)
        if self._controller is not None:
            self.states_at_call.append(self._controller.state)
        return self.outcome


# --- BR-032: opening selection -----------------------------------------------


class TestOpeningSelection:
    def test_opens_on_the_star_default_child(self) -> None:
        root = _build_tree()
        controller = MenuController(root, FakeRenderer([]), dispatch=SpyDispatch())
        # "alpha" is is_default=True and is index 0 in this fixture; use a
        # tree where the default is NOT first to prove it's not accidental.
        reordered = MenuNode(
            id="root2",
            label="root2",
            type=MenuNodeType.MENU,
            children=[
                MenuNode(id="a", label="a", type=MenuNodeType.FUNCTION),
                MenuNode(
                    id="b", label="b", type=MenuNodeType.FUNCTION, is_default=True
                ),
                MenuNode(id="c", label="c", type=MenuNodeType.FUNCTION),
            ],
        )
        controller2 = MenuController(
            reordered, FakeRenderer([]), dispatch=SpyDispatch()
        )
        assert controller2.selected_index == 1
        assert controller.selected_index == 0  # "alpha" — first child, also ★

    def test_opens_on_first_child_when_no_default_marked(self) -> None:
        no_default = MenuNode(
            id="root3",
            label="root3",
            type=MenuNodeType.MENU,
            children=[
                MenuNode(id="a", label="a", type=MenuNodeType.FUNCTION),
                MenuNode(id="b", label="b", type=MenuNodeType.FUNCTION),
            ],
        )
        controller = MenuController(
            no_default, FakeRenderer([]), dispatch=SpyDispatch()
        )
        assert controller.selected_index == 0

    def test_opening_selection_is_recomputed_on_reentry(self) -> None:
        # BR-032 defines "opening" selection; a stale cursor is not carried
        # back to a submenu the operator already left and re-entered.
        root = _build_tree()
        renderer = FakeRenderer(
            [
                KeyEvent.ENTER,  # root -> alpha (opening index 0: alpha-one)
                KeyEvent.DOWN,  # move to alpha-two (index 1)
                KeyEvent.BACK,  # pop back to root
                KeyEvent.ENTER,  # re-enter alpha
            ]
        )
        controller = MenuController(root, renderer, dispatch=SpyDispatch())
        controller.step()
        controller.step()
        assert controller.selected_index == 1  # moved off the opening index
        controller.step()  # BACK: real pop (alpha's parent is root)
        assert controller.state == ControllerState.ROOT_MENU
        controller.step()  # re-enter alpha
        assert controller.current_node.label == "alpha"
        assert (
            controller.selected_index == 0
        )  # recomputed opening index, not the stale 1


# --- FR-P3 / BR-033: arrow keys move selection, invoke nothing --------------


class TestArrowKeys:
    def test_down_moves_and_wraps(self) -> None:
        root = _build_tree()
        controller = MenuController(root, FakeRenderer([]), dispatch=SpyDispatch())
        assert controller.selected_index == 0
        controller._move_selection(1)
        assert controller.selected_index == 1
        controller._move_selection(1)
        assert controller.selected_index == 2
        controller._move_selection(1)
        assert controller.selected_index == 0  # wraps

    def test_up_moves_and_wraps_backward(self) -> None:
        root = _build_tree()
        controller = MenuController(root, FakeRenderer([]), dispatch=SpyDispatch())
        controller._move_selection(-1)
        assert controller.selected_index == 2  # wraps to last

    def test_arrow_keys_do_not_change_state_or_dispatch(self) -> None:
        root = _build_tree()
        spy = SpyDispatch()
        renderer = FakeRenderer([KeyEvent.DOWN, KeyEvent.UP, KeyEvent.DOWN])
        controller = MenuController(root, renderer, dispatch=spy)
        spy.bind(controller)
        for _ in range(3):
            controller.step()
        assert controller.state == ControllerState.ROOT_MENU
        assert spy.calls == []


# --- FR-P4: Enter on menu opens child; Enter on leaf dispatches -------------


class TestSelectChildMenu:
    def test_root_to_sub_menu_on_menu_child(self) -> None:
        root = _build_tree()
        renderer = FakeRenderer(
            [KeyEvent.ENTER]
        )  # Enter on "alpha" (opening ★ default)
        controller = MenuController(root, renderer, dispatch=SpyDispatch())
        controller.step()
        assert controller.state == ControllerState.SUB_MENU
        assert controller.current_node.label == "alpha"
        assert controller.selected_index == 0  # opening index of "alpha"'s children

    def test_sub_menu_to_sub_menu_on_nested_menu_child(self) -> None:
        root = _build_tree()
        renderer = FakeRenderer([KeyEvent.ENTER, KeyEvent.DOWN, KeyEvent.ENTER])
        controller = MenuController(root, renderer, dispatch=SpyDispatch())
        controller.step()  # -> alpha (SUB_MENU)
        controller.step()  # DOWN -> alpha-two selected
        controller.step()  # ENTER on alpha-two (menu) -> push again
        assert controller.state == ControllerState.SUB_MENU
        assert controller.current_node.label == "alpha-two"
        assert len(controller._stack) == 3


# --- FR-P8 / BR-034: display leaves ------------------------------------------


class TestDisplayLeaf:
    def test_select_display_from_root_renders_and_enters_display_state(self) -> None:
        root = _build_tree()
        spy = SpyDispatch(DispatchOutcome(content="hello from beta"))
        renderer = FakeRenderer(
            [KeyEvent.DOWN, KeyEvent.ENTER]
        )  # DOWN to "beta", ENTER
        controller = MenuController(root, renderer, dispatch=spy)
        controller.step()  # render root, DOWN -> beta selected
        controller.step()  # ENTER on beta (display)
        assert controller.state == ControllerState.DISPLAY
        assert spy.calls == [root.children[1]]  # beta
        assert renderer.rendered_displays == ["hello from beta"]

    def test_display_opened_from_root_returns_to_root_on_any_keypress(self) -> None:
        root = _build_tree()
        renderer = FakeRenderer(
            [KeyEvent.DOWN, KeyEvent.ENTER, KeyEvent.UP]
        )  # UP dismisses too
        controller = MenuController(root, renderer, dispatch=SpyDispatch())
        controller.step()
        controller.step()
        assert controller.state == ControllerState.DISPLAY
        controller.step()  # any keypress dismisses
        assert controller.state == ControllerState.ROOT_MENU

    def test_display_opened_from_sub_menu_returns_to_sub_menu(self) -> None:
        root = _build_tree()
        # alpha -> alpha-two -> alpha-two-deep (display)
        renderer = FakeRenderer(
            [
                KeyEvent.ENTER,
                KeyEvent.DOWN,
                KeyEvent.ENTER,
                KeyEvent.ENTER,
                KeyEvent.BACK,
            ]
        )
        controller = MenuController(root, renderer, dispatch=SpyDispatch())
        controller.step()  # -> alpha (SUB_MENU)
        controller.step()  # DOWN -> alpha-two selected
        controller.step()  # ENTER -> alpha-two (SUB_MENU, deeper)
        controller.step()  # ENTER on alpha-two-deep (display)
        assert controller.state == ControllerState.DISPLAY
        controller.step()  # BACK dismisses display (any keypress)
        assert controller.state == ControllerState.SUB_MENU
        assert controller.current_node.label == "alpha-two"

    def test_display_dispatch_is_not_called_again_on_dismiss(self) -> None:
        root = _build_tree()
        spy = SpyDispatch(DispatchOutcome(content="x"))
        renderer = FakeRenderer([KeyEvent.DOWN, KeyEvent.ENTER, KeyEvent.ENTER])
        controller = MenuController(root, renderer, dispatch=spy)
        controller.step()
        controller.step()
        controller.step()  # dismiss
        assert len(spy.calls) == 1


# --- EXECUTING guarded returns ------------------------------------------------


class TestFunctionLeaf:
    def test_short_running_function_from_root_returns_to_root(self) -> None:
        root = _build_tree()
        spy = SpyDispatch(DispatchOutcome(long_running=False))
        renderer = FakeRenderer(
            [KeyEvent.DOWN, KeyEvent.DOWN, KeyEvent.ENTER]
        )  # -> gamma
        controller = MenuController(root, renderer, dispatch=spy)
        spy.bind(controller)
        controller.step()
        controller.step()
        controller.step()
        assert controller.state == ControllerState.ROOT_MENU
        assert spy.calls == [root.children[2]]  # gamma
        assert spy.states_at_call == [ControllerState.EXECUTING]

    def test_long_running_function_from_root_exits(self) -> None:
        root = _build_tree()
        spy = SpyDispatch(DispatchOutcome(long_running=True))
        renderer = FakeRenderer([KeyEvent.DOWN, KeyEvent.DOWN, KeyEvent.ENTER])
        controller = MenuController(root, renderer, dispatch=spy)
        controller.step()
        controller.step()
        controller.step()
        assert controller.state == ControllerState.EXITED

    def test_short_running_function_from_sub_menu_returns_to_sub_menu(self) -> None:
        root = _build_tree()
        spy = SpyDispatch(DispatchOutcome(long_running=False))
        renderer = FakeRenderer(
            [KeyEvent.ENTER, KeyEvent.ENTER]
        )  # -> alpha -> alpha-one (function)
        controller = MenuController(root, renderer, dispatch=spy)
        controller.step()  # -> alpha (SUB_MENU)
        controller.step()  # ENTER on alpha-one (function)
        assert controller.state == ControllerState.SUB_MENU
        assert controller.current_node.label == "alpha"
        assert spy.calls == [root.children[0].children[0]]  # alpha-one

    def test_long_running_function_from_sub_menu_exits(self) -> None:
        root = _build_tree()
        spy = SpyDispatch(DispatchOutcome(long_running=True))
        renderer = FakeRenderer([KeyEvent.ENTER, KeyEvent.ENTER])
        controller = MenuController(root, renderer, dispatch=spy)
        controller.step()
        controller.step()
        assert controller.state == ControllerState.EXITED


# --- BR-034: Back / Exit ------------------------------------------------------


class TestBackAndExit:
    def test_back_at_root_is_a_no_op(self) -> None:
        root = _build_tree()
        renderer = FakeRenderer([KeyEvent.DOWN, KeyEvent.BACK])
        controller = MenuController(root, renderer, dispatch=SpyDispatch())
        controller.step()  # DOWN -> beta selected
        assert controller.selected_index == 1
        controller.step()  # BACK: no-op at root
        assert controller.state == ControllerState.ROOT_MENU
        assert controller.selected_index == 1  # unchanged — genuinely a no-op
        assert len(controller._stack) == 1

    def test_back_in_first_level_sub_menu_returns_to_root(self) -> None:
        root = _build_tree()
        renderer = FakeRenderer([KeyEvent.ENTER, KeyEvent.BACK])  # -> alpha, then back
        controller = MenuController(root, renderer, dispatch=SpyDispatch())
        controller.step()
        controller.step()
        assert controller.state == ControllerState.ROOT_MENU
        assert controller.current_node.label == "root"

    def test_back_in_deeper_sub_menu_pops_to_ancestor_sub_menu(self) -> None:
        root = _build_tree()
        renderer = FakeRenderer(
            [KeyEvent.ENTER, KeyEvent.DOWN, KeyEvent.ENTER, KeyEvent.BACK]
        )
        controller = MenuController(root, renderer, dispatch=SpyDispatch())
        controller.step()  # -> alpha
        controller.step()  # DOWN -> alpha-two
        controller.step()  # ENTER -> alpha-two (deeper SUB_MENU)
        controller.step()  # BACK -> pops to alpha, still SUB_MENU
        assert controller.state == ControllerState.SUB_MENU
        assert controller.current_node.label == "alpha"

    def test_exit_from_root_goes_straight_to_exited(self) -> None:
        root = _build_tree()
        spy = SpyDispatch()
        renderer = FakeRenderer([KeyEvent.EXIT])
        controller = MenuController(root, renderer, dispatch=spy)
        controller.step()
        assert controller.state == ControllerState.EXITED
        assert spy.calls == []

    def test_exit_from_sub_menu_goes_straight_to_exited_without_dispatch(self) -> None:
        root = _build_tree()
        spy = SpyDispatch()
        renderer = FakeRenderer([KeyEvent.ENTER, KeyEvent.EXIT])
        controller = MenuController(root, renderer, dispatch=spy)
        controller.step()
        controller.step()
        assert controller.state == ControllerState.EXITED
        assert spy.calls == []


# --- BR-033: purity across a full scripted run -------------------------------


class TestPurityAndRunLoop:
    def test_pure_navigation_never_dispatches(self) -> None:
        root = _build_tree()
        spy = SpyDispatch()
        renderer = FakeRenderer(
            [
                KeyEvent.DOWN,
                KeyEvent.UP,
                KeyEvent.ENTER,  # into alpha
                KeyEvent.DOWN,
                KeyEvent.BACK,  # back to root
                KeyEvent.EXIT,
            ]
        )
        controller = MenuController(root, renderer, dispatch=spy)
        controller.run()
        assert controller.state == ControllerState.EXITED
        assert spy.calls == []

    def test_run_walks_root_to_function_leaf_and_exits_on_long_running(self) -> None:
        root = _build_tree()
        spy = SpyDispatch(DispatchOutcome(long_running=True))
        renderer = FakeRenderer(
            [KeyEvent.ENTER, KeyEvent.ENTER]
        )  # alpha -> alpha-one (function)
        controller = MenuController(root, renderer, dispatch=spy)
        controller.run()
        assert controller.state == ControllerState.EXITED
        assert spy.calls == [root.children[0].children[0]]

    def test_render_menu_called_with_mapped_menu_items(self) -> None:
        root = _build_tree()
        renderer = FakeRenderer([KeyEvent.EXIT])
        controller = MenuController(root, renderer, dispatch=SpyDispatch())
        controller.step()
        items, selected_index = renderer.rendered_menus[0]
        assert [i.label for i in items] == ["alpha", "beta", "gamma"]
        assert [i.is_default for i in items] == [True, False, False]
        assert selected_index == 0
