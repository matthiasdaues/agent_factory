"""usage-query CLI entry point.

Routes queries through named views over a fixed local input set.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from usage import contract_check, input_snapshot, preflight

AVAILABLE_VIEWS = ("capture_health",)


def _capture_health(
    paths: list[Path],
    digest: str,
    preflight_result: preflight.PreflightResult | None = None,
) -> dict:
    """Return a minimal typed result for capture_health.

    The real column contract is delivered in ST-0244.  For now include
    preflight summary when available.
    """
    result: dict = {"view": "capture_health", "rows": []}
    if preflight_result is not None:
        result["preflight"] = {
            "valid_count": preflight_result.valid_count,
            "failure_count": preflight_result.failure_count,
            "has_failures": preflight_result.has_failures,
        }
    return result


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

    args = parser.parse_args()

    # Validate view name.
    if args.view not in AVAILABLE_VIEWS:
        available = ", ".join(AVAILABLE_VIEWS)
        print(
            f"unknown view '{args.view}'. Available views: {available}",
            file=sys.stderr,
        )
        sys.exit(2)

    # Validate directory exists.
    usage_dir = Path(args.usage_dir)
    if not usage_dir.is_dir():
        print(
            f"directory not found: {args.usage_dir}",
            file=sys.stderr,
        )
        sys.exit(2)

    # Take input snapshot.
    paths, digest = input_snapshot.snapshot(usage_dir)

    # Run contract check on each selected file (Python import, not subprocess).
    if paths:
        file_args = [str(p) for p in paths]
        rc = contract_check.main(file_args)
        if rc != 0:
            sys.exit(rc)

    # Run operational preflight on selected files.
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

    # Route to view.
    if args.view == "capture_health":
        result = _capture_health(paths, digest, preflight_result)

    print(json.dumps(result))
    sys.exit(0)
