---
title: Agent Context Composition
category: architecture
enforcement: context-lint (CX-* codes), rules.md
version: 2.0.0
---

# Agent Context Composition

`docs/agent-context/` is the factory-facing interface between agents and a
project's own knowledge. It is a routing table, not a knowledge base: it
tells an agent where to look, never what it will find there. This document
states the binding rules that keep that interface honest as a project
matures.

Design origin: [yaml-charter-lifecycle.md](../../../docs/proposals/yaml-charter-lifecycle.md).
Structural decision: [ADR-0013](../../../docs/adr/0013-yaml-agent-context-replaces-markdown-charter.md).
Lifecycle decision: [ADR-0014](../../../docs/adr/0014-two-layer-routing-with-two-mode-lifecycle.md).

## The four files

| File                  | Layer | Carries                                                        |
| --------------------- | ----- | -------------------------------------------------------------- |
| `reading-guides.yaml` | 1     | Concern-based routing to Layer 2 sections. No `source:`.       |
| `stack.yaml`          | 2     | What the project is built with.                                |
| `workflow.yaml`       | 2     | How to build, test, and deploy it.                             |
| `governance.yaml`     | 2     | What rules apply.                                              |
| `testing.yaml`        | peer  | Machine-readable test config. Exempt from the lifecycle below. |

## Derived content

Agent context is always derived content. In steady state it links to
sources; it is never the primary authority. Early in a greenfield project,
before source documents exist, fields may hold inline prose values under
`name:` — but the direction of truth still flows from the project's own
records (handbook, ADRs, code) toward the index files, never the reverse.
`update-context` writes only to `docs/agent-context/*.yaml`; it never
writes upstream to a source document.

## Field states

Each leaf field in a Layer 2 index file is in exactly one of three states:

- **Valued** — the field carries a `name:` (display label) and optionally a
  `source:` (the authoritative document). Early fields may have only
  `name:` with no source yet; mature fields carry both. `name:` is the
  display label an agent reads; `source:` is the authority it follows.
- **Deferred** — the field carries `deferred: "<reason>"` as the sole key.
  A deferral is a conscious choice to postpone, not a defect. `deferred`
  must never coexist with `name` or `source` in the same mapping.
- **Absent** — the key does not exist. This means the concept does not
  apply to this project. Key absence is the correct state for inapplicable
  fields — do not leave them as `null`.

`null` is never a valid field state. A `null` leaf is always a lint error
(`CX-NULL`). If the decision is pending, use `deferred:`. If the concept
does not apply, remove the key.

## Write-path ownership

- `capture-context` creates the initial templates and fills first values.
- `update-context` is the write path for index files after initial setup.
- `detect-test-regime` is the sole writer of `testing.yaml`. It writes
  directly because `testing.yaml` does not participate in the index-file
  lifecycle.
- The reading guide (`reading-guides.yaml`) is assembled by `capture-context`
  (brownfield) or proposed by `update-context` (greenfield, on the first
  `source:` pointer). It is never hand-authored as a substitute for the
  index files.

## Format exclusivity

A project uses exactly one context format: YAML agent context
(`docs/agent-context/`) or the legacy markdown charter (`docs/charter/`),
never both. Format detection walks a fixed resolution chain and treats
files present in more than one location as an error (`CX-FORMAT`), except
for `testing.yaml`, which is a lifecycle-exempt peer file explicitly
permitted to resolve across both locations (see next section).

## Source-pointer direction of truth

Sources are maintained in exactly one place: the three Layer 2 index files.
`reading-guides.yaml` references index-file sections only
(`<file>#<dotted.key.path>`); it must never carry a `source:` pointer of its
own. A `source:` pointer prefers the project-local convention document over
a factory rulebook default when both describe the same decision — the
project's own record is the closer, more specific authority.

## Source resolution

A `source:` value is tried as a file path first (`CX-SRC-EXIST`). If it
does not resolve to a file on disk, it is treated as inline prose — a
verbal reference or a URL. No lint finding fires for a non-path source;
`CX-SRC-EXIST` is a warning only when the value looks like a path but the
file is missing.

## `testing.yaml` carve-out

`testing.yaml` is a peer file, not an index file. It is always code-derived,
written directly by `detect-test-regime`, and consumed as structured
configuration by scripts, hooks, and playbooks. It does not participate in
the index-file lifecycle and is validated by `context-lint` for `CX-PARSE`
only — `CX-NULL` and `CX-KEYS` checks do not apply to it. Consumers
resolve its path by checking `docs/agent-context/testing.yaml` first, then
`docs/charter/testing.yaml` as a fallback; the split location does not
trigger `CX-FORMAT`.
