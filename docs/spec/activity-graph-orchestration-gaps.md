# Gaps Report: Activity-Graph Orchestration

Generated: 2026-09-18
Source: docs/proposals/activity-graph-orchestration.md
Supersedes: docs/spec/cycle-based-orchestration-gaps.md

## Actor-Goal Matrix

| Actor                   | Goal                            | Rule                                                                  | Status    |
| ----------------------- | ------------------------------- | --------------------------------------------------------------------- | --------- |
| Human operator          | Navigate session menu           | Session menu presents four lanes                                      | specified |
| Human operator          | Access housekeeping             | Housekeeping shows factory state and offers maintenance actions       | specified |
| Human operator          | Start a workstream              | Human operator starts a new workstream                                | specified |
| Human operator          | Continue a workstream           | Human operator continues an existing workstream                       | specified |
| Human operator          | See precondition evidence       | Human operator sees all agents with precondition evidence             | specified |
| Human operator          | Select any agent                | Human operator selects any agent regardless of precondition status    | specified |
| Human operator          | Chain via external orchestrator | Chaining happens externally when deterministic fences pass            | specified |
| Human operator          | Fix upstream artifact           | Human operator fixes an upstream artifact without transition ceremony | specified |
| Human operator          | Rework without ceremony         | Rework requires no transition or state update                         | specified |
| Human operator          | Run intent select               | Intent select lists all agents with precondition status               | specified |
| Human operator          | Run intent assess               | Intent assess runs validators and reports results                     | specified |
| Human operator          | Complete a delivery sequence    | Single delivery sequence completes under the activity model           | specified |
| Agent definition author | Declare structured inputs       | Agent definition declares required and contextual inputs              | specified |
| Skill definition author | Declare contextual inputs       | Skill definition carries contextual inputs only                       | specified |
| Precondition evaluator  | Check inputs against repository | Precondition evaluator checks agent inputs against the repository     | specified |
| Precondition evaluator  | Resolve path patterns           | Precondition evaluator resolves path patterns with scope filtering    | specified |
| Precondition evaluator  | Fence agent outputs             | Every agent activity is fenced by a deterministic check               | specified |
| Artifact author         | Carry scope declaration         | Graph-addressable artifact carries a scope declaration                | specified |
| Workstream manager      | Maintain immutable state        | Workstream state file is immutable after creation                     | specified |
| Session manager         | Attach session to workstream    | Session binding attaches a session to a workstream                    | specified |
| Usage capture pipeline  | Retain structured transcripts   | Usage capture retains structured transcripts                          | specified |
| Factory installer       | Consolidate layout              | Factory content consolidates under .agent-factory/                    | specified |
| Factory maintainer      | Retire orchestrator             | Orchestrator package is retired                                       | specified |
| Factory maintainer      | Supersede cycle proposal        | Cycle-based orchestration proposal is superseded                      | specified |
| Compatibility verifier  | Preserve contracts              | Kept contracts preserve acceptance-commit behavior                    | specified |
| Research user           | Route via precondition graph    | Research brief uses the precondition graph for routing                | specified |

## Missing Rules

No actor-goal pair from the proposal is without a corresponding Rule.

## Rules Without Scenarios

No Rule is without at least one Scenario.

## Ambiguous Wording

| Location                                      | Step Text                                               | Issue                                        | Resolution                                                                                             |
| --------------------------------------------- | ------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Rule: Housekeeping / Scenario: Update Factory | "the factory relays the command output and exit status" | "output" is broad — stdout, stderr, or both? | Acceptable: init-factory is a known script with defined output. The scenario tests relay, not parsing. |
| Rule: Single delivery sequence                | "the human follows the precondition chain"              | "follows" is vague about mechanism           | Acceptable: this is an integration-level scenario verifying end-to-end flow, not a unit contract.      |

## Coverage Against Proposal Completion Criteria

| Completion Criterion                                        | Covering Rule(s)                                                  | Covered |
| ----------------------------------------------------------- | ----------------------------------------------------------------- | ------- |
| Session menu presents four lanes                            | Session menu presents four lanes                                  | yes     |
| capture-context --update --scan                             | Housekeeping shows factory state and offers maintenance actions   | yes     |
| Agent definitions carry structured inputs                   | Agent definition declares required and contextual inputs          | yes     |
| Precondition evaluator reports evidence                     | Precondition evaluator checks agent inputs against the repository | yes     |
| All agents presented with evidence after binding            | Human operator sees all agents with precondition evidence         | yes     |
| Workstream state files contain only identity fields         | Workstream state file is immutable after creation                 | yes     |
| Governed artifacts carry scope                              | Graph-addressable artifact carries a scope declaration            | yes     |
| Structured transcripts retained                             | Usage capture retains structured transcripts                      | yes     |
| Deterministic fencing of agent outputs                      | Every agent activity is fenced by a deterministic check           | yes     |
| Workstream state under .agent-factory/workstreams/          | Factory content consolidates under .agent-factory/                | yes     |
| Session bindings under .agent-factory/workstreams/sessions/ | Session binding attaches a session to a workstream                | yes     |
| intent select and intent assess                             | Intent select; Intent assess                                      | yes     |
| Deterministic checks under .agent-factory/checks/           | Factory content consolidates under .agent-factory/                | yes     |
| All factory content under .agent-factory/                   | Factory content consolidates under .agent-factory/                | yes     |
| packages/orchestrator retired                               | Orchestrator package is retired                                   | yes     |
| Cycle-based proposal superseded                             | Cycle-based orchestration proposal is superseded                  | yes     |
| Single delivery sequence completes                          | Single delivery sequence completes under the activity model       | yes     |
| Rework requires no transition                               | Rework requires no transition or state update                     | yes     |

## Deferred Items Not Covered

The following items from the proposal's "Explicitly deferred" list are intentionally absent from the feature file:

- Per-CLI activity extractors and common activity record format
- Git-diff-based change tracking for activity impact analysis
- Capture-time activity extraction
- Automated artifact-impact analysis
- structured-only transcript retention mode
- Self-directed delegation beyond external chaining
- Batch identity tracking
- Replacing internal research routes
- Usage record enrichment (workstream_id, workstream_origin, skills_invoked)
