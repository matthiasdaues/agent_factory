---
title: How an implementation run earns trust
type: concept
status: implemented
order: 5
description: Follow a story through test-first development, independent review, deterministic gates, and merge.
---

# How an implementation run earns trust

Agent Factory makes AI-assisted development easier to trust by checking the work at each handover. An **implementation run** takes an approved backlog, builds its stories, and checks how they work together. Each story gathers evidence before it can merge into the feature branch. The assembled feature is then checked before it can merge into `dev`.

## One story at a time

Consider the invoice export story. When a filter matches 25 invoices and the screen shows 20, the CSV should contain all 25. The developer first writes a test that exposes the missing behavior and sees it fail. Then the developer implements the change, sees the test pass, tidies the code, and commits.

```text
Approved story
      |
      v
Developer: failing test -> implementation -> passing test -> commit
      |
      v
Independent code reviewer checks the story diff
      |-- Blocking finding -> Fresh developer fixes -> Review again
      |
      v
Dispatcher runs the applicable deterministic gates
      |-- Fails -> Fresh developer fixes if a retry remains -> Gates again
      |-- Cannot measure -> Story stops until the setup is fixed
      |
      v
Pre-merge check -> Story merges into the feature branch
```

The reviewer sees the committed diff in a separate session. A passing export test gives the reviewer evidence about the 25-invoice case. The reviewer can still find that the export bypasses an existing permissions check. A blocking finding sends the diff back for a fix and another review. This [author–reviewer loop](../concepts/author-and-reviewer.md) gives a second agent a chance to catch an assumption the author carried into the code.

## What the gates add

Once the story review has no open blocking findings, the dispatcher runs the [gates that apply](gates.md#semantic-gates) to the committed change. Each gate checks an explicit requirement. For example, `dependency-check` checks declared import rules. If the story requires named test evidence, `test-design-verify` checks that it is present.

The **Change Risk Anti-Pattern score (CRAP Score)** combines a function's complexity and test coverage. A complex function with little coverage scores higher. If the story selects the [`crap-score` gate](../scripts/crap-score.md), the script compares scores for the changed functions with the configured threshold. If the export puts filtering, formatting, and currency conversion into one complex function with weak coverage, the score can send the story back for a focused fix.

The dispatcher distinguishes a failed check from a check that could not measure. For example, if the coverage command needs a test service that is down, the story stops while someone restores the service. A gate failure with attempts left goes to a fresh developer with the report and affected files. The merge command then checks the branch and its evidence through `premerge-check`.

A [run by hand](../branches-and-dispatch/run-dispatch-by-hand.md) goes through these checks one story at a time and pauses at decision points. An [orchestrated run](../branches-and-dispatch/dispatch-runs.md) can work on independent stories in the same wave. Both use the same story workflow and gates.

## Check the assembled feature

```text
Merged stories -> Whole-feature code review -> QA -> Pre-merge check
                         |                     |           |
                         +-- blocking findings-+           v
                                     |              Stakeholder merges
                                     v                   into dev
                           Fix through story flow          |
                                     |                     v
                            Repeat the review        Reconcile docs
                              or QA check            with merged code
```

A story's tests and review see that story's change. Whole-feature review and QA see the stories together. A combined run might expose a currency mismatch that never appeared in any single story's fixture. A blocking finding goes through the story workflow and the affected feature check runs again. After the stakeholder merges, reconciliation checks that the specification and architecture still describe the code.

For the exact handovers and stop conditions, see the [implementation agent's story workflow](../../../agents/implementation-agent.md#story-workflow) and [feature checks](../../../agents/implementation-agent.md#feature-checks-and-the-merge-into-dev).
