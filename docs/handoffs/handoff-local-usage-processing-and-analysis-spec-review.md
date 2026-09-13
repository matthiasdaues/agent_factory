# Phase Handoff

## Boundary

Outgoing phase: requirements
Incoming phase: review
Boundary: requirements -> review

## Repository state

Checkout: /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/local-usage-processing-and-analysis
Branch: feature/local-usage-processing-and-analysis
HEAD: 89000e4ea79fadb6f4ba81b3e61555940d049cc2
Upstream: none
Upstream SHA: none
Ahead: 0
Behind: 0
Working tree: untracked `docs/handoffs/handoff-local-usage-processing-and-analysis-requirements.md` and `docs/handoffs/handoff-local-usage-processing-and-analysis-spec-review.md`, both owned by phase handoffs; no other changes
Retained work: primary `dev` worktree at `/home/matthiasdaues/Documents/datenschoenheit/agent_factory` is at `34350d5bc5a079eb8cfd666ec4f2906c3e6e86dd` and retains unrelated modifications to `packages/factory/CHANGELOG.md`, `packages/factory/rulebooks/templates/story.md`, `packages/factory/scripts/backlog-lint`, `packages/factory/skills/create-backlog-stories/SKILL.md`, `packages/factory/skills/create-backlog/SKILL.md`, and `packages/factory/skills/grilling/SKILL.md`, plus untracked `docs/reviews/skill-agent-audit-2026-09-12.md`, `packages/factory/skills/create-backlog-make-concrete/`, and `packages/factory/skills/create-backlog-slice-story/`; unrelated worktree `/home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/test-design-layer-redistribution` and branch `feature/test-design-layer-redistribution` are at `4926554398098019550f5e466f9d21c412cf24dc` with untracked local convenience path `factory`

## Decisions and open items

Decisions: Requirements preserve accepted proposal baseline `00836e73de3d754012a3443e158e6f52c5120537` without scope expansion and specify nine actor-goal Rules. Query startup snapshots the sorted top-level JSONL input set, records source-file and line evidence identity, and selects latest cumulative snapshots by capture sequence with deterministic evidence-position tie-breaking. Strict preflight registers valid and failure relations; `capture_health` remains queryable for invalid input, while all other stable views refuse partial results. The exact six published views are `raw_usage_snapshots`, `latest_run_snapshots`, `canonical_session_usage`, `usage_by_dimension`, `cache_efficiency`, and `capture_health`. Four-CLI accounting conserves Claude Code as latest root plus distinct children, Pi as root plus distinct descendants, and Codex/GitHub Copilot CLI as latest inclusive roots with children used only for attribution. Required outputs are table, JSON, DuckDB relation, and PyArrow table; Parquet replacement is atomic and attributable; DuckDB's bundled UI is the only release-1 exploration surface. Usage analysis is opt-in; component removal deletes analysis but preserves `.agent-factory/usage/`, whereas full `remove-factory` retains complete-removal semantics including raw data. Installed invocation is `uv run --project .agent-factory/usage-analysis usage-query`, using `.agent-factory/usage/` by default or `--usage-dir`, and becomes offline-capable after dependency caching. The scope map adds all nine Rules as `specified`; the gaps report finds no missing Rule, scenario, or ambiguous wording; the QA strategy assigns contracts LU-01 through LU-11 to one deterministic-linter, contract-test, or integration-test owner each. PostgreSQL, SQLite, a persistent authoritative DuckDB database, automatic Parquet materialization, Marimo, Jupyter, Grafana, dashboards, services/APIs, remote/cloud resources, price catalogs, transcript-content indexing, retention automation, Pandas, and Polars remain explicitly deferred. At the stakeholder's explicit direction, `docs/spec/agent-context.feature` was restored byte-for-byte from the parent of deletion commit `45667fb4a28ee48c9a67fa497f4e9d8eade434d5`; rebased commit `89000e4ea79fadb6f4ba81b3e61555940d049cc2` corrects an accidental Markdown-formatting pass so the restored file's SHA-256 is again `6b2af3294f033c167b7d1bc3a476b99300b8db65a61bcce4abb94a5ba8efa678`. BUG-0027 repaired the public feature-addition `spec-review` manifest so it now admits `docs/CONTEXT.md` and permits the mandatory `docs/reviews/spec-review-*.md` report.
Open items: The QA strategy records that `docs/testing.yaml` lacks a deterministic-linter layer binding for five future standalone usage gates; implementation must add the binding when those gates exist. Planning must rescan concrete test locations because the Requirements step manifest excluded source and test-tree reads. Eight pre-existing entries remain in `docs/spec/todos.md`; current `spec-lint` reports them and 25 pre-existing unused-business-rule notices plus one pre-existing entity-model notice as 27 information findings, with no warnings or errors. Repository-wide Ruff validation has 24 pre-existing lint errors and seven files needing Ruff formatting; `concern-lint` has four linked-worktree-only missing CLI-index errors; the earlier Requirements `index-lint --check` could not resolve `tiktoken` because network access was unavailable. Non-blocking baseline gates report `arch-lint` 0 errors/1 `ARCH-PARSE` warning, `backlog-lint` 0 errors/11 warnings, and `matrix-lint` 0 errors/0 warnings. The restored `agent-context.feature` describes the formerly archived YAML model; independent specification review must assess its consistency with the current concern-oriented context specification and references rather than assuming that link restoration makes its behavior current.

## Artifacts

- docs/handoffs/handoff-local-usage-processing-and-analysis-requirements.md
- docs/handoffs/handoff-local-usage-processing-and-analysis-spec-review.md
- docs/proposals/usage-processing-and-storage.md
- docs/CONTEXT.md
- docs/spec/local-usage-processing-and-analysis.feature
- docs/spec/local-usage-processing-and-analysis-gaps.md
- docs/spec/local-usage-processing-and-analysis-qa-strategy.md
- docs/spec/agent-context.feature
- docs/spec/scope-map.md
- docs/spec/todos.md
- docs/spec/supplementary_specs/entity-model.md
- docs/spec/supplementary_specs/interface-contracts.md
- docs/spec/supplementary_specs/state-machines.md
- docs/spec/supplementary_specs/validation-rules.md
- docs/testing.yaml
- packages/factory/playbooks/feature-addition.md
- packages/factory/INDEX.yaml
- packages/factory/agents/spec-review-agent.md
- packages/factory/skills/inspect-spec/SKILL.md
- packages/factory/scripts/spec-lint
- packages/factory/scripts/statemachine-lint
- packages/factory/scripts/link-check
- tests/factory/test_feature_addition_contract.py
- docs/findings/BUG-0027.md

## Gate and verification evidence

Gates: Rebased Requirements commit `02dc5a7` passed its commit hooks; rebased restored-feature correction commit `89000e4ea79fadb6f4ba81b3e61555940d049cc2` passed `spec-lint` in both installed and tracked hook sets. Post-commit `packages/factory/scripts/spec-lint --spec-dir docs/spec` reports 0 errors, 0 warnings, and 27 information findings across 18 files; `statemachine-lint` reports 0 errors, 0 warnings, and 0 information findings; changed-spec local link checking passes; Mermaid lint reports no raw semicolons. Repository-wide baseline results are Ruff check 24 errors, Ruff format 7 files, `concern-lint` 4 missing CLI-index errors, earlier Requirements `index-lint --check` unavailable because `tiktoken` could not be fetched without network, `arch-lint` 0 errors/1 warning, `backlog-lint` 0 errors/11 warnings, and `matrix-lint` 0 errors/0 warnings. BUG-0027 implementation commit `a7f616f2338498ad1b1a673753aa99719c10c514` passed all commit hooks, two focused regression tests, Ruff checks, an independent QA review with zero findings, and the post-merge suite at 477 passed and 7 skipped; resolution commit is `34350d5bc5a079eb8cfd666ec4f2906c3e6e86dd`.
Verification: The restored `agent-context.feature` matches the historical blob by SHA-256; the Requirements-era complete pytest suite passed 482 tests after installing the linked-worktree convenience path, and the current post-repair suite passes 477 tests with 7 skips; `git diff --check` passes. Requirements artifacts trace the accepted proposal's nine actor goals, 20 completion criteria, and release-1 deferrals into the feature, gaps report, scope map, supplementary specifications, and QA ownership table.

## Next action

In a fresh spec-review-agent session, read this handoff first and verify its checkout, branch, HEAD, upstream, working tree, and retained work. Create the feature-addition `spec-review` step manifest, then run the two-pass `inspect-spec` workflow: rerun deterministic `spec-lint` and independently inspect the new local-usage feature, gaps report, QA strategy, scope-map rows, and supplementary changes against the accepted proposal. Explicitly assess whether the stakeholder-restored `agent-context.feature` is consistent with the current specification set. Persist the mandatory `docs/reviews/spec-review-*.md` report and every blocking review finding as canonical `docs/findings/SPEC-*.md` artifacts on `dev`, return only the disposition envelope, and do not enter Architecture.

## Semantic review

Reviewer: pending assignment
Status: pending
Evidence: accepted proposal, committed Requirements diff, restored historical feature blob, gaps and QA-strategy open items, Git state, gate results, artifact inventory, and specification-review next action must be compared for omission or distortion
