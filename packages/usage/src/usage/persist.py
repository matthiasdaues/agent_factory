"""Shared DuckDB persistence — atomic export of in-memory views to a .duckdb file."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import duckdb

_EXCLUDE = {"latest_run_snapshots": "(_snapshot_rank)"}


def _escape_path(p: Path) -> str:
    """Escape a filesystem path for use in a DuckDB SQL string literal."""
    return str(p).replace("'", "''")


def persist_to_duckdb(conn: duckdb.DuckDBPyConnection, dest: Path) -> int:
    """Atomically materialize in-memory views as tables in *dest*.

    Writes to a temporary sibling file and replaces *dest* only on
    success, so a crash mid-export never destroys the prior file.

    Returns the number of tables written.
    """
    dest = dest.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path_str = tempfile.mkstemp(
        suffix=".duckdb.tmp",
        dir=str(dest.parent),
    )
    os.close(fd)
    Path(tmp_path_str).unlink()

    try:
        conn.execute(f"ATTACH '{_escape_path(Path(tmp_path_str))}' AS export_db")

        objects = conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'main' "
            "AND table_name NOT LIKE '\\_%' ESCAPE '\\'"
        ).fetchall()

        for (name,) in objects:
            exc = _EXCLUDE.get(name)
            exc_clause = f" EXCLUDE {exc}" if exc else ""
            conn.execute(
                f'CREATE TABLE export_db."{name}" AS '
                f'SELECT *{exc_clause} FROM main."{name}"'
            )

        conn.execute("DETACH export_db")
        os.replace(tmp_path_str, str(dest))
        return len(objects)

    except BaseException:
        tmp = Path(tmp_path_str)
        if tmp.exists():
            tmp.unlink()
        raise
