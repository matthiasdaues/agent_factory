# Readiness Fagan Review Report — 2026-07-22

## Scope

- Branch: `qa/token-usage-ready`, complete feature range
  `af81d0a0cf724570ae20e8af190f820c8c35b390..db88ace7ddc513cc5ffdb41901e1641f59432d6c`.
- Fresh inspection covered the complete feature and the 22-file
  `FAGAN-0005` remediation diff, including all native hooks, the shared Python
  lifecycle registrar/supervisor, Pi integration, removal, tests,
  architecture, stories, and user documentation.
- All prior FAGAN, SEC, and RECON findings were rechecked.

## Finding table

| Finding                                                                                                                                                            | Artifact                                                                                | Category | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- | -------- | -------- |
| Pi can register before the Python-dependent supervisor has a cleanup owner; add a tiny Node bootstrap that transfers ownership only after an acceptance handshake. | `factory/config/extensions/pi-usage.ts:170`; `factory/scripts/usage-capture-runtime:12` | Defect   | Major    |

Filed as `docs/findings/FAGAN-0006.md`.

## Prior finding verification

- `FAGAN-0002`, `FAGAN-0003`, and `FAGAN-0005` remain resolved. Registration
  ordering, concurrent evidence allocation, and native Claude/Codex/Copilot
  removal coordination are correct.
- The shared Python supervisor correctly owns cleanup after it starts, but the
  Pi launch path reopens `FAGAN-0004` before Python can accept ownership.
- `SEC-0001` through `SEC-0003` and `RECON-0006` through `RECON-0012` remain
  resolved.

## Reproduction

1. Start `capturePiStream()` with a ready installed runtime.
2. Allow it to hard-link the active state, replace the marker metadata, and
   write the staged transcript.
3. Before `usage-capture-runtime` resolves its interpreter, remove or disable
   `.agent-factory/usage-runtime/bin/python`.
4. The shell launcher exits 71. Because the shell itself spawned successfully,
   Node's `error` handler does not run, and Python never reaches supervisor
   cleanup.
5. The pending marker and staged source remain. `remove-factory` drain reaches
   its timeout and restores the installation to active.

The expected corrected outcome is marker/source cleanup, one private
transcript-free diagnostic, bounded removal success, and no late Factory path
recreation.

## Five focus areas

**Correctness.** Native lifecycle drain/cancel behavior now satisfies
`FAGAN-0005`. Pi still has a bootstrap ownership gap before the shared
supervisor starts.

**Clean Architecture.** One shared Python lifecycle is appropriate. The fix is
a minimal launch-ownership bridge, not a second lifecycle implementation.

**SOLID.** Registrar, supervisor, capture, and removal responsibilities are
otherwise clear. No additional SOLID defect was found.

**Maintainability.** The native race matrix is strong. Pi needs one barrier
test at the exact registration-to-acceptance boundary; the existing
pre-registration missing-runtime case is not equivalent.

**Consistency.** Every accepted registration must reach terminal cleanup.
Native hooks and post-start Python supervision now do; the Pi bootstrap window
does not.

## YAGNI check

The approved remediation is deliberately narrow: a tiny Node bootstrap owns
cleanup only until the existing Python supervisor acknowledges acceptance.
Building a second full supervisor or a general process/job framework would be
speculative and is prohibited.

## Verification evidence

- The all-CLI lifecycle/adversarial matrix passed under `-W error`, including
  native drain/cancel races, Codex with a poisoned `node`, missing
  runtime/source/supervisor paths, full/omit persistence, and Pi cleanup.
- Fresh OWASP A01-A10 inspection found no new realistic Medium-or-higher
  security issue.
- The mandatory final full suite is deferred until `FAGAN-0006` is fixed,
  because readiness cannot pass with an open Major defect.

## Done-check

- [x] Changed files inspected against all five focus areas
- [x] Prior findings reverified
- [x] New defect is reproducible, actionable, and YAGNI-constrained
- [x] Specification compliance explicitly checked
- [ ] QA passes: `FAGAN-0006` remains open
