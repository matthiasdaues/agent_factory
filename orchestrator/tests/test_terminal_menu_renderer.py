"""Tests for TerminalMenuRenderer, the concrete MenuRenderer adapter (ST-0038).

Drives the adapter headlessly: a scripted ``ByteReader`` stands in for a real
POSIX tty on stdin, and an in-memory ``StringIO`` stands in for stdout. No
real interactive terminal is required, so this suite runs in CI.
"""

from __future__ import annotations

import io

import pytest

from orchestrator.adapters.menu_renderer import ScriptedByteReader, TerminalMenuRenderer
from orchestrator.ports import KeyEvent, MenuItem, MenuRenderer


def make_renderer(script: str = "") -> tuple[TerminalMenuRenderer, io.StringIO]:
    out = io.StringIO()
    reader = ScriptedByteReader(script)
    renderer = TerminalMenuRenderer(output_stream=out, byte_reader=reader)
    return renderer, out


class TestProtocolConformance:
    def test_terminal_menu_renderer_satisfies_menu_renderer_protocol(self):
        renderer, _ = make_renderer()
        assert isinstance(renderer, MenuRenderer)


class TestRenderMenu:
    def test_active_item_gets_arrow_cursor_others_get_indent(self):
        renderer, out = make_renderer()
        items = [
            MenuItem(label="Alpha"),
            MenuItem(label="Beta"),
            MenuItem(label="Gamma"),
        ]

        renderer.render_menu(items, selected_index=1)

        lines = out.getvalue().splitlines()
        assert lines[0] == "   Alpha"
        assert lines[1] == "-> Beta"
        assert lines[2] == "   Gamma"

    def test_default_item_shows_star_marker(self):
        renderer, out = make_renderer()
        items = [MenuItem(label="Alpha", is_default=True), MenuItem(label="Beta")]

        renderer.render_menu(items, selected_index=0)

        lines = out.getvalue().splitlines()
        assert lines[0] == "-> Alpha ★"
        assert lines[1] == "   Beta"

    def test_suffix_is_rendered_after_label(self):
        renderer, out = make_renderer()
        items = [MenuItem(label="implementation-agent", suffix="[standard]")]

        renderer.render_menu(items, selected_index=0)

        assert out.getvalue().splitlines()[0] == "-> implementation-agent [standard]"

    def test_default_marker_and_suffix_combine(self):
        renderer, out = make_renderer()
        items = [
            MenuItem(label="requirements-agent", suffix="[strong]", is_default=True)
        ]

        renderer.render_menu(items, selected_index=0)

        assert out.getvalue().splitlines()[0] == "-> requirements-agent ★ [strong]"

    def test_empty_item_list_renders_nothing(self):
        renderer, out = make_renderer()

        renderer.render_menu([], selected_index=0)

        assert out.getvalue() == ""

    def test_render_menu_matches_spec_example(self):
        """cli_specification.md 'Navigation conventions > Example rendering'."""
        renderer, out = make_renderer()
        items = [
            MenuItem(label="requirements-agent", suffix="[strong]"),
            MenuItem(label="architecture-agent", suffix="[strong]"),
            MenuItem(label="planning-agent", suffix="[strong]"),
            MenuItem(label="implementation-agent", suffix="[standard]"),
            MenuItem(label="qa-agent", suffix="[strong]"),
            MenuItem(label="coaching-agent", suffix="[strong]"),
        ]

        renderer.render_menu(items, selected_index=3)

        lines = out.getvalue().splitlines()
        assert lines[3] == "-> implementation-agent [standard]"
        assert lines[0].startswith("   requirements-agent")


class TestRepaintInPlace:
    def test_first_render_menu_emits_no_clear_sequence(self):
        renderer, out = make_renderer()
        items = [MenuItem(label="Alpha"), MenuItem(label="Beta")]

        renderer.render_menu(items, selected_index=0)

        assert "\x1b[" not in out.getvalue()

    def test_second_render_menu_clears_previous_frame_first(self):
        renderer, out = make_renderer()
        items = [
            MenuItem(label="Alpha"),
            MenuItem(label="Beta"),
            MenuItem(label="Gamma"),
        ]

        renderer.render_menu(items, selected_index=0)
        renderer.render_menu(items, selected_index=1)

        # Previous frame was 3 lines: cursor up 3, erase to end of screen.
        second_frame = out.getvalue().split("Gamma\n", 1)[1]
        assert second_frame == "\x1b[3A\x1b[J   Alpha\n-> Beta\n   Gamma\n"

    def test_shorter_second_frame_still_clears_full_previous_frame(self):
        renderer, out = make_renderer()
        long_menu = [MenuItem(label=f"Item{i}") for i in range(5)]
        short_menu = [MenuItem(label="Only")]

        renderer.render_menu(long_menu, selected_index=0)
        renderer.render_menu(short_menu, selected_index=0)

        second_frame = out.getvalue().split("Item4\n", 1)[1]
        assert second_frame == "\x1b[5A\x1b[J-> Only\n"

    def test_render_display_clears_a_prior_menu_frame(self):
        renderer, out = make_renderer()
        items = [MenuItem(label="Alpha"), MenuItem(label="Beta")]

        renderer.render_menu(items, selected_index=0)
        renderer.render_display("Agent: test-agent")

        second_frame = out.getvalue().split("Beta\n", 1)[1]
        assert second_frame == "\x1b[2A\x1b[JAgent: test-agent\n"

    def test_render_menu_clears_a_prior_display_frame(self):
        renderer, out = make_renderer()

        renderer.render_display("line one\nline two")
        renderer.render_menu([MenuItem(label="Alpha")], selected_index=0)

        second_frame = out.getvalue().split("line two\n", 1)[1]
        assert second_frame == "\x1b[2A\x1b[J-> Alpha\n"


class TestRenderDisplay:
    def test_render_display_writes_content(self):
        renderer, out = make_renderer()

        renderer.render_display("Agent: test-agent\nRole: author")

        assert out.getvalue() == "Agent: test-agent\nRole: author\n"

    def test_render_display_does_not_double_trailing_newline(self):
        renderer, out = make_renderer()

        renderer.render_display("already terminated\n")

        assert out.getvalue() == "already terminated\n"


class TestGetKeypressBasicKeys:
    def test_up_arrow_escape_sequence(self):
        renderer, _ = make_renderer("\x1b[A")
        assert renderer.get_keypress() == KeyEvent.UP

    def test_down_arrow_escape_sequence(self):
        renderer, _ = make_renderer("\x1b[B")
        assert renderer.get_keypress() == KeyEvent.DOWN

    def test_enter_on_carriage_return(self):
        renderer, _ = make_renderer("\r")
        assert renderer.get_keypress() == KeyEvent.ENTER

    def test_enter_on_newline(self):
        renderer, _ = make_renderer("\n")
        assert renderer.get_keypress() == KeyEvent.ENTER

    def test_lone_esc_is_back(self):
        renderer, _ = make_renderer("\x1b")
        assert renderer.get_keypress() == KeyEvent.BACK

    def test_q_alone_is_back(self):
        renderer, _ = make_renderer("q")
        assert renderer.get_keypress() == KeyEvent.BACK

    def test_qq_is_exit(self):
        renderer, _ = make_renderer("qq")
        assert renderer.get_keypress() == KeyEvent.EXIT

    def test_ctrl_c_is_exit(self):
        renderer, _ = make_renderer("\x03")
        assert renderer.get_keypress() == KeyEvent.EXIT


class TestGetKeypressSequencing:
    def test_multiple_keypresses_drive_a_navigation_sequence(self):
        renderer, _ = make_renderer("\x1b[B\x1b[B\r")
        assert renderer.get_keypress() == KeyEvent.DOWN
        assert renderer.get_keypress() == KeyEvent.DOWN
        assert renderer.get_keypress() == KeyEvent.ENTER

    def test_q_followed_by_unrelated_key_pushes_back_the_lookahead(self):
        """'q' peeks one char ahead to detect 'qq'; a non-'q' char must not
        be swallowed — it belongs to the *next* get_keypress() call."""
        renderer, _ = make_renderer("qx\r")

        first = renderer.get_keypress()  # 'q' with 'x' lookahead -> BACK
        second = renderer.get_keypress()  # pushed-back 'x' is unrecognised,
        # so the reader keeps consuming until '\r' -> ENTER

        assert first == KeyEvent.BACK
        assert second == KeyEvent.ENTER

    def test_unrecognised_bytes_are_skipped(self):
        renderer, _ = make_renderer("zzz\r")
        assert renderer.get_keypress() == KeyEvent.ENTER

    def test_esc_followed_by_unrecognised_sequence_is_ignored_then_next_key_read(self):
        renderer, _ = make_renderer("\x1b[Z\r")
        # '\x1b[Z' is not a known arrow sequence; get_keypress should not
        # get stuck, and should proceed to read the next real key.
        assert renderer.get_keypress() == KeyEvent.ENTER

    def test_blocking_read_past_end_of_script_raises(self):
        """A scripted reader that runs out of input on a *blocking* read
        signals it loudly (EOFError) instead of hanging forever, so a
        mis-scripted test fails fast rather than deadlocking CI."""
        renderer, _ = make_renderer("")
        with pytest.raises(EOFError):
            renderer.get_keypress()


class TestScriptedByteReader:
    def test_timeout_read_past_end_of_script_returns_empty(self):
        reader = ScriptedByteReader("")
        assert reader.read_byte(timeout=0.01) == ""

    def test_reads_characters_in_order(self):
        reader = ScriptedByteReader("ab")
        assert reader.read_byte() == "a"
        assert reader.read_byte() == "b"
