# Clean-Cycle Fagan Review Report — 2026-07-22

## Scope

- Branch: `qa/token-usage-clean`, complete feature range
  `af81d0a0cf724570ae20e8af190f820c8c35b390..e88a455bc48fc9a2a488df01c0eb9f591680eaa8`.
- Every changed file was inspected against correctness, Clean Architecture,
  SOLID, maintainability, consistency, specification, and YAGNI.
- Focused re-verification covered all prior FAGAN, SEC, and RECON findings;
  trusted offline runtime; all installed CLI hooks; concurrent allocation;
  hostile paths; permissions and omission; and Pi registration, supervision,
  diagnostics, cancellation, drain, and cleanup.

## Finding table

| Finding                                                                                                                                                                                                   | Artifact                                                                                                                                                                               | Category | Severity |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------- |
| Claude, Codex, and Copilot background captures are invisible to the removal fence; reuse the existing supervised generation handoff for these adapters and add one uninstall-race regression per adapter. | `factory/config/hooks/capture-usage.sh:68`; `factory/config/hooks/capture-codex-usage.sh:35`; `factory/config/hooks/capture-copilot-usage.sh:33`; `factory/scripts/remove-factory:423` | Defect   | Major    |

Filed as `docs/findings/FAGAN-0005.md`.

## Prior finding verification

- `FAGAN-0002`, `FAGAN-0003`, and `FAGAN-0004` remain resolved. Pi registration
  is linearizable, concurrent IDs reserve distinct evidence, and the detached
  supervisor owns terminal cleanup and private diagnostics.
- `SEC-0001`, `SEC-0002`, and `SEC-0003` remain resolved. Identifier mapping,
  path/link defenses, exact private modes, omission, and hash-verified offline
  runtime execution are effective.
- `RECON-0006` through `RECON-0012` remain resolved against implementation and
  tests. `FAGAN-0005` extends uninstall coordination to the three native shell
  adapters; it does not reopen Pi's resolved lifecycle protocol.

## Five focus areas

**Correctness.** Capture normalization, provider totals, conservation,
persistence, and Pi lifecycle behavior conform to the proposal and ADR. The
remaining defect is cross-adapter uninstall behavior: three native hook workers
are not visible to the remover.

**Clean Architecture.** Native event parsing stays in per-CLI hooks and shared
capture behavior stays in the common pipeline. The fix should reuse the Pi
lifecycle handoff at this existing infrastructure boundary.

**SOLID.** Normalizer and persistence seams remain focused. No SOLID defect was
found.

**Maintainability.** Installed tests cover each adapter's ordinary trigger and
failure behavior. They need one deterministic uninstall interleaving per native
adapter to match Pi's lifecycle coverage.

**Consistency.** All capture sites promise best-effort, nonblocking persistence
and traceless removal. Pi fulfills both through registration and supervision;
the three shell hooks currently fulfill only the nonblocking half.

## YAGNI check

`FAGAN-0005` requires only a narrow reuse of the existing generation-fenced
supervised handoff for three known adapters. A generic job queue, process
manager, scheduling abstraction, or reusable background-work framework would
be speculative and is explicitly out of scope. No other YAGNI violation was
found.

## Verification evidence

- Exact full suite: `uvx pytest orchestrator/tests/ -q -W error` — clean exit,
  418 tests, no warning or temporary-directory cleanup failure, no overlapping
  pytest process. An isolated existing `PYTEST_DEBUG_TEMPROOT` prevented stale
  temp trees from contaminating the result.
- Isolated Pi lifecycle bug-hunt cycle:
  `uvx pytest orchestrator/tests/test_usage_capture_pi_e2e.py -q -W error` —
  27 passed in 21.29 seconds.
- Fresh OWASP review: no new realistic Medium-or-higher security finding.

## Done-check

- [x] Every changed file inspected against all five focus areas
- [x] All prior findings reverified
- [x] Finding is categorized, actionable, and constrained by YAGNI
- [x] Specification compliance explicitly checked
- [ ] Fagan review passes: `FAGAN-0005` remains open
