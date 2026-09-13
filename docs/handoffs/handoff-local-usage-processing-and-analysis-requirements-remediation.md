# Phase Handoff

## Boundary

Outgoing phase: requirements
Incoming phase: review
Boundary: requirements -> review

## Repository state

Checkout: /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/local-usage-processing-and-analysis
Branch: feature/local-usage-processing-and-analysis
HEAD: 47dc7920fdd31eca12f9f3bd54ec0435d3c26598
Upstream: none
Upstream SHA: none
Ahead: 0
Behind: 0
Working tree: untracked `docs/handoffs/handoff-local-usage-processing-and-analysis-requirements.md` and `docs/handoffs/handoff-local-usage-processing-and-analysis-spec-review.md` are pre-existing phase handoffs; untracked `factory` is the pre-existing convenience symlink; untracked `docs/handoffs/handoff-local-usage-processing-and-analysis-requirements-remediation.md` is this handoff. No tracked modifications remain.
Retained work: current feature worktree and branch are the named review base; `/home/matthiasdaues/Documents/datenschoenheit/agent_factory` on `dev` and `/home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/test-design-layer-redistribution` on `feature/test-design-layer-redistribution` are unrelated retained worktrees.

## Decisions and open items

Decisions: Stakeholder required the concern-oriented agent-context specification to replace, not delete, the restored legacy feature. `docs/agent-context.md`, `concern-lint`, controlled concern vocabulary, direct registry maintenance, and `docs/testing.yaml` now form the sole live model. All four usage CLIs use logical-run identity `(cli, session_id, run_id)`; `parent_run_id` defines ancestry and source identity is removed from the logical-run key while selected source evidence remains available. Latest evidence maximizes `(capture_sequence, normalized_source_path, source_line)` after repository-independent path normalization, using numeric, unsigned UTF-8 byte lexicographic, then numeric comparison. Canonical session dimensions and `captured_at` come from the selected root snapshot; additive Claude Code and Pi descendants contribute measures without replacing root dimensions. Cache aggregation uses exactly the logical runs admitted by the selected CLI conservation rule. Query-model-v1 defines complete schemas, keys, nullability, and stable result ordering for six published views. Dimension requests use an ordered subset of seven named dimensions plus `none|hour|day|week|month`; defaults and invalid requests are explicit. Required `pyarrow.Table` output is retained; the specification requires direct, isolated, locked DuckDB and PyArrow dependencies, and future LU-13 must prove lock compatibility and offline-cache operation. UI launch remains optional; LU-12 owns an executable documentation/bootstrap smoke contract without launching or fetching the UI. These decisions are traced across the named proposal origins, feature files, QA strategy, and supplementary specifications and are committed at `47dc7920fdd31eca12f9f3bd54ec0435d3c26598`.
Open items: [SPEC-0015](../findings/SPEC-0015.md), [SPEC-0016](../findings/SPEC-0016.md), [SPEC-0017](../findings/SPEC-0017.md), [SPEC-0018](../findings/SPEC-0018.md), and [SPEC-0019](../findings/SPEC-0019.md) remain `open`; only the independent repeat reviewer may verify and change their status. Architecture has not started.

## Artifacts

- docs/handoffs/handoff-local-usage-processing-and-analysis-requirements-remediation.md
- docs/reviews/spec-review-2026-09-13.md
- docs/findings/SPEC-0015.md
- docs/findings/SPEC-0016.md
- docs/findings/SPEC-0017.md
- docs/findings/SPEC-0018.md
- docs/findings/SPEC-0019.md
- docs/proposals/factory-concern-oriented-agent-context.md
- docs/proposals/usage-processing-and-storage.md
- docs/spec/agent-context.feature
- docs/spec/local-usage-processing-and-analysis.feature
- docs/spec/local-usage-processing-and-analysis-gaps.md
- docs/spec/local-usage-processing-and-analysis-qa-strategy.md
- docs/spec/scope-map.md
- docs/spec/supplementary_specs/entity-model.md
- docs/spec/supplementary_specs/interface-contracts.md
- docs/spec/supplementary_specs/state-machines.md
- docs/spec/supplementary_specs/validation-rules.md

## Gate and verification evidence

Gates: `factory/scripts/handoff-lint docs/handoffs/handoff-local-usage-processing-and-analysis-requirements-remediation.md` reported that the handoff is structurally valid; `factory/scripts/spec-lint --spec-dir docs/spec` passed with 0 errors, 0 warnings, and 27 pre-existing informational notices across 18 files; `factory/scripts/statemachine-lint docs/spec/supplementary_specs/state-machines.md` passed with 0 errors, 0 warnings, and 0 info; changed-artifact `factory/scripts/link-check` passed; changed-Mermaid `factory/scripts/mermaid-lint` passed; `factory/scripts/validate` passed on all changed Markdown; `git diff --check` passed. Commit hooks repeated mdformat, link-check, spec-lint, and statemachine-lint successfully.
Verification: focused checks confirmed all feature Rule names occur in `docs/spec/scope-map.md`, exactly six query-model-v1 schema headings exist, the complete maximum evidence tuple is declared, LU-12 owns UI documentation/bootstrap behavior, LU-13 owns locked DuckDB/PyArrow and offline-cache behavior, obsolete `context-lint` and YAML-routing terms are absent from the rewritten live agent-context specification and supplementary traces, and no finding file status was changed.

## Next action

Start a fresh specification-review-agent session. Read this handoff first, verify its Git and working-tree claims, then read the five findings and named changed specification artifacts in bounded chunks. Re-run deterministic spec-lint, verify each prior finding individually, conduct a fresh full semantic inspection, update finding statuses only from evidence, and publish the repeat review disposition. Do not enter Architecture unless the repeat review passes.

## Semantic review

Reviewer: pending independent semantic reviewer
Status: pending
Evidence: pending comparison of the handoff against the committed remediation, five open findings, proposal decisions, changed specification artifacts, gate results, repository state, and next action.
