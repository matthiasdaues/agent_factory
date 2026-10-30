---
title: "Comparison Note: LinkML"
---

# Comparison Note: LinkML

**Tool:** `linkml` 1.12.1 and `linkml-runtime` 1.12.1, installed with `uv pip`
into the Docker volume `dsl-poc-linkml-venv` from the image
`ghcr.io/astral-sh/uv:python3.12-bookworm`. **Gigacron:** `40954f18`.
**Run on:** 2026-10-29.

## Result in short

LinkML meets all four hard requirements, two of them only with a wrapper. It
cannot express five of the twelve constructs. Its generators lose more: the
SQL and SQLAlchemy output has no constraint names, no `bigint`, no time zone,
no JSON columns, and the SQLAlchemy output drops every unique key. The
comparison wrapper found 12 of the 16 expected differences, including
`uq_task_domain_name`, and reported 3 falsely.

## Definition of Done

**1. Slice expressed.** [acid-slice.yaml](../linkml/acid-slice.yaml). Each gap
is marked `NOT EXPRESSED` in the file.

| No. | Construct                    | In LinkML                                                                                                                                          |
| --- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Composite primary key        | Workaround. A class has at most one `identifier`, so `attempt_pkey` is a `unique_keys` entry.                                                      |
| 2   | Composite foreign key        | Not expressed. A slot references one class through its single identifier.                                                                          |
| 3   | JSON payload column          | Not expressed as a column. `range: Any` is a class, and the generators turn it into a table.                                                       |
| 4   | Enumerated string domain     | Expressed as `enums`.                                                                                                                              |
| 5   | Self-referencing foreign key | Expressed: `supersedes_event_id` has `range: AuditEvent`.                                                                                          |
| 6   | Nullable foreign key         | Expressed for single columns. `outbox_attempt_fk` is composite, see 2.                                                                             |
| 7   | Multi-column UNIQUE          | Expressed as `unique_keys`.                                                                                                                        |
| 8   | Partial UNIQUE               | Not expressed.                                                                                                                                     |
| 9   | One-to-zero-or-one           | Not expressed. It rests on the partial `uq_outbox_attempt`.                                                                                        |
| 10  | CHECK across columns         | Partly. `ck_folder_state` and half of `ck_outbox_attempt` are `rules`. `ck_task_version_range` compares two slots, which `slot_conditions` cannot. |
| 11  | Exclusion constraint         | Not expressed.                                                                                                                                     |
| 12  | `domain_id` convention       | Through the wrapper, see item 3. Domain-owned classes carry the annotation `domain_owned: true`.                                                   |

Types: LinkML's `integer` stands for `bigint` and `smallint`, and `datetime`
stands for `timestamptz`. The schema keeps the table names as `sql_table`
annotations.

**2. Valid slice.** `linkml-lint --ignore-warnings acid-slice.yaml` exits 0.
Without `--ignore-warnings` it exits 1 on 125 warnings and no errors
([lint-warnings.out](../linkml/runs/lint-warnings.out)): 90 `recommended`
(missing descriptions), 33 `standard_naming` (upper-case enum values, which
the model requires), and 1 `canonical_prefixes`.

**3. Broken models.** Plain `linkml-lint --ignore-warnings`, then the
[wrapper](../linkml/linkml-validate.sh):

| File                    | Error                           | Lint exit | Wrapper exit | Message                                                |
| ----------------------- | ------------------------------- | --------- | ------------ | ------------------------------------------------------ |
| `broken-syntax.yaml`    | missing `:` after `annotations` | 2         | 2            | YAML parse error at line 42 (`valid-schema`)           |
| `broken-reference.yaml` | `agent_id` with `range: Agent`  | 2         | 2            | `range 'Agent' is not defined. (no_undeclared_ranges)` |
| `broken-domain.yaml`    | `Plan` without `domain_id`      | 0         | 1            | `class Plan is domain-owned but has no slot domain_id` |

The wrapper reads the annotation through `linkml_runtime.SchemaView`. A first
version of the wrapper exited 0 on `broken-domain.yaml`, because `docker run`
without `-i` passed no script to Python. The fixed version is the one above.

**4. SVG.** `gen-erdiagram` writes Mermaid inside Markdown. The fenced block is
[acid-slice.mmd](../out/linkml/acid-slice.mmd), and `minlag/mermaid-cli` 12.0.0
renders [acid-slice.svg](../out/linkml/acid-slice.svg). Both exit 0. The
diagram sorts columns alphabetically and marks no keys. Reference slots and
JSON slots appear as lines to other boxes, not as columns. No UNIQUE or CHECK
constraint appears.

**5. PNG.** The same `mmdc` call writes
[acid-slice.png](../out/linkml/acid-slice.png).

**6. Generation.** All generators exit 0. Output in [gen/](../linkml/gen/).

| Construct             | `gen-sqltables --dialect postgresql` | `gen-sqla`           | `gen-pydantic`     |
| --------------------- | ------------------------------------ | -------------------- | ------------------ |
| 1 Composite PK        | lost: surrogate `id`, plus UNIQUE    | lost: surrogate `id` | lost               |
| 2 Composite FK        | lost                                 | lost                 | lost               |
| 3 JSON column         | lost: FK to table `"Any"`            | lost: FK to `Any`    | field typed `Any`  |
| 4 Enum                | kept: `CREATE TYPE … AS ENUM`        | kept                 | kept               |
| 5 Self-reference      | kept                                 | kept                 | kept as an integer |
| 6 Nullable FK         | kept (single column)                 | kept                 | kept               |
| 7 Multi-column UNIQUE | kept, unnamed                        | lost                 | metadata only      |
| 10 CHECK (`rules`)    | lost                                 | lost                 | metadata only      |

Table names follow the class names (`"TaskVersion"`), not the `sql_table`
annotation. Every integer becomes `INTEGER` or `SERIAL`. Constraint names are
lost.

**7. Named views.** LinkML has no named-view construct. Nothing to run.

**8. Comparison with the live schema.** LinkML has no comparison tool. The
[wrapper](../linkml/linkml-compare.sh) generates SQLAlchemy code with
`gen-sqla`, renames each table to its `sql_table` annotation in the schema
`application`, and runs `alembic.autogenerate.compare_metadata` against the
live database:

```bash
linkml/linkml-compare.sh linkml/acid-slice.yaml domain task task_version folder
```

Exit 0, 52 reported differences, output in
[compare.out](../linkml/runs/compare.out). `folder` is in scope so that the
foreign keys to it can appear.

| Entry | Result    | Evidence                                                      |
| ----- | --------- | ------------------------------------------------------------- |
| D01   | not found | the wrapper sets the schema `application` itself              |
| D02   | found     | `modify_nullable` on `domain.state_changed_at`                |
| D03   | found     | `modify_type` `domain.state` `VARCHAR(length=16)` → `Enum(…)` |
| D04   | found     | `remove_column` `task.name`                                   |
| D05   | found     | `remove_constraint UniqueConstraint(domain_id, name)`         |
| D06   | not found | LinkML has no foreign-key names                               |
| D07   | found     | `modify_nullable` on `task.state_changed_at`                  |
| D08   | found     | `modify_type` `task.state` → `Enum(…)`                        |
| D09   | found     | `add_column` `task_version.name`                              |
| D10   | found     | `add_column` `task_version.runs_until_set_by_folder_id`       |
| D11   | found     | `modify_nullable` on `task_version.folder_id`                 |
| D12   | found     | `modify_nullable` on `task_version.created_by`                |
| D13   | found     | `add_fk` `folder_id` → `folder.folder_id` (single column)     |
| D14   | found     | `add_fk` `runs_until_set_by_folder_id` → `folder.folder_id`   |
| D15   | not found | construct 11 is not expressed                                 |
| D16   | not found | `ck_task_version_range` is not expressed                      |

False reports, 3: `remove_constraint` for `uq_domain_name`, `uq_task_domain`,
and `uq_task_version_number`. The LinkML schema declares all three as
`unique_keys`, but `gen-sqla` drops them, so the comparison claims the model
lacks them.

Unspecified reports: the `jsonb` columns replaced by `*_id` foreign keys to
`Any` (construct 3), `Integer` against `BIGINT` and `DateTime` against
`TIMESTAMP(timezone=True)` (types LinkML cannot state), `Text` against
`VARCHAR`, identity defaults, single-column foreign keys in place of the
composite ones (construct 2), `uq_task_version_current` (construct 8), and the
table `folder`.

**Score: (12 − 3) / 16 = 0.56.**

**9. Dialects.** `gen-sqltables --help` says `--dialect TEXT  SQL-Alchemy dialect, e.g. sqlite, mysql+odbc [default: sqlite]`. So the DDL generator
targets whatever SQLAlchemy supports. The LinkML language itself has no
dialect-specific constructs, so no dialect-specific constraint can be stated.
LinkML's documentation was not read in this run.

**10. Commands.** Every command is above, in the wrappers, or in
[build-live-schema.sh](../live-schema/build-live-schema.sh).

## Wrapper cost

- `linkml-validate.sh` asserts construct 12. LinkML's linter has no custom rules.
- `linkml-compare.sh` provides the whole comparison: code generation, table
  renaming, and an Alembic comparison. It is the largest wrapper in the PoC so
  far, and it depends on Alembic, which is not part of LinkML.

## Licence

`linkml` is published on PyPI. This run did not read its licence file.

## Survey claims

- The survey rated composite keys and JSON columns as workarounds, and
  questioned whether constructs survive generation. Observed: both workarounds
  hold in the schema but do not survive `gen-sqltables` or `gen-sqla`.
- The survey reported that LinkML's diagram generator cannot produce SVG.
  Observed: `gen-erdiagram` writes Mermaid, and `mmdc` renders it to SVG in a
  container.
