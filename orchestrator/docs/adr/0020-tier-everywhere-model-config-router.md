# 0020. Tier everywhere — story tier replaces classification, model matrix becomes a tier router

**Status**: Accepted — revises [ADR-0018](0018-two-axis-tier-model-resolution.md) (story-side vocabulary only; the two-axis, two-level architecture stands); supersedes the classification/tier-pivot mechanism of [ADR-0009](0009-task-classification-and-tier-pivot-model-matrix.md); resolves [SPEC-0009](../findings/SPEC-0009.md).

## Context

ADR-0009 introduced a **tier pivot**: a story declares a difficulty `classification` (`trivial | standard | hard`), and a `[policy]` table in `model-matrix.conf` maps classification (and phase) to an abstract `tier` (`economy | standard | strong`), which per-CLI `[facts]` then resolve to a concrete model. ADR-0018 later added a second axis — an agent declares its own `tier` directly in frontmatter — and settled where each axis governs: agent tier resolves every agent the orchestrator invokes directly; story classification resolves only the tier-less developer sub-agents the implementation dispatcher commissions. The two axes never combine.

This left two vocabularies for the same concept. Agent frontmatter carries `tier` directly. A story carries `classification`, which exists only to be looked up in a table and turned into the same `tier` values. [SPEC-0009](../findings/SPEC-0009.md) flagged the resulting ambiguity: nothing in the spec said whether the matrix's `phase.<name>` policy still governed anything once agent-declared tier existed.

Reading the code surfaces a sharper problem than a wording gap. `orchestrator/src/orchestrator/model_resolver.py` has three resolution paths, not two: `resolve_agent_tier` and `resolve_story_classification` (the pair ADR-0018 decided on) plus an older `resolve(phase, classification, explicit_model)` method that still reads `[policy]` directly (`class.<name>`, `phase.<name>`). `phase_runner.py` — the code that actually executes `run-phase` — still calls that older method. `run-phase` has never been migrated to ADR-0018's agent-tier resolution; today it resolves phase agents from the (already-supposed-to-be-dead) `phase.<name>` policy line, not from the agent's own declared tier. SPEC-0009 is not just a spec inconsistency; it is live behavior lagging a decision already made.

The project owner decided to resolve both problems at once: collapse `classification` into `tier`. A story declares `tier` (`economy | standard | strong`) directly — the same field name and vocabulary as agent frontmatter — instead of a difficulty label that only ever gets translated into a tier. This does not change ADR-0018's two-axis, two-level architecture: agent tier still resolves every orchestrator-invoked agent; a story's own tier still separately drives the implementation dispatcher's tier-less developer sub-agents; the two axes still never combine on one invocation. Only the story-side vocabulary changes — from a difficulty label needing a lookup, to the tier itself.

### Alternatives (Pugh Matrix — extends ADR-0009's)

ADR-0009 compared **A** (manual `--model`), **B** (a concrete model id per CLI stored in the story), and **C** (classification → tier pivot, what was built) and picked C. It did not consider **D**: the story stores an abstract tier directly, with no separate classification vocabulary and no translation table. Same criteria and weights as ADR-0009's matrix; A, B, C carry forward unchanged.

| Criterion                            | Weight | A: manual | B: id-per-CLI in story | C: classification pivot | D: story stores tier directly |
| ------------------------------------ | ------ | --------- | ---------------------- | ----------------------- | ----------------------------- |
| Determinism of selection (Q1)        | 3      | 0         | +1                     | +1                      | +1                            |
| CLI-agnostic backlog (Q5)            | 2      | 0         | -1                     | +1                      | +1                            |
| Cost/quality control (NFR-6)         | 2      | 0         | +1                     | +1                      | +1                            |
| Maintainability as models churn (Q4) | 2      | 0         | -1                     | +1                      | +1                            |
| Simplicity (Q7)                      | 1      | 0         | 0                      | -1                      | +1                            |
| **Weighted total**                   |        | **0**     | **+1**                 | **+8**                  | **+12**                       |

D wins. It keeps every property that made C beat B — the story never holds a concrete, CLI-specific id, so it stays portable and models can be retired with a one-line facts edit — because none of those properties depended on the story-side field being *named* `classification`. They depended only on it being CLI-agnostic. D pays none of C's simplicity cost, because there is no translation table left to indirect through.

D drops one thing C had, outside what the scored criteria capture: a single policy edit (`class.standard = economy`) that re-tiered every story in a difficulty band at once — the lever ADR-0009 called "the tuning lever" and [T-20](../spec/todos.md) deferred a per-project override of. Under D, re-tiering a band of stories means editing each story's `tier` field individually. This is accepted, not overlooked — the project owner made this trade explicitly.

## Decision

1. **Single vocabulary.** A story's frontmatter field is `tier` (`economy | standard | strong`), not `classification`. Every existing story migrates 1:1: `trivial → economy`, `standard → standard`, `hard → strong`. `backlog-lint`'s required-field name and enum change to match.

2. **ADR-0018's architecture is unchanged, only revised where classification was the vocabulary.** Agent tier still resolves every orchestrator-invoked agent, at every phase (ADR-0018 §1, unchanged). A story's own `tier` still separately drives the implementation dispatcher's tier-less developer sub-agents, below the adapter boundary; the two axes still never combine on one invocation (ADR-0018 §2, vocabulary only). `resolve_story_classification` is replaced by a direct dictionary lookup on the story's `tier` — no translation table, because there is nothing left to translate.

3. **The model matrix's `[policy]` section is deleted.** `class.<name>` is redundant (a story's `tier` already is the tier). `phase.<name>` was already dead — ADR-0018 made agent-declared tier the sole resolver for every orchestrator-invoked agent, including phase agents; nothing but the deprecated `resolve()` method still read it. With `[policy]` empty, the artifact is no longer a two-axis matrix — it is a flat, per-CLI **tier router**: `[facts]` (tier → concrete model) plus `on_missing`.

4. **Rename `model-matrix.conf` to `model.conf`**, at every location it exists (root `config/`, `factory/config/` template, orchestrator's own operational copy at `orchestrator/model-matrix.conf`). Update its header comment to describe a tier router, not a two-part policy/facts artifact.

5. **Dead code removed.** `ModelResolver.resolve()`, `ModelMatrix.get_tier()`, `FileModelMatrix.policy`, and the `_CLASSIFICATION_TIER` table are deleted. `phase_runner.py` is fixed to call `resolve_agent_tier` for the phase's author and reviewer agents (closing the ADR-0018 migration gap this ADR's Context section surfaced) and to resolve each developer sub-agent's model from the story's `tier` field directly.

6. **Spec updated to match.** `FR-K1`–`FR-K5`, `FR-R10`–`FR-R12`, `VR-023`, `VR-024`, `VR-041`, and the `StoryFrontmatter` and Model Matrix schemas in `interface-contracts.md` — `classification` becomes `tier` throughout; `[policy]` language is removed; "model matrix" becomes "model config" / "tier router" wherever it described the now-gone two-axis behavior. `docs/CONTEXT.md`'s `Classification`, `Tier`, and `Model matrix` glossary entries are updated to match. This closes [SPEC-0009](../findings/SPEC-0009.md).

7. **`matrix-lint`'s scope shrinks** to validating `[facts]` completeness only. Its name no longer matches what it checks — no matrix remains to lint. A rename (e.g. `model-lint`) is a follow-up recommendation, not decided here.

8. **T-20 is obsolete.** The per-project policy override it deferred assumed a policy layer to override; none remains. Mark it resolved-by-obsolescence in `docs/spec/todos.md`, not left open.

## Consequences

**Positive**

- One vocabulary, one field, no lookup — a reader learns `tier` once and it means the same thing everywhere.
- `model.conf` is honestly named: it routes a tier to a model per CLI, nothing more.
- Deleting `resolve()` removes a code path that silently diverged from the decided architecture — `phase_runner.py`'s fix closes a real gap between ADR-0018 and what `run-phase` actually did.

**Negative / risks**

- Loses the single-edit, project-wide re-tiering lever `classification` gave (see the Pugh Matrix note above) — a deliberate trade, not an oversight.
- Every existing backlog story needs a mechanical frontmatter migration (`classification` → `tier`, value remapped) before `backlog-lint` accepts it.
- `matrix-lint`, the TUI's `configure > model-matrix > edit` menu label, and any remaining "model matrix" prose outside the files listed in Decision §6 will read stale until renamed in follow-up work; this ADR does not enumerate every prose site.

## Follow-up (not done in this pass — this ADR is the design record, not the migration)

- Rename `model-matrix.conf` → `model.conf` (`config/`, `factory/config/`, `orchestrator/model-matrix.conf`); strip `[policy]`.
- Update `backlog-lint` (field rename, enum change) and every existing story under `orchestrator/backlog/`.
- Delete `ModelResolver.resolve()`, `ModelMatrix.get_tier()`, `FileModelMatrix.policy`, `_CLASSIFICATION_TIER`; fix `phase_runner.py` to call `resolve_agent_tier` / story-tier lookup.
- Update `FR-K1`–`FR-K5`, `FR-R10`–`FR-R12`, `VR-023`, `VR-024`, `VR-041`, `interface-contracts.md`, `docs/CONTEXT.md`.
- Consider renaming `matrix-lint` and the TUI's `model-matrix` menu label for consistency.

## Referenced from

- [SPEC-0009](../findings/SPEC-0009.md)
