"""Contract tests for the voice-anchor-lint gate script."""

from __future__ import annotations

from pathlib import Path

from conftest import load_script

val = load_script("voice-anchor-lint")


def _factory(tmp_path: Path) -> Path:
    (tmp_path / "agents").mkdir()
    (tmp_path / "skills").mkdir()
    return tmp_path


def _agent(root: Path, name: str, body: str) -> None:
    (root / "agents" / f"{name}.md").write_text(f"# {name}\n\n{body}\n")


def _skill(root: Path, name: str, body: str) -> None:
    (root / "skills" / name).mkdir()
    (root / "skills" / name / "SKILL.md").write_text(f"# {name}\n\n{body}\n")


class TestCheck:
    def test_anchored_agent_and_skill_pass(self, tmp_path: Path):
        root = _factory(tmp_path)
        _agent(root, "a", val.anchor_sentence(".."))
        _skill(root, "s", val.anchor_sentence("../.."))
        assert val.check(root) == []

    def test_agent_without_anchor_fails(self, tmp_path: Path):
        root = _factory(tmp_path)
        _agent(root, "a", "Apply the factory voice.")
        errors = val.check(root)
        assert len(errors) == 1
        assert "agents/a.md" in errors[0]

    def test_reworded_anchor_fails(self, tmp_path: Path):
        root = _factory(tmp_path)
        reworded = val.anchor_sentence("../..").replace("all four gates", "the gates")
        _skill(root, "s", reworded)
        assert len(val.check(root)) == 1

    def test_wrong_relative_path_fails(self, tmp_path: Path):
        root = _factory(tmp_path)
        _skill(root, "s", val.anchor_sentence(".."))
        assert len(val.check(root)) == 1

    def test_exempt_skill_without_anchor_passes(self, tmp_path: Path):
        root = _factory(tmp_path)
        _skill(root, "scratchpad", "Append the note.")
        assert val.check(root) == []


class TestSourceTree:
    def test_every_agent_and_skill_in_the_factory_is_anchored(self):
        assert val.check(val.FACTORY_DIR) == []
