---
title: "Story: Validation Depth and Oracle"
---

# Story: Validation Depth and Oracle

**Goal.** Measure how deep the DBML and LinkML validators check a model, and
whether both hold a legacy Oracle schema, without an Oracle database.

**Why this is a comparison case.** Validation is the reason the entity model
exists as a file, as `structurizr validate` is for `architecture.dsl`. The
candidate stories tested three errors only. Legacy systems in Java or C on
Oracle are in scope, and the slice uses PostgreSQL only.

**What to build.**

- Twelve semantic error cases, each one change to the valid slice, generated
  by [make-cases.py](../validation/make-cases.py) and run by
  [run-cases.sh](../validation/run-cases.sh). A case that cannot arise in a
  language is marked not applicable.
- The DBML slice with Oracle types, validated and turned into Oracle DDL.
- Oracle DDL in the style of a legacy schema, imported with `sql2dbml --oracle`.
- The LinkML slice turned into Oracle DDL.

**Definition of Done.** Every exit code and first error line is recorded in
[results.tsv](../validation/results.tsv) and the logs under `validation/runs/`
and `validation/oracle/`.

**Output.** The comparison note [notes/validation.md](../notes/validation.md).
