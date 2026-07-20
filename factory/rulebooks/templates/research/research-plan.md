---
title: Research Plan Template
version: 1.0.0
---

# Research Plan Template

Skeleton for a single research-plan artifact (JSON), produced from a research
brief. Validated against
[research-plan.schema.json](../../schemas/research/research-plan.schema.json)
via `factory/scripts/schema-validate`.

## Fields

### research_questions

The bounded questions this plan sets out to answer, as a list.

### competing_conjectures

The rival candidate answers under consideration, as a list.

### evidence_requirements

What evidence each conjecture needs to be evaluated, as a list.

### refutation_strategies

The approaches for trying to disprove each conjecture, as a list.

### assignments

The bounded assignments this plan hands out, as a list.

### review_requirements

What a review of this plan's output must check, as a list.

### stop_conditions

The conditions under which this research effort stops, as a list.

## Instance shape

```json
{
  "research_questions": ["..."],
  "competing_conjectures": ["..."],
  "evidence_requirements": ["..."],
  "refutation_strategies": ["..."],
  "assignments": ["..."],
  "review_requirements": ["..."],
  "stop_conditions": ["..."]
}
```

## Referenced from

- [research-plan.schema.json](../../schemas/research/research-plan.schema.json)
- [schema-validate script](../../../scripts/schema-validate)
