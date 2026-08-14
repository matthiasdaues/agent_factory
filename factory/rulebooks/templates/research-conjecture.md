---
title: Conjecture Template
version: 1.0.0
---

# Conjecture Template

Skeleton for a single conjecture JSON artifact — the claim-forming unit of the
falsification-driven research playbook (Procedure Step 5). Validated by
`factory/scripts/schema-validate` against
[conjecture.schema.json](../../schemas/research-conjecture.schema.json).

## Fields

```json
{
  "claim": "",
  "scope": "",
  "assumptions": [],
  "supporting_evidence": [],
  "contrary_evidence": [],
  "possible_refuting_evidence": "",
  "planned_tests": [],
  "qualifications": [],
  "content_hash": ""
}
```

### claim

Exactly one claim, stated as a single sentence — not a list of claims.

### scope

The boundary within which the claim is asserted to hold.

### assumptions

Background assumptions the claim depends on.

### supporting_evidence

Source-record references or excerpts that support the claim.

### contrary_evidence

Source-record references or excerpts that weigh against the claim.

### possible_refuting_evidence

What observation, if made, would refute this claim. Mandatory: a claim that
cannot state what would count against it is structurally incomplete and
cannot enter review.

### planned_tests

Concrete checks planned to look for the refuting evidence described above.

### qualifications

Caveats on the claim's strength or confidence.

### content_hash

Hex digest (e.g. SHA-256) of the conjecture's content, for change detection.

## Referenced from

- [conjecture.schema.json](../../schemas/research-conjecture.schema.json)
