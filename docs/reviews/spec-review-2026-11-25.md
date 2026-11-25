---
type: inspect-spec
title: Factory Handbooks specification review, pass 1
date: 2026-11-25
status: defects
reviewer: spec-review-agent
findings_filed: 15
story: Factory Handbooks
run: feature/handbooks
branch: feature/handbooks
branch_base: 4ebf5101f70c1540a0d53dcfb3d00cfa977d361a
branch_head: a39f9b6d5242b51fb5de51a1b789b2a646eae1f1
scope: Committed specification diff under docs/spec against the accepted Factory Handbooks proposal
---

# Factory Handbooks specification review

## Reviewed specification

I reviewed the committed changes under `docs/spec/` against the [accepted proposal](../proposals/factory-handbooks.md), the [settled run decisions](../spec/work/handbooks-decision-log.md), and the existing tests and link checker where the specification relies on them. The worktree already held a staged addition to the decision log for review filing. The semantic review uses the committed decisions through L-27.

`spec-lint: 0 error(s), 0 warning(s), 58 info across 144 spec file(s).`

The first launch hit a read-only uv cache. The retry used a temporary cache. The Markdown wrapper hit the same cache restriction, so the artifacts were formatted with the cached mdformat executable and its plugins.

## Deterministic findings

| Output                                      | Count | Disposition                                                                                                                                 |
| ------------------------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| GLOSS001, glossary use heuristic            | 32    | Dismissed as standalone findings. The only new advisory, Page Type, describes a field the specification uses as `type`.                     |
| TODO001, open todo inventories              | 2     | Dismissed for this review. Both inventories predate the feature.                                                                            |
| TRACE003, unreferenced rules                | 23    | Confirmed for BR-141 and BR-151 in [SPEC-0150](../findings/register/document/SPEC-0150.json). The other 21 advisories are outside the diff. |
| TRACE004, entity without an attribute block | 1     | Dismissed for this review. EPIC_BUILDING_BLOCK is outside the diff.                                                                         |

## Semantic findings

| Finding                                                                                                                                                                                                                                                                                             | Artifact                                                                                             | Characteristic | Category | Severity | Filed as                                                  | Owner                 |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | -------------- | -------- | -------- | --------------------------------------------------------- | --------------------- |
| The obsolete-guide search matches its own specification. Define the forbidden references as obsolete runtime or documentation consumers. Explicitly allow the migration specification to name its inputs, and align the proposal, scenario, and QA search.                                          | [docs/spec/features/factory-handbooks.feature:465](../spec/features/factory-handbooks.feature)       | Feasible       | defect   | major    | [SPEC-0140](../findings/SPEC-0140.md)                     | requirements-agent    |
| The update check permits extra installed files and omits the fresh install. Compare the complete sets of relative paths and file bytes on update, including removal of stale files. Check a fresh installation and verify that it includes the user handbook and excludes the contributor handbook. | [docs/spec/features/factory-handbooks.feature:428](../spec/features/factory-handbooks.feature)       | Complete       | defect   | major    | [SPEC-0141](../findings/SPEC-0141.md)                     | requirements-agent    |
| The lint acceptance cases omit present but invalid titles. State the error and field diagnostic for a present non-text title. Define how null and an empty title count, then add representative lint cases.                                                                                         | [docs/spec/validation-rules.md:649](../spec/validation-rules.md)                                     | Verifiable     | defect   | major    | [SPEC-0142](../findings/SPEC-0142.md)                     | domain-modeling-agent |
| The index command leaves invalid frontmatter behavior open. Define what both index modes do with malformed or invalid page metadata and how lint reports the underlying format error while continuing across both handbooks.                                                                        | [docs/spec/interface-contracts.md:1826](../spec/interface-contracts.md)                              | Unambiguous    | defect   | major    | [SPEC-0143](../findings/SPEC-0143.md)                     | domain-modeling-agent |
| The chapter sort has no rule for equal order and title. Keep the decided order and title keys. Specify a stable final key, such as the chapter path, and test two chapters with identical order and title.                                                                                          | [docs/spec/validation-rules.md:657](../spec/validation-rules.md)                                     | Unambiguous    | defect   | major    | [SPEC-0144](../findings/SPEC-0144.md)                     | domain-modeling-agent |
| The migration repurposes the spec-writer path guard. Keep the full spec-writer scan and replace only its retired guide target with the relevant handbook path. Keep the original content assertions in the other two tests.                                                                         | [docs/spec/features/factory-handbooks.feature:564](../spec/features/factory-handbooks.feature)       | Consistent     | defect   | major    | [SPEC-0145](../findings/SPEC-0145.md)                     | requirements-agent    |
| The migration-map check covers only one of the three source files. Give one check ownership of the committed map against all three source files at the acceptance commit. Check each required source section and its destination, including the contributor directory-tree reference.               | [docs/spec/work/factory-handbooks-qa-strategy.md:108](../spec/work/factory-handbooks-qa-strategy.md) | Verifiable     | defect   | major    | [SPEC-0146](../findings/SPEC-0146.md)                     | test-strategy-agent   |
| The reference-style rewrite test relies on a link absent from the repository. Pass a reference-style link and definition to the rewrite in a controlled fixture. Assert the new destination and unchanged reference label, and retain the repository check for migration results.                   | [docs/spec/work/factory-handbooks-qa-strategy.md:187](../spec/work/factory-handbooks-qa-strategy.md) | Verifiable     | defect   | major    | [SPEC-0147](../findings/SPEC-0147.md)                     | test-strategy-agent   |
| The order test can pass when the generator ignores zero and negative values. Add a sort case where using zero or a negative value changes the expected relative position, and keep the format acceptance check.                                                                                     | [docs/spec/work/factory-handbooks-qa-strategy.md:96](../spec/work/factory-handbooks-qa-strategy.md)  | Verifiable     | defect   | major    | [SPEC-0148](../findings/SPEC-0148.md)                     | test-strategy-agent   |
| Rule-summary checks can pass when pages introduce binding rules. Give the handbook content review an explicit check for binding rules in ordinary prose in both handbooks. Keep the automated check for callout structure and source links.                                                         | [docs/spec/work/factory-handbooks-qa-strategy.md:102](../spec/work/factory-handbooks-qa-strategy.md) | Complete       | defect   | major    | [SPEC-0149](../findings/SPEC-0149.md)                     | test-strategy-agent   |
| The glossary gives the migration map a different home. Describe the standalone file in the glossary and link to the rule that defines its path.                                                                                                                                                     | [docs/spec/glossary.md:221](../spec/glossary.md)                                                     | Terminology    | defect   | minor    | [SPEC-0151](../findings/register/document/SPEC-0151.json) | domain-modeling-agent |
| The stub definition omits the chapter-index exception. Limit the exclusion to chapter page lists and link to the top-level chapter-index rule.                                                                                                                                                      | [docs/spec/glossary.md:216](../spec/glossary.md)                                                     | Terminology    | defect   | minor    | [SPEC-0152](../findings/register/document/SPEC-0152.json) | domain-modeling-agent |
| The gaps report routes readers to an empty candidate table. Point to the confirmed glossary entries and update the count of recorded answers.                                                                                                                                                       | [docs/spec/work/factory-handbooks-gaps.md:10](../spec/work/factory-handbooks-gaps.md)                | Traceability   | defect   | minor    | [SPEC-0153](../findings/register/document/SPEC-0153.json) | requirements-agent    |
| The QA layer summary points to the superseded hook check. Update the layer summary to describe the two hook settings in the owner row.                                                                                                                                                              | [docs/spec/work/factory-handbooks-qa-strategy.md:41](../spec/work/factory-handbooks-qa-strategy.md)  | Traceability   | defect   | minor    | [SPEC-0154](../findings/register/document/SPEC-0154.json) | test-strategy-agent   |

## Structure checks

- [Entity model](../spec/entity-model.md). The change introduces documentation files and CLI checks. It adds no persistent entity, as L-17 records.
- [State machines](../spec/state-machines.md). The change adds no transition contract for a modeled entity.
- [Validation rules](../spec/validation-rules.md#factory-handbooks-handbook-index-handbook-lint-br-140br-152). Findings [SPEC-0142](../findings/SPEC-0142.md), [SPEC-0144](../findings/SPEC-0144.md), and [SPEC-0150](../findings/register/document/SPEC-0150.json) cover value validation, ordering, and rule links.
- [Interface contracts](../spec/interface-contracts.md#factory-handbooks-contracts). Scenarios reach both scripts and both generator modes. [SPEC-0143](../findings/SPEC-0143.md) covers invalid input.
- [Schemas](../spec/schemas). The two CLI contracts add no serialized DTO schema.
- [Area specifications](../spec/areas). The existing mechanized-dispatch area gains no handbook rule. L-07 settles the area-spec scope.
- [Glossary](../spec/glossary.md#factory-handbooks-vocabulary). Findings [SPEC-0151](../findings/register/document/SPEC-0151.json) and [SPEC-0152](../findings/register/document/SPEC-0152.json) cover the map and stub definitions.
- [Term candidates](../spec/work/term-candidates.md). The table has no proposed rows. [SPEC-0153](../findings/register/document/SPEC-0153.json) covers the stale reference to the table.

## Traceability summary

The [scope map](../spec/scope-map.md) traces the 14 handbook Rules to their feature file. BR-141 and BR-151 have scenario coverage with missing explicit links. The gaps report assigns the lector pass to the release process. The QA strategy assigns the full suite to the merge gate and the tutorial walkthrough to its author. The review records a coverage gap for the complete migration map in [SPEC-0146](../findings/SPEC-0146.md).

## Disposition

The review found ten major defects and five minor defects. The major defects return the specification to its authors before planning. The run lead will claim the IDs and file the artifacts.
