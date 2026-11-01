---
schema_version: 2
title: Core Artifact Layout
status: draft
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

Written by `write-primer` once the design is settled.

## Summary

All of a project's specification core lives in `docs/spec/`, and nothing
else lives at the top of that folder. Feature files live in
`docs/spec/features/`, payload schemas in `docs/spec/schemas/`, and the
working output that agents write in `docs/spec/work/`. A migration script
moves an installed project into this layout. The question the layout answers
is one a newcomer cannot answer today: which files are the source, and where
are they?

## Motivation

The factory spreads a project's specification over five places:
`docs/spec/`, `docs/spec/supplementary_specs/`, `docs/arc42/`, `docs/`, and
`docs/agent-context/`. `docs/spec/` mixes sources such as `scope-map.md` with
working output such as `*-gaps.md` and `prd.md`. The factory's own files
refer to `CONTEXT.md` at two paths, `docs/CONTEXT.md` (67 references) and
`docs/arc42/CONTEXT.md` (7). The convention `context-format.md` names one
path, and the `grilling` and `domain-modeling` skills name the other. Two
files route agents: `agent-context.md` and `CONTEXT-MAP.md`. The factory
refers to the todo list as both `todo.md` and
`todos.md`.

T-0006 asked for one canonical entity-model path across all scenarios. The
proposal [entity-model-as-dbml.md](entity-model-as-dbml.md) needs that path
for its DBML file. It was split off this proposal so that each can be
reviewed on its own, and it builds on this layout (DEC-01).

## Core Principles

- **One root for the core.** Every core file lives in `docs/spec/`.
- **Nothing else at the top.** A file at the top of `docs/spec/` is a core
  file. Folders hold the rest.
- **The move is mechanical and confirmed.** A script moves files and rewrites
  links the same way in every project, and only after the developer confirms.

## Design

### The core artifact set

A project's specification core is the set of files that people edit by hand,
that every other artifact derives from or is checked against, and that a gate
checks or should check (DEC-02). ADRs are not core; they are a record of
decisions and stay in `docs/adr/` (DEC-03).

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
| `glossary.md`            | The domain vocabulary all of the above uses  | none yet                   |

The entity-model proposal replaces `entity-model.md` with
`entity-model.dbml` and adds gates for it and for `schemas/`.

Working output that agents write while they derive or review the core lives
in `docs/spec/work/`: gaps reports, QA strategies, `prd.md`, and update
summaries (DEC-05). The arc42 prose stays in `docs/arc42/` and refers to
`docs/spec/architecture.dsl`. `testing.yaml` and `agent-context.md` stay in
`docs/`: the first is derived from code, and the second routes agents rather
than specifying the system.

### Routing and vocabulary

`docs/agent-context.md` is the project's one routing file (DEC-07). It
absorbs the two files that routed before it. `CONTEXT-MAP.md` listed the
bounded contexts and where their documents live; each context becomes a
domain concern in `agent-context.md`, with its description and `Read:` paths.
`CONTEXT.md` pointed at the glossary; the domain concerns now route there.
Neither file exists after the move.

The term definitions live in `docs/spec/glossary.md`, a core file. A project
with several bounded contexts keeps one section per context in that file. In
a project with arc42, chapter `12_glossary.md` keeps one line that links to
`docs/spec/glossary.md`.

### Path table

Every move the layout makes:

| Old path                                               | New path                                                             |
| ------------------------------------------------------ | -------------------------------------------------------------------- |
| `docs/spec/scope-map.md`                               | unchanged                                                            |
| `docs/spec/<name>.feature`                             | `docs/spec/features/<name>.feature`                                  |
| `docs/spec/supplementary_specs/entity-model.md`        | `docs/spec/entity-model.md`                                          |
| `docs/spec/supplementary_specs/state-machines.md`      | `docs/spec/state-machines.md`                                        |
| `docs/spec/supplementary_specs/validation-rules.md`    | `docs/spec/validation-rules.md`                                      |
| `docs/spec/supplementary_specs/interface-contracts.md` | `docs/spec/interface-contracts.md`                                   |
| `docs/arc42/architecture.dsl`                          | `docs/spec/architecture.dsl`                                         |
| `docs/arc42/dependency-rules.dsl`                      | `docs/spec/dependency-rules.dsl`                                     |
| `docs/arc42/12_glossary.md`                            | `docs/spec/glossary.md`; chapter 12 links to it                      |
| `docs/CONTEXT.md`, `docs/arc42/CONTEXT.md`             | terms to `docs/spec/glossary.md`, routing to `docs/agent-context.md` |
| `docs/arc42/CONTEXT-MAP.md`                            | domain concerns in `docs/agent-context.md`                           |
| `docs/spec/prd.md`                                     | `docs/spec/work/prd.md`                                              |
| `docs/spec/<name>-gaps.md`                             | `docs/spec/work/<name>-gaps.md`                                      |
| `docs/spec/<name>-qa-strategy.md`                      | `docs/spec/work/<name>-qa-strategy.md`                               |
| `docs/spec/SPEC-UPDATE-SUMMARY.md`                     | `docs/spec/work/SPEC-UPDATE-SUMMARY.md`                              |

Open Question 1 settles the files this table does not yet place.

### The migration script

`packages/factory/scripts/migrate-spec-layout` moves an installed project's
files with `git mv`, following the path table. It rewrites the local Markdown
links that point at an old path. It lists every other occurrence of an old
path, for example in CI files or scripts, for the developer to fix; it never
rewrites those. `--dry-run` prints the moves and rewrites without making
them.

Folding routing into `agent-context.md` is not mechanical. The script moves a
`CONTEXT.md` that holds terms to `docs/spec/glossary.md` when no glossary
exists yet; otherwise it stops and lists both files for the developer to
merge. It leaves `CONTEXT-MAP.md` and any routing in `CONTEXT.md` in place
and names `capture-context --update` as the next step. That skill turns each
listed context into a domain concern; the developer then deletes the old
file (DEC-08).

`update-factory` offers the script and runs it only after the developer
confirms (DEC-04). The factory's own repository moves first, with the same
script.

### Factory changes

Every factory script, agent, skill, playbook, and template that names an old
path names the new one. The scripts with a hard-coded path are
`structurizr`, `arch-lint`, `dependency-check`, `spec-lint`, `scope-lint`,
and `statemachine-lint`.

## Scope

**In the first release:**

- The layout in `docs/spec/`, with `features/`, `schemas/`, and `work/`.
- The migration script, offered by `update-factory`.
- Every factory reference updated to the new paths.
- The factory's own repository migrated.

**Explicitly deferred (do NOT plan stories for these):**

- **DBML and its gates.** They belong to
  [entity-model-as-dbml.md](entity-model-as-dbml.md), which builds on this
  layout.
- **A gate for `glossary.md`.** No check for a glossary has been designed.

## Open Questions

1. **Files without a home.** The path table does not place `todo.md`,
   `todos.md`, and the area specs in `supplementary_specs/`, such as `mechanized-dispatch.md` with
   its QA strategy. Raised by PROP-06 of the entity-model proposal.
   `use_cases/` and `actor-goal-list.md` need no home: the first is archived
   in `~archive/`, and no factory step produces the second since ST-0098.

## Completion Criteria

- After the factory's own migration, `docs/spec/` holds only the core files
  of the table at its top, plus the folders `features/`, `schemas/`, and
  `work/`.
- For every old path in the path table,
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
- After the factory's own migration, `docs/spec/glossary.md` holds the terms
  of `docs/arc42/12_glossary.md`, `docs/agent-context.md` has one domain
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

| ID     | Date       | Kind       | Decided by     | Decision                                                                                                                                                                                                                                          | Raised by                                   |
| ------ | ---------- | ---------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| DEC-01 | 2026-11-01 | decision   | Matthias Daues | The layout is its own proposal and ships before the entity-model proposal, which builds on it.                                                                                                                                                    | PROP-11 of `entity-model-as-dbml.md`        |
| DEC-02 | 2026-10-30 | decision   | Matthias Daues | The core is the set of files people edit by hand, that other artifacts derive from or are checked against, and that a gate checks or should check. It lives in `docs/spec/`, with feature files in `features/` and payload schemas in `schemas/`. | DEC-08, DEC-13 of `entity-model-as-dbml.md` |
| DEC-03 | 2026-10-30 | decision   | Matthias Daues | ADRs are not core and stay in `docs/adr/`.                                                                                                                                                                                                        | DEC-07 of `entity-model-as-dbml.md`         |
| DEC-04 | 2026-10-30 | decision   | Matthias Daues | Installed projects move through a migration script that `update-factory` offers and runs only after the developer confirms. It rewrites Markdown links, lists other hits without changing them, and has `--dry-run`.                              | DEC-09 of `entity-model-as-dbml.md`         |
| DEC-05 | 2026-10-30 | decision   | Matthias Daues | Working output lives in `docs/spec/work/`.                                                                                                                                                                                                        | DEC-12 of `entity-model-as-dbml.md`         |
| DEC-06 | 2026-11-01 | assumption | Matthias Daues | The migration script is named `migrate-spec-layout`.                                                                                                                                                                                              | Draft                                       |
| DEC-07 | 2026-11-01 | decision   | Matthias Daues | `docs/agent-context.md` is the one routing file; `CONTEXT.md` and `CONTEXT-MAP.md` fold into its domain concerns. Term definitions live in the core file `docs/spec/glossary.md`.                                                                 | Open Question 1, `CONTEXT-MAP.md`           |
| DEC-08 | 2026-11-01 | assumption | Matthias Daues | The script moves terms to `glossary.md` but leaves routing to `capture-context --update`, because folding routing into domain concerns needs judgment.                                                                                            | Draft, follows DEC-07                       |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
