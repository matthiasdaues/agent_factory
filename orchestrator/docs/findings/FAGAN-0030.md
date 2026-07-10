---
id: FAGAN-0030
source: fagan-review
severity: major
category: defect
artifact: tests/test_backlog_lint.py
status: resolved
traces: [VR-022]
---

# backlog-lint missing traces/traceability tests

**What is wrong:** `backlog-lint` tests cover required fields, enums, deps, cycles, and duplicates, but not missing/invalid `traces` or story→use-case traceability failures. VR-022 requires `backlog-lint` to enforce traceability.

**Fix:** Add negative tests for absent `traces`, malformed `traces` values, and unresolved traceability links.
