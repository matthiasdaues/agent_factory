"""usage_by_dimension view — dimensional totals over session contributions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usage import accounting

if TYPE_CHECKING:
    from usage.preflight import PreflightResult


SUPPORTED_DIMENSIONS: dict[str, str] = {
    "time": "recorded_at",
    "project": "project_id",
    "cli": "cli",
    "provider": "provider",
    "model": "model",
    "agent": "agent",
    "branch": "branch",
    "exit_status": "exit_status",
}

VALID_GRANULARITIES = frozenset({"none", "hour", "day", "week", "month"})

TIME_TRUNC_SQL = {
    "hour": "DATE_TRUNC('hour', recorded_at)",
    "day": "DATE_TRUNC('day', recorded_at)",
    "week": "DATE_TRUNC('week', recorded_at)",
    "month": "DATE_TRUNC('month', recorded_at)",
}


def _check_dimension_list(dimensions: list[str]) -> str | None:
    """Validate individual dimension names for duplicates and support."""
    seen: set[str] = set()
    for d in dimensions:
        if d not in SUPPORTED_DIMENSIONS:
            return f"unsupported dimension: {d}"
        if d in seen:
            return f"duplicate dimension: {d}"
        seen.add(d)
    return None


def _validate(
    dimensions: list[str] | None,
    granularity: str,
) -> str | None:
    """Return an error message string, or None if valid."""
    if granularity not in VALID_GRANULARITIES:
        return f"unsupported granularity: {granularity}"

    if not dimensions:
        return None

    err = _check_dimension_list(dimensions)
    if err:
        return err

    if "time" in dimensions and granularity == "none":
        return "time dimension requires a granularity other than none"

    return None


def _aggregate_total(conn) -> list[dict]:
    """Return a single aggregated row when no dimensions are specified."""
    rows = conn.execute(
        "SELECT SUM(normalized_input) AS normalized_input, "
        "SUM(normalized_output) AS normalized_output, "
        "SUM(normalized_total) AS normalized_total "
        "FROM session_contributions"
    ).fetchall()
    r = rows[0]
    return [
        {
            "normalized_input": r[0] or 0,
            "normalized_output": r[1] or 0,
            "normalized_total": r[2] or 0,
        }
    ]


def _build_dimension_clause(d: str, granularity: str) -> tuple[str, str, str]:
    """Return (select_expr, group_expr, col_name) for one dimension."""
    if d == "time":
        expr = TIME_TRUNC_SQL[granularity]
        return f"{expr} AS time_bucket", expr, "time_bucket"
    col = SUPPORTED_DIMENSIONS[d]
    return f'"{col}"', f'"{col}"', col


def _aggregate_grouped(
    conn, dimensions: list[str], granularity: str
) -> tuple[list[str], list[tuple]]:
    """Run a GROUP BY query over the given dimensions and return (col_names, rows)."""
    select_parts: list[str] = []
    group_parts: list[str] = []
    col_names: list[str] = []

    for d in dimensions:
        sel, grp, name = _build_dimension_clause(d, granularity)
        select_parts.append(sel)
        group_parts.append(grp)
        col_names.append(name)

    select_str = ", ".join(select_parts)
    group_str = ", ".join(group_parts)

    query = (
        f"SELECT {select_str}, "
        "SUM(normalized_input) AS normalized_input, "
        "SUM(normalized_output) AS normalized_output, "
        "SUM(normalized_total) AS normalized_total "
        f"FROM session_contributions "
        f"GROUP BY {group_str} "
        f"ORDER BY {group_str}"
    )
    all_cols = col_names + ["normalized_input", "normalized_output", "normalized_total"]
    return all_cols, conn.execute(query).fetchall()


def _prepare_contributions(conn) -> list[str] | None:
    """Build accounting views and check for unknown CLIs.

    Returns sorted unknown CLI names, or None if all CLIs are known.
    """
    accounting.select_latest_snapshots(conn)
    unknown = accounting.check_unknown_clis(conn)
    if unknown:
        return sorted(unknown)
    accounting.build_session_roots(conn)
    accounting.build_session_contributions(conn)
    return None


def usage_by_dimension(
    preflight_result: PreflightResult | None,
    *,
    dimensions: list[str] | None = None,
    granularity: str = "none",
) -> dict:
    if preflight_result is None:
        return {"view": "usage_by_dimension", "rows": []}

    err = _validate(dimensions, granularity)
    if err:
        return {"error": "validation", "message": err}

    unknown = _prepare_contributions(preflight_result.conn)
    if unknown:
        return {"error": "unknown_cli", "values": unknown}

    if not dimensions:
        result_rows = _aggregate_total(preflight_result.conn)
        return {
            "view": "usage_by_dimension",
            "dimensions": [],
            "granularity": granularity,
            "rows": result_rows,
        }

    all_cols, raw_rows = _aggregate_grouped(
        preflight_result.conn, dimensions, granularity
    )
    return {
        "view": "usage_by_dimension",
        "dimensions": dimensions,
        "granularity": granularity,
        "rows": [dict(zip(all_cols, r)) for r in raw_rows],
    }
