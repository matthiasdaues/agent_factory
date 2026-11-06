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

References: [architecture.dsl Eligibility Engine container](../spec/architecture.dsl), [section 5.3](05_building_block_view.md#53-level-2-component-view----eligibility-engine)

### QS-2: Human authority over agent selection

| Field             | Description                                                                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Controllability                                                                                                                              |
| Stimulus          | The Eligibility Engine classifies an agent as blocked, but the human wants to run it anyway.                                                 |
| Environment       | Normal operation. `intent select` shows both eligible and blocked agents with evidence.                                                      |
| Response          | The human sees the unsatisfied preconditions and may dispatch the agent via `trigger` regardless. No gate prevents human-initiated dispatch. |
| Response measure  | The agent runs. The unsatisfied preconditions are visible but not enforced as hard blocks for human invocation.                              |

References: [architecture.dsl](../spec/architecture.dsl), [section 5.3](05_building_block_view.md#53-level-2-component-view----eligibility-engine)

### QS-3: Clean Architecture dependency direction

| Field             | Description                                                                                                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Testability, Maintainability                                                                                                                                                    |
| Stimulus          | A developer adds a filesystem read or a lock acquisition call inside the Eligibility Engine container.                                                                          |
| Environment       | `dependency-check` enforces the rules of `dependency-rules.dsl`.                                                                                                                |
| Response          | `dependency-check` detects the inward-violating import and fails.                                                                                                               |
| Response measure  | Exit code 1 with the violating import path named. The engine has zero relationships to state files in the DSL. All data reaches the engine as function arguments from adapters. |

References: [architecture.dsl Eligibility Engine container](../spec/architecture.dsl), [section 5.3](05_building_block_view.md#53-level-2-component-view----eligibility-engine)

### QS-4: Workstream identity immutability

| Field             | Description                                                                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Simplicity, Correctness                                                                                                                       |
| Stimulus          | Two CLI sessions read the same workstream state file concurrently.                                                                            |
| Environment       | Workstream state files under `.agent-factory/workstreams/` are immutable identity records (schema_version, workstream_id, topic, origin_ref). |
| Response          | Both sessions read the same immutable content. No locking or conflict detection is needed.                                                    |
| Response measure  | No write contention. No revision or digest fields to conflict on. Concurrent reads always see consistent state.                               |

References: [architecture.dsl Workstream State container](../spec/architecture.dsl)

### QS-5: Observable-state resume

| Field             | Description                                                                                                                                                            |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Resilience                                                                                                                                                             |
| Stimulus          | A session terminates unexpectedly (crash, network loss, user interrupt).                                                                                               |
| Environment       | Workstream state files and session bindings exist on disk.                                                                                                             |
| Response          | A new session reads the workstream identity, evaluates agent preconditions against the repository, and presents the eligible agent set. No prior process state needed. |
| Response measure  | The new session produces the same eligibility result as the interrupted session would have at the same commit. All state is derived from files on disk.                |

References: [architecture.dsl](../spec/architecture.dsl), [section 8](08_crosscutting_concepts.md)

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

References: [architecture.dsl OpenCode Plugin container](../spec/architecture.dsl), [section 8.14](08_crosscutting_concepts.md#814-opencode-plugin-as-enforcement-boundary)

### QS-8: CLI integration preserves existing CLI files

| Field             | Description                                                                                                                   |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Compatibility                                                                                                                 |
| Stimulus          | A project with Claude Code and Pi installed adds OpenCode as a third CLI target.                                              |
| Environment       | `init-factory` runs with `--add opencode`.                                                                                    |
| Response          | OpenCode files are created under `.opencode/`. Claude Code files under `.claude/` and Pi files under `.pi/` remain unchanged. |
| Response measure  | Zero modifications to files owned by other CLIs. One root `AGENTS.md` serves all CLIs.                                        |

References: [opencode-cli-integration.feature Rule: Project maintainer runs OpenCode alongside other Factory CLIs](../spec/features/opencode-cli-integration.feature)

### QS-9: Read-only preflight before installation

| Field             | Description                                                                                                                                                 |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Safety                                                                                                                                                      |
| Stimulus          | A newcomer runs the bootstrap script in a project directory.                                                                                                |
| Environment       | The target directory may contain existing configuration, uncommitted work, or a prior Factory installation.                                                 |
| Response          | The bootstrap checks host platform, required tools, Git state, network reachability, and target directory without writing, installing, or editing anything. |
| Response measure  | Zero filesystem writes during preflight. The preflight result is a data structure available for inspection before any consent prompt appears.               |

References: [architecture.dsl Distribution container](../spec/architecture.dsl), [section 5.8](05_building_block_view.md#58-level-2-component-view----distribution), [section 8.15](08_crosscutting_concepts.md#815-consent-gated-mutation-value-first-onboarding)

### QS-10: Consent-gated installation

| Field             | Description                                                                                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Quality attribute | Controllability                                                                                                                                              |
| Stimulus          | The bootstrap reaches the installation step after a clean preflight.                                                                                         |
| Environment       | The preflight result shows all checks passed. The newcomer sees an installation preview.                                                                     |
| Response          | The preview lists source, version, target path, interfaces to install, paths to create, and the uninstall command. Installation waits for consent.           |
| Response measure  | Blank input stops the sequence without installing. Declined consent leaves the target directory unchanged. Only an affirmative response starts installation. |

References: [architecture.dsl Distribution container](../spec/architecture.dsl), [section 6.10.1](06_runtime_view.md#6101-sequence-newcomer-installs-a-verified-factory-release), [section 8.15](08_crosscutting_concepts.md#815-consent-gated-mutation-value-first-onboarding)

### QS-11: Installation integrity verification

| Field             | Description                                                                                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Safety                                                                                                                                                            |
| Stimulus          | The bootstrap downloads a Factory release archive from the Distribution Remote.                                                                                   |
| Environment       | The release includes a SHA-256 checksum manifest alongside the archive.                                                                                           |
| Response          | The bootstrap computes the digest of the downloaded archive and compares it against the manifest entry. A mismatch aborts installation with a diagnostic message. |
| Response measure  | No archive with a failed digest check is extracted. The abort message names the expected and actual digests.                                                      |

References: [architecture.dsl install-agent-factory relationships](../spec/architecture.dsl), [section 6.10.1](06_runtime_view.md#6101-sequence-newcomer-installs-a-verified-factory-release)

### QS-12: First-session insight budget

| Field             | Description                                                                                                                          |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Quality attribute | Usability                                                                                                                            |
| Stimulus          | A newcomer completes installation and starts a first session.                                                                        |
| Environment       | The Factory is installed and `init-factory` has run. The session agent (Virgil) starts.                                              |
| Response          | The session presents a project insight (language, frameworks, test infrastructure, configuration) within the decision budget.        |
| Response measure  | The newcomer sees a useful project insight within two minutes of session start and three user decisions after installation approval. |

References: [section 6.10.3](06_runtime_view.md#6103-sequence-first-session-delivers-project-insight), [value-first-onboarding-journey.feature Rule 7](../spec/features/value-first-onboarding-journey.feature)

### QS-13: First-task result budget

| Field             | Description                                                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Usability                                                                                                                             |
| Stimulus          | A newcomer completes the first session and approves the first task.                                                                   |
| Environment       | The Factory is installed, the first session has delivered project insight, and the newcomer has approved the first-task preview.      |
| Response          | The first task produces an inspectable result in an isolated sandbox. The newcomer can examine the result and choose its disposition. |
| Response measure  | The newcomer holds an inspectable first-task result within ten minutes and five user decisions after installation approval.           |

References: [section 6.10.4](06_runtime_view.md#6104-sequence-first-task-runs-in-an-isolated-sandbox), [value-first-onboarding-journey.feature Rule 8](../spec/features/value-first-onboarding-journey.feature)

### QS-14: Update moves the project into the new layout

| Field             | Description                                                                                                                                                                                                                                                             |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Compatibility                                                                                                                                                                                                                                                           |
| Stimulus          | A project maintainer approves an update from a factory version before the layout release.                                                                                                                                                                               |
| Environment       | The project has the old layout and the install record `install.json`. Files at old paths may be untracked, ignored, or carry uncommitted changes.                                                                                                                       |
| Response          | The new `init-factory` runs `migrate-spec-layout` as its last step. Tracked files move with `git mv`, the other files with a plain file move. `init-factory` then writes the new `factory_version`.                                                                     |
| Response measure  | No old path of the path table remains, except a file of the removal set that is untracked, ignored, or tracked with uncommitted changes; the script lists each such file. No git state stops the move. Every tracked file that moved shows as a rename in `git status`. |

References: [section 6.10.6](06_runtime_view.md#6106-sequence-update-moves-the-project-into-the-core-artifact-layout), [ADR-0026](../adr/0026-layout-migration-runs-inside-the-factory-update.md), [core-artifact-layout.feature Rule: Project maintainer receives the new layout with the factory update](../spec/features/core-artifact-layout.feature)

### QS-15: Failed migration leaves a retryable project

| Field             | Description                                                                                                                                                                                                        |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Quality attribute | Operability                                                                                                                                                                                                        |
| Stimulus          | `migrate-spec-layout` fails partway through an update.                                                                                                                                                             |
| Environment       | The installed `update-factory` is `v1.1.0-rc` or later, which the layout release requires.                                                                                                                         |
| Response          | The script undoes its own changes. `init-factory` keeps the prior `factory_version`, reports the old layout, names the fix (run the update again), and exits non-zero. `update-factory` restores the factory tree. |
| Response measure  | `git status` shows no change against the state before the run. The factory tree is the old one, and `install.json` holds the prior version. The next update runs the migration again.                              |

References: [section 6.10.7](06_runtime_view.md#6107-sequence-failed-layout-migration-rolls-back-the-update), [ADR-0026](../adr/0026-layout-migration-runs-inside-the-factory-update.md)

### QS-16: Every core artifact has a known producer and review

| Field             | Description                                                                                                                                                                                                                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Maintainability (artifact ownership)                                                                                                                                                                                                                                                         |
| Stimulus          | A factory maintainer changes an agent definition so that a core or seam artifact loses its producer, gains a second producer, loses its `reviewed_by:` list, or names a reviewer that does not read it.                                                                                      |
| Environment       | The factory's own repository, with `packages/factory/rulebooks/core-artifacts.yaml` and a generated `INDEX.yaml`.                                                                                                                                                                            |
| Response          | The ownership contract test or `index-lint --check` fails and names the artifact and the broken declaration.                                                                                                                                                                                 |
| Response measure  | Every entry of the core list has exactly one producing declaration with at least one reviewer, and every named reviewer declares the artifact as a required or context input. A change that breaks this fails before it merges. No person has to read the agent definitions to find the gap. |

References: [8.17](08_crosscutting_concepts.md#817-artifact-ownership-one-producer-one-declared-review), [ADR-0028](../adr/0028-declared-review-and-core-list-check-ownership.md), [core-artifact-ownership.feature](../spec/features/core-artifact-ownership.feature)

### QS-17: The specification lags the code by one wave at most

| Field             | Description                                                                                                                                                                                                                                                                                                                             |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Maintainability (specification currency)                                                                                                                                                                                                                                                                                                |
| Stimulus          | A developer agent finds during a story that the code and a core artifact disagree.                                                                                                                                                                                                                                                      |
| Environment       | Automated mode; several developer agents run the stories of one wave in parallel.                                                                                                                                                                                                                                                       |
| Response          | The developer agent writes an `open` row of its story's spec-feedback report. The implementation agent dispatches the row's owner and then the owner's reviewer. `dispatch close-wave` fails while the row is `open`, or `fixed` on a core or seam artifact. `dispatch prepare-wave` refuses the next wave until the close is recorded. |
| Response measure  | The next wave starts only after every drift row on a core or seam artifact is `confirmed` or `rejected`, and each `rejected` row has a `BUG` finding against the code.                                                                                                                                                                  |

References: [6.12](06_runtime_view.md#612-spec-feedback-and-wave-close), [ADR-0029](../adr/0029-per-story-drift-reports-block-the-wave-close.md)

### QS-18: No ID is handed out twice

| Field             | Description                                                                                                                                    |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Correctness (unique IDs)                                                                                                                       |
| Stimulus          | Two sessions in two clones run `next-id` at the same moment, for the same prefix or for two prefixes.                                          |
| Environment       | Both clones push to the same remote, which holds `refs/ids/counters`. Each session works on its own branch and sees none of the other's files. |
| Response          | The remote accepts one leased push and refuses the other as stale. The refused claim reads the counter again and retries.                      |
| Response measure  | In 20 rounds of two parallel claims on a local bare repository, all 40 IDs differ, no number of a prefix is skipped, and every call exits `0`. |

References: [6.15](06_runtime_view.md#615-id-claim-with-a-stale-lease), [8.18](08_crosscutting_concepts.md#818-id-allocation), [ADR-0031](../adr/0031-ids-come-from-one-git-ref-with-leased-pushes.md)

## 10.2 Quality Attribute Priority

| Priority | Quality attribute                        | Scenarios |
| -------- | ---------------------------------------- | --------- |
| 1        | Flexibility (precondition routing)       | QS-1      |
| 1        | Controllability (human authority)        | QS-2      |
| 1        | Testability (Clean Architecture)         | QS-3      |
| 1        | Resilience (observable resume)           | QS-5      |
| 2        | Simplicity (immutable state)             | QS-4      |
| 2        | Safety (deterministic validation)        | QS-6      |
| 2        | Safety (fail-closed plugin)              | QS-7      |
| 2        | Compatibility (CLI coexistence)          | QS-8      |
| 1        | Safety (read-only preflight)             | QS-9      |
| 1        | Controllability (consent gate)           | QS-10     |
| 2        | Safety (integrity verification)          | QS-11     |
| 2        | Usability (first-session insight)        | QS-12     |
| 2        | Usability (first-task result)            | QS-13     |
| 2        | Compatibility (layout update)            | QS-14     |
| 2        | Operability (retryable migration)        | QS-15     |
| 2        | Maintainability (artifact ownership)     | QS-16     |
| 2        | Maintainability (specification currency) | QS-17     |
| 1        | Correctness (unique IDs)                 | QS-18     |

## Referenced from

- [09_architecture_decisions.md](09_architecture_decisions.md) — architecture decisions that underpin these scenarios
- [08_crosscutting_concepts.md](08_crosscutting_concepts.md) — principles that underpin QS-3, QS-6, QS-9, and QS-10
