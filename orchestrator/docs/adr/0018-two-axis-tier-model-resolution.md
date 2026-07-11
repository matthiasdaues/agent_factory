# 0018. Two-axis tier model resolution — agent tier and story classification at two levels

**Status**: Accepted — revises ADR-0009 (resolution mechanism); resolves T-34; corrected by SPEC-0008. Story-side vocabulary (point 2 below) revised by [ADR-0020](0020-tier-everywhere-model-config-router.md) — the two-axis, two-level architecture decided here still stands.

## Context

ADR-0009 resolves a model from a **story's classification** (or a phase default) through the operator-curated model matrix. The TUI addendum adds a second axis: an **agent declares the `tier`** its task needs in front-matter (FR-R10), and `run-step` runs an agent with no story context at all, so classification cannot apply there (FR-R11). It also introduces per-adapter **model dictionaries** (ADR-0017) that map a tier to a concrete model.

This left the model-selection rule specified three incompatible ways at once — max of the two axes, agent tier only, and classification via the matrix — which the spec review flagged (SPEC-0003) and the addendum tracked as T-34. Two questions must be settled together: **at what level each axis applies** (the axes do not combine on one invocation — an initial resolution tried a "higher-of-two elevation" and was corrected by SPEC-0008), and which artifact is the runtime source of truth for the tier→model mapping now that both a matrix and per-adapter dictionaries exist.

### Alternatives (Pugh Matrix)

Baseline **A**: keep ADR-0009 unchanged — classification/phase → tier via the matrix, no agent-tier axis. **B**: agent tier fully replaces classification everywhere; the story's difficulty no longer influences the model. **C**: two axes at two levels — agent tier resolves every agent the orchestrator invokes directly (all phases); story classification is the sole determinant of the tier-less developer sub-agents the implementation dispatcher commissions; the axes never combine; the adapter dictionary is the runtime source of truth, populated from the matrix facts.

| Criterion                                               | Weight | A: classification only | B: agent tier only | C: two-axis |
| ------------------------------------------------------- | ------ | ---------------------- | ------------------ | ----------- |
| Determinism / single unambiguous rule (Q1)              | 3      | +1                     | +1                 | +1          |
| Fits run-step (no story context) (FR-R11)               | 3      | -1                     | +1                 | +1          |
| Preserves implementation difficulty sensitivity (NFR-6) | 2      | +1                     | -1                 | +1          |
| CLI-agnostic backlog (Q5)                               | 2      | +1                     | +1                 | +1          |
| Simplicity (Q7)                                         | 1      | +1                     | +1                 | -1          |
| **Weighted total**                                      |        | **+4**                 | **+6**             | **+13**     |

C wins. Classification-only (A) cannot express `run-step`. Agent-tier-only (B) throws away the difficulty signal that made a hard implementation story get the strong model — the very lever ADR-0009 introduced. The two-level rule keeps both by assigning each axis to the level where it actually decides a model, so no invocation ever needs to reconcile the two.

## Decision

1. **Agent tier is the primary axis.** `ModelResolver` resolves an agent's declared `tier` (`economy` < `standard` < `strong`) to a concrete model through the **active adapter's model dictionary**. For `run-step`, the agent's tier applies directly; `--model` overrides the whole chain. For `run-phase`, each invoked agent resolves independently; there is no phase-level `--model`.

2. **Story classification governs the developer sub-agents, at a lower level.** During the implementation phase the `implementation-agent` acts as a dispatcher: it reads each ready story's `classification` and assigns that story's developer sub-agent a model from the classification **alone**. Developer agents declare **no tier** by design — the model for a unit of work is the dispatcher's decision, and the classification is its single source of truth. This selection happens below the adapter boundary (FR-M); the orchestrator sees one `implementation-agent` invocation, resolved from that agent's own tier per point 1. The two axes never combine on a single invocation.

3. **The adapter dictionary is the runtime source of truth**; the model matrix is the operator-authored artifact that **populates** it (ADR-0017). Runtime resolution never reads the matrix file directly.

4. **Null tier resolves as `standard`** (VR-041) for orchestrator-invoked agents, so every such agent resolves a model before all definitions carry an explicit tier. This fallback does not apply to developer sub-agents, which are tier-less by design and resolved by classification (point 2). An unresolved required tier halts as a configuration error unless adapter-default fallback is enabled (FR-K4, BR-020).

## Consequences

**Positive**

- One unambiguous rule replaces three contradictory statements; the axes compose predictably (Q1).
- `run-step` gets a well-defined model without inventing a story, while implementation keeps its difficulty sensitivity (FR-R11, NFR-6).
- The backlog stays CLI-agnostic — a story still stores only its classification; concrete model ids live only in adapter dictionaries (Q5).

**Negative / risks**

- ADR-0009's resolution mechanism is revised: the runtime now reads adapter dictionaries, not the matrix directly. ADR-0009's classification model and its facts/policy separation stand; only the read path changes.
- The two-level split is a distinction a reader must hold: agent tier for orchestrator-invoked agents, classification for the dispatcher's developer sub-agents. It is the price of keeping difficulty sensitivity without a false "combine the axes" step.
- The `standard` default for a null tier is a convenience that could mask a missing, deliberately-chosen tier; orchestrator-invoked agents should declare one explicitly. Developer agents are deliberately tier-less and are exempt.
