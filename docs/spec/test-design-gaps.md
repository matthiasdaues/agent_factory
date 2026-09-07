# Gaps Report: test-design

Generated: 2026-09-01
Source: docs/proposals/test-design-skill.md

## Actor-Goal Matrix

| Actor           | Goal                                                                 | Rule                                                                           | Status    |
| --------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------ | --------- |
| Planning Agent  | Design test scenarios from .feature contracts before stories are cut | Rule: Planning Agent designs test scenarios from feature contracts             | specified |
| Planning Agent  | Guard on detect-test-regime prerequisite                             | Rule: Test-design skill guards on detect-test-regime prerequisite              | specified |
| Planning Agent  | Assign one test owner per contract across the backlog                | Rule: Test-design skill assigns one test owner per contract across the backlog | specified |
| Planning Agent  | Classify contracts by risk class to determine test treatment         | Rule: Test-design skill classifies contracts by risk class                     | specified |
| Planning Agent  | Propagate prior tests to non-owning stories                          | Rule: Test-design skill propagates prior tests to non-owning stories           | specified |
| Planning Agent  | Integrate test-design as optional step in create-backlog sequence    | Rule: Create-backlog sequence integrates test-design as optional step          | specified |
| Planning Agent  | Carry test-design sections from epics.md into story files            | Rule: Create-backlog-stories carries test-design sections into story files     | specified |
| Developer-Agent | Consume prescribed RED phase from test-design output                 | Rule: Developer-Agent consumes test-design as prescribed RED phase             | specified |
| Developer-Agent | Fall back to existing behavior without test-design                   | Rule: Developer-Agent falls back without test-design output                    | specified |
| User            | Configure risk classes per project in testing.yaml                   | Rule: User configures risk classes per project in testing.yaml                 | specified |
| User            | Configure gate thresholds centrally in testing.yaml                  | Rule: User configures gate thresholds in testing.yaml                          | specified |
| Dispatcher      | Read gate configuration from testing.yaml                            | Rule: Dispatcher reads gate configuration from testing.yaml                    | specified |
| Dispatcher      | Validate test-design completeness via gate script                    | Rule: Test-design-verify gate validates test-design completeness               | specified |
| Dispatcher      | Resolve CRAP threshold from testing.yaml gates section               | Rule: CRAP score reads threshold from testing.yaml gates section               | specified |

## Missing Rules

None. Every actor-goal pair has a corresponding Rule in the .feature file.

## Rules Without Scenarios

None. Every Rule has at least one Scenario.

## Ambiguous Wording

| Location                                                               | Step Text                                                                               | Issue                                                                                            | Suggested Fix                                                                                                                      |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| Scenario: Ownership assigned to the story that introduces the contract | "one story introduces the contract's infrastructure or first exercises it"              | "introduces" and "first exercises" may be ambiguous when multiple stories share a dependency     | Clarify: ownership goes to the story that appears first in dependency-sorted order among stories that trace the contract           |
| Scenario: Risk class resolved from convention defaults                 | "critical is assigned to contracts with atomicity, concurrency, or security invariants" | The classification criteria overlap; a contract with both CRUD and security aspects is ambiguous | The testing strategy should specify that security invariants elevate a contract to critical regardless of its CRUD characteristics |

## Completion Criteria Traceability

| CC # | Completion Criterion                                           | Traced To                                                                                                          |
| ---- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| 1    | test-design skill exists with procedure and prerequisite guard | Rule: Planning Agent designs test scenarios; Rule: Test-design skill guards on detect-test-regime prerequisite     |
| 2    | Testing strategy defines three risk classes                    | Rule: Testing strategy defines risk-class conventions                                                              |
| 3    | create-backlog includes test-design step                       | Rule: Create-backlog sequence integrates test-design as optional step                                              |
| 4    | create-backlog-write-epics surfaces option                     | Rule: Create-backlog sequence integrates test-design as optional step                                              |
| 5    | create-backlog-stories carries sections                        | Rule: Create-backlog-stories carries test-design sections into story files                                         |
| 6    | testing.yaml gates and risk_classes sections                   | Rule: User configures gate thresholds; Rule: User configures risk classes                                          |
| 7    | crap-score reads from testing.yaml                             | Rule: CRAP score reads threshold from testing.yaml gates section                                                   |
| 8    | test-design-verify gate exists                                 | Rule: Test-design-verify gate validates test-design completeness                                                   |
| 9    | developer-agent consumes test-design                           | Rule: Developer-Agent consumes test-design as prescribed RED phase                                                 |
| 10   | One test owner per contract                                    | Rule: Test-design skill assigns one test owner per contract across the backlog                                     |
| 11   | Non-owning stories have Prior Tests                            | Rule: Test-design skill propagates prior tests to non-owning stories                                               |
| 12   | Developer-Agent never invents when test-design exists          | Rule: Developer-Agent consumes test-design as prescribed RED phase (Scenario: Developer-Agent never invents tests) |
| 13   | Implementation-agent reads gates from yaml                     | Rule: Dispatcher reads gate configuration from testing.yaml                                                        |
| 14   | ADR-0012 documents test_design_verify                          | Rule: Dispatcher reads gate configuration from testing.yaml (Scenario: ADR-0012 documents test_design_verify)      |
| 15   | testing.yaml template has risk_classes example                 | Rule: User configures risk classes per project (Scenario: Template includes risk_classes schema)                   |
