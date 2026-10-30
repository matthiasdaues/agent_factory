---
id: 0024
status: accepted
evaluation: pugh-matrix
---

# DBML as the entity-model language

## Context

A project's entity model lives today in `entity-model.md`, as Mermaid
`erDiagram` blocks and prose tables. Mermaid catches syntax errors only. It
renders a relationship to an undeclared entity without an error, and it cannot
state nullability, composite references, or constraints beyond PK, FK, and UK.
Nothing checks the prose tables, so the model drifts from the code unnoticed.

`architecture.dsl` shows the shape the entity model needs: one plain-text file,
a validator with exit codes, named views rendered to SVG, and a lint hook for
drift. In September 2026 the factory picked LinkML in T-0006 without testing
it. The [data-model DSL PoC](../../poc/data_model_from_dsl/proposal-data-model-dsl-technical-poc.md)
tested DBML, LinkML, Atlas HCL, and Mermaid on nine entities from Gigacron,
plus twelve semantic errors and a legacy Oracle schema.

Two constraints narrowed the field. Only MIT, Apache-2.0, or similarly
permissive licences qualify, with no paywalled features; this excluded Atlas,
whose image is under the Ariga End User License Agreement. Behaviour already
lives in `state-machines.md`, `validation-rules.md`, and the `.feature` files,
so the model file needs declarative structure only.

## Decision

DBML is the factory standard for a project's entity model. The canonical
source is `docs/spec/entity-model.dbml`. Validation runs through the
`@dbml/core` parser in a container, not through `dbml2sql`. Rendered SVG and
any Markdown view are derived from the DBML file.

Scale −2 to +2 against the Mermaid baseline; weights confirmed by the
stakeholder on 2026-10-30. Evidence per cell:
[recommendation.md](../../poc/data_model_from_dsl/recommendation.md).

| Criterion                       | Weight | Mermaid (baseline) | DBML     | LinkML   |
| ------------------------------- | ------ | ------------------ | -------- | -------- |
| Validation depth                | 40     | 0                  | +2       | +2       |
| Legacy and dialect coverage     | 15     | 0                  | +2       | −1       |
| Named views                     | 14     | 0                  | +2       | +1       |
| Constructs                      | 14     | 0                  | +2       | +1       |
| Lint hook                       | 10     | 0                  | +2       | +2       |
| Comparison with the live schema | 7      | 0                  | +1       | +1       |
| **Weighted total**              |        | **0**              | **+193** | **+120** |

Validation does not separate DBML from LinkML. DBML wins on legacy coverage:
it holds Oracle types and imports Oracle DDL with `sql2dbml`, while LinkML's
Oracle DDL loses enum values, time zones, and JSON columns. DBML also names
views inside the model and expresses more of the PostgreSQL constraints.
LinkML scores higher on no criterion.

LinkML's classes, inheritance, and `rules` belong to the object and behaviour
layer, which the factory keeps in other artifacts. They are not a reason to
prefer it here.

## Consequences

- The factory must ship a validation wrapper. `dbml2sql` exits 0 on every
  broken model; `@dbml/core` caught 8 of 12 semantic errors.
- The DBML renderer ignores `checks` and `DiagramView`. Rendering needs a
  wrapper until the renderer catches up.
- CHECK expressions are free text. A lint that checks the columns they name
  needs an SQL expression parser.
- A one-to-one reference written with `-` puts the foreign key on the wrong
  table. The convention writes `>` with a UNIQUE index.
- `Note` blocks hold no behaviour. Transitions and rules stay in the
  specification artifacts.
- Structured JSON payloads stay opaque `jsonb` columns in DBML. How their
  schemas are kept is open; the PoC did not test it.
- T-0006's LinkML choice is replaced. No migration had started.
