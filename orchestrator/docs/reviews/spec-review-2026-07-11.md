# Specification Review — Repeat Pass

**Date**: 2026-07-11
**Reviewer**: Specification Review Agent (separate session from the author)
**Prior reports**: [spec-review-2026-07-07.md](spec-review-2026-07-07.md), [spec-review-2026-07-07-b.md](spec-review-2026-07-07-b.md)
**Result**: `spec-lint` and `statemachine-lint` both report zero errors. All eight prior `SPEC` findings verify resolved. Two new Major findings surfaced during this fresh pass; they must be addressed before architecture proceeds.

## Reviewed specification

Full spec set under `docs/spec/`: `prd.md`, `prd-tui-addendum.md`, `actor-goal-list.md`, `cli_specification.md`, `todos.md`, `traceability.json`, `use_cases/system-use-cases.md`, `use_cases/UC-01` through `UC-06` and `UC-08` through `UC-12`, and `supplementary_specs/entity-model.md`, `interface-contracts.md`, `state-machines.md`, `validation-rules.md`. `orchestrator/CONTEXT.md` read for terminology. All eight `docs/findings/SPEC-0001.md` through `SPEC-0008.md` read and individually verified against current spec text.

```
spec-lint --spec-dir docs/spec --graph docs/spec/traceability.json
  0 error(s), 13 warning(s), 18 info across 21 spec files

statemachine-lint --spec-dir docs/spec
  0 error(s), 0 warning(s), 0 info
```

## Verification of prior findings

| Finding   | Severity | Verification                                                                                                                                                                                                                       | Status       |
| --------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| SPEC-0001 | Critical | UC-10, UC-11, UC-12 each carry a `## Postconditions` heading. `STRUCT001` gone.                                                                                                                                                    | **Resolved** |
| SPEC-0002 | Major    | The five TUI sections of `system-use-cases.md` cite BR-037…041 (config), BR-042…049 (adapters), BR-050…054 (skill-scoped), BR-056…060 (backlog). `TRACE003` orphans down to two (BR-053, BR-055) — see carried-forward note below. | **Resolved** |
| SPEC-0003 | Major    | `cli_specification.md` design rule 4, the resolution-chain diagram, FR-R12, and the Model selection section all state the same two-level rule; T-34 marked resolved.                                                               | **Resolved** |
| SPEC-0004 | Major    | `interface-contracts.md` carries an authority note: the per-adapter model dictionary is the runtime source of truth; the matrix `[facts]` section populates it.                                                                    | **Resolved** |
| SPEC-0005 | Major    | UC-08 declares `Realizes: AG-08, AG-13`.                                                                                                                                                                                           | **Resolved** |
| SPEC-0006 | Major    | FR-R11 treats an absent/null tier as `standard`; VR-041 and the `interface-contracts.md` Agent Tier Extension note both restate the fallback.                                                                                      | **Resolved** |
| SPEC-0007 | Major    | `statemachine-lint` reports zero errors; the TUI navigation pseudocode and Mermaid diagram both use concrete `ROOT_MENU`/`SUB_MENU` transitions, no phantom state.                                                                 | **Resolved** |
| SPEC-0008 | Major    | FR-R12, `cli_specification.md` design rule 4, and VR-023 all state the two-level rule (agent tier vs. story classification) without a "higher-of-two" elevation.                                                                   | **Resolved** |

All eight prior findings hold under fresh inspection. No regression found in the areas they touched.

## New findings (this pass)

| Finding                                                                                                                                | Artifact                   | Category | Severity |
| -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | -------- | -------- |
| Model matrix's `phase.<name> = <tier>` policy contradicts the agent-frontmatter-tier resolution chain (Consistent, Necessary)          | `prd.md#FR-K2`             | Defect   | Major    |
| Adapter registry persistence location disagrees across `prd-tui-addendum.md`, `interface-contracts.md`, `entity-model.md` (Consistent) | `prd-tui-addendum.md#T-32` | Defect   | Major    |

Filed as [SPEC-0009](../findings/SPEC-0009.md) and [SPEC-0010](../findings/SPEC-0010.md).

**SPEC-0009 detail.** FR-K2 (original PRD, unmodified by the TUI addendum) still resolves a phase to a tier through the model-matrix policy, and the Model Matrix schema still carries `phase.<name> = <tier> | by-class`. But VR-023 and FR-R10 through FR-R12 — the newer, TUI-addendum mechanism — resolve every orchestrator-invoked agent's tier from that agent's own frontmatter alone, with no mention of the matrix's phase policy. The spec never states whether the phase-tier entry is dead, a fallback, or still authoritative for some case. This is the same class of defect SPEC-0003/SPEC-0008 fixed for agent-tier vs. story-classification, but on a different axis (phase-matrix vs. agent-frontmatter) that was never reconciled.

**SPEC-0010 detail.** T-32's resolution note says the adapter registry and model dictionaries live inside `.orchestrator/config.toml`. `interface-contracts.md`'s `Config` dataclass — the schema explicitly bound to that file — has no room for them, and defines `AdapterRegistry` as an unlocated separate port. `entity-model.md` says the registry is persisted "alongside" the configuration store, i.e., a second file. Architecture cannot proceed on three artifacts that disagree about where this state lives.

## Carried-forward Minor observations (not blocking)

- **m1** (from 2026-07-07) — VR-035 omits BR-042's "safe validation probe" clause; still present. Minor.
- **m2** (from 2026-07-07) — Twelve `FMT004` non-atomic-`shall` warnings in `system-use-cases.md` remain (compound requirements with more than one `shall`). Minor.
- **m3** (from 2026-07-07-b) — BR-053 and BR-055 (UC-11) remain defined but unreferenced elsewhere (`TRACE003`). BR-055 still duplicates FR-R11/BR-046. Minor.

## New Minor observations (this pass, not filed)

- `cli_specification.md`'s "Tier ordering: economy < standard < strong" line is a leftover from the abandoned "higher-of-two" elevation rule SPEC-0008 removed; no current rule compares tiers by order. Consider deleting it as dead prose (Necessary).
- `spec-lint` reports a new `TRACE006` warning: `todos.md` T-36 cross-references `UC-07`, which does not exist because the Scheduler/`run-all` feature it describes is deferred (see AG-07, `actor-goal-list.md` Deferred scope). The reference is intentional but reads as broken; consider dropping the dangling `UC-07` token from T-36's prose.

## Traceability summary

`spec-lint`'s graph checks (`TRACE001` orphan goals, `TRACE002` unrealized use cases) report zero. Two `TRACE003` info-level items remain (BR-053, BR-055 — see m3). One `TRACE006` warning (the intentional `UC-07` reference above). No `TRACE004`/`TRACE005` issues. Traceability is otherwise complete: every FR and AG in scope traces to a use case or subfunction, and no goal in `actor-goal-list.md` is missing a realizing use case.

## YAGNI check

Walked every FR group in `prd.md` and `prd-tui-addendum.md` against `actor-goal-list.md`. All TUI-addendum requirement groups (FR-P, FR-Q, FR-R, FR-S, FR-T, FR-U, FR-V) trace to a stated AG or SF. No gold-plating found in the use-case or requirement text itself. The one YAGNI-adjacent issue found is SPEC-0009 above: a requirement (FR-K2's phase-to-tier matrix policy) that may no longer be exercised by any actor goal now that agent-frontmatter tier governs the same case — filed as a defect rather than a pure suggestion because its retention actively conflicts with FR-R10 through FR-R12 rather than merely sitting unused.

## Disposition and handoff

`spec-lint` and `statemachine-lint` both report zero errors. All eight prior `SPEC` findings are resolved. Two new Major findings (SPEC-0009, SPEC-0010) are open and must be addressed before architecture consumes the model-resolution and adapter-registry designs.

**Handoff → Requirements Agent.** Spec review found 2 open findings (SPEC-0009, SPEC-0010). Address them, then request a repeat pass.
