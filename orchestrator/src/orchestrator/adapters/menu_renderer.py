"""TerminalMenuRenderer — concrete MenuRenderer adapter for a POSIX terminal.

ST-0038 / T-29 / ADR-0016. Renders one menu or display node at a time and
decodes raw keyboard input into normalised ``KeyEvent``s, so the core never
touches a terminal library directly (ADR-0001).

Framework choice (T-29, NFR-12): raw ANSI cursor conventions over the
standard-library ``termios``/``tty`` modules, not ``curses`` and not a
third-party TUI framework. `curses` was considered and rejected for this
specific seam: it takes over the whole screen buffer and wants a real
terminal (or its own, heavier test harness) to drive headlessly, which
conflicts with "tests must not require a real interactive terminal". Raw
ANSI + termios reads and writes plain bytes/text through two small,
injectable seams (``byte_reader`` for input, ``output_stream`` for output),
so the whole adapter is exercised in CI against an in-memory fake reader and
a ``StringIO`` — no third-party dependency, honouring NFR-12/ADR-0006.
"""

from __future__ import annotations

import os
import select
from contextlib import contextmanager
from typing import Iterator, List, Optional, Protocol, TextIO

from orchestrator.ports import KeyEvent, MenuItem

try:  # pragma: no cover - POSIX only; the fallback keeps import safe elsewhere
    import termios
    import tty
except ImportError:  # pragma: no cover
    termios = None  # type: ignore[assignment]
    tty = None  # type: ignore[assignment]


ESC = "\x1b"
CTRL_C = "\x03"
ENTER_CHARS = ("\r", "\n")

# How long get_keypress() waits, after a lone ESC or 'q', for a second byte
# before deciding it was a standalone key rather than the start of an arrow
# escape sequence (ESC '[' 'A'/'B') or the "qq" exit gesture.
LOOKAHEAD_TIMEOUT_S = 0.05


class ByteReader(Protocol):
    """Input seam for get_keypress(): a real tty, or a scripted test fake."""

    def read_byte(self, timeout: Optional[float] = None) -> str:
        """Return the next input character.

        ``timeout=None`` means block until a byte is available. A bounded
        ``timeout`` means "peek": return "" if nothing arrives in time.
        """
        ...


class TermiosByteReader:
    """Reads one character at a time from a real POSIX terminal fd.

    Uses ``select`` so a bounded-timeout read can distinguish "nothing typed
    yet" from "byte available", which is what lets get_keypress() tell a
    lone Esc/`q` apart from the start of a multi-byte sequence.
    """

    def __init__(self, stream: TextIO) -> None:
        self._fd = stream.fileno()

    def read_byte(self, timeout: Optional[float] = None) -> str:
        ready, _, _ = select.select([self._fd], [], [], timeout)
        if not ready:
            return ""
        data = os.read(self._fd, 1)
        return data.decode("utf-8", errors="replace")


class ScriptedByteReader:
    """Feeds a fixed character script; a real-tty stand-in for headless tests.

    A bounded-timeout read past the end of the script returns "" (mirrors a
    real reader's "nothing arrived in time"). A *blocking* read (timeout is
    None) past the end of the script raises ``EOFError`` instead of hanging
    forever, so a mis-scripted test fails fast.
    """

    def __init__(self, script: str) -> None:
        self._chars: List[str] = list(script)

    def read_byte(self, timeout: Optional[float] = None) -> str:
        if not self._chars:
            if timeout is None:
                raise EOFError("ScriptedByteReader: no more scripted input")
            return ""
        return self._chars.pop(0)


class _NullByteReader:
    """Fallback reader when no real tty and no injected reader is available.

    Fails loudly on use rather than silently hanging, so running the
    adapter outside a terminal (and without a test double) is a clear
    error, not a deadlock.
    """

    def read_byte(self, timeout: Optional[float] = None) -> str:
        raise EOFError(
            "TerminalMenuRenderer: no interactive terminal and no byte_reader injected"
        )


class TerminalMenuRenderer:
    """Concrete MenuRenderer for a POSIX terminal (ST-0038).

    Structurally satisfies ``orchestrator.ports.MenuRenderer`` (a
    ``runtime_checkable`` Protocol) — no explicit inheritance needed.
    """

    INDENT = "   "
    CURSOR = "-> "
    DEFAULT_MARKER = "★"  # ★

    def __init__(
        self,
        input_stream: Optional[TextIO] = None,
        output_stream: Optional[TextIO] = None,
        byte_reader: Optional[ByteReader] = None,
    ) -> None:
        import sys

        self._in: TextIO = input_stream if input_stream is not None else sys.stdin
        self._out: TextIO = output_stream if output_stream is not None else sys.stdout
        self._reader: ByteReader = (
            byte_reader if byte_reader is not None else self._make_default_reader()
        )
        self._pushback: Optional[str] = None
        self._last_frame_lines: int = 0

    # -- MenuRenderer protocol -------------------------------------------------

    def render_menu(self, items: List[MenuItem], selected_index: int) -> None:
        """Paint each item; the active item gets '-> ', defaults get '★'."""
        lines = []
        for index, item in enumerate(items):
            prefix = self.CURSOR if index == selected_index else self.INDENT
            parts = [item.label]
            if item.is_default:
                parts.append(self.DEFAULT_MARKER)
            if item.suffix:
                parts.append(item.suffix)
            lines.append(prefix + " ".join(parts))
        if lines:
            self._repaint("\n".join(lines) + "\n")

    def render_display(self, content: str) -> None:
        """Render read-only content. Ensures exactly one trailing newline.

        Waiting for the next keypress and returning to the parent menu is
        the MenuController's job (UC-08 §9a): it calls render_display(),
        then get_keypress(), then transitions state. This method only
        paints.
        """
        if not content.endswith("\n"):
            content += "\n"
        self._repaint(content)

    # -- internals ---------------------------------------------------------

    def _repaint(self, content: str) -> None:
        """Erase the previous frame in place, then paint the new one.

        NFR-8/NFR-9 require redraw via cursor movement, not a scrolling
        transcript: move the cursor up over every line the last frame
        wrote, erase from there to the end of the screen (`\\x1b[J`, so a
        shorter new frame doesn't leave stale lines below it), then paint.
        The very first frame has no prior lines, so no escape codes are
        emitted and existing single-frame assertions are unaffected.
        """
        if self._last_frame_lines:
            self._out.write(f"\x1b[{self._last_frame_lines}A\x1b[J")
        self._out.write(content)
        self._last_frame_lines = content.count("\n")
        self._out.flush()

    def get_keypress(self) -> KeyEvent:
        """Block for one key, decode it (incl. arrow escapes) into a KeyEvent."""
        with self._raw_mode():
            while True:
                ch = self._next_char()
                if ch == "":
                    continue
                if ch == CTRL_C:
                    return KeyEvent.EXIT
                if ch in ENTER_CHARS:
                    return KeyEvent.ENTER
                if ch == ESC:
                    event = self._decode_escape()
                    if event is not None:
                        return event
                    continue
                if ch == "q":
                    event = self._decode_q()
                    if event is not None:
                        return event
                    continue
                # Unrecognised byte: ignore and keep reading.

    # -- internals ---------------------------------------------------------

    def _decode_escape(self) -> Optional[KeyEvent]:
        """After a lone ESC byte, look ahead for a '[A'/'[B' arrow sequence."""
        nxt = self._next_char(timeout=LOOKAHEAD_TIMEOUT_S)
        if nxt == "[":
            seq = self._next_char(timeout=LOOKAHEAD_TIMEOUT_S)
            if seq == "A":
                return KeyEvent.UP
            if seq == "B":
                return KeyEvent.DOWN
            # Unrecognised escape sequence (e.g. other cursor/function keys):
            # swallow it and let the caller read the next real key.
            return None
        if nxt:
            self._pushback_char(nxt)
        return KeyEvent.BACK

    def _decode_q(self) -> Optional[KeyEvent]:
        """After a single 'q', look ahead one char for the 'qq' exit gesture."""
        nxt = self._next_char(timeout=LOOKAHEAD_TIMEOUT_S)
        if nxt == "q":
            return KeyEvent.EXIT
        if nxt:
            self._pushback_char(nxt)
        return KeyEvent.BACK

    def _next_char(self, timeout: Optional[float] = None) -> str:
        if self._pushback is not None:
            ch, self._pushback = self._pushback, None
            return ch
        return self._reader.read_byte(timeout)

    def _pushback_char(self, ch: str) -> None:
        self._pushback = ch

    def _make_default_reader(self) -> ByteReader:
        if termios is not None and hasattr(self._in, "fileno"):
            try:
                fd = self._in.fileno()
                if os.isatty(fd):
                    return TermiosByteReader(self._in)
            except (AttributeError, OSError, ValueError):
                pass
        return _NullByteReader()

    @contextmanager
    def _raw_mode(self) -> Iterator[None]:
        """Put the real terminal in raw mode for the duration of one read.

        A no-op when stdin is not a real, POSIX interactive terminal (e.g.
        under test with a ScriptedByteReader), so headless test runs never
        touch termios.
        """
        if termios is None or tty is None or not hasattr(self._in, "fileno"):
            yield
            return
        try:
            fd = self._in.fileno()
            if not os.isatty(fd):
                yield
                return
        except (AttributeError, OSError, ValueError):
            yield
            return
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            yield
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
