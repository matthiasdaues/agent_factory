---
name: retrospective
description: Run a structured session retrospective across five categories. Produces a timestamped report in docs/reviews/.
category: utility
disable-model-invocation: false
---

# Retrospective

Run a structured retrospective at the end of a work session or phase. Mine the conversation history for concrete examples — do not invent or generalize. Every item must cite a specific event from the session.

## Step 1 — Gather evidence

Scan the session history for concrete items per category:

| Category            | Question to answer                                                                |
| ------------------- | --------------------------------------------------------------------------------- |
| **Went Well**       | What produced good results, saved time, or caught real problems?                  |
| **Caused Friction** | What slowed us down, required rework, or caused avoidable round trips?            |
| **Stop Doing**      | What practice or pattern proved counterproductive and should not be repeated?     |
| **Continue Doing**  | What practice or pattern worked and should become standard?                       |
| **Start Doing**     | What new practice emerged from this session that should be adopted going forward? |

Rules:

- Concrete example per item, not a general principle.
- Friction: state root cause and cost (time, rework, risk).
- Stop/Continue/Start: actionable — a future agent or user can follow it.
- Zero items in a category: say so. Do not pad.

When the session usage record is available, read its provider-qualified
`cache_miss_turns`, `cache_miss_input_tokens`, and
`late_early_input_ratio` values with `cli`, `provider`, and
`usage_capability`. Use non-null values only as concrete evidence in **Caused
Friction**, retaining the qualifier and distinguishing numeric zero from
unavailable data. These session-end signals support diagnosis; they are never
a live budget gate and must not be used to interrupt or control a run.

**Completion**: items collected for all five categories.

## Step 2 — Draft the report

Write the report using the format in [RETRO-FORMAT.md](RETRO-FORMAT.md). Save to:

```
docs/reviews/retro-YYYY-MM-DD.md
```

Use today's date. If a retro already exists for today, append a sequence number: `retro-YYYY-MM-DD-2.md`.

Format via `scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

**Completion**: report written, all five sections populated with evidence.

## Step 3 — Extract action items

From the Stop/Continue/Start sections, extract concrete action items. Present them to the user for confirmation. Confirmed items should be:

- Filed as todos in `docs/spec/todo.md` or the project's issue tracker
- Or captured as updates to agent definitions, skills, or `docs/CONTEXT.md`
- Or filed as a backlog story (`backlog/ST-NNNN.md`, this repo's INVEST/MoSCoW schema) and handed off to `implementation-agent` for dispatch

Do not file action items without user confirmation.

**Completion**: user confirms which action items to track. Report is final.
