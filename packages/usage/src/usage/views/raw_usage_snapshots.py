"""raw_usage_snapshots view — all valid snapshots with evidence identity."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from usage.preflight import PreflightResult


def raw_usage_snapshots(preflight_result: PreflightResult | None) -> dict:
    if preflight_result is None:
        return {"view": "raw_usage_snapshots", "rows": []}

    conn = preflight_result.conn

    cols = conn.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'preflight_valid' ORDER BY ordinal_position"
    ).fetchall()
    col_names = [c[0] for c in cols]

    rows = conn.execute(
        "SELECT * FROM preflight_valid ORDER BY _source_file, _line_number"
    ).fetchall()

    return {
        "view": "raw_usage_snapshots",
        "rows": [dict(zip(col_names, r)) for r in rows],
    }
