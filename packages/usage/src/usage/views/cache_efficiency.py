"""cache_efficiency view — per-session cache signals with null preservation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usage import accounting

if TYPE_CHECKING:
    from usage.preflight import PreflightResult


CACHE_COLUMNS = (
    "reported_cache_read",
    "reported_cache_write",
    "cache_miss_turns",
    "cache_miss_input_tokens",
    "late_early_input_ratio",
)


def cache_efficiency(preflight_result: PreflightResult | None) -> dict:
    if preflight_result is None:
        return {"view": "cache_efficiency", "rows": []}

    conn = preflight_result.conn

    accounting.select_latest_snapshots(conn)

    unknown = accounting.check_unknown_clis(conn)
    if unknown:
        return {"error": "unknown_cli", "values": sorted(unknown)}

    accounting.build_session_roots(conn)
    accounting.build_session_contributions(conn)

    cache_cols = ", ".join(f'"{c}"' for c in CACHE_COLUMNS)
    rows = conn.execute(
        f"SELECT root_session_id AS session_id, cli, provider, model, "
        f"{cache_cols} "
        "FROM session_contributions "
        "ORDER BY cli, root_session_id, record_id"
    ).fetchall()

    col_names = ["session_id", "cli", "provider", "model", *CACHE_COLUMNS]
    return {
        "view": "cache_efficiency",
        "rows": [dict(zip(col_names, r)) for r in rows],
    }
