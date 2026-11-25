---
type: inspect-spec
title: Factory Handbooks specification review, pass 2
date: 2026-11-25
status: defects
reviewer: spec-review-agent
findings_filed: 4
story: Factory Handbooks
run: feature/handbooks
branch: feature/handbooks
branch_base: 4ebf5101f70c1540a0d53dcfb3d00cfa977d361a
branch_head: 67863a45b3e3bb9ca043e4253ed9f8d555189829
scope: Committed changes under docs/spec against the accepted Factory Handbooks proposal
---

# Factory Handbooks specification review

## Reviewed specification

The review covered the committed changes under `docs/spec/`. It used the [accepted proposal](../proposals/factory-handbooks.md) and [settled decisions](../spec/work/handbooks-decision-log.md).

`spec-lint: 0 error(s), 0 warning(s), 56 info across 144 spec file(s).`

## Deterministic findings

| Output   | Count | Disposition                                                                                                      |
| -------- | ----- | ---------------------------------------------------------------------------------------------------------------- |
| GLOSS001 | 32    | Dismissed. The handbook term Page Type names the field used as `type`. The other advisories predate this change. |
| TODO001  | 2     | Dismissed. Both todo inventories predate this change.                                                            |
| TRACE003 | 21    | Dismissed. The remaining rules sit outside the diff.                                                             |
| TRACE004 | 1     | Dismissed. EPIC_BUILDING_BLOCK sits outside the diff.                                                            |

## Prior findings

| Finding                                                   | Verdict  | Verification                                                                                                                                                                                              |
| --------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SPEC-0140](../findings/SPEC-0140.md)                     | Resolved | The search excludes the migration specification under L-30. [`docs/spec/features/factory-handbooks.feature:526`](../spec/features/factory-handbooks.feature)                                              |
| [SPEC-0141](../findings/SPEC-0141.md)                     | Resolved | The update compares path sets and bytes, removes stale pages, and has a fresh-install case. [`docs/spec/features/factory-handbooks.feature:473`](../spec/features/factory-handbooks.feature)              |
| [SPEC-0142](../findings/SPEC-0142.md)                     | Resolved | BR-140 and the invalid-field outline reject numeric, empty, and null titles. [`docs/spec/validation-rules.md:649`](../spec/validation-rules.md)                                                           |
| [SPEC-0143](../findings/SPEC-0143.md)                     | Resolved | Both generator modes refuse invalid metadata without writing, and lint continues its independent checks. [`docs/spec/interface-contracts.md:1826`](../spec/interface-contracts.md)                        |
| [SPEC-0144](../findings/SPEC-0144.md)                     | Resolved | The chapter path breaks ties after order and title. FH-02-05 exercises the tie. [`docs/spec/validation-rules.md:657`](../spec/validation-rules.md)                                                        |
| [SPEC-0145](../findings/SPEC-0145.md)                     | Resolved | FH-11-01 now explicitly retains the full spec-writer scan. The remaining QA wording has its own finding. [`docs/spec/features/factory-handbooks.feature:626`](../spec/features/factory-handbooks.feature) |
| [SPEC-0146](../findings/SPEC-0146.md)                     | Resolved | FH-08-IT-01 checks section headings and destinations for all three sources. [`docs/spec/work/factory-handbooks-qa-strategy.md:148`](../spec/work/factory-handbooks-qa-strategy.md)                        |
| [SPEC-0147](../findings/SPEC-0147.md)                     | Resolved | FH-10-CT-07 rewrites a reference-style fixture and checks that its label stays. [`docs/spec/work/factory-handbooks-qa-strategy.md:129`](../spec/work/factory-handbooks-qa-strategy.md)                    |
| [SPEC-0148](../findings/SPEC-0148.md)                     | Resolved | FH-01-CT-11 asserts the relative order of -5, 0, and 1. [`docs/spec/work/factory-handbooks-qa-strategy.md:69`](../spec/work/factory-handbooks-qa-strategy.md)                                             |
| [SPEC-0149](../findings/SPEC-0149.md)                     | Resolved | The lector and story reviewers check ordinary prose for binding rules in both handbooks. [`docs/spec/work/factory-handbooks-qa-strategy.md:161`](../spec/work/factory-handbooks-qa-strategy.md)           |
| [SPEC-0150](../findings/register/document/SPEC-0150.json) | Resolved | BR-141 and BR-151 now cite scenarios. Neither appears in TRACE003. [`docs/spec/validation-rules.md:650`](../spec/validation-rules.md)                                                                     |
| [SPEC-0151](../findings/register/document/SPEC-0151.json) | Resolved | Migration Map names the standalone file and cites BR-151. [`docs/spec/glossary.md:221`](../spec/glossary.md)                                                                                              |
| [SPEC-0152](../findings/register/document/SPEC-0152.json) | Resolved | Stub distinguishes chapter page lists from the top-level chapter list. [`docs/spec/glossary.md:216`](../spec/glossary.md)                                                                                 |
| [SPEC-0153](../findings/register/document/SPEC-0153.json) | Resolved | The report counts seven answers and points to confirmed glossary terms. [`docs/spec/work/factory-handbooks-gaps.md:6`](../spec/work/factory-handbooks-gaps.md)                                            |
| [SPEC-0154](../findings/register/document/SPEC-0154.json) | Resolved | The contract-layer summary names always_run and pass_filenames. [`docs/spec/work/factory-handbooks-qa-strategy.md:41`](../spec/work/factory-handbooks-qa-strategy.md)                                     |

## Semantic findings

| Finding                                                   | Artifact                                                                                               | Characteristic | Category | Severity | Finding and fix                                                                                                                                                                                       | Owner                 |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | -------------- | -------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| [SPEC-0155](../findings/SPEC-0155.md)                     | [`docs/spec/validation-rules.md:662`](../spec/validation-rules.md)                                     | Consistency    | defect   | major    | Stale-list diagnostics can disappear after an unrelated refusal. Define which lists can still be checked after a refusal. Check a stale list in one handbook alongside a malformed page in the other. | domain-modeling-agent |
| [SPEC-0156](../findings/SPEC-0156.md)                     | [`docs/spec/work/factory-handbooks-qa-strategy.md:220`](../spec/work/factory-handbooks-qa-strategy.md) | Feasibility    | defect   | major    | Link checks depend on a handbook absent from the main checkout. Give both link checks an installed fixture populated from the reviewed tree. Resolve installed links against that fixture.            | test-strategy-agent   |
| [SPEC-0157](../findings/register/document/SPEC-0157.json) | [`docs/spec/work/factory-handbooks-qa-strategy.md:110`](../spec/work/factory-handbooks-qa-strategy.md) | Traceability   | defect   | minor    | The update test row omits equality of the installed and source path sets. Use the current scenario title and name both path-set and byte equality in the owner row.                                   | test-strategy-agent   |
| [SPEC-0158](../findings/register/document/SPEC-0158.json) | [`docs/spec/work/factory-handbooks-qa-strategy.md:132`](../spec/work/factory-handbooks-qa-strategy.md) | Traceability   | defect   | minor    | The test strategy omits the preserved spec-writer scan. Describe the unchanged scan scope and replacement target separately from the two content assertions. Update the retention summary too.        | test-strategy-agent   |

The review checked consistency, ambiguity, verifiability, completeness, feasibility, necessity, and terminology. The diagnostic requirements and test setup account for the blocking findings.

## Structure checks

- The handbook contracts add no persistent entities or state transitions. [Entity model](../spec/entity-model.md), [state machines](../spec/state-machines.md).
- Two rules leave the scope of stale-list detection unclear when a generator run refuses. [Validation rules](../spec/validation-rules.md), [SPEC-0155](../findings/SPEC-0155.md).
- Scenarios reach both scripts and both generator modes. The diagnostic conflict also applies to the lint command contract. [Interface contracts](../spec/interface-contracts.md#factory-handbooks-contracts).
- Both commands operate on Markdown and expose no new DTO. [Schemas](../spec/schemas).
- The handbooks add no rule to the existing area specification. [Mechanized dispatch](../spec/areas/mechanized-dispatch.md).
- The stub and migration map definitions agree with the validation rules. The actor renames use Contributor consistently in the changed feature text. [Glossary](../spec/glossary.md#factory-handbooks-vocabulary).
- The table has no proposed rows. [Term candidates](../spec/work/term-candidates.md).

## Traceability summary

The [scope map](../spec/scope-map.md) traces the fourteen handbook Rules to the feature. BR-141 and BR-151 now cite their scenarios. The review found two QA summaries that omit parts of their scenarios.

## Disposition

Resolve the two major defects before planning. The run lead will claim IDs for the two finding files and two minor register entries.
