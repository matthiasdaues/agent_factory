Feature: Test Gate Presence over Test Execution

  Factory ensures test gates exist; the project decides what runs inside them.
  Testing is project-owned infrastructure declared in docs/charter/testing.yaml.
  Factory's guardrails and FSM gates read that declaration. Factory never owns
  test execution, framework detection, or structured test output.

  Rule: Human Operator declares project test commands via charter
    # actor: Human Operator
    # @docs/charter/testing.yaml (new artifact)

    Scenario: Project declares test commands in testing.yaml
      Given a project at the repository root
      When the operator creates docs/charter/testing.yaml with test_command
      Then Factory's FSM gates can resolve the test command
      And block-dangerous-git.sh can read the agent allowlist

    Scenario: Project declares optional mode commands
      Given docs/charter/testing.yaml exists with test_command
      When the operator adds test_staged_command and test_changed_command
      Then all three commands are available to FSM gates and guardrails
      And each command is a project-defined shell command, not a framework name

    Scenario: Factory's own repository uses the same mechanism
      Given the Factory repository
      When docs/charter/testing.yaml is created for Factory
      Then it declares test_command as the Factory test suite command
      And Factory's gates resolve test_command the same way any consumer project would

  Rule: FSM gate conditions resolve test command from charter
    # actor: Human Operator, Orchestrator-as-Trigger
    # @factory/playbooks/greenfield-development.fsm.yml
    # @factory/playbooks/bug-fix.fsm.yml

    Scenario: Phase advance resolves test command from charter
      Given a playbook FSM declares a script_exit_zero entry condition
      And docs/charter/testing.yaml declares test_command
      When phase advance evaluates the gate
      Then it resolves test_command from the charter
      And executes it from the repository root
      And reads only the exit code

    Scenario: Phase advance blocks when charter is absent
      Given a playbook FSM declares a script_exit_zero entry condition
      And docs/charter/testing.yaml does not exist
      When phase advance evaluates the gate
      Then it reports the missing charter
      And blocks advancement

    Scenario: Phase advance blocks when test_command is missing
      Given docs/charter/testing.yaml exists but lacks test_command
      When phase advance evaluates the gate
      Then it reports the missing test_command field
      And blocks advancement

    Scenario: Gate passes on exit code zero
      Given docs/charter/testing.yaml declares test_command
      And the declared command exits 0
      When phase advance evaluates the gate
      Then the gate passes
      And phase advance proceeds

    Scenario: Gate blocks on nonzero exit code
      Given docs/charter/testing.yaml declares test_command
      And the declared command exits 1
      When phase advance evaluates the gate
      Then the gate reports test_command as unmet
      And phase advance is blocked

  Rule: Guardrail allowlists charter-declared test commands for agents
    # actor: CLI-Invoked Agent
    # @factory/config/hooks/block-dangerous-git.sh

    Scenario: Agent runs a charter-declared test command
      Given docs/charter/testing.yaml declares test_staged_command
      When an agent runs the exact declared command string
      Then block-dangerous-git.sh allows the command
      # @factory/config/hooks/block-dangerous-git.sh

    Scenario: Agent blocked from bare test command
      Given an agent session
      When the agent attempts to run a bare test command
      Then block-dangerous-git.sh intercepts at PreToolUse
      And the command is denied with exit 2
      And the agent sees a message directing it to the charter-declared command

    Scenario: Allowlist uses exact string matching
      Given docs/charter/testing.yaml declares test_command as "make test"
      When an agent runs "make test --verbose"
      Then block-dangerous-git.sh denies the command
      Because it does not exactly match the declared command string

    Scenario: All three charter fields are allowlisted when present
      Given docs/charter/testing.yaml declares test_command, test_staged_command, and test_changed_command
      When an agent runs any one of the three exact command strings
      Then block-dangerous-git.sh allows the command

    Scenario: No charter means no agent test commands allowed
      Given docs/charter/testing.yaml does not exist
      When an agent attempts any test command
      Then block-dangerous-git.sh denies it
      And bare test command deny patterns still apply

  Rule: Factory does not inject test hooks into pre-commit config
    # actor: Human Operator
    # @factory/config/pre-commit-config.yaml

    Scenario: Pre-commit config contains no test-related hooks
      Given Factory's pre-commit configuration
      Then no entry named agent_factory_hook-run-tests-full exists
      And no Factory-owned test hook is injected into projects

    Scenario: Project owns its test hooks
      Given a project with its own pre-commit test hook
      When init-factory runs
      Then Factory does not add or replace test hooks
      And the project's existing test hooks are preserved

  Rule: Factory deletes run-tests and mutation-analysis scripts
    # actor: Human Operator
    # @factory/scripts/run-tests (to be deleted)
    # @factory/scripts/mutation-analysis (to be deleted)

    Scenario: run-tests script is deleted from repository
      Given the Factory repository
      Then factory/scripts/run-tests does not exist
      And no consumer project receives it through the factory/scripts symlink

    Scenario: mutation-analysis script is deleted from repository
      Given the Factory repository
      Then factory/scripts/mutation-analysis does not exist
      And mutation testing is entirely the project's responsibility

  Rule: Detect-test-regime skill discovers test entrypoints during onboarding
    # actor: Human Operator
    # @factory/scripts/init-factory

    Scenario: Single test entrypoint detected
      Given a project with a Makefile containing a test target
      And no other conventional test entrypoints
      When the detect-test-regime skill runs during onboarding
      Then it records the entrypoint in docs/charter/testing.yaml

    Scenario: Multiple test entrypoints detected
      Given a project with both a Makefile test target and a package.json test script
      When the detect-test-regime skill runs during onboarding
      Then it asks the operator for disambiguation
      And does not guess which entrypoint to use

    Scenario: No test entrypoint detected
      Given a project with no conventional test entrypoints
      When the detect-test-regime skill runs during onboarding
      Then it surfaces the gap to the operator
      And offers to help build project-owned test infrastructure

  Rule: Dispatcher gate sequence reduces from three to two
    # actor: Human Operator, CLI-Invoked Agent

    Scenario: Dispatcher runs two quality gates after developer commit
      Given a developer-agent has committed code
      When the dispatcher evaluates quality gates
      Then it runs crap-score on committed artifacts
      And it runs dependency-check against architecture.dsl dependency rules
      And it does not run mutation-analysis

    Scenario: All gates pass and dispatcher proceeds to merge
      Given crap-score and dependency-check both pass
      When the dispatcher evaluates the gate results
      Then it proceeds to premerge-check and merge

    Scenario: A gate fails and dispatcher spawns a fix iteration
      Given crap-score or dependency-check fails
      When the dispatcher evaluates the gate results
      Then it spawns a fresh developer agent with the failing gate reports
      And the maximum fix iterations before blocking is three

  Rule: Mutation-analysis skill provides setup guidance
    # actor: Human Operator
    # @factory/skills/mutation-analysis/SKILL.md

    Scenario: Mutation-analysis skill describes setup process
      Given the mutation-analysis skill document
      Then it describes how to set up project-owned mutation testing
      And it does not prescribe a specific tool chain
      And it does not reference factory/scripts/mutation-analysis

  Rule: Remove-factory leaves project test infrastructure intact
    # actor: Human Operator

    Scenario: Remove-factory preserves testing.yaml
      Given a project with docs/charter/testing.yaml
      When remove-factory runs
      Then docs/charter/testing.yaml remains
      And the project can run tests freely without Factory's guardrail mediation

    Scenario: Remove-factory removes guardrail but not test commands
      Given a project with Factory installed
      When remove-factory runs
      Then block-dangerous-git.sh is removed
      And project-owned test hooks remain
      And bare test commands become available again

  Rule: Gate contract is exit-code-only
    # actor: Human Operator, Orchestrator-as-Trigger

    Scenario: Factory does not parse structured test output
      Given a charter-declared test command that outputs JSON results
      When the FSM gate evaluates the command
      Then it reads only the exit code
      And ignores all stdout and stderr content for the pass/fail decision

    Scenario: Exit code zero means pass
      Given a charter-declared test command
      When the command exits 0
      Then the gate passes regardless of stdout content

    Scenario: Exit code nonzero means fail
      Given a charter-declared test command
      When the command exits with any nonzero code
      Then the gate fails regardless of stdout content

  Rule: Charter declares layer bindings for QA strategy grounding
    # actor: Human Operator
    # @docs/charter/testing.yaml

    Scenario: Project declares layer bindings in testing.yaml
      Given docs/charter/testing.yaml exists with test_command
      When the operator adds a layers section mapping Factory layer names to tooling
      Then each layer declares tool, infrastructure, entry_point, and optional anti_patterns
      And unused layers are omitted, not set to null

    Scenario: Layer declares fidelity for environment reality
      Given docs/charter/testing.yaml declares an integration_test layer
      When the operator adds a fidelity map to the layer
      Then each entry names a dependency and whether it is real or substituted
      And qa-strategy-from-spec checks fidelity against contract requirements

    Scenario: Kit-manager populates layer bindings during onboarding
      Given a project with existing test infrastructure
      When the kit-manager runs charter completeness sweep
      Then it scans conftest.py, test directories, Makefile targets, and runner configs
      And records layer bindings in docs/charter/testing.yaml
      And a human reviewer confirms the bindings match the repository

    Scenario: Detect-test-regime populates both commands and layer bindings
      Given a project with a single test entrypoint and identifiable test layers
      When the detect-test-regime skill runs during onboarding
      Then it records the entrypoint as test_command in docs/charter/testing.yaml
      And it records identified layer bindings in the layers section

  Rule: QA strategy grounds contract-owner assignments in charter
    # actor: CLI-Invoked Agent
    # @factory/skills/qa-strategy-from-spec/SKILL.md

    Scenario: QA strategy reads charter layer bindings
      Given docs/charter/testing.yaml declares a layers section
      When qa-strategy-from-spec derives a per-feature QA strategy
      Then it maps feature contracts to charter-declared layers
      And it does not use the Factory convention's generic layers when bindings exist

    Scenario: QA strategy emits gap for undeclared layer
      Given docs/charter/testing.yaml declares three of five layers
      And a feature contract requires a layer not declared in the charter
      When qa-strategy-from-spec assigns test owners
      Then it emits a gap finding naming the missing layer
      And does not silently assume the layer exists

    Scenario: QA strategy falls back when layer bindings are absent
      Given docs/charter/testing.yaml exists but has no layers section
      When qa-strategy-from-spec derives a per-feature QA strategy
      Then it falls back to the Factory convention's generic five layers
      And emits a gap finding noting the absent layer bindings

    Scenario: QA strategy verifies charter matches repository
      Given docs/charter/testing.yaml declares layer bindings
      When qa-strategy-from-spec scans the repository's test infrastructure
      And a declared entry_point or infrastructure does not match what exists
      Then it records a mismatch as a gap finding

    Scenario: QA strategy uses layer status states instead of add/strengthen/out
      Given qa-strategy-from-spec derives a per-feature QA strategy
      When it writes the Test Layers in Scope table
      Then each layer status is one of available, partially covered, planned, blocked, or out
      And available means the harness works but tests may not exist yet
      And planned means neither harness nor tests exist

    Scenario: QA strategy emits test IDs for contract-owner rows
      Given qa-strategy-from-spec assigns a contract to an owning layer
      When it writes the contract-owner table
      Then each row includes a test ID following the pattern scope-ID-layer-abbreviation-sequence
      And the test ID is a stable identifier tied to the scope ID

    Scenario: QA strategy checks fidelity before assigning contract ownership
      Given docs/charter/testing.yaml declares a layer with fidelity declarations
      And a contract requires real transactions
      When qa-strategy-from-spec assigns the contract to a layer
      Then it verifies the layer's fidelity covers the contract's requirements
      And emits a gap finding if the layer's fidelity is insufficient

  Rule: Developer-agent feeds back test-harness mismatches
    # actor: CLI-Invoked Agent
    # @factory/agents/developer-agent.md

    Scenario: Developer-agent detects harness mismatch during implementation
      Given a QA strategy prescribes a layer and tooling for a contract
      When the developer-agent writes tests and finds the prescribed harness missing
      Then it invokes spec-feedback against the QA strategy document
      And the finding names the contract, prescribed layer, and concrete obstacle

    Scenario: Spec-feedback finding proposes a correction
      Given the developer-agent filed a spec-feedback finding against the QA strategy
      Then the finding names the specific contract-owner row that is wrong
      And proposes a correction
      And the QA strategy is updated in the same story or a follow-up QA loop

  Rule: Mutation-analysis skill classifies survivors by contract ownership
    # actor: CLI-Invoked Agent
    # @factory/skills/mutation-analysis/SKILL.md

    Scenario: Mutation analysis with contract-owner table classifies owner_held
      Given a per-feature QA strategy with a contract-owner table
      And the declared owner's test killed a mutant
      When the mutation-analysis skill classifies the survivor
      Then the status is owner_held
      And overlap tests that also killed it are safe to trim

    Scenario: Mutation analysis classifies owner_failed
      Given a per-feature QA strategy with a contract-owner table
      And the declared owner did not kill a mutant but another layer did
      When the mutation-analysis skill classifies the survivor
      Then the status is owner_failed
      And a spec-feedback finding is filed against the contract-owner row

    Scenario: Mutation analysis classifies uncaught
      Given a per-feature QA strategy with a contract-owner table
      And no layer caught a mutant
      When the mutation-analysis skill classifies the survivor
      Then the status is uncaught
      And existing resolution actions apply directed at the declared owner

    Scenario: Mutation analysis joins by spec marker when available
      Given tests carry spec markers linking them to scope IDs
      And a per-feature QA strategy with a contract-owner table is provided
      When the mutation-analysis skill classifies a survivor
      Then it joins the mutant to its contract via the spec marker
      And the marker-based join takes precedence over file-path join

    Scenario: Mutation analysis falls back to file-path join without markers
      Given tests do not carry spec markers
      And a per-feature QA strategy with a contract-owner table is provided
      When the mutation-analysis skill classifies a survivor
      Then it joins the mutant to its contract by file path

    Scenario: Mutation analysis without contract-owner table uses existing classification
      Given no per-feature QA strategy is provided
      When the mutation-analysis skill classifies a survivor
      Then it uses the existing resolution actions only
      And does not attempt contract-ownership classification
