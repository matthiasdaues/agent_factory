---
id: "0016"
status: accepted
evaluation: none
---

# Concern-oriented agent context replaces YAML index

## Context

ADR-0013 replaced the markdown charter with four YAML index files
(`stack.yaml`, `workflow.yaml`, `governance.yaml`, `reading-guides.yaml`)
under `docs/agent-context/`. ADR-0014 added two-layer routing and a
two-mode lifecycle on top of that format.

Two problems surfaced in production use:

1. **Four files are four places to drift.** Maintaining consistent
   source pointers across three index files and one routing file created
   the same staleness problem the YAML format was meant to solve.

2. **Two-mode lifecycle added complexity without payoff.** The
   primary-to-index transition was mechanically testable but never
   triggered in practice. Every project either stayed in primary mode
   or skipped straight to a concern-based layout.

The concern-oriented agent context proposal demonstrated that a single
markdown file with concern sections and `Read:` paths satisfies every
consumer that the four YAML files served, with less maintenance overhead.

## Decision

Replace the four YAML agent-context files with a single CLI-agnostic
markdown file: `docs/agent-context.md`. Agents discover project
knowledge through three concern categories (cross-cutting, technical,
domain), each carrying `Read:` paths. Stories declare concerns in
frontmatter. `concern-lint` replaces `context-lint`, validating with
`CTX-*` finding codes. `testing.yaml` remains a separate file at
`docs/testing.yaml`.

This supersedes [ADR-0013](0013-yaml-agent-context-replaces-markdown-charter.md)
and [ADR-0014](0014-two-layer-routing-with-two-mode-lifecycle.md).

See the [concern-oriented agent context proposal](../proposals/factory-concern-oriented-agent-context.md).

## Consequences

**Easier:**

- One file to maintain instead of four. No source-pointer drift.
- Concern sections match how agents approach work. No indirection
  through key-path references.
- `capture-context` auto-detects old YAML format and offers migration.

**Harder:**

- Projects that adopted the YAML format must migrate. The migration
  is automated but requires a session.
- Per-field source pointers are gone. The tradeoff is accepted:
  concern-level `Read:` paths are coarser but sufficient, and they
  do not drift.
