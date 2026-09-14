"""Shared fixtures for usage package tests."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
SNAPSHOT_DIR = FIXTURES_DIR / "snapshot"
ANCESTRY_DIR = FIXTURES_DIR / "ancestry"


@pytest.fixture()
def snapshot_dir() -> Path:
    """Path to the snapshot fixture directory with three top-level JSONL files."""
    return SNAPSHOT_DIR


@pytest.fixture()
def ancestry_dir() -> Path:
    """Path to the ancestry fixture directory with per-failure-code JSONL files."""
    return ANCESTRY_DIR


@pytest.fixture()
def empty_dir(tmp_path: Path) -> Path:
    """An empty temporary directory."""
    return tmp_path
