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
    - packages/factory/rulebooks/conventions/state-machine-notation.md
    - packages/factory/rulebooks/templates/state-machine.md
    - packages/factory/scripts/statemachine-lint
    - packages/factory/skills/detect-test-regime/SKILL.md
    - docs/testing.yaml

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

The factory keeps a project's entity model as one DBML file. It checks the
file the way it checks `architecture.dsl`: with a validator with exit codes, a
lint for the errors the parser misses, a pre-commit hook, and one SVG per named
view. These checks answer a question no factory gate answers today: does the
entity model still hold together after this commit?

The first release covers the tooling and the factory's agents and playbooks.
It also gives the specification core a single home in `docs/spec/`, with a
migration for installed projects. A pilot runs the tools on a pinned copy of
Gigacron's full model.

## Motivation

Today the entity model lives in `docs/spec/supplementary_specs/entity-model.md`
as Mermaid `erDiagram` blocks and prose tables. Mermaid checks syntax only. It
renders a relationship to an undeclared entity without an error, and nothing
checks the prose tables. Gigacron shows the cost: its model and its code
disagree in 16 places on three tables, and no gate noticed (see the PoC's
`expected-differences.md`).

ADR-0024 chose DBML after a
[technical PoC](../../poc/data_model_from_dsl/proposal-data-model-dsl-technical-poc.md).
The PoC ported the
[acid slice](../../poc/data_model_from_dsl/acid-slice.md), nine entities of
Gigacron's model. It ran each tool on twelve semantic error cases built from
that slice, E01 to E12. The PoC's wrapper scripts show that each piece works,
but they are throwaway code. They assume Gigacron's tables, run only by
hand, and live under `poc/`. No project can use them.

T-0006 asked for one canonical entity-model path across all scenarios. The
path is chosen, but no scenario uses it yet. The factory also scatters its
specification artifacts across `docs/spec/`, `docs/spec/supplementary_specs/`, `docs/arc42/`, and `docs/`
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
  project's language, ORM, or database product (DEC-08 of the
  [PoC proposal](../../poc/data_model_from_dsl/proposal-data-model-dsl-technical-poc.md#decisions)).
- **Containers only.** Every factory tool runs through `docker run --rm`, as
  the `structurizr` script does. The project's own commands run in the
  project's toolchain.

## Design

### The core artifact set

A project's specification core is the set of files that meet three
conditions. People edit them by hand. Every other artifact derives from them or
is checked against them. A gate checks them or should check them.

All core files live in `docs/spec/` (DEC-08, DEC-13). The feature files sit in
`features/`, the schemas for structured payloads in `schemas/`, and every other
core file at the top:

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

The only other folder in `docs/spec/` is `work/`. It holds no core file, only
the working output that agents write while they derive or review the core:
gaps reports, QA strategies, `prd.md`, and update summaries.

ADRs live in `docs/adr/` (DEC-07). The arc42 prose lives in `docs/arc42/` and
refers to `docs/spec/architecture.dsl`. `testing.yaml` and `agent-context.md`
live in `docs/`. They are not core files: `testing.yaml` is derived from code,
and `agent-context.md` routes agents and does not specify the system.

### Moving installed projects

A migration script moves an installed project's files into this layout with
`git mv`. It also rewrites the local Markdown links that point at the old
paths. It lists every other occurrence of an old path, for example in CI files
or scripts, for the developer to fix. It never rewrites those. `--dry-run` prints
the moves and rewrites without making them. `update-factory` offers the script
and runs it only after the developer confirms (DEC-09). The factory's own
repository is the first project to migrate this way.

### The `entity-model` script

One factory script, `packages/factory/scripts/entity-model`, wraps the DBML
tools in a pinned `node` container (DEC-03). It has four subcommands:

| Subcommand | Does                                                                          | Exit code                           |
| ---------- | ----------------------------------------------------------------------------- | ----------------------------------- |
| `validate` | Parses the file with `@dbml/core`, then runs the lint rules below.            | 0 clean, 1 errors, 2 tool fail      |
| `render`   | Writes one SVG for the full model and one per `DiagramView`.                  | 0 written, 1 errors                 |
| `import`   | Runs `sql2dbml` on DDL for a named dialect and writes a DBML file for review. | 0 written, 1 errors                 |
| `compare`  | Compares the model with the project's live schema and lists every difference. | 0 equal, 1 differences, 2 tool fail |

It reads `docs/spec/entity-model.dbml` unless the caller gives a path. A
`DiagramView` is a DBML block that names a subset of tables for one diagram.

The renderer reads neither `checks` blocks nor `DiagramView` blocks. So
`render` removes the `checks` blocks and copies each view's tables into a
temporary model before it calls the renderer. The PoC's `dbml-render.sh` and `dbml-views.sh` show both steps.

- The container image and the `@dbml/core` version are pinned in the script.
  The PoC used `node:20-bookworm` and `@dbml/core` 11.0.0.
- `validate` prints one line per error as `<file>:<line>: <rule>: <message>`,
  like `arch-lint`.
- `render` writes to `docs/assets/images/`, named `entity-model.svg` and
  `entity-model-<view>.svg`.

### Lint rules

The parser caught 8 of the PoC's 12 semantic errors. The lint adds rules that
it answers from the `@dbml/core` model:

| Rule                 | Checks                                                                                                                              | PoC case                                                                                    |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `fk-type-match`      | A foreign-key column has the same type as the column it references.                                                                 | E04                                                                                         |
| `single-primary-key` | A table declares at most one primary key.                                                                                           | E11                                                                                         |
| `known-type`         | Each column type is in the allowed list for the file's `database_type`.                                                             | E07                                                                                         |
| `one-to-one-owner`   | A one-to-one reference is written with `>` and a UNIQUE index, never `-`.                                                           | [PoC finding](../../poc/data_model_from_dsl/notes/validation.md#finding-for-the-dbml-story) |
| `enum-matches-state` | Each enum linked to a state machine has exactly that machine's states (see [State-machine link](#state-machine-link)).              | none                                                                                        |
| `payload-schema`     | Each `json` or `jsonb` column names a schema in its note, and that file exists in `docs/spec/schemas/` and is valid.                | none                                                                                        |
| `prose-in-notes`     | The file has no `//` or `/* */` comment. Every explanation is a note (see [Explanations in the model](#explanations-in-the-model)). | none                                                                                        |

E10, a CHECK expression that names a missing column, is deferred (see [Scope](#scope)).

A payload column names its schema in its note, for example
`note: 'schema: task-trigger'`. The folder name `schemas/` does not tie the
folder to one format. This release checks JSON Schema files only (DEC-13).

### Explanations in the model

The entity model's explanatory prose lives in DBML notes. A note may sit on
the project, a table, a column, an index, an enum value, or a table group, or
stand alone. It may span several lines and use Markdown. The parser keeps
every note but drops comments, so `prose-in-notes` forbids comments
(DEC-17). `dbml2sql` exports table and column notes as the database's own
comments, and `sql2dbml` imports those comments back as notes.

A note explains. It never states behaviour. A note such as "FORWARD ONLY"
states a transition rule, which belongs in `state-machines.md`. No lint can
tell an explanation from a rule, so the spec-review agent checks every note
for transitions, ordering, and conditions (DEC-14).

### State-machine link

A state machine whose state is stored names the DBML enum that stores it. The
line `Enum: task_state` opens its pseudocode block. A machine without a stored
state has no such line. `statemachine-lint` reads the line, and
`enum-matches-state` compares the machine's `State:` declarations with the
enum's values. It reports a value missing on either side, and an `Enum:` name
that the DBML file does not define (DEC-04). `state-machine-notation.md` and
the state-machine template describe the line.

### Pre-commit hook

The pre-commit hook `entity-model-lint` runs `entity-model validate` when the DBML file
changes. `merge-precommit-config` adds it to installed projects, next to
`arch-lint`.

### Drift check

`compare` checks the model against the code without knowing the project's
stack (DEC-10). The factory owns the database container. The project names
only how its schema gets built (DEC-11):

1. `docs/testing.yaml` names, under `schema`, the database image
   (`database_image`, for example `postgres:16`) and the project's apply
   command (`apply`, for example `alembic upgrade head`, `flyway migrate`, or
   `psql -f schema.sql`).
2. `compare` starts the image as a throwaway container and runs the apply
   command with `DATABASE_URL` pointing at it. The command runs in the
   project's own toolchain and may itself be a `docker run`.
3. `compare` dumps the schema with the database's own client from the same
   image, removes the container, and turns the dump into DBML with
   `sql2dbml`.
4. It parses both files with `@dbml/core` and compares tables, columns, types,
   nullability, primary keys, foreign keys, unique keys, indexes, and CHECK
   constraints by name.

Every difference prints as one line,
`<table>.<column or constraint>: <model> ≠ <live>`. Items the model leaves
open, such as identity generation or column order, do not count as
differences.

When `schema.comments` is `true`, `compare` also checks that each table and
column note matches the database comment on that table or column. The key
defaults to `false`, because a project that sets no comments would see every
note as a difference (DEC-18).

The built-in dump step covers PostgreSQL (`pg_dump --schema-only`). For any
other database, the project names a full dump command under `schema.dump`
instead. `compare` then runs that command in place of steps 2 and 3, starts
no container, and turns the dump into DBML with `sql2dbml` as in step 3. The factory ships no reference to a
database image under a non-permissive licence, such as Oracle's.

`detect-test-regime` keeps the `schema` keys when it rewrites
`docs/testing.yaml`.

The drift check opens with a probe: `sql2dbml --postgres` on the PoC's
`live-schema.sql`. If `sql2dbml` cannot read that dump, the drift check moves
to the deferred list, with the probe's output as the reason. The pilot then
runs without it (DEC-10).

### Factory wiring

- `requirements-agent` writes the DBML file instead of `entity-model.md`.
- Brownfield onboarding imports with `entity-model import` when DDL or a
  database dump exists, so existing database comments arrive as notes.
  Otherwise, it lets an agent derive the model from code. The stakeholder
  confirms either result.
- `reverse-map`, `reconcile-spec`, `spec-feedback`, `qa-strategy-from-spec`,
  and `create-backlog-story-slices` read the DBML file.
- The factory writes no `entity-model.md`. Its diagrams become the rendered
  SVGs, its tables the DBML file, and its explanatory prose the DBML notes
  (DEC-05). An existing `entity-model.md` is ported in full, prose included.

### Gigacron pilot

The factory reads Gigacron at one pinned commit and never writes to it, as the
PoC did. It ports all 29 entities of Gigacron's `entity-model.md`, prose
included, into a fixture at `packages/factory/fixtures/entity-model/gigacron/`.
The fixture's README names the pinned commit. Every `entity-model` subcommand
runs on the fixture. The fixture is a frozen test input. It does not follow later changes in
Gigacron (DEC-20).

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
- The factory wiring above, and the closure of T-0006.
- The Gigacron pilot.
- `entity-model compare`, the drift check.

The slices run in this order (DEC-02, DEC-19):

1. The validator and the hook, tested on the PoC's acid slice, with the
   drift-check probe alongside.
2. The renderer.
3. The core layout and the migration.
4. The factory wiring.
5. The state-machine link.
6. The drift check.
7. The Gigacron pilot.

[Drift check](#drift-check) describes the probe.

**Explicitly deferred (do NOT plan stories for these):**

- **E10, CHECK expressions.** It needs an SQL expression parser. No
  permissively licensed one has been tested.
- **Migration of other projects' Mermaid models.** The pilot shows the path.
  Each project migrates when it next touches its model.
- **Generating application code or migrations from DBML.** ADR-0024 makes DBML
  the model, not a code generator.
- **A state-machine language, and a soundness check for the current
  pseudocode.** Whether a validatable language replaces the pseudocode is its
  own question, tracked as T-0007. A soundness check written now would be
  thrown away if the notation changes. The `Enum:` line carries over to any
  notation.
- **Built-in dump steps for databases other than PostgreSQL.** A built-in step
  follows when a project needs one.
- **Schema formats other than JSON Schema.** No project uses one yet.
- **Gigacron's own adoption.** Gigacron moves to DBML through its own
  proposal, once the factory release exists. It may start from the fixture.
- **Project-specific rules,** such as Gigacron's rule that every Domain-owned table carries `domain_id`. They need a
  rule-configuration format, which no second project has asked for yet.

## Open Questions

None.

## Completion Criteria

- `entity-model validate` exits 1 on each of the PoC's cases E01–E09, E11,
  and E12, and 0 on the valid acid slice.
- `entity-model render` writes one SVG for the full model and one per
  `DiagramView` in the PoC's `acid-slice-views.dbml`.
- `entity-model import --dialect oracle` turns the PoC's
  `legacy.oracle.sql` into a file that `validate` accepts.
- In a project installed with `init-factory`, the `entity-model-lint` hook
  rejects a commit that breaks the DBML file.
- `validate` reports a one-to-one reference written with `-`.
- `enum-matches-state` reports an enum value that a linked state machine lacks.
- `prose-in-notes` reports every `//` and `/* */` comment in the DBML file.
- The spec-review agent's instructions name the review rule for notes.
- `payload-schema` reports a `jsonb` column without a schema, and a schema name
  with no file in `docs/spec/schemas/`.
- `grep -r entity-model.md packages/factory/` finds nothing outside
  `CHANGELOG.md`.
- After migration, `docs/spec/` holds the eight single-file core artifacts at
  the top, the feature files in `features/`, payload schemas in `schemas/`,
  working output in `work/`, and nothing else. `link-check` passes.
- `arch-lint` and `structurizr validate` pass on the factory's own repository
  after its migration.
- The migration script runs on a copy of an installed project, moves its
  files, and leaves `link-check` passing. It lists each old path found outside
  Markdown, and `--dry-run` changes no file.
- T-0006 is resolved with `docs/spec/entity-model.dbml`.
- The fixture's README maps each prose paragraph of `entity-model.md` at the
  pinned commit to the note that holds it, and no paragraph is unmapped.
- The Gigacron fixture passes `entity-model validate` and renders, and
  `entity-model compare` runs on it, unless the probe deferred the drift
  check.
- With `schema.comments: true`, `compare` reports a column whose note differs
  from its database comment. With the key absent, it reports no comment
  difference.
- With `schema.dump` set, `compare` runs that command and starts no container.
- `detect-test-regime` rewrites a `docs/testing.yaml` that has `schema` keys
  and keeps them.
- `entity-model compare` on the PoC's acid slice, against Gigacron's live
  schema at the pinned commit, reports each of the 16 differences in the PoC's
  `expected-differences.md` and no other, under that file's matching rules.
  If the probe failed, its output is recorded instead as the reason for
  deferral.

## Guiding Rule

If a commit can break the entity model without a gate failing, the feature is
not done.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by     | Decision                                                                                                                                                                                                                                                    | Raised by                                              |
| ------ | ---------- | ---------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| DEC-01 | 2026-10-30 | decision   | Matthias Daues | Adopt DBML as the entity-model language, as ADR-0024 records.                                                                                                                                                                                               | Data-model DSL PoC                                     |
| DEC-02 | 2026-10-30 | decision   | Matthias Daues | The first slice is the validator and the pre-commit hook, tested on the PoC's acid slice.                                                                                                                                                                   | Planning after the PoC                                 |
| DEC-03 | 2026-10-30 | decision   | Matthias Daues | One script named after its role, `entity-model`, wraps all DBML tools, so callers do not depend on the tool's name.                                                                                                                                         | Draft                                                  |
| DEC-04 | 2026-10-30 | decision   | Matthias Daues | A state machine names its DBML enum with an `Enum:` line in its pseudocode block. Behaviour points at structure; the DBML file names no state machine, and `note-shape` keeps one keyword.                                                                  | Grilling, question 2                                   |
| DEC-05 | 2026-10-30 | decision   | Matthias Daues | `entity-model.md` is retired, not kept as a derived view. Its explanatory prose moves into DBML notes; the rendered SVGs carry the picture.                                                                                                                 | Grilling, question 3                                   |
| DEC-06 | 2026-10-30 | decision   | Matthias Daues | The core artifact set and its storage root are settled before the DBML path is fixed.                                                                                                                                                                       | Stakeholder, planning session                          |
| DEC-07 | 2026-10-30 | decision   | Matthias Daues | ADRs are not part of the core artifact set. They are a record of decisions, not a model, and `docs/adr/` already makes them easy to find.                                                                                                                   | Open Question 1                                        |
| DEC-08 | 2026-10-30 | decision   | Matthias Daues | `docs/spec/` holds the nine core artifacts and nothing else, with `.feature` files under `features/`. Working output moves to `docs/spec/work/`. `architecture.dsl` and `dependency-rules.dsl` move in from `docs/arc42/`. DEC-13 adds `schemas/`.          | Open Question 1                                        |
| DEC-09 | 2026-10-30 | decision   | Matthias Daues | Installed projects move through a migration script that `update-factory` offers and runs only after the developer confirms. It rewrites Markdown links, lists other hits without changing them, and has `--dry-run`.                                        | Grilling, question 4                                   |
| DEC-10 | 2026-10-30 | decision   | Matthias Daues | The drift check compares DBML with DBML: the live schema is dumped as DDL, imported with `sql2dbml`, and diffed. It is the last slice and opens with a probe on the PoC's `live-schema.sql`; if the probe fails, the check is deferred.                     | Open Question on the drift check                       |
| DEC-11 | 2026-10-30 | decision   | Matthias Daues | `docs/testing.yaml` holds the drift check's settings under `schema`: `database_image` and `apply`, or `dump` as the fallback. The factory starts the container and dumps PostgreSQL itself. `.agent-factory/config/` was rejected because it is gitignored. | Grilling, question 5                                   |
| DEC-12 | 2026-10-30 | decision   | Matthias Daues | Working output lives in `docs/spec/work/`, not in a sibling folder. The core files are the only files at the top of `docs/spec/`.                                                                                                                           | Stakeholder, refines DEC-08                            |
| DEC-13 | 2026-10-30 | decision   | Matthias Daues | Schemas for structured payloads join the core in `docs/spec/schemas/`. The folder name does not tie it to one format; this release checks JSON Schema only.                                                                                                 | Open Question on JSON payloads                         |
| DEC-14 | 2026-10-30 | decision   | Matthias Daues | "No behaviour in a note" is checked by the spec-review agent. No lint judges a note's content; DEC-17 revises the mechanical half.                                                                                                                          | Open Question on notes, revised in grilling question 3 |
| DEC-15 | 2026-10-30 | assumption | Matthias Daues | A note is limited to one sentence of at most 160 characters. Replaced by DEC-17: the limit would leave no room for the model's explanatory prose.                                                                                                           | Draft, follows DEC-14                                  |
| DEC-16 | 2026-10-30 | decision   | Matthias Daues | The choice of a validatable state-machine language is a separate question (T-0007), outside this proposal. A soundness check for the current pseudocode waits for it.                                                                                       | Grilling, question 2                                   |
| DEC-17 | 2026-10-30 | decision   | Matthias Daues | Notes carry all explanatory prose, with no limit on length or position. `prose-in-notes` replaces `note-shape` and forbids comments, because the parser drops them and every export loses them.                                                             | Grilling, question 3                                   |
| DEC-18 | 2026-10-30 | decision   | Matthias Daues | `compare` checks notes against database comments only when `schema.comments` is `true`; the default is `false`.                                                                                                                                             | Grilling, structure and scope, question 1              |
| DEC-19 | 2026-10-30 | decision   | Matthias Daues | The drift-check probe runs alongside slice 1, and the drift check comes before the Gigacron pilot, so the pilot exercises every tool.                                                                                                                       | Grilling, structure and scope, question 2              |
| DEC-20 | 2026-10-30 | decision   | Matthias Daues | The pilot ports Gigacron's model at a pinned commit into a factory fixture and writes nothing to Gigacron. Gigacron adopts DBML through its own proposal.                                                                                                   | Grilling, structure and scope, question 3              |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
