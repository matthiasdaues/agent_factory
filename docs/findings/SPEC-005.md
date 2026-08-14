---
id: SPEC-005
source: spec-review
severity: major
category: defect
artifact: docs/spec/prd.md#fr-k--session-transcript-token-control
status: resolved
resolved_by: requirements-agent
resolution_date: 2026-08-04
traces: [FR-K6, FR-K7, BR-042]
---

# Retrospective usage signals lack deterministic definitions

**What is wrong:** FR-K6, BR-042, the entity model, and the usage-capture interface name three derived signals without defining the cache-miss predicate, the turn aggregation unit, the early/late partition, the ratio formula, or zero-denominator and partially unavailable provider behavior. Different implementations can produce incompatible values from the same transcript, and contract fixtures cannot verify correctness.

**Fix:** Define provider-qualified source fields and exact formulas for all three signals, including session/turn boundaries, early-versus-late partitioning, nullability, partial availability, and zero denominators. Add acceptance examples with expected derived values for each supported provider capability class.

## Resolution Evidence

- BR-042 now defines the eligible top-level assistant-turn unit, native provider fields, cache-miss predicate, sums, deterministic first/last-third partition, ratio formula, and provider-qualified capability classes.
- System and interface contracts define complete-cache, input-only, unavailable, zero-miss, zero-denominator, and null behavior.
- UC-11 includes numeric Gherkin fixtures for each capability class plus zero-miss and zero-denominator cases.

## Reviewer Verification

Verified on 2026-08-04. BR-042 defines the eligible-turn unit, provider fields, cache-miss predicate, aggregation, first/last-third partition, null and zero rules, and capability classes. UC-11 provides deterministic numeric examples for full-cache, input-only, unavailable, zero-miss, and zero-denominator behavior.
