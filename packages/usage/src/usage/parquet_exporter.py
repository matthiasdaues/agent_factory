"""Parquet Exporter — atomic, attributable Parquet output from published views."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import duckdb

QUERY_MODEL_VERSION = "v1"


def export_parquet(
    conn: duckdb.DuckDBPyConnection,
    view_name: str,
    dest: Path,
    *,
    input_digest: str = "",
) -> None:
    """Export *view_name* as atomic, attributable Parquet.

    1. Write to a temporary sibling of *dest*.
    2. Round-trip verify rows and schema.
    3. Record provenance metadata.
    4. Atomically replace *dest* via ``os.rename``.

    Raises RuntimeError on verification failure.
    Raises ImportError when PyArrow is not installed.
    """
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        raise ImportError(
            "pyarrow is required for Parquet export. "
            "Install with: pip install usage[arrow]"
        ) from None

    rel = conn.sql(f'SELECT * FROM "{view_name}"')
    source_table = rel.arrow()

    dest = dest.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path_str = tempfile.mkstemp(
        suffix=".parquet.tmp",
        dir=str(dest.parent),
    )
    os.close(fd)
    tmp_path = Path(tmp_path_str)

    try:
        metadata = {
            b"query_model_version": QUERY_MODEL_VERSION.encode(),
            b"input_digest": input_digest.encode(),
        }
        existing_meta = source_table.schema.metadata or {}
        merged = {**existing_meta, **metadata}
        attributed = source_table.replace_schema_metadata(merged)

        pq.write_table(attributed, str(tmp_path))

        roundtrip = pq.read_table(str(tmp_path))
        if roundtrip.num_rows != source_table.num_rows:
            raise RuntimeError(
                f"row count mismatch: wrote {source_table.num_rows}, "
                f"read back {roundtrip.num_rows}"
            )
        if roundtrip.schema.remove_metadata() != source_table.schema.remove_metadata():
            raise RuntimeError("schema mismatch after round-trip")

        os.rename(str(tmp_path), str(dest))

    except BaseException:
        if tmp_path.exists():
            tmp_path.unlink()
        raise
