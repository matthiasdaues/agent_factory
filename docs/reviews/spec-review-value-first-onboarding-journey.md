---
type: inspect-spec
title: "Specification review — value-first onboarding journey (repeat pass)"
date: 2026-09-23
status: pass
reviewer: spec-review-agent
findings_filed: 0
scope: value-first-onboarding-journey feature specification and supplementary specs
---

# Specification Review — Value-First Onboarding Journey (Repeat Pass)

## Reviewed Specification

Artifacts read:

- [value-first-onboarding-journey.feature](../spec/value-first-onboarding-journey.feature) -- 9 Rules, 31 Scenarios
- [value-first-onboarding-journey-gaps.md](../spec/value-first-onboarding-journey-gaps.md) -- actor-goal matrix and boundary coverage
- [value-first-onboarding-journey-qa-strategy.md](../spec/value-first-onboarding-journey-qa-strategy.md) -- test layer assignments and contract owners
- [scope-map.md](../spec/scope-map.md) -- traceability rows for all 9 Rules
- [interface-contracts.md](../spec/supplementary_specs/interface-contracts.md) -- Value-First Onboarding Contracts section
- [entity-model.md](../spec/supplementary_specs/entity-model.md) -- Value-First Onboarding Entities section
- [value-first-onboarding-journey.md](../proposals/value-first-onboarding-journey.md) -- accepted proposal (design origin)

`spec-lint` summary: 0 error(s), 0 warning(s), 24 info across 24 spec file(s).

## Prior Findings

| ID                                    | Prior Status | New Status | Verification                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------- | ------------ | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SPEC-0023](../findings/SPEC-0023.md) | open         | resolved   | The First-task sandbox table in [interface-contracts.md](../spec/supplementary_specs/interface-contracts.md#first-task-sandbox) now contains eight rows, none of which carry OpenCode session-start constraints. The OpenCode CLI Integration section in the same file retains the Orientation row that owns the plugin-injected orientation, the `instructions` field prohibition, and root `AGENTS.md` preservation. |

## Deterministic Findings

| Code     | Count | Detail                                                                  | Disposition |
| -------- | ----- | ----------------------------------------------------------------------- | ----------- |
| TODO001  | 1     | 5 unresolved items in [todos.md](../spec/todos.md)                      | Dismissed   |
| TRACE003 | 22    | Business rules defined but never cross-referenced                       | Dismissed   |
| TRACE004 | 1     | `EPIC_BUILDING_BLOCK` used in a relationship without an attribute block | Dismissed   |

All 24 items are info-level. TODO001 covers pre-existing items unrelated to this feature. TRACE003 covers business rules from other features. TRACE004 is a pre-existing entity-model gap outside this feature's scope.

## Semantic Findings

| Finding                                                                                                                                                                                                                                                                                            | Characteristic | Artifact                                                                                                                  | Category   | Severity |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------- | ---------- | -------- |
| The First-task sandbox "Ready-host budget" row in interface-contracts.md says "ten minutes and five decisions after installation approval." The feature file anchors the time budget to "session start" and the decision count to "installation approval." The contract conflates the two anchors. | Consistent     | [interface-contracts.md](../spec/supplementary_specs/interface-contracts.md#first-task-sandbox), feature file line 286    | Suggestion | Minor    |
| The First-session insight "Ready-host budget" row uses the same "after installation approval" phrasing. The feature file and proposal anchor the two-minute time budget to the session opening, not to installation approval.                                                                      | Consistent     | [interface-contracts.md](../spec/supplementary_specs/interface-contracts.md#first-session-insight), feature file line 204 | Suggestion | Minor    |

Both findings describe the same pattern: the interface-contracts "Ready-host budget" rows use "after installation approval" as the anchor for both time and decision budgets, while the feature file and proposal use two anchors. The feature file anchors time to session start and decisions to installation approval. The feature file is authoritative; the interface contract is a derived summary.

Neither finding reaches Major severity because the feature file is unambiguous and authoritative. A test written from the feature file would use the correct anchors. The inconsistency affects only readers who consult the interface contract in isolation.

## Traceability Summary

All nine value-first onboarding rules appear in the [scope map](../spec/scope-map.md) with status `specified` and correct source links. The [gaps report](../spec/value-first-onboarding-journey-gaps.md) confirms:

- Every actor-goal pair has a Rule.
- Every Rule has at least one Scenario.
- No ambiguous wording detected.
- Boundary coverage accounts for all proposal boundaries.
- Deferred scope is explicitly listed.

No orphan rules or untraced scenarios found.

## Verdict

The specification passes review. No Major or Critical findings. One prior finding ([SPEC-0023](../findings/SPEC-0023.md)) is verified and resolved. Two Minor suggestions note a wording inconsistency in the interface-contracts "Ready-host budget" rows. The author may address these at their discretion; they do not block architecture or planning.
