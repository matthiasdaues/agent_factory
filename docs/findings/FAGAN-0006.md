---
id: FAGAN-0006
source: fagan-review
severity: major
category: defect
artifact: factory/config/extensions/pi-usage.ts:170
status: resolved
traces: [ST-0044, ADR-0007, FAGAN-0004]
---

# Pi can lose its cleanup owner before the Python supervisor starts

**What is wrong:** Pi checks that the provisioned interpreter exists, then
creates its pending marker and staged transcript before spawning
`usage-capture-runtime --lifecycle supervise`. That shell launcher needs the
same interpreter to start the Python supervisor. If the interpreter disappears
after registration but before the launcher executes, the launcher exits 71.
Node sees a successfully spawned shell process rather than a spawn `error`, no
Python supervisor ever accepts cleanup ownership, and the marker/source remain
indefinitely. Default removal then times out waiting for the orphan
registration. The current missing-interpreter test deletes the interpreter
before capture begins, so Pi declines registration and does not exercise this
window.

**Fix:** Add only a tiny Pi-side Node bootstrap that owns validated
marker/source cleanup until the shared Python supervisor writes an explicit
acceptance handshake. After acceptance, transfer ownership and let the existing
Python supervisor remain the sole full supervisor. The bootstrap must write a
private transcript-free diagnostic and clean the registered source/marker if
the launcher exits or acceptance never arrives. Add a deterministic regression
that removes or disables the interpreter after registration but before
supervisor acceptance, then proves terminal cleanup, an owner-private
diagnostic, bounded successful removal, and no post-removal path resurrection.
Do not add a second full supervisor, job queue, process manager, or general
background-work framework.

**Resolution:** Pi now detaches a capture-specific Node bootstrap that owns
only the interval between durable registration and explicit Python acceptance.
It validates the canonical Factory root, pending marker, staged source,
completion status, acceptance path, and generation before launching the trusted
runtime. The shared Python supervisor writes a private `0600` acceptance file
immediately after its own validation; observing that exact handshake transfers
ownership and the bootstrap exits. Python remains the sole normalization,
persistence, status, diagnostic, and post-acceptance cleanup supervisor.

Before acceptance, launcher spawn/exit and bounded timeout produce a private,
transcript-free diagnostic and narrowly clean marker, source, status, and
handshake. Cancel/removal suppresses diagnostics and no path is recreated.
Installed regressions remove the interpreter after registration, exercise
successful transfer, timeout, and pre-accept cancel, then prove bounded removal
and no resurrection. The bootstrap contains no tokenization, persistence,
drain policy, queue, or general process-management behavior.
