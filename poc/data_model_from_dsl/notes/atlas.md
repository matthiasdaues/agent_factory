---
title: "Comparison Note: Atlas HCL"
---

# Comparison Note: Atlas HCL

**Excluded from the Pugh Matrix.** On 2026-10-29 the stakeholder set a licence
rule: only MIT, Apache-2.0, and similar fully permissive licences, and no
paywalled features. The build tested here is licensed under the Ariga End User
License Agreement and gates `schema lint` and extensions behind Atlas Pro or a
login. The Apache-2.0 community build was checked briefly but not recorded,
and the stakeholder dropped Atlas from the comparison. This note stays as
evidence.

**Tool:** `arigaio/atlas:latest`, which reports `atlas version v1.3.7-1696d6d-canary`. **Gigacron:** `40954f18`. **Run on:** 2026-10-29.

## Result in short

Atlas meets all four hard requirements, two of them only with a wrapper. It
expresses all twelve constructs. Without an Atlas login it cannot declare the
extension `btree_gist` or run `schema lint`. The wrapper fills both gaps. Its
comparison found 15 of the 16 expected differences and reported none falsely.
The image is licensed under the Ariga End User License Agreement.

## Definition of Done

**1. Slice expressed.** [acid-slice.pg.hcl](../atlas/acid-slice.pg.hcl)
expresses all twelve constructs. Enumerated columns use PostgreSQL enum types.
Two substitutions:

- The extension `btree_gist` is not in the model. Atlas answered
  `Error: extensions are available to logged-in users only. Use 'atlas login' to access this feature`. The dev database gets the extension before
  validation instead.
- Construct 12 needs a marker for Domain-owned tables. Each of them carries
  `comment = "domain-owned"`.

**2. Valid slice.** Exit 0.

```bash
docker run --rm --network dsl-poc -v "$PWD":/w -w /w arigaio/atlas:latest \
  schema inspect --url file://acid-slice.pg.hcl \
  --dev-url "postgres://postgres:poc@dsl-poc-pg:5432/atlas_dev?sslmode=disable&search_path=public" \
  --format '{{ sql . }}'
```

The output ([atlas-valid.out](../atlas/runs/atlas-valid.out)) keeps the
exclusion constraint, all four partial UNIQUE indexes, and `ck_outbox_attempt`.

**3. Broken models.** Plain Atlas, then the
[wrapper](../atlas/atlas-validate.sh):

| File                      | Error                        | Atlas exit | Wrapper exit | Message                                                  |
| ------------------------- | ---------------------------- | ---------- | ------------ | -------------------------------------------------------- |
| `broken-syntax.pg.hcl`    | unclosed `table` block       | 1          | 1            | `Unclosed configuration block`                           |
| `broken-reference.pg.hcl` | foreign key to `table.agent` | 1          | 1            | `This object does not have an attribute named "agent"`   |
| `broken-domain.pg.hcl`    | `plan` without `domain_id`   | 0          | 1            | `table plan is domain-owned but has no column domain_id` |

`atlas schema lint` could carry the domain rule, but it answered `Abort: command 'atlas schema lint' is available only to Atlas Pro users`. The wrapper reads
`schema inspect --format '{{ json . }}'` and checks every table whose comment
is `domain-owned` with Python in a container.

**4. SVG.** `schema inspect --format '{{ mermaid . }}'` writes
[acid-slice.mmd](../out/atlas/acid-slice.mmd), and
`minlag/mermaid-cli` 12.0.0 renders [acid-slice.svg](../out/atlas/acid-slice.svg).
Both exit 0. The diagram shows all nine tables, their columns, keys, and every
foreign key, including the self-reference on `audit_event`. It shows no
UNIQUE, CHECK, or exclusion constraints.

**5. PNG.** The same `mmdc` call writes
[acid-slice.png](../out/atlas/acid-slice.png).

**6. Generation.** Atlas generates SQL DDL. The DDL keeps constructs 1 to 11.
Construct 12 is a rule, not DDL. Atlas has no first-party generator for
application types such as Pydantic or SQLAlchemy.

**7. Named views.** Atlas HCL has no named-view construct. Nothing to run.

**8. Comparison with the live schema.** The first run stopped with exit 1:
`Error: mismatched HCL and database schemas: "application" <> "public"`
([atlas-diff-public.out](../atlas/runs/atlas-diff-public.out)). That is D01.
The wrapper step renames the schema in a copy of the model to `application`
([acid-slice.application.pg.hcl](../atlas/runs/acid-slice.application.pg.hcl))
and uses a dev database `atlas_dev_app` with the schema `application` and
`btree_gist`. Then:

```bash
docker run --rm --network dsl-poc -v "$PWD":/w -w /w arigaio/atlas:latest \
  schema diff \
  --from "postgres://postgres:poc@dsl-poc-pg:5432/gigacron?sslmode=disable&search_path=application" \
  --to file://acid-slice.application.pg.hcl \
  --dev-url "postgres://postgres:poc@dsl-poc-pg:5432/atlas_dev_app?sslmode=disable&search_path=application" \
  --exclude plan --exclude task_instance --exclude attempt --exclude outbox \
  --exclude audit_event --exclude task_draft
```

Exit 0, output in [atlas-diff-with-folder.out](../atlas/runs/atlas-diff-with-folder.out).
A first run that also excluded `folder` lost D13 and D14, because Atlas drops
foreign keys to excluded tables ([atlas-diff.out](../atlas/runs/atlas-diff.out)).

| Entry | Result    | Evidence in the diff                                                       |
| ----- | --------- | -------------------------------------------------------------------------- |
| D01   | found     | `mismatched HCL and database schemas: "application" <> "public"`           |
| D02   | found     | `domain` … `ALTER COLUMN "state_changed_at" SET NOT NULL`                  |
| D03   | found     | `domain` … `ALTER COLUMN "state" TYPE "domain_state"`                      |
| D04   | found     | `task` … `DROP COLUMN "name"`                                              |
| D05   | not found | no line names `uq_task_domain_name`; it falls with the column              |
| D06   | found     | `DROP CONSTRAINT "task_domain_id_fkey"`, `ADD CONSTRAINT "task_domain_fk"` |
| D07   | found     | `task` … `ALTER COLUMN "state_changed_at" SET NOT NULL`                    |
| D08   | found     | `task` … `ALTER COLUMN "state" TYPE "task_state"`                          |
| D09   | found     | `ADD COLUMN "name" character varying NOT NULL`                             |
| D10   | found     | `ADD COLUMN "runs_until_set_by_folder_id" bigint NULL`                     |
| D11   | found     | `ALTER COLUMN "folder_id" SET NOT NULL`                                    |
| D12   | found     | `ALTER COLUMN "created_by" SET NOT NULL`                                   |
| D13   | found     | `ADD CONSTRAINT "task_version_folder_fk"`                                  |
| D14   | found     | `ADD CONSTRAINT "task_version_set_by_folder_fk"`                           |
| D15   | found     | `ADD CONSTRAINT "ex_task_version_range" EXCLUDE USING GIST`                |
| D16   | found     | `ADD CONSTRAINT "ck_task_version_range" CHECK`                             |

Unspecified reports: `DROP IDENTITY` on three key columns, `COMMENT ON TABLE`
for the `domain-owned` marker, and the `CREATE TYPE` and `CREATE TABLE`
statements for `folder` and its enums. False reports: none.

**Score: (15 − 0) / 16 = 0.94.**

**9. Dialects (unchecked).** This run checked PostgreSQL only. Atlas's
documentation was not read in this run. The list of other dialects stays open
until someone reads it.

**10. Commands.** Every command is above or in
[atlas-validate.sh](../atlas/atlas-validate.sh) and
[build-live-schema.sh](../live-schema/build-live-schema.sh).

## Wrapper cost

The wrapper does three jobs that the free Atlas build does not:

- It asserts construct 12, which `schema lint` would do with Atlas Pro.
- It prepares dev databases with `btree_gist`, which an HCL `extension` block
  would do after `atlas login`.
- It renames the model's schema for the comparison. A model that names its
  schema `application` would make this step unnecessary, at the cost of a
  slice that names a schema the model does not specify.

## Licence

`docker run --rm arigaio/atlas:latest license` prints: "This distribution of
Atlas is licensed under the Ariga End User License Agreement". The image labels
name no licence. This run did not check whether an open-source community build
exists under another tag. The survey left the tag-to-licence question open,
and this run settles it for `latest`.

## Survey claims

- The survey's open question was whether Atlas validates HCL without a live
  database. Observed: validation needs a dev database. A PostgreSQL container
  serves, so the requirement "no local install" holds.
- The survey recorded that Atlas's schema-rule engine is paid. Observed:
  `schema lint` aborts with "available only to Atlas Pro users".
- The survey recorded that Atlas's ERD visualization is cloud-only. Observed:
  that holds for Atlas's own viewer, but `--format '{{ mermaid . }}'` works
  without login, and `mmdc` renders the result to SVG in a container.
