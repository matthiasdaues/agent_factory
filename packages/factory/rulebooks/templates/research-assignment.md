---
title: Research Assignment Template
version: 1.0.0
---

# Research Assignment Template

Skeleton for a single research-assignment artifact (JSON), one bounded piece
of work handed out from a research plan. Validated against
[research-assignment.schema.json](../../schemas/research-assignment.schema.json)
via `factory/scripts/schema-validate`.

## Fields

### bounded_question

The single, narrow question this assignment must answer.

### assignment_type

The stance this assignment takes: `direct-evidence`, `contrary-evidence`, or
`alternative-explanation`.

## Instance shape

```json
{
  "bounded_question": "...",
  "assignment_type": "direct-evidence"
}
```

## Referenced from

- [research-assignment.schema.json](../../schemas/research-assignment.schema.json)
- [schema-validate script](../../../scripts/schema-validate)
