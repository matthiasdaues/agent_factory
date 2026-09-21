"""usage-query CLI entry point.

Routes queries through named views over a fixed local input set.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from usage import adapters, contract_check, input_snapshot, preflight
from usage.views.cache_efficiency import cache_efficiency
from usage.views.session_usage import session_usage
from usage.views.capture_health import capture_health
from usage.views.latest_run_snapshots import latest_run_snapshots
from usage.views.raw_usage_snapshots import raw_usage_snapshots
from usage.views.usage_by_dimension import usage_by_dimension

AVAILABLE_VIEWS = (
    "capture_health",
    "session_usage",
    "raw_usage_snapshots",
    "latest_run_snapshots",
    "usage_by_dimension",
    "cache_efficiency",
)


def _find_project_root() -> Path | None:
    """Walk up from cwd to find the directory containing .agent-factory/."""
    current = Path(os.getcwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / ".agent-factory").is_dir():
            return parent
    return None


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Build the argument parser and return parsed args."""
    parser = argparse.ArgumentParser(
        prog="usage-query",
        description="Query published views over local usage JSONL files.",
    )
    parser.add_argument("view", help="View name to query.")
    parser.add_argument(
        "--usage-dir", default=".agent-factory/usage/",
        help="Directory containing JSONL files (default: .agent-factory/usage/).",
    )
    parser.add_argument(
        "--diagnostic", action="store_true", default=False,
        help="Run in diagnostic mode (only capture_health, informational output).",
    )
    parser.add_argument(
        "--dimensions", default=None,
        help="Comma-separated ordered dimension list for usage_by_dimension.",
    )
    parser.add_argument(
        "--granularity", default="none",
        choices=("none", "hour", "day", "week", "month"),
        help="Time granularity for usage_by_dimension (default: none).",
    )
    parser.add_argument(
        "--format", dest="output_format", default="json",
        help="Output format: json (default), table, relation, arrow, parquet.",
    )
    parser.add_argument(
        "-o", "--output", default=None,
        help="Output file path (required for parquet format).",
    )
    parser.add_argument(
        "--persist", metavar="PATH", default=None,
        help="Materialize pipeline views as tables in a persistent .duckdb file.",
    )
    return parser.parse_args(argv)


def _validate_args(args: argparse.Namespace) -> str | None:
    """Return an error message if *args* are invalid, else None."""
    fmt_err = adapters.validate_format(args.output_format)
    if fmt_err:
        return fmt_err
    if args.view not in AVAILABLE_VIEWS:
        available = ", ".join(AVAILABLE_VIEWS)
        return f"unknown view '{args.view}'. Available views: {available}"
    if args.diagnostic and args.view != "capture_health":
        return "diagnostic mode only supports capture_health"
    return _validate_parquet_args(args)


def _validate_parquet_args(args: argparse.Namespace) -> str | None:
    """Return an error message for invalid parquet-specific args, else None."""
    if args.output_format != "parquet":
        return None
    if not args.output:
        return "--format parquet requires -o OUTPUT"
    if args.view == "capture_health":
        return "capture_health does not support Parquet export"
    return None


def _resolve_usage_dir(args: argparse.Namespace) -> Path | None:
    """Resolve --usage-dir to an existing directory, or return None."""
    usage_dir = Path(args.usage_dir)
    if usage_dir.is_dir():
        return usage_dir
    root = _find_project_root()
    if root is not None:
        candidate = root / args.usage_dir
        if candidate.is_dir():
            return candidate
    return None


def _format_and_output(
    args: argparse.Namespace,
    result: dict,
    preflight_result,
    digest: str,
) -> None:
    """Render *result* to stdout in the requested format."""
    if args.output_format == "parquet":
        from usage.parquet_exporter import export_parquet
        _ensure_view_materialized(args, preflight_result)
        export_parquet(
            preflight_result.conn,
            _duckdb_view_name(args.view),
            Path(args.output),
            input_digest=digest,
        )
        print(f"exported to {args.output}", file=sys.stderr)
        return
    if args.output_format == "table":
        print(adapters.to_table(result))
        return
    if args.output_format in ("relation", "arrow") and preflight_result is not None:
        print(
            f"format '{args.output_format}' is for programmatic use. "
            "Use the Python API instead.",
            file=sys.stderr,
        )
    print(adapters.to_json(result))


def _persist_if_requested(args: argparse.Namespace, preflight_result) -> None:
    """Persist pipeline views to a .duckdb file when --persist is given."""
    if not args.persist or preflight_result is None:
        return
    persist_path = args.persist
    root = _find_project_root()
    if root is not None and not Path(persist_path).is_absolute():
        persist_path = str(root / persist_path)
    from usage.persist import persist_to_duckdb
    count = persist_to_duckdb(preflight_result.conn, Path(persist_path))
    print(f"persisted {count} table(s) to {persist_path}", file=sys.stderr)


def _run_preflight(paths, view: str):
    """Run preflight and exit on failure for stable views."""
    if not paths:
        return None
    result = preflight.run_preflight(paths)
    if result.has_failures and view != "capture_health":
        print(
            f"preflight: {result.failure_count} failure(s) "
            f"in {result.failure_count + result.valid_count} record(s)",
            file=sys.stderr,
        )
        sys.exit(1)
    return result


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    err = _validate_args(args)
    if err:
        print(err, file=sys.stderr)
        sys.exit(2)

    usage_dir = _resolve_usage_dir(args)
    if usage_dir is None:
        print(f"directory not found: {args.usage_dir}", file=sys.stderr)
        sys.exit(2)

    paths, digest = input_snapshot.snapshot(usage_dir)

    if paths:
        rc = contract_check.main([str(p) for p in paths])
        if rc != 0:
            sys.exit(rc)

    preflight_result = _run_preflight(paths, args.view)

    result = _route(args, preflight_result)
    _format_and_output(args, result, preflight_result, digest)
    _persist_if_requested(args, preflight_result)
    sys.exit(0)


def _route_usage_by_dimension(args, preflight_result) -> dict:
    """Route for usage_by_dimension with validation error handling."""
    dims = args.dimensions.split(",") if args.dimensions else None
    result = usage_by_dimension(
        preflight_result, dimensions=dims, granularity=args.granularity,
    )
    if "error" in result and result["error"] == "validation":
        print(result["message"], file=sys.stderr)
        sys.exit(2)
    return result


_VIEW_DISPATCH: dict[str, object] = {
    "capture_health": lambda args, pr: capture_health(pr, diagnostic=args.diagnostic),
    "session_usage": lambda args, pr: session_usage(pr),
    "raw_usage_snapshots": lambda args, pr: raw_usage_snapshots(pr),
    "latest_run_snapshots": lambda args, pr: latest_run_snapshots(pr),
    "usage_by_dimension": _route_usage_by_dimension,
    "cache_efficiency": lambda args, pr: cache_efficiency(pr),
}

_VIEWS_WITH_CLI_CHECK = frozenset({
    "session_usage", "latest_run_snapshots",
    "usage_by_dimension", "cache_efficiency",
})


def _route(args: argparse.Namespace, preflight_result) -> dict:
    """Dispatch to the requested view and handle error results."""
    handler = _VIEW_DISPATCH.get(args.view)
    if handler is None:
        raise AssertionError(f"unhandled view: {args.view}")
    result = handler(args, preflight_result)
    if args.view in _VIEWS_WITH_CLI_CHECK:
        _exit_on_unknown_cli(result)
    return result


_VIEW_TO_DUCKDB = {
    "capture_health": None,
    "session_usage": "session_usage",
    "raw_usage_snapshots": "preflight_valid",
    "latest_run_snapshots": "latest_run_snapshots",
    "usage_by_dimension": "session_contributions",
    "cache_efficiency": "session_contributions",
}


def _duckdb_view_name(view: str) -> str:
    name = _VIEW_TO_DUCKDB.get(view)
    if name is None:
        raise ValueError(f"view '{view}' does not support Parquet export")
    return name


def _ensure_view_materialized(args, preflight_result) -> None:
    """Ensure the DuckDB views are built for the requested view."""
    from usage import accounting
    conn = preflight_result.conn
    if args.view in ("session_usage", "usage_by_dimension", "cache_efficiency"):
        accounting.select_latest_snapshots(conn)
        accounting.build_session_roots(conn)
        accounting.build_session_contributions(conn)
        if args.view == "session_usage":
            accounting.compute_session_usage(conn)
    elif args.view == "latest_run_snapshots":
        accounting.select_latest_snapshots(conn)


def _exit_on_unknown_cli(result: dict) -> None:
    if "error" in result and result["error"] == "unknown_cli":
        values = ", ".join(result["values"])
        print(f"unsupported CLI: {values}", file=sys.stderr)
        sys.exit(1)
