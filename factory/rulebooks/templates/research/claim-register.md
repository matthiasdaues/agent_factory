---
title: Claim Register Template
version: 1.0.0
---

# Claim Register Template

Skeleton for a research run's claim register. Validated against
[claim-register.schema.json](../../schemas/research/claim-register.schema.json).

## Frontmatter

```yaml
---
schema: factory/rulebooks/schemas/research/claim-register.schema.json
---
```

## Body

Every claim examined during the run goes into exactly one of the four lists
below, by its final disposition.

### surviving_claims

Claims that withstood every test and review applied to them. Each entry:

- `claim_text` — the claim, stated as a single testable sentence.
- `scope` — the conditions under which the claim is asserted to hold.
- `assumptions` — the premises the claim depends on.
- `evidence` — the evidence gathered for or against the claim.
- `tests` — the tests run against the claim.
- `failed_tests` — the tests, of the above, that this claim failed to survive
  intact (kept as its own field so later report validation can prove it
  stays visible, not folded into `tests`).
- `reviews` — the reviews the claim went through.
- `vote_result` — the outcome of the reviewers' vote on the claim.
- `qualifications` — the caveats the claim survived only under (kept as its
  own field for the same visibility reason as `failed_tests`).
- `remaining_possible_refuters` — tests or reviews that could still falsify
  the claim but have not yet been run.
- `applicable_date` — the date (or date-time) up to which the claim is
  asserted to hold.

### refuted_claims

Claims a test or review falsified.

### unresolved_claims

Claims neither confirmed nor falsified by the run's tests and reviews.

### superseded_claims

Claims replaced by a later, more precise claim during the run.

## Referenced from

- [claim-register.schema.json](../../schemas/research/claim-register.schema.json)
