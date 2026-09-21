// scope: global
workspace "Agent Factory" "Precondition-based agent eligibility, dispatch, validation, and usage capture for Agent Factory" {

    properties {
        "arc42.projected" "true"
    }

    model {
        # External actors
        humanOperator = person "Human Operator" "Person driving Agent Factory by hand"
        cliAgent = person "CLI-Invoked Agent" "Claude Code, Copilot CLI, Pi, or OpenCode agent session under scoped allowlist; under Pi also the caller of run_agent, under OpenCode controlled by Factory plugin" "Agent"

        # Git as supporting actor
        git = softwareSystem "Git / pre-commit" "Version control and hook execution" "External"

        # Local output selected explicitly by the operator
        parquetFile = softwareSystem "Parquet Export" "Optional, attributable, atomically replaced local export; never authoritative state" "External"

        # Factory Flow Control system
        factoryFlowControl = softwareSystem "Factory Flow Control" "Precondition-based agent eligibility, dispatch, and validation for Agent Factory" {

            # Eligibility Engine — pure domain logic, returns immutable decisions, never writes state
            eligibilityEngine = container "Eligibility Engine" "Evaluates agent preconditions against the repository, derives per-agent readiness, and classifies agents by eligibility; returns immutable decisions without writing state" "Python 3.10+" {
                intentCli = component "intent" "CLI entry point with two subcommands: select (list agents with precondition evidence) and assess (validate governed artifacts); calls evaluate_all and load_agent_definitions" "Python"
                agentLoader = component "Agent Loader" "Loads agent definitions from YAML frontmatter in the agents directory" "Python"
                preconditionEvaluator = component "Precondition Evaluator" "Evaluates each agent's inputs.required declarations against the filesystem: resolves path patterns, checks frontmatter conditions, runs validator scripts" "Python"
                readinessEvaluator = component "Readiness Evaluator" "Accepts evaluation evidence from the precondition evaluator and derives per-agent AgentReadiness verdicts with eligible/unsatisfied/warnings" "Python"
                recommendationClassifier = component "Recommendation Classifier" "Classifies agents by eligibility into eligible and blocked groups from readiness verdicts" "Python"
                workstreamResolver = component "Workstream Resolver" "Resolves workstream identity from session binding" "Python"
                sessionBindingManager = component "Session Binding Manager" "Creates and manages session-to-workstream bindings; records session_id, workstream_id, and bound_at" "Python"
            }

            # Validator — deterministic gates and validators
            validator = container "Validator" "Enforces gates, permissions, project-declared test gate presence, agent-context structure, and semantic quality checks" "Bash/Python" {
                blockDangerousGit = component "block-dangerous-git.sh" "PreToolUse hook blocking destructive commands and allowlisting project-declared test commands via format-detected testing.yaml" "Bash"
                concernLint = component "concern-lint" "Validates concern-oriented agent context: category headings, Read/Boundary path resolution, story concern vocabulary, and absence of legacy YAML files (CTX-* codes)" "Python"
                schemaValidate = component "schema-validate" "Deterministic JSON-Schema validator for research artifacts: stage 1 of the schema->policy->semantic validation order" "Python"
                policyValidate = component "policy-validate" "Deterministic research-policy validator: stage 2; --pipeline runs schema then policy in order, stopping at the first failure" "Python"
                crapScore = component "crap-score" "CRAP scoring gate: cyclomatic complexity weighted against test coverage, diff-scoped per story" "Bash/Python"
                dependencyCheck = component "dependency-check" "Dependency-rule enforcement gate: validates imports against architecture.dsl dependency declarations" "Bash/Python"
                moduleGraphCheck = component "module-graph-check" "Derives module map from architecture.dsl, compares against concept outputs to determine architecture routing" "Bash/Python"
                fenceRunner = component "Fence Runner" "Deterministic output validation after agent activity; snapshots declared output patterns, compares post-activity filesystem state, and stores fence evidence" "Python"
                proposalValidator = component "Proposal Validator" "Checks proposal file existence, format, and required fields; returns the shared validator result shape" "Python"
            }

            # Dispatcher — agent and model resolution, CLI session spawning
            dispatcher = container "Dispatcher" "Resolves agents/models and spawns CLI sessions" "Bash/Python" {
                trigger = component "trigger" "Dispatches named agent or playbook step to CLI" "Bash"
                indexLint = component "index-lint" "Generates INDEX.yaml from frontmatter" "Python"
                runAgent = component "run-agent (Pi extension)" "Pi model-callable tool: spawns a separate pi session to run one factory agent" "TypeScript/Pi"
                dispatchWave = component "dispatch-wave (Pi extension)" "Pi model-callable tool: runs a parallel wave of factory agents, each in its own git worktree, integrating premerge-check before merging" "TypeScript/Pi"
                openrouterDiscover = component "openrouter-discover" "Operator aid: queries OpenRouter catalog to curate/validate pi.* tier rows in model.conf (offline of the runtime path)" "Python"
            }

            # Usage Capture — with optional workstream context
            usageCaptureContainer = container "Usage Capture" "Normalizes CLI-native transcripts and appends versioned usage records with optional workstream context" "Python/Shell/TypeScript" {
                usageCapture = component "usage-capture" "Normalizes one CLI transcript and appends a canonical usage record; adds workstream_id and workstream_origin from the session binding when available" "Python"
            }

            # Distribution — component lifecycle
            distribution = container "Distribution" "Installs, updates, removes, and reports opt-in Factory components" "Bash/Python" {
                initFactory = component "init-factory" "Installs, updates, or removes the usage component and maintains the install manifest" "Python"
                updateFactory = component "update-factory" "Updates Factory core and reports installed components without changing them" "Python"
                removeFactory = component "remove-factory" "Performs complete Factory removal, including analysis and raw usage data" "Python"
            }

            # Storage
            workstreamState = container "Workstream State" "Immutable workstream identity records under .agent-factory/workstreams/; each records schema_version, workstream_id, topic, and origin_ref" "YAML files" "Storage"
            sessionBindings = container "Session Bindings" "Session-to-workstream mapping under .agent-factory/workstreams/sessions/<session-id>.yaml; records session_id, workstream_id, and bound_at" "YAML files" "Storage"
            stateFiles = container "State Files" "Local git-ignored dispatch ledgers and quality-gate reports" "YAML/JSON files" "Storage"
            catalog = container "Catalog" "Generated INDEX.yaml of agents/skills/playbooks" "YAML file" "Storage"
            usageRecordContract = container "Usage Record Contract" "Factory-owned JSON Schema Draft 2020-12 and compatibility manifest; v1 schema includes optional workstream_id and workstream_origin fields" "JSON Schema/YAML" "Storage"
            rawUsageSpool = container "Raw Usage Spool" "Authoritative append-only top-level JSONL records under .agent-factory/usage/" "JSONL files" "Storage"
            installManifest = container "Install Manifest" "Records installed CLI integrations and opt-in components" "JSON file" "Storage"

            # OpenCode Plugin — V2 plugin adapter for OpenCode CLI
            opencodePlugin = container "OpenCode Plugin" "V2 plugin adapter mapping Factory safety controls to OpenCode session hooks, tool restrictions, and worktree isolation" "TypeScript/OpenCode V2 Plugin API" {
                permissionEnforcer = component "Permission Enforcer" "Evaluates ordered allow/ask/deny rules and enforces step-manifest read/write boundaries through execute.before hooks" "TypeScript"
                toolRestrictor = component "Tool Restrictor" "Removes tools not in the active agent's declared set via session.hook context; enforces read-only for review agents" "TypeScript"
                usageObserver = component "Usage Observer" "Captures completed root and child session usage via execute.after hooks without double-counting child tokens" "TypeScript"
                worktreeStrategyComponent = component "Worktree Strategy" "Registers a Factory worktree strategy through ctx.worktree.transform; delegates branch and path creation to Factory scripts" "TypeScript"
                orientationInjector = component "Orientation Injector" "Injects AGENTS.opencode.md into session context via session.hook context; describes OpenCode tool names and session-start procedure" "TypeScript"
                pluginHealthMonitor = component "Health Monitor" "Tracks plugin health lifecycle; fails closed on initialization, manifest, permission, or worktree failures with named recovery actions" "TypeScript"
            }

            # OpenCode Catalog — generated agent definitions and index
            opencodeCatalog = container "OpenCode Catalog" "OpenCode-visible agent definitions under .opencode/agents/ and index at .opencode/INDEX.yaml, generated by init-factory" "YAML/Markdown files" "Storage"
        }

        # Separate bounded context: local analytical consumer
        usageAnalysis = softwareSystem "Usage Analysis" "Opt-in, local, read-only JSONL-to-DuckDB analysis with reproducible published views; workstream dimension available" {
            usageAnalysisRuntime = container "Usage Analysis Runtime" "Runs usage-query from the installed, locked Python project and owns the query model" "Python/DuckDB/PyArrow" {
                inputSnapshot = component "Input Snapshot" "Selects and normalizes a sorted, top-level JSONL input set at query start" "Python"
                contractCheck = component "Contract Check" "Validates the installed record contract, every selected line, and producer-consumer compatibility" "Python/JSON Schema"
                operationalPreflight = component "Operational Preflight" "Classifies every line, validates ancestry, and registers valid and failure relations" "Python/DuckDB"
                accountingRegistry = component "Accounting Registry" "Maps exactly five producer CLI values to their conservation rule" "Python/SQL"
                queryModel = component "Query Model v1" "Publishes six versioned DuckDB views over query-scoped relations; workstream dimension available in usage_by_dimension" "DuckDB SQL"
                resultAdapters = component "Result Adapters" "Projects a published view as table, JSON, DuckDB relation, or PyArrow table" "Python"
                parquetExporter = component "Parquet Exporter" "Stages, verifies, attributes, and atomically replaces an explicit export" "Python/DuckDB"
            }

            duckdbUi = container "DuckDB UI" "Optional ephemeral localhost exploration of the same six published views; never gate evidence" "DuckDB bundled UI"
            installedAnalysis = container "Installed Analysis Module" "Versioned SQL, accounting rules, contract copy, lockfile, and executable package under .agent-factory/usage-analysis/" "Files" "Storage"
        }

        # Deployment
        deploymentEnvironment "Release 1" {
            deploymentNode "Operator Workstation" "Single local machine; no container, database server, or remote service" "Linux/macOS" {
                deploymentNode "Factory Project" "Project checkout with a local .agent-factory directory" "Filesystem/processes" {
                    containerInstance eligibilityEngine
                    containerInstance validator
                    containerInstance dispatcher
                    containerInstance usageCaptureContainer
                    containerInstance distribution
                    containerInstance workstreamState
                    containerInstance sessionBindings
                    containerInstance stateFiles
                    containerInstance catalog
                    containerInstance usageRecordContract
                    containerInstance rawUsageSpool
                    containerInstance installManifest
                    containerInstance opencodePlugin
                    containerInstance opencodeCatalog
                    containerInstance usageAnalysisRuntime
                    containerInstance duckdbUi
                    containerInstance installedAnalysis
                }
            }
        }

        # ================================================================
        # Relationships — Human Operator
        # ================================================================
        humanOperator -> intentCli "Selects eligible agents via intent select"
        humanOperator -> git "Runs git commit, git push"
        humanOperator -> trigger "Invokes via CLI"
        humanOperator -> usageAnalysisRuntime "Runs usage-query locally"
        humanOperator -> inputSnapshot "Starts a stable local query"
        humanOperator -> parquetExporter "Requests an explicit Parquet export"
        humanOperator -> duckdbUi "Optionally explores published views"
        humanOperator -> initFactory "Installs, updates, or removes the usage component"

        # ================================================================
        # Relationships — Git hooks
        # ================================================================
        git -> blockDangerousGit "Fires PreToolUse before command execution"
        git -> concernLint "Fires pre-commit"

        # ================================================================
        # Relationships — Eligibility Engine internals
        # ================================================================
        intentCli -> preconditionEvaluator "Calls evaluate_all for agent selection"
        intentCli -> agentLoader "Calls load_agent_definitions"
        preconditionEvaluator -> readinessEvaluator "Passes evaluation evidence"
        readinessEvaluator -> recommendationClassifier "Passes readiness verdicts"
        workstreamResolver -> workstreamState "Resolves workstream identity"
        workstreamResolver -> sessionBindings "Reads session-to-workstream mapping"
        sessionBindingManager -> sessionBindings "Creates session-to-workstream bindings"

        # ================================================================
        # Relationships — Validator
        # ================================================================
        blockDangerousGit -> cliAgent "Blocks destructive commands before execution"
        cliAgent -> concernLint "Validate skill or pre-commit hook invokes concern-lint on agent-context files"
        cliAgent -> schemaValidate "Research skills/agents validate an artifact against its schema (stage 1)"
        cliAgent -> policyValidate "Research skills/agents validate artifacts against enforceable policy (stage 2)"
        policyValidate -> schemaValidate "Chains stage 1 in --pipeline mode"

        # ================================================================
        # Relationships — Dispatcher
        # ================================================================
        trigger -> catalog "Resolves agent/playbook by name"
        trigger -> cliAgent "Spawns CLI session with scoped allowlist"
        indexLint -> catalog "Generates/validates INDEX.yaml"
        cliAgent -> runAgent "Pi: invokes run_agent tool (no native subagents)"
        runAgent -> catalog "Resolves agent by name; tier via model.conf"
        runAgent -> cliAgent "Spawns a separate pi session for the agent"
        cliAgent -> dispatchWave "Pi: invokes dispatch_wave tool for a parallel, worktree-isolated wave"
        dispatchWave -> catalog "Resolves each item's agent by name; tier via model.conf"
        dispatchWave -> cliAgent "Spawns parallel pi sessions, one per worktree"

        # ================================================================
        # Relationships — Usage Capture
        # ================================================================
        cliAgent -> usageCapture "Supplies CLI-native transcript and invocation context"
        usageCapture -> usageRecordContract "Produces records governed by"
        usageCapture -> rawUsageSpool "Appends canonical records"
        usageCapture -> sessionBindings "Reads workstream context for usage attribution"

        # ================================================================
        # Relationships — Distribution
        # ================================================================
        initFactory -> usageRecordContract "Copies the compatible contract into the component"
        initFactory -> installedAnalysis "Installs, updates, or removes without touching raw data"
        initFactory -> installManifest "Records installed_components.usage"
        updateFactory -> installManifest "Reports component presence without changing it"
        removeFactory -> installedAnalysis "Removes during complete uninstall"
        removeFactory -> rawUsageSpool "Deletes during complete uninstall"

        # ================================================================
        # Relationships — Usage Analysis
        # ================================================================
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

        # ================================================================
        # Relationships — Semantic Quality Gates (dispatcher-invoked)
        # ================================================================
        cliAgent -> crapScore "Implementation-agent dispatcher runs after developer commit"
        cliAgent -> dependencyCheck "Implementation-agent dispatcher runs after developer commit"
        crapScore -> stateFiles "Writes JSON report to .current-work/crap-score/"
        dependencyCheck -> stateFiles "Writes JSON report to .current-work/dependency-check/"

        # ================================================================
        # Relationships — Fence Runner and Proposal Validator
        # ================================================================
        cliAgent -> fenceRunner "Runs after agent activity to validate declared outputs"
        fenceRunner -> stateFiles "Stores fence evidence"
        intentCli -> proposalValidator "intent assess validates proposal artifacts"

        # ================================================================
        # Relationships — Module-graph check
        # ================================================================
        cliAgent -> moduleGraphCheck "Orchestrating session runs at architecture boundary"

        # ================================================================
        # Relationships — OpenCode Plugin
        # ================================================================
        cliAgent -> opencodePlugin "OpenCode sessions routed through V2 plugin hooks"
        cliAgent -> permissionEnforcer "Tool invocation reaches execute.before hook for permission check"
        cliAgent -> worktreeStrategyComponent "Dispatcher requests child session workspace via plugin"
        permissionEnforcer -> cliAgent "Denies or allows tool invocation"
        opencodePlugin -> opencodeCatalog "Reads agent definitions for permissions and tool sets"
        permissionEnforcer -> stateFiles "Reads step manifest for boundary enforcement"
        toolRestrictor -> opencodeCatalog "Reads agent tool declarations"
        usageObserver -> usageCapture "Delegates usage recording to existing pipeline"
        worktreeStrategyComponent -> stateFiles "Delegates branch and worktree operations to Factory scripts"
        orientationInjector -> opencodeCatalog "Reads AGENTS.opencode.md for session context injection"
        pluginHealthMonitor -> permissionEnforcer "Monitors permission evaluation failures"
        pluginHealthMonitor -> worktreeStrategyComponent "Monitors worktree creation failures"
        initFactory -> opencodeCatalog "Generates OpenCode agent definitions and index"
        removeFactory -> opencodeCatalog "Removes Factory-owned OpenCode files via install manifest"

        # ================================================================
        # Relationships — CLI Agent hooks
        # ================================================================
        cliAgent -> blockDangerousGit "Every shell command routed through PreToolUse (or Pi extension)"
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

        component eligibilityEngine "EligibilityEngineComponents" "Eligibility engine internals: agent loading, precondition evaluation, readiness derivation, and recommendation classification" {
            include *
            include workstreamState
            include sessionBindings
            autoLayout tb
        }

        component validator "ValidationComponents" "Validation components: hook-triggered gates, on-demand validators, and semantic quality gates" {
            include *
            include git
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

        dynamic eligibilityEngine "AgentSelection" "Human selects an eligible agent for the current workstream" {
            humanOperator -> intentCli "1. Invokes intent select"
            intentCli -> agentLoader "2. Loads agent definitions from agents directory"
            intentCli -> preconditionEvaluator "3. Evaluates each agent's preconditions against the filesystem"
            preconditionEvaluator -> readinessEvaluator "4. Passes evaluation evidence for readiness derivation"
            readinessEvaluator -> recommendationClassifier "5. Classifies agents into eligible and blocked groups"
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

        component opencodePlugin "OpenCodePluginComponents" "OpenCode V2 plugin internals: permission enforcement, tool restriction, usage capture, worktree isolation, and health monitoring" {
            include *
            include stateFiles
            include opencodeCatalog
            include usageCapture
            include cliAgent
            autoLayout tb
        }

        dynamic opencodePlugin "OpenCodePermissionEnforcement" "Plugin enforces permission and step boundaries on tool invocation" {
            cliAgent -> permissionEnforcer "1. Tool invocation reaches execute.before hook"
            permissionEnforcer -> stateFiles "2. Reads active step manifest"
            permissionEnforcer -> cliAgent "3. Denies or allows the invocation"
        }

        dynamic opencodePlugin "OpenCodeWorktreeIsolation" "Plugin isolates a dispatched child session in a Factory-managed worktree" {
            cliAgent -> worktreeStrategyComponent "1. Dispatcher requests child session workspace"
            worktreeStrategyComponent -> stateFiles "2. Delegates branch and worktree creation to Factory scripts"
            cliAgent -> permissionEnforcer "3. Primary checkout receives session-scoped write denial"
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
