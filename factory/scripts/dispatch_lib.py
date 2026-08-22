"""Dispatch ledger model and story lifecycle state machine.

Shared library for factory/scripts/dispatch. No third-party dependencies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _validate_sha(sha: str) -> None:
    """Raise ShaFormatError if *sha* is not exactly 40 lowercase hex chars."""
    if not _SHA_RE.match(sha):
        raise ShaFormatError(
            f"SHA must be exactly 40 lowercase hex characters, got: {sha!r}"
        )


class StoryState(str, Enum):
    PENDING = "pending"
    PREPARED = "prepared"
    DISPATCHING = "dispatching"
    DISPATCHED = "dispatched"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"


VALID_TRANSITIONS: dict[StoryState, set[StoryState]] = {
    StoryState.PENDING: {StoryState.PREPARED},
    StoryState.PREPARED: {StoryState.DISPATCHING},
    StoryState.DISPATCHING: {StoryState.DISPATCHED, StoryState.FAILED},
    StoryState.DISPATCHED: {StoryState.DONE, StoryState.BLOCKED, StoryState.FAILED},
    StoryState.DONE: set(),
    StoryState.FAILED: {StoryState.PREPARED},
    StoryState.BLOCKED: {StoryState.PREPARED},
}


class TransitionError(Exception):
    pass


class ShaFormatError(ValueError):
    pass


@dataclass
class StoryEntry:
    id: str
    wave: int | None = None
    status: StoryState = StoryState.PENDING
    branch: str | None = None
    worktree: str | None = None
    base_sha: str | None = None
    gate_results: dict[str, Any] = field(default_factory=dict)
    attempts: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.base_sha is not None:
            _validate_sha(self.base_sha)

    def set_sha(self, sha: str) -> None:
        _validate_sha(sha)
        self.base_sha = sha

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "wave": self.wave,
            "status": self.status.value,
            "branch": self.branch,
            "worktree": self.worktree,
            "base_sha": self.base_sha,
            "gate_results": self.gate_results,
        }
        if self.attempts:
            d["attempts"] = self.attempts
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoryEntry:
        return cls(
            id=data["id"],
            wave=data.get("wave"),
            status=StoryState(data["status"]),
            branch=data.get("branch"),
            worktree=data.get("worktree"),
            base_sha=data.get("base_sha"),
            gate_results=data.get("gate_results", {}),
            attempts=data.get("attempts", []),
        )


class Ledger:
    def __init__(self) -> None:
        self.stories: dict[str, StoryEntry] = {}

    def transition(self, story_id: str, target: StoryState) -> None:
        entry = self.stories[story_id]
        if entry.status == target:
            return
        allowed = VALID_TRANSITIONS[entry.status]
        if target not in allowed:
            raise TransitionError(
                f"invalid transition: {entry.status.value} -> {target.value} "
                f"for story {story_id}"
            )
        entry.status = target

    def save(self, path: Path) -> None:
        for entry in self.stories.values():
            if entry.base_sha is not None:
                _validate_sha(entry.base_sha)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "stories": {sid: e.to_dict() for sid, e in self.stories.items()},
        }
        path.write_text(_dump_yaml(data))

    @classmethod
    def load(cls, path: Path) -> Ledger:
        if not path.exists():
            raise FileNotFoundError(path)
        raw = _load_yaml(path.read_text())
        ledger = cls()
        for sid, sdata in raw.get("stories", {}).items():
            ledger.stories[sid] = StoryEntry.from_dict(sdata)
        return ledger

    def format_status_table(self) -> str:
        if not self.stories:
            return "No stories in ledger."
        header = f"{'ID':<12} {'Wave':<6} {'Status':<14} {'Branch':<40} {'SHA':<42}"
        sep = "-" * len(header)
        lines = [header, sep]
        for entry in self.stories.values():
            sha_display = entry.base_sha or ""
            branch_display = entry.branch or ""
            wave_display = str(entry.wave) if entry.wave is not None else ""
            lines.append(
                f"{entry.id:<12} {wave_display:<6} {entry.status.value:<14} "
                f"{branch_display:<40} {sha_display:<42}"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Minimal YAML handling (stdlib only, no PyYAML dependency)
# ---------------------------------------------------------------------------


def _dump_yaml(data: dict[str, Any]) -> str:
    if yaml is not None:
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    return _stdlib_dump(data)


def _load_yaml(text: str) -> dict[str, Any]:
    if yaml is not None:
        result = yaml.safe_load(text)
    else:
        result = _stdlib_load(text)
    if not isinstance(result, dict):
        raise TypeError(f"expected mapping, got {type(result).__name__}")
    return result


def _stdlib_dump(data: dict[str, Any], indent: int = 0) -> str:
    lines: list[str] = []
    prefix = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict) and value:
            lines.append(f"{prefix}{key}:")
            lines.append(_stdlib_dump(value, indent + 1))
        elif isinstance(value, list) and value:
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    first = True
                    for k, v in item.items():
                        if first:
                            lines.append(f"{prefix}  - {k}: {_scalar(v)}")
                            first = False
                        else:
                            lines.append(f"{prefix}    {k}: {_scalar(v)}")
                else:
                    lines.append(f"{prefix}  - {_scalar(item)}")
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}: []")
        elif isinstance(value, dict):
            lines.append(f"{prefix}{key}: {{}}")
        else:
            lines.append(f"{prefix}{key}: {_scalar(value)}")
    return "\n".join(lines)


def _scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return str(value)


def _stdlib_load(text: str) -> dict[str, Any]:
    """Minimal YAML subset parser — enough for ledger round-trips.

    Handles: nested mappings, sequences of scalars, sequences of flat
    mappings (``- key: val`` with continuation lines), inline ``[]``
    and ``{}``, and scalars (null, bool, int, str).
    """
    result: dict[str, Any] = {}
    # (indent, dict) — the dict that owns children at deeper indents
    stack: list[tuple[int, dict[str, Any]]] = [(-1, result)]
    # Track a pending key whose value is a list (detected on first ``- ``)
    pending_list_key: str | None = None
    pending_list_parent: dict[str, Any] | None = None
    # Active list context
    current_list: list[Any] | None = None
    current_list_indent: int = -1
    current_list_item: dict[str, Any] | None = None

    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(stripped)

        if stripped.startswith("- "):
            item_text = stripped[2:]
            # First list item after a ``key:`` with no inline value
            if current_list is None and pending_list_key is not None:
                current_list = []
                current_list_indent = indent
                assert pending_list_parent is not None
                pending_list_parent[pending_list_key] = current_list
                pending_list_key = None
                pending_list_parent = None
                # Also pop the placeholder dict from the stack
                if stack and stack[-1][1] is not current_list:
                    # The placeholder was pushed as a dict; remove it
                    for idx in range(len(stack) - 1, -1, -1):
                        if isinstance(stack[idx][1], dict) and not stack[idx][1]:
                            stack.pop(idx)
                            break

            if current_list is not None and indent == current_list_indent:
                if ":" in item_text:
                    key, _, rest = item_text.partition(":")
                    item_dict: dict[str, Any] = {
                        key.strip(): _parse_scalar(rest.strip())
                    }
                    current_list.append(item_dict)
                    current_list_item = item_dict
                else:
                    current_list.append(_parse_scalar(item_text.strip()))
                    current_list_item = None
            continue

        # Continuation of a list-item dict: indented deeper than ``- ``
        if (
            current_list_item is not None
            and indent > current_list_indent
            and ":" in stripped
        ):
            key, _, rest = stripped.partition(":")
            current_list_item[key.strip()] = _parse_scalar(rest.strip())
            continue

        # Left the list context
        current_list = None
        current_list_item = None
        current_list_indent = -1
        pending_list_key = None
        pending_list_parent = None

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else result

        if ":" not in stripped:
            raise ValueError(f"malformed YAML: unrecognized line: {stripped!r}")
        key, _, rest = stripped.partition(":")
        key = key.strip()
        rest = rest.strip()
        if not rest:
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
            pending_list_key = key
            pending_list_parent = parent
        elif rest == "[]":
            parent[key] = []
        elif rest == "{}":
            parent[key] = {}
        else:
            parent[key] = _parse_scalar(rest)

    return result


def _parse_scalar(text: str) -> Any:
    if text == "null":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    try:
        return int(text)
    except ValueError:
        pass
    return text
