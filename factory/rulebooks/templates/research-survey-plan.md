---
title: Survey Research Plan Template
version: 1.0.0
---

# Survey Research Plan Template

Skeleton for a source-grounded survey-plan JSON artifact. Validate it with
`factory/scripts/schema-validate` against
[research-survey-plan.schema.json](../schemas/research-survey-plan.schema.json).

## Fields

### research_questions

The bounded questions this survey will answer.

### search_angles

The perspectives or query approaches used to look for sources.

### source_targets

The source types, publishers, or repositories to seek.

### assignments

The bounded source-search assignments. Each assignment should declare its unique
output path before dispatch.

### stop_conditions

The conditions under which the survey stops gathering sources.

## Instance shape

```json
{
  "research_questions": ["..."],
  "search_angles": ["..."],
  "source_targets": ["..."],
  "assignments": ["..."],
  "stop_conditions": ["..."]
}
```

## Referenced from

- [research-survey-plan.schema.json](../schemas/research-survey-plan.schema.json)
- [schema-validate script](../../scripts/schema-validate)
