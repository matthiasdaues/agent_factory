---
title: Test Record Template
version: 1.0.0
---

# Test Record Template

Skeleton for a single test-record artifact — the outcome of one adversarial
test run against one conjecture (proposal Procedure Step 7). Governed by
[test-record.schema.json](../../schemas/research-test-record.schema.json).

## Fields

```json
{
  "claim_id": "<CLAIM-NNNN — id of the claim this test targets>",
  "claim_version": "<integer — version of the claim this test was run against>",
  "test_question": "<the specific, bounded question this test answers>",
  "refuting_result": "<the result that would refute the claim, stated before observing>",
  "method": "<how the test was carried out>",
  "evidence_examined": ["<one source or data point examined, one per entry>"],
  "observed_result": "<what was actually observed>",
  "limitations": "<known limitations of this test>",
  "outcome": "<SURVIVED | REFUTED | INCONCLUSIVE | INVALID_TEST>"
}
```

## Referenced from

- [test-record.schema.json](../../schemas/research-test-record.schema.json)
