---
title: Agent Context Composition
category: architecture
enforcement: concern-lint (CTX-* codes), rules.md
version: 3.0.0
---

# Agent Context Composition

`docs/agent-context.md` is the factory-facing interface between agents and a
project's own knowledge. It routes agents by concern name, not by file path.
Each concern carries a description and file references that tell an agent
where to read, never what it will find there. This document states the
binding rules that keep that interface honest as a project matures.

Design origin: [factory-concern-oriented-agent-context.md](../../../docs/proposals/factory-concern-oriented-agent-context.md).

## The concern model

Agent context is organized into three concern categories, distinguished by
when they are active:

| Category      | When active                       | Examples                                                                       |
| ------------- | --------------------------------- | ------------------------------------------------------------------------------ |
| Cross-cutting | Always. Every agent, every story. | Branching, committing, testing discipline, review, scope discipline, security. |
| Technical     | Per story, set by planning-agent. | Backend, frontend, data-storage; or data-source, processing, visualization.    |
| Domain        | Per story, set by planning-agent. | Varies by project — derived from scope map areas or specification structure.   |

Cross-cutting concerns are the professional baseline — an agent is always
aware of them, the way a human colleague always knows the branching policy.
Technical concerns narrow the stack context per task. Domain concerns focus
the product knowledge.

## The `agent-context.md` structure

The concern registry lives in `docs/agent-context.md`, organized by
category. Each concern is a `###` heading beneath its category's `##`
heading, carrying:

- A one-line description of what knowledge it covers.
- One or more `Read:` lines listing the current paths where that knowledge lives.
- Optional `Boundary:` lines naming cross-concern interfaces to respect.

Required `##` category headings:

1. `## Always (cross-cutting)`
2. `## Technical concerns`
3. `## Domain concerns`

Example:

```markdown
# Agent Context

## Always (cross-cutting)

### Branching
Branching policy and worktree discipline.
Read: factory/rulebooks/conventions/branching-policy.md

### Testing discipline
Risk-based testing, test admission, layer ownership.
Read: docs/handbook/testing/conventions.md, docs/handbook/testing/strategy.md

## Technical concerns

### backend
Server-side application code: routes, models, services, repositories.
Read: docs/handbook/backend/conventions.md, docs/handbook/backend/cookbook/*.md
Boundary: docs/spec/supplementary_specs/interface-contracts.md

## Domain concerns

### payments
Payment processing domain logic.
Read: docs/spec/payments.feature, docs/spec/supplementary_specs/payment-rules.md
```

## Controlled vocabulary

The concern names in `agent-context.md` form a controlled vocabulary. The
planning-agent writes a `concerns` field into each story's frontmatter,
picking from this vocabulary:

```yaml
concerns:
  domain: [payments]
  technical: [backend, frontend]
```

Cross-cutting is absent because it is always active — no declaration needed.
If a story needs a concern that does not exist in the registry, the
planning-agent proposes the new concern section for user confirmation rather
than coining a name silently. This keeps the vocabulary stable and
intentional.

## Advisory nature

The concerns field is advisory — it tells the agent what is relevant, not
what is permitted. The agent always has access to the full registry via the
include chain. Cross-cutting concerns are always visible, and peripheral
awareness of adjacent technical or domain concerns helps the agent respect
boundaries it does not own.

## Derived content

Agent context is always derived content. It links to sources maintained
elsewhere (handbook, ADRs, specifications, code); it is never the primary
authority. When a file moves, the human edits the path in the concern
entry. When a new concern emerges, the human or the planning-agent adds a
section.

## `testing.yaml` carve-out

`testing.yaml` is machine-consumed configuration (test commands, suite
definitions, gate thresholds), not a routing artifact. It remains a YAML
file and is validated separately by `detect-test-regime` and gate scripts.
`concern-lint` does not validate `testing.yaml`. A `testing.yaml` file
under `docs/agent-context/` does not trigger the CTX-LEGACY check.

## Validation: concern-lint

`concern-lint` validates `docs/agent-context.md` with three checks:

| Check             | ID           | What it validates                                                                                                              |
| ----------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| Section structure | CTX-SECTIONS | Every required category heading exists. Each concern section has a description line and at least one `Read:` path.             |
| Path resolution   | CTX-PATHS    | Every path in a `Read:` or `Boundary:` line resolves to an existing file or glob match.                                        |
| No legacy residue | CTX-LEGACY   | No `.yaml` files (other than `testing.yaml`) under `docs/agent-context/`, and no `docs/charter/` directory alongside the file. |

`concern-lint` exits 0 when all checks pass and non-zero when any check
fails. It runs as part of the `validate` skill (gate #12) and as a
pre-commit hook.
