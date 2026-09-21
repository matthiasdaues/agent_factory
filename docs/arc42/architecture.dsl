// scope: global
workspace "Agent Factory" "Precondition-based agent eligibility, dispatch, validation, and usage capture for Agent Factory" {

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
        factoryFlowControl = softwareSystem "Factory Flow Control" "Precondition-based agent eligibility, dispatch, and validation for Agent Factory" {

            # Eligibility Engine — pure domain logic, returns immutable decisions, never writes state
            eligibilityEngine = container "Eligibility Engine" "Evaluates agent preconditions against the repository, derives per-agent readiness, and classifies agents by eligibility; returns immutable decisions without writing state" "Python 3.10+" {
                intentCli = component "intent" "CLI entry point with two subcommands: select (list agents with precondition evidence) and assess (validate governed artifacts); calls evaluate_all and load_agent_definitions" "Python"
                agentLoader = component "Agent Loader" "Loads agent definitions from YAML frontmatter in the agents directory" "Python"
                preconditionEvaluator = component "Precondition Evaluator" "Evaluates each agent's inputs.required declarations against the filesystem: resolves path patterns, checks frontmatter conditions, runs validator scripts" "Python"
                readinessEvaluator = component "Readiness Evaluator" "Accepts evaluation evidence from the precondition evaluator and derives per-agent AgentReadiness verdicts with eligible/unsatisfied/warnings" "Python"
                recommendationClassifier = component "Recommendation Classifier" "Classifies agents by eligibility into eligible and blocked groups from readiness verdicts" "Python"
                workstreamResolver = component "Workstream Resolver" "Resolves workstream identity from session binding and validates revision and digest consistency" "Python"
            }

            # State Adapter — thin command adapters that own state writes and lock acquisition
            stateAdapter = container "State Adapter" "Thin command adapters that acquire locks, call the engine for decisions, write workstream state, and advance playbook phases" "Python" {
                phaseAdvance = component "phase" "Advances or retries a structured-playbook run's state marker, enforcing the target state's entry_conditions before it moves" "Python 3.10+"
                runStep = component "run-step skill" "Derives what comes next from cycle state and the delivery model; dispatches the resolved agent" "Markdown/LLM-executed"
            }

            # Validator — deterministic gates and validators
            validator = container "Validator" "Enforces gates, permissions, playbook phase ordering, project-declared test gate presence, agent-context structure, and semantic quality checks" "Bash/Python" {
                transitionLint = component "transition-lint" "Validates playbook phase ordering by mapping staged files to FSM output globs; blocks commits that stage files belonging to a non-current phase" "Python 3.10+"
                blockDangerousGit = component "block-dangerous-git.sh" "PreToolUse hook blocking destructive commands and allowlisting project-declared test commands via format-detected testing.yaml" "Bash"
                concernLint = component "concern-lint" "Validates concern-oriented agent context: category headings, Read/Boundary path resolution, story concern vocabulary, and absence of legacy YAML files (CTX-* codes)" "Python"
                schemaValidate = component "schema-validate" "Deterministic JSON-Schema validator for research artifacts: stage 1 of the schema->policy->semantic validation order" "Python"
                policyValidate = component "policy-validate" "Deterministic research-policy validator: stage 2; --pipeline runs schema then policy in order, stopping at the first failure" "Python"
                crapScore = component "crap-score" "CRAP scoring gate: cyclomatic complexity weighted against test coverage, diff-scoped per story" "Bash/Python"
                dependencyCheck = component "dependency-check" "Dependency-rule enforcement gate: validates imports against architecture.dsl dependency declarations" "Bash/Python"
                moduleGraphCheck = component "module-graph-check" "Derives module map from architecture.dsl, compares against concept outputs to determine architecture routing" "Bash/Python"
            }

            # Dispatcher — agent and model resolution, CLI session spawning
            dispatcher = container "Dispatcher" "Resolves agents/models and spawns CLI sessions" "Bash/Python" {
                trigger = component "trigger" "Dispatches named agent or playbook step to CLI" "Bash"
                indexLint = component "index-lint" "Generates INDEX.yaml from frontmatter" "Python"
                runAgent = component "run-agent (Pi extension)" "Pi model-callable tool: spawns a separate pi session to run one factory agent" "TypeScript/Pi"
                dispatchWave = component "dispatch-wave (Pi extension)" "Pi model-callable tool: runs a parallel wave of factory agents, each in its own git worktree, integrating premerge-check before merging" "TypeScript/Pi"
                openrouterDiscover = component "openrouter-discover" "Operator aid: queries OpenRouter catalog to curate/validate pi.* tier rows in model.conf (offline of the runtime path)" "Python"
            }

            # Usage Capture — with optional workstream and cycle context
            usageCaptureContainer = container "Usage Capture" "Normalizes CLI-native transcripts and appends versioned usage records with optional workstream and cycle context" "Python/Shell/TypeScript" {
                usageCapture = component "usage-capture" "Normalizes one CLI transcript and appends a canonical usage record; adds workstream_id, workstream_origin, and cycle fields from the session binding when available" "Python"
            }

            # Distribution — component lifecycle
            distribution = container "Distribution" "Installs, updates, removes, and reports opt-in Factory components" "Bash/Python" {
                initFactory = component "init-factory" "Installs, updates, or removes the usage component and maintains the install manifest" "Python"
                updateFactory = component "update-factory" "Updates Factory core and reports installed components without changing them" "Python"
                removeFactory = component "remove-factory" "Performs complete Factory removal, including analysis and raw usage data" "Python"
            }

            # Storage — workstream orchestration
            deliveryModel = container "Delivery Model" "Declarative YAML cycle graph with delivery cycles, terminal DONE node, artifact declarations, trusted validator references, and declared routes" "YAML file" "Storage"
            cycleStateFiles = container "Workstream State Files" "One YAML workstream state file per active workstream under .current-work/cycles/; each tracks cycle, attempt, revision, work references, and optional delegation grant" "YAML files" "Storage"
            sessionBindings = container "Session Bindings" "Session-to-workstream navigation state under .current-work/session-bindings/<cli>/<session-id>.yaml; tracks observed revision and SHA-256 digest" "YAML files" "Storage"

            # Storage — existing
            stateFiles = container "State Files" "Local git-ignored dispatch ledgers, quality-gate reports, and legacy playbook marker" "YAML/JSON files" "Storage"
            catalog = container "Catalog" "Generated INDEX.yaml of agents/skills/playbooks" "YAML file" "Storage"
            usageRecordContract = container "Usage Record Contract" "Factory-owned JSON Schema Draft 2020-12 and compatibility manifest; v1 schema includes optional workstream_id, workstream_origin, and cycle fields" "JSON Schema/YAML" "Storage"
            rawUsageSpool = container "Raw Usage Spool" "Authoritative append-only top-level JSONL records under .agent-factory/usage/" "JSONL files" "Storage"
            installManifest = container "Install Manifest" "Records installed CLI integrations and opt-in components" "JSON file" "Storage"
        }

        # Separate bounded context: local analytical consumer
        usageAnalysis = softwareSystem "Usage Analysis" "Opt-in, local, read-only JSONL-to-DuckDB analysis with reproducible published views; workstream and cycle dimensions available" {
            usageAnalysisRuntime = container "Usage Analysis Runtime" "Runs usage-query from the installed, locked Python project and owns the query model" "Python/DuckDB/PyArrow" {
                inputSnapshot = component "Input Snapshot" "Selects and normalizes a sorted, top-level JSONL input set at query start" "Python"
                contractCheck = component "Contract Check" "Validates the installed record contract, every selected line, and producer-consumer compatibility" "Python/JSON Schema"
                operationalPreflight = component "Operational Preflight" "Classifies every line, validates ancestry, and registers valid and failure relations" "Python/DuckDB"
                accountingRegistry = component "Accounting Registry" "Maps exactly four producer CLI values to their conservation rule" "Python/SQL"
                queryModel = component "Query Model v1" "Publishes six versioned DuckDB views over query-scoped relations; workstream and cycle dimensions available in usage_by_dimension" "DuckDB SQL"
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
                    containerInstance stateAdapter
                    containerInstance validator
                    containerInstance dispatcher
                    containerInstance usageCaptureContainer
                    containerInstance distribution
                    containerInstance deliveryModel
                    containerInstance cycleStateFiles
                    containerInstance sessionBindings
                    containerInstance stateFiles
                    containerInstance catalog
                    containerInstance usageRecordContract
                    containerInstance rawUsageSpool
                    containerInstance installManifest
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
        humanOperator -> phaseAdvance "Advances or retries playbook phase"
        humanOperator -> git "Runs git commit, git push"
        humanOperator -> trigger "Invokes via CLI"
        humanOperator -> usageAnalysisRuntime "Runs usage-query locally"
        humanOperator -> inputSnapshot "Starts a stable local query"
        humanOperator -> parquetExporter "Requests an explicit Parquet export"
        humanOperator -> duckdbUi "Optionally explores published views"
        humanOperator -> initFactory "Installs, updates, or removes the usage component"

        # ================================================================
        # Relationships — Orchestrator
        # ================================================================
        orchestrator -> intentCli "Invokes programmatically"
        orchestrator -> phaseAdvance "Invokes programmatically"
        orchestrator -> trigger "Invokes programmatically"

        # ================================================================
        # Relationships — Git hooks
        # ================================================================
        git -> transitionLint "Fires pre-commit"
        git -> blockDangerousGit "Fires PreToolUse before command execution"
        git -> concernLint "Fires pre-commit"

        # ================================================================
        # Relationships — State Adapter to Eligibility Engine
        # ================================================================
        phaseAdvance -> eligibilityEngine "Checks entry conditions"
        runStep -> eligibilityEngine "Requests agent eligibility evaluation"
        intentCli -> preconditionEvaluator "Calls evaluate_all for agent selection"
        intentCli -> agentLoader "Calls load_agent_definitions"
        preconditionEvaluator -> readinessEvaluator "Passes evaluation evidence"
        readinessEvaluator -> recommendationClassifier "Passes readiness verdicts"

        # ================================================================
        # Relationships — Eligibility Engine to storage (read-only)
        # ================================================================
        eligibilityEngine -> deliveryModel "Loads delivery graph and route declarations"

        # ================================================================
        # Relationships — State Adapter to storage
        # ================================================================
        phaseAdvance -> cycleStateFiles "Reads workstream state for entry condition checks"
        phaseAdvance -> sessionBindings "Reads/writes session binding"
        runStep -> cycleStateFiles "Reads workstream state and delegation grant"
        runStep -> trigger "Dispatches resolved agent"

        # ================================================================
        # Relationships — Validator
        # ================================================================
        transitionLint -> stateFiles "Reads playbook-state.yml for current phase"
        transitionLint -> cycleStateFiles "Maps staged files against FSM output globs"
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
        # Relationships — Module-graph check
        # ================================================================
        cliAgent -> moduleGraphCheck "Orchestrating session runs at architecture boundary"

        # ================================================================
        # Relationships — CLI Agent hooks
        # ================================================================
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

        component eligibilityEngine "EligibilityEngineComponents" "Eligibility engine internals: agent loading, precondition evaluation, readiness derivation, and recommendation classification" {
            include *
            include stateAdapter
            include deliveryModel
            autoLayout tb
        }

        component stateAdapter "StateAdapterComponents" "State adapter commands: phase advance/retry and run-step skill" {
            include *
            include eligibilityEngine
            include cycleStateFiles
            include sessionBindings
            include stateFiles
            include trigger
            include humanOperator
            include orchestrator
            autoLayout tb
        }

        component validator "ValidationComponents" "Validation components: hook-triggered gates, on-demand validators, and semantic quality gates" {
            include *
            include git
            include cliAgent
            include stateFiles
            include stateFiles
            include cycleStateFiles
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
