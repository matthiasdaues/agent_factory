---
title: "Comparison Note: DBML"
---

# Comparison Note: DBML

**Tools:** `@dbml/cli` 11.0.0 and `@dbml/core` 11.0.0 (Apache-2.0), and
`@softwaretechnik/dbml-renderer` 1.0.31 (ISC), installed with `npm` into the
Docker volume `dsl-poc-dbml-node` from the image `node:20-bookworm`.
**Gigacron:** `40954f18`. **Run on:** 2026-10-29.

## Result in short

DBML expresses nine of the twelve constructs directly and keeps them in its
PostgreSQL DDL. A wrapper adds construct 12. It meets all four hard requirements only with wrappers. `dbml2sql` exits 0
on broken models, as the survey suspected. The renderer cannot read the
`checks` block and ignores `DiagramView`. The comparison wrapper found 13 of
the 16 expected differences and reported 4 falsely.

## Definition of Done

**1. Slice expressed.** [acid-slice.dbml](../dbml/acid-slice.dbml). Gaps are
marked `NOT EXPRESSED` in the file.

| No. | Construct                    | In DBML                                                                                                                                      |
| --- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Composite primary key        | Expressed: `(task_instance_id, attempt_no) [pk]`.                                                                                            |
| 2   | Composite foreign key        | Expressed: `Ref: task_version.(domain_id, task_id) > task.(domain_id, task_id)`.                                                             |
| 3   | JSON payload column          | Expressed: column type `jsonb`.                                                                                                              |
| 4   | Enumerated string domain     | Expressed as `Enum`.                                                                                                                         |
| 5   | Self-referencing foreign key | Expressed.                                                                                                                                   |
| 6   | Nullable foreign key         | Expressed, including the composite `outbox_attempt_fk`.                                                                                      |
| 7   | Multi-column UNIQUE          | Expressed as a unique index.                                                                                                                 |
| 8   | Partial UNIQUE               | Not expressed. Indexes take no `WHERE`. `uq_outbox_attempt` keeps its meaning as a full UNIQUE, because PostgreSQL treats NULLs as distinct. |
| 9   | One-to-zero-or-one           | Expressed through `uq_outbox_attempt` and a `-` reference.                                                                                   |
| 10  | CHECK across columns         | Expressed in a `checks` block.                                                                                                               |
| 11  | Exclusion constraint         | Not expressed.                                                                                                                               |
| 12  | `domain_id` convention       | Through the wrapper, see item 3. The Domain-owned tables form the `TableGroup domain_owned`.                                                 |

**2. Valid slice.** `dbml2sql --postgres acid-slice.dbml -o runs/acid-slice.sql`
exits 0 ([dbml2sql-valid.out](../dbml/runs/dbml2sql-valid.out)).

**3. Broken models.** Plain `dbml2sql`, then the
[wrapper](../dbml/dbml-validate.sh):

| File                    | Error                         | `dbml2sql` exit | Wrapper exit | Message                                                  |
| ----------------------- | ----------------------------- | --------------- | ------------ | -------------------------------------------------------- |
| `broken-syntax.dbml`    | missing `]` in column setting | 0               | 1            | `(90,20): Expect an identifier`                          |
| `broken-reference.dbml` | `Ref` to table `agent`        | 0               | 1            | `Table 'agent' does not exist in Schema 'public'`        |
| `broken-domain.dbml`    | `plan` without `domain_id`    | 0               | 1            | `table plan is domain-owned but has no column domain_id` |

`dbml2sql` prints `ERROR:` and the message for the first two files, writes no
SQL file, and still exits 0. The wrapper parses with `@dbml/core`, whose
`Parser` throws on both errors, and checks the `domain_owned` group.

**4. SVG.** `dbml-renderer` 1.0.31 fails on the valid slice with exit 1:
`Could not parse input at line 117:5. Expected "'", "'''", "\"", or whitespace but "`" found.`Line 117 opens the first`checks`block. The [render wrapper](../dbml/dbml-render.sh) removes every`checks`block from a copy and renders the copy to [acid-slice.svg](../out/dbml/acid-slice.svg) with exit 0. The diagram shows all nine tables, columns with types and NOT NULL marks, the composite keys and references, the enums, the self-reference, and the`domain_owned\` group as a frame. It shows no CHECK constraint.

**5. PNG.** `dbml-renderer` writes SVG only. No PNG.

**6. Generation.** `dbml2sql` generates DDL for PostgreSQL. The DDL keeps
constructs 1 to 7, 9, and 10, with these changes: multi-column UNIQUE becomes
`CREATE UNIQUE INDEX`, and every foreign key is `DEFERRABLE INITIALLY IMMEDIATE`
(11 of 11 in [acid-slice.sql](../dbml/runs/acid-slice.sql)). DBML has no
first-party generator for application types.

**7. Named views.** `@dbml/core` 11.0.0 parses a `DiagramView` block and returns
its tables under `diagramViews[].visibleEntities`. `dbml-renderer` rejects the
same block: `Expected … "TableGroup" … but "D" found.` No tool in this run draws
a named view.

**8. Comparison with the live schema.** DBML has no comparison tool. The
[wrapper](../dbml/dbml-compare.sh) loads the `dbml2sql` DDL into a fresh
database `dbml_scratch`, schema `application`, reflects it with SQLAlchemy, and
runs `alembic.autogenerate.compare_metadata` against the live database:

```bash
dbml/dbml-compare.sh dbml/acid-slice.dbml domain task task_version folder
```

Exit 0, 26 reported differences, output in [compare.out](../dbml/runs/compare.out).

| Entry | Result    | Evidence                                                                               |
| ----- | --------- | -------------------------------------------------------------------------------------- |
| D01   | not found | the wrapper sets the schema `application` itself                                       |
| D02   | found     | `modify_nullable` on `domain.state_changed_at`                                         |
| D03   | found     | `modify_type` `domain.state` `VARCHAR(length=16)` → `ENUM(…)`                          |
| D04   | found     | `remove_column` `task.name`                                                            |
| D05   | found     | `remove_constraint UniqueConstraint(domain_id, name)`                                  |
| D06   | found     | `remove_fk` `task_domain_id_fkey`, `add_fk` `task_domain_fk`                           |
| D07   | found     | `modify_nullable` on `task.state_changed_at`                                           |
| D08   | found     | `modify_type` `task.state` → `ENUM(…)`                                                 |
| D09   | found     | `add_column` `task_version.name`                                                       |
| D10   | found     | `add_column` `task_version.runs_until_set_by_folder_id`                                |
| D11   | found     | `modify_nullable` on `task_version.folder_id`                                          |
| D12   | found     | `modify_nullable` on `task_version.created_by`                                         |
| D13   | found     | `add_fk` `task_version_folder_fk`                                                      |
| D14   | found     | `add_fk` `task_version_set_by_folder_fk`                                               |
| D15   | not found | construct 11 is not expressed                                                          |
| D16   | not found | DBML expresses `ck_task_version_range`, but Alembic does not compare CHECK constraints |

False reports, 4, counted per constraint:

- `uq_domain_name`, `uq_task_domain`, `uq_task_version_number`: each appears
  as `remove_constraint` plus `add_index`, because `dbml2sql` writes a unique
  index where the live schema has a UNIQUE constraint. Both mean the same.
- `task_version_task_fk`: `remove_fk` plus `add_fk`. The columns match. The
  generated key is `DEFERRABLE`.

Unspecified reports: `uq_task_version_current` (construct 8) and the table
`folder` with its indexes.

**Score: (13 − 4) / 16 = 0.56.**

**9. Dialects.** `dbml2sql --help` lists `--mysql`, `--postgres`, `--mssql`, and
`--oracle`. DBML column types are free text, so a model can name any dialect's
type. Dialect-specific constraints beyond types, such as partial indexes and
exclusion constraints, have no syntax. DBML's documentation was not read in
this run.

**10. Commands.** Every command is above or in the three wrappers.

## Wrapper cost

- `dbml-validate.sh` turns errors into exit 1 and asserts construct 12. It
  calls DBML's own parser, so the cost is small.
- `dbml-render.sh` removes `checks` blocks before rendering, because the
  renderer lags behind the language.
- `dbml-compare.sh` provides the whole comparison, with Alembic, as for LinkML.
  Alembic does not compare CHECK constraints, so D16 stays hidden even though
  the model holds it.

## Survey claims

- The survey found no `process.exit(1)` in the `dbml2sql` source. Observed:
  `dbml2sql` exits 0 on a syntax error and on an undeclared table.
- The survey named `DiagramView` as the only model-aware named-view construct.
  Observed: the parser accepts it, and no renderer in this run draws it.
- The survey reported no official Docker image for DBML. This run used the
  generic `node:20-bookworm` image, so the claim stays as it was.
