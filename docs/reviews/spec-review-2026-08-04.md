---
title: Specification Review — Accepted Token-Efficiency Proposals
date: 2026-08-04
reviewer: spec-review-agent
baseline: 5219c64b6586b7606df346cac668d128bd3c21fe
status: clean
---

# Specification Review — Accepted Token-Efficiency Proposals

## Reviewed specification

Reviewed the complete `docs/spec/` specification and both accepted design inputs:

- `docs/proposals/agent-dispatch-token-efficiency.md`
- `docs/proposals/proposal-session-transcript-token-control.md`

The immutable accepted baseline was `5219c64b6586b7606df346cac668d128bd3c21fe`. `docs/CONTEXT.md` does not exist; `docs/CONTEXT-MAP.md` was used as the repository's available context map.

`spec-lint`: 0 errors, 0 warnings, 17 information messages across 20 specification files.

## Deterministic findings

| Finding                                        | Severity | Disposition                                                                                                                                                     |
| ---------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FMT001: sixteen possible non-EARS requirements | Info     | Dismissed for this pass: the flagged normative statements are readable constraints; no deterministic error or ambiguity follows merely from the heuristic form. |
| TODO001: nine unresolved todo items            | Info     | Dismissed for this change review: the todo list records known implementation gaps and does not itself conflict with the accepted proposals.                     |

## Semantic findings

| Finding                                                                                                                                                                     | Artifact                                                             | Category | Severity | Characteristic                    |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------- | -------- | --------------------------------- |
| [SPEC-003](../findings/SPEC-003.md): dispatch assurance has no actor-goal-to-use-case chain; add or incorporate a justified audit use case and trace BR-043 through BR-048. | `docs/spec/prd.md#fr-l--dispatch-safeguard-assurance-audit`          | Defect   | Major    | Complete, necessary, traceable    |
| [SPEC-004](../findings/SPEC-004.md): deterministic handoff lint cannot infer omitted decisions; separate structural validation from semantic losslessness review.           | `docs/spec/use_cases/UC-11-cross-a-phase-boundary.md#business-rules` | Defect   | Major    | Consistent, verifiable            |
| [SPEC-005](../findings/SPEC-005.md): retrospective usage signals have no exact formulas or boundary behavior; define provider-qualified derivation rules and examples.      | `docs/spec/prd.md#fr-k--session-transcript-token-control`            | Defect   | Major    | Unambiguous, verifiable, complete |

No additional YAGNI defect was found. FR-L correctly treats already-delivered safeguards as audit-only and limits remediation to verified gaps. Chunked reads are advisory by design and do not claim deterministic enforcement.

## Traceability summary

The generated graph contains AG-01 through AG-11, UC-01 through UC-11, and BR-001 through BR-048. UC-11 realizes AG-11 and references BR-037 through BR-042. BR-043 through BR-048 have no referencing use-case edges, confirming the dispatch-assurance orphan described in SPEC-003. The graph does not model PRD goals or functional requirements, so G11-to-FR-L coverage must be inspected semantically.

## Disposition

The first pass found three Major defects. Requirements must address SPEC-003, SPEC-004, and SPEC-005 before the Requirements phase can pass. Architecture, planning, and implementation must not proceed on this specification.

## Repeat pass

The requirements remedies were reviewed individually, the deterministic gate was rerun, and the complete specification was semantically reinspected fresh.

### Prior-finding verification

| Finding  | Result   | Evidence                                                                                                                                           |
| -------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-003 | Resolved | AG-12 and fully dressed UC-12 now cover the audit's complete and verified-gap outcomes; the graph links UC-12 to BR-043 through BR-048.            |
| SPEC-004 | Resolved | Structural lint is restricted to observable defects; UC-11 now requires a distinct semantic losslessness review and includes an omission scenario. |
| SPEC-005 | Resolved | BR-042 supplies deterministic units, predicates, aggregation, partitions, capability classes, and null/zero behavior, with numeric UC-11 fixtures. |

### Fresh deterministic inspection

`spec-lint`: 0 errors, 0 warnings, 18 information messages across 21 specification files. The FMT001 and TODO001 information messages were reviewed and dismissed on the same grounds as the first pass.

### Fresh semantic findings

| Finding                                                                                                                                                                                                           | Artifact                                                             | Category | Severity | Characteristic                    |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------- | -------- | --------------------------------- |
| [SPEC-006](../findings/SPEC-006.md): `BR-038a` is outside the machine-recognized `BR-###` grammar, leaving the semantic handoff gate absent from traceability; assign a canonical rule ID or fold it into BR-038. | `docs/spec/use_cases/UC-11-cross-a-phase-boundary.md#business-rules` | Defect   | Major    | Consistent, verifiable, traceable |
| UC-11 extensions 7a and 8a point to the wrong main-flow steps after remedies inserted new steps; renumber them to 8a and 9a.                                                                                      | `docs/spec/use_cases/UC-11-cross-a-phase-boundary.md#extensions`     | Defect   | Minor    | Consistent, unambiguous           |

### Repeat-pass disposition

SPEC-003, SPEC-004, and SPEC-005 are verified resolved. One new Major defect, SPEC-006, remains open. The extension-numbering defect is Minor and remains report-only. Requirements must address SPEC-006 before the phase passes.

## Final repeat pass

SPEC-006 and the report-only extension-numbering defect were checked individually, followed by another complete deterministic and semantic inspection.

### Remedy verification

| Item                      | Result   | Evidence                                                                                                                                                                |
| ------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-006                  | Resolved | The semantic-review obligation is canonical BR-049; `traceability.json` contains the node and UC-11 → BR-049 edges, and no `BR-038a` reference remains in `docs/spec/`. |
| UC-11 extension numbering | Resolved | Child-persistence failure is now 8a and unavailable usage metrics are now 9a, matching main-flow steps 8 and 9.                                                         |

### Final deterministic inspection

`spec-lint`: 0 errors, 0 warnings, 18 information messages across 21 specification files. FMT001 and TODO001 remain informational and were dismissed after fresh review.

### Final semantic inspection

No new Major or Critical defect was found across consistency, ambiguity, verifiability, completeness, feasibility, necessity, terminology, traceability, or YAGNI.

Two non-blocking Minor wording issues remain report-only:

- UC-11's Human Operator stakeholder interest still says omissions are caught “mechanically,” although BR-038 and BR-049 correctly divide structural lint from semantic omission detection. Replace “omissions caught mechanically” with wording that covers mechanical defects plus semantic omissions.
- The validation-rules heading “BR-037…BR-042” omits BR-049 even though that section defines it. Include BR-049 in the heading or rename the heading without a numeric range.

### Final disposition

The specification review is clean: all Major findings SPEC-003 through SPEC-006 are verified resolved, the deterministic gate has zero errors and warnings, and no open SPEC finding remains. The Requirements phase may proceed to its next approved gate.
