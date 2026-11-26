"""Rewrite the references to moved files in a project's text files.

Two kinds of reference exist. A Markdown link resolves relative to the file
that holds it, so ``rewrite_links`` recomputes its destination. A full path
names a file from the project root, such as ``docs/proposals/a.md`` in front
matter, a code span, YAML, or prose, so ``rewrite_paths`` replaces it as text. A file whose sections move to
several pages needs a section map, so ``rewrite_section_links`` repoints
each link by its anchor.

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


# ── Section map ──────────────────────────────────────────────────────────
#
# ``rewrite_links`` moves one file to one file. A file split across several
# pages needs a section map instead: for an old path, each section anchor
# maps to the page that now holds the section, and the key "" gives the
# page of a link without an anchor (BR-151). A link to the installed copy
# under .agent-factory/factory/ keeps that prefix (L-11), unless the caller
# asks for the source page, as for this repository's own files (L-62).

SOURCE_ROOT = "packages/factory/"
INSTALLED_ROOT = ".agent-factory/factory/"
MAP_ROW = re.compile(r"^\| *`([^`]+)` *\|[^|]*\| *`#([^`]+)` *\| *\[`([^`]+)`\]")


class UnmappedAnchor(ValueError):
    """A link names a section that the section map does not assign."""


def read_section_map(table: str, sources: set[str]) -> dict[str, dict[str, str]]:
    """Read the rows of ``sources`` from the migration map's Markdown table.

    Each row gives a source path, an anchor, and the root-relative path of
    a page. The first row of a source is its opening, so its page is also
    the page of a link without an anchor.
    """
    sections: dict[str, dict[str, str]] = {}
    for line in table.splitlines():
        row = MAP_ROW.match(line)
        if row is None or row.group(1) not in sources:
            continue
        pages = sections.setdefault(row.group(1), {"": row.group(3)})
        pages[row.group(2)] = row.group(3)
    return sections


def _installed_split(target: str) -> tuple[str, bool]:
    """Return the source path of ``target`` and whether it is installed."""
    if target.startswith(INSTALLED_ROOT):
        return SOURCE_ROOT + target[len(INSTALLED_ROOT) :], True
    return target, False


def section_target(
    target: str,
    anchor: str,
    sections: dict[str, dict[str, str]],
    anchors: dict[str, set[str]],
    installed_links: bool = True,
) -> str | None:
    """Return the new root-relative target and anchor of a link, or None.

    None means the section map does not hold ``target``. The anchor stays
    when the new page has its heading in ``anchors``. With
    ``installed_links`` false, a link to the installed copy gets the source
    page.
    """
    source, installed = _installed_split(target)
    pages = sections.get(source)
    if pages is None:
        return None
    if anchor not in pages:
        raise UnmappedAnchor(f"{target}#{anchor}")
    page = pages[anchor]
    if installed and installed_links:
        if not page.startswith(SOURCE_ROOT):
            raise UnmappedAnchor(f"{target}#{anchor}: {page} is not installed")
        page = INSTALLED_ROOT + page[len(SOURCE_ROOT) :]
    keep = anchor and anchor in anchors.get(_installed_split(page)[0], set())
    return page + (f"#{anchor}" if keep else "")


def _link_spans(masked: str) -> list[tuple[int, int]]:
    """Every destination span of an inline link and a reference definition."""
    spans: list[tuple[int, int]] = []
    for match in LINK_START.finditer(masked):
        span = _destination_span(masked, match.end())
        if span is not None:
            spans.append(span[:2])
    for match in REFERENCE_DEFINITION.finditer(masked):
        begin, end = match.span(2)
        if masked[begin] == "<":
            begin, end = begin + 1, end - 1
        spans.append((begin, end))
    return sorted(spans)


def _section_destination(
    dest: str,
    src: str,
    sections: dict[str, dict[str, str]],
    anchors: dict[str, set[str]],
    installed_links: bool,
) -> str | None:
    """Return the new destination of one link of ``src``, or None."""
    if not dest or SCHEME.match(dest) or dest.startswith(("/", "#")):
        return None
    path, _, anchor = dest.partition("#")
    folder = posixpath.dirname(src)
    target = posixpath.normpath(posixpath.join(folder, unquote(path)))
    new = section_target(target, anchor, sections, anchors, installed_links)
    if new is None:
        return None
    page, mark, kept = new.partition("#")
    return posixpath.relpath(page, folder or ".") + mark + kept


def rewrite_section_links(
    text: str,
    src: str,
    sections: dict[str, dict[str, str]],
    anchors: dict[str, set[str]],
    installed_links: bool = True,
) -> tuple[str, list[tuple[str, str]]]:
    """Repoint the links of ``text`` to the pages of the section map.

    ``src`` is the file's path relative to the project root. ``anchors``
    maps each root-relative page path to the anchors its headings give.
    Only link destinations change; links in code stay. The result is the
    new text and each (old destination, new destination) in document order.
    ``installed_links`` is passed on to ``section_target``. Raises
    UnmappedAnchor for a link to a section that the map lacks.
    """
    edits: list[tuple[int, int, str, str]] = []
    for begin, end in _link_spans(mask_code(text)):
        raw = text[begin:end]
        new = _section_destination(raw, src, sections, anchors, installed_links)
        if new is not None and new != raw:
            edits.append((begin, end, raw, new))
    rewritten = text
    for begin, end, _, new in reversed(edits):
        rewritten = rewritten[:begin] + new + rewritten[end:]
    return rewritten, [(raw, new) for _, _, raw, new in edits]


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
