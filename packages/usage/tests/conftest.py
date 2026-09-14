"""Shared fixtures for usage package tests."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
SNAPSHOT_DIR = FIXTURES_DIR / "snapshot"


@pytest.fixture()
def snapshot_dir() -> Path:
    """Path to the snapshot fixture directory with three top-level JSONL files."""
    return SNAPSHOT_DIR


@pytest.fixture()
def empty_dir(tmp_path: Path) -> Path:
    """An empty temporary directory."""
    return tmp_path
