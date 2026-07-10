"""Tests for the MenuNode entity and menu tree builder (ST-0036)."""

from __future__ import annotations

import pytest

from orchestrator.entities import MenuNode, MenuNodeType
from orchestrator.menu_tree import build_root_menu


class TestMenuNodeEntity:
    """MenuNode dataclass structure."""

    def test_menu_node_creation(self):
        """MenuNode is created with required fields."""
        node = MenuNode(
            id="test",
            label="Test Item",
            type=MenuNodeType.MENU,
            is_default=False,
            children=[],
        )
        assert node.id == "test"
        assert node.label == "Test Item"
        assert node.type == MenuNodeType.MENU
        assert node.is_default is False
        assert node.children == []

    def test_menu_node_with_defaults(self):
        """MenuNode uses default values for is_default and children."""
        node = MenuNode(id="test", label="Test", type=MenuNodeType.MENU)
        assert node.is_default is False
        assert node.children == []

    def test_menu_node_frozen(self):
        """MenuNode is immutable (frozen)."""
        node = MenuNode(id="test", label="Test", type=MenuNodeType.MENU)
        with pytest.raises(AttributeError):
            node.id = "changed"

    def test_menu_node_type_enum(self):
        """MenuNodeType has the three required values."""
        assert MenuNodeType.MENU.value == "menu"
        assert MenuNodeType.DISPLAY.value == "display"
        assert MenuNodeType.FUNCTION.value == "function"


class TestRootMenuTreeStructure:
    """Root menu tree shape and order."""

    def test_root_menu_exists(self):
        """build_root_menu returns a MenuNode."""
        root = build_root_menu()
        assert isinstance(root, MenuNode)

    def test_root_menu_properties(self):
        """Root menu has id='orchestrate', is a menu type."""
        root = build_root_menu()
        assert root.id == "orchestrate"
        assert root.label == "orchestrate"
        assert root.type == MenuNodeType.MENU

    def test_root_has_seven_children(self):
        """Root menu has exactly seven children."""
        root = build_root_menu()
        assert len(root.children) == 7

    def test_children_in_spec_order(self):
        """Children are in spec order: init, configure, run-step, etc."""
        root = build_root_menu()
        expected_ids = [
            "init",
            "configure",
            "run-step",
            "run-phase",
            "status",
            "manage-run",
            "backlog",
        ]
        actual_ids = [child.id for child in root.children]
        assert actual_ids == expected_ids

    def test_child_ids_match_labels(self):
        """Each child's id matches its label."""
        root = build_root_menu()
        for child in root.children:
            assert child.id == child.label

    def test_all_root_children_are_menus(self):
        """Each child at root level is a menu-type node."""
        root = build_root_menu()
        for child in root.children:
            assert child.type == MenuNodeType.MENU

    def test_all_children_have_no_default_set(self):
        """Root children have is_default=False (per spec, no ★ at root depth)."""
        root = build_root_menu()
        for child in root.children:
            assert child.is_default is False

    def test_unpopulated_children_have_empty_children_list(self):
        """Root children other than `status`, `backlog`, `manage-run`,
        `configure` have no children yet.

        `status` gained its four display-node children in ST-0055; `backlog`
        gained its four children (three display leaves, one `view story`
        menu) in ST-0057; `manage-run` gained its five function-node
        children in ST-0040; `configure` gained its `defaults` child in
        ST-0044. `init`, `run-step`, `run-phase` remain untouched until
        their own stories add children (ST-0047/48/50/53).
        """
        root = build_root_menu()
        for child in root.children:
            if child.id in ("status", "backlog", "manage-run", "configure"):
                continue
            assert child.children == []


class TestStatusMenuChildren:
    """`status` gains four read-only display children (ST-0055, FR-T1)."""

    def _status_node(self):
        root = build_root_menu()
        return next(child for child in root.children if child.id == "status")

    def test_status_has_four_children(self):
        status = self._status_node()
        assert len(status.children) == 4

    def test_status_children_are_display_leaves(self):
        status = self._status_node()
        for child in status.children:
            assert child.type == MenuNodeType.DISPLAY
            assert child.children == []

    def test_status_children_labels_in_spec_order(self):
        status = self._status_node()
        assert [child.label for child in status.children] == [
            "overview",
            "phase details",
            "findings",
            "log",
        ]

    def test_status_children_ids_in_spec_order(self):
        status = self._status_node()
        assert [child.id for child in status.children] == [
            "status.overview",
            "status.phase-details",
            "status.findings",
            "status.log",
        ]

    def test_status_children_have_no_default_marked(self):
        """cli_specification.md marks no ★ at this menu depth."""
        status = self._status_node()
        assert all(not child.is_default for child in status.children)


class TestManageRunMenuChildren:
    """`manage-run` gains five function children (ST-0040, FR-V3,
    cli_specification.md §Manage run)."""

    def _manage_run_node(self):
        root = build_root_menu()
        return next(child for child in root.children if child.id == "manage-run")

    def test_manage_run_has_five_children(self):
        manage_run = self._manage_run_node()
        assert len(manage_run.children) == 5

    def test_manage_run_children_are_function_leaves(self):
        manage_run = self._manage_run_node()
        for child in manage_run.children:
            assert child.type == MenuNodeType.FUNCTION
            assert child.children == []

    def test_manage_run_children_in_spec_order(self):
        manage_run = self._manage_run_node()
        assert [child.label for child in manage_run.children] == [
            "resume",
            "approve",
            "reject",
            "release",
            "abort",
        ]

    def test_manage_run_children_ids_in_spec_order(self):
        manage_run = self._manage_run_node()
        assert [child.id for child in manage_run.children] == [
            "manage-run.resume",
            "manage-run.approve",
            "manage-run.reject",
            "manage-run.release",
            "manage-run.abort",
        ]

    def test_manage_run_children_have_no_default_marked(self):
        """cli_specification.md marks no ★ at this menu depth."""
        manage_run = self._manage_run_node()
        assert all(not child.is_default for child in manage_run.children)


class TestConfigureDefaultsMenuChildren:
    """`configure` gains a populated `defaults` child (ST-0044, UC-09,
    FR-Q4, cli_specification.md §Configure)."""

    def _configure_node(self):
        root = build_root_menu()
        return next(child for child in root.children if child.id == "configure")

    def _defaults_node(self):
        configure = self._configure_node()
        return next(
            child for child in configure.children if child.id == "configure.defaults"
        )

    def test_configure_has_four_children(self):
        """`defaults` (ST-0044), `cli-list` (ST-0047), `cli` (ST-0048), and
        `model-matrix` (ST-0050) are all populated."""
        configure = self._configure_node()
        assert [child.id for child in configure.children] == [
            "configure.defaults",
            "configure.cli-list",
            "configure.cli",
            "configure.model-matrix",
        ]

    def test_defaults_has_four_children(self):
        defaults = self._defaults_node()
        assert len(defaults.children) == 4

    def test_defaults_children_in_spec_order(self):
        defaults = self._defaults_node()
        assert [child.label for child in defaults.children] == [
            "adapter",
            "timeout",
            "cap",
            "auto-approve",
        ]

    def test_defaults_children_ids_in_spec_order(self):
        defaults = self._defaults_node()
        assert [child.id for child in defaults.children] == [
            "configure.defaults.adapter",
            "configure.defaults.timeout",
            "configure.defaults.cap",
            "configure.defaults.auto-approve",
        ]

    def test_adapter_child_is_a_menu_with_no_static_children(self):
        """`adapter` needs runtime data (registered adapters) populated by
        `cli.py:build_configure_defaults_adapter_menu` — the pure tree
        builder cannot know it (mirrors `backlog.view-story`)."""
        defaults = self._defaults_node()
        adapter = next(
            c for c in defaults.children if c.id == "configure.defaults.adapter"
        )
        assert adapter.type == MenuNodeType.MENU
        assert adapter.children == []

    def test_timeout_cap_auto_approve_are_function_leaves(self):
        defaults = self._defaults_node()
        for leaf_id in (
            "configure.defaults.timeout",
            "configure.defaults.cap",
            "configure.defaults.auto-approve",
        ):
            leaf = next(c for c in defaults.children if c.id == leaf_id)
            assert leaf.type == MenuNodeType.FUNCTION
            assert leaf.children == []

    def test_defaults_children_have_no_default_marked(self):
        """cli_specification.md marks no ★ at this menu depth — ★ belongs to
        the `adapter` submenu's own (runtime-populated) children."""
        defaults = self._defaults_node()
        assert all(not child.is_default for child in defaults.children)


class TestConfigureCliListMenuChildren:
    """`configure` gains a populated `cli-list` child (ST-0047, UC-10,
    FR-R2, FR-R3, FR-R4, cli_specification.md §Configure lines 121-136)."""

    def _configure_node(self):
        root = build_root_menu()
        return next(child for child in root.children if child.id == "configure")

    def _cli_list_node(self):
        configure = self._configure_node()
        return next(
            child for child in configure.children if child.id == "configure.cli-list"
        )

    def test_cli_list_has_three_children_in_spec_order(self):
        cli_list = self._cli_list_node()
        assert [child.id for child in cli_list.children] == [
            "configure.cli-list.auto-detect",
            "configure.cli-list.add-adapter",
            "configure.cli-list.remove-adapter",
        ]
        assert [child.label for child in cli_list.children] == [
            "auto-detect",
            "add adapter",
            "remove adapter",
        ]

    def test_auto_detect_and_add_adapter_are_function_leaves(self):
        cli_list = self._cli_list_node()
        for leaf_id in (
            "configure.cli-list.auto-detect",
            "configure.cli-list.add-adapter",
        ):
            leaf = next(c for c in cli_list.children if c.id == leaf_id)
            assert leaf.type == MenuNodeType.FUNCTION
            assert leaf.children == []

    def test_remove_adapter_is_a_menu_with_no_static_children(self):
        """`remove adapter` needs runtime data (registered adapters)
        populated by `cli.py:build_cli_list_remove_adapter_menu` — the pure
        tree builder cannot know it (mirrors `backlog.view-story` and
        `configure.defaults.adapter`)."""
        cli_list = self._cli_list_node()
        remove_adapter = next(
            c for c in cli_list.children if c.id == "configure.cli-list.remove-adapter"
        )
        assert remove_adapter.type == MenuNodeType.MENU
        assert remove_adapter.children == []

    def test_cli_list_children_have_no_default_marked(self):
        cli_list = self._cli_list_node()
        assert all(not child.is_default for child in cli_list.children)


class TestConfigureCliMenuChildren:
    """`configure` gains a (statically unpopulated) `cli` child (ST-0048,
    UC-10 steps 9-22, cli_specification.md §Configure lines 138-164). Its
    real, runtime-populated children (one menu per registered adapter) are
    built by `cli.py:build_configure_cli_menu` — covered in
    tests/test_model_dictionary_menu.py, mirroring `backlog.view-story`,
    `configure.defaults.adapter`, and `configure.cli-list.remove-adapter`
    before it."""

    def _configure_node(self):
        root = build_root_menu()
        return next(child for child in root.children if child.id == "configure")

    def test_cli_is_a_menu_with_no_static_children(self):
        configure = self._configure_node()
        cli = next(child for child in configure.children if child.id == "configure.cli")
        assert cli.type == MenuNodeType.MENU
        assert cli.label == "cli"
        assert cli.children == []


class TestConfigureModelMatrixMenuChildren:
    """`configure` gains a fully-populated `model-matrix` child (ST-0050,
    UC-10, FR-R9, FR-K5, cli_specification.md lines 166-179). Unlike
    `defaults`/`cli-list`/`cli`, this submenu needs no runtime-populated
    children — all three leaves are static — so the pure tree builder owns
    it completely, no composition-root merge step needed."""

    def _configure_node(self):
        root = build_root_menu()
        return next(child for child in root.children if child.id == "configure")

    def _model_matrix_node(self):
        configure = self._configure_node()
        return next(
            child
            for child in configure.children
            if child.id == "configure.model-matrix"
        )

    def test_model_matrix_has_three_children_in_spec_order(self):
        model_matrix = self._model_matrix_node()
        assert [child.id for child in model_matrix.children] == [
            "configure.model-matrix.show",
            "configure.model-matrix.edit",
            "configure.model-matrix.validate",
        ]
        assert [child.label for child in model_matrix.children] == [
            "show",
            "edit",
            "validate",
        ]

    def test_show_is_a_display_leaf(self):
        model_matrix = self._model_matrix_node()
        show = next(
            c for c in model_matrix.children if c.id == "configure.model-matrix.show"
        )
        assert show.type == MenuNodeType.DISPLAY
        assert show.children == []

    def test_edit_and_validate_are_function_leaves(self):
        model_matrix = self._model_matrix_node()
        for leaf_id in (
            "configure.model-matrix.edit",
            "configure.model-matrix.validate",
        ):
            leaf = next(c for c in model_matrix.children if c.id == leaf_id)
            assert leaf.type == MenuNodeType.FUNCTION
            assert leaf.children == []

    def test_model_matrix_children_have_no_default_marked(self):
        model_matrix = self._model_matrix_node()
        assert all(not child.is_default for child in model_matrix.children)


class TestMenuDefaultValidation:
    """Validation: exactly one child per menu may have is_default=True."""

    def test_multiple_defaults_in_children_raises_error(self):
        """Building a menu with multiple default children raises ValueError."""
        child1 = MenuNode(id="a", label="A", type=MenuNodeType.MENU, is_default=True)
        child2 = MenuNode(id="b", label="B", type=MenuNodeType.MENU, is_default=True)
        child3 = MenuNode(id="c", label="C", type=MenuNodeType.MENU, is_default=False)

        with pytest.raises(ValueError, match="multiple default"):
            MenuNode(
                id="root",
                label="Root",
                type=MenuNodeType.MENU,
                children=[child1, child2, child3],
            )

    def test_zero_defaults_in_children_is_valid(self):
        """Menu with zero default children is valid."""
        child1 = MenuNode(id="a", label="A", type=MenuNodeType.MENU, is_default=False)
        child2 = MenuNode(id="b", label="B", type=MenuNodeType.MENU, is_default=False)

        node = MenuNode(
            id="root",
            label="Root",
            type=MenuNodeType.MENU,
            children=[child1, child2],
        )
        assert node.children == [child1, child2]

    def test_one_default_in_children_is_valid(self):
        """Menu with one default child is valid."""
        child1 = MenuNode(id="a", label="A", type=MenuNodeType.MENU, is_default=True)
        child2 = MenuNode(id="b", label="B", type=MenuNodeType.MENU, is_default=False)

        node = MenuNode(
            id="root",
            label="Root",
            type=MenuNodeType.MENU,
            children=[child1, child2],
        )
        assert node.children == [child1, child2]


class TestMenuTreePurity:
    """Tree is pure data — no embedded logic."""

    def test_menu_node_has_no_callable_attributes(self):
        """MenuNode dataclass has no methods (pure data)."""
        root = build_root_menu()
        # All public attributes should be data, not methods
        for attr in dir(root):
            if not attr.startswith("_"):
                assert not callable(getattr(root, attr))
