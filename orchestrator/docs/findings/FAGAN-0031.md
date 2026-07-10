---
id: FAGAN-0031
source: fagan-review
severity: major
category: defect
artifact: tests/
status: resolved
traces: [FR-K2, FR-K3, VR-023]
---

# No end-to-end test that model reaches adapter command

**What is wrong:** Tests verify `ModelResolver` in isolation and that stubs return the right values, but no test asserts that the resolved model actually appears in the final adapter subprocess command. The critical defect (FAGAN-0001) is therefore untested.

**Fix:** Add an integration test that captures the adapter's subprocess command and asserts explicit-model, matrix-resolved, and adapter-default scenarios.
