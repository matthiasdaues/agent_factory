---
id: SPEC-003
source: spec-review
severity: major
category: defect
artifact: docs/spec/prd.md#fr-l--dispatch-safeguard-assurance-audit
status: resolved
resolved_by: requirements-agent
resolution_date: 2026-08-04
traces: [G11, FR-L1, FR-L2, FR-L3, BR-043, BR-044, BR-045, BR-046, BR-047, BR-048]
---

# Dispatch assurance has no actor-goal-to-use-case chain

**What is wrong:** G11 and FR-L introduce a dispatch-safeguard assurance goal, and BR-043 through BR-048 define its rules, but no actor goal or Cockburn use case realizes them. AG-11 and UC-11 concern phase-boundary continuity only. The generated graph therefore contains BR-043 through BR-048 as nodes without any use-case reference, leaving the audit workflow, failure extensions, and acceptance criteria unspecified.

**Fix:** Add a justified actor goal and a Cockburn use case for performing the baseline assurance audit, including its verified-gap and already-complete outcomes, or explicitly incorporate the audit into an existing actor goal and use case without conflating it with phase-boundary continuation. Trace FR-L and BR-043 through BR-048 through that chain.

## Resolution Evidence

- Added Assurance Auditor and AG-12 in `docs/spec/actor-goal-list.md`.
- Added Cockburn fully dressed `docs/spec/use_cases/UC-12-audit-dispatch-safeguards.md`, with complete and verified-gap flows, Gherkin acceptance criteria, and explicit BR-043…BR-048 traceability.
- Preserved the accepted baseline rule that complete evidence creates no retrospective implementation work.

## Reviewer Verification

Verified on 2026-08-04. AG-12 and the fully dressed UC-12 now provide the actor-goal-use-case chain, exercise both `complete` and `verified gap` outcomes, and reference BR-043 through BR-048 in the generated traceability graph.
