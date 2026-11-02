---
type: inspect-spec
title: "Specification review repeat — core artifact layout"
date: 2026-11-02
status: clean
reviewer: spec-review-agent
findings_filed: 0
scope: core-artifact-layout feature specification after fix commit e5cf4a178d0a80ea4afcc76357f8aded6235b996, against the first review (commit 943a17ee) and the accepted proposal, planning baseline 307979af90fedc6a7b0d9208ca9b3b0d41295f01
---

# Specification Review Repeat — Core Artifact Layout

## Summary

The specification is ready for architecture. The fix commit resolves all four major findings, SPEC-0024 to SPEC-0027, and the four minor items M-01 to M-04 of the [first review](spec-review-core-artifact-layout.md). The fresh inspection found no new major defect. Two new minor items stay in this report and need no finding file. No finding requires a change to the proposal's design.

## Reviewed Specification

Artifacts read:

- `git show e5cf4a17`: the fix commit
- [core-artifact-layout.feature](../spec/core-artifact-layout.feature): 15 Rules, read in full
- [core-artifact-layout-gaps.md](../spec/core-artifact-layout-gaps.md): gaps CAL-G01 to CAL-G16 and the decision on SPEC-0024
- [core-artifact-layout-qa-strategy.md](../spec/core-artifact-layout-qa-strategy.md): the rows the fixes changed
- [interface-contracts.md § migrate-spec-layout](../spec/supplementary_specs/interface-contracts.md), the `update-factory` Layout move row, and the consumer hook Layout move row
- [validation-rules.md § Anchor-file prerequisite](../spec/supplementary_specs/validation-rules.md#anchor-file-prerequisite-feature-addition)
- The first review report and the findings `SPEC-0024` to `SPEC-0027`

`spec-lint` summary: `spec-lint: 0 error(s), 0 warning(s), 25 info across 26 spec file(s).`

## Deterministic Findings

| Check    | Location                                                                    | Disposition                                                         |
| -------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| TODO001  | `docs/spec/todo.md`, `docs/spec/todos.md`                                   | Dismissed: open todo items, not in this feature's scope.            |
| TRACE003 | 23 business rules (BR-011 to BR-055) defined but never referenced elsewhere | Dismissed: none belongs to this feature, which defines no `BR-###`. |
| TRACE004 | `entity-model.md`: `EPIC_BUILDING_BLOCK` has no attribute block             | Dismissed: an existing entity, not touched by this feature.         |

The output matches the first review. `spec-lint` reports nothing in the files of this feature.

## Verification of Prior Findings

| ID        | Verdict  | Evidence                                                                                                                                                                                                                                                                                                                              |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0024 | resolved | The path-table outline (feature lines 52-74) has no glossary row. `Scenario: Git shows the glossary as a new file and keeps the history of chapter 12` (lines 153-158) states the history check, and CAL-06-IT-02 owns it. The gaps report records the stakeholder decision.                                                          |
| SPEC-0025 | resolved | The script scenario (lines 96-101) fails after a link rewrite and the hook rewrite and asserts that `git status` shows no change. The update scenario (lines 249-258) asserts old paths and old content, `.pre-commit-config.yaml` included. The contract's Exit code row lists every change the undo covers.                         |
| SPEC-0026 | resolved | CAL-G15 names the four Rules of `newcomer-onboarding.feature` and assigns their update and their scope-map rows to this feature's stories. CAL-G01 and `validation-rules.md` point at CAL-G15. `Scenario: reverse-map seeds the domain vocabulary into the glossary` (lines 437-442) states the new target, and CAL-12-LN-01 owns it. |
| SPEC-0027 | resolved | CAL-14-IT-01 runs each of the seven gates by its own command, with `structurizr validate` under `-m container`. No owner uses `pre-commit run --all-files`. CAL-09-LN-01 appears nowhere in the specification.                                                                                                                        |
| M-01      | resolved | The Rewrites row of the contract names the `theme` line. The Never rewrites row names the hook block and the `theme` line as the only exceptions. The Moves row and the scenario (line 80) both expect the relative text `theme ../assets/themes/default/theme.json`.                                                                 |
| M-02      | resolved | `Scenario: GLOSS001 stays silent for a term that only a feature file uses besides the glossary` (lines 358-363) fails on a corpus built from Markdown files only. CAL-10-CT-01 owns it.                                                                                                                                               |
| M-03      | resolved | `Scenario: Every gate passes on the migrated factory repository` sits under `Rule: Factory maintainer migrates the factory's own repository first` (lines 496-499). The completion-criteria trace in the gaps report follows.                                                                                                         |
| M-04      | resolved | Gap CAL-G16 records the open arguments of `arch-lint`, `structurizr`, and `spec-lint`, names today's values (`--docs-dir docs/arc42`, `/workspace/arc42/architecture.dsl`, `--context`), and assigns each to the story that changes the script.                                                                                       |

## Semantic Findings

| ID   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Artifact                                                                                 | Characteristic | Category | Severity |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | -------------- | -------- | -------- |
| M-05 | The glossary scenario expects git to show `docs/spec/glossary.md` as added. The script commits nothing, and the contract says only that moves use `git mv`. If the script does not stage the new file, `git status --porcelain` shows `?? docs/spec/glossary.md`, not `A`. The `git log` step is also true by construction, because the script commits nothing. State in the Glossary row of the contract whether the script stages the new glossary and the new chapter 12. Then CAL-06-IT-02 has one assertion. | `core-artifact-layout.feature:153-158`; `interface-contracts.md` § `migrate-spec-layout` | Unambiguous    | Defect   | Minor    |
| M-06 | `validation-rules.md` gives the reason "no migrated project has it" for leaving `docs/CONTEXT.md` out of the anchor set. A migrated project keeps `docs/CONTEXT.md` until the developer runs the fold and deletes the file (feature lines 198-201 and 293-297). The rule itself is right. Only the reason is wrong. Write "no project has it after the fold", as CAL-G01 does. The line predates the fix commit.                                                                                                  | `validation-rules.md:96`                                                                 | Consistent     | Defect   | Minor    |

Neither item blocks planning, so neither has a finding file. The story for `migrate-spec-layout` can settle M-05, and the next edit of `validation-rules.md` can fix M-06.

## Traceability Summary

- **Completion criteria to Rules.** All 24 criteria map to a Rule. The criterion "seven gates pass" now maps to the factory maintainer Rule, which holds its scenario.
- **Rules to scope map.** The fix commit adds or removes no Rule, so the 15 scope-map rows of the first review still match.
- **Rules to QA owners.** Every Rule has an owner. The new scenarios have owners: CAL-06-IT-02, CAL-10-CT-01, CAL-12-LN-01, and CAL-14-IT-01. No owner row cites a removed identifier.
- **Decisions.** DEC-01 to DEC-18 and the CAL-G01 anchor set hold. The SPEC-0024 decision is recorded in the gaps report.
- **Open gaps.** CAL-G02, CAL-G03, CAL-G05, CAL-G06, CAL-G08 to CAL-G14, CAL-G15, and CAL-G16 are open. Each names the story or phase that settles it. None blocks architecture.

## Next Step

Run the Architecture Agent on the core artifact layout. Hand M-05 and M-06 to the planning pass, so the story for `migrate-spec-layout` and the next edit of `validation-rules.md` pick them up.
