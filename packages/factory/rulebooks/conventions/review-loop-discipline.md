---
title: Repeat-Pass Verification
category: review
enforcement: reviewer-agent workflow (discipline, not lint-checkable)
version: 1.0.0
---

# Repeat-Pass Verification

Governs what a reviewer does on a **repeat pass** — after the author has addressed a prior review's findings.

## Rule

Canonical statement: [rules.md § Review loop discipline](../rules.md#review-loop-discipline). The three parts:

1. Re-run the deterministic check (lint/gate) — confirm its errors are gone.
2. For each prior open finding, verify individually — set `resolved` if the fix is adequate, otherwise note what's still missing and leave it `open`.
3. **Re-run the full inspection pass fresh** — not just against the prior findings list. A fix can introduce a defect the first pass never saw.

Treating a repeat pass as "check the old findings list, done" skips the one step that actually stands between a fix and an unreviewed regression — step 3 is not optional.

## Enforcement

Not mechanically checkable — no lint can verify a reviewer actually re-inspected rather than rubber-stamped. This rulebook exists because the failure mode is silent: a shortened repeat pass and a thorough one produce an identical-looking `status: resolved`.

## References

- Used by: spec review, ATAM architecture review, spec reconciliation
