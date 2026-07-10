---
id: FAGAN-0020
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/backlog_store.py#update_status
status: resolved
traces: [ADR-0008]
---

# update_status() is not atomic

**What is wrong:** `update_status()` reads the story file, modifies it in memory, and writes it back in place. A crash or interruption mid-write can leave a partial or empty file, losing the story. Other adapters (run_state_store, findings_store) use atomic temp-file + `os.replace()`.

**Fix:** Write to a temp file in `backlog_dir` and `os.replace()` atomically, following the pattern in `run_state_store.py`.
