---
schema_version: 2
title: Entity Model as DBML
status: draft
owner: Matthias Daues
created: 2026-10-30
updated: 2026-10-30
supersedes:

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - docs/adr/0024-dbml-as-entity-model-language.md
    - docs/spec/todo.md
    - packages/factory/agents/requirements-agent.md
    - packages/factory/playbooks/brownfield-onboarding.md
    - packages/factory/skills/reverse-map/SKILL.md
    - packages/factory/skills/reconcile-spec/SKILL.md
    - packages/factory/skills/spec-feedback/SKILL.md
    - packages/factory/scripts/merge-precommit-config
    - packages/factory/agents/spec-review-agent.md

governance:
  assurance: elevated
  risk_domains:
    - data_integrity
    - compatibility

estimate:
  as_of: 2026-10-30
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Feature Request: Entity Model as DBML

## Primer

Written by `write-primer` once the design is settled.

## Summary

The factory keeps a project's entity model as one DBML file, checked the way
`architecture.dsl` is checked: a validator with exit codes, a lint for the
errors the parser misses, a pre-commit hook, and one SVG per named view. The
question it answers is one the factory cannot answer today: does the entity
model still hold together after this commit? The first release covers the
tooling, the factory's agents and playbooks, and a pilot on Gigacron's full
model.

## Motivation

Today the entity model lives in `docs/spec/supplementary_specs/entity-model.md`
as Mermaid `erDiagram` blocks and prose tables. Mermaid checks syntax only. It
renders a relationship to an undeclared entity without an error, and nothing
checks the prose tables. Gigacron shows the cost: its model and its code
disagree in 16 places on three tables, and no gate noticed (see the PoC's
`expected-differences.md`).

ADR-0024 chose DBML after a technical PoC. The PoC's wrappers prove each piece
works, but they are spike code. They assume Gigacron's tables, run only by
hand, and live under `poc/`. No project can use them.

T-0006 asked for one canonical entity-model path across all scenarios. It is
still open, and the factory today scatters its specification artifacts across
`docs/spec/`, `docs/spec/supplementary_specs/`, `docs/arc42/`, and `docs/`
itself. `CONTEXT.md` is referenced at both `docs/CONTEXT.md` and
`docs/arc42/CONTEXT.md`.

## Core Principles

- **The DBML file is the source.** Every diagram and every other view is
  derived from it and never edited by hand.
- **Structure only.** The model holds tables, columns, keys, constraints, and
  enums. Behaviour stays in the state machines, validation rules, and
  `.feature` files.
- **The parser is the authority.** Validation runs through `@dbml/core`, never
  through `dbml2sql`, which exits 0 on broken models.
- **No assumption about the project's stack.** No check may depend on the
  project's language, ORM, or database product (PoC DEC-08).
- **Containers only.** Every tool runs through `docker run --rm`, as the
  `structurizr` script does.

## Design

### The core artifact set

A project's specification core is the set of files that people edit by hand,
that every other artifact derives from or is checked against, and that a gate
checks. All of them live in `docs/spec/`: the feature files in `features/`,
the schemas for structured payloads in `schemas/`, and every other core file
at the top. The only other folder is `work/`, which holds no core file
(DEC-08, DEC-13):

| File                     | Holds                                             | Gate                       |
| ------------------------ | ------------------------------------------------- | -------------------------- |
| `scope-map.md`           | What the system does, by domain area              | `scope-lint`               |
| `features/*.feature`     | Behaviour, as Rules per actor goal                | `spec-lint`                |
| `entity-model.dbml`      | Tables, keys, constraints, enums                  | `entity-model validate`    |
| `state-machines.md`      | States and transitions                            | `statemachine-lint`        |
| `validation-rules.md`    | Rules on input and on data                        | `spec-lint`                |
| `interface-contracts.md` | Contracts at the system's boundaries              | `spec-lint`                |
| `architecture.dsl`       | Building blocks, views, deployment                | `arch-lint`, `structurizr` |
| `dependency-rules.dsl`   | Allowed dependencies between building blocks      | `dependency-check`         |
| `schemas/*`              | Structure inside payload columns, such as `jsonb` | `entity-model validate`    |
| `CONTEXT.md`             | The domain vocabulary all of the above uses       | none yet                   |

Working output that agents write while they derive or review the core moves
to `docs/spec/work/`: gaps reports, QA strategies, `prd.md`, and update
summaries. ADRs stay in `docs/adr/` (DEC-07). The arc42 prose stays in
`docs/arc42/` and refers to `docs/spec/architecture.dsl`. `testing.yaml` and
`agent-context.md` stay in `docs/`, because the first is derived from code and
the second routes agents rather than specifying the system.

### Moving installed projects

A migration script moves an installed project's files into this layout and
rewrites the local links that point at the old paths. `update-factory` offers
it and runs it only after the developer confirms (DEC-09). The factory's own
repository is migrated the same way, as the first project.

### The `entity-model` script

One factory script, `packages/factory/scripts/entity-model`, wraps the DBML
tools in a pinned `node` container (DEC-03). Its subcommands:

| Subcommand | Does                                                                          | Exit code                           |
| ---------- | ----------------------------------------------------------------------------- | ----------------------------------- |
| `validate` | Parses the file with `@dbml/core`, then runs the lint rules below.            | 0 clean, 1 errors, 2 tool fail      |
| `render`   | Writes one SVG for the full model and one per `DiagramView`.                  | 0 written, 1 errors                 |
| `import`   | Runs `sql2dbml` on DDL for a named dialect and writes a DBML file for review. | 0 written, 1 errors                 |
| `compare`  | Compares the model with the project's live schema and lists every difference. | 0 equal, 1 differences, 2 tool fail |

It reads `docs/spec/entity-model.dbml` unless a path is given.

`render` removes the `checks` blocks and copies each view's tables into a
temporary model before it calls the renderer, because the renderer reads
neither. The PoC's `dbml-render.sh` and `dbml-views.sh` show both steps.

### Drift check

`compare` checks the model against the code without knowing the project's
stack (DEC-10):

1. The project names one command that dumps its live schema as DDL, built by
   whatever the project uses: migrations, an ORM, or plain SQL. The command
   lives in `.agent-factory/config/project.json` under
   `entity_model.schema_dump` (DEC-11).
2. `compare` runs the command and turns the dump into DBML with `sql2dbml`.
3. It parses both files with `@dbml/core` and compares tables, columns, types,
   nullability, primary keys, foreign keys, unique keys, indexes, and CHECK
   constraints by name.

Every difference prints as one line, `<table>.<column or constraint>: <model> ≠ <live>`. Items the model leaves open, such as identity generation or column
order, do not count as differences.

### Lint rules

The parser caught 8 of the PoC's 12 semantic errors. The lint adds rules that
the `@dbml/core` model can answer:

| Rule                 | Checks                                                                                                                    | PoC case |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------- | -------- |
| `fk-type-match`      | A foreign-key column has the same type as the column it references.                                                       | E04      |
| `single-primary-key` | A table declares at most one primary key.                                                                                 | E11      |
| `known-type`         | Each column type is in the allowed list for the file's `database_type`.                                                   | E07      |
| `one-to-one-owner`   | A one-to-one reference is written with `>` and a UNIQUE index, never `-`.                                                 | PoC note |
| `enum-matches-state` | Each enum linked to a state machine has exactly that machine's states.                                                    | none     |
| `payload-schema`     | Each `json` or `jsonb` column names a schema in its note, and that file exists in `docs/spec/schemas/` and is valid.      | none     |
| `note-shape`         | A note is one sentence of at most 160 characters, sits on a table or column, and carries no keyword other than `schema:`. | none     |

E10, a CHECK expression that names a missing column, needs an SQL expression
parser and stays out of this release.

A payload column names its schema in its note, for example
`note: 'schema: task-trigger'`. The folder is named `schemas/`, not after one
format. This release checks JSON Schema files only; another format gets a rule
when a project needs one (DEC-13).

`note-shape` keeps long rule texts out of the model. A short rule such as
"FORWARD ONLY" still fits in a note, so the spec-review agent also checks that
no note states behaviour: transitions, ordering, or conditions. Behaviour
belongs in `state-machines.md`, `validation-rules.md`, or a feature file
(DEC-14).

### State-machine link

`statemachine-lint` already reads `state-machines.md`. A state machine names
the DBML enum it governs, for example `enum: task_state`. `enum-matches-state`
compares the two sets and reports values missing on either side (DEC-04).

### Pre-commit hook

A hook `entity-model-lint` runs `entity-model validate` when the DBML file
changes. `merge-precommit-config` adds it to installed projects, next to
`arch-lint`.

### Factory wiring

- `requirements-agent` writes the DBML file instead of `entity-model.md`.
- Brownfield onboarding imports with `entity-model import` when DDL or a
  database dump exists, and lets an agent derive the model from code
  otherwise. Either result goes to the stakeholder for confirmation.
- `reverse-map`, `reconcile-spec`, `spec-feedback`, `qa-strategy-from-spec`,
  and `create-backlog-story-slices` read the DBML file.
- `entity-model.md` is no longer written. Short descriptions go into DBML
  `Note` fields on tables and columns (DEC-05).

### Gigacron pilot

Gigacron's 29-entity model is ported to DBML, validated, linted, and rendered.
The port runs in Gigacron's repository and follows Gigacron's own process.

## Scope

**In the first release:**

- The core artifact set in `docs/spec/`, working output in `docs/spec/work/`,
  and the migration script for installed projects.
- Every factory script, agent, skill, playbook, and template that names an
  old path names the new one.
- The `entity-model` script with `validate`, `render`, and `import`.
- The seven lint rules, and the review rule for notes in the spec-review
  agent.
- The `entity-model-lint` pre-commit hook, installed through
  `merge-precommit-config`.
- The state-machine link in `state-machines.md` and `statemachine-lint`.
- The factory wiring listed above, and T-0006 closed.
- The Gigacron pilot.
- `entity-model compare`, the drift check.

The slices run in this order: validator and hook on the PoC's acid slice;
renderer; core layout and migration; factory wiring; state-machine link;
Gigacron pilot; drift check (DEC-02). The drift check opens with a probe:
`sql2dbml --postgres` on the PoC's `live-schema.sql`. If `sql2dbml` cannot
read that dump, the drift check moves to the deferred list, with the probe's
output as the reason (DEC-10).

**Explicitly deferred (do NOT plan stories for these):**

- **E10, CHECK expressions.** It needs an SQL expression parser; no
  permissively licensed one has been tested.
- **Migration of other projects' Mermaid models.** The pilot shows the path;
  each project migrates when it next touches its model.
- **Generating application code or migrations from DBML.** ADR-0024 makes DBML
  the model, not a code generator.
- **Schema formats other than JSON Schema.** No project uses one yet.
- **Project-specific rules,** such as Gigacron's Domain-owned rule. They need a
  rule-configuration format, which no second project has asked for yet.

## Design Details

- The container image and the `@dbml/core` version are pinned in the script.
  The PoC used `node:20-bookworm` and `@dbml/core` 11.0.0.
- `validate` prints one line per error as `<file>:<line>: <rule>: <message>`,
  like `arch-lint`.
- `render` writes to `docs/assets/images/`, named `entity-model.svg` and
  `entity-model-<view>.svg`.

## Open Questions

None.

## Completion Criteria

- `entity-model validate` exits 1 on each of the PoC's cases E01–E09, E11,
  and E12, and 0 on the valid acid slice.
- `entity-model render` writes one SVG for the full model and one per
  `DiagramView` in the acid slice.
- `entity-model import --dialect oracle` turns the PoC's
  `legacy.oracle.sql` into a file that `validate` accepts.
- A commit that breaks the DBML file is rejected by the `entity-model-lint`
  hook in a project installed with `init-factory`.
- `enum-matches-state` reports an enum value that a linked state machine lacks.
- `note-shape` reports a note longer than one sentence or 160 characters, and
  a note on the project or on a table group.
- The spec-review agent's instructions name the review rule for notes.
- `payload-schema` reports a `jsonb` column without a schema, and a schema name
  with no file in `docs/spec/schemas/`.
- No factory agent, skill, playbook, or template writes or reads
  `entity-model.md`; `grep` finds no reference outside the changelog.
- After migration, `docs/spec/` holds the eight single-file core artifacts at
  the top, the feature files in `features/`, payload schemas in `schemas/`,
  working output in `work/`, and nothing else. `link-check` passes.
- The migration script runs on a copy of an installed project, moves its
  files, and leaves `link-check` passing.
- T-0006 is resolved with `docs/spec/entity-model.dbml`.
- Gigacron's full model passes `entity-model validate` and renders.
- `entity-model compare` on the PoC's acid slice, against Gigacron's live
  schema at the pinned commit, reports each of the 16 differences in the PoC's
  `expected-differences.md` and no other. Or the probe's output is recorded as
  the reason for deferral.

## Guiding Rule

If a commit can break the entity model without a gate failing, the feature is
not done.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by     | Decision                                                                                                                                                                                                                                | Raised by                        |
| ------ | ---------- | ---------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| DEC-01 | 2026-10-30 | decision   | Matthias Daues | Adopt DBML as the entity-model language, as ADR-0024 records.                                                                                                                                                                           | Data-model DSL PoC               |
| DEC-02 | 2026-10-30 | decision   | Matthias Daues | The first slice is the validator and the pre-commit hook, tested on the PoC's acid slice.                                                                                                                                               | Planning after the PoC           |
| DEC-03 | 2026-10-30 | assumption | Matthias Daues | One script named after its role, `entity-model`, wraps all DBML tools, so callers do not depend on the tool's name.                                                                                                                     | Draft                            |
| DEC-04 | 2026-10-30 | assumption | Matthias Daues | A state machine names its DBML enum explicitly; the lint does not guess the link from column names.                                                                                                                                     | Draft                            |
| DEC-05 | 2026-10-30 | assumption | Matthias Daues | `entity-model.md` is retired, not kept as a derived view. DBML `Note` fields carry short descriptions; the rendered SVGs carry the picture.                                                                                             | Draft                            |
| DEC-06 | 2026-10-30 | decision   | Matthias Daues | The core artifact set and its storage root are settled before the DBML path is fixed.                                                                                                                                                   | Stakeholder, planning session    |
| DEC-07 | 2026-10-30 | decision   | Matthias Daues | ADRs are not part of the core artifact set. They are a record of decisions, not a model, and `docs/adr/` already makes them easy to find.                                                                                               | Open Question 1                  |
| DEC-08 | 2026-10-30 | decision   | Matthias Daues | `docs/spec/` holds the nine core artifacts and nothing else, with `.feature` files under `features/`. Working output moves to `docs/spec/work/`. `architecture.dsl` and `dependency-rules.dsl` move in from `docs/arc42/`.              | Open Question 1                  |
| DEC-09 | 2026-10-30 | assumption | Matthias Daues | Installed projects move through a migration script that `update-factory` offers and runs only after the developer confirms.                                                                                                             | Draft, follows DEC-08            |
| DEC-10 | 2026-10-30 | decision   | Matthias Daues | The drift check compares DBML with DBML: the live schema is dumped as DDL, imported with `sql2dbml`, and diffed. It is the last slice and opens with a probe on the PoC's `live-schema.sql`; if the probe fails, the check is deferred. | Open Question on the drift check |
| DEC-11 | 2026-10-30 | assumption | Matthias Daues | The schema dump command lives in `.agent-factory/config/project.json` under `entity_model.schema_dump`.                                                                                                                                 | Draft, follows DEC-10            |
| DEC-12 | 2026-10-30 | decision   | Matthias Daues | Working output lives in `docs/spec/work/`, not in a sibling folder. The core files are the only files at the top of `docs/spec/`.                                                                                                       | Stakeholder, refines DEC-08      |
| DEC-13 | 2026-10-30 | decision   | Matthias Daues | Schemas for structured payloads join the core in `docs/spec/schemas/`. The folder name does not tie it to one format; this release checks JSON Schema only.                                                                             | Open Question on JSON payloads   |
| DEC-14 | 2026-10-30 | decision   | Matthias Daues | "No behaviour in a note" is enforced twice: the `note-shape` lint limits a note's form, and the spec-review agent judges its content.                                                                                                   | Open Question on notes           |
| DEC-15 | 2026-10-30 | assumption | Matthias Daues | A note is limited to one sentence of at most 160 characters.                                                                                                                                                                            | Draft, follows DEC-14            |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
