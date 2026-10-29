---
schema_version: 2
title: Data-Model DSL Technical Proof-of-Concept
status: open
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
    - .agent-factory/factory/scripts/structurizr

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

Gigacron is an enterprise job scheduler. Its entity model describes the data that Gigacron stores in its PostgreSQL database: 29 entities and the constraints on each one. The model is a Mermaid diagram, and no tool checks it. Developers have written the Python code that maps four of the tables with the SQLAlchemy library.

The model and the code already disagree. The code declares a uniqueness rule on task names that the model does not have. In the model, a separate table keeps each name unique inside the Folder that contains the task. Nobody noticed the difference, because nothing compares the model with the code. That raises two questions. Which language can hold the model so that a tool can check it? And how does the model stay consistent with the code?

The design answers the second question first. The model file is the source of truth, and it changes through accepted proposals. The SQLAlchemy mappings follow the model. A developer writes a mapping by hand or generates a first version from the model. Either way, an automatic check called a gate compares the mappings with the model and fails on every difference. So the comparison is required, and generation is a convenience.

This proof-of-concept (PoC) answers the first question by running tools. An earlier survey only read the tools' documentation and source code, so it left the deciding questions open. The PoC tries four candidates: DBML (Database Markup Language), LinkML, Atlas HCL (HashiCorp Configuration Language), and the current Mermaid diagram as the baseline. Every candidate models the same slice of the model: nine entities that carry twelve constructs, such as composite keys. Each candidate must meet four hard requirements. The model is a plain-text file, and a validator fails on a broken model. A container renders the model to SVG. A command compares the model with the mappings. The task-name rule is the test case for that comparison.

Three rules shape the work:

- The slice keeps PostgreSQL features, because Gigacron uses PostgreSQL. A candidate that cannot express them records the loss in its comparison note.
- A candidate that misses a hard requirement may repair it with a thin wrapper script. A working wrapper meets the requirement but counts as maintenance cost. Without one, the candidate stays in the scoring with a heavy penalty, because a failed requirement is still a result.
- Two languages count as one option only when a command generates the second file from the first, so each constraint is written once.

The PoC ends with one comparison note per candidate and a Pugh Matrix, a table that scores options against weighted criteria. The stakeholder confirms the weights before scoring. The comparison with the code weighs high, and generation weighs low. The PoC recommends a language or defers with a stated reason, but it adopts nothing. A later architecture decision record makes the choice, and a human approves it. The task-name difference goes to Gigacron as a finding.

The proposal has no open questions.

## Summary

This proof-of-concept (PoC) settles by observation which text-based data-modeling language can hold Gigacron's entity model as a checked source of truth. Gigacron is an enterprise job scheduler, and its entity model describes the data it persists. Under the [technical-poc.md](../../.agent-factory/factory/playbooks/technical-poc.md) playbook, the PoC ports one fixed slice of today's model to four candidate languages. It runs each candidate and compares it with Gigacron's SQLAlchemy mappings. The first release ends with four comparison notes and a [Pugh Matrix](../../.agent-factory/factory/skills/pugh-matrix/SKILL.md), and it adopts no language (DEC-01).

## Motivation

Gigacron's persisted model lives as a Mermaid `erDiagram` in `docs/spec/supplementary_specs/entity-model.md` of the Gigacron repository. It holds 29 entities, a constraint table per entity, and the database comments. No tool validates it.

The [survey](survey-report.md) read each candidate's documentation and source code, but nobody installed or ran the tools. On that evidence, no candidate meets all three of the survey's hard requirements. The survey also found that expressive languages have weak tooling, and the reverse. Its `candidates_for_deeper_falsification_study` list in [survey-report.json](survey-report.json) names the open questions and the command that answers each one. Two of them decide the outcome. Does `dbml2sql` exit non-zero on a broken model? Do LinkML's generators keep a composite key and a CHECK constraint? Only running the tools answers them.

Since the survey, the Gigacron code has begun. The SQLAlchemy mappings in `domain_registry/models.py` and `task_registry/models.py` cover `domain`, `task`, `task_draft`, and `task_version`. In Gigacron, a Domain is one scheduling domain, such as `production-eu` or `staging`, and every Domain-owned table carries its `domain_id`. A Folder groups Tasks inside a Domain. The mappings already disagree with the model. The code declares `uq_task_domain_name (domain_id, name)` on `task`. The model has no such constraint, because a separate `NAME_CLAIM` table keeps each name unique inside its containing Folder. Nobody noticed the difference, because nothing compares the model with the code.

So the question has two parts. First, which language can express the model and be checked by a gate? Second, how does the model stay consistent with the code that implements it?

## Core Principles

- **One fixed slice, ported identically.** Every candidate models the same nine entities. No candidate picks the example that suits it.
- **Observation outranks documentation.** Every claim in a comparison note comes from a command that was run and an output that was seen. Where a note cannot back a claim this way, it says so.
- **Docker only.** Every candidate runs only through `docker run --rm`, like [structurizr](../../.agent-factory/factory/scripts/structurizr). A capability that needs a local install fails the requirement it claims to meet.
- **The model must be checkable against the code.** A language whose model cannot be compared with the SQLAlchemy mappings cannot catch a difference such as `uq_task_domain_name`.
- **A failed requirement is a result.** A candidate that misses a [Definition-of-Done](#per-story-definition-of-done) item, even with a wrapper, is recorded as answered. It stays in the Pugh Matrix with the penalty that [Scoring](#scoring) describes (DEC-07). It gets no more time than the others got.
- **The PoC decides nothing by itself.** It produces comparison notes, a Pugh Matrix, and a recommendation. The architecture decision record (ADR) comes later, and a human approves it.

## Design

### The target database

Gigacron uses PostgreSQL (Gigacron ADR-0006 and ADR-0010). The model already uses PostgreSQL features: `jsonb`, partial unique indexes, and an exclusion constraint on `btree_gist`. The [acid slice](#the-acid-slice) keeps them. A candidate that can express only portable SQL loses those constructs, and its note records the loss (DEC-02).

### Model and code

The model file is the source of truth for the persisted schema. It changes when the specification changes, and the specification changes through accepted proposals. The SQLAlchemy mappings follow the model. A developer may write a mapping by hand, or generate a first version from the model and then edit it. In both cases, a gate compares the mappings with the model and fails on every difference (DEC-04). So the comparison is required, and generation is a convenience.

One file is edited by hand. The PoC may recommend a pair of languages, but only when a command generates the second artifact from the first. A constraint is then written once (DEC-05).

### The acid slice

The acid slice is the part of the model that tests each candidate hardest, as an acid test does. It is the fixed input to every candidate story: nine entities from today's `entity-model.md` that together carry the twelve constructs below (DEC-03).

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

| Entity          | Constructs it contributes                                                                                                                                                                                                                   |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DOMAIN`        | root of the `domain_id` convention; single-column UNIQUE `uq_domain_name`                                                                                                                                                                   |
| `TASK`          | multi-column UNIQUE `uq_task_domain (domain_id, task_id)` as the target of composite foreign keys                                                                                                                                           |
| `FOLDER`        | partial UNIQUE `uq_folder_root_per_domain` (`domain_id` WHERE `is_root`); CHECK across two columns `ck_folder_root_regular`; enumerated `state`                                                                                             |
| `TASK_VERSION`  | six `jsonb` sections; composite foreign keys to `TASK` and `FOLDER`; two foreign keys to `FOLDER` from one table; multi-column UNIQUE `uq_task_version_number`; CHECK `ck_task_version_range`; exclusion constraint `ex_task_version_range` |
| `PLAN`          | multi-column UNIQUE `uq_plan_domain_odate (domain_id, odate)`, not tied to the primary key                                                                                                                                                  |
| `TASK_INSTANCE` | parent of `ATTEMPT`; enumerated `state`; `jsonb` `filled_values`                                                                                                                                                                            |
| `ATTEMPT`       | composite primary key `(task_instance_id, attempt_no)`; partial UNIQUE `uq_attempt_open` with an enum predicate; enumerated `attempt_state`                                                                                                 |
| `OUTBOX`        | nullable composite foreign key to `ATTEMPT`; the zero-or-one side of the one-to-zero-or-one relationship from `ATTEMPT`                                                                                                                     |
| `AUDIT_EVENT`   | self-referencing foreign key `supersedes_event_id`                                                                                                                                                                                          |

The entities keep their columns unchanged. A foreign key that points outside the slice is left out, and `acid-slice.md` lists each one.

Two artifacts are written once and reused by every story. `acid-slice.md` is the readable specification of the nine entities and their constraints. `acid-slice-broken.<ext>` is a broken model, one per candidate. It carries one syntax error and one semantic error, so the stories can observe how each validator behaves. The semantic error is a relationship to an undeclared entity.

### One story per candidate

Each story is a plain Markdown file under `poc/data_model_from_dsl/stories/`, per [technical-poc.md § Step 1](../../.agent-factory/factory/playbooks/technical-poc.md). Each story states its goal, the risk it tests, what to build, a mechanical Definition of Done, and the instruction to write a comparison note.

The four candidates and the question each story settles:

- **DBML.** Does `dbml2sql` exit non-zero on a broken model? The survey read the CLI source and found no `process.exit(1)`. Does any renderer honour `DiagramView`? A named view shows a chosen subset of the entities from one model, and `DiagramView` is the only construct of that kind in the field.
- **LinkML.** Do the first-party Pydantic, SQLAlchemy, and SQL DDL generators keep the composite key, the composite foreign key, the JSON column, the enumerated domain, and the CHECK constraint? Can the generated SQLAlchemy code be compared with Gigacron's hand-written mappings?
- **Atlas HCL.** Can Atlas validate the HCL file against an ephemeral PostgreSQL container? Can it compare the HCL file with the SQLAlchemy mappings? Which Docker tag family carries which licence? The survey left that open.
- **Mermaid erDiagram (the incumbent baseline).** Does `mmdc`, the Mermaid command-line renderer, render a relationship to an undeclared entity without an error? Running the baseline on the same slice makes "better than what we have" a finding, not an assertion.

### Hard requirements

A candidate, or a generated pair, must meet four hard requirements. The first three come from the survey's three. The survey also required a product-neutral language and PNG output; DEC-02 and DEC-06 drop both. The fourth is new (DEC-04).

1. The model is a plain-text file under version control.
2. A validator exits non-zero on a broken model.
3. A container with no local install renders the model to SVG.
4. A command compares the model with the SQLAlchemy mappings and reports differences.

A candidate that fails a hard requirement may repair it with a thin wrapper around its tool. The story builds the wrapper and runs it, for example a script that turns `dbml2sql`'s error output into exit code 1. If the wrapper works, the requirement counts as met (DEC-07). [Scoring](#scoring) says how a wrapper and a failed requirement count.

### Per-story Definition of Done

Each item is mechanical and has the same shape for every candidate:

1. The acid slice is expressed in the candidate's language. Where a construct cannot be expressed, the story names it and records what was substituted.
2. `docker run --rm <image> <validate-command>` runs against the valid slice and exits 0.
3. The same command runs against `acid-slice-broken`. The note records the exact numeric exit code and whether the semantic error was detected.
4. A container with no local install produces SVG into `poc/data_model_from_dsl/out/<candidate>/`.
5. Where the container also produces PNG, the note records it. PNG is optional, because no consumer reads a rendered PNG diagram (DEC-06).
6. Where the candidate claims application-type or DDL generation, the generator runs. The note marks each of the twelve constructs as kept or lost in the output.
7. Where the candidate claims named views, a view over a subset of the nine entities is produced, and the rendered result is inspected.
8. The slice is compared with the SQLAlchemy mappings for `domain`, `task`, and `task_version` by a command. The note records whether the comparison reports the `uq_task_domain_name` difference, and which constructs the comparison can see.
9. The comparison note captures every command verbatim, so a reader can run it again.

### Scoring

The Pugh Matrix scores the candidates from their comparison notes. The stakeholder confirms the weights before scoring.

- The comparison with the mappings (item 8) carries a high weight. Generation (item 6) carries a low weight (DEC-04).
- A generated pair of languages may score as one option (DEC-05).
- A working wrapper counts as maintenance cost. A candidate without a working wrapper stays in the matrix with a heavy weighted penalty, and the matrix records the failed requirement (DEC-07).
- PNG output does not count (DEC-06).

## Scope

**In the first release:**

- `acid-slice.md` and one broken model per candidate.
- Four candidate stories: DBML, LinkML, Atlas HCL, and Mermaid erDiagram.
- Four comparison notes, each answering the nine Definition-of-Done items.
- A Pugh Matrix over the four candidates, scored from the comparison notes with [pugh-matrix](../../.agent-factory/factory/skills/pugh-matrix/SKILL.md).
- A written recommendation, or an explicit deferral with a stated reason.

**Explicitly deferred (do NOT plan stories for these):**

- **Prisma, PlantUML IE, and D2.** The survey's evidence excludes each one. Prisma has no official Docker image, cannot express CHECK constraints, and has only an archived Python generator. PlantUML reduces composite keys, multi-column UNIQUE, and value constraints to free-text notes, so a validator cannot check those constraints. D2 cannot express six of the survey's ten constructs, the older list that DEC-03 replaced with twelve, and cannot represent multi-column foreign keys. A story may revive any of the three if it finds evidence that overturns the exclusion.
- Porting the full 29-entity model. The PoC ports only the slice. The full port belongs to adoption.
- Writing the ADR, or changing `entity-model.md` or the SQLAlchemy mappings. The `uq_task_domain_name` difference is a finding for Gigacron, not work for this PoC.
- A Docker wrapper script for the chosen candidate as shipped tooling. The wrappers that stories build under DEC-07 stay spike code under `poc/data_model_from_dsl/`.
- Alembic migrations, CI integration, and pre-commit gates. They depend on the chosen language and belong to adoption.

## Design Details

Prototype material lives under `poc/data_model_from_dsl/` and stays marked as spike code, per [technical-poc.md § DONE](../../.agent-factory/factory/playbooks/technical-poc.md).

The PoC reads Gigacron's files and never writes to them. The comparison in Definition-of-Done item 8 reads the SQLAlchemy mappings from the Gigacron checkout. A story records the Gigacron commit it read.

The candidates are independent, so their stories may run in parallel, one worktree per candidate, per [branching-policy.md § Every Branch Has A Worktree](../../.agent-factory/factory/rulebooks/conventions/branching-policy.md#every-branch-has-a-worktree). The orchestrating session builds each candidate itself and starts no subagent, per [technical-poc.md § Step 2](../../.agent-factory/factory/playbooks/technical-poc.md).

Where the survey recorded a documented claim, the comparison note says whether observation confirmed or contradicted it. The note cites the survey's source record by filename, so the PoC's evidence extends the survey's evidence instead of starting over.

Where a candidate needs a live database, the story uses an ephemeral PostgreSQL container. The note records the dependency.

## Open Questions

None.

## Completion Criteria

- `acid-slice.md` exists and contains all twelve constructs.
- Each of the four candidates has a comparison note that answers all nine Definition-of-Done items, or states why an item could not be answered.
- Every exit code in every note comes from a command that was run, never from documentation.
- A Pugh Matrix scores the four candidates against weighted criteria taken from the comparison notes. The stakeholder confirmed the weights before scoring.
- A recommendation is recorded, or the decision is deferred with a stated reason.
- Nothing under `poc/` has been promoted into the specification, the architecture, or the factory scripts.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by     | Decision                                                                                                                                                                                                                                                                | Raised by                                                       |
| ------ | ---------- | -------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| DEC-01 | 2026-10-29 | decision | Matthias Daues | Run this PoC before the factory adopts any entity-model language. The LinkML choice in the factory's T-0006 stays an assumption until the Pugh Matrix and the ADR confirm it.                                                                                           | Effort question on introducing LinkML                           |
| DEC-02 | 2026-10-29 | decision | Matthias Daues | Refresh the proposal in place. PostgreSQL replaces the product-neutral requirement, because Gigacron's ADR-0006 and ADR-0010 use it. A comparison with the SQLAlchemy mappings becomes a Definition-of-Done item.                                                       | The 2026-10-29 model rewrite and the code in Gigacron           |
| DEC-03 | 2026-10-29 | decision | Matthias Daues | The slice changes to `DOMAIN`, `TASK`, `FOLDER`, `TASK_VERSION`, `PLAN`, `TASK_INSTANCE`, `ATTEMPT`, `OUTBOX`, and `AUDIT_EVENT`. The construct list drops "several logical schemas" and adds composite foreign keys, partial UNIQUE, CHECK, and exclusion constraints. | Four slice entities removed in the 2026-10-29 model             |
| DEC-04 | 2026-10-29 | decision | Matthias Daues | The model is the source of truth and changes through specification updates from accepted proposals. Mappings are written by hand or generated as a first version; a gate compares them with the model. Comparison weighs high, generation low.                          | Grilling: Open Question on the direction between model and code |
| DEC-05 | 2026-10-29 | decision | Matthias Daues | A pair of languages is acceptable only when a command generates the second artifact from the hand-edited first. The Pugh Matrix may score such a pair as one option. Two hand-kept files are not acceptable.                                                            | Grilling: Open Question on a two-language split                 |
| DEC-06 | 2026-10-29 | decision | Matthias Daues | SVG rendering from a container is required. PNG is optional and does not count in the Pugh Matrix. No file in Gigacron or the factory reads a rendered PNG diagram, and `publish-docs` uses vector diagrams.                                                            | Grilling: Open Question on the PNG requirement                  |
| DEC-07 | 2026-10-29 | decision | Matthias Daues | A candidate that fails a hard requirement may repair it with a thin wrapper that the story builds and runs. A working wrapper meets the requirement and counts as maintenance cost. Without one, the candidate takes a heavy weighted penalty and stays in the matrix.  | Grilling: Open Question on scoring a failed hard requirement    |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
