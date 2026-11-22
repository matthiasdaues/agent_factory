# scope: global
workspace "Agent Factory" "Precondition-based agent eligibility, dispatch, validation, and usage capture for Agent Factory" {

    properties {
        "arc42.projected" "true"
    }

    model {
        # External actors
        humanOperator = person "Human Operator" "Person driving Agent Factory by hand"
        cliAgent = person "CLI-Invoked Agent" "A Claude Code, Codex, Copilot CLI, pi, or OpenCode session under a scoped allowlist" "Agent"
        newcomer = person "Newcomer" "Person installing and using Agent Factory for the first time"
        releaseMaintainer = person "Release Maintainer" "Person who builds and publishes Factory release assets"
        stakeholder = person "Stakeholder" "Person who owns the domain; confirms the scope map, every glossary term as the second glossary review, docs/agent-context.md, and every change to docs/testing.yaml"

        # Git as supporting actor
        git = softwareSystem "Git / pre-commit" "Version control and hook execution" "External"

        # Local output selected explicitly by the operator
        parquetFile = softwareSystem "Parquet Export" "Optional, attributable, atomically replaced local export; never authoritative state" "External"

        # Distribution remote for verified releases
        distributionRemote = softwareSystem "Distribution Remote" "HTTPS release base hosting bootstrap scripts, Factory archives, and checksum manifests" "External"

        # The project's git remote, which holds the ID counter
        projectRemote = softwareSystem "Project Git Remote" "The project's git remote: origin, or the URL that next-id gets with --remote; holds refs/ids/counters, the one ref with every ID sequence of the project" "External"

        # The project's own repository, which holds the ID counter while the project has no origin
        localCounter = softwareSystem "Local Counter" "The .git of the project's main repository: holds refs/ids/counters while the project has no origin, and the marker commit after the move; the git setting agent-factory.counterRemote in its .git/config names its path, so every worktree and local clone claims from it" "External"

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
                blockDangerousGit = component "block-dangerous-git.sh" "The one git guardrail of all five agent tools: refuses an agent destructive and remote git commands, gate bypasses, unchecked merges, and dispatch return-story and close --drop" "Bash"
                gitGuardPi = component "block-dangerous-git.ts" "pi's guardrail entry: passes each bash command to block-dangerous-git.sh and returns its answer" "TypeScript/Pi"
                concernLint = component "concern-lint" "Validates concern-oriented agent context: category headings, Read/Boundary path resolution, story concern vocabulary, and absence of legacy YAML files (CTX-* codes)" "Python"
                schemaValidate = component "schema-validate" "Deterministic JSON-Schema validator for research artifacts: stage 1 of the schema->policy->semantic validation order" "Python"
                policyValidate = component "policy-validate" "Deterministic research-policy validator: stage 2; --pipeline runs schema then policy in order, stopping at the first failure" "Python"
                crapScore = component "crap-score" "crap-score (--base <revision> | --all): runs the project's measuring commands, scores each kept function, and judges the changed ones against gates.crap-score.threshold; reads the threshold, the files pattern and the exclude list of each measure, and the exceptions register through one reader, the trusted gate source, whose only backend is the git ref of the integration branch; exits 0 on a pass, 1 when code fails, and 2 when it cannot measure; on exit 0 or 1 writes <report-dir>/<story-id>.json" "Python"
                gateSetupProof = component "gate-setup-proof" "gate-setup-proof --measure <name> --plant <folder>: runs crap-score in a temporary worktree of its own on planted code and checks four results before a person enables the gate; exits 0 when all checks pass, 1 when one fails, and 2 on a wrong call or wrong planted code" "Python"
                dependencyCheck = component "dependency-check" "Checks Python imports against docs/spec/dependency-rules.dsl; also runs as a pre-commit hook" "Bash/Python"
                testDesignVerify = component "test-design-verify" "Checks that every owned contract in the story's traces has a test assertion" "Python"
                mutationTesting = component "mutation-testing" "Runs gates.mutation-testing.command within its time limit and writes its result file" "Python"
                moduleGraphCheck = component "module-graph-check" "Derives module map from architecture.dsl, compares against concept outputs to determine architecture routing" "Bash/Python"
                fenceRunner = component "Fence Runner" "Deterministic output validation after agent activity; snapshots declared output patterns, compares post-activity filesystem state, and stores fence evidence" "Python"
                proposalValidator = component "Proposal Validator" "Checks proposal file existence, format, and required fields; returns the shared validator result shape" "Python"
                findingLint = component "finding-lint" "packages/factory/scripts/finding-lint [--staged]: reads each finding file that carries review_class or whose HEAD version carries it, and every register file; recomputes the severity from the basis, runs schema-validate on each register file with the schema of its folder, compares each file with its HEAD version for a lowering, a removal, or a lost review_class, and runs the git check of in_use when a code, runtime, or security finding is new or its basis or artifact changed; writes nothing and exits 1 on any violation" "Python" "Finding Classification"
                guardHumanFields = component "guard-human-fields" "packages/factory/config/hooks/guard-human-fields: reads one tool call as its CLI passes it and, for a write, the current content of the target; refuses a call that sets a human field in docs/findings/*.md, docs/findings/register/**/*.json, or the Appendix tables of docs/proposals/*.md, and every call that writes docs/findings/exceptions.md; for a patch call, apply_patch in Codex, Copilot CLI, and Pi or patch in OpenCode, reads the paths and lines from the patch text and refuses a patch it cannot parse when the raw text names a guarded path; exits 0 to pass and 2 to refuse; an agent that hides the field name, such as by building it from pieces in a script, passes it" "Hook script" "Finding Classification"
                guardClaudeCode = component "guard entry: Claude Code" "PreToolUse entries in .claude/settings.json for Edit, MultiEdit, Write, NotebookEdit, and Bash that run guard-human-fields" "Hook configuration" "Finding Classification"
                guardCodex = component "guard entry: Codex" "PreToolUse entries in .codex/hooks.json for Edit, Write, apply_patch, and Bash that run guard-human-fields" "Hook configuration" "Finding Classification"
                guardCopilot = component "guard entry: Copilot CLI" "preToolUse entries in a hook file under .github/hooks/, as step-guard.json has them, for edit, apply_patch, write_file, create, and bash; run guard-human-fields" "Hook configuration" "Finding Classification"
                guardPi = component "guard entry: Pi extension" "tool_call event of a project-local Pi extension for edit, write, write_file, create, apply_patch, and bash; runs guard-human-fields and blocks the call when the guard script is missing, unlike step-guard.ts" "TypeScript/Pi" "Finding Classification"
                premergeCheck = component "premerge-check" "Checks a branch head at every merge: the stop, the base, the scope, the reviews and findings, and every gate, rerun in a temporary worktree" "Python" "Finding Classification"
                mainCheckout = component "Primary Checkout Locator" "packages/factory/scripts/_main_checkout.py: finds the primary checkout from a linked worktree, so finding-lint blames the installed copy .agent-factory/factory/ of the primary checkout" "Python" "Finding Classification"
                ownershipContractTest = component "Ownership Contract Test" "Reads the core list and INDEX.yaml; fails when an entry's sample path matches no producing output pattern or more than one, or when the producer's declaration has no reviewed_by list; skips declarations with edits: wording" "pytest"
            }

            # Dispatcher — agent and model resolution, CLI session spawning
            dispatcher = container "Dispatcher" "Resolves agents/models and spawns CLI sessions" "Bash/Python" {
                trigger = component "trigger" "Dispatches named agent or playbook step to CLI" "Bash"
                indexLint = component "index-lint" "Generates INDEX.yaml from frontmatter and carries reviewed_by and edits of every output declaration; fails on a reviewer that is not an agent or stakeholder, or that lacks the artifact as a required or context input" "Python"
                dispatchCli = component "dispatch" "The run CLI on both ways: starts the run, moves each unit of work through the ledger, merges, and closes waves and the run" "Python"
                dispatchLedger = component "Ledger" "dispatch_lib.py: the ledger model and the transition table of the Ledger Entry Lifecycle" "Python"
                stopCheck = component "Stop Check" "Prints the stop notice and makes its caller exit 1 while a critical finding is unconfirmed" "Python" "Finding Classification"
                runAgent = component "run-agent (Pi extension)" "Pi model-callable tool: spawns a separate pi session to run one factory agent" "TypeScript/Pi"
                dispatchWave = component "dispatch-wave (Pi extension)" "Pi model-callable tool: runs a parallel wave of factory agents, each in its own git worktree, integrating premerge-check before merging" "TypeScript/Pi"
                openrouterDiscover = component "openrouter-discover" "Operator aid: queries OpenRouter catalog to curate/validate pi.* tier rows in model.conf (offline of the runtime path)" "Python"
            }

            # Usage Capture — with optional workstream context
            usageCaptureContainer = container "Usage Capture" "Normalizes CLI-native transcripts and appends versioned usage records with optional workstream context" "Python/Shell/TypeScript" {
                usageCapture = component "usage-capture" "Normalizes one CLI transcript and appends a canonical usage record; adds workstream_id and workstream_origin from the session binding when available" "Python"
            }

            # Distribution — component lifecycle and onboarding
            distribution = container "Distribution" "Installs, updates, removes, and reports opt-in Factory components; provides the value-first onboarding bootstrap, release building, and gate demonstration" "Bash/Python" {
                initFactory = component "init-factory" "Installs, updates, or removes the usage component and maintains the install manifest; on an update from a version before the layout release runs migrate-spec-layout as its last step and writes the new factory_version only after the script succeeds" "Python"
                updateFactory = component "update-factory" "Full update transaction: check mode, approval, verified staging, atomic application with rollback, local-change policy, source-boundary consent, and receipt" "Python"
                migrateSpecLayout = component "migrate-spec-layout" "Moves an installed project into the core artifact layout with git mv for tracked files and a plain move for untracked and ignored files, rewrites Markdown links, the factory hook block, and the DSL theme line, moves glossary terms into docs/spec/glossary.md, and undoes its own changes when it fails partway" "Python"
                removeFactory = component "remove-factory" "Performs complete Factory removal, including analysis and raw usage data" "Python"
                installAgentFactory = component "install-agent-factory" "Bootstrap script: read-only preflight, confirmed prerequisite fixes, release verification, installation preview, consent, and receipt with one next command" "Bash/Python"
                buildRelease = component "build-release" "Deterministic release builder: produces install-agent-factory, agent-factory.tar.gz, and SHA256SUMS with reproducible archive digests" "Python"
                hookDemo = component "hook-demo" "Gate demonstration: runs a real Factory gate against a disposable fixture, shows one failure-to-pass cycle, and removes the fixture without changing the target project" "Python"
            }

            # Storage
            workstreamState = container "Workstream State" "Immutable workstream identity records under .agent-factory/workstreams/; each records schema_version, workstream_id, topic, and origin_ref" "YAML files" "Storage"
            sessionBindings = container "Session Bindings" "Session-to-workstream mapping under .agent-factory/workstreams/sessions/<session-id>.yaml; records session_id, workstream_id, and bound_at" "YAML files" "Storage"
            stateFiles = container "State Files" "Git-ignored run state under .current-work/: ledgers, gate results, markers, briefs, and step manifests" "YAML/JSON files" "Storage"
            runWorktrees = container "Run Worktrees" "Git worktrees under .current-work/<feature-branch>/: the feature and story worktrees of an orchestrated run, and the temporary worktrees of premerge-check under premerge/" "git worktrees" "Storage"
            catalog = container "Catalog" "Generated INDEX.yaml of agents/skills/playbooks" "YAML file" "Storage"
            usageRecordContract = container "Usage Record Contract" "Factory-owned JSON Schema Draft 2020-12 and compatibility manifest; v1 schema includes optional workstream_id and workstream_origin fields" "JSON Schema/YAML" "Storage"
            rawUsageSpool = container "Raw Usage Spool" "Authoritative append-only top-level JSONL records under .agent-factory/usage/" "JSONL files" "Storage"
            installManifest = container "Install Manifest" "Records installed CLI integrations and opt-in components" "JSON file" "Storage"
            projectFilesystem = container "Project Filesystem" "Project source, configuration, and documentation that Factory changes only through defined contracts" "Filesystem" "Storage"
            measuringCommands = container "Measuring Commands" "Project-owned commands that gates.crap-score.measures names: each ready command answers whether its measuring command can run now; each measuring command writes one JSON array of rows to the path in GATE_OUTPUT, or exits non-zero and names the cause when it cannot measure; they refer to nothing under .agent-factory/" "Project scripts" "Project-owned"
            coreArtifacts = container "Core Artifacts" "The core files under docs/spec/ and the seam files docs/agent-context.md and docs/testing.yaml" "Markdown/DSL/YAML files" "Storage"
            workingOutput = container "Working Output" "Reports, QA strategies, and finding files under docs/spec/work/, docs/reviews/, and docs/findings/" "Markdown files" "Storage"
            findingRegisters = container "Finding Registers" "The folders docs/findings/register/<class>/, one per review class: one JSON register file <ID>.json per minor finding, with status open, resolved, or waived; a missing folder is an empty register" "JSON files" "Storage,Finding Classification"
            findingSchemas = container "Finding Schemas" "packages/factory/rulebooks/schemas/finding-register-<class>.schema.json, one per review class, each with the basis shape of its class from docs/spec/schemas/finding-basis.json" "JSON Schema" "Storage,Finding Classification"
            factorySettings = container "Factory Settings" "docs/factory-settings.yaml, tracked in git: the list release_tag_patterns names the git tags that count as releases for the in_use check, and the key integration_branch names the branch that the trusted gate source of crap-score reads, dev when the key is missing; the project writes it, and init-factory and update-factory never do" "YAML file" "Storage,Finding Classification"
            coreList = container "Core List" "rulebooks/core-artifacts.yaml under the Factory root, packages/factory/ in this repository and .agent-factory/factory/ in an installed project: every core and seam artifact with path_pattern, sample_path, family, and optional" "YAML file" "Storage"

            # Factory Agents — agent definitions run by a CLI session; each frontmatter declares tier, skills, inputs, and outputs
            factoryAgents = container "Factory Agents" "Agent definitions under packages/factory/agents/; a CLI session runs one definition and writes only the outputs it declares" "Markdown with YAML frontmatter" {
                requirementsAgent = component "requirements-agent" "Produces scope and behaviour: the scope map, the feature files, and the area specs; writes gaps reports and term candidates; hands off to the domain-modeling agent" "Agent definition, strong tier"
                domainModelingAgent = component "domain-modeling-agent" "Produces domain structure: the glossary, the entity model, state machines, validation rules, interface contracts, and schemas; moves confirmed term candidates into the glossary" "Agent definition, strong tier"
                architectureAgent = component "architecture-agent" "Produces architecture.dsl and dependency-rules.dsl; reads the entity model and state machines as context and files ARCH findings on a contradiction" "Agent definition, strong tier"
                testStrategyAgent = component "test-strategy-agent" "Produces docs/testing.yaml and the QA strategies; chooses the test guardrails and their thresholds; sets the CRAP gate up with the skill setup-crap-score; resolves QA findings it owns" "Agent definition, strong tier"
                virgil = component "virgil" "Produces docs/agent-context.md with capture-context during the fitting; seeds the ID counter in fitting step 4 and offers the move of a local counter to origin at the session start" "Agent definition"
                specReviewAgent = component "spec-review-agent" "Reviews the feature files, the glossary, the structure files, the area specs, and the schemas in a session separate from their producers; shares the glossary review with the stakeholder" "Agent definition"
                architectureReviewAgent = component "architecture-review-agent" "Reviews architecture.dsl and dependency-rules.dsl in a session separate from the architecture agent" "Agent definition"
                developerAgent = component "developer-agent" "Implements one unit of work test first and commits on its story branch; fixes one finding or one gate failure per spawn" "Agent definition"
                implementationAgent = component "implementation-agent" "Drives a run on both ways: runs dispatch, spawns the developer and code-review agents, and runs the gate-check step; by hand, waits for the User's go" "Agent definition"
                codeReviewAgent = component "code-review-agent" "Reviews one story branch, or the whole feature after the last wave, and files its findings" "Agent definition"
                qaAgent = component "qa-agent" "Writes the Fagan, security, and bug-hunt reports on the feature and files findings with run set" "Agent definition"
                migrationAgent = component "Migration Agent" "The role of the agent session that runs the one-time migration of every open finding without review_class: classifies each one with the rulebook, rewrites its artifact, fills Possible damage for a critical result, and changes files only after the stakeholder's pause point" "Agent session" "Finding Classification"
                reconciliationAgent = component "reconciliation-agent" "Compares the core with the code and writes one reconciliation report per run, one row per drift with the artifact's owner; edits no core file" "Agent definition"
            }

            # OpenCode Plugin — V2 plugin adapter for OpenCode CLI
            opencodePlugin = container "OpenCode Plugin" "V2 plugin adapter mapping Factory safety controls to OpenCode session hooks, tool restrictions, and worktree isolation" "TypeScript/OpenCode V2 Plugin API" {
                permissionEnforcer = component "Permission Enforcer" "Evaluates ordered allow/ask/deny rules and enforces step-manifest read/write boundaries through execute.before hooks" "TypeScript"
                toolRestrictor = component "Tool Restrictor" "Removes tools not in the active agent's declared set via session.hook context; enforces read-only for review agents" "TypeScript"
                usageObserver = component "Usage Observer" "Captures completed root and child session usage via execute.after hooks without double-counting child tokens" "TypeScript"
                worktreeStrategyComponent = component "Worktree Strategy" "Registers a Factory worktree strategy through ctx.worktree.transform; delegates branch and path creation to Factory scripts" "TypeScript"
                orientationInjector = component "Orientation Injector" "Injects AGENTS.opencode.md into session context via session.hook context; describes OpenCode tool names and session-start procedure" "TypeScript"
                guardOpenCode = component "guard entry: OpenCode plugin" "execute.before of packages/factory/config/plugins/agent-factory.ts for the tools edit, write, patch, shell, and execute: runs guard-human-fields, which checks the JavaScript of an execute call as the text of a shell call, and blocks the call when the guard script is missing; the first version of the plugin holds only this component, and the OpenCode CLI feature adds the others to the same file" "TypeScript" "Finding Classification"
                gitGuardOpenCode = component "git guardrail entry: OpenCode plugin" "OpenCode's guardrail entry: passes each shell command and the JavaScript of each execute call to block-dangerous-git.sh" "TypeScript"
                pluginHealthMonitor = component "Health Monitor" "Tracks plugin health lifecycle; fails closed on initialization, manifest, permission, or worktree failures with named recovery actions" "TypeScript"
            }

            # ID Allocation — claims the number of every new indexed artifact on the counter's remote
            idAllocation = container "ID Allocation" "Claims the number of every new story, finding, todo entry, and ADR as a leased push of refs/ids/counters on the counter's remote: the Project Git Remote, or the Local Counter while the project has no origin; plans the seed and moves a local counter to origin" "Script, git CLI" {
                nextId = component "next-id" "packages/factory/scripts/next-id: checks the prefix against its fixed prefix list, or the seed arguments; finds the remote from --remote, then agent-factory.counterRemote, then origin; calls the counter port; with --plan-seed counts the IDs in use on every local and remote-tracking branch and prints the seed command; with --move-to-origin moves the local counter and removes agent-factory.counterRemote; prints the ID or the seed lines on standard output. The only caller of the counter port" "Script"
                counterPort = component "Counter Port" "Four operations: claim <prefix> returns the next number of the prefix that no other caller holds; seed <number> [<PREFIX>=<n> ...] creates the counter and refuses when it exists; inspect reports whether the counter is missing, in use, or a marker commit; move <remote> carries the claim commit of the local counter to a remote without a counter" "Interface"
                gitRefAdapter = component "Git-Ref Adapter" "Implements the counter port on refs/ids/counters: works in a throwaway bare repository, writes a parentless claim commit with a new token, pushes it with a lease on the old SHA, and retries only on a stale lease, at most ten times in a row; for a move, sets the marker commit, a child of the claim commit, under a lease on the claim commit before it pushes with the create-only lease; finishes a stopped move from the marker's parent" "Script, git CLI"
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
                    containerInstance runWorktrees
                    containerInstance catalog
                    containerInstance usageRecordContract
                    containerInstance rawUsageSpool
                    containerInstance installManifest
                    containerInstance projectFilesystem
                    containerInstance opencodePlugin
                    containerInstance opencodeCatalog
                    containerInstance coreArtifacts
                    containerInstance workingOutput
                    containerInstance coreList
                    containerInstance findingRegisters
                    containerInstance findingSchemas
                    containerInstance factorySettings
                    containerInstance factoryAgents
                    containerInstance idAllocation
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
        humanOperator -> git "Commits, pushes, and merges the feature branch into dev"
        humanOperator -> trigger "Invokes via CLI"
        humanOperator -> usageAnalysisRuntime "Runs usage-query locally"
        humanOperator -> inputSnapshot "Starts a stable local query"
        humanOperator -> parquetExporter "Requests an explicit Parquet export"
        humanOperator -> duckdbUi "Optionally explores published views"
        humanOperator -> initFactory "Installs, updates, or removes the usage component"
        humanOperator -> updateFactory "Updates Factory core via the update transaction"

        # ================================================================
        # Relationships — Git hooks
        # ================================================================
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
        blockDangerousGit -> cliAgent "Refuses with exit 2 and names the reason, or allows with exit 0"
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
        initFactory -> installManifest "Reads the prior factory_version from install.json; records installed_components.usage, and the new version after migrate-spec-layout succeeds"
        updateFactory -> installManifest "Reads source and version; writes receipt after update"
        updateFactory -> distributionRemote "Downloads and verifies release assets for update"
        updateFactory -> humanOperator "Presents update preview for approval"
        updateFactory -> updateFactory "Stages, applies, and rolls back verified replacement"
        updateFactory -> initFactory "Runs the new version's init-factory after applying the staged replacement"
        initFactory -> migrateSpecLayout "Runs as its last step on an update from a version before the layout release"
        initFactory -> projectFilesystem "Lists old layout paths on a first install without moving them"
        initFactory -> humanOperator "Reports a failed layout migration and names the fix: run the update again"
        humanOperator -> migrateSpecLayout "Runs by hand, optionally with --dry-run"
        migrateSpecLayout -> git "Moves tracked files with git mv and removes tracked files with git rm"
        migrateSpecLayout -> projectFilesystem "Moves untracked and ignored files directly; reads and rewrites files under docs/ and the agent_factory_hook-* block of .pre-commit-config.yaml"
        migrateSpecLayout -> humanOperator "Reports moves, unrewritten old paths, duplicate terms, and two follow-up steps"
        removeFactory -> installedAnalysis "Removes during complete uninstall"
        removeFactory -> rawUsageSpool "Deletes during complete uninstall"

        # ================================================================
        # Relationships — Value-First Onboarding
        # ================================================================
        newcomer -> installAgentFactory "Downloads and runs the bootstrap with source and target"
        newcomer -> hookDemo "Optionally runs the gate demonstration before hook configuration"
        releaseMaintainer -> buildRelease "Builds a deterministic release from a versioned source tree"
        installAgentFactory -> distributionRemote "Downloads and verifies release assets over HTTPS"
        installAgentFactory -> initFactory "Delegates installation after release verification and approval"
        installAgentFactory -> installManifest "Records source selector, resolved source, and installation metadata"
        buildRelease -> distributionRemote "Publishes bootstrap, archive, and checksum manifest"
        hookDemo -> stateFiles "Creates and removes the disposable fixture"
        installAgentFactory -> newcomer "Presents installation preview and receipt"

        # ================================================================
        # Relationships — First-Session and First-Task Lifecycle
        # ================================================================
        newcomer -> cliAgent "Opens first Factory session via the installation receipt command"
        cliAgent -> hookDemo "Runs gate demonstration during first session"
        cliAgent -> git "Creates or removes detached worktree for the first-task sandbox"
        cliAgent -> dispatcher "Dispatches poc-spike inside the first-task sandbox"
        cliAgent -> workstreamState "Creates or selects production workstream for handoff"
        cliAgent -> sessionBindings "Creates session binding for production workstream"
        cliAgent -> newcomer "Presents evidence, previews, and results during onboarding"
        cliAgent -> installManifest "Reads installation state during first session"
        cliAgent -> projectFilesystem "Scans project files, copies retained artifacts to poc/spikes/, and runs capture-context --fold-context-map, which folds the context map into domain concerns of docs/agent-context.md"

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
        implementationAgent -> crapScore "Runs crap-score --base <feature-branch> in the gate-check step as a background job; on exit 2 spawns no developer agent and runs mark-blocked"
        implementationAgent -> dependencyCheck "Runs in the gate-check step, when the rules file exists"
        implementationAgent -> testDesignVerify "Runs in the gate-check step, when the story has a Test Design"
        implementationAgent -> mutationTesting "Runs in the gate-check step, when the gate is enabled"
        crapScore -> stateFiles "Writes its report on exit 0 or 1, and no report on exit 2"
        dependencyCheck -> stateFiles "Writes its result file"
        testDesignVerify -> stateFiles "Writes its result file"
        mutationTesting -> stateFiles "Writes its result file"
        mutationTesting -> coreArtifacts "Reads its command and time limit"
        crapScore -> coreArtifacts "Reads gates.crap-score in the folder it runs in: timeout_minutes and the measures; takes threshold, files and exclude from there only with --settings-from-folder, or when the ref, the file or gates.crap-score is missing on the integration branch, and prints which values it read from where"
        crapScore -> measuringCommands "Runs the ready command and then the measuring command of each measure, in list order, with GATE_OUTPUT set, within timeout_minutes for the whole run"
        measuringCommands -> crapScore "Writes one JSON array of rows to the path in GATE_OUTPUT; exits non-zero when it cannot measure, which crap-score turns into exit 2"
        crapScore -> git "Reads the diff from the merge base of --base to HEAD"
        crapScore -> git "Reads through the trusted gate source, from the ref of the integration branch: the section CRAP score of docs/findings/exceptions.md, and threshold and the files pattern and the exclude list of each measure from gates.crap-score of docs/testing.yaml; exits 2 when a measure that the branch names is missing at the story head, when integration_branch is not a non-empty string, or when docs/testing.yaml on the branch cannot be parsed or its gates.crap-score has no threshold"
        crapScore -> factorySettings "Reads integration_branch from the folder it runs in; uses dev when the file or the key is missing"
        crapScore -> git "Holds an operating-system file lock on crap-score/<measure>.lock under the git common directory for each measure with ready commands, from the ready commands through the measuring command; waits for it within timeout_minutes; the lock ends with the process"
        testStrategyAgent -> gateSetupProof "Runs the proof in setup-crap-score steps 5 and 7, before the person enables the gate"
        testStrategyAgent -> crapScore "Runs crap-score --all in setup-crap-score step 6 and reports the failing functions and the run time"
        testStrategyAgent -> measuringCommands "Writes the measuring commands and ready commands into the project in setup-crap-score, after the person confirms"
        gateSetupProof -> coreArtifacts "Reads the threshold and the measure from gates.crap-score, also with enabled: false"
        gateSetupProof -> git "Adds a temporary worktree at a fixed path under .current-work/gate-setup-proof/ with two commits of planted code, after it removes one that a crashed run left, and removes it afterwards; no branch of the project moves"
        gateSetupProof -> crapScore "Runs crap-score --base <start> --settings-from-folder in its worktree, whose first commit holds docs/factory-settings.yaml of the working tree, so the threshold, the files pattern and the exclude list come from the values the User has not committed yet, and compares the exit codes and the rows"

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
        cliAgent -> blockDangerousGit "Claude Code, Codex, Copilot CLI: each shell command fires the native hook"

        # ================================================================
        # Relationships — Core artifact ownership
        # ================================================================
        cliAgent -> factoryAgents "Runs one agent definition per session"
        requirementsAgent -> coreArtifacts "Produces the scope map, feature files, and area specs"
        requirementsAgent -> workingOutput "Writes gaps reports and term candidates"
        requirementsAgent -> domainModelingAgent "Names as the next producer in its handoff"
        stakeholder -> requirementsAgent "Confirms the scope map, one domain batch at a time"
        domainModelingAgent -> coreArtifacts "Produces the glossary and structure files; moves confirmed terms into the glossary"
        domainModelingAgent -> workingOutput "Proposes term definitions; sets its drift rows to fixed"
        domainModelingAgent -> stakeholder "Presents proposed term definitions, one domain area at a time"
        domainModelingAgent -> specReviewAgent "Names as the review in its handoff"
        domainModelingAgent -> architectureAgent "Names for the component pass when the entity model or state machines changed"
        architectureAgent -> coreArtifacts "Produces architecture.dsl and dependency-rules.dsl; reads the entity model and state machines"
        architectureAgent -> workingOutput "Files ARCH findings with the domain-modeling agent as owner; sets its drift rows to fixed"
        testStrategyAgent -> coreArtifacts "Produces docs/testing.yaml, including the gates section"
        testStrategyAgent -> workingOutput "Writes QA strategies; resolves QA findings it owns"
        testStrategyAgent -> stakeholder "Asks for confirmation of every change to docs/testing.yaml"
        virgil -> coreArtifacts "Produces docs/agent-context.md during the fitting"
        specReviewAgent -> coreArtifacts "Reviews behaviour and domain structure"
        specReviewAgent -> workingOutput "Sets fixed rows to confirmed or rejected; files SPEC and BUG findings"
        architectureReviewAgent -> coreArtifacts "Reviews architecture.dsl and dependency-rules.dsl"
        architectureReviewAgent -> workingOutput "Sets fixed rows to confirmed or rejected; files ATAM and BUG findings"
        developerAgent -> workingOutput "Writes drift rows with status open into its story's spec-feedback report"
        implementationAgent -> developerAgent "Spawns one per unit of work, and a fresh one per blocking finding or failed gate"
        implementationAgent -> requirementsAgent "Spawns as the owner of a drift row at the wave close"
        implementationAgent -> domainModelingAgent "Spawns as the owner of a drift row at the wave close"
        implementationAgent -> architectureAgent "Spawns as the owner of a drift row at the wave close"
        implementationAgent -> testStrategyAgent "Spawns as the owner of a drift row at the wave close, and for each open QA finding with owner test-strategy-agent"
        implementationAgent -> specReviewAgent "Spawns as the reviewer of a fixed row at the wave close"
        implementationAgent -> architectureReviewAgent "Spawns as the reviewer of a fixed row at the wave close"
        implementationAgent -> dispatchCli "Runs every subcommand except return-story, close, and close --drop"
        reconciliationAgent -> coreArtifacts "Reads the core to compare it with the code"
        reconciliationAgent -> workingOutput "Writes one reconciliation report per run"
        cliAgent -> reconciliationAgent "Dispatches the reconciliation run as orchestrator of the documentation-update playbook"
        cliAgent -> workingOutput "Reads every reconciliation report; sets the status of a row the stakeholder reviewed"
        cliAgent -> coreList "Reads the core list to tell rows on core artifacts from the others"
        cliAgent -> requirementsAgent "Dispatches as the owner of an open reconciliation row"
        cliAgent -> domainModelingAgent "Dispatches as the owner of an open reconciliation row"
        cliAgent -> architectureAgent "Dispatches as the owner of an open reconciliation row"
        cliAgent -> testStrategyAgent "Dispatches as the owner of an open reconciliation row"
        cliAgent -> virgil "Dispatches as the owner of an open reconciliation row"
        cliAgent -> specReviewAgent "Dispatches as the reviewer of a fixed reconciliation row"
        cliAgent -> architectureReviewAgent "Dispatches as the reviewer of a fixed reconciliation row"
        cliAgent -> stakeholder "Presents the fix of a row whose declared reviewer is the stakeholder"
        dispatchCli -> workingOutput "Reads spec-feedback reports and finding files; sets resolved at a merge"
        dispatchCli -> coreList "Reads the core list"
        dispatchCli -> dispatchLedger "Loads the ledger and changes states through the transition table"
        dispatchCli -> dispatchLedger "resume-gates sets a blocked entry with the reason gate cannot measure: crap-score back to dispatched, with its attempts and branch"
        dispatchLedger -> stateFiles "Reads and writes the ledger of the run"
        dispatchCli -> stateFiles "Writes step manifests; removes the state of the run at close"
        indexLint -> coreList "Reads sample paths for the reviewer check"
        indexLint -> factoryAgents "Reads output declarations with reviewed_by and edits"
        ownershipContractTest -> coreList "Reads every entry and its sample path"
        ownershipContractTest -> catalog "Counts the producing output patterns that match each sample path"
        dependencyCheck -> coreArtifacts "Reads the dependency rules"

        # ================================================================
        # Relationships — Counter IDs
        # ================================================================
        cliAgent -> nextId "Runs next-id <PREFIX> at the step of an ID producer that creates an indexed artifact, with the prefix of that artifact's kind"
        humanOperator -> nextId "Runs next-id --seed <number> by hand, when the project skipped the seed step"
        virgil -> nextId "Runs next-id --plan-seed and the printed seed command in fitting step 4, and next-id --move-to-origin at the session start, each after the User confirms"
        virgil -> localCounter "Sets agent-factory.counterRemote to the path of the main repository in fitting step 4, when the project has no origin"
        nextId -> counterPort "Calls claim <prefix>, seed, inspect, or move"
        nextId -> git "Lists file names, register id fields, and todo headings on every local and remote-tracking branch for --plan-seed; never reads body text"
        nextId -> findingRegisters "Counts the file name of each register file docs/findings/register/**/*.json on every local and remote-tracking branch as an ID in use for --plan-seed; cross-feature dependency of counter-ids-fitting BR-099 on DEC-60" "" "Finding Classification,Cross-feature"
        nextId -> localCounter "Reads agent-factory.counterRemote; removes it after a move succeeds"
        gitRefAdapter -> counterPort "Implements claim, seed, inspect, and move; returns the claimed number or the state of the counter"
        gitRefAdapter -> projectRemote "Fetches refs/ids/counters and pushes a claim commit with --force-with-lease; on a move, pushes the claim commit with the create-only lease"
        gitRefAdapter -> localCounter "Fetches refs/ids/counters and pushes a claim commit with --force-with-lease; on a move, sets the marker commit under a lease on the claim commit and never removes it"
        nextId -> cliAgent "Prints the ID on standard output, or exits non-zero and names the reason"
        initFactory -> projectRemote "Asks origin whether refs/ids/counters exists, when agent-factory.counterRemote is not set; derives fitting.counter_seeded from the answer; never seeds"
        # ================================================================
        # Relationships — Finding Classification
        # ================================================================
        # The stop
        dispatchCli -> stopCheck "Calls it before each subcommand that moves the run" "" "Finding Classification"
        premergeCheck -> stopCheck "Calls it before any other check" "" "Finding Classification"
        stopCheck -> workingOutput "Reads every finding file in the working tree" "" "Finding Classification"
        stopCheck -> git "Reads the HEAD version of each finding file" "" "Finding Classification"
        stopCheck -> cliAgent "Prints the stop notice; its caller exits 1" "" "Finding Classification"
        cliAgent -> premergeCheck "Runs it before each merge" "" "Finding Classification"
        premergeCheck -> stateFiles "Writes the premerge-check-ok marker on a pass; reads the mutation-testing result" "" "Finding Classification"
        blockDangerousGit -> stateFiles "Reads the markers and the ledgers" "" "Finding Classification"
        cliAgent -> dispatchCli "Runs a dispatch subcommand" "" "Finding Classification"
        stakeholder -> workingOutput "Writes the human fields of a finding file in an editor or with a ! command: confirms a stop, waives a finding, or lowers it" "" "Finding Classification"
        stakeholder -> workingOutput "Writes the exceptions register docs/findings/exceptions.md on dev: accepts a function above the CRAP threshold with its score and a reason"
        stakeholder -> findingRegisters "Writes the human fields of a register file in an editor or with a ! command: waives a minor finding, or writes the register file that replaces a lowered finding file" "" "Finding Classification"

        # The guard
        cliAgent -> guardClaudeCode "Claude Code: an Edit, MultiEdit, Write, NotebookEdit, or Bash call fires PreToolUse" "" "Finding Classification"
        cliAgent -> guardCodex "Codex: an Edit, Write, apply_patch, or Bash call fires PreToolUse" "" "Finding Classification"
        cliAgent -> guardCopilot "Copilot CLI: an edit, apply_patch, write_file, create, or bash call fires preToolUse" "" "Finding Classification"
        cliAgent -> guardPi "Pi: an edit, write, write_file, create, apply_patch, or bash call fires tool_call" "" "Finding Classification"
        cliAgent -> guardOpenCode "OpenCode: an edit, write, patch, shell, or execute call fires execute.before" "" "Finding Classification"
        guardClaudeCode -> guardHumanFields "Runs with the tool call on standard input" "" "Finding Classification"
        guardCodex -> guardHumanFields "Runs with the tool call on standard input" "" "Finding Classification"
        guardCopilot -> guardHumanFields "Runs with the tool call on standard input" "" "Finding Classification"
        guardPi -> guardHumanFields "Runs with the tool call; blocks the call when the script is missing" "" "Finding Classification"
        guardOpenCode -> guardHumanFields "Runs with the tool call; blocks the call when the script is missing" "" "Finding Classification"
        guardHumanFields -> workingOutput "Reads the current content of a guarded finding file for a write" "" "Finding Classification"
        guardHumanFields -> findingRegisters "Reads the current content of a guarded register file for a write" "" "Finding Classification"
        guardHumanFields -> projectFilesystem "Reads the current content of a proposal docs/proposals/*.md for a write" "" "Finding Classification"
        guardHumanFields -> cliAgent "Refuses a call that sets a human field with exit 2 and names the file, the field, and the stakeholder's way to write it" "" "Finding Classification"
        guardOpenCode -> cliAgent "Blocks the call through the plugin API when the guard refuses it or the guard script is missing" "" "Finding Classification"
        guardPi -> cliAgent "Blocks the call through the extension API when the guard refuses it or the guard script is missing" "" "Finding Classification"
        initFactory -> guardClaudeCode "Writes the PreToolUse entries for Edit, MultiEdit, Write, NotebookEdit, and Bash into .claude/settings.json beside the step-guard entries; update-factory runs it after each update, so an earlier install gets the missing entries" "" "Finding Classification"
        initFactory -> guardCodex "Writes the PreToolUse entries for Edit, Write, apply_patch, and Bash into .codex/hooks.json beside the step-guard entries" "" "Finding Classification"
        initFactory -> guardCopilot "Writes the preToolUse entries for edit, apply_patch, write_file, create, and bash into a hook file under .github/hooks/, beside step-guard.json" "" "Finding Classification"
        initFactory -> guardPi "Links the project-local guard extension beside step-guard.ts" "" "Finding Classification"
        initFactory -> projectFilesystem "Splices the factory hook block into .pre-commit-config.yaml; the block holds agent_factory_hook-finding-lint, which hook-metadata.yaml marks trade_off none and availability always, so fitting includes it without asking" "" "Finding Classification"
        updateFactory -> projectFilesystem "Re-splices the agent_factory_hook-* block of .pre-commit-config.yaml from the template of the new release with merge-precommit-config --update, so an earlier install gets agent_factory_hook-finding-lint; shows the diff and writes on yes" "" "Finding Classification"
        initFactory -> opencodePlugin "With --cli opencode, links .agent-factory/factory/config/plugins/agent-factory.ts into .opencode/plugins/; the OpenCode CLI feature extends the same plugin file" "" "Finding Classification,Cross-feature"

        # The lint and its git check
        git -> findingLint "Fires pre-commit with --staged" "" "Finding Classification"
        cliAgent -> findingLint "The validate skill runs finding-lint on the working tree" "" "Finding Classification"
        findingLint -> workingOutput "Reads each finding file that carries review_class, or whose HEAD version carries it" "" "Finding Classification"
        findingLint -> findingRegisters "Reads every register file" "" "Finding Classification"
        findingLint -> schemaValidate "Runs schema-validate on each register file with the schema of its folder" "" "Finding Classification"
        schemaValidate -> findingSchemas "Reads the register schema of the class" "" "Finding Classification"
        findingLint -> git "Reads the HEAD version of each file; blames the artifact range on the reviewed branch, on dev, main, origin/dev, origin/main, and each release tag" "" "Finding Classification"
        findingLint -> factorySettings "Reads release_tag_patterns when a git check is due; exits 1 and names the file and the key when either is missing" "" "Finding Classification"
        findingLint -> mainCheckout "Finds the primary checkout from a linked worktree" "" "Finding Classification"
        findingLint -> projectFilesystem "Blames the installed copy .agent-factory/factory/ with git blame --contents, when packages/factory/ exists" "" "Finding Classification"

        # The reviews
        cliAgent -> findingRegisters "A review skill records each minor finding as a register file with status open; the commit that fixes the finding sets resolved" "" "Finding Classification"
        specReviewAgent -> findingRegisters "Records each minor finding as a register file of its class" "" "Finding Classification"
        architectureReviewAgent -> findingRegisters "Records each minor finding as a register file of its class" "" "Finding Classification"

        # The migration
        cliAgent -> migrationAgent "Runs the one-time migration after docs/factory-settings.yaml is committed" "" "Finding Classification"
        migrationAgent -> workingOutput "Classifies every open finding file without review_class; after the pause point, writes review_class, basis, and the Why this severity line, removes each minor result, and sets deferred on a result without an artifact" "" "Finding Classification"
        migrationAgent -> stakeholder "Presents every result at one pause point before any file changes" "" "Finding Classification"
        migrationAgent -> findingRegisters "Writes one register file with status open for each minor result and for each line of the old .jsonl registers, then removes the three .jsonl files" "" "Finding Classification"
        migrationAgent -> git "Commits the migration, which fires finding-lint with --staged" "" "Finding Classification"

        # ================================================================
        # Relationships — Run Lifecycle
        # ================================================================
        # Who drives a run
        humanOperator -> implementationAgent "Asks for a run; by hand, gives each go"
        implementationAgent -> humanOperator "By hand, shows each decision point and waits for the go; shows the cause of a stop"
        humanOperator -> dispatchCli "Runs return-story, close, and close --drop"

        # The story workflow and the feature checks
        implementationAgent -> codeReviewAgent "Spawns the review of each story branch and each repeat review"
        codeReviewAgent -> workingOutput "Writes the review report and files its findings"
        qaAgent -> workingOutput "Writes the QA reports and files its findings"
        cliAgent -> codeReviewAgent "Runs the review of the whole feature"
        cliAgent -> qaAgent "Runs QA on the feature"
        developerAgent -> git "Commits on the story branch"
        implementationAgent -> stateFiles "Reads gate results; writes the list mutants"
        implementationAgent -> workingOutput "Files a QA finding for a surviving mutant; routes QA findings at the wave close"
        implementationAgent -> premergeCheck "Runs the feature merge check"

        # dispatch
        dispatchCli -> git "Cuts and merges branches, moves the feature branch back on a red suite, deletes merged branches"
        dispatchCli -> runWorktrees "Creates the worktrees of an orchestrated run; removes them at close"
        dispatchCli -> projectFilesystem "By hand, checks out the story branch, and the feature branch after premerge-check passes"
        dispatchCli -> coreArtifacts "Reads the test command, the attempt limits, and refuse_dirty_feature_worktree"
        dispatchCli -> premergeCheck "merge-story runs it first and merges only on exit 0; on exit 3 sets the entry blocked with the reason gate cannot measure: crap-score"
        dispatchCli -> measuringCommands "init runs the ready command of every measure of an enabled gate in the primary checkout, before it cuts a branch or writes the ledger"

        # premerge-check
        premergeCheck -> git "Checks the base, diff size, and scope, and reads reviews and findings at the head"
        premergeCheck -> runWorktrees "Removes a leftover worktree at its path under premerge/, adds a new one, and reruns the gates there"
        premergeCheck -> dependencyCheck "Reruns it in the temporary worktree"
        premergeCheck -> crapScore "Calls crap-score --base <target> in the temporary worktree, with the report in the primary checkout; exit 2 gives exit 3 when every other check that ran passed"
        premergeCheck -> measuringCommands "Runs the ready command of every measure of an enabled gate in the temporary worktree, before the test suite; a failure gives exit 3 at once"
        premergeCheck -> testDesignVerify "Reruns it in the temporary worktree"
        premergeCheck -> coreArtifacts "Reads the gates and the test command"

        # The git guardrail in Pi and OpenCode
        cliAgent -> gitGuardPi "pi: a bash call fires tool_call"
        gitGuardPi -> blockDangerousGit "Passes the command"
        gitGuardPi -> cliAgent "Blocks the call on a refusal"
        cliAgent -> gitGuardOpenCode "OpenCode: a shell or execute call fires execute.before"
        gitGuardOpenCode -> blockDangerousGit "Passes the command or the JavaScript"
        gitGuardOpenCode -> cliAgent "Blocks the call on a refusal"
        blockDangerousGit -> coreArtifacts "Reads the test commands for the allowlist"

        # The pre-commit hook
        git -> dependencyCheck "Fires pre-commit when a commit stages a .py file"

        initFactory -> localCounter "Asks the local counter whether refs/ids/counters exists, when agent-factory.counterRemote is set; derives fitting.counter_seeded from the answer; never seeds"
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
            humanOperator -> intentCli "Invokes intent select"
            intentCli -> agentLoader "Loads agent definitions from agents directory"
            intentCli -> preconditionEvaluator "Evaluates each agent's preconditions against the filesystem"
            preconditionEvaluator -> readinessEvaluator "Passes evaluation evidence for readiness derivation"
            readinessEvaluator -> recommendationClassifier "Classifies agents into eligible and blocked groups"
        }

        dynamic validator "GateCheckStep" "The gate-check step of ST-0350: a failing gate gets a fresh developer agent, and a surviving mutant becomes a QA finding" {
            implementationAgent -> dependencyCheck "Runs dependency-check on story/ST-0350"
            dependencyCheck -> stateFiles "Writes a passing result"
            implementationAgent -> crapScore "Runs crap-score --base feature/login as a background job and waits for its exit"
            crapScore -> stateFiles "Writes a failing row: login() scores 42, and exits 1"
            implementationAgent -> dispatchCli "Runs mark-failed ST-0350 --class acceptance_unmet"
            implementationAgent -> dispatchCli "Runs escalate ST-0350, only when the attempts on the tier are used up"
            implementationAgent -> dispatchCli "Runs re-dispatch ST-0350"
            implementationAgent -> stateFiles "Reads the failing result of crap-score"
            implementationAgent -> dispatchCli "Runs mark-dispatching ST-0350"
            implementationAgent -> developerAgent "Spawns a fresh developer agent with the output of crap-score"
            developerAgent -> git "Fixes login() and commits on story/ST-0350"
            implementationAgent -> dispatchCli "Runs mark-dispatched ST-0350"
            implementationAgent -> crapScore "Runs every gate again, and crap-score passes"
            implementationAgent -> mutationTesting "Runs mutation-testing, and a mutant in src/login.py:42 survives"
            implementationAgent -> workingOutput "Files QA-0012 with run feature/login and commits it on story/ST-0350"
            implementationAgent -> stateFiles "Writes the list mutants with finding QA-0012"
            implementationAgent -> humanOperator "Shows the cause and waits, when ST-0350 has stopped"
        }

        dynamic validator "PremergeStoryCheck" "premerge-check at the merge of story/ST-0350 reruns the gates in a temporary worktree, on both ways of driving a run" {
            dispatchCli -> premergeCheck "merge-story runs premerge-check feature/login story/ST-0350"
            premergeCheck -> stopCheck "Calls the stop check first"
            premergeCheck -> git "Checks the base, diff size, and scope, and reads reviews and findings at the head"
            premergeCheck -> runWorktrees "Removes any worktree left at premerge/ST-0350, then prunes"
            premergeCheck -> runWorktrees "Adds a detached worktree at the head of story/ST-0350"
            premergeCheck -> measuringCommands "Runs the ready command of each measure of crap-score in the worktree"
            premergeCheck -> dependencyCheck "Reruns dependency-check in the worktree"
            premergeCheck -> crapScore "Calls crap-score --base feature/login, whose measuring commands measure the code of the worktree"
            premergeCheck -> stateFiles "Reads the mutation-testing result, the one stored result"
            premergeCheck -> runWorktrees "Runs the test suite and the other gates, then removes the worktree"
            premergeCheck -> stateFiles "Writes premerge-check-ok for the head and exits 0"
            dispatchCli -> projectFilesystem "By hand, checks out feature/login only now"
            dispatchCli -> git "Merges story/ST-0350 into feature/login"
        }

        dynamic validator "GitGuardrailOneScript" "Agents in pi, OpenCode, and Claude Code issue dispatch close --drop, and every entry hands the command to the one script" {
            cliAgent -> gitGuardPi "pi: the bash call dispatch close --drop fires tool_call"
            gitGuardPi -> blockDangerousGit "Passes the command"
            gitGuardPi -> cliAgent "Blocks the call with the script's reason"
            cliAgent -> gitGuardOpenCode "OpenCode: the shell call dispatch close --drop fires execute.before"
            gitGuardOpenCode -> blockDangerousGit "Passes the command"
            gitGuardOpenCode -> cliAgent "Blocks the call with the script's reason"
            cliAgent -> gitGuardOpenCode "OpenCode: an execute call whose JavaScript runs dispatch close --drop fires execute.before"
            gitGuardOpenCode -> blockDangerousGit "Passes the JavaScript as command text"
            gitGuardOpenCode -> cliAgent "Blocks the call with the script's reason"
            cliAgent -> blockDangerousGit "Claude Code: the Bash call dispatch close --drop fires PreToolUse"
            blockDangerousGit -> cliAgent "Refuses with exit 2 and names the User as the one who drops a run"
        }

        dynamic usageAnalysisRuntime "UsageQuery" "Strict local usage query and optional result projection" {
            humanOperator -> inputSnapshot "Invokes usage-query for a published view"
            inputSnapshot -> rawUsageSpool "Snapshots sorted top-level JSONL evidence"
            inputSnapshot -> contractCheck "Supplies normalized evidence and records"
            contractCheck -> operationalPreflight "Registers valid rows and structured failures"
            operationalPreflight -> accountingRegistry "Supplies a valid rooted run graph"
            accountingRegistry -> queryModel "Applies the registered conservation rule"
            operationalPreflight -> queryModel "Registers valid and failure relations"
            queryModel -> resultAdapters "Projects the selected published view"
        }

        dynamic usageAnalysisRuntime "UsageParquetExport" "Verified explicit Parquet replacement" {
            humanOperator -> parquetExporter "Requests a published view as Parquet"
            queryModel -> parquetExporter "Supplies the selected stable view"
            parquetExporter -> parquetFile "Replaces the destination after verification"
        }

        component opencodePlugin "OpenCodePluginComponents" "OpenCode V2 plugin internals: permission enforcement, tool restriction, usage capture, worktree isolation, and health monitoring" {
            include *
            include stateFiles
            include opencodeCatalog
            include usageCapture
            include cliAgent
            autoLayout tb
        }

        component distribution "DistributionComponents" "Distribution internals: bootstrap, release building, installation, update, removal, and gate demonstration" {
            include *
            include newcomer
            include releaseMaintainer
            include distributionRemote
            include installManifest
            include projectFilesystem
            include stateFiles
            include usageRecordContract
            include installedAnalysis
            include rawUsageSpool
            include opencodeCatalog
            autoLayout tb
        }

        dynamic distribution "OnboardingInstallation" "Newcomer installs a verified Factory release through the bootstrap" {
            newcomer -> installAgentFactory "Runs the bootstrap with source selector and target"
            installAgentFactory -> newcomer "Presents installation preview from preflight and planned effects"
            installAgentFactory -> distributionRemote "Downloads and verifies release assets after approval (SHA-256)"
            installAgentFactory -> initFactory "Delegates project-level setup after verification"
            initFactory -> installManifest "Records installed paths and source metadata"
            installAgentFactory -> installManifest "Records source selector and installation metadata"
        }

        dynamic distribution "ReleaseBuild" "Release maintainer produces reproducible installation assets" {
            releaseMaintainer -> buildRelease "Runs build-release for a versioned source tree"
            buildRelease -> distributionRemote "Publishes bootstrap, archive, and checksum manifest"
        }

        dynamic distribution "UpdateTransactionCheck" "Check mode reports installed and candidate state without mutation" {
            humanOperator -> updateFactory "Runs update-factory --check"
            updateFactory -> installManifest "Reads source selector and installed version"
            updateFactory -> distributionRemote "Queries candidate version and digest"
            updateFactory -> humanOperator "Reports installed vs. candidate, local modifications, and planned effects"
        }

        dynamic distribution "UpdateTransaction" "Normal-update transaction: approval, staging with rollback, and receipt" {
            humanOperator -> updateFactory "Runs update-factory"
            updateFactory -> installManifest "Reads source selector and installed version"
            updateFactory -> humanOperator "Presents update preview"
            humanOperator -> updateFactory "Gives affirmative approval"
            updateFactory -> humanOperator "Presents source-change confirmation when source selector changed"
            humanOperator -> updateFactory "Confirms source change"
            updateFactory -> distributionRemote "Downloads and verifies release assets (SHA-256)"
            updateFactory -> updateFactory "Stages verified replacement alongside current installation"
            updateFactory -> updateFactory "Applies staged replacement; restores prior tree on failure"
            updateFactory -> initFactory "Runs the new version's init-factory; restores prior tree when it fails"
            updateFactory -> installManifest "Writes receipt: source, version, digest, changed paths"
        }

        dynamic distribution "UpdateLayoutMigration" "An update from a version before the layout release moves the project into the core artifact layout" {
            humanOperator -> updateFactory "Approves the update; the approval covers the layout move"
            updateFactory -> updateFactory "Applies the staged replacement"
            updateFactory -> initFactory "Runs the new version's init-factory"
            initFactory -> installManifest "Reads the prior factory_version from install.json"
            initFactory -> migrateSpecLayout "Runs migrate-spec-layout as its last step, because the prior version is older than the layout release"
            migrateSpecLayout -> git "Moves tracked files with git mv and removes clean tracked use-case files with git rm"
            migrateSpecLayout -> projectFilesystem "Moves untracked and ignored files directly, rewrites links, moves glossary terms, sets the factory hook block and the theme line"
            migrateSpecLayout -> humanOperator "Reports unrewritten old paths, duplicate terms, and the follow-up steps"
            initFactory -> installManifest "Writes the new factory_version after the script exits 0"
            updateFactory -> installManifest "Writes receipt: source, version, digest, changed paths"
        }

        dynamic distribution "UpdateLayoutMigrationRollback" "A failed layout migration undoes its own changes and the update rolls back" {
            updateFactory -> initFactory "Runs the new version's init-factory"
            initFactory -> installManifest "Reads the prior factory_version and writes no new one yet"
            initFactory -> migrateSpecLayout "Runs migrate-spec-layout as its last step"
            migrateSpecLayout -> git "Moves and removes tracked files"
            migrateSpecLayout -> projectFilesystem "Fails partway, then undoes every move, removal, and rewrite it made"
            migrateSpecLayout -> initFactory "Exits non-zero"
            initFactory -> humanOperator "Reports that the project keeps its old layout and prior factory_version, and names the fix: run the update again"
            initFactory -> updateFactory "Fails with a non-zero exit"
            updateFactory -> updateFactory "Restores the prior factory tree, install manifest, and instruction headers"
            updateFactory -> humanOperator "Reports the failure"
        }

        dynamic distribution "FirstSessionInsight" "First session delivers project insight before advanced configuration" {
            newcomer -> cliAgent "Opens first Factory session via the receipt command"
            cliAgent -> installManifest "Reads installation state"
            cliAgent -> projectFilesystem "Scans project filesystem (read-only)"
            cliAgent -> newcomer "Reports detected stack, test entry point, and safety signals"
            cliAgent -> newcomer "Recommends one next action; defers advanced configuration"
            cliAgent -> newcomer "Explains context capture scope, output, and validation"
            newcomer -> cliAgent "Gives affirmative consent for context capture"
            cliAgent -> newcomer "Runs capture-context and presents results"
            cliAgent -> newcomer "Offers gate demonstration"
            newcomer -> cliAgent "Gives affirmative consent for gate demonstration"
            cliAgent -> hookDemo "Runs gate demonstration on disposable fixture"
            hookDemo -> stateFiles "Creates and removes disposable fixture"
            cliAgent -> newcomer "Presents hook choices grouped by protected outcome"
        }

        dynamic factoryFlowControl "FirstTaskLifecycle" "Newcomer reaches an inspectable result in a detached-worktree sandbox; the first-task state machine owns disposition branching" {
            cliAgent -> newcomer "Presents task preview: goal, duration, artifacts, decisions, cleanup"
            newcomer -> cliAgent "Gives affirmative approval for the first task"
            cliAgent -> git "Creates detached worktree at .current-work/onboarding-spike/"
            cliAgent -> dispatcher "Dispatches poc-spike inside sandbox"
            cliAgent -> newcomer "Shows inspectable result and check evidence"
        }

        dynamic factoryFlowControl "FirstTaskLifecycleNoHead" "Newcomer reaches an inspectable result in a plain-directory sandbox; the first-task state machine owns disposition branching" {
            cliAgent -> newcomer "Presents task preview: goal, duration, artifacts, decisions, cleanup"
            newcomer -> cliAgent "Gives affirmative approval for the first task"
            cliAgent -> projectFilesystem "Creates plain sandbox directory at .current-work/onboarding-spike/"
            cliAgent -> dispatcher "Dispatches poc-spike inside sandbox"
            cliAgent -> newcomer "Shows inspectable result and check evidence"
        }

        dynamic opencodePlugin "OpenCodePermissionEnforcement" "Plugin enforces permission and step boundaries on tool invocation" {
            cliAgent -> permissionEnforcer "Tool invocation reaches execute.before hook"
            permissionEnforcer -> stateFiles "Reads active step manifest"
            permissionEnforcer -> cliAgent "Denies or allows the invocation"
        }

        dynamic opencodePlugin "OpenCodeWorktreeIsolation" "Plugin isolates a dispatched child session in a Factory-managed worktree" {
            cliAgent -> worktreeStrategyComponent "Dispatcher requests child session workspace"
            worktreeStrategyComponent -> stateFiles "Delegates branch and worktree creation to Factory scripts"
            cliAgent -> permissionEnforcer "Primary checkout receives session-scoped write denial"
        }

        component dispatcher "RunLifecycleDispatch" "Run lifecycle: dispatch with its ledger and the agents that drive a run" {
            include dispatchCli
            include dispatchLedger
            include stopCheck
            include premergeCheck
            include implementationAgent
            include developerAgent
            include codeReviewAgent
            include humanOperator
            include git
            include stateFiles
            include runWorktrees
            include projectFilesystem
            include workingOutput
            exclude "premergeCheck -> git"
            exclude "premergeCheck -> stateFiles"
            exclude "premergeCheck -> runWorktrees"
            exclude "premergeCheck -> stopCheck"
            exclude "stopCheck -> git"
            exclude "stopCheck -> workingOutput"
            exclude "humanOperator -> git"
            autoLayout lr
        }

        component validator "RunLifecycleMergeCheck" "Run lifecycle: the gates of the gate-check step and premerge-check, which reruns them at the merge" {
            include premergeCheck
            include crapScore
            include dependencyCheck
            include testDesignVerify
            include mutationTesting
            include measuringCommands
            include dispatchCli
            include implementationAgent
            include git
            include stateFiles
            include runWorktrees
            include coreArtifacts
            exclude "dispatchCli -> git"
            exclude "dispatchCli -> stateFiles"
            exclude "dispatchCli -> runWorktrees"
            exclude "dispatchCli -> coreArtifacts"
            exclude "implementationAgent -> dispatchCli"
            exclude "implementationAgent -> stateFiles"
            exclude "git -> dependencyCheck"
            autoLayout lr
        }

        component validator "CrapGate" "CRAP gate: crap-score, the project's measuring commands, the proof, and the callers of the gate" {
            include crapScore
            include gateSetupProof
            include premergeCheck
            include measuringCommands
            include implementationAgent
            include testStrategyAgent
            include dispatchCli
            include coreArtifacts
            include factorySettings
            include stateFiles
            include git
            exclude "premergeCheck -> git"
            exclude "dispatchCli -> git"
            exclude "dispatchCli -> stateFiles"
            exclude "dispatchCli -> coreArtifacts"
            exclude "implementationAgent -> dispatchCli"
            exclude "implementationAgent -> stateFiles"
            exclude "implementationAgent -> testStrategyAgent"
            exclude "implementationAgent -> premergeCheck"
            exclude "testStrategyAgent -> coreArtifacts"
            exclude "premergeCheck -> stateFiles"
            exclude "premergeCheck -> coreArtifacts"
            autoLayout lr
        }

        component validator "RunLifecycleGuardrail" "Run lifecycle: the git guardrail script and its entries in pi and OpenCode" {
            include blockDangerousGit
            include gitGuardPi
            include gitGuardOpenCode
            include cliAgent
            include stateFiles
            include coreArtifacts
            autoLayout lr
        }

        component factoryAgents "AgentOwnershipComponents" "Factory agents and the artifacts each one produces, reviews, or reports on" {
            include *
            include stakeholder
            include coreArtifacts
            include workingOutput
            include coreList
            include dispatchCli
            exclude cliAgent
            exclude indexLint
            autoLayout lr
        }

        dynamic factoryAgents "SpecificationHandoff" "The requirements agent hands off to the domain-modeling agent, which hands off to its review and to the architecture agent's component pass" {
            requirementsAgent -> coreArtifacts "Writes the scope map and the feature files"
            requirementsAgent -> domainModelingAgent "Names the domain-modeling agent as the next producer"
            domainModelingAgent -> coreArtifacts "Writes the glossary and the entity model, and the other structure files the domain needs"
            domainModelingAgent -> stakeholder "Presents proposed term definitions, one domain area at a time"
            domainModelingAgent -> specReviewAgent "Names the spec-review agent as the review"
            domainModelingAgent -> architectureAgent "Names the architecture agent when the entity model or state machines changed"
            specReviewAgent -> coreArtifacts "Reviews behaviour and domain structure in a separate session"
        }

        dynamic factoryAgents "RunOrchestrated" "An orchestrated run of ST-0350 and ST-0351 on feature/login, from dispatch init to dispatch close" {
            humanOperator -> implementationAgent "Asks for an orchestrated run of ST-0350 and ST-0351"
            implementationAgent -> dispatchCli "Runs init --mode orchestrated --stories ST-0350,ST-0351"
            dispatchCli -> git "Cuts feature/login from dev"
            dispatchCli -> runWorktrees "Creates the worktree of feature/login"
            dispatchCli -> dispatchLedger "Writes a ledger with both stories pending"
            dispatchLedger -> stateFiles "Saves the ledger of feature/login"
            implementationAgent -> dispatchCli "Runs plan and prepare-wave 1"
            dispatchCli -> runWorktrees "Creates one story worktree per story"
            implementationAgent -> developerAgent "Spawns one developer agent per story, and both run the story workflow"
            implementationAgent -> dispatchCli "Runs merge-story for each story whose workflow passed"
            implementationAgent -> dispatchCli "Runs close-wave 1 after the last story of wave 1 stops"
            cliAgent -> codeReviewAgent "Runs the review of the whole feature"
            cliAgent -> qaAgent "Runs QA on feature/login"
            implementationAgent -> premergeCheck "Runs premerge-check dev feature/login and shows the result"
            humanOperator -> git "Merges feature/login into dev"
            humanOperator -> dispatchCli "Runs dispatch close"
            dispatchCli -> runWorktrees "Stashes each worktree's uncommitted files under a name, then removes it"
            dispatchCli -> stateFiles "Removes the state of the run"
            dispatchCli -> git "Deletes the merged branches and lists each stash and each unmerged branch"
            cliAgent -> reconciliationAgent "Runs the reconciliation on dev, outside the run"
        }

        dynamic factoryAgents "RunByHand" "A run by hand of ST-0350 on feature/login: the implementation agent stops at every decision point and acts on the User's go" {
            humanOperator -> implementationAgent "Asks for a run by hand of ST-0350"
            implementationAgent -> dispatchCli "Runs init --mode by-hand --stories ST-0350"
            dispatchCli -> git "Cuts feature/login from dev and checks nothing out"
            dispatchCli -> dispatchLedger "Writes a ledger with mode by-hand"
            implementationAgent -> humanOperator "Names prepare-story ST-0350 and waits"
            humanOperator -> implementationAgent "Gives the go"
            implementationAgent -> dispatchCli "Runs prepare-story ST-0350"
            dispatchCli -> projectFilesystem "Checks out story/ST-0350 in the primary checkout"
            implementationAgent -> developerAgent "Spawns the developer agent, and ST-0350 runs the story workflow"
            implementationAgent -> dispatchCli "Runs merge-story ST-0350 --dry-run, which merges nothing"
            dispatchCli -> premergeCheck "Runs premerge-check on story/ST-0350"
            implementationAgent -> humanOperator "Shows the branch head, the findings, and the merge-check output, then names merge-story and waits"
            humanOperator -> implementationAgent "Gives the go"
            implementationAgent -> dispatchCli "Runs merge-story ST-0350"
            dispatchCli -> premergeCheck "Runs premerge-check again, while story/ST-0350 stays checked out"
            dispatchCli -> projectFilesystem "After exit 0, checks out feature/login and merges"
            implementationAgent -> dispatchCli "Runs close-wave 1 before the next story starts"
            cliAgent -> codeReviewAgent "Runs the review of the whole feature"
            cliAgent -> qaAgent "Runs QA on feature/login"
            implementationAgent -> premergeCheck "Runs premerge-check dev feature/login"
            implementationAgent -> humanOperator "Shows the result and stops before the merge into dev"
            humanOperator -> git "Merges feature/login into dev"
            humanOperator -> dispatchCli "Runs dispatch close with ! in Claude Code"
        }

        dynamic factoryAgents "PremergeStoryRefused" "premerge-check refuses the merge of story/ST-0350 by hand: the entry stays dispatched, and the failed check decides the next step" {
            implementationAgent -> dispatchCli "Runs merge-story ST-0350 after the User's go"
            dispatchCli -> premergeCheck "Runs premerge-check while story/ST-0350 stays checked out"
            premergeCheck -> dependencyCheck "Reruns dependency-check in the temporary worktree, and it fails"
            premergeCheck -> runWorktrees "Removes the temporary worktree and writes no marker"
            implementationAgent -> humanOperator "Shows the failed check, and ST-0350 stays dispatched on story/ST-0350"
            implementationAgent -> dependencyCheck "Runs the gate-check step, and dependency-check fails there too"
            implementationAgent -> dispatchCli "Runs mark-failed ST-0350 and re-dispatch ST-0350"
            implementationAgent -> dispatchCli "Runs mark-dispatching ST-0350"
            implementationAgent -> developerAgent "Spawns a fresh developer agent with the output of dependency-check"
            developerAgent -> git "Fixes the import and commits on story/ST-0350"
            implementationAgent -> dispatchCli "Runs mark-dispatched ST-0350"
            implementationAgent -> dependencyCheck "Runs the gate-check step again, and every gate passes"
            implementationAgent -> humanOperator "Names merge-story ST-0350 again and waits for the go"
        }

        dynamic factoryAgents "MergeCheckoutRefused" "Every check passes, but an uncommitted change stops the merge: git refuses it by hand, and merge-story refuses it in an orchestrated run" {
            implementationAgent -> dispatchCli "Runs merge-story ST-0350 after the User's go"
            dispatchCli -> premergeCheck "Runs premerge-check, and every check passes"
            dispatchCli -> projectFilesystem "Checks out feature/login, and git refuses over the uncommitted change to src/login.py"
            implementationAgent -> humanOperator "Shows the message unchanged: the files, the checkout, and that nothing merged"
            implementationAgent -> dispatchCli "Orchestrated: runs merge-story ST-0351 in the worktree of feature/login"
            dispatchCli -> premergeCheck "Runs premerge-check first, and it exits 0"
            dispatchCli -> runWorktrees "Finds an uncommitted change to a tracked file, names the files and the worktree, and merges nothing"
            implementationAgent -> humanOperator "Reports the message unchanged and does not repair the worktree"
        }

        dynamic factoryAgents "StoryWorkflow" "ST-0350 goes through the story workflow on story/ST-0350, on both ways of driving a run" {
            implementationAgent -> dispatchCli "Runs mark-dispatching ST-0350"
            implementationAgent -> developerAgent "Spawns the developer agent for ST-0350"
            developerAgent -> git "Implements ST-0350 test first and commits"
            implementationAgent -> dispatchCli "Runs mark-dispatched ST-0350"
            implementationAgent -> codeReviewAgent "Spawns the review of story/ST-0350"
            codeReviewAgent -> workingOutput "Writes code-review-ST-0350-2026-11-24.md and files IMPL-0091"
            developerAgent -> git "Commits the report and the finding"
            implementationAgent -> developerAgent "Spawns a fresh developer agent for IMPL-0091"
            developerAgent -> git "Fixes IMPL-0091 and commits"
            implementationAgent -> codeReviewAgent "Spawns a repeat review, which sets IMPL-0091 to resolved"
            implementationAgent -> crapScore "Runs the gate-check step: every gate of ST-0350"
            implementationAgent -> dispatchCli "Runs merge-story ST-0350"
            dispatchCli -> premergeCheck "Runs premerge-check feature/login story/ST-0350"
            dispatchCli -> git "Merges and sets status done in backlog/ST-0350.md in the merge commit"
            dispatchCli -> git "Runs the test suite and moves feature/login back on a red suite"
            dispatchCli -> dispatchLedger "Sets ST-0350 done, or blocked after a red suite"
        }

        dynamic factoryAgents "WaveClose" "The close of wave 1: each drift row reaches its owner and then its reviewer on the feature branch, the open QA findings go to their owners, and wave 2 waits for the wave record" {
            developerAgent -> workingOutput "Writes an open row into docs/spec/work/spec-feedback-ST-0318.md during the story"
            implementationAgent -> dispatchCli "Runs dispatch close-wave 1 after the last unit of work of wave 1 stops"
            dispatchCli -> workingOutput "Reads the spec-feedback reports of wave 1 at the head of feature/login"
            dispatchCli -> coreList "Reads the core list under its Factory root"
            dispatchCli -> dispatchLedger "Checks that each unit of work of wave 1 is done, returned, or has stopped"
            implementationAgent -> domainModelingAgent "Spawns the owner of the listed row on feature/login, one session at a time"
            domainModelingAgent -> coreArtifacts "Changes validation-rules.md"
            domainModelingAgent -> workingOutput "Sets the row to fixed and commits it with the change"
            implementationAgent -> specReviewAgent "Spawns the owner's reviewer on feature/login"
            specReviewAgent -> coreArtifacts "Reviews the change"
            specReviewAgent -> workingOutput "Sets the row to confirmed or rejected and commits the status"
            implementationAgent -> dispatchCli "Runs dispatch close-wave 1 again"
            dispatchLedger -> stateFiles "Saves the wave record of wave 1"
            implementationAgent -> workingOutput "Reads the open QA findings of wave 1 and their owners"
            implementationAgent -> dispatchCli "Runs dispatch add QA-0012, whose owner is planning-agent"
            implementationAgent -> testStrategyAgent "Spawns the test-strategy agent for each QA finding with owner test-strategy-agent, and wave 2 waits for every spawn"
            implementationAgent -> dispatchCli "Runs dispatch prepare-wave 2"
            dispatchLedger -> stateFiles "Reads the wave record of wave 1"
        }

        dynamic factoryAgents "ReconciliationBackfeed" "After a reconciliation run, the orchestrator of the documentation-update playbook brings each row back to its owner and then to the owner's reviewer" {
            cliAgent -> reconciliationAgent "Dispatches the reconciliation run"
            reconciliationAgent -> coreArtifacts "Reads the core to compare it with the code"
            reconciliationAgent -> workingOutput "Writes the run's report, one open row per new drift with the artifact's owner"
            cliAgent -> workingOutput "Reads every reconciliation report, not only the new one"
            cliAgent -> coreList "Reads the core list to tell rows on core artifacts from the others"
            cliAgent -> architectureAgent "Dispatches the owner of an open row, naming the row and the report and no skill"
            architectureAgent -> coreArtifacts "Changes architecture.dsl with the skill its own definition names for it"
            architectureAgent -> workingOutput "Sets the row to fixed in the same commit as the change"
            cliAgent -> architectureReviewAgent "Dispatches the reviewer that reviewed_by names, one session at a time"
            architectureReviewAgent -> coreArtifacts "Reviews the change"
            architectureReviewAgent -> workingOutput "Sets the row to confirmed or rejected"
            cliAgent -> stakeholder "Presents the fix when reviewed_by names the stakeholder, after any agent reviewer confirmed it"
            cliAgent -> workingOutput "Sets the row to confirmed or rejected as the stakeholder decides"
            cliAgent -> workingOutput "Checks the DONE list: no row of any report is open, or fixed on a core artifact"
        }

        component idAllocation "IdAllocationComponents" "ID allocation internals: next-id, the counter port, and the git-ref adapter on the counter's remote" {
            include *
            include initFactory
            include virgil
            autoLayout lr
        }

        dynamic idAllocation "IdClaimStaleLeaseRetry" "A claim of next-id ST meets a stale lease, because another caller claimed first, and succeeds on the second try" {
            cliAgent -> nextId "Runs next-id ST from create-backlog-stories"
            nextId -> counterPort "Calls claim ST on the URL of origin"
            gitRefAdapter -> projectRemote "Fetches refs/ids/counters into a throwaway bare repository and reads ST=1012"
            gitRefAdapter -> projectRemote "Pushes a claim commit with ST=1013 under the lease on the old SHA; the remote reports a stale lease, because another caller claimed FAGAN-1004 first"
            gitRefAdapter -> projectRemote "Waits a random 0.1 to 1 second, fetches again, and reads ST=1012 and FAGAN=1004"
            gitRefAdapter -> projectRemote "Pushes a claim commit with ST=1013 under the lease on the new SHA; the remote accepts it"
            gitRefAdapter -> counterPort "Returns 1013 and deletes the throwaway repository"
            nextId -> cliAgent "Prints ST-1013 and exits 0"
        }

        dynamic idAllocation "IdMoveToOrigin" "next-id --move-to-origin sets the marker on the local counter first and then pushes the claim commit to origin, each under a lease" {
            virgil -> nextId "Runs next-id --move-to-origin at the session start, after the User confirms the move"
            nextId -> localCounter "Reads agent-factory.counterRemote, the path of the main repository"
            nextId -> counterPort "Calls move to the URL of origin"
            gitRefAdapter -> localCounter "Fetches refs/ids/counters and reads the claim commit C with ST=0012"
            gitRefAdapter -> localCounter "Replaces refs/ids/counters with the marker commit moved=<origin>, whose parent is C, under the lease on C; the local counter accepts it"
            gitRefAdapter -> projectRemote "Pushes C from a throwaway bare repository to refs/ids/counters with --force-with-lease=refs/ids/counters:; origin holds no counter and accepts it"
            gitRefAdapter -> counterPort "Returns moved"
            nextId -> localCounter "Removes agent-factory.counterRemote and exits 0"
        }

        dynamic idAllocation "IdMoveToOriginResume" "A second next-id --move-to-origin finishes a move that stopped after the marker, taking the claim commit C from the marker's parent" {
            virgil -> nextId "Runs next-id --move-to-origin again at the next session start, after the User confirms the move"
            nextId -> localCounter "Reads agent-factory.counterRemote, which the stopped move left set"
            nextId -> counterPort "Calls move to the URL of origin"
            gitRefAdapter -> localCounter "Fetches refs/ids/counters, reads the marker commit moved=<origin>, and takes C with ST=0012 from its parent"
            gitRefAdapter -> projectRemote "Asks origin for refs/ids/counters with git ls-remote; origin holds no counter"
            gitRefAdapter -> projectRemote "Pushes C from a throwaway bare repository to refs/ids/counters with --force-with-lease=refs/ids/counters:; origin accepts it"
            gitRefAdapter -> counterPort "Returns moved"
            nextId -> localCounter "Removes agent-factory.counterRemote and exits 0"
        }

        component validator "FindingClassification" "Finding classification: the stop in dispatch and premerge-check, the guard on human fields in every CLI, finding-lint with its git check, the registers, and the migration" {
            include "element.tag==Finding Classification"
            include cliAgent
            include stakeholder
            include git
            include workingOutput
            include stateFiles
            include projectFilesystem
            include schemaValidate
            include blockDangerousGit
            include dispatchCli
            include nextId
            include initFactory
            include updateFactory
            include opencodePlugin
            exclude specReviewAgent
            exclude architectureReviewAgent
            autoLayout lr
        }

        dynamic dispatcher "CriticalStop" "A critical finding stops dispatch and merge until the stakeholder confirms the damage checks" {
            cliAgent -> dispatchCli "Runs dispatch prepare-wave"
            dispatchCli -> stopCheck "Calls the stop check before the subcommand"
            stopCheck -> workingOutput "Reads BUG-0037.md: severity critical, stop_confirmed_by empty"
            stopCheck -> git "Reads the HEAD version of BUG-0037.md, which is not confirmed either"
            stopCheck -> cliAgent "Prints the stop notice; dispatch writes nothing and exits 1"
            cliAgent -> premergeCheck "Runs premerge-check for a story branch"
            premergeCheck -> stopCheck "Calls the stop check before any other check"
            stopCheck -> cliAgent "Prints the same stop notice; premerge-check writes no marker and exits 1"
            cliAgent -> blockDangerousGit "Runs git merge"
            blockDangerousGit -> stateFiles "Finds no premerge-check-ok marker"
            blockDangerousGit -> cliAgent "Denies the merge"
            stakeholder -> workingOutput "Runs each damage check, then writes stop_confirmed_by and stop_confirmed_reason in an editor"
            cliAgent -> dispatchCli "Runs dispatch prepare-wave again"
            dispatchCli -> stopCheck "Calls the stop check"
            stopCheck -> workingOutput "Finds both confirmation fields with text; the stop ends, and BUG-0037 loops like a major finding"
        }

        dynamic validator "GuardRefusesHumanField" "A headless run tries to confirm its own stop, and the guard refuses the edit" {
            cliAgent -> guardClaudeCode "Edit call adds stop_confirmed_by: human to docs/findings/BUG-0037.md"
            guardClaudeCode -> guardHumanFields "Runs guard-human-fields with the call"
            guardHumanFields -> cliAgent "Finds stop_confirmed_by in new_string and not in old_string; exits 2 and names the file, the field, and the ! command"
        }

        dynamic opencodePlugin "GuardFailsClosed" "The guard script is missing from an OpenCode install, and the plugin blocks the call" {
            cliAgent -> guardOpenCode "A write call on docs/findings/FAGAN-0042.md fires execute.before"
            guardOpenCode -> guardHumanFields "Looks for the guard script and finds none"
            guardOpenCode -> cliAgent "Blocks the call and names the missing script"
        }

        dynamic validator "FindingLintCommit" "The pre-commit run of finding-lint checks a new register file against its schema and rejects a new finding whose in_use answer git contradicts" {
            git -> findingLint "Runs finding-lint --staged for a commit that adds FAGAN-0042.md and register file security/SEC-0012.json"
            findingLint -> findingRegisters "Reads the staged SEC-0012.json"
            findingLint -> schemaValidate "Runs schema-validate on SEC-0012.json with the security schema"
            schemaValidate -> findingSchemas "Reads finding-register-security.schema.json"
            findingLint -> workingOutput "Reads the staged FAGAN-0042.md: review_class code, in_use false"
            findingLint -> git "Reads the HEAD versions; neither file exists there, so the git check is due for both"
            findingLint -> factorySettings "Reads release_tag_patterns"
            findingLint -> git "Blames the artifact range on the reviewed branch, then on dev, main, origin/dev, origin/main, and each release tag"
            findingLint -> mainCheckout "Finds the primary checkout, because the commit runs in a linked worktree"
            findingLint -> projectFilesystem "Blames the installed copy in the primary checkout with --contents"
            findingLint -> git "Finds every line identity of FAGAN-0042 on dev; exits 1 with artifact lines exist unchanged on dev"
        }

        dynamic factoryAgents "FindingMigration" "The one-time migration classifies every open finding without review_class, and the stakeholder confirms each result before any file changes" {
            cliAgent -> migrationAgent "Runs the migration after docs/factory-settings.yaml is committed"
            migrationAgent -> workingOutput "Classifies each open finding file without review_class with the rulebook"
            migrationAgent -> stakeholder "Presents every result at one pause point"
            stakeholder -> workingOutput "Confirms the stop of each critical result"
            migrationAgent -> workingOutput "Writes review_class, basis, and Why this severity; removes BUG-0067.md; sets deferred on RETRO-0002.md"
            migrationAgent -> findingRegisters "Writes code/BUG-0067.json and document/RECON-0027.json with status open; removes the three .jsonl files"
            migrationAgent -> git "Commits the migration"
            git -> findingLint "Fires pre-commit with --staged"
            findingLint -> factorySettings "Reads release_tag_patterns for the git check of each migrated code, runtime, or security finding"
        }

        deployment * "Release 1" "Deployment" "Local, process-bound release-1 deployment" {
            include *
            autoLayout lr
        }

        theme ../assets/themes/default/theme.json

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
            element "Project-owned" {
                border dashed
                background #F2F2F2
                color #000000
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
        }
    }
}
