---
id: 0007
status: proposed
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

Persist the exact tokenized text as a local transcript copy referenced by the
record. Keep retention, aggregation, presentation, PostgreSQL storage, cost
rates, and enforcement out of this release under YAGNI.

For Pi subprocess trees, resolve the persistence base once as the consumer
repository's primary checkout and propagate it as validated process context.
Linked worktrees share Git's common directory, so this keeps descendant
records outside worktrees that `dispatch_wave` removes after successful merges.
The capture executable is resolved from that independently validated primary
checkout; an environment value cannot select arbitrary code to execute.

Pi performs the smallest reliable synchronous handoff by writing the completed
stream to Factory's local capture scratch directory. It then detaches
`usage-capture` with ignored standard streams, so tokenization and persistence
cannot delay the measured lifecycle or tool result. The detached process owns
guarded source cleanup. Normal parent exit permits completion; abrupt host or
process-group termination remains best-effort.

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
- Local transcript copies contain the run's prompts, reasoning, and tool data;
  they consume unbounded disk until manually pruned and require the same local
  confidentiality as the source transcript.
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
- Append safety does not make same-session sequence allocation atomic; the MVP
  assumes one writer at a time per session id.
