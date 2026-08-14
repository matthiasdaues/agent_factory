---
id: SPEC-004
source: spec-review
severity: major
category: defect
artifact: docs/spec/use_cases/UC-11-cross-a-phase-boundary.md#business-rules
status: resolved
resolved_by: requirements-agent
resolution_date: 2026-08-04
traces: [FR-K2, FR-K3, BR-037, BR-038]
---

# Handoff lint overclaims semantic losslessness

**What is wrong:** FR-K3, UC-11, and BR-038 require `handoff-lint` to block an omitted open decision and treat a lint-clean handoff as information-complete. A deterministic validator can verify declared sections and syntax, but it cannot infer a decision that the author omitted. The immutable accepted proposal explicitly assigns semantic omissions to semantic review, so the specification both contradicts its design baseline and defines an unverifiable success guarantee.

**Fix:** Limit `handoff-lint` to mechanically observable structure, path, SHA, and repository-state rules. Add the accepted semantic completeness review obligation, its responsible actor, and an acceptance scenario that distinguishes structural validation from losslessness review.

## Resolution Evidence

- Narrowed FR-K3, BR-038, system requirements, and the `handoff-lint` interface contract to mechanically observable validation only.
- Added Handoff Semantic Reviewer and BR-049 as the separate completeness/losslessness obligation.
- Updated UC-11's flow, guarantee, diagram, and Gherkin to show that lint may pass while semantic review rejects an undeclared omission.

## Reviewer Verification

Verified on 2026-08-04. FR-K3, BR-038, UC-11, and the `handoff-lint` interface now limit deterministic validation to observable structure and explicitly assign omitted-fact detection to a separate semantic review. The follow-up identifier defect is tracked separately as SPEC-006.
