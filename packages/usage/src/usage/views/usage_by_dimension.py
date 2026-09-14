"""usage_by_dimension view — dimensional totals over canonical contributions."""

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


def _validate(
    dimensions: list[str] | None,
    granularity: str,
) -> str | None:
    """Return an error message string, or None if valid."""
    if granularity not in VALID_GRANULARITIES:
        return f"unsupported granularity: {granularity}"

    if not dimensions:
        return None

    seen: set[str] = set()
    for d in dimensions:
        if d not in SUPPORTED_DIMENSIONS:
            return f"unsupported dimension: {d}"
        if d in seen:
            return f"duplicate dimension: {d}"
        seen.add(d)

    if "time" in seen and granularity == "none":
        return "time dimension requires a granularity other than none"

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

    conn = preflight_result.conn

    accounting.select_latest_snapshots(conn)

    unknown = accounting.check_unknown_clis(conn)
    if unknown:
        return {"error": "unknown_cli", "values": sorted(unknown)}

    accounting.build_session_roots(conn)
    accounting.build_canonical_contributions(conn)

    if not dimensions:
        rows = conn.execute(
            "SELECT SUM(normalized_input) AS normalized_input, "
            "SUM(normalized_output) AS normalized_output, "
            "SUM(normalized_total) AS normalized_total "
            "FROM canonical_contributions"
        ).fetchall()
        r = rows[0]
        return {
            "view": "usage_by_dimension",
            "dimensions": [],
            "granularity": granularity,
            "rows": [
                {
                    "normalized_input": r[0] or 0,
                    "normalized_output": r[1] or 0,
                    "normalized_total": r[2] or 0,
                },
            ],
        }

    select_parts: list[str] = []
    group_parts: list[str] = []
    col_names: list[str] = []

    for d in dimensions:
        if d == "time":
            expr = TIME_TRUNC_SQL[granularity]
            select_parts.append(f"{expr} AS time_bucket")
            group_parts.append(expr)
            col_names.append("time_bucket")
        else:
            col = SUPPORTED_DIMENSIONS[d]
            select_parts.append(f'"{col}"')
            group_parts.append(f'"{col}"')
            col_names.append(col)

    select_str = ", ".join(select_parts)
    group_str = ", ".join(group_parts)

    query = (
        f"SELECT {select_str}, "
        "SUM(normalized_input) AS normalized_input, "
        "SUM(normalized_output) AS normalized_output, "
        "SUM(normalized_total) AS normalized_total "
        f"FROM canonical_contributions "
        f"GROUP BY {group_str} "
        f"ORDER BY {group_str}"
    )
    rows = conn.execute(query).fetchall()

    all_cols = col_names + ["normalized_input", "normalized_output", "normalized_total"]
    return {
        "view": "usage_by_dimension",
        "dimensions": dimensions,
        "granularity": granularity,
        "rows": [dict(zip(all_cols, r)) for r in rows],
    }
