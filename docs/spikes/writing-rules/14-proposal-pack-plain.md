---
schema_version: 2
title: Run Lifecycle
status: draft
owner: stakeholder
created: 2026-11-17
updated: 2026-11-17
supersedes: docs/proposals/story-workflow.md

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
    - packages/factory/scripts/init-factory
    - packages/factory/config/hooks/block-dangerous-git.sh
    - packages/factory/config/hooks/block-dangerous-git.json
    - packages/factory/config/hooks/guard-human-fields
    - packages/factory/config/extensions/block-dangerous-git.ts
    - packages/factory/config/extensions/guard-human-fields.ts
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
    - docs/adr/0012-dispatcher-owned-semantic-gate-loop.md
    - docs/adr/0029-per-story-drift-reports-block-the-wave-close.md
    - docs/spec/areas/mechanized-dispatch.md
    - docs/spec/interface-contracts.md
    - docs/spec/state-machines.md
    - docs/spec/glossary.md
    - docs/testing.yaml
    - docs/proposals/crap-gate-setup.md

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - data_integrity
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

This proposal defines one lifecycle for a run, from `dispatch init` to `dispatch close`, for both ways of driving it. The two ways differ only in whether stories run in parallel and in which commands the human runs. The first release covers the whole lifecycle with its checks, a close command that also clears the runs that ended before it, one git guardrail script for all five agent tools, and one vocabulary for the living Factory documents.

## Motivation

The Factory knows how a run starts but not how it ends. `dispatch init` writes a ledger, a file that tracks the stories of the run, and no command ever removes it. The ledger field `closed` exists, but no code sets it to true. So every check that asks "is a run active?" sees old runs as live.

This repository shows the result. It holds six ledgers of finished features, 13 worktrees besides the primary checkout, and 36,109 files under `.current-work/`. One ledger sits one level too deep, inside the `counter-ids-fitting` worktree. ST-0344 is `blocked` in the `core-artifact-layout` ledger, although its branch is gone.

Nobody owns the last merge. Only one line in the branching policy says that the feature branch merges into `dev`. No agent step makes that merge, and `premerge-check` skips its story checks for every branch that is not named `story/ST-NNNN`.

Driving by hand is a second process today, not a second way to drive the same one. It has no story branches, no ledger and no merge step. So `premerge-check` never runs there, and the gate results written by hand have no reader.

The documents and the code also disagree in about fifteen places. These are the ones that need a design decision:

- Three sources name three owners for setting a story to `done`.
- ADR-0012 marks a story `blocked` when its gate attempts run out, and the implementation agent marks it `failed`.
- ADR-0012 says the developer agent never runs a gate script, and the developer agent's instructions tell it to run the gates by hand.
- The spec reverts the merge commit after a red test suite, and the code moves the branch back.
- ADR-0029 makes a wave wait for the close of the previous wave, and the code waits only for its stories to stop.
- The dispatch contract lists ledger fields that the code never writes.

The terms drift as well. "Feature branch" means the branch of the run in one place and the story branch in another. "Dispatch" means a whole run in one place and one agent start in another.

The story workflow proposal answers some of these questions for single stories. Its open questions are questions about the whole process, so this proposal replaces it and contains the story workflow as one section.

## Core Principles

- Both ways of driving a run share one frame: a feature branch, a ledger, story branches cut from the feature branch, a merge check at each story merge, and a defined end.
- A script judges and an agent acts. Every check that decides a merge is a script that reruns its measurement; no stored result decides a merge, with the one exception named in [Checks at the story merge](#checks-at-the-story-merge).
- Every piece of state has a reader. A ledger field without a command that reads it is removed.
- A run ends. After the close, nothing of the run remains except unmerged branches and named stashes, and the human decides about both.
- A mechanism must work in all five agent tools: Claude Code, Codex, GitHub Copilot CLI, pi and OpenCode. A mechanism that only one tool offers is not used.
- By hand, the human watches each step and can undo a wrong one. The guardrail refuses only the commands that destroy work.

## Design

### Terms

This proposal and the living Factory documents use only these terms.

| Term                 | Meaning                                                                                      | Replaces                                         |
| -------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| run                  | everything from `dispatch init` to `dispatch close` for one feature branch                   | dispatch (for the whole), invocation             |
| orchestrated         | the way of driving a run in which the implementation agent starts stories in waves           | automated mode, mechanized dispatch              |
| by hand              | the way of driving a run in which the human decides each step and one story runs at a time   | manual mode, human-driven                        |
| feature branch       | the branch of a run, cut from `dev`                                                          | invocation branch                                |
| story branch         | `story/<unit-id>`, cut from the feature branch                                               | "feature branch" where it meant the story branch |
| unit of work         | a story or a blocking finding that the run implements on its own story branch                | none                                             |
| wave                 | the units of work that start from the same base and close together                           | none                                             |
| gate-check step      | running the gates and fixing what they report                                                | gate-check loop, semantic gate loop              |
| spawn                | starting one agent                                                                           | "dispatch" where it meant one agent start        |
| spec-feedback report | a story's report of drift between code and documents, `docs/spec/work/spec-feedback-<id>.md` | drift report                                     |
| primary checkout     | the repository's main folder, as opposed to a linked worktree                                | main checkout                                    |

The word "dispatch" names only the script `dispatch`. The ledger's mode values are `orchestrated` and `by-hand`. A drift session is one spawn of a row's owner or reviewer that handles a row of a spec-feedback report.

### The run

A run has five phases. Each phase names the command that starts it.

1. **Start.** `dispatch init --base dev --feature-branch feature/<name> --stories <ids>` creates the feature branch from `dev` and writes the ledger to `.current-work/<feature-branch>/dispatch-ledger.yaml`. The ledger records the mode and sets the branch root to the tip of the feature branch. `init` checks the dependency tree against the backlog once. It refuses a story whose dependency outside the run is not done in the backlog, and it names that dependency. `--stories` is required on both ways.
2. **Waves.** The implementation agent plans the waves with `dispatch plan`, which writes the wave numbers into the ledger. Each unit of work runs through [the story workflow](#the-story-workflow) and merges into the feature branch through `dispatch merge-story`. Wave N+1 starts only after `dispatch close-wave N` succeeds ([Wave close](#wave-close)).
3. **Feature steps.** After the last wave closes, the code-review agent reviews the whole feature, and then the QA agent explores it. Each blocking finding from these two steps becomes a unit of work in a new wave ([Feature steps](#feature-steps-and-the-merge-into-dev)).
4. **Merge into `dev`.** The implementation agent runs `premerge-check dev <feature-branch>` and shows the result. The human runs `git merge`.
5. **Close.** The human runs `dispatch close`, which removes the state of the run ([Close](#close)).

Reconciliation is not part of the run. It edits shared documents such as the scope map, the glossary and the arc42 chapters, so two parallel runs would conflict there. The reconciliation agent runs on `dev` after the merge, one feature at a time.

Several runs may be active at once, one per feature branch. Every check that asks whether a run is active reads only the ledger of the feature branch it works on. `init` refuses when the same feature branch already has a ledger. It also refuses a run by hand while another run by hand is active, because both need the primary checkout.

### Two ways to drive it

| Point                   | Orchestrated                                    | By hand                                                                        |
| ----------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------ |
| Where stories run       | each in its own worktree under `.current-work/` | in the primary checkout                                                        |
| Units of work at once   | as many as dependencies and file overlap allow  | one; each unit is a wave of its own                                            |
| Feature branch worktree | `init` creates one                              | none; `init` creates the branch only                                           |
| Who decides a step      | the implementation agent                        | the human, at each [person decision](#guidance-by-hand)                        |
| Who runs the commands   | the implementation agent                        | the implementation agent after the human's go, except the human commands below |

By hand, `dispatch prepare-story` checks out the story branch in the primary checkout. `dispatch merge-story` switches back to the feature branch before it merges.

Each `dispatch` subcommand has one place:

| Subcommand                                                                                                      | Orchestrated         | By hand                                                        |
| --------------------------------------------------------------------------------------------------------------- | -------------------- | -------------------------------------------------------------- |
| `init`, `plan`                                                                                                  | implementation agent | implementation agent                                           |
| `prepare-wave`                                                                                                  | implementation agent | not used                                                       |
| `prepare-story`                                                                                                 | implementation agent | implementation agent, after the go                             |
| `mark-dispatching`, `mark-dispatched`, `verify-story`, `escalate`, `mark-failed`, `mark-blocked`, `re-dispatch` | implementation agent | implementation agent                                           |
| `refresh-story`                                                                                                 | implementation agent | not used; the feature branch does not move while one unit runs |
| `merge-story`                                                                                                   | implementation agent | implementation agent, after the go                             |
| `close-wave`                                                                                                    | implementation agent | implementation agent, after each unit                          |
| `add <finding-id>`                                                                                              | implementation agent | implementation agent                                           |
| `return-story`                                                                                                  | human                | human                                                          |
| `close`, `close --drop`, `close --orphans`                                                                      | human                | human                                                          |
| `mark-done`                                                                                                     | removed              | removed                                                        |

`mark-done` sets `done` without a merge, which breaks the rule that only the merge sets `done`. No document and no agent calls it, and `merge-story` makes its own transition.

### Guidance by hand

A run by hand needs a person at four points, the person decisions:

- before a unit of work starts;
- before it merges;
- when it stops as `failed` or `blocked`;
- before the merge into `dev`.

At each person decision, the implementation agent stops and shows the output of `premerge-check`, the findings of the unit with their status, and the branch head. It names the command it will run next and waits for the human's go. After the go, it runs `prepare-story` or `merge-story` itself and reports the result.

When a unit stops, the human chooses. If the cause can be fixed, the human fixes it and tells the agent to continue; the agent runs `re-dispatch`. If the cause cannot be fixed, the human runs `dispatch return-story <id>` ([Stops](#stops-retry-and-return)).

Before the merge into `dev`, the agent runs `premerge-check dev <feature-branch>` and shows the result. The human runs `git merge` and then `dispatch close`.

The agent does not refuse itself the commands that start or merge a unit. The human watches, and a wrong merge can be undone. The guardrail refuses only `dispatch return-story` and `dispatch close --drop`, because both destroy work ([The git guardrail](#the-git-guardrail)).

### The story workflow

Every unit of work runs through the same steps on its story branch, on both ways:

1. The developer agent implements the unit test first and commits with the unit ID in the subject. It never sets `done` and never runs a gate script. The pre-commit hooks give it early feedback on each commit.
2. The code-review agent reviews the diff of the story branch. It writes its report to `docs/reviews/code-review-<unit-id>-YYYY-MM-DD.md` and files its findings with the field `story` set to the unit ID.
3. A fresh developer agent fixes each blocking finding. A finding blocks under the rule in [finding-classification.md](../../../packages/factory/rulebooks/conventions/finding-classification.md#shared-severity-scale-and-blocking-rule): its category is `defect` or `risk`, and its severity is `critical` or `major`. A minor finding goes to a register file under `docs/findings/register/` and never blocks.
4. The implementation agent runs the gate-check step ([The gates](#the-gates-and-attempts)).
5. `dispatch merge-story` runs the [checks at the story merge](#checks-at-the-story-merge), merges the story branch into the feature branch, and sets `status: done` in the story file in the merge commit. For a finding, it sets `status: resolved` in the finding file instead. `done` means merged into the feature branch.
6. When the full test suite fails after the merge, `merge-story` moves the feature branch back to the commit before the merge, and the unit becomes `blocked`. The feature branch is local, so nobody has built on the failed merge. A revert commit would make git treat the unit's commits as merged, and a second merge would bring in nothing.

### The gates and attempts

The gates are `dependency-check`, `test-design-verify`, `crap-score`, `mutation-testing`, and a security scanner when the project enables one. The implementation agent runs them on both ways, from the unit's checkout. When a gate fails, it spawns a fresh developer agent with the gate reports and the affected files, and it counts the attempts.

Two keys in [`docs/testing.yaml`](../../../docs/testing.yaml) set the attempts, under `gates`:

| Key                        | Default | Meaning                                                         |
| -------------------------- | ------- | --------------------------------------------------------------- |
| `gates.attempts`           | 3       | attempts on the story's tier: the first attempt and two retries |
| `gates.attempts_escalated` | 3       | attempts on the next stronger tier, after `dispatch escalate`   |

With the defaults, a unit gets at most six developer spawns. When the attempts on the stronger tier also fail, the unit becomes `failed`. Every unit that uses up its attempts on its own tier may escalate. No limit of one escalation per wave applies.

A security scanner runs as a gate only when `docs/testing.yaml` enables it. The scanner key and the tools per language belong to a separate setup proposal. `premerge-check` reruns every gate that `docs/testing.yaml` enables, so a scanner added later runs at the merge with no change to this design. The OWASP review of the `security-review` skill stays with the QA agent at the feature level.

Mutation testing runs per story. If the trial planned in [mutation-gate.md](../../../docs/proposals/mutation-gate.md) shows that it is too slow per story, it moves to the feature steps, and the rest of the frame stays the same.

### Stops, retry and return

A unit stops in one of two states. Both wait for the human, and both are handled the same way:

- `failed`: the gates still fail after all attempts.
- `blocked`: a merge conflict, a refresh conflict, or a red test suite after the merge.

The two names stay, because each tells the human why the unit stopped.

The human then takes one of two paths:

- **Retry.** The human fixes the cause and tells the implementation agent to continue. The agent runs `dispatch re-dispatch <id>`, which moves the unit back to `prepared`, and the unit continues in the same run.
- **Return.** The cause cannot be fixed in this run. The human runs `dispatch return-story <id>`. It sets the unit back to `pending` in the ledger and in the backlog. With the Markdown backlog, the backlog entry is the story file on the feature branch. The ledger gains the transitions `failed -> pending` and `blocked -> pending`. No new state is added.

A unit starts only when every dependency inside the run is `done`. `prepare-wave` and `prepare-story` read only the ledger, and both check every dependency, not only the first one. `init` checks every dependency outside the run, so such a dependency does not count during the run. A return therefore carries through a chain. Take ST-0351, which depends on ST-0350, and ST-0352, which depends on ST-0351. The human returns ST-0350. ST-0351 never starts, and ST-0352 waits as well. A story that depends on neither runs and merges. The feature can then merge into `dev` with all three stories `pending` in the backlog.

### Checks at the story merge

`dispatch merge-story` calls `premerge-check` on the story branch. The merge goes ahead only when every check passes:

| Check                     | Rule                                                                                                                                                                                                                                                     |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Clean tracked files       | A tracked file that differs from the branch head, staged or not, refuses the check. The output names each such file.                                                                                                                                     |
| Untracked files set aside | Untracked files go into a stash named `premerge <unit-id> <date>` before the gates run, and come back with `git stash pop` afterwards. If they cannot come back, the stash stays, and the output names it. Files that `.gitignore` covers stay in place. |
| Review ran                | A review report for the unit exists.                                                                                                                                                                                                                     |
| No blocking finding       | No open blocking finding in a Markdown finding file names the unit in its `story` field. Register files are not read.                                                                                                                                    |
| Gates pass                | Each enabled gate runs its full measuring command at the branch head, tests included. For `mutation-testing`, the check reads the result that the gate-check step stored.                                                                                |
| Scope                     | The changed files stay inside the unit's scope (below).                                                                                                                                                                                                  |

The scope of a unit holds its declared outputs and touches, its backlog file, its spec-feedback report and `INDEX.yaml`. It also holds the unit's own review reports, finding files and register files. A file counts as the unit's own when its name contains the unit ID or its `story` field names the unit. The unit's own files do not count toward the limit on changed files. Any other finding file outside the scope refuses the merge.

`premerge-check` reads the unit ID from the branch name. It accepts `story/<story-id>` and `story/<finding-id>`. A branch with any other name gets no semantic checks.

### Wave close

A wave closes in two parts. First, the implementation agent spawns the owner of each `open` row in the spec-feedback reports of the wave, and then the owner's reviewer for each `fixed` row. These drift sessions commit on the feature branch. The agent waits for their commits. Then it runs `dispatch close-wave N`, which refuses while a row is `open` or while a row about a core-list artifact is `fixed`. On success, `close-wave` appends the wave record to the ledger.

Drift sessions run at the wave close and not after each merge, so a story merge and a drift session never commit on the same branch at the same time. Both stories of a wave start from the same base, so neither could use the other's fixes. The next wave starts after the close and sees the fixed documents.

`prepare-wave N+1` reads the ledger and refuses until the record of wave N exists. By hand, each unit is a wave of its own, so its rows are handled before the next unit starts.

After `close-wave`, the implementation agent routes the open `QA` findings of the wave. A `QA` finding records a test that the coding work could not add, such as one for a surviving mutant.

### Feature steps and the merge into dev

After the last wave closes, two steps run on the feature branch:

1. The code-review agent reviews the whole feature. It looks at how the units fit together and writes `docs/reviews/code-review-<feature-branch>-YYYY-MM-DD.md`, with the slash in the branch name replaced by a hyphen.
2. The QA agent explores the feature and writes its Fagan, security and bug-hunt reports.

A finding filed in these steps belongs to no single unit. It carries the field `run` with the feature branch, for example `run: feature/login`. The implementation agent adds each blocking finding to the run with `dispatch add <finding-id>`. `add` puts it in a new wave and runs the same dependency check as `init`. The finding then runs through [the story workflow](#the-story-workflow) on `story/<finding-id>`: a fix with a regression test, a review, the gates and the merge check. `merge-story` sets `status: resolved` in its merge commit.

`premerge-check dev <feature-branch>` checks the whole run before the merge into `dev`:

- No unit of the run is `failed` or `blocked`. `done` and `pending` units pass.
- Every wave has its record.
- Both feature steps ran.
- No open blocking finding has a `run` field that names the feature branch or a `story` field that names a unit of the run. Other findings on the branch do not count.
- The full test suite passes.

Take `feature/login`. QA files BUG-0090 with `run: feature/login`. An open FAGAN-0071 from an earlier, unrelated review also lies in `docs/findings/`. The check refuses while BUG-0090 is open and ignores FAGAN-0071.

### Close

A run ends in one of two ways: finished or dropped.

**Finished.** After the human merged the feature branch into `dev`, the human runs `dispatch close`. It refuses while a unit is `failed` or `blocked`. It then removes:

- the ledger;
- the worktrees of the run, after it stashed the untracked files of each worktree as `run <feature-branch> <unit-id> <date>`;
- the gate results, the markers, the briefs and the scratch files under `.current-work/<feature-branch>/`;
- the merged branches, with `git branch -d`.

`close` does not pop the stashes. It lists the stashes it made and every unmerged branch. The human decides what to keep and deletes unmerged branches with `git branch -D`. No tracked record of the run is written. The merge commits in `dev` and the status in each backlog entry hold the outcome.

**Dropped.** The human decides to drop the feature and runs `dispatch close --drop`. Every unfinished unit returns to the backlog as `pending`, and the close then removes the state of the run as above.

**Orphans.** `dispatch close --orphans` handles what has no current run:

- worktrees and branches that no ledger names: it removes a worktree whose branch is merged and lists the unmerged ones for the human;
- ledgers whose feature branch is gone, nested ledgers included: it removes a ledger in which every story is `done`, and it lists every other one and leaves it.

`--orphans` does not read the ledger's mode.

### The ledger

The ledger is `.current-work/<feature-branch>/dispatch-ledger.yaml`. Only `dispatch` writes it. It lives under the git-ignored `.current-work/`, and `dispatch close` removes it.

Every field has a command that reads it. The ledger changes in these points:

- `mode` holds `orchestrated` or `by-hand`. `dispatch` and the implementation agent read it. The guardrail does not.
- `invocation_branch` becomes `feature_branch`.
- `closed` goes, because the existence of the ledger already says that the run is active.
- `gate_results` goes, because the merge check reruns the gates.
- The wave records under `waves:` stay, because `prepare-wave` reads them.
- After a merge, `commit_sha` holds the merge commit. `prepare-story` reads it as the base of the next unit in a serial chain. The scope check reads the unit's own commit before the merge, and an interrupted merge resumes from the branch tip, so no command needs the unit's own commit after the merge.

The dispatch contract describes exactly the fields the code writes, under the names the code uses.

### The git guardrail

The git guardrail is one script, `config/hooks/block-dangerous-git.sh`, and all five agent tools call it:

- Claude Code, Codex and GitHub Copilot CLI call it as they do today.
- pi's `config/extensions/block-dangerous-git.ts` becomes a thin wrapper that hands the command to the script, as `config/extensions/guard-human-fields.ts` does.
- OpenCode's plugin `config/plugins/agent-factory.ts` calls the same script.

The guardrail applies one list of checks in every session. The list holds today's checks, including the three worktree rules: a branch is created only with its worktree, worktrees lie under `.current-work/`, and a commit in a linked worktree needs the `verify-base-ok` marker. The list adds one refusal: agents may not run `dispatch return-story` or `dispatch close --drop`.

The guardrail reads the text of a command. An agent that builds a command from variables can get past it. The guardrail stops mistakes, not a deliberate attempt to get around it.

### Pre-commit hooks

The `dependency-check` hook runs on commits. In a project without `docs/spec/dependency-rules.dsl`, the hook prints `dependency-check: no docs/spec/dependency-rules.dsl, skipped` and passes. The gate at the merge does the same. Today the script exits with code 2 in that case, so this is a change of behavior.

### Documents that change

Where a document and the code disagree and no design question lies behind it, the document changes to match the code:

- [mechanized-dispatch.md](../../../docs/spec/areas/mechanized-dispatch.md): `dispatch plan` writes the waves into the ledger; the test command comes from `docs/testing.yaml`; a red test suite moves the feature branch back; `init` refuses per feature branch.
- [interface-contracts.md](../../../docs/spec/interface-contracts.md): the test command comes from `docs/testing.yaml`.
- [dispatch-contract.md](../../../packages/factory/rulebooks/conventions/dispatch-contract.md): `merge-story` copies `packages/factory` into the installed copy; the ledger schema matches the code; the sections on manual mode, completed close and abandoned close follow this design.
- [branching-policy.md](../../../packages/factory/rulebooks/conventions/branching-policy.md): the branch root is the tip of the feature branch at `init`; story branches start from the feature branch on both ways.
- [implementation-agent.md](../../../packages/factory/agents/implementation-agent.md): the handoff line follows the order in [feature-addition.md](../../../packages/factory/playbooks/feature-addition.md); the manual-mode workflow becomes the by-hand workflow of this design.

These documents change because of a decision in this proposal:

- [ADR-0012](../../../docs/adr/0012-dispatcher-owned-semantic-gate-loop.md): attempts per tier, `failed` at the end of the attempts, the implementation agent runs the gates on both ways.
- [ADR-0029](../../../docs/adr/0029-per-story-drift-reports-block-the-wave-close.md): drift sessions run at the wave close; `merge-story` does not wait for them.
- [developer-agent.md](../../../packages/factory/agents/developer-agent.md): the developer agent commits on both ways, never sets `done`, and never runs a gate script.
- [code-review-agent.md](../../../packages/factory/agents/code-review-agent.md): the report names of [Design Details](#design-details).
- [finding-format.md](../../../packages/factory/rulebooks/conventions/finding-format.md): the fields `story` and `run`.
- [rules.md](../../../packages/factory/rulebooks/rules.md): the dispatch rules on the ledger's audit content and on gate decisions by hand follow this design. The ledger is removed at the close, and git history holds the merges.
- [state-machines.md](../../../docs/spec/state-machines.md): the two new ledger transitions.
- [crap-gate-setup.md](../../../docs/proposals/crap-gate-setup.md): links to this proposal.

The vocabulary of [Terms](#terms) applies to the living Markdown under `packages/factory/` and `docs/spec/`. It also applies to code identifiers and error messages: `invocation_branch` becomes `feature_branch`, the mode value `"automated"` becomes `"orchestrated"`, and error messages say "feature branch". Accepted ADRs, superseded proposals and file names keep their words, for example `docs/spec/areas/mechanized-dispatch.md` and `_main_checkout.py`.

## Scope

**In the first release:**

- The run's five phases, with `init` checking dependencies and refusing only per feature branch or for a second run by hand.
- Both ways of driving a run, with the subcommand table and the guidance by hand.
- The story workflow for stories and for findings, including `dispatch add` and `status: resolved` at the merge.
- The gate-check step run by the implementation agent on both ways, with `gates.attempts` and `gates.attempts_escalated`.
- Retry and return of a stopped unit, `dispatch return-story`, and the dependency check over every dependency.
- The checks at the story merge, including the stash of untracked files and the scope of a unit's own files.
- The wave close with drift sessions, and `prepare-wave` waiting for the wave record.
- The feature steps, the `run` field on findings, and `premerge-check dev`.
- `dispatch close`, `--drop` and `--orphans`.
- The ledger changes.
- One guardrail script for all five agent tools, with the refusal of `return-story` and `close --drop`.
- The `dependency-check` hook that passes without a rules file.
- The documents that change, and the vocabulary in living documents, code identifiers and error messages.

**Explicitly deferred (do NOT plan stories for these):**

- The security scanner hook, the scanner key in `docs/testing.yaml` and the setup skill that picks the tools per language. They belong together in a separate setup proposal, like [crap-gate-setup.md](../../../docs/proposals/crap-gate-setup.md), because the key belongs with the skill that chooses the tools.
- A backlog outside Markdown, such as Jira. [jira-backlog-projection.md](../../../docs/proposals/jira-backlog-projection.md) defines that source; this design touches the backlog only at `init`, at `return-story` and at the merge.
- Limits on repeat reviews. [review-loop-cap.md](../../../docs/proposals/review-loop-cap.md) covers them.
- Moving mutation testing to the feature steps. It waits for the trial in [mutation-gate.md](../../../docs/proposals/mutation-gate.md).

## Design Details

- **Stash names.** The merge check names its stash `premerge <unit-id> <date>`, for example `premerge ST-0350 2026-11-20`. The close names its stashes `run <feature-branch> <unit-id> <date>`, for example `run feature/login ST-0350 2026-11-24`. git keeps a stash in the repository, so a stash made in a worktree survives the removal of that worktree.
- **Review report names.** A unit review goes to `docs/reviews/code-review-<unit-id>-YYYY-MM-DD.md`. A feature review goes to `docs/reviews/code-review-<feature-branch>-YYYY-MM-DD.md`, with the slash replaced by a hyphen. A second review of the same unit on the same day adds `-2`, a third adds `-3`. Two stories reviewed on the same day then never add a file at the same path.
- **Review coverage.** `premerge-check` can show that a review ran and that no blocking finding is open. It cannot judge the quality of the review.
- **Red suite.** The script moves the feature branch back itself, so the guardrail never sees that command.
- **Leftovers in this repository.** `--orphans` removes the ledgers of `brownfield-onboarding` and `bug-hunt-fixes`, whose branches are gone and whose stories are all `done`. It lists the `core-artifact-layout` ledger, because ST-0344 is `blocked` there. The human returns ST-0344 to the backlog on `dev` and then removes that ledger. The worktrees without a ledger are those of `data-model-dsl-poc` with its six story worktrees, `agent-cli-devcontainer`, `core-artifact-ownership` and `plan/reconciliation-backfeed`. Other projects that use the Factory clear their leftovers with the same commands; no one-time migration script runs.

## Open Questions

01. **A returned unit in `prepare-wave`.** A returned unit is `pending`, and `prepare-wave` prepares every eligible `pending` unit. Take ST-0350, returned in wave 2. Wave 3 would prepare it again. The design must say how `prepare-wave` tells a returned unit from one that has not started. This becomes an acceptance criterion of the return story.
02. **The other checks of `dispatch escalate`.** Today `escalate` also requires exactly one earlier implementation attempt, the failure class `acceptance_unmet` or `contradictory_evidence`, a passing `verify-base` and no scope violation. The wave limit goes. Whether the other checks stay with three attempts per tier, and what `gates.attempts_escalated: 0` means, is open.
03. **Unmerged branches at `close --drop`.** The guardrail refuses `close --drop` because it destroys work. `close` itself only lists unmerged branches. Whether `--drop` deletes the unmerged branches or lists them like `close` is open.
04. **Routing of `QA` findings at the wave close.** Today the implementation agent routes a `QA` finding by its owner: `owner: test-strategy-agent` goes to that agent, and `owner: planning-agent` waits for a story. The design must say whether that routing stays or every finding goes to the test-strategy agent.
05. **The story's `quality-gates` field.** In `premerge-check`, the field replaces the gate pick from `docs/testing.yaml` and accepts only `crap-score` and `mutation-testing`. Take a story with `quality-gates: [crap-score]` while `docs/testing.yaml` enables mutation testing: mutation testing does not run. Whether the field replaces or adds is open.
06. **The installed copy with several runs.** `merge-story` copies `packages/factory` into `.agent-factory/factory`. With two runs active in the Factory repository, every session then uses the scripts and the guardrail of the run that merged last. Whether this copy stays in `merge-story` is open.
07. **The stash in the primary checkout.** By hand, the merge check stashes all untracked files of the primary checkout, including the human's own files unrelated to the unit. This repository holds about 15 such paths. If `pop` fails, they stay in the stash. Whether the stash takes only some paths, or the human accepts this, is open.
08. **The order of work at the wave close.** The design has the agent spawn the drift sessions before it runs `close-wave`. Whether `close-wave` lists the rows to handle on a first run, and how often the agent runs it, is open.
09. **"run" and "playbook run".** [glossary.md](../../../docs/spec/glossary.md) uses "playbook run" for a wider idea. Whether the glossary keeps both terms or renames one is open.
10. **The `dependency-check` hook trigger.** The script starts with `#!/usr/bin/env -S uv run --script`, so a project without `uv` fails the hook. It also reads only Python imports. Which commits trigger the hook, and what it does without `uv`, is open.
11. **Gate result files.** After this change, only `mutation-testing` has a reader for its stored result in `.current-work/<gate>/<unit-id>.json`. Whether the other gate scripts keep writing result files is open.
12. **The tier of a finding.** A finding has no `tier` field, so a finding run as a unit of work needs a default tier. Which tier, or which rule of the tier rubric in the dispatch contract applies, is open.
13. **Unplaced subcommands.** `clear-manifest` and `suggest-merge-args` have no place in the subcommand table. Whether each stays, and who runs it, is open.
14. **Where `init` writes the ledger.** `init` writes the ledger under the git top level of its working folder. Run from a worktree, it produced the nested ledger in `counter-ids-fitting`. Whether `init` always writes under the primary checkout is open.

## Completion Criteria

- `dispatch init` refuses a story whose dependency outside the run is not done in the backlog, and names that dependency.
- `dispatch init` starts a second orchestrated run on another feature branch while one is active, and refuses a second run on the same feature branch and a second run by hand.
- By hand, `dispatch init` creates the feature branch without a worktree, and `prepare-story` checks out the story branch in the primary checkout.
- By hand, a unit reaches `dispatched` through `mark-dispatching` and `mark-dispatched` run by the implementation agent, and merges through `dispatch merge-story`.
- By hand, the implementation agent stops at each of the four person decisions, shows the `premerge-check` output, the findings with status and the branch head, names the command, and waits for the go.
- `dispatch mark-done` does not exist.
- `dispatch merge-story` sets `status: done` in the story file, or `status: resolved` in the finding file, in the merge commit. The developer agent's instructions contain no step that sets `done` or runs a gate script.
- After a red test suite, the feature branch head equals the commit before the merge, and the unit is `blocked`.
- With `gates.attempts: 3` and `gates.attempts_escalated: 3`, a unit whose gates never pass gets six developer spawns and then becomes `failed`. Two units of one wave that both use up their first-tier attempts both escalate.
- `dispatch return-story` sets a `failed` or `blocked` unit to `pending` in the ledger and in its story file.
- In the chain ST-0350, ST-0351, ST-0352, returning ST-0350 keeps ST-0351 and ST-0352 `pending`, while an independent story runs and merges. `prepare-story` checks every dependency, not only the first.
- `premerge-check` refuses a checkout with a changed tracked file and names the file.
- An untracked test file in the unit's checkout does not take part in the gate rerun and is back in the checkout afterwards.
- `premerge-check` refuses a unit without a review report and a unit with an open blocking finding that names it. A minor finding in a register file does not refuse the merge.
- `premerge-check` reruns `crap-score` with its full measuring command at the branch head; an untested function added in the last commit refuses the merge.
- A unit's own review report, finding files and register files do not refuse the merge for scope and do not count toward the file limit.
- `premerge-check` runs its semantic checks on `story/BUG-0090`.
- `prepare-wave N+1` refuses until the ledger holds the record of wave N.
- `dispatch close-wave` refuses while a spec-feedback row of the wave is `open`.
- `dispatch add BUG-0090` adds the finding to the ledger as a new wave.
- `premerge-check dev feature/login` refuses while BUG-0090 with `run: feature/login` is open, ignores an unrelated open FAGAN-0071, passes `pending` units, and refuses a `failed` or `blocked` unit.
- After `dispatch close` on a finished run, no ledger, worktree, gate result, marker or brief of the run remains. Merged branches are deleted, and the output lists each unmerged branch and each stash it made. An untracked file from a story worktree is in a named stash.
- After `dispatch close --orphans` in this repository, the ledgers of `brownfield-onboarding` and `bug-hunt-fixes` are gone, and every remaining ledger without a branch is one the command listed.
- The ledger has the field `mode` with `orchestrated` or `by-hand`, has `feature_branch`, and has neither `closed` nor `gate_results`. The dispatch contract lists exactly the fields the code writes.
- In each of the five agent tools, an agent's `dispatch return-story` and `dispatch close --drop` are refused, and branch creation without a worktree is refused.
- pi's `block-dangerous-git.ts` contains no rule of its own and calls `config/hooks/block-dangerous-git.sh`.
- In a real OpenCode session, not a mock, the plugin calls the guardrail script and an agent's `git push` is refused.
- In a project without `docs/spec/dependency-rules.dsl`, a commit with a Python file passes the `dependency-check` hook and prints the skip notice.
- No living Markdown file under `packages/factory/` or `docs/spec/` uses the terms automated mode, manual mode, mechanized dispatch, invocation branch, gate-check loop, drift report or main checkout. No code identifier or error message in `dispatch`, `dispatch_lib.py` or `premerge-check` uses `invocation_branch`, `"automated"` or "invocation branch".

## Guiding Rule

A run has one frame and one end on both ways, and every check that decides a merge is a script that measures what merges.

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
