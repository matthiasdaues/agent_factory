"""Accounting Registry — conservation rules and canonical session usage.

Maps each known CLI to a conservation strategy and provides functions
that create DuckDB views for latest-snapshot selection, session-root
resolution, and per-CLI canonical usage aggregation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from usage.registry import KNOWN_CLIS

if TYPE_CHECKING:
    import duckdb

# ---------------------------------------------------------------------------
# Conservation rules registry
# ---------------------------------------------------------------------------

CONSERVATION_RULES: dict[str, str] = {
    "claude-code": "root_and_children",
    "pi": "root_and_descendants",
    **{cli: "inclusive_root" for cli in KNOWN_CLIS - {"claude-code", "pi"}},
}


# ---------------------------------------------------------------------------
# Latest snapshot selection
# ---------------------------------------------------------------------------

def select_latest_snapshots(conn: duckdb.DuckDBPyConnection) -> None:
    """Create ``latest_run_snapshots`` view on *conn*.

    For each logical run ``(cli, session_id, record_id)``, keep the single
    record with the greatest ``_source_file`` (unsigned UTF-8 byte order),
    breaking ties by greatest ``_line_number``.
    """
    conn.execute("""
        CREATE OR REPLACE VIEW latest_run_snapshots AS
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY cli, session_id, record_id
                ORDER BY _source_file DESC, _line_number DESC
            ) AS _snapshot_rank
            FROM preflight_valid
        ) WHERE _snapshot_rank = 1
    """)


# ---------------------------------------------------------------------------
# Unknown CLI check
# ---------------------------------------------------------------------------

def check_unknown_clis(conn: duckdb.DuckDBPyConnection) -> set[str]:
    """Return CLI values in ``latest_run_snapshots`` not in ``KNOWN_CLIS``."""
    rows = conn.execute(
        "SELECT DISTINCT cli FROM latest_run_snapshots"
    ).fetchall()
    found = {r[0] for r in rows}
    return found - KNOWN_CLIS


# ---------------------------------------------------------------------------
# Session roots (recursive CTE)
# ---------------------------------------------------------------------------

def build_session_roots(conn: duckdb.DuckDBPyConnection) -> None:
    """Create ``session_roots`` view mapping each session to its root."""
    conn.execute("""
        CREATE OR REPLACE VIEW session_roots AS
        WITH RECURSIVE roots AS (
            SELECT DISTINCT cli, session_id, session_id AS root_session_id
            FROM latest_run_snapshots
            WHERE parent_session_id IS NULL

            UNION ALL

            SELECT DISTINCT l.cli, l.session_id, r.root_session_id
            FROM latest_run_snapshots l
            JOIN roots r ON l.parent_session_id = r.session_id AND l.cli = r.cli
            WHERE l.parent_session_id IS NOT NULL
        )
        SELECT DISTINCT * FROM roots
    """)


# ---------------------------------------------------------------------------
# Canonical session usage view
# ---------------------------------------------------------------------------

def compute_canonical(conn: duckdb.DuckDBPyConnection) -> None:
    """Create ``canonical_session_usage`` view applying per-CLI rules.

    - claude-code: root + direct children only
    - pi: root + ALL descendants
    - codex, copilot: inclusive root only (children excluded)
    """
    conn.execute("""
        CREATE OR REPLACE VIEW canonical_session_usage AS

        -- claude-code: root + direct children
        SELECT r.root_session_id AS session_id, l.cli,
               SUM(l.normalized_input) AS normalized_input,
               SUM(l.normalized_output) AS normalized_output,
               SUM(l.normalized_total) AS normalized_total
        FROM latest_run_snapshots l
        JOIN session_roots r ON l.cli = r.cli AND l.session_id = r.session_id
        WHERE l.cli = 'claude-code'
          AND (l.parent_session_id IS NULL
               OR l.parent_session_id = r.root_session_id)
        GROUP BY r.root_session_id, l.cli

        UNION ALL

        -- pi: root + all descendants
        SELECT r.root_session_id AS session_id, l.cli,
               SUM(l.normalized_input) AS normalized_input,
               SUM(l.normalized_output) AS normalized_output,
               SUM(l.normalized_total) AS normalized_total
        FROM latest_run_snapshots l
        JOIN session_roots r ON l.cli = r.cli AND l.session_id = r.session_id
        WHERE l.cli = 'pi'
        GROUP BY r.root_session_id, l.cli

        UNION ALL

        -- codex and copilot: inclusive root only
        SELECT r.root_session_id AS session_id, l.cli,
               SUM(l.normalized_input) AS normalized_input,
               SUM(l.normalized_output) AS normalized_output,
               SUM(l.normalized_total) AS normalized_total
        FROM latest_run_snapshots l
        JOIN session_roots r ON l.cli = r.cli AND l.session_id = r.session_id
        WHERE l.cli IN ('codex', 'copilot')
          AND l.parent_session_id IS NULL
        GROUP BY r.root_session_id, l.cli
    """)
