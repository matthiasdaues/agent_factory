---
id: FAGAN-0055
source: fagan-review
severity: major
category: defect
artifact: orchestrator/src/orchestrator/cli.py:_handle_abort
status: resolved
traces: [BR-017]
---

# `abort` and `release` bypass the run lock — race condition

**What is wrong:** `_handle_abort()` and `_handle_release()` both mutate run state and call `run_lock.release()` without first acquiring the lock. If another orchestrator process holds the lock and is actively running, these commands delete the lock file from under it and write unlocked state. This violates BR-017 (single-run lock). By contrast, `approve`/`reject` use `_with_lock()`.

**Fix:** Route `abort` and `release` through `_with_lock()`, or at minimum check `run_lock.is_held()` and refuse if a different live process holds the lock. For `abort` specifically, consider whether terminating the holding process's PID is also required.
