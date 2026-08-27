"""Shared pytest fixtures for all test suites."""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _scrub_git_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove GIT_* env vars leaked by pre-commit hooks."""
    for key in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(key, raising=False)
