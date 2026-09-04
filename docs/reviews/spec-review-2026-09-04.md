---
title: Specification Review — Agentic Quality Reconciliation
date: 2026-09-04
scope: docs/spec/ reconciled against docs/proposals/implemented/agentic-quality-gates-and-specification-consolidation.md
reviewer: spec-review (inspect-spec skill)
---

# Specification Review — 2026-09-04

## Reviewed specification

Artifacts read: all 18 files under `docs/spec/`, the agentic-quality proposal, and the `test-gate-presence.feature` supersession. `spec-lint` summary: 0 error(s), 8 warning(s), 27 info.

## Deterministic findings (Pass 1)

| Code         | Severity | Artifact           | Status                                                                                                                                                                                                            |
| ------------ | -------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TRACE002 ×8  | warning  | docs/spec          | BR-005, -006, -018, -020, -030, -031, -033, -035 referenced but never defined. **Confirmed** — stale references to BR IDs whose definitions lived in archived UC files. Remediation: strip parenthetical BR tags. |
| TODO001      | info     | docs/spec/todos.md | 8 unresolved todo items. **Dismissed** — tracked items, not review defects.                                                                                                                                       |
| TRACE003 ×25 | info     | docs/spec          | 25 BRs defined but never referenced. **Dismissed** — informational; definitions are authoritative, unused references are not defects.                                                                             |
| TRACE004     | info     | entity-model.md    | EPIC_BUILDING_BLOCK in relationship but no attribute block. **Dismissed** — entity is a relationship participant only.                                                                                            |

## Semantic findings (Pass 2)

| Finding                                                                                                                                                                                                                               | Artifact                                                                                                 | Category | Severity | Characteristic |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | -------- | -------- | -------------- |
| [SPEC-0014](../findings/SPEC-0014.md): `REQUIRED_ARTIFACTS` omits `scope-map.md`. Proposal and both playbook terminal conditions define it as required. `check_required_artifacts()` cannot detect its absence. **Fix:** add to list. | `factory/scripts/spec-lint:82`                                                                           | Defect   | Major    | Complete       |
| `traceability.json` emits empty `actor_goals` and `use_cases` arrays. Scope-map supersedes it for `.feature`-based specifications. **Fix:** remove `--graph` output and the generated file; scope-map is the traceability mechanism.  | `factory/scripts/spec-lint`                                                                              | Defect   | Minor    | Complete       |
| 8 stale BR references (TRACE002 warnings). BR definitions lived in archived UC files; parenthetical tags are now dangling. **Fix:** strip the `(BR-NNN)` tags from prose; the rules they described are stated inline.                 | `docs/spec/prd.md`, `validation-rules.md`, `state-machines.md`, `todos.md`, `test-gate-presence-gaps.md` | Defect   | Minor    | Complete       |

## Superseded completion criteria (verified)

The following agentic-quality proposal criteria were superseded by `test-gate-presence.feature` and are correctly absent:

- `factory/scripts/mutation-analysis` — intentionally deleted. Mutation-analysis is now a skill providing setup guidance, not a gate script.
- `premerge-check` semantic gate integration — superseded by dispatcher-owned gate loop (2 gates: crap-score, dependency-check).

## Verified as implemented

- `derive-feature` skill, `scope-map-migration` skill, `qa-strategy-from-spec` skill
- `@-reference` convention in `cross-reference-format.md`
- `.feature` file acceptance test layer in `testing-strategy.md`
- `quality-gates` field in `story.md` template with precedence chain
- Feature-addition Step 1.4 mechanical architecture check with override semantics
- Greenfield and brownfield terminal conditions including `scope-map.md`
- Reconciliation-agent inputs/outputs listing scope-map, `.feature`, `@-ref` backfill
- 4 `.feature` files, 3 QA strategy documents, 3 gaps reports on disk
