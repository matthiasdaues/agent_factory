workspace "Orchestrator" "run-playbook — step-at-a-time FSM runner" {

    properties {
        "arc42.projected" "true"
    }

    model {
        user = person "User" "Initiates playbook runs, handles human gates"

        orchestrator = softwareSystem "Orchestrator (run-playbook)" "Replaces you pressing enter between agent sessions" {
            runPlaybook = container "run-playbook" "While loop calling phase/trigger scripts" "Python 3.10+ stdlib"
        }

        factory = softwareSystem "Factory Scripts" "Deterministic flow-control mechanisms" {
            phaseAdvance = container "phase advance" "Gate evaluation + marker write" "Python"
            phaseRetry = container "phase retry" "Iteration cap enforcement" "Python"
            trigger = container "trigger" "Agent resolution + CLI dispatch" "Python"
        }

        marker = softwareSystem "Playbook State Marker" ".agent-factory/playbook-state.yml" {
            tags "File"
        }

        fsm = softwareSystem "FSM Definitions" "factory/playbooks/*.fsm.yml" {
            tags "File"
        }

        aiCli = softwareSystem "AI CLI" "Claude Code or GitHub Copilot CLI"

        user -> orchestrator "invokes run-playbook"
        runPlaybook -> phaseAdvance "calls (check gate / advance marker)"
        runPlaybook -> phaseRetry "calls (check iteration cap)"
        runPlaybook -> trigger "calls (dispatch agent)"
        trigger -> aiCli "launches CLI session"
        phaseAdvance -> marker "reads / writes"
        phaseRetry -> marker "reads / writes"
        runPlaybook -> marker "reads (never writes)"
        runPlaybook -> fsm "reads (agent resolution, state detection)"
    }

    views {
        systemContext orchestrator "SystemContext" {
            include *
            autoLayout
        }

        container orchestrator "Containers" {
            include *
            autoLayout
        }

        theme default
    }

}
