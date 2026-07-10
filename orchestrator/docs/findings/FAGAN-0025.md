---
id: FAGAN-0025
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/cli.py#main
status: resolved
traces: [UC-03, VR-017]
---

# run-all reuses existing run instead of requiring resume

**What is wrong:** `_load_or_create_chain_run()` loads an existing `run.json` if present and reuses it for `run-all`. A paused or halted run can be silently re-entered by `run-all` instead of requiring the explicit `resume`/`approve` flow. This undermines the approval boundary.

**Fix:** If an active run exists with mode != `complete`, reject `run-all` and direct the operator to `resume` or `approve`.
