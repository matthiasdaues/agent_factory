---
type: remediation-strategy
title: Documentation Drift Remediation Strategy
date: 2026-11-03
status: proposed
owner: reconciliation-agent
source: reconciliation-2026-11-03.md
---

# Documentation Drift Remediation Strategy

## Objective

Restore one testable product contract across user-facing documentation, specification, architecture, code, generated artifacts, and reconciliation records. This strategy remediates the findings in the [2026-11-03 reconciliation report](reconciliation-2026-11-03.md) without overwriting concurrent core-artifact-ownership work.

Completion means that a new user can install, configure, operate, query, update, and remove Agent Factory by following published commands; every resulting behaviour is represented by the specification and guarded by an executable check.

## Remediation principles

1. Settle disputed contracts before editing explanatory prose. Otherwise documentation can become internally polished while remaining wrong.
2. Repair executable journeys before promoting them as the default path.
3. Assign one owner to every generated artifact and configuration field: project source, installed runtime state, or removable Factory output.
4. Add a deterministic guard for every corrected drift class so reconciliation is not a recurring manual cleanup.
5. Sequence work by file overlap. The concurrently edited core-artifact-ownership specification files are a temporary exclusion zone until their changes land.

## Decisions required before implementation

| Decision                      | Options                                                                                       | Recommended default                                                                                                                          | Blocks                                                                                                                                                                                                                                                          |
| ----------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage query model             | Implement all six `query-model-v1` views consistently, or narrow and version the public model | Preserve and implement the six-view model unless product intent has changed                                                                  | [C-01](reconciliation-2026-11-03.md#c-01--published-usage-query-model-is-not-implemented-as-specified), [M-09](reconciliation-2026-11-03.md#m-09----persist-does-not-materialize-every-public-view), [E-03 and E-06](reconciliation-2026-11-03.md#minor-errata) |
| `docs/testing.yaml` lifecycle | Retained project source, or installation-owned removable output                               | Retained project source; document that removal deliberately preserves it                                                                     | [M-04 and M-05](reconciliation-2026-11-03.md#m-04--the-install-and-removal-footprint-is-understated)                                                                                                                                                            |
| Dispatch configuration owner  | Tracked project configuration, or installed `.agent-factory/config/project.json`              | Use the declared installed configuration only for install identity; place project routing policy in a tracked, schema-validated project file | [M-14](reconciliation-2026-11-03.md#m-14--dispatcher-routing-configuration-has-two-owners)                                                                                                                                                                      |
| Story schema                  | `outputs`, or the `touches`-based template schema                                             | Adopt one schema based on current consumers, migrate existing stories, and make the shipped template a linter fixture                        | [M-15](reconciliation-2026-11-03.md#m-15--the-story-schema-is-split-across-three-contracts)                                                                                                                                                                     |
| Freshness policy              | Warning-only, or automatic mutation                                                           | Keep warning-only behaviour and correct the documentation                                                                                    | [M-13](reconciliation-2026-11-03.md#m-13--freshness-checking-warns-but-does-not-update)                                                                                                                                                                         |

Record decisions that change public or architectural contracts before code work begins. Pure corrections to match already-decided behaviour do not need new ADRs.

## Delivery sequence

### Wave 0 — Stabilize the baseline

1. Land or explicitly abandon the concurrent core-artifact-ownership work.
2. Rebase the finding map on the resulting commit and recheck the pre-existing sections cited by this review.
3. Resolve the five decisions above and name an owner for each workstream.
4. Reverify [RECON-0018](../findings/RECON-0018.md), [RECON-0019](../findings/RECON-0019.md), [RECON-0023](../findings/RECON-0023.md), and [RECON-cycle-retirement](../findings/RECON-cycle-retirement.md). Close obsolete entries and split any surviving discrepancy into a current, bounded finding.

Exit criterion: a fixed remediation baseline, no unresolved contract choice, and no ambiguous open reconciliation record.

### Wave 1 — Remove unsafe user journeys

These tracks can proceed in parallel when their listed files do not overlap.

#### Track A: installation and removal

- Restore and test automatic selection for exactly one detected interface and linked instruction installation.
- Make bootstrap the primary root-README path; move cloning to a contributor section.
- Correct the removal command to name an explicit target.
- Test the complete tracked and untracked footprint of initialization and removal, including the chosen `docs/testing.yaml` lifecycle.
- Correct the generated-file and configuration inventory.

Primary files: [README.md](../../README.md), [packages/factory/README.md](../../packages/factory/README.md), [install-agent-factory](../../packages/factory/scripts/install-agent-factory), [init-factory](../../packages/factory/scripts/init-factory), [remove-factory](../../packages/factory/scripts/remove-factory), and the onboarding tests.

Exit criterion: a temporary repository can follow the published bootstrap and removal commands with the expected receipt and a clean, policy-compliant final `git status`.

#### Track B: usage query contract

- Implement or deliberately narrow the six-view public query model.
- Use one schema definition or conformance fixture for Python, DuckDB bootstrap, CLI output, and persistence.
- Apply equivalent ancestry validation in both execution paths.
- Make `--persist` semantics explicit and test all named public relations.
- Align `--granularity`, optional PyArrow behaviour, and advertised output formats.

Primary files: [packages/usage/src/usage](../../packages/usage/src/usage/), [bootstrap-v1.sql](../../packages/usage/sql/bootstrap-v1.sql), usage tests, and—after the concurrent edit window closes—the usage sections of [interface-contracts.md](../spec/interface-contracts.md).

Exit criterion: one golden fixture produces schema-equivalent results through Python, direct DuckDB bootstrap, CLI serialization, and a reopened persisted database.

#### Track C: schema and routing contracts

- Choose and migrate the story frontmatter schema.
- Make an untouched copy of the shipped story template pass `backlog-lint`.
- Select a single routing-policy owner and migrate dispatcher lookup accordingly.
- Add schema validation and an actionable failure for missing or placeholder model configuration.

Primary files: the story template, `backlog-lint`, `dispatch_lib.py`, initializer configuration generation, and—after the concurrent edit window closes—the relevant interface-contract section.

Exit criterion: generated stories pass the governing linter unchanged, and dispatch consumes only the documented routing configuration.

### Wave 2 — Synchronize user-facing documentation

Apply this wave only after Wave 1 behaviour is merged, so the prose describes tested reality.

- Replace obsolete `.agent-factory/usage-analysis/` paths with `.agent-factory/usage/analysis/`, except in explicit migration history.
- Correct installed wrapper paths to `.agent-factory/factory/scripts/`.
- Document usage analysis as opt-in through `--with-usage` or `--add usage`.
- Correct persistence and explorer watch examples.
- Replace Factory-owned test-hook claims with the project-owned testing model.
- Explain `CONFIGURE-ME` fitting requirements and halt behaviour.
- Describe freshness as warning-only.
- Introduce manual, mechanized, and automated modes together in the guide.
- Apply E-01 through E-09 from the [minor errata register](reconciliation-2026-11-03.md#minor-errata).

Primary files: [README.md](../../README.md), [packages/factory/README.md](../../packages/factory/README.md), [packages/usage/README.md](../../packages/usage/README.md), [factory-guide.md](../../packages/factory/docs/factory-guide.md), and [ui-exploration.md](../../packages/usage/docs/ui-exploration.md).

Exit criterion: every shell command in user-facing docs succeeds in a clean temporary project, and the terminology/path sweep finds no obsolete live references.

### Wave 3 — Reconcile specification and architecture

- Update usage contracts and architecture views to the decided model and installed path.
- Normalize the three fenced or escaped-comment feature files and every noncanonical `Rule` declaration.
- Add deterministic Gherkin parsing and reference checks; do not rely on indentation-sensitive regular expressions.
- Reconcile OpenCode support, the granularity option, dependency claims, test ownership, and mechanized dispatch with the consolidated feature set and scope map.
- Update or supersede historical ADR text only where it incorrectly presents an old path as current. Preserve true historical decisions.

Primary files: [docs/spec](../spec/), [architecture.dsl](../spec/architecture.dsl), relevant ADRs, and specification linters.

Exit criterion: `spec-lint` and architecture validation pass, every feature parses as Gherkin, all Rule references are discoverable, and no current contract names the obsolete installed path.

### Wave 4 — Close the loop

- Run a fresh code-versus-spec reconciliation from the post-remediation commit.
- Resolve this report only when every row is either corrected or superseded by an explicit product decision.
- File separate bounded defects only for work intentionally deferred beyond the remediation release.
- Publish a short user-visible migration note for any changed command, path, database schema, or configuration owner.

Exit criterion: the repeat reconciliation has no critical or major discrepancies and every accepted minor exception has an owner and expiry condition.

## Ownership and overlap map

| Workstream                  | Primary ownership boundary                                                  | Must coordinate with                                           |
| --------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Bootstrap journey           | Factory installer, initializer, remover, onboarding tests                   | Root and Factory README owner                                  |
| Usage model                 | `packages/usage`, usage tests, usage SQL                                    | Usage specification and architecture owner                     |
| Story schema                | Story template, backlog linter, backlog migration                           | Interface-contract owner and planning workflow owner           |
| Dispatch configuration      | Initializer configuration and dispatcher library                            | Guide and architecture owner                                   |
| Public documentation        | Root/package READMEs and user guides                                        | Every executable workstream; starts after behaviour stabilizes |
| Specification normalization | Features, supplementary contracts, architecture DSL, ADR current-state text | Concurrent core-artifact-ownership work must land first        |
| Finding retirement          | `docs/findings` and reconciliation reports                                  | Owners of the corrected code/spec rows                         |

Do not assign the same file to parallel workers. In particular, [interface-contracts.md](../spec/interface-contracts.md), [validation-rules.md](../spec/validation-rules.md), and the other concurrently modified core-artifact-ownership documents should have one integration owner after the current work completes.

## Verification gates

The remediation is complete only when all applicable gates below pass from a writable, supported development environment.

01. Bootstrap journey tests cover zero, one, and multiple detected interfaces; linked instruction installation; preflight failure; receipt generation; update; and targeted removal.
02. A clean temporary Git repository proves the documented tracked/untracked footprint before and after removal.
03. A shared usage fixture proves field names, types, nullability, ordering, validation, and row equivalence across Python, DuckDB bootstrap, persistence, and CLI output.
04. The persisted database contains every public relation promised by the decided query-model version.
05. The shipped story template passes `backlog-lint` without editing.
06. All feature files parse as Gherkin, and the reconciliation/reference sweep discovers every Rule independently of indentation.
07. `spec-lint`, `concern-lint`, `index-lint`, `backlog-lint`, the usage suite, the full repository suite, and Structurizr validation pass or have a separately approved environment exception.
08. A command extractor executes user-facing shell examples in disposable projects.
09. A terminology sweep finds no live `.agent-factory/usage-analysis/`, `factory/scripts/` installed wrapper, automatic updater, or Factory-owned test-hook claim.
10. Every open `RECON` finding names a currently reproducible discrepancy and current artifact.

## Priority and release policy

- **P0:** Decide and reconcile the usage query model; fix the single-interface bootstrap regression; correct the unsafe removal example.
- **P1:** Correct install/removal ownership, usage paths and persistence, dispatch configuration, story schema, test ownership, model fitting, and Gherkin structure.
- **P2:** Apply the nine minor errata and prose cleanup after the governing behaviour is stable.

Do not mark the documentation set reconciled, or use the existing six-view and frictionless-bootstrap claims in release material, until all P0 items and their verification gates pass. P1 work may ship in successive slices if each slice leaves commands and contracts internally consistent. P2 work may follow, but accepted errata must remain visible in the reconciliation register until closed.
