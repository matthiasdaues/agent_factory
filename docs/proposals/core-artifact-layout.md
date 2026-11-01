---
schema_version: 2
title: Core Artifact Layout
status: open
owner: Matthias Daues
created: 2026-11-01
updated: 2026-11-01
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
and how its parts fit together. Today these files sit in five folders. The
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

The update tool offers the script and runs it only after the developer
confirms. When a project keeps terms both in the old vocabulary file and in a
glossary, the script stops and lists both, so the developer can merge them.

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

The factory spreads a project's specification over five places:
`docs/spec/`, `docs/spec/supplementary_specs/`, `docs/arc42/`, `docs/`, and
`docs/agent-context/`. `docs/spec/` mixes sources such as `scope-map.md` with
working output such as `*-gaps.md` and `prd.md`. The factory's own files
refer to `CONTEXT.md` at two paths, `docs/CONTEXT.md` (67 references) and
`docs/arc42/CONTEXT.md` (7). The convention `context-format.md` names one
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
- **The move is mechanical and confirmed.** A script moves files and rewrites
  links the same way in every project, and only after the developer confirms.

## Design

### The core artifact set

A project's specification core is a set of files with three marks (DEC-02).
People edit them by hand. Every other artifact derives from them or is checked
against them. A gate checks them or should check them. ADRs are not core. They
record decisions and stay in `docs/adr/` (DEC-03).

| File                     | Holds                                        | Gate                       |
| ------------------------ | -------------------------------------------- | -------------------------- |
| `scope-map.md`           | What the system does, by domain area         | `scope-lint`               |
| `features/*.feature`     | Behaviour, as Rules per actor goal           | `spec-lint`                |
| `entity-model.md`        | Tables, keys, constraints, enums             | none yet                   |
| `state-machines.md`      | States and transitions                       | `statemachine-lint`        |
| `validation-rules.md`    | Rules on input and on data                   | `spec-lint`                |
| `interface-contracts.md` | Contracts at the system's boundaries         | `spec-lint`                |
| `architecture.dsl`       | Building blocks, views, deployment           | `arch-lint`, `structurizr` |
| `dependency-rules.dsl`   | Allowed dependencies between building blocks | `dependency-check`         |
| `schemas/*`              | Structure inside payload columns             | none yet                   |
| `areas/*.md`             | One subsystem's specification in depth       | `spec-lint`                |
| `glossary.md`            | The domain vocabulary all of the above uses  | none yet                   |

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
`docs/spec/architecture.dsl`. `testing.yaml` and `agent-context.md` stay in
`docs/`, because neither specifies the system. `testing.yaml` is derived from
code, and `agent-context.md` routes agents.

The actor-goal list and the use-case files belong to the factory's earlier
specification method, which the scope map and the feature files replaced. No factory step produces them (ST-0098), and
they do not fit the scope map and feature files. So the move removes them
(DEC-10).

### Routing and vocabulary

`docs/agent-context.md` is the project's one routing file (DEC-07). Each
bounded context becomes a domain concern in it, with its description and
`Read:` paths. The domain concerns also route to the glossary. After the
move, `CONTEXT.md` and `CONTEXT-MAP.md` do not exist.

The term definitions live in `docs/spec/glossary.md`, a core file. A project
with several bounded contexts keeps one section per context in that file. In
a project with arc42, chapter `12_glossary.md` keeps one line that links to
`docs/spec/glossary.md`.

### Path table

The table lists every move the layout makes.

| Old path                                                   | New path                                                             |
| ---------------------------------------------------------- | -------------------------------------------------------------------- |
| `docs/spec/scope-map.md`                                   | unchanged                                                            |
| `docs/spec/<name>.feature`                                 | `docs/spec/features/<name>.feature`                                  |
| `docs/spec/supplementary_specs/entity-model.md`            | `docs/spec/entity-model.md`                                          |
| `docs/spec/supplementary_specs/state-machines.md`          | `docs/spec/state-machines.md`                                        |
| `docs/spec/supplementary_specs/validation-rules.md`        | `docs/spec/validation-rules.md`                                      |
| `docs/spec/supplementary_specs/interface-contracts.md`     | `docs/spec/interface-contracts.md`                                   |
| `docs/arc42/architecture.dsl`                              | `docs/spec/architecture.dsl`                                         |
| `docs/arc42/dependency-rules.dsl`                          | `docs/spec/dependency-rules.dsl`                                     |
| `docs/arc42/12_glossary.md`                                | `docs/spec/glossary.md`; chapter 12 links to it                      |
| `docs/CONTEXT.md`, `docs/arc42/CONTEXT.md`                 | terms to `docs/spec/glossary.md`, routing to `docs/agent-context.md` |
| `docs/arc42/CONTEXT-MAP.md`                                | domain concerns in `docs/agent-context.md`                           |
| `docs/spec/prd.md`                                         | `docs/spec/work/prd.md`                                              |
| `docs/spec/<name>-gaps.md`                                 | `docs/spec/work/<name>-gaps.md`                                      |
| `docs/spec/<name>-qa-strategy.md`                          | `docs/spec/work/<name>-qa-strategy.md`                               |
| `docs/spec/SPEC-UPDATE-SUMMARY.md`                         | `docs/spec/work/SPEC-UPDATE-SUMMARY.md`                              |
| `docs/spec/todo.md`, `docs/spec/todos.md`                  | `docs/spec/work/todo.md`, `docs/spec/work/todos.md`                  |
| `docs/spec/supplementary_specs/<area>.md`                  | `docs/spec/areas/<area>.md`                                          |
| `docs/spec/supplementary_specs/<area>-qa-strategy.md`      | `docs/spec/work/<area>-qa-strategy.md`                               |
| `actor-goal-list.md`, `use_cases/`, anywhere under `docs/` | removed                                                              |

### The migration script

`packages/factory/scripts/migrate-spec-layout` moves an installed project's
files with `git mv`, following the path table (DEC-06). It removes the files
that the path table marks as removed with `git rm`, so the git history keeps
them. It rewrites the local Markdown links that point at an old path. A
Markdown link to a removed file becomes its link text in a code span, so
`link-check` still passes. The script lists every other occurrence of an old
path, for example in CI files or scripts, for the developer to fix. It never
rewrites those occurrences. `--dry-run` prints the moves and rewrites without
making them.

The script moves `docs/arc42/12_glossary.md` to `docs/spec/glossary.md` and
writes a new chapter 12 with one line that links to it. A `CONTEXT.md` holds
terms when it has a `## Language` section, as the
[`CONTEXT.md` template](../../packages/factory/rulebooks/templates/context.md)
defines. The script moves such a file to `docs/spec/glossary.md` when no
glossary exists. When a glossary exists too, the script stops and lists
both files for the developer to merge. A `CONTEXT.md` without a `## Language` section
holds routing only and does not stop the script.

Folding routing into `agent-context.md` is not mechanical, so the script
leaves `CONTEXT-MAP.md` and any routing in `CONTEXT.md` in place. It names
`capture-context --update` as the next step. That skill turns each listed
context into a domain concern. Then the developer deletes the old file
(DEC-08).

`update-factory` offers the script and runs it only after the developer
confirms (DEC-04). The factory's own repository moves first, with the same
script.

### Factory changes

Every factory script, agent, skill, playbook, and template that names an old
path names the new one. The scripts with a hard-coded path are
`structurizr`, `arch-lint`, `dependency-check`, `spec-lint`, `scope-lint`,
and `statemachine-lint`. `developer-agent` and `reconciliation-agent` lose
their fallback to the use-case files (DEC-10).

## Scope

**In the first release:**

- The layout in `docs/spec/`, with `features/`, `schemas/`, `areas/`, and
  `work/`.
- The actor-goal list and the use-case files removed, and the use-case
  fallbacks removed from `developer-agent` and `reconciliation-agent`.
- The migration script, offered by `update-factory`.
- Every factory reference updated to the new paths.
- The factory's own repository migrated.

**Explicitly deferred (do NOT plan stories for these):**

- **DBML and its gates.** They belong to
  [entity-model-as-dbml.md](entity-model-as-dbml.md), which builds on this
  layout.
- **A gate for `glossary.md`.** No check for a glossary has been designed.
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
  the factory's own repository, and `grep -rE 'UC-XX|use_cases|actor-goal-list' packages/factory/` finds nothing outside `CHANGELOG.md` and `reports/`.
- For every old path in a path-table row that moves a file,
  `grep -r <old path> packages/factory/` finds nothing outside `CHANGELOG.md`.
- `link-check`, `arch-lint`, `structurizr validate`, `dependency-check`,
  `spec-lint`, `scope-lint`, and `statemachine-lint` pass on the factory's
  own repository after its migration.
- `migrate-spec-layout --dry-run` on a copy of an installed project changes
  no file and prints every planned move.
- `migrate-spec-layout` on a copy of an installed project moves its files,
  leaves `link-check` passing, and lists each old path found outside
  Markdown.
- On a project with a `CONTEXT.md` that holds terms and an existing
  glossary, the script stops and lists both before it moves either one.
- The factory's own migration runs without stopping, because its
  `docs/CONTEXT.md` has no `## Language` section. After the migration and the
  `capture-context --update` run that follows it,
  `docs/spec/glossary.md` holds the terms of the old
  `docs/arc42/12_glossary.md`, `docs/agent-context.md` has one domain
  concern per context of the old `CONTEXT-MAP.md`, and `concern-lint` passes.
- `grep -rE 'CONTEXT(-MAP)?\.md' packages/factory/` finds nothing outside
  `CHANGELOG.md`.
- `update-factory` offers the migration and runs it only after the developer
  confirms.

## Guiding Rule

A newcomer who opens `docs/spec/` sees every source file and nothing else at
the top.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by     | Decision                                                                                                                                                                                                                                          | Raised by                                   |
| ------ | ---------- | -------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| DEC-01 | 2026-11-01 | decision | Matthias Daues | The layout is its own proposal and ships before the entity-model proposal, which builds on it.                                                                                                                                                    | PROP-11 of `entity-model-as-dbml.md`        |
| DEC-02 | 2026-10-30 | decision | Matthias Daues | The core is the set of files people edit by hand, that other artifacts derive from or are checked against, and that a gate checks or should check. It lives in `docs/spec/`, with feature files in `features/` and payload schemas in `schemas/`. | DEC-08, DEC-13 of `entity-model-as-dbml.md` |
| DEC-03 | 2026-10-30 | decision | Matthias Daues | ADRs are not core and stay in `docs/adr/`.                                                                                                                                                                                                        | DEC-07 of `entity-model-as-dbml.md`         |
| DEC-04 | 2026-10-30 | decision | Matthias Daues | Installed projects move through a migration script that `update-factory` offers and runs only after the developer confirms. It rewrites Markdown links, lists other hits without changing them, and has `--dry-run`.                              | DEC-09 of `entity-model-as-dbml.md`         |
| DEC-05 | 2026-10-30 | decision | Matthias Daues | Working output lives in `docs/spec/work/`.                                                                                                                                                                                                        | DEC-12 of `entity-model-as-dbml.md`         |
| DEC-06 | 2026-11-01 | decision | Matthias Daues | The migration script is named `migrate-spec-layout`.                                                                                                                                                                                              | Draft                                       |
| DEC-07 | 2026-11-01 | decision | Matthias Daues | `docs/agent-context.md` is the one routing file; `CONTEXT.md` and `CONTEXT-MAP.md` fold into its domain concerns. Term definitions live in the core file `docs/spec/glossary.md`.                                                                 | Open Question 1, `CONTEXT-MAP.md`           |
| DEC-08 | 2026-11-01 | decision | Matthias Daues | The script moves terms to `glossary.md` but leaves routing to `capture-context --update`, because folding routing into domain concerns needs judgment.                                                                                            | Draft, follows DEC-07                       |
| DEC-09 | 2026-11-01 | decision | Matthias Daues | `todo.md` and `todos.md` move to `docs/spec/work/`; merging them is a separate todo. Area specs move to `docs/spec/areas/`, their QA strategies to `work/`. A project may fold an area spec into the single-file core artifacts later.            | Open Question 1                             |
| DEC-10 | 2026-11-01 | decision | Matthias Daues | The actor-goal list and the use-case files are removed, along with the agents' use-case fallbacks. They do not fit the scope map and feature files.                                                                                               | Open Question 1                             |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
