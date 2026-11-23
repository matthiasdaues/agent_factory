#!/usr/bin/env python3
"""Select the test files that a set of changed paths affects.

The run-tests pre-commit hook passes the staged paths. The selector prints
one test file per line. It prints `tests` when a change needs the whole
suite, and nothing when no test is affected.

The rules, in order:

- `tests/conftest.py`, `pyproject.toml` and `uv.lock` affect every test.
- A changed test file selects itself.
- A changed fixture under `tests/fixtures/<folder>/` selects the test files
  that name `<folder>`.
- Another changed `.py` file under `tests/` selects the test files that
  name its module.
- A changed script under `packages/factory/scripts/` selects the test files
  that name the script. A changed `.py` library also selects the tests of
  every script that imports it, directly or through another library.
- Any changed script also selects the test files that list the whole
  scripts folder.

A name counts only as a whole token: `dispatch` does not match
`dispatch_lib` or `dispatch-ledger`. A test that reaches a script by a
computed name is not found. The full suite at push time covers that gap.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SCRIPTS = "packages/factory/scripts/"
FIXTURES = "tests/fixtures/"
WHOLE_SUITE = {"tests/conftest.py", "pyproject.toml", "uv.lock"}
SWEEP_RE = re.compile(r"SCRIPTS\w*\.(iterdir|r?glob)\(")


def _token_re(name: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])")


def _imported_by(root: Path, module: str) -> set[str]:
    """Return the script names that import *module*, directly or not."""
    found: set[str] = set()
    pending = [module]
    while pending:
        current = pending.pop()
        import_re = re.compile(rf"^\s*(from\s+{re.escape(current)}\s+import|import\s+{re.escape(current)}\b)", re.M)
        for script in sorted((root / SCRIPTS).iterdir()):
            if not script.is_file() or script.name in found:
                continue
            if import_re.search(script.read_text(encoding="utf-8", errors="replace")):
                found.add(script.name)
                if script.suffix == ".py":
                    pending.append(script.stem)
    return found


def select(root: Path, paths: list[str]) -> list[str]:
    if any(path in WHOLE_SUITE or path.endswith("/conftest.py") for path in paths):
        return ["tests"]
    test_files = {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((root / "tests").rglob("test_*.py"))
    }
    selected: set[str] = set()
    names: set[str] = set()
    for path in paths:
        name = Path(path).name
        if path.startswith("tests/") and name.startswith("test_") and name.endswith(".py"):
            selected.add(path)
        elif path.startswith(FIXTURES):
            names.add(path[len(FIXTURES):].split("/", 1)[0])
        elif path.startswith("tests/") and name.endswith(".py"):
            names.add(Path(name).stem)
        elif path.startswith(SCRIPTS) and "/" not in path[len(SCRIPTS):]:
            names.add(name)
            if name.endswith(".py"):
                names.add(Path(name).stem)
                names |= _imported_by(root, Path(name).stem)
            selected |= {test for test, text in test_files.items() if SWEEP_RE.search(text)}
    for name in names:
        pattern = _token_re(name)
        selected |= {test for test, text in test_files.items() if pattern.search(text)}
    return sorted(selected)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("paths", nargs="*", help="changed paths, relative to the root")
    args = parser.parse_args()
    for test in select(args.root.resolve(), args.paths):
        print(test)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
