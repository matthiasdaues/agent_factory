---
id: "0014"
status: proposed
evaluation: none
---

# Two-layer routing with two-mode lifecycle

## Context

The accepted proposal for agent context ([yaml-charter-lifecycle.md](../proposals/yaml-charter-lifecycle.md)) introduced two structural mechanisms on top of the YAML format decision ([ADR-0013](0013-yaml-agent-context-replaces-markdown-charter.md)):

1. **Two routing layers.** The initial design (September 2, 2026) used a single layer of index files keyed by decision domain (stack, workflow, governance). A separate `agent-context.md` file routed by work type (backend, frontend, testing). Maintaining two independent routing tables over one document tree created two places to drift. The revision unified them: Layer 1 (`reading-guides.yaml`) routes by work-type concern to sections in Layer 2 index files. Sources are maintained in exactly one place (the index files). The reading guide references index sections, never source documents directly.

2. **Two-mode lifecycle.** Greenfield projects have no source documents to link to; the index files must serve as the upstream source of decisions during early setup. Mature projects need a pure link index that cannot drift from the handbook. A single mode cannot satisfy both. The lifecycle has two states: `mode: primary` (the index files are the upstream source, values written directly) and `mode: index` (the index files are downstream routing tables, every non-null, non-deferred leaf has a `source:` pointer). The transition from primary to index is one-directional and atomic across all three index files.

Neither mechanism has a genuine alternative to evaluate. The two-layer design is the resolution of a concrete failure (two independent routing tables drifting). The two-mode lifecycle is the consequence of a real constraint (greenfield projects have no sources to link to). In both cases the only alternative is "don't solve the problem."

## Decision

Adopt two-layer routing and a two-mode lifecycle for agent context, as specified in the proposal.

**Two-layer routing:**

- Layer 1: `reading-guides.yaml` routes by concern (backend, frontend, testing, architecture, packaging, and project-specific additions) to key-path references in Layer 2 files. It carries no `source:` pointers.
- Layer 2: `stack.yaml`, `workflow.yaml`, `governance.yaml` carry `source:` pointers to authoritative project documents. They are the sole location for source references.
- Reading-guide entries use key-path notation: `<file>#<dotted.key.path>`.
- `context-lint` validates references via `CX-GUIDE-REF` by confirming the key path exists in the target file.

**Two-mode lifecycle:**

- `mode: primary` -- greenfield setup, before handbook and conventions exist. Values written directly, no `source:` pointers required.
- `mode: index` -- mature projects. Every non-null, non-deferred leaf has a `source:` pointer. Hand-editing forbidden; only `update-context` writes.
- Transition condition: every non-null, non-deferred leaf field across all three index files has a `source:` pointer. Verified mechanically by `context-lint` via `CX-SRC`.
- Transition is one-directional (primary to index only) and atomic (all three files in a single commit).
- `testing.yaml` is exempt from the lifecycle -- it is a peer file written by `detect-test-regime`.

## Consequences

**Easier:**

- Sources maintained in exactly one place. The reading guide is a relevance filter, not a second source index. Drift between routing tables is structurally impossible.
- Greenfield projects have a primary source to capture decisions before code exists. The context starts as a notepad and matures into an index.
- The transition condition is mechanically testable. `context-lint` reports `CX-SRC` findings for fields missing source pointers when in index mode.
- Concern-based routing matches how agents approach work (by task type), while decision-domain indexing matches how projects organize knowledge (by topic). Both access patterns coexist without duplication.

**Harder:**

- Four files instead of three. The reading guide adds a file that must be maintained as concerns evolve.
- The one-directional transition cannot be reversed. A project that prematurely transitions to index mode must manually restore primary mode if it needs to write inline values again. This is deliberate: the transition represents a maturity milestone, not a toggle.
- All factory consumers must understand both modes and route behavior accordingly.
