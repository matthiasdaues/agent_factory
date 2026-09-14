"""Result Adapters — project published views as table, JSON, relation, or Arrow."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import duckdb
    import pyarrow


SUPPORTED_FORMATS = frozenset({"table", "json", "relation", "arrow", "parquet"})
REJECTED_FORMATS = frozenset({"pandas", "polars"})


def validate_format(fmt: str) -> str | None:
    """Return an error message if *fmt* is unsupported, else None."""
    if fmt in REJECTED_FORMATS:
        return f"unsupported format: {fmt}"
    if fmt not in SUPPORTED_FORMATS:
        return f"unknown format: {fmt}. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
    return None


def to_json(result: dict) -> str:
    """Serialise the view result dict to JSON with explicit nulls."""
    import json
    return json.dumps(result, default=str)


def to_table(result: dict) -> str:
    """Format the view result dict as an aligned text table."""
    rows = result.get("rows", [])
    if not rows:
        return f"({result.get('view', 'view')}: 0 rows)"

    cols = list(rows[0].keys())
    str_rows = [[str(r.get(c, "")) if r.get(c) is not None else "NULL" for c in cols] for r in rows]
    widths = [max(len(c), *(len(sr[i]) for sr in str_rows)) for i, c in enumerate(cols)]

    header = "  ".join(c.ljust(w) for c, w in zip(cols, widths))
    sep = "  ".join("-" * w for w in widths)
    body = "\n".join(
        "  ".join(v.ljust(w) for v, w in zip(sr, widths))
        for sr in str_rows
    )
    return f"{header}\n{sep}\n{body}\n\n({len(rows)} row{'s' if len(rows) != 1 else ''})"


def to_relation(
    conn: duckdb.DuckDBPyConnection,
    view_name: str,
) -> duckdb.DuckDBPyRelation:
    """Return the DuckDB relation for *view_name* directly."""
    return conn.sql(f'SELECT * FROM "{view_name}"')


def to_arrow(
    conn: duckdb.DuckDBPyConnection,
    view_name: str,
) -> Any:
    """Convert *view_name* to a PyArrow Table preserving schema and nulls.

    Raises ImportError when PyArrow is not installed.
    """
    try:
        import pyarrow as _pa  # noqa: F841
    except ImportError:
        raise ImportError(
            "pyarrow is required for Arrow format. "
            "Install with: pip install usage[arrow]"
        ) from None
    rel = to_relation(conn, view_name)
    return rel.arrow()
