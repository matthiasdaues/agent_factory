"""Tests for `factory/scripts/resolve-model`.

resolve-model is the shared tier resolver behind both `trigger` and the Pi
`run_agent` tool (ADR-0004, UC-10). These tests cover the three surfaces the
`run_agent` extension depends on: reading an agent's tier from frontmatter,
resolving `<cli>.<tier>` against model.conf, and the on_missing halt/auto
branch. The script is extensionless, so it is loaded via importlib the same way
the other init-factory tests load their target.
"""

from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "resolve-model"
_loader = SourceFileLoader("resolve_model", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("resolve_model", _loader)
resolve_model = importlib.util.module_from_spec(_spec)
sys.modules["resolve_model"] = resolve_model
_loader.exec_module(resolve_model)


MODEL_CONF_HALT = """\
[facts]
pi.economy  = openrouter/anthropic/claude-haiku-4.5
pi.standard = openrouter/anthropic/claude-sonnet-4.6
pi.strong   = openrouter/anthropic/claude-opus-4.8
on_missing = halt
"""

MODEL_CONF_AUTO = """\
[facts]
pi.economy = openrouter/anthropic/claude-haiku-4.5
on_missing = auto
"""


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _agent(agents_dir: Path, name: str, tier: str | None) -> None:
    agents_dir.mkdir(parents=True, exist_ok=True)
    if tier is None:
        body = f"# {name}\n\nNo frontmatter here.\n"
    else:
        body = f"---\nname: {name}\ntier: {tier}\n---\n\n# {name}\n"
    (agents_dir / f"{name}.md").write_text(body, encoding="utf-8")


class TestReadAgentTier:
    def test_reads_declared_tier(self, tmp_path):
        _agent(tmp_path, "spec-review-agent", "strong")
        assert resolve_model.read_agent_tier(tmp_path, "spec-review-agent") == "strong"

    def test_defaults_to_standard_without_frontmatter(self, tmp_path):
        _agent(tmp_path, "plain-agent", None)
        assert resolve_model.read_agent_tier(tmp_path, "plain-agent") == "standard"

    def test_defaults_to_standard_when_tier_field_absent(self, tmp_path):
        agents_dir = tmp_path
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "no-tier.md").write_text(
            "---\nname: no-tier\n---\n\n# no-tier\n", encoding="utf-8"
        )
        assert resolve_model.read_agent_tier(agents_dir, "no-tier") == "standard"

    def test_missing_agent_raises(self, tmp_path):
        with pytest.raises(resolve_model.ResolutionError):
            resolve_model.read_agent_tier(tmp_path, "nonexistent")


class TestResolve:
    def test_configured_tier_returns_model(self, tmp_path):
        conf = _write(tmp_path / "model.conf", MODEL_CONF_HALT)
        assert (
            resolve_model.resolve(conf, "pi", "strong")
            == "openrouter/anthropic/claude-opus-4.8"
        )

    def test_missing_tier_halt_raises(self, tmp_path):
        conf = _write(tmp_path / "model.conf", MODEL_CONF_HALT)
        with pytest.raises(resolve_model.ResolutionError):
            resolve_model.resolve(conf, "pi", "nonexistent-tier")

    def test_missing_tier_auto_returns_none(self, tmp_path):
        conf = _write(tmp_path / "model.conf", MODEL_CONF_AUTO)
        assert resolve_model.resolve(conf, "pi", "strong") is None

    def test_missing_conf_raises(self, tmp_path):
        with pytest.raises(resolve_model.ResolutionError):
            resolve_model.resolve(tmp_path / "absent.conf", "pi", "standard")


class TestMain:
    def test_resolves_agent_to_model_on_stdout(self, tmp_path, capsys):
        _agent(tmp_path / "agents", "reviewer", "standard")
        conf = _write(tmp_path / "model.conf", MODEL_CONF_HALT)

        rc = resolve_model.main(
            [
                "--agent",
                "reviewer",
                "--cli",
                "pi",
                "--model-conf",
                str(conf),
                "--agents-dir",
                str(tmp_path / "agents"),
            ]
        )
        assert rc == 0
        assert (
            capsys.readouterr().out.strip() == "openrouter/anthropic/claude-sonnet-4.6"
        )

    def test_tier_override_skips_agent_file(self, tmp_path, capsys):
        conf = _write(tmp_path / "model.conf", MODEL_CONF_HALT)
        rc = resolve_model.main(
            ["--tier", "economy", "--cli", "pi", "--model-conf", str(conf)]
        )
        assert rc == 0
        assert (
            capsys.readouterr().out.strip() == "openrouter/anthropic/claude-haiku-4.5"
        )

    def test_unknown_agent_exits_2(self, tmp_path, capsys):
        conf = _write(tmp_path / "model.conf", MODEL_CONF_HALT)
        rc = resolve_model.main(
            [
                "--agent",
                "ghost",
                "--cli",
                "pi",
                "--model-conf",
                str(conf),
                "--agents-dir",
                str(tmp_path / "agents"),
            ]
        )
        assert rc == 2
        assert "resolve-model:" in capsys.readouterr().err

    def test_auto_missing_tier_exits_0_with_empty_stdout(self, tmp_path, capsys):
        conf = _write(tmp_path / "model.conf", MODEL_CONF_AUTO)
        rc = resolve_model.main(
            ["--tier", "strong", "--cli", "pi", "--model-conf", str(conf)]
        )
        assert rc == 0
        assert capsys.readouterr().out.strip() == ""
