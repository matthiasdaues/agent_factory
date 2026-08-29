"""UC-09 contracts: Factory does not inject test hooks; projects own testing (ST-0149)."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    loader = SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


init_factory = _load("init_factory_prepush", _ROOT / "factory/scripts/init-factory")
merge_precommit = _load(
    "merge_precommit_config_prepush",
    _ROOT / "factory/scripts/merge-precommit-config",
)

HOOK = """\
      - id: agent_factory_hook-run-tests-full
        name: "agent_factory: run-tests (full suite)"
        entry: factory/scripts/run-tests --full
        language: system
        stages: [pre-push]
        pass_filenames: false
        always_run: true
"""


def _install_template(target: Path) -> Path:
    config = target / "factory/config"
    config.mkdir(parents=True)
    template = config / "pre-commit-config.yaml"
    shutil.copyfile(_ROOT / "factory/config/pre-commit-config.yaml", template)
    return template


def test_UC_09_fresh_init_does_not_install_test_hook(tmp_path):
    _install_template(tmp_path)
    install = {"remove_paths": []}

    init_factory.handle_precommit(tmp_path, install, [])

    installed = (tmp_path / ".pre-commit-config.yaml").read_text()
    assert HOOK not in installed


def test_UC_09_merge_does_not_inject_test_hook_and_remains_idempotent(tmp_path):
    template = _install_template(tmp_path)
    target = tmp_path / ".pre-commit-config.yaml"
    target.write_text(
        "repos:\n"
        "  - repo: local\n"
        "    hooks:\n"
        "      - id: consumer-hook\n"
        "        entry: echo consumer\n"
        "        language: system\n"
    )

    assert (
        merge_precommit.main(["--target", str(target), "--template", str(template)])
        == 0
    )
    first_merge = target.read_text()
    assert HOOK not in first_merge
    assert "id: consumer-hook" in first_merge

    assert (
        merge_precommit.main(["--target", str(target), "--template", str(template)])
        == 0
    )
    assert target.read_text() == first_merge


def test_UC_09_init_installs_pre_commit_and_pre_push_hook_types(monkeypatch, tmp_path):
    calls = []

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(init_factory.subprocess, "run", fake_run)

    init_factory.pre_commit_install(tmp_path, [])

    assert calls == [
        (
            [
                "uvx",
                "pre-commit",
                "install",
                "--hook-type",
                "pre-commit",
                "--hook-type",
                "pre-push",
            ],
            {
                "cwd": tmp_path,
                "capture_output": True,
                "text": True,
                "check": False,
            },
        )
    ]
