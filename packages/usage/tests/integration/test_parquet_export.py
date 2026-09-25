"""Integration tests for ST-0248 — Parquet export and dependency check."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_HAS_PYARROW = True
try:
    import pyarrow
    import pyarrow.parquet
except ImportError:
    _HAS_PYARROW = False


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "from usage.cli import main; main()", *args],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture()
def pi_dir(tmp_path: Path) -> Path:
    import shutil

    src = (
        Path(__file__).resolve().parent.parent.parent
        / "fixtures"
        / "multi-cli"
        / "pi_sessions.jsonl"
    )
    shutil.copy(src, tmp_path / "pi.jsonl")
    return tmp_path


# ---------------------------------------------------------------------------
# CLI validation
# ---------------------------------------------------------------------------


class TestParquetCliValidation:
    def test_parquet_without_output_rejected(self, pi_dir: Path) -> None:
        r = _run_cli("session_usage", "--usage-dir", str(pi_dir), "--format", "parquet")
        assert r.returncode == 2
        assert "-o" in r.stderr or "OUTPUT" in r.stderr


# ---------------------------------------------------------------------------
# Parquet export (requires PyArrow)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _HAS_PYARROW, reason="pyarrow not installed")
class TestParquetExport:
    def test_successful_export(self, pi_dir: Path, tmp_path: Path) -> None:
        dest = tmp_path / "out.parquet"
        r = _run_cli(
            "session_usage",
            "--usage-dir",
            str(pi_dir),
            "--format",
            "parquet",
            "-o",
            str(dest),
        )
        assert r.returncode == 0, r.stderr
        assert dest.exists()
        tbl = pyarrow.parquet.read_table(str(dest))
        assert tbl.num_rows == 1

    def test_provenance_metadata(self, pi_dir: Path, tmp_path: Path) -> None:
        dest = tmp_path / "out.parquet"
        _run_cli(
            "session_usage",
            "--usage-dir",
            str(pi_dir),
            "--format",
            "parquet",
            "-o",
            str(dest),
        )
        meta = pyarrow.parquet.read_metadata(str(dest))
        kv = meta.metadata
        assert b"query_model_version" in kv
        assert kv[b"query_model_version"] == b"v1"
        assert b"input_digest" in kv

    def test_atomic_replacement_preserves_prior(
        self, pi_dir: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "out.parquet"
        dest.write_text("prior content")
        from usage.parquet_exporter import export_parquet
        from usage.preflight import run_preflight
        from usage.views.session_usage import session_usage

        paths = sorted(pi_dir.glob("*.jsonl"))
        pf = run_preflight(paths)
        session_usage(pf)
        export_parquet(pf.conn, "session_usage", dest, input_digest="test")
        content = pyarrow.parquet.read_table(str(dest))
        assert content.num_rows == 1


# ---------------------------------------------------------------------------
# Dependency check gate
# ---------------------------------------------------------------------------


class TestDependencyCheck:
    def test_gate_passes(self) -> None:
        script = (
            Path(__file__).resolve().parent.parent.parent
            / "scripts"
            / "usage-dependency-check"
        )
        r = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert r.returncode == 0
        assert "OK" in r.stdout
