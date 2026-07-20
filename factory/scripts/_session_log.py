"""Session-log helper for Agent Factory gate scripts.

What: Records one JSON Lines entry per wrapped gate run — the on-disk delta,
      the run's exit code, and its structured summary where emitted.
When: Around each gate run that opts into session logging.
By:   imported by gate scripts (e.g. spec-lint) — not run directly.

Records one JSON Lines entry per wrapped gate run: what actually moved on disk
(a ``git status --porcelain`` diff taken around the run), the run's own exit
code, and — where the gate emits it — its structured summary. See
factory/docs/proposals/session-log-addendum.md.

Transparency guarantee. ``record()`` is a no-op unless the ``AF_SESSION_LOG``
environment variable names a log-file path. A session that has not opted in
sees zero behaviour change: the same ``with`` wrapper compiles either way, and
nothing is written.

Timestamp. ``ts`` is taken from this helper's own ``datetime.now(timezone.utc)``
at the moment the wrapped block ends — never from anything the wrapped script or
an agent supplies. That is the point of the log: it records what the machine
observed, not what the agent said.

Exit-code capture (the gap in the proposal's sketch). The proposal shows::

    with session_log.record("spec-lint", argv):
        return real_main(argv)

but a bare ``with`` block cannot see the value a ``return`` inside it produces,
so the record could never learn the exit code. This helper closes that gap by
yielding a small ``Recorder`` whose ``.exit_code`` the caller assigns through
the call itself::

    with session_log.record("spec-lint", sys.argv[1:]) as rec:
        rec.exit_code = main()
    sys.exit(rec.exit_code if rec.exit_code is not None else 0)

Because the assignment wraps the call, every ``return`` path inside ``main()``
(including early error returns) is captured. If the block raises instead, the
record is still written (with ``exit_code`` left ``None``) and the exception
propagates. The ``summary`` field is folded in out-of-band via ``set_summary``:
the wrapped gate calls it once its own ``--format json`` counts are known, and
it is a no-op when logging is inactive.
"""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Recorder:
    """Handle yielded by :func:`record`; the caller sets ``exit_code`` on it."""

    exit_code: int | None = None
    summary: dict | None = None


# The in-flight recorder, so a wrapped gate can attach its summary without the
# record() call site having to thread the Recorder down into the gate's body.
_active: Recorder | None = None


def set_summary(summary: dict) -> None:
    """Attach a summary block to the in-flight record, if logging is active.

    A no-op when no ``record()`` context is open (e.g. ``AF_SESSION_LOG`` unset),
    so gates may call it unconditionally.
    """
    if _active is not None:
        _active.summary = summary


def _git_status() -> dict[str, str]:
    """Return ``{path: status}`` from ``git status --porcelain`` (empty on error)."""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return {}
    status: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        code, path = line[:2], line[3:]
        if " -> " in path:  # rename: record the destination path
            path = path.split(" -> ", 1)[1]
        status[path.strip('"')] = code.strip()
    return status


def _diff(before: dict[str, str], after: dict[str, str]) -> list[dict[str, str]]:
    """Paths whose porcelain status appeared or changed between the snapshots."""
    changed = [
        {"path": path, "status": code}
        for path, code in after.items()
        if before.get(path) != code
    ]
    changed.sort(key=lambda c: c["path"])
    return changed


@contextlib.contextmanager
def record(script: str, argv: list[str]):
    """Wrap a gate run; append one JSONL record when ``AF_SESSION_LOG`` is set.

    Yields a :class:`Recorder`. Assign its ``.exit_code`` (see module docstring);
    ``summary`` is populated separately via :func:`set_summary`.
    """
    global _active
    log_path = os.environ.get("AF_SESSION_LOG")
    rec = Recorder()
    if not log_path:
        yield rec
        return

    before = _git_status()
    _active = rec
    try:
        yield rec
    finally:
        after = _git_status()
        _active = None
        entry: dict = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "script": script,
            "argv": list(argv),
            "exit_code": rec.exit_code,
            "files_changed": _diff(before, after),
        }
        if rec.summary is not None:
            entry["summary"] = rec.summary
        parent = os.path.dirname(log_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
