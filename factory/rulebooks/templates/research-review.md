---
title: Review Template
version: 1.0.0
---

# Review Template

Skeleton for a single review artifact — one reviewer's adversarial check of a
claim against its test records (proposal Procedure Step 8). Governed by
[review.schema.json](../../schemas/research-review.schema.json).

## Fields

```json
{
  "claim_id": "<CLAIM-NNNNNN — id of the claim under review>",
  "checks": {
    "testable": "<true/false — the claim is stated so a test could refute it>",
    "alternatives_considered": "<true/false — competing conjectures were considered>",
    "tests_severe": "<true/false — the tests run were severe, not softballs>",
    "survived_unchanged": "<true/false — the claim survived without being reworded to fit>",
    "sources_support_wording": "<true/false — cited sources actually support the wording used>",
    "sources_independent": "<true/false — supporting sources are independent, not copies of one another>",
    "assumptions_explicit": "<true/false — the claim's assumptions are stated, not implicit>",
    "within_tested_scope": "<true/false — the claim is not asserted beyond what was tested>",
    "contrary_evidence_addressed": "<true/false — contrary evidence was addressed, not ignored>",
    "possible_overturning_evidence": "<true/false — the claim states what evidence could still overturn it>"
  },
  "defect_level": "<BLOCKER | MAJOR | MINOR | NOTE>"
}
```

## Referenced from

- [review.schema.json](../../schemas/research-review.schema.json)
