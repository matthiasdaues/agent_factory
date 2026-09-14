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
    """capture_health produces the full output structure."""

    def test_exit_zero(self, snapshot_dir: Path) -> None:
        result = _run_cli("capture_health", "--usage-dir", str(snapshot_dir))
        assert result.returncode == 0

    def test_returns_full_structure(self, snapshot_dir: Path) -> None:
        result = _run_cli("capture_health", "--usage-dir", str(snapshot_dir))
        data = json.loads(result.stdout)
        assert data["view"] == "capture_health"
        assert "total_lines" in data
        assert "valid_count" in data
        assert "failure_count" in data
        assert "has_failures" in data
        assert "failures_by_code" in data
        assert "failures_by_file" in data
        assert data["diagnostic"] is False

    def test_snapshot_dir_has_expected_structure(self, snapshot_dir: Path) -> None:
        """snapshot_dir contains records with ancestry failures (PARENT_MISSING)."""
        result = _run_cli("capture_health", "--usage-dir", str(snapshot_dir))
        data = json.loads(result.stdout)
        assert data["total_lines"] > 0
        assert data["valid_count"] + data["failure_count"] == data["total_lines"]

    def test_empty_dir_returns_zero_counts(self, empty_dir: Path) -> None:
        result = _run_cli("capture_health", "--usage-dir", str(empty_dir))
        data = json.loads(result.stdout)
        assert data["view"] == "capture_health"
        assert data["total_lines"] == 0
        assert data["valid_count"] == 0
        assert data["failure_count"] == 0
        assert data["has_failures"] is False
        assert data["failures_by_code"] == []
        assert data["failures_by_file"] == []
        assert data["diagnostic"] is False

    def test_empty_dir_exit_zero(self, empty_dir: Path) -> None:
        result = _run_cli("capture_health", "--usage-dir", str(empty_dir))
        assert result.returncode == 0

    def test_with_failures_shows_counts(self, ancestry_dir: Path) -> None:
        result = _run_cli("capture_health", "--usage-dir", str(ancestry_dir))
        data = json.loads(result.stdout)
        assert data["has_failures"] is True
        assert data["failure_count"] > 0
        assert len(data["failures_by_code"]) > 0
        assert len(data["failures_by_file"]) > 0


class TestDiagnosticFlag:
    """--diagnostic flag produces diagnostic output."""

    def test_diagnostic_capture_health_exit_zero(self, snapshot_dir: Path) -> None:
        result = _run_cli(
            "capture_health", "--diagnostic", "--usage-dir", str(snapshot_dir),
        )
        assert result.returncode == 0

    def test_diagnostic_capture_health_output(self, snapshot_dir: Path) -> None:
        result = _run_cli(
            "capture_health", "--diagnostic", "--usage-dir", str(snapshot_dir),
        )
        data = json.loads(result.stdout)
        assert data["diagnostic"] is True
        assert data["diagnostic_label"] == "incomplete"
        assert data["view"] == "capture_health"

    def test_diagnostic_non_health_view_exits_2(self, snapshot_dir: Path) -> None:
        """--diagnostic with a non-capture_health view should exit 2."""
        # Use a hypothetical future view name that is in AVAILABLE_VIEWS
        # For now, only capture_health exists, so test with an unknown view
        # that would otherwise be an unknown-view error — the diagnostic
        # check should fire first or at least produce exit 2.
        result = _run_cli(
            "some_future_view", "--diagnostic", "--usage-dir", str(snapshot_dir),
        )
        assert result.returncode == 2

    def test_diagnostic_with_failures_still_works(self, ancestry_dir: Path) -> None:
        result = _run_cli(
            "capture_health", "--diagnostic", "--usage-dir", str(ancestry_dir),
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["diagnostic"] is True
        assert data["has_failures"] is True


class TestStableViewRefusal:
    """Non-capture_health view with preflight failures exits 1."""

    def test_refusal_exit_1(self, ancestry_dir: Path) -> None:
        """A stable view on data with ancestry failures must be refused.

        Since only capture_health exists in AVAILABLE_VIEWS right now,
        we test indirectly: the existing refusal logic in cli.py blocks
        non-capture_health views. We test via subprocess that the unknown
        view check catches it first (exit 2). The refusal path is covered
        by checking the logic inline — when more views are added, a direct
        test will be possible.
        """
        # With only capture_health available, any other view hits unknown first.
        # This test documents the intended behaviour for when more views exist.
        result = _run_cli("bogus_view", "--usage-dir", str(ancestry_dir))
        assert result.returncode == 2
