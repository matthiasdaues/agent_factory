"""Ports — abstract seams the core depends on (ADR-0001).

The core depends on these abstractions, never on a concrete CLI. This module
holds all port protocols and their DTOs, per
docs/spec/supplementary_specs/interface-contracts.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Protocol, runtime_checkable

from .entities import (
    AdapterEntry,
    AgentInvocation,
    Config,
    Finding,
    GateResult,
    InvocationContext,
    Run,
    Story,
)


# --- TUI / Menu Renderer ---------------------------------------------------


class KeyEvent(str, Enum):
    """Normalized navigation events for the TUI menu (ST-0037, UC-08).

    The core receives these enumerated events from the renderer, never raw
    terminal bytes. The concrete adapter (ST-0038) owns the terminal library
    and translates input to these events.
    """

    UP = "UP"
    DOWN = "DOWN"
    ENTER = "ENTER"
    BACK = "BACK"
    EXIT = "EXIT"


@dataclass(frozen=True)
class MenuItem:
    """One menu item presented to the operator (ST-0037, UC-08).

    Immutable DTO carrying display information for a single menu entry.
    The renderer owns cursor presentation; this DTO carries only the label
    and metadata.

    Attributes:
        label: Display text for this menu item.
        suffix: Optional suffix (e.g., "[strong]" tier tag, None for no suffix).
        is_default: Whether this item is marked with ★ (pre-selected on menu open).
    """

    label: str
    suffix: Optional[str] = None
    is_default: bool = False


@runtime_checkable
class MenuRenderer(Protocol):
    """Renders the TUI menu and reads navigation input (ST-0037, UC-08).

    Abstracts the concrete terminal library from the application layer.
    Dependency Inversion (ADR-0001): the core depends on this protocol, never
    on a concrete terminal adapter. The adapter (ST-0038) implements this port.
    """

    def render_menu(self, items: List[MenuItem], selected_index: int) -> None:
        """Render a menu with items and highlight the selected one.

        The renderer owns cursor presentation (the '-> ' prefix and layout).
        This method blocks until rendering is complete.

        Args:
            items: List of menu items to display.
            selected_index: 0-based index of the currently selected item.
        """
        ...

    def render_display(self, content: str) -> None:
        """Render read-only display content (e.g., agent detail, backlog summary).

        Used for display nodes (UC-08 §9a): shows the content and returns
        control to the parent menu on the next keypress.

        Args:
            content: The read-only content to display.
        """
        ...

    def get_keypress(self) -> KeyEvent:
        """Wait for and return the next normalized navigation event.

        Blocks until the operator presses a key, then returns a normalized
        KeyEvent (never raw terminal bytes). This method is the seam that
        lets the core ignore terminal details.

        Returns:
            One of the five normalized navigation events.
        """
        ...


# --- CLI Adapter & Invocation --------------------------------------------------


@dataclass(frozen=True)
class InvocationResult:
    """Result of one CLI invocation. The only type an adapter returns.

    Two flags let the core route a failure correctly instead of blindly
    looping the author:

    - `auth_error` — an authentication/availability failure (halt, BR-018).
    - `config_error` — an operator-fixable, deterministically-repeating
      failure such as a bad `--model` id (halt, ATAM-R01/T-11). Looping the
      author on such an error only burns the iteration cap and CLI credits,
      because it fails identically every pass.

    Everything else non-zero is treated as an author failure (loop).
    """

    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    auth_error: bool
    config_error: bool = False


@runtime_checkable
class CLIAdapter(Protocol):
    """Drives one AI CLI non-interactively in a fresh subprocess (ADR-0002)."""

    def invoke(
        self, prompt: str, cwd: Path, timeout_s: int, model: Optional[str] = None
    ) -> InvocationResult:
        """Run the CLI with a composed prompt in `cwd`, bounded by `timeout_s`.

        *model* overrides the adapter-default model for this single call,
        implementing per-invocation model selection (FR-K2/K3, VR-023).
        """
        ...


@runtime_checkable
class GateRunner(Protocol):
    """Working-tree cleanliness gate — agents commit, orchestrator verifies (ADR-0013)."""

    def verify(self, cwd: Path, exit_code: int) -> GateResult:
        """Check working-tree state after agent exit. Returns a GateResult.

        Maps the four-cell matrix (exit_code × tree_state) to GateResult:
        - exit 0 + clean → passed
        - exit 0 + dirty → confabulation (errored, halt)
        - non-zero + dirty → failed (clean tree, retry)
        - non-zero + clean → failed (retry)
        """
        ...

    def clean_tree(self, cwd: Path) -> None:
        """Reset working tree before retry (ADR-0013, VR-026)."""
        ...

    def artifacts_changed(self, artifact_paths: List[str]) -> bool:
        """Return True if any declared artifact has uncommitted changes (VR-012)."""
        ...


@runtime_checkable
class FindingsStore(Protocol):
    """File-per-finding JSON store (ADR-0004, VR-006/007)."""

    def ingest(self, findings: List[Finding]) -> None:
        """Write findings to the store, assigning IDs."""
        ...

    def supersede_prior(self, phase: str, current_iteration: int) -> int:
        """Mark prior iteration's open findings as superseded (BR-014).
        Returns the count of superseded findings."""
        ...

    def open_count(self, phase: str, iteration: int) -> int:
        """Count of open findings for the given phase and iteration."""
        ...

    def list_open(self, phase: str, iteration: int) -> List[Finding]:
        """Return open findings for the given phase and iteration."""
        ...

    def next_id(self) -> str:
        """Return the next available finding ID."""
        ...


@runtime_checkable
class FindingIngestor(Protocol):
    """Reads the review agent's filed findings and writes them to the store.

    The orchestrator owns finding-ID allocation and the raw→DTO mapping (BR-019,
    interface-contracts.md "Ingest mapping"). The core depends on this seam so it
    never imports the concrete file-reading/storage adapter.
    """

    def ingest_open_findings(self, phase: str, iteration: int) -> int:
        """Read the review agent's open findings (docs/findings/*.md), store them
        tagged with `phase`/`iteration`, and return the count ingested (UC-02 §7)."""
        ...

    def ingest_gate_output(self, gate_output: str, phase: str, iteration: int) -> int:
        """Parse deterministic gate/spec-lint findings from pre-commit output,
        store them tagged with `phase`/`iteration`, return count ingested."""
        ...


@runtime_checkable
class RunStateStore(Protocol):
    """Atomic read/write of .orchestrator/run.json (VR-010)."""

    def load(self) -> Optional[Run]:
        """Load the current run state, or None if absent."""
        ...

    def save(self, run: Run) -> None:
        """Atomically write the run state."""
        ...

    def exists(self) -> bool:
        """Whether a run.json is present."""
        ...


@runtime_checkable
class RunLock(Protocol):
    """Single-run lock (BR-017)."""

    def acquire(self, run_id: str) -> None:
        """Acquire the lock. Raises if already held by a live process."""
        ...

    def release(self) -> None:
        """Release the lock."""
        ...

    def is_held(self) -> bool:
        """Whether the lock is held by a live process."""
        ...


@dataclass(frozen=True)
class AgentInfo:
    """Resolved agent information from the registry."""

    name: str
    outputs: List[str]
    definition_path: Path
    skills: List[str] = field(default_factory=list)
    tier: Optional[str] = None
    interactive: bool = True


@runtime_checkable
class AgentRegistry(Protocol):
    """Resolves phase agents and their declared outputs (VR-011)."""

    def resolve(self, phase: str, role: str) -> AgentInfo:
        """Return agent info for a phase/role. Raises on unknown agent."""
        ...


@runtime_checkable
class PromptComposer(Protocol):
    """Composes the prompt for an agent invocation (FR-B2)."""

    def compose(
        self,
        agent_info: AgentInfo,
        context_paths: List[Path],
        invocation: InvocationContext,
        findings: Optional[List[Finding]] = None,
        skill: Optional[str] = None,
    ) -> str:
        """Return the composed prompt string.

        *skill*, when set, scopes the invocation to that one declared skill's
        workflow step instead of the agent's full workflow (BR-051). ``None``
        (the default) or the ``"all skills"`` sentinel composes the standard
        full-workflow prompt (BR-052).
        """
        ...


@runtime_checkable
class Logger(Protocol):
    """Append-only invocation log (.orchestrator/log.jsonl, FR-J)."""

    def log(self, record: AgentInvocation, gate: Optional[GateResult] = None) -> None:
        """Append one invocation record."""
        ...


@dataclass(frozen=True)
class LogRecord:
    """One parsed line of the invocation log (FR-T5)."""

    invocation: AgentInvocation
    gate: Optional[GateResult]


@runtime_checkable
class InvocationLogReader(Protocol):
    """Read-only access to the invocation log (.orchestrator/log.jsonl, FR-T5).

    Kept separate from the write-only ``Logger`` port (ISP): the phase-runner
    writes invocations, the status service reads them back — different seams,
    different lifecycles. Reads never drive control flow (FR-T6).
    """

    def read_entries(self) -> List[LogRecord]:
        """Return all logged invocations in append order."""
        ...


@runtime_checkable
class BacklogStore(Protocol):
    """Reads/writes backlog stories (ADR-0008)."""

    def list_stories(self) -> List[Story]:
        """Return all stories with their frontmatter fields."""
        ...

    def get_story(self, story_id: str) -> Story:
        """Return a single story, including its prose body. Raises on missing."""
        ...

    def update_status(self, story_id: str, new_status: str) -> None:
        """Update a story's status without touching the prose body."""
        ...

    def stories_by_epic(self) -> Dict[str, List[Story]]:
        """Group the loaded snapshot's stories under their epic, read-only."""
        ...

    def ready_stories(self) -> List[Story]:
        """Return pending stories whose deps all resolve to done stories."""
        ...


@runtime_checkable
class ModelMatrix(Protocol):
    """Reads the model matrix (ADR-0009, FR-K5)."""

    def get_tier(self, key: str) -> Optional[str]:
        """Get the tier for a classification (class.<name>) or phase (phase.<name>)."""
        ...

    def get_model(self, cli: str, tier: str) -> Optional[str]:
        """Get the concrete model for a CLI and tier."""
        ...

    def get_on_missing(self) -> str:
        """Return 'halt' or 'auto'."""
        ...

    def configured_clis(self) -> List[str]:
        """Return the CLIs with facts entries."""
        ...


@runtime_checkable
class Clock(Protocol):
    """Wall clock for timestamps (testable via injection)."""

    def now_ms(self) -> int:
        """Current time in milliseconds since epoch."""
        ...


@runtime_checkable
class ConfigStore(Protocol):
    """Reads/writes persisted operator defaults (UC-09, ST-0041, ADR-0017).

    Encodes the four persisted defaults: adapter, timeout, cap, auto_approve.
    All fields are optional; None means the operator set no override, so the
    resolver falls through to the next precedence layer (BR-040).

    The concrete adapter (ST-0042) persists this as .orchestrator/config.toml,
    writing atomically (write-temp-then-rename). The port itself imports no
    TOML library — that's adapter business only.

    Dependency Inversion (ADR-0001): the core depends on this protocol, never
    on a concrete file format. The adapter (ST-0042) implements this port.
    """

    def load(self) -> Optional[Config]:
        """Load the stored configuration.

        Returns:
            Config with the persisted defaults, or None if .orchestrator/config.toml
            is absent (BR-037). The absence of a field (None value) means the
            operator has not set an override.
        """
        ...

    def save(self, config: Config) -> None:
        """Store the configuration atomically.

        The concrete adapter writes to a temporary file in the target directory,
        then renames it into place (write-then-rename semantics, VR-032).
        A failed write leaves the prior configuration intact; the file is created
        only on the first successful persist.

        Args:
            config: The Config entity to persist.
        """
        ...


@runtime_checkable
class AdapterRegistry(Protocol):
    """Registry of installed CLI adapters and their model dictionaries (UC-10, ST-0045).

    Manages the catalog of available adapters and each adapter's tier-to-model mappings.
    The registry is the runtime single source of truth for adapter-to-model resolution
    (FR-R1, FR-R5, BR-044, BR-045).

    Each registered adapter carries a logical name (primary key) and a binary path.
    Each adapter owns exactly one model dictionary, created/removed atomically with
    the adapter itself (BR-044). The dictionary maps three fixed tiers (economy,
    standard, strong) to opaque model identifiers.

    Dependency Inversion (ADR-0001): the core depends on this protocol, never on a
    concrete store. The concrete adapter (ST-0046) implements this port backed by
    TOML (adapters) and per-adapter JSON (model dictionaries).

    The port itself imports no TOML library — the concrete adapter does (BR-045).
    """

    def list_adapters(self) -> List[AdapterEntry]:
        """Return all registered adapters.

        Returns:
            List of AdapterEntry objects representing each installed adapter.
            Empty list if no adapters are registered.
        """
        ...

    def get_adapter(self, name: str) -> AdapterEntry:
        """Retrieve a single adapter by name.

        Args:
            name: The logical adapter name (primary key).

        Returns:
            The AdapterEntry for the given name.

        Raises:
            KeyError: If the adapter name is not registered.
        """
        ...

    def register(self, name: str, binary_path: str) -> None:
        """Register a new adapter, creating its model dictionary.

        Atomically registers the adapter and initializes an empty model dictionary
        for it. The dictionary is empty after creation; the operator populates it
        via set_model() operations.

        Args:
            name: Logical adapter name (primary key). Must be unique.
            binary_path: Filesystem path to the adapter executable.

        Raises:
            ValueError: If the adapter name is already registered.
        """
        ...

    def unregister(self, name: str) -> None:
        """Remove an adapter and its model dictionary as one atomic operation.

        Unregister removes the adapter registration and deletes all entries in
        its model dictionary in a single atomic change set (BR-044). This ensures
        no orphaned model dictionaries remain after adapter removal.

        Args:
            name: The adapter name to remove.

        Raises:
            KeyError: If the adapter name is not registered.
        """
        ...

    def get_model(self, adapter: str, tier: str) -> Optional[str]:
        """Retrieve a model_id for an adapter and tier.

        Delegates to the adapter's model dictionary.

        Args:
            adapter: The adapter name.
            tier: One of {economy, standard, strong}.

        Returns:
            The model_id if mapped, or None if unmapped.

        Raises:
            KeyError: If the adapter name is not registered.
            ValueError: If tier is not in {economy, standard, strong}.
        """
        ...

    def set_model(self, adapter: str, tier: str, model_id: str) -> None:
        """Set a tier-to-model mapping in an adapter's dictionary.

        Delegates to the adapter's model dictionary, which validates the tier.

        Args:
            adapter: The adapter name.
            tier: One of {economy, standard, strong}.
            model_id: The concrete model identifier.

        Raises:
            KeyError: If the adapter name is not registered.
            ValueError: If tier is not in {economy, standard, strong}.
        """
        ...

    def remove_model(self, adapter: str, tier: str) -> None:
        """Unmap a tier in an adapter's dictionary (idempotent).

        Delegates to the adapter's model dictionary, which validates the tier.

        Args:
            adapter: The adapter name.
            tier: One of {economy, standard, strong}.

        Raises:
            KeyError: If the adapter name is not registered.
            ValueError: If tier is not in {economy, standard, strong}.
        """
        ...

    def list_models(self, adapter: str) -> List[tuple[str, str]]:
        """List all tier-to-model mappings for an adapter.

        Delegates to the adapter's model dictionary.

        Args:
            adapter: The adapter name.

        Returns:
            List of (tier, model_id) tuples.

        Raises:
            KeyError: If the adapter name is not registered.
        """
        ...
