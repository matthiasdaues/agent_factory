---
id: FAGAN-0003
source: fagan-review
reachable: no — the dangling-draft half is fixed in ST-0003C; the duplicate-row half is now refused by the schema
artifact: packages/server/backend/src/gigacron_server/task_registry/models.py:82
traces: [DEF-12, ST-0003C, ST-0003E]
owner: ST-0003E
---

# Drafts linked through the unconstrained logical_task_id

**Resolved in ST-0003E.** The column is now `TASK_DRAFT.task_id`, carrying a
composite foreign key `task_draft_task_fk` on `(domain_id, task_id)` against
`task (domain_id, task_id)` and a partial unique index `uq_task_draft_per_task`
on `task_id WHERE task_id IS NOT NULL`. Migration `GC_007` applies both. The
two halves below record what was wrong and how each was closed.

`TASK_DRAFT.logical_task_id` carried neither a foreign key nor a unique index.
Two consequences followed, with different reachability and different owners.

## Half A — the vanishing Draft (**resolved in ST-0003C**)

**What was wrong:** `GET /api/v1/tasks` dropped any Draft whose
`logical_task_id` matched no Task in the same Domain. `_published_task_rows`
starts from `TASK`, so no Task meant no row; `_unpublished_draft_rows` filtered
on `logical_task_id IS NULL`, so a non-null value excluded the Draft there too.
It reached neither arm of the union and was missing from `items` and `total`.

**Why it mattered more than first assessed.** The original deferral rested on
"no write path accepts the column". That is true of the HTTP surface, but
incomplete:

- `packages/server/scripts/seed_demo_data.py:144` writes `logical_task_id: 1`
  straight through the ORM and seeds no Task, so any freshly seeded demo
  database demonstrated the defect.
- `GET /api/v1/task-drafts` never filtered on the column, so the Task Draft
  list that ST-0003C retired *did* show these Drafts. ST-0003C turned a visible
  Draft into an invisible one — a regression the story itself introduced, not
  an inherited gap.
- ST-0003E's planned fix would not have closed it. A single-column foreign key
  to `TASK.task_id` constrains the Task's existence, not its Domain, while
  every query here matches on both. A Draft naming a real Task in another
  Domain would have stayed invisible after that migration shipped.

**Fix, in ST-0003C:** `_unpublished_draft_rows` now selects the Drafts that no
Task row stands for, rather than the Drafts with a null link:

```python
.where(TaskDraft.logical_task_id.is_(None) | ~revised_task_exists)
```

where `revised_task_exists` is a correlated `EXISTS` mirroring the join in
`_published_task_rows`. The two arms are exhaustive by construction, whatever
constraints the column carries, so this no longer depends on ST-0003E.

Covered at the time by two `db` tests in `tests/task_registry/test_routes.py`:

| Test                                                                       | Asserts                                                                                                    |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `test_DEF_12_list_tasks_still_reports_a_draft_whose_task_is_gone`          | A link to a non-existent Task still reports the Draft                                                      |
| `test_DEF_12_list_tasks_still_reports_a_draft_naming_another_domains_task` | A cross-Domain link reports the Draft in its own Domain, and does not attach it to the other Domain's Task |

Both were confirmed to fail (`total == 0`) against the previous predicate and
to pass against the new one.

**ST-0003E retired both tests.** Each had to build its state through raw SQL,
and `task_draft_task_fk` now refuses that state at the database. A test cannot
construct a dangling or cross-Domain link any more, so neither test could still
run. The refusal itself is asserted in their place by
`test_a_draft_cannot_name_a_task_that_does_not_exist` and
`test_a_draft_cannot_name_another_domains_task` in
`tests/task_registry/test_repositories.py`, and `test_routes.py` carries a
comment at the removal site explaining why. The union predicate is unchanged
and still exhaustive by construction; it is simply no longer the only thing
standing between a dangling link and a vanishing row.

## Half B — the duplicate rows (**resolved in ST-0003E**)

Without a unique index, two Drafts could name one Task. The outer join would then
emit that Task once per Draft, so:

- the "one row per Task" guarantee in `ST-0003C.md` would not hold;
- `total` would be inflated — note that `count_rows` counts the same union, so
  `items` and `total` stay consistent with each other and paging does not
  break; the number is wrong against the contract, not internally inconsistent;
- the frontend row key `task-${task_id}` (`TasksView.vue`) would collide,
  taking `data-key` and the `data-testid`s with it.

**No writer produces this state.** The API refuses it on both paths, which
`test_DEF_07_the_api_does_not_let_a_caller_link_a_draft_to_a_task`
(`tests/task_registry/test_publication_routes.py:510`) enforces: `POST` with
the column stores `None`, `PATCH` with it returns `422`. The seed script sets
the column on a single Draft, so it reached Half A but not Half B.

Deliberately **not** defended with `DISTINCT ON` or a window function: the
state is unreachable, and that complexity would outlive the one migration that
makes it impossible.

### Acceptance criterion — met

The criterion was: a `db` test that links two Drafts to one Task and asserts the
partial unique index **rejects the second write** — the error, not a row count.
`test_a_task_cannot_be_continued_by_two_drafts`
(`tests/task_registry/test_repositories.py:310`) raises on the second flush and
asserts `uq_task_draft_per_task` in the message.
`test_two_drafts_without_a_task_are_allowed` holds the other side: a null
`task_id` never collides, so Drafts for brand-new Tasks stay unlimited.

The foreign key was also required to be composite, `(domain_id, task_id)`
against `TASK (domain_id, task_id)`, which `uq_task_domain` already backs.
`GC_007` creates it that way, and both halves are asserted —
`test_a_draft_cannot_name_another_domains_task` and
`test_a_draft_cannot_name_a_task_that_does_not_exist`.

Beyond the criterion, `tests/task_registry/test_successor_concurrency.py` drives
two concurrent sessions at one Task: the second `INSERT` blocks on the index
until the first commits and then surfaces as `TASK_DRAFT_EXISTS` (409), leaving
exactly one Draft. The service's own look-up cannot see an uncommitted Draft in
another transaction, so the index — not the look-up — is the arbiter.

`repositories.py` carries this reasoning in the docstrings of
`_published_task_rows` and `_unpublished_draft_rows`, so a reader of the query
finds it without this file.
