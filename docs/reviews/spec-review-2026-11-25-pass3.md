---
type: inspect-spec
title: Factory Handbooks specification review, pass 3
date: 2026-11-25
status: defects
reviewer: spec-review-agent
findings_filed: 6
story: Factory Handbooks
run: feature/handbooks
branch: feature/handbooks
branch_base: 4ebf5101f70c1540a0d53dcfb3d00cfa977d361a
branch_head: 8ad7ceeeb3d57d358f94d74ad90606ae236eb849
scope: Committed changes under docs/spec against the accepted Factory Handbooks proposal
---

# Factory Handbooks specification review, pass 3

## Reviewed specification

The review covered the entire specification diff, including the actor and path changes in existing features. The review used the [`docs/proposals/factory-handbooks.md`](../proposals/factory-handbooks.md) and the [`docs/spec/work/handbooks-decision-log.md`](../spec/work/handbooks-decision-log.md).

The fresh inspection covered consistency, ambiguity, verifiability, completeness, feasibility, necessity, and terminology.

`spec-lint: 0 error(s), 0 warning(s), 56 info across 144 spec file(s).`

## Deterministic findings

| Code     | Count | Disposition                                                                                                                     |
| -------- | ----- | ------------------------------------------------------------------------------------------------------------------------------- |
| GLOSS001 | 32    | Dismissed. The handbook term Page Type names the field used as `type`. The other advisories lie outside the changed vocabulary. |
| TODO001  | 2     | Dismissed. Both todo inventories lie outside the diff.                                                                          |
| TRACE003 | 21    | Dismissed. These rules lie outside the diff.                                                                                    |
| TRACE004 | 1     | Dismissed. The entity EPIC_BUILDING_BLOCK lies outside the diff.                                                                |

## Prior findings

| Finding                                                                                          | Verdict  | Verification                                                                                                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`docs/findings/SPEC-0155.md`](../findings/SPEC-0155.md)                                         | Resolved | BR-146 requires comparisons of independent valid lists, and FH-04-16 checks the two diagnostics in one run. [`docs/spec/validation-rules.md:658`](../spec/validation-rules.md) [`docs/spec/features/factory-handbooks.feature:407`](../spec/features/factory-handbooks.feature) |
| [`docs/findings/SPEC-0156.md`](../findings/SPEC-0156.md)                                         | Resolved | Both tests resolve installed links against a temporary installation from the reviewed tree. [`docs/spec/work/factory-handbooks-qa-strategy.md:221`](../spec/work/factory-handbooks-qa-strategy.md)                                                                              |
| [`docs/findings/register/document/SPEC-0157.json`](../findings/register/document/SPEC-0157.json) | Partial  | The row checks path sets and bytes. The previous scenario title remains, as recorded in [SPEC-0160](../findings/register/document/SPEC-0160.json).                                                                                                                              |
| [`docs/findings/register/document/SPEC-0158.json`](../findings/register/document/SPEC-0158.json) | Partial  | The row names the full scan. The retention summary still describes the three tests as reading handbook pages, as recorded in [SPEC-0161](../findings/register/document/SPEC-0161.json).                                                                                         |

## Semantic findings

| Finding                                                   | Artifact                                                                                               | Characteristic | Category | Severity | Finding and fix                                                                                                                                                                                                                         | Owner                 |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | -------------- | -------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| [SPEC-0159](../findings/SPEC-0159.md)                     | [`docs/spec/validation-rules.md:650`](../spec/validation-rules.md)                                     | Complete       | defect   | major    | Lint can pass after deletion of a required top-level index. Require both top-level indexes in the lint rule, and check a deletion with all chapter lists current.                                                                       | domain-modeling-agent |
| [SPEC-0160](../findings/register/document/SPEC-0160.json) | [`docs/spec/work/factory-handbooks-qa-strategy.md:111`](../spec/work/factory-handbooks-qa-strategy.md) | Traceability   | defect   | minor    | FH-07-IT-02 still quotes the old FH-07-02 title after adding path-set equality. Use the current title ending in "file for file".                                                                                                        | test-strategy-agent   |
| [SPEC-0161](../findings/register/document/SPEC-0161.json) | [`docs/spec/work/factory-handbooks-qa-strategy.md:240`](../spec/work/factory-handbooks-qa-strategy.md) | Consistent     | defect   | minor    | The retention policy still omits the spec-writer scan and its replacement target. Name the unchanged scan and replacement input separately from the two tests that read handbook pages, in both the owner row and the retention policy. | test-strategy-agent   |
| [SPEC-0162](../findings/register/document/SPEC-0162.json) | [`docs/spec/validation-rules.md:658`](../spec/validation-rules.md)                                     | Unambiguous    | defect   | minor    | BR-146 leaves the inputs of an independently comparable list implicit. Define the input pages for each list and state that a broken marker pair prevents comparing that list.                                                           | domain-modeling-agent |
| [SPEC-0163](../findings/register/document/SPEC-0163.json) | [`docs/spec/work/factory-handbooks-qa-strategy.md:42`](../spec/work/factory-handbooks-qa-strategy.md)  | Traceability   | defect   | minor    | The integration inventory omits FH-04-IT-10, and the decision inventory at line 8 stops at L-15. Include FH-04-IT-10 and extend the decision range through L-33.                                                                        | test-strategy-agent   |
| [SPEC-0164](../findings/register/document/SPEC-0164.json) | [`docs/spec/work/factory-handbooks-qa-strategy.md:131`](../spec/work/factory-handbooks-qa-strategy.md) | Verifiable     | defect   | minor    | The FH-10-IT-01 owner row describes passing whole files, which can count unrelated links in a record. State that the record check validates rewritten destinations and reserve whole-file checks for live documents under FH-10-IT-02.  | test-strategy-agent   |

## Structure checks

- The handbooks add no persistent entity. [`docs/spec/entity-model.md`](../spec/entity-model.md)
- The handbooks add no modeled entity transition. [`docs/spec/state-machines.md`](../spec/state-machines.md)
- The validation rules leave a lint failure condition and the inputs of an independent comparison unclear. [SPEC-0159](../findings/SPEC-0159.md) and [SPEC-0162](../findings/register/document/SPEC-0162.json).
- Scenarios reach both commands and both generator modes. The command contract points to BR-146 for comparison behavior. [`docs/spec/interface-contracts.md:1814`](../spec/interface-contracts.md)
- The Markdown commands add no serialized DTO schema. [`docs/spec/schemas`](../spec/schemas)
- The existing area specification gains no handbook behavior. [`docs/spec/areas/mechanized-dispatch.md`](../spec/areas/mechanized-dispatch.md)
- The glossary terms for the two handbooks, stubs, and the migration map agree with the feature and validation rules. The actor renames use Contributor. [`docs/spec/glossary.md:209`](../spec/glossary.md)
- The term-candidate table has no proposed rows. [`docs/spec/work/term-candidates.md`](../spec/work/term-candidates.md)

## Traceability summary

The scope map traces all 14 handbook Rules. The feature has 84 scenarios, counting each outline once. [`docs/spec/scope-map.md:250`](../spec/scope-map.md) [`docs/spec/features/factory-handbooks.feature`](../spec/features/factory-handbooks.feature)

The QA strategy owns script and migration checks, the merge gate owns the full-suite run, and the contributor walks through the tutorial. The gaps report assigns the lector pass to the release process. [`docs/spec/work/factory-handbooks-qa-strategy.md:151`](../spec/work/factory-handbooks-qa-strategy.md) [`docs/spec/work/factory-handbooks-gaps.md:58`](../spec/work/factory-handbooks-gaps.md)

## Disposition

Resolve [SPEC-0159](../findings/SPEC-0159.md) before planning. The run lead claims the IDs and files the six artifacts.
