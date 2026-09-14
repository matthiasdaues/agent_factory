"""Tests for usage.cli — argument parsing, view routing, error exits."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run usage-query via ``python -m`` to avoid needing installed entry point."""
    return subprocess.run(
        [sys.executable, "-c", "from usage.cli import main; main()", *args],
        capture_output=True,
        text=True,
    )


class TestUnknownView:
    """Unknown view name exits 2 with available views on stderr."""

    def test_unknown_view_exit_code(self, snapshot_dir: Path) -> None:
        result = _run_cli("bogus_view", "--usage-dir", str(snapshot_dir))
        assert result.returncode == 2

    def test_unknown_view_stderr_lists_available(self, snapshot_dir: Path) -> None:
        result = _run_cli("bogus_view", "--usage-dir", str(snapshot_dir))
        assert "capture_health" in result.stderr
        assert "bogus_view" in result.stderr


class TestMissingDirectory:
    """Nonexistent --usage-dir exits 2 with the path in stderr."""

    def test_missing_dir_exit_code(self) -> None:
        result = _run_cli("capture_health", "--usage-dir", "/nonexistent/path/xyz")
        assert result.returncode == 2

    def test_missing_dir_stderr_names_path(self) -> None:
        result = _run_cli("capture_health", "--usage-dir", "/nonexistent/path/xyz")
        assert "/nonexistent/path/xyz" in result.stderr


class TestCaptureHealth:
    """capture_health on fixture dir returns typed empty result."""

    def test_exit_zero(self, snapshot_dir: Path) -> None:
        result = _run_cli("capture_health", "--usage-dir", str(snapshot_dir))
        assert result.returncode == 0

    def test_returns_typed_result_with_preflight(self, snapshot_dir: Path) -> None:
        result = _run_cli("capture_health", "--usage-dir", str(snapshot_dir))
        data = json.loads(result.stdout)
        assert data["view"] == "capture_health"
        assert data["rows"] == []
        assert "preflight" in data

    def test_empty_dir_returns_typed_empty_result(self, empty_dir: Path) -> None:
        result = _run_cli("capture_health", "--usage-dir", str(empty_dir))
        data = json.loads(result.stdout)
        assert data == {"view": "capture_health", "rows": []}

    def test_empty_dir_exit_zero(self, empty_dir: Path) -> None:
        result = _run_cli("capture_health", "--usage-dir", str(empty_dir))
        assert result.returncode == 0
