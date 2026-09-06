---
title: "Implementation Report: ST-0098 — Update requirements-agent with scope-map and derive-feature integration"
date: 2026-01-26
story: ST-0098
status: done
---

# Implementation Report: ST-0098

## Summary

Updated `factory/agents/requirements-agent.md` from v0.4.0 to v0.5.0, replacing
the `derive-spec` invocation with `derive-feature` and adding scope-map, QA
strategy, and gaps-report outputs. All ten acceptance criteria met.

## Artifact Changed

| File                                   | Change                                               |
| -------------------------------------- | ---------------------------------------------------- |
| `factory/agents/requirements-agent.md` | Updated: header, Role, Workflow, Completion Criteria |
| `backlog/ST-0098.md`                   | `status: pending` → `status: done`                   |
| `factory/INDEX.yaml`                   | Regenerated (stale, non-blocking)                    |

## Acceptance Criteria Coverage

| #    | Criterion                                                                                                | Status                                              |
| ---- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| AC1  | `derive-feature` invoked instead of `derive-spec`                                                        | ✅ Step 4b                                          |
| AC2  | `docs/spec/scope-map.md` produced with Rules, status, slice, feature-file link                           | ✅ Step 4c (derive-feature updates it)              |
| AC3  | `docs/spec/<feature-name>.feature` with Rule-per-actor-goal structure                                    | ✅ Step 4b (derive-feature writes it)               |
| AC4  | `docs/spec/<feature-name>-gaps.md` produced                                                              | ✅ Step 4b (derive-feature writes it)               |
| AC5  | `docs/spec/<feature-name>-qa-strategy.md` via `qa-strategy-from-spec` skill                              | ✅ Step 5                                           |
| AC6  | Scope map lifecycle: deferred → specified → implemented                                                  | ✅ Step 4c (derive-feature § Scope Map Integration) |
| AC7  | Migration check: if scope-map absent but UC-XX docs exist, run `scope-map-migration` first               | ✅ Step 4a                                          |
| AC8  | Supplementary specs still produced (entity-model, interface-contracts, state-machines, validation-rules) | ✅ Step 4d                                          |
| AC9  | UC-XX document chain and `actor-goal-list.md` no longer produced as separate artifacts                   | ✅ outputs list, "What is not produced" section     |
| AC10 | All outputs pass `factory/scripts/validate`                                                              | ✅ Completion Criteria                              |

## Key Design Decisions

**No UC document chain**: The `.feature` file's Rule-per-actor-goal structure
replaces `actor-goal-list.md` and the UC-XX file chain. The `derive-feature`
skill uses Cockburn reasoning internally but produces no intermediate prose
documents.

**Scope-map lifecycle in derive-feature**: The `derive-feature` skill (ST-0096)
already implements the scope-map update as part of its § Scope Map Integration
step. The requirements-agent's Step 4c references this behavior rather than
duplicating it.

**Migration trigger**: Step 4a checks for `docs/spec/scope-map.md` before
step 4b. If absent but UC-XX files exist, `scope-map-migration` is invoked
first. If neither exists, `derive-feature` creates the scope map from scratch.

**Supplementary specs retained**: Steps 4d produces `entity-model.md`,
`interface-contracts.md`, `state-machines.md`, `validation-rules.md` — they
carry structural facts (entity lifecycles, validation rules, boundary schemas)
the Gherkin `.feature` file does not encode.

## Gating Results

| Gate                               | Result                                                        |
| ---------------------------------- | ------------------------------------------------------------- |
| `backlog-lint`                     | 0 errors, 14 warnings (pre-existing, unrelated to this story) |
| `mdformat` (requirements-agent.md) | PASS                                                          |
| `index-lint`                       | Stale index regenerated                                       |
| `link-check`                       | No failures on changed artifacts                              |

## Findings

No defects identified. No open SPEC-\* findings.

## Disposition

`pass` — all acceptance criteria met, file updated to v0.5.0.
