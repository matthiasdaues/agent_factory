# 0020. Tier everywhere — story tier replaces classification, model matrix becomes a tier router

**Status**: Accepted — revises [ADR-0018](0018-two-axis-tier-model-resolution.md) (story-side vocabulary only; architecture stands); supersedes the tier-pivot mechanism of [ADR-0009](0009-task-classification-and-tier-pivot-model-matrix.md); resolves [SPEC-0009](../findings/SPEC-0009.md). [ADR-0021](0021-adapter-registry-discovery-and-precedence.md) confirms `model.conf` is read directly at resolution time — its `[policy]` removal here stands unchanged.

> **Amended 2026-07-12 (PhaseRunner collapse):** `model.conf` still exists and `FileModelMatrix` still reads it for menu display and management; the tier→model resolution at invocation time this ADR describes moved to `factory/`. See the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`.

## Context

ADR-0009 introduced a **tier pivot**: a story declares a difficulty `classification` (`trivial | standard | hard`), which a `[policy]` table in `model-matrix.conf` maps to an abstract `tier` (`economy | standard | strong`), which per-CLI `[facts]` resolve to a concrete model. ADR-0018 added a second axis — an agent declares its own `tier` directly — and split governance: agent tier resolves every agent the orchestrator invokes directly; story classification resolves only the implementation dispatcher's tier-less developer sub-agents. The two axes never combine.

This left two vocabularies for one concept. Agent frontmatter carries `tier` directly; a story carries `classification`, looked up in a table to produce the same `tier` values. [SPEC-0009](../findings/SPEC-0009.md) flagged the fallout: nothing said whether the matrix's `phase.<name>` policy still governed anything once agent-declared tier existed.

The code shows a sharper problem than a wording gap. `orchestrator/src/orchestrator/model_resolver.py` has three resolution paths, not two: `resolve_agent_tier` and `resolve_story_classification` (the pair ADR-0018 decided on), plus an older `resolve(phase, classification, explicit_model)` that still reads `[policy]` directly. `phase_runner.py` — the code that runs `run-phase` — still calls that older method; `run-phase` was never migrated to ADR-0018's agent-tier resolution. SPEC-0009 is not just a spec inconsistency; it is live behavior lagging a decision already made.

The fix: collapse `classification` into `tier`, without touching ADR-0018's two-axis architecture. Decision, below.

### Alternatives (Pugh Matrix — extends ADR-0009's)

ADR-0009 compared **A** (manual `--model`), **B** (a concrete model id per CLI in the story), and **C** (classification → tier pivot, what was built) and picked C. It never considered **D**: the story stores an abstract tier directly, no classification vocabulary, no translation table. Same criteria and weights as ADR-0009's matrix; A, B, C carry forward unchanged.

| Criterion                            | Weight | A: manual | B: id-per-CLI in story | C: classification pivot | D: story stores tier directly |
| ------------------------------------ | ------ | --------- | ---------------------- | ----------------------- | ----------------------------- |
| Determinism of selection (Q1)        | 3      | 0         | +1                     | +1                      | +1                            |
| CLI-agnostic backlog (Q5)            | 2      | 0         | -1                     | +1                      | +1                            |
| Cost/quality control (NFR-6)         | 2      | 0         | +1                     | +1                      | +1                            |
| Maintainability as models churn (Q4) | 2      | 0         | -1                     | +1                      | +1                            |
| Simplicity (Q7)                      | 1      | 0         | 0                      | -1                      | +1                            |
| **Weighted total**                   |        | **0**     | **+1**                 | **+8**                  | **+12**                       |

D wins: it keeps everything that made C beat B — the story never holds a concrete, CLI-specific id — because none of that depended on the field being *named* `classification`. D pays none of C's simplicity cost, since there is no translation table to indirect through.

D drops one thing outside the scored criteria: `class.standard = economy`, a single edit that re-tiered every story in a band at once — the lever ADR-0009 called "the tuning lever" and [T-20](../spec/todos.md) deferred a per-project override of. Under D, re-tiering a band means editing each story's `tier` individually. Accepted, not overlooked.

## Decision

1. **Single vocabulary.** A story's frontmatter field is `tier` (`economy | standard | strong`), not `classification`. Every existing story migrates 1:1: `trivial → economy`, `standard → standard`, `hard → strong`. `backlog-lint`'s required field and enum change to match.

2. **ADR-0018's architecture stands; only the vocabulary it names changes.** Agent tier still resolves every orchestrator-invoked agent, at every phase (ADR-0018 §1). A story's own `tier` still drives the dispatcher's tier-less developer sub-agents, below the adapter boundary; the two axes still never combine (ADR-0018 §2). `resolve_story_classification` becomes a direct dictionary lookup on the story's `tier` — no translation table, nothing left to translate.

3. **The model matrix's `[policy]` section is deleted.** `class.<name>` is redundant (a story's `tier` already is the tier). `phase.<name>` was already dead — ADR-0018 made agent-declared tier the sole resolver for phase agents; only the deprecated `resolve()` still read it. With `[policy]` empty, the artifact is a flat, per-CLI **tier router**: `[facts]` plus `on_missing`.

4. **Rename `model-matrix.conf` to `model.conf`**, everywhere it exists (`config/`, `factory/config/`, `orchestrator/model-matrix.conf`). Its header describes a tier router, not a policy/facts pair.

5. **Dead code removed.** `ModelResolver.resolve()`, `ModelMatrix.get_tier()`, `FileModelMatrix.policy`, `_CLASSIFICATION_TIER` are deleted. `phase_runner.py` calls `resolve_agent_tier` for the phase's author and reviewer, and resolves each developer sub-agent from the story's `tier` directly — closing the migration gap Context surfaced.

6. **Spec updated to match.** `FR-K1`–`FR-K5`, `FR-R10`–`FR-R12`, `VR-023`, `VR-024`, `VR-041`, and the `StoryFrontmatter`/Model Matrix schemas in `interface-contracts.md`: `classification` becomes `tier`, `[policy]` language is removed, "model matrix" becomes "model config"/"tier router" where it described the now-gone two-axis behavior. `docs/CONTEXT.md`'s `Classification`, `Tier`, `Model matrix` entries updated to match. Closes [SPEC-0009](../findings/SPEC-0009.md).

7. **`matrix-lint` shrinks** to validating `[facts]` completeness only; its name no longer matches what it checks. A rename (e.g. `model-lint`) is a follow-up recommendation, not decided here.

8. **T-20 is obsolete.** It deferred a per-project override of a policy layer that no longer exists. Marked resolved-by-obsolescence in `docs/spec/todos.md`.

None of the above is executed in this pass — this ADR is the design record. Points 1, 3–7 are the punch list.

## Consequences

**Positive**

- One vocabulary, one field, no lookup.
- `model.conf` is honestly named: it routes a tier to a model per CLI, nothing more.
- Deleting `resolve()` removes a code path that had silently diverged from the decided architecture; the `phase_runner.py` fix closes a real gap between ADR-0018 and what `run-phase` actually did.

**Negative / risks**

- Loses the single-edit, project-wide re-tiering lever `classification` gave — a deliberate trade, not an oversight.
- Every existing backlog story needs a mechanical frontmatter migration before `backlog-lint` accepts it.
- `matrix-lint`, the TUI's `configure > model-matrix > edit` menu label, and any "model matrix" prose outside Decision §6 will read stale until renamed; this ADR does not enumerate every prose site.

## Referenced from

- [SPEC-0009](../findings/SPEC-0009.md)
