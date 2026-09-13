---
id: 0015
status: accepted
evaluation: pugh-matrix
---

# Query authoritative JSONL with ephemeral DuckDB views

## Context

Factory already appends canonical usage records beneath `.agent-factory/usage/`
as defined by [ADR-0007](0007-normalize-runtime-usage-through-cli-adapters.md).
The records are durable evidence, but cumulative snapshots and CLI-specific
parent-child semantics make direct summation incorrect. The superseded Usage
Accounting design added PostgreSQL, a projector, containers, remote
configuration, and retention workflows. Release 1 needs reproducible local
analysis for one operator without operating a data service.

The analytical boundary must not delay capture, rewrite evidence, read
transcripts, or require a network connection. Stable results must apply one
versioned query model and one closed four-CLI accounting registry. Persistent
analytical state would introduce freshness, synchronization, and recovery
contracts that the accepted feature does not require.

No existing ADR conflicts with this decision. [ADR-0007](0007-normalize-runtime-usage-through-cli-adapters.md)
and [ADR-0009](0009-cli-prefixed-usage-record-filenames-when-filesystem-safe.md)
govern production and filesystem identity of the input records; this ADR adds
their read-only analytical consumer.

## Decision

Use the retained top-level JSONL files as authoritative evidence. An opt-in
Usage Analysis package snapshots a sorted input set at query start, validates
every selected line, and registers query-scoped valid and failure relations in
an embedded DuckDB process. Version-controlled SQL publishes exactly six
`query-model-v1` views. No persistent DuckDB database or projector is
authoritative state.

DuckDB is the computation engine and SQL is the canonical transformation
language. Python owns input selection, contract and ancestry preflight,
parameter validation, and result adapters. Stable results come only from the
published views as a table, JSON, DuckDB relation, PyArrow table, or explicit
Parquet export. Parquet is staged, verified, attributed, and atomically
replaced; it is rebuildable output, not synchronized state. DuckDB's bundled UI
may explore the same views in an ephemeral localhost session but is never a
gate or data authority.

Factory owns the usage-record contract and capture. Usage Analysis depends on
that published contract; Factory has no dependency on Usage Analysis. The
analysis package directly declares and locks DuckDB and PyArrow, and
installation is opt-in under `.agent-factory/usage-analysis/`.

The stakeholder confirmed this Pugh Matrix against the accepted feature's
quality requirements:

| Criterion                               | Weight | PostgreSQL projector (baseline) | Persistent DuckDB file | SQLite | Ephemeral DuckDB views over JSONL |
| --------------------------------------- | -----: | ------------------------------: | ---------------------: | -----: | --------------------------------: |
| Reproducible from retained evidence     |      3 |                               0 |                     +1 |      0 |                                +1 |
| Capture independence                    |      3 |                               0 |                     +1 |     +1 |                                +1 |
| Local operational simplicity            |      3 |                               0 |                     +1 |     +1 |                                +1 |
| Deterministic accounting tests          |      3 |                               0 |                     +1 |      0 |                                +1 |
| Local, transcript-blind operation       |      3 |                               0 |                     +1 |     +1 |                                +1 |
| Ad hoc exploration                      |      1 |                               0 |                     +1 |      0 |                                +1 |
| No freshness or synchronization state   |      3 |                               0 |                     -1 |     -1 |                                +1 |
| Clean Architecture dependency direction |      3 |                               0 |                     +1 |     +1 |                                +1 |
| **Weighted total**                      |        |                           **0** |                **+12** | **+6** |                           **+22** |

## Consequences

**Positive**

- Every stable result is reproducible from a named input set and versioned
  query model.
- Capture remains available when analysis is absent, broken, or removed.
- Accounting rules live in one tested SQL and registry boundary instead of
  presentation code.
- Local operation needs no service, container, credential, or remote resource.
- Optional exports and UI sessions cannot become hidden sources of truth.

**Negative / risks**

- Every query repeats input validation and view construction; release 1 accepts
  this cost instead of introducing persistent state.
- DuckDB and PyArrow add a locked, isolated runtime to the opt-in component.
- A DuckDB or SQL compatibility change can affect all published views and must
  be handled through the query-model and dependency contracts.
- The bundled UI may fetch assets when an operator opens it, so deterministic
  gates must verify only the documented bootstrap and never launch the UI.
