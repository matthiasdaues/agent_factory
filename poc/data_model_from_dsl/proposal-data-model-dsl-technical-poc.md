---
schema_version: 2
title: Data-Model DSL Technical Proof-of-Concept
status: accepted
owner: Matthias Daues
created: 2026-08-14
updated: 2026-10-29
supersedes:

impact:
  scope: cross_project
  architecture_change: false
  external_contract_change: false
  boundaries:
    - gigacron:docs/spec/supplementary_specs/entity-model.md
    - gigacron:packages/server/backend/src/gigacron_server/task_registry/models.py
    - gigacron:packages/server/backend/src/gigacron_server/domain_registry/models.py
    - packages/factory/scripts/structurizr
    - docs/spec/todo.md

governance:
  assurance: elevated
  risk_domains:
    - data_integrity
    - compatibility

estimate:
  as_of: 2026-10-29
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Feature Request: Data-Model DSL Technical Proof-of-Concept

## Primer

Every factory project keeps a description of the data it stores in its database. This description is the entity model. It names each table, its columns, and the rules between them, such as which values must be unique. The factory wants one text-based language for entity models in every project.

The factory's to-do list already names LinkML, but nobody ran a tool to support that choice. An earlier survey only read the candidates' documentation and source code. The deciding questions, such as whether a validator rejects a broken model, need a running tool.

Gigacron, an enterprise job scheduler, is the first factory project with a large model and code that builds it. Its model is a diagram that no tool checks, and the code already disagrees with it. The code makes a task's name unique within its scheduling domain. The model keeps the name on each version of a task and makes names unique within a folder. Nobody noticed, because nothing compares the model with the code.

The proposal separates three things. The model file is the source of truth and changes when the specification changes. The code follows the model, written by hand or generated as a first draft. The live schema is the set of tables the code creates in a database. A check compares the model with the live schema, not the code text, so it works with any database library. If the proof of concept recommends two languages, a command generates one model from the other, so a developer edits only one file by hand.

This proof of concept tests four languages: DBML, LinkML, Atlas HCL, and Mermaid. Gigacron uses Mermaid today, so Mermaid is the baseline, and "better than what we have" becomes a measured result. Each candidate models the same nine Gigacron tables from one fixed version. These tables carry twelve hard cases, such as keys made of two columns and rules specific to PostgreSQL, the database Gigacron uses. Before any candidate runs, a list records every known difference between these tables and the live schema. The task-name difference is one entry. Each candidate's tool then compares its model with a throwaway database built by Gigacron's code. The comparison scores the listed differences found, minus false reports.

Every candidate must keep its model as plain text under version control, reject a broken model, render a diagram in a container, and compare the model with the live schema. The model must also hold rules specific to the project's database, or those rules drift unseen. A candidate may fix a missed requirement with a wrapper script, which counts as maintenance cost. Without a working fix, it stays in the comparison with a heavy penalty. Gigacron supplies the test data, not the criteria.

The result is four comparison notes, a weighted scoring table called a Pugh Matrix, and a recommendation or a deferral. A stakeholder confirms the weights before scoring. A human later approves the choice in an architecture decision record. The proposal has no open questions.

## Summary

This proof-of-concept (PoC) runs the tools to find which text-based data-modeling language the factory makes its standard for a project's entity model. The test case is Gigacron, an enterprise job scheduler. Its entity model describes the data Gigacron persists. Under the [technical-poc.md](../../packages/factory/playbooks/technical-poc.md) playbook, the PoC ports one fixed slice of Gigacron's model to four candidate languages. It runs each candidate's tools and compares the ported model with the schema that Gigacron's code builds. The first release ends with four comparison notes, a [Pugh Matrix](../../packages/factory/skills/pugh-matrix/SKILL.md), and a recommendation. The PoC adopts no language (DEC-01, DEC-08).

## Motivation

The factory's to-do item T-0006 in `docs/spec/todo.md` names LinkML as the canonical format for every project's entity model. No tool was run to support that choice. Gigacron is the first factory project with a large model and code that implements it, so it is the test case.

Gigacron's persisted model lives as a Mermaid `erDiagram` in `docs/spec/supplementary_specs/entity-model.md` of the Gigacron repository. It holds 29 entities, a constraint table per entity, and the database comments. No tool validates it.

The [survey](survey-report.md) read each candidate's documentation and source code, but nobody installed or ran the tools. On that evidence, no candidate meets all three of the survey's hard requirements. The survey also found that expressive languages have weak tooling, and that languages with strong tooling express less. Its `candidates_for_deeper_falsification_study` list in [survey-report.json](survey-report.json) names the open questions and the command that answers each one. Two questions decide the outcome. Does `dbml2sql` exit non-zero on a broken model? Do LinkML's generators keep a composite key and a CHECK constraint? Only running the tools answers them.

Since the survey, Gigacron has gained its first code. The SQLAlchemy mappings in `domain_registry/models.py` and `task_registry/models.py` cover `domain`, `task`, `task_draft`, and `task_version`. The mappings already disagree with the model. In Gigacron, a Domain is one scheduling domain, such as `production-eu` or `staging`. A Folder groups Tasks inside a Domain. For example, the code declares `uq_task_domain_name (domain_id, name)` on `task`. The model keeps the name on `TASK_VERSION`, and a separate `NAME_CLAIM` table keeps each name unique inside its containing Folder. Nobody noticed the differences, because nothing compares the model with the code.

So the question has two parts. First, which language can express a project's model so that a gate can check it? Second, how does the model stay consistent with the code that implements it?

## Core Principles

- **One fixed slice, ported identically.** Every candidate models the same nine entities from one pinned Gigacron commit. No candidate picks the example that suits it.
- **Observation outranks documentation.** Every claim in a comparison note comes from a command the story ran and an output it observed. Where a note cannot back a claim this way, it says so.
- **Docker only.** Every tool runs only through `docker run --rm`, as the factory's [structurizr](../../packages/factory/scripts/structurizr) script does. A capability that needs a local install fails the requirement it claims to meet.
- **Project-neutral criteria.** The result sets the factory standard, so no criterion assumes Gigacron's database or ORM. Gigacron supplies the test data, not the rules (DEC-08).
- **The model must be checkable against the code.** A difference such as `uq_task_domain_name` is caught only if the model can be compared with the schema that the code builds.
- **A failed requirement is a result.** A candidate that fails a [hard requirement](#hard-requirements), even with a wrapper, is recorded as answered. It stays in the Pugh Matrix with the penalty that [Scoring](#scoring) describes (DEC-07). It gets no more time than the others got.
- **The PoC decides nothing by itself.** It produces comparison notes, a Pugh Matrix, and a recommendation. The architecture decision record (ADR) comes later, in the factory's `docs/adr/`, and a human approves it.

## Design

### Database dialects

A factory project may use any relational database. Many constraints in real schemas work in only one database, such as PostgreSQL's exclusion constraints. If the model cannot hold such a constraint, the model and the code can differ on it without anyone noticing. So a candidate must express the dialect-specific constraints of the project's database (DEC-09).

The PoC checks this requirement with PostgreSQL, because Gigacron uses PostgreSQL. The slice keeps Gigacron's PostgreSQL features: `jsonb`, partial unique indexes, and an exclusion constraint on `btree_gist`. Each comparison note also lists the other database dialects that the candidate's documentation claims, marked as unchecked.

### Model and code

The model file is the source of truth for the persisted schema. It changes when the specification changes, and the specification changes through accepted proposals. The code follows the model. A developer may write the code by hand, or generate a first version from the model and then edit it. In both cases, a gate compares the code with the model and fails on every difference (DEC-04). So the comparison is required, and generation is a convenience.

The gate compares the model with the live schema, not with the code itself. The project's own code or migrations create the tables in an ephemeral database container. The candidate's command then compares the model with that database. So the gate works the same way for a project that uses SQLAlchemy, Django, or plain SQL (DEC-10).

A developer edits one file by hand. The PoC may recommend a pair of languages, but only when a command generates the second artifact from the first. Each constraint is then written once (DEC-05).

### The acid slice

The acid slice is the part of the model that tests each candidate hardest, as an acid test does. It is the fixed input to every candidate story. It holds nine entities from Gigacron's `entity-model.md` at commit `40954f18fe72b237ecc865905a31cf0b9b146556`. Together they carry the twelve constructs below (DEC-03, DEC-11). The Gigacron model changes often, so every story reads this commit and no other.

01. Composite primary key.
02. Composite foreign key.
03. JSON payload column.
04. Enumerated string domain.
05. Self-referencing foreign key.
06. Nullable foreign key.
07. Multi-column UNIQUE constraint not tied to the primary key.
08. Partial UNIQUE constraint.
09. One-to-zero-or-one relationship.
10. CHECK constraint across columns.
11. Exclusion constraint.
12. The `domain_id` convention: the candidate's own validator asserts that every Domain-owned table carries `domain_id`.

Each entity contributes these constructs:

| Entity          | Constructs it contributes                                                                                                                                                                                                                                                                           |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DOMAIN`        | root of the `domain_id` convention; single-column UNIQUE `uq_domain_name`                                                                                                                                                                                                                           |
| `TASK`          | Domain-owned; multi-column UNIQUE `uq_task_domain (domain_id, task_id)` as the target of composite foreign keys                                                                                                                                                                                     |
| `FOLDER`        | Domain-owned; partial UNIQUE `uq_folder_root_per_domain` (`domain_id` WHERE `kind = 'ROOT'`); CHECK across two columns `ck_folder_state`; enumerated `kind` and `state`                                                                                                                             |
| `TASK_VERSION`  | Domain-owned; six `jsonb` sections; composite foreign keys to `TASK` and `FOLDER`; two foreign keys to `FOLDER` from one table; multi-column UNIQUE `uq_task_version_number`; partial UNIQUE `uq_task_version_current`; CHECK `ck_task_version_range`; exclusion constraint `ex_task_version_range` |
| `PLAN`          | Domain-owned; multi-column UNIQUE `uq_plan_domain_odate (domain_id, odate)`, not tied to the primary key                                                                                                                                                                                            |
| `TASK_INSTANCE` | parent of `ATTEMPT`; enumerated `state`; `jsonb` `filled_values`                                                                                                                                                                                                                                    |
| `ATTEMPT`       | composite primary key `(task_instance_id, attempt_no)`; partial UNIQUE `uq_attempt_open` with an enum predicate; enumerated `attempt_state`                                                                                                                                                         |
| `OUTBOX`        | nullable composite foreign key to `ATTEMPT`; the zero-or-one side of the one-to-zero-or-one relationship from `ATTEMPT`; CHECK across three columns `ck_outbox_attempt`                                                                                                                             |
| `AUDIT_EVENT`   | self-referencing foreign key `supersedes_event_id`                                                                                                                                                                                                                                                  |

The Domain-owned tables are `TASK`, `FOLDER`, `TASK_VERSION`, and `PLAN`. `TASK_INSTANCE`, `ATTEMPT`, `OUTBOX`, and `AUDIT_EVENT` reach their Domain through a parent row and carry no `domain_id`, so construct 12 does not apply to them.

Each entity keeps its columns unchanged. The slice leaves out every foreign key that points outside it, and `acid-slice.md` lists each one.

Three kinds of artifact are written once, before any candidate runs:

- `acid-slice.md` is the readable specification of the nine entities and their constraints.
- `expected-differences.md` lists every difference between the slice and the schema that Gigacron's code builds for `domain`, `task`, and `task_version` at the pinned commit. The list comes from reading the model and the code side by side. `uq_task_domain_name` is one entry.
- Each candidate gets three broken models, each with exactly one error. `broken-syntax.<ext>` has a syntax error. `broken-reference.<ext>` has a relationship to an undeclared entity. `broken-domain.<ext>` leaves `domain_id` out of `PLAN`.

### One story per candidate

Each story is a plain Markdown file under `poc/data_model_from_dsl/stories/`, per [technical-poc.md § Step 1](../../packages/factory/playbooks/technical-poc.md#step-1--frame-one-story-per-candidate). Each story states its goal, the risk it tests, what to build, a mechanical Definition of Done, and the instruction to write a comparison note.

The four candidates and the question each story settles:

- **DBML.** Does `dbml2sql` exit non-zero on a broken model? The survey read the CLI source and found no `process.exit(1)`. Does any renderer honour `DiagramView`? `DiagramView` is a named view: it shows a chosen subset of the entities from one model. It is the only construct of that kind among the seven languages the survey examined.
- **LinkML.** Do the first-party Pydantic, SQLAlchemy, and SQL DDL generators keep the composite key, the composite foreign key, the JSON column, the enumerated domain, and the CHECK constraint? Can a LinkML model be compared with a live database schema?
- **Atlas HCL.** Can Atlas validate the HCL file against an ephemeral PostgreSQL container? Can `atlas schema diff` compare the HCL file with the live schema? Which Docker tag family carries which licence? The survey left that open.
- **Mermaid erDiagram (the incumbent baseline).** Does `mmdc`, the Mermaid command-line renderer, render a relationship to an undeclared entity without an error? Running the baseline on the same slice makes "better than what we have" a finding, not an assertion.

### Hard requirements

A candidate, or a generated pair, must meet four hard requirements. The first three follow the survey's three hard requirements, with two differences. A candidate must express the dialect-specific constraints of the project's database instead of being product-neutral (DEC-09). PNG output is not required (DEC-06). The fourth requirement has no counterpart in the survey (DEC-04, DEC-10).

1. The model is a plain-text file under version control, and it can express the dialect-specific constraints of the project's database.
2. A validator exits non-zero on a broken model.
3. A container with no local install renders the model to SVG.
4. A command compares the model with the live schema in a database container and reports differences.

A candidate that fails a hard requirement may repair it with a thin wrapper around its tool. For example, a script can turn `dbml2sql`'s error output into exit code 1. The story builds the wrapper and runs it. If the wrapper works, the requirement counts as met (DEC-07). [Scoring](#scoring) says how a wrapper and a failed requirement count.

A wrapper may not call another candidate's tool. A candidate may need another language's tool, for example when DBML exports DDL for `atlas schema diff`. Then the combination is a generated pair (DEC-05). It scores as its own option, apart from the single candidate (DEC-10).

### Building the live schema

One shared step builds the live schema for every candidate, and it does not count in any score. A `python` container mounts the Gigacron checkout at the pinned commit read-only and installs it from its `uv.lock`. Gigacron has no migrations yet, so the step calls `Base.metadata.create_all` against an ephemeral PostgreSQL container. The step's commands are recorded in `expected-differences.md`.

### Per-story Definition of Done

Each item is mechanical and has the same shape for every candidate:

01. The acid slice is expressed in the candidate's language. Where the language cannot express a construct, the story names the construct and records its substitute.
02. `docker run --rm <image> <validate-command>` runs against the valid slice and exits 0.
03. The same command runs against each of the three broken models. The note records the exact numeric exit code for each file, and whether the tool reported the error in it.
04. A container with no local install produces SVG into `poc/data_model_from_dsl/out/<candidate>/`.
05. Where the container also produces PNG, the note records it. PNG is optional, because no consumer reads a rendered PNG diagram (DEC-06).
06. Where the candidate claims application-type or DDL generation, the story runs the generator. The note marks each of the twelve constructs as kept or lost in the output.
07. Where the candidate claims named views, the story produces a view over a subset of the nine entities and inspects the rendered result.
08. The candidate's command compares the slice with the live schema for `domain`, `task`, and `task_version`. Gigacron's code has no tables yet for the other six slice entities. The note counts the entries of `expected-differences.md` that the command reports, and the differences it reports that are not in the list.
09. The note lists the database dialects the candidate's documentation claims, marked as unchecked.
10. The comparison note captures every command verbatim, so a reader can run it again.

### Scoring

The Pugh Matrix scores the candidates from their comparison notes. The stakeholder confirms the weights before scoring.

- The comparison with the live schema (item 8) carries a high weight. Its score is the number of listed differences the command finds, minus the number of differences it reports falsely, divided by the length of the list (DEC-12). Generation (item 6) carries a low weight (DEC-04).
- A generated pair of languages may score as one option (DEC-05).
- A working wrapper counts as maintenance cost. A candidate without a working wrapper stays in the matrix with a heavy weighted penalty, and the matrix records the failed requirement (DEC-07).
- PNG output does not count (DEC-06).

## Scope

**In the first release:**

- `acid-slice.md`, `expected-differences.md`, and three broken models per candidate.
- Four candidate stories: DBML, LinkML, Atlas HCL, and Mermaid erDiagram.
- Four comparison notes, each answering the ten Definition-of-Done items.
- A Pugh Matrix over the four candidates and any generated pairs, scored from the comparison notes with [pugh-matrix](../../packages/factory/skills/pugh-matrix/SKILL.md).
- A recommendation in `poc/data_model_from_dsl/recommendation.md`, or an explicit deferral with a stated reason.

**Explicitly deferred (do NOT plan stories for these):**

- **Prisma, PlantUML IE, and D2.** The survey's evidence excludes each one. Prisma has no official Docker image, cannot express CHECK constraints, and has only an archived Python generator. PlantUML reduces composite keys, multi-column UNIQUE, and value constraints to free-text notes, so a validator cannot check those constraints. D2 cannot express six of the survey's ten constructs and cannot represent multi-column foreign keys. The survey used its own list of ten constructs, not the twelve above (DEC-03). If a story finds evidence that overturns an exclusion, it records a finding for the stakeholder. It starts no fifth story (DEC-13).
- Porting the full 29-entity model. The PoC ports only the slice. The full port belongs to adoption.
- Writing the ADR, changing T-0006, or changing anything in Gigacron. The differences in `expected-differences.md` are findings for Gigacron, not work for this PoC.
- A Docker wrapper script for the chosen candidate as shipped factory tooling. The wrappers that stories build under DEC-07 stay spike code under `poc/data_model_from_dsl/`.
- Migrations, CI integration, and pre-commit gates. They depend on the chosen language and belong to adoption.

## Design Details

Prototype material lives under `poc/data_model_from_dsl/` and stays marked as spike code, per [technical-poc.md § DONE](../../packages/factory/playbooks/technical-poc.md#done).

The PoC reads Gigacron's files and never writes to them. Every story reads the pinned commit.

The orchestrating session builds each candidate itself, one story after another, and starts no subagent, per [technical-poc.md § Step 2](../../packages/factory/playbooks/technical-poc.md#step-2--build-or-research-each-candidate-independently). Each story runs on its own branch with its own worktree, per [branching-policy.md § Every Branch Has A Worktree](../../packages/factory/rulebooks/conventions/branching-policy.md#every-branch-has-a-worktree).

Where the survey recorded a documented claim, the comparison note says whether observation confirmed or contradicted it. The note cites the survey's source record by filename, so the PoC's evidence extends the survey's evidence instead of starting over.

## Open Questions

None.

## Completion Criteria

- `acid-slice.md` exists and contains all twelve constructs from the pinned Gigacron commit.
- `expected-differences.md` exists and was written before any candidate ran.
- Each of the four candidates has a comparison note that answers all ten Definition-of-Done items, or states why an item could not be answered.
- Every exit code in every note comes from a command that was run, never from documentation.
- A Pugh Matrix scores the four candidates and any generated pairs against weighted criteria taken from the comparison notes. The stakeholder confirmed the weights before scoring.
- `recommendation.md` names a language or a generated pair as the factory standard, or defers with a stated reason.
- Nothing under `poc/` has been promoted into the specification, the architecture, or the factory scripts.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by     | Decision                                                                                                                                                                                                                                                                                                         | Raised by                                                       |
| ------ | ---------- | -------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| DEC-01 | 2026-10-29 | decision | Matthias Daues | Run this PoC before the factory adopts any entity-model language. The LinkML choice in the factory's T-0006 stays an assumption until the Pugh Matrix and the ADR confirm it.                                                                                                                                    | Effort question on introducing LinkML                           |
| DEC-02 | 2026-10-29 | decision | Matthias Daues | Refresh the proposal in place. PostgreSQL replaces the product-neutral requirement, because Gigacron's ADR-0006 and ADR-0010 use it. A comparison with the SQLAlchemy mappings becomes a Definition-of-Done item. DEC-09 and DEC-10 replace both parts, after DEC-08.                                            | The 2026-10-29 model rewrite and the code in Gigacron           |
| DEC-03 | 2026-10-29 | decision | Matthias Daues | The slice changes to `DOMAIN`, `TASK`, `FOLDER`, `TASK_VERSION`, `PLAN`, `TASK_INSTANCE`, `ATTEMPT`, `OUTBOX`, and `AUDIT_EVENT`. The construct list drops "several logical schemas" and adds composite foreign keys, partial UNIQUE, CHECK, and exclusion constraints.                                          | Four slice entities removed in the 2026-10-29 model             |
| DEC-04 | 2026-10-29 | decision | Matthias Daues | The model is the source of truth and changes through specification updates from accepted proposals. Mappings are written by hand or generated as a first version; a gate compares them with the model. Comparison weighs high, generation low.                                                                   | Grilling: Open Question on the direction between model and code |
| DEC-05 | 2026-10-29 | decision | Matthias Daues | A pair of languages is acceptable only when a command generates the second artifact from the hand-edited first. The Pugh Matrix may score such a pair as one option. Two hand-kept files are not acceptable.                                                                                                     | Grilling: Open Question on a two-language split                 |
| DEC-06 | 2026-10-29 | decision | Matthias Daues | SVG rendering from a container is required. PNG is optional and does not count in the Pugh Matrix. No file in Gigacron or the factory reads a rendered PNG diagram, and `publish-docs` uses vector diagrams.                                                                                                     | Grilling: Open Question on the PNG requirement                  |
| DEC-07 | 2026-10-29 | decision | Matthias Daues | A candidate that fails a hard requirement may repair it with a thin wrapper that the story builds and runs. A working wrapper meets the requirement and counts as maintenance cost. Without one, the candidate takes a heavy weighted penalty and stays in the matrix.                                           | Grilling: Open Question on scoring a failed hard requirement    |
| DEC-08 | 2026-10-29 | decision | Matthias Daues | The recommendation sets the factory standard for every project's entity model. Gigacron is the test case only. The ADR goes to the factory's `docs/adr/`, and the recommendation to `poc/data_model_from_dsl/recommendation.md`. No criterion may assume Gigacron's database or ORM.                             | PROP-06                                                         |
| DEC-09 | 2026-10-29 | decision | Matthias Daues | A candidate must express the dialect-specific constraints of the project's database. The PoC observes PostgreSQL through Gigacron, and each note lists the other dialects the candidate claims, marked unchecked. Exclusion and partial UNIQUE constraints count in the matrix.                                  | PROP-06, replaces DEC-02's PostgreSQL target                    |
| DEC-10 | 2026-10-29 | decision | Matthias Daues | The gate compares the model with the live schema that the project's code or migrations build in an ephemeral database container. Only the candidate's tool or its DEC-07 wrapper runs the comparison. A combination with another candidate's tool is a generated pair under DEC-05 and scores as its own option. | PROP-05                                                         |
| DEC-11 | 2026-10-29 | decision | Matthias Daues | The slice reads Gigacron commit `40954f18fe72b237ecc865905a31cf0b9b146556`, because the model changed twice on 2026-10-29. The Domain-owned slice tables are `TASK`, `FOLDER`, `TASK_VERSION`, and `PLAN`.                                                                                                       | PROP-01, PROP-02                                                |
| DEC-12 | 2026-10-29 | decision | Matthias Daues | `expected-differences.md` is written before any candidate runs. Item 8 scores listed differences found minus differences reported falsely, divided by the length of the list.                                                                                                                                    | PROP-04                                                         |
| DEC-13 | 2026-10-29 | decision | Matthias Daues | A story that finds evidence against an excluded candidate records a finding for the stakeholder and starts no fifth story.                                                                                                                                                                                       | PROP-07                                                         |

## Review findings

| ID      | Pass | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Resolution                                                                                                                                                                                                                                                                                                              |
| ------- | ---- | -------- | ----- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | 1    | major    | 03    | fixed  | The `FOLDER` row (line 114) names constraints that the model does not have. Gigacron's `entity-model.md` at 40954f18 has no `ck_folder_root_regular`; its cross-column CHECK on `FOLDER` is `ck_folder_state` (`kind = 'SMART' OR state = 'ACTIVE'`). `uq_folder_root_per_domain` filters on `kind = 'ROOT'`, not on `is_root`, and `FOLDER` has no `is_root` column. The acid slice is the fixed input to every story, so a planner who copies this row writes a wrong `acid-slice.md`. Correct the row against the model.                                                                                                                                                                                                                                             | Fixed. The `FOLDER` row now names `kind = 'ROOT'` and `ck_folder_state`, read from Gigacron 40954f18, and the slice pins that commit (DEC-11). Evidence: Gigacron `entity-model.md` lines 530-532.                                                                                                                      |
| PROP-02 | 1    | major    | 01    | fixed  | Construct 12 (line 106) cannot be checked as written. The proposal does not say which of the nine slice tables count as Domain-owned. In the model, `TASK_INSTANCE`, `ATTEMPT`, `OUTBOX`, and `AUDIT_EVENT` carry no `domain_id`, so a validator that asserts the rule on every table fails the valid slice. The broken model (line 124) also does not break this rule, so no story observes the validator reject it. Name the Domain-owned tables in the slice, and add a case that drops `domain_id` from one of them.                                                                                                                                                                                                                                                | Fixed. The acid slice section names the four Domain-owned tables and exempts the other four. A third broken model, `broken-domain.<ext>`, leaves `domain_id` out of `PLAN` (DEC-11).                                                                                                                                    |
| PROP-03 | 1    | major    | 01    | fixed  | One broken file carries both a syntax error and a semantic error (line 124). Most parsers stop at the first syntax error and never reach the semantic check. So Definition-of-Done item 3 (line 154) cannot observe "whether the semantic error was detected", and a candidate that would miss it looks the same as one that would catch it. Use two broken files, one per error, and record the exit code of each.                                                                                                                                                                                                                                                                                                                                                     | Fixed. Three broken models per candidate, each with exactly one error, and item 3 records an exit code per file.                                                                                                                                                                                                        |
| PROP-04 | 1    | major    | 01    | fixed  | Definition-of-Done item 8 (line 159) has no expected result beyond `uq_task_domain_name`. At Gigacron 40954f18 the real difference between the slice and the mappings is wider. The model keeps `name` on `TASK_VERSION`, not on `TASK`, while the code has `task.name` and no `task_version.name`. The code also lacks `runs_until_set_by_folder_id`, both foreign keys to `FOLDER`, `ex_task_version_range`, and `ck_task_version_range`, and ships `folder_id` as nullable. A tool that reports everything as different passes item 8, and so does a tool that finds only the task-name rule. Item 8 carries the highest weight, so list the expected differences at a pinned Gigacron commit and score each candidate on how many it finds and how many it invents. | Fixed. `expected-differences.md` lists every difference at the pinned commit before any candidate runs. Item 8 and Scoring count found and falsely reported differences (DEC-12).                                                                                                                                       |
| PROP-05 | 1    | major    | 02    | fixed  | The proposal does not say what may perform the comparison in item 8 (lines 144, 159). One option is the candidate's own tool. Another is a wrapper under DEC-07, and a third is a neutral tool such as `atlas schema diff` or SQLAlchemy reflection run on DDL that the candidate exports. If the DBML story may export DDL and compare it with Atlas, every candidate with a DDL generator meets requirement 4 the same way, and the high-weighted criterion stops telling the candidates apart. The proposal also does not say how a container loads `gigacron_server` models under the Docker-only rule (line 74). Decide whether a neutral comparison tool is allowed, and if so whether it counts as maintenance cost or as a separate shared option.              | Fixed. The comparison target is the live schema in a database container, built by a shared step. Only the candidate's tool or its wrapper compares; a combination with another candidate's tool scores as a generated pair (DEC-10). The section Building the live schema says how a container loads the Gigacron code. |
| PROP-06 | 1    | major    | 02    | fixed  | The proposal does not say how far the recommendation reaches. DEC-01 makes the PoC decide the factory-wide LinkML choice in `docs/spec/todo.md` T-0006, which applies to every project. The hard requirements, however, are tied to Gigacron: PostgreSQL, SQLAlchemy, and the dropped product-neutral requirement (DEC-02). The proposal names neither the repository that receives the ADR nor the file that holds the recommendation in the completion criterion (line 211). Say whether the result applies to Gigacron alone or sets the factory default. If it sets the default, say how the Gigacron-specific criteria carry over to other projects.                                                                                                               | Fixed. The recommendation sets the factory standard, with Gigacron as the test case. The ADR goes to the factory's `docs/adr/`, the recommendation to `recommendation.md`, and the criteria are project-neutral (DEC-08, DEC-09, DEC-10).                                                                               |
| PROP-07 | 1    | minor    | 02    | fixed  | The deferred list lets "a story revive any of the three" excluded candidates (line 183), while Scope (line 176) and Completion Criteria (line 208) fix the count at four. A planner cannot tell whether a fifth story is in scope or how a revived candidate enters the Pugh Matrix. Either drop the revival clause, or say that a revival produces a finding for the stakeholder and no story.                                                                                                                                                                                                                                                                                                                                                                         | Fixed. A revival produces a finding for the stakeholder and no fifth story (DEC-13).                                                                                                                                                                                                                                    |
| PROP-08 | 1    | minor    | 05    | fixed  | The boundary `.agent-factory/factory/scripts/structurizr` (line 18) is the installed copy, and `.gitignore` excludes it, so the path does not resolve at the reviewed commit. The template asks for tracked paths, and the tracked source is `packages/factory/scripts/structurizr`. The body links to `technical-poc.md`, `pugh-matrix`, `branching-policy.md`, and `structurizr` point into the same untracked tree (lines 58, 74, 128, 178, 191, 195).                                                                                                                                                                                                                                                                                                               | Fixed. The boundary and all body links point to `packages/factory/`, the tracked source. `docs/spec/todo.md` is added as a boundary, because T-0006 depends on the result.                                                                                                                                              |

## Review passes

| Pass | Date       | Reviewed commit                          | Disposition | Failed checks  | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---- | ---------- | ---------------------------------------- | ----------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | 2026-10-29 | f5d8b73762ae33513388db8137f30767f8830c4c | findings    | 01, 02, 03, 05 | The impact classification, the open questions, the motivation, and the `unknown` estimate pass. The acid slice misstates two `FOLDER` constraints, and three Definition-of-Done items cannot be judged without an expected result: construct 12, the semantic error, and the comparison with the mappings. Before planning, the proposal must also settle which tool may compare model and code, and whether the recommendation binds Gigacron or the factory. Gigacron facts were checked at commit 40954f18. |
