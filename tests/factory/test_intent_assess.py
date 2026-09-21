"""Contract tests for the intent assess command."""

from __future__ import annotations

import json
import os
import textwrap

import pytest

from conftest import load_script

intent = load_script("intent")


def _write_proposal(tmp_path, name="my-proposal", status="accepted"):
    docs = tmp_path / "docs" / "proposals"
    docs.mkdir(parents=True, exist_ok=True)
    path = docs / f"{name}.md"
    path.write_text(textwrap.dedent(f"""\
        ---
        title: {name}
        status: {status}
        ---
        # {name}

        ## Problem
        Something is wrong.

        ## Solution
        Fix it.

        ## Scope
        Everything.
    """))
    return path


def _write_story(tmp_path, story_id="ST-0001", scope=None):
    backlog = tmp_path / "backlog"
    backlog.mkdir(parents=True, exist_ok=True)
    fm = f"---\ntitle: test story\nstatus: ready\n"
    if scope:
        fm += f"scope: {scope}\n"
    fm += "---\n# Story\n"
    path = backlog / f"{story_id}.md"
    path.write_text(fm)
    return path


class TestAssessDiscovery:
    def test_discovers_proposals(self, tmp_path, capsys):
        _write_proposal(tmp_path)
        os.chdir(tmp_path)
        result = intent.main(["assess"])
        assert result == 0
        out = capsys.readouterr().out
        assert "my-proposal" in out

    def test_discovers_stories(self, tmp_path, capsys):
        _write_story(tmp_path)
        os.chdir(tmp_path)
        result = intent.main(["assess"])
        assert result == 0
        out = capsys.readouterr().out
        assert "ST-0001" in out

    def test_no_artifacts_found(self, tmp_path, capsys):
        os.chdir(tmp_path)
        result = intent.main(["assess"])
        assert result == 0
        out = capsys.readouterr().out
        assert "no governed artifacts found" in out


class TestAssessProposalValidation:
    def test_accepted_proposal_passes(self, tmp_path, capsys):
        _write_proposal(tmp_path, status="accepted")
        os.chdir(tmp_path)
        result = intent.main(["assess"])
        assert result == 0
        out = capsys.readouterr().out
        assert "✓" in out
        assert "file_exists" in out

    def test_draft_proposal_warns(self, tmp_path, capsys):
        _write_proposal(tmp_path, status="draft")
        os.chdir(tmp_path)
        result = intent.main(["assess"])
        assert result == 0
        out = capsys.readouterr().out
        assert "status_accepted" in out
        assert "✗" in out


class TestAssessFrontmatterChecks:
    def test_story_frontmatter_checked(self, tmp_path, capsys):
        _write_story(tmp_path)
        os.chdir(tmp_path)
        result = intent.main(["assess"])
        assert result == 0
        out = capsys.readouterr().out
        assert "frontmatter_present" in out
        assert "title_present" in out
        assert "status_present" in out


class TestAssessJsonFormat:
    def test_json_output_parseable(self, tmp_path, capsys):
        _write_proposal(tmp_path)
        os.chdir(tmp_path)
        result = intent.main(["assess", "--format", "json"])
        assert result == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "artifact_type" in data[0]
        assert "checks" in data[0]

    def test_json_has_assessed_commit(self, tmp_path, capsys):
        _write_proposal(tmp_path)
        os.chdir(tmp_path)
        result = intent.main(["assess", "--format", "json"])
        assert result == 0
        data = json.loads(capsys.readouterr().out)
        assert "assessed_commit" in data[0]


class TestAssessWorkstreamFilter:
    def test_workstream_filters_by_scope(self, tmp_path, capsys):
        _write_story(tmp_path, "ST-0001", scope="alpha")
        _write_story(tmp_path, "ST-0002", scope="beta")
        os.chdir(tmp_path)
        result = intent.main(["assess", "--workstream", "alpha"])
        assert result == 0
        out = capsys.readouterr().out
        assert "ST-0001" in out
        assert "ST-0002" not in out

    def test_no_workstream_shows_all(self, tmp_path, capsys):
        _write_story(tmp_path, "ST-0001", scope="alpha")
        _write_story(tmp_path, "ST-0002", scope="beta")
        os.chdir(tmp_path)
        result = intent.main(["assess"])
        assert result == 0
        out = capsys.readouterr().out
        assert "ST-0001" in out
        assert "ST-0002" in out


class TestAssessReadOnly:
    def test_no_files_written(self, tmp_path):
        _write_proposal(tmp_path)
        os.chdir(tmp_path)
        before = set(tmp_path.rglob("*"))
        intent.main(["assess"])
        after = set(tmp_path.rglob("*"))
        assert before == after


class TestAssessExitCode:
    def test_exit_zero_on_success(self, tmp_path):
        os.chdir(tmp_path)
        result = intent.main(["assess"])
        assert result == 0
