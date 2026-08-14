---
id: FAGAN-0002
source: fagan-review
severity: major
category: defect
artifact: factory/config/extensions/pi-usage.ts:122
status: resolved
traces: [ST-0044, ADR-0007, RECON-0012]
---

# Pi removal can miss a capture registration created after the drain fence

**What is wrong:** `capturePiStream()` reads an `active` state before it creates
its pending marker. In the interval between those operations,
`remove-factory` can change the state to `drain`, observe an empty pending
directory, and begin deleting Factory paths. The capture then creates its
marker and its second state check accepts `drain`, so it can proceed against a
teardown that no longer waits for it. This loses usage or recreates Factory
paths after removal. Current tests cover a marker visible before removal and a
registration begun after the fence, but not this interleaving.

**Fix:** Serialize registration and the removal state transition with one
filesystem-backed exclusion protocol. A capture must establish a visible
registration atomically while the state is active; removal must acquire the
same exclusion before transitioning state and deciding that the registry is
empty. Add a deterministic barrier-based installed-path regression for the
sequence `read active -> remover sees empty -> create marker`, proving removal
either drains the registered capture or prevents it without late path
recreation.

**Resolution:** Pi now creates the final pending marker as a hard link to
`state.json` before it reads lifecycle state. Hard-link creation and the
remover's atomic state replacement have a filesystem order: a token linked
first snapshots the active-generation inode and is visible before drain scans;
a token linked afterward snapshots drain/cancel and cannot spawn persistence.
Registration metadata is atomically renamed over that same marker, so it never
disappears from the registry during conversion.

Drain treats active snapshot tokens as in-flight and aborts boundedly on a
crashed token, restoring the active installation. Cancel may discard snapshot
or pending tokens, while committing workers still drain. Initialization probes
same-volume hard-link support without failing unrelated CLI setup, and both init
and runtime report a clear limitation instead of silently weakening the fence.

An installed-path regression patches Node's filesystem bindings to pause the
old implementation after its active read and the new implementation after its
atomic link. It proves removal remains blocked by the visible token, then by the
detached worker, before completing without path resurrection. Separate tests
cover stale-token drain restoration, cancel cleanup, and unsupported-filesystem
diagnostics.
