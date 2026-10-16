#!/usr/bin/env python3
"""_docs_assemble — turn a project's published documents into a Quarkdown build.

What: Reads docs/publish-docs.yaml, rewrites each listed document for
      Quarkdown and writes main.qd, the Mermaid bodies, the images and
      expected.json into a build directory. The sources stay unchanged.
When: Stages 0, 2 and 3 of `publish-docs pdf`.
By:   run by the publish-docs script inside the render image; not run by
      hand.

Exit codes: 0 when the build directory is written, 2 when the manifest is
missing or names a file that does not exist. A missing manifest prints a
starter manifest to standard output.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

MANIFEST_NAME = "publish-docs.yaml"
PROJECT_CSS_NAME = "publish-docs.css"
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg"}

FENCE_RE = re.compile(r"^(```|~~~)[^\n]*\n.*?^\1[ \t]*$\n?", re.S | re.M)
MERMAID_RE = re.compile(r"^```mermaid[ \t]*\n(.*?)^```[ \t]*$\n?", re.S | re.M)
CODE_SPAN_RE = re.compile(r"(`+)(?:(?!\1).)+?\1")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---[ \t]*\n", re.S)
BACK_TO_INDEX_RE = re.compile(r"^\[back to index\]\([^)]*\)[ \t]*\n?", re.M | re.I)
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$", re.M)


class ManifestError(Exception):
    """The manifest is missing, malformed, or names a missing document."""


@dataclass
class Manifest:
    title: str
    chapters: list[Path]
    appendix_title: str | None = None
    appendix: list[Path] = field(default_factory=list)


@dataclass
class Provenance:
    sha: str
    branch: str
    built_at: str
    dirty: bool

    def line(self) -> str:
        changes = " with uncommitted changes in docs/" if self.dirty else ""
        return (
            f"Built from `{self.sha}` (branch `{self.branch}`){changes}, "
            f"{self.built_at} UTC"
        )


# --- manifest ---------------------------------------------------------------


def _expand(docs: Path, entry: str) -> list[Path]:
    if any(ch in entry for ch in "*?["):
        matches = sorted(p for p in docs.glob(entry) if p.is_file())
        if not matches:
            raise ManifestError(f"manifest entry matches no file: {entry}")
        return matches
    path = docs / entry
    if not path.is_file():
        raise ManifestError(f"manifest names a missing file: {entry}")
    return [path]


def load_manifest(docs: Path) -> Manifest:
    """Read and expand docs/publish-docs.yaml."""
    import yaml

    path = docs / MANIFEST_NAME
    if not path.is_file():
        raise ManifestError(f"missing manifest: docs/{MANIFEST_NAME}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or not data.get("title") or not data.get("chapters"):
        raise ManifestError("manifest needs a 'title' and a non-empty 'chapters' list")
    chapters = [p for entry in data["chapters"] for p in _expand(docs, str(entry))]
    appendix = data.get("appendix") or {}
    documents = [p for entry in appendix.get("documents") or [] for p in _expand(docs, str(entry))]
    if documents and not appendix.get("title"):
        raise ManifestError("manifest appendix needs a 'title'")
    for doc in chapters + documents:
        heads = HEADING_RE.findall(_mask_code(FRONTMATTER_RE.sub("", doc.read_text(encoding="utf-8"), count=1))[0])
        if not heads or len(heads[0][0]) != 1:
            rel = doc.relative_to(docs).as_posix()
            raise ManifestError(f"document does not start with a top-level '# ' heading: {rel}")
    return Manifest(
        title=str(data["title"]),
        chapters=chapters,
        appendix_title=appendix.get("title") if documents else None,
        appendix=documents,
    )


def starter_manifest(docs: Path, project: str) -> str:
    """Return a starter manifest built from the arc42 and ADR conventions."""
    chapters = sorted(p.relative_to(docs).as_posix() for p in docs.glob("arc42/[0-9][0-9]_*.md"))
    lines = [
        "---",
        f"# Save as docs/{MANIFEST_NAME}. Add documents outside these folders by path.",
        f"# Optional: docs/{PROJECT_CSS_NAME} overrides the default PDF style.",
        f"title: {project} — Architecture",
        "chapters:",
        *(f"  - {c}" for c in chapters),
    ]
    if not chapters:
        lines.append("  - arc42/01_introduction_and_goals.md")
    if any(docs.glob("adr/*.md")):
        lines += ["appendix:", "  title: Architecture decisions", "  documents:", "    - adr/*.md"]
    return "\n".join(lines) + "\n"


# --- slugs ------------------------------------------------------------------


def quarkdown_slug(text: str) -> str:
    """Heading id as Quarkdown derives it: GitHub's rule, `_` before a leading digit.

    "6.1 Approval flow" becomes "_61-approval-flow". The dead-anchor render
    check catches any heading where the two schemes differ.
    """
    slug = github_slug(text)
    return "_" + slug if slug[:1].isdigit() else slug


def github_slug(text: str) -> str:
    """Heading anchor as GitHub derives it, used to read source fragments."""
    slug = re.sub(r"[^\w\- ]", "", _plain(text).lower())
    return slug.replace(" ", "-")


def _plain(text: str) -> str:
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[`*_]", "", text)


def headings(text: str) -> list[str]:
    text = FRONTMATTER_RE.sub("", text, count=1)
    return [m.group(2) for m in HEADING_RE.finditer(_mask_code(text)[0])]


# --- rewriting --------------------------------------------------------------


def _mask_code(text: str) -> tuple[str, list[str]]:
    """Replace fenced blocks and code spans with placeholders."""
    saved: list[str] = []

    def keep(m: re.Match) -> str:
        saved.append(m.group(0))
        return f"\x00{len(saved) - 1}\x00"

    return CODE_SPAN_RE.sub(keep, FENCE_RE.sub(keep, text)), saved


def _unmask(text: str, saved: list[str]) -> str:
    return re.sub(r"\x00(\d+)\x00", lambda m: saved[int(m.group(1))], text)


@dataclass
class Build:
    docs: Path
    out: Path
    views: Path | None
    targets: dict[Path, str] = field(default_factory=dict)  # doc -> first heading id
    fragments: dict[Path, dict[str, str]] = field(default_factory=dict)  # doc -> github -> qd
    mermaid: int = 0
    raster: int = 0

    def index(self, paths: list[Path]) -> None:
        for path in paths:
            heads = headings(path.read_text(encoding="utf-8"))
            key = path.resolve()
            self.targets[key] = quarkdown_slug(heads[0]) if heads else ""
            self.fragments[key] = {github_slug(h): quarkdown_slug(h) for h in heads}

    def rewrite(self, path: Path, demote: bool = False) -> str:
        text = path.read_text(encoding="utf-8")
        status = None
        fm = FRONTMATTER_RE.match(text)
        if fm:
            found = re.search(r"^status:[ \t]*(.+?)[ \t]*$", fm.group(1), re.M)
            status = found.group(1).strip("'\"") if found else None
            text = text[fm.end():]
        text = BACK_TO_INDEX_RE.sub("", text)
        text = MERMAID_RE.sub(self._mermaid, text)
        body, saved = _mask_code(text)
        body = IMAGE_RE.sub(lambda m: self._image(path, m), body)
        body = LINK_RE.sub(lambda m: self._link(path, m), body)
        if status:
            body = HEADING_RE.sub(lambda m: f"{m.group(0)}\n\n**Status:** {status}", body, count=1)
        if demote:
            body = HEADING_RE.sub(
                lambda m: f"{'#' * min(len(m.group(1)) + 1, 6)} {m.group(2)}", body
            )
        return _unmask(body, saved)

    def _mermaid(self, m: re.Match) -> str:
        self.mermaid += 1
        name = f"d{self.mermaid}.mmd"
        (self.out / name).write_text(m.group(1), encoding="utf-8")
        return f".mermaid\n    .read {{{name}}}\n"

    def _image(self, path: Path, m: re.Match) -> str:
        alt, target = m.group(1), m.group(2)
        if target.startswith(("http://", "https://", "data:")):
            return m.group(0)
        src = (path.parent / target).resolve()
        fresh = self.views / src.name if self.views else None
        if fresh is not None and fresh.is_file():
            src = fresh
        if not src.is_file():
            return m.group(0)  # left for the render check to report
        dest = self.out / "images" / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        if src.suffix.lower() in RASTER_SUFFIXES:
            self.raster += 1
        return f"![{alt}](images/{src.name})"

    def _link(self, path: Path, m: re.Match) -> str:
        label, target = m.group(1), m.group(2)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        file_part, _, fragment = target.partition("#")
        dest = (path.parent / file_part).resolve()
        if dest in self.targets:
            anchor = self.fragments[dest].get(fragment, fragment) if fragment else self.targets[dest]
            return f"[{label}](#{anchor})"
        if dest.suffix.lower() == ".md":
            return label
        already_code = re.fullmatch(r"\x00\d+\x00", label)  # masked code span
        return label if already_code else f"`{label}`"


def assemble(docs: Path, out: Path, views: Path | None, provenance: Provenance, factory_css: Path | None) -> dict:
    """Write the build directory; return the expected counts."""
    manifest = load_manifest(docs)
    out.mkdir(parents=True, exist_ok=True)
    build = Build(docs=docs, out=out, views=views)
    build.index(manifest.chapters + manifest.appendix)

    parts = [
        f".docname {{{manifest.title}}}",
        ".doctype {paged}",
        ".numbering\n    - headings: none\n    - figures: none\n    - tables: none",
        "",
    ]
    for css, name in ((factory_css, "publish.css"), (docs / PROJECT_CSS_NAME, "project.css")):
        if css is not None and css.is_file():
            shutil.copyfile(css, out / name)
            parts += [f".css {{.read {{{name}}}}}", ""]
    parts += [
        f".container classname:{{title-page}}\n    .text {{{manifest.title}}} size:{{huge}}\n\n    {provenance.line()}",
        "",
        ".tableofcontents",  # its heading starts a new page
        "",
    ]
    parts += [build.rewrite(p) for p in manifest.chapters]
    if manifest.appendix:
        parts += [f"# {manifest.appendix_title}", ""]
        parts += [build.rewrite(p, demote=True) for p in manifest.appendix]
    (out / "main.qd").write_text("\n".join(parts), encoding="utf-8")
    expected = {"mermaid": build.mermaid, "raster": build.raster}
    (out / "expected.json").write_text(json.dumps(expected) + "\n", encoding="utf-8")
    return expected


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--docs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--views", type=Path, help="directory with freshly exported Structurizr SVGs")
    ap.add_argument("--factory-css", type=Path)
    ap.add_argument("--project", default="project")
    ap.add_argument("--sha", required=True)
    ap.add_argument("--branch", required=True)
    ap.add_argument("--built-at", required=True)
    ap.add_argument("--dirty", action="store_true")
    args = ap.parse_args(argv)
    try:
        expected = assemble(
            args.docs,
            args.out,
            args.views,
            Provenance(args.sha, args.branch, args.built_at, args.dirty),
            args.factory_css,
        )
    except ManifestError as exc:
        print(f"publish-docs: {exc}", file=sys.stderr)
        if not (args.docs / MANIFEST_NAME).is_file():
            print(starter_manifest(args.docs, args.project))
        return 2
    print(f"assembled: {expected['mermaid']} Mermaid diagrams, {expected['raster']} raster images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
