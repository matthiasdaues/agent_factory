---
id: FAGAN-0002
source: fagan-review
severity: major
category: defect
artifact: factory/config/extensions/pi-usage.ts:122
status: open
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
