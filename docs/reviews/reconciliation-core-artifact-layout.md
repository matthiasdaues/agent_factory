---
type: reconcile-spec
title: Reconciliation of the core artifact layout
date: 2026-11-03
status: pass
reviewer: reconciliation-agent
findings_filed: 0
scope: Specification, architecture, and factory docs of core-artifact-layout against feature/core-artifact-layout at c8724ac0e597890b01443715f87c0786c5adf903
---

# Reconciliation: core artifact layout

The documentation now matches the code of `feature/core-artifact-layout`. Every
discrepancy below was stale documentation. The code review of the same branch
filed the two code defects (IMPL-0001 and IMPL-0002), so this pass files no
RECON finding of its own.

## Scope

- Code: `packages/factory/scripts/` (`migrate-spec-layout`, `init-factory`,
  `update-factory`, `module-graph-check`, `arch-lint`, `structurizr`,
  `spec-lint`, `scope-lint`, `concern-lint`), the skills `capture-context` and
  `domain-modeling`, and the tests in `tests/factory/`.
- Documentation: `docs/spec/` (core files, `features/`, `work/`), `docs/arc42/`,
  ADR-0025, ADR-0026, `packages/factory/docs/factory-guide.md`, and one line of
  `docs/proposals/core-artifact-layout.md`.

## Discrepancy table

| #   | Location                                                 | Discrepancy                                                                                                                                                       | Classification | Action                                                                                                                    |
| --- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------- |
| 1   | `glossary.md`, chapter 5 (two tables), chapter 6 § 6.4.3 | `module-graph-check` was said to exit 1 for the architecture phase. It exits 0 and prints `architecture_change=true` or `false`; exit 2 means a missing input.    | Spec stale     | Rewritten. Chapter 5 also shows the real call, `--proposal PATH`.                                                         |
| 2   | `interface-contracts.md` § `migrate-spec-layout`         | `--dry-run` row left the duplicate terms open and did not say that it skips the repository refusals.                                                              | Spec stale     | Row lists every printed line and the skipped refusals.                                                                    |
| 3   | same section                                             | No `hook:` line, no order of edits and moves, no staging of the glossary (M-05), no exit 2 for a `## Language` section outside the list form, output stream wrong | Spec stale     | Rewrites, new Order row, Glossary, Output, Preconditions, and Exit code rows. The list-form refusal cites IMPL-0002.      |
| 4   | same section, No work row                                | A hook block that differs from the template also gives the script work.                                                                                           | Spec stale     | Row names the hook block.                                                                                                 |
| 5   | `interface-contracts.md` § `init-factory`                | First-install output format and the exit code of a failed migration were not stated.                                                                              | Spec stale     | `init-factory: old layout: <line>` and exit `1` recorded.                                                                 |
| 6   | `interface-contracts.md` § `update-factory`              | No row for the hook refresh without a question after a layout migration (ST-0333).                                                                                | Undocumented   | New Hook refresh row.                                                                                                     |
| 7   | `interface-contracts.md` § Referenced from               | Lists the removed `use_cases/system-use-cases.md`.                                                                                                                | Spec stale     | Line removed.                                                                                                             |
| 8   | `work/core-artifact-layout-gaps.md`                      | CAL-G02, G03, G05, G06, G08, G10 to G16 still open although stories settled them.                                                                                 | Spec stale     | Each closed with its story and the contract row that holds the value. CAL-G09 stays open.                                 |
| 9   | `entity-model.md`                                        | CAL-G13 listed as unspecified.                                                                                                                                    | Spec stale     | At most once per section, as `context-format.md` and `domain-modeling` define it.                                         |
| 10  | `validation-rules.md`                                    | Wrong reason for leaving `docs/CONTEXT.md` out of the anchor set (M-06).                                                                                          | Spec stale     | "No project has a `docs/CONTEXT.md` after the fold."                                                                      |
| 11  | `work/core-artifact-layout-qa-strategy.md`               | All 38 owner rows `planned`; CAL-07-IT-05 named `test_update_factory.py`; two rows named one of two test files.                                                   | Spec stale     | Rows `implemented` with real paths; acceptance rows cite ST-0343 and ST-0344. Stale harness text and gap actions updated. |
| 12  | `packages/factory/docs/factory-guide.md`                 | Three anchor files; `spec-lint` row named PRD and actor-goal checks.                                                                                              | Spec stale     | Four anchor files; `spec-lint` row names what the script checks.                                                          |
| 13  | `features/newcomer-onboarding.feature`                   | Feature description said three anchor files (CAL-G15). The Rules and scope-map rows were already right.                                                           | Spec stale     | Four anchor files.                                                                                                        |
| 14  | `docs/proposals/core-artifact-layout.md`                 | `impact.boundaries` named the deleted `templates/context.md`.                                                                                                     | Spec stale     | Now names `templates/glossary.md`.                                                                                        |
| 15  | Chapter 6 § 6.10.6, ADR-0026                             | "Planning sets the layout release (gap CAL-G02)."                                                                                                                 | Spec stale     | Layout release `1.4.0`, `LAYOUT_RELEASE`. Chapter 6 also names the staging and the hook refresh.                          |
| 16  | Chapter 8 § current state                                | Said `CONTEXT.md` and `CONTEXT-MAP.md` remain until ST-0344.                                                                                                      | Spec stale     | States the folded routing.                                                                                                |
| 17  | `docs/arc42/concepts.md` tree                            | Showed `orchestrator/`, a flat `docs/` with `architecture.dsl`, `CONTEXT-MAP.md`, and use cases.                                                                  | Spec stale     | Tree shows `packages/` and the core layout.                                                                               |
| 18  | `features/core-artifact-layout.feature`                  | Eleven Rules had no `@`-reference.                                                                                                                                | Undocumented   | Rule-level `@`-references added; every reference resolves.                                                                |
| 19  | `scope-map.md`                                           | The 15 rows of this feature were `specified` with no Feature Link.                                                                                                | Spec stale     | `implemented`, with the implementing files.                                                                               |

## Not changed

- `docs/README.md` links chapter 12 as the glossary definition. The file is
  outside this pass's ownership. The link still resolves, because chapter 12
  links on to `docs/spec/glossary.md`.
- `docs/proposals/core-artifact-layout.md` also names the deleted
  `templates/context-map.md` in `impact.boundaries`. The brief allowed one line.
- `scope-map.md` keeps the `specified` row "LinkML entity model serves as
  canonical domain source". `activity-graph-orchestration.feature` has no such
  Rule since commit `96ceb690`, before this feature. RECON-cycle-retirement
  covers that cleanup.
- The `UC-NN` code spans in the spec are the designed result of a link to a
  removed use-case file (`Scenario: A link to a removed file becomes its link text in a code span`).
- No story of this feature has a `tests:` field. `backlog/` is outside this
  pass's ownership. The QA strategy maps every owned contract to its test file,
  and 678 tests of those files pass without the container suite.
- The QA layer status has no value for a layer whose contracts all have tests.
  The table uses `partially covered`, the defined value once any test exists.
- `migrate-spec-layout` lists a term only when it stands in more than one
  section. A term twice in one copied section is not listed.

## Code defects filed

None by this pass. The code review filed IMPL-0001 (two old files with one new
path) and IMPL-0002 (the list-form refusal of a `## Language` section). The
contract states the behaviour of IMPL-0002 and names the finding.

## Linter results

| Gate                                   | Exit | Note                                                                                                                           |
| -------------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------ |
| `spec-lint`                            | 0    | 0 errors, 0 warnings, 58 info                                                                                                  |
| `arch-lint --docs-dir docs/arc42`      | 0    | 1 warning, `ARCH-PARSE`, also on the base commit                                                                               |
| `scope-lint`                           | 1    | 77 errors, the same list as on the base commit (todo T-0010)                                                                   |
| `concern-lint`                         | 4    | `CTX-PATHS` for the generated `INDEX.yaml` of four CLI folders, which a fresh worktree lacks; the same four on the base commit |
| `link-check` on changed Markdown files | 0    | All local links resolve                                                                                                        |
