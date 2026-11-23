"""Rewrite the references to moved files in a project's text files.

Two kinds of reference exist. A Markdown link resolves relative to the file
that holds it, so ``rewrite_links`` recomputes its destination. A full path
names a file from the project root, such as ``docs/proposals/a.md`` in front
matter, a code span, YAML, or prose, so ``rewrite_paths`` replaces it as text.

The link syntax follows packages/factory/scripts/link-check, the gate the
rewritten files must pass: inline links and images, reference definitions,
and no link inside front matter, a fenced block, or a code span.

migrate-spec-layout and move-docs share this module. It uses only the
standard library.
"""

from __future__ import annotations

import posixpath
import re
from urllib.parse import quote, unquote

LINK_START = re.compile(r"!?\[[^\]]*\]\(")
REFERENCE_DEFINITION = re.compile(
    r"^ {0,3}\[([^\]^][^\]]*)\]:[ \t]*(<[^>\n]*>|\S+)", re.MULTILINE
)
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"`+[^`\n]*`+")




def _blank(text: str) -> str:
    return re.sub(r"[^\r\n]", " ", text)


def mask_code(text: str) -> str:
    """Blank front matter, fenced blocks, and code spans; keep every offset."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    index = 0
    if lines and lines[0].strip() == "---":
        for end in range(1, len(lines)):
            if lines[end].strip() in ("---", "..."):
                out += [_blank(line) for line in lines[: end + 1]]
                index = end + 1
                break
    closing: re.Pattern[str] | None = None
    for line in lines[index:]:
        body = line.rstrip("\r\n")
        if closing is None:
            match = FENCE_OPEN.match(body)
            if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                run = match.group(1)
                closing = re.compile(
                    rf"^ {{0,3}}{re.escape(run[0])}{{{len(run)},}}[ \t]*$"
                )
                out.append(_blank(line))
                continue
            out.append(line)
        else:
            if closing.match(body):
                closing = None
            out.append(_blank(line))
    return INLINE_CODE.sub(lambda span: " " * len(span.group()), "".join(out))


def _destination_span(text: str, start: int) -> tuple[int, int, int] | None:
    """Locate the destination after a link's "(": (begin, end, after).

    ``text[begin:end]`` is the raw destination without angle brackets;
    ``after`` is the offset behind it.
    """
    position = start
    while position < len(text) and text[position] in " \t\n":
        position += 1
    if position < len(text) and text[position] == "<":
        end = text.find(">", position + 1)
        if end == -1 or "\n" in text[position:end]:
            return None
        return position + 1, end, end + 1
    begin, depth = position, 0
    while position < len(text):
        char = text[position]
        if char == "\\" and position + 1 < len(text):
            position += 2
            continue
        if char.isspace():
            break
        if char == "(":
            depth += 1
        elif char == ")":
            if depth == 0:
                break
            depth -= 1
        position += 1
    return begin, position, position


def _link_close(text: str, position: int) -> int | None:
    """Return the offset behind the ")" that closes a link, or None."""
    while position < len(text) and text[position] in " \t\n":
        position += 1
    if position < len(text) and text[position] in "\"'(":
        closer = ")" if text[position] == "(" else text[position]
        end = text.find(closer, position + 1)
        if end == -1:
            return None
        position = end + 1
        while position < len(text) and text[position] in " \t\n":
            position += 1
    if position < len(text) and text[position] == ")":
        return position + 1
    return None


def code_span(text: str) -> str:
    """Render ``text`` as a code span, with a longer fence around a backtick."""
    if "`" in text:
        return f"`` {text} ``"
    return f"`{text}`"


def _new_destination(
    dest: str, src: str, dst: str, moved: dict[str, str]
) -> str | None:
    """Return the destination of a link of ``src`` read from ``dst``, or None.

    None means the link stays as it is: an external link, a link to the
    same file, an absolute path, or a target that neither moves nor needs a
    rebase.
    """
    if not dest or SCHEME.match(dest) or dest.startswith(("/", "#")):
        return None
    cut = min((i for i in (dest.find("?"), dest.find("#")) if i != -1), default=-1)
    path, suffix = (dest, "") if cut == -1 else (dest[:cut], dest[cut:])
    decoded = unquote(path)
    target = posixpath.normpath(posixpath.join(posixpath.dirname(src), decoded))
    new_target = moved.get(target, target)
    new_dir = posixpath.dirname(dst) or "."
    if posixpath.normpath(posixpath.join(new_dir, decoded)) == new_target:
        return None
    new = posixpath.relpath(new_target, new_dir)
    if decoded.endswith("/"):
        new += "/"
    if decoded != path:
        new = quote(new)
    return new + suffix


def _removed_target(dest: str, src: str, removed: set[str]) -> bool:
    if not dest or SCHEME.match(dest) or dest.startswith(("/", "#")):
        return False
    path = re.split(r"[?#]", dest, maxsplit=1)[0]
    target = posixpath.normpath(posixpath.join(posixpath.dirname(src), unquote(path)))
    return target in removed


def rewrite_links(
    text: str, src: str, dst: str, moved: dict[str, str], removed: set[str]
) -> tuple[str, list[tuple[str, str]]]:
    """Rewrite the Markdown links of ``text`` for the move from ``src`` to ``dst``.

    ``src`` and ``dst`` are the file's paths before and after the run,
    relative to the project root. ``moved`` maps each moved path to its new
    path; ``removed`` holds the paths the run removes. A link to a moved
    file points at its new path; a relative link of a moved file resolves
    from its new folder; a link to a removed file becomes its link text in
    a code span. Anchors and queries stay. The result is the new text and
    each (old target, new target) in document order.
    """
    masked = mask_code(text)
    edits: list[tuple[int, int, str, str, str]] = []
    for match in LINK_START.finditer(masked):
        span = _destination_span(masked, match.end())
        if span is None:
            continue
        begin, end, after = span
        raw = text[begin:end]
        dest = re.sub(r"\\(.)", r"\1", raw)
        if _removed_target(dest, src, removed):
            close = _link_close(masked, after)
            if close is None:
                continue
            label = match.group()[match.group().index("[") + 1 : -2]
            shown = code_span(label or dest)
            edits.append((match.start(), close, shown, raw, shown))
            continue
        new = _new_destination(dest, src, dst, moved)
        if new is not None:
            edits.append((begin, end, new, raw, new))
    for match in REFERENCE_DEFINITION.finditer(masked):
        begin, end = match.span(2)
        if masked[begin] == "<":
            begin, end = begin + 1, end - 1
        raw = text[begin:end]
        if _removed_target(raw, src, removed):
            line_end = masked.find("\n", end)
            line_end = len(masked) if line_end == -1 else line_end
            shown = code_span(match.group(1))
            edits.append((match.start(), line_end, shown, raw, shown))
            continue
        new = _new_destination(raw, src, dst, moved)
        if new is not None:
            edits.append((begin, end, new, raw, new))
    edits.sort()
    rewritten = text
    for start, stop, replacement, _, _ in reversed(edits):
        rewritten = rewritten[:start] + replacement + rewritten[stop:]
    return rewritten, [(old, new) for _, _, _, old, new in edits]


# ── Full paths ───────────────────────────────────────────────────────────
#
# A full path starts at the project root. It stands alone: no word
# character, dot, slash, or hyphen before it, so ``../docs/a.md`` and
# ``x/docs/a.md`` do not match. Nothing that extends the name follows it, so
# ``docs/a.md`` does not match ``docs/a.mdx`` or ``docs/a.md/b``. A dot that
# ends a sentence and an anchor such as ``#decisions`` may follow.


def _full_path_pattern(paths: list[str]) -> re.Pattern[str]:
    names = "|".join(re.escape(p) for p in sorted(paths, key=len, reverse=True))
    return re.compile(rf"(?<![\w./-])(?:{names})(?![\w/-]|\.[\w-])")


def rewrite_paths(
    text: str, moved: dict[str, str]
) -> tuple[str, list[tuple[int, str, str]]]:
    """Replace each full path of a moved file in ``text`` with its new path.

    ``moved`` maps each old path to its new path, both relative to the
    project root. The result is the new text and each (line, old path, new
    path) in document order, with lines counted from 1.
    """
    if not moved:
        return text, []
    pattern = _full_path_pattern(list(moved))
    rewrites: list[tuple[int, str, str]] = []

    def replace(match: re.Match[str]) -> str:
        line = text.count("\n", 0, match.start()) + 1
        rewrites.append((line, match.group(), moved[match.group()]))
        return moved[match.group()]

    return pattern.sub(replace, text), rewrites
