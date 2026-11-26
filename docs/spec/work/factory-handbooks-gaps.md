# Gaps Report: factory-handbooks

Generated: 2026-11-25
Source: [factory-handbooks.md](../../proposals/factory-handbooks.md), accepted at commit `4ebf5101f70c1540a0d53dcfb3d00cfa977d361a` on `dev`

The feature file [factory-handbooks.feature](../features/factory-handbooks.feature) has 7 Rules and 14 Scenarios. Each Rule carries a trace comment `FH-NN`, and each Scenario carries a trace comment `FH-NN-NN`, so a test can name the Scenario it checks. The Scenarios state the behaviour a person sees. The details of each rule live in BR-140 to BR-152 of [validation-rules.md](../validation-rules.md#factory-handbooks-handbook-index-handbook-lint-br-140br-152). The one-time checks of the migration live in [Acceptance criteria for the stories](#acceptance-criteria-for-the-stories). No question is open.

## Actor-Goal Matrix

The User is the person who runs the factory in a project. The Contributor is a person who changes the factory itself. The [glossary](../glossary.md) defines both.

| ID    | Actor             | Goal                                                                 | Rule                                                                                          | Status    |
| ----- | ----------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | --------- |
| FH-01 | Contributor       | See the page lists without writing them by hand                      | Rule: Contributor sees the page lists of a handbook written by handbook-index                 | specified |
| FH-02 | Contributor       | Learn which page or page list breaks the handbook rules              | Rule: Contributor learns which page or page list breaks the handbook rules                    | specified |
| FH-03 | Contributor       | Keep a broken page out of a commit                                   | Rule: Contributor cannot commit a handbook page that breaks the page rules                    | specified |
| FH-04 | User              | Read the user handbook that matches the installed code               | Rule: User reads the installed user handbook after init-factory or update-factory             | specified |
| FH-05 | User, Contributor | Find the content of the three deleted files at its new home          | Rule: User and contributor find the content of the three deleted files at its new home        | specified |
| FH-06 | User              | Reach the user handbook from each factory entry point                | Rule: User reaches the user handbook from every factory entry point                           | specified |
| FH-07 | Contributor       | Reach the contributor handbook from the README and the agent context | Rule: Contributor reaches the contributor handbook from the root README and the agent context | specified |

## Completion Criteria Trace

| Completion criterion of the proposal                                                          | Scenario or acceptance criterion           |
| --------------------------------------------------------------------------------------------- | ------------------------------------------ |
| `handbook-lint` exits 0 on both handbooks and non-zero on a test page for each failure        | FH-02-02, FH-02-03, acceptance criterion 1 |
| `handbook-index --check` exits 0 on both handbooks                                            | FH-02-01, acceptance criterion 1           |
| `link-check` over every live document exits 0                                                 | FH-05-02                                   |
| `handbook-index` and `handbook-lint` fail on an `index.md` without markers, no self-listing   | FH-01-02, FH-02-02, BR-143                 |
| The pre-commit configuration runs `handbook-lint`, and a page without `type` fails the commit | FH-03-01, BR-148                           |
| `factory-guide.md` is gone, the `rg` search finds nothing, the tests pass, the changelog      | FH-05-03, acceptance criteria 6, 7, and 8  |
| Every section heading of the guide maps to a user handbook page                               | FH-05-01                                   |
| No tracked Markdown file links to the three deleted files                                     | FH-05-02                                   |
| `concepts.md` and `beginner-intro.md` are gone, their content is on the two new pages         | FH-05-03, acceptance criteria 4 and 5      |
| After `update-factory`, the installed `index.md` lists every user handbook chapter            | FH-04-01, FH-01-04, acceptance criterion 2 |
| Session menu H as a new user starts the `getting-started/` tutorial                           | FH-06-01, newcomer-onboarding Rule         |
| The contributor tutorial goes from `git clone` to a passing test run                          | acceptance criterion 3                     |
| The `contributing/` chapter is written, every other chapter has an index and a stub           | acceptance criterion 3                     |
| The READMEs and the agent context link to the handbooks                                       | FH-06-01, FH-07-01                         |
| The lector agent's report exists and its fixes are applied                                    | acceptance criterion 9                     |

## Missing Rules

None. Every actor-goal pair has a Rule.

## Rules Without Scenarios

None. Every Rule has at least one Scenario.

## Changes to existing feature files

- [newcomer-onboarding.feature](../features/newcomer-onboarding.feature), Rule "Newcomer walks through a guided tour before choosing a workflow": the @-reference and Scenario "Newcomer selects the guided tour from the session entrypoint" name the tutorial page of `.agent-factory/factory/docs/handbook/getting-started/`.
- [opencode-cli-integration.feature](../features/opencode-cli-integration.feature), Scenario "Documentation records OpenCode support": the three steps and the @-reference name a page in `packages/factory/docs/handbook/cli-integrations/`.
- [scope-map.md](../scope-map.md): the row "Newcomer walks through a guided tour before choosing a workflow" links to `.agent-factory/factory/docs/handbook/getting-started/`. The 7 Rules of this feature are rows with status `specified`.

## Ambiguous Wording

None.

## Resolved questions

The run lead answered seven questions while the feature file was derived. Each answer lives in a rule:

| Question                              | Answer                                                                                      | Home         |
| ------------------------------------- | ------------------------------------------------------------------------------------------- | ------------ |
| Order and headings of the type groups | The type table's order, with the headings "Tutorials" to "Learning"; no heading when empty  | BR-144, L-12 |
| Chapters with the same `order`        | They sort by `title`, then by the path of the folder                                        | BR-145, L-13 |
| A folder inside a chapter             | `handbook-lint` fails and names the folder                                                  | BR-141, L-14 |
| Values of `order`                     | Any integer is valid, 0 and negative numbers included; a decimal or a word fails            | BR-140       |
| Repeated or reversed markers          | Each marker appears once, the start marker first; anything else is an error of both scripts | BR-143       |
| Titles that differ only in case       | They count as one title, so `handbook-lint` fails                                           | BR-142       |
| A commit that only deletes a page     | The hook runs on every commit, so the out-of-date page list fails the commit                | BR-148       |

## Review findings that touch the specification

- PROP-07: FH-04 checks the installed files but not the links of the installed pages. A user handbook link to a file outside `packages/factory/` breaks in a user project. The product owner keeps PROP-07 open as a minor, so no Scenario covers it (L-15).
- PROP-08: BR-151 needs a section-by-section rewrite. `_link_rewrite.py` maps one old path to one new path and keeps the old anchor, so the migration must extend it. The product owner keeps PROP-08 open as a minor, so planning carries it as implementation work (L-15).
- PROP-09: [core-artifact-layout.feature](../features/core-artifact-layout.feature) names `docs/arc42/concepts.md` in an example step. The step describes an example project, not this repository's file, so it needs no change.

## Acceptance criteria for the stories

These checks hold once, after the migration. They come from the proposal's Scope and Completion Criteria. No Scenario states them, because each checks one state of this repository and not the behaviour of a script. The story that does the work carries the criterion.

01. `handbook-lint` and `handbook-index --check` exit 0 on both handbooks of this repository.
02. `packages/factory/docs/handbook/` holds an `index.md` and the twelve chapter folders of the proposal: `getting-started/`, `concepts/`, `playbooks/`, `agent-context/`, `quality-and-review/`, `branches-and-dispatch/`, `research/`, `cli-integrations/`, `installation-and-updates/`, `usage-capture/`, `reference/`, and `troubleshooting/`. Each holds an `index.md`, and the guide's section "Getting Started" is the `tutorial` page of `getting-started/`.
03. `docs/handbook/` holds an `index.md` and the nine chapter folders `getting-started/`, `architecture/`, `agents-and-skills/`, `gates-and-hooks/`, `cli-integrations/`, `testing/`, `workflow/`, `release/`, and `contributing/` (DEC-08). The `getting-started/` tutorial takes a person from `git clone` to a passing test run, and every script and path it names exists. Its author runs it once on a fresh clone before the feature merge and records the result in the story (L-20). `contributing/` describes the page format, the stub rule, `handbook-index`, and `handbook-lint`. Each other chapter holds at least one stub with one sentence of scope and a link to a source.
04. The `concept` page of the user handbook's `concepts/` holds the sections "The phase chain" and "Key ideas" of `concepts.md` (DEC-09).
05. The `reference` page of the contributor handbook's `architecture/` holds the directory tree of `concepts.md`, corrected to name `packages/factory/` as the source of the factory. It has status `implemented`, and `architecture/` still holds a stub. `docs/README.md` links to this page and to the page of criterion 4.
06. No file under `tests/` names the guide. `test_core_layout_references.py` keeps its scan of every spec-writer file, with the handbook path in place of the guide. `test_brownfield_order.py` and `test_hook_missing_factory.py` keep their content checks and read the user handbook page that now holds the checked text.
07. The full test suite passes. `premerge-check` runs it at the feature merge (L-20).
08. The `CHANGELOG.md` entry of the release names the move of `factory-guide.md` and the path `.agent-factory/factory/docs/handbook/` (DEC-07).
09. The lector agent reads the migrated user handbook once before release, and its fixes are applied.
10. Every `> Rule summary:` callout on a handbook page is followed by a `> Source:` line that links to `packages/factory/rulebooks/rules.md` or a file under `packages/factory/rulebooks/` (BR-149).
11. The migration writes the migration map `docs/spec/work/factory-handbooks-migration-map.md` before FH-05-01 can run.
12. Every section of `factory-guide.md` at commit `4ebf5101f70c1540a0d53dcfb3d00cfa977d361a` is on the page that the migration map names: its facts, commands, and paths are there, rewritten in the factory voice. The code review of the migration story checks this section by section (SPEC-0172).
