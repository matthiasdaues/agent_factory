---
type: inspect-spec
title: Factory Handbooks specification review, pass 7
date: 2026-11-26
status: pass
reviewer: spec-review-agent
findings_filed: 2
story: factory-handbooks
scope: Factory Handbooks specification against the accepted proposal and settled decisions
---

# Factory Handbooks specification review, pass 7

Yes. A planner can cut stories and a developer can write tests without asking the author. The 14 Scenarios cover the actor goals. The validation rules define the script behavior, and the story criteria cover the one-time migration. Planning can proceed under L-40.

## Reviewed specification

Reviewed `feature/handbooks` at `469beb9875c23d0cc314f4f005427c100de2eb2c` against the [accepted proposal](../proposals/factory-handbooks.md#scope) and the [decision log](../spec/work/handbooks-decision-log.md). Reviewed the [feature](../spec/features/factory-handbooks.feature), [gaps report](../spec/work/factory-handbooks-gaps.md#acceptance-criteria-for-the-stories), and [QA strategy](../spec/work/factory-handbooks-qa-strategy.md#contract-owners).

## Deterministic findings

`spec-lint: 0 error(s), 0 warning(s), 56 info across 144 spec file(s).`

The default cache was read-only. The successful run used a cache under `/tmp`. The informational notices identify no handbook defect.

## Prior findings

- [SPEC-0172](../findings/SPEC-0172.md) is resolved. [Criterion 12](../spec/work/factory-handbooks-gaps.md#acceptance-criteria-for-the-stories) and the [migration review](../spec/work/factory-handbooks-qa-strategy.md#review-checks) require a section-by-section comparison at the baseline. The reviewer checks the mapped pages for the guide's facts, commands, and paths.
- [SPEC-0173](../findings/register/document/SPEC-0173.json) remains resolved. The duplicate-title example specifies a current page list, which isolates the duplicate-title failure.
- [SPEC-0174](../findings/register/document/SPEC-0174.json) remains resolved. FH-05-IT-02 links to the proposal's definition of a live document.

## Semantic findings

| Finding                                                                                                                                                                | Artifact                                                                              | Characteristic | Category | Severity | Filed as                                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------------- | -------- | -------- | --------------------------------------------------------- |
| FH-04-IT-01 omits the absence of the installed guide and contributor handbook files. Add both assertions to the owner row.                                             | [QA strategy, line 44](../spec/work/factory-handbooks-qa-strategy.md#contract-owners) | Completeness   | Defect   | Minor    | [SPEC-0175](../findings/register/document/SPEC-0175.json) |
| FH-05-IT-01 omits the checks for the required destination handbooks. Add the user handbook destinations and the contributor directory-tree reference to the owner row. | [QA strategy, line 45](../spec/work/factory-handbooks-qa-strategy.md#contract-owners) | Completeness   | Defect   | Minor    | [SPEC-0176](../findings/register/document/SPEC-0176.json) |

Both owner rows summarize Scenarios that state the missing assertions. Each answers no to `fails_purpose` and yes to `raises_cost`. The fixes fit in the existing rows.

## Structure checks

- The [validation rules](../spec/validation-rules.md#factory-handbooks-handbook-index-handbook-lint-br-140br-152) define index generation, lint failures, hook behavior, rule summaries, and link migration. They give test authors the valid and invalid cases behind the Scenarios.
- The [interface contracts](../spec/interface-contracts.md#factory-handbooks-contracts) give both scripts' inputs, writes, reports, and exit behavior. The Scenarios reach both scripts and the index check mode.
- The [glossary](../spec/glossary.md#factory-handbooks-vocabulary) agrees with the feature's audience, page, navigation, and migration terms. The term-candidate file contains no proposed handbook term.
- The feature adds no persistent entity, state machine, schema, or area spec under L-07 and L-17.

## Traceability and disposition

The seven handbook rows in the [scope map](../spec/scope-map.md) trace to the seven feature Rules. Each of the 14 Scenarios has a QA owner. The BR rules and the acceptance criteria cover the script details and the repository changes that the cut moved out of Scenarios.

Two minor findings remain open. Planning can proceed. The run lead claims the permanent finding IDs.
