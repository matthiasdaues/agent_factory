---
title: "Recommendation: Entity-Model Language"
---

# Recommendation: Entity-Model Language

**Recommendation.** DBML becomes the factory standard for a project's entity
model. It plays the role for the data model that `architecture.dsl` plays for
the architecture: one file, a validator with exit codes, named views rendered
to SVG, and a lint hook for drift (DEC-15). Gigacron was the test case; the
standard applies to every project (DEC-08).

**Why.** DBML scored +193 and LinkML +120 against the Mermaid baseline. Both
validate deeply, but only DBML holds a legacy Oracle schema and imports one,
names its views inside the model, and expresses the PostgreSQL constraints of
the slice directly. Both are licensed under Apache-2.0 (`@dbml/core` and
`@dbml/cli` 11.0.0; `linkml` 1.12.1, with `linkml-runtime` under CC0-1.0), so
both pass the licence filter (DEC-14).

**Status.** The proposal is re-accepted (DEC-16).
[ADR-0024](../../docs/adr/0024-dbml-as-entity-model-language.md) records the
decision, and T-0006 in `docs/spec/todo.md` now names DBML.

## Pugh Matrix

Scale −2 to +2 against the Mermaid erDiagram baseline. The stakeholder
confirmed the weights on 2026-10-30. Atlas is excluded by the licence filter;
its story and note stay as evidence (DEC-14).

| Criterion                       | Weight | Mermaid (baseline) | DBML     | LinkML   |
| ------------------------------- | ------ | ------------------ | -------- | -------- |
| Validation depth                | 40     | 0                  | +2       | +2       |
| Legacy and dialect coverage     | 15     | 0                  | +2       | −1       |
| Named views                     | 14     | 0                  | +2       | +1       |
| Constructs                      | 14     | 0                  | +2       | +1       |
| Lint hook                       | 10     | 0                  | +2       | +2       |
| Comparison with the live schema | 7      | 0                  | +1       | +1       |
| **Weighted total**              |        | **0**              | **+193** | **+120** |

## Evidence per criterion

- **Validation depth.** `@dbml/core` caught 8 of 12 semantic errors.
  `linkml-lint` caught 5 of the 7 errors that can arise in LinkML. Mermaid
  catches syntax errors only. Source: [notes/validation.md](notes/validation.md).
- **Legacy and dialect coverage.** The DBML slice with Oracle types validates,
  `dbml2sql --oracle` writes DDL, and `sql2dbml --oracle` imports a legacy
  schema with its CHECK constraints, composite foreign key, and function-based
  index. LinkML's Oracle DDL loses the enum values, the time zone, and the JSON
  columns, and LinkML has no import tool. Source:
  [notes/validation.md](notes/validation.md).
- **Named views.** DBML names the view in the model with `DiagramView`, and a
  wrapper renders it with keys and enum values. LinkML renders a class subset,
  but the model cannot name the view. Source: [notes/views.md](notes/views.md).
- **Constructs.** DBML expresses nine of the twelve constructs directly, and a
  wrapper adds the Domain-owned rule. LinkML cannot express five. Sources:
  [notes/dbml.md](notes/dbml.md), [notes/linkml.md](notes/linkml.md).
- **Lint hook.** Both parsers expose the model to a script: `@dbml/core` as
  JSON, LinkML through `SchemaView`.
- **Comparison with the live schema.** Both scored 0.56 against the 16
  expected differences; Mermaid scored 0.19. Sources:
  [notes/dbml.md](notes/dbml.md), [notes/linkml.md](notes/linkml.md),
  [notes/mermaid.md](notes/mermaid.md).

The validation criterion carries the most weight, but it does not separate
DBML from LinkML; both score +2. The gap comes from legacy coverage, views,
and constructs. LinkML scores higher on no criterion, so no change of weights
puts it ahead.

## Risks of DBML

1. **The CLI exits 0 on a broken model.** `dbml2sql` caught none of the 12
   errors. Validation must run through `@dbml/core`, in a factory wrapper.
2. **The renderer lags behind the language.** It cannot read `checks` and
   ignores `DiagramView`. The PoC's wrappers strip `checks` and copy the view's
   tables into a separate file before rendering.
3. **CHECK expressions are free text.** Nothing checks the columns they name
   (case E10). A factory lint needs an SQL expression parser for this.
4. **A one-to-one reference with `-` reverses the foreign key.** `dbml2sql`
   puts the key on the right-hand table. The convention writes `>` together
   with a UNIQUE index.

## Conventions for adoption

- **No behaviour in `Note`.** Transitions, ordering rules, and conditions
  belong in `state-machines.md`, `validation-rules.md`, and the `.feature`
  files. The model file holds declarative structure only. A lint enforces it.
- **Enums match the state machines.** A lint candidate compares each DBML
  `Enum` with the states in `state-machines.md`. It is untested.
- **Missed errors become lint rules.** E04 (foreign key type) and E11 (two
  primary keys) can be read from the `@dbml/core` model. E07 needs a list of
  allowed types per database.

## Open items

- **Structured JSON payloads.** DBML sees a `jsonb` column as opaque. Gigacron
  validates the six `jsonb` sections on `task_version` against JSON Schema
  files. Whether those schemas belong next to the DBML model is not tested.
- **Oracle without a database.** No Oracle instance ran. The copied
  PostgreSQL CHECK expressions are likely invalid in Oracle before 23ai.
- **Findings for Gigacron.** The differences in
  [expected-differences.md](expected-differences.md) go to Gigacron as
  findings, not as PoC work.

This file is spike output. Nothing here is promoted into the specification,
the architecture, or the factory scripts until the ADR is accepted.
