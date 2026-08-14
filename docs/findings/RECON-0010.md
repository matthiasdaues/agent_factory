---
id: RECON-0010
source: reconcile-spec
severity: major
category: defect
artifact: factory/config/extensions/pi-usage.ts
status: resolved
traces: [ST-0044, ADR-0007]
---

# Pi capture can block the measured run for thirty seconds

**What is wrong:** `capturePiStream()` invokes `usage-capture` with synchronous
`spawnSync()` and a 30-second timeout. Human shutdown, `run_agent`, and
`dispatch_wave` all call this function inline before their lifecycle or tool
result completes. A slow or stalled tokenizer or persistence path can therefore
delay the run by up to thirty seconds, contradicting the mandatory contract
that telemetry never blocks or slows the work it measures. Existing
best-effort tests cover swallowed failures, not stalled capture latency.

**Fix:** Move Pi persistence off the measured lifecycle path while retaining a
reliable lifetime for the temporary transcript and eventual record. Add stalled
capture regression tests at the installed human-shutdown, `run_agent`, and
`dispatch_wave` boundaries that prove each measured operation completes without
waiting for the capture process.

**Resolution:** Pi now writes only the durable local handoff synchronously,
then starts `usage-capture` detached with ignored standard streams and releases
the child handle. The detached process owns source cleanup through a guarded
`--delete-source` option that accepts only a regular, non-symlink file directly
inside the canonical `.agent-factory/usage/.capture/` directory. Spawn failures
remove the staged source without delaying the caller.

Installed behavioral tests gate the real capture executable after it starts.
Human `session_shutdown`, `run_agent`, and `dispatch_wave` each return while the
gate remains closed; after release, every test observes the eventual record,
persisted transcript, correct lineage, and staged-source cleanup. RECON-0009's
nested merge/removal regression now polls for detached completion and continues
to prove that both descendant records survive worktree deletion.
