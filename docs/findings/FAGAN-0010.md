---
id: FAGAN-0010
source: fagan-review
severity: major
category: defect
artifact: factory/config/extensions/run-agent.ts:275
status: resolved
traces: [UC-10, BR-034a, BUG-0004]
---

# Cancellation can hang on a non-cooperative child

**What is wrong:** `runPiStreamed` delegates cancellation entirely to Node's
`spawn(..., { signal })`, which sends one `SIGTERM`, and then waits without a
deadline for the child `close` event and both pipe `end` events. A child that
traps or ignores `SIGTERM`, or leaves descendants holding its pipes open, keeps
the `run_agent` invocation and its staging file alive indefinitely. The current
regression exits cooperatively from its `SIGTERM` handler, so it does not verify
UC-10 extension 6b or the minimal guarantee for a non-cooperative process.
Cancellation is also reported as `failed to spawn pi` even though the child
successfully spawned.

**Fix:** Own cancellation explicitly: remove the abort listener during final
cleanup, send `SIGTERM` once, wait a short bounded grace period, then send
`SIGKILL` to the child process group where the platform supports it. Bound pipe
drain as well, destroy remaining streams, await or otherwise reap the child,
and unlink bridge-owned staging in a `finally` block. Return a distinct
cancellation diagnostic and never retry. Add an installed-path regression
whose child ignores `SIGTERM` (and, if process-group cleanup is supported,
leaves a descendant holding stdout open); assert bounded return, forced
termination, staging cleanup, and exactly one spawn.

**Resolution:** `run_agent` now owns cancellation independently of Node's
single-signal spawn option. On POSIX it starts the child as a process-group
leader, sends `SIGTERM` to that group once, escalates to `SIGKILL` after 250
milliseconds, and destroys undrained pipes after a 750-millisecond bound. It
removes the abort listener and timers during cleanup, always unlinks
bridge-owned staging on cancellation, returns a distinct cancelled/no-retry
result, and never respawns. The installed-path tracer uses a child and
stdout-holding descendant that both ignore `SIGTERM`; the red implementation
exceeded the three-second test bound, while the fix returns within the
two-second contract bound, proves both PIDs terminated, staging is empty, and
the spawn count is exactly one.
