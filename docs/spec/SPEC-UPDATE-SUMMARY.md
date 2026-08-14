# Spec Update: Test Execution via Hooks

## Summary

Extended Factory Flow Control specification to add test execution via hooks as AG-09/UC-09.

**Design Principle**: Creation is agentic, validation is deterministic and MUST be triggered mechanically through unavoidable hooks.

## Files Updated

### 1. docs/spec/prd.md

- Added **G9** to Goals section: "Run project tests deterministically via unavoidable hooks (pre-commit, pre-push, phase advance), never via agent-commanded shell execution (`run-tests`)"
- Added **FR-I** section with 6 requirements (FR-I1 through FR-I6) covering:
  - Framework auto-detection (pytest, jest, go test, cargo test)
  - changed-only and full modes
  - Exit codes (0=pass, 1=fail, 2=error)
  - JSON summary output
  - Three hook integration points
  - Agent blocking via block-dangerous-git.sh

### 2. docs/spec/actor-goal-list.md

- Added **AG-09**: "Run project tests deterministically via unavoidable hooks, never via agent-commanded shell execution"
- Actor: Human Operator
- Level: User Goal

### 3. docs/spec/use_cases/UC-09-run-tests-via-hook.md (NEW)

- Realizes: AG-09
- Primary Actor: git / pre-commit (supporting actor)
- Three trigger points: pre-commit (changed-only), pre-push (full), phase advance (full)
- Main Success Scenario: detect framework → run tests → pass → allow operation
- Extensions:
  - No framework detected (exit 2)
  - Test framework config error (exit 2)
  - Tests fail (exit 1, block operation)
  - Agent attempts direct test execution (blocked by hook)
  - Human operator commit/push with failing tests (blocked)
- Business Rules: BR-023 through BR-027
- Activity Diagram in Mermaid
- 6 Gherkin acceptance criteria scenarios

### 4. docs/spec/supplementary_specs/validation-rules.md

- Added new section: **Test execution (run-tests, BR-023, BR-024, BR-025, BR-026, BR-027)**
- BR-023: Framework detection order and logic
- BR-024: Agent blocking patterns for test commands
- BR-025: changed-only fast filter behavior per framework
- BR-026: full mode complete suite requirements
- BR-027: JSON output format and stderr/stdout separation
- Added UC-09 to "Referenced from" section

## Traceability

```
PRD G9 → AG-09 → UC-09
           ↓
    BR-023..BR-027 (validation-rules.md)
           ↓
    FR-I1..FR-I6 (prd.md)
```

## Key Design Decisions

1. **Hook-triggered only**: Agents cannot run test commands; execution is mechanical via pre-commit/pre-push/phase-advance
2. **Three integration points**:
   - Pre-commit (fast, changed-only, bypassable)
   - Pre-push (full, unavoidable "ready to share" gate)
   - Phase advance (full, FSM entry condition)
3. **Framework detection**: Auto-detect from project structure (pyproject.toml, package.json, go.mod, Cargo.toml)
4. **Performance tiers**: Fast subset for commit, full suite for push/advance
5. **Agent prohibition**: Test commands added to block-dangerous-git.sh deny patterns

## Next Steps (Implementation)

Per docs/proposals/implemented/test-execution-via-hooks.md:

1. Create factory/scripts/run-tests with framework detection
2. Add pre-commit hook to factory/config/pre-commit-config.yaml
3. Add pre-push hook
4. Enable script_exit_zero in FSM (resolves T-03)
5. Add test command patterns to block-dangerous-git.sh

## Referenced Proposal

- docs/proposals/implemented/test-execution-via-hooks.md (implementation strategy)
