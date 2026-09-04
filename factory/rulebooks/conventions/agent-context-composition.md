---
title: Agent Context Composition
category: architecture
enforcement: context-lint (CX-* codes), rules.md
version: 1.0.0
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
sources; it is never the primary authority. The single exception is
`mode: primary` during greenfield setup, before source documents exist.
Direction of truth flows from source documents (handbook, ADRs, code) to the
index files — never the reverse. `update-context` writes only to
`docs/agent-context/*.yaml`; it never writes upstream to a source document.

## Mode semantics

Each of the three Layer 2 index files carries a top-level `mode` field with
exactly two legal values:

- **`mode: primary`** — the index files are the primary source of project
  decisions. This is the greenfield state, active before a handbook or
  conventions exist. Fields hold direct values. No `source:` pointers are
  required.
- **`mode: index`** — the index files are downstream routing tables. Every
  non-null, non-deferred leaf field holds a name and a `source:` pointer to
  the authoritative document. Summaries and compressed values are forbidden
  in this mode — a name and a link, nothing else.

The transition from `primary` to `index` is one-directional and atomic: all
three index files flip together, in a single commit, once every non-null,
non-deferred leaf across all three has a `source:` pointer. `update-context`
is the sole agent of this transition.

A `null` field means the decision does not apply to this project and is
excluded from the transition condition. A `deferred: "reason"` mapping means
the decision is pending; it is also excluded from the transition condition
and is not itself a lint finding — a deferral is a conscious choice, not a
defect. `deferred` must be the only key at that field: it must never coexist
with `name` or `source` in the same mapping.

## Write-path ownership

- `capture-context` creates the initial templates and fills first values.
- `update-context` is the only write path for an index file once it carries
  `mode: index`. Hand-editing an index file in `mode: index` is forbidden.
- `detect-test-regime` is the sole writer of `testing.yaml`. It writes
  directly regardless of the other files' mode, because `testing.yaml` does
  not participate in the two-mode lifecycle.
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

## `testing.yaml` carve-out

`testing.yaml` is a peer file, not an index file. It is always code-derived,
written directly by `detect-test-regime`, and consumed as structured
configuration by scripts, hooks, and playbooks. It does not carry `mode`,
does not participate in the primary/index lifecycle, and is validated by
`context-lint` for `CX-PARSE` only — `CX-SRC`, `CX-MODE`, and `CX-NULL`
checks do not apply to it. Consumers resolve its path by checking
`docs/agent-context/testing.yaml` first, then `docs/charter/testing.yaml` as
a fallback; the split location does not trigger `CX-FORMAT`.
