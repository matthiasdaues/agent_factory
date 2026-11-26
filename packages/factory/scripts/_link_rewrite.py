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
    return INLINE_CODE.sub(lambda span: " " * len(span.group()), _mask_blocks(text))


def _mask_blocks(text: str) -> str:
    """Blank front matter and fenced blocks; keep every offset."""
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
    return "".join(out)


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


class AmbiguousLink(ValueError):
    """The scanner cannot tell a link to a mapped file safely: "file:line: why"."""


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


BACKTICKS = re.compile(r"`+")
BLANK_LINE = re.compile(r"\n[ \t]*\n")
LABEL_END = re.compile(r"\]\(")
SPLIT_DEFINITION = re.compile(
    r"^ {0,3}\[[^\]^][^\]]*\]:[ \t]*\n[ \t]*(<[^>\n]*>|\S+)", re.MULTILINE
)

Span = tuple[int, int]
Doubt = tuple[int, int, int, str]  # (offset, begin, end, reason)


def _escaped(text: str, offset: int) -> bool:
    """Whether an odd run of backslashes escapes the character at ``offset``."""
    count = 0
    while count < offset and text[offset - count - 1] == "\\":
        count += 1
    return count % 2 == 1


def _span_close(masked: str, begin: int, end: int) -> int | None:
    """Return the offset behind the run that closes ``masked[begin:end]``, or None.

    The closing run has the same length and lies in the same paragraph.
    """
    if begin == end:
        return None
    close = re.compile(rf"(?<!`)`{{{end - begin}}}(?!`)").search(masked, end)
    if close is None or BLANK_LINE.search(masked, end, close.start()):
        return None
    return close.end()


def _code_spans(masked: str) -> tuple[list[Span], list[Span]]:
    """Return the one-line and the multiline code spans of ``masked``.

    The rules follow CommonMark. A backslash before a run makes its first
    backtick a literal character. A span opens with a backtick run and
    closes with the next run of the same length inside the same paragraph;
    a run without one stays text.
    """
    single: list[Span] = []
    multi: list[Span] = []
    run = BACKTICKS.search(masked)
    while run is not None:
        begin = run.start() + _escaped(masked, run.start())
        close = _span_close(masked, begin, run.end())
        if close is None:
            run = BACKTICKS.search(masked, run.end())
            continue
        (multi if "\n" in masked[begin:close] else single).append((begin, close))
        run = BACKTICKS.search(masked, close)
    return single, multi


def _mask_section_code(text: str) -> tuple[str, list[Span]]:
    """Blank front matter, fences, and one-line code spans; return the multiline spans."""
    masked = _mask_blocks(text)
    single, multi = _code_spans(masked)
    for begin, end in single:
        masked = masked[:begin] + _blank(masked[begin:end]) + masked[end:]
    return masked, multi


def _region_start(regions: list[Span], offset: int) -> int | None:
    return next((begin for begin, end in regions if begin <= offset < end), None)


def _inline_links(
    masked: str, regions: list[Span]
) -> tuple[list[Span], list[Doubt], set[int]]:
    """Return the sure destinations, the doubtful links, and each label's end."""
    spans: list[Span] = []
    doubts: list[Doubt] = []
    label_ends: set[int] = set()
    for match in LINK_START.finditer(masked):
        label_ends.add(match.end())
        span = _destination_span(masked, match.end())
        if span is None:
            continue
        begin, end, after = span
        region = _region_start(regions, begin)
        if region is not None:
            doubts.append((region, begin, end, "a link inside a multiline code span"))
        elif _link_close(masked, after) is None:
            doubts.append((match.start(), begin, end, "an unclosed link"))
        else:
            spans.append((begin, end))
    return spans, doubts, label_ends


def _open_bracket(masked: str, offset: int) -> bool:
    """Whether a "[" before ``offset`` in the same paragraph stays unmatched.

    A backslash-escaped bracket is a literal character.
    """
    starts = [blank.end() for blank in BLANK_LINE.finditer(masked, 0, offset)]
    depth = 0
    for position in range(starts[-1] if starts else 0, offset):
        if masked[position] in "[]" and not _escaped(masked, position):
            depth = depth + 1 if masked[position] == "[" else max(depth - 1, 0)
    return depth > 0


def _nested_labels(masked: str, label_ends: set[int]) -> list[Doubt]:
    """Every "](" that ends a label no simple link start matched.

    Only a "](" behind an unmatched "[" in its paragraph ends a label; any
    other "](" is plain text.
    """
    doubts: list[Doubt] = []
    for match in LABEL_END.finditer(masked):
        if match.end() in label_ends or not _open_bracket(masked, match.start()):
            continue
        span = _destination_span(masked, match.end())
        if span is not None:
            doubts.append(
                (match.start(), span[0], span[1], "a nested bracket in a link label")
            )
    return doubts


def _unangled(masked: str, match: re.Match[str], group: int) -> Span:
    begin, end = match.span(group)
    return (begin + 1, end - 1) if masked[begin] == "<" else (begin, end)


def _definitions(masked: str, regions: list[Span]) -> tuple[list[Span], list[Doubt]]:
    """Return the sure destinations of the reference definitions and the doubtful ones.

    A definition inside a multiline code span or split over two lines is
    doubtful.
    """
    spans: list[Span] = []
    doubts: list[Doubt] = []
    for match in REFERENCE_DEFINITION.finditer(masked):
        begin, end = _unangled(masked, match, 2)
        region = _region_start(regions, begin)
        if region is None:
            spans.append((begin, end))
        else:
            reason = "a reference definition inside a multiline code span"
            doubts.append((region, begin, end, reason))
    doubts += [
        (
            m.start(),
            *_unangled(masked, m, 1),
            "a reference definition split over two lines",
        )
        for m in SPLIT_DEFINITION.finditer(masked)
    ]
    return spans, doubts


def _link_scan(text: str) -> tuple[list[Span], list[Doubt]]:
    """Every sure destination span of ``text`` and every doubtful link."""
    masked, regions = _mask_section_code(text)
    spans, doubts, label_ends = _inline_links(masked, regions)
    definitions, definition_doubts = _definitions(masked, regions)
    nested = _nested_labels(masked, label_ends)
    return sorted(spans + definitions), doubts + nested + definition_doubts


def _target(dest: str, src: str) -> tuple[str, str, str] | None:
    """Return the root-relative target, query, and fragment of a link, or None."""
    if not dest or SCHEME.match(dest) or dest.startswith(("/", "#")):
        return None
    rest, mark, fragment = dest.partition("#")
    path, question, query = rest.partition("?")
    target = posixpath.normpath(posixpath.join(posixpath.dirname(src), unquote(path)))
    return target, question + query, mark + fragment


def _refuse_doubts(
    text: str, src: str, doubts: list[Doubt], sections: dict[str, dict[str, str]]
) -> None:
    """Raise AmbiguousLink for the first doubtful link to a mapped file."""
    for offset, begin, end, reason in sorted(doubts):
        found = _target(text[begin:end], src)
        if found is not None and _installed_split(found[0])[0] in sections:
            line = text.count("\n", 0, offset) + 1
            raise AmbiguousLink(f"{src}:{line}: {reason}: {text[begin:end]}")


def _section_destination(
    dest: str,
    src: str,
    sections: dict[str, dict[str, str]],
    anchors: dict[str, set[str]],
    installed_links: bool,
) -> str | None:
    """Return the new destination of one link of ``src``, or None.

    The query stays. The fragment is decoded for the lookup and keeps its
    spelling when the new page has the heading.
    """
    found = _target(dest, src)
    if found is None:
        return None
    target, query, fragment = found
    new = section_target(
        target, unquote(fragment[1:]), sections, anchors, installed_links
    )
    if new is None:
        return None
    page, mark, _ = new.partition("#")
    folder = posixpath.dirname(src) or "."
    return posixpath.relpath(page, folder) + query + (fragment if mark else "")


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
    UnmappedAnchor for a link to a section that the map lacks, and
    AmbiguousLink, before any edit, for a link to a mapped file that the
    scanner cannot tell safely: one in a multiline code span, behind a
    nested bracket in its label, in a reference definition split over two
    lines, or without its closing parenthesis.
    """
    spans, doubts = _link_scan(text)
    _refuse_doubts(text, src, doubts, sections)
    edits: list[tuple[int, int, str, str]] = []
    for begin, end in spans:
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
