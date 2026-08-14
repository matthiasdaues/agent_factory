---
title: QA Re-validation — BUG-0011 dispatch-wave spawn-abort fix
review: qa-revalidation
branch: bug/run-agent-envelope-recovery
tip: 4857385023a41acf460008d832f2cd954c0dd458
base: 0fe8387fe65cc7953bd3d6f243f3a091dd6b37fd
date: 2026-08-06
reviewer: qa-agent
---

# QA Re-validation — BUG-0011 dispatch-wave spawn-abort fix

## Scope

Step-3 QA validation of the bug-fix playbook for `docs/findings/BUG-0011.md`
(major, infra) on branch `bug/run-agent-envelope-recovery`. Focus is the fix
commit `4857385` only; the rest of the branch was already re-validated at
`b9e3a71` and is **not** re-opened. The prior QA pass intentionally left
BUG-0011 open; this pass independently verifies the fix, runs the suites, and
sets the finding status.

`BUG-0011`: `spawnPi` in `factory/config/extensions/dispatch-wave.ts` passed
the parent agent-turn `signal` straight into `spawn("pi", …, { signal })`, so
an abort at/just after the nested spawn killed the child at birth and was
reported as `failed to spawn pi: The operation was aborted` for a child that
never ran. The fix (commit `4857385`) is supposed to stop passing the signal,
short-circuit an already-aborted signal to a distinct `cancelled: true`
outcome (never touching spawn), cancel a running child on mid-run abort via
SIGTERM→SIGKILL grace, preserve genuine spawn-failure surfacing, and add the
regression test `__tests__/spawn-abort.test.ts`.

## Verdict

| Finding  | Severity | Fix commit                                 | Verdict | Status         |
| -------- | -------- | ------------------------------------------ | ------- | -------------- |
| BUG-0011 | major    | `4857385023a41acf460008d832f2cd954c0dd458` | PASS    | resolved (set) |

**Reported-symptom PASS** — the misreporting BUG-0011 describes is fixed and
verified (criteria (a)–(d) below, suites green). One **new** defect was found
**in the fix's mid-run cancellation path** and filed as `BUG-0012` (major,
open); see below. Per the QA→Implementation handoff, that open finding loops
back for a fix and re-QA.

## Fix verification (commit 4857385)

Working tree clean against `4857385` (`git diff 4857385 -- <touched files>`
empty), so the inspected code is the committed fix.

**(a) No `signal` in `spawn()` options.** `spawnPi` now spawns with
`_spawn("pi", args, { cwd, env })` — only `cwd` and `env`. The old `signal:`
key is gone. The `signal` is consumed solely by an early-abort short-circuit
and a `signal.addEventListener("abort", terminate, { once: true })` listener.
Verified in `factory/config/extensions/dispatch-wave.ts` (`spawnPi` body) and
the regression test asserts `capturedOptions?.signal === undefined`.

**(b) Already-aborted → distinct cancellation, not the misleading error.**
`if (signal.aborted) return { status: null, stdout: "", stderr: "", error: null, cancelled: true };`
returns **before** `spawn` is ever called, so a never-ran child is reported as
`cancelled: true` with `error: null` — never
`failed to spawn pi: The operation was aborted`. The regression case
"pre-aborted signal: spawn NOT called with signal; reports cancellation"
passes, asserting `result.cancelled === true` and `result.error === null`.

**(c) Genuine spawn failure still surfaces as an error.** The
`child.on("error")` handler returns `{ …, error: err.message, cancelled: false }`
when `cancelled` is false, so a real ENOENT / bad cwd surfaces as an error,
distinct from cancellation. The regression case "genuine ENOENT still surfaces
as real error (not cancellation)" passes, asserting `result.error` includes
`ENOENT` and `result.cancelled === false`.

**(d) Caller (`execute`) handles `cancelled` distinctly from `failed to spawn`.**
In the dispatch loop, `if (child.cancelled)` is checked **before**
`if (child.error)`:

- `child.cancelled` → `r.error = "child process tree terminated because invocation was cancelled; task was not retried"`.
- `child.error` → `r.error = "failed to spawn pi: ${child.error}"`.

The cancelled item carries `r.error`, so the Phase-C merge filter
(`if (r.error || r.spawnExit !== 0) continue;`) skips it — no false merge of a
cancelled child.

## Suites

Run from `factory/config/extensions/__tests__/`:

- `node --experimental-strip-types --import ./envelope-loader.mjs --test ./spawn-abort.test.ts`
  → **3 pass, 0 fail** (pre-aborted cancellation; ENOENT surfaces as error;
  clean spawn reports `status: 0`). Matches the expected 3.
- `node --experimental-strip-types --import ./envelope-loader.mjs --test ./envelope.test.ts`
  → **19 pass, 0 fail** (no envelope regression). Matches the expected 19.

`dispatch-wave.ts` is imported by the passing `spawn-abort.test.ts`
(`import { spawnPi, type SpawnResult } from "../dispatch-wave.ts"`) under
`--experimental-strip-types`, so the clean import — all three tests load and
run the module — is the requested typecheck evidence.

## New defect filed — BUG-0012 (major, open)

While verifying the mid-run cancellation the finding's "Fix" section requires
("cancels a running child on mid-run abort via SIGTERM→SIGKILL grace"), a
defect was found **in the fix's new `terminate` path**:

`terminate` signals the running child with a process-group kill
(`process.kill(-child.pid, "SIGTERM")`, escalating to `SIGKILL`), but the
child is spawned with only `{ cwd, env }` — **no `detached`** — so on Linux the
child is not a process-group leader, no group with PGID `== child.pid` exists,
`process.kill(-child.pid, …)` throws `ESRCH`, the `catch {}` swallows it, and
the `else` branch (`child.kill(…)`) is unreachable on non-win32. The child is
never terminated on abort; `dispatch_wave` blocks on `await spawnPi(…)` until
natural completion. The distinct `cancelled: true` is still reported (so
BUG-0011's misreporting is gone), but the cancellation is not effected — a
functional regression vs. the pre-fix signal-in-`spawn` behaviour, which did
kill the mid-run child (and merely misreported).

`runPiStreamed` (`run-agent.ts:557`) makes the same group kill work by spawning
`detached: process.platform !== "win32"`; the fix mirrored `terminateChild`
but not that spawn option. `spawn-abort.test.ts` does not catch this because
its `MockChild.kill()` short-circuits to `close` and never exercises a real
process group.

Empirically confirmed on Linux: `spawn("sleep", ["30"], { cwd, env })` →
`process.kill(-pid, 0)` throws `ESRCH`; `process.kill(-pid, "SIGTERM")` throws
`ESRCH` (swallowed); child still alive after; a direct `child.kill("SIGTERM")`
on an identical child kills it.

This is a distinct root cause from the misreporting BUG-0011 describes, so it
is filed as a fresh finding — `docs/findings/BUG-0012.md` — and is **not** a
reason to keep BUG-0011 open: the symptom BUG-0011 reports (a never-ran child
misreported as a spawn failure) is resolved and verified. Fix direction for
BUG-0012: add `detached: process.platform !== "win32"` to the `spawnPi` spawn
options (mirror `runPiStreamed`'s actual spawn), so the group kill targets a
real group; add a regression case that asserts a real subprocess is terminated
within the grace window on abort.

## Finding table

| Finding                                                                                                                                                            | Artifact                                               | Category | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------ | -------- | -------- |
| BUG-0011 reported symptom (never-ran child misreported as `failed to spawn pi: The operation was aborted`) — fixed; status set `resolved`.                         | `factory/config/extensions/dispatch-wave.ts:spawnPi`   | Defect   | Major    |
| BUG-0012 (new): mid-run cancellation never terminates the child — group SIGTERM/SIGKILL ESRCHs on a non-detached spawn; `dispatch_wave` blocks until natural exit. | `factory/config/extensions/dispatch-wave.ts:terminate` | Defect   | Major    |

## Completion

BUG-0011's reported defect is resolved and verified (criteria (a)–(d), suites
3 + 19 green); status set `resolved`. One new major defect (BUG-0012) was
found in the fix's mid-run cancellation path and filed open. Per the
QA→Implementation handoff, the open BUG-0012 loops back for a fix and
re-QA; BUG-0011 itself is QA-clean for its scoped symptom.
