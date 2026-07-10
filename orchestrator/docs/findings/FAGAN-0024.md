---
id: FAGAN-0024
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/cli.py#_build_runtime
status: resolved
traces: [UC-05, VR-008]
---

# All commands build full runtime unnecessarily

**What is wrong:** `main()` constructs the full `_Runtime` — including model matrix, adapter, phase runner, and agent registry — before dispatching any command. Read-only commands like `status` and side-effect-free commands like `approve`/`reject` are coupled to unrelated dependencies. If `model-matrix.conf` is missing, `status` fails.

**Fix:** Dispatch first, then construct only the dependencies each command needs. Extract a minimal `_StatusRuntime` and `_ApprovalRuntime`.
