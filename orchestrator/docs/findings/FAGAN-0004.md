---
id: FAGAN-0004
source: fagan-review
severity: critical
category: defect
artifact: src/orchestrator/adapters/run_state_store.py#FileRunLock.acquire
status: resolved
traces: [VR-017, BR-017]
---

# RunLock acquire is not atomic (TOCTOU race)

**What is wrong:** `FileRunLock.acquire()` reads the lockfile, checks the PID, then writes a new lockfile. This is a read-then-replace sequence, not an atomic lock acquisition. Two concurrent starts can both observe "unlocked" and both win, violating VR-017's single-run invariant. The window is small but real.

**Fix:** Use atomic lock creation with `os.open(path, O_CREAT | O_EXCL | O_WRONLY)` which fails atomically if the file exists. Only reclaim stale locks through an atomic compare-and-swap path (read PID, verify dead, then atomic create).
