# Gaps Report: factory-handbooks

Generated: 2026-11-25
Source: [factory-handbooks.md](../../proposals/factory-handbooks.md), accepted at commit `4ebf5101f70c1540a0d53dcfb3d00cfa977d361a` on `dev`

The feature file [factory-handbooks.feature](../features/factory-handbooks.feature) has 14 Rules and 84 Scenarios. Each Rule carries a trace comment `FH-NN`, and each Scenario carries a trace comment `FH-NN-NN`, so a test can name the Scenario it checks. No question is open. [Resolved questions](#resolved-questions) records the seven answers of the run lead.

## Actor-Goal Matrix

The User is the person who runs the factory in a project, as the [glossary](../glossary.md) defines. The Contributor is a person who changes the factory itself, as the proposal's Primer defines. The [glossary](../glossary.md) holds Contributor and the other handbook terms as confirmed entries.

| ID    | Actor             | Goal                                                                 | Rule                                                                                              | Status    |
| ----- | ----------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------- |
| FH-01 | Contributor       | See the page list of a folder without writing it by hand             | Rule: Contributor sees the page list of a folder written by handbook-index                        | specified |
| FH-02 | Contributor       | See every chapter in the top-level index                             | Rule: Contributor sees every chapter in the top-level index of a handbook                         | specified |
| FH-03 | Contributor       | Learn that a page list is out of date                                | Rule: Contributor learns from handbook-index --check that a page list is out of date              | specified |
| FH-04 | Contributor       | Learn which page breaks the page format                              | Rule: Contributor learns from handbook-lint which page breaks the page format                     | specified |
| FH-05 | Contributor       | Keep a broken page out of a commit                                   | Rule: Contributor cannot commit a handbook page that breaks the page format                       | specified |
| FH-06 | Contributor       | Keep each binding rule in one home                                   | Rule: Contributor repeats a binding rule only in a rule summary that links to its home            | specified |
| FH-07 | User              | Read the user handbook that matches the installed code               | Rule: User reads the installed user handbook after init-factory or update-factory                 | specified |
| FH-08 | User              | Find the content of the factory guide                                | Rule: User finds the content of the factory guide on user handbook pages                          | specified |
| FH-09 | User, Contributor | Find the content of `concepts.md` and `beginner-intro.md`            | Rule: User and contributor find the content of concepts.md and beginner-intro.md in the handbooks | specified |
| FH-10 | User, Contributor | Follow an old link to the new home of its information                | Rule: User and contributor follow every old link to the new home of its information               | specified |
| FH-11 | Contributor       | Run a passing test suite after the move                              | Rule: Contributor runs the test suite against the handbook pages                                  | specified |
| FH-12 | User              | Reach the user handbook from each factory entry point                | Rule: User reaches the user handbook from every factory entry point                               | specified |
| FH-13 | Contributor       | Reach the contributor handbook from the README and the agent context | Rule: Contributor reaches the contributor handbook from the root README and the agent context     | specified |
| FH-14 | Contributor       | Find the first contributor chapters written and the others started   | Rule: Contributor finds the first contributor chapters written and the others started as stubs    | specified |

## Completion Criteria Trace

| Completion criterion of the proposal                                                          | Scenario                                        |
| --------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `handbook-lint` exits 0 on both handbooks and non-zero on a test page for each failure        | FH-04-01 to FH-04-15                            |
| `handbook-index --check` exits 0 on both handbooks                                            | FH-03-01                                        |
| `link-check` over every live document exits 0                                                 | FH-10-08                                        |
| `handbook-index` and `handbook-lint` fail on an `index.md` without markers, no self-listing   | FH-01-08, FH-01-10, FH-03-03, FH-04-05          |
| The pre-commit configuration runs `handbook-lint`, and a page without `type` fails the commit | FH-05-01 to FH-05-03, FH-05-05                  |
| `factory-guide.md` is gone, the `rg` search finds nothing, the tests pass, the changelog      | FH-07-04, FH-08-04, FH-11-01, FH-11-02          |
| Every section heading of the guide maps to a user handbook page                               | FH-08-02, FH-08-03                              |
| No tracked Markdown file links to the three deleted files                                     | FH-10-01 to FH-10-07                            |
| `concepts.md` and `beginner-intro.md` are gone, their content is on the two new pages         | FH-09-01 to FH-09-04                            |
| After `update-factory`, the installed `index.md` lists every user handbook chapter            | FH-07-01, FH-07-02, FH-07-05, FH-07-06          |
| Session menu H as a new user starts the `getting-started/` tutorial                           | FH-12-01, FH-12-02, newcomer-onboarding Rule    |
| The contributor tutorial goes from `git clone` to a passing test run                          | FH-14-02                                        |
| The `contributing/` chapter is written, every other chapter has an index and a stub           | FH-14-01, FH-14-03 to FH-14-05                  |
| The READMEs and the agent context link to the handbooks                                       | FH-12-06, FH-13-01, FH-13-02                    |
| The lector agent's report exists and its fixes are applied                                    | none, see [Process criteria](#process-criteria) |

## Missing Rules

None. Every actor-goal pair has a Rule.

## Rules Without Scenarios

None. Every Rule has at least one Scenario.

## Process criteria

Two completion criteria describe work steps, not behaviour, so no Scenario states them:

- The lector agent reads the migrated user handbook once before release, and its fixes are applied.
- The migration writes the migration map to `docs/spec/work/factory-handbooks-migration-map.md`. FH-08-02 and FH-08-03 read that file, so it must exist before the two Scenarios can run.

The `type` table of the proposal also sets what each page type contains. No script checks page content, so the lector and the reviewer own that table.

## Changes to existing feature files

- [newcomer-onboarding.feature](../features/newcomer-onboarding.feature), Rule "Newcomer walks through a guided tour before choosing a workflow": the @-reference and Scenario "Newcomer selects the guided tour from the session entrypoint" name the tutorial page of `.agent-factory/factory/docs/handbook/getting-started/`.
- [opencode-cli-integration.feature](../features/opencode-cli-integration.feature), Scenario "Documentation records OpenCode support": the three steps and the @-reference name a page in `packages/factory/docs/handbook/cli-integrations/`.
- [scope-map.md](../scope-map.md): the row "Newcomer walks through a guided tour before choosing a workflow" links to `.agent-factory/factory/docs/handbook/getting-started/`. The 14 Rules of this feature are new rows with status `specified`.

## Ambiguous Wording

| Location | Step Text                                              | Issue                                                                                                 | Suggested Fix                                                    |
| -------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| FH-14-02 | "every script and path that the tutorial names exists" | A test can check that each named path exists. Whether the commands run in order needs a manual check. | Keep the Scenario. The QA strategy decides which part is manual. |

## Resolved questions

1. **Order and heading of the type groups.** Case: `getting-started/index.md` lists a `tutorial` page "Run your first session" and a `reference` page "Session menu options". The run lead's answer: the groups follow the type table, so the tutorial group comes first. The headings are "Tutorials", "Concepts", "How-to guides", "Reference", and "Learning". A group with no listed page has no heading. FH-01-02 and FH-01-11 to FH-01-13 state it.

2. **Chapters with the same `order`.** Case: `research/` and `usage-capture/` both keep the default 100. The run lead's answer: ties sort by `title`, as pages do, so "Research" comes before "Usage capture". FH-02-04 states it.

3. **A folder inside a chapter.** Case: a contributor creates `cli-integrations/opencode/`. The run lead's answer: the first release has no folder inside a chapter, so `handbook-lint` exits non-zero and reports the path `cli-integrations/opencode/`. FH-04-13 states it.

4. **Values of `order`.** Case: a page has `order: -5`, another `order: 2.5`. The run lead's answer: any integer is valid, including 0 and negative integers, so `-5` passes. A decimal or a value that is not a number is a `handbook-lint` error that names the file, so `2.5` fails. FH-04-03 and FH-04-14 state it.

5. **Repeated or reversed markers.** Case: `cli-integrations/index.md` holds the end marker before the start marker. The run lead's answer: each `index.md` holds each marker exactly once, the start marker first. A missing, repeated, or reversed marker is an error of `handbook-index`, of `handbook-index --check`, and of `handbook-lint`. FH-01-10, FH-03-03, and FH-04-05 state it.

6. **Titles that differ only in case.** Case: "Add a CLI integration" and "add a CLI Integration" in one chapter. The run lead's answer: they are duplicates, so `handbook-lint` fails. FH-04-06 states it.

7. **A commit that only deletes a page.** Case: a contributor deletes `remove-an-integration.md` and stages only the deletion. The run lead's answer: the hook runs `handbook-lint` on every commit (`always_run`), so the out-of-date page list fails the commit. FH-05-03 and FH-05-05 state it.

## Review findings that touch the specification

- PROP-07: FH-07 checks the installed index but not the links of the installed pages. A user handbook link to a file outside `packages/factory/` breaks in a user project. No Scenario covers it. The product owner keeps PROP-07 open as a minor, so no Scenario covers it.
- PROP-08: FH-10-01 to FH-10-03 need a section-by-section rewrite. `_link_rewrite.py` maps one old path to one new path and keeps the old anchor, so the migration must extend it. The product owner keeps PROP-08 open as a minor, so no Scenario covers it.
- PROP-09: [core-artifact-layout.feature](../features/core-artifact-layout.feature) names `docs/arc42/concepts.md` in an example step. The step describes an example project, not this repository's file, so it needs no change.
