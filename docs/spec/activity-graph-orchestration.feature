# scope: global
Feature: Activity-graph orchestration

  Replace stage-based orchestration with a precondition graph over
  activities and artifacts. The system tracks what artifacts exist and
  what shape they are in. Agents declare their prerequisites. The system
  shows what can run next given the current repository state. No named
  stages, no transition matrix, no state machine. The sequence emerges
  from the dependency chain.

  Proposal trace: docs/proposals/activity-graph-orchestration.md
  Supersedes: docs/spec/cycle-based-orchestration.feature

  Rule: Session menu presents four lanes
    # actor: Human operator
    # @packages/factory/config/session-menu.md

    Scenario: Menu displays Help, Housekeeping, Project Work, and Open Stage
      Given the factory session starts with no fitting pending
      When the session menu is displayed
      Then the menu offers lane H for Help
      And the menu offers lane K for Housekeeping
      And the menu offers lane P for Project Work
      And the menu offers lane O for Open Stage

    Scenario: Help lane routes to tour skills
      Given the session menu is displayed
      When the human selects lane H
      Then the session routes to the newcomer-tour or guided-tour skill

    Scenario: Concept explanation is available at any point
      Given the session is active in any lane
      When the human asks "what is [concept]?"
      Then the explain-concept skill looks up the concept and explains it
      # @packages/factory/skills/explain-concept/SKILL.md

    Scenario: Open Stage opens freeform conversation under VIRGIL
      Given the session menu is displayed
      When the human selects lane O
      Then the VIRGIL agent enters freeform conversation with no structure
      And no workstream binding is created
      And VIRGIL routes to the appropriate skill or agent when the conversation reaches a concrete next step
      # @packages/factory/agents/virgil.md

  Rule: Housekeeping shows factory state and offers maintenance actions
    # actor: Human operator

    Scenario: About section displays factory state
      Given the human selects lane K
      When the Housekeeping lane opens
      Then the About section shows the installed Factory version
      And the About section shows the fitting status
      And the About section shows configured CLI integrations
      And the About section shows usage pipeline health
      And unreadable values appear as unknown with their source error

    Scenario: Re-fit reruns all five fitting steps
      Given the Housekeeping lane is open
      When the human selects Re-fit
      Then the factory runs the complete five-step fitting procedure
      And the factory reports the resulting completed and remaining fitting steps

    Scenario: Update Factory runs init-factory and refreshes About
      Given the Housekeeping lane is open
      When the human selects Update Factory
      Then the factory runs .agent-factory/factory/scripts/init-factory --update <project-root> --force
      And the factory relays the command output and exit status
      And the About section refreshes after success

    Scenario: Update agent context invokes interactive scan
      Given the Housekeeping lane is open
      And docs/agent-context.md exists
      When the human selects Update agent context
      Then the factory invokes capture-context --update --scan
      And discovered differences in concerns and Read paths are presented
      And changes are written only after human confirmation
      And .agent-factory/factory/scripts/concern-lint passes after writing

    Scenario: Update agent context without existing file directs to init
      Given the Housekeeping lane is open
      And docs/agent-context.md does not exist
      When the human selects Update agent context
      Then the factory directs the human to capture-context --init --scan
      And no file is written

  Rule: Human operator starts a new workstream
    # actor: Human operator

    Scenario: Project Work lane creates a named workstream
      Given the human selects lane P
      And no workstream is bound
      When the human provides a topic description
      Then a workstream state file is created under .agent-factory/workstreams/
      And the state file records workstream_id, topic, and origin_ref
      And no cycle, attempt, delegation, or work field exists in the state file

    Scenario: Workstream state file records the proposal origin when one exists
      Given the human provides a topic and names an existing proposal
      When the workstream state file is created
      Then the origin_ref field contains the proposal path

  Rule: Human operator continues an existing workstream
    # actor: Human operator

    Scenario: Project Work lane lists current workstreams
      Given at least one workstream state file exists under .agent-factory/workstreams/
      When the human selects lane P and chooses to continue
      Then each workstream topic is displayed
      And the human selects a workstream from the list

    Scenario: Selected workstream binds to the session and shows precondition evidence
      Given the human selects a workstream from the list
      When the session binding is created
      Then the precondition evaluator checks all agents against the repository
      And all agents are presented with their requirement evidence

    Scenario: No workstreams exist when continuing is selected
      Given no workstream state files exist under .agent-factory/workstreams/
      When the human chooses to continue
      Then the factory offers to start a new workstream or return to the menu
      And the factory does not select a workstream automatically

  Rule: Agent definition declares required and contextual inputs
    # actor: Agent definition author
    # @packages/factory/agents

    Scenario: Agent frontmatter carries structured inputs
      Given an agent definition file exists
      When the definition is parsed
      Then inputs.required lists artifacts with type, path_pattern, and conditions
      And inputs.context lists plain paths to reading material
      And outputs lists paths the agent creates or modifies

    Scenario: Required input with conditions checks frontmatter fields
      Given an agent definition declares a required input with condition field: status, value: accepted
      When the evaluator checks the input
      Then the evaluator reads the target artifact YAML frontmatter
      And the evaluator compares the field value against the declared condition

    Scenario: Required input with one_of condition accepts any listed value
      Given an agent definition declares a required input with condition field: status, one_of: [accepted, revised]
      When the evaluator checks the input
      Then the evaluator accepts the artifact when the field value matches any entry in the list

    Scenario: Required input with check condition that passes marks the requirement satisfied
      Given an agent definition declares a required input with condition check: spec-lint
      And the validator returns a passing result
      When the evaluator checks the input
      Then the requirement is marked satisfied with the validator result as evidence

    Scenario: Required input with check condition that fails marks the requirement unsatisfied
      Given an agent definition declares a required input with condition check: spec-lint
      And the validator returns a failing result
      When the evaluator checks the input
      Then the requirement is marked unsatisfied with the validator result as evidence
      And the human can still select the agent

    Scenario: Required input with no conditions checks file existence only
      Given an agent definition declares a required input with no conditions key
      When the evaluator checks the input
      Then the evaluator checks that the file exists
      And no frontmatter or validator check runs

  Rule: Skill definition carries contextual inputs only
    # actor: Skill definition author

    Scenario: Skill frontmatter uses inputs.context without inputs.required
      Given a skill definition file exists
      When the definition is parsed
      Then inputs.context lists paths to reading material
      And inputs.required is absent
      And the skill does not appear in the precondition graph

  Rule: Precondition evaluator checks agent inputs against the repository
    # actor: Precondition evaluator
    # @packages/factory/engine/eligibility.py

    Scenario: Evaluator reports evidence for every agent
      Given agent definitions with inputs.required declarations exist
      When the evaluator runs
      Then the evaluator returns evidence for every agent
      And each required input is marked satisfied or unsatisfied
      And evidence includes the checked path, condition, and result

    Scenario: Agent with all required inputs satisfied is reported as eligible
      Given an agent declares two required inputs
      And both inputs exist and satisfy their conditions
      When the evaluator runs
      Then the agent is reported with all requirements satisfied

    Scenario: Agent with one unsatisfied required input is reported with evidence
      Given an agent declares two required inputs
      And one input exists and one does not
      When the evaluator runs
      Then the agent is reported with one requirement satisfied and one unsatisfied
      And the unsatisfied requirement names the missing artifact

    Scenario: Agent with no required inputs is always eligible
      Given an agent declares no inputs.required
      When the evaluator runs
      Then the agent is reported with all requirements satisfied

  Rule: Precondition evaluator resolves path patterns with scope filtering
    # actor: Precondition evaluator

    Scenario: Placeholder in path pattern expands to glob
      Given an agent declares path_pattern "docs/proposals/{name}.md"
      When the evaluator resolves the pattern
      Then the evaluator replaces {name} with * and expands against the filesystem
      And every matching file is a candidate

    Scenario: Scope filtering narrows candidates when a workstream is bound
      Given a workstream is bound with identifier W1
      And two proposals exist with scope W1 and scope W2
      When the evaluator resolves a path pattern
      Then only the proposal with scope W1 or scope global survives filtering

    Scenario: Scope filtering is skipped in Open Stage
      Given no workstream is bound
      When the evaluator resolves a path pattern
      Then all matching files are candidates regardless of scope

    Scenario: Condition checking removes failing candidates
      Given two proposals survive scope filtering
      And one has status accepted and one has status draft
      And the condition requires field status value accepted
      When the evaluator checks conditions
      Then the draft proposal is removed
      And the accepted proposal survives

    Scenario: Zero survivors means unsatisfied precondition
      Given a path pattern matches no files after filtering
      When the evaluator counts survivors
      Then the precondition is unsatisfied

    Scenario: One survivor satisfies the precondition
      Given a path pattern matches exactly one file after filtering
      When the evaluator counts survivors
      Then the precondition is satisfied against that file

    Scenario: Multiple survivors are reported for human selection
      Given a path pattern matches two files after filtering and conditions
      When the evaluator counts survivors
      Then the evaluator reports both candidates
      And the human picks one or an external orchestrator supplies an explicit artifact selection

  Rule: Graph-addressable artifact carries a scope declaration
    # actor: Artifact author

    Scenario: Proposal carries scope in place of title in YAML frontmatter
      Given a proposal exists under docs/proposals/
      When the scope lint runs
      Then the proposal YAML frontmatter contains a scope field
      And the scope value is the workstream identifier matching the proposal filename
      And no title field exists in the frontmatter
      And the display name is carried in the document heading

    Scenario: Epic carries scope in YAML frontmatter
      Given an epic exists under backlog/
      When the scope lint runs
      Then the epic YAML frontmatter contains a scope field

    Scenario: Story carries scope in YAML frontmatter
      Given a story exists under backlog/
      When the scope lint runs
      Then the story YAML frontmatter contains a scope field

    Scenario: Gherkin feature file carries scope as first-line comment
      Given a feature file exists under docs/spec/
      When the scope lint runs
      Then the first line is a comment in the form "# scope: <value>"

    Scenario: Structurizr DSL carries scope as first-line comment
      Given docs/arc42/architecture.dsl exists
      When the scope lint runs
      Then the first line is a comment in the form "// scope: global"

    Scenario: Entity model carries scope as top-level YAML field
      Given docs/spec/entity-model.yaml exists
      When the scope lint runs
      Then the top-level YAML contains a scope field

    Scenario: Scope map carries scope in YAML frontmatter
      Given docs/spec/scope-map.md exists
      When the scope lint runs
      Then the scope-map YAML frontmatter contains a scope field with value global

    Scenario: Governed artifact without scope declaration fails lint
      Given a proposal exists without a scope field in its frontmatter
      When the scope lint runs at artifact creation time
      Then lint rejects the artifact and names the missing declaration

    Scenario: Governed artifact with unknown scope value fails lint
      Given a proposal carries scope: nonexistent-workstream
      And no workstream with that identifier exists
      When the scope lint runs
      Then lint rejects the artifact and names the unknown value

    Scenario: Non-governed artifact needs no scope declaration
      Given an ADR exists under docs/adr/
      When the scope lint runs
      Then no scope check applies to the ADR

  Rule: Human operator sees all agents with precondition evidence
    # actor: Human operator

    Scenario: All agents displayed after workstream binding
      Given the session is bound to a workstream
      When the precondition evaluator completes
      Then every agent is listed with its name and description
      And each agent shows each required input as satisfied or unsatisfied
      And satisfied inputs show the matched artifact path
      And unsatisfied inputs show what is missing

    Scenario: Agents with all inputs satisfied are distinguishable from others
      Given three agents exist and one has all inputs satisfied
      When the agent list is displayed
      Then the human can distinguish eligible agents from ineligible ones

  Rule: Human operator selects any agent regardless of precondition status
    # actor: Human operator

    Scenario: Human selects an agent with all inputs satisfied
      Given an agent has all required inputs satisfied
      When the human selects that agent
      Then the agent is dispatched without warning

    Scenario: Human selects an agent with unsatisfied inputs
      Given an agent has one unsatisfied required input
      When the human selects that agent
      Then the evaluator reports the unsatisfied requirements
      And the agent is dispatched without requiring an override

    Scenario: No override flag or justification is required
      Given an agent has unsatisfied inputs
      When the human selects it
      Then no confirmation dialog, override flag, or justification field is presented

  Rule: Every agent activity is fenced by a deterministic check
    # actor: Precondition evaluator

    Scenario: Agent outputs are validated by a deterministic fence after completion
      Given an agent declares outputs
      And a deterministic check exists for the output artifact type
      When the agent activity completes
      Then the fence runs the applicable lint, validator, or formatter against the outputs
      And the fence result is recorded as evidence

    Scenario: Fence pass makes downstream preconditions satisfiable
      Given an agent activity completes and its output fence passes
      When the evaluator checks downstream agents
      Then the fenced outputs satisfy downstream required inputs
      And evidence includes the fence result

    Scenario: Fence failure is reported without blocking human action
      Given an agent activity completes and its output fence fails
      When the evaluator checks downstream agents
      Then the failed fence is reported as unsatisfied evidence
      And the human can still select any agent

    Scenario: Chaining happens externally when fences pass
      Given an agent activity completes and its fence passes
      And exactly one downstream agent has all required inputs satisfied
      When an external orchestrator or the human inspects the evaluator evidence
      Then the next activity can be dispatched by the orchestrator or selected by the human
      And no internal delegation mechanism is involved

  Rule: Human operator fixes an upstream artifact without transition ceremony
    # actor: Human operator

    Scenario: Fixing an artifact requires no state update
      Given a grilling session discovers a flaw in the specification
      When the human edits the specification artifact
      Then no workstream state transition is needed
      And no ceremony or reconciliation step is triggered

    Scenario: Re-evaluation reflects the fix
      Given the human fixed an upstream artifact
      When the precondition evaluator runs again
      Then the evaluator checks the current repository state
      And the requirement evidence reflects the fixed artifact

  Rule: Workstream state file is immutable after creation
    # actor: Workstream manager

    Scenario: Workstream state file contains only identity fields
      Given a workstream is created with topic T and origin_ref R
      When the state file is written
      Then the file contains schema_version: 2, workstream_id, topic, and origin_ref
      And no other fields exist

    Scenario: Attempted modification of an existing state file fails
      Given a workstream state file exists
      When a process attempts to modify the file
      Then the modification fails without changing the file

    Scenario: Multiple sessions bind to the same workstream
      Given a workstream state file exists
      When session S1 and session S2 both bind to the workstream
      Then both sessions create separate session binding files
      And the workstream state file is unchanged

  Rule: Session binding attaches a session to a workstream
    # actor: Session manager

    Scenario: Session binding file records binding metadata
      Given a session binds to a workstream
      When the binding file is created at .agent-factory/workstreams/sessions/<session-id>.yaml
      Then the file records the session_id, workstream_id, and bound_at timestamp
      And the workstream_id key is always present
      And a known workstream identifier means bound
      And explicit null means Open Stage
      And a missing workstream_id key fails validation

    Scenario: Session binding dies with the session
      Given a session binding file exists
      When the session ends
      Then the binding file is no longer active
      And the next session creates a fresh binding

  Rule: Intent select lists all agents with precondition status
    # actor: Human operator
    # @packages/factory/scripts/intent

    Scenario: intent select lists every agent with its precondition status
      Given agent definitions with inputs.required exist
      When the human runs intent select
      Then every agent is listed
      And each agent shows its required inputs as satisfied or unsatisfied

    Scenario: intent select shows evidence for each requirement
      Given an agent has a required input with condition field: status, value: accepted
      And the target artifact has status: accepted
      When the human runs intent select
      Then the requirement is shown as satisfied with the matched artifact path

  Rule: Intent assess runs validators and reports results
    # actor: Human operator

    Scenario: intent assess runs all applicable validators
      Given artifacts exist on disk
      When the human runs intent assess
      Then each validator returns artifact type, artifact reference, assessed commit, individual checks, and warnings
      And the result follows the shared validator result format

    Scenario: Mechanical validation checks file existence and format
      Given a governed artifact exists
      When intent assess runs mechanical validation
      Then the validator checks file existence, format lint, and required fields

  Rule: Usage capture retains structured transcripts
    # actor: Usage capture pipeline

    Scenario: Structured transcript is retained alongside text rendering
      Given transcript retention is set to full
      When the usage capture pipeline processes a session
      Then a structured JSONL file is written alongside the text rendering
      And the structured file is a verbatim copy of the source transcript

    Scenario: Both files are stored under the same session key
      Given a structured transcript is retained
      When the files are written
      Then both files exist under .agent-factory/usage/transcripts/<session-key>/

    Scenario: Omit retention writes neither file
      Given transcript retention is set to omit
      When the usage capture pipeline processes a session
      Then no text rendering and no structured transcript is written

  Rule: Factory content consolidates under .agent-factory/
    # actor: Factory installer
    # @packages/factory/scripts/init-factory

    Scenario: Installed factory tree lives under .agent-factory/factory/
      Given init-factory completes
      When the project root is inspected
      Then .agent-factory/factory/ contains scripts, agents, skills, rulebooks, and engine
      And no top-level factory/ directory exists

    Scenario: Project configuration lives under .agent-factory/config/
      Given init-factory completes
      When the project root is inspected
      Then .agent-factory/config/ contains project-context.json and testing.yaml
      And no top-level config/ directory exists

    Scenario: Workstream state files live under .agent-factory/workstreams/
      Given a workstream is created
      When the state file is written
      Then the file is at .agent-factory/workstreams/<workstream-id>.yaml

    Scenario: Session bindings live under .agent-factory/workstreams/sessions/
      Given a session binds to a workstream
      When the binding file is written
      Then the file is at .agent-factory/workstreams/sessions/<session-id>.yaml

    Scenario: Quality gate results live under .agent-factory/checks/
      Given a deterministic check runs
      When the result is written
      Then the file is under .agent-factory/checks/

    Scenario: Usage pipeline state lives under .agent-factory/usage/
      Given the usage pipeline is active
      When the pipeline writes state
      Then records are under .agent-factory/usage/records/
      And transcripts are under .agent-factory/usage/transcripts/
      And control state is under .agent-factory/usage/control/
      And the query database is at .agent-factory/usage/store.duckdb

    Scenario: .current-work/ remains the runtime root
      Given .current-work/ contains linked worktrees, dispatch ledgers, and verification markers
      When folder consolidation completes
      Then .current-work/ retains all existing path contracts
      And branching, worktree, and dispatch-ledger paths are unchanged

    Scenario: Internal naming drops the factory- prefix
      Given init-factory completes
      When .agent-factory/ is inspected
      Then install.json exists instead of factory-install.json
      And checksums.json exists instead of factory-checksums.json

  Rule: Orchestrator package is retired
    # actor: Factory maintainer

    Scenario: packages/orchestrator/ does not exist
      Given folder consolidation and orchestrator retirement complete
      When the project tree is inspected
      Then packages/orchestrator/ does not exist

    Scenario: No references to orchestrator remain
      Given the orchestrator is retired
      When documentation, backlog stories, and CI configuration are inspected
      Then no file references the orchestrator package

    Scenario: Still-needed tests are migrated
      Given orchestrator tests covered behavior the factory engine still needs
      When the retirement completes
      Then those tests exist under packages/factory/engine/ or the appropriate package

  Rule: Cycle-based orchestration proposal is superseded
    # actor: Factory maintainer

    Scenario: Superseded proposal carries status superseded
      Given docs/proposals/cycle-based-orchestration.md exists
      When the activity-graph work completes
      Then the proposal frontmatter status is superseded

  Rule: Kept contracts preserve acceptance-commit behavior
    # actor: Compatibility verifier

    Scenario: Standard check commands retain their contracts
      Given the acceptance commit defines deterministic checks
      When characterization tests run after migration
      Then every standard check retains its command name, triggers, result format, and exit behavior

    Scenario: Branch safety commands retain their contracts
      Given verify-base and premerge-check exist at the acceptance commit
      When characterization tests run after migration
      Then both commands retain their existing contract

    Scenario: Every indexed agent and skill name from the acceptance commit still exists
      Given the INDEX.yaml at the acceptance commit lists agent and skill names
      When the compatibility check runs after migration
      Then every listed name still exists in the post-migration index

  Rule: Rework requires no transition or state update
    # actor: Human operator

    Scenario: Fixing an upstream artifact is just fixing an artifact
      Given an agent discovers a concept-level flaw during implementation work
      When the human edits the upstream artifact directly
      Then no cycle transition, reconciliation evidence, or state-machine update is needed

    Scenario: The dependency graph has no forward direction to violate
      Given the precondition graph is computed from inputs.required and outputs
      When the human works on any artifact at any time
      Then no direction constraint is checked
      And no stage-ordering violation is possible

  Rule: Research brief uses the precondition graph for routing
    # actor: Research user

    Scenario: Research agent output satisfies downstream preconditions
      Given a research agent produces a research report
      And another agent declares that report as a required input
      When the evaluator checks the downstream agent
      Then the requirement is satisfied by the research output

    Scenario: Research brief omits cycle-vocabulary fields
      Given a research brief is created
      When the brief is inspected
      Then no origin_cycle or return_cycle field exists

  Rule: Single delivery sequence completes under the activity model
    # actor: Human operator

    Scenario: Proposal through implementation without named stage transitions
      Given an accepted proposal exists
      When the human follows the precondition chain through specification, architecture, planning, and implementation
      Then each activity is selected based on satisfied preconditions
      And no named stage transition occurs at any point
