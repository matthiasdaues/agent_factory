"""Accounting Registry — conservation rules and deduplicated session usage.

Maps each known CLI to a conservation strategy and provides functions
that create DuckDB views for latest-snapshot selection, session-root
resolution, and per-CLI usage aggregation.
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
    rows = conn.execute("SELECT DISTINCT cli FROM latest_run_snapshots").fetchall()
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
# Session contributions and usage views
# ---------------------------------------------------------------------------

_CONTRIBUTION_COLS = (
    "record_id",
    "project_id",
    "project_name",
    "normalized_input",
    "normalized_output",
    "normalized_total",
    "cli",
    "session_id",
    "parent_session_id",
    "depth",
    "recorded_at",
    "agent",
    "model",
    "provider",
    "reported_input",
    "reported_output",
    "reported_cache_read",
    "reported_cache_write",
    "usage_granularity",
    "usage_capability",
    "cache_miss_turns",
    "cache_miss_input_tokens",
    "late_early_input_ratio",
    "exit_status",
    "branch",
    "commit_id",
    "_source_file",
    "_line_number",
)

_L_COLS = ", ".join(f'l."{c}"' for c in _CONTRIBUTION_COLS)


def build_session_contributions(conn: duckdb.DuckDBPyConnection) -> None:
    """Create ``session_contributions`` view — one row per contributing run.

    Applies the same conservation filters as ``session_usage``
    but without aggregation, preserving all dimension columns for
    downstream grouping (e.g. ``usage_by_dimension``).
    """
    conn.execute(f"""
        CREATE OR REPLACE VIEW session_contributions AS

        -- claude-code: root + direct children
        SELECT r.root_session_id, {_L_COLS}
        FROM latest_run_snapshots l
        JOIN session_roots r ON l.cli = r.cli AND l.session_id = r.session_id
        WHERE l.cli = 'claude-code'
          AND (l.parent_session_id IS NULL
               OR l.parent_session_id = r.root_session_id)

        UNION ALL

        -- pi: root + all descendants
        SELECT r.root_session_id, {_L_COLS}
        FROM latest_run_snapshots l
        JOIN session_roots r ON l.cli = r.cli AND l.session_id = r.session_id
        WHERE l.cli = 'pi'

        UNION ALL

        -- codex and copilot: inclusive root only
        SELECT r.root_session_id, {_L_COLS}
        FROM latest_run_snapshots l
        JOIN session_roots r ON l.cli = r.cli AND l.session_id = r.session_id
        WHERE l.cli IN ('codex', 'copilot')
          AND l.parent_session_id IS NULL
    """)


def compute_session_usage(conn: duckdb.DuckDBPyConnection) -> None:
    """Create ``session_usage`` view applying per-CLI rules.

    Aggregates ``session_contributions`` by root session.
    """
    build_session_contributions(conn)
    conn.execute("""
        CREATE OR REPLACE VIEW session_usage AS
        SELECT root_session_id AS session_id, cli,
               SUM(normalized_input) AS normalized_input,
               SUM(normalized_output) AS normalized_output,
               SUM(normalized_total) AS normalized_total
        FROM session_contributions
        GROUP BY root_session_id, cli
    """)
