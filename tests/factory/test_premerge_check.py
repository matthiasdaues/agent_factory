"""Contract tests for premerge-check gate script."""

from __future__ import annotations

from conftest import load_script

pm = load_script("premerge-check")


class TestCheckBlowout:
    def test_under_limit_passes(self):
        ok, msg = pm.check_blowout(["a.py", "b.py"], max_files=5)
        assert ok
        assert "PASS" in msg

    def test_over_limit_blocks(self):
        files = [f"file_{i}.py" for i in range(25)]
        ok, msg = pm.check_blowout(files, max_files=20)
        assert not ok
        assert "BLOCK" in msg
        assert "25" in msg


class TestCheckOutOfScope:
    def test_no_scope_skips(self):
        ok, msg = pm.check_out_of_scope(["any/file.py"], [], None)
        assert ok
        assert "SKIP" in msg

    def test_in_scope_passes(self):
        ok, msg = pm.check_out_of_scope(
            ["factory/scripts/lint.py"],
            ["factory/scripts/"],
        )
        assert ok
        assert "PASS" in msg

    def test_out_of_scope_blocks(self):
        ok, msg = pm.check_out_of_scope(
            ["docs/README.md", "factory/scripts/lint.py"],
            ["factory/scripts/"],
        )
        assert not ok
        assert "BLOCK" in msg
        assert "docs/README.md" in msg


class TestExtractStoryId:
    def test_story_branch_extracts_id(self):
        assert pm.extract_story_id("story/ST-0190") == "ST-0190"

    def test_non_story_branch_returns_none(self):
        assert pm.extract_story_id("feature/agent-context") is None

    def test_nested_story_branch_returns_none(self):
        assert pm.extract_story_id("story/ST-0190/fix") is None
