---
title: Vote Template
version: 1.0.0
---

# Vote Template

Skeleton for a single vote artifact — one eligible reviewer's disposition on a
claim, cast against one completed review of one exact claim hash (proposal
Procedure Step 9). Governed by
[vote.schema.json](../../schemas/research/vote.schema.json).

## Fields

```json
{
  "review_ref": "<REVIEW-NNNN — reference to the one completed review this vote is cast on>",
  "claim_hash": "<64-char hex content hash of the exact claim version voted on>",
  "reviewer": "<identity of the one eligible reviewer casting this vote>",
  "value": "<SURVIVE | REFUTE | UNRESOLVED | ABSTAIN>"
}
```

## Referenced from

- [vote.schema.json](../../schemas/research/vote.schema.json)
