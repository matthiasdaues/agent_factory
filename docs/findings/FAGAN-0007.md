---
id: FAGAN-0007
source: fagan-review
severity: major
category: defect
artifact: factory/scripts/pi-capture-bootstrap.mjs:185
status: open
traces: [ST-0044, ADR-0007, FAGAN-0006]
---

# Pi bootstrap retains the accepted Python supervisor

**What is wrong:** After the Python supervisor acknowledges acceptance, the Pi
bootstrap removes the handshake but never unreferences the spawned child.
Node therefore retains the child-process handle and remains alive until the
Python capture finishes. This contradicts the explicit ownership transfer in
`FAGAN-0006`: after acceptance, Python should be the sole supervisor and the
bootstrap should exit. A stalled capture instead leaves both processes alive.
The current acceptance regression waits for the final usage record, so it does
not detect that the bootstrap survives the transfer.

**Fix:** Call `child.unref()` only after the validated acceptance handshake has
been acknowledged and removed. Add one deterministic fake-supervisor
regression that writes the valid acceptance handshake and then stays alive;
prove the bootstrap exits promptly while the accepted supervisor continues.
Do not add another lifecycle protocol, process manager, or broader bootstrap
responsibility.
