"""Contract tests for fence runner — deterministic output validation."""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest
import yaml

from engine.fence import (
    DeclarationResult,
    FenceResult,
    load_fence_evidence,
    run_fence,
    snapshot_outputs,
    store_evidence,
)


def _agent(declarations, minimum_changed=1, name="test-agent"):
    return {
        "name": name,
        "outputs": {
            "minimum_changed": minimum_changed,
            "declarations": declarations,
        },
    }


class TestSnapshotOutputs:
    def test_captures_mtimes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        d = tmp_path / "docs"
        d.mkdir()
        f = d / "a.md"
        f.write_text("hello")

        agent = _agent([{"path_pattern": "docs/*.md", "validator": None, "required": True}])
        snap = snapshot_outputs(agent)

        assert "docs/*.md" in snap
        assert str(f) in snap["docs/*.md"] or "docs/a.md" in snap["docs/*.md"]

    def test_empty_declarations(self):
        agent = {"name": "x", "outputs": {"minimum_changed": 0, "declarations": []}}
        snap = snapshot_outputs(agent)
        assert snap == {}

    def test_no_outputs_key(self):
        agent = {"name": "x"}
        snap = snapshot_outputs(agent)
        assert snap == {}


class TestRunFence:
    def test_required_output_created_passes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        agent = _agent([
            {"path_pattern": "out/*.md", "validator": None, "required": True},
        ])
        pre = snapshot_outputs(agent)

        d = tmp_path / "out"
        d.mkdir()
        (d / "new.md").write_text("created")

        result = run_fence(agent, pre, "s1", "i1")
        assert result.aggregate == "passed"
        assert result.declarations_changed == 1
        assert result.declarations[0].status == "passed"
        assert "out/new.md" in result.declarations[0].changed_files

    def test_required_output_missing_fails(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        agent = _agent([
            {"path_pattern": "out/*.md", "validator": None, "required": True},
        ])
        pre = snapshot_outputs(agent)

        result = run_fence(agent, pre, "s1", "i1")
        assert result.aggregate == "failed"
        assert result.declarations[0].status == "failed"
        assert any("required output" in r for r in result.failure_reasons)

    def test_optional_output_no_change_skipped(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        agent = _agent(
            [{"path_pattern": "opt/*.md", "validator": None, "required": False}],
            minimum_changed=0,
        )
        pre = snapshot_outputs(agent)

        result = run_fence(agent, pre, "s1", "i1")
        assert result.aggregate == "passed"
        assert result.declarations[0].status == "skipped"

    def test_optional_output_changed_runs_validator(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        d = tmp_path / "opt"
        d.mkdir()
        scripts = tmp_path / ".agent-factory" / "factory" / "scripts"
        scripts.mkdir(parents=True)
        validator = scripts / "check-opt"
        validator.write_text("#!/bin/sh\nexit 0\n")
        validator.chmod(0o755)

        agent = _agent(
            [{"path_pattern": "opt/*.md", "validator": "check-opt", "required": False}],
            minimum_changed=0,
        )
        pre = snapshot_outputs(agent)

        (d / "new.md").write_text("created")

        result = run_fence(agent, pre, "s1", "i1")
        assert result.declarations[0].status == "passed"
        assert result.declarations[0].validator_passed is True

    def test_minimum_changed_not_met_fails(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        agent = _agent(
            [{"path_pattern": "a/*.md", "validator": None, "required": False}],
            minimum_changed=2,
        )
        d = tmp_path / "a"
        d.mkdir()
        pre = snapshot_outputs(agent)

        (d / "one.md").write_text("x")

        result = run_fence(agent, pre, "s1", "i1")
        assert result.aggregate == "failed"
        assert result.declarations_changed == 1
        assert any("minimum_changed" in r for r in result.failure_reasons)

    def test_minimum_changed_met_passes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        agent = _agent([
            {"path_pattern": "a/*.md", "validator": None, "required": False},
            {"path_pattern": "b/*.md", "validator": None, "required": False},
        ], minimum_changed=2)
        (tmp_path / "a").mkdir()
        (tmp_path / "b").mkdir()
        pre = snapshot_outputs(agent)

        (tmp_path / "a" / "x.md").write_text("new")
        (tmp_path / "b" / "y.md").write_text("new")

        result = run_fence(agent, pre, "s1", "i1")
        assert result.aggregate == "passed"
        assert result.declarations_changed == 2

    def test_validator_fail_fails_fence(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        scripts = tmp_path / ".agent-factory" / "factory" / "scripts"
        scripts.mkdir(parents=True)
        validator = scripts / "fail-check"
        validator.write_text("#!/bin/sh\nexit 1\n")
        validator.chmod(0o755)

        d = tmp_path / "out"
        d.mkdir()
        agent = _agent([
            {"path_pattern": "out/*.md", "validator": "fail-check", "required": True},
        ])
        pre = snapshot_outputs(agent)

        (d / "x.md").write_text("new")

        result = run_fence(agent, pre, "s1", "i1")
        assert result.aggregate == "failed"
        assert result.declarations[0].validator_passed is False
        assert result.declarations[0].status == "failed"

    def test_validator_missing_warns_passes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        d = tmp_path / "out"
        d.mkdir()
        agent = _agent([
            {"path_pattern": "out/*.md", "validator": "nonexistent-validator", "required": True},
        ])
        pre = snapshot_outputs(agent)

        (d / "x.md").write_text("new")

        result = run_fence(agent, pre, "s1", "i1")
        assert result.aggregate == "passed"
        assert result.declarations[0].validator_passed is True
        assert any("nonexistent-validator" in w for w in result.warnings)

    def test_no_declarations_passes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        agent = _agent([], minimum_changed=0)
        pre = snapshot_outputs(agent)

        result = run_fence(agent, pre, "s1", "i1")
        assert result.aggregate == "passed"
        assert result.declarations == []

    def test_all_optional_none_changed_passes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        agent = _agent([
            {"path_pattern": "a/*.md", "validator": None, "required": False},
            {"path_pattern": "b/*.md", "validator": None, "required": False},
        ], minimum_changed=0)
        pre = snapshot_outputs(agent)

        result = run_fence(agent, pre, "s1", "i1")
        assert result.aggregate == "passed"
        assert all(d.status == "skipped" for d in result.declarations)

    def test_modified_file_detected(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        d = tmp_path / "out"
        d.mkdir()
        f = d / "existing.md"
        f.write_text("original")

        agent = _agent([
            {"path_pattern": "out/*.md", "validator": None, "required": True},
        ])
        pre = snapshot_outputs(agent)

        time.sleep(0.05)
        f.write_text("modified")

        result = run_fence(agent, pre, "s1", "i1")
        assert result.aggregate == "passed"
        assert "out/existing.md" in result.declarations[0].changed_files


class TestStoreEvidence:
    def test_creates_yaml(self, tmp_path):
        result = FenceResult(
            agent_name="test-agent",
            session_id="sess-001",
            invocation_id="inv-001",
            timestamp="2026-09-18T15:00:00+00:00",
            declarations=[],
            declarations_changed=0,
            minimum_changed=0,
            aggregate="passed",
            failure_reasons=[],
            warnings=[],
        )
        path = store_evidence(result, base_dir=tmp_path)
        assert path.exists()
        assert path == tmp_path / "sess-001" / "inv-001.yaml"

        data = yaml.safe_load(path.read_text())
        assert data["agent_name"] == "test-agent"
        assert data["aggregate"] == "passed"
        assert data["session_id"] == "sess-001"

    def test_stores_declaration_details(self, tmp_path):
        result = FenceResult(
            agent_name="a",
            session_id="s1",
            invocation_id="i1",
            timestamp="t",
            declarations=[
                DeclarationResult(
                    path_pattern="docs/*.md",
                    required=True,
                    validator="lint",
                    pre_snapshot={},
                    post_snapshot={"docs/x.md": 1.0},
                    changed_files=["docs/x.md"],
                    validator_passed=True,
                    status="passed",
                ),
            ],
            declarations_changed=1,
            minimum_changed=1,
            aggregate="passed",
            failure_reasons=[],
            warnings=[],
        )
        path = store_evidence(result, base_dir=tmp_path)
        data = yaml.safe_load(path.read_text())

        assert len(data["declarations"]) == 1
        d = data["declarations"][0]
        assert d["path_pattern"] == "docs/*.md"
        assert d["required"] is True
        assert d["changed_files"] == ["docs/x.md"]
        assert d["validator_passed"] is True
        assert d["status"] == "passed"


class TestLoadFenceEvidence:
    def test_loads_all_evidence(self, tmp_path):
        sess_dir = tmp_path / "sess-001"
        sess_dir.mkdir()

        for i in range(3):
            (sess_dir / f"inv-{i}.yaml").write_text(
                yaml.safe_dump({"invocation_id": f"inv-{i}", "aggregate": "passed"})
            )

        results = load_fence_evidence("sess-001", base_dir=tmp_path)
        assert len(results) == 3
        assert all(r["aggregate"] == "passed" for r in results)

    def test_missing_session_returns_empty(self, tmp_path):
        results = load_fence_evidence("nonexistent", base_dir=tmp_path)
        assert results == []

    def test_skips_malformed_yaml(self, tmp_path):
        sess_dir = tmp_path / "s1"
        sess_dir.mkdir()
        (sess_dir / "good.yaml").write_text(yaml.safe_dump({"ok": True}))
        (sess_dir / "bad.yaml").write_text("{{invalid")

        results = load_fence_evidence("s1", base_dir=tmp_path)
        assert len(results) == 1
        assert results[0]["ok"] is True
