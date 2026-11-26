---
type: inspect-spec
title: Factory Handbooks specification review, pass 6
date: 2026-11-26
status: defects
reviewer: spec-review-agent
findings_filed: 3
story:
scope: Cut Factory Handbooks specification against the accepted proposal
---

# Factory Handbooks specification review, pass 6

No. A planner can identify the migration story, but the spec can pass a migration that leaves guide content behind. The developer needs a content check for that story.

## Reviewed specification

Reviewed `feature/handbooks` at `e0d58e6473784752ec069f402266f0d42e269612` against the [accepted proposal](../proposals/factory-handbooks.md) and [decision log](../spec/work/handbooks-decision-log.md). Checked the [14 Scenarios](../spec/features/factory-handbooks.feature), [story criteria](../spec/work/factory-handbooks-gaps.md#acceptance-criteria-for-the-stories), and [QA strategy](../spec/work/factory-handbooks-qa-strategy.md).

## Deterministic findings

`spec-lint` exited 0 with 0 errors, 0 warnings, and 56 informational messages across 144 spec files. The glossary heuristic flags “Page Type”, whose field is used as `type`. No informational message requires a handbook fix.

## Prior findings

- [SPEC-0170](../findings/SPEC-0170.md) is resolved. [FH-05-01](../spec/features/factory-handbooks.feature) requires every guide row to point into the user handbook. FH-05-IT-01 traces to that Scenario.
- The fix for [SPEC-0168](../findings/register/document/SPEC-0168.json) holds. [FH-02-02](../spec/features/factory-handbooks.feature) starts with both handbooks passing and expects only the root-index failure in that row.
- [SPEC-0171](../findings/register/document/SPEC-0171.json) has its coverage restored. [FH-05-IT-02](../spec/work/factory-handbooks-qa-strategy.md) requires the full live-document run. The requested link is still missing.

## Semantic findings

| Characteristic                 | Finding and fix                                                                                                           | Artifact                                                              | Category | Severity | Filed as                                                  |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | -------- | -------- | --------------------------------------------------------- |
| Completeness and verifiability | An existing destination can pass while the guide content is missing. Require a content comparison in the migration story. | [Story criteria, line 84](../spec/work/factory-handbooks-gaps.md)     | defect   | major    | [SPEC-0172](../findings/SPEC-0172.md)                     |
| Verifiability                  | The duplicate-title fixture can also trigger a stale-list failure. Regenerate its list before linting it.                 | [Feature, line 110](../spec/features/factory-handbooks.feature)       | defect   | minor    | [SPEC-0173](../findings/register/document/SPEC-0173.json) |
| Traceability                   | The full link-check row leaves the live-document definition a lookup away. Link the row to the proposal definition.       | [QA strategy, line 46](../spec/work/factory-handbooks-qa-strategy.md) | defect   | minor    | [SPEC-0174](../findings/register/document/SPEC-0174.json) |

## Structure checks

- The [validation rules](../spec/validation-rules.md#factory-handbooks-handbook-index-handbook-lint-br-140br-152) cover the detailed script, authoring, and migration behavior.
- The [interface contracts](../spec/interface-contracts.md#factory-handbooks-contracts) agree with the rules. The Scenarios reach both commands and the generator's check mode.
- The [glossary](../spec/glossary.md#factory-handbooks-vocabulary) agrees with the feature. “Section” names headings in the old files.
- The entity model, state machines, schemas, and area specs have no handbook-specific entries. No handbook term candidate is pending.

## Traceability and disposition

The [scope map](../spec/scope-map.md) contains all seven Rules, and the QA owner rows cover all 14 Scenarios. The proposed fixes fit within that Scenario count.

Return the specification to the requirements agent for SPEC-0172 before planning. Two minor findings are open.
