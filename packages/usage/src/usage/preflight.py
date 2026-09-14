"""Operational Preflight — classify JSONL lines and validate run ancestry.

Every selected JSONL line lands in exactly one of two DuckDB relations:

  preflight_valid    — records that pass all ancestry checks
  preflight_failure  — records tagged with one of six failure codes

Failure codes (checked in priority order):

  USAGE_ANCESTRY_PARENT_CONFLICT  — snapshots of one logical run disagree
                                    on parent_session_id
  USAGE_ANCESTRY_SELF_PARENT      — parent_session_id == own session_id
  USAGE_ANCESTRY_PARENT_BOUNDARY  — parent session exists under a
                                    different CLI
  USAGE_ANCESTRY_PARENT_MISSING   — parent session not in selected input
  USAGE_ANCESTRY_CYCLE            — directed cycle in parent chain
  USAGE_ANCESTRY_ROOT_COUNT       — CLI has zero or more than one root
"""

from __future__ import annotations

import json
import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb

# ---------------------------------------------------------------------------
# Failure codes
# ---------------------------------------------------------------------------

PARENT_CONFLICT = "USAGE_ANCESTRY_PARENT_CONFLICT"
SELF_PARENT = "USAGE_ANCESTRY_SELF_PARENT"
PARENT_BOUNDARY = "USAGE_ANCESTRY_PARENT_BOUNDARY"
PARENT_MISSING = "USAGE_ANCESTRY_PARENT_MISSING"
CYCLE = "USAGE_ANCESTRY_CYCLE"
ROOT_COUNT = "USAGE_ANCESTRY_ROOT_COUNT"

ALL_FAILURE_CODES: frozenset[str] = frozenset({
    PARENT_CONFLICT,
    SELF_PARENT,
    PARENT_BOUNDARY,
    PARENT_MISSING,
    CYCLE,
    ROOT_COUNT,
})


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PreflightResult:
    """Outcome of operational preflight.

    *conn* holds two relations — ``preflight_valid`` and
    ``preflight_failure`` — queryable via SQL.
    """

    conn: duckdb.DuckDBPyConnection
    has_failures: bool
    valid_count: int
    failure_count: int


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_lines(paths: list[Path]) -> list[dict[str, Any]]:
    """Read every JSONL line from *paths*, annotating with source metadata."""
    records: list[dict[str, Any]] = []
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            for line_no, raw in enumerate(fh, start=1):
                stripped = raw.strip()
                if not stripped:
                    continue
                rec = json.loads(stripped)
                rec["_source_file"] = str(path)
                rec["_line_number"] = line_no
                records.append(rec)
    return records


_NULLABLE_CASTS: dict[str, str] = {
    "parent_session_id": "VARCHAR",
    "reported_cache_read": "BIGINT",
    "reported_cache_write": "BIGINT",
    "cache_miss_turns": "BIGINT",
    "cache_miss_input_tokens": "BIGINT",
    "late_early_input_ratio": "DOUBLE",
    "_failure_code": "VARCHAR",
}


def _coerce_nullable_types(conn: duckdb.DuckDBPyConnection) -> None:
    """Cast columns that ``read_json_auto`` may infer as JSON to their contract types."""
    cols = conn.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = '_staging'"
    ).fetchall()
    alterations = []
    for name, dtype in cols:
        target = _NULLABLE_CASTS.get(name)
        if target and dtype != target:
            alterations.append(
                f'ALTER TABLE _staging ALTER COLUMN "{name}" '
                f"SET DATA TYPE {target}"
            )
    for stmt in alterations:
        conn.execute(stmt)


LineKey = tuple[str, int]  # (_source_file, _line_number)
SessionKey = tuple[str, str]  # (cli, session_id)


def _find_parent_conflicts(
    records: list[dict[str, Any]],
) -> set[LineKey]:
    """Return line keys of records whose logical run has conflicting parents.

    A logical run is identified by ``(cli, session_id, record_id)``.  All
    snapshots of the same run must agree on ``parent_session_id``.
    """
    run_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        key = (rec["cli"], rec["session_id"], rec["record_id"])
        run_groups[key].append(rec)

    conflict_lines: set[LineKey] = set()
    for _key, recs in run_groups.items():
        parents = {r["parent_session_id"] for r in recs}
        if len(parents) > 1:
            for r in recs:
                conflict_lines.add((r["_source_file"], r["_line_number"]))
    return conflict_lines


def _build_session_map(
    records: list[dict[str, Any]],
) -> dict[SessionKey, str | None]:
    """Deduplicate records to one ``(cli, session_id) -> parent_session_id``."""
    session_parent: dict[SessionKey, str | None] = {}
    for rec in records:
        key: SessionKey = (rec["cli"], rec["session_id"])
        if key not in session_parent:
            session_parent[key] = rec["parent_session_id"]
    return session_parent


def _build_session_cli_lookup(
    session_parent: dict[SessionKey, str | None],
) -> dict[str, set[str]]:
    """Map each session_id to the set of CLIs it appears under."""
    lookup: dict[str, set[str]] = defaultdict(set)
    for cli, sid in session_parent:
        lookup[sid].add(cli)
    return lookup


def _detect_cycles(
    session_parent: dict[SessionKey, str | None],
    session_failures: dict[SessionKey, str],
) -> None:
    """Find directed cycles in the parent chain per CLI.

    Only considers sessions not already flagged with a higher-priority
    failure code.  Mutates *session_failures* in place.
    """
    cli_sessions: dict[str, dict[str, str | None]] = defaultdict(dict)
    for (cli, sid), parent in session_parent.items():
        if (cli, sid) not in session_failures:
            cli_sessions[cli][sid] = parent

    for cli, sessions in cli_sessions.items():
        for sid in _find_cycle_members(sessions):
            session_failures[(cli, sid)] = CYCLE


def _find_cycle_members(
    sessions: dict[str, str | None],
) -> set[str]:
    """Return session_ids that participate in a directed cycle.

    Each node has at most one outgoing edge (its parent).  Algorithm is
    iterative path-following with three-colour marking — O(V).
    """
    # 0 = unvisited, 1 = in-progress, 2 = done
    state: dict[str, int] = {}
    in_cycle: set[str] = set()

    for start in sessions:
        if state.get(start, 0) != 0:
            continue
        path: list[str] = []
        current: str | None = start
        while (
            current is not None
            and current in sessions
            and state.get(current, 0) == 0
        ):
            state[current] = 1
            path.append(current)
            current = sessions[current]

        # If we stopped at an in-progress node, everything from that node
        # to the end of *path* forms a cycle.
        if (
            current is not None
            and current in sessions
            and state.get(current) == 1
        ):
            idx = path.index(current)
            for sid in path[idx:]:
                in_cycle.add(sid)

        for sid in path:
            state[sid] = 2

    return in_cycle


def _find_connected_components(
    session_parent: dict[SessionKey, str | None],
) -> list[set[SessionKey]]:
    """Return connected components in the session parent graph per CLI.

    Two sessions belong to the same component when one names the other
    as parent (directly or transitively) under the same CLI.
    """
    children: dict[SessionKey, list[SessionKey]] = defaultdict(list)
    all_keys: set[SessionKey] = set(session_parent.keys())

    for (cli, sid), parent in session_parent.items():
        if parent is not None:
            parent_key: SessionKey = (cli, parent)
            if parent_key in all_keys:
                children[parent_key].append((cli, sid))
                children[(cli, sid)]  # ensure child exists as key
            # parent not in all_keys → PARENT_MISSING already flagged

    visited: set[SessionKey] = set()
    components: list[set[SessionKey]] = []

    for key in all_keys:
        if key in visited:
            continue
        component: set[SessionKey] = set()
        stack = [key]
        while stack:
            node = stack.pop()
            if node in visited or node not in all_keys:
                continue
            visited.add(node)
            component.add(node)
            for child in children.get(node, []):
                stack.append(child)
            cli, sid = node
            parent = session_parent.get(node)
            if parent is not None:
                stack.append((cli, parent))
        components.append(component)

    return components


def _check_root_count(
    session_parent: dict[SessionKey, str | None],
    session_failures: dict[SessionKey, str],
) -> None:
    """Flag sessions in connected components whose root count is not one.

    Root = session with ``parent_session_id is None``.  The count is
    checked per connected component (not per CLI), so independent
    sessions each form a valid single-root component.
    """
    components = _find_connected_components(session_parent)

    for component in components:
        root_count = sum(
            1 for key in component
            if session_parent.get(key) is None
        )
        if root_count == 1:
            continue
        for key in component:
            if key not in session_failures:
                session_failures[key] = ROOT_COUNT


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_preflight(paths: list[Path]) -> PreflightResult:
    """Classify every JSONL line and validate run ancestry.

    Returns a :class:`PreflightResult` whose *conn* holds two queryable
    DuckDB relations: ``preflight_valid`` and ``preflight_failure``.
    """
    records = _parse_lines(paths)

    if not records:
        conn = duckdb.connect()
        conn.execute(
            "CREATE TABLE preflight_valid "
            "(_source_file VARCHAR, _line_number INTEGER)"
        )
        conn.execute(
            "CREATE TABLE preflight_failure "
            "(_source_file VARCHAR, _line_number INTEGER, _failure_code VARCHAR)"
        )
        return PreflightResult(
            conn=conn, has_failures=False, valid_count=0, failure_count=0,
        )

    # Phase 1 — parent-conflict (record-level, runs first).
    conflict_lines = _find_parent_conflicts(records)

    # Phase 2 — session-level data from non-conflict records.
    non_conflict = [
        r for r in records
        if (r["_source_file"], r["_line_number"]) not in conflict_lines
    ]
    session_parent = _build_session_map(non_conflict)
    session_clis = _build_session_cli_lookup(session_parent)

    session_failures: dict[SessionKey, str] = {}

    # Phase 3a — self-parent.
    for (cli, sid), parent in session_parent.items():
        if parent is not None and parent == sid:
            session_failures[(cli, sid)] = SELF_PARENT

    # Phase 3b — boundary / missing (mutually exclusive per session).
    for (cli, sid), parent in session_parent.items():
        if (cli, sid) in session_failures:
            continue
        if parent is None:
            continue
        if parent in session_clis:
            if cli not in session_clis[parent]:
                session_failures[(cli, sid)] = PARENT_BOUNDARY
        else:
            session_failures[(cli, sid)] = PARENT_MISSING

    # Phase 4 — cycle detection (sessions not yet flagged).
    _detect_cycles(session_parent, session_failures)

    # Phase 5 — root count per CLI.
    _check_root_count(session_parent, session_failures)

    # Propagate to individual lines.
    failure_map: dict[LineKey, str] = {}
    for lk in conflict_lines:
        failure_map[lk] = PARENT_CONFLICT
    for rec in non_conflict:
        sk: SessionKey = (rec["cli"], rec["session_id"])
        lk = (rec["_source_file"], rec["_line_number"])
        if sk in session_failures:
            failure_map[lk] = session_failures[sk]

    # Annotate every record and split.
    all_annotated: list[dict[str, Any]] = []
    for rec in records:
        out = dict(rec)
        lk = (rec["_source_file"], rec["_line_number"])
        out["_failure_code"] = failure_map.get(lk)
        all_annotated.append(out)

    valid_count = sum(1 for r in all_annotated if r["_failure_code"] is None)
    failure_count = len(all_annotated) - valid_count

    # Build DuckDB relations via temp JSONL (stdlib + duckdb only).
    conn = duckdb.connect()
    fd, tmp_path = tempfile.mkstemp(suffix=".jsonl", prefix="preflight_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            for rec in all_annotated:
                fh.write(json.dumps(rec) + "\n")
        conn.execute(
            "CREATE TABLE _staging AS "
            f"SELECT * FROM read_json_auto('{tmp_path}')"
        )
    finally:
        os.unlink(tmp_path)

    _coerce_nullable_types(conn)

    conn.execute(
        "CREATE VIEW preflight_valid AS "
        "SELECT * EXCLUDE (_failure_code) FROM _staging "
        "WHERE _failure_code IS NULL"
    )
    conn.execute(
        "CREATE VIEW preflight_failure AS "
        "SELECT * FROM _staging "
        "WHERE _failure_code IS NOT NULL"
    )

    return PreflightResult(
        conn=conn,
        has_failures=failure_count > 0,
        valid_count=valid_count,
        failure_count=failure_count,
    )
