# scope: global
Feature: OpenCode CLI integration

  Add OpenCode V2 as a fifth Factory CLI target. A project maintainer
  installs the Factory for OpenCode, and OpenCode users run Factory
  agents, skills, and workflows with plugin-enforced permissions, step
  boundaries, usage capture, and worktree-isolated dispatch.

  Proposal trace: docs/proposals/opencode-cli-integration.md

  Rule: Project maintainer installs Factory for OpenCode CLI
    # actor: Project maintainer
    # @packages/factory/scripts/init-factory

    Scenario: Auto-detection selects OpenCode when its markers exist
      Given a project contains a .opencode/ directory
      When init-factory runs without --cli
      Then init-factory selects OpenCode as an active CLI target

    Scenario: Auto-detection selects OpenCode from opencode.json
      Given a project contains opencode.json but no .opencode/ directory
      When init-factory runs without --cli
      Then init-factory selects OpenCode as an active CLI target

    Scenario: Auto-detection selects OpenCode from opencode.jsonc
      Given a project contains opencode.jsonc but no .opencode/ directory
      When init-factory runs without --cli
      Then init-factory selects OpenCode as an active CLI target

    Scenario: Explicit CLI selection installs OpenCode
      Given the project has no OpenCode markers
      When init-factory runs with --cli opencode
      Then init-factory creates the .opencode/ directory structure
      And init-factory links the Factory catalog into .opencode/INDEX.yaml
      And init-factory links the Factory plugin into .opencode/plugins/
      And init-factory generates agent definitions under .opencode/agents/
      And init-factory places skills under .agents/skills/ for native discovery
      And init-factory records every created OpenCode path in .agent-factory/install.json

    Scenario: Installer rejects an unsupported OpenCode version
      Given the installed OpenCode CLI version is older than 1.18.31
      When init-factory runs with --cli opencode
      Then init-factory stops before creating any OpenCode path
      And init-factory prints an upgrade instruction naming the minimum version

    Scenario: Installer accepts a supported OpenCode version
      Given the installed OpenCode CLI version is 1.18.31 or later
      When init-factory runs with --cli opencode
      Then init-factory proceeds with the OpenCode installation

    Scenario: Repeated installation produces no additional changes
      Given init-factory has completed an OpenCode installation
      When init-factory runs again with the same arguments
      Then init-factory exits successfully without creating or modifying files

    Scenario: Installer preserves user-owned files under .opencode/
      Given .opencode/ contains user-created configuration files
      When init-factory runs with --cli opencode
      Then the user-created files remain unchanged after installation

    Scenario: Documentation records OpenCode support
      Given an OpenCode installation completes
      Then packages/factory/docs/factory-guide.md lists the supported OpenCode version
      And packages/factory/docs/factory-guide.md describes the plugin trust model
      And packages/factory/docs/factory-guide.md describes the host-authority limitation
      And packages/factory/README.md lists OpenCode as a supported CLI
      # @packages/factory/docs/factory-guide.md
      # @packages/factory/README.md

  Rule: Project maintainer updates an existing OpenCode integration
    # actor: Project maintainer
    # @packages/factory/scripts/init-factory

    Scenario: Update refreshes Factory-owned OpenCode files
      Given init-factory previously installed OpenCode support
      When init-factory runs with --cli opencode after a Factory version change
      Then init-factory updates Factory-owned files under .opencode/
      And init-factory preserves user-owned files under .opencode/

  Rule: Project maintainer removes Factory OpenCode files cleanly
    # actor: Project maintainer

    Scenario: remove-factory removes Factory-owned OpenCode entries
      Given init-factory previously installed OpenCode support
      When remove-factory runs
      Then remove-factory deletes every path recorded in .agent-factory/install.json for OpenCode
      And remove-factory leaves user-owned OpenCode configuration intact

  Rule: Project maintainer runs OpenCode alongside other Factory CLIs
    # actor: Project maintainer
    # @packages/factory/scripts/init-factory
    # @packages/factory/config/AGENTS.md

    Scenario: Pi, Codex, and OpenCode coexist with one root AGENTS.md
      Given a project uses Pi, Codex, and OpenCode
      When init-factory installs all three CLIs
      Then one valid root AGENTS.md exists
      And OpenCode receives its dedicated orientation through the Factory plugin
      And Pi receives its orientation through the root AGENTS.md
      And Codex receives its orientation through the root AGENTS.md

    Scenario: Adding OpenCode to an existing multi-CLI project
      Given a project already has Claude Code and Pi installed
      When init-factory runs with --add opencode
      Then OpenCode files are created under .opencode/
      And existing Claude Code files under .claude/ remain unchanged
      And existing Pi files under .pi/ remain unchanged

  Rule: OpenCode user enters Factory through plugin-injected orientation
    # actor: OpenCode user

    Scenario: Plugin injects Factory orientation into system context
      Given the Factory plugin is loaded in an OpenCode session
      When the session context is assembled
      Then the plugin injects AGENTS.opencode.md into the system context
      And the orientation describes OpenCode tool names and child-session behavior
      And the orientation describes skill discovery paths
      And the orientation describes the session-start procedure

    Scenario: Orientation does not use legacy instructions field
      Given the Factory plugin is loaded
      When the plugin injects orientation
      Then the orientation does not depend on the legacy instructions configuration field
      And the orientation does not replace the root AGENTS.md

  Rule: OpenCode user discovers agents and skills through native paths
    # actor: OpenCode user

    Scenario: Agents are discoverable under .opencode/agents/
      Given init-factory has installed OpenCode support
      When an OpenCode session starts
      Then agents listed in .opencode/INDEX.yaml are discoverable under .opencode/agents/

    Scenario: Skills are discoverable under .agents/skills/
      Given init-factory has installed OpenCode support
      When an OpenCode session starts
      Then skills listed in .opencode/INDEX.yaml are discoverable under .agents/skills/

    Scenario: Generated agent definitions carry OpenCode-specific fields
      Given init-factory generates an agent definition for OpenCode
      Then the definition includes the agent's OpenCode mode
      And the definition includes the agent's model tier
      And the definition includes the agent's permissions

    Scenario: AGENTS.md CLI table includes OpenCode
      Given the shared AGENTS.md is updated for OpenCode
      Then the CLI detection table includes OpenCode with .opencode/INDEX.yaml
      # @packages/factory/config/AGENTS.md

  Rule: Factory plugin enforces permissions and step boundaries
    # actor: Factory plugin (system)

    Scenario: Plugin applies ordered allow, ask, and deny rules
      Given the Factory plugin is active in an OpenCode session
      When a tool invocation occurs
      Then the plugin evaluates allow rules first
      And the plugin evaluates ask rules second
      And the plugin evaluates deny rules last
      And explicit denials are final

    Scenario: Pre-tool hook rejects a read outside the step manifest
      Given an active step manifest declares specific input paths
      When the agent requests a read of a path not in the manifest
      Then the plugin denies the read before tool execution

    Scenario: Pre-tool hook rejects a write outside the step manifest
      Given an active step manifest declares specific output paths
      When the agent requests a write to a path not in the manifest
      Then the plugin denies the write before tool execution

    Scenario: Dangerous Git command is denied before shell execution
      Given the plugin carries a deny rule for destructive Git commands
      When the agent invokes a shell command matching a denied Git pattern
      Then the plugin denies the command before execution

    Scenario: Review agent receives read-only permissions
      Given an agent definition declares no write outputs
      When the agent is activated in an OpenCode session
      Then the plugin removes write tools from the agent's tool set

    Scenario: Plugin never broadens a configured denial
      Given OpenCode has a configured deny rule for a path
      When the plugin's permission hook evaluates a request for that path
      Then the plugin does not change the deny effect to allow or ask

    Scenario: Tool removal restricts the active agent's tool set
      Given an agent definition declares a restricted tool set
      When the agent's session context is assembled
      Then the plugin removes tools not in the agent's declared set

    Scenario: Child sessions inherit session-scoped restrictions
      Given the root session has plugin-enforced restrictions
      When a child session starts
      Then the child session inherits the root session's restrictions
      And the child session applies its own generated agent permissions

    Scenario: Plugin fails closed on initialization failure
      Given the Factory plugin cannot complete its setup
      When the OpenCode session starts
      Then the Factory entry flow stops
      And the error names the failed control and the recovery action

    Scenario: Plugin fails closed on manifest loading failure
      Given an active step manifest cannot be read or parsed
      When a tool invocation occurs
      Then the plugin denies the invocation
      And the error names the manifest loading failure

    Scenario: Plugin fails closed on permission evaluation failure
      Given the permission evaluation hook encounters an error
      When a tool invocation occurs
      Then the plugin denies the invocation
      And the error names the evaluation failure

    Scenario: Plugin error names recovery action
      Given the Factory plugin detects an unhealthy state
      When the plugin reports the error
      Then the error message names the specific failed control
      And the error message names the recovery action

  Rule: Factory plugin captures completed session usage
    # actor: Factory plugin (system)

    Scenario: Completed root session produces a usage record
      Given the Factory plugin observes a root session
      When the root session completes
      Then the plugin sends the session's usage to the existing Factory usage pipeline
      And the usage record follows the existing usage contract

    Scenario: Completed child session produces a usage record
      Given the Factory plugin observes a child session
      When the child session completes
      Then the plugin sends the child session's usage to the existing Factory usage pipeline

    Scenario: Child usage is not counted twice
      Given a root session spawns a child session
      When both sessions complete
      Then the root session's usage record does not include the child session's usage

    Scenario: Session completion does not reactivate the agent
      Given a session completes and usage is captured
      Then the session remains complete
      And no completion gate specific to OpenCode is introduced

    Scenario: Usage capture failure does not block the session
      Given the usage pipeline is unreachable or returns an error
      When a session completes
      Then the session completes normally
      And the plugin reports the usage capture failure without blocking

  Rule: Factory plugin isolates child sessions in Factory-managed worktrees
    # actor: Factory plugin (system)

    Scenario: Plugin registers a Factory worktree strategy
      Given the Factory plugin initializes in an OpenCode session
      Then the plugin registers a worktree strategy through OpenCode's worktree API
      And the strategy delegates branch creation to Factory scripts
      And the strategy delegates worktree creation to Factory scripts
      And the strategy delegates path and verification rules to Factory scripts

    Scenario: Each dispatched child runs in its own branch and worktree
      Given a child session is dispatched for implementation work
      When the plugin creates the child session's workspace
      Then the child receives its own Factory branch
      And the child receives its own Git worktree under .current-work/<feature-branch>/

    Scenario: Each dispatched child verifies its declared base
      Given a child session starts in its assigned worktree
      When the child's first tool call executes
      Then the child verifies its declared base commit before reading or changing files

    Scenario: Primary checkout rejects writes while isolated work is active
      Given a child session is running in an isolated worktree
      When the root session attempts a write to the primary checkout
      Then the plugin denies the write with a session-scoped write denial

    Scenario: Plugin fails closed on worktree creation failure
      Given the worktree strategy encounters an error during creation
      When a child session dispatch is requested
      Then the plugin denies the dispatch
      And the error names the worktree creation failure and recovery action

  Rule: Fitting operator configures OpenCode model tiers
    # actor: Fitting operator
    # @packages/factory/config/model.conf

    Scenario: model.conf gains OpenCode entries for three tiers
      Given the fitting flow runs for an OpenCode project
      When the operator configures model tiers
      Then model.conf contains opencode.economy with a provider/model identifier
      And model.conf contains opencode.standard with a provider/model identifier
      And model.conf contains opencode.strong with a provider/model identifier

    Scenario: Fitting presents OpenCode model identifiers in provider/model form
      Given the fitting flow configures OpenCode model tiers
      When the operator selects a model
      Then the model identifier follows the provider/model format

    Scenario: Missing model mapping halts
      Given a required model tier has no OpenCode mapping in model.conf
      When an agent requiring that tier is dispatched
      Then the model resolver halts with the existing halt policy

    Scenario: Plugin sets model per child session explicitly
      Given the model inheritance bug prevents runtime model inheritance
      When a child session is created
      Then each generated OpenCode agent definition carries a model field
      And the model field is derived from the agent's tier mapping in model.conf
