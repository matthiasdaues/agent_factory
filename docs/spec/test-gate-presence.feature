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
