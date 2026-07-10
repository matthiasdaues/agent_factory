---
id: FAGAN-0026
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/cli.py#main
status: resolved
traces: [VR-017, BR-017]
---

# VR-017 check incomplete — only lock, not run.json mode

**What is wrong:** The single-run invariant is enforced only via the lockfile. If `run.json` says `mode: running` but the lock is absent (crashed process, manual delete), a second start is allowed. VR-017 says to refuse when "a lock is held or a run is running."

**Fix:** Before starting, check both the lockfile and `run.json` mode. Refuse to start if either indicates an active run, unless an explicit stale-recovery path is used.
