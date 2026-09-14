"""usage-query CLI entry point.

Routes queries through named views over a fixed local input set.
"""

from __future__ import annotations

import argparse
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
        help="Output format: json (default), table, relation, arrow.",
    )

    args = parser.parse_args()

    fmt_err = adapters.validate_format(args.output_format)
    if fmt_err:
        print(fmt_err, file=sys.stderr)
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

    if args.output_format == "json":
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


def _exit_on_unknown_cli(result: dict) -> None:
    if "error" in result and result["error"] == "unknown_cli":
        values = ", ".join(result["values"])
        print(f"unsupported CLI: {values}", file=sys.stderr)
        sys.exit(1)
