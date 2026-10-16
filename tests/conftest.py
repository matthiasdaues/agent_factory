"""Shared pytest fixtures for all test suites."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCRIPTS_DIR = REPO_ROOT / "packages" / "factory" / "scripts"
SCRIPTS_DIR = SOURCE_SCRIPTS_DIR

# Scripts like spec-lint do `import _session_log` at module scope. Tests
# check the source, so only the source directory goes on sys.path.
if str(SOURCE_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_SCRIPTS_DIR))


def _docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        probe = subprocess.run(["docker", "info"], capture_output=True, check=False, timeout=20)
    except subprocess.TimeoutExpired:
        return False
    return probe.returncode == 0


# Explicit precondition for tests that run containers: skipped, with the
# reason named, when no Docker daemon answers.
requires_docker = pytest.mark.skipif(
    not _docker_available(), reason="Docker daemon not available"
)


def load_script(name: str):
    """Import a factory script as a Python module."""
    path = SOURCE_SCRIPTS_DIR / name
    module_name = name.replace("-", "_")
    loader = SourceFileLoader(module_name, str(path))
    spec = importlib.util.spec_from_loader(module_name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def _scrub_git_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove GIT_* env vars leaked by pre-commit hooks."""
    for key in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(key, raising=False)
