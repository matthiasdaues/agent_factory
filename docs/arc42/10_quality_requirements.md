[back to index](../README.md)

# 10. Quality Requirements

This chapter defines testable quality scenarios for the precondition-based eligibility architecture. Each scenario follows the standard form: stimulus, environment, response, and response measure.

## 10.1 Quality Attribute Scenarios

### QS-1: Agent selection by precondition evidence

| Field             | Description                                                                                                                            |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Flexibility                                                                                                                            |
| Stimulus          | A feature needs only implementation, not architecture or planning work.                                                                |
| Environment       | Agent definitions declare `inputs.required` preconditions against repository artifacts.                                                |
| Response          | `intent select` evaluates preconditions and lists only the agents whose inputs are satisfied. The human selects from the eligible set. |
| Response measure  | Agents with unsatisfied preconditions are excluded. The eligible set reflects the current repository state, not a fixed sequence.      |

References: [architecture.dsl Eligibility Engine container](architecture.dsl), [section 5.3](05_building_block_view.md#53-level-2-component-view----eligibility-engine)

### QS-2: Human authority over agent selection

| Field             | Description                                                                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Controllability                                                                                                                              |
| Stimulus          | The Eligibility Engine classifies an agent as blocked, but the human wants to run it anyway.                                                 |
| Environment       | Normal operation. `intent select` shows both eligible and blocked agents with evidence.                                                      |
| Response          | The human sees the unsatisfied preconditions and may dispatch the agent via `trigger` regardless. No gate prevents human-initiated dispatch. |
| Response measure  | The agent runs. The unsatisfied preconditions are visible but not enforced as hard blocks for human invocation.                              |

References: [architecture.dsl](architecture.dsl), [section 5.3](05_building_block_view.md#53-level-2-component-view----eligibility-engine)

### QS-3: Clean Architecture dependency direction

| Field             | Description                                                                                                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Testability, Maintainability                                                                                                                                                    |
| Stimulus          | A developer adds a filesystem read or a lock acquisition call inside the Eligibility Engine container.                                                                          |
| Environment       | The architecture.dsl dependency rules are enforced by `dependency-check`.                                                                                                       |
| Response          | `dependency-check` detects the inward-violating import and fails.                                                                                                               |
| Response measure  | Exit code 1 with the violating import path named. The engine has zero relationships to state files in the DSL. All data reaches the engine as function arguments from adapters. |

References: [architecture.dsl Eligibility Engine container](architecture.dsl), [section 5.3](05_building_block_view.md#53-level-2-component-view----eligibility-engine)

### QS-4: Workstream identity immutability

| Field             | Description                                                                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Simplicity, Correctness                                                                                                                       |
| Stimulus          | Two CLI sessions read the same workstream state file concurrently.                                                                            |
| Environment       | Workstream state files under `.agent-factory/workstreams/` are immutable identity records (schema_version, workstream_id, topic, origin_ref). |
| Response          | Both sessions read the same immutable content. No locking or conflict detection is needed.                                                    |
| Response measure  | No write contention. No revision or digest fields to conflict on. Concurrent reads always see consistent state.                               |

References: [architecture.dsl Workstream State container](architecture.dsl)

### QS-5: Observable-state resume

| Field             | Description                                                                                                                                                            |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Resilience                                                                                                                                                             |
| Stimulus          | A session terminates unexpectedly (crash, network loss, user interrupt).                                                                                               |
| Environment       | Workstream state files and session bindings exist on disk.                                                                                                             |
| Response          | A new session reads the workstream identity, evaluates agent preconditions against the repository, and presents the eligible agent set. No prior process state needed. |
| Response measure  | The new session produces the same eligibility result as the interrupted session would have at the same commit. All state is derived from files on disk.                |

References: [architecture.dsl](architecture.dsl), [section 8](08_crosscutting_concepts.md)

### QS-6: Deterministic validation

| Field             | Description                                                                                                             |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Safety                                                                                                                  |
| Stimulus          | An agent commits code that violates dependency rules or exceeds CRAP score thresholds.                                  |
| Environment       | The implementation-agent dispatcher runs `crap-score` and `dependency-check` after each developer commit.               |
| Response          | The gate script detects the violation and fails. The dispatcher spawns a fresh developer agent with the failure report. |
| Response measure  | Exit code 1 from the gate. The developer agent that authored the code never validates its own work.                     |

References: [ADR-0012](../adr/0012-dispatcher-owned-semantic-gate-loop.md), [section 5.2.3](05_building_block_view.md#523-semantic-quality-gates-crap-score-mutation-analysis-dependency-check)

### QS-7: Plugin fails closed on control failure

| Field             | Description                                                                                                                               |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Safety                                                                                                                                    |
| Stimulus          | The OpenCode Factory plugin cannot load the step manifest, evaluate a permission, or create a worktree.                                   |
| Environment       | An OpenCode session with the Factory plugin active.                                                                                       |
| Response          | The plugin denies the operation. The error names the failed control and the recovery action.                                              |
| Response measure  | No tool invocation executes after the failure. The Factory entry flow stops. Usage capture failure does not trigger fail-closed behavior. |

References: [architecture.dsl OpenCode Plugin container](architecture.dsl), [section 8.14](08_crosscutting_concepts.md#814-opencode-plugin-as-enforcement-boundary)

### QS-8: CLI integration preserves existing CLI files

| Field             | Description                                                                                                                   |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Compatibility                                                                                                                 |
| Stimulus          | A project with Claude Code and Pi installed adds OpenCode as a third CLI target.                                              |
| Environment       | `init-factory` runs with `--add opencode`.                                                                                    |
| Response          | OpenCode files are created under `.opencode/`. Claude Code files under `.claude/` and Pi files under `.pi/` remain unchanged. |
| Response measure  | Zero modifications to files owned by other CLIs. One root `AGENTS.md` serves all CLIs.                                        |

References: [opencode-cli-integration.feature Rule: Project maintainer runs OpenCode alongside other Factory CLIs](../spec/opencode-cli-integration.feature)

### QS-9: Read-only preflight before installation

| Field             | Description                                                                                                                                                 |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Safety                                                                                                                                                      |
| Stimulus          | A newcomer runs the bootstrap script in a project directory.                                                                                                |
| Environment       | The target directory may contain existing configuration, uncommitted work, or a prior Factory installation.                                                 |
| Response          | The bootstrap checks host platform, required tools, Git state, network reachability, and target directory without writing, installing, or editing anything. |
| Response measure  | Zero filesystem writes during preflight. The preflight result is a data structure available for inspection before any consent prompt appears.               |

References: [architecture.dsl Distribution container](architecture.dsl), [section 5.8](05_building_block_view.md#58-level-2-component-view----distribution), [section 8.15](08_crosscutting_concepts.md#815-consent-gated-mutation-value-first-onboarding)

### QS-10: Consent-gated installation

| Field             | Description                                                                                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Quality attribute | Controllability                                                                                                                                              |
| Stimulus          | The bootstrap reaches the installation step after a clean preflight.                                                                                         |
| Environment       | The preflight result shows all checks passed. The newcomer sees an installation preview.                                                                     |
| Response          | The preview lists source, version, target path, interfaces to install, paths to create, and the uninstall command. Installation waits for consent.           |
| Response measure  | Blank input stops the sequence without installing. Declined consent leaves the target directory unchanged. Only an affirmative response starts installation. |

References: [architecture.dsl Distribution container](architecture.dsl), [section 6.10.1](06_runtime_view.md#6101-sequence-newcomer-installs-a-verified-factory-release), [section 8.15](08_crosscutting_concepts.md#815-consent-gated-mutation-value-first-onboarding)

### QS-11: Installation integrity verification

| Field             | Description                                                                                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Safety                                                                                                                                                            |
| Stimulus          | The bootstrap downloads a Factory release archive from the Distribution Remote.                                                                                   |
| Environment       | The release includes a SHA-256 checksum manifest alongside the archive.                                                                                           |
| Response          | The bootstrap computes the digest of the downloaded archive and compares it against the manifest entry. A mismatch aborts installation with a diagnostic message. |
| Response measure  | No archive with a failed digest check is extracted. The abort message names the expected and actual digests.                                                      |

References: [architecture.dsl install-agent-factory relationships](architecture.dsl), [section 6.10.1](06_runtime_view.md#6101-sequence-newcomer-installs-a-verified-factory-release)

### QS-12: First-session insight budget

| Field             | Description                                                                                                                             |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Usability                                                                                                                               |
| Stimulus          | A newcomer completes installation and starts a first session.                                                                           |
| Environment       | The Factory is installed and `init-factory` has run. The session agent (Virgil) starts.                                                 |
| Response          | The session presents a project insight (language, frameworks, test infrastructure, configuration) within the decision budget.           |
| Response measure  | The newcomer sees a useful project insight within two minutes of session start and three consent decisions after installation approval. |

References: [section 6.10.3](06_runtime_view.md#6103-sequence-first-session-delivers-project-insight), [value-first-onboarding-journey.feature Rule 7](../spec/value-first-onboarding-journey.feature)

### QS-13: First-task result budget

| Field             | Description                                                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Usability                                                                                                                             |
| Stimulus          | A newcomer completes the first session and approves the first task.                                                                   |
| Environment       | The Factory is installed, the first session has delivered project insight, and the newcomer has approved the first-task preview.      |
| Response          | The first task produces an inspectable result in an isolated sandbox. The newcomer can examine the result and choose its disposition. |
| Response measure  | The newcomer holds an inspectable first-task result within ten minutes and five consent decisions after installation approval.        |

References: [section 6.10.4](06_runtime_view.md#6104-sequence-first-task-runs-in-an-isolated-sandbox), [value-first-onboarding-journey.feature Rule 8](../spec/value-first-onboarding-journey.feature)

## 10.2 Quality Attribute Priority

| Priority | Quality attribute                  | Scenarios |
| -------- | ---------------------------------- | --------- |
| 1        | Flexibility (precondition routing) | QS-1      |
| 1        | Controllability (human authority)  | QS-2      |
| 1        | Testability (Clean Architecture)   | QS-3      |
| 1        | Resilience (observable resume)     | QS-5      |
| 2        | Simplicity (immutable state)       | QS-4      |
| 2        | Safety (deterministic validation)  | QS-6      |
| 2        | Safety (fail-closed plugin)        | QS-7      |
| 2        | Compatibility (CLI coexistence)    | QS-8      |
| 1        | Safety (read-only preflight)       | QS-9      |
| 1        | Controllability (consent gate)     | QS-10     |
| 2        | Safety (integrity verification)    | QS-11     |
| 2        | Usability (first-session insight)  | QS-12     |
| 2        | Usability (first-task result)      | QS-13     |

## Referenced from

- [09_architecture_decisions.md](09_architecture_decisions.md) — architecture decisions that underpin these scenarios
- [08_crosscutting_concepts.md](08_crosscutting_concepts.md) — principles that underpin QS-3, QS-6, QS-9, and QS-10
