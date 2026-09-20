"""Tests for scope filtering in the precondition evaluator."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PACKAGES_DIR = Path(__file__).resolve().parents[2] / "packages" / "factory"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.eligibility import _extract_scope, _scope_filter


class TestExtractScope:
    """Test _extract_scope handles all three scope declaration formats."""

    def test_yaml_frontmatter(self, tmp_path):
        p = tmp_path / "story.md"
        p.write_text("---\nid: ST-0001\nscope: my-workstream\n---\n# Title\n")
        assert _extract_scope(p) == "my-workstream"

    def test_yaml_frontmatter_global(self, tmp_path):
        p = tmp_path / "epic.md"
        p.write_text("---\nscope: global\n---\n# Epic\n")
        assert _extract_scope(p) == "global"

    def test_yaml_frontmatter_missing_scope(self, tmp_path):
        p = tmp_path / "story.md"
        p.write_text("---\nid: ST-0001\ntitle: Foo\n---\n# Title\n")
        assert _extract_scope(p) is None

    def test_feature_file_first_line(self, tmp_path):
        p = tmp_path / "test.feature"
        p.write_text("# scope: activity-graph-orchestration\nFeature: Test\n")
        assert _extract_scope(p) == "activity-graph-orchestration"

    def test_feature_file_missing_scope(self, tmp_path):
        p = tmp_path / "test.feature"
        p.write_text("Feature: Test\n  Scenario: foo\n")
        assert _extract_scope(p) is None

    def test_dsl_first_line(self, tmp_path):
        p = tmp_path / "arch.dsl"
        p.write_text('// scope: global\nworkspace "Test" {\n}\n')
        assert _extract_scope(p) == "global"

    def test_dsl_missing_scope(self, tmp_path):
        p = tmp_path / "arch.dsl"
        p.write_text('workspace "Test" {\n}\n')
        assert _extract_scope(p) is None

    def test_top_level_yaml(self, tmp_path):
        p = tmp_path / "entity-model.yaml"
        p.write_text("scope: global\nentities:\n  - Foo\n")
        assert _extract_scope(p) == "global"

    def test_nonexistent_file(self, tmp_path):
        p = tmp_path / "missing.md"
        assert _extract_scope(p) is None

    def test_no_frontmatter_md(self, tmp_path):
        p = tmp_path / "plain.md"
        p.write_text("# Just a heading\n\nSome content.\n")
        assert _extract_scope(p) is None


class TestScopeFilter:
    """Test _scope_filter keeps/removes candidates by workstream scope."""

    def _make_scoped_file(self, tmp_path, name, scope):
        p = tmp_path / name
        p.write_text(f"---\nscope: {scope}\n---\n# {name}\n")
        return str(p)

    def test_open_stage_skips_filtering(self, tmp_path):
        a = self._make_scoped_file(tmp_path, "a.md", "ws-a")
        b = self._make_scoped_file(tmp_path, "b.md", "ws-b")
        result = _scope_filter([a, b], None)
        assert result == [a, b]

    def test_matching_workstream_kept(self, tmp_path):
        a = self._make_scoped_file(tmp_path, "a.md", "ws-a")
        b = self._make_scoped_file(tmp_path, "b.md", "ws-b")
        result = _scope_filter([a, b], "ws-a")
        assert result == [a]

    def test_global_scope_always_passes(self, tmp_path):
        a = self._make_scoped_file(tmp_path, "a.md", "global")
        b = self._make_scoped_file(tmp_path, "b.md", "ws-b")
        result = _scope_filter([a, b], "ws-a")
        assert result == [a]

    def test_no_scope_passes_through(self, tmp_path):
        p = tmp_path / "no-scope.md"
        p.write_text("---\nid: foo\n---\n# No scope\n")
        result = _scope_filter([str(p)], "ws-a")
        assert result == [str(p)]

    def test_different_workstream_excluded(self, tmp_path):
        a = self._make_scoped_file(tmp_path, "a.md", "ws-other")
        result = _scope_filter([a], "ws-mine")
        assert result == []

    def test_feature_file_scope_filtering(self, tmp_path):
        f1 = tmp_path / "a.feature"
        f1.write_text("# scope: ws-a\nFeature: A\n")
        f2 = tmp_path / "b.feature"
        f2.write_text("# scope: ws-b\nFeature: B\n")
        result = _scope_filter([str(f1), str(f2)], "ws-a")
        assert result == [str(f1)]

    def test_mixed_formats(self, tmp_path):
        md = self._make_scoped_file(tmp_path, "story.md", "ws-a")
        feat = tmp_path / "test.feature"
        feat.write_text("# scope: ws-a\nFeature: Test\n")
        dsl = tmp_path / "arch.dsl"
        dsl.write_text("// scope: global\nworkspace {}\n")
        other = self._make_scoped_file(tmp_path, "other.md", "ws-b")
        result = _scope_filter([md, str(feat), str(dsl), other], "ws-a")
        assert result == [md, str(feat), str(dsl)]
