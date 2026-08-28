Feature: Newcomer onboarding and incremental brownfield

  The factory presents rigour as a ramp, not a wall. A newcomer walks
  through a guided tour before touching factory vocabulary. Brownfield
  onboarding exits after three anchor files. Feature work deepens the
  baseline incrementally.

  Rule: Newcomer walks through a guided tour before choosing a workflow
    # actor: Newcomer
    # @docs/arc42/beginner-intro.md
    # @factory/config/AGENTS.md

    Scenario: Newcomer selects the guided tour from the session entrypoint
      Given the session entrypoint presents option A "I'm new here — show me around"
      When the newcomer selects option A
      Then the CLI reads docs/arc42/beginner-intro.md
      And walks the user through it conversationally, one section at a time
      And pauses for questions after each section

    Scenario: Guided tour checks for prior work before starting
      Given the newcomer selects option A
      And a completed poc-spike or charter exists in the project
      When the tour begins
      Then the CLI acknowledges what the user has done
      And offers to skip ahead or start fresh

    Scenario: Guided tour offers poc-spike at the end
      Given the newcomer has completed the guided tour
      When the tour reaches its final section
      Then the CLI offers to run the poc-spike playbook
      And the newcomer can accept or decline

    Scenario: Newcomer encounters no undefined vocabulary during tour
      Given the newcomer is walking through the guided tour
      When any factory term appears (agent, skill, playbook, gate)
      Then the term has already been introduced in a prior section of the tour

  Rule: User reorients mid-session via the guided-tour skill
    # actor: Returning User
    # new: factory/skills/guided-tour/SKILL.md

    Scenario: User invokes guided-tour skill for orientation
      Given the user is in an active session
      When the user invokes the guided-tour skill
      Then the skill presents where the user is in the current workflow
      And what they can do next
      And what factory concepts are relevant to the current context

    Scenario: Guided-tour skill works outside any active playbook
      Given the user is in a session with no active playbook
      When the user invokes the guided-tour skill
      Then the skill presents the session entrypoint options
      And explains what each option leads to

  Rule: Session entrypoint presents four options including newcomer path
    # actor: Newcomer, Returning User
    # @factory/config/AGENTS.md

    Scenario: Session entrypoint shows the four-option menu
      Given a new session starts
      When the CLI presents the session entrypoint
      Then option A is "I'm new here — show me around"
      And option B is "I want to start something"
      And option C is "I want to run an agent or playbook directly"
      And option D is "I just want to talk something through"

    Scenario: Existing option B content is preserved under new letter
      Given the user selects option B
      When the intention tree expands
      Then it contains the same choices as the former option A
      And all playbook routing is unchanged

  Rule: In-session agents are adopted, not spawned as subagents
    # actor: Newcomer, Returning User
    # @factory/agents/chat-agent.md
    # @factory/agents/kit-manager.md
    # @factory/agents/coaching-agent.md

    Scenario: Chat-agent is adopted in the current session
      Given the user selects option D "I just want to talk something through"
      When the CLI activates the chat-agent
      Then it reads the chat-agent definition from the path resolved via INDEX.yaml
      And adopts the chat-agent's role, boundaries, and workflow as its own
      And no subagent is spawned
      And the conversation is direct with the stakeholder

    Scenario: Kit-manager is adopted when invoked by a playbook step
      Given a playbook step invokes the kit-manager
      When the CLI activates the kit-manager
      Then it reads the kit-manager definition and adopts its role
      And the stakeholder interview happens in the current session
      And no subagent is spawned

    Scenario: Coaching-agent is adopted when invoked
      Given the user or a playbook step invokes the coaching-agent
      When the CLI activates the coaching-agent
      Then it reads the coaching-agent definition and adopts its role
      And retrospective facilitation happens in the current session
      And no subagent is spawned

  Rule: Brownfield onboarding exits after three anchor files
    # actor: Brownfield User
    # @factory/playbooks/brownfield-onboarding.md

    Scenario: Stage 1 completes with three anchor files
      Given the brownfield-onboarding playbook is running
      When Stage 1 completes
      Then docs/arc42/architecture.dsl exists with system context and container views
      And docs/spec/scope-map.md exists with Rules marked implemented
      And docs/CONTEXT.md exists seeded with domain vocabulary
      And Structurizr validation passes on the DSL

    Scenario: User is offered the choice to stop or go deeper after Stage 1
      Given Stage 1 has completed
      When the playbook presents the exit point
      Then the message reads "You now have the structural shape and the functional inventory. You can start feature work from here. Want to go deeper, or start building?"
      And the user can choose to proceed to Stage 2 or exit

    Scenario: User exits after Stage 1 and starts feature work
      Given the user chose to exit after Stage 1
      When the user starts a feature-addition
      Then the feature-addition playbook accepts the brownfield-lite baseline
      And does not require full specification artifacts

    Scenario: User continues to Stage 2 for full reverse engineering
      Given the user chose to go deeper after Stage 1
      When Stage 2 begins
      Then the playbook runs the current Phases 3-6
      And produces full specification extraction, component resolution, ATAM review, and reconciliation

  Rule: Reverse-map skill populates scope map from forensic evidence
    # actor: Brownfield User
    # new: factory/skills/reverse-map/SKILL.md

    Scenario: Reverse-map sweeps tests first as primary evidence
      Given the reverse-map skill is invoked during Stage 1
      When it scans the codebase
      Then it reads test files first as the highest-confidence evidence
      And matches test names to behavioral claims
      And records each finding with confidence level "verified"

    Scenario: Reverse-map sweeps code entry points as secondary evidence
      Given the reverse-map skill has finished the test sweep
      When it scans for code entry points
      Then it identifies HTTP routes, CLI commands, queue consumers, and cron jobs
      And records each finding with confidence level "high"
      And matches entry points to test coverage where possible

    Scenario: Reverse-map presents results in batches by domain area
      Given the skill has found behaviors in a domain area
      When it presents results to the stakeholder
      Then results are grouped by domain area
      And each batch shows the behavior, test count, and implementing code
      And discrepancies are surfaced as questions, not findings
      And the stakeholder confirms, corrects, or adds missing behaviors

    Scenario: Reverse-map accepts additional unstructured sources
      Given the code and test sweep is complete
      When the skill offers to accept additional sources
      Then the stakeholder can provide wiki pages, API specs, README files, or verbal knowledge
      And the skill cross-checks additional sources against existing findings
      And records the source type and confidence level for each new finding

    Scenario: Reverse-map writes scope map with provenance
      Given the stakeholder says "that's enough"
      When the skill writes docs/spec/scope-map.md
      Then each row includes Rule, Status, Confidence, Sources, and Feature Link columns
      And rows backed by passing tests have confidence "verified"
      And rows from docs alone have confidence "claimed"
      And the skill summarises the inventory count

    Scenario: Reverse-map seeds docs/CONTEXT.md with domain vocabulary
      Given the reverse-map skill is scanning the codebase
      When it encounters type names, class names, and module names
      Then it extracts domain vocabulary into docs/CONTEXT.md
      And the vocabulary forms the seed for arc42 chapter 12 (Glossary)

  Rule: Feature-addition deepens anchor files incrementally
    # actor: Feature Developer
    # @factory/playbooks/feature-addition.md

    Scenario: Feature-addition adds a Rule to the scope map
      Given a feature-addition runs against a brownfield-lite baseline
      When the requirements-agent derives the feature spec
      Then a new Rule is added to docs/spec/scope-map.md with status "specified"
      And the Rule links to the new .feature file

    Scenario: Feature-addition updates architecture.dsl when structural shape changes
      Given a feature changes the structural shape of the system
      When the architecture-agent runs during the feature-addition
      Then it updates docs/arc42/architecture.dsl with the new component or container
      And the DSL change is part of the same feature-addition run

    Scenario: Feature-addition grows docs/CONTEXT.md with new domain terms
      Given the grilling and domain-modeling skills surface new terms during requirements
      When terms are confirmed with the stakeholder
      Then the new terms are added to docs/CONTEXT.md
      And the vocabulary accumulates toward arc42 chapter 12

    Scenario: Feature-addition works without full specification artifacts
      Given only architecture.dsl, scope-map.md, and docs/CONTEXT.md exist
      And no full specification artifacts (PRD, UC files, supplementary specs) are present
      When a feature-addition starts
      Then the playbook proceeds with the available baseline
      And does not require or block on missing full-spec artifacts

  Rule: Feature-addition prerequisite checks anchor file presence, not a gate marker
    # actor: Feature Developer
    # @factory/playbooks/feature-addition.md

    Scenario: Feature-addition detects brownfield-lite readiness from anchor files
      Given the user starts a feature-addition
      When the playbook checks prerequisites
      Then it checks for the existence of architecture.dsl, scope-map.md, and docs/CONTEXT.md
      And does not look for a Stage 1 completion marker file

    Scenario: Feature-addition proceeds when all three anchor files exist
      Given architecture.dsl, scope-map.md, and docs/CONTEXT.md all exist
      When the playbook evaluates prerequisites
      Then the prerequisites pass
      And the feature-addition proceeds normally

    Scenario: Feature-addition reports missing anchor files
      Given one or more of the three anchor files is missing
      When the playbook evaluates prerequisites
      Then it reports which files are missing
      And suggests running brownfield-onboarding to establish the baseline
