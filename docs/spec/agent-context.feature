Feature: Agent Context

  Two-layer YAML-based routing interface between factory agents and project
  knowledge. Layer 1 (reading-guides.yaml) routes by work-type concern to
  sections in Layer 2 index files (stack.yaml, workflow.yaml, governance.yaml).
  A two-mode lifecycle lets greenfield projects write values directly
  (mode: primary) and mature projects maintain a pure link index (mode: index).
  testing.yaml is a peer file outside the lifecycle.

  Proposal trace: docs/proposals/yaml-charter-lifecycle.md

  Rule: Factory agent reads project context through unified two-layer routing
    # actor: Factory Agent
    # Any agent that needs project knowledge reads all four agent-context files.
    # Layer 1 (reading-guides.yaml) routes by concern to Layer 2 index sections.
    # Layer 2 (stack.yaml, workflow.yaml, governance.yaml) carries source pointers.

    Scenario: Agent reads all four context files for a complete project
      Given a project with docs/agent-context/ containing all four YAML files
      When a factory agent reads the agent context
      Then the agent receives reading-guides.yaml, stack.yaml, workflow.yaml, and governance.yaml

    Scenario: Reading guide routes agent to relevant index sections by concern
      Given reading-guides.yaml contains a "backend" concern with references to stack.yaml#frameworks.backend and workflow.yaml#testing
      When a factory agent reads the reading guide for the "backend" concern
      Then the agent receives the key paths stack.yaml#frameworks.backend and workflow.yaml#testing as relevant sections

    Scenario: Index file in index mode provides name and source pointer
      Given stack.yaml has mode: index
      And the frameworks.backend field has name: FastAPI and source: docs/adr/004-use-fastapi.md
      When an agent reads stack.yaml#frameworks.backend
      Then the agent receives the name "FastAPI" and the source path docs/adr/004-use-fastapi.md

    Scenario: Index file in primary mode provides inline values
      Given stack.yaml has mode: primary
      And the frameworks.backend field has a direct value "FastAPI 0.100"
      When an agent reads stack.yaml#frameworks.backend
      Then the agent receives the inline value "FastAPI 0.100" with no source pointer

    Scenario: Greenfield project has no reading guide
      Given a greenfield project with three index files in mode: primary
      And reading-guides.yaml does not exist
      When a factory agent reads the agent context
      Then the agent receives only stack.yaml, workflow.yaml, and governance.yaml

  Rule: Operator initializes agent context for a greenfield project
    # actor: Human Operator
    # @factory/skills/capture-context/SKILL.md
    # @factory/scripts/init-factory

    Scenario: capture-context --init creates three index-file templates
      Given no docs/agent-context/ directory exists
      When the operator runs capture-context --init
      Then docs/agent-context/stack.yaml is created from the template with mode: primary and null placeholders
      And docs/agent-context/workflow.yaml is created from the template with mode: primary and null placeholders
      And docs/agent-context/governance.yaml is created from the template with mode: primary and null placeholders
      And reading-guides.yaml is not created

    Scenario: capture-context --init does not overwrite existing context
      Given docs/agent-context/stack.yaml already exists with populated values
      When the operator runs capture-context --init
      Then the existing stack.yaml is preserved unchanged

    Scenario: Stakeholder interview fills greenfield index values directly
      Given three index files exist with mode: primary
      When the operator answers stakeholder questions about technology choices
      Then capture-context writes the answers as inline values to the appropriate index file fields

  Rule: Operator onboards brownfield documentation into agent context
    # actor: Human Operator
    # @factory/skills/capture-context/SKILL.md

    Scenario: capture-context --init --scan discovers documentation signals
      Given a project with pyproject.toml, docs/adr/, and .github/workflows/
      When the operator runs capture-context --init --scan
      Then the scan identifies languages, frameworks, CI/CD, and decision documentation from those files

    Scenario: Concern-based interview populates indexes and reading guide
      Given a brownfield project with backend and testing documentation
      When the concern interview completes for backend and testing concerns
      Then stack.yaml has source pointers for the discovered framework documentation
      And workflow.yaml has source pointers for the discovered testing documentation
      And reading-guides.yaml routes backend and testing concerns to the populated index sections

    Scenario: Brownfield scan achieves full source coverage and proposes index mode
      Given capture-context --init --scan has populated all non-null, non-deferred fields with source pointers
      When the scan completes
      Then capture-context proposes setting mode: index across all three files
      And the operator confirms or declines the transition

    Scenario: Brownfield scan with partial coverage sets primary mode
      Given capture-context --init --scan has populated some fields but others remain without source pointers
      When the scan completes
      Then all three index files remain in mode: primary

    Scenario: Brownfield scan detects legacy markdown charter and offers migration
      Given docs/charter/tech-stack.md exists as a legacy markdown charter
      When the operator runs capture-context --init --scan
      Then capture-context operates on the existing markdown format
      And offers migration to YAML agent-context as an optional step

    Scenario: Operator declines brownfield migration
      Given capture-context has offered migration from markdown charter to YAML agent-context
      When the operator declines the migration
      Then the markdown charter files remain unchanged
      And no docs/agent-context/ directory is created

  Rule: Operator updates agent context as decisions emerge
    # actor: Human Operator (via update-context skill)
    # @factory/skills/update-context/SKILL.md

    Scenario: update-context writes inline values when mode is primary
      Given stack.yaml has mode: primary
      When update-context records a technology choice for frameworks.backend
      Then the field receives the inline value directly

    Scenario: update-context writes name and source together when mode is index
      Given stack.yaml has mode: index
      When update-context records a change to frameworks.backend with source docs/adr/015-switch-to-django.md
      Then the field receives both name: Django and source: docs/adr/015-switch-to-django.md

    Scenario: update-context refuses hand-edit when mode is index
      Given stack.yaml has mode: index
      When an agent attempts to write an inline value without a source pointer
      Then update-context rejects the write

    Scenario: update-context proposes reading-guide creation on first source pointer
      Given three index files exist with mode: primary
      And reading-guides.yaml does not exist
      When update-context writes the first source pointer to any index file
      Then update-context proposes creating reading-guides.yaml from the template

    Scenario: update-context writes deferred field
      Given stack.yaml has mode: primary
      And the operator defers the data_stores decision with reason "evaluating options"
      When update-context records the deferral
      Then the data_stores field becomes deferred: "evaluating options"
      And no other keys coexist with the deferred key at that field

  Rule: Operator transitions context from primary to index mode
    # actor: Human Operator (via update-context skill)

    Scenario: Transition condition is met
      Given all three index files have mode: primary
      And every non-null, non-deferred leaf field across all three files has a source pointer
      When update-context checks the transition condition
      Then update-context prompts the operator to switch to index mode

    Scenario: Operator confirms mode transition
      Given update-context has prompted for mode transition
      When the operator confirms
      Then all three index files are set to mode: index in a single atomic commit
      And inline values are stripped to names only
      And source pointers are preserved

    Scenario: Operator declines mode transition
      Given update-context has prompted for mode transition
      When the operator declines
      Then all three files remain in mode: primary

    Scenario: Transition blocked by null field without deferral
      Given stack.yaml has a null field without a deferred mapping
      And that field has no source pointer
      When update-context checks the transition condition
      Then the transition condition is not met
      And no prompt is issued

    Scenario: Transition not blocked by deferred fields
      Given stack.yaml has a field with deferred: "reason"
      And all other non-null, non-deferred fields have source pointers
      When update-context checks the transition condition
      Then the deferred field is excluded from the condition
      And the transition condition is met

    Scenario: Transition not blocked by null fields
      Given stack.yaml has existing_systems: null
      And all other non-null, non-deferred fields have source pointers
      When update-context checks the transition condition
      Then the null field is excluded from the condition
      And the transition condition is met

  Rule: context-lint validates agent context structure and references
    # actor: context-lint (deterministic gate)
    # @factory/scripts/context-lint

    Scenario: CX-FILE reports missing required file
      Given docs/agent-context/ exists
      And stack.yaml is missing
      When context-lint runs
      Then a CX-FILE error finding is reported for the missing file

    Scenario: CX-FILE does not require reading-guides.yaml when mode is primary
      Given all three index files have mode: primary
      And reading-guides.yaml does not exist
      When context-lint runs
      Then no CX-FILE error is reported for reading-guides.yaml

    Scenario: CX-PARSE reports invalid YAML
      Given stack.yaml contains a YAML syntax error
      When context-lint runs
      Then a CX-PARSE error finding is reported

    Scenario: CX-KEYS reports missing required top-level keys
      Given stack.yaml is missing the languages key
      When context-lint runs
      Then a CX-KEYS error finding is reported for the missing key

    Scenario: CX-KEYS reports deferred coexisting with name or source
      Given stack.yaml has a field with both deferred: "reason" and name: "value"
      When context-lint runs
      Then a CX-KEYS error finding is reported for the invalid coexistence

    Scenario: CX-NULL reports null values in default mode
      Given stack.yaml has frameworks.backend: null
      When context-lint runs in default mode
      Then a CX-NULL warning finding is reported

    Scenario: CX-NULL reports null values as error in planning-gate mode
      Given stack.yaml has frameworks.backend: null
      When context-lint runs with --planning-gate
      Then a CX-NULL error finding is reported

    Scenario: CX-MODE reports valid mode field
      Given stack.yaml has mode: primary
      When context-lint runs
      Then a CX-MODE info finding confirms the mode

    Scenario: CX-MODE-INVALID reports unrecognized mode value
      Given stack.yaml has mode: staging
      When context-lint runs
      Then a CX-MODE-INVALID error finding is reported for the unrecognized mode value

    Scenario: CX-SRC reports missing source pointer when mode is index
      Given stack.yaml has mode: index
      And frameworks.backend has a name but no source pointer
      When context-lint runs
      Then a CX-SRC warning finding is reported

    Scenario: CX-SRC-EXIST reports unresolvable source path
      Given stack.yaml has a source pointer to docs/adr/nonexistent.md
      When context-lint runs
      Then a CX-SRC-EXIST warning finding is reported

    Scenario: CX-SRC-STALE reports stale index entry
      Given stack.yaml has a source pointer to docs/adr/004.md
      And docs/adr/004.md was modified more recently than stack.yaml
      When context-lint runs
      Then a CX-SRC-STALE info finding is reported

    Scenario: CX-GUIDE-REF validates key-path references
      Given reading-guides.yaml references stack.yaml#frameworks.backend
      And stack.yaml has a frameworks.backend key
      When context-lint runs
      Then no CX-GUIDE-REF finding is reported for that reference

    Scenario: CX-GUIDE-REF reports unresolvable key path
      Given reading-guides.yaml references stack.yaml#frameworks.nonexistent
      And stack.yaml has no frameworks.nonexistent key
      When context-lint runs
      Then a CX-GUIDE-REF warning finding is reported

    Scenario: CX-GUIDE-REF checks key existence only not value
      Given reading-guides.yaml references stack.yaml#frameworks.backend
      And stack.yaml has frameworks.backend: null
      When context-lint runs
      Then no CX-GUIDE-REF finding is reported because the key exists

    Scenario: CX-FORMAT reports mixed locations
      Given both docs/agent-context/stack.yaml and docs/charter/tech-stack.md exist
      When context-lint runs
      Then a CX-FORMAT error finding is reported for the mixed locations

    Scenario: CX-FORMAT does not flag split testing.yaml location
      Given docs/agent-context/stack.yaml exists
      And testing.yaml exists only at docs/charter/testing.yaml
      When context-lint runs
      Then no CX-FORMAT error is reported for the testing.yaml location

  Rule: Legacy projects continue working without migration
    # actor: Human Operator
    # @factory/scripts/context-lint

    Scenario: Format detection resolves legacy markdown charter
      Given docs/charter/tech-stack.md exists
      And no docs/agent-context/ directory exists
      When format detection runs
      Then the legacy markdown charter mode is selected

    Scenario: Legacy markdown charter passes context-lint
      Given docs/charter/ contains the three markdown charter files
      When context-lint runs
      Then validation applies the existing CH-* finding codes
      And no migration is forced

    Scenario: Format detection resolves legacy YAML charter
      Given docs/charter/tech-stack.yaml exists
      And no docs/agent-context/ directory exists
      When format detection runs
      Then the legacy YAML charter mode is selected

    Scenario: Legacy consumers read charter files unchanged
      Given a project uses markdown charter under docs/charter/
      When any factory agent or script reads project context
      Then the consumer reads docs/charter/ files as before

  Rule: testing.yaml operates as a lifecycle-exempt peer file
    # actor: detect-test-regime (skill)
    # @factory/skills/detect-test-regime/SKILL.md
    # @factory/config/hooks/block-dangerous-git.sh

    Scenario: detect-test-regime writes testing.yaml directly
      Given docs/agent-context/ exists
      When detect-test-regime scans the project for test suites
      Then it writes docs/agent-context/testing.yaml with test configuration
      And does not consult or modify the mode field of index files

    Scenario: context-lint validates testing.yaml with CX-PARSE only
      Given docs/agent-context/testing.yaml exists
      When context-lint runs
      Then CX-PARSE validation applies to testing.yaml
      And CX-SRC, CX-MODE, and CX-NULL checks do not apply to testing.yaml

    Scenario: testing.yaml resolution walks both paths
      Given docs/agent-context/ exists but testing.yaml is at docs/charter/testing.yaml
      When a consumer resolves the testing.yaml path
      Then docs/agent-context/testing.yaml is checked first
      And docs/charter/testing.yaml is used as fallback
      And no CX-FORMAT error is raised for the split location

    Scenario: testing.yaml at new path takes precedence
      Given testing.yaml exists at both docs/agent-context/testing.yaml and docs/charter/testing.yaml
      When a consumer resolves the testing.yaml path
      Then docs/agent-context/testing.yaml is used

  Rule: Factory consumers resolve context file paths via format detection
    # actor: Factory Consumer (agent, skill, script, hook)
    # Subfunction reused by all consumers listed in the proposal inventory

    Scenario: Format detection selects YAML agent-context mode
      Given docs/agent-context/stack.yaml exists
      When format detection runs
      Then YAML agent-context mode is selected

    Scenario: Format detection falls back to legacy YAML charter
      Given docs/agent-context/stack.yaml does not exist
      And docs/charter/tech-stack.yaml exists
      When format detection runs
      Then legacy YAML charter mode is selected

    Scenario: Format detection falls back to legacy markdown charter
      Given docs/agent-context/stack.yaml does not exist
      And docs/charter/tech-stack.yaml does not exist
      And docs/charter/tech-stack.md exists
      When format detection runs
      Then legacy markdown charter mode is selected

    Scenario: Format detection reports error on mixed locations
      Given docs/agent-context/stack.yaml exists
      And docs/charter/tech-stack.md also exists
      When format detection runs
      Then a CX-FORMAT error is reported

  Rule: Convention codifies agent context composition rules
    # actor: Factory governance

    Scenario: agent-context-composition.md convention exists
      Given the feature is implemented
      When a developer or agent reads factory/rulebooks/conventions/agent-context-composition.md
      Then binding rules for agent context composition are documented

    Scenario: rules.md carries MUST entries for agent context
      Given the feature is implemented
      When a developer or agent reads factory/rulebooks/rules.md
      Then the Agent context composition section contains MUST and MUST NOT entries
      And the entries match those specified in the proposal

    Scenario: Path updates completed across all factory consumers
      Given the feature is implemented
      When any factory agent, skill, playbook, script, or hook references project context
      Then it uses the format-detection chain to resolve context file paths
      And no hardcoded docs/charter/ path remains in active factory code
