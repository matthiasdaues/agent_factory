---
schema_version: 2
scope: global
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
    - packages/factory/rulebooks/conventions/branching-policy.md
    - packages/factory/rulebooks/conventions/finding-format.md
    - packages/factory/config/hooks/block-dangerous-git.sh
    - packages/factory/scripts/crap-score
    - packages/factory/scripts/dependency-check
    - packages/factory/scripts/test-design-verify
    - docs/proposals/core-artifact-ownership.md
    - docs/proposals/counter-ids.md

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

In manual mode, the human names a story branch, which is cut from dev, and the developer agent hands it back finished. On that branch the agent implements, gets a code review, fixes the findings, and passes the slow gates. Only then does the human review the branch and merge it into dev. The same quality gates hold as in automated mode, and a mechanism enforces them. The fast gates run as pre-commit hooks on every commit. The slow gates run in a story-close check. A hook refuses the commit that sets a story to `done` until that check has passed and no finding for the story is open. The first release covers `crap-score`, `dependency-check`, `test-design-verify`, and mutation testing.

## Motivation

In manual mode, the human commits each story, and no quality gate runs. [implementation-agent.md](../../packages/factory/agents/implementation-agent.md) says: "The gate-check loop applies to automated mode only. In manual mode, the code-review-agent replaces the mechanized gate-check loop." Only the pre-commit hooks run, with the test suite and the Factory linters.

So a function with a CRAP score of 42 against a threshold of 30 merges in manual mode, and the same function blocks the merge in automated mode. The two modes measure the code differently, although they work against the same `testing.yaml`.

The accepted proposal [core-artifact-ownership.md](core-artifact-ownership.md) closes this with an instruction: the developer agent runs the gates before it hands a story back (DEC-23 there). An instruction is not enforcement. If the agent skips it, nothing notices.

## Core Principles

- **One gate set, two modes.** Both modes run the gates that the story's `quality-gates` field or `testing.yaml` selects, with the same thresholds.
- **Enforced at a fixed point.** A gate runs where it cannot be skipped: at the commit, or at the commit that closes a story.
- **Fast on every commit, slow once per story.** A gate that takes minutes does not run on every commit.

## Design

### The manual-mode story flow

The human owns the branch. For each story, one branch is cut from dev and checked out in the primary checkout. Either the human cuts it, or the human gives the implementation agent the branch name and the agent cuts it. The agent never chooses the name or cuts a branch without one. The human checks the name in the agent's handback. Manual mode has no invocation branch, no dispatch ledger, and no worktrees. So the branching rules of the two modes stay separate: [branching-policy.md](../../packages/factory/rulebooks/conventions/branching-policy.md) states the manual-mode rule in its own section.

On that branch, the developer agent works through a fixed sequence and commits as it goes:

1. Implement the story with TDD and commit.
2. Run the code-review agent on the branch diff. Each finding becomes a file under `docs/findings/` with a `story` field.
3. Fix each open finding, commit, and get a repeat review until no finding for the story is open.
4. Run `story-gates` for the story, which runs `crap-score`, mutation testing, and `test-design-verify`.
5. Set the story's `status` to `done` in the last commit, and hand the branch back.

The story is done when step 5 succeeds, not when the developer agent stops writing code. The handback names the branch, its head commit, the findings and their resolution, and the gate results. The human then reviews the branch and merges it into dev.

### The git guardrail by mode

The git guardrail, `block-dangerous-git.sh`, runs before every shell command an agent issues. Its checks fall into two sets:

| Set               | Checks                                                                                                                                                                                                       | Applies               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------- |
| Always            | destructive and remote commands (`push`, `reset --hard`, `clean -f`, `branch -D`, `checkout .`, `restore .`); gate bypasses (`--no-verify`, `core.hooksPath`, `SKIP=`); test commands outside `testing.yaml` | in both modes         |
| Dispatch workflow | commit in a worktree needs `verify-base-ok`; branch creation only with a worktree; worktrees under `.current-work/`; merge needs `premerge-check-ok`                                                         | while a dispatch runs |

A dispatch runs while a `dispatch-ledger.yaml` exists under `.current-work/`. Manual mode has no ledger, so the implementation agent can cut the story branch in the primary checkout with `git checkout -b`. The guardrail does not check the branch name, because it cannot read the human's prompt.

### Findings name their story

A finding file gets a `story` field with the story ID, such as `story: ST-0350`. [finding-format.md](../../packages/factory/rulebooks/conventions/finding-format.md) defines the field. A review that runs outside a story leaves it empty. `story-gates` reads the field: while any finding for the story has `status: open`, `story-gates` fails and names the open findings.

The findings and the `done` status are committed on the story branch. Their IDs come from the central counter of [counter-ids.md](counter-ids.md), so a finding filed on the story branch cannot collide with one filed elsewhere (DEC-10).

Which findings must be fixed and which may stay unfixed is the subject of a separate proposal. Until it exists, every open finding for the story blocks.

### Fast gates as pre-commit hooks

Two new hooks join the Factory hook block in `packages/factory/config/pre-commit-config.yaml`:

| Hook               | Runs on             | Needs                                                                    |
| ------------------ | ------------------- | ------------------------------------------------------------------------ |
| `dependency-check` | staged source files | `docs/spec/dependency-rules.dsl`                                         |
| `crap-score`       | staged source files | a coverage file from the test run, and the threshold from `testing.yaml` |

`crap-score` reads coverage. So the `run-tests` hook writes its coverage report to a fixed path, and the `crap-score` hook runs after it and reads that file. Both hooks skip when `testing.yaml` disables their gate. The `run-tests` hook runs only when a commit touches its `files` paths. On other commits the `crap-score` hook has no fresh coverage and skips, so `story-gates` runs `crap-score` again as the check that always holds (DEC-12).

The hooks run in both modes. In automated mode they also run on the developer agent's commit, before the dispatcher's gate-check loop runs the same gates again.

### Slow gates in a story-close check

A new script, `packages/factory/scripts/story-gates`, runs the slow gates for one story: `crap-score`, mutation testing through the project's command in `gates.mutation_testing.command`, and `test-design-verify` against the story file. It also checks that no finding for the story is open. Mutation testing runs for every story, limited to the source files the story branch changes against dev (DEC-11). `story-gates` passes that file list to the mutation command, so the cost grows with the size of the diff. On a pass, it writes the marker `.current-work/story-gates/<story-id>.ok`, with the commit it checked.

A new hook, `story-done-gate`, watches staged story files. When a commit sets a story's `status` to `done`, the hook requires a marker for that story whose commit is the parent of the commit being made. Without such a marker, the hook refuses the commit and names `story-gates`.

In manual mode, the developer agent runs `story-gates` before it sets the story to `done`. In automated mode, `merge-story` sets `status: done` after the gate-check loop has passed, so the dispatcher writes the marker itself.

### Relation to the ownership proposal

This proposal replaces DEC-23's "the developer agent runs them before it hands a story back" with the two mechanisms above. The test-strategy agent of that proposal still owns the gates, their thresholds, and the mutation command.

## Scope

**In the first release:**

- The hooks `dependency-check` and `crap-score`, and the coverage report of `run-tests`.
- The script `story-gates` and its marker.
- The hook `story-done-gate`.
- The manual-mode story flow in the implementation agent and the developer agent, with commits on the story branch and the handback contents.
- The manual-mode section of the branching policy: one branch per story from dev, cut by the human or by the implementation agent under the name the human gives.
- The split of the git guardrail into checks that always apply and dispatch-workflow checks that apply while a dispatch ledger exists.
- The `story` field in finding files, and the open-findings check in `story-gates`.
- The dispatch contract states that manual mode runs the same gates.

**Explicitly deferred (do NOT plan stories for these):**

- **The rule that decides which findings must be fixed.** A separate proposal covers it for every review loop, with quantifiable measures such as a failure case and an expected cost.
- **The command that closes a whole dispatch.** It is [T-0014](../spec/work/todo.md) and concerns automated mode.
- **Gates for documents.** YAML and prose gates are a separate concern.

## Design Details

- **Bypass.** `git commit --no-verify` skips every hook. The Factory's git guardrail already blocks it for agents. A human who bypasses it does so on purpose.

## Open Questions

- **Which commit does the marker name?** The parent of the closing commit is strict: any change after `story-gates` forces a rerun. A looser rule would accept changes to the story file alone.
- **Does `story-gates` replace part of the automated gate-check loop?** The loop could call the same script, so both modes share one implementation.

## Completion Criteria

- A commit in manual mode that adds a function above the CRAP threshold fails in the `crap-score` hook.
- The time that coverage adds to the `run-tests` hook is measured and stated in `testing.yaml` before the `crap-score` hook ships.
- A commit that breaks a rule of `dependency-rules.dsl` fails in the `dependency-check` hook.
- A commit that sets a story to `done` without a matching `story-gates` marker fails in the `story-done-gate` hook and names `story-gates`.
- `story-gates <story-id>` runs `crap-score`, mutation testing, and `test-design-verify`, and writes the marker only when all three pass and no finding for the story is open.
- `story-gates <story-id>` mutates only the source files that the story branch changes against dev.
- `story-gates <story-id>` fails and names the finding when a finding with `story: <story-id>` has `status: open`.
- In manual mode, the developer agent hands back a story branch whose last commit sets the story to `done`, and the handback names the branch head, the findings, and the gate results.
- With no dispatch ledger under `.current-work/`, the guardrail allows `git checkout -b <branch> dev` in the primary checkout. With a ledger, it denies the same command.
- With or without a ledger, the guardrail denies `git push`, `git reset --hard`, and `git commit --no-verify`.
- `implementation-agent.md` does not say that the code review replaces the gates in manual mode.
- `index-lint --check` passes.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by  | Decision                                                                                                                                                                     | Raised by                                                              |
| ------ | ---------- | ---------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| DEC-01 | 2026-11-03 | decision   | stakeholder | Manual mode gets the same quality gates as automated mode: the fast gates as pre-commit hooks, the slow ones in a story-close check.                                         | project truth map, page 4                                              |
| DEC-02 | 2026-11-03 | decision   | stakeholder | The change gets its own proposal, separate from the accepted core-artifact-ownership proposal.                                                                               | process question                                                       |
| DEC-03 | 2026-11-03 | assumption | author      | A hook enforces the story-close check by requiring a marker before a story can be set to `done`, as `premerge-check-ok` does for merges.                                     | stakeholder rule: enforcement over prose                               |
| DEC-04 | 2026-11-03 | decision   | stakeholder | In manual mode, the developer agent commits on the story branch. The story is done after review, fixes, `crap-score`, and mutation testing, not when the agent stops coding. | [review-scrapbook.md](../../poc/workflow/review-scrapbook.md) FAULT-02 |
| DEC-05 | 2026-11-03 | decision   | stakeholder | The human cuts each story branch directly from dev. Manual mode has no invocation branch and no ledger, so the branching rules of the two modes stay separate.               | [review-scrapbook.md](../../poc/workflow/review-scrapbook.md) FAULT-02 |
| DEC-06 | 2026-11-03 | decision   | stakeholder | The rule that decides which findings must be fixed gets its own proposal, because it applies to every review loop.                                                           | [review-scrapbook.md](../../poc/workflow/review-scrapbook.md) BAD-04   |
| DEC-07 | 2026-11-03 | assumption | author      | A gate can find a story's findings only through a `story` field in the finding file.                                                                                         | finding files carry no story reference                                 |
| DEC-08 | 2026-11-03 | decision   | stakeholder | Refines DEC-05: the implementation agent may cut the story branch when the human names it in the prompt.                                                                     | stakeholder, after DEC-05                                              |
| DEC-09 | 2026-11-03 | decision   | stakeholder | The guardrail applies its dispatch-workflow checks only while a dispatch ledger exists. It does not check the branch name the human gave.                                    | guardrail has no mode check                                            |
| DEC-10 | 2026-11-03 | decision   | stakeholder | Indexed artifacts of a story are committed on the story branch. Unique IDs come from the counter of counter-ids.md, not from a dev-only rule.                                | indexed-artifacts question                                             |
| DEC-11 | 2026-11-03 | decision   | stakeholder | Every story runs mutation testing, limited to the files the story changes. No risk tier decides it.                                                                          | mutation-testing question                                              |
| DEC-12 | 2026-11-03 | decision   | stakeholder | `crap-score` runs both as a hook and in `story-gates`. The suite already runs per commit in about 86 seconds, so the hook adds only the coverage cost.                       | hook speed question                                                    |

## Review findings

No review has run yet.

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

No review has run yet.

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
