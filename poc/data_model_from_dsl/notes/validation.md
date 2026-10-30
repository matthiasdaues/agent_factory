---
title: "Comparison Note: Validation Depth and Oracle"
---

# Comparison Note: Validation Depth and Oracle

**Tools:** `@dbml/cli` and `@dbml/core` 11.0.0 in the volume
`dsl-poc-dbml-node`; `linkml` 1.12.1 in the volume `dsl-poc-linkml-venv`.
**Run on:** 2026-10-29. No database was used.

## Result in short

DBML's parser caught 8 of 12 semantic errors. LinkML's linter caught 5 of the
7 errors that can arise in LinkML; the other 5 cannot occur, because LinkML
references point to classes, not to columns. Each validator misses errors that
a thin factory lint can add. DBML holds a legacy Oracle schema as written,
including a function-based index, and imports Oracle DDL. LinkML loses the
Oracle enum values, the time zone, and the JSON columns in its Oracle DDL, and
has no import tool in this installation.

## Validation depth

Validators: `dbml2sql --postgres` (DBML's CLI), `dbml-validate.sh` (DBML's
parser `@dbml/core` plus the domain rule), and `linkml-lint --ignore-warnings`.
The LinkML wrapper `linkml-validate.sh` gave the same exit code as the linter
in every case. Raw rows: [results.tsv](../validation/results.tsv).

| Case | Error                                             | `dbml2sql` | `@dbml/core` | `linkml-lint` | First message                                                        |
| ---- | ------------------------------------------------- | ---------- | ------------ | ------------- | -------------------------------------------------------------------- |
| E01  | reference to a column that does not exist         | 0          | **1**        | n/a           | DBML: `Column 'domain_key' does not exist in Table 'public.domain'`  |
| E02  | unique key on a column that does not exist        | 0          | **1**        | 0             | DBML: `No column named 'odate_x' inside Table 'plan'`                |
| E03  | composite reference with mismatched column counts | 0          | **1**        | n/a           | DBML: `Unequal fields in ref endpoints`                              |
| E04  | foreign key type differs from the target          | 0          | 0            | n/a           | none                                                                 |
| E05  | duplicate table                                   | 0          | **1**        | **2**         | DBML: `Table 'plan' already exists`; LinkML: `Duplicate key: "Plan"` |
| E06  | duplicate column                                  | 0          | **1**        | **2**         | DBML: `Duplicate column 'odate'`; LinkML: `Duplicate key: "odate"`   |
| E07  | type that is not defined                          | 0          | 0            | **2**         | LinkML: `range 'PlanStatus' is not defined. (no_undeclared_ranges)`  |
| E08  | duplicate enum value                              | 0          | **1**        | **2**         | DBML: `Duplicate enum field 'OPEN'`; LinkML: `Duplicate key: "OPEN"` |
| E09  | primary key on a column that does not exist       | 0          | **1**        | n/a           | DBML: `No column named 'plan_key' inside Table 'plan'`               |
| E10  | check or rule names a column that does not exist  | 0          | 0            | 0             | none                                                                 |
| E11  | two primary keys in one table                     | 0          | 0            | **2**         | LinkML: `Class 'Plan' has more than one 'identifier' slot`           |
| E12  | group member that does not exist                  | 0          | **1**        | n/a           | DBML: `Table 'task_x' does not exist in Schema 'public'`             |
|      | **Caught**                                        | **0 / 12** | **8 / 12**   | **5 / 7**     |                                                                      |

Not applicable in LinkML: E01, E04, and E09, because a reference names a class
and takes its key from there; E03, because LinkML has no composite
references; E12, because LinkML has no groups.

What a factory lint would add, judged from the parsers' models (not built in
this run):

- DBML: E04 and E11 from the `@dbml/core` model, which lists field types and
  primary keys. E07 needs a list of allowed types per database. E10 needs a
  SQL expression parser, because DBML stores checks as free text.
- LinkML: E02 and E10 from `SchemaView`, which lists slots per class.

## Oracle without an Oracle database

**O1. DBML slice with Oracle types.**
[acid-slice.oracle.dbml](../validation/oracle/acid-slice.oracle.dbml) uses
`NUMBER(19)`, `VARCHAR2(4000)`, `CLOB`, `"TIMESTAMP WITH TIME ZONE"`, and
`database_type: 'Oracle'`. `@dbml/core` exits 0. `dbml2sql --oracle` exits 0
and writes [acid-slice.oracle.sql](../validation/oracle/acid-slice.oracle.sql):
enums become `CHECK ("state" IN (…))`, the composite key and composite foreign
keys stay, and the `checks` expressions are copied verbatim.
`ck_outbox_attempt` compares truth values, which is PostgreSQL syntax. Whether
Oracle accepts it is unchecked; it is likely not, because Oracle SQL had no
boolean type before 23ai.

**O2. Import from Oracle DDL.** `sql2dbml --oracle` on
[legacy.oracle.sql](../validation/oracle/legacy.oracle.sql) exits 0 and writes
[legacy.from-oracle.dbml](../validation/oracle/legacy.from-oracle.dbml). It
keeps the Oracle types, the CHECK constraints with their names, the composite
foreign key, and the function-based index
`CASE WHEN superseded_at IS NULL THEN task_id END` as a unique expression index.
`@dbml/core` accepts the imported file with exit 0.

**O3. LinkML to Oracle DDL.** `gen-sqltables --dialect oracle` exits 0 and
writes [o3-linkml-oracle.sql](../validation/oracle/o3-linkml-oracle.sql):
enums become `VARCHAR(8 CHAR)` with no CHECK, so the values are lost;
`datetime` becomes `DATE` without a time zone; the JSON slots become a table
`"Any"`; 7 UNIQUE entries remain. The installation has `gen-*` generators but
no tool that imports DDL or a database into a LinkML schema.

## Finding for the DBML story

The reference `outbox_attempt_fk` is written with `-` (one-to-one). Both
`dbml2sql --postgres` and `--oracle` place the foreign key on `attempt`,
pointing to `outbox`: line 236 of [acid-slice.sql](../dbml/runs/acid-slice.sql).
The model wants the key on `outbox`, pointing to `attempt`. DBML's `-` does not
say which side owns the key, and `dbml2sql` picks the right-hand side. Written
as `>` with the existing UNIQUE index, the direction would be explicit. The
comparison score of the DBML story is not affected, because it compared
`domain`, `task`, `task_version`, and `folder` only.
