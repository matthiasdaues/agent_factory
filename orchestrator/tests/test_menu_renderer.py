"""Tests for MenuRenderer port, MenuItem DTO, and KeyEvent enum (ST-0037)."""

from __future__ import annotations

import pytest
from typing import List

from orchestrator.ports import MenuRenderer, MenuItem, KeyEvent


class TestMenuItemDTO:
    """MenuItem dataclass structure and immutability."""

    def test_menu_item_creation_all_fields(self):
        """MenuItem is created with all fields: label, suffix, is_default."""
        item = MenuItem(label="Test", suffix="[strong]", is_default=True)
        assert item.label == "Test"
        assert item.suffix == "[strong]"
        assert item.is_default is True

    def test_menu_item_suffix_optional(self):
        """MenuItem suffix defaults to None."""
        item = MenuItem(label="Test", is_default=False)
        assert item.suffix is None

    def test_menu_item_is_default_optional(self):
        """MenuItem is_default defaults to False."""
        item = MenuItem(label="Test")
        assert item.is_default is False

    def test_menu_item_frozen(self):
        """MenuItem is immutable (frozen)."""
        item = MenuItem(label="Test")
        with pytest.raises(AttributeError):
            item.label = "Changed"

    def test_menu_item_with_none_suffix(self):
        """MenuItem explicitly accepts None for suffix."""
        item = MenuItem(label="Test", suffix=None, is_default=False)
        assert item.suffix is None


class TestKeyEventEnum:
    """KeyEvent normalized navigation events."""

    def test_key_event_has_up(self):
        """KeyEvent has UP event."""
        assert hasattr(KeyEvent, "UP")
        assert KeyEvent.UP.value == "UP"

    def test_key_event_has_down(self):
        """KeyEvent has DOWN event."""
        assert hasattr(KeyEvent, "DOWN")
        assert KeyEvent.DOWN.value == "DOWN"

    def test_key_event_has_enter(self):
        """KeyEvent has ENTER event."""
        assert hasattr(KeyEvent, "ENTER")
        assert KeyEvent.ENTER.value == "ENTER"

    def test_key_event_has_back(self):
        """KeyEvent has BACK event (q/Esc navigation)."""
        assert hasattr(KeyEvent, "BACK")
        assert KeyEvent.BACK.value == "BACK"

    def test_key_event_has_exit(self):
        """KeyEvent has EXIT event (qq/Ctrl+C)."""
        assert hasattr(KeyEvent, "EXIT")
        assert KeyEvent.EXIT.value == "EXIT"

    def test_key_event_exactly_five_values(self):
        """KeyEvent has exactly five normalized events."""
        events = list(KeyEvent)
        assert len(events) == 5
        assert set(e.name for e in events) == {"UP", "DOWN", "ENTER", "BACK", "EXIT"}


class TestMenuRendererPort:
    """MenuRenderer protocol and contract."""

    def test_menu_renderer_is_protocol(self):
        """MenuRenderer is a Protocol (abc)."""
        # Verify it's a runtime_checkable protocol
        # runtime_checkable protocols have _is_protocol or __mro__ containing Protocol
        assert isinstance(MenuRenderer, type)

    def test_menu_renderer_render_menu_signature(self):
        """MenuRenderer has render_menu(items, selected_index) -> None."""
        import inspect

        sig = inspect.signature(MenuRenderer.render_menu)
        params = list(sig.parameters.keys())
        # Skip 'self' in protocol methods
        assert "items" in params
        assert "selected_index" in params

    def test_menu_renderer_render_display_signature(self):
        """MenuRenderer has render_display(content) -> None."""
        import inspect

        sig = inspect.signature(MenuRenderer.render_display)
        params = list(sig.parameters.keys())
        assert "content" in params

    def test_menu_renderer_get_keypress_signature(self):
        """MenuRenderer has get_keypress() -> KeyEvent."""
        import inspect

        sig = inspect.signature(MenuRenderer.get_keypress)
        # Return annotation should be KeyEvent (or string "KeyEvent" due to __future__ annotations)
        assert sig.return_annotation in (KeyEvent, "KeyEvent")

    def test_stub_menu_renderer_conforms_to_protocol(self):
        """A stub MenuRenderer implementation conforms to the protocol."""

        class StubMenuRenderer:
            def render_menu(self, items: List[MenuItem], selected_index: int) -> None:
                pass

            def render_display(self, content: str) -> None:
                pass

            def get_keypress(self) -> KeyEvent:
                return KeyEvent.UP

        renderer = StubMenuRenderer()
        assert isinstance(renderer, MenuRenderer)

    def test_render_menu_accepts_empty_list(self):
        """render_menu can be called with an empty items list."""

        class StubMenuRenderer:
            def render_menu(self, items: List[MenuItem], selected_index: int) -> None:
                self.last_items = items
                self.last_index = selected_index

            def render_display(self, content: str) -> None:
                pass

            def get_keypress(self) -> KeyEvent:
                return KeyEvent.UP

        renderer = StubMenuRenderer()
        renderer.render_menu([], 0)
        assert renderer.last_items == []
        assert renderer.last_index == 0

    def test_render_menu_with_items(self):
        """render_menu accepts a list of MenuItems and selected index."""

        class StubMenuRenderer:
            def render_menu(self, items: List[MenuItem], selected_index: int) -> None:
                self.last_items = items
                self.last_index = selected_index

            def render_display(self, content: str) -> None:
                pass

            def get_keypress(self) -> KeyEvent:
                return KeyEvent.UP

        renderer = StubMenuRenderer()
        items = [
            MenuItem(label="First", is_default=True),
            MenuItem(label="Second", suffix="[strong]", is_default=False),
            MenuItem(label="Third", is_default=False),
        ]
        renderer.render_menu(items, 1)
        assert renderer.last_items == items
        assert renderer.last_index == 1

    def test_render_display_with_content(self):
        """render_display accepts arbitrary content string."""

        class StubMenuRenderer:
            def render_menu(self, items: List[MenuItem], selected_index: int) -> None:
                pass

            def render_display(self, content: str) -> None:
                self.last_content = content

            def get_keypress(self) -> KeyEvent:
                return KeyEvent.UP

        renderer = StubMenuRenderer()
        content = "Agent: test-agent\nRole: author\nStatus: pending"
        renderer.render_display(content)
        assert renderer.last_content == content

    def test_get_keypress_returns_key_event(self):
        """get_keypress returns exactly one of the five KeyEvent values."""

        class StubMenuRenderer:
            def render_menu(self, items: List[MenuItem], selected_index: int) -> None:
                pass

            def render_display(self, content: str) -> None:
                pass

            def get_keypress(self) -> KeyEvent:
                return KeyEvent.DOWN

        renderer = StubMenuRenderer()
        key = renderer.get_keypress()
        assert isinstance(key, KeyEvent)
        assert key in [
            KeyEvent.UP,
            KeyEvent.DOWN,
            KeyEvent.ENTER,
            KeyEvent.BACK,
            KeyEvent.EXIT,
        ]
