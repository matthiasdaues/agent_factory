#!/usr/bin/env python3
"""Compatibility launcher for the packaged Agent Factory orchestrator."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    package_src = Path(__file__).resolve().parent
    sys.path.insert(0, str(package_src))
    from agent_factory_orchestrator.cli import main as package_main

    return package_main()


if __name__ == "__main__":
    sys.exit(main())
