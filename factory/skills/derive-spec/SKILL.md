---
name: derive-spec
description: Derive the full specification chain from a PRD — actor-goal list, persona use cases, system use cases, supplementary specs.
category: requirements
disable-model-invocation: true
---

# Derive Specification

A four-step pipeline that takes a PRD and produces a complete, cross-referenced specification. Each step feeds the next — do not skip ahead or work multiple steps simultaneously.

Read `docs/CONTEXT.md` if it exists — match the project's domain vocabulary in every artifact.

## Step 1 — Actor-Goal List

Read `docs/spec/prd.md`. For each actor, list every goal they have against the system.

Apply the **goal-level test**: _"Does the actor go home happy if this goal is achieved?"_ If yes, it's a **User Goal**. If not, it's a **Subfunction** — extract only when reused across multiple use cases.

Save as `docs/spec/actor-goal-list.md` — a table with columns: ID, Actor, Goal, Level. Give every goal a unique ID — `AG-01`, `AG-02`, … These IDs anchor the traceability graph.

## Step 2 — Persona Use Cases

For each User Goal, write a use case in **Cockburn's Fully Dressed format** — see [COCKBURN.md](COCKBURN.md) for the template and rules.

Each use case declares which User Goal it realizes with a `Realizes: AG-##` line near the top — the traceability link the review step uses to confirm every goal is covered.

Then add, per use case:

- **Activity Diagram** in **Mermaid** covering all flows — happy path _and_ extensions
- Acceptance criteria in **Gherkin**

Save each use case as `docs/spec/use_cases/UC-XX-short-name.md`.

## Step 3 — System Use Cases

Apply **Clean Architecture** to define system boundaries.

For each system interface (API endpoint, CLI command, gRPC service, event, file format), specify:

- Trigger and Preconditions (technical: HTTP method, auth token, system state)
- Input: format, validation rules, constraints
- Processing: steps the system performs (reference Business Rules by ID)
- Output: response format, status codes, payload schema
- Error responses: codes, messages, recovery hints
- Non-functional: performance budget, rate limits, timeouts

Use **EARS syntax** — see [EARS.md](EARS.md) — for individual requirements where applicable.

Save as `docs/spec/use_cases/system-use-cases.md`.

## Step 4 — Supplementary Specifications

Apply **Clean Architecture** and **SOLID** — Dependency Inversion and Interface Segregation for interface contracts, Single Responsibility for entity design.

Create (as applicable to the project):

1. **Entity Model** — create a specification-level **Mermaid** ERD of the
   domain. Save it as `docs/spec/supplementary_specs/entity-model.md`.

   The ERD defines stakeholder-visible domain facts before architecture begins:

   - Model top-level domain entities, their essential semantic attributes, and
     exact relationship cardinalities. For example, a Tenant contains one or
     more Domains and every Domain belongs to exactly one Tenant.
   - Include a concept only when it appears in the PRD, use cases, business
     rules, or ubiquitous language. State important relationship constraints in
     prose below the diagram when Mermaid cannot express them precisely.
   - Use domain names and domain-level identifiers. Attributes may express
     identity or required business meaning, but must not prescribe a database
     representation.
   - Do not model architecture or persistence mechanisms such as tables,
     primary/foreign-key annotations, database-specific types, outboxes, claim
     leases, transport messages, payload hashes, denormalized counters, or
     storage partitions. An otherwise technical-looking concept belongs only if
     stakeholders observe it as part of the domain and the specification defines
     its semantics independently of implementation.
   - Do not use the ERD to allocate ownership to components or containers. The
     architecture phase decides representation, persistence, messaging,
     recovery mechanisms, and deployment boundaries.

   The result answers *which domain concepts exist and how they relate*, not
   *how the system stores or transports them*.

2. **State Machines** — for entities with lifecycle behavior. Write On If/Else pseudocode first, then derive **Mermaid** state diagrams. Save as `docs/spec/supplementary_specs/state-machines.md`.

3. **Interface Contracts** — DTOs and schemas at system boundaries. Save as `docs/spec/supplementary_specs/interface-contracts.md`.

4. **Validation Rules** — cross-cutting rules not tied to a single use case, numbered and cross-referenced. Save as `docs/spec/supplementary_specs/validation-rules.md`.

## Output

```
docs/spec/
├── actor-goal-list.md
├── use_cases/
│   ├── UC-XX-short-name.md  (one per User Goal)
│   └── system-use-cases.md
└── supplementary_specs/
    ├── entity-model.md
    ├── state-machines.md
    ├── interface-contracts.md
    └── validation-rules.md
```

All files cross-reference each other with relative Markdown links and Use Case IDs.

Format each file via `scripts/mdformat --number <path>` as it's written, per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).
