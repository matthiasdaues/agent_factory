"""Consumer-install contract for the shipped playbook orchestrator."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_INIT = _ROOT / "factory" / "scripts" / "init-factory"
_loader = SourceFileLoader("init_factory_orchestrator", str(_INIT))
_spec = importlib.util.spec_from_loader("init_factory_orchestrator", _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules["init_factory_orchestrator"] = init_factory
_loader.exec_module(init_factory)


@pytest.fixture(autouse=True)
def _isolate_external_installers(monkeypatch):
    monkeypatch.setattr(
        init_factory, "provision_usage_runtime", lambda _target, _report: True
    )
    monkeypatch.setattr(
        init_factory,
        "initialize_usage_lifecycle",
        lambda _target, _report, _retention: None,
    )
    monkeypatch.setattr(
        init_factory, "pre_commit_install", lambda _target, _report: None
    )


def test_fresh_install_ships_runnable_orchestrator(tmp_path):
    assert (
        init_factory.main(
            [
                "--target",
                str(tmp_path),
                "--source",
                str(_ROOT),
                "--project-name",
                "Test Project",
            ]
        )
        == 0
    )

    command = tmp_path / "factory" / "scripts" / "run-playbook"
    assert command.is_file()
    assert command.stat().st_mode & 0o111

    result = subprocess.run(
        [str(command), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "AF_ORCHESTRATOR_SOURCE": str(_ROOT / "orchestrator"),
            "UV_CACHE_DIR": str(tmp_path / ".uv-cache"),
            "UV_TOOL_DIR": str(tmp_path / ".uv-tools"),
        },
    )

    assert result.returncode == 0
    assert "--cli" in result.stdout
    assert "claude" in result.stdout
    assert "copilot" in result.stdout


def test_factory_launcher_defaults_to_exact_package_version():
    launcher = (_ROOT / "factory/scripts/run-playbook").read_text(encoding="utf-8")
    assert "@orchestrator-v0.1.0#subdirectory=orchestrator" in launcher
    assert "@main" not in launcher
    assert "@dev" not in launcher


def test_legacy_authoring_launcher_remains_runnable():
    result = subprocess.run(
        [sys.executable, str(_ROOT / "orchestrator/src/run_playbook.py"), "--help"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--playbook" in result.stdout
