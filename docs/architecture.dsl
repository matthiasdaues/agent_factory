workspace "Factory Flow Control" "The deterministic state-machine harness, CLI-agnostic dispatch mechanism, and generated catalog that govern how Agent Factory playbooks run." {

    model {
        humanOperator = person "Human Operator" "A person driving Agent Factory directly: running scripts by hand, committing code, approving phase gates."

        orchestratorAsTrigger = softwareSystem "Orchestrator-as-Trigger" "The nested orchestrator/ Python CLI. A peer of the Human Operator — invokes the same factory mechanisms programmatically instead of a human typing them. Holds no flow-control state of its own." "External"
        cliInvokedAgent = softwareSystem "CLI-Invoked Agent" "The Claude Code or Copilot CLI session that trigger dispatches, operating under the scoped permission allowlist trigger constructs for it." "External"
        gitPreCommit = softwareSystem "git / pre-commit" "The host git repository and its pre-commit hook set. Invokes transition-lint and the guardrail hook at the moments a git operation fires. Has no goal of its own." "External"

        factory = softwareSystem "Factory Flow Control" "Gates which files may be staged in which playbook phase, advances a run only when entry conditions hold, caps retry loops, and dispatches agents under a scoped allowlist — all from observable, git-ignored local state." {

            transitionLint = container "transition-lint" "Phase-ordering gate: blocks a staged file whose declared state differs from the marker's current state. Never evaluates entry_conditions — that is phase advance's job alone." "Python 3.8 stdlib"
            phaseCli = container "phase" "advance: moves the marker to its next state once entry_conditions hold. retry: caps how many times a phase's author step re-runs after a failing gate." "Python 3.8 stdlib"
            trigger = container "trigger" "Resolves a named agent or playbook step and dispatches it to a CLI session, interactive or unattended, under a hardcoded scoped permission allowlist." "Python 3.8 stdlib"
            indexLint = container "index-lint" "Regenerates the machine-readable catalog of every agent, skill, and playbook from source frontmatter. Never hand-edited." "Python 3.8 stdlib"
            runStep = container "run-step" "Skill: resolves what 'resume' means from observable state — the marker, gate results, open findings — never from a separately persisted execution status." "Agent-followed skill (prose procedure)"
            guardrailHook = container "block-dangerous-git.sh" "Denies a fixed list of destructive or gate-bypassing git commands before they run, for both supported CLIs." "Bash / PreToolUse hook"
            initFactory = container "init-factory" "Wires factory/, the guardrail hook, and gate config into a new or existing project, idempotently, without disturbing what is already there." "Python 3.8 stdlib"

            marker = container "Marker" ".agent-factory/playbook-state.yml — git-ignored, single-file run state: which playbook, which state, which iteration." "Filesystem (YAML)" "Data"
            fsmDefinition = container "Playbook FSM" "factory/playbooks/<name>.fsm.yml — states, entry_conditions, gate_conditions, halt_conditions for one playbook. Only greenfield-development has one today." "Filesystem (YAML)" "Data"
            catalog = container "INDEX.yaml" "Generated catalog of every agent, skill, and playbook, grouped by phase/category, with each playbook's derived agent sequence and fsm: pointer." "Filesystem (YAML)" "Data"
            modelConfig = container "model.conf" "Per-CLI tier -> model routing table that trigger resolves an agent's dispatch model against." "Filesystem (key-value)" "Data"
            findings = container "Findings" "docs/findings/*.md — status: open|resolved frontmatter, counted by no_open_findings gate conditions." "Filesystem (Markdown)" "Data"
        }

        # People/external systems -> factory
        humanOperator -> transitionLint "Stages files; the pre-commit hook runs this"
        humanOperator -> phaseCli "Runs phase advance / phase retry by hand"
        humanOperator -> trigger "Runs trigger to dispatch an agent"
        humanOperator -> runStep "Invokes to find out what to do next"
        humanOperator -> initFactory "Runs once per project"

        orchestratorAsTrigger -> phaseCli "Invokes programmatically — same peer relationship as Human Operator"
        orchestratorAsTrigger -> trigger "Invokes programmatically"

        gitPreCommit -> transitionLint "Fires at commit time, staged files as input"
        gitPreCommit -> guardrailHook "Fires PreToolUse before a shell command runs"

        # Inside factory
        trigger -> cliInvokedAgent "Dispatches: background subprocess or interactive session"
        trigger -> catalog "Resolves agent/playbook data (reuses index-lint's loaders)"
        trigger -> modelConfig "Resolves tier -> model (reuses matrix-lint's parser)"

        transitionLint -> marker "Reads current playbook + state"
        transitionLint -> fsmDefinition "Reads outputs: globs per state"

        phaseCli -> marker "Reads current state, or bootstraps at the FSM root"
        phaseCli -> marker "Writes state/iteration/recorded_at on a successful advance or allowed retry"
        phaseCli -> fsmDefinition "Reads entry_conditions, halt_conditions, transitions"
        phaseCli -> findings "Counts open findings for no_open_findings conditions"

        indexLint -> catalog "Generates from source frontmatter"

        runStep -> marker "Reads to resolve current playbook + state"
        runStep -> catalog "Reads fsm: field, and agents: as the fallback ordering"
        runStep -> phaseCli "Calls advance on a clean gate, retry on open findings"
        runStep -> trigger "Dispatches the resolved agent"

        initFactory -> guardrailHook "Symlinks into the target project's hook config"
        initFactory -> modelConfig "Copies as a starter, once, never touched again"

        deploymentEnvironment "Local" {
            deploymentNode "Developer Workstation" "macOS or Linux. Every mechanism is a stdlib-only script or shell hook run directly inside the project's git checkout — no server process, no network service." "git checkout" {
                containerInstance transitionLint
                containerInstance phaseCli
                containerInstance trigger
                containerInstance indexLint
                containerInstance runStep
                containerInstance guardrailHook
                containerInstance initFactory
                containerInstance marker
                containerInstance fsmDefinition
                containerInstance catalog
                containerInstance modelConfig
                containerInstance findings
            }
        }
    }

    views {
        systemContext factory "SystemContext" {
            include *
            autoLayout
        }

        container factory "Containers" {
            include *
            autoLayout
        }

        dynamic factory "PhaseAdvance" "UC-01 — Advance a Playbook Phase" {
            humanOperator -> phaseCli "Runs phase advance"
            phaseCli -> marker "Reads current state, or bootstraps at the FSM root"
            phaseCli -> fsmDefinition "Resolves forward transition + target's entry_conditions"
            phaseCli -> findings "Evaluates no_open_findings conditions"
            phaseCli -> marker "Writes state/iteration/recorded_at on a successful advance or allowed retry"
            autoLayout
        }

        dynamic factory "BlockOutOfPhaseCommit" "UC-02 — Block an Out-of-Phase Commit" {
            gitPreCommit -> transitionLint "Fires at commit time, staged files as input"
            transitionLint -> marker "Reads current playbook + state"
            transitionLint -> fsmDefinition "Reads outputs: globs per state"
            autoLayout
        }

        dynamic factory "ResumeAndDispatch" "UC-05 — Resume an Interrupted Playbook Run" {
            humanOperator -> runStep "Invokes to find out what to do next"
            runStep -> marker "Reads to resolve current playbook + state"
            runStep -> catalog "Reads fsm: field, and agents: as the fallback ordering"
            runStep -> phaseCli "Calls advance on a clean gate, retry on open findings"
            runStep -> trigger "Dispatches the resolved agent"
            trigger -> cliInvokedAgent "Dispatches: background subprocess or interactive session"
            autoLayout
        }

        deployment factory "Local" "Deployment" {
            include *
            autoLayout
        }

        styles {
            element "Person" {
                shape person
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Data" {
                shape cylinder
            }
        }

        theme default
    }
}
