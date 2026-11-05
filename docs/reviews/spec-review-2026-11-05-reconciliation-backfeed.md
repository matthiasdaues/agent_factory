---
type: inspect-spec
title: Spec review of the reconciliation backfeed (CAO-19, BR-067, CAO-G32)
date: 2026-11-05
status: defects
reviewer: spec-review-agent
findings_filed: 2
story: CAO-19
scope: git diff b411dc7d 5d31b0ba -- docs/spec, at commit 5d31b0bab45003623eb495a79fe589988ad7598a, on branch plan/reconciliation-backfeed
---

# Spec review of the reconciliation backfeed

## Reviewed specification

- `docs/spec/features/core-artifact-ownership.feature`, Rule CAO-19, read against CAO-14, CAO-15, and CAO-18.
- `docs/spec/validation-rules.md`, BR-067, read against BR-061 and BR-062.
- `docs/spec/interface-contracts.md`, the report-row contract and the core list table.
- `docs/spec/work/core-artifact-ownership-gaps.md`, CAO-G32 and the Actor-Goal Matrix.
- `docs/spec/work/core-artifact-ownership-qa-strategy.md`, the CAO-19 rows.
- `docs/spec/scope-map.md`, the CAO-19 row.
- `docs/proposals/core-artifact-ownership.md`, DEC-17, DEC-28, and DEC-35.

`spec-lint`: `0 error(s), 0 warning(s), 59 info across 29 spec file(s).` The installed copy is missing in this worktree, so the review ran `packages/factory/scripts/spec-lint`.

## Deterministic findings

| Rule     | Finding                                      | Disposition                                                    |
| -------- | -------------------------------------------- | -------------------------------------------------------------- |
| TRACE003 | BR-043 to BR-055 are never referenced        | Dismissed. These rules predate the delta and are out of scope. |
| TRACE004 | `EPIC_BUILDING_BLOCK` has no attribute block | Dismissed. This entity predates the delta and is out of scope. |

No info line names BR-067 or CAO-19.

## Semantic findings

| ID        | Severity | Category | Characteristic | Location       | Finding                                                                                                                                                                               |
| --------- | -------- | -------- | -------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0037 | major    | defect   | Complete       | BR-067, CAO-19 | BR-067 dispatches the `reviewed_by:` reviewer, but four core entries name `stakeholder`, and CAO-19 does not carry the stakeholder-session rule of BR-061.                            |
| SPEC-0038 | major    | defect   | Consistent     | BR-067, CAO-19 | The DONE list waits on every reconciliation report, but the backfeed dispatches only the rows of the new report, so a row left by an earlier report keeps the playbook open for good. |

## Checks that passed

- CAO-19 carries all three readings of CAO-G32: the orchestrator drives the backfeed, only the DONE list waits, and the owner's agent definition names the skill.
- BR-067 follows BR-061 for the statuses and DEC-35 for rows outside the core list. The Scenario Outline matches the `close-wave` table of CAO-14.
- The `rejected` row becomes a `BUG` finding with `owner: developer-agent`, as in CAO-14.
- The report-row table names a dispatcher and a waiting check for both reports. The waiting check for reconciliation matches BR-067.
- The `documentation-update` playbook runs the reconciliation agent in Step 1, as CAO-G32 states.

## Traceability summary

- The scope map, the Actor-Goal Matrix, and the QA strategy each list CAO-19. No orphan was found.
- BR-067 is referenced by CAO-19 and by the interface contract. CAO-19-LN-01 to CAO-19-LN-03 cover every Scenario of the Rule.
- Gap: no Scenario or QA row covers a reviewer named `stakeholder` (SPEC-0037), or a row left by an earlier report (SPEC-0038).

## Handoff

Requirements agent: the spec review found 2 open findings, SPEC-0037 and SPEC-0038. Address them.
