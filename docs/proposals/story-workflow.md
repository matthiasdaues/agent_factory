---
schema_version: 2
scope: global
title: Story Workflow
status: draft
owner: agent-factory
created: 2026-11-09
updated: 2026-11-11
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/config/pre-commit-config.yaml
    - packages/factory/agents/implementation-agent.md
    - packages/factory/agents/developer-agent.md
    - packages/factory/agents/code-review-agent.md
    - packages/factory/rulebooks/conventions/dispatch-contract.md
    - packages/factory/rulebooks/conventions/branching-policy.md
    - packages/factory/rulebooks/conventions/finding-format.md
    - packages/factory/config/hooks/block-dangerous-git.sh
    - packages/factory/scripts/dependency-check
    - packages/factory/scripts/premerge-check
    - packages/factory/rulebooks/conventions/report-format.md
    - docs/spec/areas/mechanized-dispatch.md
    - docs/proposals/core-artifact-ownership.md
    - docs/proposals/counter-ids.md
    - docs/proposals/crap-gate-setup.md

governance:
  assurance: elevated
  risk_domains:
    - reliability

estimate:
  as_of: 2026-11-09
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Story Workflow

## Primer

The primer is written last, by the `write-primer` skill, once the design is settled.

## Summary

The Factory has one workflow for implementing a story. A developer agent implements the story and commits, a code review follows, the agent fixes the findings, the gates run, and the agent fixes what they report and commits. Two ways of driving this workflow exist. The implementation agent can orchestrate stories into parallel waves, or a human can start them by hand, one at a time. The two differ in how a story starts and in who merges it. Everything between those two points is the same.

## Motivation

The Factory has two different procedures today. In [implementation-agent.md](../../packages/factory/agents/implementation-agent.md), the automated path goes from the developer's commit to the gate-check loop to the merge, with no code review per story. The manual path has a code review per story, but the developer agent does not commit, and the human reviews and commits each change.

The gates differ as well. In the automated path, the implementation agent runs the gates and `premerge-check` blocks the merge. In the manual path, the instruction says: "In manual mode, the developer agent runs the same gates before it hands the story back." An instruction leaves no trace. If the agent skips the gates, the human cannot see that from the branch. So a function with a CRAP score of 42 against a threshold of 30 can merge by hand, and the same function blocks the merge in an automated run.

An orchestrated story gets no review until the end of the feature. A defect then reaches the merged code, and the next wave builds on it.

## Core Principles

- **One workflow, two ways to drive it.** Every story goes through the same steps, the same gates, and the same thresholds.
- **Review story by story.** A story's diff is small enough to read in full, and a defect is cheapest to fix before another story builds on it.
- **The agent commits.** Both paths produce commits on a story branch, so review and gates always see committed work.
- **Fast on every commit, slow once per story.** A gate that takes minutes does not run on every commit.
- **Check the result, not the order.** A script reads the state of the branch head at the merge. It does not follow which steps ran in which order.

## Design

### The story workflow

```
ORCHESTRATED                          BY HAND
implementation agent                  human starts
plans waves, starts stories           one story at a time
        \                               /
         v                             v
      +-----------------------------------+
      |  one story                        |
      |  develop, commit                  |
      |  code review, fix                 |
      |  gates, fix, commit               |
      +-----------------------------------+
         |                             |
         v                             v
   agent merges                  human reviews the branch
                                 and merges
```

Every story goes through these steps on its own branch:

1. Implement the story with TDD and commit.
2. Run the code-review agent on the story's branch diff. Each finding becomes a file under `docs/findings/` with a `story` field.
3. Fix each open finding, commit, and get a repeat review until no finding for the story is open.
4. Run the gates of the [Gate-Check Loop](../../packages/factory/agents/implementation-agent.md#gate-check-loop), fix what they report, and commit.
5. Hand the branch over for the merge.

The gates are `dependency-check`, `test-design-verify` when the story has a Test Design or Prior Tests section, and the test guardrails that `docs/testing.yaml` enables, such as `crap-score` from [crap-gate-setup.md](crap-gate-setup.md). The story's `quality-gates` field can add a gate.

### Two ways to drive it

| Point                      | Orchestrated                               | By hand                                                             |
| -------------------------- | ------------------------------------------ | ------------------------------------------------------------------- |
| Who starts a story         | The implementation agent, wave by wave.    | The human, story by story.                                          |
| How stories run            | In parallel where they do not overlap.     | One at a time.                                                      |
| Where a story runs         | In its own worktree.                       | In the primary checkout.                                            |
| Where the branch starts    | The invocation branch.                     | `dev`.                                                              |
| Run record                 | A dispatch ledger under `.current-work/`.  | None.                                                               |
| Sets `status: done`        | `dispatch merge-story`.                    | The agent, in the last commit of the branch.                        |
| Merge                      | The agent, through `dispatch merge-story`. | The human, after reviewing the branch.                              |
| What stops a failing story | `premerge-check` refuses the merge.        | The human, who sees the output of `premerge-check` in the handback. |

A human who drives by hand names the story branch. Either the human cuts it, or the implementation agent cuts it under that name. The agent never chooses the name or cuts a branch without one. The human checks the name in the handback, because the guardrail cannot read the human's prompt. [branching-policy.md](../../packages/factory/rulebooks/conventions/branching-policy.md) states this rule in its own section.

The handback names the branch, its head commit, the findings and their resolution, and the output of `premerge-check`. The agent runs `premerge-check` as the last act before the handback, and the human can run it again before the merge.

The story is done when step 5 succeeds, not when the developer agent stops writing code.

### Checks at the merge

Every story passes one point, the merge, and `premerge-check` checks the branch head there. In an orchestrated run, `dispatch merge-story` runs it, and the git guardrail refuses a merge without a passing marker for the branch's current head. By hand, the agent runs the same command before the handback. Today `premerge-check` checks the base, the size of the diff, and the scope. It gains three checks:

| Step                | What `premerge-check` checks at the branch head                                                                                                                                                                                        |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Code review ran     | A code-review report on the branch has `story` set to the story's ID, and its `branch_head` is an ancestor of the branch head. Both fields exist in [report-format.md](../../packages/factory/rulebooks/conventions/report-format.md). |
| Findings are closed | No file under `docs/findings/` has `story` set to the story's ID and `status: open`.                                                                                                                                                   |
| Gates pass          | `premerge-check` runs `dependency-check`, `test-design-verify` when the story has a Test Design or Prior Tests section, and every enabled test guardrail, on the branch head. It reads no stored result of these gates.                |

Each failed check names the story and the cause. `mutation-testing` keeps its stored result until [mutation-gate.md](mutation-gate.md) settles how it runs.

A script cannot judge whether a review was good, only that it ran and that its findings are closed. Code that changes after the last review, such as a gate fix, is not reviewed again. A gate fix is usually small, and another review would cost a full agent run.

### The git guardrail by path

The git guardrail, `block-dangerous-git.sh`, runs before every shell command an agent issues. Its checks fall into two sets:

| Set               | Checks                                                                                                                                                                                                       | Applies               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------- |
| Always            | destructive and remote commands (`push`, `reset --hard`, `clean -f`, `branch -D`, `checkout .`, `restore .`); gate bypasses (`--no-verify`, `core.hooksPath`, `SKIP=`); test commands outside `testing.yaml` | on both paths         |
| Dispatch workflow | commit in a worktree needs `verify-base-ok`; branch creation only with a worktree; worktrees under `.current-work/`; merge needs `premerge-check-ok`                                                         | while a dispatch runs |

A dispatch runs while a `dispatch-ledger.yaml` exists under `.current-work/`. A story driven by hand has no ledger, so the implementation agent can cut the story branch in the primary checkout with `git checkout -b`.

### Findings name their story

A finding file gets a `story` field with the story ID, such as `story: ST-0350`. [finding-format.md](../../packages/factory/rulebooks/conventions/finding-format.md) defines the field. A review that runs outside a story leaves it empty. The handback lists the findings of the story with their status.

The findings and the `done` status are committed on the story branch. Their IDs come from the central counter of [counter-ids.md](counter-ids.md), so a finding filed on a story branch cannot collide with one filed elsewhere.

Which findings must be fixed and which may stay unfixed is the subject of a separate proposal. Until it exists, the agent fixes every open finding for the story before step 4.

### Fast gates as pre-commit hooks

One new hook joins the Factory hook block in `packages/factory/config/pre-commit-config.yaml`:

| Hook               | Runs on             | Needs                            |
| ------------------ | ------------------- | -------------------------------- |
| `dependency-check` | staged source files | `docs/spec/dependency-rules.dsl` |

The hooks run on both paths, and the gate-check step runs the same gates again on the story's whole diff.

### Relation to the ownership proposal

The instruction in [core-artifact-ownership.md](core-artifact-ownership.md) that "the developer agent runs the same gates before it hands the story back" becomes the shared workflow and the hooks above. The test-strategy agent still owns the gates, their thresholds, and the mutation command.

## Scope

**In the first release:**

- The story workflow in the implementation agent and the developer agent, as one description with two ways to drive it.
- A code review per story in orchestrated runs, before the gate-check step.
- Three checks in `premerge-check`: a code-review report for the story, no open finding for the story, and a rerun of the gates on the branch head.
- Commits by the developer agent when a human drives by hand, which replaces the human committing each change.
- The handback contents.
- The section of the branching policy for stories driven by hand: one branch per story from dev, cut by the human or by the implementation agent under the name the human gives.
- The hook `dependency-check`.
- The split of the git guardrail into checks that always apply and dispatch-workflow checks that apply while a dispatch ledger exists.
- The `story` field in finding files.
- The dispatch contract states the story workflow and the two ways to drive it.

**Explicitly deferred (do NOT plan stories for these):**

- **The rule that decides which findings must be fixed.** A separate proposal covers it for every review loop, with quantifiable measures such as a failure case and an expected cost.
- **A limit on repeat reviews.** [review-loop-cap.md](review-loop-cap.md) owns it.
- **The command that closes a whole dispatch.** It is [T-0014](../spec/work/todo.md) and concerns orchestrated runs.
- **Gates for documents.** YAML and prose gates are a separate concern.
- **Trusted gate results.** A receipt that lets a later step skip a gate is the subject of [gate-evidence.md](gate-evidence.md).
- **The code review at the end of a feature.** It stays as it is and sees what a story-level review cannot, which is how the stories fit together.

## Design Details

- **Cost of the review per story.** Each orchestrated story needs one more review agent and sometimes a fix round. A large run pays this once per story.
- **Bypass.** `git commit --no-verify` skips every hook. The Factory's git guardrail already blocks it for agents. A human who bypasses it does so on purpose.

## Open Questions

None.

## Completion Criteria

- `implementation-agent.md` and `developer-agent.md` describe one story workflow and two ways to drive it, and neither says that the gate-check loop applies to one path only.
- In an orchestrated run, each story gets a code review of its branch diff before the gate-check step, and the merge waits until no finding for the story is open.
- When a human drives by hand, the developer agent commits on the story branch, and the gates of the Gate-Check Loop run after the last review fix and before the final commit.
- When a human drives by hand, the developer agent hands back a story branch whose last commit sets the story to `done`, and the handback names the branch head, the findings with their status, and the output of each gate.
- `premerge-check` refuses a story branch with no code-review report whose `story` is the story's ID and whose `branch_head` is an ancestor of the branch head.
- `premerge-check` refuses a story branch while a finding with `story: <story-id>` has `status: open` at the branch head, and names the finding.
- `premerge-check` refuses a story branch whose head fails `dependency-check`, even when a passing result file for that gate exists under `.current-work/`.
- When a human drives by hand, the handback contains the output of `premerge-check` for the branch head.
- A commit that breaks a rule of `dependency-rules.dsl` fails in the `dependency-check` hook.
- With no dispatch ledger under `.current-work/`, the guardrail allows `git checkout -b <branch> dev` in the primary checkout. With a ledger, it denies the same command.
- With or without a ledger, the guardrail denies `git push`, `git reset --hard`, and `git commit --no-verify`.
- `index-lint --check` passes.
