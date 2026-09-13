workspace "Factory Flow Control" "Deterministic state-machine harness, CLI-agnostic dispatch, and generated catalog for Agent Factory playbooks" {

    properties {
        "arc42.projected" "true"
    }

    model {
        # External actors
        humanOperator = person "Human Operator" "Person driving Agent Factory by hand"
        orchestrator = softwareSystem "Orchestrator CLI" "Python CLI that invokes factory mechanisms programmatically" "External"
        cliAgent = person "CLI-Invoked Agent" "Claude Code, Copilot CLI, or Pi agent session under scoped allowlist; under Pi also the caller of run_agent" "Agent"
        
        # Git as supporting actor
        git = softwareSystem "Git / pre-commit" "Version control and hook execution" "External"

        # Local output selected explicitly by the operator
        parquetFile = softwareSystem "Parquet Export" "Optional, attributable, atomically replaced local export; never authoritative state" "External"

        # Factory Flow Control system
        factoryFlowControl = softwareSystem "Factory Flow Control" "State machine, dispatch, and validation for Agent Factory" {
            
            # State management container
            stateManager = container "State Manager" "Reads/writes playbook state, resolves FSM transitions" "Bash/Python" {
                phaseAdvance = component "phase advance" "Advances playbook to next state when entry conditions met" "Bash"
                phaseRetry = component "phase retry" "Retries current phase within iteration cap" "Bash"
                runStep = component "run-step skill" "Derives what's next from observable state" "Markdown/LLM-executed"
            }
            
            # Validation container
            validator = container "Validator" "Enforces gates, permissions, project-declared test gate presence, agent-context structure, and semantic quality checks" "Bash/Python" {
                transitionLint = component "transition-lint" "Pre-commit hook blocking out-of-phase files" "Python"
                blockDangerousGit = component "block-dangerous-git.sh" "PreToolUse hook blocking destructive commands and allowlisting project-declared test commands via format-detected testing.yaml" "Bash"
                contextLint = component "context-lint" "Validates agent-context YAML structure, key presence, mode compliance, source-pointer integrity, and reading-guide references (CX-* codes); falls back to charter-lint CH-* codes for legacy markdown projects" "Python"
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

            # Capture and distribution remain independent from analysis
            usageCaptureContainer = container "Usage Capture" "Normalizes CLI-native transcripts and appends versioned usage records without waiting for analysis" "Python/Shell/TypeScript" {
                usageCapture = component "usage-capture" "Normalizes one CLI transcript and appends a canonical usage record" "Python"
            }

            distribution = container "Distribution" "Installs, updates, removes, and reports opt-in Factory components" "Bash/Python" {
                initFactory = component "init-factory" "Installs, updates, or removes the usage component and maintains the install manifest" "Python"
                updateFactory = component "update-factory" "Updates Factory core and reports installed components without changing them" "Python"
                removeFactory = component "remove-factory" "Performs complete Factory removal, including analysis and raw usage data" "Python"
            }
            
            # Configuration and state storage
            stateFiles = container "State Files" "Local git-ignored marker and FSM definitions" "YAML files" "Storage"
            catalog = container "Catalog" "Generated INDEX.yaml of agents/skills/playbooks" "YAML file" "Storage"
            usageRecordContract = container "Usage Record Contract" "Factory-owned JSON Schema Draft 2020-12 and compatibility manifest" "JSON Schema/YAML" "Storage"
            rawUsageSpool = container "Raw Usage Spool" "Authoritative append-only top-level JSONL records under .agent-factory/usage/" "JSONL files" "Storage"
            installManifest = container "Install Manifest" "Records installed CLI integrations and opt-in components" "JSON file" "Storage"
        }

        # Separate bounded context: local analytical consumer
        usageAnalysis = softwareSystem "Usage Analysis" "Opt-in, local, read-only JSONL-to-DuckDB analysis with reproducible published views" {
            usageAnalysisRuntime = container "Usage Analysis Runtime" "Runs usage-query from the installed, locked Python project and owns the query model" "Python/DuckDB/PyArrow" {
                inputSnapshot = component "Input Snapshot" "Selects and normalizes a sorted, top-level JSONL input set at query start" "Python"
                contractCheck = component "Contract Check" "Validates the installed record contract, every selected line, and producer-consumer compatibility" "Python/JSON Schema"
                operationalPreflight = component "Operational Preflight" "Classifies every line, validates ancestry, and registers valid and failure relations" "Python/DuckDB"
                accountingRegistry = component "Accounting Registry" "Maps exactly four producer CLI values to their conservation rule" "Python/SQL"
                queryModel = component "Query Model v1" "Publishes six versioned DuckDB views over query-scoped relations" "DuckDB SQL"
                resultAdapters = component "Result Adapters" "Projects a published view as table, JSON, DuckDB relation, or PyArrow table" "Python"
                parquetExporter = component "Parquet Exporter" "Stages, verifies, attributes, and atomically replaces an explicit export" "Python/DuckDB"
            }

            duckdbUi = container "DuckDB UI" "Optional ephemeral localhost exploration of the same six published views; never gate evidence" "DuckDB bundled UI"
            installedAnalysis = container "Installed Analysis Module" "Versioned SQL, accounting rules, contract copy, lockfile, and executable package under .agent-factory/usage-analysis/" "Files" "Storage"
        }

        deploymentEnvironment "Release 1" {
            deploymentNode "Operator Workstation" "Single local machine; no container, database server, or remote service" "Linux/macOS" {
                deploymentNode "Factory Project" "Project checkout with a local .agent-factory directory" "Filesystem/processes" {
                    containerInstance usageCaptureContainer
                    containerInstance distribution
                    containerInstance usageRecordContract
                    containerInstance rawUsageSpool
                    containerInstance installManifest
                    containerInstance usageAnalysisRuntime
                    containerInstance duckdbUi
                    containerInstance installedAnalysis
                }
            }
        }

        # Relationships - Human Operator
        humanOperator -> git "Runs git commit, git push"
        humanOperator -> phaseAdvance "Invokes via CLI"
        humanOperator -> phaseRetry "Invokes via CLI"
        humanOperator -> trigger "Invokes via CLI"
        humanOperator -> usageAnalysisRuntime "Runs usage-query locally"
        humanOperator -> inputSnapshot "Starts a stable local query"
        humanOperator -> parquetExporter "Requests an explicit Parquet export"
        humanOperator -> duckdbUi "Optionally explores published views"
        humanOperator -> initFactory "Installs, updates, or removes the usage component"
        
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
        cliAgent -> contextLint "Validate skill or pre-commit hook invokes context-lint on agent-context files"
        git -> contextLint "Fires pre-commit"
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

        # Relationships - Usage capture and Factory-owned contract
        cliAgent -> usageCapture "Supplies CLI-native transcript and invocation context"
        usageCapture -> usageRecordContract "Produces records governed by"
        usageCapture -> rawUsageSpool "Appends canonical records"

        # Relationships - Usage component distribution
        initFactory -> usageRecordContract "Copies the compatible contract into the component"
        initFactory -> installedAnalysis "Installs, updates, or removes without touching raw data"
        initFactory -> installManifest "Records installed_components.usage"
        updateFactory -> installManifest "Reports component presence without changing it"
        removeFactory -> installedAnalysis "Removes during complete uninstall"
        removeFactory -> rawUsageSpool "Deletes during complete uninstall"

        # Relationships - Local usage analysis
        usageAnalysisRuntime -> installedAnalysis "Loads locked code, SQL, accounting rules, and contract copy"
        inputSnapshot -> rawUsageSpool "Snapshots sorted top-level JSONL paths read-only"
        inputSnapshot -> contractCheck "Supplies normalized evidence positions and records"
        contractCheck -> operationalPreflight "Supplies valid rows and structured failures"
        operationalPreflight -> accountingRegistry "Supplies valid rooted run graphs"
        accountingRegistry -> queryModel "Applies CLI-specific conservation rules"
        operationalPreflight -> queryModel "Registers query-scoped valid and failure relations"
        queryModel -> resultAdapters "Supplies selected published view"
        queryModel -> parquetExporter "Supplies selected published view"
        parquetExporter -> parquetFile "Atomically replaces after round-trip verification"
        duckdbUi -> queryModel "Explores the same published views locally"

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

        component usageAnalysisRuntime "UsageAnalysisComponents" "Local query pipeline from immutable evidence to versioned results" {
            include *
            include humanOperator
            include rawUsageSpool
            include installedAnalysis
            include parquetFile
            include duckdbUi
            autoLayout lr
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

        dynamic usageAnalysisRuntime "UsageQuery" "Strict local usage query and optional result projection" {
            humanOperator -> inputSnapshot "1. Invokes usage-query for a published view"
            inputSnapshot -> rawUsageSpool "2. Snapshots sorted top-level JSONL evidence"
            inputSnapshot -> contractCheck "3. Supplies normalized evidence and records"
            contractCheck -> operationalPreflight "4. Registers valid rows and structured failures"
            operationalPreflight -> accountingRegistry "5. Supplies a valid rooted run graph"
            accountingRegistry -> queryModel "6. Applies the registered conservation rule"
            operationalPreflight -> queryModel "7. Registers valid and failure relations"
            queryModel -> resultAdapters "8. Projects the selected published view"
        }

        dynamic usageAnalysisRuntime "UsageParquetExport" "Verified explicit Parquet replacement" {
            humanOperator -> parquetExporter "1. Requests a published view as Parquet"
            queryModel -> parquetExporter "2. Supplies the selected stable view"
            parquetExporter -> parquetFile "3. Replaces the destination after verification"
        }

        deployment * "Release 1" "Deployment" "Local, process-bound release-1 deployment" {
            include *
            autoLayout lr
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
