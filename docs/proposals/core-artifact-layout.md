---
schema_version: 2
title: Core Artifact Layout
status: open
owner: Matthias Daues
created: 2026-11-01
updated: 2026-11-02
supersedes:

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - docs/spec/todo.md
    - packages/factory/scripts/update-factory
    - packages/factory/scripts/link-check
    - packages/factory/scripts/arch-lint
    - packages/factory/scripts/structurizr
    - packages/factory/scripts/dependency-check
    - packages/factory/scripts/spec-lint
    - packages/factory/scripts/scope-lint
    - packages/factory/scripts/statemachine-lint
    - packages/factory/agents/requirements-agent.md
    - packages/factory/agents/spec-review-agent.md
    - packages/factory/agents/developer-agent.md
    - packages/factory/agents/reconciliation-agent.md
    - packages/factory/agents/coaching-agent.md
    - packages/factory/skills/write-prd/SKILL.md
    - packages/factory/playbooks/brownfield-onboarding.md
    - packages/factory/skills/derive-feature/SKILL.md
    - packages/factory/skills/domain-modeling/SKILL.md
    - packages/factory/skills/write-adr/SKILL.md
    - packages/factory/skills/grilling/SKILL.md
    - packages/factory/skills/capture-context/SKILL.md
    - packages/factory/rulebooks/conventions/context-format.md
    - packages/factory/rulebooks/templates/context.md
    - packages/factory/rulebooks/templates/context-map.md
    - packages/factory/scripts/concern-lint
    - docs/agent-context.md
    - docs/CONTEXT.md
    - docs/arc42/CONTEXT-MAP.md
    - docs/arc42/12_glossary.md
    - docs/spec/todos.md
    - packages/factory/scripts/intent
    - packages/factory/scripts/module-graph-check
    - packages/factory/scripts/publish-docs
    - packages/factory/scripts/_docs_assemble.py
    - packages/factory/scripts/test-design-verify
    - packages/factory/scripts/init-factory
    - packages/factory/scripts/merge-precommit-config
    - packages/factory/config/hook-metadata.yaml
    - packages/factory/config/pre-commit-config.yaml
    - docs/arc42/themes
    - packages/factory/config/extensions
    - .pre-commit-config.yaml
    - tests/factory

governance:
  assurance: elevated
  risk_domains:
    - compatibility
    - operations

estimate:
  as_of: 2026-11-01
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Feature Request: Core Artifact Layout

## Primer

A developer who opens a project built with the Agent Factory looks for its
specification: the files that say what the system does, which data it keeps,
and how its parts fit together. Today these files sit in four folders. The
specification folder also holds reports that agents write while they work. The
factory points to its vocabulary file at two different paths, and two files
tell agents what to read. So a newcomer cannot tell which files are the source
and where they live.

The proposal sorts these files into kinds. A core file has three marks. People
edit it by hand. Other files derive from it or are checked against it. An
automatic check script, called a gate, checks it or should check it. The core
files include the scope map, the feature files that describe behaviour, the
data model, the architecture model, and the glossary. Working output is what
agents write while they derive or review the core, such as gaps reports. Some
files stay where they are, because they do not specify the system.
Architecture decision records keep the reasons for decisions, and the agent
context file tells agents what to read for each task.

In the new layout, every core file lives in the specification folder, and no
other file sits at its top level. An area spec describes one subsystem in
depth. Feature files, payload schemas, and area specs get their own
subfolders. Working output and the todo lists go into a work folder.

A migration script moves a project into this layout, and the factory's own
repository moves first. The script moves each file with git, so the history
keeps it. It rewrites the Markdown links that point at old paths. It lists
every other mention of an old path, and the developer fixes those by hand. The
glossary chapter of the architecture documentation moves into the
specification folder. A new chapter in its old place holds one line that links
to it.

The old context map lists the parts of the domain, and the script leaves it in
place. Folding it into the agent context file needs judgment, and the move
should stay mechanical. So the developer runs the context skill, which turns
each listed part into an entry of the agent context file. Then the developer
deletes the context map.

Every factory update runs the script, so the update moves the files. The
developer approves the update, not the move. When a project keeps terms both
in the old vocabulary file and in a glossary, the script puts both into the
new glossary and lists the terms that appear twice. Cleaning up the glossary
is a follow-up step, like the fold of the context map.

The layout gives the core one root. A newcomer who opens the specification
folder sees every source file and nothing else at the top. A later proposal
for the data model needs this fixed path.

The proposal has no open questions. A gate for the glossary and the merge of
the two todo lists are left for later work.

## Summary

All of a project's specification core lives in `docs/spec/`, and nothing
else lives at the top of that folder. Feature files live in
`docs/spec/features/`, payload schemas in `docs/spec/schemas/`, area specs in
`docs/spec/areas/`, and the working output of agents in `docs/spec/work/`.
A migration script moves an installed project into this layout. A newcomer
can then see which files are the source and where they are. Today a newcomer
cannot.

## Motivation

The factory spreads a project's specification over four places:
`docs/spec/`, `docs/spec/supplementary_specs/`, `docs/arc42/`, and `docs/`. `docs/spec/` mixes sources such as `scope-map.md` with
working output such as `*-gaps.md` and `prd.md`. The factory's own files
refer to `CONTEXT.md` at two paths, `docs/CONTEXT.md` (68 references) and
`docs/arc42/CONTEXT.md` (7 occurrences on 6 lines). The convention `context-format.md` names one
path, and the `grilling` and `domain-modeling` skills name the other. Two
files route agents: `agent-context.md` and `CONTEXT-MAP.md`. The factory
keeps two todo lists, `todo.md` and `todos.md`, with two ID schemes.

The proposal [entity-model-as-dbml.md](entity-model-as-dbml.md) needs one
fixed path for its DBML file in every project (todo T-0006). It builds on
this layout, which ships first (DEC-01).

## Core Principles

- **One root for the core.** Every core file lives in `docs/spec/`.
- **Nothing else at the top.** The top of `docs/spec/` holds only the
  single-file core artifacts. The core folders are `features/`, `schemas/`,
  and `areas/`. `work/` holds no core file.
- **The move is mechanical.** A script moves files and rewrites links the
  same way in every project, as part of every factory update.

## Design

### The core artifact set

A project's specification core is a set of files with three marks (DEC-02).
People edit them by hand. Every other artifact derives from them or is checked
against them. A gate checks them or should check them. ADRs are not core. They
record decisions and stay in `docs/adr/` (DEC-03).

| File                     | Holds                                        | Gate                          |
| ------------------------ | -------------------------------------------- | ----------------------------- |
| `scope-map.md`           | What the system does, by domain area         | `scope-lint`                  |
| `features/*.feature`     | Behaviour, as Rules per actor goal           | `scope-lint` (scope header)   |
| `entity-model.md`        | Tables, keys, constraints, enums             | none yet                      |
| `state-machines.md`      | States and transitions                       | `statemachine-lint`           |
| `validation-rules.md`    | Rules on input and on data                   | `spec-lint`                   |
| `interface-contracts.md` | Contracts at the system's boundaries         | `spec-lint`                   |
| `architecture.dsl`       | Building blocks, views, deployment           | `arch-lint`, `structurizr`    |
| `dependency-rules.dsl`   | Allowed dependencies between building blocks | `dependency-check`            |
| `schemas/*`              | Structure inside payload columns             | none yet                      |
| `areas/*.md`             | One subsystem's specification in depth       | `spec-lint`                   |
| `glossary.md`            | The domain vocabulary all of the above uses  | `spec-lint` `GLOSS001` (info) |

The entity-model proposal replaces `entity-model.md` with
`entity-model.dbml` and adds gates for it and for `schemas/`.

### Files outside the core

Agents write working output while they derive or review the core. It lives
in `docs/spec/work/`: gaps reports, QA strategies, `prd.md`, and update
summaries (DEC-05). The two todo lists are records of open work, not sources,
so they live in `work/` too (DEC-09).

An area spec describes one subsystem in depth. It is core and lives in
`docs/spec/areas/`. So the top of `docs/spec/` keeps its fixed set of files,
and the move stays mechanical. A project may fold an area spec into the
single-file core artifacts later, when it works on that area (DEC-09).

The arc42 prose stays in `docs/arc42/` and refers to
`docs/spec/architecture.dsl`. `structurizr`, `arch-lint`, and `publish-docs`
read the DSL from `docs/spec/` and the chapters from `docs/arc42/`. The
Structurizr theme moves from `docs/arc42/themes/` to `docs/assets/themes/`,
next to the rendered arc42 images, and the DSL's `theme` line points there
(DEC-14). The first story checks that Structurizr accepts a theme path outside
the DSL's folder; if it does not, that is a finding for the stakeholder.
`publish-docs` puts the content of `docs/spec/glossary.md` into the PDF as
chapter 12 (DEC-16). When a manifest entry, a glob included, selects
`arc42/12_glossary.md`, `publish-docs` renders `docs/spec/glossary.md` in its
place. So no manifest needs a change. `testing.yaml` and `agent-context.md` stay in
`docs/`, because neither specifies the system. `testing.yaml` is derived from
code, and `agent-context.md` routes agents.

The actor-goal list and the use-case files belong to the factory's earlier
specification method, which the scope map and the feature files replaced. No factory step produces them (ST-0098), and
they do not fit the scope map and feature files. So the move removes them, also from `docs/~archive/`; every other file in the
archive stays (DEC-10).

### Routing and vocabulary

`docs/agent-context.md` is the project's one routing file (DEC-07). Each
bounded context becomes a domain concern in it, with its description and
`Read:` paths. The domain concerns also route to the glossary. After the
move, `CONTEXT.md` and `CONTEXT-MAP.md` do not exist.

The term definitions live in `docs/spec/glossary.md`, a core file. Each
section of the glossary is one table with the columns Term, Definition, and
Avoid (DEC-12). A section covers a bounded context or a topic, such as
acronyms (DEC-15). Which contexts exist is a routing fact, and
`agent-context.md` holds it. In a project with arc42, chapter `12_glossary.md` keeps
one line that links to `docs/spec/glossary.md`. `domain-modeling` writes new
terms into this table. The `CONTEXT.md` template becomes a glossary template
in this form, the `context-map.md` template goes, and the convention
`context-format.md` describes `glossary.md` and the domain concerns.
`spec-lint` `GLOSS001` reads the terms from the table. It reports, as `info`,
a term that no other core file uses. It does not count `glossary.md` itself
or the files in `work/` as uses.

### Path table

The table lists every move the layout makes.

| Old path                                                                                 | New path                                                             |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `docs/spec/scope-map.md`                                                                 | unchanged                                                            |
| `docs/spec/<name>.feature`                                                               | `docs/spec/features/<name>.feature`                                  |
| `docs/spec/supplementary_specs/entity-model.md`                                          | `docs/spec/entity-model.md`                                          |
| `docs/spec/supplementary_specs/state-machines.md`                                        | `docs/spec/state-machines.md`                                        |
| `docs/spec/supplementary_specs/validation-rules.md`                                      | `docs/spec/validation-rules.md`                                      |
| `docs/spec/supplementary_specs/interface-contracts.md`                                   | `docs/spec/interface-contracts.md`                                   |
| `docs/arc42/architecture.dsl`                                                            | `docs/spec/architecture.dsl`                                         |
| `docs/arc42/dependency-rules.dsl`                                                        | `docs/spec/dependency-rules.dsl`                                     |
| `docs/arc42/themes/`                                                                     | `docs/assets/themes/`                                                |
| `docs/arc42/12_glossary.md`                                                              | `docs/spec/glossary.md`; chapter 12 links to it                      |
| `docs/CONTEXT.md`, `docs/arc42/CONTEXT.md`                                               | terms to `docs/spec/glossary.md`, routing to `docs/agent-context.md` |
| `docs/arc42/CONTEXT-MAP.md`                                                              | domain concerns in `docs/agent-context.md`                           |
| `docs/spec/prd.md`                                                                       | `docs/spec/work/prd.md`                                              |
| `docs/spec/<name>-gaps.md`                                                               | `docs/spec/work/<name>-gaps.md`                                      |
| `docs/spec/<name>-qa-strategy.md`                                                        | `docs/spec/work/<name>-qa-strategy.md`                               |
| `docs/spec/SPEC-UPDATE-SUMMARY.md`                                                       | `docs/spec/work/SPEC-UPDATE-SUMMARY.md`                              |
| `docs/spec/todo.md`, `docs/spec/todos.md`                                                | `docs/spec/work/todo.md`, `docs/spec/work/todos.md`                  |
| `docs/spec/supplementary_specs/<area>.md`                                                | `docs/spec/areas/<area>.md`                                          |
| `docs/spec/supplementary_specs/<area>-qa-strategy.md`                                    | `docs/spec/work/<area>-qa-strategy.md`                               |
| `actor-goal-list.md` and `use_cases/`, anywhere under `docs/`, `docs/~archive/` included | removed                                                              |

### The migration script

`packages/factory/scripts/migrate-spec-layout` moves an installed project's
files with `git mv`, following the path table (DEC-06). It removes the files
that the path table marks as removed with `git rm`, so the git history keeps
them. It rewrites the local Markdown links that point at an old path. It also
rewrites the relative links inside each moved file, so a link from
`work/todo.md` to `../reviews/` becomes `../../reviews/`. A Markdown link to a
removed file becomes its link text in a code span, so
`link-check` still passes. The script lists every other occurrence of an old
path, for example in CI files or scripts, for the developer to fix. It never
rewrites those occurrences. `--dry-run` prints the moves and rewrites without
making them.

The script moves `docs/arc42/12_glossary.md` to `docs/spec/glossary.md` and
writes a new chapter 12 with one line that links to it. Every section of the
chapter that holds a two-column table moves into `glossary.md`, under its
heading. A table directly under the chapter title becomes the section
"Terms". The script renames the table's columns to Term and Definition and
adds an empty Avoid column. A section without a table, such as a list of
references, stays in chapter 12 below the link. A `CONTEXT.md` holds
terms when it has a `## Language` section, as the
[`CONTEXT.md` template](../../packages/factory/rulebooks/templates/context.md)
defines. The script moves its terms into `glossary.md` as a section of their
own, named after the file's title, whether or not a glossary exists. It never
stops on two vocabularies. It lists every term that appears in more than one
section and exits 0 (DEC-18). Then it removes the `## Language` section from
the `CONTEXT.md`, so the rest of the file holds routing only and the fold
handles it. A `CONTEXT.md` without a `## Language` section holds routing
only. A per-context `CONTEXT.md` next to a context's code, which
a context map lists, is handled the same way: its terms become that context's
section in `glossary.md`. The script converts the template's list form,
`**Term**:` with a definition and `_Avoid_:`, into table rows (DEC-12).

The script also updates the factory's own hook entries, the
`agent_factory_hook-*` block of the project's `.pre-commit-config.yaml`. It
sets the `files:` value of each factory hook to the value in the new hook
template, because the old paths sit inside regular expressions that a path
substitution does not match. The factory owns that block, so the update
changes it without a separate question.
The developer's own hooks stay as they are; the script lists their old paths
like any other occurrence.

The script ends by naming two follow-up steps for the developer. One folds the
routing, as described below. The other removes the duplicate terms it listed
and cleans up the glossary, for example with `domain-modeling` (DEC-18).

Folding routing into `agent-context.md` is not mechanical, so the script
leaves `CONTEXT-MAP.md` and any routing in `CONTEXT.md` in place. It names
`capture-context --fold-context-map` as the next step. That new mode of the
skill reads the context map and any `CONTEXT.md` that holds routing only. It
writes one domain concern per listed context with a `Read:` path that
`concern-lint` accepts, marks each concern as folded, and shows the result to
the developer. It rewrites every Markdown link under `docs/` that points at
`CONTEXT.md` or `CONTEXT-MAP.md` so that it points at `docs/agent-context.md`.
Then the developer deletes the old files (DEC-08, DEC-13).
`capture-context --update --scan` keeps every concern marked as folded.

The update moves the files; the developer does not confirm the move
separately (DEC-17). After the download, `update-factory` runs the new
version's `init-factory`, and `init-factory` runs `migrate-spec-layout` as its
last step. So the first update that ships the layout already runs the new
script. The developer approves the update as a whole at the approval step of
ADR-0023. Declining it means no update.

`init-factory` runs the script only on an update: when
`.agent-factory/install.json` records a factory version older than the
release that ships the layout. An `install.json` without a
`factory_version`, or with the value `unknown`, counts as older; older
installs did not record the version. Only a project without `install.json` is
a first install. A first install and a later run of
`init-factory` move nothing, so `init-factory` keeps its promise to leave the
project's own files alone. If a first install finds old paths, `init-factory`
lists them and names `migrate-spec-layout` as a command the developer can run.

The script has work to do while the project still has one of these paths:

- an old path of a row that moves or removes a file; the row for
  `scope-map.md` does not count;
- `docs/arc42/12_glossary.md`, while it holds a two-column table;
- a `CONTEXT.md` with a `## Language` section.

`CONTEXT-MAP.md` and a routing-only `CONTEXT.md` do not count, because the
fold removes them, not the script. On a project without any of these paths,
the script moves nothing and prints nothing.

If the script fails partway, it undoes its own moves and exits non-zero.
`init-factory` then fails, and `update-factory` rolls back the factory tree as
it does for any failed `init-factory`. The project keeps its old layout and
its old factory version, so its scripts and hooks stay consistent with its
layout. The factory's own repository moves first, with the same script.

### Factory changes

Every factory file that names an old path names the new one. That covers:

- the scripts `structurizr`, `arch-lint`, `dependency-check`, `spec-lint`,
  `scope-lint`, `statemachine-lint`, `intent`, `module-graph-check`,
  `publish-docs` with its assembler `_docs_assemble.py`, `test-design-verify`,
  `init-factory`, and `merge-precommit-config`;
- `config/hook-metadata.yaml`, the TypeScript files in `config/extensions/`,
  the hook template `config/pre-commit-config.yaml` that installed projects
  receive, and the repository's `.pre-commit-config.yaml`; in both, only the
  DSL paths change in the `files:` pattern of the `arch-lint` hook, which
  becomes
  `^docs/(spec/(architecture|dependency-rules)\.dsl|arc42/05_building_block_view\.md|assets/images/.*|adr/.*\.md)$`;
- the agents, skills, playbooks, conventions, and templates;
- the tests under `tests/factory/` that name a moved path.

`developer-agent` and `reconciliation-agent` lose their fallback to the
use-case files, and `spec-lint` loses the checks that read use-case files.
Its traceability checks `TRACE002` to `TRACE004` stay (DEC-10). `TRACE002`
stays an error, whether or not `use_cases/` exists; `spec-lint` drops the
downgrade to a warning. `capture-context` gains the mode `--fold-context-map`
(DEC-13). `init-factory` runs `migrate-spec-layout` as its last step (DEC-17).

## Scope

**In the first release:**

- The layout in `docs/spec/`, with `features/`, `schemas/`, `areas/`, and
  `work/`.
- The actor-goal list and the use-case files removed, and the use-case
  fallbacks removed from `developer-agent` and `reconciliation-agent`.
- The migration script, which every factory update runs through
  `init-factory`.
- The Structurizr theme in `docs/assets/themes/`, and the glossary as chapter
  12 of the PDF.
- The glossary table, and `capture-context --fold-context-map`.
- Every factory reference updated to the new paths.
- The factory's own repository migrated.

**Explicitly deferred (do NOT plan stories for these):**

- **DBML and its gates.** They belong to
  [entity-model-as-dbml.md](entity-model-as-dbml.md), which builds on this
  layout.
- **A blocking gate for `glossary.md`.** `GLOSS001` stays an `info` finding;
  no blocking check for a glossary has been designed.
- **One todo list.** Merging `todo.md` and `todos.md` changes one ID scheme
  and its references. Todo T-0008 tracks the merge (DEC-09).

## Open Questions

None.

## Completion Criteria

- After the factory's own migration, the top of `docs/spec/` holds only the
  single-file core artifacts of the table, and no folder other than
  `features/`, `schemas/`, `areas/`, and `work/`. `schemas/` exists only when
  the project has payload schemas.
- `find docs -name actor-goal-list.md -o -name use_cases` finds nothing in
  the factory's own repository.
- Outside `CHANGELOG.md`, `reports/`, `scripts/migrate-spec-layout`, and that
  script's tests, `grep -rE` finds nothing in `packages/factory/`, `tests/factory/`, and
  `.pre-commit-config.yaml` for each of these patterns:
  `supplementary_specs`, `docs/arc42/[a-z-]+\.dsl`, `docs/spec/[^/]+\.feature`,
  `docs/spec/prd\.md`, `docs/spec/[^/]+-(gaps|qa-strategy)\.md`,
  `docs/spec/todos?\.md`, `docs/arc42/themes`, `arc42/\(architecture`,
  `UC-XX`, `use_cases`, and `actor-goal-list`.
- `pre-commit run --files docs/spec/architecture.dsl` runs `arch-lint`, both in
  the factory's repository and in a project installed from the hook template.
- `link-check`, `arch-lint`, `structurizr validate`, `dependency-check`,
  `spec-lint`, `scope-lint`, and `statemachine-lint` pass on the factory's
  own repository after its migration.
- After the migration, each of these gates fails on a copy of the factory's
  repository in which one file it checks, at its new path, holds a
  deliberate error. A gate that skips a missing file therefore cannot pass.
- `migrate-spec-layout --dry-run` on a copy of an installed project changes
  no file and prints every planned move.
- `migrate-spec-layout` on a copy of an installed project moves its files,
  leaves `link-check` passing, and lists each old path found outside
  Markdown.
- On a project with a `CONTEXT.md` that holds terms and an existing
  glossary, the script exits 0. `glossary.md` holds both sets of terms in
  separate sections, and the script lists every term that appears twice.
- A first install of the factory on a project in the old layout moves no
  file and lists the old paths. An update from a version before the layout
  moves the files, and so does an update of a project whose `install.json`
  has no `factory_version`.
- After the migration, no `CONTEXT.md` in the project has a `## Language`
  section.
- After an update of a project in the old layout, its factory hook block
  triggers `arch-lint` on `docs/spec/architecture.dsl` and on chapter 5. The
  developer was not asked about the hooks.
- The factory's own migration runs without stopping, because its
  `docs/CONTEXT.md` has no `## Language` section. After the migration and the
  `capture-context --fold-context-map` run that follows it,
  `docs/spec/glossary.md` holds the terms of the old
  `docs/arc42/12_glossary.md`, `docs/agent-context.md` has one domain
  concern per context of the old `CONTEXT-MAP.md`, and `concern-lint` passes.
- Outside `CHANGELOG.md`, `scripts/migrate-spec-layout` and its tests, and the
  `--fold-context-map` section of `capture-context`, `grep -rE 'CONTEXT(-MAP)?\.md' packages/factory/` finds nothing.
- The fixture of `tests/factory/test_publish_docs.py` gains an
  `arc42/12_glossary.md` with one term, and its manifest selects that file.
  After `migrate-spec-layout` runs on the fixture, `publish-docs` builds its
  PDF, and the PDF's chapter 12 contains that term.
- A moved file's relative links resolve after the migration; `link-check`
  passes on `docs/spec/work/todo.md`.
- An update of an installed project in the old layout leaves it in the new
  layout. The developer approves the update and is not asked about the move.
- When `migrate-spec-layout` fails partway during an update, the project's
  files and factory version are as before the update, and `update-factory`
  reports the failure.
- `capture-context --fold-context-map` on the factory's `CONTEXT-MAP.md`
  writes one domain concern per listed context, and `concern-lint` passes.
  After the developer deletes the old files, neither `docs/CONTEXT.md` nor
  `docs/arc42/CONTEXT-MAP.md` exists, and `link-check` passes on every
  Markdown file under `docs/`.
- A `capture-context --update --scan` run after the fold keeps every folded
  concern.
- On a project already in the new layout, `migrate-spec-layout` moves no
  file. That holds also while chapter 12 keeps its link and its list of
  references, and while `CONTEXT-MAP.md` waits for the fold.
- Every section of the factory's `glossary.md` is a table with the columns
  Term, Definition, and Avoid, and `GLOSS001` reads them. Its Acronyms and
  Abbreviations section is among them.
- `GLOSS001` reports a term that appears only in `glossary.md` and in
  `work/`.
- In a project without `use_cases/`, `spec-lint` exits 1 on a business rule
  that is referenced but never defined.

## Guiding Rule

A newcomer who opens `docs/spec/` sees every source file and nothing else at
the top.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by     | Decision                                                                                                                                                                                                                                                                                                        | Raised by                                   |
| ------ | ---------- | ---------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| DEC-01 | 2026-11-01 | decision   | Matthias Daues | The layout is its own proposal and ships before the entity-model proposal, which builds on it.                                                                                                                                                                                                                  | PROP-11 of `entity-model-as-dbml.md`        |
| DEC-02 | 2026-10-30 | decision   | Matthias Daues | The core is the set of files people edit by hand, that other artifacts derive from or are checked against, and that a gate checks or should check. It lives in `docs/spec/`, with feature files in `features/` and payload schemas in `schemas/`.                                                               | DEC-08, DEC-13 of `entity-model-as-dbml.md` |
| DEC-03 | 2026-10-30 | decision   | Matthias Daues | ADRs are not core and stay in `docs/adr/`.                                                                                                                                                                                                                                                                      | DEC-07 of `entity-model-as-dbml.md`         |
| DEC-04 | 2026-10-30 | decision   | Matthias Daues | Installed projects move through a migration script that `update-factory` offers and runs only after the developer confirms. It rewrites Markdown links, lists other hits without changing them, and has `--dry-run`. DEC-17 drops the separate confirmation.                                                    | DEC-09 of `entity-model-as-dbml.md`         |
| DEC-05 | 2026-10-30 | decision   | Matthias Daues | Working output lives in `docs/spec/work/`.                                                                                                                                                                                                                                                                      | DEC-12 of `entity-model-as-dbml.md`         |
| DEC-06 | 2026-11-01 | decision   | Matthias Daues | The migration script is named `migrate-spec-layout`.                                                                                                                                                                                                                                                            | Draft                                       |
| DEC-07 | 2026-11-01 | decision   | Matthias Daues | `docs/agent-context.md` is the one routing file; `CONTEXT.md` and `CONTEXT-MAP.md` fold into its domain concerns. Term definitions live in the core file `docs/spec/glossary.md`.                                                                                                                               | Open Question 1, `CONTEXT-MAP.md`           |
| DEC-08 | 2026-11-01 | decision   | Matthias Daues | The script moves terms to `glossary.md` but leaves routing to `capture-context --fold-context-map` (named in DEC-13; first drafted as `--update`), because folding routing into domain concerns needs judgment.                                                                                                 | Draft, follows DEC-07                       |
| DEC-09 | 2026-11-01 | decision   | Matthias Daues | `todo.md` and `todos.md` move to `docs/spec/work/`; merging them is a separate todo. Area specs move to `docs/spec/areas/`, their QA strategies to `work/`. A project may fold an area spec into the single-file core artifacts later.                                                                          | Open Question 1                             |
| DEC-10 | 2026-11-01 | decision   | Matthias Daues | The actor-goal list and the use-case files are removed, along with the agents' use-case fallbacks. They do not fit the scope map and feature files.                                                                                                                                                             | Open Question 1                             |
| DEC-11 | 2026-11-01 | decision   | Matthias Daues | The migration is a required effect of the update. The update preview lists it, and the developer approves both at the approval step of ADR-0023; declining means no update. No script reads both layouts. DEC-17 replaces the preview entry.                                                                    | PROP-03, pass 1 and 2                       |
| DEC-12 | 2026-11-01 | decision   | Matthias Daues | `glossary.md` is one table with the columns Term, Definition, and Avoid, one table per section (see DEC-15). `domain-modeling`, the template, and `GLOSS001` use this form; the migration converts the list form.                                                                                               | PROP-07, PROP-08                            |
| DEC-13 | 2026-11-01 | assumption | Matthias Daues | `capture-context` gains a mode `--fold-context-map`, which turns a context map into domain concerns for the developer to review.                                                                                                                                                                                | PROP-05                                     |
| DEC-14 | 2026-11-01 | decision   | Matthias Daues | The Structurizr theme moves to `docs/assets/themes/`, next to the arc42 images.                                                                                                                                                                                                                                 | PROP-13                                     |
| DEC-15 | 2026-11-01 | decision   | Matthias Daues | A glossary section covers a bounded context or a topic. Every section is a Term/Definition/Avoid table; the migration adds an empty Avoid column to two-column tables.                                                                                                                                          | PROP-16                                     |
| DEC-16 | 2026-11-01 | decision   | Matthias Daues | `publish-docs` puts `docs/spec/glossary.md` into the PDF as chapter 12.                                                                                                                                                                                                                                         | PROP-18                                     |
| DEC-17 | 2026-11-02 | decision   | Matthias Daues | The update moves the files; the developer approves the update, not the move. The new version's `init-factory` runs `migrate-spec-layout` as its last step. A failed migration undoes its moves, and the update rolls back. The fold of routing stays a separate step with `capture-context --fold-context-map`. | PROP-21                                     |
| DEC-18 | 2026-11-02 | decision   | Matthias Daues | The script never stops on two vocabularies. Terms from a `CONTEXT.md` become their own section of `glossary.md`; the script lists terms that appear twice and exits 0. Removing duplicates and cleaning the glossary is a follow-up step for the developer, like the fold of routing.                           | PROP-26                                     |

## Review findings

| ID      | Pass | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Resolution                                                                                                                                                                                                  |
| ------- | ---- | -------- | ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | 1    | major    | 03    | resolved | Lines 262-264 name six scripts with a hard-coded path, but more factory files name an old path. `intent`, `module-graph-check`, `publish-docs`, `test-design-verify`, and `init-factory` do. So do `config/pre-commit-config.yaml` (`arch-lint --docs-dir docs/arc42`), `config/hook-metadata.yaml` (`requires-path:docs/arc42`), and both `config/extensions/*.ts`. 19 test files under `tests/factory/` name old paths, and no criterion covers them. `spec-lint` keeps four use-case checks (`check_use_cases`, `check_traceability`, `check_actor_goal_coverage`, `check_ears`), which the criterion at line 300 needs removed. Lines 265-266 name only the two agents. List every file that changes, so planning can cut stories from it.                                                                                                                                        | Fixed in pass 3. Both hook configurations match `docs/spec/(architecture\|dependency-rules)\.dsl`; the pattern `arc42/\(architecture` and a `pre-commit run --files` criterion cover it.                    |
| PROP-02 | 1    | major    | 03    | resolved | The design does not say how the architecture tools find the DSL once it leaves `docs/arc42/`. `arch-lint` reads `architecture.dsl` and chapter 5 from one `--docs-dir`. `structurizr` mounts the docs folder and reads `/workspace/arc42/architecture.dsl`. `publish-docs` checks `docs/arc42/architecture.dsl` and copies the `arc42/` folder into its build. After the move, the DSL is in `docs/spec/` and the chapters stay in `docs/arc42/`. State each script's new arguments or defaults.                                                                                                                                                                                                                                                                                                                                                                                      | Fixed. `structurizr`, `arch-lint`, and `publish-docs` read the DSL from `docs/spec/` and the chapters from `docs/arc42/`; a criterion builds the PDF after the move.                                        |
| PROP-03 | 1    | major    | 03    | resolved | Lines 256-258 let the developer decline the migration, but the design does not say what the updated factory does then. The new scripts look for the new paths, so the gates of an unmigrated project fail or skip silently. The project's own `.pre-commit-config.yaml` keeps `--docs-dir docs/arc42` and the `files:` patterns, and the design does not name `merge-precommit-config`. State whether the scripts fall back to the old paths, refuse to run, or require the migration.                                                                                                                                                                                                                                                                                                                                                                                                | Fixed in pass 2. The update preview lists the migration as a planned effect, approved at ADR-0023's approval step; declining means no update (DEC-11). No rollback claim remains.                           |
| PROP-04 | 1    | major    | 03    | resolved | Lines 234-236 rewrite links that point at an old path. They do not cover links inside a moved file whose target stays put. The files that move hold 128 relative Markdown links. For example, `docs/spec/todo.md` links to `../reviews/root-cause-...md`, which breaks in `docs/spec/work/`. The links in `supplementary_specs/*.md` break when those files move up one level. State that the script rewrites the relative links inside every moved file, and which files it scans for links to old paths.                                                                                                                                                                                                                                                                                                                                                                            | Fixed. The script also rewrites relative links inside each moved file; a criterion checks `docs/spec/work/todo.md`.                                                                                         |
| PROP-05 | 1    | major    | 03    | resolved | Lines 251-253 and the criterion at lines 314-318 depend on `capture-context --update` turning each context of `CONTEXT-MAP.md` into a domain concern. The skill has no bare `--update` mode. Its `--update --scan` mode derives domain concerns from the scope-map areas (Step 4 and lines 361-400 of its `SKILL.md`) and never reads `CONTEXT-MAP.md`. Section "Factory changes" does not list this skill change. The context "Factory API" has no files, so its concern has no `Read:` path that passes the `CTX-PATHS` check of `concern-lint`.                                                                                                                                                                                                                                                                                                                                    | Fixed. `capture-context` gains `--fold-context-map` (DEC-13); a criterion checks its output with `concern-lint`.                                                                                            |
| PROP-06 | 1    | major    | 01    | resolved | The grep criteria at lines 301-302 and 319-320 cannot pass as written. `migrate-spec-layout` lives in `packages/factory/scripts/` and must name every old path, and `CONTEXT.md` to find the `## Language` section. `capture-context` must name `CONTEXT-MAP.md` to read it (PROP-05). Rows with `<name>` and `<area>` give no literal string to grep for. Name the exclusions and give the exact patterns.                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Fixed in pass 2. `12_glossary.md` left the patterns, because the chapter 12 stub stays; the migration script's tests are excluded.                                                                          |
| PROP-07 | 1    | major    | 03    | resolved | Lines 198-201 fix the glossary's path but not its format. `docs/arc42/12_glossary.md` is a table with terms in bold. The `CONTEXT.md` template has a `## Language` list, and the script moves either one unchanged (lines 241-247). `domain-modeling` writes terms to `docs/CONTEXT.md` under `context-format.md` and `templates/context.md`. The design does not say what replaces the convention and the template, or where the skill writes. `spec-lint` already checks glossary terms (`check_glossary`, finding `GLOSS001`, input `--context CONTEXT.md`), so "none yet" at lines 164 and 285 is not accurate. The design must say where that check reads from.                                                                                                                                                                                                                  | Fixed in pass 2. The `context-map.md` template goes, `context.md` becomes the glossary template, and `context-format.md` describes `glossary.md` and domain concerns.                                       |
| PROP-08 | 1    | minor    | 02    | resolved | `context-format.md` lets a multi-context project keep one `CONTEXT.md` per context, at the place `CONTEXT-MAP.md` names. The grilling skill reads such per-package files. Line 199 puts every context into one `glossary.md`, but the path table (line 218) and the script handle only `docs/CONTEXT.md` and `docs/arc42/CONTEXT.md`. A per-package `CONTEXT.md` is neither moved nor listed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Fixed. Per-context `CONTEXT.md` files with a `## Language` section become sections of `glossary.md`, converted from list to table form (DEC-12).                                                            |
| PROP-09 | 1    | minor    | 02    | resolved | The path table (line 227) and the criterion at line 299 remove the actor-goal list and `use_cases/` anywhere under `docs/`. In this repository they exist only in `docs/~archive/spec/`, 14 files. That folder also keeps an old feature file, its gaps report, its QA strategy, and `traceability.json`. State whether archived copies are in scope. Removing them from the archive defeats its purpose.                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Fixed. Only `actor-goal-list.md` and `use_cases/` are removed, `docs/~archive/` included; the rest of the archive stays.                                                                                    |
| PROP-10 | 1    | minor    | 02    | resolved | The sibling `entity-model-as-dbml.md` still claims this layout. Its first release (line 341) and slice 3 (line 360) include the migration. Its core table (line 173) names `CONTEXT.md` as the vocabulary file. Line 175 allows only `work/` as another folder, so `areas/` has no place. Its criterion at line 413 counts eight single-file core artifacts. DEC-21 there promises a cut. Until then, planning both proposals plans the migration twice. Cut the sibling's layout sections before this proposal is accepted.                                                                                                                                                                                                                                                                                                                                                          | Fixed. `entity-model-as-dbml.md` no longer contains the layout; it points to this proposal.                                                                                                                 |
| PROP-11 | 1    | minor    | 04    | resolved | Every path in `impact.boundaries` resolves, but the list leaves out files the design changes. Missing are the scripts in PROP-01, `merge-precommit-config`, `config/pre-commit-config.yaml`, `config/hook-metadata.yaml`, and `tests/factory/`. The moved sources are missing too: `docs/spec/todos.md`, `docs/CONTEXT.md`, `docs/arc42/CONTEXT-MAP.md`, and `docs/arc42/12_glossary.md`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Fixed in pass 2. Boundaries add `packages/factory/config/pre-commit-config.yaml` and `docs/arc42/themes`.                                                                                                   |
| PROP-12 | 1    | minor    | 07    | resolved | Motivation (lines 120-127) states two facts the repository does not support. No `docs/agent-context/` folder exists; the project has the file `docs/agent-context.md`. `docs/arc42/CONTEXT.md` has 6 references in `packages/factory/`, not 7. The timing argument holds.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Fixed. Motivation names four places and counts 7 occurrences on 6 lines.                                                                                                                                    |
| PROP-13 | 2    | major    | 03    | resolved | `architecture.dsl` loads its theme with `theme themes/default/theme.json`, a path relative to the DSL file. The theme lives in `docs/arc42/themes/default/`, and `scaffold-arc42` copies it there. The path table does not move `themes/`, and the script rewrites Markdown links only. So the theme path breaks when the DSL moves to `docs/spec/`. A `docs/spec/themes/` folder would break the rule that `docs/spec/` holds no other folder. `publish-docs` also copies only `docs/arc42/` into its model build. State where the theme lives and how the DSL finds it.                                                                                                                                                                                                                                                                                                             | Fixed. The theme moves to `docs/assets/themes/` (DEC-14); the path table, the patterns, and the first story's check cover it.                                                                               |
| PROP-14 | 2    | major    | 03    | resolved | The core table names `spec-lint` as the gate for feature files, `validation-rules.md`, `interface-contracts.md`, and `areas/*.md`. `spec-lint` reads no `.feature` file; its Gherkin check sits inside `check_use_cases`. Its only checks on the other three are the business-rule checks `TRACE002` and `TRACE003` in `check_traceability`. Line 303 removes `check_traceability` as one of the four use-case checks, and with it `TRACE004` on the entity model. Name the parts of `check_traceability` that stay, and correct the Gate column.                                                                                                                                                                                                                                                                                                                                     | Fixed. Feature files' gate is `scope-lint` (scope header). Only the checks that read use-case files go; `TRACE002`–`TRACE004` stay.                                                                         |
| PROP-15 | 2    | major    | 01    | resolved | The criteria cannot catch a gate that still looks at an old path. `scope-lint` builds its paths from parts, such as `spec_dir.glob("*.feature")`, and skips a missing file without a message. `spec-lint` `check_todos` skips missing todo files the same way. After the migration, an unchanged `scope-lint` passes and matches no grep pattern. Add a criterion that each gate checks the moved files, for example a test per gate on a fixture in the new layout.                                                                                                                                                                                                                                                                                                                                                                                                                  | Fixed. A criterion seeds an error into each gate's file at its new path and requires the gate to fail.                                                                                                      |
| PROP-16 | 2    | major    | 03    | resolved | The factory's `12_glossary.md` holds four tables with two columns each: the Factory terms, Usage Analysis, Research Vocabulary, and Acronyms and Abbreviations. Its terms are bold, and it has no Avoid column. The script converts only the list form of `CONTEXT.md` and moves chapter 12 as it is. So the criterion that `glossary.md` is one table with Term, Definition, and Avoid fails on the factory's own migration. Research Vocabulary and Acronyms are not bounded contexts, so DEC-12 gives them no section. State whether the script converts the arc42 table and where these two sections go.                                                                                                                                                                                                                                                                          | Fixed in pass 3. The script renames two-column tables to Term and Definition and adds Avoid; a section without a table stays in chapter 12 below the link.                                                  |
| PROP-17 | 2    | minor    | 03    | resolved | `capture-context --update --scan` takes domain concerns from scope-map areas only. It offers to remove every concern the rescan does not find (its `SKILL.md`, Step 4 and lines 394-465). The bounded contexts Factory, Usage Analysis, and Factory API are not scope-map areas. So the first rescan after `--fold-context-map` offers to remove every folded concern. State how context concerns relate to scope-map areas, and whether the rescan keeps them.                                                                                                                                                                                                                                                                                                                                                                                                                       | Fixed. The fold marks its concerns, and `--update --scan` keeps them; a criterion checks it.                                                                                                                |
| PROP-18 | 2    | minor    | 01    | resolved | The criterion that `publish-docs` builds the factory's PDF fails today and after the migration. The factory has no `docs/publish-docs.yaml`. Without it, the assembler prints a starter manifest and exits 2. The design also does not say whether the PDF's chapter 12 becomes the one-line stub or shows `docs/spec/glossary.md`. Name the manifest as a deliverable or drop the criterion, and state what the PDF shows as its glossary.                                                                                                                                                                                                                                                                                                                                                                                                                                           | Fixed in pass 3. `publish-docs` renders `docs/spec/glossary.md` wherever a manifest selects `arc42/12_glossary.md`; the fixture gains a chapter 12 with one term.                                           |
| PROP-19 | 2    | minor    | 03    | resolved | The factory's `docs/CONTEXT.md` holds no terms. It is an 11-line pointer to chapter 12 and to `CONTEXT-MAP.md`. The script leaves it in place, and `--fold-context-map` reads only the context map. Line 279 has the developer delete "the old file", which names one file. No step or criterion removes `docs/CONTEXT.md`, yet line 210 says it no longer exists after the move. Name the step that deletes a routing-only `CONTEXT.md`, and add it to a criterion.                                                                                                                                                                                                                                                                                                                                                                                                                  | Fixed. `--fold-context-map` also reads a routing-only `CONTEXT.md`; a criterion checks that neither old file exists afterwards.                                                                             |
| PROP-20 | 2    | minor    | 03    | resolved | The migration is a required step, and declining it cancels the update. The design does not say how `update-factory` decides that a project still needs the migration. A project already in the new layout, or one without `docs/spec/`, must not be asked on every later update. State the test that `update-factory` uses, and add a criterion for a project that is already migrated.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Fixed in pass 3. The design names the paths that trigger the script and leaves out `scope-map.md`, the chapter 12 link, and the files the fold removes.                                                     |
| PROP-21 | 3    | major    | 03    | resolved | The update that ships this layout runs the installed `update-factory`, which is the old version. It shows the preview and asks for approval before it downloads the new version (`update-factory` lines 485-519, ADR-0023 step 2). It never runs code from the new version. So that update neither lists nor runs the migration, and it installs the new scripts and hooks on the old layout. DEC-11 rules out exactly that state. State how the first update reaches the migration.                                                                                                                                                                                                                                                                                                                                                                                                  | Fixed in pass 3. The new `init-factory`, which every update runs, runs the script as its last step; a failed migration undoes its moves, and the update rolls back (DEC-17).                                |
| PROP-22 | 3    | minor    | 03    | resolved | No step fixes the links to the files the developer deletes after `--fold-context-map`. `docs/arc42/concepts.md:69` links to `CONTEXT-MAP.md`, and so does the Referenced from section of the glossary, which the script moves. Two more files under `docs/proposals/implemented/` and `docs/reviews/` link to `CONTEXT.md` or `CONTEXT-MAP.md`. The script leaves both targets in place, so its link rewrite never touches these links. The link-check criterion at line 369 runs before the deletion, and the hook checks only changed files. Name the step that rewrites or removes these links.                                                                                                                                                                                                                                                                                    | Fixed in pass 3. `--fold-context-map` rewrites links to the two files to `docs/agent-context.md`; a criterion runs `link-check` on all of `docs/` after the deletion.                                       |
| PROP-23 | 3    | minor    | 03    | resolved | `GLOSS001` cannot report a term once the glossary lives in `docs/spec/`. `check_glossary` reads every Markdown file under the spec folder as the specification (`spec-lint` line 562). After the move, that includes `glossary.md`, where every term appears in its own row. It also includes `work/`, so a term used only in a gaps report counts as used. State which files `GLOSS001` reads as the specification.                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Fixed in pass 3. `GLOSS001` reads terms from the table and does not count `glossary.md` or `work/` as uses; a criterion checks it.                                                                          |
| PROP-24 | 3    | minor    | 03    | resolved | `TRACE002` is an error only while `docs/spec/use_cases/` exists (`spec-lint` line 335). Otherwise it is a warning, and `spec-lint` fails only on errors. The design removes the use-case files and keeps `TRACE002`. So after the move, a business rule that is referenced but never defined no longer blocks a commit in any project. State the severity that `TRACE002` keeps.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Fixed in pass 3. `TRACE002` stays an error without `use_cases/`; a criterion requires exit code 1.                                                                                                          |
| PROP-25 | 4    | major    | 03    | resolved | `init-factory` runs `migrate-spec-layout` as its last step on every run (lines 305-307 and 350), not only inside an update. A first install also runs `init-factory`, and so does the `init-factory` skill. On a first install, the script moves files the project owns, such as its own `docs/CONTEXT.md`, `docs/spec/*.feature`, or `docs/arc42/architecture.dsl`. The `init-factory` skill promises that the script never disturbs what the project owns, and that `remove-factory` undoes everything it adds (`skills/init-factory/SKILL.md` line 11). The glossary term Consent-Gated Mutation requires separate consent for every change during installation (`12_glossary.md` line 54). DEC-17 covers updates only. State when `init-factory` runs the script, for example only when the install record shows an earlier factory version. Add a criterion for a first install. | Fixed in pass 4. `init-factory` runs the script only when `install.json` records a version older than the layout release; a first install moves nothing and lists old paths. A criterion covers both cases. |
| PROP-26 | 4    | major    | 03    | resolved | The design does not say how the stop on two glossaries ends (lines 284-286, criterion at line 410). It gives no exit code. It does not say whether the script has moved the other files when it stops, or whether chapter 12 counts as an existing glossary. Under DEC-17 the exit code decides the update. A non-zero exit rolls the update back, so the project cannot update until the developer merges by hand. Exit 0 leaves the new factory on a layout that is only partly moved, which DEC-11 rules out. The case is common: `scaffold-arc42` creates `12_glossary.md`, and `domain-modeling` writes terms to `docs/CONTEXT.md` under `## Language`. State the exit code, what the script has moved when it stops, and what the update does then.                                                                                                                             | Fixed in pass 4. The script never stops: terms from `CONTEXT.md` become their own section, it lists duplicates and exits 0, and cleaning the glossary is a follow-up step (DEC-18).                         |
| PROP-27 | 4    | minor    | 03    | resolved | After the migration succeeds, `update-factory` refreshes the factory hooks only on a second, separate yes (`refresh_precommit_hooks`, `update-factory` lines 417-484). A developer who declines keeps the old `files:` pattern of the `arch-lint` hook, which matches `docs/arc42/architecture.dsl`. The DSL has moved by then, so `arch-lint` no longer runs when `docs/spec/architecture.dsl` changes, and nothing reports it. Lines 325-326 keep hooks consistent with the layout only for a failed migration. The criterion at lines 397-398 covers a fresh install from the template, not an update. State whether the hook refresh is part of the approved update when the layout moves, and add the update case to the criterion.                                                                                                                                              | Fixed in pass 4. The script rewrites the old paths in the factory's `agent_factory_hook-*` block, without a question; a criterion checks the hooks after an update.                                         |
| PROP-28 | 4    | minor    | 03    | resolved | Lines 339-341 say the `arch-lint` hook matches `docs/spec/(architecture\|dependency-rules)\.dsl` "instead of the old `docs/arc42/` paths". The old pattern holds two such paths: `architecture.dsl` and `05_building_block_view.md`. `arch-lint` compares chapter 5 with the DSL (`arch-lint` lines 7-9 and 347-363), and chapter 5 stays in `docs/arc42/`. Read as written, the change drops the chapter 5 trigger, so an edit to chapter 5 no longer runs `arch-lint`. State that the pattern keeps `docs/arc42/05_building_block_view.md`.                                                                                                                                                                                                                                                                                                                                         | Fixed in pass 4. Only the DSL paths change; the text gives the full regex with chapter 5, `assets/images/`, and `adr/` kept.                                                                                |
| PROP-29 | 5    | minor    | 03    | fixed    | `init-factory` tells an update from a first install by the `factory_version` in `install.json` (lines 325-330). The design does not say what happens when that key is missing or reads `unknown`. `init-factory` writes the key only since commit `08de90af` of 2026-09-07. `_read_factory_version` returns `unknown` when `factory/VERSION` is missing (`init-factory` lines 244-250). If `init-factory` treats such a project like a first install, the update leaves the new factory on the old layout. DEC-11 rules out that state. State how `init-factory` treats a record without a usable version, and add that case to the criterion at lines 434-436.                                                                                                                                                                                                                       | Fixed in pass 5. An `install.json` without a usable `factory_version` counts as older; only a missing `install.json` is a first install. A criterion covers the case.                                       |
| PROP-30 | 5    | minor    | 03    | fixed    | Line 297 has the script rewrite the old paths in the `agent_factory_hook-*` block. The only old path in that block sits inside the `files:` regex of the `arch-lint` hook: `^docs/(arc42/(architecture\.dsl\|05_building_block_view\.md)\|assets/images/.*\|adr/.*\.md)$` (`config/pre-commit-config.yaml` line 103). The string `docs/arc42/architecture.dsl` does not occur in it, so a path substitution finds nothing to rewrite. Then the criterion at lines 437-439 fails. State the rule for this hook. For example, the script replaces the `files:` value with the pattern from "Factory changes" when it equals the old template pattern, and lists it otherwise.                                                                                                                                                                                                           | Fixed in pass 5. The script sets each factory hook's `files:` value to the template's value instead of substituting paths; the hook criterion checks the result.                                            |
| PROP-31 | 5    | minor    | 03    | fixed    | Pass 4 changed the script from moving a `CONTEXT.md` to moving its terms (lines 288-291). The design no longer says what happens to the rest of the file. A file from the template keeps its title, its description, and possibly an empty `## Language` heading. If that heading stays, the file still counts as work for the script (line 337) and is not routing-only (line 291). Then `--fold-context-map` skips it, and no step deletes it. Yet line 223 says `CONTEXT.md` does not exist after the move. State that the script removes the `## Language` section from the source file. Add a criterion that the file has no such section afterwards.                                                                                                                                                                                                                            | Fixed in pass 5. The script removes the `## Language` section after moving the terms, so the file holds routing only and the fold handles it; a criterion checks it.                                        |

## Review passes

| Pass | Date       | Reviewed commit                          | Disposition | Failed checks      | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---- | ---------- | ---------------------------------------- | ----------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | 2026-11-01 | c7f4476bbe1f53917325f259a477e1b1a823a08d | findings    | 01, 02, 03, 04, 07 | Checks 05, 06, and 08 pass: every boundary resolves, the proposal has no open questions, and the estimate says `unknown` openly. The design leaves out many files that name old paths, the new interface of the architecture tools, the declined-migration case, link rebasing inside moved files, and the glossary's format. Two grep criteria fail on the migration script itself, and the sibling proposal still claims the layout.                           |
| 2    | 2026-11-01 | 8d89accbcd58470b7c7eb04cb4984916f9aacd40 | findings    | 01, 03, 04         | Checks 02 and 05 to 08 pass, and seven pass-1 findings are resolved. PROP-01, PROP-03, PROP-06, PROP-07, and PROP-11 are open again: the hook template, the decline path, two grep patterns, and the context convention remain. Eight new findings cover the DSL theme, the `spec-lint` gates, gates that pass on old paths, the factory glossary's form, rescans, the PDF manifest, the routing-only `CONTEXT.md`, and the migration check in `update-factory`. |
| 3    | 2026-11-02 | 551be07aacd24c931057727c186d4ecbca4135de | findings    | 01, 03             | Checks 02 and 04 to 08 pass, and nine pass-2 fixes are resolved. PROP-01, PROP-16, PROP-18, and PROP-20 are open again: a stale hook trigger, two glossary sections that are not Term tables, the source of the PDF glossary, and a migration check that never turns off. Four new findings cover the first update running old code, links to the deleted context files, `GLOSS001` reading the glossary itself, and the severity of `TRACE002`.                 |
| 4    | 2026-11-02 | ab9b365aa1f007be11c8cf7dbfc8b7d3caed7cac | findings    | 03                 | Checks 01, 02, and 04 to 08 pass, and all eight pass-3 fixes are resolved. Two new major findings concern `init-factory`: it runs the script on a first install too, and the design does not say how the stop on two glossaries ends an update. Two minor findings concern the `arch-lint` hook: a declined hook refresh after the move, and the dropped chapter 5 trigger.                                                                                      |
| 5    | 2026-11-02 | 5b229c0904bf55845850bce2d0fe05823095053f | findings    | 03                 | Checks 01, 02, and 04 to 08 pass, and all four pass-4 fixes are resolved. Three new minor findings concern edge cases of the migration: an install record without a usable version, a hook path that sits inside a regex, and the rest of a `CONTEXT.md` after its terms move.                                                                                                                                                                                   |
