# Gaps Report: test-gate-presence

Generated: 2026-08-28
Source: docs/proposals/test-gate-presence-over-test-execution.md

## Actor-Goal Matrix

| Actor                         | Goal                                               | Rule                                                                        | Status    |
| ----------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------- | --------- |
| User                          | Declare project test commands via charter          | Rule: User declares project test commands via charter                       | specified |
| User, Orchestrator-as-Trigger | Resolve test command from charter for FSM gates    | Rule: FSM gate conditions resolve test command from charter                 | specified |
| CLI-Invoked Agent             | Run only charter-declared test commands            | Rule: Guardrail allowlists charter-declared test commands for agents        | specified |
| User                          | Ensure Factory injects no test hooks               | Rule: Factory does not inject test hooks into pre-commit config             | specified |
| User                          | Delete run-tests and mutation-analysis scripts     | Rule: Factory deletes run-tests and mutation-analysis scripts               | specified |
| User                          | Detect existing test entrypoints during onboarding | Rule: Detect-test-regime skill discovers test entrypoints during onboarding | specified |
| User, CLI-Invoked Agent       | Use two-gate dispatcher sequence                   | Rule: Dispatcher gate sequence reduces from three to two                    | specified |
| User                          | Mutation-analysis skill as setup guidance          | Rule: Mutation-analysis skill provides setup guidance                       | specified |
| User                          | Remove-factory leaves test infrastructure intact   | Rule: Remove-factory leaves project test infrastructure intact              | specified |
| User, Orchestrator-as-Trigger | Gate contract is exit-code-only                    | Rule: Gate contract is exit-code-only                                       | specified |
| User                          | Declare layer bindings for QA strategy grounding   | Rule: Charter declares layer bindings for QA strategy grounding             | specified |
| CLI-Invoked Agent             | Ground contract-owner assignments in charter       | Rule: QA strategy grounds contract-owner assignments in charter             | specified |
| CLI-Invoked Agent             | Feed back test-harness mismatches                  | Rule: Developer-agent feeds back test-harness mismatches                    | specified |
| CLI-Invoked Agent             | Classify mutation survivors by contract ownership  | Rule: Mutation-analysis skill classifies survivors by contract ownership    | specified |

## Missing Rules

No actor-goal pairs are missing a corresponding Rule.

## Rules Without Scenarios

No Rules are missing Scenarios.

## Ambiguous Wording

| Location                                               | Step Text                                                | Issue                                                      | Suggested Fix                                                                                                                                                             |
| ------------------------------------------------------ | -------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rule: Detect-test-regime, Scenario: No test entrypoint | "offers to help build project-owned test infrastructure" | "help build" is vague — unclear what Factory actually does | Specify: "surfaces the gap and records an empty testing.yaml with a TODO comment" or defer to the full kit-manager onboarding interview (explicitly deferred in proposal) |

## Specification Update Coverage

All seven documents listed in the proposal's Design section 9 have been updated:

| Document               | Update                                                                      |
| ---------------------- | --------------------------------------------------------------------------- |
| UC-09                  | Rewritten for project-owned testing via charter declaration                 |
| ADR-0003               | Amended with project-owned testing rationale and what changes/stays         |
| prd.md                 | G9 and FR-I (FR-I1 through FR-I6) revised for charter-declared testing      |
| UC-10                  | Acceptance criteria updated for charter-declared allowlist                  |
| interface-contracts.md | Guardrail binding updated for charter-declared commands                     |
| validation-rules.md    | BR-023 through BR-029 rewritten for charter-declared, project-owned testing |
| ADR-0012               | Amended: three-gate sequence becomes two-gate sequence                      |

## Scope Map

The scope map at `docs/spec/scope-map.md` exists on `dev` as an untracked file for a different feature (newcomer-onboarding). Creating a scope map in this branch would create a merge conflict. The scope map should be updated after this branch merges, adding the Rules from `test-gate-presence.feature` as `specified` entries.

## Remaining Gaps

1. **T-06 reference**: The monorepo multi-framework limitation (T-06) referenced in the old BR-023 is no longer relevant because Factory no longer detects frameworks. The todo entry may need updating or closing.
2. **Detect-test-regime skill document**: The `detect-test-regime` skill does not yet exist at `factory/skills/detect-test-regime/SKILL.md`. It is listed in the proposal scope as a new artifact to create during implementation.
3. **Charter template**: The `factory/rulebooks/templates/charter-testing.yaml` template does not yet exist. It is listed in the proposal scope as a new artifact to create during implementation.
4. **Init-factory wiring**: The wiring of `detect-test-regime` into `init-factory` is an implementation concern, not a specification gap, but the proposal scope note (PROP-09) asks for clarity on whether it is part of skill creation or a separate story.
5. **qa-strategy-from-spec update**: The skill at `factory/skills/qa-strategy-from-spec/SKILL.md` needs two new inputs (charter layer bindings, repo scan) and a changed Step 3 assignment policy. This is an implementation artifact to create during implementation (Design sections 10–11).
6. **Developer-agent workflow update**: The agent at `factory/agents/developer-agent.md` needs an explicit harness-mismatch check after writing tests. This is an implementation artifact to create during implementation (Design section 12).
7. **Mutation-analysis skill rewrite**: The skill at `factory/skills/mutation-analysis/SKILL.md` needs both setup guidance and contract-ownership classification sections. This is an implementation artifact to create during implementation (Design section 13).
8. **Kit-manager layer-bindings population**: The agent at `factory/agents/kit-manager.md` needs a charter completeness sweep that populates layer bindings from repo scan. This is an implementation artifact to create during implementation (Design section 10).
