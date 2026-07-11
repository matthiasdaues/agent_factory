# 0009. Task classification and a tier-pivot model matrix

**Status**: Superseded by [ADR-0020](0020-tier-everywhere-model-config-router.md) — the classification/tier-pivot mechanism below is replaced by a story-declared tier; the underlying need (difficulty-aware model selection) still stands.

## Context

Different tasks deserve different models: a trivial edit wastes money on the strongest model, and a hard task fails on the cheapest. A live spike confirmed the orchestrator can already set the model per invocation (`--model`), and that model ids differ per CLI (`gpt-5.4`, `claude-opus-4-8`). We want the orchestrator to choose a model per task automatically, driven by the planning phase's understanding of the work, while keeping the backlog CLI-agnostic (NFR-5) and the choice deterministic (NFR-1) and cost-aware (NFR-6).

Two decisions compose here: how tasks are classified, and how a classification becomes a concrete model for whichever CLI runs.

### Classification

The planning agent classifies each story by difficulty — `trivial`, `standard`, `hard` — as it writes the backlog. This is sound because planning already analyses each story against the dependency tree and runs on a strong model, so a story that looks trivial but touches a gnarly file is caught and marked `hard` at planning time. A separate manual override is therefore unnecessary; an operator who disagrees re-classifies the story. Difficulty, not task type, is the axis, because model strength tracks difficulty: a hard test and a hard implementation both want the strong model.

### Alternatives for resolution (Pugh Matrix)

Baseline **A**: no policy — the operator sets `--model` by hand each run. **B**: the story stores a concrete model id per CLI (direct mapping in the backlog). **C**: a tier pivot — the story stores only its classification; a matrix maps classification (and phase) to an abstract tier (`economy`, `standard`, `strong`), and per-CLI facts map a tier to a concrete model.

| Criterion                            | Weight | A: manual | B: id-per-CLI in story | C: tier pivot |
| ------------------------------------ | ------ | --------- | ---------------------- | ------------- |
| Determinism of selection (Q1)        | 3      | 0         | +1                     | +1            |
| CLI-agnostic backlog (Q5)            | 2      | 0         | -1                     | +1            |
| Cost/quality control (NFR-6)         | 2      | 0         | +1                     | +1            |
| Maintainability as models churn (Q4) | 2      | 0         | -1                     | +1            |
| Simplicity (Q7)                      | 1      | 0         | 0                      | -1            |
| **Weighted total**                   |        | **0**     | **+1**                 | **+8**        |

C wins clearly. Storing ids in the story (B) couples the backlog to a CLI and rots when a model is retired — every story must be rewritten. The tier pivot (C) confines CLI specifics to one small facts table and keeps the backlog portable; its only cost is one level of indirection.

## Decision

- **Classification**: the planning phase assigns each story `trivial | standard | hard` (BR-021, FR-K1); it is a required, `backlog-lint`-validated frontmatter field.
- **Tier pivot**: a **model matrix** maps classification and phase to a tier (CLI-agnostic *policy*), and tier plus CLI to a concrete model (per-CLI *facts*). Selection resolves classification/phase → tier → model.
- **Precedence**: `--model` flag overrides the matrix, which overrides the adapter default (FR-K3). No per-story model field — re-classification is the tuning lever.
- **Fallback**: an unresolved tier for the active CLI halts as a config error by default, configurable to the adapter default (FR-K4, BR-020).
- **Facts and policy are separate sections** so a project can later override policy (its budget stance) without touching facts (T-20).
- The matrix is a **first-class, operator-curated artifact** with its own maintenance workstep and a `matrix-lint` gate (FR-K5); it is not a chain output, because model facts are CLI-global and change on their own cadence.

## Consequences

**Positive**

- Model choice is automatic, deterministic, and tuned to difficulty — the cost/quality lever the requirement asked for (NFR-1, NFR-6).
- The backlog stays CLI-agnostic; adding or retiring a model is a one-line facts edit, not a backlog rewrite (Q5, Q4).
- The same matrix governs non-task phases through phase-defaults (e.g. `planning`, `qa` → strong), so model control is coherent across the whole chain.

**Negative / risks**

- One more artifact and one more indirection (classification → tier → model) to understand and keep valid; `matrix-lint` guards the dangling-tier failure mode.
- Classification quality depends on the planner running on a strong model — a mild self-reference, since the matrix sets `planning → strong`. A misconfigured planner tier would degrade every downstream classification.
- The shared matrix currently encodes one budget stance for all projects; per-project policy override is deferred (T-20).
