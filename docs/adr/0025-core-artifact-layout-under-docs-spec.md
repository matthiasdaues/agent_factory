---
id: 0025
status: accepted
evaluation: none
---

# Core artifact layout under `docs/spec/`

## Context

A developer who opens a factory project looks for the files that specify the
system. The factory spreads these files over four places: `docs/spec/`,
`docs/spec/supplementary_specs/`, `docs/arc42/`, and `docs/`. `docs/spec/`
also holds the reports that agents write while they work, such as
`*-gaps.md` and `prd.md`. So a newcomer cannot tell which files are the
source.

Vocabulary and routing have the same problem. Factory files name
`CONTEXT.md` at two paths, `docs/CONTEXT.md` and `docs/arc42/CONTEXT.md`. Two
files tell agents what to read: `docs/agent-context.md` and
`docs/arc42/CONTEXT-MAP.md`. The terms live in chapter 12 and in each
`CONTEXT.md`.

The proposal [entity-model-as-dbml.md](../proposals/entity-model-as-dbml.md)
needs one fixed path for its DBML file in every project. It builds on this
layout, so the layout ships first (DEC-01).

The accepted proposal [core-artifact-layout.md](../proposals/core-artifact-layout.md)
settles the options. The rejected options are:

- **ADRs as core files.** ADRs record why a decision was made. Nothing
  derives from them, and no gate checks them against the system. They stay in
  `docs/adr/` (DEC-03).
- **Area specs at the top of `docs/spec/`.** The top would then hold a
  different set of files in every project, and the move would stop being
  mechanical. Area specs get their own folder (DEC-09).
- **One merged todo list now.** The merge changes an ID scheme and its
  references. Todo T-0008 tracks it (DEC-09).
- **The glossary as chapter 12 or in `CONTEXT.md`.** Chapter 12 exists only
  in projects with arc42, and `CONTEXT.md` exists at two paths. The glossary
  needs one path in every project (DEC-07).

`evaluation: none`, because the proposal decided each point and no open
alternative is left to weigh.

## Decision

A project's specification core lives in `docs/spec/`. A core file has three
marks: people edit it by hand, other artifacts derive from it or are checked
against it, and a gate checks it or should check it (DEC-02).

The top of `docs/spec/` holds only the single-file core artifacts:
`scope-map.md`, `entity-model.md`, `state-machines.md`, `validation-rules.md`,
`interface-contracts.md`, `architecture.dsl`, `dependency-rules.dsl`, and
`glossary.md`. Three core folders hold the multi-file core: `features/` for
the `.feature` files, `schemas/` for payload schemas, and `areas/` for area
specs (DEC-02, DEC-09).

`docs/spec/work/` holds working output: gaps reports, QA strategies,
`prd.md`, update summaries, and the two todo lists. Working output is not
core (DEC-05, DEC-09).

`docs/agent-context.md` is the project's one routing file. Each bounded
context is a domain concern in it, with its description and `Read:` paths.
`CONTEXT.md` and `CONTEXT-MAP.md` do not exist in the target layout (DEC-07).

`docs/spec/glossary.md` holds the term definitions. Each section is one table
with the columns Term, Definition, and Avoid. A section covers a bounded
context or a topic (DEC-12, DEC-15). In a project with arc42, chapter
`12_glossary.md` holds one line that links to `docs/spec/glossary.md`, and
`publish-docs` renders the glossary as chapter 12 of the PDF (DEC-16).

The arc42 prose stays in `docs/arc42/`. The Structurizr theme lives in
`docs/assets/themes/`, next to the rendered images, and the `theme` line of
`docs/spec/architecture.dsl` points there (DEC-14).

`docs/adr/`, `docs/testing.yaml`, and `docs/agent-context.md` stay where they
are, because none of them specifies the system. `testing.yaml` is derived
from code, and `agent-context.md` routes agents.

The actor-goal list and the use-case files do not fit the scope map and the
feature files. The layout removes them, also from `docs/~archive/` (DEC-10).

## Consequences

**Easier:** a newcomer finds every source file in one folder. A gate or a
script reads a core file from one fixed path in every project, so the DBML
proposal can name `docs/spec/entity-model.dbml`. Agents read one routing file
and one glossary.

**Harder:** every factory script, agent, skill, playbook, template, and hook
that names an old path must name the new one. Installed projects need a
migration, which [ADR-0026](0026-layout-migration-runs-inside-the-factory-update.md)
defines. Folding the context map into domain concerns needs judgment, so it
stays a separate step for the developer. Until a project runs that step,
`CONTEXT-MAP.md` and routing-only `CONTEXT.md` files remain beside
`agent-context.md`.
