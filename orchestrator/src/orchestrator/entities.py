"""Domain entities — pure state, no I/O (entity-model.md).

Every entity is a dataclass mirroring the schemas in interface-contracts.md.
The core depends on these; adapters translate to/from persistence formats.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# --- Enums -------------------------------------------------------------------


class RunMode(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    HALTED = "halted"
    COMPLETE = "complete"


class PhaseStatus(str, Enum):
    PENDING = "pending"
    AUTHORING = "authoring"
    GATING = "gating"
    REVIEWING = "reviewing"
    AWAITING_APPROVAL = "awaiting-approval"
    COMPLETE = "complete"
    HALTED = "halted"


class FindingStatus(str, Enum):
    OPEN = "open"
    SUPERSEDED = "superseded"
    RESOLVED = "resolved"


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class FindingSource(str, Enum):
    SPEC_LINT = "spec-lint"
    SEMANTIC = "semantic"


class StoryStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    DONE = "done"
    BLOCKED = "blocked"


class ApprovalDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class AgentRole(str, Enum):
    AUTHOR = "author"
    REVIEWER = "reviewer"


class MenuNodeType(str, Enum):
    MENU = "menu"
    DISPLAY = "display"
    FUNCTION = "function"


class Tier(str, Enum):
    """Fixed tier vocabulary for model resolution (UC-10, BR-045).

    Each adapter dictionary maps one of these three fixed tiers to a concrete model_id.
    The tier choice drives model selection at runtime (FR-R10, FR-R11, FR-R12).
    """

    ECONOMY = "economy"
    STANDARD = "standard"
    STRONG = "strong"


# --- Entities ----------------------------------------------------------------


@dataclass(frozen=True)
class InvocationContext:
    """Invocation metadata passed to prompt composition."""

    phase: str
    role: AgentRole
    iteration: int


@dataclass
class GateResult:
    """Structured outcome of a gate run (interface-contracts.md)."""

    passed: bool
    errored: bool
    hook: str
    error_count: int
    timed_out: bool = False
    output: str = ""


@dataclass
class Finding:
    """One review finding (file-per-finding, interface-contracts.md)."""

    id: str
    phase: str
    iteration: int
    source: FindingSource
    code: str
    severity: Severity
    artifact: str
    message: str
    status: FindingStatus = FindingStatus.OPEN
    created_by: str = ""
    resolved_by: Optional[str] = None


@dataclass
class AgentInvocation:
    """Record of one CLI invocation (entity-model.md)."""

    agent: str
    role: AgentRole
    adapter: str
    model: Optional[str]
    exit_code: int
    duration_ms: int
    timed_out: bool
    auth_error: bool
    config_error: bool


@dataclass
class Artifact:
    """A declared output artifact."""

    path: str
    kind: str = "file"


@dataclass
class Iteration:
    """One author→gate→review cycle."""

    number: int
    outcome: Optional[str] = None


@dataclass
class Approval:
    """Human sign-off at a phase gate."""

    decision: ApprovalDecision
    note: str = ""
    approved_by: str = ""


@dataclass
class PhaseRecord:
    """One phase within a run (matches RunState.phases[] schema)."""

    name: str
    author: str
    reviewer: Optional[str] = None
    status: PhaseStatus = PhaseStatus.PENDING
    iteration: int = 0
    last_gate: Optional[GateResult] = None
    rejection_note: Optional[str] = None
    # FAGAN-0040: the review CYCLE (1-based) most recently ingested/counted by
    # the reviewer for this phase. Persisted so approval and status read the
    # SAME cycle the reviewer used, instead of re-deriving ``iteration + 1``
    # (which regresses the empty-commit pause path). ``None`` means no review
    # has ever run (e.g. a gate-passed-no-reviewer phase).
    last_reviewed_cycle: Optional[int] = None
    halted_from: Optional[PhaseStatus] = None


@dataclass
class Run:
    """Root run entity (matches RunState schema in interface-contracts.md)."""

    run_id: str
    branch: str
    chain: List[str]
    current_phase: str
    iteration: int = 0
    mode: RunMode = RunMode.RUNNING
    phases: List[PhaseRecord] = field(default_factory=list)
    tooling_version: Optional[str] = None


@dataclass
class Story:
    """One backlog story (StoryFrontmatter schema)."""

    id: str
    epic: str
    title: str
    tier: Tier
    status: StoryStatus = StoryStatus.PENDING
    deps: List[str] = field(default_factory=list)
    traces: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    body: str = ""


@dataclass(frozen=True)
class MenuNode:
    """One node in the menu tree (entity-model.md, TUI Addendum).

    Pure data structure holding navigation state and default markers.
    No node embeds a service call or terminal logic.

    Validation rule: exactly one child per menu may carry is_default=True.
    """

    id: str
    label: str
    type: MenuNodeType
    is_default: bool = False
    children: List[MenuNode] = field(default_factory=list)

    def __post_init__(self):
        """Validate menu tree structure after initialization.

        Raises:
            ValueError: if more than one child has is_default=True.
        """
        defaults = [child for child in self.children if child.is_default]
        if len(defaults) > 1:
            raise ValueError(
                f"Menu node '{self.id}' has multiple default children "
                f"({len(defaults)}). Exactly one child may be marked is_default."
            )


@dataclass(frozen=True)
class Config:
    """Persisted operator defaults (UC-09, interface-contracts.md).

    All fields are optional; a None field means the operator has not set an
    override, so the resolver falls through to the next precedence layer
    (menu selection > CLI flag > config.toml > built-in default, BR-040).

    This entity mirrors the Config schema in interface-contracts.md §
    "Configuration Store". The concrete adapter (ST-0042) persists it as
    .orchestrator/config.toml.

    Attributes:
        adapter: CLI adapter name override (e.g., "copilot", "claude"), or None.
        timeout: Timeout in seconds, or None.
        cap: Iteration cap (must be >= 1), or None.
        auto_approve: Whether to auto-approve phases, or None.
    """

    adapter: Optional[str] = None
    timeout: Optional[int] = None
    cap: Optional[int] = None
    auto_approve: Optional[bool] = None


@dataclass(frozen=True)
class AdapterEntry:
    """One registered CLI adapter (UC-10, interface-contracts.md).

    Immutable DTO representing a registered adapter: its logical name (the
    adapter's identifier in the registry) and the filesystem path to its
    executable binary.

    The name is the primary key; the same binary path may not be registered
    twice under different names (BR-043). Each adapter owns exactly one model
    dictionary, created and removed together with the adapter registration
    (BR-044).

    Attributes:
        name: Logical adapter name (e.g., "copilot", "claude"), primary key.
        binary_path: Filesystem path to the adapter executable.
    """

    name: str
    binary_path: str


@dataclass
class ModelDictionary:
    """Tier-to-model-id mapping for one adapter (UC-10, BR-045).

    Each registered adapter owns exactly one dictionary. The dictionary maps
    the three fixed tiers (economy, standard, strong) to concrete model
    identifiers. Tier coverage may be incomplete; incomplete dictionaries may
    be persisted but block later agent-tier resolution unless adapter-default
    fallback is explicitly enabled (BR-046).

    This entity is mutable (unlike AdapterEntry); it supports in-memory CRUD
    operations (get_model, set_model, remove_model, list_models). The concrete
    adapter (ST-0046) persists it atomically as needed.

    Internally uses a dict keyed by tier string. Tier validation happens at
    write time (set_model, remove_model).
    """

    # Dict mapping tier name (str) to model_id (str)
    _models: dict[str, str] = field(default_factory=dict)

    def get_model(self, tier: str) -> Optional[str]:
        """Retrieve the model_id for a tier, or None if unmapped.

        Args:
            tier: One of {economy, standard, strong}.

        Returns:
            The model_id string if mapped, or None if the tier is unmapped.
        """
        return self._models.get(tier)

    def set_model(self, tier: str, model_id: str) -> None:
        """Map a tier to a model_id.

        Validates that tier is in the fixed vocabulary {economy, standard, strong}.
        Raises ValueError if tier is not recognized.

        Args:
            tier: One of {economy, standard, strong}.
            model_id: The concrete model identifier (opaque string).

        Raises:
            ValueError: If tier is not in {economy, standard, strong}.
        """
        valid_tiers = {t.value for t in Tier}
        if tier not in valid_tiers:
            raise ValueError(
                f"Invalid tier '{tier}'. Must be one of {sorted(valid_tiers)}."
            )
        self._models[tier] = model_id

    def remove_model(self, tier: str) -> None:
        """Unmap a tier, removing its model_id.

        Validates tier membership. If the tier is not currently mapped, this is
        a no-op (idempotent).

        Args:
            tier: One of {economy, standard, strong}.

        Raises:
            ValueError: If tier is not in {economy, standard, strong}.
        """
        valid_tiers = {t.value for t in Tier}
        if tier not in valid_tiers:
            raise ValueError(
                f"Invalid tier '{tier}'. Must be one of {sorted(valid_tiers)}."
            )
        self._models.pop(tier, None)

    def list_models(self) -> list[tuple[str, str]]:
        """Return all mappings as a list of (tier, model_id) tuples.

        Returns:
            List of (tier, model_id) pairs in undefined order.
        """
        return [(tier, model_id) for tier, model_id in self._models.items()]
