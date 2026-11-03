---
schema_version: 2
title: Manual Mode Gates
status: draft
owner: agent-factory
created: 2026-11-03
updated: 2026-11-03
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/config/pre-commit-config.yaml
    - packages/factory/agents/implementation-agent.md
    - packages/factory/agents/developer-agent.md
    - packages/factory/rulebooks/conventions/dispatch-contract.md
    - packages/factory/scripts/crap-score
    - packages/factory/scripts/dependency-check
    - packages/factory/scripts/test-design-verify
    - docs/proposals/core-artifact-ownership.md

governance:
  assurance: elevated
  risk_domains:
    - reliability

estimate:
  as_of: 2026-11-03
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Manual Mode Gates

## Primer

The primer is written last, by the `write-primer` skill, once the design is settled.

## Summary

In manual mode, the same quality gates hold as in automated mode, and a mechanism enforces them. The fast gates run as pre-commit hooks on every commit. The slow gates run in a story-close check, and a hook refuses the commit that sets a story to `done` until that check has passed. The first release covers `crap-score`, `dependency-check`, `test-design-verify`, and mutation testing.

## Motivation

In manual mode, the human commits each story, and no quality gate runs. [implementation-agent.md](../../packages/factory/agents/implementation-agent.md) says: "The gate-check loop applies to automated mode only. In manual mode, the code-review-agent replaces the mechanized gate-check loop." Only the pre-commit hooks run, with the test suite and the Factory linters.

So a function with a CRAP score of 42 against a threshold of 30 merges in manual mode, and the same function blocks the merge in automated mode. The two modes measure the code differently, although they work against the same `testing.yaml`.

The accepted proposal [core-artifact-ownership.md](core-artifact-ownership.md) closes this with an instruction: the developer agent runs the gates before it hands a story back (DEC-23 there). An instruction is not enforcement. If the agent skips it, nothing notices.

## Core Principles

- **One gate set, two modes.** Both modes run the gates that the story's `quality-gates` field or `testing.yaml` selects, with the same thresholds.
- **Enforced at a fixed point.** A gate runs where it cannot be skipped: at the commit, or at the commit that closes a story.
- **Fast on every commit, slow once per story.** A gate that takes minutes does not run on every commit.

## Design

### Fast gates as pre-commit hooks

Two new hooks join the Factory hook block in `packages/factory/config/pre-commit-config.yaml`:

| Hook               | Runs on             | Needs                                                                    |
| ------------------ | ------------------- | ------------------------------------------------------------------------ |
| `dependency-check` | staged source files | `docs/spec/dependency-rules.dsl`                                         |
| `crap-score`       | staged source files | a coverage file from the test run, and the threshold from `testing.yaml` |

`crap-score` reads coverage. So the `run-tests` hook writes its coverage report to a fixed path, and the `crap-score` hook runs after it and reads that file. Both hooks skip when `testing.yaml` disables their gate.

The hooks run in both modes. In automated mode they also run on the developer agent's commit, before the dispatcher's gate-check loop runs the same gates again.

### Slow gates in a story-close check

A new script, `packages/factory/scripts/story-gates`, runs the slow gates for one story: mutation testing through the project's command in `gates.mutation_testing.command`, and `test-design-verify` against the story file. On a pass, it writes the marker `.current-work/story-gates/<story-id>.ok`, with the commit it checked.

A new hook, `story-done-gate`, watches staged story files. When a commit sets a story's `status` to `done`, the hook requires a marker for that story whose commit is the parent of the commit being made. Without such a marker, the hook refuses the commit and names `story-gates`.

In manual mode, the human runs `story-gates` before setting the story to `done`. The developer agent's handback names the command. In automated mode, `merge-story` sets `status: done` after the gate-check loop has passed, so the dispatcher writes the marker itself.

### Relation to the ownership proposal

This proposal replaces DEC-23's "the developer agent runs them before it hands a story back" with the two mechanisms above. The test-strategy agent of that proposal still owns the gates, their thresholds, and the mutation command.

## Scope

**In the first release:**

- The hooks `dependency-check` and `crap-score`, and the coverage report of `run-tests`.
- The script `story-gates` and its marker.
- The hook `story-done-gate`.
- The manual-mode workflow of the implementation agent and the developer agent's handback name `story-gates`.
- The dispatch contract states that manual mode runs the same gates.

**Explicitly deferred (do NOT plan stories for these):**

- **The command that closes a whole dispatch.** It is [T-0014](../spec/work/todo.md) and concerns automated mode.
- **Gates for documents.** YAML and prose gates are a separate concern.

## Design Details

- **Bypass.** `git commit --no-verify` skips every hook. The Factory's git guardrail already blocks it for agents. A human who bypasses it does so on purpose.

## Open Questions

- **How fast must a hook be?** `crap-score` needs a test run with coverage on every commit. If the suite is slow, `crap-score` may belong in the story-close check too.
- **Which commit does the marker name?** The parent of the closing commit is strict: any change after `story-gates` forces a rerun. A looser rule would accept changes to the story file alone.
- **Does `story-gates` replace part of the automated gate-check loop?** The loop could call the same script, so both modes share one implementation.

## Completion Criteria

- A commit in manual mode that adds a function above the CRAP threshold fails in the `crap-score` hook.
- A commit that breaks a rule of `dependency-rules.dsl` fails in the `dependency-check` hook.
- A commit that sets a story to `done` without a matching `story-gates` marker fails in the `story-done-gate` hook and names `story-gates`.
- `story-gates <story-id>` runs mutation testing and `test-design-verify` and writes the marker only when both pass.
- `implementation-agent.md` no longer says that the code review replaces the gates in manual mode.
- `index-lint --check` passes.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by  | Decision                                                                                                                                 | Raised by                                |
| ------ | ---------- | ---------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| DEC-01 | 2026-11-03 | decision   | stakeholder | Manual mode gets the same quality gates as automated mode: the fast gates as pre-commit hooks, the slow ones in a story-close check.     | project truth map, page 4                |
| DEC-02 | 2026-11-03 | decision   | stakeholder | The change gets its own proposal, separate from the accepted core-artifact-ownership proposal.                                           | process question                         |
| DEC-03 | 2026-11-03 | assumption | author      | A hook enforces the story-close check by requiring a marker before a story can be set to `done`, as `premerge-check-ok` does for merges. | stakeholder rule: enforcement over prose |

## Review findings

No review has run yet.

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

No review has run yet.

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
