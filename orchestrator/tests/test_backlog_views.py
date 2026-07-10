"""Tests for the `backlog` menu submenu's four read-only display views.

Traces: UC-12, AG-12, FR-U1..U6, BR-056, BR-058, BR-059, BR-060,
cli_specification.md §Backlog (ST-0057). Covers the formatter functions,
`build_backlog_dispatch`'s dispatch-hook wiring for the three static display
leaves (`backlog.list`, `backlog.by-epic`, `backlog.ready`) and the dynamic
`backlog.view-story.{id}` leaves, `build_backlog_view_story_menu`'s per-story
submenu construction, the empty-backlog explicit-message rule (BR-058), and
the read-only guarantee (BR-056, FR-U6, VR-039).
"""

from __future__ import annotations

import pytest

from orchestrator.cli import (
    _format_backlog_by_epic,
    _format_backlog_list,
    _format_backlog_ready,
    _format_story_detail,
    build_backlog_dispatch,
    build_backlog_view_story_menu,
)
from orchestrator.entities import (
    Classification,
    MenuNode,
    MenuNodeType,
    Story,
    StoryStatus,
)
from orchestrator.menu_controller import DispatchOutcome
from orchestrator.menu_tree import build_root_menu


def _backlog_node(node_id: str) -> MenuNode:
    root = build_root_menu()
    backlog = next(child for child in root.children if child.id == "backlog")
    return next(child for child in backlog.children if child.id == node_id)


def _story(
    id="ST-0200",
    epic="Epic A",
    title="A story",
    classification=Classification.STANDARD,
    status=StoryStatus.PENDING,
    deps=None,
    traces=None,
    outputs=None,
    body="",
) -> Story:
    return Story(
        id=id,
        epic=epic,
        title=title,
        classification=classification,
        status=status,
        deps=deps or [],
        traces=traces or [],
        outputs=outputs or [],
        body=body,
    )


# --- Formatter unit tests (fixture data) -------------------------------------


class TestFormatBacklogList:
    def test_empty(self) -> None:
        text = _format_backlog_list([])
        assert "no stories" in text.lower()

    def test_populated(self) -> None:
        story = _story(deps=["ST-0100"])
        text = _format_backlog_list([story])
        assert "ST-0200" in text
        assert "A story" in text
        assert "Epic A" in text
        assert "standard" in text
        assert "pending" in text
        assert "ST-0100" in text


class TestFormatBacklogByEpic:
    def test_empty(self) -> None:
        text = _format_backlog_by_epic({})
        assert "no stories" in text.lower()

    def test_groups_under_epic_headings_with_status(self) -> None:
        grouped = {
            "Alpha": [_story(id="ST-0201", epic="Alpha", status=StoryStatus.DONE)],
            "Beta": [_story(id="ST-0202", epic="Beta", status=StoryStatus.PENDING)],
        }
        text = _format_backlog_by_epic(grouped)
        assert "Alpha" in text
        assert "Beta" in text
        assert "ST-0201" in text
        assert "done" in text
        assert "ST-0202" in text
        assert "pending" in text
        assert text.index("Alpha") < text.index("ST-0201")
        assert text.index("ST-0201") < text.index("Beta")


class TestFormatBacklogReady:
    def test_empty_shows_explicit_message(self) -> None:
        text = _format_backlog_ready([])
        assert text.strip() != ""
        assert "no" in text.lower()

    def test_populated(self) -> None:
        story = _story(id="ST-0203", status=StoryStatus.PENDING)
        text = _format_backlog_ready([story])
        assert "ST-0203" in text


class TestFormatStoryDetail:
    def test_renders_full_frontmatter_and_body(self) -> None:
        story = _story(
            id="ST-0204",
            deps=["ST-0100"],
            traces=["UC-12"],
            outputs=["src/x.py"],
            body="\n# Heading\n\nProse body text.\n",
        )
        text = _format_story_detail(story)
        assert "ST-0204" in text
        assert "Epic A" in text
        assert "A story" in text
        assert "standard" in text
        assert "pending" in text
        assert "ST-0100" in text
        assert "UC-12" in text
        assert "src/x.py" in text
        assert "Prose body text." in text


# --- Dispatch-hook wiring -----------------------------------------------------


class _StubBacklogStore:
    """Exposes only the four read methods ST-0056 defines — no `update_status`,
    so any attempt by the dispatch hook to mutate raises AttributeError rather
    than silently succeeding."""

    def __init__(self, stories, by_epic, ready) -> None:
        self._stories = stories
        self._by_epic = by_epic
        self._ready = ready

    def list_stories(self):
        return self._stories

    def stories_by_epic(self):
        return self._by_epic

    def ready_stories(self):
        return self._ready

    def get_story(self, story_id):
        for story in self._stories:
            if story.id == story_id:
                return story
        raise KeyError(story_id)


def _stub_store() -> _StubBacklogStore:
    story = _story(id="ST-0210", title="Stub story")
    return _StubBacklogStore(
        stories=[story], by_epic={"Epic A": [story]}, ready=[story]
    )


class TestBuildBacklogDispatch:
    def test_list_node_renders_list_stories(self) -> None:
        dispatch = build_backlog_dispatch(_stub_store())
        outcome = dispatch(_backlog_node("backlog.list"))
        assert isinstance(outcome, DispatchOutcome)
        assert outcome.long_running is False
        assert "ST-0210" in outcome.content

    def test_by_epic_node_renders_stories_by_epic(self) -> None:
        dispatch = build_backlog_dispatch(_stub_store())
        outcome = dispatch(_backlog_node("backlog.by-epic"))
        assert "Epic A" in outcome.content
        assert "ST-0210" in outcome.content

    def test_ready_node_renders_ready_stories(self) -> None:
        dispatch = build_backlog_dispatch(_stub_store())
        outcome = dispatch(_backlog_node("backlog.ready"))
        assert "ST-0210" in outcome.content

    def test_ready_node_empty_shows_explicit_empty_state(self) -> None:
        store = _StubBacklogStore(stories=[], by_epic={}, ready=[])
        dispatch = build_backlog_dispatch(store)
        outcome = dispatch(_backlog_node("backlog.ready"))
        assert outcome.content.strip() != ""
        assert "no" in outcome.content.lower()

    def test_list_node_empty_shows_explicit_empty_state(self) -> None:
        store = _StubBacklogStore(stories=[], by_epic={}, ready=[])
        dispatch = build_backlog_dispatch(store)
        outcome = dispatch(_backlog_node("backlog.list"))
        assert outcome.content.strip() != ""
        assert "no" in outcome.content.lower()

    def test_by_epic_node_empty_shows_explicit_empty_state(self) -> None:
        store = _StubBacklogStore(stories=[], by_epic={}, ready=[])
        dispatch = build_backlog_dispatch(store)
        outcome = dispatch(_backlog_node("backlog.by-epic"))
        assert outcome.content.strip() != ""
        assert "no" in outcome.content.lower()

    def test_view_story_leaf_renders_story_detail(self) -> None:
        store = _stub_store()
        dispatch = build_backlog_dispatch(store)
        menu = build_backlog_view_story_menu(store)
        outcome = dispatch(menu.children[0])
        assert "ST-0210" in outcome.content
        assert "Stub story" in outcome.content
        assert outcome.long_running is False

    def test_view_story_leaf_missing_story_reports_failure_without_raising(
        self,
    ) -> None:
        store = _stub_store()
        dispatch = build_backlog_dispatch(store)
        bogus = MenuNode(
            id="backlog.view-story.ST-9999",
            label="ST-9999: gone",
            type=MenuNodeType.DISPLAY,
        )
        outcome = dispatch(bogus)
        assert "ST-9999" in outcome.content
        assert outcome.long_running is False

    def test_unknown_node_id_raises(self) -> None:
        dispatch = build_backlog_dispatch(_stub_store())
        bogus = MenuNode(id="backlog.bogus", label="bogus", type=MenuNodeType.DISPLAY)
        with pytest.raises(ValueError, match="backlog.bogus"):
            dispatch(bogus)


# --- `view story` submenu construction (FR-U5, BR-058) ------------------------


class TestBuildBacklogViewStoryMenu:
    def test_is_a_menu_node(self) -> None:
        menu = build_backlog_view_story_menu(_stub_store())
        assert menu.id == "backlog.view-story"
        assert menu.type == MenuNodeType.MENU

    def test_lists_story_ids_with_titles(self) -> None:
        menu = build_backlog_view_story_menu(_stub_store())
        assert len(menu.children) == 1
        child = menu.children[0]
        assert child.type == MenuNodeType.DISPLAY
        assert "ST-0210" in child.label
        assert "Stub story" in child.label

    def test_children_ids_are_scoped_per_story(self) -> None:
        menu = build_backlog_view_story_menu(_stub_store())
        assert menu.children[0].id == "backlog.view-story.ST-0210"

    def test_children_follow_list_stories_order(self) -> None:
        story_a = _story(id="ST-0212", title="Second")
        story_b = _story(id="ST-0211", title="First")
        store = _StubBacklogStore(stories=[story_b, story_a], by_epic={}, ready=[])
        menu = build_backlog_view_story_menu(store)
        assert [child.id for child in menu.children] == [
            "backlog.view-story.ST-0211",
            "backlog.view-story.ST-0212",
        ]

    def test_empty_backlog_offers_no_selectable_story(self) -> None:
        store = _StubBacklogStore(stories=[], by_epic={}, ready=[])
        menu = build_backlog_view_story_menu(store)
        assert menu.children == []

    def test_all_children_are_display_leaves_no_function_action(self) -> None:
        """FR-U6/BR-056: no edit/create/delete/reorder action exists."""
        store = _StubBacklogStore(
            stories=[_story(id="ST-0213"), _story(id="ST-0214")],
            by_epic={},
            ready=[],
        )
        menu = build_backlog_view_story_menu(store)
        assert menu.children
        assert all(child.type == MenuNodeType.DISPLAY for child in menu.children)
        assert all(child.children == [] for child in menu.children)


# --- Read-only guarantee (BR-056, FR-U6, VR-039) ------------------------------


class _GuardBacklogStore:
    """Exposes the read methods plus a mutator that fails the test if called."""

    def __init__(self, stories) -> None:
        self._stories = stories

    def list_stories(self):
        return self._stories

    def stories_by_epic(self):
        return {}

    def ready_stories(self):
        return []

    def get_story(self, story_id):
        for story in self._stories:
            if story.id == story_id:
                return story
        raise KeyError(story_id)

    def update_status(self, story_id, new_status):  # pragma: no cover - defensive
        raise AssertionError("update_status must not be called by a backlog view")


class TestBacklogViewsAreReadOnly:
    @pytest.mark.parametrize(
        "node_id", ["backlog.list", "backlog.by-epic", "backlog.ready"]
    )
    def test_dispatch_never_mutates(self, node_id: str) -> None:
        store = _GuardBacklogStore([_story(id="ST-0220")])
        dispatch = build_backlog_dispatch(store)
        outcome = dispatch(_backlog_node(node_id))
        assert isinstance(outcome.content, str)

    def test_view_story_dispatch_never_mutates(self) -> None:
        store = _GuardBacklogStore([_story(id="ST-0221")])
        dispatch = build_backlog_dispatch(store)
        menu = build_backlog_view_story_menu(store)
        outcome = dispatch(menu.children[0])
        assert isinstance(outcome.content, str)

    def test_building_view_story_menu_never_mutates(self) -> None:
        store = _GuardBacklogStore([_story(id="ST-0222")])
        build_backlog_view_story_menu(store)  # would raise via the store if it did


# --- Root menu tree wiring (mirrors TestStatusMenuChildren, test_menu_tree.py) --


class TestBacklogMenuChildren:
    def _node(self):
        root = build_root_menu()
        return next(child for child in root.children if child.id == "backlog")

    def test_backlog_has_four_children(self) -> None:
        assert len(self._node().children) == 4

    def test_backlog_children_labels_in_spec_order(self) -> None:
        assert [c.label for c in self._node().children] == [
            "list",
            "by-epic",
            "ready",
            "view story",
        ]

    def test_backlog_children_ids_in_spec_order(self) -> None:
        assert [c.id for c in self._node().children] == [
            "backlog.list",
            "backlog.by-epic",
            "backlog.ready",
            "backlog.view-story",
        ]

    def test_first_three_children_are_display_leaves(self) -> None:
        for child in self._node().children[:3]:
            assert child.type == MenuNodeType.DISPLAY
            assert child.children == []

    def test_view_story_child_is_a_menu_with_no_static_children(self) -> None:
        """`view story`'s children are the current backlog snapshot's stories
        (FR-U5) — runtime data the pure tree builder cannot know; see
        `build_backlog_view_story_menu` (cli.py) for the populated node."""
        view_story = self._node().children[3]
        assert view_story.type == MenuNodeType.MENU
        assert view_story.children == []

    def test_backlog_children_have_no_default_marked(self) -> None:
        assert all(not c.is_default for c in self._node().children)
