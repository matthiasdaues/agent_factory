workspace "Agent Session Orchestrator" "Manages run state and provides a TUI for the Agent HQ agent chain: approval gates, status, backlog browsing, and adapter/model configuration. Execution (author-reviewer loop, gating, model resolution) is driven by factory/, not this system — see docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md." {

    model {
        operator  = person "Operator" "Human driving a project through the Agent HQ chain, one phase at a time."

        gitpc      = softwareSystem "Git + pre-commit" "The host git repository and its pre-commit hook set. Agents (invoked by factory) commit their own work and hooks fire inside those subprocesses; the orchestrator only re-checks working-tree cleanliness at approve time (VR-012)." "External"
        aitooling  = softwareSystem "Tooling assets" "The agent definitions, skills, and lint scripts factory drives — resolved from the package-relative path and exposed via symlinks (ADR-0010)." "External"
        factory    = softwareSystem "factory/ (flow control)" "Owns phase sequencing, gating, iteration caps, CLI dispatch, prompt composition, model resolution, and findings ingestion (factory/scripts/{phase,trigger,transition-lint}, factory/skills/run-step). Writes the same .orchestrator/run.json and findings/ the orchestrator reads. See docs/adr/0002." "External"

        orchestrator = softwareSystem "Agent Session Orchestrator" "Observes and manages run state: status, phase-gate approval, halted-run recovery, project init, and a TUI for backlog browsing and adapter/model configuration." {

            cli = container "CLI Entry Point" "Parses commands (status, approve, reject, release, abort, init) and dispatches to application services." "Python / argparse" {
                dispatcher = component "Command Dispatcher" "Maps argv to an application service; validates arguments; owns process exit codes." "argparse"
            }

            core = container "Orchestration Core" "CLI-agnostic domain and application logic: read-only status projections, phase-gate approval, menu navigation, and settings resolution. Depends only on ports." "Python (stdlib)" {
                statusService = component "StatusService" "Read-only projections for the status views: overview, per-phase details, and open findings (UC-05, UC-08, FR-T). status > log always renders empty (no invocation-log writer remains in the orchestrator)." "Python"
                approvalSvc   = component "ApprovalService" "Records approve/reject at a phase gate and advances or halts (UC-04); re-verifies the working tree if artifacts changed since the gate (VR-012)." "Python"
                menuController = component "MenuController" "Traverses the menu tree, tracks navigation state, and dispatches each function leaf to the same application service as its direct-mode equivalent; hands long-running operations back to the streaming path (UC-08, FR-P, FR-V, ADR-0016). run-step and run-phase are inert, childless menu entries; manage-run > resume reports that execution moved to factory." "Python"
                settingsResolver = component "SettingsResolver" "Resolves each invocation setting through the four-layer precedence menu selection > CLI flag > config.toml > built-in default (UC-09, FR-Q3, SF-07)." "Python"
                domain        = component "Domain Entities" "Run, PhaseRecord, Finding, GateResult, AgentInvocation, Story, Config, AdapterEntry, ModelDictionary, MenuNode — pure state, no I/O." "Python dataclasses"
                ports         = component "Ports" "Abstract interfaces the core depends on: MenuRenderer, GateRunner, FindingsStore, RunStateStore, RunLock, AgentRegistry, InvocationLogReader, BacklogStore, ModelMatrix, ConfigStore, AdapterRegistry" "Python Protocol"
            }

            gateRunner     = container "Working-Tree Gate" "Verifies working-tree cleanliness; maps (exit_code, tree_state) to a GateResult. Called once per approval, not per phase iteration (ADR-0013)." "Python / subprocess + git"
            findingsStore  = container "Findings Store Adapter" "File-per-finding JSON store with a monotonic ID allocator; validates every finding against the schema on write. Read today by status views; ingestion is factory's job." "Python / jsonschema"
            runStateStore  = container "Run State Store" "Atomic (write-then-rename) reader/writer of .orchestrator/run.json and the run lock. Does not manage git branches — factory creates and selects the run branch during execution." "Python / json"
            agentRegistry  = container "Agent Registry" "Reads agents/*.md front-matter to resolve a phase's author outputs (for approval's staleness check) and each agent's tier, interactive policy, and skills (for menu display)." "Python"
            menuRenderer   = container "Terminal Menu Renderer" "Concrete MenuRenderer: paints one menu or display node at a time with the -> cursor and star default, and normalizes keypresses to KeyEvents." "Python / terminal"
            configAdapter  = container "Config & Registry Store" "Implements ConfigStore and AdapterRegistry over .orchestrator/config.toml: operator defaults, registered adapters with binary paths, and per-adapter tier->model dictionaries; atomic write-then-rename (UC-09, UC-10, ADR-0017)." "Python / tomllib"
            backlogStore   = container "Backlog Store" "Reads backlog/ST-NNNN.md; parses story frontmatter for routing, leaves the prose body for display (ADR-0008)." "Python"
            modelMatrix    = container "Model Matrix Reader" "Reads model.conf ([facts] only) for configure > model-matrix > show/edit/validate. Read-only display; tier->model resolution at invocation time happens in factory (ADR-0020, ADR-0021)." "Python"
            adapterDetect  = container "Adapter Auto-Detect" "Scans $PATH for known CLI adapter binaries for configure > cli-list > auto-detect." "Python / subprocess"

            findingsData = container "findings/" "One JSON file per finding — read by status views; populated by factory during execution." "Filesystem (JSON)" "Data"
            runData      = container ".orchestrator/" "run.json + run.lock — the resumable run record and single-run lock, written by both the orchestrator (approve/reject/release/abort) and factory (execution)." "Filesystem (JSON)" "Data"
            backlogData  = container "backlog/" "One markdown file per story — strict frontmatter + prose body (ADR-0008)." "Filesystem (Markdown)" "Data"
            matrixData   = container "model.conf" "Operator-curated per-CLI tier router: [facts] only, no policy layer (ADR-0020)." "Config (TOML)" "Data"
            configData   = container ".orchestrator/config.toml" "Persisted operator defaults + adapter registry + per-adapter model dictionaries (ADR-0017)." "Filesystem (TOML)" "Data"
        }

        # People -> system
        operator  -> cli "Runs commands" "shell"

        # Inside the orchestrator: dispatch into the core
        dispatcher -> statusService "status"
        dispatcher -> approvalSvc "approve / reject"
        dispatcher -> runStateStore "release / abort"
        dispatcher -> menuController "bare orchestrate (menu mode)"

        # Menu mode: the controller dispatches leaves to the same core services as direct mode
        menuController -> menuRenderer "Renders nodes, reads keys" "MenuRenderer port"
        menuController -> settingsResolver "Resolves effective settings"
        menuController -> statusService "status views"
        menuController -> approvalSvc "manage-run > approve / reject"
        menuController -> runStateStore "manage-run > release / abort"
        menuController -> backlogStore "backlog views" "BacklogStore port"
        menuController -> configAdapter "configure leaves (defaults, adapters, models)" "ConfigStore / AdapterRegistry port"
        menuController -> adapterDetect "configure > cli-list > auto-detect"
        menuController -> modelMatrix "configure > model-matrix > show / edit"

        # Settings resolution reads persisted config
        settingsResolver -> configAdapter "Reads persisted defaults" "ConfigStore port"

        # Core internal
        statusService -> ports "Uses"
        approvalSvc -> ports "Uses"

        # Core -> adapters via ports (dependency inversion: adapters implement ports)
        statusService -> runStateStore "Reads run state" "RunStateStore port"
        statusService -> findingsStore "Counts open findings" "FindingsStore port"
        approvalSvc -> runStateStore "Records approval" "RunStateStore port"
        approvalSvc -> findingsStore "Checks open findings" "FindingsStore port"
        approvalSvc -> gateRunner "Re-verifies tree on staleness (VR-012)" "GateRunner port"
        approvalSvc -> agentRegistry "Resolves artifact paths" "AgentRegistry port"

        # Adapters -> externals & data
        gateRunner -> gitpc "Checks working-tree state" "git status / diff"
        agentRegistry -> aitooling "Reads agents/*.md outputs"
        findingsStore -> findingsData "Reads finding files"
        runStateStore -> runData "Reads/writes run.json + lock"
        backlogStore -> backlogData "Reads story files"
        modelMatrix -> matrixData "Reads facts"
        modelMatrix -> configAdapter "Populates adapter dictionaries from matrix facts (startup / edit)" "AdapterRegistry port"
        configAdapter -> configData "Reads/writes config.toml (atomic)"

        # The orchestrator observes what factory and agents produce
        factory -> runData "Drives phase execution; writes run.json during authoring/gating/reviewing"
        factory -> findingsData "Ingests reviewer/gate findings"
        gitpc -> runData "Agents (invoked by factory) commit phase artifacts on the run branch"

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
                    containerInstance adapterDetect
                    containerInstance gateRunner
                    containerInstance menuRenderer
                    containerInstance configAdapter
                }
                deploymentNode "Project directory" "" "Git repository" {
                    containerInstance findingsData
                    containerInstance runData
                    containerInstance backlogData
                    containerInstance matrixData
                    containerInstance configData
                }
                deploymentNode "Host tooling" "" "Installed on PATH" {
                    softwareSystemInstance gitpc
                    softwareSystemInstance aitooling
                    softwareSystemInstance factory
                }
            }
        }
    }

    views {
        systemContext orchestrator "SystemContext" "Who uses the orchestrator and which external systems it observes." {
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

        dynamic core "RunPhaseClean" "An operator approves a clean phase gate factory already produced (UC-04 main success)." {
            approvalSvc -> agentRegistry "Resolve author's declared outputs"
            approvalSvc -> gateRunner "Re-verify working-tree cleanliness if artifacts changed"
            approvalSvc -> findingsStore "Check open findings for the reviewed cycle"
            approvalSvc -> runStateStore "Write run.json (advance to next phase or complete)"
            autoLayout lr
        }

        dynamic core "RunPhaseLoop" "An operator checks status mid-loop while factory drives the author-reviewer cycle (UC-05)." {
            statusService -> runStateStore "Read current phase, iteration, mode"
            statusService -> findingsStore "Count open findings for the last-reviewed cycle"
            autoLayout lr
        }

        dynamic core "NavigateMenuToRunStep" "Operator opens the run-step menu entry; it is inert (childless) because execution moved to factory (UC-08, §6.7)." {
            dispatcher -> menuController "Bare orchestrate enters menu mode"
            menuController -> menuRenderer "Render root menu, read arrow/Enter keys"
            menuController -> menuRenderer "run-step has no children; selecting it reports the change"
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
