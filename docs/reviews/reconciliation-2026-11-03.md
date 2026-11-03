---
type: reconcile-spec
title: User-Facing Documentation, Specification, and Code Reconciliation
date: 2026-11-03
status: defects
reviewer: reconciliation-agent
findings_filed: 0
scope: User-facing documentation and specification reconciled against implementation, tests, generated artifacts, and open reconciliation findings
---

# User-Facing Documentation, Specification, and Code Reconciliation

## Finding table

| Finding                                                                                                                                                                                                              | Artifact                                                                                                                                                                                                                                          | Category | Severity |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------- |
| [C-01](#c-01--published-usage-query-model-is-not-implemented-as-specified): decide whether `query-model-v1` remains the public contract, then align both implementations and persistence or narrow the specification | [interface contract](../spec/interface-contracts.md), [Python views](../../packages/usage/src/usage/views/), [SQL bootstrap](../../packages/usage/sql/bootstrap-v1.sql), [persistence](../../packages/usage/src/usage/persist.py)                 | Defect   | Critical |
| [M-01](#m-01--the-public-install-path-is-incomplete): make bootstrap the primary install path and label source installation as a developer path                                                                      | [root README](../../README.md), [bootstrap installer](../../packages/factory/scripts/install-agent-factory), [onboarding feature](../spec/features/value-first-onboarding-journey.feature)                                                        | Defect   | Major    |
| [M-02](#m-02--the-single-interface-bootstrap-journey-regressed): restore automatic single-interface selection and linked instruction installation before advertising that journey                                    | [bootstrap tests](../../tests/factory/test_bootstrap_installer.py), [journey tests](../../tests/factory/test_onboarding_journey.py)                                                                                                               | Defect   | Major    |
| [M-03](#m-03--the-root-removal-example-targets-the-wrong-directory): add `cd` or `--target` to the removal example                                                                                                   | [root README](../../README.md), [remove script](../../packages/factory/scripts/remove-factory)                                                                                                                                                    | Defect   | Major    |
| [M-04](#m-04--the-install-and-removal-footprint-is-understated): define the ownership and removal policy for `docs/testing.yaml`, then correct the footprint claims                                                  | [Factory README](../../packages/factory/README.md), [initializer](../../packages/factory/scripts/init-factory)                                                                                                                                    | Defect   | Major    |
| [M-05](#m-05--the-generated-configuration-inventory-is-inaccurate): document the generated `project.json` shape and the tracked status of project-owned documents accurately                                         | [Factory README](../../packages/factory/README.md), [initializer](../../packages/factory/scripts/init-factory)                                                                                                                                    | Defect   | Major    |
| [M-06](#m-06--usage-analysis-is-opt-in-not-automatic): document `--with-usage` and `--add usage` throughout installation and CLI references                                                                          | [usage README](../../packages/usage/README.md), [initializer](../../packages/factory/scripts/init-factory)                                                                                                                                        | Defect   | Major    |
| [M-07](#m-07--the-installed-usage-analysis-path-has-drifted): replace the obsolete `.agent-factory/usage-analysis/` path outside explicit migration history                                                          | [usage README](../../packages/usage/README.md), [UI guide](../../packages/usage/docs/ui-exploration.md), [specification](../spec/), [architecture DSL](../spec/architecture.dsl)                                                                  | Defect   | Major    |
| [M-08](#m-08--usage-wrapper-commands-point-to-a-nonexistent-path): use `.agent-factory/factory/scripts/` in installed-project examples                                                                               | [usage README](../../packages/usage/README.md), [UI guide](../../packages/usage/docs/ui-exploration.md)                                                                                                                                           | Defect   | Major    |
| [M-09](#m-09----persist-does-not-materialize-every-public-view): either build all six public relations before persistence or document selection-dependent persistence                                                | [usage README](../../packages/usage/README.md), [persistence](../../packages/usage/src/usage/persist.py)                                                                                                                                          | Defect   | Major    |
| [M-10](#m-10--the-direct-explorer-command-does-not-auto-watch): add `--watch` or remove the auto-watch claim                                                                                                         | [usage README](../../packages/usage/README.md), [explorer CLI](../../packages/usage/src/usage/explorer.py)                                                                                                                                        | Defect   | Major    |
| [M-11](#m-11--test-hook-behaviour-is-described-as-factory-owned): replace obsolete pre-commit, pre-push, and phase-transition test claims with the project-owned gate model                                          | [Factory README](../../packages/factory/README.md), [hook configuration](../../packages/factory/config/hooks/), [scope map](../spec/scope-map.md)                                                                                                 | Defect   | Major    |
| [M-12](#m-12--generated-model-configuration-is-not-ready-by-default): state that fitting must replace `CONFIGURE-ME` placeholders before dispatch                                                                    | [guide](../../packages/factory/docs/factory-guide.md), [initializer](../../packages/factory/scripts/init-factory)                                                                                                                                 | Defect   | Major    |
| [M-13](#m-13--freshness-checking-warns-but-does-not-update): describe the warning-only hook, or implement the claimed automatic updater                                                                              | [Factory README](../../packages/factory/README.md), [freshness hook](../../packages/factory/config/hooks/)                                                                                                                                        | Defect   | Major    |
| [M-14](#m-14--dispatcher-routing-configuration-has-two-owners): select one installed routing-configuration path and make documentation, initialization, and dispatch agree                                           | [dispatcher library](../../packages/factory/scripts/dispatch_lib.py), [initializer](../../packages/factory/scripts/init-factory)                                                                                                                  | Defect   | Major    |
| [M-15](#m-15--the-story-schema-is-split-across-three-contracts): choose one story frontmatter schema and align the specification, template, and linter                                                               | [interface contract](../spec/interface-contracts.md), [story template](../../packages/factory/rulebooks/templates/story.md), [backlog linter](../../packages/factory/scripts/backlog-lint)                                                        | Defect   | Major    |
| [M-16](#m-16--some-feature-files-are-not-canonical-gherkin): remove Markdown fences and escaped comments, normalize indentation, and add parser-level validation                                                     | [feature specifications](../spec/features/)                                                                                                                                                                                                       | Defect   | Major    |
| [M-17](#m-17--the-guide-contradicts-itself-about-automation): introduce manual and mechanized modes together and state their different stop conditions                                                               | [guide](../../packages/factory/docs/factory-guide.md)                                                                                                                                                                                             | Defect   | Major    |
| [M-18](#m-18--the-open-reconciliation-register-contains-stale-findings): reverify and resolve obsolete findings while retaining any still-live scope-map discrepancy                                                 | [reconciliation findings](../findings/)                                                                                                                                                                                                           | Defect   | Major    |
| [E-01](#minor-errata): change the update-backup path to `.agent-factory/user-changes/`                                                                                                                               | [Factory README](../../packages/factory/README.md), [updater](../../packages/factory/scripts/update-factory)                                                                                                                                      | Defect   | Minor    |
| [E-02](#minor-errata): change the health-output example from `total_records` to `total_lines`                                                                                                                        | [usage README](../../packages/usage/README.md), [capture health](../../packages/usage/src/usage/views/capture_health.py)                                                                                                                          | Defect   | Minor    |
| [E-03](#minor-errata): reconcile `--time-granularity` with `--granularity` and make the PyArrow dependency wording accurate                                                                                          | [interface contract](../spec/interface-contracts.md), [usage CLI](../../packages/usage/src/usage/cli.py)                                                                                                                                          | Defect   | Minor    |
| [E-04](#minor-errata): reconcile the OpenCode contract with the usage registry, which currently omits it                                                                                                             | [interface contract](../spec/interface-contracts.md), [scope map](../spec/scope-map.md), [registry](../../packages/usage/src/usage/registry.py)                                                                                                   | Defect   | Minor    |
| [E-05](#minor-errata): qualify the no-network UI claim because `INSTALL ui` downloads dependencies                                                                                                                   | [usage README](../../packages/usage/README.md)                                                                                                                                                                                                    | Defect   | Minor    |
| [E-06](#minor-errata): stop advertising relation and Arrow output until the CLI returns those formats                                                                                                                | [usage CLI](../../packages/usage/src/usage/cli.py)                                                                                                                                                                                                | Defect   | Minor    |
| [E-07](#minor-errata): qualify the standard-library-only claim and describe dependency checking as import-rule enforcement, not vulnerability scanning                                                               | [guide](../../packages/factory/docs/factory-guide.md), [CRAP scorer](../../packages/factory/scripts/crap-score), [index linter](../../packages/factory/scripts/index-lint), [dependency checker](../../packages/factory/scripts/dependency-check) | Defect   | Minor    |
| [E-08](#minor-errata): remove the nonexistent top-level `config/` entry and the duplicated skills heading                                                                                                            | [root README](../../README.md), [guide](../../packages/factory/docs/factory-guide.md)                                                                                                                                                             | Defect   | Minor    |
| [E-09](#minor-errata): state that the guard blocks every `git push`, not only force pushes                                                                                                                           | [root README](../../README.md), [guard hook](../../packages/factory/config/hooks/)                                                                                                                                                                | Defect   | Minor    |

## Scope and method

This reconciliation compares user-facing documentation, executable code, tests, and the consolidated specification at Git commit `20375592874a629086521509edef7c9f80e25391` on branch `dev`. The sweep covered the root and package READMEs, the user guide and usage UI guide, specification features and supplementary contracts, architecture references, factory and usage implementation entry points, templates, linters, hooks, and the open reconciliation register.

Tests were read before implementation where a behavioural claim was testable. Commands and generated artifacts were then exercised where the environment permitted. A documentation statement was treated as a contract when a user could reasonably use it to install, remove, configure, operate, or query the product.

Several core-artifact-ownership specification files changed concurrently during the audit. New work concerning that feature was excluded from the discrepancy count. Findings that cite [interface-contracts.md](../spec/interface-contracts.md), [entity-model.md](../spec/entity-model.md), [glossary.md](../spec/glossary.md), [state-machines.md](../spec/state-machines.md), or [validation-rules.md](../spec/validation-rules.md) concern pre-existing sections but must be rechecked after the concurrent work lands.

## Reconciliation result

The repository is not presently safe to describe as reconciled. The audit found one critical contract split, 18 major discrepancies, and nine minor errata. The critical issue is architectural rather than editorial: the published local-usage query model, the Python implementation, the DuckDB bootstrap, and persisted database shape do not describe the same product.

No specification or code was changed during this review. No individual `RECON` finding was filed; the user authorized this consolidated report and remediation strategy only. The proposed sequencing is in the [documentation drift remediation strategy](documentation-drift-remediation-strategy-2026-11-03.md).

## Critical discrepancy

### C-01 — Published usage query model is not implemented as specified

The [local usage-analysis interface contract](../spec/interface-contracts.md) promises fixed `query-model-v1` schemas, strict ancestry validation, and six equivalent public views. The Python view builders, including [session_usage.py](../../packages/usage/src/usage/views/session_usage.py) and [usage_by_dimension.py](../../packages/usage/src/usage/views/usage_by_dimension.py), return reduced dictionaries without all published schema fields. The [DuckDB bootstrap](../../packages/usage/sql/bootstrap-v1.sql) defines a different shape and does not apply equivalent ancestry validation. [persist.py](../../packages/usage/src/usage/persist.py) writes the internal relations assembled by the selected operation rather than materializing all six named public views.

An exercised persisted database contained `latest_run_snapshots`, `preflight_failure`, `preflight_valid`, `session_contributions`, `session_roots`, and `session_usage`; four of the six specified public views were absent. This is not repairable by wording changes alone. Product ownership must first decide whether `query-model-v1` remains the contract. If it does, Python, DuckDB, persistence, and conformance tests must catch up together. If it does not, the public and specification claims must be narrowed and versioned.

## Major discrepancies

### M-01 — The public install path is incomplete

The [root README](../../README.md) leads with a clone-based command containing a placeholder repository URL. It omits the verified bootstrap, preflight, and receipt journey represented by the [bootstrap installer](../../packages/factory/scripts/install-agent-factory) and [onboarding feature](../spec/features/value-first-onboarding-journey.feature). Bootstrap should be the primary user path; a source checkout should be clearly labelled as a contributor or developer path.

### M-02 — The single-interface bootstrap journey regressed

Focused executions of [test_bootstrap_installer.py](../../tests/factory/test_bootstrap_installer.py) and [test_onboarding_journey.py](../../tests/factory/test_onboarding_journey.py) reproduce three failures in the promised single-detected-interface path, including linked instruction installation. Restore automatic selection and linked instruction behaviour, and retain the journey tests as release gates before the public docs advertise it.

### M-03 — The root removal example targets the wrong directory

The [root README](../../README.md) invokes the repository-relative removal script without changing directory or passing a target. The script defaults to the current directory, so copying the example can remove from the wrong target. The example must either `cd` into the installed project or pass an explicit `--target`.

### M-04 — The install and removal footprint is understated

The [Factory README](../../packages/factory/README.md) says installation produces only two tracked changes and removal removes everything added. [init-factory](../../packages/factory/scripts/init-factory) can also create `docs/testing.yaml`; that project-owned file is neither ignored nor represented consistently in removal claims. The contract must decide whether the file is retained project source or installation-owned output, then tests and documentation must state the same lifecycle.

### M-05 — The generated configuration inventory is inaccurate

The [Factory README](../../packages/factory/README.md) says `project.json` contains test commands and safety paths, while [init-factory](../../packages/factory/scripts/init-factory) writes identity fields only. It also describes `docs/testing.yaml` and `docs/agent-context.md` as local or gitignored even though they are project-owned tracked sources. Correct the inventory and distinguish installed runtime state from project knowledge.

### M-06 — Usage analysis is opt-in, not automatic

The [usage README](../../packages/usage/README.md) says the fitting process installs usage analysis automatically. The initializer exposes opt-in `--with-usage` and `--add usage` paths, while user-facing CLI references omit them. Installation, augmentation, update, and removal documentation must describe one consistent opt-in lifecycle.

### M-07 — The installed usage-analysis path has drifted

Implementation installs usage analysis below `.agent-factory/usage/analysis/`, but the [usage README](../../packages/usage/README.md), [UI guide](../../packages/usage/docs/ui-exploration.md), feature text, interface contract, architecture DSL, and an ADR still use `.agent-factory/usage-analysis/`. The old path should remain only in explicit migration history; live commands and contracts must use the installed path.

### M-08 — Usage wrapper commands point to a nonexistent path

Installed-project examples in the [usage README](../../packages/usage/README.md) and [UI guide](../../packages/usage/docs/ui-exploration.md) invoke `factory/scripts/...`. The installed wrappers live below `.agent-factory/factory/scripts/`. All copy-and-paste commands must use the latter.

### M-09 — `--persist` does not materialize every public view

The [usage README](../../packages/usage/README.md) says persistence materializes every public view. [persist.py](../../packages/usage/src/usage/persist.py) persists the relations built for the selected operation. Either persistence must deliberately assemble all six public views, or the database must be documented as selection-dependent and unsuitable as the complete public query model.

### M-10 — The direct explorer command does not auto-watch

The [usage README](../../packages/usage/README.md) says the documented direct explorer command watches automatically, but [explorer.py](../../packages/usage/src/usage/explorer.py) enables watching only with `--watch`. Add the flag to the example or remove the claim.

### M-11 — Test-hook behaviour is described as Factory-owned

The [Factory README](../../packages/factory/README.md) claims that Factory runs changed tests on pre-commit, the full suite on pre-push, and phase tests during transitions. Current hook configuration and the [scope map](../spec/scope-map.md) describe project-owned test gates rather than injected test execution. Replace the obsolete behavioural claims and link to the project test-regime contract.

### M-12 — Generated model configuration is not ready by default

The [guide](../../packages/factory/docs/factory-guide.md) says greenfield model defaults work and implies Claude has no generated entries. [init-factory](../../packages/factory/scripts/init-factory) emits `CONFIGURE-ME` placeholders and dispatch halts when required model configuration is missing. The guide must make the fitting obligation and failure mode explicit.

### M-13 — Freshness checking warns but does not update

The [Factory README](../../packages/factory/README.md) says the freshness hook automatically runs the updater. The installed hook warns once and exits successfully. Document warning-only behaviour or deliberately implement automatic updates; silent mutation should not be implied.

### M-14 — Dispatcher routing configuration has two owners

[dispatch_lib.py](../../packages/factory/scripts/dispatch_lib.py) loads `config/project.json`, while initialization moved install identity to `.agent-factory/config/project.json`. As a result, documented safety paths cannot influence tier selection through the declared installed file. Select a single tracked or installed contract owner and update initialization, migration, dispatch, and docs together.

### M-15 — The story schema is split across three contracts

The [interface contract](../spec/interface-contracts.md) requires `outputs`; the [story template](../../packages/factory/rulebooks/templates/story.md) uses `touches`, `tests`, and `test-design-pass`; and [backlog-lint](../../packages/factory/scripts/backlog-lint) requires `touches` while rejecting `tests` and `test-design-pass`. Choose one schema and prove that a newly generated template passes the same linter that governs real stories.

### M-16 — Some feature files are not canonical Gherkin

At least [agent-context.feature](../spec/features/agent-context.feature), [local-usage-processing-and-analysis.feature](../spec/features/local-usage-processing-and-analysis.feature), and [opencode-cli-integration.feature](../spec/features/opencode-cli-integration.feature) contain Markdown fences or escaped comments. Twenty-seven `Rule` declarations lack the two-space indentation assumed by reconciliation tooling. Normalize the sources and add a deterministic parser or structural gate so rule discovery is not whitespace-dependent.

### M-17 — The guide contradicts itself about automation

Early sections of the [guide](../../packages/factory/docs/factory-guide.md) say Factory is manual-only and stops for every move; later sections describe mechanized and automated dispatch. Introduce the modes together, state which approvals each preserves, and remove universal claims that apply only to manual operation.

### M-18 — The open reconciliation register contains stale findings

The open register includes [RECON-0018](../findings/RECON-0018.md), whose test-hook premise is obsolete; [RECON-0019](../findings/RECON-0019.md), which refers to a removed state machine; [RECON-0023](../findings/RECON-0023.md), whose main implementation gap is largely addressed while one scope-map row remains stale; and [RECON-cycle-retirement](../findings/RECON-cycle-retirement.md), which no longer reproduces. Reverify each against the current baseline, resolve obsolete entries, and retain or split only the surviving discrepancy.

## Minor errata

- **E-01:** The documented update backup directory is `factory-user-changes`; [update-factory](../../packages/factory/scripts/update-factory) uses `.agent-factory/user-changes/`.
- **E-02:** The capture-health example expects `total_records`; [capture_health.py](../../packages/usage/src/usage/views/capture_health.py) returns `total_lines`.
- **E-03:** The interface contract names `--time-granularity`, while implementation and other docs use `--granularity`; the contract also treats PyArrow as mandatory while code treats it as optional.
- **E-04:** The interface contract and scope map include OpenCode, while the usage [registry.py](../../packages/usage/src/usage/registry.py) still lists only `claude-code`, `pi`, `codex`, and `copilot`.
- **E-05:** A blanket claim that both browser paths require no network conflicts with dependency downloads performed by `INSTALL ui`.
- **E-06:** The usage CLI advertises relation and Arrow output, then warns and returns JSON.
- **E-07:** The guide says all scripts are standard-library-only even though the CRAP scorer and index linter use external libraries; it also describes dependency checking as vulnerability scanning even though it enforces import-direction rules.
- **E-08:** The root README names a nonexistent top-level `config/` directory; the guide contains a duplicated “Notable skills by concern” heading.
- **E-09:** The root README says only force-push is blocked, while the installed guard rejects every `git push`.

## Validation evidence

| Check                        | Result                                          | Interpretation                                                                                                                                               |
| ---------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| User-facing local-link sweep | Pass                                            | The inspected local links resolved; semantic and command drift remains.                                                                                      |
| Usage package test suite     | 280 passed, 7 skipped                           | Existing tests do not establish conformance to the published six-view model.                                                                                 |
| `spec-lint`                  | 0 errors, 0 warnings, 58 informational findings | Structural lint passes but does not detect the semantic discrepancies above.                                                                                 |
| `concern-lint`               | Pass                                            | Concern routing is internally valid.                                                                                                                         |
| `index-lint`                 | Current; two prompt-size warnings               | Index freshness is not the source of the drift.                                                                                                              |
| `backlog-lint`               | 12 warnings across 336 stories                  | The story-schema split remains visible at the backlog boundary.                                                                                              |
| Full repository test run     | 2,405 passed, 70 failed, 25 errors, 21 skipped  | Most failures and errors were caused by read-only cache paths in the review environment; the three bootstrap journey failures were reproduced independently. |
| Architecture validation      | Blocked                                         | Docker access was unavailable, so Structurizr validation was not completed.                                                                                  |

The full test-run counts must not be treated as a release verdict because the environment prevented cache writes. The focused bootstrap failures and all source-level contract comparisons are independently actionable.

## Artifact disposition

- Specification files updated: none.
- User-facing documentation updated: none.
- Code defects filed: none.
- Individual reconciliation findings filed: none.
- Follow-up plan: [Documentation Drift Remediation Strategy — 2026-11-03](documentation-drift-remediation-strategy-2026-11-03.md).
