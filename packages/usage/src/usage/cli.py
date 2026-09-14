"""usage-query CLI entry point.

Routes queries through named views over a fixed local input set.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from usage import contract_check, input_snapshot

AVAILABLE_VIEWS = ("capture_health",)


def _capture_health(
    paths: list[Path],
    digest: str,
) -> dict:
    """Return a minimal typed empty result for capture_health.

    The real column contract is delivered in ST-0244.
    """
    return {"view": "capture_health", "rows": []}


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

    # Route to view.
    if args.view == "capture_health":
        result = _capture_health(paths, digest)

    print(json.dumps(result))
    sys.exit(0)
