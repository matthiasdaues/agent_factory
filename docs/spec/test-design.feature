Feature: Test Design Skill

  The test-design skill designs test scenarios from .feature contracts and the
  scope map before stories are cut. It assigns one test owner per contract,
  classifies contracts by risk class, and writes concrete failure scenarios
  into backlog/epics.md. The developer-agent consumes this output as its
  prescribed RED phase instead of inventing its own tests.

  Proposal trace: docs/proposals/test-design-skill.md

  Rule: Planning Agent designs test scenarios from feature contracts
    # actor: Planning Agent
    # @factory/skills/test-design/SKILL.md

    Scenario: Test-design skill reads feature contracts and scope map
      Given backlog/epics.md exists with confirmed epic slicing
      And docs/spec/*.feature files declare behavioral contracts
      And docs/spec/scope-map.md maps contracts to architecture owners
      And docs/charter/testing.yaml contains testing_strategy and suites
      When the Planning Agent invokes the test-design skill
      Then the skill reads all trace IDs from each epic's building-block inventory
      And reads the corresponding .feature rules and scenarios
      And reads the scope-map architecture owner for each contract

    Scenario: Test-design skill writes failure scenarios for critical contracts
      Given a contract is classified as critical
      When the test-design skill writes failure scenarios
      Then each scenario uses Given/When/Then/Forbidden format
      And the Forbidden line names the specific failure mode the test catches
      And the scenarios appear in a Test Design section within the owning story's epics.md entry

    Scenario: Test-design skill writes concrete scenarios for standard contracts
      Given a contract is classified as standard
      When the test-design skill writes test scenarios
      Then each scenario has concrete expected inputs and assertions
      And the number of scenarios respects the admit-a-test budget
      And the budget allows one per equivalence class plus boundaries and distinct failure modes

    Scenario: Test-design skill emits no scenarios for structural contracts
      Given a contract is classified as structural
      When the test-design skill evaluates the contract
      Then it emits no failure scenarios
      And the contract remains owned by the deterministic linter layer

    Scenario: Test-design skill populates the tests key with owned modules
      Given the skill has assigned test ownership for a story
      When it writes the test-design output to epics.md
      Then the story's building-block entry gains a tests key listing only owned test modules

  Rule: Test-design skill guards on detect-test-regime prerequisite
    # actor: Planning Agent
    # @factory/skills/detect-test-regime/SKILL.md

    Scenario: Prerequisite met when testing_strategy is present
      Given docs/charter/testing.yaml contains a testing_strategy link
      And docs/charter/testing.yaml contains a suites section
      When the test-design skill checks prerequisites
      Then the skill proceeds with its procedure

    Scenario: Prerequisite fails when testing_strategy is absent
      Given docs/charter/testing.yaml exists but lacks a testing_strategy link
      When the test-design skill checks prerequisites
      Then the skill fails with a message telling the user to run detect-test-regime first
      And no test-design output is written

    Scenario: Prerequisite fails when testing.yaml is missing
      Given docs/charter/testing.yaml does not exist
      When the test-design skill checks prerequisites
      Then the skill fails with a message that the charter testing declaration is absent
      And no test-design output is written

  Rule: Test-design skill assigns one test owner per contract across the backlog
    # actor: Planning Agent
    # @factory/skills/test-design/SKILL.md

    Scenario: Ownership assigned to the story that introduces the contract
      Given a contract is traced by multiple stories across epics
      And one story introduces the contract's infrastructure or first exercises it
      When the test-design skill resolves ownership in a single backlog-wide pass
      Then the introducing story owns the contract's test
      And the dependency order in deps determines which story introduces first

    Scenario: Ownership resolved across multiple epics
      Given a contract spans stories in two different epics
      When the test-design skill resolves ownership
      Then ownership is resolved in one pass through the entire epics.md
      And exactly one story owns the contract's test regardless of epic boundaries

    Scenario: No contract tested twice at the same layer
      Given the test-design skill has resolved all contract ownership
      When a non-owning story traces the same contract
      Then no duplicate test is assigned at the owning layer
      And the non-owning story receives a Prior Tests section instead

  Rule: Test-design skill classifies contracts by risk class
    # actor: Planning Agent
    # @factory/rulebooks/conventions/testing-strategy.md

    Scenario: Risk class resolved from testing.yaml overrides
      Given docs/charter/testing.yaml contains a risk_classes section
      And the risk_classes section defines a classification for the contract
      When the test-design skill classifies the contract
      Then the testing.yaml classification takes precedence over convention defaults

    Scenario: Risk class resolved from convention defaults
      Given docs/charter/testing.yaml has no risk_classes section
      When the test-design skill classifies the contract
      Then the Factory convention defaults from testing-strategy.md apply
      And critical is assigned to contracts with atomicity, concurrency, or security invariants
      And standard is assigned to CRUD operations and input validation
      And structural is assigned to declarative structure and schema conformance

    Scenario: Custom project risk class applied
      Given docs/charter/testing.yaml defines a custom risk class named financial
      And a contract is tagged with the financial risk class
      When the test-design skill classifies the contract
      Then the custom risk class's format and budget rules govern the test design

  Rule: Test-design skill propagates prior tests to non-owning stories
    # actor: Planning Agent
    # @factory/skills/test-design/SKILL.md

    Scenario: Non-owning story receives Prior Tests section
      Given story A owns the test for contract DOM-01
      And story B traces contract DOM-01 but does not own it
      When the test-design skill writes output for story B
      Then story B gains a Prior Tests section
      And the section lists the test modules and specific test functions from story A
      And the developer-agent runs these as its first RED check

    Scenario: Prior Tests entry points to the owner's test module and function
      Given the owning story's test is at tests/test_domain.py::test_entity_uniqueness
      When the test-design skill writes the Prior Tests section for a non-owning story
      Then the entry names both the test module and the specific test function

  Rule: Create-backlog sequence integrates test-design as optional step
    # actor: Planning Agent
    # @factory/skills/create-backlog/SKILL.md
    # @factory/skills/create-backlog-write-epics/SKILL.md

    Scenario: Operational sequence includes test-design between phases 2 and 3
      Given the create-backlog parent skill's operational sequence table
      When the table is read by a planning agent
      Then a step 2.5 row exists for the test-design skill
      And the step is marked optional

    Scenario: Create-backlog-write-epics surfaces the test-design option
      Given the create-backlog-write-epics skill has completed step 2
      When it presents epics.md to the user for confirmation
      Then it includes a prompt about optionally invoking test-design
      And the prompt explains that test-design prescribes the developer-agent's TDD RED phase

    Scenario: Sequence proceeds without test-design
      Given the user chooses not to invoke test-design after step 2
      When the planning agent proceeds to step 3
      Then step 3 runs normally
      And no test-design sections exist in epics.md

  Rule: Create-backlog-stories carries test-design sections into story files
    # actor: Planning Agent
    # @factory/skills/create-backlog-stories/SKILL.md

    Scenario: Story files receive test-design sections from epics.md
      Given backlog/epics.md contains Test Design sections from the test-design skill
      When the create-backlog-stories skill writes backlog/ST-NNNN.md files
      Then each story's tests frontmatter field is populated from the epic building-block entry
      And the Test Design section is written verbatim into the story body
      And the Prior Tests section is written verbatim into the story body

    Scenario: Stories written normally when no test-design output exists
      Given backlog/epics.md contains no Test Design sections
      When the create-backlog-stories skill writes backlog/ST-NNNN.md files
      Then it behaves exactly as it does today
      And no test-design-related sections appear in the story files

  Rule: Developer-Agent consumes test-design as prescribed RED phase
    # actor: Developer-Agent
    # @factory/agents/developer-agent.md

    Scenario: Developer-Agent uses Test Design section as RED phase input
      Given the story file contains a Test Design section
      When the developer-agent begins step 3 Red-Green-Refactor
      Then it writes exactly the failure scenarios specified in the Test Design section as failing tests
      And it does not invent additional test cases
      And it does not substitute its own test scenarios
      And the risk-class and layer assignment determine where each test lives

    Scenario: Developer-Agent runs Prior Tests before writing new code
      Given the story file contains a Prior Tests section
      When the developer-agent begins step 3
      Then it runs the listed test modules and functions first
      And its implementation must keep those tests green
      And it treats these as inherited RED tests, not new work

    Scenario: Developer-Agent never invents tests when test-design output exists
      Given the story file contains a Test Design section
      When the developer-agent's RED phase is complete
      Then every test it wrote corresponds to a scenario in the Test Design section
      And no test exists that was not specified by the test-design skill

  Rule: Developer-Agent falls back without test-design output
    # actor: Developer-Agent
    # @factory/agents/developer-agent.md

    Scenario: Developer-Agent falls back to existing behavior
      Given the story file has no Test Design section
      And the story file has no Prior Tests section
      When the developer-agent begins step 3
      Then it follows the existing Red-Green-Refactor cycle
      And it invents its own RED phase as it does today

    Scenario: Backward compatibility preserved for pre-existing stories
      Given stories were created before the test-design skill existed
      When the developer-agent processes such a story
      Then no workflow step fails due to missing test-design output

  Rule: Testing strategy defines risk-class conventions
    # actor: Human Operator
    # @factory/rulebooks/conventions/testing-strategy.md

    Scenario: Testing strategy declares three default risk classes
      Given the testing strategy at factory/rulebooks/conventions/testing-strategy.md
      Then it defines the critical risk class for atomicity, concurrency, and security invariants
      And it defines the standard risk class for CRUD operations and input validation
      And it defines the structural risk class for declarative structure and schema conformance

    Scenario: Testing strategy defines failure-scenario formats per risk class
      Given the testing strategy defines risk classes
      Then critical uses Given/When/Then/Forbidden format
      And standard uses concrete scenario text with expected inputs and assertions
      And structural delegates to the deterministic linter layer with no test-design output

    Scenario: Testing strategy defines budget rules per risk class
      Given the testing strategy defines risk classes
      Then critical has unbounded budget covering every distinct failure mode
      And standard has equivalence budget of one per equivalence class plus boundaries
      And structural has no test-design budget because the linter owns it

  Rule: Human Operator configures risk classes per project in testing.yaml
    # actor: Human Operator
    # @docs/charter/testing.yaml
    # @factory/rulebooks/templates/charter-testing.yaml

    Scenario: Project overrides default risk class settings
      Given docs/charter/testing.yaml contains a risk_classes section
      And the section redefines standard with a stricter budget
      When the test-design skill reads risk-class definitions
      Then the project override takes precedence over Factory convention defaults

    Scenario: Project adds a custom risk class
      Given docs/charter/testing.yaml defines a new risk class named financial
      And the financial class specifies format as forbidden and budget as unbounded
      And the financial class has a requires list including double_entry_invariant
      When the test-design skill classifies a contract tagged as financial
      Then it applies the custom class's format, budget, and requires rules

    Scenario: Template includes risk_classes schema by example
      Given the charter template at factory/rulebooks/templates/charter-testing.yaml
      Then it includes a risk_classes section with format, budget, and optional requires fields
      And the schema is defined by a concrete YAML example

  Rule: Human Operator configures gate thresholds in testing.yaml
    # actor: Human Operator
    # @docs/charter/testing.yaml
    # @factory/rulebooks/templates/charter-testing.yaml

    Scenario: Gates section declares crap_score configuration
      Given docs/charter/testing.yaml contains a gates section
      Then the gates.crap_score entry has an enabled flag set to true
      And the gates.crap_score entry has a threshold value

    Scenario: Gates section declares mutation_testing configuration
      Given docs/charter/testing.yaml contains a gates section
      Then the gates.mutation_testing entry has an enabled flag set to false
      And mutation testing is disabled by default until project infrastructure is ready

    Scenario: Template includes gates section
      Given the charter template at factory/rulebooks/templates/charter-testing.yaml
      Then it includes a gates section with crap_score and mutation_testing entries
      And each entry documents its enabled flag and any threshold parameters

  Rule: Dispatcher reads gate configuration from testing.yaml
    # actor: Dispatcher (Implementation-Agent)
    # @factory/agents/implementation-agent.md
    # @docs/adr/0012-dispatcher-owned-semantic-gate-loop.md

    Scenario: Dispatcher reads per-gate enabled flag from testing.yaml
      Given docs/charter/testing.yaml contains a gates section
      When the dispatcher evaluates quality gates after a developer commit
      Then it reads each gate's enabled flag from gates
      And it skips gates where enabled is false

    Scenario: Dispatcher reads CRAP threshold from testing.yaml
      Given docs/charter/testing.yaml declares gates.crap_score.threshold as 8
      When the dispatcher runs the crap-score gate
      Then it passes the threshold from testing.yaml to the crap-score script
      And the script uses that threshold instead of its hardcoded default

    Scenario: ADR-0012 documents test_design_verify as conditional gate
      Given docs/adr/0012-dispatcher-owned-semantic-gate-loop.md
      When it is amended for the test-design skill
      Then it documents test_design_verify as a conditional gate
      And the gate is active when test-design output exists in the story
      And the gate is skipped when no test-design output exists

  Rule: Test-design-verify gate validates test-design completeness
    # actor: Dispatcher (Implementation-Agent)
    # @factory/scripts/test-design-verify

    Scenario: Gate resolves trace-to-scenario chain
      Given a story with traces frontmatter listing DOM-01 and OBS-04
      When the test-design-verify gate runs
      Then it reads each trace ID from the story's traces field
      And looks up the corresponding entry in docs/spec/scope-map.md
      And reads the .feature file and collects scenarios under the matching rule
      And verifies each scenario has a corresponding entry in the story's Test Design section

    Scenario: Gate passes when all owned contracts have assertions
      Given a story with a Test Design section covering every reachable scenario
      When the test-design-verify gate runs
      Then it exits with code 0

    Scenario: Gate fails when an owned contract lacks an assertion
      Given a story's Test Design section is missing a scenario from the .feature file
      When the test-design-verify gate runs
      Then it exits with code 1
      And reports which scenario lacks a corresponding test assertion

    Scenario: Gate accepts valid waivers
      Given a story's Test Design section contains a waiver line
      And the waiver follows the blockquote format naming an owner path
      And the named test module exists in the repository
      When the test-design-verify gate runs
      Then it treats the waivered scenario as covered

    Scenario: Gate rejects waivers without a resolvable owner path
      Given a story's Test Design section contains a waiver line
      And the named test module does not exist
      When the test-design-verify gate runs
      Then it exits with code 1
      And reports the invalid waiver

    Scenario: Gate validates non-owning story Prior Tests entries
      Given a non-owning story traces a contract
      And the story has a Prior Tests section
      When the test-design-verify gate runs
      Then it verifies the Prior Tests entry points to the owner's test module and function
      And it exits with code 0 when the entry resolves

    Scenario: Gate skips stories without test-design output
      Given a story has no Test Design section and no Prior Tests section
      When the test-design-verify gate runs
      Then it exits with code 0
      And produces no findings

    Scenario: Gate exits with code 2 on configuration error
      Given the story's traces field references a scope-map entry that does not exist
      When the test-design-verify gate runs
      Then it exits with code 2
      And reports the unresolvable trace ID

  Rule: CRAP score reads threshold from testing.yaml gates section
    # actor: Dispatcher (Implementation-Agent)
    # @factory/scripts/crap-score
    # @factory/skills/crap-score/SKILL.md

    Scenario: CRAP script reads threshold from testing.yaml
      Given docs/charter/testing.yaml declares gates.crap_score.threshold as 8
      When the crap-score script resolves its threshold
      Then it reads the value from testing.yaml's gates.crap_score.threshold
      And uses 8 as the threshold instead of the hardcoded default of 30

    Scenario: CRAP script falls back to hardcoded default
      Given docs/charter/testing.yaml has no gates section
      When the crap-score script resolves its threshold
      Then it uses the hardcoded default of 30

    Scenario: Dead-code house-rules lookup path replaced
      Given the crap-score script's resolve_threshold function
      When it resolves the threshold
      Then it reads from testing.yaml's gates.crap_score.threshold
      And the read_threshold_from_house_rules function is replaced
      # @factory/scripts/crap-score::read_threshold_from_testing_yaml
      # @factory/scripts/crap-score::resolve_threshold
