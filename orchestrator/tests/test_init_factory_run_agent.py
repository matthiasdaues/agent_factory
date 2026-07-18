"""Tests for the Pi run_agent invocation-layer extension wired in by
`factory/scripts/init-factory`.

Pi has no native subagent concept; `run-agent.ts` (ADR-0004, UC-10) is the
extension through which a factory agent runs another agent in a separate Pi
session. init-factory symlinks it into `.pi/extensions/` alongside the
git-safety guardrail. These tests prove the wiring only — that the symlink is
installed, points at the copied factory config, is idempotent on re-run, and is
recorded in the removal manifest so remove-factory reverses it.

init-factory is loaded via importlib against the real (extensionless) file, the
same way test_init_factory_guardrail.py loads it.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "init-factory"
_loader = SourceFileLoader("init_factory", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("init_factory", _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules["init_factory"] = init_factory
_loader.exec_module(init_factory)


def _run_init(target: Path) -> int:
    return init_factory.main(["--target", str(target), "--source", str(_ROOT)])


# The invocation-layer extensions init-factory symlinks into .pi/extensions/.
INVOCATION_EXTENSIONS = ("run-agent.ts", "dispatch-wave.ts")


def _extension_link(target: Path, name: str = "run-agent.ts") -> Path:
    return target / ".pi" / "extensions" / name


def _manifest(target: Path) -> dict:
    path = target / init_factory.MANIFEST_PATH
    return json.loads(path.read_text(encoding="utf-8"))


class TestFreshTarget:
    @pytest.mark.parametrize("name", INVOCATION_EXTENSIONS)
    def test_extension_symlinked_into_copied_factory_config(self, tmp_path, name):
        rc = _run_init(tmp_path)
        assert rc == 0

        link = _extension_link(tmp_path, name)
        assert link.is_symlink()

        resolved = link.resolve()
        expected = (tmp_path / "factory" / "config" / "extensions" / name).resolve()
        assert resolved == expected
        assert resolved.is_file()

    @pytest.mark.parametrize("name", INVOCATION_EXTENSIONS)
    def test_removal_path_recorded_in_manifest(self, tmp_path, name):
        rc = _run_init(tmp_path)
        assert rc == 0

        assert f".pi/extensions/{name}" in _manifest(tmp_path)["remove_paths"]


class TestReRunIsNoop:
    @pytest.mark.parametrize("name", INVOCATION_EXTENSIONS)
    def test_second_run_leaves_symlink_unchanged(self, tmp_path, name):
        assert _run_init(tmp_path) == 0

        link = _extension_link(tmp_path, name)
        target_before = link.resolve()

        assert _run_init(tmp_path) == 0

        assert link.is_symlink()
        assert link.resolve() == target_before

    @pytest.mark.parametrize("name", INVOCATION_EXTENSIONS)
    def test_removal_path_not_duplicated_on_rerun(self, tmp_path, name):
        assert _run_init(tmp_path) == 0
        assert _run_init(tmp_path) == 0

        remove_paths = _manifest(tmp_path)["remove_paths"]
        assert remove_paths.count(f".pi/extensions/{name}") == 1


class TestCoexistsWithGuardrail:
    def test_all_pi_extensions_installed(self, tmp_path):
        rc = _run_init(tmp_path)
        assert rc == 0

        extensions_dir = tmp_path / ".pi" / "extensions"
        assert (extensions_dir / "block-dangerous-git.ts").is_symlink()
        for name in INVOCATION_EXTENSIONS:
            assert (extensions_dir / name).is_symlink()
