# scope: global
Feature: Core artifact ownership

  Every core artifact and every seam file has exactly one producer, the agent
  that writes it, and a declared review in a separate session. The producer
  names its reviewers in the reviewed_by: field of its output declaration.
  The core splits into three families: the requirements agent owns scope and
  behaviour, the domain-modeling agent owns domain structure, and the
  architecture agent owns the architecture. The test-strategy agent owns the
  test practice family, and Virgil owns docs/agent-context.md. An agent that
  reads a file it does not own reports the problem to the owner and leaves
  the file alone.

  The list of core and seam artifacts is
  packages/factory/rulebooks/core-artifacts.yaml. A sample path of an entry
  is one concrete path that the entry's path pattern matches, such as
  docs/spec/entity-model.md or docs/spec/features/example.feature.

  Proposal trace: docs/proposals/core-artifact-ownership.md

  Rule: Factory maintainer finds exactly one producer for every core and seam artifact
    # actor: Factory maintainer
    # rules: BR-056, BR-057, BR-058, BR-060
    # @packages/factory/scripts/index-lint::build_agents_data
    # @tests/factory/test_index_lint.py

    Scenario: The contract test passes when each listed artifact has one producer with a review
      Given core-artifacts.yaml lists docs/spec/entity-model.md in the family domain structure
      And only the domain-modeling agent declares docs/spec/entity-model.md as an output
      And that declaration carries reviewed_by: [spec-review-agent]
      When the factory maintainer runs the contract test
      Then the test passes for docs/spec/entity-model.md

    Scenario: An artifact that no agent declares fails the contract test
      Given core-artifacts.yaml lists docs/spec/dependency-rules.dsl
      And no agent declares an output pattern that matches docs/spec/dependency-rules.dsl
      When the factory maintainer runs the contract test
      Then the test fails and names docs/spec/dependency-rules.dsl as an artifact without a producer

    Scenario: An artifact with two producers fails the contract test
      Given the domain-modeling agent declares docs/spec/state-machines.md as an output
      And the reconciliation agent declares docs/spec/*.md as an output
      When the factory maintainer runs the contract test
      Then the test fails and names docs/spec/state-machines.md with both agents

    Scenario Outline: A producer declaration without a review fails the contract test
      Given the domain-modeling agent declares docs/spec/glossary.md as an output
      And the declaration carries <review field>
      When the factory maintainer runs the contract test
      Then the test fails and names docs/spec/glossary.md as an artifact without a review

      Examples:
        | review field    |
        | no reviewed_by: |
        | reviewed_by: [] |

    Scenario: A wording-only declaration does not count as a producer
      Given the lector agent declares docs/**/*.md with edits: wording
      And the domain-modeling agent declares docs/spec/glossary.md with reviewed_by: [spec-review-agent, stakeholder]
      When the factory maintainer runs the contract test
      Then the test counts one producer for docs/spec/glossary.md
      And the test passes for docs/spec/glossary.md

    Scenario: The contract test checks the seam files like the core files
      Given core-artifacts.yaml lists docs/testing.yaml and docs/agent-context.md in the family seam
      When the factory maintainer runs the contract test
      Then the test finds the test-strategy agent as the one producer of docs/testing.yaml
      And the test finds Virgil as the one producer of docs/agent-context.md
      And both declarations carry reviewed_by: [stakeholder]

    Scenario Outline: Each core and seam artifact has its declared producer and review
      Given the factory's agent definitions after this feature
      When the factory maintainer runs the contract test
      Then the one producer of <artifact> is <producer>
      And its declaration carries reviewed_by: <reviewers>

      Examples:
        | artifact                         | producer              | reviewers                        |
        | docs/spec/scope-map.md           | requirements-agent    | [stakeholder]                    |
        | docs/spec/features/*.feature     | requirements-agent    | [spec-review-agent]              |
        | docs/spec/areas/*.md             | requirements-agent    | [spec-review-agent]              |
        | docs/spec/glossary.md            | domain-modeling-agent | [spec-review-agent, stakeholder] |
        | docs/spec/entity-model.md        | domain-modeling-agent | [spec-review-agent]              |
        | docs/spec/state-machines.md      | domain-modeling-agent | [spec-review-agent]              |
        | docs/spec/validation-rules.md    | domain-modeling-agent | [spec-review-agent]              |
        | docs/spec/interface-contracts.md | domain-modeling-agent | [spec-review-agent]              |
        | docs/spec/schemas/*              | domain-modeling-agent | [spec-review-agent]              |
        | docs/spec/architecture.dsl       | architecture-agent    | [architecture-review-agent]      |
        | docs/spec/dependency-rules.dsl   | architecture-agent    | [architecture-review-agent]      |
        | docs/agent-context.md            | virgil                | [stakeholder]                    |
        | docs/testing.yaml                | test-strategy-agent   | [stakeholder]                    |

  Rule: Factory maintainer sees every declared review checked against the reviewer's inputs
    # actor: Factory maintainer
    # rules: BR-057, BR-059, BR-060
    # @packages/factory/scripts/index-lint::build_agents_data
    # @packages/factory/scripts/index-lint::_render_structured_field

    Scenario: index-lint carries reviewed_by and edits into INDEX.yaml
      Given the domain-modeling agent declares docs/spec/glossary.md with reviewed_by: [spec-review-agent, stakeholder]
      And the lector agent declares docs/**/*.md with edits: wording
      When the factory maintainer runs index-lint
      Then INDEX.yaml holds reviewed_by: [spec-review-agent, stakeholder] on the glossary declaration
      And INDEX.yaml holds edits: wording on the lector agent's declaration

    Scenario: A reviewer that declares the artifact as a context input passes
      Given the domain-modeling agent declares docs/spec/schemas/* with reviewed_by: [spec-review-agent]
      And the spec-review agent declares docs/spec/schemas/* as a context input
      When the factory maintainer runs index-lint --check
      Then index-lint reports no reviewer finding for docs/spec/schemas/*

    Scenario: The reviewer check matches patterns of different form by sample path
      Given the requirements agent declares docs/spec/features/{name}.feature with reviewed_by: [spec-review-agent]
      And the spec-review agent declares docs/spec/features/*.feature as a required input
      When the factory maintainer runs index-lint --check
      Then index-lint matches both patterns through the sample path docs/spec/features/example.feature
      And index-lint reports no reviewer finding for the feature files

    Scenario: A reviewer name that is no agent fails index-lint
      Given an output declaration carries reviewed_by: [spec-reviewer]
      And no agent named spec-reviewer exists
      When the factory maintainer runs index-lint --check
      Then index-lint fails and names spec-reviewer as an unknown reviewer

    Scenario: A reviewer that does not read the artifact fails index-lint
      Given the architecture agent declares docs/spec/dependency-rules.dsl with reviewed_by: [architecture-review-agent]
      And the architecture-review agent declares docs/spec/dependency-rules.dsl neither as a required nor as a context input
      When the factory maintainer runs index-lint --check
      Then index-lint fails and names the architecture-review agent and docs/spec/dependency-rules.dsl

    Scenario: The stakeholder needs no input declaration
      Given the requirements agent declares docs/spec/scope-map.md with reviewed_by: [stakeholder]
      When the factory maintainer runs index-lint --check
      Then index-lint reports no reviewer finding for docs/spec/scope-map.md

    Scenario: A reader is never counted as a review
      Given the QA agent declares docs/spec/features/{name}.feature as a required input
      And no output declaration names qa-agent in reviewed_by:
      When the factory maintainer runs the contract test
      Then the review of the feature files is the spec-review agent alone

    Scenario: The factory catalog is up to date after the change
      Given the factory's agent definitions after this feature
      When the factory maintainer runs index-lint --check
      Then index-lint exits 0

  Rule: Requirements agent keeps scope and behaviour only
    # actor: Requirements agent
    # @packages/factory/agents/requirements-agent.md

    Scenario: The requirements agent declares three core outputs and its working output
      Given the requirements agent definition after this feature
      When the factory maintainer reads its output declarations
      Then the core outputs are docs/spec/scope-map.md, docs/spec/features/*.feature, and docs/spec/areas/*.md
      And the other outputs are the gaps reports, docs/spec/work/term-candidates.md, the spec-feedback reports, and the reconciliation reports
      And no output declaration names a QA strategy, a structure file, or the glossary

    Scenario: The requirements agent hands QA strategy and agent context to their owners
      Given the requirements agent definition after this feature
      When the factory maintainer reads its skill list and its workflow
      Then the skill list contains neither qa-strategy-from-spec nor capture-context
      And the workflow has no step that writes the structure files or a QA strategy

    Scenario: The requirements agent writes an area spec where the stakeholder asks for depth
      Given an accepted proposal for a subsystem named billing
      And the stakeholder says that billing needs more depth than its feature files give
      When the requirements agent runs its area spec step
      Then the requirements agent writes docs/spec/areas/billing.md

    Scenario: The requirements agent hands off to the domain-modeling agent
      Given the requirements agent has written the scope map and a feature file
      When the requirements agent writes its handoff
      Then the handoff names the domain-modeling agent as the next producer

  Rule: Domain-modeling agent produces the domain structure family
    # actor: Domain-modeling agent
    # @packages/factory/skills/domain-modeling/SKILL.md

    Scenario: The domain-modeling agent definition declares the domain structure family
      Given packages/factory/agents/domain-modeling-agent.md
      When the factory maintainer reads its frontmatter
      Then the tier is strong
      And the required inputs are docs/spec/scope-map.md and docs/spec/features/*.feature
      And the context inputs are docs/spec/glossary.md, docs/spec/work/term-candidates.md, the source code, and docs/agent-context.md
      And the outputs are glossary.md, entity-model.md, state-machines.md, validation-rules.md, interface-contracts.md, and schemas/* under docs/spec/
      And glossary.md and entity-model.md are declared with required: true

    Scenario: The domain-modeling agent becomes eligible after the requirements agent
      Given a project with docs/spec/scope-map.md and no feature file
      When run-step evaluates the domain-modeling agent
      Then the domain-modeling agent is not eligible
      And the unmet reason names docs/spec/features/*.feature

    Scenario: The domain-modeling agent always writes the glossary and the entity model
      Given a project whose glossary holds no confirmed term
      When the domain-modeling agent runs
      Then docs/spec/glossary.md exists
      And docs/spec/entity-model.md exists

    Scenario: The domain-modeling agent writes the other structure files only when the domain needs them
      Given a domain with entities but no state machine, no rule, no contract, and no structured payload
      When the domain-modeling agent runs
      Then it writes no state-machines.md, no validation-rules.md, no interface-contracts.md, and no schemas/ folder

    Scenario: The domain-modeling agent writes a schema for a structured payload column
      Given the entity model has an entity Task with a payload column whose value has inner structure
      When the domain-modeling agent runs its schema step
      Then a file under docs/spec/schemas/ holds the structure of that payload column

    Scenario: The domain-modeling agent writes each state machine as pseudocode with a derived diagram
      Given the entity model gives the entity Task a lifecycle
      When the domain-modeling agent writes state-machines.md
      Then the Task state machine has a pseudocode block and a derived Mermaid diagram
      And statemachine-lint passes on docs/spec/state-machines.md

    Scenario Outline: The handoff names the architecture agent only after a change it must check
      Given the domain-modeling agent run <change>
      When the domain-modeling agent writes its handoff
      Then the handoff names the spec-review agent in a new session
      And the handoff <names architecture> the architecture agent for its component pass

      Examples:
        | change                                     | names architecture |
        | changed docs/spec/entity-model.md          | names              |
        | changed docs/spec/state-machines.md        | names              |
        | changed only docs/spec/validation-rules.md | does not name      |

    Scenario: The domain-modeling agent takes over existing structure files without a move
      Given an installed project whose docs/spec/entity-model.md the requirements agent wrote
      When the project updates to the release with this feature
      Then no file of docs/spec/ moves
      And the domain-modeling agent changes docs/spec/entity-model.md on its next run

  Rule: Stakeholder confirms every glossary term before it enters the glossary
    # actor: Stakeholder
    # rules: BR-065
    # @packages/factory/skills/domain-modeling/SKILL.md

    Scenario: The domain-modeling agent proposes a definition for each candidate
      Given docs/spec/work/term-candidates.md has the row Task, domain area Scheduling, status candidate
      When the domain-modeling agent runs
      Then the row Task has a proposed definition
      And the row Task has the status proposed

    Scenario: The stakeholder confirms the proposed definitions one domain area at a time
      Given term-candidates.md has proposed rows in the domain areas Scheduling and Billing
      When the domain-modeling agent reaches its pause point with the stakeholder
      Then it presents the proposed rows of Scheduling together
      And it presents the proposed rows of Billing only after the stakeholder has answered for Scheduling

    Scenario: A confirmed term moves into the glossary and leaves the work file
      Given the stakeholder confirms the proposed definition of Task in the domain area Scheduling
      When the domain-modeling agent records the answer
      Then docs/spec/glossary.md has a Term, Definition, and Avoid row for Task
      And docs/spec/work/term-candidates.md has no row for Task

    Scenario: A rejected definition stays in the work file with the stakeholder's note
      Given the stakeholder rejects the proposed definition of Slot because a Slot is not a time window
      When the domain-modeling agent records the answer
      Then the row Slot has the status rejected
      And its Note column gives the stakeholder's reason
      And docs/spec/glossary.md has no row for Slot

    Scenario: An unattended run leaves its proposals in the work file
      Given the domain-modeling agent runs without a stakeholder in the session
      When it has proposed a definition for Task
      Then the row Task keeps the status proposed
      And docs/spec/glossary.md has no row for Task

    Scenario: A term the stakeholder settled in another session moves without a second question
      Given term-candidates.md has the row Payout with status confirmed from a grilling session
      When the domain-modeling agent runs
      Then docs/spec/glossary.md has a row for Payout
      And the domain-modeling agent does not ask the stakeholder about Payout

    Scenario: Terms that the layout migration moved count as confirmed
      Given a project whose glossary terms migrate-spec-layout moved from chapter 12
      When the spec-review agent reviews the glossary
      Then it files no finding that a migrated term lacks the stakeholder's confirmation

  Rule: Agents other than the domain-modeling agent record terms as candidates
    # actor: CLI-Invoked Agent
    # rules: BR-065
    # @packages/factory/skills/reverse-map/SKILL.md
    # @packages/factory/skills/grilling/SKILL.md
    # @packages/factory/skills/reconcile-spec/SKILL.md

    Scenario: reverse-map writes the names it finds as term candidates
      Given a project in brownfield onboarding whose code has the class PaymentRun
      When reverse-map sweeps the tests and the code
      Then docs/spec/work/term-candidates.md has a row PaymentRun with status candidate
      And the Source column names the code path of PaymentRun
      And reverse-map writes no docs/spec/glossary.md

    Scenario Outline: A term settled by another agent becomes a confirmed row
      Given <agent> runs <skill>
      And the stakeholder settles the term Payout in that session
      When the skill records the term
      Then term-candidates.md has a row Payout with status confirmed
      And docs/spec/glossary.md is unchanged

      Examples:
        | agent              | skill                            |
        | requirements-agent | grilling in domain-modeling mode |
        | virgil             | grilling on a proposal           |
        | virgil             | domain-modeling                  |

    Scenario: reconcile-spec reports terminology drift as a report row
      Given the code calls an entity Payment and the glossary calls it Payout
      When reconcile-spec runs
      Then the reconciliation report has a row for docs/spec/glossary.md with the domain-modeling agent as owner
      And term-candidates.md is unchanged

  Rule: Architecture agent owns the components and their dependency rules
    # actor: Architecture agent
    # @packages/factory/agents/architecture-agent.md
    # @packages/factory/skills/maintain-architecture/SKILL.md

    Scenario: The architecture agent declares the dependency rules and its findings
      Given the architecture agent definition after this feature
      When the factory maintainer reads its frontmatter
      Then its outputs include docs/spec/dependency-rules.dsl with reviewed_by: [architecture-review-agent]
      And its outputs include docs/findings/ARCH-*.md
      And its outputs include no docs/spec/state-machines.md
      And its context inputs include docs/spec/entity-model.md and docs/spec/state-machines.md

    Scenario: The architecture agent builds the baseline before the domain structure exists
      Given a project with a feature file and no docs/spec/entity-model.md
      When run-step evaluates the architecture agent
      Then the architecture agent is eligible
      And its run skips the state machine check

    Scenario: A contradiction with the state machines becomes an ARCH finding
      Given docs/spec/state-machines.md lets a Task move from WAITING to DONE
      And the component view has no component that performs that move
      When the architecture agent runs Step 5 of maintain-architecture
      Then docs/findings/ has a new ARCH finding with owner: domain-modeling-agent
      And docs/spec/state-machines.md is unchanged

    Scenario: run-step does not restart the architecture agent by itself
      Given the architecture agent's outputs exist
      When the domain-modeling agent changes docs/spec/entity-model.md
      Then run-step counts the architecture agent's step as done
      And only the domain-modeling agent's handoff starts the component pass

    Scenario: The dependency-check report names the architecture agent as owner
      Given docs/spec/dependency-rules.dsl forbids imports from engine to cli
      And a module in engine imports a module in cli
      When dependency-check runs for story ST-0318
      Then the JSON report names the architecture agent as the owner of that violation
      # @packages/factory/scripts/dependency-check::write_report

  Rule: Spec-review agent reviews behaviour and domain structure
    # actor: Spec-review agent
    # @packages/factory/agents/spec-review-agent.md
    # @packages/factory/skills/inspect-spec/SKILL.md

    Scenario: The spec-review agent requires only the files that always exist
      Given the spec-review agent definition after this feature
      When the factory maintainer reads its inputs
      Then the required inputs are docs/spec/features/*.feature, docs/spec/scope-map.md, docs/spec/glossary.md, and docs/spec/entity-model.md
      And the context inputs include docs/spec/state-machines.md, docs/spec/validation-rules.md, docs/spec/interface-contracts.md, docs/spec/areas/*.md, docs/spec/schemas/*, and docs/spec/work/term-candidates.md

    Scenario: The spec review runs in a project without schemas or area specs
      Given a project with a feature file, the scope map, the glossary, and the entity model
      And the project has no docs/spec/schemas/ folder and no area spec
      When run-step evaluates the spec-review agent
      Then the spec-review agent is eligible

    Scenario Outline: inspect-spec checks each structure file and the glossary
      Given a project with <file>
      When inspect-spec runs
      Then inspect-spec runs its check for <file>

      Examples:
        | file                             |
        | docs/spec/entity-model.md        |
        | docs/spec/state-machines.md      |
        | docs/spec/validation-rules.md    |
        | docs/spec/interface-contracts.md |
        | docs/spec/glossary.md            |

    Scenario Outline: The glossary check finds the three kinds of term defect
      Given <defect>
      When inspect-spec reviews the glossary
      Then the spec review files a finding with owner: domain-modeling-agent

      Examples:
        | defect                                                                   |
        | the glossary defines Payout and Disbursement for the same concept        |
        | a feature file uses the term Slot and the glossary does not define it    |
        | a structure file uses the word Job, which the Avoid column of Task names |

    Scenario: A proposed term without confirmation becomes a spec-review finding
      Given term-candidates.md has the row Task with status proposed
      When the spec-review agent writes its report
      Then the report files a finding for the row Task with owner: domain-modeling-agent

    Scenario: The spec review reads the scope map and leaves its review to the stakeholder
      Given the spec-review agent runs
      When it reads docs/spec/scope-map.md
      Then it checks the feature files against the scope map
      And it does not record a review of the scope map

  Rule: Architecture-review agent reviews the dependency rules
    # actor: Architecture-review agent
    # @packages/factory/agents/architecture-review-agent.md
    # @packages/factory/skills/atam-review/SKILL.md

    Scenario: The architecture-review agent checks the rules against the component view
      Given docs/spec/dependency-rules.dsl allows imports from cli to engine
      And the component view of docs/spec/architecture.dsl has no relationship from cli to engine
      When the architecture-review agent runs
      Then its review files a finding that names the rule and the component view

    Scenario: The architecture review runs in a project without dependency rules
      Given a migrated project without docs/spec/dependency-rules.dsl
      When run-step evaluates the architecture-review agent
      Then the architecture-review agent is eligible
      And core-artifacts.yaml marks docs/spec/dependency-rules.dsl as an artifact a project may lack

  Rule: Test-strategy agent owns the test practice family
    # actor: Test-strategy agent
    # @packages/factory/skills/detect-test-regime/SKILL.md
    # @packages/factory/skills/qa-strategy-from-spec/SKILL.md

    Scenario: The test-strategy agent definition declares the test practice family
      Given packages/factory/agents/test-strategy-agent.md
      When the factory maintainer reads its frontmatter
      Then the tier is strong
      And the skills are detect-test-regime, qa-strategy-from-spec, crap-score, and mutation-testing
      And it declares no required input
      And its outputs include docs/testing.yaml with reviewed_by: [stakeholder] and docs/spec/work/*-qa-strategy.md
      And its outputs include docs/findings/QA-*.md

    Scenario: No other agent declares the test practice files
      Given the factory's agent definitions after this feature
      When the factory maintainer runs the contract test
      Then no agent other than the test-strategy agent declares docs/testing.yaml or docs/spec/work/*-qa-strategy.md as an output

    Scenario: The test-strategy agent writes testing.yaml in a project without a feature file
      Given a project with a test suite and no feature file
      When the test-strategy agent runs
      Then it proposes docs/testing.yaml from the scan of the test suites
      And it writes no QA strategy

    Scenario: The test-strategy agent writes a QA strategy only when its inputs exist
      Given a project with docs/spec/features/payments.feature and docs/spec/entity-model.md
      And the project has no docs/spec/interface-contracts.md
      When the test-strategy agent runs
      Then it writes no docs/spec/work/payments-qa-strategy.md
      And it names docs/spec/interface-contracts.md as the missing input

    Scenario: Every change to testing.yaml waits for the stakeholder
      Given the test-strategy agent proposes the CRAP threshold 30 in docs/testing.yaml
      When the stakeholder has not confirmed the change
      Then docs/testing.yaml keeps its earlier threshold

    Scenario: The test-strategy agent hands off to the planning agent
      Given the test-strategy agent has written docs/spec/work/payments-qa-strategy.md
      When it writes its handoff
      Then the handoff names the planning agent

    Scenario: Virgil gives up testing.yaml and the fitting names the test-strategy agent
      Given the Virgil definition after this feature
      When the factory maintainer reads its outputs and the fitting step 2b
      Then Virgil declares no docs/testing.yaml output
      And step 2b says that the session takes the test-strategy agent's role
      # @packages/factory/agents/virgil.md

    Scenario: The planning agent stops on a missing testing.yaml
      Given a project without docs/testing.yaml
      When the planning agent runs its pre-flight
      Then the pre-flight stops and names the test-strategy agent
      And the planning agent does not run detect-test-regime
      # @packages/factory/agents/planning-agent.md

    Scenario: The test-strategy agent declares the files its mutation setup writes
      Given docs/testing.yaml names the configuration files of the project's mutation tool
      When the test-strategy agent sets up mutation testing
      Then every file it writes for the setup matches one of its output declarations

  Rule: Implementation agent blocks a merge on a failing test guardrail
    # actor: Implementation agent
    # rules: BR-066
    # @packages/factory/agents/implementation-agent.md

    Scenario: A function above the CRAP threshold blocks the merge
      Given docs/testing.yaml sets gates.crap_score.threshold to 30
      And after ST-0318 crap-score reports the function plan_moves at 42
      When the implementation agent runs the gates in automated mode
      Then the merge of ST-0318 is blocked
      And the developer agent gets a fix iteration for plan_moves

    Scenario: The implementation agent runs the project's mutation command as a gate
      Given docs/testing.yaml enables mutation testing with gates.mutation_testing.command set
      When the implementation agent runs the gates after a story
      Then it runs crap-score, test-design-verify, dependency-check, and the command in gates.mutation_testing.command
      And a non-zero exit of any of them blocks the merge

    Scenario: An enabled mutation gate without a command fails and names its owner
      Given docs/testing.yaml enables mutation testing without gates.mutation_testing.command
      When the implementation agent runs the gates after a story
      Then the mutation gate fails
      And the failure names the test-strategy agent

    Scenario Outline: The gate list comes from the story first, then from testing.yaml, then from the default
      Given a story with <story field>
      And docs/testing.yaml <gates section>
      When the implementation agent picks the gates for the story
      Then it runs <gates run>

      Examples:
        | story field                 | gates section                               | gates run                                              |
        | quality-gates: [crap-score] | enables crap-score and mutation testing     | crap-score                                             |
        | no quality-gates field      | enables crap-score only                     | crap-score                                             |
        | no quality-gates field      | has no gates section                        | crap-score and dependency-check                        |
        | no quality-gates field      | has no gates section and a mutation command | crap-score, dependency-check, and the mutation command |

    Scenario: The developer agent runs the gates in manual mode
      Given the implementation agent runs in manual mode
      When the developer agent finishes a story
      Then the developer agent runs the same gates before it hands the story back
      # @packages/factory/agents/developer-agent.md

    Scenario: The developer agent resolves each surviving mutant before the merge
      Given mutation testing leaves three surviving mutants in the path-table planner after ST-0318
      When the developer agent handles them inside the coding loop
      Then each mutant ends as removed dead code, a new test, or a QA finding
      # @packages/factory/skills/mutation-testing/SKILL.md

  Rule: Test-strategy agent resolves the surviving mutants that a developer agent cannot resolve
    # actor: Test-strategy agent
    # @packages/factory/skills/mutation-testing/SKILL.md

    Scenario: mutation-testing files an unresolved mutant as a QA finding for the test-strategy agent
      Given the developer agent cannot resolve a surviving mutant in plan_moves
      When it files the mutant through the mutation-testing skill
      Then docs/findings/ has a new QA finding with owner: test-strategy-agent

    Scenario: The implementation agent dispatches the test-strategy agent for each open QA finding
      Given ST-0318 has merged and QA-0003 is open
      When the implementation agent handles the merged story
      Then it dispatches the test-strategy agent for QA-0003

    Scenario Outline: The test-strategy agent resolves a QA finding in one of two ways
      Given the test-strategy agent works on QA-0003
      When it decides that <decision>
      Then it <action>
      And it sets the status of QA-0003

      Examples:
        | decision                                     | action                                              |
        | the contract has the wrong owning test layer | changes the contract-owner table of the QA strategy |
        | a test is missing                            | records in QA-0003 which test is missing            |

    Scenario: The planning agent reads QA findings to add a missing test to a story
      Given QA-0003 records that a contract test for plan_moves is missing
      When the planning agent cuts the next stories
      Then it reads docs/findings/QA-0003.md as a context input
      # @packages/factory/agents/planning-agent.md

  Rule: Developer agent reports specification drift without editing the specification
    # actor: Developer agent
    # @packages/factory/agents/developer-agent.md
    # @packages/factory/skills/spec-feedback/SKILL.md

    Scenario: The developer and implementation agents declare no specification output
      Given the developer agent and implementation agent definitions after this feature
      When the factory maintainer reads their outputs
      Then neither declares docs/spec/**/*.md
      And the developer agent declares docs/spec/work/spec-feedback-*.md

    Scenario: Drift becomes a row of the story's spec-feedback report
      Given the developer agent implements ST-0318
      And the migration script must refuse a repository with uncommitted changes
      And docs/spec/validation-rules.md has no such rule
      When spec-feedback Step 2 runs
      Then docs/spec/work/spec-feedback-ST-0318.md has a row for validation-rules.md
      And the row names the drift, its evidence in the code, the domain-modeling agent as owner, and the status open
      And docs/spec/validation-rules.md is unchanged

    Scenario: Parallel developer agents write separate reports
      Given ST-0318 and ST-0319 run in the same wave
      When both developer agents find drift
      Then the rows of ST-0318 are in spec-feedback-ST-0318.md
      And the rows of ST-0319 are in spec-feedback-ST-0319.md

    Scenario: A test harness that cannot test a contract becomes a row for the test-strategy agent
      Given the QA strategy prescribes an integration test for a contract
      And the project has no fixture for that integration test
      When the developer agent runs its harness-mismatch check
      Then the story's spec-feedback report has a row for the QA strategy with the test-strategy agent as owner

  Rule: Implementation agent closes a wave only after the owners have handled every drift row
    # actor: Implementation agent
    # rules: BR-061, BR-062, BR-063, BR-064
    # @packages/factory/scripts/dispatch_lib.py::Ledger.close_wave
    # @packages/factory/scripts/dispatch::cmd_close_wave
    # @packages/factory/rulebooks/conventions/dispatch-contract.md

    Scenario: After a merge the implementation agent dispatches each row's owner and then the reviewer
      Given ST-0318 has merged and its report has an open row for validation-rules.md owned by the domain-modeling agent
      When the implementation agent handles the merged story
      Then it dispatches the domain-modeling agent for the row
      And after the row is fixed it dispatches the spec-review agent for the row

    Scenario Outline: close-wave checks the status of each row in the wave's reports
      Given wave 2 holds ST-0318
      And spec-feedback-ST-0318.md has one row for <artifact> with status <status>
      When the implementation agent runs dispatch close-wave 2
      Then close-wave <result>

      Examples:
        | artifact                                    | status    | result                  |
        | docs/spec/validation-rules.md               | open      | fails and names the row |
        | docs/spec/validation-rules.md               | fixed     | fails and names the row |
        | docs/spec/validation-rules.md               | confirmed | passes                  |
        | docs/spec/work/payments-qa-strategy.md      | open      | fails and names the row |
        | docs/spec/work/payments-qa-strategy.md      | fixed     | passes                  |
        | docs/adr/0012-dispatcher-owned-gate-loop.md | fixed     | passes                  |
        | docs/spec/validation-rules.md               | rejected  | passes                  |

    Scenario: close-wave reads the core list to tell core rows from other rows
      Given core-artifacts.yaml lists docs/spec/validation-rules.md and does not list QA strategies
      When dispatch close-wave reads a fixed row
      Then it treats the row as blocking only when the row's artifact matches an entry of core-artifacts.yaml

    Scenario: A rejected row becomes a BUG finding against the code
      Given the spec-review agent finds that the code of ST-0318 breaks an accepted requirement
      When it rejects the row
      Then the row has the status rejected
      And the spec-review agent files a BUG finding with owner: developer-agent

    Scenario: The agent of a stakeholder session records the stakeholder's review
      Given a fixed row about docs/spec/scope-map.md, whose reviewer is the stakeholder
      When the requirements agent presents the fix to the stakeholder and the stakeholder rejects it
      Then the requirements agent sets the row to rejected
      And the requirements agent files the BUG finding

    Scenario: In manual mode the human closes a story only after its rows are handled
      Given the implementation agent runs in manual mode
      And spec-feedback-ST-0318.md has a fixed row for docs/spec/validation-rules.md
      When the human checks whether ST-0318 may close
      Then the dispatch contract's manual-mode section says the story stays open

  Rule: Reconciliation agent reports drift to each artifact's owner
    # actor: Reconciliation agent
    # rules: BR-061
    # @packages/factory/agents/reconciliation-agent.md
    # @packages/factory/skills/reconcile-spec/SKILL.md

    Scenario: The reconciliation agent declares one report and nothing else
      Given the reconciliation agent definition after this feature
      When the factory maintainer reads its frontmatter
      Then its only output is docs/reviews/reconciliation-*.md
      And its skill list does not contain capture-context

    Scenario: The code renames a status and the report names the state machine's owner
      Given the code renames the task status PENDING to WAITING
      And docs/spec/state-machines.md still says PENDING
      When the reconciliation agent runs on 2026-11-03
      Then docs/reviews/reconciliation-2026-11-03.md has a row for docs/spec/state-machines.md
      And the row names the mismatch, its evidence in the code, the domain-modeling agent as owner, and the status open
      And docs/spec/state-machines.md is unchanged

    Scenario Outline: Drift outside the specification goes to its owner as a row
      Given the code contradicts <artifact>
      When the reconciliation agent runs
      Then its report has a row for <artifact> with <owner> as owner
      And no file outside the report changes

      Examples:
        | artifact                                    | owner              |
        | docs/adr/0012-dispatcher-owned-gate-loop.md | architecture-agent |
        | docs/agent-context.md                       | virgil             |
        | docs/spec/features/payments.feature         | requirements-agent |

    Scenario: The next reconciliation run checks each fixed row
      Given the previous report has a fixed row for docs/spec/state-machines.md
      When the reconciliation agent runs again
      Then it checks the row's mismatch against the code

  Rule: Owner receives every finding about its artifact
    # actor: Factory maintainer
    # @packages/factory/rulebooks/conventions/finding-format.md
    # @packages/factory/rulebooks/templates/finding.md

    Scenario: The finding format defines the owner field and the new tags
      Given finding-format.md and templates/finding.md after this feature
      When the factory maintainer reads them
      Then the finding frontmatter has an owner: field
      And the tag table lists ARCH and QA
      And the tag table does not list RECON

    Scenario: The orchestrator routes an open finding to the agent in owner
      Given the spec-review agent files SPEC-0040 about docs/spec/state-machines.md with owner: domain-modeling-agent
      When the orchestrator loops over the open findings
      Then it sends SPEC-0040 to the domain-modeling agent
      And it does not send SPEC-0040 to the author of the reviewed phase

  Rule: Factory maintainer sees every writer of shared working output declare its path
    # actor: Factory maintainer

    Scenario Outline: Each writer of a shared working-output file declares its path
      Given the factory's agent definitions after this feature
      When the factory maintainer reads the output declarations of <agent>
      Then they include <path>

      Examples:
        | agent                     | path                              |
        | requirements-agent        | docs/spec/work/term-candidates.md |
        | virgil                    | docs/spec/work/term-candidates.md |
        | domain-modeling-agent     | docs/spec/work/term-candidates.md |
        | developer-agent           | docs/spec/work/spec-feedback-*.md |
        | requirements-agent        | docs/spec/work/spec-feedback-*.md |
        | domain-modeling-agent     | docs/spec/work/spec-feedback-*.md |
        | architecture-agent        | docs/spec/work/spec-feedback-*.md |
        | test-strategy-agent       | docs/spec/work/spec-feedback-*.md |
        | virgil                    | docs/spec/work/spec-feedback-*.md |
        | spec-review-agent         | docs/spec/work/spec-feedback-*.md |
        | architecture-review-agent | docs/spec/work/spec-feedback-*.md |
        | reconciliation-agent      | docs/reviews/reconciliation-*.md  |
        | requirements-agent        | docs/reviews/reconciliation-*.md  |
        | domain-modeling-agent     | docs/reviews/reconciliation-*.md  |
        | architecture-agent        | docs/reviews/reconciliation-*.md  |
        | test-strategy-agent       | docs/reviews/reconciliation-*.md  |
        | virgil                    | docs/reviews/reconciliation-*.md  |
        | spec-review-agent         | docs/reviews/reconciliation-*.md  |
        | architecture-review-agent | docs/reviews/reconciliation-*.md  |
        | spec-review-agent         | docs/findings/BUG-*.md            |
        | architecture-review-agent | docs/findings/BUG-*.md            |

    Scenario: The single-producer rule does not count working output
      Given several agents declare docs/spec/work/term-candidates.md
      When the factory maintainer runs the contract test
      Then the test reports no finding for docs/spec/work/term-candidates.md

  Rule: Human operator reaches the new owners through the playbooks and the routing
    # actor: Human operator
    # @packages/factory/INDEX.yaml
    # @packages/factory/scripts/intent

    Scenario Outline: A playbook names the new owner of a moved responsibility
      Given the playbook <playbook> after this feature
      When the human operator reads the step that produces <artifact>
      Then the step names <owner>

      Examples:
        | playbook               | artifact                     | owner                        |
        | feature-addition       | the structure files          | domain-modeling-agent        |
        | feature-addition       | the QA strategy              | test-strategy-agent          |
        | greenfield-development | the structure files          | domain-modeling-agent        |
        | greenfield-development | the QA strategy              | test-strategy-agent          |
        | brownfield-onboarding  | the glossary                 | domain-modeling-agent        |
        | brownfield-onboarding  | the entity model             | domain-modeling-agent        |
        | brownfield-onboarding  | the state machines           | domain-modeling-agent        |
        | documentation-update   | the fix of a stale core file | the owner in each report row |

    Scenario: intent routes the two new agents
      Given a project with the scope map and a feature file and no entity model
      When the human operator runs intent select
      Then the domain-modeling agent appears as an eligible agent

    Scenario: The declared inputs set the order of the producers
      Given a project with an accepted proposal and no specification
      When run-step evaluates the agents after each producer finishes
      Then the requirements agent becomes eligible first
      And the domain-modeling agent becomes eligible after the feature file exists
      And the spec-review agent becomes eligible after the glossary and the entity model exist
      # @packages/factory/skills/run-step/SKILL.md

    Scenario: The human operator chooses the order when two agents are eligible
      Given the spec review of payments still runs
      And docs/spec/features/payments.feature, docs/spec/entity-model.md, and docs/spec/interface-contracts.md exist
      When run-step evaluates the agents
      Then the test-strategy agent is eligible beside the spec-review agent
      And the human operator chooses which one runs first
