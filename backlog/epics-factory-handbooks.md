---
scope: global
---

# EPICs — Factory Handbooks

Proposal trace: [factory-handbooks.md](../docs/proposals/factory-handbooks.md), accepted, DEC-01 to DEC-14
Specification trace: [factory-handbooks.feature](../docs/spec/features/factory-handbooks.feature) (7 Rules, 14 Scenarios), [gaps report](../docs/spec/work/factory-handbooks-gaps.md) with acceptance criteria 01 to 12, [validation-rules.md § Factory handbooks](../docs/spec/validation-rules.md#factory-handbooks-handbook-index-handbook-lint-br-140br-152) (BR-140 to BR-152), [interface-contracts.md § Factory Handbooks Contracts](../docs/spec/interface-contracts.md#factory-handbooks-contracts)
Architecture trace: none. `impact.architecture_change` is `false` by manual override (L-40), so no ADR or arc42 section changes.
QA strategy trace: [factory-handbooks-qa-strategy.md](../docs/spec/work/factory-handbooks-qa-strategy.md), one owner row per Scenario
Run decisions: [handbooks-decision-log.md](../docs/spec/work/handbooks-decision-log.md), L-01 to L-45

The six stories are ST-0452 to ST-0457. Each holds its Goal, Demo, and Evidence in its own file under `backlog/`.

## Story waves

`dispatch plan` sets the waves from the dependencies and the file overlap. This table is the expected result.

| Wave | Stories          | Reason for the order                                                                                                        |
| ---- | ---------------- | --------------------------------------------------------------------------------------------------------------------------- |
| W1   | ST-0452          | The hook of ST-0452 runs `handbook-lint` on every commit, so both handbook roots must exist before any page is written      |
| W2   | ST-0453, ST-0456 | ST-0453 writes the user handbook and ST-0456 the contributor handbook; they share no file                                   |
| W3   | ST-0455          | The entry points name pages that ST-0453 writes                                                                             |
| W4   | ST-0454          | ST-0454 deletes the three old files, so every text that names them must already point elsewhere (ST-0453, ST-0455, ST-0456) |
| W5   | ST-0457          | The lector reads the user handbook once it is complete, after the concept page of ST-0454                                   |

ST-0452 and ST-0454 change Python scripts, so they carry `quality-gates: [crap-score]`. The other four stories change only Markdown, tests, and configuration text, so they carry `quality-gates: []`. `docs/testing.yaml` disables mutation testing.

## Terms used in this file

The proposal's [Primer](../docs/proposals/factory-handbooks.md#primer) and the [glossary](../docs/spec/glossary.md) define each term. A short reminder:

- **User handbook.** `packages/factory/docs/handbook/`. It installs into every project as `.agent-factory/factory/docs/handbook/`.
- **Contributor handbook.** `docs/handbook/`. It stays in this repository.
- **Chapter.** A folder of a handbook. Its `index.md` is the chapter page.
- **Page list.** The text between `<!-- handbook-index:start -->` and `<!-- handbook-index:end -->` in an `index.md`. `handbook-index` writes it.
- **Stub.** A page with `status: stub`. It names its scope and its sources, and no page list shows it.
- **The three old files.** `packages/factory/docs/factory-guide.md` (the guide), `docs/arc42/concepts.md`, and `docs/arc42/beginner-intro.md`.
- **Migration map.** `docs/spec/work/factory-handbooks-migration-map.md`. One row per section of the three old files names the handbook page that now holds it.
- **Live document and record folder.** The proposal's [§ Design Details](../docs/proposals/factory-handbooks.md#design-details) lists the record folders. Every other tracked Markdown file outside `poc/` is a live document.

## Rules that hold for every story

- Source edits go to `packages/factory/`, never to `.agent-factory/factory/`.
- No story edits the feature file, `validation-rules.md`, or `interface-contracts.md`. A story that finds a conflict writes a spec-feedback row.
- Each story owns the QA strategy rows that the Ownership Resolution below assigns to it. A test carries `@pytest.mark.spec("<Test ID>")` and names the Scenario trace in its function name.
- `test_handbook_index.py` and `test_handbook_lint.py` name `handbook-index` and `handbook-lint` literally, because `tests/select_tests.py` selects a test file by the script name.
- Agents do not run `uv run pytest` by hand, because the guardrail blocks it. The tests run through the commit hook `run-tests` and the gate-check step.
- Every handbook page follows [factory-voice.md](../packages/factory/rulebooks/conventions/factory-voice.md). A page repeats a binding rule only in a `> Rule summary:` callout followed by a `> Source:` line (BR-149, acceptance criterion 10).
- A story that writes a page runs `handbook-index` in the same commit, so `handbook-lint` and `handbook-index --check` keep exiting 0 (acceptance criterion 01).
- A story that changes an agent, a skill, or a convention regenerates `packages/factory/INDEX.yaml` in the same commit, and `index-lint --check` passes.
- No story plans deferred scope: a rendered site, rules generated from pages, handbooks for user projects, contributor chapters beyond their stubs, or a change to the playbook concept.

## E1: Look up one task on one handbook page

### Why this EPIC exists

Today a user who wants one task reads an 862-line guide, and an agent that answers one question loads the whole guide into its context. A contributor finds twelve lines in the root `README.md`. This EPIC gives each audience a handbook of short typed pages, keeps the page lists current by script, and moves the content of the three old files there. Without the two scripts and the hook, the page lists would drift the way a hand-kept list does.

### Actor Goals

The goals are the Rule titles of the feature file:

- Contributor sees the page lists of a handbook written by handbook-index (FH-01)
- Contributor learns which page or page list breaks the handbook rules (FH-02)
- Contributor cannot commit a handbook page that breaks the page rules (FH-03)
- User reads the installed user handbook after init-factory or update-factory (FH-04)
- User and contributor find the content of the three deleted files at its new home (FH-05)
- User reaches the user handbook from every factory entry point (FH-06)
- Contributor reaches the contributor handbook from the root README and the agent context (FH-07)

### Demo

1. A contributor adds `docs/handbook/testing/layers.md` with `type: how-to` and `status: implemented`, and runs `packages/factory/scripts/handbook-index`. `docs/handbook/testing/index.md` lists the page under "How-to guides".
2. The contributor removes the `type` line and runs `git commit`. The hook `handbook-lint` names the page and the field `type`, and no commit is created.
3. A user runs `update-factory` in a project with the previous release. `.agent-factory/factory/docs/handbook/index.md` lists the twelve chapters, and `.agent-factory/factory/docs/factory-guide.md` is gone.
4. The user opens `cli-integrations/index.md` of the installed handbook and follows the link "Remove a CLI integration" to a how-to page with the commands.
5. A new user picks H in the session menu. VIRGIL (the agent that guides each session) starts the `newcomer-tour` skill on the `getting-started/` tutorial of the installed handbook.
6. A contributor follows the "Contributing" link of the root `README.md` to the contributor tutorial and gets from `git clone` to a passing test run.
7. `packages/factory/scripts/link-check` over every live document exits 0.

### Scope

**In:**

- `handbook-index [--check]` and `handbook-lint` in `packages/factory/scripts/`, as BR-140 to BR-147 and the interface contracts define them. The hook `handbook-lint` in this repository's `.pre-commit-config.yaml` with `always_run: true` (BR-148). Both handbook roots with an `index.md`, so the hook passes from its first commit.
- The user handbook with its twelve chapters. Each section of the guide moves to the page of the right type, rewritten in the factory voice. The guide rows of the migration map. The tests `test_core_layout_references.py`, `test_brownfield_order.py`, and `test_hook_missing_factory.py` read the handbook pages instead of the guide. The chapter brief of `installation-and-updates/` uses the current path `.agent-factory/factory-user-changes/<timestamp>/` (PROP-05).
- The contributor handbook with nine chapters. `getting-started/` and `contributing/` are written in full, and each other chapter holds an `index.md` and at least one stub that names its sources (DEC-08). The "Contributing" section of the root `README.md` and three concerns of `docs/agent-context.md` route to its pages.
- The entry points of the user: `session-menu.md`, VIRGIL, `newcomer-tour`, `guided-tour`, `explain-concept`, the inputs of VIRGIL in `INDEX.yaml`, and `packages/factory/README.md`.
- The split of `concepts.md` into a `concept` page of the user handbook and a corrected `reference` page of the contributor handbook (DEC-09). The section-map extension of `_link_rewrite.py`: today `rewrite_links` maps one old path to one new path and keeps the anchor, so it cannot send two anchors of one file to two pages (PROP-08). The repointing of the 86 links in 36 files, in live documents and records (DEC-14, BR-150, BR-151). The deletion of the three old files (DEC-07, DEC-10, DEC-13), the comment in `scripts/trigger`, and the `CHANGELOG.md` entry.
- One lector pass over the finished user handbook, with its fixes applied (acceptance criterion 09).

**Out:**

- A check of the links of the installed pages in a user project. PROP-07 stays an open minor without a Scenario (L-15).
- The example step of `core-artifact-layout.feature` that names `docs/arc42/concepts.md`. It describes an example project, so it needs no change (PROP-09, L-15).
- The changes to `newcomer-onboarding.feature`, `opencode-cli-integration.feature`, and `docs/spec/scope-map.md`. The requirements agent made them before planning; no file of `docs/spec/features/` except the handbooks feature names the guide.
- Every item of the proposal's deferral list.

### Dependencies

None. This is the only EPIC of the feature.

### Boundaries

- Scripts: `packages/factory/scripts/` (new `handbook-index`, `handbook-lint`; `_link_rewrite.py`, `link-check`, `trigger`)
- Handbooks: `packages/factory/docs/handbook/`, `docs/handbook/`
- Entry points: `packages/factory/config/session-menu.md`, `packages/factory/agents/virgil.md`, `packages/factory/skills/newcomer-tour/`, `guided-tour/`, `explain-concept/`, `packages/factory/INDEX.yaml`, `packages/factory/README.md`, `README.md`, `docs/agent-context.md`, `docs/README.md`
- Install: `packages/factory/scripts/init-factory` and `update-factory` copy `packages/factory/` whole, so the user handbook installs without a script change. `update-factory` replaces the installed tree through a staging folder, so the deleted guide leaves the installed copy.
- Configuration: `.pre-commit-config.yaml`
- Tests: `tests/factory/` (new `test_handbook_index.py`, `test_handbook_lint.py`, `test_handbook_content.py`, `test_handbook_links.py`, `test_handbook_link_rewrite.py`; `test_precommit_config_contract.py`, `test_update_factory.py`, and the three tests that read the guide)

### Domain Rules

- The folder tree is the navigation. A page joins its chapter's page list on the next run of `handbook-index`, and nobody edits a page list by hand (BR-144, BR-145).
- `handbook-index` writes only between the markers and never changes a byte outside them (BR-143).
- A page describes what the code does today. A page for behaviour that does not exist yet is a stub.
- A binding rule lives only in `rules.md` and the rulebooks (DEC-02, BR-149).
- A file in a record folder changes only in its link destinations (DEC-14, BR-150).
- Guide content goes to the user handbook, because an installed user never sees the contributor handbook (L-42).

### Size

6 stories. The brief expected five to seven. The lector pass is its own story, because it reads pages that ST-0453 and ST-0454 write.

### Building-Block Inventory

| Story   | Capability                                                                     | Tier     | Spawns | Goal                                                                                                                                                                             | Basis                                                                                                                                                                                                                                           |
| ------- | ------------------------------------------------------------------------------ | -------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0452 | Keep the handbook page lists current and block a broken page at commit         | standard | 4      | A contributor runs `handbook-index` to get each page list written, `handbook-lint` to see every broken page and stale list, and a commit with a broken page fails.               | No handbook, no `handbook-*` script, no hook. `finding-lint` shows the hook pattern with `always_run: true`. Adds both scripts, both handbook roots with an `index.md`, the hook, and the tests of FH-01 to FH-03.                              |
| ST-0453 | Read the guide's content as typed pages in the user handbook                   | strong   | 5      | A user opens a chapter of the installed user handbook and finds each topic of the guide on a page of the right type, and the migration map names the page of each guide section. | The guide has 15 sections and 54 headings in one file; three tests read it. Adds the twelve chapters and their pages, the guide rows of the migration map, and moves the three tests to the pages. The guide stays until ST-0454.               |
| ST-0454 | Find the content of the three old files at its new home after they are deleted | strong   | 5      | Every link to the three old files leads to the page that now holds its section, the three files are gone from the source and the installed copy, and `link-check` passes.        | `_link_rewrite.py` maps one path to one path and keeps anchors; `concepts.md` has three sections. Extends the rewrite with a section map, writes the two pages of `concepts.md`, repoints 86 links in 36 files, and deletes the three files.    |
| ST-0455 | Reach the user handbook from every factory entry point                         | standard | 2      | A new user who picks H in the session menu gets the `getting-started/` tutorial, and every other entry point names the user handbook instead of the guide.                       | Six entry-point files and `INDEX.yaml` name `factory-guide.md`; `packages/factory/README.md` holds the guide's topics. Rewrites them to name handbook pages and cuts the package README to install, update, and removal.                        |
| ST-0456 | Get from `git clone` to a passing test run with the contributor handbook       | standard | 3      | A contributor follows the root `README.md` to the contributor tutorial and reaches a passing test run, and the agent context routes three concerns to contributor pages.         | `README.md` "Contributing" holds twelve lines; `docs/agent-context.md` has no handbook concern. Adds nine chapters, writes `getting-started/` and `contributing/` in full, adds a stub per other chapter, and repoints the README and concerns. |
| ST-0457 | Read the user handbook in the factory voice after one lector pass              | standard | 2      | The lector agent's report on the finished user handbook exists, and each fix it lists is applied.                                                                                | No lector report on the handbook exists. Runs the lector agent once on `packages/factory/docs/handbook/` and applies its fixes.                                                                                                                 |

### Testability Assessment

FH-01 to FH-04 produce observable outcomes at script boundaries: the exit code and report of `handbook-index` and `handbook-lint`, the bytes of each `index.md`, the result of a real `git commit`, and the file tree after `init-factory` and `update-factory`. Integration tests run the scripts as subprocesses on temporary handbook folders; contract tests load the functions with `load_script`. FH-05 to FH-07 are text checks over the repository and `link-check` runs over a temporary install. Three goals have red flags that the specification already handles by a review step instead of a test: the completeness of each moved section (acceptance criterion 12, SPEC-0172), the absence of binding rules in prose (DEC-12), and the lector pass (acceptance criterion 09). The fresh-clone run of the contributor tutorial is a manual step of its author, recorded in ST-0456 (L-20).

### Ownership Resolution

| Contract                                                                                                         | .feature Rule                                                                                                     | Owner   | Rationale                                             |
| ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------- | ----------------------------------------------------- |
| FH-01-IT-01 to FH-01-IT-04 and the `test_handbook_index.py` contract tests: grouped lists, stubs, refusal, tops  | factory-handbooks.feature#Contributor sees the page lists of a handbook written by handbook-index                 | ST-0452 | introduces `handbook-index`                           |
| FH-02-IT-01 to FH-02-IT-03 and the `test_handbook_lint.py` contract tests: `--check` and every failure kind      | factory-handbooks.feature#Contributor learns which page or page list breaks the handbook rules                    | ST-0452 | introduces `handbook-lint` and `--check`              |
| FH-03-IT-01 and the `test_precommit_config_contract.py` cases: the hook fails a commit, no hook in user projects | factory-handbooks.feature#Contributor cannot commit a handbook page that breaks the page rules                    | ST-0452 | introduces the hook                                   |
| FH-04-IT-01: the installed handbook equals the source, the guide and the contributor handbook are absent         | factory-handbooks.feature#User reads the installed user handbook after init-factory or update-factory             | ST-0454 | first story after which the installed guide is absent |
| FH-05-IT-01: every section of the three old files has a map row with an existing page                            | factory-handbooks.feature#User and contributor find the content of the three deleted files at its new home        | ST-0454 | writes the last map rows and the pages they name      |
| FH-05-IT-02 and the `test_handbook_link_rewrite.py` contract tests: every link repointed, records keep wording   | factory-handbooks.feature#User and contributor find the content of the three deleted files at its new home        | ST-0454 | introduces the section-map rewrite                    |
| FH-05-LN-01: the three files and archive copies are gone, the search finds nothing                               | factory-handbooks.feature#User and contributor find the content of the three deleted files at its new home        | ST-0454 | deletes the three files                               |
| FH-06-LN-01: session menu H, the tour skills, and the other entry points name the handbook                       | factory-handbooks.feature#User reaches the user handbook from every factory entry point                           | ST-0455 | rewrites the entry points                             |
| FH-07-LN-01: the root README and the agent context route to contributor pages                                    | factory-handbooks.feature#Contributor reaches the contributor handbook from the root README and the agent context | ST-0456 | writes the contributor pages and the routes           |

FH-04-IT-01 could be written after ST-0453, because the user handbook installs from then on. Its Scenario also requires the absence of the installed guide, so its owner is ST-0454. The QA strategy places FH-05-LN-01, FH-06-LN-01, and FH-07-LN-01 in one file, `test_handbook_content.py`. The first of these stories to merge creates the file, and the others add to it. The waves keep the three stories apart, so they never edit the file at the same time.
