---
type: inspect-spec
title: Factory Handbooks specification review, pass 5
date: 2026-11-25
status: block
reviewer: spec-review-agent
findings_filed: 2
story:
run: feature/handbooks
branch: feature/handbooks
branch_head: 746ef16f45659d9ef974421732336e39db571909
scope: Factory Handbooks specification after the cut to 14 scenarios
---

# Factory Handbooks specification review, pass 5

**Can a planner cut stories and a developer write tests from the specification without asking the author?** No. The migration-map test can pass a destination that installed users cannot read. The accepted proposal supplies the missing requirement.

## Reviewed specification

I checked the committed [proposal](../proposals/factory-handbooks.md) and [decision log through L-38](../spec/work/handbooks-decision-log.md) at the review SHA. The cut has seven rules and 14 scenarios, with one-time checks in the [story acceptance criteria](../spec/work/factory-handbooks-gaps.md#acceptance-criteria-for-the-stories).

## Deterministic findings

`spec-lint: 0 error(s), 0 warning(s), 56 info across 144 spec file(s).`

| Lint output                 | Verdict                   | Reason                                                                                                                                              |
| --------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| GLOSS001                    | Dismissed for this review | The handbook term flagged by the heuristic, Page Type, defines the `type` field used in the specification. The other flags concern unrelated terms. |
| TODO001, TRACE003, TRACE004 | Dismissed for this review | The notices concern existing todo counts, unrelated business rules, and an unrelated entity.                                                        |

## Semantic findings

| ID                                                        | Severity | Characteristic | Location                                                              | Finding                                                                                     | Owner               |
| --------------------------------------------------------- | -------- | -------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------- |
| [SPEC-0170](../findings/SPEC-0170.md)                     | Major    | Verifiable     | [Feature, line 164](../spec/features/factory-handbooks.feature)       | The migration-map test can pass when a guide section points to a contributor handbook page. | Requirements agent  |
| [SPEC-0171](../findings/register/document/SPEC-0171.json) | Minor    | Complete       | [QA strategy, line 46](../spec/work/factory-handbooks-qa-strategy.md) | The test owner row leaves out the run of `link-check` over every live document.             | Test-strategy agent |

## Prior minors

| Finding                                                   | Verdict | Evidence                                                                                                                                                            |
| --------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SPEC-0158](../findings/register/document/SPEC-0158.json) | moot    | Acceptance criterion 6 distinguishes the spec-writer scan from the two content checks.                                                                              |
| [SPEC-0161](../findings/register/document/SPEC-0161.json) | moot    | The retention summary is gone. Acceptance criterion 6 names the scan and replacement input.                                                                         |
| [SPEC-0165](../findings/register/document/SPEC-0165.json) | moot    | The owner row and retention policy are gone. Acceptance criterion 6 names all three retained tests and their inputs.                                                |
| [SPEC-0166](../findings/register/document/SPEC-0166.json) | moot    | The completion trace names FH-02-02 and FH-02-03. They cover the missing root index and mixed failures.                                                             |
| [SPEC-0167](../findings/register/document/SPEC-0167.json) | moot    | The QA strategy links to the decision log without an obsolete upper bound.                                                                                          |
| [SPEC-0168](../findings/register/document/SPEC-0168.json) | applies | The missing-root row of FH-02-02 still leaves the state of the other indexes implicit. BR-141 and the expected diagnostic let the test author isolate the deletion. |
| [SPEC-0169](../findings/register/document/SPEC-0169.json) | moot    | The introduction no longer calls the top-level index a chapter page.                                                                                                |

## Structure checks

- The [validation rules](../spec/validation-rules.md#factory-handbooks-handbook-index-handbook-lint-br-140br-152) give the test author metadata, marker, sort, and diagnostic cases.
- The [interface contracts](../spec/interface-contracts.md#factory-handbooks-contracts) describe both commands and their exit, write, and reporting behavior. FH-01 and FH-02 reach both commands.
- The [glossary](../spec/glossary.md) distinguishes the two audiences, chapter pages, and top-level page lists. The [term candidates](../spec/work/term-candidates.md) have no proposed rows.
- L-17 excludes handbook entities, state machines, and schemas. No handbook-specific area specification applies.

## Traceability and disposition

The [scope map](../spec/scope-map.md) traces all seven rules to the feature. The [gaps report](../spec/work/factory-handbooks-gaps.md#completion-criteria-trace) traces the proposal's checks. The migration-map trace gives a weaker check than the proposal requires.

Return the specification to the requirements agent for SPEC-0170 before planning. Keep the 14 scenarios. The QA strategy edit is nonblocking.
