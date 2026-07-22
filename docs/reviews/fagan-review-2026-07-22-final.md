# Final Fagan Review Report — 2026-07-22

## Scope

- Branch: `qa/token-usage-final`, complete feature range
  `af81d0a0cf724570ae20e8af190f820c8c35b390..328e46d9b43b0896f78719bd2a12d8b5bf3f0456`.
- All changed files were re-inspected after fixes for `FAGAN-0002`,
  `FAGAN-0003`, and `SEC-0001` through `SEC-0003`.
- Focused verification covered all four installed CLI paths, offline runtime
  execution, permission and omit behavior, hostile identifiers, concurrent
  record allocation, and Pi registration/removal state transitions.

## Finding table

| Finding                                                                                                                                                                                                                                      | Artifact                                                                               | Category | Severity |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------- | -------- |
| A detached Pi worker can exit before Python accepts cleanup ownership, leaking its pending marker and staged transcript; add launcher-owned cleanup or a supervised handshake, durable diagnostics, and deterministic async-test completion. | `factory/config/extensions/pi-usage.ts:168`; `factory/scripts/usage-capture-runtime:9` | Defect   | Major    |

Filed as `docs/findings/FAGAN-0004.md`.

## Prior finding verification

- **FAGAN-0002 — resolved:** the state-inode hard-link registration is visible
  atomically before metadata replacement. Drain observes and waits for the
  token; cancel removes it; stale active snapshots cause bounded abort and
  restoration. The barrier-based installed test covers the former pre-marker
  race.
- **FAGAN-0003 — resolved:** transcript reservation uses exclusive creation and
  the filesystem-key mapping. Twelve synchronized capture processes produce
  unique IDs, references, and evidence; pre-existing reservations cause safe
  sequence gaps rather than overwrite.

## Five focus areas

**Correctness.** Normal capture, conservation, path containment, permission,
retention, and uninstall scenarios conform to the stories and ADR. The one
remaining gap is the failure boundary between a successful detached spawn and
Python accepting cleanup ownership (`FAGAN-0004`).

**Clean Architecture.** Per-CLI event mapping remains isolated behind adapters,
while normalization, tokenization, records, and persistence remain shared. The
new offline runtime wrapper is an appropriate infrastructure boundary; its
cleanup handoff is incomplete rather than architecturally misplaced.

**SOLID.** The adapter protocols and storage-path object retain focused
responsibilities. No new SOLID defect was found.

**Maintainability.** Regression coverage is extensive, but detached tests must
wait for a terminal side-effect state. Otherwise a green test body can leave a
worker racing pytest teardown, as the warning-as-error reproduction proves.

**Consistency.** Best-effort capture consistently avoids failing the measured
run. That convention still requires owned cleanup and a durable diagnostic
when telemetry is dropped; silently abandoning registered state is
inconsistent with the removal contract.

## Pytest cleanup diagnosis

Command:

```text
uvx pytest orchestrator/tests/test_usage_capture_pi_e2e.py -q -W error -rA
```

Observed result: all test bodies reached 100%, followed by a session-finish
trace from `_pytest.pathlib.rm_rf` reporting `OSError: [Errno 39] Directory not empty` for a prior pytest temporary directory. Detached capture processes can
outlive their test and create or remove files after pytest starts deleting that
directory. This is nondeterministic test cleanup and the observable symptom of
the same missing terminal-state ownership as `FAGAN-0004`.

## YAGNI check

The security fixes add concrete containment, exclusive allocation, owner-only
storage, retention selection, and a verified offline runtime. Each serves an
accepted defect and executable test. No speculative abstraction was found.

## Done-check

- [x] Every changed file inspected against all five focus areas
- [x] Prior Fagan and security remediations reverified
- [x] Finding is categorized, reproducible, and actionable
- [x] Specification compliance and YAGNI explicitly checked
- [ ] Fagan review passes: `FAGAN-0004` remains open
