---
title: "Comparison Note: Mermaid erDiagram (baseline)"
---

# Comparison Note: Mermaid erDiagram (baseline)

**Tool:** `minlag/mermaid-cli:latest`, which reports version 12.0.0.
**Gigacron:** `40954f18`. **Run on:** 2026-10-29.

## Result in short

The baseline catches syntax errors and nothing else. `mmdc` renders a
relationship to an undeclared entity without an error. The `erDiagram` syntax
cannot state nullability, composite references, or any constraint beyond
PK, FK, and UK markers, so Gigacron keeps those in prose tables today. A
hand-written parser makes the checks and a column-name comparison possible.
The comparison found 3 of the 16 expected differences.

## Definition of Done

**1. Slice expressed.** [acid-slice.mmd](../mermaid/acid-slice.mmd) copies the
nine entity blocks and the ten relationship lines between them unchanged from
the pinned model. The wrapper's `%% domain-owned:` line is the only addition.

| No. | Construct                    | In Mermaid `erDiagram`                                                                                          |
| --- | ---------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 1   | Composite primary key        | Workaround: `PK` on both attributes of `ATTEMPT`.                                                               |
| 2   | Composite foreign key        | Not expressed. `FK` marks a column, not its target.                                                             |
| 3   | JSON payload column          | Expressed as the type name `jsonb`, which is free text.                                                         |
| 4   | Enumerated string domain     | Not expressed. The type is `enum`, the values live in prose.                                                    |
| 5   | Self-referencing foreign key | Not expressed in the model: `AUDIT_EVENT` has no relationship line and no `FK` marker on `supersedes_event_id`. |
| 6   | Nullable foreign key         | Workaround: the cardinality `o` on a relationship. No column-level nullability.                                 |
| 7   | Multi-column UNIQUE          | Not expressed.                                                                                                  |
| 8   | Partial UNIQUE               | Not expressed.                                                                                                  |
| 9   | One-to-zero-or-one           | Expressed: `ATTEMPT \|\|--o\| OUTBOX`.                                                                          |
| 10  | CHECK across columns         | Not expressed.                                                                                                  |
| 11  | Exclusion constraint         | Not expressed.                                                                                                  |
| 12  | `domain_id` convention       | Through the wrapper and a `%% domain-owned:` comment line.                                                      |

**2. Valid slice.** `mmdc -i acid-slice.mmd -o runs/acid-slice.svg` exits 0.

**3. Broken models.** Plain `mmdc`, then the [wrapper](../mermaid/mermaid-check.sh)
(`mermaid-check.sh validate`):

| File                   | Error                                 | `mmdc` exit | Wrapper exit | Message                                                      |
| ---------------------- | ------------------------------------- | ----------- | ------------ | ------------------------------------------------------------ |
| `broken-syntax.mmd`    | `TASK {{`                             | 1           | 1            | `Parse error on line 16`                                     |
| `broken-reference.mmd` | relationship `AGENT \|\|--o{ ATTEMPT` | 0           | 1            | `relationship names undeclared entity AGENT`                 |
| `broken-domain.mmd`    | `PLAN` without `domain_id`            | 0           | 1            | `entity PLAN is domain-owned but has no attribute domain_id` |

The survey's question is answered: a relationship to an undeclared entity
renders without an error.

**4. SVG.** [acid-slice.svg](../out/mermaid/acid-slice.svg), exit 0.

**5. PNG.** [acid-slice.png](../out/mermaid/acid-slice.png), exit 0.

**6. Generation.** Mermaid generates nothing but diagrams.

**7. Named views.** No named-view construct.

**8. Comparison with the live schema.** `mermaid-check.sh compare acid-slice.mmd domain task task_version folder` reads each entity's attribute names with a
regular expression and compares them with `information_schema.columns`. Exit
0, output in [compare.out](../mermaid/runs/compare.out).

| Entry | Result    | Evidence                                                                  |
| ----- | --------- | ------------------------------------------------------------------------- |
| D04   | found     | `table task: column name in the live schema, not in the model`            |
| D09   | found     | `table task_version: column name in the model, not in the live schema`    |
| D10   | found     | `column runs_until_set_by_folder_id in the model, not in the live schema` |
| other | not found | Mermaid states no nullability, constraint, enum value, or schema          |

Unspecified: `table folder: not in the live schema`. False reports: none.

**Score: (3 − 0) / 16 = 0.19.**

**9. Dialects.** Mermaid is not tied to a database. Type names are free text.
No dialect-specific constraint can be stated.

**10. Commands.** Every command is above or in the wrapper.

## Wrapper cost

The wrapper is a hand-written regular-expression parser for `erDiagram`
blocks. It is the most fragile wrapper in the PoC: any syntax it does not
expect, such as attribute comments in quotes, breaks it. It can compare only
column names, because the language holds nothing more.

## Survey claims

- The survey expected that `mmdc` renders a relationship to an undeclared
  entity silently. Observed: exit 0, with no error message.
