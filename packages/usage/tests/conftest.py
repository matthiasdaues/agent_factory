"""Shared fixtures for usage package tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def pytest_sessionstart(session):
    """Enable subprocess coverage tracking when running under pytest-cov."""
    if session.config.pluginmanager.hasplugin("_cov"):
        config_file = str(Path(__file__).resolve().parent.parent / "pyproject.toml")
        os.environ["COVERAGE_PROCESS_START"] = config_file


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
SNAPSHOT_DIR = FIXTURES_DIR / "snapshot"
ANCESTRY_DIR = FIXTURES_DIR / "ancestry"
MULTI_CLI_DIR = FIXTURES_DIR / "multi-cli"


@pytest.fixture()
def snapshot_dir() -> Path:
    """Path to the snapshot fixture directory with three top-level JSONL files."""
    return SNAPSHOT_DIR


@pytest.fixture()
def ancestry_dir() -> Path:
    """Path to the ancestry fixture directory with per-failure-code JSONL files."""
    return ANCESTRY_DIR


@pytest.fixture()
def multi_cli_dir() -> Path:
    """Path to the multi-cli fixture directory with per-CLI JSONL files."""
    return MULTI_CLI_DIR


@pytest.fixture()
def empty_dir(tmp_path: Path) -> Path:
    """An empty temporary directory."""
    return tmp_path
