---
schema_version: 2
scope: global
title: Run Lifecycle
status: accepted
owner: agent-factory
created: 2026-11-15
updated: 2026-11-18
supersedes: docs/proposals/superseded/story-workflow.md

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
    - packages/factory/config/hooks/block-dangerous-git.json
    - packages/factory/config/extensions/block-dangerous-git.ts
    - packages/factory/config/plugins/agent-factory.ts
    - packages/factory/config/pre-commit-config.yaml
    - packages/factory/config/hook-metadata.yaml
    - docs/arc42/05_building_block_view.md
    - docs/arc42/06_runtime_view.md
    - packages/factory/
    - docs/spec/
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
    - docs/proposals/implemented/counter-ids.md
    - tests/
    - docs/spec/glossary.md

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - operations

estimate:
  as_of: 2026-11-18
  basis: decomposition
  confidence: medium
  human_review_hours:
    min: 6.0
    max: 12.0
  normalized_tokens:
    min: 200000
    max: 400000
  estimated_consumption:
    min: 3000000
    max: 6000000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Run Lifecycle

## Primer

The Agent Factory is a set of AI agents and scripts that build software from a backlog of stories. Work on one feature happens on a feature branch, cut from the dev branch. Each story gets its own story branch, cut from the feature branch. A developer agent writes the code there, and the finished story merges back into the feature branch.

Today the Factory defines how this work starts, but not how it ends. A script named dispatch writes a ledger, a file that tracks the stories, and no command ever removes it. So old ledgers pile up, and checks treat them as active runs. The work also follows two different processes. When agents drive it, a check at each merge blocks code that fails a gate. When the human drives it, there is no merge step, so failing code can merge.

The proposal calls everything the Factory does for one feature branch a run. In an orchestrated run, the implementation agent starts stories in waves, sets of stories that run in parallel. In a run by hand, stories run one at a time, each on the human's go. Both ways share the same branches, ledger, steps, checks, and end.

Take a run by hand on a feature branch named feature/login. On the human's go, the implementation agent starts a story. The developer agent writes the code test first and commits. The code-review agent reviews it and files findings that name the story. A fresh developer agent fixes the blocking findings. The implementation agent then runs the gates, automatic checks such as the dependency check. For each failure, it spawns, or starts, a fresh developer agent. The test-strategy agent sets the gates and the number of attempts. Before the merge, a merge check looks at the head of the story branch. It confirms that a review ran and no blocking finding is open, and it runs every gate again. On the human's go, the agent merges.

By hand, the implementation agent waits for the human's go before each such step. The human watches and can undo a wrong step. The git guardrail checks every shell command an agent issues. It refuses agents the two commands that destroy work: returning a story and dropping a run.

When tests fail after a merge, the usual fix is a revert commit. The proposal moves the feature branch back instead, because a revert makes git treat the story as merged, and a second attempt would bring in nothing.

After the last wave, the code-review agent reviews the whole feature, and the QA agent explores it. After the merge into dev, the reconciliation agent updates the shared documents there, so parallel runs do not conflict.

A run has an end. It is finished after the merge into dev, or the human drops it. A close command then removes the ledger, the worktrees, and the merged branches. The merge commits in dev and the status in each story file are then the only record.

## Summary

This proposal defines one lifecycle for a run, from `dispatch init` to `dispatch close`, for both ways of driving it. The two ways differ only in who starts a story, whether stories run in parallel, and who runs the commands that need a person. The first release covers the whole lifecycle, the cleanup of runs that ended before it, and one vocabulary for all Factory documents.

## Motivation

The Factory defines how a run starts, but not how it ends. `dispatch init` writes a ledger, and no command ever removes it. The ledger's `closed` field is never set. This repository holds six old ledgers, thirteen worktrees besides the primary checkout, and 36,109 files under `.current-work/`. Every check that asks whether a run is active sees those old runs as live.

Driving by hand is a different process today, not a second way to drive the same one. It has no story branches, no ledger and no merge step, so `premerge-check` cannot run there. The developer agent runs the gates by hand, and nobody reads their results. A function with a CRAP score of 42 against the default threshold of 30 can merge by hand, while an orchestrated run blocks it.

No step owns the merge of a feature branch into `dev`. One line of the branching policy says it happens.

The documents and the code disagree in many places. Three sources name three different owners for setting a story to `done`. At the cap on attempts, ADR-0012 marks the story `blocked`, and the implementation agent marks it `failed`. The spec says a red test suite after a merge reverts the merge commit, and the code moves the branch back instead. The dispatch contract lists ledger fields the code never writes. The same words name different things: "feature branch" means the branch of the run in one place and a story branch in another.

## Core Principles

- **One frame, two ways to drive it.** The two ways differ only in who acts, as [Two ways to drive it](#two-ways-to-drive-it) shows.
- **A run has an end.** A run is either finished or dropped. After `dispatch close`, nothing of the run remains except unmerged branches and named stashes, which the human handles.
- **The person watches, and the guardrail blocks what cannot be undone.** In a run driven by hand, the human sees each step and can undo a wrong one. The git guardrail refuses agents only the commands that destroy work.
- **Check the result, not the order.** `premerge-check` reads the state of the branch head at the merge. It does not track which steps ran in which order.
- **Every piece of state has a reader and a remover.** A ledger field that no command reads is removed, and the close removes the rest, as [Close](#close) describes.
- **Fast on every commit, slow once per story.** A gate that takes minutes runs in the gate-check step and again at the merge, never in a commit hook.

## Design

### Terms

| Term                 | Meaning                                                                                                                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| dispatch run         | Everything the Factory does for one feature branch, from `dispatch init` to `dispatch close`. This proposal shortens it to run. One playbook run contains the dispatch run of its feature. |
| orchestrated         | The way of driving a run in which the implementation agent starts stories in waves.                                                                                                        |
| by hand              | The way of driving a run in which the human decides when each story starts.                                                                                                                |
| feature branch       | The branch of a run, cut from `dev`.                                                                                                                                                       |
| story branch         | `story/<story-id>`, cut from the feature branch.                                                                                                                                           |
| wave                 | A set of stories that start together. By hand, each story is a wave of its own.                                                                                                            |
| gate-check step      | Running the gates on a story branch and fixing what they report.                                                                                                                           |
| spawn                | Starting one agent.                                                                                                                                                                        |
| spec-feedback report | A story's report of drift between its code and the documents, `docs/spec/work/spec-feedback-<story-id>.md`.                                                                                |
| drift session        | The spawn of an owner, or of that owner's reviewer, to settle one row of a spec-feedback report.                                                                                           |
| primary checkout     | The repository's main folder.                                                                                                                                                              |

"Dispatch" names only the script `dispatch`.

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

1. **Start.** `dispatch init --mode orchestrated|by-hand` cuts the feature branch from `dev` and writes the ledger to `.current-work/<feature-branch>/dispatch-ledger.yaml`. `--stories` names the stories of the run on both ways. In an orchestrated run, `init` also creates a worktree for the feature branch. By hand it creates none, because the run works in the primary checkout, and git cannot check out a branch that another worktree holds. One run may be active per feature branch, and several runs may be active at once. `init` refuses only in two cases. The first is a feature branch that already has a ledger. The second is a run by hand started while another run by hand is active, because both would need the primary checkout. Today `init` refuses while any ledger anywhere is active.
2. **Waves.** In an orchestrated run, `dispatch plan` writes the waves into the ledger. By hand, each story opens a wave of its own.
3. **Stories.** Each story follows the [story workflow](#the-story-workflow) on its story branch and merges into the feature branch through `dispatch merge-story`.
4. **Wave close.** After the last story of a wave stops, `dispatch close-wave` handles the spec-feedback reports of the wave, as [Wave close](#wave-close) describes. The next wave starts only after this succeeds.
5. **Feature checks.** After the last wave closes, the code-review agent reviews the whole feature and writes its report to `docs/reviews/code-review-<feature-branch>-YYYY-MM-DD.md`, with the slash of the branch name replaced by a hyphen. Then the QA agent explores the feature. Each blocking finding they file becomes a unit of work of its own, as [Findings as units of work](#findings-as-units-of-work) describes.
6. **Merge into dev.** The human merges the feature branch into `dev`, on both ways, after the [feature merge check](#checks-at-the-merge) passes.
7. **Close.** `dispatch close` removes the run's state, as [Close](#close) describes.
8. **Reconciliation.** The reconciliation agent then brings the documents in line with the code, on `dev` and outside the run. Reconciliation edits shared documents such as the scope map, the glossary and the arc42 chapters. On a feature branch, two parallel runs would edit the same files and conflict at the merge into `dev`.

### Two ways to drive it

| Point                        | Orchestrated                                | By hand                                         |
| ---------------------------- | ------------------------------------------- | ----------------------------------------------- |
| Who starts a story           | The implementation agent, wave by wave.     | The implementation agent, after the human's go. |
| How stories run              | In parallel where they do not overlap.      | One at a time.                                  |
| Where a story runs           | In its own worktree under `.current-work/`. | In the primary checkout.                        |
| Who runs the gate-check step | The implementation agent.                   | The implementation agent.                       |
| Who merges into `dev`        | The human.                                  | The human.                                      |

By hand, `dispatch prepare-story` checks out the new story branch in the primary checkout, and `dispatch merge-story` checks out the feature branch before it merges.

Both ways use the same ledger states, so a story reaches `dispatched` before it merges on either way. The `dispatch` subcommands fall to these actors:

| Subcommand                                                                                                      | Orchestrated              | By hand                                         |
| --------------------------------------------------------------------------------------------------------------- | ------------------------- | ----------------------------------------------- |
| `prepare-story`                                                                                                 | The implementation agent. | The implementation agent, after the human's go. |
| `add`                                                                                                           | The implementation agent. | The implementation agent, after the human's go. |
| `mark-dispatching`, `mark-dispatched`, `verify-story`, `escalate`, `mark-failed`, `mark-blocked`, `re-dispatch` | The implementation agent. | The implementation agent.                       |
| `refresh-story`                                                                                                 | The implementation agent. | Not used.                                       |
| `merge-story`                                                                                                   | The implementation agent. | The implementation agent, after the human's go. |
| `return-story`, `close`, `close --drop`                                                                         | The human.                | The human.                                      |

The implementation agent runs `mark-dispatching` before it spawns the developer agent, and `mark-dispatched` after that agent commits. It does so by hand too, because it still spawns the developer agent and runs the gates there. `refresh-story` brings a story branch up to a feature branch that moved while the story ran. By hand only one story runs at a time, so the feature branch does not move under it. `dispatch` drops `mark-done`, which sets `done` without a merge, because only `merge-story` sets `done`.

### Guidance by hand

In a run driven by hand, the implementation agent leads the human through the run. It stops at every point where a person decides:

- before a story starts;
- before a story merges;
- when a story stops as `failed` or `blocked`;
- before the merge into `dev`.

At each stop, it shows what the decision needs: the story and its branch head, the findings with their status, and the output of `premerge-check`. It then names the command it will run and waits. On the human's go, it runs `dispatch prepare-story` or `dispatch merge-story` itself. The human runs only three commands: `dispatch return-story` and `dispatch close --drop`, which the guardrail refuses agents, and `dispatch close`. The human runs them with `!` in Claude Code or in a terminal of their own. The merge into `dev` stays the human's, as on the orchestrated way.

A run by hand relies on the human watching, so the guardrail refuses agents only the two commands that destroy work, as [The git guardrail](#the-git-guardrail) describes.

### The story workflow

Every story goes through these steps on its story branch, on both ways:

1. The developer agent implements the story with TDD and commits.
2. The code-review agent reviews the story's branch diff. It writes its report to `docs/reviews/code-review-<story-id>-YYYY-MM-DD.md`, so two stories reviewed on the same day do not collide at the merge. A second review of the same story on the same day adds `-2` to the name, and a third adds `-3`. Each finding names the story, as [Findings name their story or run](#findings-name-their-story-or-run) describes. The developer agent commits the report and the findings on the story branch. It commits the report also when the review has no findings.
3. A fresh developer agent fixes each open blocking finding and commits. A repeat review follows until no blocking finding for the story is open. [finding-classification.md § Shared severity scale and blocking rule](../../packages/factory/rulebooks/conventions/finding-classification.md#shared-severity-scale-and-blocking-rule) defines which findings block.
4. The implementation agent runs the gate-check step: the gates of [The gates](#the-gates), with a fresh developer agent for each retry.
5. The story merges into the feature branch through `dispatch merge-story`, which sets `status: done` in the merge commit.

The developer agent commits on both ways, so review and gates always see committed work. It never runs a gate script and never sets `status: done`. The pre-commit hooks give it early feedback on every commit.

### The gates

The gates of a story are:

- `dependency-check`;
- `test-design-verify`, when the story has a Test Design or Prior Tests section;
- the test guardrails that `docs/testing.yaml` enables, such as `crap-score` from [crap-gate-setup.md](crap-gate-setup.md) and `mutation-testing` from [mutation-gate.md](mutation-gate.md);
- a security scanner, when `docs/testing.yaml` enables one.

`premerge-check` reads the gates from `docs/testing.yaml`: every entry under `gates` with `enabled: true` and a command runs. Today it knows only `crap-score` and `mutation-testing` by name and ignores any other entry, so a new gate needs a code change. After this work, a new gate needs only its entry in `docs/testing.yaml`.

A story's `quality-gates` field can only add gates. The gates the project enables always run, because a single story should not switch off a gate the project relies on. Today the field replaces the project's choice, so a story with `quality-gates: [mutation-testing]` skips `crap-score`. The test-strategy agent owns the gates, their thresholds and their commands.

The security scanner is a deterministic gate. Each project chooses whether to enable it and which scanners to run, such as Bandit or Semgrep for code and Gitleaks for leaked keys. Its setup, its key in `docs/testing.yaml`, its scanner commands and its pre-commit hook belong to a separate proposal, as [Scope](#scope) states. The OWASP review of the `security-review` skill stays in QA, at the feature level, because the flaws it finds usually lie in how stories fit together.

`mutation-testing` runs per story. If the trial in [mutation-gate.md](mutation-gate.md) shows that it is too slow per story, it moves to the feature checks without changing the rest of the run.

### Fast gates as pre-commit hooks

The Factory hook block in `packages/factory/config/pre-commit-config.yaml` gains one hook:

| Hook               | Runs                                                                              | Needs                                     |
| ------------------ | --------------------------------------------------------------------------------- | ----------------------------------------- |
| `dependency-check` | on the whole source root, when a commit stages a `.py` file under the source root | `docs/spec/dependency-rules.dsl` and `uv` |

The hook entry checks for the rules file before it calls the script. Without the file, it prints `dependency-check: no docs/spec/dependency-rules.dsl, skipped` and passes, so a project without dependency rules needs neither the script nor `uv`. `premerge-check` makes the same check before it runs the gate at the merge. Called directly, the script still exits with 2 for a missing rules file. With a rules file, the hook needs `uv`, because the script runs through `uv run --script`, as `crap-score` does. The hook watches only `.py` files, because `dependency-check` reads Python imports only.

The hook gets its entry in `packages/factory/config/hook-metadata.yaml`, which the fitting step reads to offer hooks to a project:

```yaml
  agent_factory_hook-dependency-check:
    outcome: Architecture rules
    trade_off: none
    availability: requires-path:docs/spec/dependency-rules.dsl
    description: Refuses a commit whose Python imports break a rule of dependency-rules.dsl.
```

With that `availability`, fitting leaves the hook out of a project without a rules file. The check in the hook entry still covers a project whose rules file is removed later.

### Attempts and stops

When a gate fails, the implementation agent spawns a fresh developer agent with the gate's output. A story gets `gates.attempts` attempts on its model tier, and then `gates.attempts_escalated` attempts with a stronger model. The first attempt counts, so the default of 3 means the first attempt and two retries on each tier, six attempts in all. Both values live in `docs/testing.yaml`, which is tracked and which the test-strategy agent owns. A value of 0 for `gates.attempts_escalated` turns escalation off. The same counts apply on both ways. Every story that uses up its attempts escalates. `dispatch escalate` today lets only one story per wave escalate, and that limit is dropped.

A story stops in one of two states:

| State     | Cause                                                                      |
| --------- | -------------------------------------------------------------------------- |
| `failed`  | The attempts ran out and a gate still fails.                               |
| `blocked` | A merge conflict, a refresh conflict, or a red test suite after the merge. |

The names tell the human why the story stopped. Both states wait for the human. When the root cause can be fixed, the human fixes it and tells the implementation agent to continue. The agent runs `dispatch re-dispatch`, and the story carries on in the same run. When the root cause cannot be fixed, the human returns the story to the backlog with `dispatch return-story`. Returning sets the story back to `pending`, in the ledger and in the backlog. The ledger needs no new state for this. It gains the transitions from `failed` to `pending` and from `blocked` to `pending`.

When the test suite fails after a story merges, `dispatch merge-story` moves the feature branch back to the commit before the merge, and the story is `blocked`. The feature branch is not shared yet, so nobody has built on the failed merge. A revert commit would make git treat the story's commits as merged, and a second attempt would bring in nothing.

### Dependencies in a run

The run checks the dependency tree against the backlog once, at its start. `dispatch init` refuses a story whose dependency outside the run is not done in the backlog, and names that dependency. During the run, `dispatch prepare-wave` and `dispatch prepare-story` read only the ledger. A story starts only when every story it depends on inside the run is `done`, and both commands check every such dependency.

So a returned story holds back the stories that depend on it, and through them the whole chain behind it. Take ST-0351, which depends on ST-0350, and ST-0352, which depends on ST-0351. When the human returns ST-0350, ST-0351 does not start, and so ST-0352 does not start either. Stories that depend on none of them continue. At the end of the run, the returned story and the stories that wait on it are `pending`, and they stay in the backlog.

### Findings name their story or run

A finding file has a `story` field with the story ID, such as `story: ST-0350`. [finding-format.md](../../packages/factory/rulebooks/conventions/finding-format.md) and the finding template define it. A finding filed at the feature level, by the review of the whole feature or by QA, belongs to no single story and leaves `story` empty. It names its run instead, in a field `run` with the feature branch, such as `run: feature/login`. A review outside any run leaves both fields empty. A minor finding goes to a register file under `docs/findings/register/`, which already has a required `story` field.

The `traces` field lists the spec items and stories a finding concerns. Only `story` and `run` say which review filed the finding, and only they count at the merges.

The findings are committed on the story branch. Their IDs come from the central counter of [counter-ids.md](implemented/counter-ids.md), so a finding filed on a story branch cannot collide with one filed elsewhere.

### Findings as units of work

A blocking finding from the feature checks runs like a story. `dispatch add BUG-0090` adds the open finding to the ledger, in a new wave of the same run. It runs through the [story workflow](#the-story-workflow) on the branch `story/BUG-0090`, with a regression test for the fix. `dispatch merge-story` sets `status: resolved` in the finding file in the merge commit, as it sets `done` for a story. The finding's `artifact` serves the overlap planning in place of a story's file list. A finding has no dependencies and no model tier, so it runs on the default tier.

A finding has no story file, so `dispatch` reads `backlog/<id>.md` only for a story. When a finding stops as `failed` or `blocked` and its cause cannot be fixed, `dispatch return-story BUG-0090` sets only its ledger entry to `pending`. The finding file stays `status: open`. It still carries `run: feature/login`, so it still blocks the feature merge: returning a finding does not change what it found. The human then fixes the cause and adds the finding again with `dispatch add`, waives the finding, or drops the run. `dispatch add` on an ID that the ledger holds as `pending` reuses that entry: it puts the entry into a new wave and resets its attempts to the first attempt on the default tier. The branch `story/BUG-0090` stays, so the new attempt builds on the earlier work, as `re-dispatch` does. `dispatch add` refuses an ID that the ledger holds in any other state, and names that state.

The implementation agent files a `QA` finding when the gate-check step cannot resolve something, such as a surviving mutant. At the wave close, it routes the open `QA` findings of the wave by their `owner` field. A finding with `owner: test-strategy-agent` goes to the test-strategy agent. A finding with `owner: planning-agent` needs a missing test. The implementation agent adds it as a unit of work with `dispatch add QA-0012`, so it runs in the next wave with a test that kills the mutant.

### Checks at the merge

`premerge-check` checks the branch head at every merge. For a story merge, `dispatch merge-story` runs it, on both ways. Besides the base, the size of the diff and the scope, it checks:

| Check               | What `premerge-check` checks at the story branch head                                                                                                                                                                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Code review ran     | A code-review report has `story` set to the story's ID, and its `branch_head` is an ancestor of the branch head. Both fields are defined in [report-format.md](../../packages/factory/rulebooks/conventions/report-format.md).                                                                                     |
| Findings are closed | No blocking finding with `story` set to the story's ID has `status: open`. [finding-classification.md § Shared severity scale and blocking rule](../../packages/factory/rulebooks/conventions/finding-classification.md#shared-severity-scale-and-blocking-rule) defines which findings block.                     |
| Gates pass          | `premerge-check` runs each gate of [The gates](#the-gates) with its full command on the branch head, tests included, so `crap-score` reads fresh coverage. It reads no stored result, except for `mutation-testing`, which keeps its stored result until [mutation-gate.md](mutation-gate.md) settles how it runs. |

`premerge-check` reads the ID of the unit of work from the branch name `story/<id>`, which holds a story ID or a finding ID. Today it accepts only `story/ST-NNNN` and skips the semantic gates on every other branch name, so this pattern widens. It reads the review report and the finding files from the branch head with git, not from the folder it runs in.

`premerge-check` reruns the gates in a temporary worktree at the branch head, such as `.current-work/feature/login/premerge/ST-0350`, on both ways, and removes that worktree afterwards. A fresh worktree holds exactly the branch head, so the gates measure the code that merges, and no file in the story's checkout or the primary checkout is touched. The worktree needs its own environment, so the rerun takes longer, for example while `uv` builds it on the first run. If a temporary worktree is left behind after a crash, `dispatch close` removes it with the run's other worktrees.

`dispatch merge-story` declares the story's scope to `premerge-check`. The scope includes the story's review reports, finding files and register files, and they do not count toward the file limit. A file belongs to the story when its name contains the story ID, as a review report's name does. A file also belongs to the story when its `story` field names the story, as in a finding file or a register file. Any other finding file outside the scope still blocks the merge.

For the merge into `dev`, `premerge-check dev <feature-branch>` checks:

- every story of the run is `done` or `pending`, and none is `failed` or `blocked`;
- every wave is closed;
- the code-review report of the whole feature and the Fagan, security and bug-hunt reports of the QA agent have a `branch_head` that is an ancestor of the feature branch head;
- no blocking finding is open whose `run` names the feature branch, or whose `story` names a story of the run;
- the full test suite passes on the feature branch head.

The implementation agent runs this check and shows the result. The human then merges.

### Wave close

The implementation agent drives the wave close. After the last story of a wave stops, it runs `dispatch close-wave`. The script refuses while a spec-feedback report of the wave has an `open` row, or a `fixed` row about an artifact on the core list in `rulebooks/core-artifacts.yaml`. It lists each such row with its owner. The agent spawns the owner of each listed row, and then that owner's reviewer. Their commits land on the feature branch. The agent then runs `close-wave` again, until it passes and writes a wave record into the ledger. The agent does not wait for the human's go here, because the wave close starts, merges and destroys nothing.

These drift sessions run at the wave close and not after each merge, so a story merge and a drift session never commit on the feature branch at the same time. The stories of one wave start from the same base, so none of them could use a drift fix of another.

The implementation agent then routes the open `QA` findings of the wave, as [Findings as units of work](#findings-as-units-of-work) describes.

`dispatch prepare-wave` and `dispatch prepare-story` refuse until the previous wave has a wave record. By hand, each story is a wave of its own, so the spec-feedback report of a story is handled before the next story starts.

### Close

A run ends in one of two ways:

| End      | Precondition                                                                                      | Command                 |
| -------- | ------------------------------------------------------------------------------------------------- | ----------------------- |
| Finished | The human has merged the feature branch into `dev`.                                               | `dispatch close`        |
| Dropped  | The human has decided to drop the feature, and every unfinished story is returned to the backlog. | `dispatch close --drop` |

In both cases, every story of the run is `done` or `pending`. `dispatch close` then removes:

- the ledger;
- the story worktrees and the worktree of the feature branch. Before it removes a worktree, it stashes the worktree's untracked files under a name such as `run feature/login ST-0350 2026-11-24`, and it does not put them back. Git keeps stashes in the repository, not in the folder, so they survive the removal;
- the gate results of the run's stories under `.current-work/`;
- the `premerge-check-ok` and `verify-base-ok` markers of the run;
- the briefs and scratch files under `.current-work/<feature-branch>/`;
- every merged branch of the run, with `git branch -d`.

It lists each stash it made, and the human decides what to keep. It lists each unmerged branch. Git refuses `git branch -d` for those, and the guardrail refuses agents a forced delete, so the human deletes them.

After the close, the record of the run is the merge commits in `dev` and the `done` status in each story file. The ledger holds nothing a later step reads.

`dispatch close --orphans` cleans up what no active run owns. It lists worktrees and branches that belong to no ledger, removes each worktree whose branch is merged, and lists the rest for the human. It also finds ledgers whose feature branch is gone, including ledgers nested inside a worktree. It removes such a ledger when every story in it is `done`, and lists every other one for the human. It does not read the ledger's `mode`, so it handles an old ledger with `mode: automated` like any other.

### The ledger

The ledger holds only fields that a command reads. [dispatch-contract.md](../../packages/factory/rulebooks/conventions/dispatch-contract.md) describes exactly the fields the code writes, under the names the code uses. The ledger's `mode` takes the values `orchestrated` and `by-hand`, which `dispatch` and the implementation agent read. The old value `automated` becomes `orchestrated`, and `invocation_branch` is renamed to `feature_branch`. The ledger loses `gate_results`, because the gates are rerun at the merge, and `closed`, because a ledger exists only while its run is active. The wave records stay, because `prepare-wave` and `prepare-story` read them.

After a merge, `commit_sha` holds the merge commit, and `prepare-story` reads it as the base of the next story in a serial chain. No command reads the story's own commit after the merge.

### The git guardrail

The git guardrail runs before every shell command an agent issues. It finds the run of a folder from the folder's branch: a feature branch has its ledger at `.current-work/<feature-branch>/`, and a story branch belongs to the run whose ledger lists it. A ledger of another branch never counts.

It applies one set of checks in every session:

- destructive and remote commands: `push`, `reset --hard`, `clean -f`, `branch -D`, `checkout .` and `restore .`;
- gate bypasses: `--no-verify`, `core.hooksPath` and `SKIP=`;
- test commands outside `testing.yaml`;
- a merge needs `premerge-check-ok` for the current head;
- no merge during a stop on a critical finding;
- a commit in a worktree needs `verify-base-ok`;
- a branch is created only together with a worktree, and worktrees live under `.current-work/`;
- agents may not run `dispatch return-story` or `dispatch close --drop`.

Agents may not run these two commands because both destroy work, and both are always the human's decision, in either way of driving a run. The guardrail refuses no other `dispatch` command, because the human watches a run by hand and can undo any other step. If an agent starts or merges a story too early, the human returns the story, or moves the feature branch back to undo the merge.

The guardrail must work in every agent tool the Factory supports: Claude Code, Codex, Copilot, pi and OpenCode. It relies on refusing a command, which every tool's guard supports. All five tools call one script, `config/hooks/block-dangerous-git.sh`, the way they already call `guard-human-fields`. pi's TypeScript copy, `config/extensions/block-dangerous-git.ts`, holds its own rules today and has drifted from the script. It becomes a thin wrapper that hands the command to the script and returns its answer, as `config/extensions/guard-human-fields.ts` does. OpenCode has no git guardrail today. Its plugin, `config/plugins/agent-factory.ts`, gets one that calls the same script.

### Tests run from the source

`dispatch merge-story` copies nothing into the installed copy. The Factory repository is a project like any other: its code and tests live in `packages/factory` and `tests/`, and the tests run the code from there. Today some tests run scripts from this repository's installed copy, so `merge-story` copies the merged code there first. That copy overwrites the installed copy of the checkout where the merge runs. Every session there then runs code that has not reached `dev`. The tests that read this repository's installed copy change to `packages/factory`. Tests that install the Factory into a temporary project keep using that project's `.agent-factory`.

### Documents that change

Each change follows one rule: where a document and the code disagree and no design question lies behind it, the document changes to match the code. The cases are:

- `dispatch plan` writes the waves into the ledger, and the spec says so.
- The test command comes from `docs/testing.yaml`, not from `config/project.json`.
- The ledger's branch root is the tip of the feature branch at `dispatch init`.
- After the run, the playbook order holds: code review at the end of the feature, then QA, then reconciliation. The line in the implementation agent that names reconciliation first is deleted.

These changes follow the decisions above:

- ADR-0012 allows the configured attempts with escalation and marks a story that uses them up `failed`, and the implementation agent runs the gates on both ways.
- ADR-0029 moves the drift sessions to the wave close and drops the wait in `dispatch merge-story`.
- The spec on red test suites describes moving the branch back, not a revert commit.
- The developer agent's instructions drop the gate run by hand and the `done` update.
- The rules drop the line that the human owns every gate decision by hand. They also drop the rule that the ledger records gate results and the merge commit as an audit trail, because the ledger is removed at the close and git history holds the merges.
- The branching policy describes story branches by hand, cut from the feature branch.
- The glossary gains the entry Dispatch Run, with the meaning in [Terms](#terms). Its other entries keep their words: Playbook Run is wider, and Unattended Run and Logical Run name other things.
- arc42 chapters 5 and 6 describe `premerge-check` rerunning the gates instead of reading stored results.
- The implementation agent's instructions add a `QA` finding with `owner: planning-agent` as a unit of work with `dispatch add`, in place of waiting for a story.
- Every Factory document uses the terms of [Terms](#terms) in place of these: automated mode, manual mode, mechanized dispatch, invocation branch, gate-check loop, drift report, main checkout.

## Scope

**In the first release:**

- `dispatch init --mode`, `dispatch add`, `dispatch return-story`, `dispatch close`, `dispatch close --drop` and `dispatch close --orphans`.
- `dispatch prepare-story` and `dispatch merge-story` for runs driven by hand, in the primary checkout.
- The story workflow on both ways, with a code review per story.
- The three story checks and the feature merge check in `premerge-check`.
- The configurable attempts with escalation, without the limit of one escalation per wave.
- The wave close with the drift sessions, and the refusal of the next wave until the close succeeds.
- The ledger with `mode` and without `gate_results` and `closed`.
- The refusal of `dispatch return-story` and `dispatch close --drop` in the git guardrail.
- One guardrail script for all five agent tools: pi's copy becomes a wrapper, and OpenCode gets a git guardrail.
- The guidance by hand in the implementation agent.
- The `story` field in finding files and the review report name with the story ID.
- The `dependency-check` hook.
- The vocabulary in the living Factory documents, the ledger fields and values, and the error messages of the scripts.
- The document changes listed in [Documents that change](#documents-that-change).

**Explicitly deferred (do NOT plan stories for these):**

- **The security scanner.** A separate proposal covers its setup skill, its key in `docs/testing.yaml` and its pre-commit hook, like [crap-gate-setup.md](crap-gate-setup.md). The key belongs with the skill that chooses the tools.
- **A limit on repeat reviews.** [review-loop-cap.md](review-loop-cap.md) owns it.
- **Trusted gate results.** A receipt that lets a later step skip a gate is the subject of [gate-evidence.md](gate-evidence.md).
- **Gates for documents.** YAML and prose gates are a separate concern.
- **Mutation testing at the merge.** [mutation-gate.md](mutation-gate.md) settles it, as [Checks at the merge](#checks-at-the-merge) states.

## Design Details

- **Cost.** Each story needs one more review spawn, and sometimes a retry. A slow gate runs twice per story, in the gate-check step and at the merge.
- **Bypass.** `git commit --no-verify` skips every hook. The git guardrail refuses it to agents, but a human can still run it.
- **Review coverage.** `premerge-check` can show that a review ran and that its findings are closed. It cannot judge whether the review was good. Code that changes after the last review, such as a gate fix, is not reviewed again. A gate fix is usually small, and another review would cost a full spawn.
- **Gate result files.** The gate scripts still write their results under `.current-work/<gate>/`, because the implementation agent hands a failing gate's output to the next developer agent. `dispatch close` removes these files with the run.
- **Parts for planning.** The estimate stays `unknown` until planning cuts stories. Planning can estimate and ship these parts separately: the git guardrail in five agent tools; the ledger states and the `dispatch` subcommands; `premerge-check`; the cleanup of old runs; and the vocabulary.
- **Interrupted runs.** Every `dispatch` command reads the ledger and the branch state before it acts, so a new session continues an interrupted run from where it stopped.
- **The leftovers in this repository.** All ledgers in this repository have `mode: automated`. Three of them, `brownfield-onboarding`, `core-artifact-layout` and `bug-hunt-fixes`, have no feature branch left, and one is nested inside the `counter-ids-fitting` worktree. There are also worktrees without a ledger, such as those of `data-model-dsl-poc`. A ledger whose branch still exists closes with `dispatch close`. `dispatch close --orphans` removes the ledgers of `brownfield-onboarding` and `bug-hunt-fixes`, whose stories are all `done`. It lists the `core-artifact-layout` ledger, which marks ST-0344 as `blocked`. The human returns ST-0344 to the backlog on `dev` and then removes that ledger.

## Open Questions

None.

## Completion Criteria

- `dispatch init --mode by-hand` cuts a feature branch from `dev`, creates no worktree for it, and writes a ledger with `mode: by-hand`.
- With an orchestrated run active on `feature/login`, `dispatch init` starts an orchestrated run on `feature/search`. With a run by hand active, `dispatch init --mode by-hand` refuses.
- With `dev` checked out and a ledger of another branch under `.current-work/`, the guardrail allows the commands that it refuses inside a run.
- In every session, the guardrail refuses an agent `dispatch return-story` and `dispatch close --drop`, in each of the five agent tools. For OpenCode, a real session shows this, not a mock.
- `config/extensions/block-dangerous-git.ts` holds no rule of its own. It passes each command to `config/hooks/block-dangerous-git.sh` and returns the script's answer.
- In every session, the guardrail refuses an agent `git merge <branch>` without a `premerge-check-ok` marker for the current head of that branch.
- In an orchestrated run, the implementation agent runs `dispatch merge-story` without a refusal.
- In a run driven by hand, the implementation agent stops before each step listed in [Guidance by hand](#guidance-by-hand) and waits for the human's go before it runs the command.
- In a run driven by hand, a story reaches `dispatched` through the implementation agent's `mark-dispatching` and `mark-dispatched`, and the implementation agent merges it with `dispatch merge-story` after the human's go.
- `dispatch` has no `mark-done` subcommand. Only `dispatch merge-story` sets a story to `done`, in the merge commit, and the developer agent's commits never set it.
- Two stories reviewed on the same day merge without a conflict on their review reports.
- `premerge-check` runs a gate that has an entry with `enabled: true` and a command under `gates` in `docs/testing.yaml`, although the script does not name that gate.
- With `crap-score` enabled in `docs/testing.yaml` and a second gate listed there but not enabled, a story whose `quality-gates` names the second gate runs both gates at the merge.
- `premerge-check` refuses a story branch with no code-review report whose `story` is the story's ID and whose `branch_head` is an ancestor of the branch head.
- `premerge-check` refuses a story branch while a blocking finding with `story: <story-id>` has `status: open` at the branch head, and names the finding. It refuses also when no finding is open in the folder it runs in. An open `minor` finding in the register, or an open finding file that the blocking rule does not count, does not stop the merge.
- `premerge-check` refuses a story branch whose head fails `dependency-check`, even when a passing result file for that gate exists under `.current-work/`.
- `premerge-check` passes on a branch head whose gates pass, while the primary checkout holds a changed tracked file and an untracked file, and afterwards both files are unchanged and no stash was made.
- An untracked test file in the story's checkout does not take part in the rerun, and it is back in the checkout afterwards.
- `dispatch merge-story` passes a story whose branch holds its review report and finding files, and the file limit does not count them.
- `premerge-check` runs the semantic gates on `story/BUG-0090` as on `story/ST-0350`.
- `premerge-check dev <feature-branch>` refuses while a story is `failed` or `blocked`, a wave is not closed, or the end-of-feature review or a Fagan, security or bug-hunt report of the QA agent is missing.
- `premerge-check dev feature/login` refuses while a blocking finding with `run: feature/login` is open, and ignores an open finding whose `story` and `run` name neither the branch nor a story of the run.
- With the defaults, a story whose gate still fails gets three attempts on its tier and three on the stronger tier, the first attempt included, and is then `failed`. With `gates.attempts_escalated: 0` in `docs/testing.yaml`, no attempt runs with a stronger model.
- When two stories of one wave use up their attempts, both escalate.
- When the test suite fails after a story merge, the feature branch is back at the commit before the merge, and the story is `blocked`.
- `dispatch return-story` sets a `failed` or `blocked` story to `pending`, in the ledger and in the backlog.
- `dispatch return-story BUG-0090` sets the finding's ledger entry to `pending`, leaves the finding file at `status: open`, and reads no `backlog/BUG-0090.md`. `premerge-check dev feature/login` then still refuses.
- After `dispatch return-story BUG-0090`, `dispatch add BUG-0090` puts the same ledger entry into a new wave with its attempts reset, and the next attempt runs on the existing branch `story/BUG-0090`. `dispatch add` refuses an ID that the ledger holds as `dispatched`, and names that state.
- `dispatch init` refuses a story whose dependency outside the run is not done in the backlog, and names the dependency.
- After ST-0350 is returned, `dispatch prepare-wave` and `dispatch prepare-story` refuse a story that depends on ST-0350, directly or through another story, and start a story that does not.
- `dispatch prepare-story` refuses a story whose second dependency inside the run is not `done`.
- `dispatch add BUG-0090` adds the open finding to the ledger in a new wave, and after `dispatch merge-story` the finding file has `status: resolved` in the merge commit.
- After `dispatch close-wave`, an open `QA` finding with `owner: planning-agent` is in the ledger as a unit of work of the next wave, and one with `owner: test-strategy-agent` has gone to the test-strategy agent.
- `dispatch prepare-wave 2` refuses while wave 1 has no wave record.
- `dispatch close-wave` refuses while a spec-feedback report of the wave has an `open` row, or a `fixed` row about a core-list artifact, and lists each such row with its owner.
- `dispatch close` refuses while a story is `failed` or `blocked`, and accepts a run whose stories are `done` or `pending`.
- After `dispatch close`, the run's ledger, worktrees, gate results, markers and briefs are gone, the merged branches are deleted, and the unmerged branches are listed.
- An untracked file in a story worktree is in a named stash after `dispatch close`, and the close lists that stash.
- `dispatch close --orphans` removes a worktree whose branch is merged and lists a worktree whose branch is not.
- `dispatch close --orphans` removes a ledger whose feature branch is gone and whose stories are all `done`, also when the ledger is nested inside a worktree, and lists a ledger whose branch is gone and which holds a story that is not `done`.
- After `dispatch close --orphans` in this repository, the only ledger without a branch left is the one it listed, of `core-artifact-layout`.
- A commit that breaks a rule of `dependency-rules.dsl` fails in the `dependency-check` hook.
- Fitting a project without `dependency-rules.dsl` leaves the `dependency-check` hook out of its generated configuration.
- In a project whose `dependency-rules.dsl` is removed after fitting, the installed hook passes with a notice, also when `uv` is not installed. Called directly without the file, `dependency-check` still exits with 2.
- `hook-metadata.yaml` has an entry for `agent_factory_hook-dependency-check`, and `test_every_hook_has_metadata` passes.
- The ledger has no `gate_results` and no `closed` field, has `feature_branch` in place of `invocation_branch` and `mode: orchestrated` in place of `mode: automated`, and the dispatch contract lists exactly the fields the code writes.
- `dispatch merge-story` leaves `.agent-factory/factory` unchanged, and the test suite of this repository passes without reading this repository's installed copy.
- No Markdown file under `packages/factory/` or `docs/spec/` uses the terms automated mode, manual mode, mechanized dispatch, invocation branch, gate-check loop, drift report or main checkout. Accepted ADRs, superseded proposals and file names keep their terms. No error message of `dispatch` or `premerge-check` says "invocation branch" or "main checkout".
- `index-lint --check` passes.
