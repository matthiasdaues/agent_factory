# QA Strategy: newcomer-onboarding

Generated from:

- Feature spec: `docs/spec/newcomer-onboarding.feature`
- Entity model: `docs/spec/supplementary_specs/entity-model.md`
- Interface contracts: `docs/spec/supplementary_specs/interface-contracts.md`

## Feature

- Proposal trace: `docs/proposals/newcomer-onboarding-and-incremental-brownfield.md`
- Gherkin trace: `docs/spec/newcomer-onboarding.feature`
- Summary: This feature changes process artifacts (playbooks, agent definitions, CLI orientation, skill files) and introduces two new skills. The primary QA risk is behavioral regression in existing workflows: the session entrypoint must still route correctly, brownfield onboarding must still produce valid architecture artifacts, and feature-addition must still enforce its full pipeline when full spec artifacts are present. The secondary risk is that the adopt pattern breaks the stakeholder conversation by failing to fully assume an agent's boundaries.
- Rules in scope:
  - `Rule: Newcomer walks through a guided tour before choosing a workflow`
  - `Rule: User reorients mid-session via the guided-tour skill`
  - `Rule: Session entrypoint presents four options including newcomer path`
  - `Rule: In-session agents are adopted, not spawned as subagents`
  - `Rule: Brownfield onboarding exits after three anchor files`
  - `Rule: Reverse-map skill populates scope map from forensic evidence`
  - `Rule: Feature-addition deepens anchor files incrementally`
  - `Rule: Feature-addition prerequisite checks anchor file presence, not a gate marker`

## Test Layers in Scope

| Layer                 | Status     | Feature-specific scope                                                                                                                                      | Owned contracts                                        |
| --------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Deterministic linter  | strengthen | `index-lint --check` must pass after new skills are added to INDEX.yaml; `mdformat` must pass on all new and edited markdown files                          | INDEX.yaml consistency, markdown formatting            |
| Acceptance test       | add        | Manual walkthrough scenarios for each Rule — guided tour, adopt pattern, brownfield-lite exit, reverse-map interaction, feature-addition from lite baseline | All 8 Rules                                            |
| Contract test         | out        | No new CLI scripts or APIs; existing script contracts are unchanged                                                                                         | n/a                                                    |
| Integration test      | add        | Brownfield-lite → feature-addition pipeline: run brownfield Stage 1, exit, start feature-addition, verify it accepts the baseline                           | Anchor-file prerequisite, scope-map incremental update |
| End-to-end smoke test | out        | No runtime system; all artifacts are process documentation and skill files                                                                                  | n/a                                                    |

## Contract Owners

| Contract                            | Source scenario or gap                                                           | Owner layer                            | Failure mode                                                         | Test strategy note                                                                      |
| ----------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Session entrypoint four-option menu | `Scenario: Session entrypoint shows the four-option menu`                        | Acceptance test                        | Newcomer sees wrong options or old three-option menu                 | Verify AGENTS.md contains exact A/B/C/D text after implementation                       |
| Adopt pattern — no subagent spawned | `Scenario: Chat-agent is adopted in the current session`                         | Acceptance test                        | Subagent spawned instead of adopt, breaking stakeholder conversation | Manual test: select option D, verify direct conversation, no relay                      |
| Brownfield Stage 1 exit condition   | `Scenario: Stage 1 completes with three anchor files`                            | Acceptance test + deterministic linter | Missing anchor file not detected; user cannot start feature work     | Verify file-existence check in brownfield playbook prose; Structurizr validation on DSL |
| Anchor-file prerequisite            | `Scenario: Feature-addition detects brownfield-lite readiness from anchor files` | Acceptance test                        | Feature-addition blocks on missing full-spec artifacts               | Run feature-addition with only three anchor files; verify it proceeds                   |
| Reverse-map confidence hierarchy    | `Scenario: Reverse-map writes scope map with provenance`                         | Acceptance test                        | Wrong confidence level assigned; sources column empty                | Verify scope-map output against known test/code/doc sources                             |
| Guided-tour skill invocability      | `Scenario: User invokes guided-tour skill for orientation`                       | Acceptance test                        | Skill not found in INDEX.yaml; invocation fails                      | Verify INDEX.yaml lists guided-tour after implementation                                |
| Existing option B routing           | `Scenario: Existing option B content is preserved under new letter`              | Acceptance test                        | Existing playbook routing broken by menu renumbering                 | Verify each former option A sub-path routes identically under new option B              |

## Boundary Cases

| Boundary case                               | Source scenario or gap                                                 | Risk addressed                                    | Owner layer     | Notes                                                          |
| ------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------- | --------------- | -------------------------------------------------------------- |
| Newcomer with prior work (poc-spike exists) | `Scenario: Guided tour checks for prior work before starting`          | Tour repeats content user already knows           | Acceptance test | Check for charter, poc-spike output, prior playbook runs       |
| Zero anchor files present                   | `Scenario: Feature-addition reports missing anchor files`              | Feature-addition starts without baseline          | Acceptance test | All three missing — verify clear error message                 |
| Partial anchor files (1 or 2 of 3)          | `Scenario: Feature-addition reports missing anchor files`              | Ambiguous state — partial brownfield              | Acceptance test | Verify each missing file named individually                    |
| Brownfield with no tests                    | `Scenario: Reverse-map sweeps code entry points as secondary evidence` | Reverse-map fails if it expects tests             | Acceptance test | Verify fallback to entry-point scan with degraded confidence   |
| Adopt pattern for agent not in INDEX.yaml   | Gap: no scenario covers unresolvable agent path                        | Adopt fails silently with wrong behavior          | Acceptance test | Verify error message when INDEX.yaml path resolution fails     |
| Guided-tour invoked mid-playbook            | `Scenario: User invokes guided-tour skill for orientation`             | Skill disrupts active playbook state              | Acceptance test | Verify tour is read-only and does not modify playbook marker   |
| Greenfield playbook coaching-agent adoption | Gap: covered by general adopt pattern, no separate scenario            | Adopt pattern not applied to all invocation sites | Acceptance test | Verify greenfield-development.md retro step uses adopt wording |

## Defect Severity Triage

| Impact on this feature                                                                  | Severity          | Expected action                                                                  |
| --------------------------------------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------- |
| Existing playbook routing broken (option B sub-paths no longer reach correct playbooks) | blocking          | Stop release, fix before merge — this is a regression in core factory navigation |
| Adopt pattern spawns subagent instead of adopting (stakeholder conversation breaks)     | fix-in-same-story | Repair wording in AGENTS.md and playbook steps; retest                           |
| Brownfield Stage 1 exit message wording unclear or missing                              | fix-in-same-story | Edit brownfield-onboarding.md; retest with walkthrough                           |
| Reverse-map assigns wrong confidence level to a source type                             | defer             | File finding; confidence is informational, not gatekeeping                       |
| Guided-tour skill missing from INDEX.yaml after implementation                          | fix-in-same-story | Run `index-lint` to regenerate; verify skill appears                             |
| Beginner-intro uses undefined vocabulary before introduction                            | fix-in-same-story | Edit beginner-intro.md; retest with walkthrough                                  |

## Test Retention Policy

- Surviving owner per major contract: acceptance test (manual walkthrough) for all behavioral contracts; deterministic linter (`index-lint --check`, `mdformat`) for structural consistency
- Expected overlap to remove later: none anticipated — this feature introduces no code-level tests, only process artifacts and their deterministic lint
- Consolidation rule: keep one owner per contract per [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md)
- Deletion protocol: follow [testing-strategy.md § Delete overlapping tests safely](../../factory/rulebooks/conventions/testing-strategy.md)
