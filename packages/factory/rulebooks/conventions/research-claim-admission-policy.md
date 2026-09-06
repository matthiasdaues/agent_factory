---
title: Claim-Admission Policy
category: policies
enforcement: semantic review validator
version: 1.0.0
---

# Claim-Admission Policy

## Purpose

The claim-admission policy governs whether a claim may enter the surviving portion of the claim register and, from there, the final report. It states the full set of conditions a claim must satisfy — no partial satisfaction admits a claim, and no single condition substitutes for the rest.

## Requirements

A claim is admitted only when every condition below holds, evaluated against the conjecture, its reviews, its votes, and its test records.

### One Assertion

The conjecture's `claim` field states exactly one assertion. A conjecture that bundles more than one assertion into a single claim is not admissible; each assertion must be split into its own conjecture and evaluated independently.

### Clear Scope

The conjecture's `scope` field states the boundary within which the claim is asserted to hold. A claim without a stated scope, or whose scope is too vague to test against, is not admissible.

### Explicit Assumptions

The conjecture's `assumptions` field lists every background assumption the claim depends on. Assumptions introduced only after a test has failed do not satisfy this condition; assumptions must be explicit before testing, not added afterward to preserve a claim under review.

### A Stated Refutation Condition

The conjecture's `possible_refuting_evidence` field states what observation, if made, would refute the claim. A claim that cannot state what would count against it is structurally incomplete and is not admissible.

### Required Tests Run

Every planned test listed in the conjecture's `planned_tests` has a corresponding test record with an `outcome` of `SURVIVED`, `REFUTED`, `INCONCLUSIVE`, or `INVALID_TEST`. A claim with planned tests that were never run is not admissible.

### Evidence Checks Passed

The claim's supporting and contrary evidence satisfy the Evidence Policy — precise source references, source dates, source provenance, source-family identification, source limitations, and contrary-evidence searches. Evidence that fails these checks does not count toward admission.

### Required Reviews Completed

At least one review exists for the claim, and that review's `checks` are complete: testability, alternatives considered, test severity, survival unchanged, source wording support, source independence, explicit assumptions, scope adherence, contrary-evidence treatment, and possible overturning evidence have all been assessed.

### Strict Majority of Decisive Votes for Survival

Among votes cast on the claim, only `SURVIVE` and `REFUTE` are decisive; `UNRESOLVED` and `ABSTAIN` are not decisive and do not count toward the majority. `SURVIVE` must receive a strict majority of the decisive votes — strictly more than half — for the claim to be admissible. A tie, or a plurality short of a strict majority, does not admit the claim.

### No Blocking Defect

No review of the claim records a `defect_level` of `BLOCKER`. A claim with an outstanding blocking defect is not admissible regardless of its vote tally.

### No Unanswered Material Refutation

Every material refutation raised in a review or test record has been addressed — either resolved by evidence, or by narrowing, replacing, or withdrawing the claim. A material refutation left unanswered blocks admission even if the vote tally otherwise favors survival.

### All Votes Reference the Current Claim Version

Every vote's `claim_hash` matches the content hash of the claim version currently under evaluation. Any semantic change to the claim's substance produces a new claim version; votes and reviews cast against a prior version do not carry forward and do not count toward admission of the current version.

## What a Vote Decides

A vote decides whether a claim met the process standard set out above — whether it was tested, reviewed, and evidenced as this policy requires. A vote does not decide whether the claim is true. A claim that is admitted has survived the defined tests within its stated scope; it has not been proved true, and admission must never be represented as a determination of truth.

## Application

These requirements apply when a claim is considered for inclusion in the frozen claim register's surviving claims. A claim failing any condition above is refuted, unresolved, or superseded — never surviving — regardless of how many other conditions it satisfies.

## Not Covered by This Policy

This policy does not decide:

- how many reviewers or votes constitute quorum,
- how contested votes are resolved procedurally,
- how a refuted or unresolved claim is reworked,
- how surviving claims are presented in the final report.

Those decisions belong to research planning, the Role-Separation Policy, and the Report Policy.
