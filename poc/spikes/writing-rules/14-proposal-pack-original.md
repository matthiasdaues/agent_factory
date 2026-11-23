---
schema_version: 2
title: Run Lifecycle
status: draft
owner: stakeholder
created: 2026-11-17
updated: 2026-11-17
supersedes: docs/proposals/superseded/story-workflow.md

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/dispatch
    - packages/factory/scripts/dispatch_lib.py
    - packages/factory/scripts/premerge-check
    - packages/factory/scripts/verify-base
    - packages/factory/scripts/crap-score
    - packages/factory/scripts/mutation-testing
    - packages/factory/scripts/test-design-verify
    - packages/factory/scripts/dependency-check
    - packages/factory/config/hooks/block-dangerous-git.sh
    - packages/factory/config/hooks/block-dangerous-git.json
    - packages/factory/config/hooks/guard-human-fields
    - packages/factory/config/extensions/block-dangerous-git.ts
    - packages/factory/config/plugins/agent-factory.ts
    - packages/factory/agents/implementation-agent.md
    - packages/factory/agents/developer-agent.md
    - packages/factory/agents/code-review-agent.md
    - packages/factory/agents/qa-agent.md
    - packages/factory/playbooks/feature-addition.md
    - packages/factory/rulebooks/rules.md
    - packages/factory/rulebooks/conventions/dispatch-contract.md
    - packages/factory/rulebooks/conventions/branching-policy.md
    - packages/factory/rulebooks/conventions/finding-format.md
    - packages/factory/rulebooks/conventions/report-format.md
    - docs/adr/0012-dispatcher-owned-semantic-gate-loop.md
    - docs/adr/0029-per-story-drift-reports-block-the-wave-close.md
    - docs/spec/areas/mechanized-dispatch.md
    - docs/spec/glossary.md
    - docs/spec/state-machines.md
    - docs/spec/interface-contracts.md
    - docs/testing.yaml
    - docs/proposals/superseded/story-workflow.md
    - docs/proposals/crap-gate-setup.md

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - operations

estimate:
  as_of: 2026-11-17
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Run Lifecycle

## Primer

Not written in this test.

## Summary

This proposal defines one lifecycle for a run, from `dispatch init` to `dispatch close`, for both ways of driving it. The two ways differ only in who decides when a story starts, whether stories run in parallel, and who runs the commands that destroy work. The first release covers the whole lifecycle, the cleanup of runs that ended before it, and one vocabulary for the Factory's living documents and code.

## Motivation

The Factory defines how the work on a feature starts, but not how it ends. `dispatch init` writes a ledger, and no command removes it. The ledger has a `closed` field, and no code sets it to true. So every check that asks "is a run active?" sees old runs as live.

This repository shows the result. `.current-work/` holds about 556 MB in 36,109 files. Six ledgers remain from features that have merged. Thirteen worktrees besides the primary checkout still exist. One ledger sits one level too deep, inside a worktree, because `init` wrote it to the worktree's top folder.

The two ways of driving the work are two different processes today. When agents drive it, `premerge-check` blocks a story that fails a gate. When a human drives it, there are no story branches, no ledger and no merge step. So `premerge-check` cannot run, and the gate results written by hand have no reader.

The documents and the code disagree in about fifteen places. Some examples:

- Three sources name three different owners for setting a story to `done`.
- ADR-0012 marks a story `blocked` when its fix rounds run out. The implementation agent marks it `failed`.
- ADR-0012 says the developer agent never runs a gate script. The developer agent's instructions tell it to run the gates by hand.
- The spec says a red test suite after a merge reverts the merge commit. The code moves the branch back with a hard reset.
- The dispatch contract lists ledger fields that the code never writes.

The terms drift as well. "Feature branch" means the invocation branch in one place and the story branch in another. "Dispatch" means a whole run in one place and a single agent start in another.

The story workflow, [story-workflow.md](../../proposals/story-workflow.md), ran into these gaps. It is a part of the dispatch process, so this proposal defines the whole process and takes the story workflow in as one section.

## Core Principles

- Both ways share one frame. It has a feature branch, a ledger, story branches cut from the feature branch, a merge of each story through `premerge-check`, and a defined end.
- A run ends either finished or dropped. After the close, only unmerged branches and named stashes remain, and the human handles both.
- Every piece of state has a command that reads it. State without a reader is not written.
- No stored result decides a merge. The merge check measures the code that merges.
- Every mechanism works in all five agent tools: Claude Code, Codex, GitHub Copilot CLI, pi and OpenCode.
- A run by hand relies on the person watching. The guardrail refuses agents only the commands that destroy work.
- Where a document and the code disagree and no design question lies behind it, the document follows the code.

## Design

### Terms

The proposal, the living documents and the code use these terms.

| Term                 | Meaning                                                                        | Old terms in use                                       |
| -------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------ |
| run                  | everything from `dispatch init` to `dispatch close` for one feature branch     | dispatch (for the whole), invocation                   |
| orchestrated         | the way in which the implementation agent starts stories in parallel waves     | automated mode, mechanized dispatch, dispatch workflow |
| by hand              | the way in which the human decides when each story starts, one story at a time | manual mode, human-driven                              |
| feature branch       | the branch of a run, cut from `dev`                                            | invocation branch                                      |
| story branch         | `story/<id>`, cut from the feature branch                                      | "feature branch" where it meant the story branch       |
| gate-check step      | running the gates on a story branch and fixing what they report                | gate-check loop, semantic gate loop                    |
| spawn                | starting one agent                                                             | "dispatch" where it meant one agent start              |
| spec-feedback report | a story's report of drift between the code and the documents                   | drift report                                           |
| primary checkout     | the repository's main folder                                                   | main checkout                                          |

The word "dispatch" names only the script `dispatch`. The ledger's mode values are `orchestrated` and `by-hand`.

A run carries units of work. A unit of work is a backlog story or a blocking finding from the end of the feature, as [Feature checks](#feature-checks) describes. The story workflow treats both the same way.

### The run

The examples in this proposal use an invented feature, `feature/login`, with the invented stories ST-0901 to ST-0905. A run passes through seven steps:

1. **Start.** The implementation agent runs `dispatch init --base dev --feature-branch feature/login --stories <ids>`. `init` checks the dependencies of the listed stories, as [Dependencies and returned stories](#dependencies-and-returned-stories) describes. It creates the feature branch from `dev` and writes the ledger. The branch root is the tip of the feature branch at `init`.
2. **Plan.** `dispatch plan` groups the stories into waves and writes the waves into the ledger.
3. **Waves.** Each unit of work in a wave passes through [the story workflow](#the-story-workflow) and merges into the feature branch.
4. **Wave close.** `dispatch close-wave` closes each wave, as [Wave close](#wave-close) describes. The next wave starts only after the previous wave is closed.
5. **Feature checks.** After the last wave closes, the code-review agent reviews the whole feature, and the QA agent explores it. Their blocking findings run as units of work in new waves.
6. **Merge into `dev`.** The implementation agent runs the feature merge check. When it passes, the human merges the feature branch into `dev` with `git merge`.
7. **Close.** `dispatch close` removes everything the run left behind.

After the run, the reconciliation agent brings the spec and the architecture back in line with the code. It runs on `dev`, one feature at a time, outside any run. Reconciliation edits shared documents such as the glossary and the arc42 chapters. Two parallel runs would conflict in those files, so reconciliation waits for the merge.

`init` creates the feature branch differently on the two ways. In an orchestrated run, the feature branch gets its own worktree under `.current-work/feature/login/`. By hand, the run works in the primary checkout, and `init` creates no worktree. Git refuses to check out a branch that another worktree holds, so a worktree would block the primary checkout.

Several runs may be active at once, one per feature branch. A run is active while its feature branch has a ledger. Every check that asks whether a run is active reads only the ledger of the branch it works on. `init` refuses in two cases: the feature branch already has a ledger, or a run by hand starts while another run by hand is active. Two runs by hand would both need the primary checkout.

### Two ways to drive it

The two ways run the same steps, checks and commands. They differ in three points:

| Point                           | Orchestrated                                    | By hand                                                      |
| ------------------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| Who decides when a story starts | the implementation agent                        | the human; the implementation agent runs the command         |
| Parallel stories                | yes, in waves; each story in its own worktree   | no; each story is a wave of its own, in the primary checkout |
| Who decides a merge             | the implementation agent, after the checks pass | the human; the implementation agent runs the command         |

The human merges the feature branch into `dev` on both ways. The human also runs the commands that destroy work: `dispatch return-story` and `dispatch close --drop`.

Each `dispatch` subcommand has one place on each way:

| Subcommand                                | Orchestrated                          | By hand                                               |
| ----------------------------------------- | ------------------------------------- | ----------------------------------------------------- |
| `init`, `plan`                            | implementation agent                  | implementation agent, after the human's go            |
| `prepare-wave`                            | implementation agent                  | not used                                              |
| `prepare-story`                           | implementation agent                  | implementation agent, after the human's go            |
| `mark-dispatching`, `mark-dispatched`     | implementation agent                  | implementation agent                                  |
| `verify-story`                            | implementation agent                  | implementation agent                                  |
| `mark-failed`, `mark-blocked`, `escalate` | implementation agent                  | implementation agent                                  |
| `re-dispatch`                             | implementation agent                  | implementation agent, after the human fixed the cause |
| `refresh-story`                           | implementation agent                  | not used                                              |
| `merge-story`                             | implementation agent                  | implementation agent, after the human's go            |
| `close-wave`                              | implementation agent                  | implementation agent, after each story                |
| `add`                                     | implementation agent                  | implementation agent                                  |
| `return-story`                            | human                                 | human                                                 |
| `close`, `close --orphans`                | see [Open Questions](#open-questions) | human                                                 |
| `close --drop`                            | human                                 | human                                                 |

`refresh-story` merges a moved feature branch into a story branch. By hand, only one story runs at a time, so the feature branch does not move under it. `dispatch` has no `mark-done`. Only the merge sets `done`, and `merge-story` does its own transition. `status`, `clear-manifest` and `suggest-merge-args` keep their behavior.

By hand, story branch and feature branch share the primary checkout. So `prepare-story` checks out the story branch, and `merge-story` checks out the feature branch before it merges.

### Guidance by hand

The human who drives by hand needs thorough guidance. So the implementation agent stops at each point where a person decides:

- before a story starts;
- before a story merges;
- when a story stops, as [Attempts and stops](#attempts-and-stops) describes;
- before the merge into `dev`.

At each stop, the agent shows the `premerge-check` output, the findings of the unit with their status, and the head of the branch. It names the exact command it will run next and waits. On the human's go, it runs that command.

For the commands that only the human runs, the agent prints the exact command instead. The human runs it with `!` in Claude Code or in a terminal. The agent then reads the ledger to confirm that the step happened and continues.

Before the merge into `dev`, the agent runs the feature merge check and shows its result. The human runs `git merge`.

The guardrail does not stop an agent from starting or merging a story by hand. The human watches each step, and a wrong merge can be undone. The guardrail refuses only the commands that cannot be undone, as [The git guardrail](#the-git-guardrail) describes.

### The story workflow

Every unit of work passes through the same steps on its story branch, on both ways:

1. **Development.** A developer agent writes the code test first and commits on the story branch with the unit's ID in the subject. The pre-commit hooks give it early feedback, as [Pre-commit hooks](#pre-commit-hooks) describes.
2. **Code review.** The code-review agent reviews the diff of the story branch. It writes its report and files findings that name the unit, as [Findings name their unit](#findings-name-their-unit) describes.
3. **Review fixes.** A fresh developer agent fixes every open blocking finding of the unit and commits. A finding blocks under the rule in [finding-classification.md § Shared severity scale and blocking rule](../../../packages/factory/rulebooks/conventions/finding-classification.md#shared-severity-scale-and-blocking-rule). A `minor` finding goes into a register file and never blocks.
4. **Gate-check step.** The implementation agent runs the gates, as [The gates](#the-gates) describes. For each failure, it spawns a fresh developer agent with the gate reports and the affected files.
5. **Merge.** `dispatch merge-story` runs the merge check, merges the story branch into the feature branch and sets `status: done` in the merge commit. For a finding, it sets `status: resolved` instead.

The developer agent never sets `done` and never runs a gate script. `done` means one thing: merged into the feature branch.

### The gates

The implementation agent runs the gates on both ways and counts the attempts. By hand, it runs them in the primary checkout on the story branch and reports to the human after each story. A script result does not depend on who starts the script, but the counting and the stop do. So one agent owns the gate-check step on both ways.

The gates on a story branch are:

- `dependency-check`, after every unit;
- `test-design-verify`, when the story has a Test Design or Prior Tests section;
- `crap-score` and `mutation-testing`, picked by the story's `quality-gates` field or by the `gates` section of `docs/testing.yaml`;
- a deterministic security scanner, once a project enables one in `docs/testing.yaml`.

The security scan is a step of the story workflow. Each project decides whether to enable a scanner and which tools to run. The setup skill that picks the tools and defines the scanner's key in `docs/testing.yaml` is deferred, as [Scope](#scope) lists. `premerge-check` reruns every gate that `docs/testing.yaml` enables, so a scanner added later runs at the merge without a change to this design. The OWASP review stays in QA at the feature level, because it needs judgment and finds flaws that show when stories fit together.

Mutation testing runs per story. If the trial planned in [mutation-gate.md](../../proposals/mutation-gate.md) shows that it is too slow per story, it moves to the feature level. The rest of the frame stays as it is.

#### Pre-commit hooks

The pre-commit hooks run on every commit and give the developer agent early feedback. They do not replace the gate-check step.

`dependency-check` runs as a hook when a commit stages a source file. It reads the allowed dependencies from `docs/spec/dependency-rules.dsl`. A project writes that file in its architecture phase, so a new project has none. Without the file, the hook prints `dependency-check: no docs/spec/dependency-rules.dsl, skipped` and passes. The gate at the merge does the same.

### Attempts and stops

Each tier gets three attempts by default: the first attempt and two retries. The story's `tier` field names its first tier. When the three attempts on that tier fail, the story escalates to a stronger model and gets three more attempts. Six attempts is the maximum with the default counts. Each retry is a fresh developer agent that receives only the gate reports and the affected files.

The counts live in `docs/testing.yaml`:

<!-- yaml-excerpt -->

```yaml
gates:
  attempts: 3
  attempts_escalated: 3
```

`gates.attempts` counts the attempts on the story's tier, the first attempt included. `gates.attempts_escalated` counts the attempts on the stronger tier. A value of `0` for `gates.attempts_escalated` turns escalation off. The test-strategy agent owns the file and sets these counts next to the gate thresholds.

`dispatch escalate` lets every story that runs out of attempts escalate, also when another story of the same wave has escalated. Its other conditions stay. For example, a story already at the `strong` tier does not escalate.

A unit stops in one of two states:

- `failed`: the gates could not be fixed within the attempts.
- `blocked`: the merge hit a conflict, or the tests failed after the merge.

Both states keep their names, because the name tells the human why the unit stopped. Both are handled the same way. The unit waits for the human, and the human chooses one of two paths:

- **Fix and continue.** The human fixes the root cause, for example a merge conflict in one file, and tells the agent to continue. The agent runs `dispatch re-dispatch`, and the unit runs again in the same run.
- **Return.** The root cause cannot be fixed in this run. The human runs `dispatch return-story`, and the unit goes back to `pending`.

When the tests fail after a merge, `merge-story` moves the feature branch back to the commit before the merge and blocks the story. The feature branch is local, so no one has built on the failed merge. A revert commit would cause trouble later. Git would treat the story's commits as merged, so a second merge of the story would bring in nothing.

### Dependencies and returned stories

The run checks the dependency tree against the backlog once, at its start. During the run, it reads only the ledger. Nothing in the middle of a run needs to know where stories live, so a different backlog source changes only the check at the start.

- `dispatch init` refuses a story whose dependency outside the run is not done in the backlog. It names that dependency. The human either finishes the dependency first or leaves the story out of the run.
- During the run, a story starts only when every dependency inside the run is `done` in the ledger. `prepare-wave` and `prepare-story` both check every dependency, not only the first.

`dispatch return-story` sets the unit back to `pending`, in the ledger and in the backlog. The ledger has the transitions `failed` to `pending` and `blocked` to `pending`, and no new state.

A story that depends on a returned story does not start. Stories that do not depend on it continue. The rule carries through a chain without an extra rule. Take ST-0902, which depends on ST-0901, and ST-0903, which depends on ST-0902. The human returns ST-0901. ST-0902 never starts and stays `pending`, so ST-0903 waits as well. ST-0904 depends on neither, so it runs and merges.

At the end of the run, a returned story and the stories that wait on it are `pending`. The feature merge check and `dispatch close` accept `done` and `pending` and refuse `failed` and `blocked`. So a feature can merge into `dev` with some stories still `pending`, and those stories stay in the backlog.

### Findings name their unit

Each finding names the work it belongs to, so the merge checks can find it:

- A finding about one unit of work carries the unit's ID in the field `story`, for example `story: ST-0901`. Register files for `minor` findings require this field already.
- A finding filed at the feature level carries the feature branch in the field `run`, for example `run: feature/login`.

A code-review report carries the reviewed work in its name:

- A story review goes to `docs/reviews/code-review-<id>-YYYY-MM-DD.md`, for example `docs/reviews/code-review-ST-0901-2026-11-20.md`.
- The review at the end of the feature goes to `docs/reviews/code-review-<feature-branch>-YYYY-MM-DD.md`, with the slash in the branch name replaced by a hyphen, for example `code-review-feature-login-2026-11-24.md`.
- A second review of the same work on the same day adds `-2`, a third adds `-3`.

The name keeps two stories that are reviewed on the same day from adding a file at the same path. The scope rule in [Checks at the merge](#checks-at-the-merge) also relies on the ID in the name.

### Checks at the merge

`premerge-check` runs before every merge. `dispatch merge-story` calls it for a story merge. The implementation agent calls it with `premerge-check dev <feature-branch>` for the merge into `dev`.

#### The story merge

Before a story branch merges, `premerge-check` checks the head of the story branch:

| Check               | Passes when                                                                                                     |
| ------------------- | --------------------------------------------------------------------------------------------------------------- |
| Clean checkout      | no tracked file differs from the branch head, staged or not; the check names each changed file                  |
| Review exists       | a code-review report whose name contains the unit's ID exists on the branch                                     |
| No blocking finding | no open blocking finding names the unit in its `story` field                                                    |
| Gates pass          | every gate passes in a fresh run of its full command, tests included; `mutation-testing` uses its stored result |
| Scope               | every changed file is inside the unit's scope                                                                   |

The rerun measures the files in the checkout, and the merge takes the commits of the branch. A changed tracked file would make the two differ, so the check refuses it. A change to a tracked file belongs in a commit.

An untracked file can make the two differ as well. Take a fix agent that writes `tests/test_login.py` and does not commit it. The tests would find and run the file, and the merge would take a branch head without it. So `premerge-check` puts the untracked files of the checkout into a stash before the rerun, under a name such as `premerge ST-0901 2026-11-20`. It runs the gates and then puts the files back with `git stash pop`. If the files cannot be put back, the stash stays, and the output names it. `git stash push --include-untracked` leaves files that `.gitignore` covers in place, such as coverage output.

The rerun runs each gate's full command, so `crap-score` measures fresh coverage. Coverage is a build artifact. It is not tracked, it lies in whichever folder the tests last ran in, and nothing marks it as out of date after a new commit. So the rerun produces it from the code at the branch head.

The scope of a unit is its declared outputs, its backlog file, its spec-feedback report and `INDEX.yaml`. It also holds the unit's own review reports, finding files and register files. A file counts as the unit's own when its name contains the unit's ID, or when its `story` field names the unit. These files do not count toward the limit on changed files. Any other finding file is outside the scope and blocks the merge.

`premerge-check` reads the unit's ID from the branch name. It accepts `story/<id>` for a story ID such as `ST-0901` and for a finding ID such as `BUG-0901`. A branch that matches neither form does not pass the semantic gates.

#### The merge into `dev`

Before the human merges the feature branch into `dev`, `premerge-check dev <feature-branch>` checks:

- Every unit in the ledger is `done` or `pending`. None is `failed`, `blocked` or still running.
- Every wave is closed.
- The review at the end of the feature ran, and the QA agent ran its Fagan, security and bug-hunt reviews.
- No open blocking finding carries `run: <feature-branch>` or names a unit of the run in its `story` field.
- The full test suite passes.

Take `feature/login`. QA files the invented BUG-0901 against the login form, with `run: feature/login`. An open finding from an unrelated earlier review also sits in `docs/findings/`, without a `run` or `story` that belongs to this run. The check counts BUG-0901 and ignores the other finding.

### Wave close

A wave closes after every unit in it has stopped as `done`, `failed` or `blocked`. The close handles the spec-feedback reports of the wave. For each `open` row, the implementation agent spawns the row's owner, such as the domain-modeling agent. The owner fixes the document and sets the row to `fixed`. The agent then spawns the owner's reviewer, who sets the row to `confirmed` or `rejected`. These spawns are the drift sessions of the wave. `dispatch close-wave` records the wave as closed only after the drift sessions have committed and no row is `open`.

The drift sessions run at the close of the wave, not after each merge. So a story merge and a drift session never commit on the feature branch at the same time. All units of a wave start from the same base, so none of them could use a fix from another unit's drift session. The next wave starts only after the close, so it sees the fixed documents.

`dispatch prepare-wave` for the next wave refuses until the ledger records the previous wave as closed. By hand, each story is a wave of its own, so the rows are handled right after each story.

After `close-wave`, the implementation agent routes the open `QA` findings of the wave. A `QA` finding reports a missing or weak test. [Open Questions](#open-questions) holds the routing rule.

### Feature checks

After the last wave closes, two reviews look at the whole feature on the feature branch:

1. The code-review agent reviews how the stories fit together. Its report carries the feature branch in its name.
2. The QA agent explores the whole feature with its Fagan, security and bug-hunt reviews.

Each blocking finding from these reviews becomes a unit of work. A finding already holds what the run needs. Its body says what is wrong. Its `artifact` field says where, and the overlap planning reads it in place of a story's file list. Its `status: resolved` says when it is finished. A finding has no dependencies, and a fix inside the run needs none.

- `dispatch add BUG-0901` adds the open finding to the ledger as a unit of a new wave. It runs the same dependency check as `init`.
- The finding runs through [the story workflow](#the-story-workflow) on the branch `story/BUG-0901`: a fix with a regression test, a review, the gates and the merge check.
- `merge-story` sets `status: resolved` in the finding file in the merge commit. The feature merge check then no longer counts the finding as open.

The run handles units of work without asking where they were written. No planning agent writes a second document for the fix.

### Close

A run has two ends. It is finished after the human merges the feature branch into `dev`. It is dropped when the human decides to stop the feature.

`dispatch close` removes everything the run left behind:

- the ledger;
- the worktree of the feature branch and the worktrees of the story branches;
- the gate results under `.current-work/`;
- the `verify-base-ok` and `premerge-check-ok` markers;
- the briefs and scratch files under `.current-work/<feature-branch>/`.

It deletes the merged branches with `git branch -d`, which git allows only for a fully merged branch. Before it removes a worktree, it puts the worktree's untracked files into a stash, under a name such as `run feature/login ST-0901 2026-11-24`. It does not put them back. A stash lives in the repository, not in the folder, so it survives the removal of the worktree.

At the end, `close` lists the stashes it made and every unmerged branch. The human decides what to keep and deletes unmerged branches with `git branch -D`. No tracked record of the run remains. The merge commits in `dev` and the status of each story in the backlog hold the outcome.

`close` refuses while a unit is `failed` or `blocked`, because that unit still waits for a decision.

To drop a run, the human returns every unfinished unit to the backlog with `dispatch return-story` and then runs `dispatch close --drop`. `--drop` closes a run whose feature branch is not merged into `dev`.

`dispatch close --orphans` handles what no run owns:

- It lists worktrees and branches that no ledger names. It removes such a worktree when its branch is merged, and it leaves the unmerged ones for the human.
- It finds ledgers whose feature branch no longer exists, nested ledgers included. It removes such a ledger when every story in it is `done`. It lists every other such ledger and leaves it in place.
- It does not read the ledger's `mode`.

### The ledger

Each run has one ledger at `.current-work/<feature-branch>/dispatch-ledger.yaml`. Only `dispatch` subcommands write it. The ledger exists while the run is active, and `dispatch close` deletes it.

Every ledger field has a command that reads it:

- `mode` holds `orchestrated` or `by-hand`. `dispatch` and the implementation agent read it. The guardrail does not.
- `feature_branch` names the feature branch.
- `branch_root` and `branch_head` hold the tip of the feature branch at `init` and after the last merge or wave close.
- `stories` maps each unit's ID to its record: status, wave, dependencies, branch, worktree, `base_sha`, tier, reason, attempts, escalation, `verify_base` and `commit_sha`.
- `waves` holds one closeout record per closed wave. `prepare-wave` reads it to check that the previous wave is closed.

After a merge, `commit_sha` holds the merge commit. `prepare-story` reads it as the base of the next link in a serial chain. The scope check reads the unit's own commit before the merge, and an interrupted merge resumes from the branch tip. So no command needs the unit's own commit after the merge.

The ledger has no `gate_results` and no `closed` field. The gates run again at the merge, and the existence of the ledger says that the run is active.

### The git guardrail

The git guardrail is one script, [block-dangerous-git.sh](../../../packages/factory/config/hooks/block-dangerous-git.sh), and all five agent tools call it. It works the way `guard-human-fields` works already:

- Claude Code, Codex and Copilot call the shell script through their hook configuration.
- pi's [block-dangerous-git.ts](../../../packages/factory/config/extensions/block-dangerous-git.ts) is a thin wrapper that hands the command to the script, like `guard-human-fields.ts`.
- OpenCode's plugin, [agent-factory.ts](../../../packages/factory/config/plugins/agent-factory.ts), calls the same script.

The guardrail applies one list of checks in every session. The list holds the checks the shell script applies today. Three of them are the worktree rules: no branch creation without a worktree, worktrees only under `.current-work/`, and a `verify-base-ok` marker for a commit in a linked worktree.

One check is new. In every session, the guardrail refuses agents `dispatch return-story` and `dispatch close --drop`. Both destroy work, and both are always the human's decision.

The guardrail reads command text. An agent that hides a command, for example by building it from variables, can get past it. `guard-human-fields` has the same limit. These guards stop mistakes, not a determined attempt to get around them. A mechanism outside the agent's shell would close that gap, and none works in all five tools.

### Documents and code that change

The living documents and the code follow this design.

- [dispatch-contract.md](../../../packages/factory/rulebooks/conventions/dispatch-contract.md) describes exactly the ledger fields that the code writes, under the code's names. Its Completed Close and Abandoned Close sections describe `dispatch close` and `dispatch close --drop`. The story status rule says that `merge-story` sets `done` in the merge commit.
- [rules.md](../../../packages/factory/rulebooks/rules.md) drops the requirement that the ledger records gate results and merge commits. The ledger is removed at the close, and git history holds the merges. The rule that the human owns gate decisions by hand changes to the human owning the person decisions.
- [implementation-agent.md](../../../packages/factory/agents/implementation-agent.md) describes one workflow for both ways, with the stops of [Guidance by hand](#guidance-by-hand). Its handoff line follows the playbook order.
- [developer-agent.md](../../../packages/factory/agents/developer-agent.md) never sets `done` and never runs a gate script. It commits on the story branch on both ways.
- [code-review-agent.md](../../../packages/factory/agents/code-review-agent.md) names its reports as [Findings name their unit](#findings-name-their-unit) describes.
- [feature-addition.md](../../../packages/factory/playbooks/feature-addition.md) orders the work as the run, the review at the end of the feature, QA, the merge into `dev`, and then reconciliation on `dev`.
- [branching-policy.md](../../../packages/factory/rulebooks/conventions/branching-policy.md) cuts story branches from the feature branch on both ways. The branch root is the tip of the feature branch at `init`.
- [ADR-0012](../../adr/0012-dispatcher-owned-semantic-gate-loop.md) states the attempt counts of [Attempts and stops](#attempts-and-stops) and the `failed` state at the cap.
- [ADR-0029](../../adr/0029-per-story-drift-reports-block-the-wave-close.md) states that the drift sessions run at the wave close and that `merge-story` does not wait for them.
- [mechanized-dispatch.md](../../spec/areas/mechanized-dispatch.md) says that `plan` writes the waves into the ledger, that the test command comes from `docs/testing.yaml`, and that a red suite moves the feature branch back.
- `merge-story` copies `packages/factory` into `.agent-factory/factory`, and the dispatch contract says so.
- [crap-gate-setup.md](../../proposals/crap-gate-setup.md) links to this proposal in place of [story-workflow.md](../../proposals/story-workflow.md).

The vocabulary of [Terms](#terms) applies to the Markdown under `packages/factory/` and `docs/spec/`. It also applies to code identifiers and error messages: the ledger key `invocation_branch` becomes `feature_branch`, the mode value `"automated"` becomes `"orchestrated"`, and error messages say "feature branch". Accepted ADRs keep the words they were decided in, apart from the changes this list names. Superseded proposals and file names keep their old terms.

## Scope

**In the first release:**

- One lifecycle for both ways, with the subcommand placement of [Two ways to drive it](#two-ways-to-drive-it).
- `dispatch init` without a worktree by hand, with the refusal per feature branch and the dependency check at the start.
- The dependency check on every in-run dependency in `prepare-wave` and `prepare-story`.
- The story workflow on both ways, with the gate-check step run by the implementation agent.
- `gates.attempts` and `gates.attempts_escalated` in `docs/testing.yaml`, and `escalate` without the limit of one escalation per wave.
- `dispatch return-story`, with the transitions `failed` to `pending` and `blocked` to `pending`.
- The `story` and `run` fields on findings, and the review report names.
- The story merge check and the feature merge check of [Checks at the merge](#checks-at-the-merge), including the stash of untracked files and the branch pattern for finding IDs.
- Mutation testing at the merge with its stored result, as [Checks at the merge](#checks-at-the-merge) states.
- The wave close with drift sessions, and the refusal of `prepare-wave` until the previous wave is closed.
- `dispatch add` for blocking findings from the feature checks.
- `dispatch close`, `--drop` and `--orphans`, including the stash of untracked files.
- The ledger as [The ledger](#the-ledger) describes it, without `gate_results`, `closed` and `mark-done`.
- One guardrail script for all five agent tools, with the refusal of `dispatch return-story` and `dispatch close --drop`.
- The `dependency-check` hook and gate that pass with a notice when the rules file is missing.
- The vocabulary in the living documents, code identifiers and error messages.
- The changes in [Documents and code that change](#documents-and-code-that-change).
- The cleanup of the old runs in this repository with `dispatch close` and `dispatch close --orphans`.

**Explicitly deferred (do NOT plan stories for these):**

- The security scanner's setup skill, its key in `docs/testing.yaml`, its pre-commit hook and its gate. They belong to a separate setup proposal, like [crap-gate-setup.md](../../proposals/crap-gate-setup.md), because the key belongs with the skill that chooses the tools.
- Moving mutation testing to the feature level. It waits for the trial in [mutation-gate.md](../../proposals/mutation-gate.md).
- A backlog source other than Markdown story files, such as Jira. It belongs to [jira-backlog-projection.md](../../proposals/jira-backlog-projection.md). This proposal only states that `init` checks the backlog and that a return reaches the backlog.
- Limits on repeat reviews. They belong to [review-loop-cap.md](../../proposals/review-loop-cap.md).
- A tracked record of each run. Git history and the backlog hold the outcome, and no reader needs more.
- A one-time migration script for old runs. `dispatch close` and `--orphans` handle them, and the human sees each one before anything is removed.

## Design Details

- **Stash names.** At the rerun: `premerge <unit-id> <date>`. At the close: `run <feature-branch> <unit-id> <date>`. The date is the day of the stash in `YYYY-MM-DD`.
- **Returning a Markdown story.** With today's backlog, `return-story` sets `status: pending` in the story file on the feature branch. The file reaches `dev` with the feature merge.
- **Retry after a fix.** `re-dispatch` moves a `failed` or `blocked` unit back to `prepared`. The guardrail lets the agent run it, because a retry destroys no work.
- **Review coverage.** `premerge-check` can show that a review ran. It cannot judge the quality of the review.
- **Bypass.** The human merges into `dev` outside the agent's tools, so no hook sees that merge. The feature merge check runs only because the implementation agent runs it at the stop before that merge.
- **The old runs in this repository.** Six ledgers remain. `finding-classification` and `counter-ids` still have their feature branches, and `dispatch close` closes them. `brownfield-onboarding` and `bug-hunt-fixes` have no branch left, and all their stories are `done`, so `--orphans` removes their ledgers. `core-artifact-layout` has no branch and lists ST-0344 as `blocked`. `--orphans` lists it. The human returns ST-0344 to the backlog on `dev` and then removes that ledger. The sixth ledger is nested inside the `counter-ids-fitting` worktree, and `--orphans` finds it.
- **Worktrees without a ledger in this repository.** `data-model-dsl-poc` with six story worktrees, `agent-cli-devcontainer`, `core-artifact-ownership` and `plan/reconciliation-backfeed` have no ledger. `--orphans` lists them and removes those whose branch is merged. The stray branch `feature/my-work` is listed for the human.

## Open Questions

01. **Routing of `QA` findings at the wave close.** Today the implementation agent routes an open `QA` finding by its owner: `owner: test-strategy-agent` gets a spawn, and `owner: planning-agent` waits for a story that adds the test. An earlier draft sent every `QA` finding to the test-strategy agent. Case: a `QA` finding with `owner: planning-agent` reports a missing test for ST-0902. Under the owner rule, it waits. Under the other rule, the test-strategy agent receives work that belongs to a story. The answer settles [Wave close](#wave-close) and a change line for implementation-agent.md.
02. **The story's `quality-gates` field.** In `premerge-check` today, the field replaces the pick from `docs/testing.yaml` and accepts only `crap-score` and `mutation-testing`. Case: ST-0901 lists `quality-gates: [crap-score]`, and `docs/testing.yaml` enables mutation testing. If the field replaces the pick, mutation testing does not run for ST-0901. If it adds to the pick, both run. The answer settles [The gates](#the-gates).
03. **The copy into the installed folder with several runs.** `merge-story` copies `packages/factory` into `.agent-factory/factory`. With two runs active, every session, also on `dev`, then uses the scripts and guardrail of the run that merged last. Case: run A merges a story that breaks `block-dangerous-git.sh`, and the agents of run B lose the guardrail. This happens only in the Factory repository itself. The answer settles a line of [Documents and code that change](#documents-and-code-that-change).
04. **The stash in the primary checkout.** By hand, the stash at the rerun takes the human's own untracked files as well, such as draft proposals and handoffs. If `git stash pop` fails, those files stay in the stash. The answer decides whether the rerun by hand stashes all untracked files, only files in paths the unit touches, or none. It settles [The story merge](#the-story-merge).
05. **How the wave close runs.** A script cannot spawn an agent. So the implementation agent spawns the drift sessions, and `close-wave` checks the rows. Open points: whether the agent runs `close-wave` once before the spawns and once after, and what the first run prints. The answer settles [Wave close](#wave-close).
06. **The term "run" in the glossary.** [glossary.md](../../spec/glossary.md) already uses "playbook run" in a wider sense. The answer decides whether the glossary gets a separate entry for "run" in this proposal's sense, or whether the proposal picks another word.
07. **The `dependency-check` hook in other projects.** The script starts with `#!/usr/bin/env -S uv run --script`, so a project without `uv` fails the hook. The script reads Python imports only, and "a commit stages a source file" has no definition yet. The answer settles [Pre-commit hooks](#pre-commit-hooks).
08. **Gate result files.** After this change, only `mutation-testing` keeps a reader for its result file under `.current-work/<gate>/`. The other gate scripts still write their files on every run. The answer decides whether those scripts stop writing them, under the principle that state without a reader is not written.
09. **Who runs the finished close in an orchestrated run.** By hand, the human runs `dispatch close`. In an orchestrated run, the sources name no owner for the close after the human's merge into `dev`. The answer settles a row of the subcommand table.
10. **Unmerged branches at a dropped close.** `close` lists unmerged branches for the human to delete with `git branch -D`. The sources leave open whether `dispatch close --drop` deletes them itself, since only the human runs it. The answer settles [Close](#close).
11. **The merge into `dev` and the guardrail.** The guardrail lets an agent run `git merge` once a `premerge-check-ok` marker exists. `premerge-check dev <feature-branch>` writes that marker when it passes. In an orchestrated run, nobody watches, so an agent could merge into `dev` itself. The answer decides whether the guardrail refuses agents a merge into `dev`. It settles [The git guardrail](#the-git-guardrail).
12. **The tier of a finding.** A finding added with `dispatch add` has no `tier` field. The answer names the tier its developer agents use. It settles [Feature checks](#feature-checks).
13. **Which spawns count as attempts.** The review fixes in step 3 of the story workflow also spawn developer agents. The answer decides whether those spawns count toward `gates.attempts`, or only the first attempt and the gate retries. It settles [Attempts and stops](#attempts-and-stops).
14. **The first story by hand.** By hand, the agent starts each story with `prepare-story`, which takes its base from the previous link of a serial chain. The answer names the base of the first story in a run by hand, and whether `prepare-wave` has a role there. It settles the subcommand table.
15. **How ADR-0012 and ADR-0029 change.** Accepted ADRs keep the words they were decided in, and both ADRs change in substance. The answer decides whether each ADR is edited in place or replaced by a new ADR. It settles [Documents and code that change](#documents-and-code-that-change).

## Completion Criteria

- In a run by hand on a test repository, `dispatch init` creates the feature branch without a worktree, and the run works in the primary checkout.
- `dispatch init` for a second feature branch succeeds while an orchestrated run is active on another branch. `init` refuses for a feature branch that already has a ledger, and for a second run by hand while one is active.
- `dispatch init` refuses a story whose dependency outside the run is not done in the backlog, and names the dependency.
- `prepare-story` and `prepare-wave` refuse a story while any of its in-run dependencies is not `done`, the second dependency included.
- By hand, a story reaches `dispatched` and merges through `dispatch merge-story`, with the implementation agent running every ledger command.
- By hand, the implementation agent stops before a story starts, before it merges, when it stops and before the merge into `dev`. At each stop it shows the `premerge-check` output, the findings with their status and the branch head, and it names the command.
- `dispatch merge-story` sets `status: done` in the merge commit for a story and `status: resolved` for a finding. The developer agent's instructions contain no step that sets `done` or runs a gate script.
- After a red test suite following a merge, the feature branch points at the commit before the merge, and the story is `blocked`.
- With the default counts, a story whose gates never pass receives six developer spawns, three on its tier and three on the stronger tier, and then becomes `failed`. Two stories of one wave that both run out of attempts both escalate.
- With `gates.attempts_escalated: 0`, the story becomes `failed` after its attempts on its own tier.
- `dispatch return-story` moves a `failed` or `blocked` unit to `pending` in the ledger and in its story file. A story that depends on it does not start, and an independent story starts.
- `premerge-check` refuses a story branch whose checkout has a changed tracked file, and names the file.
- An untracked test file in the checkout does not take part in the rerun, and it is back in the checkout afterwards.
- `premerge-check` refuses a story branch without a review report that contains the unit's ID, and refuses it while an open blocking finding names the unit. An open `minor` finding in a register file does not block.
- A fresh `crap-score` run at the merge refuses a function that the last fix commit added without a test, although the stored coverage predates that commit.
- A review report, finding file or register file of the unit does not trip the scope check and does not count toward the file limit. A finding file of another unit trips the scope check.
- `premerge-check` runs the semantic gates on `story/BUG-0901` as it does on `story/ST-0901`.
- `dispatch prepare-wave 2` refuses until `dispatch close-wave 1` has succeeded. `close-wave` refuses while a row of a spec-feedback report of the wave is `open`.
- `dispatch add BUG-0901` adds the finding to the ledger as a unit of a new wave.
- `premerge-check dev feature/login` counts an open blocking finding with `run: feature/login` and ignores an open finding that names neither the run nor a unit of the run.
- `premerge-check dev <feature-branch>` refuses while a unit is `failed` or `blocked`, or while a wave is not closed. It refuses while the end-of-feature review report or one of the QA agent's Fagan, security and bug-hunt reports is missing. It accepts `pending` units.
- After `dispatch close`, the run's ledger, worktrees, gate results, markers, briefs and merged branches are gone. An untracked file from a story worktree is in a named stash, and the close output lists that stash and every unmerged branch.
- `dispatch close` refuses while a unit is `failed` or `blocked`.
- `dispatch close --orphans` in this repository removes the ledgers of `brownfield-onboarding` and `bug-hunt-fixes` and the nested ledger whose stories are all `done`. It lists the ledger of `core-artifact-layout` and leaves it. Afterwards, no ledger without a branch remains except those it listed.
- The ledger has no `gate_results` and no `closed` field, its mode values are `orchestrated` and `by-hand`, and `dispatch` has no `mark-done` subcommand.
- The dispatch contract lists exactly the ledger fields that `dispatch_lib.py` writes, under the same names.
- In Claude Code, Codex, Copilot, pi and OpenCode, an agent's `dispatch return-story` and `dispatch close --drop` are refused.
- pi's `block-dangerous-git.ts` contains no check of its own and hands every command to `block-dangerous-git.sh`.
- In a real OpenCode session, not a mock, the plugin calls `block-dangerous-git.sh`, and the guardrail refuses `git branch -D`.
- In a project without `docs/spec/dependency-rules.dsl`, a commit that stages a Python file passes the `dependency-check` hook with the notice `dependency-check: no docs/spec/dependency-rules.dsl, skipped`.
- No Markdown file under `packages/factory/` or `docs/spec/`, apart from accepted ADRs, uses the terms automated mode, manual mode, mechanized dispatch, invocation branch, gate-check loop, drift report or main checkout. The code under `packages/factory/scripts/` has no `invocation_branch` key and no `"automated"` mode value.

## Guiding Rule

A run has one frame on both ways, and it ends with nothing left behind except what the human must decide about.

# Appendix

## Decisions

| ID  | Date | Kind | Decided by | Decision | Raised by |
| --- | ---- | ---- | ---------- | -------- | --------- |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
