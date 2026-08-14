---
title: QA Re-validation — BUG-0012 spawn-abort group-kill
review: qa-revalidation
branch: bug/run-agent-envelope-recovery
tip: 773d35a
base: 713b8c4
date: 2026-08-06
reviewer: qa-agent
---

# QA Re-validation — BUG-0012 (dispatch_wave mid-run cancellation group-kill)

## Scope

Repeat-pass verification of finding `docs/findings/BUG-0012.md` (Major, infra).
BUG-0011's fix (`4857385`) mirrored `runPiStreamed`'s process-group kill pattern
but spawned the child **without `detached`**, so on Linux
`process.kill(-child.pid, SIGTERM/SIGKILL)` threw a swallowed `ESRCH` and a
mid-run abort never actually terminated the child. The follow-up fix (commits
`7746cfc` + `773d35a`) adds the missing spawn options and a real-subprocess
regression test. This pass independently verifies that fix.

## What the author changed

`spawnPi` (dispatch-wave.ts) now spawns with
`stdio: ["ignore","pipe","pipe"]`, `detached: process.platform !== "win32"`,
and calls `child.unref()` on non-win32 — mirroring `runPiStreamed`
(run-agent.ts). The terminate path still sets a distinct `cancelled` state,
group-kills SIGTERM→SIGKILL within a grace window, and the `error` handler
distinguishes cancellation from genuine spawn failure. The regression test
`__tests__/spawn-abort.test.ts` adds a case that spawns a real long-running
process and asserts it is actually terminated on abort — not merely that a
mock's `kill` was called.

## Verification

1. **Code read:** `detached` / `stdio` / `unref` present; group-kill targets a
   real process group; genuine-failure and cancellation-distinct handling
   preserved. Confirmed by direct read of the final `spawnPi`.
2. **Empirical probe (this Linux host):**
   - `detached=false` → `process.kill(-pid, "SIGTERM")` throws `ESRCH`, child
     still alive — the exact pre-fix condition.
   - `detached=true` → group SIGTERM succeeds, child closes.
     Confirms the fix makes the group-kill effective on non-win32.
3. **Suite runs:**
   - `spawn-abort.test.ts` → **4/4 pass** (includes "mid-run abort terminates a
     real child process within grace window").
   - `envelope.test.ts` → **19/19 pass** (no regression).
4. **Typecheck:** `dispatch-wave.ts` is imported by the passing spawn-abort
   test under `node --experimental-strip-types`, so a clean import is evidence
   it typechecks.

## Verdict

| Finding  | Severity | Fix commit      | Verdict      | Status               |
| -------- | -------- | --------------- | ------------ | -------------------- |
| BUG-0011 | major    | 4857385         | PASS (prior) | resolved             |
| BUG-0012 | major    | 7746cfc/773d35a | PASS         | resolved (confirmed) |

No new defects found. Note: `BUG-0012` was marked `resolved` by the author; this
independent pass re-confirms the code and test evidence, so the `resolved`
status stands.
