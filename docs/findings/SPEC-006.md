---
id: SPEC-006
source: spec-review
severity: major
category: defect
artifact: docs/spec/use_cases/UC-11-cross-a-phase-boundary.md#business-rules
status: resolved
resolved_by: requirements-agent
resolution_date: 2026-08-04
traces: [FR-K3, UC-11, BR-038, BR-049]
---

# Semantic handoff rule is outside the traceable ID grammar

**What is wrong:** The remedy assigns the semantic completeness gate to `BR-038a`, but the specification's canonical and machine-recognized business-rule grammar is `BR-###`. `spec-lint` consequently produces no `BR-038a` node or edge in `traceability.json`, even though UC-11 relies on that rule to prevent information loss. The core phase-closure obligation is therefore invisible to deterministic traceability.

**Fix:** Give the semantic review obligation a canonical `BR-###` identifier, renumbering the newly added rule range and all references consistently if needed, or fold the complete obligation into BR-038. Regenerate the traceability graph and verify that UC-11 references the resulting canonical rule.

## Resolution Evidence

- Allocated canonical BR-049 to the separate Handoff Semantic Reviewer obligation.
- Replaced every noncanonical `BR-038a` reference in the specification and prior resolution evidence.
- Regenerated `docs/spec/traceability.json`; it contains BR-049 and UC-11 → BR-049 edges.

## Reviewer Verification

Verified on 2026-08-04. BR-049 is a canonical graph node, UC-11 has generated `references_br` edges to it, all inspected specification references use BR-049, and the former `BR-038a` identifier is absent from `docs/spec/`.
