---
schema_version: 2
scope: global
title: Story Workflow
status: superseded
owner: agent-factory
created: 2026-11-09
updated: 2026-11-15
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

[run-lifecycle.md](run-lifecycle.md) replaces this proposal. The story workflow is one section of it.

## Primer

Agent Factory is a set of AI agents that build software from a backlog of stories. A story is one piece of work on its own branch. A developer agent writes a story's code. A code-review agent reads the change and files each problem as a finding. Then automatic checks, called gates, measure the code. One gate computes a CRAP score, short for Change Risk Anti-Patterns, which rates how risky a function is to change.

A story can run in two ways. In an orchestrated run, the implementation agent starts stories in parallel waves and merges each one itself. When a human drives by hand, the human starts one story at a time and merges it. Today the two ways follow different procedures. An orchestrated run blocks a merge that fails the gates, but it reviews no story before the feature is done. So a defect reaches the merged code, and the next wave builds on it. By hand, each story gets a review, but the gates rest on an instruction to the agent, and an instruction leaves no trace. So a function with a CRAP score of 42 against a threshold of 30 can merge by hand, while an orchestrated run blocks it.

The proposal gives both ways one story workflow. The developer agent implements the story and commits. The code-review agent reviews the branch, and the developer agent fixes findings until none is open. Then the gates run, the developer agent fixes what they report and commits, and the branch goes to the merge. The two ways differ only in how a story starts and who merges it.

Every story passes the merge, so the checks run there. A merge check script, `premerge-check`, reads the head of the story branch. It refuses the branch when no review of the story exists, when a finding for the story is open, or when a gate fails. It reruns the gates and trusts no stored result. So the function with a score of 42 now fails both ways. In an orchestrated run, the script refuses the merge. By hand, the developer agent runs the script before it hands the branch back. Its report to the human, the handback, includes the script's output, so the human sees the failure.

The code review at the end of a feature stays, because it shows how the stories fit together. The review per story catches a defect earlier: one story's change is small enough to read in full, and a defect is cheapest to fix before another story builds on it.

The developer agent commits both ways, so review and gates see committed work. Each finding names its story, so the script knows which findings belong to the branch. The test-strategy agent owns the gates and their thresholds. The script checks only that a review ran and that its findings are closed, not whether the review was good.

A separate proposal will decide which findings may stay unfixed. Until then, the developer agent fixes every open finding.

## Summary

Stories in an orchestrated run and stories driven by hand follow one workflow. So a story merged by hand passes the same review and gates as an orchestrated story. `premerge-check` checks three points at the branch head: a code review ran, no finding for the story is open, and the gates pass on a rerun. Finding files get a `story` field, and `dependency-check` becomes a pre-commit hook. The git guardrail applies its dispatch checks only while a dispatch runs, and the rule for which findings may stay unfixed is deferred.

## Motivation

Today the Factory follows two different procedures for a story. In [implementation-agent.md](../../packages/factory/agents/implementation-agent.md), an orchestrated story goes from the developer agent's commit to the gate-check step and then to the merge. A story driven by hand gets a code review, but the developer agent does not commit. The human reviews and commits each change.

The gates differ as well. In an orchestrated run, the implementation agent runs the gates, and `premerge-check` blocks the merge. By hand, an instruction from [core-artifact-ownership.md](core-artifact-ownership.md) says: "In manual mode, the developer agent runs the same gates before it hands the story back." An instruction leaves no trace. If the agent skips the gates, the human cannot see that from the branch. So a function with a CRAP score of 42 against a threshold of 30 can merge by hand, and the same function blocks the merge in an orchestrated run. This proposal replaces that instruction with the story workflow and the hooks of [Fast gates as pre-commit hooks](#fast-gates-as-pre-commit-hooks).

An orchestrated story gets no review until the end of the feature. A defect then reaches the merged code, and the next wave builds on it.

## Core Principles

- **One workflow, two ways to drive it.** Every story goes through the same steps, the same gates, and the same thresholds.
- **Review story by story.** A story's diff is small enough to read in full, and a defect is cheapest to fix before another story builds on it.
- **The agent commits.** Both ways produce commits on a story branch, so review and gates always see committed work.
- **Fast on every commit, slow once per story.** A gate that takes minutes does not run on every commit.
- **Check the result, not the order.** `premerge-check` reads the state of the branch head at the merge. It does not track which steps ran in which order.

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
2. Run the code-review agent on the story's branch diff. Each finding becomes a file under `docs/findings/` with a `story` field, as [Findings name their story](#findings-name-their-story) describes.
3. Fix each open finding, commit, and get a repeat review until no finding for the story is open.
4. Run the gates of the [gate-check step](../../packages/factory/agents/implementation-agent.md#gate-check-step), fix what they report, and commit.
5. Hand the branch over for the merge.

The story is done when step 5 succeeds, not when the developer agent stops writing code.

The gates are `dependency-check`, `test-design-verify` when the story has a Test Design or Prior Tests section, and the test guardrails that `docs/testing.yaml` enables, such as `crap-score` from [crap-gate-setup.md](crap-gate-setup.md). The story's `quality-gates` field can add a gate. The test-strategy agent owns the gates, their thresholds, and the mutation command.

### Two ways to drive it

| Point                      | Orchestrated                                                                     | By hand                                                             |
| -------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Who starts a story         | The implementation agent, wave by wave.                                          | The human, story by story.                                          |
| How stories run            | In parallel where they do not overlap.                                           | One at a time.                                                      |
| Where a story runs         | In its own worktree.                                                             | In the primary checkout.                                            |
| Where the branch starts    | The invocation branch, which the implementation agent cuts from `dev` for a run. | `dev`.                                                              |
| Run record                 | A dispatch ledger under `.current-work/`.                                        | None.                                                               |
| Sets `status: done`        | `dispatch merge-story`.                                                          | The developer agent, in the last commit of the branch.              |
| Merge                      | The implementation agent, through `dispatch merge-story`.                        | The human, after reviewing the branch.                              |
| What stops a failing story | `premerge-check` refuses the merge.                                              | The human, who sees the output of `premerge-check` in the handback. |

A human who drives by hand names the story branch. Either the human cuts it, or the implementation agent cuts it under that name. The implementation agent never chooses the name and never cuts a branch without one. The human checks the name in the handback, because the [git guardrail](#which-git-guardrail-checks-apply) cannot read the human's prompt. [branching-policy.md](../../packages/factory/rulebooks/conventions/branching-policy.md) states this rule in its own section.

The handback from the developer agent names the branch, its head commit, the findings and their resolution, and the output of `premerge-check`. The human can run `premerge-check` again before the merge.

### Findings name their story

A finding file has a `story` field with the story ID, such as `story: ST-0350`. [finding-format.md](../../packages/factory/rulebooks/conventions/finding-format.md) defines the field. A review that runs outside a story leaves it empty.

The findings and the `done` status are committed on the story branch. Their IDs come from the central counter of [counter-ids.md](counter-ids.md), so a finding filed on a story branch cannot collide with one filed elsewhere.

### Fast gates as pre-commit hooks

The Factory hook block in `packages/factory/config/pre-commit-config.yaml` holds one hook from this proposal:

| Hook               | Runs on             | Needs                            |
| ------------------ | ------------------- | -------------------------------- |
| `dependency-check` | staged source files | `docs/spec/dependency-rules.dsl` |

The hooks run both ways, and the gate-check step runs the same gates again on the story's whole diff.

### Checks at the merge

Every story passes one point, the merge, and `premerge-check` checks the branch head there. In an orchestrated run, `dispatch merge-story` runs it. The git guardrail then refuses a merge without a passing marker for the current head of the branch. By hand, the developer agent runs `premerge-check` as the last act before the handback. Besides the base, the size of the diff, and the scope, `premerge-check` checks three points:

| Step                | What `premerge-check` checks at the branch head                                                                                                                                                                                              |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Code review ran     | A code-review report on the branch has `story` set to the story's ID, and its `branch_head` is an ancestor of the branch head. Both fields are defined in [report-format.md](../../packages/factory/rulebooks/conventions/report-format.md). |
| Findings are closed | No file under `docs/findings/` has `story` set to the story's ID and `status: open`.                                                                                                                                                         |
| Gates pass          | `premerge-check` runs the gates of [step 4](#the-story-workflow) on the branch head. It reads no stored result of these gates.                                                                                                               |

`premerge-check` runs in the checkout it is called from. In an orchestrated run, that is the checkout of the implementation agent, where the story branch is not checked out. So `premerge-check` reads the code-review report and the finding files from the branch head with git, not from the folder it runs in. It reruns the gates in the story's checkout: the story's worktree in an orchestrated run, and the primary checkout by hand.

Each failed check names the story and the cause. `mutation-testing` keeps its stored result until [mutation-gate.md](mutation-gate.md) settles how it runs.

`premerge-check` checks that a review ran and that its findings are closed. It cannot judge whether the review was good. Code that changes after the last review, such as a gate fix, is not reviewed again. A gate fix is usually small, and another review would cost a full agent run.

### Which git guardrail checks apply

The git guardrail, `block-dangerous-git.sh`, runs before every shell command an agent issues. Its checks fall into two sets:

| Set               | Checks                                                                                                                                                                                                       | Applies               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------- |
| Always            | destructive and remote commands (`push`, `reset --hard`, `clean -f`, `branch -D`, `checkout .`, `restore .`); gate bypasses (`--no-verify`, `core.hooksPath`, `SKIP=`); test commands outside `testing.yaml` | both ways             |
| Dispatch workflow | commit in a worktree needs `verify-base-ok`; branch creation only with a worktree; worktrees under `.current-work/`; merge needs `premerge-check-ok`                                                         | while a dispatch runs |

A dispatch runs while a `dispatch-ledger.yaml` exists under `.current-work/`. A story driven by hand has no ledger, so the implementation agent can cut the story branch in the primary checkout with `git checkout -b`.

## Scope

**In the first release:**

- The story workflow in the implementation agent and the developer agent, as one description with two ways to drive it.
- A code review per story in orchestrated runs, before the gate-check step.
- Three checks in `premerge-check`: a code-review report for the story, no open finding for the story, and a rerun of the gates on the branch head.
- Commits by the developer agent when a human drives by hand, instead of the human committing each change.
- The handback contents.
- The section of the branching policy for stories driven by hand: one branch per story from `dev`, cut by the human or by the implementation agent under the name the human gives.
- The hook `dependency-check`.
- The split of the git guardrail into checks that always apply and dispatch-workflow checks that apply while a dispatch ledger exists.
- The `story` field in finding files.
- The dispatch contract states the story workflow and the two ways to drive it.

**Explicitly deferred (do NOT plan stories for these):**

- **The rule that decides which findings must be fixed.** A separate proposal covers it for every review loop, with quantifiable measures such as a failure case and an expected cost.
- **A limit on repeat reviews.** [review-loop-cap.md](review-loop-cap.md) owns it.
- **The command that closes a whole dispatch.** It is tracked as [T-0014](../spec/work/todo.md) and concerns orchestrated runs.
- **Gates for documents.** YAML and prose gates are a separate concern.
- **Trusted gate results.** A receipt that lets a later step skip a gate is the subject of [gate-evidence.md](gate-evidence.md).
- **The code review at the end of a feature.** It stays as it is. It sees what a review per story cannot: how the stories fit together.

## Design Details

- **Cost of the review per story.** Each orchestrated story needs one more review agent and sometimes a fix round. A large run pays this once per story.
- **Bypass.** `git commit --no-verify` skips every hook. The [git guardrail](#which-git-guardrail-checks-apply) blocks it for agents, but a human can still run it.

## Open Questions

None.

## Completion Criteria

- `implementation-agent.md` and `developer-agent.md` describe one story workflow and two ways to drive it, and neither says that the gate-check step applies to one way only.
- In an orchestrated run, each story gets a code review of its branch diff before the gate-check step, and the merge waits until no finding for the story is open.
- When a human drives by hand, the developer agent commits on the story branch, and the gates of the gate-check step run after the last review fix and before the final commit.
- When a human drives by hand, the developer agent hands back a story branch whose last commit sets the story to `done`, and the handback names the branch head, the findings with their status, and the output of `premerge-check`.
- `premerge-check` refuses a story branch with no code-review report whose `story` is the story's ID and whose `branch_head` is an ancestor of the branch head.
- `premerge-check` refuses a story branch while a finding with `story: <story-id>` has `status: open` at the branch head, and names the finding.
- `premerge-check` refuses a story branch whose head fails `dependency-check`, even when a passing result file for that gate exists under `.current-work/`.
- In an orchestrated run, `premerge-check` refuses a story branch whose head has an open finding for the story, even when no finding is open in the checkout of the implementation agent.
- When a human drives by hand, the handback contains the output of `premerge-check` for the branch head.
- A commit that breaks a rule of `dependency-rules.dsl` fails in the `dependency-check` hook.
- With no dispatch ledger under `.current-work/`, the guardrail allows `git checkout -b <branch> dev` in the primary checkout. With a ledger, it denies the same command.
- With or without a ledger, the guardrail denies `git push`, `git reset --hard`, and `git commit --no-verify`.
- `index-lint --check` passes.
