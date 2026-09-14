# Gaps Report: Cycle-Based Orchestration

Generated: 2026-09-14
Source: docs/proposals/cycle-based-orchestration.md

## Actor-Goal Matrix

| Actor                  | Goal                                          | Rule                                                                       | Status    |
| ---------------------- | --------------------------------------------- | -------------------------------------------------------------------------- | --------- |
| Human operator         | Start a new workstream                        | Rule: Human operator starts a new workstream                               | specified |
| Human operator         | Continue an existing workstream               | Rule: Human operator continues an existing workstream                      | specified |
| Human operator         | Switch workstreams mid-session                | Rule: Human operator switches workstreams mid-session                      | specified |
| Human operator         | Select the next cycle                         | Rule: Human operator selects the next cycle                                | specified |
| Human operator         | Delegate a route sequence                     | Rule: Human operator delegates a route sequence                            | specified |
| Human operator         | Delegate through a destination                | Rule: Human operator delegates through a destination                       | specified |
| Cycle engine           | Load and validate the delivery model          | Rule: Engine loads and validates the delivery model                        | specified |
| Cycle engine           | Evaluate artifact readiness                   | Rule: Engine evaluates artifact readiness for route recommendations        | specified |
| Cycle engine           | Recommend routes from evidence                | Rule: Engine recommends routes based on artifact evidence                  | specified |
| Cycle engine           | Enforce delegated retry limits                | Rule: Engine enforces delegated retry limits                               | specified |
| State adapter          | Transition workstream state atomically        | Rule: Adapter transitions workstream state atomically                      | specified |
| State adapter          | Handle concurrent workstream access           | Rule: Adapter handles concurrent workstream access                         | specified |
| Transition recommender | Run reconciliation at cycle boundaries        | Rule: Reconciliation runs when a cycle changes code or canonical artifacts | specified |
| Usage system           | Carry workstream context in records           | Rule: Usage records carry workstream and cycle context                     | specified |
| Usage analyst          | Query by workstream and cycle dimensions      | Rule: Usage analyst queries by workstream and cycle dimensions             | specified |
| Brownfield operator    | Bootstrap canonical concept model             | Rule: Brownfield operator bootstraps the canonical concept model           | specified |
| Research user          | Create delivery-linked brief                  | Rule: Delivery cycle creates a linked research brief                       | specified |
| Agent maintainer       | Replace phase ordinals with cycle eligibility | Rule: Agent definitions carry cycle eligibility instead of phase ordinals  | specified |
| run-step skill         | Execute cycle steps                           | Rule: run-step executes cycle steps instead of playbook steps              | specified |
| phase command          | Exit as diagnostic stub                       | Rule: phase command exits as a diagnostic stub                             | specified |
| transition-lint        | Validate cycle models and state files         | Rule: transition-lint validates cycle models and state files               | specified |
| Compatibility verifier | Preserve acceptance-commit contracts          | Rule: Kept contracts preserve acceptance-commit behavior                   | specified |
| Entity modeler         | Define canonical domain source in LinkML      | Rule: LinkML entity model serves as canonical domain source                | specified |

## Missing Rules

No actor-goal pair from the proposal is missing a corresponding Rule. The following scope items are covered implicitly rather than as standalone Rules:

1. **Individual artifact validators** (13 artifact types in the readiness table) — The proposal defines each artifact type's required inventory and evidence. The feature file covers the general validator contract. Individual validator behavior is an implementation concern tracked through the verification contract, not a separate user goal.

2. **Session binding lifecycle** — Session binding creation and update are covered within the workstream Rules. No separate actor has "manage session bindings" as a satisfying goal.

3. **CONCEPT internal sequence** — Per design decision Q1, the internal ordering within CONCEPT is agent-owned, not engine-modeled. The engine sees CONCEPT as one cycle.

## Rules Without Scenarios

None. Every Rule has at least one Scenario.

## Ambiguous Wording

| Location                                                          | Step Text                                             | Issue                                                              | Suggested Fix                                                                                       |
| ----------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| Rule: Human operator switches workstreams mid-session, Scenario 1 | "When the human begins work on a different objective" | "different objective" is subjective — the factory must detect this | Clarify detection criteria: explicit topic change, new proposal reference, or different deliverable |
| Rule: Engine evaluates artifact readiness, Scenario 3             | "changed files under src/"                            | "src/" assumes a specific directory structure                      | Use "changed source code files" or define the detection scope in the engine configuration           |

## Explicitly Deferred (from proposal)

These items are explicitly deferred in the proposal and do not appear as Rules:

1. **Automated semantic ranking among downstream routes.** The first release uses mechanical evidence for recommendations. The human selects when multiple routes have support.
2. **Removing playbook files.** Playbook FSM files remain as reference documentation. They lose runtime authority.
3. **Self-directed routing beyond human-authored delegation grants.** The engine does not infer, create, extend, or broaden grants.
4. **Batch identity tracking across refinement-realization-reconciliation loops.** Required for multi-batch delivery but deferred to a follow-up.
5. **Replacing internal survey and falsification routes.** Research keeps its current routes in the first release.
