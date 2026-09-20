# Phase Handoff

## Boundary

Outgoing phase: requirements
Incoming phase: review
Boundary: requirements -> review

## Repository state

Checkout: /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/local-usage-processing-and-analysis
Branch: feature/local-usage-processing-and-analysis
HEAD: 6fb42c3c229902c9f02c6c59ca3456a5d8545e0b
Upstream: none
Upstream SHA: none
Ahead: 0
Behind: 0
Working tree: untracked `docs/handoffs/handoff-local-usage-processing-and-analysis-requirements.md`, owned by this phase handoff; untracked local `factory` symlink to `packages/factory`, used only to resolve installed-path command conventions and intentionally not committed; no other changes
Retained work: primary `dev` worktree at `/home/matthiasdaues/Documents/datenschoenheit/agent_factory` remains at `7be773c967c7e2c8c7cc905f10aaa297cec22081` with the user's unrelated `packages/factory/CHANGELOG.md` modification; worktree and branch `feature/test-design-layer-redistribution` remain active at `4926554398098019550f5e466f9d21c412cf24dc` for unrelated work

## Decisions and open items

Decisions: The accepted [Local Usage Processing and Analysis proposal](../proposals/implemented/usage-processing-and-storage.md) remains the immutable requirements origin. Release 1 keeps local JSONL as authoritative evidence and derives results through version-controlled DuckDB SQL. The specification contains nine Rule-per-actor-goal groups covering fixed local input selection, the exact six published views, conservative four-CLI accounting, strict preflight and health diagnostics, required table/JSON/DuckDB-relation/PyArrow outputs, atomic attributable Parquet export, bundled-UI exploration, opt-in component lifecycle, Factory-owned record compatibility and capture independence, and sole deterministic gate ownership. Evidence identity is source file plus line until canonical reduction; snapshot selection uses capture sequence plus a deterministic source-position tie-breaker. Invalid input leaves `capture_health` available while all other stable views and exports refuse partial output. Component add, update, and removal preserve `.agent-factory/usage/`; full `remove-factory` retains complete-removal semantics. The scope map adds all nine Rules as `specified`. Supplementary specs define entity identities and invariants, CLI/file/output/lifecycle contracts, validation rules, and query/component state machines. The QA strategy assigns each observable contract exactly one deterministic or pytest owner and prohibits query/export arithmetic duplication. PostgreSQL, persistent authoritative analytical stores, automatic Parquet materialization, notebooks, dashboards, services, containers, remote resources, centralized collection, access control, price catalogs, transcript indexing, automatic evidence retention/deletion, Pandas, and Polars remain deferred.
Open items: No unresolved requirement or design decision. The QA strategy records two implementation-time gaps: `docs/testing.yaml` does not yet bind a deterministic-linter layer for five new standalone gate owners, and the requirements step manifest excluded source/test-tree reads so concrete test locations must be re-scanned during Planning within its declared inputs. Broad repository checks also expose unrelated baseline debt: Ruff reports 24 findings and 7 unformatted test files, `concern-lint` reports four absent generated CLI INDEX paths, and an isolated-cache `index-lint --check` cannot fetch `tiktoken` because network access is unavailable; none touches or invalidates the committed Requirements artifacts.

## Artifacts

- docs/handoffs/handoff-local-usage-processing-and-analysis-requirements.md
- docs/proposals/usage-processing-and-storage.md
- docs/spec/local-usage-processing-and-analysis.feature
- docs/spec/local-usage-processing-and-analysis-gaps.md
- docs/spec/local-usage-processing-and-analysis-qa-strategy.md
- docs/spec/scope-map.md
- docs/spec/supplementary_specs/entity-model.md
- docs/spec/supplementary_specs/interface-contracts.md
- docs/spec/supplementary_specs/state-machines.md
- docs/spec/supplementary_specs/validation-rules.md
- docs/spec/agent-context.feature
- docs/testing.yaml

## Gate and verification evidence

Gates: Commit `6fb42c3c229902c9f02c6c59ca3456a5d8545e0b` passed both configured hook sets for Markdown formatting, local Markdown links, Mermaid notation, `spec-lint`, and `statemachine-lint`; direct `spec-lint` evidence was 0 errors, 0 warnings, and 27 info; direct `statemachine-lint` evidence was 0 errors, 0 warnings, and 0 info; changed-file link-check passed; direct `mermaid-lint` passed. Check-only `arch-lint` returned 0 errors and one pre-existing `ARCH-PARSE` warning; `backlog-lint` returned 0 errors and 11 pre-existing warnings; `matrix-lint` returned 0 errors and 0 warnings. Broad Ruff check/format, `concern-lint`, and isolated-cache `index-lint` have the unrelated baseline or environment blockers recorded under Open items and were not repaired by widening this Requirements change.
Verification: The committed feature has nine Rules and at least one Scenario per Rule; the gaps report records complete actor-goal coverage and no ambiguous wording; the scope map contains all nine Rules with `specified` status and live feature links; the QA strategy contains Feature, Test Layers in Scope, Contract Owners, Boundary Cases, Gap Findings, Defect Severity Triage, and Test Retention Policy sections; all four required supplementary specification files exist and carry the accepted local-only, accounting, lifecycle, ownership, and deferral semantics; `git diff --check` passed before commit.

## Next action

In a fresh specification-review session, read this handoff first, verify its Git claims, create the feature-addition `spec-review` step manifest, and run `spec-review-agent` against the named proposal and `docs/spec/` artifacts. File any `SPEC-*` findings without entering Architecture.

## Semantic review

Reviewer: pending assignment
Status: pending
Evidence: Independent reviewer must compare the handoff against commit `6fb42c3c229902c9f02c6c59ca3456a5d8545e0b`, the accepted proposal, every named Requirements artifact, the recorded gate results and blockers, the retained unrelated work, and the review-only next action.
