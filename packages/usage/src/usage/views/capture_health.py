"""capture_health view — report health of captured JSONL input.

Queries the DuckDB relations in a :class:`~usage.preflight.PreflightResult`
to produce a typed summary of valid records and failures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from usage.preflight import PreflightResult


def capture_health(
    preflight_result: PreflightResult | None,
    *,
    diagnostic: bool = False,
) -> dict:
    """Build the capture_health view output.

    Parameters
    ----------
    preflight_result:
        Result from :func:`usage.preflight.run_preflight`, or ``None``
        when the input directory was empty.
    diagnostic:
        When ``True``, the output includes ``diagnostic_label`` and is
        marked as informational only.

    Returns
    -------
    dict
        Typed JSON-serialisable summary.
    """
    if preflight_result is None:
        result: dict = {
            "view": "capture_health",
            "total_lines": 0,
            "valid_count": 0,
            "failure_count": 0,
            "has_failures": False,
            "failures_by_code": [],
            "failures_by_file": [],
            "diagnostic": diagnostic,
        }
        if diagnostic:
            result["diagnostic_label"] = "incomplete"
        return result

    conn = preflight_result.conn
    valid_count = preflight_result.valid_count
    failure_count = preflight_result.failure_count

    # Query failures grouped by code.
    by_code_rows = conn.execute(
        "SELECT _failure_code AS code, COUNT(*) AS count "
        "FROM preflight_failure "
        "GROUP BY _failure_code "
        "ORDER BY count DESC"
    ).fetchall()
    failures_by_code = [{"code": row[0], "count": row[1]} for row in by_code_rows]

    # Query failures grouped by source file.
    by_file_rows = conn.execute(
        "SELECT _source_file AS file, COUNT(*) AS count "
        "FROM preflight_failure "
        "GROUP BY _source_file "
        "ORDER BY file"
    ).fetchall()
    failures_by_file = [{"file": row[0], "count": row[1]} for row in by_file_rows]

    result = {
        "view": "capture_health",
        "total_lines": valid_count + failure_count,
        "valid_count": valid_count,
        "failure_count": failure_count,
        "has_failures": failure_count > 0,
        "failures_by_code": failures_by_code,
        "failures_by_file": failures_by_file,
        "diagnostic": diagnostic,
    }
    if diagnostic:
        result["diagnostic_label"] = "incomplete"
    return result
