"""canonical_session_usage view — per-CLI canonical session usage.

Applies conservation rules to deduplicated run snapshots, producing
one row per root session with aggregated normalised token counts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from usage import accounting

if TYPE_CHECKING:
    from usage.preflight import PreflightResult


def canonical_session_usage(preflight_result: PreflightResult) -> dict:
    """Build the canonical_session_usage view output.

    Parameters
    ----------
    preflight_result:
        Result from :func:`usage.preflight.run_preflight`.

    Returns
    -------
    dict
        ``{"view": "canonical_session_usage", "rows": [...]}`` on success,
        or ``{"error": "unknown_cli", "values": [...]}`` when unknown
        CLIs are present in the input.
    """
    conn = preflight_result.conn

    accounting.select_latest_snapshots(conn)

    unknown = accounting.check_unknown_clis(conn)
    if unknown:
        return {"error": "unknown_cli", "values": sorted(unknown)}

    accounting.build_session_roots(conn)
    accounting.compute_canonical(conn)

    rows = conn.execute(
        "SELECT session_id, cli, normalized_input, normalized_output, "
        "normalized_total FROM canonical_session_usage "
        "ORDER BY cli, session_id"
    ).fetchall()

    return {
        "view": "canonical_session_usage",
        "rows": [
            {
                "session_id": r[0],
                "cli": r[1],
                "normalized_input": r[2],
                "normalized_output": r[3],
                "normalized_total": r[4],
            }
            for r in rows
        ],
    }
