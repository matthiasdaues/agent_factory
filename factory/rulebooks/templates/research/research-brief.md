---
title: Research Brief Template
version: 1.0.0
---

# Research Brief Template

Skeleton for a single research-brief artifact (JSON), the playbook input that
opens a research effort. Validated against
[research-brief.schema.json](../../schemas/research/research-brief.schema.json)
via `factory/scripts/schema-validate`.

## Fields

### research_question

The single question this research must answer.

### intended_use

What decision, artifact, or downstream action this research feeds.

### audience

Who consumes the completed research.

### scope

What is in bounds for this research.

### exclusions

What is explicitly out of bounds, as a list.

### freshness_requirements

How current the evidence must be (e.g. publication windows), as a list.

### source_requirements

What qualifies as an acceptable source, as a list.

### cost_of_error

What it costs if this research's conclusion turns out wrong.

### completion_criteria

The conditions that mark this research as complete, as a list.

## Instance shape

```json
{
  "research_question": "...",
  "intended_use": "...",
  "audience": "...",
  "scope": "...",
  "exclusions": ["..."],
  "freshness_requirements": ["..."],
  "source_requirements": ["..."],
  "cost_of_error": "...",
  "completion_criteria": ["..."]
}
```

## Referenced from

- [research-brief.schema.json](../../schemas/research/research-brief.schema.json)
- [schema-validate script](../../../scripts/schema-validate)
