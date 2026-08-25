"""Dispatch ledger model, story lifecycle state machine, and shared utilities.

Shared library for factory/scripts/dispatch. No third-party dependencies.
"""

from __future__ import annotations

import fnmatch
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

_STRONG_RISK_DOMAINS = {"security", "privacy", "data_integrity"}
TIER_RANK = {"economy": 0, "standard": 1, "strong": 2}

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
    StoryState.PENDING: {StoryState.PREPARED, StoryState.BLOCKED},
    StoryState.PREPARED: {StoryState.DISPATCHING, StoryState.BLOCKED},
    StoryState.DISPATCHING: {
        StoryState.DISPATCHED,
        StoryState.FAILED,
        StoryState.BLOCKED,
    },
    StoryState.DISPATCHED: {StoryState.DONE, StoryState.BLOCKED, StoryState.FAILED},
    StoryState.DONE: set(),
    StoryState.FAILED: {StoryState.PREPARED},
    StoryState.BLOCKED: {StoryState.PREPARED},
}


FAILURE_CLASSES: tuple[str, ...] = (
    "context_missing",
    "contract_violation",
    "environment",
    "spend_death",
    "seam_defect",
    "acceptance_unmet",
    "contradictory_evidence",
)


class TransitionError(Exception):
    pass


class ShaFormatError(ValueError):
    pass


class ManifestExistsError(Exception):
    """Raised when a step manifest write is attempted over an existing one."""


@dataclass
class StoryEntry:
    """One story's persisted dispatch lifecycle record."""

    id: str
    wave: int | None = None
    status: StoryState = StoryState.PENDING
    deps: list[str] = field(default_factory=list)
    branch: str | None = None
    worktree: str | None = None
    feature_branch: str | None = None
    base_sha: str | None = None
    reason: str | None = None
    gate_results: dict[str, Any] = field(default_factory=dict)
    attempts: list[dict[str, Any]] = field(default_factory=list)
    verify_base: str | None = None
    commit_sha: str | None = None
    failure_class: str | None = None
    evidence: str | None = None
    manifest_recoveries: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.base_sha is not None:
            _validate_sha(self.base_sha)
        if self.commit_sha is not None:
            _validate_sha(self.commit_sha)

    def set_sha(self, sha: str) -> None:
        _validate_sha(sha)
        self.base_sha = sha

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "wave": self.wave,
            "status": self.status.value,
            "deps": self.deps,
            "branch": self.branch,
            "worktree": self.worktree,
            "feature_branch": self.feature_branch,
            "base_sha": self.base_sha,
            "reason": self.reason,
            "gate_results": self.gate_results,
        }
        if self.attempts:
            d["attempts"] = self.attempts
        if self.verify_base is not None:
            d["verify_base"] = self.verify_base
        if self.commit_sha is not None:
            d["commit_sha"] = self.commit_sha
        if self.failure_class is not None:
            d["failure_class"] = self.failure_class
        if self.evidence is not None:
            d["evidence"] = self.evidence
        if self.manifest_recoveries:
            d["manifest_recoveries"] = self.manifest_recoveries
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoryEntry:
        return cls(
            id=data["id"],
            wave=data.get("wave"),
            status=StoryState(data["status"]),
            deps=data.get("deps", []),
            branch=data.get("branch"),
            worktree=data.get("worktree"),
            feature_branch=data.get("feature_branch"),
            base_sha=data.get("base_sha"),
            reason=data.get("reason"),
            gate_results=data.get("gate_results", {}),
            attempts=data.get("attempts", []),
            verify_base=data.get("verify_base"),
            commit_sha=data.get("commit_sha"),
            failure_class=data.get("failure_class"),
            evidence=data.get("evidence"),
            manifest_recoveries=data.get("manifest_recoveries", []),
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

    def is_terminal(self, story_id: str) -> bool:
        """Return True when the story is in a terminal lifecycle state."""
        return self.stories[story_id].status in {
            StoryState.DONE,
            StoryState.FAILED,
            StoryState.BLOCKED,
        }

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


# ---------------------------------------------------------------------------
# Gitignore-style glob matching
# ---------------------------------------------------------------------------


def glob_match(pattern: str, path: str) -> bool:
    """Match *path* against a gitignore-style *pattern*.

    Rules:
      - ``*`` matches zero or more characters within a single path segment
        (does not cross ``/``).
      - ``**`` matches zero or more complete path segments (crosses ``/``).
      - ``?`` matches exactly one character that is not ``/``.
      - All other characters are literal and matched case-sensitively.

    Returns True if the pattern matches the entire path.
    """
    if not pattern:
        return not path
    return _glob_match_recursive(pattern, path, 0, 0)


def _glob_match_recursive(pattern: str, path: str, pi: int, si: int) -> bool:
    """Recursive backtracking matcher for gitignore-style globs."""
    plen = len(pattern)
    slen = len(path)

    while pi < plen:
        # Check for **
        if pattern[pi : pi + 2] == "**":
            # Consume any adjacent slashes: **/ or /**/
            npi = pi + 2
            while npi < plen and pattern[npi] == "/":
                npi += 1
            # Also consume leading slash before **
            # ** matches zero or more segments
            if npi >= plen:
                # ** at end matches everything remaining
                return True
            # Try matching ** against zero or more segments
            for i in range(si, slen + 1):
                if _glob_match_recursive(pattern, path, npi, i):
                    return True
            return False

        if si >= slen:
            return False

        if pattern[pi] == "?":
            # Match one char that is not /
            if path[si] == "/":
                return False
            pi += 1
            si += 1
        elif pattern[pi] == "*":
            # * matches zero or more chars within one segment (no /)
            # (already ruled out ** above)
            npi = pi + 1
            # Try matching * against zero or more non-slash chars
            for i in range(si, slen + 1):
                if i > si and path[i - 1] == "/":
                    break
                if _glob_match_recursive(pattern, path, npi, i):
                    return True
            return False
        else:
            if pattern[pi] != path[si]:
                return False
            pi += 1
            si += 1

    return si >= slen


# ---------------------------------------------------------------------------
# Step manifest lifecycle
# ---------------------------------------------------------------------------

MANIFEST_FILENAME = "current-step.yml"
DEFAULT_MAX_INPUT_TOKENS = 100_000


def _manifest_path(worktree_path: Path, feature_branch: str, story_branch: str) -> Path:
    """Return the per-worktree, per-story manifest path.

    Layout: <worktree_path>/.current_work/<feature-branch>/<story-branch>/current-step.yml
    """
    return (
        Path(worktree_path)
        / ".current_work"
        / feature_branch
        / story_branch
        / MANIFEST_FILENAME
    )


def write_manifest(
    worktree_path: Path,
    feature_branch: str,
    story_branch: str,
    story_meta: dict[str, Any],
) -> Path:
    """Write the step manifest activating guards for one story's worktree.

    *story_meta* supplies the story's declared ``deps``/``traces`` (folded
    into the manifest's ``inputs``), ``outputs``, and an optional
    ``max_input_tokens`` override. Raises ManifestExistsError when a manifest
    is already present at the target path (no-supersede).
    """
    manifest_path = _manifest_path(worktree_path, feature_branch, story_branch)
    if manifest_path.exists():
        raise ManifestExistsError(f"manifest already present: {manifest_path}")

    inputs = list(story_meta.get("deps") or []) + list(story_meta.get("traces") or [])
    outputs = list(story_meta.get("outputs") or [])
    max_input_tokens = story_meta.get("max_input_tokens") or DEFAULT_MAX_INPUT_TOKENS

    data: dict[str, Any] = {
        "schema_version": 1,
        "step": "implement",
        "playbook": "developer",
        "phase": "red-green",
        "inputs": inputs,
        "outputs": outputs,
        "max_input_tokens": max_input_tokens,
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(_dump_yaml(data))
    return manifest_path


def remove_manifest(worktree_path: Path, feature_branch: str, story_branch: str) -> bool:
    """Delete the step manifest, deactivating guards. Returns True if removed."""
    manifest_path = _manifest_path(worktree_path, feature_branch, story_branch)
    if manifest_path.exists():
        manifest_path.unlink()
        return True
    return False


def clear_manifest_force(
    worktree_path: Path,
    feature_branch: str,
    story_branch: str,
    ledger: Ledger,
) -> bool:
    """Force-remove a stale manifest, logging a warning and recording recovery.

    Used when a step agent died without cleanup. Records the recovery on the
    ledger entry matching *story_branch* (``story/<id>``) so the operation is
    auditable, even though the manifest itself carries no ledger link.
    """
    import sys as _sys

    manifest_path = _manifest_path(worktree_path, feature_branch, story_branch)
    existed = manifest_path.exists()
    if existed:
        manifest_path.unlink()
    print(
        f"warning: force-cleared stale step manifest at {manifest_path}",
        file=_sys.stderr,
    )

    story_id = story_branch.rsplit("/", 1)[-1]
    entry = ledger.stories.get(story_id)
    if entry is not None:
        entry.manifest_recoveries.append(
            {
                "worktree": str(worktree_path),
                "manifest_path": str(manifest_path),
                "existed": existed,
            }
        )
    return existed


# ---------------------------------------------------------------------------
# Wave planning
# ---------------------------------------------------------------------------


@dataclass
class StoryMeta:
    """Parsed story metadata for planning purposes."""

    id: str
    deps: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    tier: str = "economy"
    risk_domains: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    traces: list[str] = field(default_factory=list)
    max_input_tokens: int | None = None


@dataclass
class WavePlan:
    """Result of wave planning: waves with parallel sets and serial chains."""

    waves: list[dict[str, Any]] = field(default_factory=list)

    def to_yaml(self) -> str:
        lines: list[str] = ["waves:"]
        for wave in self.waves:
            lines.append(f"  - wave: {wave['wave']}")
            lines.append("    stories:")
            for s in wave.get("stories", []):
                lines.append(f"      - id: {s['id']}")
                lines.append(f"        tier: {s['tier']}")
                lines.append(f"        group: {s['group']}")
                if "suggested_tier" in s:
                    lines.append(f"        suggested_tier: {s['suggested_tier']}")
            if "serial_chains" in wave:
                lines.append("    serial_chains:")
                for chain in wave["serial_chains"]:
                    lines.append(f"      - [{', '.join(chain)}]")
        return "\n".join(lines) + "\n"


def parse_story_frontmatter(text: str) -> dict[str, Any] | None:
    """Parse YAML frontmatter from a story file. Returns dict or None."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for i, ln in enumerate(lines[1:], start=1):
        if ln.strip() == "---":
            end = i
            break
    if end is None:
        return None

    import re as _re

    fm: dict[str, Any] = {}
    current_key: str | None = None
    current_list: list[str] | None = None

    for ln in lines[1:end]:
        list_item = _re.match(r"^\s+-\s+(.+)$", ln)
        if list_item and current_key is not None:
            if current_list is None:
                current_list = []
            val = list_item.group(1).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                val = val[1:-1]
            current_list.append(val)
            continue

        if current_key is not None and current_list is not None:
            fm[current_key] = current_list
            current_list = None
            current_key = None

        m = _re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)?$", ln)
        if m:
            key = m.group(1)
            raw_val = (m.group(2) or "").strip()
            if not raw_val:
                current_key = key
                current_list = None
                fm[key] = None
            else:
                current_key = key
                current_list = None
                # Inline list [a, b]
                if raw_val.startswith("[") and raw_val.endswith("]"):
                    inner = raw_val[1:-1]
                    if not inner.strip():
                        fm[key] = []
                    else:
                        items = []
                        for t in inner.split(","):
                            t = t.strip()
                            if len(t) >= 2 and t[0] == t[-1] and t[0] in ('"', "'"):
                                t = t[1:-1]
                            items.append(t)
                        fm[key] = items
                elif raw_val in ("null", "~"):
                    fm[key] = None
                elif raw_val in ("true", "True"):
                    fm[key] = True
                elif raw_val in ("false", "False"):
                    fm[key] = False
                else:
                    if (
                        len(raw_val) >= 2
                        and raw_val[0] == raw_val[-1]
                        and raw_val[0] in ('"', "'")
                    ):
                        raw_val = raw_val[1:-1]
                    fm[key] = raw_val

    if current_key is not None and current_list is not None:
        fm[current_key] = current_list

    return fm


def load_stories(backlog_dir: Path) -> list[StoryMeta]:
    """Load all story files from a backlog directory."""
    stories: list[StoryMeta] = []
    for p in sorted(backlog_dir.glob("ST-*.md")):
        fm = parse_story_frontmatter(p.read_text())
        if fm is None:
            continue
        raw_traces = fm.get("traces")
        traces = raw_traces if isinstance(raw_traces, list) else ([raw_traces] if raw_traces else [])
        raw_max_tokens = fm.get("max_input_tokens")
        max_input_tokens = int(raw_max_tokens) if raw_max_tokens else None
        stories.append(
            StoryMeta(
                id=fm.get("id", p.stem),
                deps=fm.get("deps") or [],
                outputs=fm.get("outputs") or [],
                tier=fm.get("tier", "economy"),
                risk_domains=fm.get("risk_domains") or [],
                tests=fm.get("tests") or [],
                traces=traces,
                max_input_tokens=max_input_tokens,
            )
        )
    return stories


def load_project_config(project_root: Path) -> dict[str, Any]:
    """Load config/project.json from *project_root*. Returns {} if absent/invalid."""
    config_path = project_root / "config" / "project.json"
    if not config_path.exists():
        return {}
    try:
        data = json.loads(config_path.read_text())
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def suggest_tier(
    story_frontmatter: dict[str, Any], project_config: dict[str, Any]
) -> str:
    """Suggest a model tier for a story using a first-match-wins rubric.

    Rules, evaluated in order (first match wins):
      1. risk_domains includes security, privacy, or data_integrity -> strong
      2. outputs match a safety_critical_paths glob -> strong
      3. outputs span 2+ top-level directories -> standard
      4. deps has 3+ entries -> standard
      5. single directory with non-empty tests -> economy
      6. default -> standard
    """
    risk_domains = story_frontmatter.get("risk_domains") or []
    if any(d in _STRONG_RISK_DOMAINS for d in risk_domains):
        return "strong"

    outputs = story_frontmatter.get("outputs") or []
    safety_critical_paths = project_config.get("safety_critical_paths") or []
    if safety_critical_paths:
        for output in outputs:
            for pattern in safety_critical_paths:
                if fnmatch.fnmatch(output, pattern):
                    return "strong"

    top_dirs = set()
    for output in outputs:
        parts = Path(output).parts
        top_dirs.add(parts[0] if parts else output)

    if len(top_dirs) >= 2:
        return "standard"

    deps = story_frontmatter.get("deps") or []
    if len(deps) >= 3:
        return "standard"

    tests = story_frontmatter.get("tests") or []
    if len(top_dirs) <= 1 and tests:
        return "economy"

    return "standard"


def _expand_outputs(outputs: list[str], project_root: Path) -> set[str]:
    """Expand output globs against the working tree. Returns relative paths."""
    expanded: set[str] = set()
    for pattern in outputs:
        if not pattern:
            continue
        matched = list(project_root.glob(pattern))
        if matched:
            for m in matched:
                if m.is_file():
                    expanded.add(str(m.relative_to(project_root)))
        else:
            # Conservative fallback: use directory prefix
            # Extract the prefix before any wildcard
            prefix = pattern.split("*")[0].split("?")[0].rstrip("/")
            if prefix:
                expanded.add(f"__prefix__:{prefix}")
    return expanded


def _files_overlap(a: set[str], b: set[str]) -> bool:
    """Check if two expanded output sets overlap (including prefix overlap)."""
    # Direct file overlap
    direct = a & b
    if direct:
        return True
    # Check prefix overlaps
    a_prefixes = {s.split(":", 1)[1] for s in a if s.startswith("__prefix__:")}
    b_prefixes = {s.split(":", 1)[1] for s in b if s.startswith("__prefix__:")}
    a_files = {s for s in a if not s.startswith("__prefix__:")}
    b_files = {s for s in b if not s.startswith("__prefix__:")}

    for prefix in a_prefixes:
        if any(f.startswith(prefix) for f in b_files):
            return True
        if any(p.startswith(prefix) or prefix.startswith(p) for p in b_prefixes):
            return True
    for prefix in b_prefixes:
        if any(f.startswith(prefix) for f in a_files):
            return True
    return False


def _story_meta_to_frontmatter(story: StoryMeta) -> dict[str, Any]:
    """Project a StoryMeta back into the frontmatter shape suggest_tier expects."""
    return {
        "risk_domains": story.risk_domains,
        "outputs": story.outputs,
        "deps": story.deps,
        "tests": story.tests,
    }


def compute_wave_plan(
    stories: list[StoryMeta],
    project_root: Path,
    filter_ids: list[str] | None = None,
    project_config: dict[str, Any] | None = None,
) -> WavePlan:
    """Compute a wave plan from stories with dependency and file-overlap analysis.

    If *filter_ids* is provided, only those stories are included in the plan.
    Each story's ``suggested_tier`` is computed via :func:`suggest_tier`, using
    *project_config* (loaded from ``config/project.json`` under *project_root*
    when not explicitly provided).
    """
    if project_config is None:
        project_config = load_project_config(project_root)

    if filter_ids:
        id_set = set(filter_ids)
        stories = [s for s in stories if s.id in id_set]

    by_id = {s.id: s for s in stories}
    planned_ids = set(by_id.keys())

    # Expand outputs for each story
    expanded: dict[str, set[str]] = {}
    for s in stories:
        expanded[s.id] = _expand_outputs(s.outputs, project_root)

    # Assign waves based on dependencies
    wave_of: dict[str, int] = {}

    def _wave_for(sid: str, visited: set[str] | None = None) -> int:
        if sid in wave_of:
            return wave_of[sid]
        if visited is None:
            visited = set()
        if sid in visited:
            # Cycle — break it
            return 1
        visited.add(sid)
        story = by_id.get(sid)
        if story is None:
            return 0  # External dep, already done
        if not story.deps:
            return 1
        dep_waves = []
        for d in story.deps:
            if d in planned_ids:
                dep_waves.append(_wave_for(d, visited))
            # else: external dep, assumed done (wave 0)
        return max(dep_waves, default=0) + 1

    for s in stories:
        wave_of[s.id] = _wave_for(s.id)

    # Group by wave
    max_wave = max(wave_of.values(), default=0)
    waves: list[dict[str, Any]] = []

    for w in range(1, max_wave + 1):
        wave_stories = [sid for sid, wn in wave_of.items() if wn == w]

        # Within a wave, find serial chains (file-overlapping pairs)
        # Build overlap graph within the wave
        overlap_edges: dict[str, set[str]] = {sid: set() for sid in wave_stories}
        for i, a in enumerate(wave_stories):
            for b in wave_stories[i + 1 :]:
                if _files_overlap(expanded[a], expanded[b]):
                    overlap_edges[a].add(b)
                    overlap_edges[b].add(a)

        # Connected components of the overlap graph become serial chains
        visited_w: set[str] = set()
        serial_chains: list[list[str]] = []
        parallel: list[str] = []

        for sid in wave_stories:
            if sid in visited_w:
                continue
            if not overlap_edges[sid]:
                parallel.append(sid)
                visited_w.add(sid)
            else:
                # BFS to find connected component
                chain: list[str] = []
                queue = [sid]
                while queue:
                    node = queue.pop(0)
                    if node in visited_w:
                        continue
                    visited_w.add(node)
                    chain.append(node)
                    for neighbor in overlap_edges[node]:
                        if neighbor not in visited_w:
                            queue.append(neighbor)
                serial_chains.append(chain)

        wave_entry: dict[str, Any] = {"wave": w, "stories": []}
        for sid in parallel:
            story = by_id[sid]
            wave_entry["stories"].append(
                {
                    "id": sid,
                    "tier": story.tier,
                    "group": "parallel",
                    "suggested_tier": suggest_tier(
                        _story_meta_to_frontmatter(story), project_config
                    ),
                }
            )
        for chain in serial_chains:
            for sid in chain:
                story = by_id[sid]
                wave_entry["stories"].append(
                    {
                        "id": sid,
                        "tier": story.tier,
                        "group": "serial",
                        "suggested_tier": suggest_tier(
                            _story_meta_to_frontmatter(story), project_config
                        ),
                    }
                )
        if serial_chains:
            wave_entry["serial_chains"] = [
                [sid for sid in chain] for chain in serial_chains
            ]
        waves.append(wave_entry)

    return WavePlan(waves=waves)
