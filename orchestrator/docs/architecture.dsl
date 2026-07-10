workspace "Agent Session Orchestrator" "Thin Python CLI that drives the Agent HQ agent chain with deterministic gates and human approval at phase gates." {

    model {
        operator  = person "Operator" "Human driving a project through the Agent HQ chain, one phase at a time."

        aicli      = softwareSystem "AI CLI" "GitHub Copilot / Claude / Gemini CLI, invoked non-interactively as a fresh subprocess per agent. Agents commit their own work; pre-commit hooks fire inside the agent subprocess." "External"
        gitpc      = softwareSystem "Git + pre-commit" "The host git repository and its pre-commit hook set. Hooks fire inside agent subprocesses on each git commit; the orchestrator verifies working-tree cleanliness after the agent exits (ADR-0013)." "External"
        aitooling  = softwareSystem "Tooling assets" "The agent definitions, skills, and lint scripts the orchestrator drives — resolved from the package-relative path and exposed via symlinks (ADR-0010)." "External"

        orchestrator = softwareSystem "Agent Session Orchestrator" "Runs a single step, one phase's author-reviewer loop, or the full chain, with gates enforced and humans reserved for phase gates." {

            cli = container "CLI Entry Point" "Parses commands (run-step, run-phase, status, resume, approve, reject, release, abort) and dispatches to application services." "Python / argparse" {
                dispatcher = component "Command Dispatcher" "Maps argv to an application service; validates arguments; owns process exit codes." "argparse"
            }

            core = container "Orchestration Core" "CLI-agnostic domain and application logic: the phase state machine, loop policy, and chain sequencing. Depends only on ports." "Python (stdlib)" {
                phaseRunner   = component "PhaseRunner" "Drives one phase's author -> gate -> review -> loop-or-approve state machine (UC-02). The Operator drives the chain by running one phase at a time in order (UC-03)." "Python"
                loopPolicy    = component "LoopPolicy" "Caps iterations, supersedes prior findings, evaluates the loop-exit condition (SF-04, BR-001/003/014)." "Python"
                statusService = component "StatusService" "Read-only projections for the status views: overview, per-phase details, open findings, and the invocation log (UC-05, UC-08, FR-T)." "Python"
                approvalSvc   = component "ApprovalService" "Records approve/reject at a phase gate and advances or halts (UC-04)." "Python"
                modelResolver = component "ModelResolver" "Two resolution paths that never combine: agent tier -> model (for every orchestrator-invoked agent) and story classification -> model (for the dispatcher's tier-less developer sub-agents during implementation), both via the active adapter's dictionary; --model overrides on run-step; null tier resolves as standard for orchestrator-invoked agents (FR-R10..R12, VR-041, ADR-0018)." "Python"
                menuController = component "MenuController" "Traverses the menu tree, tracks navigation state, and dispatches each function leaf to the same application service as its direct-mode equivalent; hands long-running operations back to the streaming path (UC-08, FR-P, FR-V, ADR-0016)." "Python"
                settingsResolver = component "SettingsResolver" "Resolves each invocation setting through the four-layer precedence menu selection > CLI flag > config.toml > built-in default (UC-09, FR-Q3, SF-07)." "Python"
                domain        = component "Domain Entities" "Run, Phase, Iteration, Finding, GateResult, AgentInvocation, Approval, Story, InvocationContext, Config, AdapterEntry, ModelDictionary, MenuNode — pure state, no I/O." "Python dataclasses"
                ports         = component "Ports" "Abstract interfaces the core depends on: CLIAdapter, FindingsStore, FindingIngestor, GateRunner, RunStateStore, RunLock, AgentRegistry, PromptComposer, Logger, BacklogStore, ModelMatrix, MenuRenderer, ConfigStore, AdapterRegistry, Clock" "Python Protocol/ABC"
            }

            copilotAdapter = container "CLI Adapters" "Concrete CLIAdapter implementations — Copilot (MVP), Claude, Gemini. Own all CLI-specific non-interactive flags; return only InvocationResult." "Python / subprocess"
            gateRunner     = container "Working-Tree Gate" "Verifies working-tree cleanliness after agent exits; maps (exit_code, tree_state) to a GateResult. Cleans tree before retry (ADR-0013). Replaces the old stage-commit-parse GateRunner." "Python / subprocess + git"
            findingsStore  = container "Findings Store Adapter" "File-per-finding JSON store with a monotonic ID allocator; validates every finding against the schema on write." "Python / jsonschema"
            runStateStore  = container "Run State Store" "Atomic (write-then-rename) reader/writer of .orchestrator/run.json and the run lock; also the git run-branch manager." "Python / json + git"
            agentRegistry  = container "Agent Registry" "Reads agents/*.md front-matter to resolve each phase's author/reviewer, their declared outputs (FR-H), and the agent's tier, interactive policy, and skills (FR-R10, FR-S5)." "Python"
            menuRenderer   = container "Terminal Menu Renderer" "Concrete MenuRenderer: paints one menu or display node at a time with the -> cursor and star default, and normalizes keypresses to KeyEvents. Terminal framework deferred (T-29, ADR-0016)." "Python / terminal"
            configAdapter  = container "Config & Registry Store" "Implements ConfigStore and AdapterRegistry over .orchestrator/config.toml: operator defaults, registered adapters with binary paths, and per-adapter tier->model dictionaries; atomic write-then-rename (UC-09, UC-10, ADR-0017)." "Python / tomllib"
            backlogStore   = container "Backlog Store" "Reads/writes backlog/ST-NNNN.md; parses story frontmatter for routing, leaves the prose body for the agent (ADR-0008)." "Python"
            modelMatrix    = container "Model Matrix Reader" "Reads the operator-curated matrix (facts + policy); ModelResolver queries it (ADR-0009)." "Python"
            logger         = container "Invocation Log" "Appends one JSON line per invocation to .orchestrator/log.jsonl for observability (FR-J)." "Python"
            findingIngestor = container "Finding Ingestor" "Reads the review agent's filed docs/findings/*.md and parses deterministic gate/spec-lint output; maps each finding to the Finding DTO; depends on FindingsStore for ID allocation and persistence (ADR-0012)." "Python"

            findingsData = container "findings/" "One JSON file per finding — the source of truth for review findings and loop state." "Filesystem (JSON)" "Data"
            runData      = container ".orchestrator/" "run.json + run.lock + log.jsonl — the resumable run record, single-run lock, and invocation log." "Filesystem (JSON)" "Data"
            backlogData  = container "backlog/" "One markdown file per story — strict frontmatter + prose body (ADR-0008)." "Filesystem (Markdown)" "Data"
            matrixData   = container "model matrix" "Operator-curated facts + policy — tier<->model per CLI, class/phase->tier (ADR-0009)." "Config (TOML)" "Data"
            configData   = container ".orchestrator/config.toml" "Persisted operator defaults + adapter registry + per-adapter model dictionaries (ADR-0017)." "Filesystem (TOML)" "Data"
        }

        # People -> system
        operator  -> cli "Runs commands" "shell"

        # Inside the orchestrator: dispatch into the core
        dispatcher -> phaseRunner "run-phase / run-step"
        dispatcher -> statusService "status"
        dispatcher -> approvalSvc "approve / reject"
        dispatcher -> menuController "bare orchestrate (menu mode)"
        dispatcher -> settingsResolver "Resolves effective settings"

        # Menu mode: the controller dispatches leaves to the same core services as direct mode
        menuController -> menuRenderer "Renders nodes, reads keys" "MenuRenderer port"
        menuController -> settingsResolver "Resolves effective settings"
        menuController -> agentRegistry "Lists agents + tiers (run-step)" "AgentRegistry port"
        menuController -> modelResolver "Resolves default model to mark star"
        menuController -> phaseRunner "run-step / run-phase leaf"
        menuController -> statusService "status views"
        menuController -> approvalSvc "manage-run leaves"
        menuController -> backlogStore "backlog views" "BacklogStore port"
        menuController -> configAdapter "configure leaves (defaults, adapters, models)" "ConfigStore / AdapterRegistry port"

        # Settings + model resolution read persisted config and the adapter dictionary
        settingsResolver -> configAdapter "Reads persisted defaults" "ConfigStore port"
        modelResolver -> configAdapter "Resolves tier -> model via the adapter dictionary" "AdapterRegistry port"

        # Core internal
        phaseRunner -> loopPolicy "Applies cap + loop-exit"
        phaseRunner -> domain "Reads/updates run state"
        phaseRunner -> ports "Uses"
        loopPolicy  -> ports "Uses"
        statusService -> ports "Uses"
        approvalSvc -> ports "Uses"
        phaseRunner -> modelResolver "Selects the model per story/phase"
        modelResolver -> ports "Uses"

        # Core -> adapters via ports (dependency inversion: adapters implement ports)
        phaseRunner -> copilotAdapter "Invokes agent (isolated subprocess)" "CLIAdapter port"
        phaseRunner -> gateRunner "Verifies working-tree cleanliness after agent" "GateRunner port"
        phaseRunner -> findingsStore "Queries open findings + supersedes" "FindingsStore port"
        phaseRunner -> findingIngestor "Ingests deterministic + reviewer findings" "FindingIngestor port"
        phaseRunner -> runStateStore "Persists run state" "RunStateStore port"
        phaseRunner -> agentRegistry "Resolves agent + outputs" "AgentRegistry port"
        statusService -> runStateStore "Reads run state" "RunStateStore port"
        statusService -> findingsStore "Counts open findings" "FindingsStore port"
        approvalSvc -> runStateStore "Records approval" "RunStateStore port"
        approvalSvc -> findingsStore "Checks open findings" "FindingsStore port"
        approvalSvc -> gateRunner "Re-verifies tree on staleness (VR-012)" "GateRunner port"
        approvalSvc -> agentRegistry "Resolves artifact paths" "AgentRegistry port"
        phaseRunner -> backlogStore "Reads stories (implementation)" "BacklogStore port"
        phaseRunner -> logger "Logs each invocation" "Logger port"
        modelResolver -> modelMatrix "Resolves tier -> model" "ModelMatrix port"

        # Adapters -> externals & data
        copilotAdapter -> aicli "Runs agent non-interactively" "subprocess"
        copilotAdapter -> aitooling "Reads agent/skill definitions"
        gateRunner -> gitpc "Checks working-tree state; cleans tree on retry" "git status / checkout / clean"
        agentRegistry -> aitooling "Reads agents/*.md outputs"
        findingsStore -> findingsData "Reads/writes finding files"
        findingIngestor -> findingsStore "Allocates IDs + writes findings" "FindingsStore port"
        runStateStore -> runData "Reads/writes run.json + lock"
        backlogStore -> backlogData "Reads/writes story files"
        modelMatrix -> matrixData "Reads facts + policy"
        modelMatrix -> configAdapter "Populates adapter dictionaries from matrix facts (startup / edit)" "AdapterRegistry port"
        configAdapter -> configData "Reads/writes config.toml (atomic)"
        logger -> runData "Appends log.jsonl"

        # The driven CLI writes the artifacts
        aicli -> gitpc "Commits phase artifacts on the run branch; pre-commit hooks fire on each commit"

        # --- Deployment (§7.1) ---------------------------------------------------
        deploymentEnvironment "Developer-Machine" {
            deploymentNode "Developer Machine" "" "Linux / macOS / WSL" {
                deploymentNode "orchestrate process" "" "Python 3.10+ (uv tool install)" {
                    containerInstance cli
                    containerInstance core
                    containerInstance findingsStore
                    containerInstance runStateStore
                    containerInstance agentRegistry
                    containerInstance backlogStore
                    containerInstance modelMatrix
                    containerInstance logger
                    containerInstance findingIngestor
                    containerInstance gateRunner
                    containerInstance menuRenderer
                    containerInstance configAdapter
                }
                deploymentNode "Agent subprocess" "" "Fresh per invocation (ADR-0002)" {
                    containerInstance copilotAdapter
                }
                deploymentNode "Project directory" "" "Git repository" {
                    containerInstance findingsData
                    containerInstance runData
                    containerInstance backlogData
                    containerInstance matrixData
                    containerInstance configData
                }
                deploymentNode "Host tooling" "" "Installed on PATH" {
                    softwareSystemInstance aicli
                    softwareSystemInstance gitpc
                    softwareSystemInstance aitooling
                }
            }
        }
    }

    views {
        systemContext orchestrator "SystemContext" "Who uses the orchestrator and which external systems it drives." {
            include *
            autoLayout lr
        }

        container orchestrator "Containers" "The orchestrator's runtime pieces: the CLI, the CLI-agnostic core, the adapters, and the on-disk stores." {
            include *
            autoLayout lr
        }

        component core "CoreComponents" "Inside the Orchestration Core: Clean Architecture layers — the core depends only on Ports; adapters implement them." {
            include *
            autoLayout lr
        }

        dynamic core "RunPhaseClean" "A phase completes cleanly on the first iteration (UC-02 main success, §6.1)." {
            phaseRunner -> agentRegistry "Resolve author + declared outputs"
            phaseRunner -> modelResolver "Select model for invocation"
            phaseRunner -> copilotAdapter "Invoke author (fresh subprocess)"
            copilotAdapter -> aicli "Agent runs, commits work, hooks fire"
            phaseRunner -> gateRunner "Verify working-tree cleanliness"
            gateRunner -> gitpc "git status --porcelain (clean)"
            phaseRunner -> agentRegistry "Resolve reviewer"
            phaseRunner -> copilotAdapter "Invoke reviewer (fresh subprocess)"
            copilotAdapter -> aicli "Reviewer runs, files findings"
            phaseRunner -> findingIngestor "Ingest reviewer findings"
            findingIngestor -> findingsStore "Allocate IDs, write findings (0 open)"
            phaseRunner -> runStateStore "Write run.json (awaiting-approval)"
            autoLayout lr
        }

        dynamic core "RunPhaseLoop" "Author-reviewer loop: findings on iteration 1, clean on iteration 2 (UC-02 ext. 8a, §6.2)." {
            phaseRunner -> copilotAdapter "Invoke author (iteration 1)"
            phaseRunner -> gateRunner "Verify tree (passed)"
            phaseRunner -> copilotAdapter "Invoke reviewer (iteration 1)"
            phaseRunner -> findingIngestor "Ingest findings (2 open)"
            phaseRunner -> loopPolicy "Evaluate: retry (1 < cap)"
            phaseRunner -> findingsStore "Supersede iteration-1 findings"
            phaseRunner -> copilotAdapter "Invoke author (iteration 2, with findings)"
            phaseRunner -> gateRunner "Verify tree (passed)"
            phaseRunner -> copilotAdapter "Invoke reviewer (iteration 2)"
            phaseRunner -> findingIngestor "Ingest findings (0 open)"
            phaseRunner -> runStateStore "Write run.json (awaiting-approval)"
            autoLayout lr
        }

        dynamic core "NavigateMenuToRunStep" "Operator reaches a run-step leaf through menu navigation; the leaf dispatches to the same service as direct mode (UC-08, §6.7)." {
            dispatcher -> menuController "Bare orchestrate enters menu mode"
            menuController -> menuRenderer "Render root menu, read arrow/Enter keys"
            menuController -> agentRegistry "List agents + tiers (run-step)"
            menuController -> settingsResolver "Resolve default adapter"
            menuController -> modelResolver "Resolve agent tier -> model, mark star default"
            menuController -> phaseRunner "Dispatch run-step, exit TUI, stream output"
            autoLayout lr
        }

        deployment orchestrator "Developer-Machine" "Deployment" "MVP deployment: everything runs on the operator's machine (§7.1)." {
            include *
            autoLayout tb
        }

        styles {
            element "Person" {
                shape person
                background #08427b
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Data" {
                shape cylinder
                background #63a355
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
        }

        theme default
    }
}
