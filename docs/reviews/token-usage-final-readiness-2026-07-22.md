# Token Usage Capture Final Readiness — 2026-07-22

## Scope

- Branch: `qa/token-usage-final-ready`, exact base
  `8e5dd1bb0fdaa14ea126eaa8aef1a6419eed7654`.
- Reinspection covered the `FAGAN-0006` Pi bootstrap handshake remediation,
  its lifecycle tests, and the complete prior finding set.
- Correctness, architecture, SOLID, maintainability, consistency, YAGNI, and
  OWASP A01 through A10 were reconsidered.

## Finding table

| Finding                                                                                                                        | Artifact                                       | Category | Severity |
| ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------- | -------- | -------- |
| The accepted Python child remains referenced, so the Pi bootstrap survives ownership transfer; unref it after acknowledgement. | `factory/scripts/pi-capture-bootstrap.mjs:185` | Defect   | Major    |

Filed as `docs/findings/FAGAN-0007.md`.

## Assessment

`FAGAN-0006` correctly closes the pre-acceptance cleanup gap: validated,
generation-bound acceptance transfers responsibility to the shared Python
supervisor, while failure, timeout, and cancellation remain narrowly owned by
the bootstrap. However, the bootstrap does not unreference the accepted child,
so Node remains alive until capture completion. This violates the documented
single-supervisor post-acceptance lifecycle and blocks readiness.

The constrained remediation is `child.unref()` after acknowledged acceptance,
plus one fake-supervisor regression proving that the bootstrap exits promptly
while the accepted supervisor stays alive. No broader process-management
abstraction is warranted.

All earlier `FAGAN`, `SEC`, and `RECON` findings remain resolved. Fresh security
inspection found no realistic Medium-or-higher issue: bootstrap inputs are
canonically confined and generation-bound, the runtime command is fixed,
subprocess arguments are not shell-expanded, and diagnostics remain private
and transcript-free.

## Done-check

- [x] `FAGAN-0006` remediation inspected against all five Fagan focus areas
- [x] Prior findings reverified
- [x] Security review passed with no new `SEC-*` finding
- [x] New defect is actionable and YAGNI-constrained
- [ ] Final readiness passes: `FAGAN-0007` remains open
