"""End-to-end tests for `publish-docs pdf` on a generated fixture project (ST-0311).

The fixture is written at run time: its Markdown holds dead repository links
on purpose, which the repository's own link-check would reject as files. It
is written in the old layout, committed, and then migrated with
`migrate-spec-layout`, as a project maintainer would (ST-0334).
"""

from __future__ import annotations

import hashlib
import os
import re
import struct
import subprocess
import zlib
from pathlib import Path

import pytest
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, requires_docker

pytestmark = [requires_docker, pytest.mark.container]

SCRIPT = SOURCE_SCRIPTS_DIR / "publish-docs"
MIGRATE = SOURCE_SCRIPTS_DIR / "migrate-spec-layout"
DOCKERFILE = REPO_ROOT / "packages/factory/docker/publish-docs/Dockerfile"
IMAGE = "agent-factory/publish-docs:" + hashlib.sha256(DOCKERFILE.read_bytes()).hexdigest()[:12]

FIXTURE = {
    "publish-docs.yaml": """\
---
title: Demo — Architecture
chapters:
  - arc42/0*.md
  - arc42/12_glossary.md
  - spec/entity-model.md
appendix:
  title: Architecture decisions
  documents:
    - adr/*.md
""",
    "arc42/architecture.dsl": """\
workspace "Demo" "Fixture for the publish-docs end-to-end test." {
    !identifiers hierarchical
    properties {
        "arc42.projected" "false"
    }
    model {
        user = person "Reader" "Reads the published architecture."
        demo = softwareSystem "Demo" {
            web = container "Web" "Serves pages." "Python"
            db = container "Database" "Stores records." "PostgreSQL"
        }
        user -> demo.web "Uses"
        demo.web -> demo.db "Reads and writes"
    }
    views {
        container demo "Containers" {
            include *
            autolayout lr
        }
        theme themes/demo.json
    }
}
""",
    "arc42/themes/demo.json": """\
{
  "name": "Demo",
  "elements": [{ "tag": "Person", "shape": "Person" }]
}
""",
    "arc42/01_introduction.md": """\
[back to index](../README.md)

# 1. Introduction

The [building blocks](05_building_blocks.md) and the
[approval flow](06_runtime.md#61-approval-flow) explain the system. The
[project README](../README.md) is not published. The web container lives in
[the web module](../../src/web/app.py), and the model in
[`architecture.dsl`](architecture.dsl).

| Goal     | Measure        |
| -------- | -------------- |
| Readable | One PDF        |
| Current  | Fresh diagrams |
""",
    "arc42/05_building_blocks.md": """\
[back to index](../README.md)

# 5. Building Blocks

![Containers](../assets/images/Containers.svg)

![Rack](../assets/images/rack.png)

Records follow the [entity model](../spec/entity-model.md).
""",
    "arc42/06_runtime.md": """\
[back to index](../README.md)

# 6. Runtime

## 6.1 Approval flow

```mermaid
sequenceDiagram
    participant E as Editor
    participant W as Web
    E->>W: Submit for approval
    W-->>E: Accepted
```
""",
    "arc42/12_glossary.md": """\
# 12. Glossary

| Term         | Definition                           |
| ------------ | ------------------------------------ |
| Ledger Entry | One booked line of the demo records. |
""",
    "spec/entity-model.md": """\
---
scope: fixture
---

# Entity model

```mermaid
erDiagram
    TEAM ||--o{ RECORD : owns
    TEAM {
        int id PK
        string name
    }
    RECORD {
        int id PK
        int team_id FK
    }
```
""",
    "adr/0001-use-quarkdown.md": """\
---
id: 0001
status: accepted
evaluation: none
---

# Use Quarkdown for the PDF

## Context

The documentation needs a paged PDF.

## Decision

Quarkdown renders the documentation reliably.
""",
    "adr/0002-split-the-appendix.md": """\
---
id: 0002
status: proposed
---

# Start each decision on its own page

## Decision

Every appendix document begins on a new page.
""",
    "assets/images/Containers.svg": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="40">'
        '<text x="5" y="25">STALE-COMMITTED-SVG</text></svg>\n'
    ),
}


def _png(width: int = 160, height: int = 90) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    rows = b"".join(b"\x00" + b"\x78\x8c\xa0" * width for _ in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


def _env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True, env=_env()).stdout.strip()


def make_project(base: Path, name: str = "demo", edits: dict[str, str] | None = None) -> Path:
    root = base / name
    docs = root / "docs"
    for rel, text in {**FIXTURE, **(edits or {})}.items():
        path = docs / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (docs / "assets/images/rack.png").write_bytes(_png())
    _git(root.parent, "init", "-q", "-b", "main", str(root))
    _commit(root, "fixture")
    subprocess.run([str(MIGRATE), str(root)], capture_output=True, text=True, check=True, env=_env())
    _commit(root, "migrate")
    return root


def _commit(root: Path, message: str) -> None:
    _git(root, "add", "-A")
    _git(root, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-q", "-m", message)


def publish(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([str(SCRIPT), "pdf"], cwd=root, capture_output=True, text=True, env=_env(), timeout=900)


def poppler(root: Path, *args: str) -> str:
    """Run a poppler tool from the render image on a file under root."""
    cmd = ["docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}", "-v", f"{root}:/w", "-w", "/w", "--entrypoint", args[0], IMAGE, *args[1:]]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def pdf_text(root: Path, pdf: str, *pages: int) -> str:
    extra = ["-f", str(pages[0]), "-l", str(pages[-1])] if pages else []
    return poppler(root, "pdftotext", "-layout", *extra, pdf, "-")


def word_height(root: Path, pdf: str, word: str) -> float:
    xml = poppler(root, "pdftotext", "-bbox", pdf, "-")
    m = re.search(rf'<word xMin="[\d.]+" yMin="([\d.]+)" xMax="[\d.]+" yMax="([\d.]+)">{word}[.,]?</word>', xml)
    assert m, f"word {word!r} not found in the PDF"
    return float(m.group(2)) - float(m.group(1))


PDF = "docs/dist/demo-architecture.pdf"


@pytest.fixture(scope="module")
def published(tmp_path_factory: pytest.TempPathFactory):
    root = make_project(tmp_path_factory.mktemp("good"))
    result = publish(root)
    assert result.returncode == 0, result.stderr
    return root, result


class TestPublishedPdf:
    def test_writes_pdf_to_docs_dist(self, published):
        root, result = published
        assert (root / PDF).is_file()
        assert "wrote docs/dist/demo-architecture.pdf" in result.stdout

    def test_diagrams_are_vector_and_no_mermaid_source_remains(self, published):
        root, _ = published
        rows = poppler(root, "pdfimages", "-list", PDF).splitlines()[2:]
        assert [r.split()[2] for r in rows].count("image") == 1  # the rack PNG
        text = pdf_text(root, PDF)
        for source in ("sequenceDiagram", "erDiagram", "participant E"):
            assert source not in text

    def test_structurizr_view_comes_from_this_run(self, published):
        root, _ = published
        text = pdf_text(root, PDF)
        assert "STALE-COMMITTED-SVG" not in text
        assert "Database" in text

    def test_contents_follow_manifest_order(self, published):
        root, _ = published
        text = pdf_text(root, PDF, 2, 3)
        order = ["1. Introduction", "5. Building Blocks", "6. Runtime", "Entity model", "Architecture decisions", "Use Quarkdown for the PDF"]
        positions = [text.index(entry) for entry in order]
        assert positions == sorted(positions)

    def test_appendix_title_and_each_adr_start_a_page(self, published):
        root, _ = published
        pages = int(re.search(r"Pages:\s+(\d+)", poppler(root, "pdfinfo", PDF)).group(1))
        tops = [pdf_text(root, PDF, n).strip().splitlines()[0].strip() for n in range(4, pages + 1)]
        for title in ("Architecture decisions", "Use Quarkdown for the PDF", "Start each decision on its own page"):
            assert title in tops, f"{title!r} does not open a page: {tops}"
        divider = tops.index("Architecture decisions")
        assert tops[divider + 1] == "Use Quarkdown for the PDF"

    def test_no_repository_path_is_a_link(self, published):
        root, _ = published
        html = next((root / ".current-work/publish-docs/build/html").rglob("index.html")).read_text()
        assert not re.findall(r'href="(?!#)[^"]*"', re.sub(r"<(link|script)[^>]*>", "", html))
        assert re.search(r"<code>the web module</code>", html)
        assert "project README is not published" in re.sub(r"<[^>]+>|\s+", " ", html).replace("  ", " ")

    def test_navigation_and_frontmatter_removed_and_status_kept(self, published):
        root, _ = published
        text = pdf_text(root, PDF)
        assert "back to index" not in text
        assert "evaluation:" not in text and "scope: fixture" not in text
        assert re.search(r"Status:\s+accepted", text)

    def test_title_page_names_commit_branch_and_time(self, published):
        root, _ = published
        first = re.sub(r"\s+", "", pdf_text(root, PDF, 1))
        assert _git(root, "rev-parse", "HEAD") in first
        assert "(branchmain)" in first
        assert "uncommittedchanges" not in first
        assert re.search(r"\d{4}-\d{2}-\d{2}\d{2}:\d{2}UTC", first)

    def test_sources_unchanged_and_output_ignored(self, published):
        root, _ = published
        assert _git(root, "status", "--porcelain", "--", "docs") == ""
        assert "docs/dist/" in (root / ".gitignore").read_text()

    def test_second_run_gives_same_page_count(self, published):
        root, _ = published
        pages = lambda: re.search(r"Pages:\s+(\d+)", poppler(root, "pdfinfo", PDF)).group(1)
        first = pages()
        assert publish(root).returncode == 0
        assert pages() == first


def test_project_stylesheet_overrides_style_and_marks_dirty_tree(published, tmp_path: Path):
    root, _ = published
    base = word_height(root, PDF, "reliably")
    css = root / "docs/publish-docs.css"
    css.write_text(":root { --qd-main-font-size: 12pt; }\n", encoding="utf-8")
    try:
        result = publish(root)
        assert result.returncode == 0, result.stderr
        assert word_height(root, PDF, "reliably") > base * 1.1
        assert "with uncommitted changes in docs/" in re.sub(r"\s+", " ", pdf_text(root, PDF, 1))
    finally:
        css.unlink()


def test_broken_mermaid_block_stops_the_build(tmp_path: Path):
    broken = FIXTURE["arc42/06_runtime.md"].replace("    E->>W", "    ->>>> not mermaid (((\n    E->>W")
    root = make_project(tmp_path, edits={"arc42/06_runtime.md": broken})
    result = publish(root)
    assert result.returncode == 1
    assert "FAIL mermaid-error" in result.stderr
    assert not (root / PDF).exists()


def test_dead_internal_link_stops_the_build(tmp_path: Path):
    dead = FIXTURE["arc42/01_introduction.md"] + "\nSee [nowhere](#no-such-heading).\n"
    root = make_project(tmp_path, edits={"arc42/01_introduction.md": dead})
    result = publish(root)
    assert result.returncode == 1
    assert "FAIL dead-anchor: #no-such-heading" in result.stderr
    assert not (root / PDF).exists()


def test_missing_manifest_prints_starter(tmp_path: Path):
    root = make_project(tmp_path)
    (root / "docs/publish-docs.yaml").unlink()
    result = publish(root)
    assert result.returncode == 2
    assert "  - arc42/01_introduction.md" in result.stdout
    assert "    - adr/*.md" in result.stdout
    assert not (root / PDF).exists()


def test_invalid_dsl_stops_before_rendering(tmp_path: Path):
    root = make_project(tmp_path, edits={"arc42/architecture.dsl": 'workspace "Broken" {\n    model {\n        a -> b\n    }\n}\n'})
    result = publish(root)
    assert result.returncode == 1
    assert "FAIL structurizr-validate" in result.stderr
    assert not (root / ".current-work/publish-docs/build/src/main.qd").exists()


@pytest.mark.spec("CAL-11-IT-01")
def test_chapter_12_shows_the_glossary_and_manifest_is_unchanged(published):
    root, _ = published
    assert (root / "docs/spec/architecture.dsl").is_file()
    assert (root / "docs/assets/themes/demo.json").is_file()
    assert _git(root, "diff", "HEAD~1", "--", "docs/publish-docs.yaml") == ""
    text = re.sub(r"\s+", " ", pdf_text(root, PDF))
    chapter12 = text[text.rindex("Glossary") :]
    assert "Ledger Entry" in chapter12
    assert "The terms are in" not in text


def test_missing_dsl_names_the_spec_path(tmp_path: Path):
    root = make_project(tmp_path)
    (root / "docs/spec/architecture.dsl").unlink()
    result = publish(root)
    assert result.returncode == 2
    assert "docs/spec/architecture.dsl" in result.stderr
    assert not (root / PDF).exists()
