---
type: atam-review
title: ATAM Review — Value-First Onboarding Journey
date: 2026-09-23
status: pass
reviewer: architecture-review-agent
findings_filed: 0
scope: Value-first onboarding additions and their integration with the existing Agent Factory architecture
reviewed_head: 9fd607d712821dc4ad4b22e357985f824d4c372f
---

# ATAM Review — Value-First Onboarding Journey

## Disposition

Pass. The final repeat pass found no open architecture defects. The
Distribution components, onboarding dynamic views, consent-gated mutation
concept, and accepted ADR-0023 integrate with the existing architecture.

The review covered the working tree based on commit
`9fd607d712821dc4ad4b22e357985f824d4c372f`. The remediation was uncommitted at
review time.

Per stakeholder direction, this document contains the complete review. No
separate finding files were created or changed.

## Reviewed Architecture

The review examined:

- [Value-first onboarding feature](../spec/value-first-onboarding-journey.feature)
- [Scope map](../spec/scope-map.md)
- [Product requirements](../spec/prd.md)
- [QA strategy](../spec/value-first-onboarding-journey-qa-strategy.md)
- [Supplementary specifications](../spec/supplementary_specs/)
- [Architecture model](../arc42/architecture.dsl)
- All arc42 chapters, including the building-block, runtime, cross-cutting,
  decision, and quality-requirement chapters
- All architecture decision records, with emphasis on
  [ADR-0022](../adr/0022-layered-installation-bootstrap-wraps-init-factory.md)
  and
  [ADR-0023](../adr/0023-update-transaction-with-approval-staging-and-rollback.md)
- [Project context](../CONTEXT.md) and [agent context](../agent-context.md)
- [Prior ATAM review](atam-review-2026-07-12.md)

The ATAM skill names `docs/arc42/CONTEXT.md` as its preferred vocabulary
source. That file does not exist. The review used the project context,
architecture glossary, and architecture context map instead.

## Deterministic Validation

The final commands and results were:

| Check                                                                                                                 | Result                                                |
| --------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `.agent-factory/factory/scripts/mdformat --number docs/arc42/05_building_block_view.md docs/arc42/06_runtime_view.md` | Passed                                                |
| `.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42`                                                      | Exit 0; 0 errors, 1 warning, 0 informational messages |
| `.agent-factory/factory/scripts/structurizr validate docs/arc42/architecture.dsl`                                     | Passed                                                |
| `git diff --check`                                                                                                    | Passed                                                |

The first post-edit arch-lint run reported two informational messages: the DSL
was newer than its diagrams, and export completed. Arch-lint re-exported the
affected views. The final run reported no informational messages. The
subsequent Structurizr validation passed.

| Linter finding                                             | Disposition            | Assessment                                                                                                                                  |
| ---------------------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `ARCH-PARSE could not extract ports from DSL or chapter 5` | Dismissed              | The chapter-5 interface summary documents script entry points and exit codes. The warning does not identify a missing onboarding interface. |
| `ARCH-STALE`                                               | Resolved automatically | Arch-lint re-exported the Structurizr views.                                                                                                |
| `ARCH-EXPORT`                                              | Confirmed              | Diagram export completed successfully.                                                                                                      |

Structurizr also emitted an upstream warning that its cloud theme reaches end
of life on 30 September 2026. The warning did not affect validation or export.

## Prior Finding Verification

### Prior review dated 2026-07-12

| Prior finding                                     | Final status | Verification                                                                                                     |
| ------------------------------------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------- |
| `ATAM-0001` — agent test-iteration friction       | Resolved     | Factory no longer owns the removed `run-tests` mechanism. Project-declared test commands now own test execution. |
| `ATAM-0002` — monorepo multi-framework blind spot | Resolved     | Project-owned test topology replaced Factory framework detection.                                                |

### Value-first onboarding review findings

| Finding                                                                              | Final status | Verification                                                                                                                                                                                                               |
| ------------------------------------------------------------------------------------ | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Update architecture contradicted the update contract                                 | Resolved     | Accepted ADR-0023 defines check mode, approval, verified staging, application, rollback, source-boundary consent, and receipt ownership. Separate `UpdateTransactionCheck` and `UpdateTransaction` views model both paths. |
| Canonical model omitted first-session and first-task behavior                        | Resolved     | The DSL models installation-state reads, project scanning, explicit consent, both sandbox variants, and result presentation. The state machine owns mutually exclusive task dispositions.                                  |
| Consent enforcement omitted or preceded mutations                                    | Resolved     | Installation download follows approval. Context capture and the gate demonstration require explicit affirmative consent. The operation-to-consent mapping covers sandbox creation, retention, and production handoff.      |
| QS-12 weakened and conflated the onboarding budgets                                  | Resolved     | QS-12 measures insight within two minutes and three user decisions. QS-13 separately measures the first result within ten minutes and five user decisions.                                                                 |
| First installation read a manifest before creating it                                | Resolved     | The installation preview derives from preflight results and planned effects. Manifest writes occur only after verified installation begins.                                                                                |
| Update staging and application targeted the Install Manifest                         | Resolved     | Staging, application, and rollback are internal `update-factory` operations. The Install Manifest stores only installation state and the update receipt.                                                                   |
| Update approval and source confirmation were compressed into an outbound interaction | Resolved     | The dynamic view contains separate preview, approval, source-change prompt, and source-change response interactions.                                                                                                       |
| ADR-0023 remained proposed while superseding ADR-0010 and ADR-0022                   | Resolved     | ADR-0023 and the chapter-9 decision index both record `accepted`.                                                                                                                                                          |
| Project scans and sandboxes used incorrect storage containers                        | Resolved     | The Project Filesystem models project reads, consent-gated writes, plain sandboxes, and retained artifacts. Git owns detached-worktree creation and removal.                                                               |
| Mutually exclusive first-task outcomes were serialized                               | Resolved     | The two dynamic views end at the inspectable result. The first-task state machine owns discard, reference retention, and production-handoff branching.                                                                     |
| Project Filesystem responsibility was inconsistent and missing from chapter 5        | Resolved     | The DSL and chapter-5 container table describe project-controlled storage and its contract-bound, consent-gated mutations.                                                                                                 |

## Quality Scenarios

The fresh evaluation covered every current scenario:

01. QS-1 — Agent selection by precondition evidence
02. QS-2 — Human authority over agent selection
03. QS-3 — Clean Architecture dependency direction
04. QS-4 — Workstream identity immutability
05. QS-5 — Observable-state resume
06. QS-6 — Deterministic validation
07. QS-7 — Plugin fails closed on control failure
08. QS-8 — CLI integration preserves existing CLI files
09. QS-9 — Read-only preflight before installation
10. QS-10 — Consent-gated installation
11. QS-11 — Installation integrity verification
12. QS-12 — First-session insight budget
13. QS-13 — First-task result budget

## Fresh Scenario Evaluation

### QS-1 — Agent selection by precondition evidence

- **Approach:** The Eligibility Engine evaluates declared inputs against
  repository evidence.
- **Sensitivity:** Agent declarations and repository evidence must remain
  aligned.
- **Tradeoff:** Declarative routing avoids a fixed phase chain but depends on
  complete metadata.
- **Classification:** Non-risk. Onboarding introduces no second selection
  mechanism.

### QS-2 — Human authority over agent selection

- **Approach:** Eligibility is advisory. Direct human dispatch remains
  available.
- **Sensitivity:** Interfaces must show blocked evidence without enforcing the
  recommendation.
- **Tradeoff:** Human overrides retain control but permit informed risk-taking.
- **Classification:** Non-risk. Mutation consent does not restrict agent
  selection.

### QS-3 — Clean Architecture dependency direction

- **Approach:** Distribution owns host and filesystem adapters. Pure evaluation
  remains inside the Eligibility Engine.
- **Sensitivity:** Host diagnosis must not move into `init-factory` or the
  Eligibility Engine.
- **Tradeoff:** The bootstrap adds an entry point while keeping project setup
  independent of host diagnosis.
- **Classification:** Non-risk. ADR-0023 retains the layered first-install
  design from ADR-0022.

### QS-4 — Workstream identity immutability

- **Approach:** Production handoff uses immutable Workstream State and separate
  Session Bindings.
- **Sensitivity:** The onboarding sandbox must never become production state.
- **Tradeoff:** Explicit handoff adds a decision but keeps experimental state
  separate.
- **Classification:** Non-risk. The state machine retains the existing
  boundary.

### QS-5 — Observable-state resume

- **Approach:** Receipts, manifests, workstream records, and bindings provide
  observable state.
- **Sensitivity:** Receipts must identify the installed state and exact next
  command.
- **Tradeoff:** File-derived recovery avoids process coordination but requires
  complete records.
- **Classification:** Non-risk. Installation and handoff return to persisted
  state.

### QS-6 — Deterministic validation

- **Approach:** Dispatcher-owned gates run after developer commits.
- **Sensitivity:** Gate ownership must remain independent of the developer
  agent.
- **Tradeoff:** Independent validation adds a dispatch cycle but avoids
  self-review.
- **Classification:** Non-risk. The onboarding additions do not bypass these
  gates.

### QS-7 — Plugin fails closed on control failure

- **Approach:** The OpenCode plugin denies operations when permission,
  manifest, or worktree controls fail.
- **Sensitivity:** Usage capture must remain outside fail-closed controls.
- **Tradeoff:** Fail-closed behavior favors safety over availability.
- **Classification:** Non-risk. The onboarding sandbox reuses established Git
  and filesystem boundaries.

### QS-8 — CLI integration preserves existing CLI files

- **Approach:** `init-factory` owns scoped integration changes recorded in the
  Install Manifest.
- **Sensitivity:** Generated paths and marker blocks must remain CLI-specific.
- **Tradeoff:** Shared root orientation reduces duplication but needs precise
  ownership rules.
- **Classification:** Non-risk. The bootstrap delegates project setup to the
  existing scoped mechanism.

### QS-9 — Read-only preflight before installation

- **Approach:** `install-agent-factory` completes preflight before download or
  mutation.
- **Sensitivity:** Tool checks, network checks, and preview construction must
  avoid caches and target writes.
- **Tradeoff:** Separate diagnosis delays remediation but makes the no-write
  boundary testable.
- **Classification:** Non-risk. The runtime and dynamic view place preview and
  approval before download.

### QS-10 — Consent-gated installation

- **Approach:** Preview precedes explicit affirmative approval. Blank or
  declined input stops the sequence.
- **Sensitivity:** Every mutating branch must use the same affirmative-consent
  rule.
- **Tradeoff:** Consent prompts add decisions but retain human control at real
  mutation boundaries.
- **Classification:** Non-risk. The cross-cutting mapping covers installation
  and first-use mutations.

### QS-11 — Installation integrity verification

- **Approach:** The bootstrap checks the archive digest against `SHA256SUMS`
  before extraction.
- **Sensitivity:** Verification must use the selected release and reject a
  mismatch before any extraction.
- **Tradeoff:** SHA-256 detects corruption but does not authenticate the
  publisher.
- **Classification:** Non-risk within the specified integrity contract.

### QS-12 — First-session insight budget

- **Approach:** Virgil reads installation state, performs a read-only project
  scan, and reports evidence before optional configuration.
- **Sensitivity:** Decision counting and elapsed-time measurement must start at
  the specified journey boundary.
- **Tradeoff:** Early insight limits scan depth to protect time-to-value.
- **Classification:** Non-risk at architecture level. Implementation tests must
  verify the two-minute and three-decision measures.

### QS-13 — First-task result budget

- **Approach:** The approved task runs in a detached worktree or plain sandbox.
  The state machine owns the selected disposition.
- **Sensitivity:** Environment setup, dependency work, and prompts consume the
  ten-minute and five-decision budgets.
- **Tradeoff:** Isolation adds setup cost but keeps experimental output away
  from production work.
- **Classification:** Non-risk at architecture level. End-to-end tests must
  verify both sandbox variants and the budget.

## Risk Summary

No Medium, Major, or Critical architecture risks remain.

| Residual risk                                                                          | Severity                                   | Treatment                                                      |
| -------------------------------------------------------------------------------------- | ------------------------------------------ | -------------------------------------------------------------- |
| SHA-256 checks detect corruption but do not authenticate the publisher.                | Low; outside the accepted feature contract | Revisit signed release metadata in a separate security change. |
| QS-12 and QS-13 budgets depend on consistent timing and user-decision instrumentation. | Low; implementation risk                   | Use the QA strategy's end-to-end journey checks.               |
| Structurizr's hosted default theme reaches end of life on 30 September 2026.           | Low; tooling risk                          | Pin or host a replacement theme before the upstream date.      |

## Tradeoff Summary

| Tradeoff                                            | Selected position                                                        | Consequence                                                                          |
| --------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| Layered bootstrap versus one installation script    | Keep `install-agent-factory` around `init-factory`.                      | Host diagnosis stays separate from project setup at the cost of another entry point. |
| Consent versus decision budget                      | Prompt only at mutation and trust boundaries.                            | Explanations do not consume consent, while state changes remain explicit.            |
| Git worktree versus plain sandbox                   | Select by whether `HEAD` exists.                                         | Both new and established repositories receive isolation.                             |
| Dynamic views versus state-machine branching        | Dynamic views own shared execution; the state machine owns dispositions. | The canonical model avoids serializing mutually exclusive outcomes.                  |
| Digest verification versus publisher authentication | Keep SHA-256 for this feature.                                           | Corruption is detected; publisher authentication remains outside scope.              |

## Changed Artifacts

- `docs/adr/0023-update-transaction-with-approval-staging-and-rollback.md`
- `docs/arc42/architecture.dsl`
- `docs/arc42/05_building_block_view.md`
- `docs/arc42/06_runtime_view.md`
- `docs/arc42/08_crosscutting_concepts.md`
- `docs/arc42/09_architecture_decisions.md`
- `docs/arc42/10_quality_requirements.md`
- Structurizr SVG exports under `docs/assets/images/`, including the new
  `UpdateTransactionCheck` and `FirstTaskLifecycleNoHead` views
- This review report

The modified `packages/factory/config/session-menu.md` and untracked
`docs/proposals/external-artifact-sync.md` were outside this review and were not
changed as part of the remediation.

## Open Risks

No open architecture finding blocks implementation. The residual risks in the
risk summary require implementation verification or a separate future change.
