---
id: SPEC-001
title: UC-09 assumes script_exit_zero is implemented but it is stubbed
status: resolved
severity: Major
category: Consistency
date: 2026-07-12
found_by: spec-review-agent
resolved_by: requirements-agent
resolution_date: 2026-07-12
tags: [SPEC, UC-09, script_exit_zero, T-03]
---

# SPEC-001: UC-09 assumes script_exit_zero is implemented but it is stubbed

## Summary

UC-09 specifies phase advance invoking `run-tests` via `script_exit_zero` entry conditions as if this functionality is currently implemented, but validation-rules.md and T-03 both state that `script_exit_zero` is stubbed to always pass without executing the named script.

## Location

- **Use Case**: docs/spec/use_cases/UC-09-run-tests-via-hook.md
- **Supplementary Spec**: docs/spec/supplementary_specs/validation-rules.md
- **Todo**: docs/spec/todos.md (T-03)

## Evidence

**UC-09 Trigger section**:

> One of three mechanical hooks fires:
>
> - `pre-commit` (git commit) — runs changed-file subset for fast feedback
> - `pre-push` (git push) — runs full suite as the "ready to share" gate
> - `phase advance` evaluates `script_exit_zero: factory/scripts/run-tests --full` as an entry condition

**UC-09 Preconditions**:

> - For `phase advance` invocation: the FSM declares a `script_exit_zero` entry condition referencing `factory/scripts/run-tests`.

**UC-09 Extension 2a.3**:

> Hook blocks the operation; phase advance refuses with "script_exit_zero unmet".

**But validation-rules.md § Entry conditions** states:

> - `script_exit_zero`: **always satisfied** in the current implementation — deliberately stubbed, not yet running the named script. See [T-03](../todos.md#t-03-script_exit_zero-condition-type-is-stubbed).

**And T-03 confirms**:

> `factory/scripts/phase`'s `evaluate_condition` always returns `(True, "script_exit_zero <script> (stubbed pass)")` for this condition type — it never actually runs the named script.

## Impact

**Specification inconsistency**: UC-09 describes behavior (phase advance running tests via script_exit_zero) that cannot occur with the current stubbed implementation. This creates false expectations for:

1. Implementers who read UC-09 and believe phase advance already enforces test passage
2. Operators who configure FSM entry_conditions expecting tests to block phase advance
3. Readers trying to understand what functionality exists versus what is planned

## Recommended Fix

**Option 1 (Spec-before-code approach)**: Add a clarifying note to UC-09 stating this use case specifies intended behavior that requires implementing T-03 first. Update UC-09 preconditions to note the dependency on T-03 implementation.

**Option 2 (Align with current state)**: Remove or mark as "planned" the phase advance integration point from UC-09 until script_exit_zero is implemented. UC-09 would specify only the pre-commit and pre-push hooks, with phase advance deferred to a future specification update.

**Recommended**: Option 1, with this change to UC-09:

Add to the use case header after "Realizes: AG-09":

```markdown
**Implementation Status**: This use case specifies intended behavior. The `phase advance` integration point requires implementing T-03 (`script_exit_zero` condition evaluation) first. Pre-commit and pre-push hook integration points can be implemented immediately.
```

And update the Trigger section:

```markdown
One of three mechanical hooks fires:

- `pre-commit` (git commit) — runs changed-file subset for fast feedback
- `pre-push` (git push) — runs full suite as the "ready to share" gate
- `phase advance` evaluates `script_exit_zero: factory/scripts/run-tests --full` as an entry condition *(requires T-03 implementation)*
```

This preserves the complete specification while explicitly acknowledging the implementation dependency.

## References

- docs/spec/use_cases/UC-09-run-tests-via-hook.md
- docs/spec/supplementary_specs/validation-rules.md § Entry conditions
- docs/spec/todos.md § T-03
- docs/spec/prd.md § FR-I5 (lists all three hooks without noting implementation status)

## Category Rationale

**Consistency**: Specification contradicts itself — UC-09 describes script_exit_zero invoking run-tests, while validation-rules.md states script_exit_zero is stubbed to always pass without executing scripts.
