# Gaps Report: newcomer-onboarding

Generated: 2026-08-28
Source: docs/proposals/newcomer-onboarding-and-incremental-brownfield.md

## Actor-Goal Matrix

| Actor                    | Goal                                                            | Rule                                                                               | Status    |
| ------------------------ | --------------------------------------------------------------- | ---------------------------------------------------------------------------------- | --------- |
| Newcomer                 | Walk through a guided tour before choosing a workflow           | Rule: Newcomer walks through a guided tour before choosing a workflow              | specified |
| Returning User           | Reorient mid-session via guided-tour skill                      | Rule: User reorients mid-session via the guided-tour skill                         | specified |
| Newcomer, Returning User | See a four-option session entrypoint                            | Rule: Session entrypoint presents four options including newcomer path             | specified |
| Newcomer, Returning User | Have in-session agents adopted, not spawned                     | Rule: In-session agents are adopted, not spawned as subagents                      | specified |
| Brownfield User          | Get a working baseline from three anchor files                  | Rule: Brownfield onboarding exits after three anchor files                         | specified |
| Brownfield User          | Populate scope map from forensic evidence                       | Rule: Reverse-map skill populates scope map from forensic evidence                 | specified |
| Feature Developer        | Deepen anchor files incrementally through feature work          | Rule: Feature-addition deepens anchor files incrementally                          | specified |
| Feature Developer        | Start feature work with anchor file presence, not a gate marker | Rule: Feature-addition prerequisite checks anchor file presence, not a gate marker | specified |

## Missing Rules

None. Every actor-goal pair from the proposal has a corresponding Rule.

## Rules Without Scenarios

None. Every Rule has at least one Scenario.

## Ambiguous Wording

| Location                                                           | Step Text                                    | Issue                                                                                    | Suggested Fix                                                                                                                                         |
| ------------------------------------------------------------------ | -------------------------------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rule: Reverse-map, Scenario: sweeps tests first                    | "matches test names to behavioral claims"    | What constitutes a "behavioral claim" is undefined                                       | Define in the reverse-map SKILL.md: a behavioral claim is one test function asserting one observable outcome                                          |
| Rule: Feature-addition deepens, Scenario: updates architecture.dsl | "changes the structural shape of the system" | "structural shape" is informal — when does a change qualify?                             | Define: a structural change adds, removes, or renames a container or component in architecture.dsl                                                    |
| Rule: Reverse-map, Scenario: presents results in batches           | "grouped by domain area"                     | How are domain-area boundaries determined? Code modules, directories, business concepts? | Define in the reverse-map SKILL.md: the skill infers domain areas from top-level module/package boundaries and confirms grouping with the stakeholder |

## Boundary Coverage

| Boundary file                               | Touched by Rule                                 | @-reference                                       |
| ------------------------------------------- | ----------------------------------------------- | ------------------------------------------------- |
| docs/arc42/beginner-intro.md                | Guided tour                                     | @docs/arc42/beginner-intro.md                     |
| factory/playbooks/brownfield-onboarding.md  | Brownfield exits after three anchor files       | @factory/playbooks/brownfield-onboarding.md       |
| factory/playbooks/feature-addition.md       | Feature-addition deepens; prerequisite checks   | @factory/playbooks/feature-addition.md            |
| factory/agents/chat-agent.md                | In-session agents adopted                       | @factory/agents/chat-agent.md                     |
| factory/agents/kit-manager.md               | In-session agents adopted                       | @factory/agents/kit-manager.md                    |
| factory/agents/coaching-agent.md            | In-session agents adopted                       | @factory/agents/coaching-agent.md                 |
| factory/config/AGENTS.md                    | Session entrypoint; guided tour                 | @factory/config/AGENTS.md                         |
| factory/playbooks/greenfield-development.md | Coaching-agent adoption (greenfield retro step) | Not directly specified — covered by adopt pattern |
| factory/skills/reverse-map/SKILL.md         | Reverse-map skill                               | new artifact (no @-reference)                     |
| factory/skills/guided-tour/SKILL.md         | Guided-tour skill                               | new artifact (no @-reference)                     |

## New Artifacts Required

| Artifact                            | Created by                     |
| ----------------------------------- | ------------------------------ |
| factory/skills/reverse-map/SKILL.md | This feature (Design §4)       |
| factory/skills/guided-tour/SKILL.md | This feature (OQ-1 resolution) |

## Notes

1. The `greenfield-development.md` playbook invokes the coaching-agent for retrospectives. The adopt pattern applies there too but is covered by the general Rule rather than a separate Scenario, since the mechanism is identical.
2. The three ambiguous wordings flagged above are design-level terms that need precise definitions in the implementing skill files. They do not block specification but should be resolved before planning.
3. **Spec refinement from proposal:** the proposal (Design Section 3) says `docs/CONTEXT.md` is seeded "during the same code-reading pass that builds the DSL" (architecture-agent's work). The spec assigns seeding to the `reverse-map` skill instead, because reverse-map is already scanning code and extracting vocabulary during Stage 1. This is accepted as a refinement — reverse-map is the natural owner of vocabulary extraction since it performs the forensic code sweep.
