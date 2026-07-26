---
title: Survey Research Report Template
version: 1.0.0
---

# Survey Research Report Template

Skeleton for a cited survey-report JSON artifact. It reports what recorded
sources say; it is not a claim register or a falsification result. Validate it
with `factory/scripts/schema-validate` against
[research-survey-report.schema.json](../schemas/research-survey-report.schema.json).

## Fields

### findings

The per-question sourced synthesis. Each finding contains `title`, `summary`,
and non-empty `source_record_refs` naming the recorded sources it rests on.

### uncertainties

Uncertain, thin, or one-sided parts of the available source base.

### evidence_gaps

Questions or facts the gathered sources did not adequately cover.

### limitations

Scope, method, timing, or source-quality constraints on this survey.

### candidates_for_deeper_falsification_study

Questions that the survey surfaced but that need a separate falsification study
before a stronger conclusion is warranted.

## Instance shape

```json
{
  "findings": [
    {
      "title": "...",
      "summary": "...",
      "source_record_refs": ["source-records/...json"]
    }
  ],
  "uncertainties": ["..."],
  "evidence_gaps": ["..."],
  "limitations": ["..."],
  "candidates_for_deeper_falsification_study": ["..."]
}
```

## Referenced from

- [research-survey-report.schema.json](../schemas/research-survey-report.schema.json)
- [schema-validate script](../../scripts/schema-validate)
