# Specification Review — Test Execution Hooks Extension

**Date**: 2026-07-12
**Reviewer**: spec-review-agent
**Scope**: UC-09, PRD § G9/FR-I1..FR-I6, actor-goal-list.md § AG-09, validation-rules.md § BR-023..BR-027
**Review Type**: Fagan-style specification review (brownfield extension)

______________________________________________________________________

## 1. Reviewed Specification

**New Files:**

- docs/spec/use_cases/UC-09-run-tests-via-hook.md (Realizes AG-09)

**Updated Files:**

- docs/spec/prd.md (added Goal G9, Functional Requirements FR-I1..FR-I6)
- docs/spec/actor-goal-list.md (added AG-09)
- docs/spec/supplementary_specs/validation-rules.md (added Test execution section, BR-023..BR-027)

**Deterministic Validation:**

```
$ factory/scripts/spec-lint --spec-dir docs/spec --graph docs/spec/traceability.json
spec-lint: 0 error(s), 0 warning(s), 5 info across 17 spec file(s).
```

All deterministic checks pass. Traceability graph confirms:

- UC-09 → AG-09 (realizes)
- UC-09 → BR-023, BR-024, BR-025, BR-026, BR-027 (references_br)

______________________________________________________________________

## 2. Semantic Inspection Results

Evaluated against the seven requirements-quality characteristics per Wiegers/INCOSE:

### 2.1 Consistent

❌ **SPEC-001 (Major)**: UC-09 describes phase advance invoking `run-tests` via `script_exit_zero` entry conditions as if this functionality is currently implemented. However, validation-rules.md § Entry conditions and T-03 both state that `script_exit_zero` is stubbed to always pass without executing the named script. This creates a specification contradiction — UC-09's Trigger, Preconditions, and Extension 2a.3 all assume script_exit_zero works, but it doesn't.

⚠️ **SPEC-002 (Minor)**: UC-07's business rules describe `block-dangerous-git.sh`'s pattern list as covering two groups (history-discarding commands and gate-bypassing commands), but BR-024 (introduced by UC-09) adds a third group (test commands). UC-07 should acknowledge this extension of scope for completeness.

✅ Otherwise consistent:

- UC-09 correctly realizes AG-09
- G9 → FR-I1..FR-I6 → UC-09 traceability is intact
- Business rules BR-023..BR-027 are consistently referenced throughout UC-09
- The three integration points (pre-commit, pre-push, phase advance) are consistently described across PRD § FR-I5, UC-09 Trigger, and validation-rules.md

### 2.2 Unambiguous

✅ No ambiguity detected:

- Primary actor is clearly defined as "git / pre-commit (supporting actor — invoked mechanically)"
- Trigger specifies three concrete hook invocation points
- Exit codes are precisely defined (0 = pass, 1 = test failure, 2 = framework detection failure)
- JSON output format is specified exactly: `{"passed": int, "failed": int, "skipped": int, "duration_ms": int}`
- Framework detection order is explicit (pyproject.toml → package.json → go.mod → Cargo.toml)
- The two modes (`--changed-only` vs `--full`) have clear semantics

### 2.3 Verifiable

✅ Highly verifiable:

- UC-09 includes six Gherkin scenarios covering all major paths:
  - Pre-commit runs changed-file tests and passes
  - Pre-commit blocks commit on test failure
  - Pre-push runs full suite and blocks on failure
  - Phase advance refuses when tests fail
  - Agent blocked from running tests directly
  - No test framework detected
- Postconditions are concrete and testable:
  - Success Guarantee: "when run-tests exits 0, the test suite passed at the moment of invocation"
  - Minimal Guarantee: "on failure, operation is blocked, stderr shows which tests failed"
- Extensions specify observable outcomes (exit codes, stderr messages, blocked operations)

### 2.4 Complete

✅ Extensions cover realistic failure modes:

- 2a: No test framework detected
- 3a: Test framework detected but command fails (config error, missing dependencies)
- 5a: One or more tests fail
- 1a: Agent attempts to run test command directly
- 1b: Human operator commits with failing tests
- 1c: Human operator pushes with failing tests

✅ All three PRD goals are realized:

- G9 (hook-triggered test execution) → AG-09 → UC-09
- FR-I1..FR-I6 are all traceable to specific UC-09 sections

⚠️ Caveat: The phase advance integration point is specified but cannot function until T-03 (script_exit_zero implementation) is completed (see SPEC-001).

### 2.5 Feasible

✅ No conflicting requirements detected:

- Uses existing hook infrastructure (pre-commit, PreToolUse hooks)
- Relies on project-native test frameworks (no new dependencies)
- Zero-install pattern consistent with existing factory scripts
- Performance trade-offs are addressed (`--changed-only` for fast feedback, `--full` for gates)

✅ Design aligns with existing architecture:

- Extends UC-07's `block-dangerous-git.sh` mechanism (BR-024)
- Uses FSM entry_conditions pattern (script_exit_zero, once T-03 is implemented)
- Follows factory's "deterministic validation" principle from foundational-principles.md

### 2.6 Necessary (YAGNI)

✅ No gold-plating detected:

- Every element traces back to AG-09 ("Run project tests deterministically via unavoidable hooks")
- The three integration points (pre-commit, pre-push, phase advance) each serve distinct stakeholder interests:
  - Pre-commit: fast feedback for iterative development
  - Pre-push: full regression check before sharing work
  - Phase advance: quality gate at phase boundaries
- Framework detection covers the four major ecosystems (Python/pytest, JavaScript/jest, Go, Rust/cargo) — appropriate scope for an agent factory targeting those languages
- Agent blocking (BR-024) is justified by the "never trust agents to self-validate" principle

### 2.7 Terminology

✅ Terminology is consistent and precise:

- "Hook" used consistently for mechanical triggers (pre-commit, pre-push, PreToolUse)
- "Framework detection" clearly means auto-identifying pytest/jest/go test/cargo test from project structure
- "Changed-only" vs "full" modes are distinct and well-defined
- "Exit code" semantics (0/1/2) follow Unix conventions
- No domain model document exists (CONTEXT.md missing), but terminology is consistent with existing use cases (UC-01..UC-08) and PRD

______________________________________________________________________

## 3. Deterministic Findings Summary

All 5 info-severity findings from spec-lint are **dismissed** as irrelevant to this review:

| ID      | Severity | Description                               | Assessment                                                                                                                                                                     |
| ------- | -------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| FMT001  | info     | Possible non-EARS requirement (heuristic) | False positive — validation-rules.md uses descriptive format consistent with existing BRs (BR-005, BR-006, etc.). EARS format is not required for business rules in this spec. |
| FMT001  | info     | Possible non-EARS requirement (heuristic) | Same as above                                                                                                                                                                  |
| FMT001  | info     | Possible non-EARS requirement (heuristic) | Same as above                                                                                                                                                                  |
| FMT001  | info     | Possible non-EARS requirement (heuristic) | Same as above                                                                                                                                                                  |
| TODO001 | info     | 5 unresolved todo items remain            | Expected — T-03 is the relevant todo for this review, acknowledged in SPEC-001                                                                                                 |

______________________________________________________________________

## 4. Semantic Findings

| ID       | Severity | Characteristic | Summary                                                                        |
| -------- | -------- | -------------- | ------------------------------------------------------------------------------ |
| SPEC-001 | Major    | Consistent     | UC-09 assumes script_exit_zero is implemented, conflicts with T-03 stub status |
| SPEC-002 | Minor    | Consistent     | UC-07 business rules do not acknowledge test command blocking added by BR-024  |

**Finding details**: See docs/findings/SPEC-001-script-exit-zero-inconsistency.md and docs/findings/SPEC-002-uc07-missing-test-command-reference.md

______________________________________________________________________

## 5. Traceability Summary

**Graph completeness** (from docs/spec/traceability.json):

✅ UC-09 realizes AG-09
✅ UC-09 references BR-023, BR-024, BR-025, BR-026, BR-027
✅ AG-09 is listed in actor_goals
✅ UC-09 is listed in use_cases
✅ All five new business rules (BR-023..BR-027) are in business_rules

**Orphan check**:

✅ No orphaned business rules: all BR-023..BR-027 are referenced by UC-09
✅ No orphaned use cases: UC-09 is referenced from actor-goal-list.md and prd.md
✅ No orphaned actor goals: AG-09 is referenced from UC-09

**Gap check**:

✅ G9 (PRD) → AG-09 (actor-goal-list) → UC-09 (use case) — complete chain
✅ FR-I1..FR-I6 (PRD) → UC-09 sections — all functional requirements traceable

______________________________________________________________________

## 6. Format Compliance

✅ **UC-09 follows Cockburn use case format**:

- ✅ Primary Actor identified
- ✅ Stakeholders & Interests section present
- ✅ Trigger specified
- ✅ Preconditions listed
- ✅ Main Success Scenario (8 steps)
- ✅ Extensions cover failure paths (2a, 3a, 5a, 1a, 1b, 1c)
- ✅ Postconditions (Success Guarantee and Minimal Guarantee)
- ✅ Business Rules section references BR-023..BR-027
- ✅ Activity Diagram present (Mermaid flowchart)
- ✅ Acceptance Criteria in Gherkin format (6 scenarios)
- ✅ "Referenced from" section lists actor-goal-list.md, prd.md, and proposal doc

✅ **Supplementary specs formatting**:

- BR-023..BR-027 use descriptive format consistent with existing business rules
- Format is appropriate for retroactive specification (PRD status: "Documented (retroactive)")

______________________________________________________________________

## 7. Conflicts with Existing Use Cases

✅ **No conflicts detected** between UC-09 and UC-01..UC-08:

- UC-09 extends UC-07 via BR-024 (adds test commands to block-dangerous-git.sh deny list)
  - This is an additive change, not a conflict
  - SPEC-002 filed to make this extension explicit in UC-07
- UC-09 reuses UC-01's entry_conditions pattern (script_exit_zero for phase advance)
  - Consistent with existing FSM gate condition model
  - SPEC-001 filed to acknowledge T-03 implementation dependency
- UC-09's hook integration does not overlap with UC-02 (transition-lint), UC-06 (index-lint), or UC-08 (init-factory)

______________________________________________________________________

## 8. Review Criteria Assessment

Per the user's requested review criteria:

1. **Consistency**: UC-09 realizes AG-09? ✅ Yes | FR-I requirements trace to G9? ✅ Yes | **Issue**: SPEC-001 (script_exit_zero inconsistency)
2. **Completeness**: All three hook integration points covered? ✅ Yes (pre-commit, pre-push, phase advance)
3. **Traceability**: BR-023..BR-027 referenced correctly? ✅ Yes (all five are in UC-09 and validation-rules.md)
4. **Format**: UC-09 follows Cockburn format? ✅ Yes | Activity diagram present? ✅ Yes
5. **Conflicts**: UC-09 conflicts with UC-01..UC-08? ✅ No conflicts | **Issue**: SPEC-002 (UC-07 should acknowledge extension)
6. **EARS compliance**: Supplementary spec requirements in EARS format? ✅ N/A — descriptive format is consistent with existing BRs

______________________________________________________________________

## 9. Conclusion

**Spec review found 2 open findings (1 Major, 1 Minor).**

The test execution hooks specification extension is **well-structured and mostly consistent**, with strong traceability and comprehensive Gherkin acceptance criteria. The specification follows Cockburn use case format correctly and integrates cleanly with the existing Factory Flow Control spec.

**Two defects must be addressed:**

1. **SPEC-001 (Major)**: UC-09 assumes phase advance invokes run-tests via script_exit_zero, but this condition type is stubbed (T-03). The spec should explicitly acknowledge this implementation dependency.

2. **SPEC-002 (Minor)**: UC-07's business rules should acknowledge that BR-024 extends block-dangerous-git.sh with test command blocking, providing a forward reference to UC-09.

**Recommended action**: Address SPEC-001 before implementation begins — either update UC-09 to clarify implementation status, or implement T-03 concurrently with the test hooks. SPEC-002 is a documentation hygiene issue that can be addressed at any time.

______________________________________________________________________

## 10. Sign-off

Review completed per [factory/rulebooks/conventions/report-format.md](../../factory/rulebooks/conventions/report-format.md).

Findings filed per [factory/rulebooks/conventions/finding-format.md](../../factory/rulebooks/conventions/finding-format.md).

**Next step**: Hand off to Requirements Agent to address open findings (SPEC-001, SPEC-002).
