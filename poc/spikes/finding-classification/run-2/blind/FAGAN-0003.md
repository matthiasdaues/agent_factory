---
id: FAGAN-0003
source: fagan-review
artifact: packages/server/backend/src/gigacron_server/task_registry/repositories.py:106
traces: [DEF-12, ST-0003C, ST-0003E]
owner: ST-0003E
---

# A Draft whose logical_task_id names no Task disappears from GET /api/v1/tasks

**What is wrong:** The combined list drops any Task Draft that carries a
`logical_task_id` which matches no Task in the same Domain. Such a Draft
reaches neither arm of the union.

- `_published_task_rows` starts from `TASK` and joins `TASK_DRAFT` on
  `logical_task_id == task_id AND domain_id == domain_id`. No Task means no
  row.
- `_unpublished_draft_rows` selects only `WHERE logical_task_id IS NULL`, so a
  non-null value excludes the Draft here too.

The state is reachable through the public API today. `TaskDraftCreate` and
`TaskDraftUpdate` both accept `logical_task_id` (`dtos.py:123` and
`dtos.py:140`), `TASK_DRAFT.logical_task_id` carries no foreign key
(`models.py:82`), and no service or validator checks the value.
`POST /api/v1/task-drafts` with `{"domain_id": 1, "logical_task_id": 999999}`
creates a Draft that `GET /api/v1/tasks` never returns.

The consequence is a silent loss of work. `GET /api/v1/tasks` is now the only
list the Domain workspace offers, because ST-0003C retired `TaskDraftsView`.
An administrator whose Draft falls into this state cannot see it, cannot reach
its editor, and receives no error.

**Fix:** Deferred to ST-0003E, which owns the constraint. `ST-0003E-details.md`
line 35 turns `TASK_DRAFT.logical_task_id` into `task_id`, a foreign key to
`TASK`, and line 39 adds a partial unique index over it. Once that foreign key
exists, every non-null value names a real Task, the first arm reports it, and
the second arm's `IS NULL` filter becomes correct. The same migration closes
the duplicate-row half of
`ARCH-FOLLOWUP[successor-draft-uniqueness]`.

Why this does not block ST-0003C:

- ST-0003C adds a read endpoint. The cause is a missing write-side constraint
  on a column ST-0003C does not write.
- Nothing in the product sets `logical_task_id`. The column appears nowhere in
  frontend source outside the generated schema and test fixtures. Reaching the
  state needs a hand-written API call carrying an invalid Task ID.
- `backlog/ST-0003C.md` already places the case outside this story: "Until the
  successor-draft story exists, a row with status `DRAFT` and a version `v3`
  cannot occur."
- No data is lost. The Draft is stored and readable by its own ID.

When ST-0003E lands, check this finding: confirm the foreign key is in the
migration, then add a `db` route test asserting that a Draft naming a Task
appears once, and set this finding to `resolved`.

If ST-0003E is deferred or dropped, this finding returns to major, because
`GET /api/v1/tasks` is the only list the Domain workspace offers. In that case
widen the second arm to `NOT EXISTS` against a matching `TASK` in the same
Domain, which matches the story's wording "one row per Draft that revises no
Task".

`repositories.py` carries this reasoning in the
`ARCH-FOLLOWUP[successor-draft-uniqueness]` docstring, so a reader of the query
finds it without this file.
