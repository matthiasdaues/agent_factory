---
type: atam-review
title: ATAM Review — Value-First Onboarding Journey
date: 2026-09-23
status: defects
reviewer: architecture-review-agent
findings_filed: 0
scope: Value-first onboarding additions and their integration with the existing Agent Factory architecture
---

# ATAM Review — Value-First Onboarding Journey

## Disposition

The architecture needs revision before planning consumes the value-first
onboarding design. Three Major defects affect update safety, canonical runtime
coverage, and consent enforcement. One Minor defect weakens the measurable
onboarding budgets.

The component split between `install-agent-factory` and `init-factory` is a
sound starting point. The current documents do not yet carry that split through
the complete installation, update, first-session, and first-task journey.

Per stakeholder direction, this report contains every finding. No separate
`docs/findings/ATAM-*` files were created or changed.

## Reviewed Architecture

The review used these governing artifacts:

- [Value-first onboarding feature](../spec/value-first-onboarding-journey.feature)
- [Scope map](../spec/scope-map.md)
- [Architecture model](../arc42/architecture.dsl)
- [Building block view](../arc42/05_building_block_view.md)
- [Runtime view](../arc42/06_runtime_view.md)
- [Deployment view](../arc42/07_deployment_view.md)
- [Cross-cutting concepts](../arc42/08_crosscutting_concepts.md)
- [Architecture decisions](../arc42/09_architecture_decisions.md)
- [Quality requirements](../arc42/10_quality_requirements.md)
- [Glossary](../arc42/12_glossary.md)
- [ADR-0022](../adr/0022-layered-installation-bootstrap-wraps-init-factory.md)
- All other records under [the ADR directory](../adr/)
- [Project context](../CONTEXT.md)
- [Product requirements](../spec/prd.md)
- [Agent context](../agent-context.md)
- [QA strategy](../spec/value-first-onboarding-journey-qa-strategy.md)
- [Entity model](../spec/supplementary_specs/entity-model.md#value-first-onboarding-entities)
- [Interface contracts](../spec/supplementary_specs/interface-contracts.md#value-first-onboarding-contracts)
- [State machines](../spec/supplementary_specs/state-machines.md#value-first-installation-lifecycle)
- [Validation rules](../spec/supplementary_specs/validation-rules.md#value-first-onboarding-validation-rules)
- [Prior ATAM review](atam-review-2026-07-12.md)

The ATAM skill expects `docs/arc42/CONTEXT.md` as the architecture vocabulary
source. That file does not exist. This review used [the project context](../CONTEXT.md),
[the architecture glossary](../arc42/12_glossary.md), and
[the context map](../arc42/CONTEXT-MAP.md) instead.

## Deterministic Findings

The required command was:

```text
.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42
```

Result: exit code 0, with 0 errors, 1 warning, and 0 informational findings.

| Linter finding                                             | Result    | Assessment                                                                                                                                                                                                |
| ---------------------------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ARCH-PARSE could not extract ports from DSL or chapter 5` | Dismissed | [The building block view](../arc42/05_building_block_view.md#55-interfaces-summary) contains the script entry points and exit codes. The parser warning does not identify a missing onboarding interface. |

## Prior Finding Verification

The prior review filed two Major findings. Both remain resolved, but later
architecture replaced their original mitigations.

| Prior finding                                                             | Status                              | Individual verification                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ATAM-0001](../findings/ATAM-0001-agent-test-iteration-friction.md)       | Resolved through superseding design | Factory deleted its `run-tests` implementation. [BR-024](../spec/supplementary_specs/validation-rules.md#project-owned-test-gates-testingyaml-br-023-br-024-br-025-br-026-br-027-br-028-br-029) now permits exact project-declared test commands, including `test_staged_command`. The commit-per-test-cycle coupling no longer exists in the current architecture. |
| [ATAM-0002](../findings/ATAM-0002-monorepo-multi-framework-blind-spot.md) | Resolved through ownership transfer | [BR-023](../spec/supplementary_specs/validation-rules.md#project-owned-test-gates-testingyaml-br-023-br-024-br-025-br-026-br-027-br-028-br-029) assigns test topology and framework orchestration to the project. Factory no longer performs first-match framework detection, so the original silent partial-coverage path no longer exists.                        |

The prior finding files still describe their historical mitigations. They are
durable records, so this review does not rewrite them.

## Findings

| Finding                                                                                                                                                                                          | Artifact                                                                                                                                                                                                                          | Category | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------- |
| The update architecture contradicts the specified approval, staging, rollback, and source-boundary contracts. Revise ADR-0022 and ADR-0010 together, then model the complete update transaction. | [ADR-0022](../adr/0022-layered-installation-bootstrap-wraps-init-factory.md#consequences), [ADR-0010](../adr/0010-refresh-installed-factory-by-remove-and-reinstall.md#decision), [architecture model](../arc42/architecture.dsl) | Defect   | Major    |
| The canonical model omits first-session and first-task runtime behavior. Add explicit component ownership and DSL-derived dynamic views for both parts of the journey.                           | [Architecture model](../arc42/architecture.dsl), [runtime view](../arc42/06_runtime_view.md#610-value-first-onboarding)                                                                                                           | Defect   | Major    |
| Consent enforcement omits or precedes several onboarding mutations. Put remote download behind consent and extend the concept to every first-use mutation.                                       | [Runtime view](../arc42/06_runtime_view.md#6101-sequence-newcomer-installs-a-verified-factory-release), [cross-cutting concept](../arc42/08_crosscutting_concepts.md#815-consent-gated-mutation-value-first-onboarding)           | Defect   | Major    |
| QS-12 weakens the insight decision budget and omits the first-task result budget. Correct QS-12 and add a separate first-result scenario.                                                        | [QS-12](../arc42/10_quality_requirements.md#qs-12-first-session-insight-budget)                                                                                                                                                   | Defect   | Minor    |

### Major — Update Architecture Contradicts the Update Contract

**What is wrong:** [ADR-0022](../adr/0022-layered-installation-bootstrap-wraps-init-factory.md#consequences)
states that `update-factory` bypasses bootstrap preflight and consent because
the host was validated during first installation. It also says the update path
remains unchanged. That assumption is time-sensitive: tools, network, local
files, and the selected release source can change after installation.

The decision conflicts with the accepted behavior in
[the update Rule](../spec/value-first-onboarding-journey.feature) and
[the update interface contract](../spec/supplementary_specs/interface-contracts.md#update-factory).
Those artifacts require:

- approval before a normal update downloads or changes state;
- complete verified staging before application;
- rollback of the Factory tree and instruction headers;
- refusal when Factory-owned files contain unhandled modifications;
- separate consent when the source kind or remote URL changes; and
- a receipt that records the resolved input and changed paths.

The canonical model gives `update-factory` relationships only to the install
manifest and Distribution Remote. It does not show staging, application,
rollback, header management, consent, or receipts. The
[building block view](../arc42/05_building_block_view.md#58-level-2-component-view----distribution)
also describes `update-factory` as reporting components without changing them,
although the command replaces Factory core.

**Why it matters:** The architecture cannot support the update acceptance
tests without contradicting its own decision record. An implementation that
follows ADR-0022 can perform an update without the approval required by the
feature.

**What to do:** Amend or supersede
[ADR-0010](../adr/0010-refresh-installed-factory-by-remove-and-reinstall.md)
and [ADR-0022](../adr/0022-layered-installation-bootstrap-wraps-init-factory.md)
as one coherent decision. Preserve the layered first-install entry point, but
define a separate update transaction that owns check mode, approval, verified
staging, atomic application, rollback, local-change policy, source-boundary
consent, and the receipt. Add these responsibilities and relationships to the
DSL and arc42 chapters.

### Major — Canonical Model Omits the Latter Half of Onboarding

**What is wrong:** The [architecture model](../arc42/architecture.dsl)
contains dynamic views named `OnboardingInstallation` and `ReleaseBuild`. It
does not contain a dynamic view for first-session insight or the isolated first
task.

[The runtime view](../arc42/06_runtime_view.md#610-value-first-onboarding)
states that three sequences cover the key interactions. The first two cite DSL
dynamic views. The third, first-session insight, exists only as handwritten
Mermaid. The chapter contains no first-task sequence. The model also assigns no
component ownership for:

- the read-only project insight;
- deferred configuration routing;
- first-task preview and approval;
- detached-worktree or plain-sandbox creation;
- task execution and checking;
- discard and verified cleanup;
- selected reference-artifact retention; or
- production-workstream handoff.

The supplementary
[first-task state machine](../spec/supplementary_specs/state-machines.md#first-task-sandbox-lifecycle)
defines these transitions, but the canonical architecture neither locates nor
connects their owners.

**Why it matters:** The feature promises value through one inspectable result,
not installation alone. Missing canonical sequences allow planning to assign
the behavior to incompatible components or bypass the existing worktree and
workstream boundaries.

**What to do:** Add the session agent and first-task sandbox owner to the
canonical model. Add DSL dynamic views for first-session insight and the full
first-task lifecycle. Derive chapter 6 sequences from those views. Show how
Virgil, `capture-context`, `hook-demo`, `poc-spike`, Git, the sandbox path,
`docs/spikes/`, and workstream creation interact.

### Major — Consent-Gated Mutation Is Incomplete

**What is wrong:** In
[the installation runtime](../arc42/06_runtime_view.md#6101-sequence-newcomer-installs-a-verified-factory-release),
the bootstrap downloads and verifies release assets before it shows the
installation preview and receives consent. A normal archive download writes
temporary host state. The ordering conflicts with the feature-level rule that
every change requires explicit consent and with
[the consent concept](../arc42/08_crosscutting_concepts.md#815-consent-gated-mutation-value-first-onboarding).

The cross-cutting concept says it applies to every mutating operation during
installation and first use. Its Scope subsection lists the installer,
trust-boundary updates, and `hook-demo`. It omits:

- first-task worktree or sandbox creation;
- copying retained artifacts into `docs/spikes/`; and
- creating or selecting a production workstream.

The feature requires separate approval for each of these effects.

**Why it matters:** The architecture's strongest onboarding invariant does not
cover all modeled mutations. Different implementers can interpret download,
sandbox creation, retention, and handoff differently.

**What to do:** Place archive download after the installation approval. If a
pre-approval download is required, define a separate preview-staging consent,
bounded path, cleanup rule, and receipt. Extend the cross-cutting concept with
an operation-to-consent table that covers prerequisite fixes, installation,
normal update, source change, gate demonstration, sandbox creation, artifact
retention, and production handoff.

### Minor — QS-12 Weakens and Conflates the Budgets

**What is wrong:** [QS-12](../arc42/10_quality_requirements.md#qs-12-first-session-insight-budget)
allows five consent decisions after installation approval before project
insight appears. The
[first-session contract](../spec/supplementary_specs/interface-contracts.md#first-session-insight)
allows three decisions. The feature also defines a separate result budget: an
inspectable first-task result within ten minutes and five decisions after
installation approval. QS-12 does not measure that result.

**Why it matters:** An implementation can satisfy QS-12 while failing both the
three-decision insight contract and the central first-task success measure.

**What to do:** Limit the insight scenario to two minutes and three decisions.
Add a separate quality scenario for an inspectable first-task result within ten
minutes and five decisions after installation approval.

## Quality Scenario Evaluation

### QS-1 — Agent Selection by Precondition Evidence

- **Architectural approach:** The pure Eligibility Engine evaluates declared
  inputs and returns evidence-based readiness verdicts.
- **Sensitivity point:** Correctness depends on agent declarations and
  filesystem evidence remaining aligned.
- **Tradeoff point:** Dynamic eligibility avoids a fixed phase chain but moves
  completeness into declarative metadata.
- **Classification:** Non-risk for this change. The onboarding additions do
  not introduce an inward dependency or a second selection engine.

### QS-2 — Human Authority over Agent Selection

- **Architectural approach:** `intent select` recommends agents, while direct
  human dispatch remains available.
- **Sensitivity point:** Interfaces must display blocked evidence without
  converting the recommendation into an enforcement gate.
- **Tradeoff point:** Human control permits informed overrides at the cost of
  allowing unsafe manual choices.
- **Classification:** Non-risk. The onboarding journey adds consent gates for
  mutation, not a hard gate on agent selection.

### QS-3 — Clean Architecture Dependency Direction

- **Architectural approach:** Pure evaluation logic receives data through
  adapters. Distribution handles host and filesystem concerns.
- **Sensitivity point:** ADR-0022's claim that `init-factory` is a use-case
  layer boundary is not backed by a modeled port between bootstrap and setup.
- **Tradeoff point:** A wrapper adds one entry point but keeps host diagnosis
  separate from project setup.
- **Classification:** Non-risk for the chosen wrapper split. The update
  transaction needs clearer ownership before implementation.

### QS-4 — Workstream Identity Immutability

- **Architectural approach:** Workstream identity records remain immutable;
  session bindings carry session association.
- **Sensitivity point:** First-task production handoff must use the existing
  creation or selection path instead of promoting sandbox state.
- **Tradeoff point:** Explicit handoff adds one decision but keeps disposable
  work separate from production identity.
- **Classification:** Non-risk if the missing first-task dynamic view reuses
  the existing workstream boundary.

### QS-5 — Observable-State Resume

- **Architectural approach:** A new session derives readiness from files on
  disk instead of process memory.
- **Sensitivity point:** The onboarding receipt must name a command that leads
  back to observable installed state.
- **Tradeoff point:** File-derived resume avoids a coordinator but requires
  complete receipts and manifests.
- **Classification:** Non-risk for installation. First-task interruption and
  cleanup remain under-modeled.

### QS-6 — Deterministic Validation

- **Architectural approach:** Dispatcher-owned gates validate committed work
  independently of the authoring agent.
- **Sensitivity point:** The gate demonstration must call a real configured
  gate without changing project fixtures.
- **Tradeoff point:** Independent validation improves trust but adds dispatch
  and configuration overhead.
- **Classification:** Non-risk. `hook-demo` reuses the gate concept without
  moving validation into the onboarding agent.

### QS-7 — Plugin Fails Closed on Control Failure

- **Architectural approach:** The OpenCode plugin denies protected operations
  when initialization, manifest, permission, or worktree controls fail.
- **Sensitivity point:** Onboarding-generated OpenCode files must keep the
  plugin health and recovery contracts intact.
- **Tradeoff point:** Fail-closed operation can stop onboarding for a plugin
  defect, but preserves the enforcement boundary.
- **Classification:** Non-risk. The Distribution container depends on the
  catalog but does not bypass plugin enforcement.

### QS-8 — CLI Integration Preserves Existing CLI Files

- **Architectural approach:** `init-factory` generates CLI-specific files and
  records Factory ownership in the install manifest.
- **Sensitivity point:** Recursive instruction-header management touches
  shared human-authored files outside CLI-specific directories.
- **Tradeoff point:** Shared headers improve discoverability but expand the
  reversible-edit surface.
- **Classification:** Non-risk with the specified exclusions, marker blocks,
  manifest entries, and newline restoration. Integration tests own this risk.

### QS-9 — Read-Only Preflight Before Installation

- **Architectural approach:** The bootstrap returns one immutable readiness
  result before installation changes begin.
- **Sensitivity point:** Host checks must not trigger package-manager caches,
  downloads, fixture creation, or target writes.
- **Tradeoff point:** Read-only diagnosis can identify a remedy but cannot
  establish readiness until a separately approved fix runs.
- **Classification:** Non-risk for the stated preflight boundary. The runtime
  must keep asset download outside preflight.

### QS-10 — Consent-Gated Installation

- **Architectural approach:** A preview precedes installation, and blank input
  means refusal.
- **Sensitivity point:** The exact boundary of “installation” determines
  whether remote download mutates the host before consent.
- **Tradeoff point:** Downloading early can improve the preview's certainty,
  but violates the stronger no-unapproved-change rule unless staged in memory.
- **Classification:** Risk. The documented runtime orders download before the
  installation consent. See the Major consent finding.

### QS-11 — Installation Integrity Verification

- **Architectural approach:** The bootstrap compares the downloaded archive's
  SHA-256 digest with `SHA256SUMS` before extraction.
- **Sensitivity point:** The archive and checksum manifest come from the same
  Distribution Remote and share its trust boundary.
- **Tradeoff point:** A checksum detects corruption and mismatched assets
  without adding signing infrastructure. It does not authenticate the
  publisher independently of HTTPS and remote control.
- **Classification:** Non-risk against the specified integrity contract. The
  publisher-authenticity limitation remains an open security risk.

### QS-12 — First-Result Decision Budget

- **Architectural approach:** Virgil performs a read-only project scan and
  delays advanced configuration until a selected action needs it.
- **Sensitivity point:** Every prompt before insight or first result consumes
  the fixed decision budget.
- **Tradeoff point:** More confirmations increase control but delay visible
  value. Deferred configuration protects the value-first objective.
- **Classification:** Risk. The quality scenario weakens the insight budget,
  omits the task-result budget, and lacks a canonical first-task runtime view.

## Risk Summary

| Risk                                                                                               | Severity | Proposed mitigation                                                                             |
| -------------------------------------------------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------- |
| Update implementation follows ADR-0022 and bypasses required approval or rollback behavior         | Major    | Reconcile ADR-0010 and ADR-0022 with the feature, then model the update transaction in the DSL. |
| Planning assigns first-session and first-task behavior without canonical component ownership       | Major    | Add component ownership and DSL dynamic views before planning.                                  |
| Download or first-use mutations occur without the consent required by the feature                  | Major    | Define consent before each mutating operation and extend the cross-cutting operation table.     |
| Quality evaluation accepts five decisions before insight and never tests time-to-first-task result | Minor    | Split the insight and first-result budgets into two exact scenarios.                            |

## Tradeoff Summary

| Tradeoff                                            | Architectural direction                            | Consequence                                                                         |
| --------------------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Wrapper separation versus one installer             | Keep `install-agent-factory` around `init-factory` | Clear first-install boundary, but the delegated mutation contract must be explicit. |
| Early download certainty versus consent             | Prefer consent before filesystem staging           | Preview may rely on manifest metadata until approval.                               |
| More consent prompts versus time to value           | Ask only at real mutation boundaries               | Consent remains meaningful without spending the decision budget on explanations.    |
| Canonical model detail versus YAGNI                 | Model the four required onboarding sequences only  | Planning receives clear ownership without adding a general workflow engine.         |
| Checksum simplicity versus publisher authentication | Keep SHA-256 for the specified release             | Corruption is detected; remote compromise remains outside the current contract.     |

## YAGNI Review

The Distribution container is justified by the accepted feature. Its six
components correspond to explicit installation, update, removal, release, and
demonstration contracts. The bootstrap wrapper does not introduce an
unnecessary framework.

The missing first-session and first-task views should use existing components
and state models. The architecture does not need a new onboarding workflow
engine, persistent coordinator, or generic transaction framework.

## Open Risks

- `SHA256SUMS` and the archive share one HTTPS trust boundary. The design
  detects corruption and asset mismatch, but not a compromised publisher.
- [ADR-0022](../adr/0022-layered-installation-bootstrap-wraps-init-factory.md)
  remains proposed although the accepted feature and current architecture
  depend on it.
- Initial-install failure recovery is less explicit than update rollback. The
  installation state machine permits `STOPPED_VALID`, but the architecture
  does not define which partial effects may remain.
- The QA strategy marks the acceptance and end-to-end journey harnesses as
  blocked. Architecture risks around prompt order and decision budgets will
  remain weakly verified until those owners exist.

## Validation and Changed Artifacts

- `arch-lint`: passed with exit code 0.
- Deterministic result: 0 errors, 1 dismissed warning, 0 informational
  findings.
- Repeat-pass verification: both prior ATAM findings checked individually.
- Fresh evaluation: QS-1 through QS-12 evaluated.
- Changed artifact:
  [this dated workstream review](atam-review-2026-09-23-value-first-onboarding-journey.md).
- Separate finding files created or changed: none, per stakeholder direction.
