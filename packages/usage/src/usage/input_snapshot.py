"""Snapshot top-level JSONL files in a directory.

Resolves the directory to an absolute path, selects only top-level
*.jsonl files (subdirectories excluded), sorts filenames by unsigned
UTF-8 byte order, and returns a new list of absolute paths plus a
SHA-256 content digest.  A new list is created per invocation.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def snapshot(directory: str | Path) -> tuple[list[Path], str]:
    """Take a snapshot of top-level JSONL files in *directory*.

    Returns (paths, digest) where *paths* is a sorted list of absolute
    ``Path`` objects and *digest* is the SHA-256 hex string over sorted
    filenames, each newline-terminated.
    """
    resolved = Path(directory).resolve()

    names: list[str] = [
        entry.name
        for entry in resolved.iterdir()
        if entry.is_file() and entry.suffix == ".jsonl"
    ]

    names.sort(key=lambda n: n.encode("utf-8"))

    digest_input = "".join(f"{n}\n" for n in names).encode("utf-8")
    digest = hashlib.sha256(digest_input).hexdigest()

    paths = [resolved / n for n in names]
    return paths, digest
