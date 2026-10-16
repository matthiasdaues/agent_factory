"""Contract tests for the publish-docs assembly step (ST-0309)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import load_script

da = load_script("_docs_assemble.py")

PROV = da.Provenance("a" * 40, "main", "2026-10-16 10:00", False)


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def docs(tmp_path: Path) -> Path:
    d = tmp_path / "docs"
    write(
        d,
        "arc42/01_intro.md",
        "[back to index](../README.md)\n\n# 1. Introduction\n\n"
        "See [the runtime](06_runtime.md), [lookup](06_runtime.md#62-public-lookup),"
        " [the index](../README.md), [the model](../../backend/app/models/team.py)"
        " and [`team.py`](../../backend/team.py).\n\n"
        "```python\nx = '[kept](../a.md)'\n```\n\nInline `[kept](b.md)` too.\n",
    )
    write(
        d,
        "arc42/06_runtime.md",
        "# 6. Runtime\n\n## 6.2 Public lookup\n\n```mermaid\nerDiagram\n    TEAM {\n        int id PK\n    }\n```\n\n"
        "![Containers](../assets/images/Containers.svg)\n\n![Photo](../assets/images/rack.png)\n",
    )
    write(d, "assets/images/Containers.svg", "<svg>stale</svg>")
    write(d, "assets/images/rack.png", "png")
    write(d, "adr/0001-first.md", "---\nid: 0001\nstatus: accepted\n---\n\n# First decision\n\n## Context\n\nText.\n")
    write(
        d,
        "publish-docs.yaml",
        "---\ntitle: Demo — Architecture\nchapters:\n  - arc42/0*.md\n"
        "appendix:\n  title: Architecture decisions\n  documents:\n    - adr/*.md\n",
    )
    return d


def build(docs: Path, tmp_path: Path, views: Path | None = None, prov=PROV) -> tuple[str, dict, Path]:
    out = tmp_path / "build"
    expected = da.assemble(docs, out, views, prov, None)
    return (out / "main.qd").read_text(encoding="utf-8"), expected, out


class TestManifest:
    def test_glob_entries_expand_in_sorted_order(self, docs: Path):
        m = da.load_manifest(docs)
        assert [p.name for p in m.chapters] == ["01_intro.md", "06_runtime.md"]
        assert m.appendix_title == "Architecture decisions"

    def test_missing_manifest_raises(self, docs: Path):
        (docs / "publish-docs.yaml").unlink()
        with pytest.raises(da.ManifestError, match="missing manifest"):
            da.load_manifest(docs)

    def test_missing_file_raises(self, docs: Path):
        write(docs, "publish-docs.yaml", "title: T\nchapters:\n  - arc42/99_none.md\n")
        with pytest.raises(da.ManifestError, match="missing file: arc42/99_none.md"):
            da.load_manifest(docs)

    def test_empty_glob_raises(self, docs: Path):
        write(docs, "publish-docs.yaml", "title: T\nchapters:\n  - spec/*.md\n")
        with pytest.raises(da.ManifestError, match="matches no file"):
            da.load_manifest(docs)

    def test_document_without_top_level_heading_raises(self, docs: Path):
        write(docs, "arc42/07_deploy.md", "[back to index](../README.md)\n\n## 7.1 Topology\n")
        with pytest.raises(da.ManifestError, match="top-level.*arc42/07_deploy.md"):
            da.load_manifest(docs)

    def test_missing_manifest_exits_2_and_prints_starter(self, docs: Path, tmp_path: Path, capsys):
        (docs / "publish-docs.yaml").unlink()
        code = da.main(["--docs", str(docs), "--out", str(tmp_path / "b"), "--sha", "s", "--branch", "b", "--built-at", "t", "--project", "demo"])
        out = capsys.readouterr().out
        assert code == 2
        assert "  - arc42/01_intro.md\n  - arc42/06_runtime.md\n" in out
        assert "    - adr/*.md" in out
        assert "publish-docs.css" in out
        assert not (tmp_path / "b" / "main.qd").exists()


class TestRewriteRules:
    def test_mermaid_body_goes_to_file_unchanged(self, docs: Path, tmp_path: Path):
        qd, expected, out = build(docs, tmp_path)
        assert ".mermaid\n    .read {d1.mmd}\n" in qd
        assert "```mermaid" not in qd
        assert (out / "d1.mmd").read_text() == "erDiagram\n    TEAM {\n        int id PK\n    }\n"
        assert expected["mermaid"] == 1

    def test_link_to_manifest_document_becomes_anchor(self, docs: Path, tmp_path: Path):
        qd, _, _ = build(docs, tmp_path)
        assert "[the runtime](#_6-runtime)" in qd

    def test_github_fragment_becomes_quarkdown_id(self, docs: Path, tmp_path: Path):
        qd, _, _ = build(docs, tmp_path)
        assert "[lookup](#_6-2-public-lookup)" in qd

    def test_link_to_markdown_outside_manifest_becomes_plain_text(self, docs: Path, tmp_path: Path):
        qd, _, _ = build(docs, tmp_path)
        assert " the index, " in qd

    def test_link_to_source_file_becomes_inline_code(self, docs: Path, tmp_path: Path):
        qd, _, _ = build(docs, tmp_path)
        assert "`the model`" in qd
        assert " and `team.py`." in qd
        assert "../../backend" not in qd.split("```python")[0]

    def test_code_is_not_rewritten(self, docs: Path, tmp_path: Path):
        qd, _, _ = build(docs, tmp_path)
        assert "x = '[kept](../a.md)'" in qd
        assert "`[kept](b.md)`" in qd

    def test_back_to_index_and_frontmatter_removed(self, docs: Path, tmp_path: Path):
        qd, _, _ = build(docs, tmp_path)
        assert "back to index" not in qd
        assert "id: 0001" not in qd

    def test_adr_keeps_status_and_moves_under_appendix(self, docs: Path, tmp_path: Path):
        qd, _, _ = build(docs, tmp_path)
        assert "# Architecture decisions\n" in qd
        assert "## First decision\n\n**Status:** accepted" in qd
        assert "### Context" in qd

    def test_fresh_view_replaces_committed_svg(self, docs: Path, tmp_path: Path):
        views = write(tmp_path, "views/Containers.svg", "<svg>fresh</svg>").parent
        qd, _, out = build(docs, tmp_path, views)
        assert "![Containers](images/Containers.svg)" in qd
        assert (out / "images" / "Containers.svg").read_text() == "<svg>fresh</svg>"
        assert (docs / "assets/images/Containers.svg").read_text() == "<svg>stale</svg>"

    def test_raster_images_are_counted(self, docs: Path, tmp_path: Path):
        _, expected, out = build(docs, tmp_path)
        assert expected["raster"] == 1
        assert json.loads((out / "expected.json").read_text()) == {"mermaid": 1, "raster": 1}


class TestDocument:
    def test_numbering_off_and_toc_after_title_page(self, docs: Path, tmp_path: Path):
        qd, _, _ = build(docs, tmp_path)
        assert "- headings: none" in qd and "- tables: none" in qd
        assert qd.index("Built from") < qd.index(".tableofcontents")
        assert ".pagebreak" not in qd

    def test_provenance_line_clean_tree(self, docs: Path, tmp_path: Path):
        qd, _, _ = build(docs, tmp_path)
        assert f"Built from `{'a' * 40}` (branch `main`), 2026-10-16 10:00 UTC" in qd

    def test_provenance_line_marks_uncommitted_changes(self, docs: Path, tmp_path: Path):
        dirty = da.Provenance("b" * 40, "dev", "2026-10-16 11:00", True)
        qd, _, _ = build(docs, tmp_path, prov=dirty)
        assert "(branch `dev`) with uncommitted changes in docs/, 2026-10-16 11:00 UTC" in qd

    def test_project_stylesheet_loads_after_factory_default(self, docs: Path, tmp_path: Path):
        factory_css = write(tmp_path, "publish.css", "body{}")
        write(docs, "publish-docs.css", ":root{--qd-main-font-size:12pt}")
        out = tmp_path / "build"
        da.assemble(docs, out, None, PROV, factory_css)
        qd = (out / "main.qd").read_text()
        assert qd.index(".read {publish.css}") < qd.index(".read {project.css}")

    def test_sources_stay_unchanged(self, docs: Path, tmp_path: Path):
        before = {p: p.read_bytes() for p in docs.rglob("*") if p.is_file()}
        build(docs, tmp_path)
        assert before == {p: p.read_bytes() for p in docs.rglob("*") if p.is_file()}


@pytest.mark.parametrize(
    ("heading", "slug"),
    [("5. Building Block View", "_5-building-block-view"), ("Alembic owns schema evolution", "alembic-owns-schema-evolution"), ("6.2 `Public` lookup", "_6-2-public-lookup")],
)
def test_quarkdown_slug(heading: str, slug: str):
    assert da.quarkdown_slug(heading) == slug
