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
from usage.views.canonical_session_usage import canonical_session_usage
from usage.views.capture_health import capture_health
from usage.views.latest_run_snapshots import latest_run_snapshots
from usage.views.raw_usage_snapshots import raw_usage_snapshots
from usage.views.usage_by_dimension import usage_by_dimension

AVAILABLE_VIEWS = (
    "capture_health",
    "canonical_session_usage",
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


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="usage-query",
        description="Query published views over local usage JSONL files.",
    )
    parser.add_argument(
        "view",
        help="View name to query.",
    )
    parser.add_argument(
        "--usage-dir",
        default=".agent-factory/usage/",
        help="Directory containing JSONL files (default: .agent-factory/usage/).",
    )
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        default=False,
        help="Run in diagnostic mode (only capture_health, informational output).",
    )
    parser.add_argument(
        "--dimensions",
        default=None,
        help="Comma-separated ordered dimension list for usage_by_dimension.",
    )
    parser.add_argument(
        "--granularity",
        default="none",
        choices=("none", "hour", "day", "week", "month"),
        help="Time granularity for usage_by_dimension (default: none).",
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        default="json",
        help="Output format: json (default), table, relation, arrow, parquet.",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (required for parquet format).",
    )
    parser.add_argument(
        "--persist",
        metavar="PATH",
        default=None,
        help="Materialize pipeline views as tables in a persistent .duckdb file.",
    )

    args = parser.parse_args()

    fmt_err = adapters.validate_format(args.output_format)
    if fmt_err:
        print(fmt_err, file=sys.stderr)
        sys.exit(2)

    if args.output_format == "parquet" and not args.output:
        print("--format parquet requires -o OUTPUT", file=sys.stderr)
        sys.exit(2)

    if args.view not in AVAILABLE_VIEWS:
        available = ", ".join(AVAILABLE_VIEWS)
        print(
            f"unknown view '{args.view}'. Available views: {available}",
            file=sys.stderr,
        )
        sys.exit(2)

    if args.diagnostic and args.view != "capture_health":
        print(
            "diagnostic mode only supports capture_health",
            file=sys.stderr,
        )
        sys.exit(2)

    usage_dir = Path(args.usage_dir)
    if not usage_dir.is_dir():
        root = _find_project_root()
        if root is not None:
            candidate = root / args.usage_dir
            if candidate.is_dir():
                usage_dir = candidate
    if not usage_dir.is_dir():
        print(
            f"directory not found: {args.usage_dir}",
            file=sys.stderr,
        )
        sys.exit(2)

    paths, digest = input_snapshot.snapshot(usage_dir)

    if paths:
        file_args = [str(p) for p in paths]
        rc = contract_check.main(file_args)
        if rc != 0:
            sys.exit(rc)

    preflight_result = None
    if paths:
        preflight_result = preflight.run_preflight(paths)
        if preflight_result.has_failures and args.view != "capture_health":
            print(
                f"preflight: {preflight_result.failure_count} failure(s) "
                f"in {preflight_result.failure_count + preflight_result.valid_count} "
                f"record(s)",
                file=sys.stderr,
            )
            sys.exit(1)

    result = _route(args, preflight_result)

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
    elif args.output_format == "json":
        print(adapters.to_json(result))
    elif args.output_format == "table":
        print(adapters.to_table(result))
    elif args.output_format in ("relation", "arrow"):
        if preflight_result is None:
            print(adapters.to_json(result))
        else:
            print(
                f"format '{args.output_format}' is for programmatic use. "
                "Use the Python API instead.",
                file=sys.stderr,
            )
            print(adapters.to_json(result))

    if args.persist and preflight_result is not None:
        persist_path = args.persist
        root = _find_project_root()
        if root is not None and not Path(persist_path).is_absolute():
            persist_path = str(root / persist_path)
        _persist(preflight_result.conn, persist_path)

    sys.exit(0)


def _route(args: argparse.Namespace, preflight_result) -> dict:
    """Dispatch to the requested view and handle error results."""
    if args.view == "capture_health":
        return capture_health(preflight_result, diagnostic=args.diagnostic)

    if args.view == "canonical_session_usage":
        result = canonical_session_usage(preflight_result)
        _exit_on_unknown_cli(result)
        return result

    if args.view == "raw_usage_snapshots":
        return raw_usage_snapshots(preflight_result)

    if args.view == "latest_run_snapshots":
        result = latest_run_snapshots(preflight_result)
        _exit_on_unknown_cli(result)
        return result

    if args.view == "usage_by_dimension":
        dims = args.dimensions.split(",") if args.dimensions else None
        result = usage_by_dimension(
            preflight_result,
            dimensions=dims,
            granularity=args.granularity,
        )
        if "error" in result:
            if result["error"] == "validation":
                print(result["message"], file=sys.stderr)
                sys.exit(2)
            _exit_on_unknown_cli(result)
        return result

    if args.view == "cache_efficiency":
        result = cache_efficiency(preflight_result)
        _exit_on_unknown_cli(result)
        return result

    raise AssertionError(f"unhandled view: {args.view}")


_VIEW_TO_DUCKDB = {
    "capture_health": None,
    "canonical_session_usage": "canonical_session_usage",
    "raw_usage_snapshots": "preflight_valid",
    "latest_run_snapshots": "latest_run_snapshots",
    "usage_by_dimension": "canonical_contributions",
    "cache_efficiency": "canonical_contributions",
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
    if args.view in ("canonical_session_usage", "usage_by_dimension", "cache_efficiency"):
        accounting.select_latest_snapshots(conn)
        accounting.build_session_roots(conn)
        accounting.build_canonical_contributions(conn)
        if args.view == "canonical_session_usage":
            accounting.compute_canonical(conn)
    elif args.view == "latest_run_snapshots":
        accounting.select_latest_snapshots(conn)


def _exit_on_unknown_cli(result: dict) -> None:
    if "error" in result and result["error"] == "unknown_cli":
        values = ", ".join(result["values"])
        print(f"unsupported CLI: {values}", file=sys.stderr)
        sys.exit(1)


_PERSIST_EXCLUDE = {
    "latest_run_snapshots": "(_snapshot_rank)",
}


def _persist(conn, path_str: str) -> None:
    """Materialize in-memory views as tables in a persistent DuckDB file."""
    dest = Path(path_str)
    if dest.exists():
        dest.unlink()

    conn.execute(f"ATTACH '{dest}' AS export_db")

    objects = conn.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main' "
        "AND table_name NOT LIKE '\\_%' ESCAPE '\\'"
    ).fetchall()

    for (name,) in objects:
        exclude = _PERSIST_EXCLUDE.get(name)
        exc = f" EXCLUDE {exclude}" if exclude else ""
        conn.execute(
            f'CREATE TABLE export_db."{name}" AS '
            f"SELECT *{exc} FROM main.\"{name}\""
        )

    conn.execute("DETACH export_db")
    print(
        f"persisted {len(objects)} table(s) to {dest}",
        file=sys.stderr,
    )
