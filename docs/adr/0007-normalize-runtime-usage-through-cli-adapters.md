---
id: 0007
status: superseded by ADR-0009
evaluation: none
---

# Normalize runtime usage through CLI adapters into local append-only records

## Context

Agent Factory runs the same agents under Claude Code, GitHub Copilot CLI,
Codex, and Pi. Each CLI exposes a different transcript and provider-usage
shape, and each owns different lifecycle events. Provider token counts are not
comparable across models or CLIs, while capture inside the orchestrator would
miss human-started sessions and could duplicate records produced by the CLI.

Runtime telemetry must remain local, auditable, concurrency-safe across
independent sessions, and unable to fail the run it measures. It must also
leave room for a later read side or storage backend without building either
before it is needed.

No existing ADR conflicts with this decision. A Pugh Matrix is not warranted:
cross-CLI comparison requires one fixed normalization method, and operational
coverage requires each CLI's native lifecycle surface. PostgreSQL, aggregation,
and budget enforcement are deferred rather than competing MVP designs.

## Decision

Use one Factory-owned `usage-capture` pipeline with two adapter boundaries:

- A transcript normalizer per CLI converts the native event stream into ordered
  input and output text plus any provider-reported breakdown.
- A logging adapter persists the canonical record and the exact normalized
  transcript. The first adapter is append-only JSONL beneath
  `.agent-factory/usage/`.

Normalize every transcript with fixed `tiktoken cl100k_base` counts. These
`normalized_*` values are the comparison metric; nullable provider
`reported_*` values exist only for cost reconciliation. Native CLI lifecycle
hooks or extensions own capture for human and child runs. The orchestrator is a
launch path, not another capture owner.

Root and child accounting follows each CLI's observable conservation model.
Where the root transcript and provider snapshot include child activity, the
root is the total and child records are attribution only. A platform whose root
is not inclusive must define how child records compose before aggregation is
built. Capture remains best-effort and returns success even when normalization
or persistence fails.

Persist the exact tokenized text by default as a local transcript copy referenced
by the record. An explicit `omit` retention mode keeps all token totals and audit
context while retaining only an empty, marked evidence reservation. Runtime
directories/files use exact owner-only `0700`/`0600` modes; invalid retention or
platforms without enforceable owner-only semantics force text omission, never
accounting loss. Records/evidence remain until session deletion or uninstall;
automatic TTL and regex redaction stay out under YAGNI.

Treat provider and hook identifiers as opaque data. A central storage-path
mapper preserves only bounded lowercase legacy-safe components and otherwise
uses fixed digest keys, retaining raw identifiers in records. Reject symlinked
or non-directory storage components, create transcript evidence exclusively
without following links, and append session records without following links.

For Pi subprocess trees, resolve the persistence base once as the consumer
repository's primary checkout and propagate it as validated process context.
Linked worktrees share Git's common directory, so this keeps descendant
records outside worktrees that `dispatch_wave` removes after successful merges.
The capture executable is resolved from that independently validated primary
checkout; an environment value cannot select arbitrary code to execute.

Every adapter performs the smallest reliable synchronous handoff by writing a
completed stream or provider-transcript snapshot to Factory's local capture
scratch directory and generation-fenced registry. It then detaches one
capture-specific supervisor through Factory's provisioned Python runtime, so
tokenization and persistence cannot delay the measured lifecycle or tool
result. The supervisor waits only outside that measured boundary and solely
owns guarded status and staged-source cleanup after the capture child
terminates. Python writes a private completion status: `captured` only after
canonical record persistence succeeds, otherwise `dropped`. Normal launcher
and Python failures therefore reach a terminal state and retain a bounded,
owner-private diagnostic. Explicit removal cancellation stays benign and cannot
be followed by diagnostic path recreation. Abrupt supervisor/host termination
remains best-effort.

Coordinate uninstall through a generation-fenced pending registry. Default
removal drains all captures registered before the state transition; explicit
cancel may discard only work that has not entered persistence. Both paths wait
with a fixed bound for the commit fence. A timeout restores the active install
and aborts teardown. Atomic files and renames provide the portable lifecycle
protocol; PIDs are diagnostic only and are never signalled.

Registration is lock-free and linearizable: each adapter hard-links the
lifecycle state to its pending token, atomically snapshotting either the active inode before the
remover's state replacement or the drain/cancel inode after it. Metadata then
atomically replaces the token contents without making the registration
invisible. This requires same-volume file hard links; initialization probes the
capability and leaves lifecycle hooks inactive when the fence is unavailable.

Native hooks preserve their provider payload semantics and synchronously do
only validation, registration, a private O(transcript-size) snapshot, and
supervisor spawn. This local copy is the unavoidable durability cost that lets
the provider delete its original transcript immediately after hook return.
Normalization and canonical persistence remain detached. The shared lifecycle
uses no Node runtime, so standalone Codex remains supported, and is deliberately
capture-specific rather than a general background-work abstraction.

Pi alone needs a tiny Node bootstrap because its provisioned interpreter can
disappear after the TypeScript extension registers but before Python starts.
The bootstrap owns only this pre-acceptance window. The shared Python supervisor
writes an explicit private acceptance handshake after validating the exact
Factory paths and generation; the bootstrap then exits and Python remains sole
full supervisor. Pre-accept launcher failure or bounded timeout performs guarded
cleanup and a transcript-free diagnostic only while lifecycle state permits.
Cancel/removal remains quiet and cannot be followed by path recreation. This is
not a second capture supervisor or a general process framework.

Provision tokenizer code only at the explicit, user-invoked initialization
boundary. `init-factory` creates a project-owned private virtual environment
from committed exact, hashed requirements using hash-required, wheel-only
installation with Python downloads disabled, then activates lifecycle hooks.
Offline initialization uses only already cached verified artifacts; if they are
absent or verification fails, unrelated Factory setup continues but capture
hooks remain inactive. Automatic capture executes the provisioned interpreter
through a relocation-safe launcher and never invokes uv, a package resolver,
the global tool cache, a Python download, or the network. Reinitialization
rebuilds from the current committed artifact; removal deletes the runtime only
after the Pi drain/cancel fence settles.

## Consequences

**Positive**

- Runs from four CLIs share one schema and one stable comparison yardstick.
- Human and dispatched sessions use the same persistence path without making
  the orchestrator a mandatory runtime.
- CLI format drift is isolated to one normalizer or lifecycle adapter.
- Transcript references make normalized counts auditable.
- A future backend can replace the JSONL logging adapter without changing
  capture sites.

**Negative / risks**

- `cl100k_base` is deliberately neutral, not provider billing truth.
- Full local transcript copies contain prompts, reasoning, and tool data and
  consume unbounded disk until manually pruned. Owner-only modes reduce local
  exposure; sensitive projects should select whole-text omission.
- Lifecycle hooks depend on each CLI's trust and event contracts. Codex hooks
  are inactive until explicitly trusted, and format changes can silently reduce
  capture until adapter tests are updated.
- Root/child aggregation is platform-specific. Adding attribution records to
  an inclusive root would double count spend. Claude is non-inclusive: totals
  select the latest cumulative root snapshot and add each distinct child
  record once. Pi is also non-inclusive across subprocess boundaries: totals
  add the root and every distinct descendant once. Copilot and Codex child
  records remain attribution-only; repeated Copilot root events are cumulative
  snapshots, so totals select the latest one rather than summing turns.
- Same-session writers atomically reserve transcript evidence by exclusive
  creation and probe numeric candidates forward on collision. No advisory lock
  or stale-lock recovery is required. Crashes may leave empty reservations and
  valid sequence gaps; numeric reservation order, not JSONL append order, is the
  cumulative snapshot order.
