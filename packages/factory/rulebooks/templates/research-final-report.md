---
title: Final Report Template
version: 1.0.0
---

# Final Report Template

Skeleton for a research run's final report. Validated against
[final-report.schema.json](../../schemas/research-final-report.schema.json).

## Frontmatter

```yaml
---
schema: factory/rulebooks/schemas/research-final-report.schema.json
---
```

## Body

### findings

Factual sections built only from surviving claims. Each entry:

- `title` — a one-line label for the finding.
- `summary` — the finding, stated as fact.
- `surviving_claim_refs` — the ID(s), from the claim register's
  `surviving_claims`, that this finding rests on. Required and non-empty:
  a finding with no surviving claim behind it does not belong here.

### refuted_conjectures

Conjectures a test or review falsified during the run.

### unresolved_alternatives

Alternative explanations neither confirmed nor ruled out.

### recommendations

Actions recommended on the strength of the surviving findings.

### evidence_gaps

Known gaps where evidence was insufficient to settle a claim.

### limitations

Constraints on scope, method, or time that bound what this report can claim.

## Referenced from

- [final-report.schema.json](../../schemas/research-final-report.schema.json)
