"""Contract tests for step-guard gate script."""

from __future__ import annotations

import pytest
from conftest import load_script

sg = load_script("step-guard")


class TestLoadManifest:
    def test_missing_file_returns_defaults(self, tmp_path):
        result = sg._load_manifest(tmp_path / "nonexistent.yml")
        assert result == {"inputs": [], "outputs": [], "max_input_tokens": None}

    def test_parses_block_lists(self, tmp_path):
        manifest = tmp_path / "step.yml"
        manifest.write_text(
            "inputs:\n"
            "  - docs/spec/*.md\n"
            "  - backlog/ST-*.md\n"
            "outputs:\n"
            "  - src/main.py\n"
            "max_input_tokens: 5000\n"
        )
        result = sg._load_manifest(manifest)
        assert result["inputs"] == ["docs/spec/*.md", "backlog/ST-*.md"]
        assert result["outputs"] == ["src/main.py"]
        assert result["max_input_tokens"] == 5000

    def test_parses_inline_lists(self, tmp_path):
        manifest = tmp_path / "step.yml"
        manifest.write_text("inputs: ['a.py', 'b.py']\noutputs: ['c.py']\n")
        result = sg._load_manifest(manifest)
        assert result["inputs"] == ["a.py", "b.py"]
        assert result["outputs"] == ["c.py"]


class TestParseInlineList:
    def test_valid_list(self):
        assert sg._parse_inline_list("inputs: ['a', 'b']") == ["a", "b"]

    def test_invalid_syntax_raises(self):
        with pytest.raises(ValueError):
            sg._parse_inline_list("inputs: [not valid yaml")


class TestReadAllowed:
    def test_factory_prefix_always_allowed(self):
        assert sg._read_allowed("factory/scripts/lint", []) is True

    def test_claude_prefix_always_allowed(self):
        assert sg._read_allowed(".claude/settings.json", []) is True

    def test_matching_input_allowed(self):
        assert sg._read_allowed("docs/spec/prd.md", ["docs/spec/*.md"]) is True

    def test_non_matching_denied(self):
        assert sg._read_allowed("src/secret.py", ["docs/*.md"]) is False


class TestWriteAllowed:
    def test_denied_paths_always_denied(self):
        assert sg._write_allowed(".current-work/dispatch-ledger.yaml", ["*"]) is False
        assert sg._write_allowed(".current-work/current-step.yml", ["*"]) is False

    def test_explicitly_allowed_paths(self):
        assert sg._write_allowed(".current-work/verify-base-ok", []) is True
        assert sg._write_allowed(".current-work/premerge-check-ok", []) is True

    def test_findings_prefix_allowed(self):
        assert sg._write_allowed("docs/findings/report.md", []) is True

    def test_matching_output_allowed(self):
        assert sg._write_allowed("src/main.py", ["src/*.py"]) is True

    def test_non_matching_denied(self):
        assert sg._write_allowed("config/secret.yml", ["src/*.py"]) is False


class TestExtractBashPaths:
    def test_cat_extracts_read(self):
        reads, writes = sg._extract_bash_paths("cat docs/spec/prd.md")
        assert "docs/spec/prd.md" in reads
        assert writes == []

    def test_grep_skips_pattern(self):
        reads, _writes = sg._extract_bash_paths("grep TODO docs/spec/prd.md")
        assert "docs/spec/prd.md" in reads
        assert "TODO" not in reads

    def test_redirect_extracts_write(self):
        _reads, writes = sg._extract_bash_paths("echo hello > output.txt")
        assert "output.txt" in writes

    def test_tee_extracts_write(self):
        _reads, writes = sg._extract_bash_paths("tee output.log")
        assert "output.log" in writes

    def test_no_paths_returns_empty(self):
        reads, writes = sg._extract_bash_paths("echo hello")
        assert reads == []
        assert writes == []


class TestBashAllowed:
    def test_no_paths_always_allowed(self):
        assert sg._bash_allowed("echo hello", [], []) is True

    def test_allowed_read(self):
        assert sg._bash_allowed("cat docs/spec/prd.md", ["docs/spec/*.md"], []) is True

    def test_denied_read(self):
        assert sg._bash_allowed("cat /etc/passwd", ["docs/*.md"], []) is False

    def test_allowed_write(self):
        assert sg._bash_allowed("tee src/main.py", [], ["src/*.py"]) is True

    def test_denied_write(self):
        assert sg._bash_allowed("tee secret.key", [], ["src/*.py"]) is False


class TestContextAllowed:
    def test_within_budget_passes(self, tmp_path):
        (tmp_path / "small.txt").write_text("a" * 100)
        event = {"inputs": ["small.txt"], "max_input_tokens": 1000}
        manifest = {"inputs": [], "outputs": [], "max_input_tokens": None}
        allowed, msg = sg._context_allowed(event, manifest, tmp_path)
        assert allowed is True
        assert msg is None

    def test_over_budget_fails(self, tmp_path):
        (tmp_path / "big.txt").write_text("a" * 40000)
        event = {"inputs": ["big.txt"], "max_input_tokens": 100}
        manifest = {"inputs": [], "outputs": [], "max_input_tokens": None}
        allowed, msg = sg._context_allowed(event, manifest, tmp_path)
        assert allowed is False
        assert "exceeded" in msg


class TestMainRoundTrip:
    """Integration: main() wires stdin event → manifest → guard → exit code."""

    def test_read_allowed_exits_zero(self, tmp_path, monkeypatch):
        import io
        import json

        manifest = tmp_path / ".current-work" / "current-step.yml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("inputs:\n  - docs/*.md\noutputs:\n  - src/*.py\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            "sys.stdin", io.StringIO(json.dumps({"path": "factory/scripts/lint"}))
        )
        rc = sg.main(["--guard-type", "read"])
        assert rc == 0

    def test_read_denied_exits_one(self, tmp_path, monkeypatch):
        import io
        import json

        manifest = tmp_path / ".current-work" / "current-step.yml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("inputs:\n  - docs/*.md\noutputs:\n  - src/*.py\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            "sys.stdin", io.StringIO(json.dumps({"path": "secrets/key.pem"}))
        )
        rc = sg.main(["--guard-type", "read"])
        assert rc == 1

    def test_write_denied_path_exits_one(self, tmp_path, monkeypatch):
        import io
        import json

        manifest = tmp_path / ".current-work" / "current-step.yml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("inputs:\n  - docs/*.md\noutputs:\n  - src/*.py\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            "sys.stdin",
            io.StringIO(json.dumps({"path": ".current-work/dispatch-ledger.yaml"})),
        )
        rc = sg.main(["--guard-type", "write"])
        assert rc == 1

    def test_no_manifest_allows_everything(self, tmp_path, monkeypatch):
        import io
        import json

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            "sys.stdin", io.StringIO(json.dumps({"path": "anything.txt"}))
        )
        rc = sg.main(["--guard-type", "read"])
        assert rc == 0

    def test_invalid_json_exits_two(self, tmp_path, monkeypatch):
        import io

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.stdin", io.StringIO("not json"))
        rc = sg.main(["--guard-type", "read"])
        assert rc == 2

    def test_bash_guard_allowed(self, tmp_path, monkeypatch):
        import io
        import json

        manifest = tmp_path / ".current-work" / "current-step.yml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("inputs:\n  - docs/*.md\noutputs:\n  - src/*.py\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            "sys.stdin",
            io.StringIO(json.dumps({"command": "cat factory/scripts/lint"})),
        )
        rc = sg.main(["--guard-type", "bash"])
        assert rc == 0
