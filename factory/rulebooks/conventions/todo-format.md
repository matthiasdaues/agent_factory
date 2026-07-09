---
title: Todo Filing
category: requirements
enforcement: none — human/agent-consumed; collected by clarify-requirements, referenced by write-prd and retrospective, filed from Question-category findings per report-format.md
version: 1.0.0
---

# Todo Filing

Shared rules for tracking deferred decisions and open questions. Unlike findings — one file per item, under `docs/findings/` — todos are entries appended to a single running file.

## When to file

File an item when a decision is deferred, a question can't be answered inline, or a confirmed action item isn't actioned immediately. Referenced by [clarify-requirements](../../skills/clarify-requirements/SKILL.md) (collects open items), [write-prd](../../skills/write-prd/SKILL.md) (PRD's Open Questions section), [retrospective](../../skills/retrospective/SKILL.md) (confirmed action items), and any review's Question-category findings ([report-format.md](report-format.md)).

## File location

Single file: `docs/spec/todo.md`. Create lazily — only when the first item is filed.

## Entry format

```markdown
## T-0001 — <short title>

- status: open
- source: <skill, session, or review that raised it> (optional)
- traces: <related ID(s) — story, finding, ADR> (optional)

<body: what is deferred, why, what resolving it requires>
```

- ID: `T-<NNNN>`, zero-padded, sequential. Allocate the next number by scanning existing entries.
- One entry per open item, appended — do not rewrite prior entries.

## Status lifecycle

- `open` — undecided or unactioned.
- `resolved` — decided or actioned; state the resolution in the body. Keep the entry — do not delete.

## Format

Run `scripts/mdformat --number docs/spec/todo.md` after every edit, per [markdown-formatting.md](markdown-formatting.md).
