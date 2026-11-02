---
title: Expected Differences
---

# Expected Differences

This file lists every difference between the [acid slice](acid-slice.md) and
the live schema that Gigacron's code builds. It was written before any
candidate ran. Definition-of-Done item 8 of the
[PoC proposal](proposal-data-model-dsl-technical-poc.md) scores each
candidate's comparison against this list.

**Pinned input:** Gigacron commit `40954f18fe72b237ecc865905a31cf0b9b146556`.
The code maps four tables. Three of them are in the slice: `domain`, `task`, and
`task_version`. `task_draft` is not in the slice.

## How the live schema is built

[build-live-schema.sh](live-schema/build-live-schema.sh) runs once and is
shared by every candidate. It does not count in any score.

```bash
git -C <gigacron-repo> archive 40954f18fe72b237ecc865905a31cf0b9b146556 \
  docs/spec/entity-model.md packages uv.lock pyproject.toml \
  | tar -x -C <export-dir>
live-schema/build-live-schema.sh <export-dir> live-schema
```

The script starts `postgres:16` as `dsl-poc-pg` on the Docker network
`dsl-poc`. A `ghcr.io/astral-sh/uv:python3.12-bookworm` container installs
`gigacron-server` from `uv.lock` with a managed Python 3.13. It creates the
schemas `application` and `audit` and calls `Base.metadata.create_all`. Gigacron
has no migrations at this commit. The script dumps the result to
[live-schema.sql](live-schema/live-schema.sql).

Two setup facts, observed while building:

- `uv sync` failed until the container used Python 3.13, because `uv.lock`
  requires `==3.13.*`.
- `uv sync` failed until `UV_DYNAMIC_VERSIONING_BYPASS=0.0.0` was set, because
  the workspace packages read their version from git and the export has no
  `.git`.

## The list

| ID  | Table          | Difference                                                                                                              |
| --- | -------------- | ----------------------------------------------------------------------------------------------------------------------- |
| D01 | all three      | The code puts the tables in the PostgreSQL schema `application`. The slice names no schema.                             |
| D02 | `domain`       | `state_changed_at` is nullable in the code and NOT NULL in the slice.                                                   |
| D03 | `domain`       | `state` is `varchar(16)` with no CHECK in the code. The slice restricts it to `DRAFT`, `ACTIVE`, `INACTIVE`, `RETIRED`. |
| D04 | `task`         | The code has a column `name`. The slice has none.                                                                       |
| D05 | `task`         | The code has `uq_task_domain_name UNIQUE (domain_id, name)`. The slice has none.                                        |
| D06 | `task`         | The foreign key to `domain` is named `task_domain_id_fkey` in the code and `task_domain_fk` in the slice.               |
| D07 | `task`         | `state_changed_at` is nullable in the code and NOT NULL in the slice.                                                   |
| D08 | `task`         | `state` is `varchar(16)` with no CHECK in the code. The slice restricts it to `ACTIVE`, `INACTIVE`, `RETIRED`.          |
| D09 | `task_version` | The slice has a column `name`. The code has none.                                                                       |
| D10 | `task_version` | The slice has a column `runs_until_set_by_folder_id`. The code has none.                                                |
| D11 | `task_version` | `folder_id` is nullable in the code and NOT NULL in the slice.                                                          |
| D12 | `task_version` | `created_by` is nullable in the code and NOT NULL in the slice.                                                         |
| D13 | `task_version` | The slice has `task_version_folder_fk`. The code has none.                                                              |
| D14 | `task_version` | The slice has `task_version_set_by_folder_fk`. The code has none.                                                       |
| D15 | `task_version` | The slice has `ex_task_version_range`. The code has none.                                                               |
| D16 | `task_version` | The slice has `ck_task_version_range`. The code has none.                                                               |

These match on both sides and are not differences: the primary keys,
`uq_domain_name`, `uq_task_domain`, `uq_task_version_number`,
`uq_task_version_current` with its predicate, `task_version_task_fk`, the
`jsonb` columns, and every other column's nullability.

## Matching rules

A comparison report is matched to the list by these rules:

- A reported difference that names the same table and the same column or
  constraint as a list entry counts as **found** for that entry. One entry is
  found at most once.
- A difference that comes only from something the slice does not specify is
  **unspecified** and counts neither way. The slice does not specify identity
  generation, column order, string length, defaults, index names, or tables
  outside `domain`, `task`, and `task_version`.
- Every other reported difference is **false**.
- When a candidate's model cannot express a construct, the comparison note
  records it under Definition-of-Done item 1. A difference that follows from
  that gap counts as **unspecified**.

Score for item 8: (found − false) / 16.
