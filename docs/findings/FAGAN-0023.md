---
id: FAGAN-0023
source: fagan-review
severity: minor
category: defect
artifact: ~/.pi/agent/extensions/openwebui.ts:131
status: resolved
---

# Read-modify-write race on the config file between async command handlers

**What is wrong:** `persistInstance` and `removeInstance` each do read → mutate → write with awaits between the steps, and nothing serializes command handlers. Two overlapping `/register` calls, or a `/register` racing a `/unregister` (or a `/reload` while a command is in flight), can interleave at the awaits and lose one update; the last writer wins with stale content. Human-typed commands make the probability low, but the file is the single source of truth for registrations.

**Fix:** Chain config mutations through an in-module promise queue (a trivial mutex: `queue = queue.then(fn)`), or hold a lock across the read-write pair. A test with two concurrent `persistInstance` calls should show both entries surviving.

**Resolution (repeat pass 2026-08-19):** Fixed as claimed. `withConfigLock()` chains each operation on the settled previous chain (`configLock.then(operation, operation)`) and re-latches with a rejection-swallowing continuation — the standard promise-queue mutex, correct here. Both `persistInstance` and `removeInstance` perform their read-modify-write inside the lock, so two overlapping commands can no longer lose an update. The (slower) discovery fetch stays outside the lock — minimal critical section.
