"""Unit tests for usage.parquet_exporter — export_parquet."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from usage.parquet_exporter import export_parquet


def _make_pyarrow_mocks(*, roundtrip_rows=3, roundtrip_schema="test_schema"):
    """Build mock pyarrow + pyarrow.parquet and a matching source table."""
    mock_pa = MagicMock()
    mock_pq = MagicMock()
    mock_pa.parquet = mock_pq

    source_table = MagicMock()
    source_table.num_rows = 3
    source_table.schema.metadata = None
    source_table.schema.remove_metadata.return_value = "test_schema"
    source_table.replace_schema_metadata.return_value = source_table

    roundtrip = MagicMock()
    roundtrip.num_rows = roundtrip_rows
    roundtrip.schema.remove_metadata.return_value = roundtrip_schema
    mock_pq.read_table.return_value = roundtrip

    conn = MagicMock()
    conn.sql.return_value.arrow.return_value = source_table

    return mock_pa, mock_pq, conn


class TestExportParquet:
    def test_import_error_when_no_pyarrow(self):
        conn = MagicMock()
        with patch.dict("sys.modules", {"pyarrow": None, "pyarrow.parquet": None}):
            with pytest.raises(ImportError, match="pyarrow"):
                export_parquet(conn, "v", Path("/tmp/out.parquet"))

    def test_happy_path(self, tmp_path):
        mock_pa, mock_pq, conn = _make_pyarrow_mocks()
        dest = tmp_path / "out.parquet"
        with patch.dict("sys.modules", {"pyarrow": mock_pa, "pyarrow.parquet": mock_pq}):
            export_parquet(conn, "test_view", dest, input_digest="abc")
        assert dest.exists()
        mock_pq.write_table.assert_called_once()
        mock_pq.read_table.assert_called_once()

    def test_row_count_mismatch_cleans_up(self, tmp_path):
        mock_pa, mock_pq, conn = _make_pyarrow_mocks(roundtrip_rows=999)
        dest = tmp_path / "out.parquet"
        with patch.dict("sys.modules", {"pyarrow": mock_pa, "pyarrow.parquet": mock_pq}):
            with pytest.raises(RuntimeError, match="row count mismatch"):
                export_parquet(conn, "v", dest)
        assert not dest.exists()
        assert not any(f.suffix == ".tmp" for f in tmp_path.iterdir())

    def test_schema_mismatch_cleans_up(self, tmp_path):
        mock_pa, mock_pq, conn = _make_pyarrow_mocks(roundtrip_schema="different")
        dest = tmp_path / "out.parquet"
        with patch.dict("sys.modules", {"pyarrow": mock_pa, "pyarrow.parquet": mock_pq}):
            with pytest.raises(RuntimeError, match="schema mismatch"):
                export_parquet(conn, "v", dest)
        assert not any(f.suffix == ".tmp" for f in tmp_path.iterdir())
