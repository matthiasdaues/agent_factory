---
type: inspect-spec
title: Factory Handbooks specification review, pass 4
date: 2026-11-25
status: pass
reviewer: spec-review-agent
findings_filed: 5
story: Factory Handbooks
run: feature/handbooks
branch: feature/handbooks
branch_base: 4ebf5101f70c1540a0d53dcfb3d00cfa977d361a
branch_head: 1e83f92d16ef69b54d01a7ef917ef705818ba202
scope: Committed changes under docs/spec against the accepted Factory Handbooks proposal
---

# Factory Handbooks specification review, pass 4

## Reviewed specification

The review covered the full specification diff against the [accepted proposal](../proposals/factory-handbooks.md#completion-criteria) and the [settled decisions](../spec/work/handbooks-decision-log.md). It checked consistency, ambiguity, verifiability, completeness, feasibility, necessity, and terminology across the feature scenarios, validation and interface contracts, glossary, gaps report, and QA strategy. The scope map was read for traceability.

`spec-lint: 0 error(s), 0 warning(s), 56 info across 144 spec file(s).`

## Deterministic findings

| Code     | Count | Disposition                                                                                                                                |
| -------- | ----: | ------------------------------------------------------------------------------------------------------------------------------------------ |
| GLOSS001 |    32 | Dismissed as actionable findings. The unused-term heuristic includes Page Type, whose field and allowed values the feature and BR-140 use. |
| TODO001  |     2 | Dismissed for this review. The advisories count 42 and 5 existing open entries respectively.                                               |
| TRACE003 |    21 | Dismissed for this review. None of the advised rules is BR-140 through BR-152.                                                             |
| TRACE004 |     1 | Dismissed for this review. The existing EPIC_BUILDING_BLOCK relationship is outside the diff.                                              |

## Prior findings

| Finding                                                   | Verdict  | Evidence                                                                                                                                                                                                                |
| --------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SPEC-0157](../findings/register/document/SPEC-0157.json) | Verified | FH-07-IT-02 asserts equality of relative path sets and file contents and uses the current scenario title.                                                                                                               |
| [SPEC-0158](../findings/register/document/SPEC-0158.json) | Partial  | The owner row names the full spec-writer scan and the retention policy names the replacement target. Both still say all three tests read handbook pages. See [SPEC-0165](../findings/register/document/SPEC-0165.json). |
| [SPEC-0159](../findings/SPEC-0159.md)                     | Resolved | BR-141 requires each root index and a diagnostic naming the root. FH-04-17 and FH-04-IT-11 cover the deletion. Fixture isolation is a separate minor.                                                                   |
| [SPEC-0160](../findings/register/document/SPEC-0160.json) | Verified | FH-07-IT-02 quotes the current title ending in “file for file”.                                                                                                                                                         |
| [SPEC-0161](../findings/register/document/SPEC-0161.json) | Partial  | The retention policy describes the scan and replacement entry, then repeats the old description in its last sentence. See [SPEC-0165](../findings/register/document/SPEC-0165.json).                                    |
| [SPEC-0162](../findings/register/document/SPEC-0162.json) | Verified | BR-146 names each list's input pages and excludes a comparison when the target index has a broken marker pair.                                                                                                          |
| [SPEC-0163](../findings/register/document/SPEC-0163.json) | Verified | The integration inventory includes FH-04-IT-10 and the decision inventory reaches L-33, as requested in pass 3. L-34 was added in the fixing commit.                                                                    |
| [SPEC-0164](../findings/register/document/SPEC-0164.json) | Verified | FH-10-IT-01 limits record checks to rewritten destinations, and FH-10-IT-02 owns whole-file checks for live documents.                                                                                                  |

## Semantic findings

| ID                                                        | Artifact                                                                                             | Characteristic | Category | Severity | Finding and fix                                                                                                                                                                                                                                                                                                                                                 | Owner               |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | -------------- | -------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| [SPEC-0165](../findings/register/document/SPEC-0165.json) | [docs/spec/work/factory-handbooks-qa-strategy.md:134](../spec/work/factory-handbooks-qa-strategy.md) | Consistent     | defect   | minor    | The FH-11 owner row and retention policy omit the distinction between the spec-writer path scan and the two migrated content assertions when they summarize FH-11-LN-01. State that the layout test changes only the retired guide entry in its input list, and have the owner row and the last sentence at line 241 describe the two content tests separately. | test-strategy-agent |
| [SPEC-0166](../findings/register/document/SPEC-0166.json) | [docs/spec/work/factory-handbooks-gaps.md:33](../spec/work/factory-handbooks-gaps.md)                | Traceability   | defect   | minor    | The lint completion trace stops at FH-04-15. Include FH-04-16 for stale-list reporting alongside invalid metadata and FH-04-17 for a missing root index.                                                                                                                                                                                                        | requirements-agent  |
| [SPEC-0167](../findings/register/document/SPEC-0167.json) | [docs/spec/work/factory-handbooks-qa-strategy.md:8](../spec/work/factory-handbooks-qa-strategy.md)   | Traceability   | defect   | minor    | The decision inventory ends at L-33 even though FH-04-IT-11 implements the root-index decision recorded in L-34. Extend the range through L-34.                                                                                                                                                                                                                 | test-strategy-agent |
| [SPEC-0168](../findings/register/document/SPEC-0168.json) | [docs/spec/features/factory-handbooks.feature:419](../spec/features/factory-handbooks.feature)       | Verifiable     | defect   | minor    | The missing-root-index scenario leaves the state of the other indexes implicit. Start with both handbooks valid and current, then remove only the root index so another failure cannot satisfy the test.                                                                                                                                                        | requirements-agent  |
| [SPEC-0169](../findings/register/document/SPEC-0169.json) | [docs/spec/features/factory-handbooks.feature:19](../spec/features/factory-handbooks.feature)        | Terminology    | defect   | minor    | The feature introduction calls every index.md a chapter page, including a handbook root index. Use “chapter page” for the chapter index and “top-level index” for the root.                                                                                                                                                                                     | requirements-agent  |

## Structure checks

- [Entity model](../spec/entity-model.md). The handbook commands operate on Markdown files and introduce no persistent entity.
- [State machines](../spec/state-machines.md). Changing a stub to implemented takes effect through the file's metadata on the next generator run. The feature adds no modeled lifecycle.
- [Validation rules](../spec/validation-rules.md#factory-handbooks-handbook-index-handbook-lint-br-140br-152). BR-140 through BR-152 cover format, generators, the hook, and migration. The root-index rule has an acceptance case and a test owner. See [SPEC-0168](../findings/register/document/SPEC-0168.json) for fixture isolation.
- [Interface contracts](../spec/interface-contracts.md#factory-handbooks-contracts). FH-01, FH-03, and FH-04 reach generation, check mode, and lint respectively. The commands connect to the validation rules for reads, writes, diagnostics, and exit conditions.
- [Schemas](../spec/schemas). The commands add no serialized DTO contract.
- [Area specifications](../spec/areas). The existing dispatch area gains no handbook behavior. The handbook work stays in the global feature and the changes to existing features preserve their actor goals.
- [Glossary](../spec/glossary.md#factory-handbooks-vocabulary). The contributor rename and the definitions for stubs, page lists, and the migration map agree with the rules. See [SPEC-0169](../findings/register/document/SPEC-0169.json) for the use of “chapter page” in the feature introduction.
- [Term candidates](../spec/work/term-candidates.md). The table has no proposed rows.

## Traceability summary

The [scope map](../spec/scope-map.md) traces all 14 handbook Rules. The feature contains 85 scenarios counting each outline once. The QA strategy assigns the full suite to the merge gate and the fresh-clone tutorial run to its author. The gaps report assigns the lector pass to the release process. The new lint cases have integration owners; the completion summary omits their traces. [QA strategy](../spec/work/factory-handbooks-qa-strategy.md#scenarios-without-a-test-of-their-own) · [Gaps report](../spec/work/factory-handbooks-gaps.md#completion-criteria-trace)

## Disposition

Pass to planning. The pass 3 blocker is resolved. The five open minors are non-blocking. The run lead claims the permanent IDs.
