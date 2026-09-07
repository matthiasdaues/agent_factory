"""Fixture module with a conforming import."""

from pathlib import Path


def fixture_path() -> str:
    """Return this file path while importing only an allowed stdlib module."""
    return str(Path(__file__))
