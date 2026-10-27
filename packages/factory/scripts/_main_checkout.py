"""Find the main checkout from a linked worktree (BUG-0103).

The installed factory under .agent-factory/ is ignored by git, so only the
main checkout has it. A linked worktree reaches it there. scope-lint,
concern-lint, and link-check share these helpers.
"""

from __future__ import annotations

import functools
import subprocess
from pathlib import Path


@functools.lru_cache(maxsize=None)
def main_checkout(worktree_root: Path) -> Path | None:
    """Return the main checkout of the linked worktree at worktree_root.

    Returns None in the main checkout itself, outside a git repository, and
    when worktree_root is a subfolder of a checkout: there .agent-factory is
    a project folder, not the installed copy.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(worktree_root), "rev-parse", "--show-toplevel", "--git-common-dir"],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        return None
    lines = result.stdout.splitlines()
    if result.returncode != 0 or len(lines) != 2:
        return None
    toplevel = Path(lines[0]).resolve()
    if toplevel != worktree_root.resolve():
        return None
    main_root = (worktree_root / lines[1]).resolve().parent
    return None if main_root == toplevel else main_root


def installed_copy_in_main_checkout(target: Path) -> Path | None:
    """Map a path under .agent-factory/ to the main checkout's copy."""
    parts = target.parts
    if ".agent-factory" not in parts:
        return None
    index = parts.index(".agent-factory")
    main_root = main_checkout(Path(*parts[:index]))
    return None if main_root is None else main_root.joinpath(*parts[index:])
