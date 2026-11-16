---
schema_version: 2
scope: global
title: Run Lifecycle
status: draft
owner: agent-factory
created: 2026-11-15
updated: 2026-11-15
supersedes: docs/proposals/story-workflow.md

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/dispatch
    - packages/factory/scripts/dispatch_lib.py
    - packages/factory/scripts/premerge-check
    - packages/factory/scripts/dependency-check
    - packages/factory/scripts/finding-lint
    - packages/factory/config/hooks/block-dangerous-git.sh
    - packages/factory/config/extensions/block-dangerous-git.ts
    - packages/factory/config/plugins/agent-factory.ts
    - packages/factory/config/pre-commit-config.yaml
    - packages/factory/scripts/init-factory
    - packages/factory/agents/implementation-agent.md
    - packages/factory/agents/developer-agent.md
    - packages/factory/agents/code-review-agent.md
    - packages/factory/agents/qa-agent.md
    - packages/factory/rulebooks/rules.md
    - packages/factory/rulebooks/conventions/dispatch-contract.md
    - packages/factory/rulebooks/conventions/branching-policy.md
    - packages/factory/rulebooks/conventions/finding-format.md
    - packages/factory/rulebooks/conventions/report-format.md
    - packages/factory/rulebooks/templates/finding.md
    - packages/factory/playbooks/feature-addition.md
    - packages/factory/playbooks/greenfield-development.md
    - docs/spec/areas/mechanized-dispatch.md
    - docs/spec/validation-rules.md
    - docs/spec/interface-contracts.md
    - docs/testing.yaml
    - docs/adr/
    - docs/proposals/crap-gate-setup.md
    - docs/proposals/mutation-gate.md
    - docs/proposals/counter-ids.md

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - operations

estimate:
  as_of: 2026-11-15
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Run Lifecycle

## Primer

The primer is written by the `write-primer` skill once the design is settled.

## Summary

A run is everything the Factory does for one feature branch, from `dispatch init` to `dispatch close`. This proposal defines a run once, for both ways of driving it: orchestrated, where the implementation agent starts stories in waves, and by hand, where the human starts each story. Both ways share the same branches, ledger, story workflow, gates, merge checks and end. They differ only in who starts a story, whether stories run in parallel, and who runs the commands that need a person. The first release covers the whole lifecycle, the cleanup of runs that ended before it, and one vocabulary for all Factory documents.

## Motivation

The Factory defines how a run starts, but not how it ends. `dispatch init` writes a ledger, and no command ever removes it. The ledger's `closed` field is never set. This repository holds six old ledgers, thirteen worktrees besides the primary checkout, and 36,109 files under `.current-work/`. Every check that asks whether a run is active sees those old runs as live.

Driving by hand is a different process today, not a second way to drive the same one. It has no story branches, no ledger and no merge step, so `premerge-check` cannot run there. The developer agent runs the gates by hand, and nobody reads their results. A function with a CRAP score of 42 against a threshold of 30 can merge by hand, while an orchestrated run blocks it.

No step owns the merge of a feature branch into `dev`. One line of the branching policy says it happens.

The documents and the code disagree in many places. Three sources name three different owners for setting a story to `done`. ADR-0012 allows three fix rounds, and the implementation agent's instructions allow six. The spec says a red test suite after a merge reverts the merge commit, and the code moves the branch back instead. The dispatch contract lists ledger fields the code never writes. The same words name different things: "feature branch" means the branch of the run in one place and a story branch in another.

## Core Principles

- **One frame, two ways to drive it.** Both ways use the same branches, ledger, steps, gates and end.
- **A run has an end.** A run is either finished or dropped. After `dispatch close`, nothing of the run remains except unmerged branches that the human deletes.
- **A person decision is a command the agent cannot run.** In a run driven by hand, the git guardrail refuses agents the commands that need a person. This works in every agent tool the Factory supports.
- **Check the result, not the order.** `premerge-check` reads the state of the branch head at the merge. It does not track which steps ran in which order.
- **Every piece of state has a reader and a remover.** A ledger field that no command reads is removed. Every file a run creates is removed at its close.
- **Fast on every commit, slow once per story.** A gate that takes minutes runs in the gate-check step and again at the merge, never in a commit hook.

## Design

### Terms

| Term                 | Meaning                                                                                                     |
| -------------------- | ----------------------------------------------------------------------------------------------------------- |
| run                  | Everything the Factory does for one feature branch, from `dispatch init` to `dispatch close`.               |
| orchestrated         | The way of driving a run in which the implementation agent starts stories in waves.                         |
| by hand              | The way of driving a run in which the human starts each story.                                              |
| feature branch       | The branch of a run, cut from `dev`.                                                                        |
| story branch         | `story/<story-id>`, cut from the feature branch.                                                            |
| wave                 | A set of stories that start together. By hand, each story is a wave of its own.                             |
| gate-check step      | Running the gates on a story branch and fixing what they report.                                            |
| spawn                | Starting one agent.                                                                                         |
| spec-feedback report | A story's report of drift between its code and the documents, `docs/spec/work/spec-feedback-<story-id>.md`. |
| primary checkout     | The repository's main folder.                                                                               |

"Dispatch" names only the script `dispatch`. Every Factory document uses these terms and drops the old ones: automated, manual mode, mechanized dispatch, invocation branch, gate-check loop, drift report, main checkout.

### The run

```
dev ──► feature branch ──► story branches ──► merge into feature branch
             │                 (per story workflow)        │
         dispatch init                                 waves closed
                                                           │
                                     end-of-feature review, QA
                                                           │
                         human merges feature branch into dev
                                                           │
                                                    dispatch close
                                                           │
                                       reconciliation on dev
```

1. **Start.** `dispatch init --mode orchestrated|by-hand` cuts the feature branch from `dev` and writes the ledger to `.current-work/<feature-branch>/dispatch-ledger.yaml`. One run may be active per feature branch, and several runs may be active at once. A run by hand works in the primary checkout, so only one run by hand can be active at a time.
2. **Waves.** In an orchestrated run, `dispatch plan` writes the waves into the ledger. By hand, each story the human starts opens a wave of its own.
3. **Stories.** Each story follows the [story workflow](#the-story-workflow) on its story branch and merges into the feature branch through `dispatch merge-story`.
4. **Wave close.** After the last story of a wave stops, `dispatch close-wave` handles the spec-feedback reports of the wave, as [Wave close](#wave-close) describes. The next wave starts only after this succeeds.
5. **Feature checks.** After the last wave closes, the code-review agent reviews the whole feature and writes its report to `docs/reviews/code-review-<feature-branch>-YYYY-MM-DD.md`, with the slash of the branch name replaced by a hyphen. Then the QA agent explores the feature. Their findings are fixed as stories of a new wave in the same run.
6. **Merge into dev.** The human merges the feature branch into `dev`, on both ways, after the [feature merge check](#checks-at-the-merge) passes.
7. **Close.** `dispatch close` removes the run's state, as [Close](#close) describes.
8. **Reconciliation.** The reconciliation agent then brings the documents in line with the code, on `dev` and outside the run. Reconciliation edits shared documents such as the scope map, the glossary and the arc42 chapters. On a feature branch, two parallel runs would edit the same files and conflict at the merge into `dev`.

### The story workflow

Every story goes through these steps on its story branch, on both ways:

1. The developer agent implements the story with TDD and commits.
2. The code-review agent reviews the story's branch diff. It writes its report to `docs/reviews/code-review-<story-id>-YYYY-MM-DD.md`, so two stories reviewed on the same day do not collide at the merge. A second review of the same story on the same day adds `-2` to the name, a third `-3`. Each finding names the story, as [Findings name their story](#findings-name-their-story) describes. The developer agent commits the report and the findings on the story branch, also after a review with no findings.
3. A fresh developer agent fixes each open blocking finding and commits. A repeat review follows until no blocking finding for the story is open. [finding-classification.md § Shared severity scale and blocking rule](../../packages/factory/rulebooks/conventions/finding-classification.md#shared-severity-scale-and-blocking-rule) defines which findings block.
4. The implementation agent runs the gate-check step: the gates of [The gates](#the-gates), with a fresh developer agent for each fix round.
5. The story merges into the feature branch through `dispatch merge-story`.

The developer agent commits on both ways, so review and gates always see committed work. It never runs a gate script and never sets `status: done`. The pre-commit hooks give it early feedback on every commit.

### The gates

The gates of a story are:

- `dependency-check`;
- `test-design-verify`, when the story has a Test Design or Prior Tests section;
- the test guardrails that `docs/testing.yaml` enables, such as `crap-score` from [crap-gate-setup.md](crap-gate-setup.md) and `mutation-testing` from [mutation-gate.md](mutation-gate.md);
- a security scanner, when `docs/testing.yaml` enables one.

The story's `quality-gates` field can add a gate. The test-strategy agent owns the gates, their thresholds and their commands.

The security scanner is a deterministic gate. Each project chooses whether to enable it and which scanners to run, such as Bandit or Semgrep for code and Gitleaks for leaked keys. It runs as a pre-commit hook on every commit and again at the merge. A setup skill for it is the subject of a separate proposal. The OWASP review of the `security-review` skill stays in QA, at the feature level, because the flaws it finds usually show where stories fit together.

`mutation-testing` runs per story. If the trial in [mutation-gate.md](mutation-gate.md) shows that it is too slow per story, it moves to the feature checks without changing the rest of the run.

### Fix rounds and stops

When a gate fails, the implementation agent spawns a fresh developer agent with the gate's output. It allows `gates.fix_rounds` rounds on the story's model tier, and then `gates.fix_rounds_escalated` rounds with a stronger model. Both values live in `docs/testing.yaml`, which is tracked and which the test-strategy agent owns, and both default to 3. A value of 0 for the second turns escalation off. The same counts apply on both ways.

A story stops in one of two states:

| State     | Cause                                                                      |
| --------- | -------------------------------------------------------------------------- |
| `failed`  | The fix rounds ran out and a gate still fails.                             |
| `blocked` | A merge conflict, a refresh conflict, or a red test suite after the merge. |

The names tell the human why the story stopped. Both states wait for the human, who either has the story fixed or returns it to the backlog with `dispatch return-story`. Returning sets the story file back to `pending` on the feature branch.

When the test suite fails after a story merges, `dispatch merge-story` moves the feature branch back to the commit before the merge, and the story is `blocked`. The feature branch is not shared yet, so nobody has built on the failed merge. A revert commit would make git treat the story's commits as merged, and a second attempt would bring in nothing.

### Two ways to drive it

| Point                        | Orchestrated                                           | By hand                                   |
| ---------------------------- | ------------------------------------------------------ | ----------------------------------------- |
| Who starts a story           | The implementation agent, wave by wave.                | The human, with `dispatch prepare-story`. |
| How stories run              | In parallel where they do not overlap.                 | One at a time.                            |
| Where a story runs           | In its own worktree under `.current-work/`.            | In the primary checkout.                  |
| Who runs the gate-check step | The implementation agent.                              | The implementation agent.                 |
| Who merges a story           | The implementation agent, with `dispatch merge-story`. | The human, with `dispatch merge-story`.   |
| Who returns a story          | The human, with `dispatch return-story`.               | The human, with `dispatch return-story`.  |
| Who merges into `dev`        | The human.                                             | The human.                                |

By hand, `dispatch prepare-story` checks out the new story branch in the primary checkout, and `dispatch merge-story` checks out the feature branch before it merges.

### Guidance by hand

In a run driven by hand, the implementation agent leads the human through the run. It stops at every point where a person decides:

- before a story starts;
- before a story merges;
- when a story stops as `failed` or `blocked`;
- before the merge into `dev`.

At each stop, it shows what the decision needs: the story and its branch head, the findings with their status, and the output of `premerge-check`. It then prints the exact command. The human runs the command, with `!` in Claude Code or in a terminal of their own. The agent reads the ledger to confirm that the step happened, and then carries on.

The agent cannot run these commands itself, as [The git guardrail](#the-git-guardrail) describes. So the ledger shows that a person took each decision.

### Checks at the merge

`premerge-check` checks the branch head at every merge. For a story merge, `dispatch merge-story` runs it, on both ways. Besides the base, the size of the diff and the scope, it checks:

| Check               | What `premerge-check` checks at the story branch head                                                                                                                                                                                                                                          |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Code review ran     | A code-review report has `story` set to the story's ID, and its `branch_head` is an ancestor of the branch head. Both fields are defined in [report-format.md](../../packages/factory/rulebooks/conventions/report-format.md).                                                                 |
| Findings are closed | No blocking finding with `story` set to the story's ID has `status: open`. [finding-classification.md § Shared severity scale and blocking rule](../../packages/factory/rulebooks/conventions/finding-classification.md#shared-severity-scale-and-blocking-rule) defines which findings block. |
| Gates pass          | `premerge-check` runs each gate of [The gates](#the-gates) with its full command on the branch head, tests included, so `crap-score` reads fresh coverage. It reads no stored result.                                                                                                          |

`premerge-check` reads the story ID from the branch name `story/<story-id>`. It reads the review report and the finding files from the branch head with git, not from the folder it runs in. It reruns the gates in the story's checkout: the story's worktree in an orchestrated run, and the primary checkout by hand. Before the rerun, it refuses a checkout in which a tracked file differs from the branch head, staged or not, because the gates would then measure code that is not at the branch head. It names those files. It then stashes the untracked files of the checkout with `git stash push --include-untracked`, under a name such as `premerge ST-0350 2026-11-20`, runs the gates, and puts the files back with `git stash pop`. Files that `.gitignore` covers stay in place. If the files cannot be put back, the stash stays, and `premerge-check` names it. `mutation-testing` keeps its stored result until [mutation-gate.md](mutation-gate.md) settles how it runs.

`dispatch merge-story` declares the story's scope to `premerge-check`. The scope includes the story's review reports, finding files and register files, and they do not count toward the file limit. A file is the story's own when its name contains the story ID, as a review report's name does, or when its `story` field names the story, as a finding file's and a register file's do. Any other finding file outside the scope still blocks the merge.

For the merge into `dev`, `premerge-check dev <feature-branch>` checks:

- every story of the run is `done` or returned to the backlog;
- every wave is closed;
- the code-review report of the whole feature and the reports of the QA agent, its Fagan, security and bug-hunt reports, have a `branch_head` that is an ancestor of the feature branch head;
- no blocking finding filed by those reports is open;
- the full test suite passes on the feature branch head.

The implementation agent runs this check and shows the result. The human then merges.

`premerge-check` can show that a review ran and that its findings are closed. It cannot judge whether the review was good. Code that changes after the last review, such as a gate fix, is not reviewed again. A gate fix is usually small, and another review would cost a full spawn.

### Findings name their story

A finding file has a `story` field with the story ID, such as `story: ST-0350`. [finding-format.md](../../packages/factory/rulebooks/conventions/finding-format.md) and the finding template define it. A review outside a story leaves it empty. A minor finding goes to a register file under `docs/findings/register/`, which already has a required `story` field.

The `traces` field still lists the spec items and stories a finding concerns. Only `story` says which story's review filed the finding, and only `story` counts at the merge.

The findings are committed on the story branch. Their IDs come from the central counter of [counter-ids.md](counter-ids.md), so a finding filed on a story branch cannot collide with one filed elsewhere.

### Wave close

`dispatch close-wave` runs after the last story of a wave stops. For each spec-feedback report of the wave, it has the implementation agent spawn the owner of each row, and then that owner's reviewer. Their commits land on the feature branch. `close-wave` then refuses while a report has an `open` row, or a `fixed` row about an artifact on the core list in `rulebooks/core-artifacts.yaml`. When it succeeds, it writes a wave record into the ledger and routes the open QA findings.

The drift sessions run at the wave close and not after each merge, so a story merge and a drift session never commit on the feature branch at the same time. The stories of one wave start from the same base, so none of them could use a drift fix of another anyway.

`dispatch prepare-wave` and `dispatch prepare-story` refuse until the previous wave has a wave record. By hand, each story is a wave of its own, so the spec-feedback report of a story is handled before the next story starts.

### Close

A run ends in one of two ways:

| End      | Precondition                                                                                      | Command                 |
| -------- | ------------------------------------------------------------------------------------------------- | ----------------------- |
| Finished | The human has merged the feature branch into `dev`.                                               | `dispatch close`        |
| Dropped  | The human has decided to drop the feature, and every unfinished story is returned to the backlog. | `dispatch close --drop` |

In both cases, every story of the run is `done` or returned to the backlog. `dispatch close` then removes:

- the ledger;
- the story worktrees and the worktree of the feature branch. Before it removes a worktree, it stashes the worktree's untracked files under a name such as `run feature/login ST-0350 2026-11-24`, and it does not put them back. Git keeps stashes in the repository, not in the folder, so they survive the removal;
- the gate results of the run's stories under `.current-work/`;
- the `premerge-check-ok` and `verify-base-ok` markers of the run;
- the briefs and scratch files under `.current-work/<feature-branch>/`;
- every merged branch of the run, with `git branch -d`.

It lists each stash it made, and the human decides what to keep. It lists each unmerged branch. Git refuses `git branch -d` for those, and the guardrail refuses agents a forced delete, so the human deletes them.

After the close, the record of the run is the merge commits in `dev` and the `done` status in each story file. The ledger holds nothing a later step reads.

`dispatch close` also closes runs that ended before it existed. `dispatch close --orphans` lists worktrees and branches that belong to no ledger, removes each worktree whose branch is merged, and lists the rest for the human.

### The ledger

The ledger holds only fields that a command reads. [dispatch-contract.md](../../packages/factory/rulebooks/conventions/dispatch-contract.md) describes exactly the fields the code writes, under the names the code uses. The ledger gains `mode`, with the values `orchestrated` and `by-hand`, which the git guardrail reads. It loses `gate_results`, because the gates are rerun at the merge, and `closed`, because a ledger exists only while its run is active. The wave records stay, because `prepare-wave` and `prepare-story` read them.

After a merge, `commit_sha` holds the merge commit, and `prepare-story` reads it as the base of the next story in a serial chain. No command reads the story's own commit after the merge.

The rule that the ledger records gate results and the merge commit as an audit trail is dropped. The ledger is removed at the close, and git history holds the merges.

### The git guardrail

The git guardrail runs before every shell command an agent issues. It finds the run of a folder from the folder's branch: a feature branch has its ledger at `.current-work/<feature-branch>/`, and a story branch belongs to the run whose ledger lists it. A ledger of another branch never counts.

| Set          | Checks                                                                                                                                                                                                                                                                                                           | Applies                 |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| Always       | destructive and remote commands (`push`, `reset --hard`, `clean -f`, `branch -D`, `checkout .`, `restore .`); gate bypasses (`--no-verify`, `core.hooksPath`, `SKIP=`); test commands outside `testing.yaml`; merge needs `premerge-check-ok` for the current head; no merge during a stop on a critical finding | every session           |
| Orchestrated | commit in a worktree needs `verify-base-ok`; branch creation only with a worktree; worktrees under `.current-work/`                                                                                                                                                                                              | in an orchestrated run  |
| By hand      | agents may not run `dispatch prepare-story`, `dispatch merge-story`, `dispatch return-story` or `dispatch close --drop`                                                                                                                                                                                          | in a run driven by hand |

The guardrail must work in every agent tool the Factory supports: Claude Code, Codex, Copilot, pi and OpenCode. It relies on refusing a command, which every tool's guard supports. OpenCode has no git guardrail today and gets one in this work.

### Fast gates as pre-commit hooks

The Factory hook block in `packages/factory/config/pre-commit-config.yaml` gains two hooks:

| Hook               | Runs                                                         | Needs                                      |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------ |
| `dependency-check` | on the whole source root, when a commit stages a source file | `docs/spec/dependency-rules.dsl`           |
| security scanner   | on the staged files                                          | a scanner that `docs/testing.yaml` enables |

Without a rules file, the `dependency-check` hook prints `dependency-check: no docs/spec/dependency-rules.dsl, skipped` and passes. The gate at the merge does the same. `dependency-check` reads Python imports only. Without an enabled scanner, the security hook does nothing.

### Documents that change

The rule for each change: where a document and the code disagree and no design question lies behind it, the document changes to match the code. The cases are:

- `dispatch plan` writes the waves into the ledger, so the spec no longer says it changes no state.
- The test command comes from `docs/testing.yaml`, not from `config/project.json`.
- `dispatch merge-story` copies `packages/factory` into the installed copy when both exist, so the dispatch contract no longer calls that a manual step.
- The ledger's branch root is the tip of the feature branch at `dispatch init`.
- After the run, the playbook order holds: code review at the end of the feature, then QA, then reconciliation. The line in the implementation agent that names reconciliation first goes.

These changes follow the decisions above:

- ADR-0012 allows the configured fix rounds with escalation, and the implementation agent runs the gates on both ways.
- ADR-0029 moves the drift sessions to the wave close and drops the wait in `dispatch merge-story`.
- The spec on red test suites describes moving the branch back, not a revert commit.
- The developer agent's instructions drop the gate run by hand and the `done` update.
- The rules drop the line that the human owns every gate decision by hand, and the ledger's audit requirement.
- The branching policy describes story branches by hand, cut from the feature branch.
- arc42 chapters 5 and 6 describe `premerge-check` rerunning the gates instead of reading stored results.

## Scope

**In the first release:**

- `dispatch init --mode`, `dispatch return-story`, `dispatch close`, `dispatch close --drop` and `dispatch close --orphans`.
- `dispatch prepare-story` and `dispatch merge-story` for runs driven by hand, in the primary checkout.
- The story workflow on both ways, with a code review per story.
- The three story checks and the feature merge check in `premerge-check`.
- The configurable fix rounds with escalation.
- The wave close with the drift sessions, and the refusal of the next wave until the close succeeds.
- The ledger with `mode` and without `gate_results` and `closed`.
- The git guardrail sets by run and mode, in all five agent tools, including a git guardrail for OpenCode.
- The guidance by hand in the implementation agent.
- The `story` field in finding files and the review report name with the story ID.
- The `dependency-check` hook and the security hook.
- The vocabulary in every Factory document.
- The document changes listed in [Documents that change](#documents-that-change).

**Explicitly deferred (do NOT plan stories for these):**

- **The setup skill for the security scanner.** A separate proposal covers it, like [crap-gate-setup.md](crap-gate-setup.md).
- **A limit on repeat reviews.** [review-loop-cap.md](review-loop-cap.md) owns it.
- **Trusted gate results.** A receipt that lets a later step skip a gate is the subject of [gate-evidence.md](gate-evidence.md).
- **Gates for documents.** YAML and prose gates are a separate concern.
- **Mutation testing at the merge.** It keeps its stored result until [mutation-gate.md](mutation-gate.md) settles how it runs.

## Design Details

- **Cost.** Each story needs one more review spawn, and sometimes a fix round. A slow gate runs twice per story, in the gate-check step and at the merge.
- **Bypass.** `git commit --no-verify` skips every hook. The git guardrail refuses it to agents, but a human can still run it.
- **Interrupted runs.** Every `dispatch` command reads the ledger and the branch state before it acts, so a new session continues an interrupted run from where it stopped.
- **The leftovers in this repository.** Five ledgers of finished runs, one ledger nested inside the `counter-ids-fitting` worktree, ST-0344 marked `blocked` in the `core-artifact-layout` ledger with no branch left, and worktrees without a ledger such as those of `data-model-dsl-poc`. ST-0344 is returned to the backlog first. Then each run closes with `dispatch close`, and `dispatch close --orphans` handles the rest.

## Open Questions

None.

## Completion Criteria

- `dispatch init --mode by-hand` cuts a feature branch from `dev` and writes a ledger with `mode: by-hand`.
- With `dev` checked out and a ledger of another branch under `.current-work/`, the guardrail allows the commands that it refuses inside a run.
- In a run driven by hand, the guardrail refuses an agent `dispatch merge-story`, `dispatch prepare-story`, `dispatch return-story` and `dispatch close --drop`, in each of the five agent tools.
- In an orchestrated run, the implementation agent runs `dispatch merge-story` without a refusal.
- In every session, the guardrail refuses an agent `git merge <branch>` without a `premerge-check-ok` marker for the current head of that branch.
- `dispatch merge-story` sets `status: done` in the merge commit, and the developer agent's commits never set it.
- `premerge-check` refuses a story branch with no code-review report whose `story` is the story's ID and whose `branch_head` is an ancestor of the branch head.
- `premerge-check` refuses a story branch while a blocking finding with `story: <story-id>` has `status: open` at the branch head, and names the finding. An open `minor` finding in the register, or an open finding file that the blocking rule does not count, does not stop the merge.
- In an orchestrated run, `premerge-check` refuses a story branch whose head has an open blocking finding for the story, even when no finding is open in the folder it runs in.
- `premerge-check` refuses a story branch whose head fails `dependency-check`, even when a passing result file for that gate exists under `.current-work/`.
- `premerge-check` refuses to rerun the gates while a tracked file in the checkout differs from the branch head, staged or not, and names the file.
- An untracked test file in the story's checkout does not take part in the rerun, and it is back in the checkout afterwards.
- `premerge-check dev <feature-branch>` refuses while a story is `failed` or `blocked`, a wave is not closed, the end-of-feature review or the QA report is missing, or one of their blocking findings is open.
- `dispatch merge-story` passes a story whose branch holds its review report and finding files, and the file limit does not count them.
- Two stories reviewed on the same day merge without a conflict on their review reports.
- A story whose gate still fails after the configured fix rounds is `failed`. With `gates.fix_rounds_escalated: 0` in `docs/testing.yaml`, no round runs with a stronger model.
- When the test suite fails after a story merge, the feature branch is back at the commit before the merge, and the story is `blocked`.
- `dispatch prepare-wave 2` refuses while wave 1 has no wave record.
- `dispatch close-wave` refuses while a spec-feedback report of the wave has an `open` row, or a `fixed` row about a core-list artifact.
- `dispatch close` refuses while a story is `failed` or `blocked`.
- After `dispatch close`, the run's ledger, worktrees, gate results, markers and briefs are gone, the merged branches are deleted, and the unmerged branches are listed.
- An untracked file in a story worktree is in a named stash after `dispatch close`, and the close lists that stash.
- `dispatch close --orphans` removes a worktree whose branch is merged and lists a worktree whose branch is not.
- A commit that breaks a rule of `dependency-rules.dsl` fails in the `dependency-check` hook. In a project without that file, the hook passes with a notice.
- The ledger has no `gate_results` and no `closed` field, and the dispatch contract lists exactly the fields the code writes.
- No Factory document uses the terms automated mode, manual mode, mechanized dispatch, invocation branch, gate-check loop or drift report.
- `index-lint --check` passes.
