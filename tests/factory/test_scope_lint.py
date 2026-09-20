"""Tests for scope-lint — governed artifact scope declaration validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import load_script

scope_lint = load_script("scope-lint")


def _setup_workstream(base: Path, ws_id: str = "test-workstream") -> None:
    ws_dir = base / ".agent-factory" / "workstreams"
    ws_dir.mkdir(parents=True, exist_ok=True)
    (ws_dir / f"{ws_id}.yaml").write_text(
        f"schema_version: 2\nworkstream_id: {ws_id}\ntopic: Test\norigin_ref: null\n"
    )


def _write_proposal(base: Path, name: str, frontmatter: str) -> Path:
    d = base / "docs" / "proposals"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{name}.md"
    p.write_text(f"---\n{frontmatter}---\n\n# {name}\n")
    return p


def _write_feature(base: Path, name: str, first_line: str = "") -> Path:
    d = base / "docs" / "spec"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{name}.feature"
    content = f"{first_line}\nFeature: {name}\n" if first_line else f"Feature: {name}\n"
    p.write_text(content)
    return p


def _write_dsl(base: Path, first_line: str = "") -> Path:
    d = base / "docs" / "arc42"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "architecture.dsl"
    content = f"{first_line}\nworkspace {{}}\n" if first_line else "workspace {}\n"
    p.write_text(content)
    return p


def _write_entity_model_md(base: Path, frontmatter: str = "") -> Path:
    d = base / "docs" / "spec" / "supplementary_specs"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "entity-model.md"
    if frontmatter:
        p.write_text(f"---\n{frontmatter}---\n\n# Entity Model\n")
    else:
        p.write_text("# Entity Model\n")
    return p


def _write_entity_model_yaml(base: Path, content: str) -> Path:
    d = base / "docs" / "spec" / "supplementary_specs"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "entity-model.yaml"
    p.write_text(content)
    return p


def _write_scope_map(base: Path, frontmatter: str = "") -> Path:
    d = base / "docs" / "spec"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "scope-map.md"
    if frontmatter:
        p.write_text(f"---\n{frontmatter}---\n\n# Scope Map\n")
    else:
        p.write_text("# Scope Map\n")
    return p


def _write_epic(base: Path, name: str, frontmatter: str) -> Path:
    d = base / "backlog"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"epics-{name}.md"
    p.write_text(f"---\n{frontmatter}---\n\n# {name}\n")
    return p


def _write_story(base: Path, story_id: str, frontmatter: str) -> Path:
    d = base / "backlog"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{story_id}.md"
    p.write_text(f"---\n{frontmatter}---\n\n# Story\n")
    return p


class TestProposalScope:
    def test_valid_workstream_scope(self, tmp_path: Path) -> None:
        _setup_workstream(tmp_path, "my-ws")
        _write_proposal(tmp_path, "my-proposal", "scope: my-ws\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0

    def test_global_scope(self, tmp_path: Path) -> None:
        _write_proposal(tmp_path, "global-proposal", "scope: global\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0

    def test_missing_scope(self, tmp_path: Path) -> None:
        _write_proposal(tmp_path, "no-scope", "title: No Scope\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 1
        assert findings[0].error_type == "missing"
        assert "missing scope declaration" in findings[0].detail

    def test_unknown_scope_value(self, tmp_path: Path) -> None:
        _write_proposal(tmp_path, "bad-scope", "scope: nonexistent-ws\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 1
        assert findings[0].error_type == "unknown"
        assert "nonexistent-ws" in findings[0].detail


class TestFeatureFileScope:
    def test_valid_first_line_scope(self, tmp_path: Path) -> None:
        _setup_workstream(tmp_path, "feat-ws")
        _write_feature(tmp_path, "my-feature", "# scope: feat-ws")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0

    def test_missing_first_line_scope(self, tmp_path: Path) -> None:
        _write_feature(tmp_path, "no-scope-feature")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 1
        assert findings[0].error_type == "missing"
        assert "first-line comment" in findings[0].detail


class TestDslScope:
    def test_valid_dsl_scope(self, tmp_path: Path) -> None:
        _write_dsl(tmp_path, "// scope: global")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0

    def test_missing_dsl_scope(self, tmp_path: Path) -> None:
        _write_dsl(tmp_path)
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 1
        assert findings[0].error_type == "missing"


class TestEntityModelScope:
    def test_md_with_frontmatter_scope(self, tmp_path: Path) -> None:
        _write_entity_model_md(tmp_path, "scope: global\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0

    def test_md_missing_scope(self, tmp_path: Path) -> None:
        _write_entity_model_md(tmp_path)
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 1
        assert findings[0].error_type == "missing"

    def test_yaml_with_top_level_scope(self, tmp_path: Path) -> None:
        _write_entity_model_yaml(tmp_path, "scope: global\nentities:\n  - name: Foo\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0


class TestScopeMapScope:
    def test_valid_scope(self, tmp_path: Path) -> None:
        _write_scope_map(tmp_path, "scope: global\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0

    def test_missing_scope(self, tmp_path: Path) -> None:
        _write_scope_map(tmp_path)
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 1
        assert findings[0].error_type == "missing"


class TestEpicAndStoryScope:
    def test_epic_valid_scope(self, tmp_path: Path) -> None:
        _setup_workstream(tmp_path, "ws-1")
        _write_epic(tmp_path, "ws-1", "scope: ws-1\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0

    def test_story_valid_scope(self, tmp_path: Path) -> None:
        _setup_workstream(tmp_path, "ws-2")
        _write_story(tmp_path, "ST-0001", "id: ST-0001\nscope: ws-2\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0

    def test_story_missing_scope(self, tmp_path: Path) -> None:
        _write_story(tmp_path, "ST-0002", "id: ST-0002\ntier: standard\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 1
        assert findings[0].error_type == "missing"


class TestNonGovernedArtifacts:
    def test_adr_is_skipped(self, tmp_path: Path) -> None:
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-0001.md").write_text("# ADR 0001\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0

    def test_convention_is_skipped(self, tmp_path: Path) -> None:
        conv_dir = tmp_path / "docs" / "conventions"
        conv_dir.mkdir(parents=True)
        (conv_dir / "naming.md").write_text("# Naming\n")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 0


class TestMultipleErrors:
    def test_exit_code_equals_error_count(self, tmp_path: Path) -> None:
        _write_proposal(tmp_path, "p1", "title: No Scope 1\n")
        _write_proposal(tmp_path, "p2", "title: No Scope 2\n")
        _write_feature(tmp_path, "f1")
        findings = scope_lint.validate_scope(tmp_path)
        assert len(findings) == 3
        exit_code = scope_lint.main(["--base-dir", str(tmp_path)])
        assert exit_code == 3


class TestMainCli:
    def test_text_output(self, tmp_path: Path, capsys) -> None:
        _setup_workstream(tmp_path, "ws")
        _write_proposal(tmp_path, "ok", "scope: ws\n")
        code = scope_lint.main(["--base-dir", str(tmp_path)])
        assert code == 0
        out = capsys.readouterr().out
        assert "all governed artifacts pass" in out

    def test_json_output(self, tmp_path: Path, capsys) -> None:
        _write_proposal(tmp_path, "bad", "title: oops\n")
        code = scope_lint.main(["--base-dir", str(tmp_path), "--format", "json"])
        assert code == 1
        data = json.loads(capsys.readouterr().out)
        assert data["errors"] == 1
        assert len(data["findings"]) == 1


import json
