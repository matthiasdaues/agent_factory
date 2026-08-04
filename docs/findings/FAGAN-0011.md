---
id: FAGAN-0011
source: fagan-review
severity: major
category: defect
artifact: factory/config/extensions/dispatch-wave.ts:442
status: open
traces: [ST-0067, UC-10, FR-K4, BR-040]
---

# Blocked waves emit an invalid child-result envelope

**What is wrong:** `aggregateEnvelope` returns an empty `artifact_paths` list
when every wave item fails before producing a valid child envelope. The same
change defines and enforces the canonical envelope contract as requiring a
non-empty artifact list, and its regression test explicitly expects the
invalid empty list. A parent therefore cannot validate or follow the result
contract on the error path, so the bounded envelope is not closed under a
realistic child failure.

**Fix:** Persist a canonical tracked wave report for blocked/error outcomes and
include that report path in the aggregate envelope. Update the negative-path
test to parse and validate the returned aggregate with the same canonical
envelope and artifact checks used for successful child results.
