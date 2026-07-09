---
name: maintain-architecture
description: Maintain arc42 architecture docs with architecture.dsl as the single source of truth. Covers DSL-first workflow, image export, Mermaid derivation, and state machine pseudocode.
category: architecture
disable-model-invocation: true
---

# Maintain Architecture

Update architecture documentation with `architecture.dsl` as the **single source of truth** for all structural and runtime views. Prose chapters narrate and extend the model; they never contradict it.

Read `CONTEXT.md` if it exists — use the project's domain vocabulary throughout.

## Principle: DSL first, prose second

The Structurizr DSL (`docs/architecture.dsl`) owns:

- **What exists** — systems, containers, components, deployment nodes
- **How they connect** — relationships with descriptions and technologies
- **Interaction sequences** — dynamic views define the canonical step order

Prose chapters (`docs/01_*.md` through `docs/12_*.md`) own:

- **Why** — rationale, trade-offs, design rules
- **Contracts** — DTOs, validation rules, schemas
- **Behaviour not expressible in Structurizr** — state machines, flowcharts, decision tables

## Step 1 — Update the DSL model

Before touching any prose chapter, update `docs/architecture.dsl`:

1. **Static model** — add/rename/remove elements and relationships.
2. **Dynamic views** — add or update `dynamic` views for runtime scenarios. Each step references an existing model relationship.
3. **Deployment** — update `deploymentEnvironment` nodes if the deployment topology changes.

Validate after every change:

```bash
scripts/structurizr validate
```

**Completion**: DSL validates without errors. All new elements/relationships appear in the model.

## Step 2 — Export images

Export all views as PNG and SVG:

```bash
scripts/structurizr export-all
```

This overwrites `docs/assets/images/` with the current model.

**Completion**: images match the DSL. Do not commit yet.

## Step 3 — Update prose chapters

Update the relevant arc42 chapters to match the model. The mapping:

| DSL view         | Chapter                | Image reference                                        |
| ---------------- | ---------------------- | ------------------------------------------------------ |
| `SystemContext`  | §3 System Scope        | `![System Context](assets/images/SystemContext.png)`   |
| `Containers`     | §5.1 Building Block L1 | `![Containers](assets/images/Containers.png)`          |
| `CoreComponents` | §5.2 Building Block L2 | `![Core Components](assets/images/CoreComponents.png)` |
| Dynamic views    | §6 Runtime View        | Mermaid sequence diagrams (see Step 4)                 |
| `Deployment`     | §7 Deployment View     | `![Deployment](assets/images/Deployment.png)`          |

For chapters 5 (tables) and 9 (ADR index): element names and port lists must match the DSL. `arch-lint` enforces this for components and ports.

Format every updated chapter via `scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/markdown-formatting.md).

**Completion**: `arch-lint --docs-dir docs` reports 0 errors. Do not commit yet.

## Step 4 — Derive Mermaid diagrams from DSL dynamic views

Structurizr dynamic views define the canonical interaction sequence. Mermaid sequence diagrams in chapter 6 render these with richer notation (return arrows, `loop`/`alt` blocks, `Note over`).

Rules:

1. **Participants** must match DSL identifiers. Use Mermaid aliases: `participant PR as PhaseRunner` where `phaseRunner` is the DSL variable.
2. **Step order** must match the DSL dynamic view numbering.
3. **Descriptions** should match DSL step descriptions verbatim or be a natural expansion.
4. Each Mermaid section cites its source: `Derived from dynamic view \`ViewKey\` in [\`architecture.dsl\`](architecture.dsl).\`
5. Mermaid may add: return arrows (`-->>`, dotted), `loop`/`alt`/`opt` blocks, `Note over` annotations. These are rendering enhancements — they must not introduce steps absent from the DSL.

### What stays in Mermaid only (no DSL equivalent)

| Diagram type                      | Why                                   | Where                                    |
| --------------------------------- | ------------------------------------- | ---------------------------------------- |
| State machine (`stateDiagram-v2`) | Structurizr has no state machine view | `state-machines.md`                      |
| Flowchart (`flowchart TD`)        | Structurizr has no flowchart view     | §6.3 gate outcomes, UC activity diagrams |
| Short/simple sequences            | Not worth a DSL view                  | §6.5 resume, §6.6 status                 |

## Step 5 — Maintain state machine pseudocode

Canonical pseudocode format, reserved actions, and the pseudocode→Mermaid derivation rules: [state-machine-notation.md](../../rulebooks/state-machine-notation.md).

```bash
scripts/statemachine-lint --spec-dir docs/spec
```

**Completion**: `statemachine-lint` reports 0 errors.

## Commit

After all steps pass, commit everything in one atomic commit:

```bash
git add docs/
git commit -m "docs: update architecture documentation"
```

Pre-commit hooks (`arch-lint`, `statemachine-lint`) fire on this commit and enforce full consistency. If any hook fails, fix and retry.
