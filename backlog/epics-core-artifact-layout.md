---
scope: global
---

# EPICs — Core Artifact Layout

Proposal trace: [core-artifact-layout.md](../docs/proposals/core-artifact-layout.md)
Specification trace: [core-artifact-layout.feature](../docs/spec/features/core-artifact-layout.feature), [gaps report](../docs/spec/work/core-artifact-layout-gaps.md), [interface-contracts.md](../docs/spec/interface-contracts.md)
Architecture trace: [ADR-0025](../docs/adr/0025-core-artifact-layout-under-docs-spec.md), [ADR-0026](../docs/adr/0026-layout-migration-runs-inside-the-factory-update.md)
QA strategy trace: [core-artifact-layout-qa-strategy.md](../docs/spec/work/core-artifact-layout-qa-strategy.md)

Dependency order: {E1, E3, E4, E7, E8} start in parallel; E1 → E2; {E1, E3} → E5; {E1, E2, E3} → E6; E1 to E8 → E9. E9 comes last. Before ST-0343 commits, the factory maintainer reinstalls the factory from `packages/factory/` with `update-factory`, so the agents and the factory hook block of this repository read the new paths. ST-0343 states this as its human touchpoint.

The layout release is `1.4.0` (CAL-G02). The first story ID is `ST-0318`.

## Terms used in every EPIC

- **Old layout and new layout.** The old layout spreads the specification core over `docs/spec/`, `docs/spec/supplementary_specs/`, `docs/arc42/`, and `docs/`. The new layout keeps every core file in `docs/spec/`, with the folders `features/`, `schemas/`, `areas/`, and `work/`.
- **Path table.** The table in the proposal's [§ Path table](../docs/proposals/core-artifact-layout.md#path-table) that maps every old path to its new path, or marks it as removed.
- **Working output.** Files agents write while they derive or review the core: gaps reports, QA strategies, `prd.md`, update summaries, and the two todo lists. They move to `docs/spec/work/`.
- **Factory hook block.** The `agent_factory_hook-*` entries of a project's `.pre-commit-config.yaml`. The factory owns them; the project owns every other hook.

## Rules that hold for every EPIC

- Pre-alpha: the layout release supports updates only from an installed `update-factory` `v1.1.0-rc` or later. No story adds handling for older updaters or for `.agent-factory/factory-install.json` (ADR-0026).
- No script reads both layouts (DEC-11). A script that moves to the new path drops the old path.
- No story plans DBML or its gates, a blocking glossary gate, or the merge of `todo.md` and `todos.md` (T-0008). The proposal defers all three.
- Source edits go to `packages/factory/`, never to `.agent-factory/factory/`.
- Until E9 switches them, the repository's own local hooks in `.pre-commit-config.yaml` keep passing the old paths explicitly, so this repository's commits stay green while it is still in the old layout.
- Each story removes the old paths from the files it touches. Gap CAL-G08 takes the file list from the greps of the Completion Criteria. The story slicing assigns each file to one story, and each story names its files under Affected Paths.

## E1: Move a project into the new layout with its history and links kept

### Why this EPIC exists

No project can reach the new layout without a tool that moves its files. A hand move loses git history, breaks links, and differs from project to project. The script `migrate-spec-layout` makes the move mechanical and the same everywhere, and every later EPIC that touches an installed project builds on it.

### Actor Goals

- Project maintainer previews the layout migration without changes.
- Project maintainer moves the project into the new layout with its history kept.
- Project maintainer keeps every Markdown link working after the move.
- Project maintainer learns every old path that the script does not rewrite.

### Demo

1. Copy an old-layout project fixture into a temporary Git repository with a clean `git status`.
2. Run `migrate-spec-layout --dry-run`. The terminal lists every planned move and every planned link rewrite. `git status` still shows no change.
3. Run `migrate-spec-layout`. The script exits 0.
4. Run `git status`. It shows `docs/spec/payments.feature` renamed to `docs/spec/features/payments.feature` and `docs/spec/payments-gaps.md` renamed to `docs/spec/work/payments-gaps.md`.
5. Run `link-check` on every Markdown file under `docs/`. It passes.
6. Read the end of the script's output. It names `.github/workflows/docs.yml`, its line, and the old path `docs/arc42/architecture.dsl`. The workflow file is unchanged.
7. Run `pre-commit run --files docs/spec/architecture.dsl`. Pre-commit runs `arch-lint`, because the factory hook block now carries the template's `files:` value.

### Scope

**In:**

- A new script `packages/factory/scripts/migrate-spec-layout`. It plans every move of the path table, checks the repository, and then applies the plan. `migrate-layout` shows the shape: a Python script with `[--dry-run] [TARGET]`.
- Repository check before the first change. During a merge, a rebase, or a held index lock the script changes nothing, names the state, and exits non-zero (CAL-G18).
- Moves by git state (the state git reports for one file: tracked, untracked, or ignored). A tracked file moves with `git mv`, also with uncommitted changes. An untracked or ignored file moves with a plain file move.
- Removal of `actor-goal-list.md` and every `use_cases/` folder under `docs/`, `docs/~archive/` included, with `git rm`. A file in that set that is untracked, ignored, or tracked with uncommitted changes stays and is listed for the developer to delete (CAL-G17).
- The Structurizr theme move from `docs/arc42/themes/` to `docs/assets/themes/`, and the DSL's `theme` line set to `theme ../assets/themes/default/theme.json`. The first story checks that Structurizr accepts this path (CAL-G06).
- Link rewrite: each local Markdown link to an old path points at the new path; each relative link inside a moved file resolves from the new folder; each link to a removed file becomes its link text in a code span.
- The factory hook block takes the `files:` value of each hook from the new hook template, without a question.
- A listing of each old path the script does not rewrite: file, line, and old path. The project's own hooks and CI files stay unchanged.
- Self-undo: when a step fails partway, the script undoes every move, removal, and content edit it made, then exits non-zero. A file that moved with a plain move moves back with a plain move.
- No work: on a project without old paths the script moves nothing, prints nothing, and exits 0.
- Decisions the contract leaves open and the E1 stories fix: the project directory argument and how `init-factory` passes it (CAL-G10), exit codes and what `--dry-run` prints (CAL-G12), the files the script scans for links and old paths (CAL-G11), and the format and stream of the old-path listing (CAL-G05). Each story records its values in `interface-contracts.md`.

**Out:**

- The glossary step of the script (E2).
- The call of the script from `init-factory` during an update (E5).
- The fold of `CONTEXT-MAP.md` and routing-only `CONTEXT.md` files (E4). The script leaves both in place.
- Rewriting an old path outside a Markdown link. The factory hook block and the DSL `theme` line are the only exceptions.

### Dependencies

None at the EPIC level. The hook-block story needs the new hook template from E3 (ST-0325) for its demo.

### Boundaries

- Script: `packages/factory/scripts/migrate-spec-layout` (new)
- Gate used in the demo: `packages/factory/scripts/link-check` (unchanged)
- Input: the factory hook template `packages/factory/config/pre-commit-config.yaml`
- Output: the project's working tree and git index, the project's `.pre-commit-config.yaml`, terminal output
- Contract: [interface-contracts.md § migrate-spec-layout](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptsmigrate-spec-layout)
- Tests: `tests/factory/test_migrate_spec_layout.py` (new)

### Domain Rules

- The git state of a file never stops the migration. Only the state of the repository does: merge, rebase, or a held index lock.
- The script never runs `git rm -f` and never deletes a file with a plain removal.
- The script never commits.
- The script rewrites only Markdown links, the factory hook block, and the DSL `theme` line. Every other old path is listed, never changed.
- A failed run leaves `git status` as it was before the run.
- `CONTEXT-MAP.md` and a routing-only `CONTEXT.md` never count as work for the script.

### Size

5 stories.

### Building-Block Inventory

| Story   | Capability                                                                 | Tier     | Size | Goal                                                                                                                                                                                                                 | Basis                                                                                                                                        |
| ------- | -------------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0318 | Move a project's files into the new layout with their git history kept     | strong   | L    | The project maintainer runs `migrate-spec-layout` and finds every file of the path table at its new path, recorded by git as a rename where git tracks it; `--dry-run` prints the planned moves and changes nothing. | No script exists. `migrate-layout` gives the argument shape. Adds the script, its moves, theme move, repository check, self-undo, and tests. |
| ST-0319 | Remove the actor-goal list and the use-case files, also from the archive   | strong   | M    | The project maintainer runs the script and git records `actor-goal-list.md` and every `use_cases/` file as removed; a file git cannot remove safely stays and is listed.                                             | Extends ST-0318's plan with the removal set.                                                                                                 |
| ST-0320 | Keep every Markdown link working after the move                            | standard | M    | After the script runs, `link-check` passes on every Markdown file under `docs/`, and `--dry-run` also prints each planned link rewrite.                                                                              | `link-check` exists. Adds the link rewrite, rebasing, and code spans to the script.                                                          |
| ST-0321 | List every old path the script does not rewrite                            | standard | M    | The project maintainer reads each old path outside a Markdown link, with its file and line, at the end of the script's output; the listed files are unchanged.                                                       | Adds the scan of non-Markdown files and the listing format.                                                                                  |
| ST-0322 | Bring the factory hook block to the new hook template during the migration | strong   | M    | After the script runs, `pre-commit run --files docs/spec/architecture.dsl` runs `arch-lint`, and a failure after the hook rewrite leaves `.pre-commit-config.yaml` and every other file as before.                   | Reads the template E3 changes. Adds the hook-block rewrite and extends self-undo to every content edit.                                      |

### Testability Assessment

All actor goals produce observable results on a temporary Git repository: file paths, `git status` rename and removal entries, the script's exit code, its terminal output, and `link-check`'s exit code. Tests instrument the script as a subprocess on fixture repositories built in `tmp_path`, and the pure planning steps (path table, link rebasing) as contract tests. One red flag: the theme check needs `structurizr validate`, which runs only in the container suite (CAL-G09). The test carries the `container` marker, and the story runs it once by hand before it relies on the theme path (CAL-G06).

### Ownership Resolution

| Contract                                                                                      | .feature Rule                                                                                               | Owner   | Rationale                                                                        |
| --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------- | -------------------------------------------------------------------------------- |
| CAL-03-CT-01: each old path of the path table maps to its new path                            | core-artifact-layout.feature#Project maintainer moves the project into the new layout with its history kept | ST-0318 | introduces the path-table planner                                                |
| CAL-03-IT-02: the theme moves and `structurizr validate` accepts the moved DSL                | core-artifact-layout.feature#Project maintainer moves the project into the new layout with its history kept | ST-0318 | introduces the theme move and the `theme` line                                   |
| CAL-03-IT-03: a project in the new layout gives the script no work                            | core-artifact-layout.feature#Project maintainer moves the project into the new layout with its history kept | ST-0318 | introduces the no-work detection                                                 |
| CAL-03-IT-05: tracked files move with `git mv`, untracked and ignored files with a plain move | core-artifact-layout.feature#Project maintainer moves the project into the new layout with its history kept | ST-0318 | introduces the moves by git state                                                |
| CAL-03-IT-01: moves are renames, removals are git removals, the rest of the archive stays     | core-artifact-layout.feature#Project maintainer moves the project into the new layout with its history kept | ST-0319 | first story in which both renames and removals exist                             |
| CAL-03-IT-06: unsafe removals stay and are listed; a busy repository is refused               | core-artifact-layout.feature#Project maintainer moves the project into the new layout with its history kept | ST-0319 | the refusal exists from ST-0318; the removal half arrives here                   |
| CAL-04-CT-01: links are rewritten, rebased, and turned into code spans                        | core-artifact-layout.feature#Project maintainer keeps every Markdown link working after the move            | ST-0320 | introduces the link rewrite                                                      |
| CAL-04-IT-01: `link-check` passes on a migrated copy                                          | core-artifact-layout.feature#Project maintainer keeps every Markdown link working after the move            | ST-0320 | introduces the link rewrite                                                      |
| CAL-02-IT-01: `--dry-run` prints every planned move and rewrite and changes nothing           | core-artifact-layout.feature#Project maintainer previews the layout migration without changes               | ST-0320 | first story in which the dry run prints both moves and link rewrites             |
| CAL-05-IT-01: old paths outside Markdown and in the project's own hooks are listed, unchanged | core-artifact-layout.feature#Project maintainer learns every old path that the script does not rewrite      | ST-0321 | introduces the old-path listing                                                  |
| CAL-03-IT-04: a failure partway undoes every change, `git status` shows no change             | core-artifact-layout.feature#Project maintainer moves the project into the new layout with its history kept | ST-0322 | first story in which moves, a link rewrite, and the hook-block rewrite all exist |

## E2: Get one glossary from chapter 12 and from every vocabulary file

### Why this EPIC exists

Today the domain terms live in chapter 12 (`docs/arc42/12_glossary.md`, the arc42 glossary chapter) and in any `CONTEXT.md` that has a `## Language` section. Agents and people look in two places and find two answers. This EPIC adds the glossary step to `migrate-spec-layout`, so every migrated project gets one `docs/spec/glossary.md` in one table form, and no definition is lost on the way.

### Actor Goals

- Project maintainer gets one glossary from chapter 12 and from every vocabulary file.

### Demo

1. Take an old-layout project whose chapter 12 has the section "Usage Analysis Vocabulary" with a two-column table and a section "Referenced from" with a list of links. Its `docs/CONTEXT.md` has the title "Billing" and a `## Language` section that defines "Invoice". Chapter 12 also defines "Invoice".
2. Run `migrate-spec-layout`. It exits 0.
3. Open `docs/spec/glossary.md`. It has the sections "Usage Analysis Vocabulary" and "Billing", each a table with the columns Term, Definition, and Avoid.
4. Open `docs/arc42/12_glossary.md`. It starts with one line that links to `docs/spec/glossary.md`, followed by the section "Referenced from".
5. Read the script's output. It lists "Invoice" as a term in more than one section and names `capture-context --fold-context-map` and the cleanup of duplicate terms as the two follow-up steps.
6. Open `docs/CONTEXT.md`. It has no `## Language` section.

### Scope

**In:**

- Glossary conversion of chapter 12: each section with a two-column table moves into `docs/spec/glossary.md` under its heading. A table directly under the chapter title becomes the section "Terms". The columns become Term and Definition, and an empty Avoid column is added. A section without a table stays in chapter 12, below the new link line.
- A new chapter 12 at the old path, so git shows `docs/spec/glossary.md` as added and chapter 12 as modified, and `git log` on chapter 12 keeps its earlier commits (SPEC-0024).
- Term extraction from every `CONTEXT.md` with a `## Language` section, a per-context `CONTEXT.md` that a context map lists included. The template's list form (`**Term**:` with a definition and `_Avoid_:`) becomes table rows. The section takes the file's title. The script then removes the `## Language` section.
- The listing of each term that appears in more than one section, and the two follow-up steps at the end of the output.
- The no-work rule extended: chapter 12 counts as work while it holds a two-column table, and a `CONTEXT.md` counts while it has a `## Language` section.
- Self-undo extended to the new glossary, the new chapter 12, and every removed `## Language` section.
- Whether the script stages the new `glossary.md` and chapter 12 (M-05).

**Out:**

- Cleaning up duplicate terms. That is a follow-up step for the developer, for example with `domain-modeling` (DEC-18).
- The glossary as chapter 12 of the PDF (E6).
- The table form that `domain-modeling` writes later (E8).

### Dependencies

E1 (the glossary step runs inside `migrate-spec-layout`).

### Boundaries

- Script: `packages/factory/scripts/migrate-spec-layout` (extend)
- Input: `docs/arc42/12_glossary.md`, every `CONTEXT.md`, `docs/arc42/CONTEXT-MAP.md` as the list of per-context files
- Output: `docs/spec/glossary.md` (new), `docs/arc42/12_glossary.md`, trimmed `CONTEXT.md` files, terminal output
- Entity: [entity-model.md § Glossary Entities](../docs/spec/entity-model.md#glossary-entities)
- Tests: `tests/factory/test_migrate_spec_layout.py` (extend)

### Domain Rules

- Two vocabularies never stop the script. It keeps both in separate sections, lists the duplicates, and exits 0 (DEC-18).
- Every glossary section is one table with the columns Term, Definition, and Avoid (DEC-12).
- A `CONTEXT.md` without a `## Language` section holds routing only and stays unchanged.
- No definition of chapter 12 or of a `CONTEXT.md` is dropped.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                | Tier     | Size | Goal                                                                                                                                                                                                 | Basis                                                                                             |
| ------- | --------------------------------------------------------- | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| ST-0323 | Turn chapter 12 into the glossary file and a link line    | standard | M    | After the script runs, `docs/spec/glossary.md` holds every chapter 12 table as a Term/Definition/Avoid section, and chapter 12 starts with a link to it, with its history kept.                      | `_docs_assemble.py` and the script know nothing of `glossary.md`. Adds the chapter 12 conversion. |
| ST-0324 | Move the terms of every vocabulary file into the glossary | standard | M    | After the script runs, each `CONTEXT.md` term is a row in its own glossary section, no `CONTEXT.md` keeps a `## Language` section, and the output lists duplicate terms and the two follow-up steps. | Builds on ST-0323's glossary writer. Adds the list-form conversion.                               |

### Testability Assessment

All actor goals produce observable results: the content of `docs/spec/glossary.md` and chapter 12, `git status` and `git log` entries, the absence of `## Language` sections, the exit code, and the duplicate listing. Tests instrument the table conversion as contract tests on Markdown strings and the whole step as integration tests on temporary Git repositories. No red flags.

### Ownership Resolution

| Contract                                                                                             | .feature Rule                                                                                                    | Owner   | Rationale                                         |
| ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------- |
| CAL-06-CT-01: chapter 12 converts into Term/Definition/Avoid sections; sections without a table stay | core-artifact-layout.feature#Project maintainer gets one glossary from chapter 12 and from every vocabulary file | ST-0323 | introduces the chapter 12 conversion              |
| CAL-06-IT-02: git shows the glossary as added and chapter 12 as modified, with its history           | core-artifact-layout.feature#Project maintainer gets one glossary from chapter 12 and from every vocabulary file | ST-0323 | introduces the new chapter 12 at the old path     |
| CAL-06-CT-02: the list form of a `CONTEXT.md` converts into rows and `## Language` is removed        | core-artifact-layout.feature#Project maintainer gets one glossary from chapter 12 and from every vocabulary file | ST-0324 | introduces the `CONTEXT.md` conversion            |
| CAL-06-IT-01: two vocabularies give separate sections, a duplicate list, and exit 0                  | core-artifact-layout.feature#Project maintainer gets one glossary from chapter 12 and from every vocabulary file | ST-0324 | first story with two vocabularies in one glossary |

## E3: Run every gate against a project in the new layout

### Why this EPIC exists

A gate that looks only at the old path passes silently on a migrated project, because it finds no file to check. That is the second risk of the feature after a damaged migration. This EPIC moves each gate to the new paths and gives each one a test that seeds an error at the new path. It also makes `spec-lint` read the glossary table and drops its use-case checks.

### Actor Goals

- Project maintainer's gates check the core at its new paths.
- Project maintainer checks glossary terms and business rules without use-case files.

### Demo

1. Take a project fixture in the new layout.
2. Put a deliberate error that `statemachine-lint` reports into `docs/spec/state-machines.md` and run the gate. It exits non-zero.
3. Break a relation in `docs/spec/architecture.dsl` and run `arch-lint`. It exits non-zero and reads chapter 5 from `docs/arc42/`.
4. Reference `BR-099` in `docs/spec/features/payments.feature` without defining it, and run `spec-lint`. It reports `TRACE002` as an error and exits 1.
5. Define "Settlement" in the table of `docs/spec/glossary.md` and use it only in `docs/spec/work/payments-gaps.md`. Run `spec-lint`. It reports `GLOSS001` as info for "Settlement".
6. In a project installed from the new hook template, run `pre-commit run --files docs/spec/architecture.dsl`. Pre-commit runs `arch-lint`.

### Scope

**In:**

- `arch-lint` reads the DSL from `docs/spec/` and chapter 5 from `docs/arc42/`, with new arguments or defaults (CAL-G16).
- `structurizr` reads `architecture.dsl` from `docs/spec/`.
- `dependency-check` defaults to `docs/spec/dependency-rules.dsl`.
- `scope-lint` reads feature files from `docs/spec/features/`. `statemachine-lint` reads `docs/spec/state-machines.md`. `link-check` checks `docs/spec/work/`.
- `spec-lint` reads its terms from the table of `docs/spec/glossary.md`. `GLOSS001` does not count `glossary.md` itself or files in `work/` as uses, and counts a use in a feature file. `TRACE002` stays an error whether or not `use_cases/` exists. The four use-case checks go (DEC-10).
- The hook template `config/pre-commit-config.yaml` and `config/hook-metadata.yaml` take the new `files:` pattern of the `arch-lint` hook: `^docs/(spec/(architecture|dependency-rules)\.dsl|arc42/05_building_block_view\.md|assets/images/.*|adr/.*\.md)$`.
- One seeded-error test per gate at its new path (`tests/factory/test_core_layout_gates.py`, new).
- Each story records the new arguments and defaults in `interface-contracts.md` (CAL-G16).
- The repository's own local hooks in `.pre-commit-config.yaml` keep passing the old paths explicitly until E9.

**Out:**

- `publish-docs` (E6).
- Running the gates on the factory's own migrated repository (E9).
- A blocking glossary gate. `GLOSS001` stays info.

### Dependencies

None. Each gate is shown on a fixture in the new layout.

### Boundaries

- Scripts: `arch-lint`, `structurizr`, `dependency-check`, `scope-lint`, `statemachine-lint`, `spec-lint`, `link-check` in `packages/factory/scripts/`
- Config: `packages/factory/config/pre-commit-config.yaml`, `packages/factory/config/hook-metadata.yaml`, the repository's `.pre-commit-config.yaml`
- Contract: [interface-contracts.md](../docs/spec/interface-contracts.md), one section per gate
- Tests: `test_arch_lint.py`, `test_scope_lint.py`, `test_spec_lint.py`, `test_precommit_config_contract.py`, and `test_core_layout_gates.py` (new) in `tests/factory/`

### Domain Rules

- A gate reads the new path only. It never falls back to the old path (DEC-11).
- A gate whose input file is missing at the new path does not pass silently on a seeded error.
- `TRACE002` is an error, with or without `use_cases/`.
- `GLOSS001` is info. Only core files outside `work/`, other than `glossary.md` itself, count as uses.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                     | Tier     | Size | Goal                                                                                                                                                                                                | Basis                                                                                                                                                        |
| ------- | ------------------------------------------------------------------------------ | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ST-0325 | Run the architecture gates against the DSL in `docs/spec/`                     | standard | L    | `arch-lint`, `structurizr validate`, and `dependency-check` each fail on a seeded error in the DSL at `docs/spec/`, and a DSL change triggers `arch-lint` in a project installed from the template. | All three read `docs/arc42/` today; no test exists for `structurizr` or `dependency-check`. Adds new defaults, the template pattern, and the gate test file. |
| ST-0326 | Run `scope-lint`, `statemachine-lint`, and `link-check` against the new layout | standard | S    | Each of the three gates fails on a seeded error at its new path: `features/`, `state-machines.md`, and `work/todo.md`.                                                                              | `scope-lint` globs `docs/spec/*.feature`; `statemachine-lint` scans `--spec-dir`; no test exists for `statemachine-lint`.                                    |
| ST-0327 | Check glossary terms and business rules without use-case files                 | standard | M    | `spec-lint` reports `GLOSS001` from the glossary table, blocks an undefined business rule with `TRACE002`, fails on a seeded error in `validation-rules.md`, and runs no use-case check.            | `check_glossary` reads `CONTEXT.md`; `TRACE002` drops to a warning without `use_cases/`; four use-case checks run.                                           |

### Testability Assessment

All actor goals produce exit codes and findings on the terminal, which tests assert on fixture projects in the new layout. Tests instrument each gate as a subprocess and `spec-lint`'s checks as contract tests. One red flag: `structurizr validate` needs Docker, so its row of the seeded-error test runs only with the `container` marker (CAL-G09). The other six gates run in the default suite.

### Ownership Resolution

| Contract                                                                                 | .feature Rule                                                                                                   | Owner   | Rationale                                                                |
| ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------ |
| CAL-09-IT-01: each of the seven gates exits non-zero on a seeded error at the new path   | core-artifact-layout.feature#Project maintainer's gates check the core at its new paths                         | ST-0325 | creates the seeded-error test; ST-0326 and ST-0327 add their gates' rows |
| CAL-09-IT-02: a DSL change runs `arch-lint` as a hook                                    | core-artifact-layout.feature#Project maintainer's gates check the core at its new paths                         | ST-0325 | introduces the template pattern; ST-0343 checks the factory row          |
| CAL-10-CT-01: `GLOSS001` reads table terms and ignores `glossary.md` and `work/` as uses | core-artifact-layout.feature#Project maintainer checks glossary terms and business rules without use-case files | ST-0327 | introduces the glossary-table read                                       |
| CAL-10-CT-02: `TRACE002` is an error without `use_cases/`; no use-case check runs        | core-artifact-layout.feature#Project maintainer checks glossary terms and business rules without use-case files | ST-0327 | removes the downgrade and the use-case checks                            |

## E4: Fold context routing into the agent context file

### Why this EPIC exists

Two files route agents today: `docs/agent-context.md` and the context map `docs/arc42/CONTEXT-MAP.md`, plus any `CONTEXT.md` that holds routing only. The migration script leaves them in place, because turning a context into a routing entry needs judgment. This EPIC gives the developer the skill mode that does that fold, so `docs/agent-context.md` becomes the one routing file and the old files can go.

### Actor Goals

- Project maintainer folds context routing into the agent context file.

### Demo

1. Take a project whose `docs/arc42/CONTEXT-MAP.md` lists three contexts and whose `docs/arc42/concepts.md` links to `CONTEXT-MAP.md`.
2. Run `capture-context --fold-context-map`. The skill shows three new domain concerns (sections of `docs/agent-context.md` that route agents to the files of one context), each marked as folded.
3. Run `concern-lint`. It passes.
4. Open `docs/arc42/concepts.md`. Its link points at `docs/agent-context.md`.
5. Delete `docs/CONTEXT.md` and `docs/arc42/CONTEXT-MAP.md`, then run `link-check`. It passes.
6. Run `capture-context --update --scan`. The rescan offers no removal of a folded concern.

### Scope

**In:**

- A new mode `--fold-context-map` of the `capture-context` skill. It reads the context map and every routing-only `CONTEXT.md`, writes one domain concern per context with its description and `Read:` paths, routes the concerns to `docs/spec/glossary.md`, and marks each as folded.
- The form of the folded mark and its `concern-lint` check (CAL-G03).
- The mode's behaviour without `docs/agent-context.md`, and whether the developer confirms before or after the write (CAL-G14).
- The link rewrite: every Markdown link under `docs/` to a `CONTEXT.md` or to `CONTEXT-MAP.md` points at `docs/agent-context.md`.
- `capture-context --update --scan` keeps every concern marked as folded, also when it is not a scope-map area.
- The template `rulebooks/templates/context-map.md` goes.

**Out:**

- Deleting the old files. The developer deletes them after the review.
- The fold on the factory's own repository (E9).
- Moving terms out of `CONTEXT.md` (E2).

### Dependencies

None. The fold reads `CONTEXT-MAP.md`, which the script leaves in place.

### Boundaries

- Skill: `packages/factory/skills/capture-context/SKILL.md` (new mode, rescan change)
- Script: `packages/factory/scripts/concern-lint` (check of the folded mark)
- Template: `packages/factory/rulebooks/templates/context-map.md` (removed)
- Output: `docs/agent-context.md`, rewritten links under `docs/`
- Contract: [interface-contracts.md § capture-context --fold-context-map](../docs/spec/interface-contracts.md#capture-context---fold-context-map), [entity-model.md § Agent Context Entities](../docs/spec/entity-model.md#agent-context-entities)
- Tests: `test_capture_context_fold.py` (new), `test_concern_lint.py`, `test_capture_context_update.py`, `test_value_first_routing.py` in `tests/factory/`

### Domain Rules

- `docs/agent-context.md` is the project's one routing file (DEC-07).
- The fold never deletes `CONTEXT-MAP.md` or a `CONTEXT.md`.
- Every `Read:` path of a folded concern passes `concern-lint` `CTX-PATHS`.
- A rescan never offers to remove a folded concern.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                       | Tier     | Size | Goal                                                                                                                                                                                               | Basis                                                                                                                        |
| ------- | ------------------------------------------------ | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| ST-0328 | Fold the context map into the agent context file | standard | M    | The project maintainer runs `capture-context --fold-context-map` and gets one folded domain concern per listed context, links that point at `docs/agent-context.md`, and a passing `concern-lint`. | `capture-context` has `--init`, `--init --scan`, `--update --scan`; `concern-lint` exists. Adds the mode and the mark check. |
| ST-0329 | Keep folded concerns through a rescan            | standard | S    | The project maintainer runs `capture-context --update --scan` on a folded project and keeps every folded concern; the rescan offers no removal of one.                                             | `--update --scan` offers to remove every domain concern that is not a scope-map area.                                        |

### Testability Assessment

The fold is a skill that an agent runs, so its result on an arbitrary project is not machine-checked. That is a red flag. The retained test checks the skill text (the mode, the mark, the link rewrite, the rescan rule) as a deterministic text check. `concern-lint` checks the folded mark mechanically, and its test seeds a concern with and without a valid mark. The full fold runs once, on the factory's own repository, as an acceptance check (CAL-08-AC-01).

### Ownership Resolution

| Contract                                                                                              | .feature Rule                                                                                     | Owner   | Rationale                                              |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------ |
| CAL-08-LN-01: `capture-context` defines the fold, the mark, the link rewrite, and the rescan rule     | core-artifact-layout.feature#Project maintainer folds context routing into the agent context file | ST-0328 | introduces the mode; ST-0329 adds the rescan assertion |
| CAL-08-AC-01: the fold of the factory's routing passes `concern-lint` and `link-check` after deletion | core-artifact-layout.feature#Project maintainer folds context routing into the agent context file | ST-0344 | the first real fold runs on the factory's repository   |

## E5: Receive the new layout with an approved factory update

### Why this EPIC exists

Installed projects move only when someone runs the migration. If the developer had to run it by hand, projects would stay on the old layout while their new scripts read the new paths. This EPIC makes the update do the move: `init-factory` runs `migrate-spec-layout` as its last step when the installed version is older than the layout release, and a failed migration rolls the whole update back (ADR-0026).

### Actor Goals

- Project maintainer receives the new layout with the factory update.

### Demo

1. Take an old-layout project whose `.agent-factory/install.json` records `factory_version` `1.3.3`.
2. Run `update-factory` and approve the update once. The output asks nothing about the move or the hooks.
3. List `docs/spec/`. The project is in the new layout. `.agent-factory/install.json` records `1.4.0`.
4. Run `init-factory` again. No file moves.
5. Restore the old project, make `migrate-spec-layout` fail partway, and run the update again. Every project file and `.pre-commit-config.yaml` have their old content, the factory tree is the old one, `install.json` records `1.3.3`, and `update-factory` reports the failure.

### Scope

**In:**

- The layout release constant `1.4.0` in `init-factory` (CAL-G02).
- The version test by Semantic Versioning 2.0.0 precedence. A missing `factory_version`, `unknown`, or a value that does not parse counts as older. Only a missing `install.json` is a first install.
- `init-factory` runs `migrate-spec-layout` as its last step on an update, with the project directory argument of CAL-G10.
- The new `factory_version` is written only after the migration succeeds. A failed migration keeps the prior version; `init-factory` reports the old layout, names the fix (run the update again), and exits non-zero.
- A first install moves nothing, lists each old path it finds, and names `migrate-spec-layout` as a command the developer can run. A rerun at the same or a newer version moves nothing.
- `update-factory` rolls back the factory tree on the failed `init-factory`, so project files, `.pre-commit-config.yaml`, factory tree, and version are all as before.
- During an update, each factory hook takes the `files:` value of the new template without a question. `merge-precommit-config` names no old path.

**Out:**

- Updaters before `v1.1.0-rc` and `.agent-factory/factory-install.json` (pre-alpha decision).
- Release notes and the release itself.

### Dependencies

E1 (the update runs the script), E3 (the hook scenario needs the new template pattern and `arch-lint` at the new path).

### Boundaries

- Scripts: `packages/factory/scripts/init-factory`, `update-factory`, `merge-precommit-config`
- Script called: `packages/factory/scripts/migrate-spec-layout`
- Output: `.agent-factory/install.json`, the project's files and `.pre-commit-config.yaml`, terminal output
- Contract: [interface-contracts.md § init-factory](../docs/spec/interface-contracts.md#factoryscriptsinit-factory) and § `update-factory`
- Tests: `test_init_factory.py`, `test_update_factory.py`, `test_merge_precommit_config.py` in `tests/factory/`

### Domain Rules

- The developer approves the update, not the move (DEC-17). Declining the update means no move.
- `init-factory` leaves the project's own files alone on a first install and on a rerun.
- `install.json` never records the new version while the project is still in the old layout.
- Version comparison follows Semantic Versioning 2.0.0 precedence, never string order.

### Size

4 stories.

### Building-Block Inventory

| Story   | Capability                                                         | Tier     | Size | Goal                                                                                                                                                                                                | Basis                                                                                                            |
| ------- | ------------------------------------------------------------------ | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| ST-0330 | Receive the new layout with an approved update                     | standard | L    | The project maintainer approves an update from `1.3.3` and finds the project in the new layout with `1.4.0` in `install.json`; a failed migration keeps `1.3.3` and names the fix.                  | `load_prior_manifest` reads the prior record; no version test and no migration call exist. Adds both.            |
| ST-0331 | Install the factory on an old-layout project without moving a file | standard | S    | The project maintainer installs the factory on an old-layout project and reads the list of old paths and the command `migrate-spec-layout`; no file moves, also on a rerun.                         | Extends ST-0330's version test with the first-install branch.                                                    |
| ST-0332 | See a failed migration roll the whole update back                  | standard | M    | When the migration fails during an approved update, the project maintainer finds every project file, `.pre-commit-config.yaml`, the factory tree, and the version as before, and reads the failure. | `_rollback_update` restores the factory tree on a failed `init-factory`. Adds the integration path and its test. |
| ST-0333 | Get the factory hook block from the new template during an update  | standard | M    | After an approved update, each factory hook has the template's `files:` value and a change to the DSL or chapter 5 triggers `arch-lint`, without a question.                                        | `merge-precommit-config` merges the hook block today and names old paths. Adds the template values and the test. |

### Testability Assessment

All actor goals produce observable results on temporary projects: `install.json` content, file paths, `.pre-commit-config.yaml` content, the factory tree, exit codes, and terminal output. Tests instrument `init-factory` and `update-factory` as subprocesses with a staged source tree, and the version test as a contract test on version strings. To force a failure partway, the tests need a way to make `migrate-spec-layout` fail on a chosen step; the E1 stories must leave such a seam (for example a fixture file that makes one move fail). No other red flags.

### Ownership Resolution

| Contract                                                                                 | .feature Rule                                                                                   | Owner   | Rationale                                                        |
| ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------- | ---------------------------------------------------------------- |
| CAL-07-CT-01: install records classify by Semantic Versioning precedence                 | core-artifact-layout.feature#Project maintainer receives the new layout with the factory update | ST-0330 | introduces the version test                                      |
| CAL-07-IT-01: an approved update leaves the project in the new layout without a question | core-artifact-layout.feature#Project maintainer receives the new layout with the factory update | ST-0330 | introduces the migration call                                    |
| CAL-07-IT-05: a failed migration keeps the prior version, reports, and exits non-zero    | core-artifact-layout.feature#Project maintainer receives the new layout with the factory update | ST-0330 | introduces the version write after success                       |
| CAL-07-IT-02: a first install and a rerun move nothing; a first install lists old paths  | core-artifact-layout.feature#Project maintainer receives the new layout with the factory update | ST-0331 | introduces the first-install listing                             |
| CAL-07-IT-03: a failed migration rolls the whole update back                             | core-artifact-layout.feature#Project maintainer receives the new layout with the factory update | ST-0332 | first story that exercises `_rollback_update` with the migration |
| CAL-07-IT-04: the factory hook block takes the template's values during an update        | core-artifact-layout.feature#Project maintainer receives the new layout with the factory update | ST-0333 | introduces the hook block under the update                       |

## E6: Publish the architecture PDF with the glossary as chapter 12

### Why this EPIC exists

After the move, chapter 12 holds one link line, and a PDF built from it would lose the glossary. `publish-docs` also reads the DSL and the theme from `docs/arc42/`, which no longer holds them. This EPIC keeps the PDF complete without any change to a project's manifest (DEC-16).

### Actor Goals

- Project maintainer publishes the architecture PDF with the glossary as chapter 12.

### Demo

1. Take the `publish-docs` test fixture, whose chapter 12 defines "Ledger Entry" and whose manifest selects `arc42/12_glossary.md`.
2. Run `migrate-spec-layout` on the fixture.
3. Run `publish-docs`. It builds the PDF.
4. Open chapter 12 of the PDF. It contains "Ledger Entry". The manifest is unchanged.

### Scope

**In:**

- `publish-docs` reads `architecture.dsl` from `docs/spec/` and the theme from `docs/assets/themes/` (CAL-G16 for `publish-docs`).
- The assembler `_docs_assemble.py` renders `docs/spec/glossary.md` wherever a manifest entry or glob selects `arc42/12_glossary.md`.
- The `publish-docs` skill text names the new paths.

**Out:**

- Any manifest change. No manifest needs one.
- Publishing other spec files in the PDF.

### Dependencies

E1 and E2 (the fixture runs `migrate-spec-layout` with its glossary step before `publish-docs`). The structurizr wrapper from E3 (ST-0325), because `publish-docs` calls it.

### Boundaries

- Scripts: `packages/factory/scripts/publish-docs`, `packages/factory/scripts/_docs_assemble.py`
- Skill: `packages/factory/skills/publish-docs/SKILL.md`
- Output: the PDF file
- Tests: `test_docs_assemble.py`, `test_publish_docs.py` in `tests/factory/`

### Domain Rules

- No manifest needs a change for chapter 12 to show the glossary.
- `publish-docs` reads only the new paths.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                   | Tier     | Size | Goal                                                                                                                                                   | Basis                                                                                                   |
| ------- | ------------------------------------------------------------ | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| ST-0334 | Publish the architecture PDF with the glossary as chapter 12 | standard | M    | The project maintainer runs `publish-docs` on a migrated project and finds the glossary's terms in chapter 12 of the PDF, with the manifest unchanged. | `publish-docs` requires `docs/arc42/architecture.dsl`; the assembler knows no `glossary.md`. Adds both. |

### Testability Assessment

The manifest resolution is a pure function of the assembler and is assertable as a contract test. The PDF build needs Docker, so CAL-11-IT-01 runs only in the container suite (CAL-G09). That is a red flag for the default suite, not for the goal: the test reads the text of chapter 12 from the built PDF.

### Ownership Resolution

| Contract                                                                                  | .feature Rule                                                                                                  | Owner   | Rationale                              |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------- | -------------------------------------- |
| CAL-11-CT-01: a manifest entry or glob for chapter 12 resolves to `docs/spec/glossary.md` | core-artifact-layout.feature#Project maintainer publishes the architecture PDF with the glossary as chapter 12 | ST-0334 | introduces the chapter 12 substitution |
| CAL-11-IT-01: the migrated fixture builds a PDF whose chapter 12 holds the fixture term   | core-artifact-layout.feature#Project maintainer publishes the architecture PDF with the glossary as chapter 12 | ST-0334 | introduces the new DSL and theme paths |

## E7: Start feature work once the anchor files exist

### Why this EPIC exists

The `feature-addition` playbook and the Stage 1 exit of `brownfield-onboarding` check for anchor files (the files a project must have before feature work starts). Today the set names `docs/CONTEXT.md`. After the fold, no migrated project has that file, so the check would stop every migrated project (CAL-G01). This EPIC sets the anchor set to `docs/spec/architecture.dsl`, `docs/spec/scope-map.md`, `docs/spec/glossary.md`, and `docs/agent-context.md`.

### Actor Goals

- Project maintainer starts feature work once the anchor files exist.

### Demo

1. Take a migrated project with the four anchor files and no `docs/CONTEXT.md`.
2. Start `feature-addition`. The anchor-file check passes and the playbook proceeds.
3. Delete `docs/spec/glossary.md` and start `feature-addition` again. It reports `docs/spec/glossary.md` as missing and suggests `brownfield-onboarding`.

### Scope

**In:**

- The anchor set of four files in `playbooks/feature-addition.md` and in the Stage 1 exit of `playbooks/brownfield-onboarding.md`. Each missing file is named.
- The reason text for leaving `docs/CONTEXT.md` out of the anchor set, in `validation-rules.md` § Anchor-file prerequisite (M-06).
- Three `implemented` Rules of `newcomer-onboarding.feature` and their scope-map rows, updated to the four anchor files and to `docs/spec/glossary.md` (CAL-G15): `Brownfield onboarding exits after three anchor files`, `Feature-addition deepens anchor files incrementally`, and `Feature-addition prerequisite checks anchor file presence, not a gate marker`.

**Out:**

- The reverse-map Rule of `newcomer-onboarding.feature` (E8, ST-0337).
- Any other change to the two playbooks.

### Dependencies

None. The anchor check is a file-existence check that a fixture shows.

### Boundaries

- Playbooks: `packages/factory/playbooks/feature-addition.md`, `packages/factory/playbooks/brownfield-onboarding.md`
- Spec: `docs/spec/newcomer-onboarding.feature`, `docs/spec/scope-map.md`, `docs/spec/supplementary_specs/validation-rules.md`
- Tests: `test_brownfield_order.py`, `test_feature_addition_contract.py`, `test_core_layout_references.py` (new or extend) in `tests/factory/`

### Domain Rules

- The anchor set is exactly `docs/spec/architecture.dsl`, `docs/spec/scope-map.md`, `docs/spec/glossary.md`, and `docs/agent-context.md` (`ANCHOR_FILE_SET`).
- `docs/CONTEXT.md` is never an anchor file.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                          | Tier     | Size | Goal                                                                                                                                               | Basis                                                                                        |
| ------- | ------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| ST-0335 | Start feature work in a migrated project with the four anchor files | standard | M    | The project maintainer starts `feature-addition` in a migrated project and passes the check with the four anchor files; each missing one is named. | Both playbooks check anchor files and name `docs/CONTEXT.md`. Changes the set and the tests. |

### Testability Assessment

The anchor check is playbook text that an agent follows, so the retained test is a deterministic text check: both playbooks name the four files, name each missing one, and do not name `docs/CONTEXT.md` as an anchor (CAL-15-LN-01). That is a red flag only in that a text check cannot prove an agent's behaviour; the playbook's existing contract tests follow the same method. No other red flags.

### Ownership Resolution

| Contract                                                                          | .feature Rule                                                                                   | Owner   | Rationale                     |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------- | ----------------------------- |
| CAL-15-LN-01: both playbooks name the four anchor files and not `docs/CONTEXT.md` | core-artifact-layout.feature#Project maintainer starts feature work once the anchor files exist | ST-0335 | introduces the new anchor set |

## E8: Let agents read and write the core at its new paths

### Why this EPIC exists

The agents, skills, playbooks, templates, and conventions name the old paths in about 60 files. After a migration, an agent that follows its text writes a feature file to the wrong folder, looks for a use-case file that no longer exists, or writes terms into a `CONTEXT.md`. This EPIC moves every such text to the new paths, cut by what each group of agents does.

### Actor Goals

- CLI-invoked agent reads and writes the core at its new paths.

### Demo

1. In a migrated project, run `domain-modeling` to settle the term "Payout" for the context "Billing". The "Billing" section of `docs/spec/glossary.md` gets a row for "Payout" with Term, Definition, and Avoid.
2. Run the requirements agent on an accepted proposal named `payments`. The feature file lands at `docs/spec/features/payments.feature`, and the gaps report and the QA strategy land in `docs/spec/work/`.
3. Dispatch a developer agent on a story in a project without `use_cases/`. It reads the scope map and the feature files and never looks for a use-case file.
4. Run `intent select` in a project whose only feature file is in `docs/spec/features/`. The requirements stage counts as done.

### Scope

**In:**

- A glossary template in the table form, in place of the `CONTEXT.md` template. `domain-modeling` and the other vocabulary skills write and read terms in `docs/spec/glossary.md`. Whether a term may appear twice inside one section (CAL-G13).
- `reverse-map` seeds the vocabulary into the glossary tables and writes no `docs/CONTEXT.md`. Its Rule in `newcomer-onboarding.feature` and its scope-map row follow (CAL-G15).
- The requirements and spec-review agents and their skills write feature files to `docs/spec/features/` and working output to `docs/spec/work/`.
- Agents and skills that keep todo lists write to `docs/spec/work/todo.md` and `docs/spec/work/todos.md`.
- The developer and reconciliation agents lose the use-case fallback. The implementation-side agents and skills read the core at the new paths, and `test-design-verify` finds feature files in `features/`.
- The architecture agents and skills read and write the DSL at `docs/spec/`, the theme at `docs/assets/themes/`, and `module-graph-check` reads the new paths.
- `intent`, `INDEX.yaml` preconditions, and the dispatch extensions find feature files in `features/` and no use-case folder.
- Each story removes the old paths from its files. The story slicing assigns each file to one story (CAL-G08).

**Out:**

- Agent texts that an earlier EPIC already changes: `capture-context` (E4), `publish-docs` (E6), the two onboarding playbooks (E7).
- The regression guard over all factory files (E9).

### Dependencies

None. Agent texts change on their own; `domain-modeling` writes into a fixture glossary.

### Boundaries

- Agents, skills, playbooks, rulebooks under `packages/factory/`
- Scripts: `intent`, `module-graph-check`, `test-design-verify`
- Config: `packages/factory/config/extensions/dispatch-wave.ts`, `run-agent.ts`, `packages/factory/INDEX.yaml`
- Docs: `packages/factory/docs/factory-guide.md`
- Spec: `docs/spec/newcomer-onboarding.feature`, `docs/spec/scope-map.md` (reverse-map Rule only)
- Tests: the tests of section 5 for E8, and `test_core_layout_references.py`

### Domain Rules

- An agent never looks for a use-case file or an actor-goal list.
- New terms land as rows of a Term/Definition/Avoid table in `docs/spec/glossary.md`, never in a `CONTEXT.md`.
- Feature files land in `docs/spec/features/`; working output and todo lists land in `docs/spec/work/`.
- The DSL lives at `docs/spec/`; the theme at `docs/assets/themes/`.

### Size

7 stories.

### Building-Block Inventory

| Story   | Capability                                                          | Tier     | Size | Goal                                                                                                                                                                      | Basis                                                                                                                      |
| ------- | ------------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| ST-0336 | Record and look up domain terms in the glossary                     | standard | M    | `domain-modeling` writes a settled term as a row of its section in `docs/spec/glossary.md`, and the review skills look terms up there.                                    | Skills write and read `docs/CONTEXT.md` or `docs/arc42/CONTEXT.md`; the template is the `CONTEXT.md` list form.            |
| ST-0337 | Seed the domain vocabulary into the glossary during reverse mapping | standard | S    | `reverse-map` writes the extracted terms into Term/Definition/Avoid tables of `docs/spec/glossary.md` and writes no `docs/CONTEXT.md`.                                    | `reverse-map` seeds `docs/CONTEXT.md`. Needs ST-0336's template.                                                           |
| ST-0338 | Write feature files and working output to their folders             | standard | M    | The requirements agent puts `payments.feature` in `docs/spec/features/` and the gaps report, the QA strategy, and `prd.md` in `docs/spec/work/`.                          | The agents and skills write to the top of `docs/spec/` and read `supplementary_specs/`.                                    |
| ST-0339 | Record open work in the todo lists of the work folder               | economy  | S    | The coaching agent, `retrospective`, and `create-backlog-make-concrete` add todo entries to `docs/spec/work/todo.md` or `docs/spec/work/todos.md`.                        | The texts name `docs/spec/todo.md` and `docs/spec/todos.md`.                                                               |
| ST-0340 | Find a story's behaviour without use-case files                     | standard | M    | The developer and reconciliation agents read the scope map and feature files and never look for a use-case file; `test-design-verify` finds feature files in `features/`. | Both agents keep a use-case fallback; the implementation-side texts name `docs/spec/*.feature` and `supplementary_specs/`. |
| ST-0341 | Read and write the architecture model in `docs/spec/`               | standard | M    | The architecture agent and its skills write the DSL to `docs/spec/architecture.dsl` and the theme to `docs/assets/themes/`; `module-graph-check` reads the new paths.     | The texts and `module-graph-check` name `docs/arc42/*.dsl`, `docs/arc42/themes`, and `supplementary_specs/`.               |
| ST-0342 | Route agents by feature files in `features/`                        | standard | M    | `intent select` counts a feature file in `docs/spec/features/` as a done requirements stage, and the dispatch extensions name no use-case folder.                         | `intent` and `INDEX.yaml` preconditions use `docs/spec/*.feature`; `dispatch-wave.ts` and `run-agent.ts` name `use_cases`. |

### Testability Assessment

`intent`, `module-graph-check`, and `test-design-verify` produce exit codes and output that tests assert on fixtures. Everything else is agent and skill text, so the retained test is a deterministic text check (CAL-12-LN-01) plus the old-path guard of E9. That is a red flag: a text check cannot prove what an agent does at run time. The demos above are manual walkthroughs. The QA strategy's CAL-12-LN-01 names `domain-modeling`, `reverse-map`, and the developer and reconciliation agents; it does not name the requirements agent's scenario. ST-0338 adds that assertion to CAL-12-LN-01.

### Ownership Resolution

| Contract                                                                                                                        | .feature Rule                                                                             | Owner   | Rationale                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------- | -------------------------------------------------------------------------- |
| CAL-12-LN-01: `domain-modeling` and `reverse-map` write table rows; no use-case fallback; requirements outputs in their folders | core-artifact-layout.feature#CLI-invoked agent reads and writes the core at its new paths | ST-0336 | creates the text check; ST-0337, ST-0338, and ST-0340 add their assertions |

## E9: Migrate the factory's own repository and keep it free of old paths

### Why this EPIC exists

The factory's repository is the first project to move, and it proves the script on a real project before any installed project moves (Proposal Scope). A newcomer who opens it then finds the whole core in `docs/spec/`. A regression guard keeps old paths from coming back into factory files.

### Actor Goals

- Newcomer finds the whole specification core at one root.
- Factory maintainer keeps the factory free of old paths.
- Factory maintainer migrates the factory's own repository first.

### Demo

1. On a branch of the factory's repository, run `packages/factory/scripts/migrate-spec-layout`. It exits 0.
2. List `docs/spec/`. It holds only single-file core artifacts and the folders `features/`, `areas/`, and `work/`.
3. Run `link-check`, `arch-lint`, `structurizr validate`, `dependency-check`, `spec-lint`, `scope-lint`, and `statemachine-lint`. Each exits 0.
4. Run `capture-context --fold-context-map`, delete `docs/CONTEXT.md` and `docs/arc42/CONTEXT-MAP.md`, then run `concern-lint` and `link-check`. Both pass.
5. Run the eleven greps of the Completion Criteria on `packages/factory/`, `tests/factory/`, and `.pre-commit-config.yaml`, and `grep -rE 'CONTEXT(-MAP)?\.md' packages/factory/`. Neither finds anything outside the exclusions.

### Scope

**In:**

- The factory's own migration with `packages/factory/scripts/migrate-spec-layout`, and the record of the run (CAL-14-AC-01).
- The repository's local hooks in `.pre-commit-config.yaml` switched to the new paths.
- References in `backlog/` and other files that the script lists but does not rewrite, fixed by hand.
- Every chapter 12 section, "Acronyms and Abbreviations" included, as a Term/Definition/Avoid table.
- The fold of the factory's routing with `capture-context --fold-context-map`, the deletion of the old routing files, and the record of the run (CAL-08-AC-01).
- A regression guard test for the eleven old-path patterns and for `CONTEXT(-MAP)?\.md`, with the exclusions `CHANGELOG.md`, `reports/`, `scripts/migrate-spec-layout` and its tests, and the `--fold-context-map` section of `capture-context`.
- A layout check of the factory's `docs/spec/` and a check that no actor-goal list or `use_cases` remains.

**Out:**

- The reinstall from `packages/factory/`. The factory maintainer runs it before ST-0343 commits, because `update-factory` asks for confirmation. ST-0343 waits for it as its human touchpoint.
- Cleaning up duplicate glossary terms beyond what the gates need.

### Dependencies

E1 to E8. The factory moves with the complete script, every gate and agent must work there, and the guard needs every file cleaned.

### Boundaries

- Repository: `docs/`, `backlog/`, `.pre-commit-config.yaml`
- Scripts used: `migrate-spec-layout`, the seven gates, `concern-lint`
- Skill used: `capture-context --fold-context-map`
- Tests: `test_core_layout_references.py`, `test_core_layout_gates.py` in `tests/factory/`

### Domain Rules

- The factory's repository moves with the same script installed projects receive, without hand moves.
- The guard excludes only `CHANGELOG.md`, `reports/`, `scripts/migrate-spec-layout` and its tests, and the `--fold-context-map` section of `capture-context`.
- No actor-goal list and no `use_cases` folder remain under `docs/`.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                               | Tier     | Size | Goal                                                                                                                                                                        | Basis                                                                                                                 |
| ------- | -------------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| ST-0343 | Migrate the factory's own repository into the new layout | standard | L    | The factory maintainer runs the script on the factory's repository; a newcomer lists `docs/spec/` and finds only core files and the four folders, and the seven gates pass. | The repository is in the old layout; local hooks pass old paths. Runs the script, switches hooks, fixes listed paths. |
| ST-0344 | Fold the factory's routing into the agent context file   | economy  | S    | The factory maintainer runs the fold, deletes the old routing files, and `concern-lint` and `link-check` pass.                                                              | `docs/CONTEXT.md` and `docs/arc42/CONTEXT-MAP.md` exist; `docs/agent-context.md` has domain concerns.                 |
| ST-0345 | Keep the factory free of old paths                       | economy  | S    | The factory maintainer runs the old-path greps and finds nothing outside the exclusions; a test fails when an old path comes back.                                          | No guard exists; every earlier story cleaned its files.                                                               |

### Testability Assessment

All actor goals produce observable results: directory listings, gate exit codes, grep output, and `concern-lint` output. Tests instrument the repository itself as a deterministic text check (`test_core_layout_references.py`) and the gates as subprocesses (`test_core_layout_gates.py`). Two goals are runs that happen once, the migration and the fold, so they are acceptance checks recorded in the story, not retained tests. `structurizr validate` needs the container suite (CAL-G09); the QA strategy asks for the container suite before the factory's migration merges.

### Ownership Resolution

| Contract                                                                                                   | .feature Rule                                                                               | Owner   | Rationale                                      |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------- | ---------------------------------------------- |
| CAL-01-IT-01: a migrated project has `work/`, no empty `schemas/`, and non-spec files outside `docs/spec/` | core-artifact-layout.feature#Newcomer finds the whole specification core at one root        | ST-0318 | introduces the moves on a fixture              |
| CAL-01-LN-01: the top of the factory's `docs/spec/` holds only core files and the four folders             | core-artifact-layout.feature#Newcomer finds the whole specification core at one root        | ST-0343 | introduces the factory's migrated layout       |
| CAL-14-AC-01: the factory's own migration runs without stopping                                            | core-artifact-layout.feature#Factory maintainer migrates the factory's own repository first | ST-0343 | runs the migration                             |
| CAL-14-IT-01: each of the seven gates exits 0 on the migrated factory repository                           | core-artifact-layout.feature#Factory maintainer migrates the factory's own repository first | ST-0343 | first story with the factory in the new layout |
| CAL-14-LN-01: the glossary has only Term tables, Acronyms included; no use-case file remains               | core-artifact-layout.feature#Factory maintainer migrates the factory's own repository first | ST-0343 | first story with the factory's glossary        |
| CAL-13-LN-01: none of the eleven old-path patterns occurs in the factory                                   | core-artifact-layout.feature#Factory maintainer keeps the factory free of old paths         | ST-0345 | introduces the guard                           |
| CAL-13-LN-02: `CONTEXT(-MAP)?\.md` occurs in `packages/factory/` only inside the exclusions                | core-artifact-layout.feature#Factory maintainer keeps the factory free of old paths         | ST-0345 | introduces the guard                           |
