"""Tests for traceless install/removal: `factory/scripts/init-factory` wiring a
project up, and `factory/scripts/remove-factory` taking it back down to a clean
tree.

Both scripts are extensionless; they're loaded via importlib against the real
files, the same way test_init_factory_guardrail.py loads init-factory. Each
test builds a small synthetic project in `tmp_path` (its own .gitignore,
.pre-commit-config.yaml, .github/workflows, and — for the non-interference
test — its own .github/copilot-instructions.md), snapshots it, runs the full
init→remove cycle, and asserts the tree comes back byte-identical.

The synthetic project is deliberately NOT drawn from any real repo on disk, so
these tests are self-contained and stable.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    script = _ROOT / "factory" / "scripts" / name
    loader = SourceFileLoader(name.replace("-", "_"), str(script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


init_factory = _load("init-factory")
remove_factory = _load("remove-factory")


PROJECT_GITIGNORE = "__pycache__/\n*.pyc\n/dist/"  # note: no trailing newline
PROJECT_PRECOMMIT = """\
repos:
  - repo: local
    hooks:
      - id: project-own-hook
        name: project own hook
        entry: echo hi
        language: system
"""
PROJECT_WORKFLOW = "name: CI\non: [push]\njobs: {}\n"
PROJECT_CLAUDE_SETTINGS = {
    "hooks": {
        "PostToolUse": [
            {
                "matcher": "Bash",
                "hooks": [{"type": "command", "command": "echo project-done"}],
            }
        ],
        "Stop": [
            {"hooks": [{"type": "command", "command": "echo project-owned-stop"}]}
        ],
    }
}


def _make_project(root: Path, with_copilot_instructions: bool = False) -> None:
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "ci.yml").write_text(PROJECT_WORKFLOW)
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("print('hi')\n")
    (root / ".gitignore").write_text(PROJECT_GITIGNORE)
    (root / ".pre-commit-config.yaml").write_text(PROJECT_PRECOMMIT)
    if with_copilot_instructions:
        (root / ".github" / "copilot-instructions.md").write_text(
            "# The project's own Copilot instructions — do not touch.\n"
        )


def _snapshot(root: Path) -> dict[str, bytes]:
    """relpath -> bytes for every file under root except .git and the factory
    footprint (which only exists mid-cycle)."""
    out: dict[str, bytes] = {}
    for p in sorted(root.rglob("*")):
        if p.is_symlink() or not p.is_file():
            continue
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] == ".git":
            continue
        out[str(rel)] = p.read_bytes()
    return out


def _run_init(target: Path) -> int:
    return init_factory.main(["--target", str(target), "--source", str(_ROOT)])


def _run_remove(target: Path) -> int:
    return remove_factory.main(["--target", str(target)])


class TestInstallShape:
    def test_gitignore_block_targets_github_entries_not_whole_dir(self, tmp_path):
        _make_project(tmp_path)
        assert _run_init(tmp_path) == 0

        gitignore = (tmp_path / ".gitignore").read_text()
        assert "# >>> agent_factory related >>>" in gitignore
        assert "/factory/" in gitignore
        assert "/.claude/" in gitignore
        # .github is ignored entry-by-entry, never wholesale
        assert "/.github/agents" in gitignore
        assert "/.github/hooks" in gitignore
        assert "\n.github\n" not in gitignore
        assert "/.github/\n" not in gitignore

    def test_workflows_stay_unignored_and_real(self, tmp_path):
        _make_project(tmp_path)
        assert _run_init(tmp_path) == 0

        wf = tmp_path / ".github" / "workflows" / "ci.yml"
        assert wf.is_file() and not wf.is_symlink()
        assert wf.read_text() == PROJECT_WORKFLOW

    def test_precommit_block_prefixed_and_on_top(self, tmp_path):
        _make_project(tmp_path)
        assert _run_init(tmp_path) == 0

        lines = (tmp_path / ".pre-commit-config.yaml").read_text().splitlines()
        ids = [
            ln.split("id:", 1)[1].strip()
            for ln in lines
            if ln.strip().startswith("- id:")
        ]
        # our hooks come first, all prefixed; the project's own hook survives
        assert ids[0].startswith("agent_factory_hook-")
        assert "project-own-hook" in ids
        first_af = ids.index(
            next(i for i in ids if i.startswith("agent_factory_hook-"))
        )
        assert first_af < ids.index("project-own-hook")

    def test_existing_orientation_file_left_untouched(self, tmp_path):
        _make_project(tmp_path, with_copilot_instructions=True)
        before = (tmp_path / ".github" / "copilot-instructions.md").read_text()

        assert _run_init(tmp_path) == 0

        ci = tmp_path / ".github" / "copilot-instructions.md"
        assert not ci.is_symlink()
        assert ci.read_text() == before
        # a file we didn't create is never added to our ignore block
        assert "copilot-instructions" not in (tmp_path / ".gitignore").read_text()


class TestTracelessRemoval:
    def test_roundtrip_is_byte_identical(self, tmp_path):
        _make_project(tmp_path)
        before = _snapshot(tmp_path)

        assert _run_init(tmp_path) == 0
        assert _run_remove(tmp_path) == 0

        after = _snapshot(tmp_path)
        assert after == before

    def test_roundtrip_with_existing_orientation_is_byte_identical(self, tmp_path):
        _make_project(tmp_path, with_copilot_instructions=True)
        before = _snapshot(tmp_path)

        assert _run_init(tmp_path) == 0
        assert _run_remove(tmp_path) == 0

        assert _snapshot(tmp_path) == before

    def test_double_init_then_single_remove_is_byte_identical(self, tmp_path):
        _make_project(tmp_path)
        before = _snapshot(tmp_path)

        assert _run_init(tmp_path) == 0
        assert _run_init(tmp_path) == 0
        assert _run_remove(tmp_path) == 0

        assert _snapshot(tmp_path) == before

    def test_remove_without_manifest_is_noop(self, tmp_path):
        _make_project(tmp_path)
        before = _snapshot(tmp_path)

        assert _run_remove(tmp_path) == 0

        assert _snapshot(tmp_path) == before

    def test_roundtrip_with_existing_claude_settings_removes_only_our_hooks(
        self, tmp_path
    ):
        _make_project(tmp_path)
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "settings.json").write_text(
            json.dumps(PROJECT_CLAUDE_SETTINGS, indent=2) + "\n", encoding="utf-8"
        )
        before = _snapshot(tmp_path)

        assert _run_init(tmp_path) == 0
        settings_after_init = json.loads(
            (claude_dir / "settings.json").read_text(encoding="utf-8")
        )
        assert any(
            hook.get("command") == init_factory.CLAUDE_CAPTURE_HOOK_COMMAND
            for event in init_factory.CLAUDE_CAPTURE_HOOK_EVENTS
            for entry in settings_after_init["hooks"][event]
            for hook in entry.get("hooks", [])
        )

        assert _run_remove(tmp_path) == 0

        assert _snapshot(tmp_path) == before
