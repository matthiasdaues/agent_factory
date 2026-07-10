# Specification Review — TUI Menu Mode Addendum (Verification Pass)

**Date**: 2026-07-07
**Reviewer**: Specification Review Agent (separate session from the author)
**Prior report**: [spec-review-2026-07-07.md](spec-review-2026-07-07.md)
**Result**: Clean for gate and handoff — `spec-lint` reports zero errors and all six filed findings are verified resolved. Two Minor observations remain in this report only.

## Scope of this pass

This is the repeat pass over the six findings raised in the first review of commit `1c8bc23`. Each fix was verified independently against the changed artifacts; the deterministic linter was re-run; and the changed regions were re-inspected for defects introduced by the fixes.

`spec-lint --spec-dir docs/spec --graph docs/spec/traceability.json` now reports **0 errors, 12 warnings, 16 info** (previously 3 / 13 / 22). The requirements gate passes.

## Verification of prior findings

| Finding   | Severity | Fix verified                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Status                              |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| SPEC-0001 | Critical | UC-10, UC-11, and UC-12 now carry a `## Postconditions` section grouping their guarantees, matching UC-08/09. All three `STRUCT001` errors are gone; `spec-lint` exits zero.                                                                                                                                                                                                                                                                                             | **Resolved**                        |
| SPEC-0002 | Major    | The business-rule citations in all five TUI sections of `system-use-cases.md` now resolve to the governing rules: configuration cites BR-037…041, adapters cite BR-042…049, skill-scoped execution cites BR-050…054, and backlog cites BR-056…060. No citation resolves to an unrelated earlier rule. `TRACE003` orphans dropped from ten to two.                                                                                                                        | **Resolved** (residual noted below) |
| SPEC-0003 | Major    | The phase-run model rule is now stated consistently in all four places — `cli_specification.md` design rule 4, the model-resolution-chain diagram, `prd-tui-addendum.md` FR-R12, and the `system-use-cases.md` Model selection section, with VR-023 updated to match. T-34 is marked resolved: agent tier resolves independently per agent for all phases, and story classification elevates the effective tier only during implementation (the higher of the two wins). | **Resolved**                        |
| SPEC-0004 | Major    | An authority note in `interface-contracts.md` (and a matching line in `cli_specification.md`) declares the per-adapter model dictionary the runtime single source of truth for tier-to-model resolution, with the model-matrix `[facts]` section as the operator-authored artifact that populates it. T-32 is marked resolved consistently.                                                                                                                              | **Resolved**                        |
| SPEC-0005 | Major    | UC-08 now declares `Realizes: AG-08, AG-13`. The `TRACE001` coverage gap for AG-13 is gone.                                                                                                                                                                                                                                                                                                                                                                              | **Resolved**                        |
| SPEC-0006 | Major    | FR-R11 now specifies that an absent or null tier is treated as `standard`; VR-041 records the rule and `interface-contracts.md` carries a matching null-tier note.                                                                                                                                                                                                                                                                                                       | **Resolved**                        |

## Re-inspection findings (new, Minor)

Two low-severity observations surfaced while verifying the fixes. Both are Minor and remain in this report only; neither blocks the gate or the handoff.

| #   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Characteristic          | Artifact                                                  | Severity |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | --------------------------------------------------------- | -------- |
| m3  | BR-053 (scope-sensitive completion) and BR-055 (run-step default model resolution) are defined in UC-11 but referenced by no requirement (`TRACE003`). BR-055 now duplicates the FR-R11 requirement already governed by BR-046. Either cite BR-053 from a skill-scoped completion requirement and BR-055 from the run-step model-resolution requirement, or fold BR-055 into BR-046.                                                                              | Consistent, Necessary   | system-use-cases.md, UC-11                                | Minor    |
| m4  | FR-R12's new clause — "during the implementation phase the effective tier is the higher of the agent's declared tier and the story's classification tier" — is ambiguous against the Phase model and FR-M, where the orchestrator invokes `implementation-agent` once as a dispatcher and per-story model selection happens below the adapter boundary. Clarify which agent's tier is elevated and where the elevation is resolved (orchestrator vs. dispatcher). | Consistent, Unambiguous | prd-tui-addendum FR-R12, system-use-cases.md §Phase model | Minor    |

## Carried-forward Minor findings

The two Minor findings from the first pass were not required to clear the gate:

- **m1** (VR-035 vs BR-042 validation-probe clause) — not addressed; still open as a Minor.
- **m2** (EARS atomicity, compound `shall`) — not addressed; twelve `FMT004` warnings remain. Still a Minor.

## Disposition and handoff

`spec-lint` reports zero errors and no `SPEC` finding remains open (SPEC-0001 through SPEC-0006 are all `resolved`). Under the review loop's clean-exit rule, the specification is ready to hand off.

**Handoff.** Specification review is clean. Run the Architecture Agent against `docs/spec/`. The four Minor observations (m1–m4) are optional polish and may be folded into a later requirements touch-up; none needs to block architecture.
