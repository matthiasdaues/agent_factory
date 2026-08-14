---
id: FAGAN-0004
source: fagan-review
severity: major
category: defect
artifact: factory/config/extensions/pi-usage.ts:168
status: resolved
traces: [ST-0044, ADR-0007, RECON-0010, RECON-0012]
---

# A detached Pi worker can exit without cleaning its registered capture

**What is wrong:** `capturePiStream()` removes its pending marker and staged
transcript only when Node reports a spawn `error`; after a successful spawn it
unrefs the child and delegates cleanup to Python. The
`usage-capture-runtime` launcher can exit before Python starts, however. One
deterministic reproduction is an installed runtime with its readiness marker
still present but its venv interpreter removed: the launcher exits zero, the
Python `finally` block never runs, the record is lost, and both
`.agent-factory/usage-control/pending/*.pending.json` and
`.agent-factory/usage/.capture/*.jsonl` remain indefinitely. A later default
`remove-factory` waits on the orphan marker until its timeout.

The same ownership gap leaks into the tests. Running
`uvx pytest orchestrator/tests/test_usage_capture_pi_e2e.py -q -W error -rA`
passes the test bodies, then pytest's session cleanup can fail with
`PytestWarning: (rm_rf) ... Directory not empty` because a detached worker is
still mutating a prior temporary directory. This is product/process leakage,
not a harmless permission warning: tests can finish before the side effect they
started has reached a terminal state.

**Fix:** Give the launcher or a supervised handoff process unconditional
ownership of cleanup for the narrowly validated Factory pending-marker and
staged-transcript paths, including every failure before Python successfully
executes. Alternatively, add an execution handshake and keep a supervisor
until Python accepts ownership. Persist a private diagnostic when capture is
dropped because detached stdio is intentionally ignored. Add an installed-path
regression that breaks or removes the runtime interpreter after registration
and proves marker/source cleanup, a visible diagnostic, and bounded removal.
Update asynchronous tests to wait for the registered capture's terminal state
so pytest temporary-directory cleanup is deterministic.

**Resolution:** Pi initially detached a Factory-owned Node supervisor rather
than the capture launcher directly. FAGAN-0005 moved the same capture-specific
ownership protocol into the provisioned Python runtime shared by all adapters.
The supervisor remains outside the measured
lifecycle, waits for the launcher/Python child, validates the registration,
generation, staged source, completion status, and Factory directory boundaries,
then solely owns terminal cleanup. Python reports `captured` only after the
canonical record and evidence are persisted; swallowed adapter failures report
`dropped`. Supervisor/capture spawn failures, non-zero Python exits, and
missing/dropped status produce bounded owner-private diagnostics without
retaining transcript text. Explicit cancel is benign and diagnostics cannot
recreate removed lifecycle paths. Installed Pi tests now wait for pending,
committing, scratch, and completion artifacts to settle; the Pi E2E suite exits
cleanly under `-W error`.

When the provisioned interpreter is already missing, Pi now declines
registration before creating any marker or staged source; there is no detached
handoff requiring a diagnostic or cleanup.

A post-merge full-suite run appeared to reproduce the cleanup warning, but the
reported path was a stale pytest garbage tree from the synchronous
`test_modes_are_exact_independent_of_umask[0777]` unit test. Its empty
`.agent-factory` directory had mode `000`, a fixed old mtime, and no pending,
committing, completion, scratch, or transcript artifact. Repeated runs merely
renamed that same undeletable inode to a new `garbage-<uuid>` path; no Pi
supervisor was mutating it.

The audit did identify a separate harness hardening opportunity: successful
record-reading helpers waited for terminal cleanup, but direct and failure-path
tests did not all pass through those helpers. The Pi E2E module now has an
automatic teardown fence that discovers every installed Factory root created
below that test's temporary directory and waits for real UUID-backed supervisor
artifacts to settle. Synthetic markers used to exercise drain and validation
remain outside that fence. This keeps the nonblocking production boundary
intact while ensuring no test releases a temporary tree that its detached
capture can still mutate. The exact full `orchestrator/tests/` suite is the
regression boundary, not warning suppression.
