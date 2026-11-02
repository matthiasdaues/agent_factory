---
type: inspect-spec
title: "Specification review — core artifact layout"
date: 2026-11-02
status: defects
reviewer: spec-review-agent
findings_filed: 4
scope: core-artifact-layout feature specification (commit d4a3c0b78a6d33685337acad45f43b928f8deeb0) against the accepted proposal, planning baseline 307979af90fedc6a7b0d9208ca9b3b0d41295f01
---

# Specification Review — Core Artifact Layout

## Summary

The specification follows the proposal closely. All 24 completion criteria trace to a Rule. DEC-01 to DEC-18 and the anchor-set decision of gap CAL-G01 are implemented. Four major defects block a clean pass. One scenario cannot pass on a correct implementation. The failure undo is weaker than its completion criterion. Another feature file still specifies `docs/CONTEXT.md`. One QA owner command does not run three of its gates. Four minor findings stay in this report.

No finding requires a change to the proposal's design. SPEC-0024 has one optional branch that would: keeping the glossary's git history. That branch goes to the stakeholder only if wanted.

## Reviewed Specification

Artifacts read:

- [core-artifact-layout.feature](../spec/core-artifact-layout.feature): 15 Rules
- [core-artifact-layout-gaps.md](../spec/core-artifact-layout-gaps.md): gaps CAL-G01 to CAL-G14
- [core-artifact-layout-qa-strategy.md](../spec/core-artifact-layout-qa-strategy.md)
- [scope-map.md](../spec/scope-map.md): the 15 new rows
- `git show d4a3c0b7 -- docs/spec/supplementary_specs`: changes to `entity-model.md`, `interface-contracts.md`, `state-machines.md`, and `validation-rules.md`
- [core-artifact-layout.md](../proposals/core-artifact-layout.md): the accepted proposal, for traceability
- For checks: `newcomer-onboarding.feature`, `.pre-commit-config.yaml`, `docs/arc42/architecture.dsl`, and `packages/factory/scripts/spec-lint`

`spec-lint` summary: `spec-lint: 0 error(s), 0 warning(s), 25 info across 26 spec file(s).`

## Deterministic Findings

| Check    | Location                                                                    | Disposition                                                         |
| -------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| TODO001  | `docs/spec/todo.md`, `docs/spec/todos.md`                                   | Dismissed: open todo items, not in this feature's scope.            |
| TRACE003 | 23 business rules (BR-011 to BR-055) defined but never referenced elsewhere | Dismissed: none belongs to this feature, which defines no `BR-###`. |
| TRACE004 | `entity-model.md`: `EPIC_BUILDING_BLOCK` has no attribute block             | Dismissed: an existing entity, not touched by this feature.         |

`spec-lint` reports no finding in the files of this feature.

## Semantic Findings

| ID        | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Artifact                                                                               | Characteristic | Category | Severity |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------- | -------- | -------- |
| SPEC-0024 | The path-table outline requires a git rename for `12_glossary.md`. The script writes a new chapter 12 at the old path, so git shows a modified file and an added file, not a rename. A scratch-repository check confirmed this. Remove the row and state the history check in the glossary Rule.                                                                                                                                                                                                              | `core-artifact-layout.feature:52-75`                                                   | Verifiable     | Defect   | Major    |
| SPEC-0025 | Both failure scenarios and the contract check that paths are restored, not content. The script edits links, chapter 12, `CONTEXT.md`, the hook block, and the DSL theme line before it can fail. The completion criterion requires the project's files "as before the update". Assert that every change is undone.                                                                                                                                                                                            | `core-artifact-layout.feature:97-102, 243-250`                                         | Complete       | Defect   | Major    |
| SPEC-0026 | Four `implemented` Rules of `newcomer-onboarding.feature` still name three anchor files with `docs/CONTEXT.md`, and still have `reverse-map` and feature-addition write terms there. CAL-G01 notices the conflict and closes the gap without an owner. No scenario says where `reverse-map` seeds terms after the change. Update or supersede those Rules, and add a `reverse-map` scenario.                                                                                                                  | `newcomer-onboarding.feature:94-217`; `core-artifact-layout-gaps.md` CAL-G01           | Consistent     | Defect   | Major    |
| SPEC-0027 | CAL-09-LN-01 owns "every gate passes" with `pre-commit run --all-files`. The repository has no hook for `scope-lint`, `dependency-check`, or `structurizr`, and its `arch-lint` hook runs `--no-validate`. Give the contract a command that runs all seven gates.                                                                                                                                                                                                                                             | `core-artifact-layout-qa-strategy.md:90`                                               | Verifiable     | Defect   | Major    |
| M-01      | The `migrate-spec-layout` contract says the script never rewrites an old path outside a Markdown link. Its Moves row and the theme scenario require it to rewrite the `theme` line of `architecture.dsl`, which is not Markdown. Name the theme line as an exception in the Rewrites row, next to the hook block. The theme line is `theme themes/default/theme.json`, which is relative to the DSL file. So also state whether the scenario expects the relative text `../assets/themes/default/theme.json`. | `interface-contracts.md` § `migrate-spec-layout`; `core-artifact-layout.feature:77-82` | Consistent     | Defect   | Minor    |
| M-02      | The proposal says `GLOSS001` reports a term that no other core file uses. Feature files and the DSL files are core files. `check_glossary` builds its corpus from `spec.rglob("*.md")` only. Both `GLOSS001` scenarios use Markdown files, so an unchanged corpus passes them. Add a scenario in which only a `.feature` file uses the term and `GLOSS001` stays silent.                                                                                                                                      | `core-artifact-layout.feature:343-353`                                                 | Verifiable     | Defect   | Minor    |
| M-03      | `Scenario: Every gate passes on the migrated factory repository` has the factory maintainer act under a Rule whose actor is the project maintainer. Move the scenario to a factory maintainer Rule, or make the actor the project maintainer.                                                                                                                                                                                                                                                                 | `core-artifact-layout.feature:316-319`                                                 | Terminology    | Defect   | Minor    |
| M-04      | No contract or gap says how `arch-lint`, `structurizr`, and `spec-lint` find their files at the new paths. Examples are a new argument or a new default. Today the hook runs `arch-lint --docs-dir docs/arc42`, and `spec-lint` reads its terms through `--context`. The proposal marks `external_contract_change: true`. Record the open arguments as a gap for the stories that change these scripts.                                                                                                       | `core-artifact-layout-gaps.md`; `interface-contracts.md`                               | Complete       | Question | Minor    |

## Traceability Summary

- **Completion criteria to Rules.** All 24 criteria of the proposal map to a Rule in the gaps report, and each mapped Rule holds a matching scenario. The failure criterion maps to a scenario that is weaker than the criterion (SPEC-0025).
- **Rules to scope map.** All 15 Rules have a scope-map row with status `specified` and a link to the feature file. No orphan row and no Rule without a row.
- **Rules to QA owners.** Every Rule has at least one owner, CAL-01 to CAL-15. The owner of CAL-09-LN-01 does not run its gates (SPEC-0027).
- **Path table to the factory's `docs/spec/`.** Every file at the top of `docs/spec/` and in `supplementary_specs/` matches a row of the path table. `mechanized-dispatch.md` moves to `areas/` and its QA strategy to `work/`. After the migration, the top of `docs/spec/` holds only core files.
- **Decisions.** DEC-01 to DEC-18 are implemented. DEC-04 and DEC-11 are superseded by DEC-17, and the specification follows DEC-17. The anchor set of CAL-G01 is in the feature file, `validation-rules.md`, and `entity-model.md`, but not in `newcomer-onboarding.feature` (SPEC-0026).
- **Business rules.** This feature defines and references no `BR-###`.
- **Open gaps.** CAL-G02, CAL-G03, CAL-G05, CAL-G06, and CAL-G08 to CAL-G14 are open, and each names the story or phase that settles it. None blocks architecture.

## Next Step

The Requirements Agent fixes SPEC-0024 to SPEC-0027 in the specification. M-01 to M-04 can go into the same pass. Then this review runs again.
