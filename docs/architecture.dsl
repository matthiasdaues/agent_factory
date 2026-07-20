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
            validator = container "Validator" "Enforces gates, permissions, and test execution" "Bash/Python" {
                transitionLint = component "transition-lint" "Pre-commit hook blocking out-of-phase files" "Python"
                blockDangerousGit = component "block-dangerous-git.sh" "PreToolUse hook blocking destructive commands" "Bash"
                runTests = component "run-tests" "Framework-agnostic test runner for hooks" "Python"
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
        git -> runTests "Fires pre-commit (changed files), pre-push (full suite)"
        git -> blockDangerousGit "Fires PreToolUse before command execution"
        
        # Relationships - State Manager
        phaseAdvance -> stateFiles "Reads/writes marker, reads FSM"
        phaseAdvance -> runTests "Evaluates script_exit_zero entry condition"
        phaseRetry -> stateFiles "Reads/writes marker, resolves iteration cap"
        runStep -> stateFiles "Reads marker and FSM to derive next action"
        runStep -> trigger "Dispatches resolved agent"
        
        # Relationships - Validator
        transitionLint -> stateFiles "Reads marker for current state"
        runTests -> stateFiles "Invoked by phase advance script_exit_zero"
        blockDangerousGit -> cliAgent "Blocks destructive commands before execution"
        
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

        component validator "TestExecutionComponents" "Test execution validation components" {
            include *
            include git
            include phaseAdvance
            include cliAgent
            include stateFiles
            autoLayout tb
        }

        dynamic validator "TestExecutionFlow" "Test execution via hooks and phase gates" {
            humanOperator -> git "1. git commit fires pre-commit hook"
            git -> runTests "2. Pre-commit hook executes run-tests --changed-only"
            runTests -> stateFiles "3. Detects test framework from project markers"
            runTests -> git "4. Exits 0 (pass) or 1 (fail), emits JSON summary"
            
            humanOperator -> git "5. git push fires pre-push hook"
            git -> runTests "6. Pre-push hook executes run-tests --full"
            runTests -> git "7. Exits 0/1, no bypass available"
            
            humanOperator -> phaseAdvance "8. phase advance evaluates entry conditions"
            phaseAdvance -> runTests "9. Evaluates script_exit_zero gate"
            runTests -> phaseAdvance "10. Exit code determines condition met/unmet"
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
