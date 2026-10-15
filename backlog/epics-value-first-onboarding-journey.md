---
scope: global
---

# EPICs — Value-First Onboarding Journey

Proposal trace: [value-first-onboarding-journey.md](../docs/proposals/value-first-onboarding-journey.md)
Specification trace: [value-first-onboarding-journey.feature](../docs/spec/value-first-onboarding-journey.feature)
Architecture trace: [ADR-0023](../docs/adr/0023-update-transaction-with-approval-staging-and-rollback.md), Distribution container (§5.1)
QA strategy trace: [value-first-onboarding-journey-qa-strategy.md](../docs/spec/value-first-onboarding-journey-qa-strategy.md)

Dependency order: 1 → 2 → {3 ‖ 4}; 4 → 5; 4 → 6. EPIC 3 runs in parallel with EPIC 4. EPIC 5 depends on EPIC 4 (the first task follows first-session insight). The moderated protocol story in EPIC 6 additionally depends on EPIC 5.

## EPIC 1: Reproducible Release Publication

### Why this EPIC exists

No installation can happen until every approved distribution remote publishes the three required files. Today no `build-release` script or release workflow exists. Without this EPIC, installation and update flows have no reproducible, verified input.

### Actor Goals

- Release maintainer pushes the same version tag to approved distribution remotes. Each remote publishes `install-agent-factory`, `agent-factory.tar.gz`, and `SHA256SUMS` through its own workflow.
- Release maintainer compares releases for the same tag and finds the same archive SHA-256 digest on every remote.

### Demo

1. Push version tag `1.0.0` to two approved distribution remotes with the same tagged commit and release workflow.
2. Each remote's GitHub Actions workflow checks out the tag and runs `build-release --version 1.0.0` with the pinned build environment.
3. Verify that each remote release contains `install-agent-factory`, `agent-factory.tar.gz`, and `SHA256SUMS`.
4. Verify `agent-factory.tar.gz` against the checksum published by each remote.
5. Compare the archive digest from both releases. The digests match.

### Scope

**In:**

- `build-release` script — reads the tagged source tree, assembles `install-agent-factory`, creates the archive with deterministic settings, and computes `SHA256SUMS`.
- Per-remote release workflow — each approved remote reacts to the same version tag, checks out that tag, runs the pinned build, and attaches the three assets to its own release.
- Independent reproducibility — remotes do not exchange build artifacts or digests. The same tagged source, workflow, and pinned toolchain produce identical archives independently.
- Failure handling — a failed build or publication leaves no partial release asset set on that remote.

**Out:**

- Distribution remote setup, repository mirroring, tag propagation, credentials, and access administration.
- Signing or GPG verification — the feature uses SHA-256 digest comparison only.
- Real-time communication or artifact transfer between distribution remotes.

### Dependencies

None. This is the foundational EPIC.

### Boundaries

- Script: `packages/factory/scripts/build-release` (new)
- Workflow: `.github/workflows/build-release.yml` (new and present on every approved remote)
- Input: the same immutable version tag, tagged source, workflow, and pinned build environment on every remote
- Output: each remote's release containing the same three assets

### Domain Rules

- A release asset set contains exactly one bootstrap, one archive, and one checksum manifest for a version.
- Each remote builds from its local copy of the same immutable tag. Remotes do not depend on a central build artifact.
- Builds from the same tagged source, workflow, and pinned toolchain produce the same archive SHA-256 digest.
- A failed build or publication publishes no partial release set on that remote.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                                                                                                             | Tier     | Size | Basis                                                                                                                                                                                                                                           |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0280 | Each approved remote independently builds and publishes the same three release assets from the same version tag, producing an identical archive digest | standard | L    | Adds `build-release` and a tag-triggered GitHub Actions workflow. The script uses deterministic archive settings. Each remote runs the workflow against its local copy of the same tagged commit. No existing release build or workflow exists. |

### Testability Assessment

All actor goals produce observable workflow results, published release assets, checksum manifests, and archive digests. Tests can inspect local build outputs and assets published by controlled remote fixtures. Cross-remote equality is assertable after independent workflows publish the same tag. The remotes do not communicate during publication.

### Ownership Resolution

| Contract                                        | .feature Rule                                                                                          | Owner   | Rationale                                              |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------- | ------------------------------------------------------ |
| Release build produces the required asset set   | `value-first-onboarding-journey.feature#Release maintainer publishes reproducible installation assets` | ST-0280 | Introduces independent per-remote release publication  |
| Distribution remotes publish identical archives | `value-first-onboarding-journey.feature#Release maintainer publishes reproducible installation assets` | ST-0280 | Introduces deterministic publication from the same tag |

## EPIC 2: Diagnosed Installation

### Why this EPIC exists

Today, `init-factory` runs without diagnosing the host, verifying downloads, or asking for consent. A newcomer cannot tell whether the machine is ready. The script changes files without preview or approval. This EPIC wraps `init-factory` in a bootstrap that diagnoses the host, offers fixes, verifies remote releases, previews changes, requires consent, manages instruction headers, and produces a receipt.

### Actor Goals

- Newcomer runs `install-agent-factory` with one source selector and a target, and receives a preflight result (a read-only diagnosis of host platform, tools, Git state, network, and target) before any changes.
- Newcomer controls each prerequisite fix with separate consent and verification.
- Newcomer approves a previewed installation and receives a receipt (a summary of changed paths, interfaces, version, and one next command).

### Demo

01. Run `install-agent-factory --from-local ./factory-src --target ./my-project`.
02. Preflight reports readiness without changing files.
03. The preview names the source, version, target, interfaces, affected paths, instruction files, and uninstall command. Approve the installation.
04. The receipt lists changed paths, selected interface, installed version, and one next command.
05. Run `install-agent-factory --from-remote https://releases.example.com --target ./project-2 --version 1.0.0`.
06. Preflight offers a fix for a missing prerequisite. Approve the fix. The bootstrap runs and verifies the fix.
07. The preview shows the resolved release URL and verified digest. Approve the installation.
08. The receipt confirms the remote source, digest, and changed paths.
09. Inspect `AGENTS.md` in the target. A single marker-delimited Factory header is present.
10. Run the bootstrap again on the same target. No duplicate header appears.
11. Submit blank input at any consent prompt. The bootstrap stops without changes.

### Scope

**In:**

- `install-agent-factory` bootstrap script — accepts `--from-local <path>` or `--from-remote <URL>` with `--target <path>` and optional `--version <release>`. Validates arguments, resolves sources, and delegates installation to `init-factory`.
- Source and target validation — rejects missing selectors, multiple selectors, `--version` with local source, and unsafe targets (filesystem root, user home, unresolved paths, unsupported content).
- Preflight diagnosis — reads host platform, architecture, shell, tool versions, Git state, network reachability, detected coding interfaces, and target status. Produces one readiness value: `Ready`, `Ready with limitations`, or `Blocked`. Does not install software or edit files.
- Prerequisite fix loop — for supported fixes (managed Python, uv), offers each fix with purpose, command, scope, reversal, and verification. Runs a fix only after affirmative consent. Verifies the result before offering the next fix. Stops on decline, blank input, cancellation, or failed verification.
- Remote release verification — resolves an immutable versioned release URL from the distribution remote. Verifies `agent-factory.tar.gz` against `SHA256SUMS` before extraction.
- Installation preview and consent — displays the source, version, target, selected interfaces, affected paths, instruction files, and uninstall command. Requires affirmative approval. Handles ambiguous interface selection by asking again or stopping, never by selecting all interfaces.
- Installation receipt — lists changed paths, selected interface, installed version, resolved source, uninstall command, and one next command.
- Instruction header management — discovers existing regular `AGENTS.md` and `copilot-instructions.md` files outside documented exclusions (`.git/`, `.agent-factory/`, `.current-work/`, dependency trees, virtual environments, caches, build output). Prepends one marker-delimited Factory header (a delimited block of Factory instructions inserted at the top of the file) with repository-relative links. Records each injection and original newline state in the manifest. Supports update and removal without changing user-owned content.

**Out:**

- Release asset building — EPIC 1 produces the files the bootstrap downloads or locates.
- Distribution remote hosting — external infrastructure outside Factory.
- First-session behavior — EPIC 4 handles project insight and hook configuration.
- Update logic — EPIC 3 implements the seven-step update transaction.
- `init-factory` internal changes — the bootstrap delegates to `init-factory` and does not rewrite the existing script.

### Dependencies

EPIC 1 (the bootstrap downloads or locates the release asset set that EPIC 1 builds).

### Boundaries

- Script: `packages/factory/scripts/install-agent-factory` (new bootstrap)
- Script: `packages/factory/scripts/init-factory` (existing, 4413 lines, wrapped by bootstrap)
- Script: `packages/factory/scripts/remove-factory` (existing, referenced in uninstall command)
- Config: `packages/factory/config/pre-commit-config.yaml` (existing, consumed during hook setup)
- Storage: `.agent-factory/install.json` (install manifest, extended with instruction header records)
- Test: `tests/factory/test_init_factory.py` (existing nearby infrastructure)
- Test: `tests/factory/test_install_agent_factory.py` (new)

### Domain Rules

- Every mutating operation during installation requires separate affirmative consent. Blank input is not consent.
- Preflight reads the host and target without changes. The readiness value is exactly one of `Ready`, `Ready with limitations`, or `Blocked`.
- A prerequisite fix runs only after consent. The related check must pass after the fix. Failure stops the fix sequence.
- Remote archive extraction requires the SHA-256 digest in `SHA256SUMS` to match the downloaded file.
- Each instruction file contains at most one marker-delimited Factory header. Repeated installation adds no duplicate.
- The manifest records enough state to update or remove only the Factory header and restore the original newline state.
- Interface selection never defaults to all interfaces when the choice is ambiguous.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                                                                                                                        | Tier     | Size | Basis                                                                                                                                                                                                                                                                         |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0281 | Complete local installation — newcomer runs `install-agent-factory --from-local`, receives preflight diagnosis, previews changes, approves, and receives a receipt with managed instruction headers                                               | standard | L    | New bootstrap script covering argument validation, preflight diagnosis, preview assembly, consent gate, interface selection, delegation to `init-factory` (4413 lines), receipt generation, instruction header discovery and injection. `test_init_factory.py` exists nearby. |
| ST-0282 | Complete remote installation with verification — newcomer runs `install-agent-factory --from-remote`, the bootstrap verifies the archive digest, previews changes, the newcomer approves, and receives a receipt with managed instruction headers | standard | L    | Extends the local installation journey (ST-0281) with immutable URL resolution, SHA-256 verification against `SHA256SUMS`, and remote-specific preview content. Depends on ST-0281 for shared bootstrap infrastructure.                                                       |
| ST-0283 | Prerequisite fix during installation — when preflight reports a fixable missing prerequisite, the newcomer approves a fix, the fix runs and verifies, and preflight resumes                                                                       | standard | M    | Consent-gated fix loop with verification, decline and cancel handling, and recovery guidance. Extends preflight diagnosis from ST-0281. No existing fix mechanism in `init-factory`.                                                                                          |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests can inspect command output and exit status, the resolved source and target paths, downloaded assets, the target filesystem, the install manifest, instruction headers, and receipts. Supported and unsupported host conditions require controllable command and platform boundaries, but no goal requires subjective judgment.

### Ownership Resolution

| Contract                                                     | .feature Rule                                                                                               | Owner   | Rationale                                             |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- | ------- | ----------------------------------------------------- |
| Bootstrap requires one source and an explicit target         | `value-first-onboarding-journey.feature#Newcomer diagnoses installation readiness without changes`          | ST-0281 | Introduces bootstrap validation                       |
| Local source resolves from the invocation directory          | `value-first-onboarding-journey.feature#Newcomer diagnoses installation readiness without changes`          | ST-0281 | Introduces local source resolution                    |
| Version selection is valid only for remote sources           | `value-first-onboarding-journey.feature#Newcomer diagnoses installation readiness without changes`          | ST-0281 | Introduces source and version validation              |
| Unsafe target is rejected                                    | `value-first-onboarding-journey.feature#Newcomer diagnoses installation readiness without changes`          | ST-0281 | Introduces target safety checks                       |
| Supported host receives one readiness result                 | `value-first-onboarding-journey.feature#Newcomer diagnoses installation readiness without changes`          | ST-0281 | Introduces preflight classification                   |
| Unsupported host stops safely                                | `value-first-onboarding-journey.feature#Newcomer diagnoses installation readiness without changes`          | ST-0281 | Introduces unsupported-host handling                  |
| Missing prerequisite explains its remedy                     | `value-first-onboarding-journey.feature#Newcomer diagnoses installation readiness without changes`          | ST-0281 | Introduces prerequisite diagnosis                     |
| Confirmed fix runs and is verified alone                     | `value-first-onboarding-journey.feature#Newcomer controls each prerequisite fix`                            | ST-0283 | Introduces the consent-gated fix loop                 |
| Declined or blank fix input stops the sequence               | `value-first-onboarding-journey.feature#Newcomer controls each prerequisite fix`                            | ST-0283 | Introduces fix refusal handling                       |
| Failed fix verification stops the sequence                   | `value-first-onboarding-journey.feature#Newcomer controls each prerequisite fix`                            | ST-0283 | Introduces post-fix verification                      |
| Unsupported fix receives guidance only                       | `value-first-onboarding-journey.feature#Newcomer controls each prerequisite fix`                            | ST-0283 | Introduces non-mutating remediation guidance          |
| Remote release resolves to immutable verified assets         | `value-first-onboarding-journey.feature#Newcomer installs a verified Factory release with explicit consent` | ST-0282 | Introduces remote resolution and digest verification  |
| Missing or mismatched digest blocks extraction               | `value-first-onboarding-journey.feature#Newcomer installs a verified Factory release with explicit consent` | ST-0282 | Introduces the remote extraction gate                 |
| Installation preview names every planned effect              | `value-first-onboarding-journey.feature#Newcomer installs a verified Factory release with explicit consent` | ST-0282 | First completes both local and remote preview content |
| Ambiguous interface selection does not select all interfaces | `value-first-onboarding-journey.feature#Newcomer installs a verified Factory release with explicit consent` | ST-0281 | Introduces interface selection                        |
| Declined installation leaves target unchanged                | `value-first-onboarding-journey.feature#Newcomer installs a verified Factory release with explicit consent` | ST-0281 | Introduces installation consent                       |
| Approved installation returns a verifiable receipt           | `value-first-onboarding-journey.feature#Newcomer installs a verified Factory release with explicit consent` | ST-0281 | Introduces installation and receipt generation        |
| Installation injects headers into existing instruction files | `value-first-onboarding-journey.feature#Newcomer installs a verified Factory release with explicit consent` | ST-0281 | Introduces instruction-header management              |
| Instruction discovery preserves excluded and linked content  | `value-first-onboarding-journey.feature#Newcomer installs a verified Factory release with explicit consent` | ST-0281 | Introduces bounded instruction discovery              |
| Header installation and removal are reversible               | `value-first-onboarding-journey.feature#Newcomer installs a verified Factory release with explicit consent` | ST-0281 | Introduces repeatable installation and header state   |

## EPIC 3: Update Transaction

### Why this EPIC exists

The current `update-factory` script uses a remove-and-reinstall approach that leaves the installation in a broken state when any step fails. The script lacks approval, staging, rollback, source-boundary consent, and a receipt. ADR-0023 (Architecture Decision Record for the update transaction with approval, staging, and rollback) defines a seven-step replacement. Without this EPIC, every update carries a risk of partial replacement that the user cannot recover from.

### Actor Goals

- Project maintainer (a person managing an existing Factory installation) runs `update-factory --check` and sees installed and candidate versions, source, digest, local modifications, and header changes without writes.
- Project maintainer approves a normal update, and `update-factory` verifies downloaded assets, stages replacements, applies changes, and produces a receipt.
- Project maintainer sees the previous installation restored after a failed update application.

### Demo

1. Run `update-factory --check` on an installation with a newer version available.
2. The report shows the installed version, candidate version, source, digest, local modifications, and planned header changes. No files change.
3. Run `update-factory`. Approve the update.
4. `update-factory` downloads and verifies the archive, stages the Factory tree and headers, applies the staged changes, and writes a receipt.
5. Inspect the receipt. It records the resolved version, source, remote digest, and changed paths.
6. Modify a Factory-owned file. Run `update-factory`.
7. `update-factory` stops before replacing files and reports the modification.
8. Change the source URL. Run `update-factory --from-remote https://other.example.com`.
9. `update-factory` requires separate confirmation for the source-boundary change.

### Scope

**In:**

- Check mode — `update-factory --check` reads the install manifest, compares installed and candidate versions, reports local modifications and planned header changes, and exits without writes (VFO-021).
- Remote update verification and staging — `update-factory` downloads the candidate archive, verifies the digest against `SHA256SUMS`, and stages the Factory tree, derived interface files, hook configuration, and header changes before applying them (VFO-022).
- Application and rollback — `update-factory` applies staged changes. Application failure restores the previous Factory tree and instruction headers (VFO-023).
- Local modification detection — `update-factory` detects modified Factory-owned files and stops unless the user selects the existing preservation flow (VFO-024).
- Source-boundary consent — a different source selector or remote URL requires an explicit option and separate confirmation (VFO-005, VFO-025).
- Update receipt — records the selected source, resolved version or local revision, remote digest when applicable, and changed paths (VFO-025).

VFO (Value-First Onboarding) references identify validation rules from the supplementary specification.

**Out:**

- `init-factory` changes — EPIC 2 wraps `init-factory`; this EPIC changes `update-factory` only.
- First installation — the update script operates on an existing installation with a manifest.
- Instruction header discovery logic — EPIC 2 introduces header discovery; this EPIC reuses the same module for header updates.

### Dependencies

EPIC 2 (the update script reads the install manifest and instruction header records that EPIC 2's installation writes).

### Boundaries

- Script: `packages/factory/scripts/update-factory` (existing, 477 lines, restructured per ADR-0023)
- Storage: `.agent-factory/install.json` (install manifest, read and updated)
- ADR: `docs/adr/0023-update-transaction-with-approval-staging-and-rollback.md`
- Test: `tests/factory/test_update_factory.py` (existing, extended)

### Domain Rules

- Check mode performs no writes (VFO-021).
- Verification and staging complete before any application change (VFO-022).
- Application failure restores the prior Factory tree and instruction headers (VFO-023).
- Modified Factory-owned files stop the update unless the user selects the preservation flow (VFO-024).
- A source-boundary change requires a separate confirmation distinct from the update approval (VFO-005).
- The receipt records the resolved version, source, digest, and changed paths (VFO-025).

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                                                                                                                       | Tier     | Size | Basis                                                                                                                                                                                                                        |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0284 | Update check mode — project maintainer runs `update-factory --check` and sees installed and candidate versions, source, digest, local modifications, and header changes without writes                                                           | standard | M    | Extends existing `update-factory` (477 lines) with version comparison and header change detection. Existing `test_update_factory.py` provides test infrastructure.                                                           |
| ST-0285 | Safe normal update with rollback — project maintainer approves an update, `update-factory` verifies and stages the replacement, applies changes (restoring the prior installation on failure), detects local modifications, and writes a receipt | standard | L    | Major restructuring of existing `update-factory` per ADR-0023. Staging directory, digest verification, atomic application with backup and restore, modification detection, receipt generation. High reliability requirement. |
| ST-0286 | Update across source boundary — when the project maintainer selects a different source kind or remote URL, `update-factory` requires separate consent before proceeding                                                                          | standard | M    | Source-change detection, separate consent gate, trust-boundary validation. Extends the update journey from ST-0285. Existing `--force` flag provides partial infrastructure.                                                 |

### Testability Assessment

All actor goals produce observable command output, exit status, manifest content, receipt content, and installed filesystem state. Tests can control downloaded assets and application failures, then inspect the Factory tree and instruction headers after success or rollback. No testability red flags remain because every safety claim names a bounded update condition and observable result.

### Ownership Resolution

| Contract                                                 | .feature Rule                                                                                                 | Owner   | Rationale                                         |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------- |
| Update check reports candidate changes without writing   | `value-first-onboarding-journey.feature#Project maintainer updates an installation within its trust boundary` | ST-0284 | Introduces read-only update checking              |
| Remote update verifies and stages before applying        | `value-first-onboarding-journey.feature#Project maintainer updates an installation within its trust boundary` | ST-0285 | Introduces the complete staged update transaction |
| Failed update restores the prior installation            | `value-first-onboarding-journey.feature#Project maintainer updates an installation within its trust boundary` | ST-0285 | Introduces rollback                               |
| Modified Factory files stop update by default            | `value-first-onboarding-journey.feature#Project maintainer updates an installation within its trust boundary` | ST-0285 | Introduces local-modification detection           |
| Source change requires separate consent                  | `value-first-onboarding-journey.feature#Project maintainer updates an installation within its trust boundary` | ST-0286 | Introduces source-boundary consent                |
| Successful update records its resolved input and effects | `value-first-onboarding-journey.feature#Project maintainer updates an installation within its trust boundary` | ST-0285 | Introduces update receipt and manifest output     |

## EPIC 4: Value-First Session

### Why this EPIC exists

After installation, the current session asks for model tiers, hooks, and context configuration before showing any value. Virgil (the session agent that guides newcomers through setup) opens the fitting procedure immediately. This EPIC reorders the first session so the newcomer sees project-specific evidence and a gate demonstration before making configuration decisions. This EPIC also fixes BUG-0029 (consumer hooks include entries matching only gitignored Factory runtime paths).

### Actor Goals

- Newcomer opens the first Factory session and sees the detected stack, test entry point, and one safety signal (or the absence of each) before any configuration decision.
- Newcomer sees a gate demonstration (a real Factory gate running against a disposable fixture, showing one failure-to-pass cycle) before choosing hooks.
- Newcomer receives hook choices grouped by protected outcome, with unavailable hooks described without treatment as errors.

### Demo

1. Open a Factory session on a project with a Python codebase and a `pytest` entry point.
2. The session reports the detected stack (Python), the test entry point (`pytest`), and one safety signal (pre-commit hooks present) without changing files.
3. The session recommends one next action.
4. Accept the gate demonstration. A Factory gate reports a failure on a disposable fixture. Correct the fixture. The gate passes. The fixture is removed.
5. The session presents hooks grouped by protected outcome (e.g., "Formatting: mdformat", "Dangerous git commands: block-dangerous-git").
6. The session asks only about automatic file changes or material execution cost.
7. Unavailable hooks appear with a description, not as errors or choices.
8. No hook triggers match only ignored Factory runtime paths. `index-lint` (a Factory-source-only validator) is absent from the consumer set.
9. `matrix-lint` (the model matrix validator) runs after model configuration and before dispatch.

### Scope

**In:**

- First-session project insight — the session scans the project and reports detected stack, test entry point or its absence, and one observed safety signal or its absence without writes (VFO-026). The insight appears within two minutes with no more than three decisions after installation approval.
- Configuration deferral — advanced configuration (model tiers, hooks, extended context) waits until the newcomer selects an action that depends on each setting.
- Context capture gate — before scanning, onboarding explains the scan, confirmation decisions, `docs/agent-context.md` output, `concern-lint` validation, and how humans and agents use the file. Onboarding defines a concern (a routing topic that directs agents to project-specific knowledge) before using the term without a paraphrase (VFO-028). Deferral or cancellation before scanning produces no scan and no output file (VFO-029).
- Gate demonstration — `hook-demo` (a new script) runs a real Factory gate against a disposable fixture. The demonstration shows one failure-to-pass cycle without changing the target project (VFO-030). Skipping the demonstration does not change recommended hook defaults.
- Consumer hook configuration — hooks are grouped by protected outcome and ask only about automatic file changes or material execution cost. Unavailable hooks are described without treatment as errors or choices. The consumer hook set omits `index-lint` and any hook that matches only ignored Factory runtime paths (VFO-031, BUG-0029). `matrix-lint` runs after model configuration and before dispatch (VFO-032).

**Out:**

- Full Virgil rewrite — this EPIC reorders the first-session flow in the existing agent definition; it does not rewrite Virgil from scratch.
- Model matrix configuration — that configuration step exists today and is deferred by the new flow, not reimplemented.
- Instruction header management — EPIC 2 handles headers during installation.
- First-task sandbox — EPIC 5 handles the isolated first task.

### Dependencies

EPIC 2 (the first session opens after installation completes and reads the install manifest for detected interfaces).

### Boundaries

- Agent: `packages/factory/agents/virgil.md` (existing, modified)
- Skill: `packages/factory/skills/capture-context/SKILL.md` (existing, modified flow)
- Script: `packages/factory/scripts/hook-demo` (new)
- Config: `packages/factory/config/pre-commit-config.yaml` (existing, consumer subset filtered)
- Test: `tests/factory/test_value_first_routing.py` (new)
- Test: `tests/factory/test_hook_demo.py` (new)
- Test: `tests/factory/test_precommit_config_contract.py` (new)

### Domain Rules

- The first session scans the project without writes (VFO-026).
- Context capture starts only after the explanation. Deferral or cancellation before scanning produces no output (VFO-029).
- A concern is a routing topic. Onboarding defines the term before using it without a paraphrase (VFO-028).
- The gate demonstration runs on a Factory-owned disposable fixture and removes the fixture after the demonstration (VFO-030).
- No consumer hook matches only ignored Factory runtime paths (VFO-031).
- `index-lint` is absent from the consumer hook set (VFO-031).
- `matrix-lint` runs after model configuration and before dispatch (VFO-032).

### Size

4 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                       | Tier     | Size | Basis                                                                                                                                                                                       |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0287 | First-session project insight — the session reports stack, test entry point, and safety signal without writes, then recommends one action        | standard | M    | Extends Virgil's session start with project scan logic. Existing `capture-context` skill provides partial infrastructure. Ready-host budget constraint (two minutes, three decisions).      |
| ST-0288 | Context capture gate — onboarding explains the scan and offers deferral before starting `capture-context`                                        | economy  | S    | Extends the existing `capture-context` skill flow with an explanation step and deferral gate. Narrow scope: two interaction states.                                                         |
| ST-0289 | Gate demonstration — `hook-demo` runs a Factory gate against a disposable fixture, shows failure and success, and removes the fixture            | standard | M    | New script. Creates a temporary fixture, runs an existing gate, modifies the fixture, reruns the gate, removes the fixture. Real filesystem and subprocess interaction.                     |
| ST-0290 | Consumer hook configuration — hooks grouped by outcome, source-only triggers removed, BUG-0029 fixed, `matrix-lint` scheduled after model config | standard | M    | Modifies consumer hook subset generation. Existing `merge-precommit-config` (tested) and `pre-commit-config.yaml` (117 lines) provide infrastructure. BUG-0029 fix requires path filtering. |

### Testability Assessment

All actor goals produce observable session output, decision counts, elapsed time, generated hook configuration, and filesystem state. Tests can inspect the session transcript, the target project, the disposable fixture lifecycle, and hook ordering. The time bounds require a defined ready-host fixture, but the feature supplies that boundary and leaves no subjective success criterion.

### Ownership Resolution

| Contract                                                         | .feature Rule                                                                                            | Owner   | Rationale                                    |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------- | -------------------------------------------- |
| First session reports evidence without changing the project      | `value-first-onboarding-journey.feature#Newcomer receives project insight before advanced configuration` | ST-0287 | Introduces read-only project insight         |
| Ready-host insight meets the decision and time bounds            | `value-first-onboarding-journey.feature#Newcomer receives project insight before advanced configuration` | ST-0287 | Introduces bounded first-session routing     |
| Advanced configuration waits for a dependent action              | `value-first-onboarding-journey.feature#Newcomer receives project insight before advanced configuration` | ST-0287 | Introduces value-first configuration order   |
| Context capture is explained before scanning                     | `value-first-onboarding-journey.feature#Newcomer receives project insight before advanced configuration` | ST-0288 | Introduces the context-capture explanation   |
| Context capture can be deferred before scanning                  | `value-first-onboarding-journey.feature#Newcomer receives project insight before advanced configuration` | ST-0288 | Introduces the context-capture consent gate  |
| Gate demonstration shows one failure-to-pass cycle               | `value-first-onboarding-journey.feature#Newcomer sees gate value before choosing hooks`                  | ST-0289 | Introduces the disposable gate demonstration |
| Skipping the gate demonstration preserves defaults               | `value-first-onboarding-journey.feature#Newcomer sees gate value before choosing hooks`                  | ST-0289 | Introduces the demonstration skip path       |
| Hook choices describe protected outcomes and material trade-offs | `value-first-onboarding-journey.feature#Newcomer sees gate value before choosing hooks`                  | ST-0290 | Introduces outcome-based hook selection      |
| Consumer hook set omits source-only triggers                     | `value-first-onboarding-journey.feature#Newcomer sees gate value before choosing hooks`                  | ST-0290 | Introduces the filtered consumer hook set    |

## EPIC 5: Isolated First Task

### Why this EPIC exists

After installation and first-session insight, the newcomer has seen what Factory detects but has not produced anything. Without a guided first task, the newcomer must figure out how to start real work alone. This EPIC provides a sandbox (a temporary working area isolated from the project) where the newcomer runs one proof-of-concept spike and chooses what happens to the result.

### Actor Goals

- Newcomer approves a first-task preview and receives a sandbox where the poc-spike playbook (a proof-of-concept workflow that produces a quick result from a one-sentence idea) runs.
- Newcomer sees an inspectable result and chooses to discard, retain selected artifacts, or begin real work.

### Demo

1. The session recommends a first task. The preview shows the goal, expected duration, expected artifacts, required decisions, and cleanup method.
2. Approve the task. On a repository with commits, a detached worktree (a separate Git working directory checked out from HEAD without creating a branch) appears at `.current-work/onboarding-spike/<session-id>/`.
3. The poc-spike playbook runs inside the sandbox. The result is an inspectable file or runnable output.
4. The session shows which checks ran and how to remove the result.
5. Choose discard. The sandbox is removed and verified absent.
6. (Alternative to step 5) Choose retain. Select specific artifacts. The selected artifacts are copied to `docs/spikes/<name>/`. The sandbox is not promoted.
7. (Alternative to step 5) Choose production handoff. A normal workstream is created. The sandbox does not become production work.

### Scope

**In:**

- First-task preview and approval — onboarding shows the goal, expected duration, expected artifacts, required decisions, and cleanup method. Blank or declined approval creates no sandbox (VFO-033).
- Sandbox creation — a repository with HEAD uses a detached worktree from that commit at `.current-work/onboarding-spike/<session-id>/`. A repository without HEAD uses a plain sandbox at the same path. The sandbox creates no branch or commit. Active-working-tree changes are absent from the sandbox (VFO-034, VFO-035).
- Task execution — the poc-spike playbook runs inside the sandbox. The session shows the inspectable result, check results, and removal instructions.
- Ready-host budget — an inspectable result appears within ten minutes of session start with no more than five decisions after installation approval.
- Outcome selection:
  - Discard removes the sandbox and verifies its absence (VFO-037).
  - Retain copies only separately confirmed artifacts to a named `docs/spikes/` path. Retention does not promote the sandbox (VFO-036).
  - Production handoff creates or selects a normal workstream. The sandbox does not become production work (VFO-037).

**Out:**

- poc-spike playbook implementation — the playbook exists today (`poc-spike.md`). This EPIC creates the sandbox and outcome handling around the playbook.
- Workstream creation logic — production handoff delegates to the existing workstream mechanism.
- Gate demonstration — EPIC 4 handles the gate demonstration.

### Dependencies

EPICs 2 and 4 (the first task runs after installation and first-session insight; it uses the `.current-work/` structure that `init-factory` creates and follows the session reordering from EPIC 4).

### Boundaries

- Module: sandbox management (new, under `packages/factory/`)
- Playbook: `.agent-factory/factory/playbooks/poc-spike.md` (existing, invoked inside sandbox)
- Storage: `.current-work/onboarding-spike/<session-id>/` (sandbox path)
- Storage: `docs/spikes/` (retained artifact destination)
- Test: `tests/factory/test_onboarding_sandbox.py` (new)

### Domain Rules

- First-task approval is affirmative. Blank or declined input creates no sandbox (VFO-033).
- A repository with HEAD uses a detached worktree. A repository without HEAD uses a plain sandbox (VFO-034).
- The sandbox path is `.current-work/onboarding-spike/<session-id>/`. The first task creates no branch or commit (VFO-035).
- Retention copies only separately confirmed artifacts. Unconfirmed artifacts are not retained (VFO-036).
- Discard verifies sandbox removal. Production handoff requires separate approval and never promotes the sandbox (VFO-037).

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                                                                                                                                     | Tier     | Size | Basis                                                                                                                                                                                                                                                                        |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0291 | Complete first task in a repository with commits — newcomer approves a preview, receives a detached worktree sandbox from HEAD, runs the poc-spike playbook, sees an inspectable result, and chooses to discard, retain selected artifacts, or begin real work | standard | L    | End-to-end first-task journey: preview and consent, Git worktree creation from HEAD, poc-spike invocation in sandbox, result display, three outcome paths (discard with verification, selective retention to `docs/spikes/`, production handoff). No existing sandbox logic. |
| ST-0292 | Complete first task in a repository without commits — newcomer approves a preview, receives a plain sandbox, runs the poc-spike playbook, sees an inspectable result, and chooses to discard, retain selected artifacts, or begin real work                    | standard | M    | Variant of ST-0291 for a repository without HEAD. Uses a plain directory instead of a detached worktree. Shares outcome selection logic with ST-0291. Simpler sandbox creation path.                                                                                         |

### Testability Assessment

All actor goals produce observable session output, Git state, sandbox paths, retained files, and workstream selection. Tests can inspect the detached worktree or plain sandbox, the active working tree, `docs/spikes/`, and sandbox removal. Elapsed time and decision counts are measurable on the defined ready-host path, so no testability red flags remain.

### Ownership Resolution

| Contract                                                   | .feature Rule                                                                                         | Owner   | Rationale                                     |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------- | --------------------------------------------- |
| First task preview requires approval                       | `value-first-onboarding-journey.feature#Newcomer completes one isolated task and chooses its outcome` | ST-0291 | Introduces preview and sandbox consent        |
| Repository with a commit uses a detached worktree          | `value-first-onboarding-journey.feature#Newcomer completes one isolated task and chooses its outcome` | ST-0291 | Introduces the committed-repository path      |
| Repository without a commit uses a plain sandbox           | `value-first-onboarding-journey.feature#Newcomer completes one isolated task and chooses its outcome` | ST-0292 | Introduces the repository-without-HEAD path   |
| First task produces an inspectable checked result          | `value-first-onboarding-journey.feature#Newcomer completes one isolated task and chooses its outcome` | ST-0291 | First introduces task execution and results   |
| Ready-host first result meets the decision and time bounds | `value-first-onboarding-journey.feature#Newcomer completes one isolated task and chooses its outcome` | ST-0291 | First introduces the bounded complete journey |
| Newcomer discards the first task                           | `value-first-onboarding-journey.feature#Newcomer completes one isolated task and chooses its outcome` | ST-0291 | First introduces discard and verified cleanup |
| Newcomer retains selected reference artifacts              | `value-first-onboarding-journey.feature#Newcomer completes one isolated task and chooses its outcome` | ST-0291 | First introduces selective retention          |
| Newcomer begins real work explicitly                       | `value-first-onboarding-journey.feature#Newcomer completes one isolated task and chooses its outcome` | ST-0291 | First introduces production handoff           |

## EPIC 6: Journey Measurement

### Why this EPIC exists

EPICs 1 through 5 deliver the onboarding journey, but without measurement there is no evidence that the journey works for real newcomers. This EPIC provides an automated test that checks the safe path and a moderated protocol that records comprehension. Without measurement, defects in consent, routing, or terminology remain invisible until production use.

### Actor Goals

- Quality researcher (a person testing the onboarding experience with real participants) runs an automated journey test that checks diagnosis, cancellation, consent, installation, receipt, and first-session routing.
- Quality researcher conducts a moderated usability session and records elapsed time, decisions, unclear terms, abandonment points, recovery attempts, and the participant's stated next action.

### Demo

1. Run the automated journey test.
2. Verify the test checks preflight diagnosis, cancellation handling, consent gates, installation, receipt contents, and first-session routing.
3. Conduct a moderated session with a participant who did not build Agent Factory.
4. Complete the usability protocol form. Verify it records elapsed time, decision count, unclear terms, abandonment points, recovery attempts, and the participant's stated next action.

### Scope

**In:**

- Automated journey test — a pytest-based end-to-end test that exercises the safe non-interactive path through preflight, cancellation, consent, installation, receipt, and first-session routing (VFO-09-E2-01). Declares the end-to-end layer binding in `docs/testing.yaml`. The automated test does not exercise updating; it covers only installation and first-session routing.
- Moderated usability protocol — a document template at `docs/testing/value-first-onboarding-usability-protocol.md` that guides a quality researcher through a moderated session covering the complete journey including the first task. Records elapsed time, user decisions, unclear terms, abandonment points, recovery attempts, and the participant's stated next action (VFO-09-AC-01).

**Out:**

- Performance benchmarking — the time budgets (two minutes for insight, ten minutes for first result) are acceptance criteria in EPICs 4 and 5, not measured by this EPIC's test.
- Automated usability scoring — the moderated protocol records qualitative data; automated analysis is out of scope.
- Bug fixes — this EPIC measures the journey; defects found are tracked separately.
- Update testing — EPIC 3 owns its own test coverage; the automated journey test does not exercise the update path.

### Dependencies

EPIC 4 (the automated test exercises installation and first-session routing). The moderated protocol story additionally depends on EPIC 5 (the moderated session covers the complete journey including the first task).

### Boundaries

- Test: `tests/factory/test_onboarding_journey.py` (new, end-to-end)
- Config: `docs/testing.yaml` (extended with end-to-end layer binding)
- Document: `docs/testing/value-first-onboarding-usability-protocol.md` (new)

### Domain Rules

- The automated test exercises the safe non-interactive path. The test checks consent, cancellation, installation, and routing.
- The moderated protocol records elapsed time, decisions, unclear terms, abandonment points, recovery attempts, and the participant's stated next action.
- The participant did not build Agent Factory.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                                   | Tier     | Size | Basis                                                                                                                                                                                          |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0293 | Automated journey test — a pytest end-to-end test exercises the safe non-interactive path through installation and first-session routing                     | standard | L    | End-to-end test spanning installation, consent, receipt, and session routing. Requires test fixtures for all journey steps. Declares new `testing.yaml` layer. No existing end-to-end harness. |
| ST-0294 | Moderated usability protocol — a document template guides a quality researcher through a moderated newcomer session covering the complete onboarding journey | economy  | S    | Document template with structured recording fields. No code. Narrow scope. Depends on EPIC 5 for the first-task portion of the journey.                                                        |

### Testability Assessment

Both actor goals have observable outputs. The automated journey exposes its result through its exit status and contract assertions, while the moderated protocol exposes required evidence through completed record fields. Participant statements require human collection, but the contract checks whether the protocol records them rather than judging their meaning.

### Ownership Resolution

| Contract                                               | .feature Rule                                                                                      | Owner   | Rationale                                     |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------- | ------- | --------------------------------------------- |
| Automated journey checks the safe non-interactive path | `value-first-onboarding-journey.feature#Quality researcher measures the complete newcomer journey` | ST-0293 | Introduces the automated journey measurement  |
| Moderated session records newcomer comprehension       | `value-first-onboarding-journey.feature#Quality researcher measures the complete newcomer journey` | ST-0294 | Introduces the moderated measurement protocol |
