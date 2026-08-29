workspace "Factory Flow Control" "Deterministic state-machine harness, CLI-agnostic dispatch, and generated catalog for Agent Factory playbooks" {

    model {
        # External actors
        humanOperator = person "Human Operator" "Person driving Agent Factory by hand"
        orchestrator = softwareSystem "Orchestrator CLI" "Python CLI that invokes factory mechanisms programmatically" "External"
        cliAgent = person "CLI-Invoked Agent" "Claude Code, Copilot CLI, or Pi agent session under scoped allowlist; under Pi also the caller of run_agent" "Agent"
        
        # Git as supporting actor
        git = softwareSystem "Git / pre-commit" "Version control and hook execution" "External"

        # Factory Flow Control system
        factoryFlowControl = softwareSystem "Factory Flow Control" "State machine, dispatch, and validation for Agent Factory" {
            
            # State management container
            stateManager = container "State Manager" "Reads/writes playbook state, resolves FSM transitions" "Bash/Python" {
                phaseAdvance = component "phase advance" "Advances playbook to next state when entry conditions met" "Bash"
                phaseRetry = component "phase retry" "Retries current phase within iteration cap" "Bash"
                runStep = component "run-step skill" "Derives what's next from observable state" "Markdown/LLM-executed"
            }
            
            # Validation container
            validator = container "Validator" "Enforces gates, permissions, charter-declared test gate presence, and semantic quality checks" "Bash/Python" {
                transitionLint = component "transition-lint" "Pre-commit hook blocking out-of-phase files" "Python"
                blockDangerousGit = component "block-dangerous-git.sh" "PreToolUse hook blocking destructive commands and allowlisting charter-declared test commands" "Bash"
                schemaValidate = component "schema-validate" "Deterministic JSON-Schema validator for research artifacts: stage 1 of the schema->policy->semantic validation order" "Python"
                policyValidate = component "policy-validate" "Deterministic research-policy validator: stage 2; --pipeline runs schema then policy in order, stopping at the first failure" "Python"
                crapScore = component "crap-score" "CRAP scoring gate: cyclomatic complexity weighted against test coverage, diff-scoped per story" "Bash/Python"
                dependencyCheck = component "dependency-check" "Dependency-rule enforcement gate: validates imports against architecture.dsl dependency declarations" "Bash/Python"
                moduleGraphCheck = component "module-graph-check" "Derives module map from architecture.dsl, compares against Phase 1 outputs to determine architecture phase routing" "Bash/Python"
            }
            
            # Dispatch container
            dispatcher = container "Dispatcher" "Resolves agents/models and spawns CLI sessions" "Bash/Python" {
                trigger = component "trigger" "Dispatches named agent or playbook step to CLI" "Bash"
                indexLint = component "index-lint" "Generates INDEX.yaml from frontmatter" "Python"
                runAgent = component "run-agent (Pi extension)" "Pi model-callable tool: spawns a separate pi session to run one factory agent" "TypeScript/Pi"
                dispatchWave = component "dispatch-wave (Pi extension)" "Pi model-callable tool: runs a parallel wave of factory agents, each in its own git worktree, integrating premerge-check before merging (ports implementation-agent)" "TypeScript/Pi"
                openrouterDiscover = component "openrouter-discover" "Operator aid: queries OpenRouter catalog to curate/validate pi.* tier rows in model.conf (offline of the runtime path)" "Python"
            }
            
            # Configuration and state storage
            stateFiles = container "State Files" "Local git-ignored marker and FSM definitions" "YAML files" "Storage"
            catalog = container "Catalog" "Generated INDEX.yaml of agents/skills/playbooks" "YAML file" "Storage"
        }

        # Relationships - Human Operator
        humanOperator -> git "Runs git commit, git push"
        humanOperator -> phaseAdvance "Invokes via CLI"
        humanOperator -> phaseRetry "Invokes via CLI"
        humanOperator -> trigger "Invokes via CLI"
        
        # Relationships - Orchestrator
        orchestrator -> phaseAdvance "Invokes programmatically"
        orchestrator -> phaseRetry "Invokes programmatically"
        orchestrator -> trigger "Invokes programmatically"
        
        # Relationships - Git hooks
        git -> transitionLint "Fires pre-commit"
        git -> blockDangerousGit "Fires PreToolUse before command execution"

        # Relationships - State Manager
        phaseAdvance -> stateFiles "Reads/writes marker, reads FSM; resolves charter:test_command via testing.yaml"
        phaseRetry -> stateFiles "Reads/writes marker, resolves iteration cap"
        runStep -> stateFiles "Reads marker and FSM to derive next action"
        runStep -> trigger "Dispatches resolved agent"

        # Relationships - Validator
        transitionLint -> stateFiles "Reads marker for current state"
        blockDangerousGit -> cliAgent "Blocks destructive commands before execution"
        cliAgent -> schemaValidate "Research skills/agents validate an artifact against its schema (stage 1)"
        cliAgent -> policyValidate "Research skills/agents validate artifacts against enforceable policy (stage 2)"
        policyValidate -> schemaValidate "Chains stage 1 in --pipeline mode"
        
        # Relationships - Dispatcher
        trigger -> catalog "Resolves agent/playbook by name"
        trigger -> cliAgent "Spawns CLI session with scoped allowlist"
        indexLint -> catalog "Generates/validates INDEX.yaml"
        cliAgent -> runAgent "Pi: invokes run_agent tool (no native subagents)"
        runAgent -> catalog "Resolves agent by name; tier via model.conf"
        runAgent -> cliAgent "Spawns a separate pi session for the agent"
        cliAgent -> dispatchWave "Pi: invokes dispatch_wave tool for a parallel, worktree-isolated wave"
        dispatchWave -> catalog "Resolves each item's agent by name; tier via model.conf"
        dispatchWave -> cliAgent "Spawns parallel pi sessions, one per worktree"

        # Relationships - Semantic Quality Gates (dispatcher-invoked, on-demand)
        cliAgent -> crapScore "Implementation-agent dispatcher runs after developer commit"
        cliAgent -> dependencyCheck "Implementation-agent dispatcher runs after developer commit"
        crapScore -> stateFiles "Writes JSON report to .current-work/crap-score/"
        dependencyCheck -> stateFiles "Writes JSON report to .current-work/dependency-check/"

        # Relationships - Module-graph check (orchestrating session, on-demand)
        cliAgent -> moduleGraphCheck "Orchestrating session runs at Phase 1 / Phase 3 boundary"

        # Relationships - CLI Agent
        cliAgent -> blockDangerousGit "Every shell command routed through PreToolUse (or Pi extension)"
        cliAgent -> transitionLint "Commits trigger pre-commit hooks"
    }

    views {
        systemContext factoryFlowControl "SystemContext" {
            include *
            autoLayout lr
        }

        container factoryFlowControl "Containers" {
            include *
            autoLayout lr
        }

        component validator "ValidationComponents" "Validation components: hook-triggered gates, on-demand validators, and semantic quality gates" {
            include *
            include git
            include phaseAdvance
            include cliAgent
            include stateFiles
            autoLayout tb
        }

        dynamic validator "TestGatePresence" "Charter-declared test gate presence and agent allowlist" {
            humanOperator -> phaseAdvance "1. Invokes phase advance"
            phaseAdvance -> stateFiles "2. Reads FSM; resolves charter:test_command from testing.yaml"
            phaseAdvance -> stateFiles "3. Executes resolved command, reads exit code only"
            cliAgent -> blockDangerousGit "4. Agent attempts a test command"
            blockDangerousGit -> cliAgent "5. Allows charter-declared, denies bare test commands"
        }

        dynamic validator "SemanticGateLoop" "Dispatcher-owned semantic gate execution after developer commit" {
            cliAgent -> crapScore "1. Dispatcher runs crap-score on committed artifacts"
            crapScore -> stateFiles "2. Writes CRAP report (pass/fail per function)"
            cliAgent -> dependencyCheck "3. Dispatcher runs dependency-check against architecture.dsl"
            dependencyCheck -> stateFiles "4. Writes dependency report (pass/fail per rule)"
        }

        theme default
        
        styles {
            element "Person" {
                shape Person
                background #08427B
                color #ffffff
            }
            element "Agent" {
                shape Robot
                background #8B4513
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Storage" {
                shape Cylinder
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
        }
    }
}
