"""Adapter auto-detection: scan `$PATH` for known CLI adapter binaries
(ST-0047, UC-10 Main Success Scenario step 4, FR-R2, BR-042).

**Known adapter binary names.** This codebase ships exactly one concrete
`CLIAdapter` implementation today — `CopilotAdapter`
(`adapters/copilot.py`), default binary name `"copilot"`. There is no
broader established registry of adapter binary names anywhere else in the
codebase to draw from (`AdapterRegistry` tracks adapters the operator has
already *registered*, not candidate names to scan for). Rather than invent
names for adapter types this codebase has no concrete `CLIAdapter` to
actually drive, `KNOWN_ADAPTER_BINARIES` is a small explicit allowlist
seeded with the one binary this codebase can drive today. Supporting a new
adapter type is a two-part change: add its binary name here AND ship a
concrete `CLIAdapter` for it — see ST-0047.md's Analysis section for the
full rationale.

**Non-destructive probe (BR-042, UC-10 Special Requirements: "Adapter
validation probes shall be non-destructive and shall not mutate project
state").** `probe_binary` never invokes the candidate: no subprocess, no
`--version`/`--help` flag, no arguments. It only checks that the resolved
path is a file and is executable — the same check
`TomlAdapterRegistry.register()` already performs before persisting.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

KNOWN_ADAPTER_BINARIES: Tuple[str, ...] = ("copilot",)


@dataclass(frozen=True)
class DetectedAdapter:
    """One `$PATH`-discovered candidate that passed the non-destructive
    probe — not yet registered."""

    name: str
    binary_path: str


def probe_binary(path: str) -> bool:
    """Non-destructive validation probe: the candidate resolves to a file
    that exists and is executable. Never invokes the binary."""
    return os.path.isfile(path) and os.access(path, os.X_OK)


def detect_candidates(
    known_names: Tuple[str, ...] = KNOWN_ADAPTER_BINARIES,
    which_fn: Callable[[str], Optional[str]] = shutil.which,
) -> List[DetectedAdapter]:
    """Scan `$PATH` for each name in `known_names` via `which_fn` (a pure
    lookup — itself non-destructive), re-validating every hit with
    `probe_binary` before it counts as a candidate.

    `which_fn` defaults to `shutil.which`; injectable so callers/tests never
    depend on what's actually installed on the machine running them.
    """
    candidates: List[DetectedAdapter] = []
    for name in known_names:
        resolved = which_fn(name)
        if resolved and probe_binary(resolved):
            candidates.append(DetectedAdapter(name=name, binary_path=resolved))
    return candidates
