"""latest_run_snapshots view — one snapshot per logical run."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usage import accounting

if TYPE_CHECKING:
    from usage.preflight import PreflightResult


def latest_run_snapshots(preflight_result: PreflightResult | None) -> dict:
    if preflight_result is None:
        return {"view": "latest_run_snapshots", "rows": []}

    conn = preflight_result.conn

    accounting.select_latest_snapshots(conn)

    unknown = accounting.check_unknown_clis(conn)
    if unknown:
        return {"error": "unknown_cli", "values": sorted(unknown)}

    cols = conn.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'latest_run_snapshots' "
        "AND column_name != '_snapshot_rank' "
        "ORDER BY ordinal_position"
    ).fetchall()
    col_names = [c[0] for c in cols]
    select = ", ".join(f'"{c}"' for c in col_names)

    rows = conn.execute(
        f"SELECT {select} FROM latest_run_snapshots ORDER BY cli, session_id, record_id"
    ).fetchall()

    return {
        "view": "latest_run_snapshots",
        "rows": [dict(zip(col_names, r)) for r in rows],
    }
