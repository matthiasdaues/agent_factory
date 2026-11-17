# Feature Request: Run Lifecycle

## Summary

This proposal defines one lifecycle for a run, from `dispatch init` to `dispatch close`, on both ways of driving it. It answers a question that the Factory cannot answer today: when does a run end, and what remains after it? The two ways share every step and differ only in the points that [Two ways to drive a run](#two-ways-to-drive-a-run) lists. The first release covers the whole lifecycle, the cleanup of the old runs in this repository, and one vocabulary for the Factory documents.

## Motivation

A run has a start and no end today. `dispatch init` writes a ledger, and no command removes it. A ledger is the file `.current-work/<branch>/dispatch-ledger.yaml`, in which `dispatch` records the stories of a run and their states. Its field `closed` defaults to `false`, and no code in `dispatch` or `dispatch_lib.py` sets it to `true` (checked with `grep`).

The leftovers show the gap. On 2026-11-17, six ledgers lie under `.current-work/` in this repository (checked with `find`). On 2026-11-15, an inventory of the dispatch process compared the code with the documents. It found every story in these ledgers stopped or merged. It also counted 13 worktrees besides the primary checkout and 36,109 files under `.current-work/`. The guardrail's ST-0214 check accepts a commit on a story branch when any ledger exists (`block-dangerous-git.sh`, lines 68 to 76). So an old ledger of another feature counts as a live run.

Four more gaps follow from the missing end.

- Nobody owns the merge of the feature branch into `dev`. Only one line of `branching-policy.md` mentions that merge (the inventory).
- A story driven by hand has no story branch, no ledger and no merge step today (`implementation-agent.md`, manual mode). So `premerge-check` never runs by hand, and a story can reach the feature branch without its checks.
- Documents and code disagree in about fifteen places (the inventory). For example, three sources name three different owners for setting a story to `done`.
- The terms drift. "Feature branch" names the invocation branch in one file and the story branch in another.

The proposal `story-workflow.md` ran into these gaps, and its workflow is one part of a run. This proposal therefore defines the whole run and supersedes `story-workflow.md`.

## Core Principles

- Both ways of driving a run share one frame. It consists of a feature branch, a ledger, story branches, a merge check per story and a defined end.
- Only `dispatch merge-story` sets a story to `done`, in the merge commit. `done` means that the story merged into the feature branch.
- Every ledger field has a command that reads it.
- The merge check reruns every gate except `mutation-testing` at the head of the branch that merges.
- The human gives the go for each step that needs a person. Beyond its checks of today, the git guardrail refuses agents two commands that destroy work.
- After `dispatch close`, only unmerged branches and named stashes remain, and the human handles both.
- Every mechanism works in all five agent tools: Claude Code, Codex, Copilot, pi and OpenCode.

## Design

### Terms

The documents that the vocabulary rule covers use these terms. The paragraph after the table defines that rule. In them, the word "dispatch" names only the script `dispatch`.

| Term                 | Meaning                                                                                                           |
| -------------------- | ----------------------------------------------------------------------------------------------------------------- |
| run                  | Everything that happens for one feature branch, from `dispatch init` to `dispatch close`.                         |
| orchestrated         | The implementation agent starts the stories of a wave in parallel, each in its own worktree.                      |
| by hand              | The implementation agent starts one story at a time in the primary checkout, after the human's go.                |
| feature branch       | The branch of a run, cut from `dev`.                                                                              |
| story branch         | The branch `story/<id>` of one unit of work, cut from the feature branch.                                         |
| unit of work         | A story from the backlog, or a blocking finding that the run fixes in its own story branch.                       |
| wave                 | A set of units of work that start from the same feature branch head. By hand, each wave holds one unit.           |
| gate-check step      | The implementation agent runs the gates on a story branch and has a developer agent fix what they report.         |
| attempt              | One spawn of a developer agent that writes or fixes a story's code. The first implementation counts as attempt 1. |
| spawn                | One start of one agent.                                                                                           |
| spec-feedback report | The file `docs/spec/work/spec-feedback-<story-id>.md`, in which a story records drift between code and documents. |
| primary checkout     | The repository's main folder, as opposed to a linked worktree.                                                    |
| go                   | The human's message to the implementation agent that approves the next step.                                      |

The old terms are automated mode, manual mode, mechanized dispatch, invocation branch, gate-check loop, drift report and main checkout. The vocabulary rule covers the Markdown files under `packages/factory/` and `docs/spec/`. It also covers code identifiers and error messages. For example, the ledger key `invocation_branch` becomes `feature_branch`, and the mode value `automated` becomes `orchestrated`. File names keep their old terms, such as `docs/spec/areas/mechanized-dispatch.md` and `_main_checkout.py`. Accepted ADRs and superseded proposals also keep their words.

### The run

A run passes through seven steps. The implementation agent runs every `dispatch` command in these steps, except the commands that [Two ways to drive a run](#two-ways-to-drive-a-run) gives to the human.

1. **Start.** `dispatch init --stories <ids>` cuts the feature branch from `dev` and writes the ledger, with every story `pending`. In an orchestrated run, `init` also creates a worktree for the feature branch at `.current-work/<feature-branch>/invocation`. By hand, `init` creates no worktree, because the run works in the primary checkout.
2. **Dependency check.** `dispatch init` reads the dependency tree of the listed stories from the backlog. A dependency outside the run must be `done` in the backlog. Otherwise `init` refuses and names the story and its dependency.
3. **Plan.** `dispatch plan` writes the waves and the dependencies into the ledger.
4. **Waves.** Each unit of work of a wave goes through [the story workflow](#the-story-workflow). Then the wave closes, as [Wave close](#wave-close) describes. Wave N+1 starts only after `dispatch close-wave N` succeeds.
5. **Feature checks.** After the last wave closes, the code-review agent reviews the whole feature, and then the QA agent explores it. [Feature checks](#feature-checks) describes how their blocking findings become units of work.
6. **Feature merge.** The implementation agent runs `premerge-check dev <feature-branch>` and shows the result. The human runs `git merge` into `dev`, on both ways.
7. **Close.** `dispatch close` removes the state of the run, as [Close](#close) describes.

After the merge into `dev`, the reconciliation agent brings the specification and the architecture in line with the code. It works on `dev`, one feature at a time, outside the run. It edits shared documents such as the glossary and the arc42 chapters. Two runs that reconciled on their own feature branches would conflict in those files at the merge into `dev`.

`dispatch init` refuses in two cases. The feature branch already has a ledger. Or the new run is by hand, and another run by hand is active, because both would need the primary checkout. Several orchestrated runs may be active at once, one per feature branch. Every check that asks whether a run is active reads only the ledger of the feature branch it works on.

### Two ways to drive a run

The two ways differ in five points.

| Point                          | Orchestrated                                                                           | By hand                                                        |
| ------------------------------ | -------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Where a story runs             | Each story runs in its own worktree under `.current-work/<feature-branch>/story/<id>`. | The story runs in the primary checkout.                        |
| Stories in parallel            | The stories of a wave run in parallel.                                                 | One story runs at a time, and each story is a wave of its own. |
| Worktree of the feature branch | `dispatch init` creates one.                                                           | `dispatch init` creates none.                                  |
| Go before a start or a merge   | The implementation agent goes on without asking.                                       | The implementation agent waits for the human's go.             |
| Runs at once                   | Several orchestrated runs may be active, one per feature branch.                       | One run by hand may be active at a time.                       |

By hand, `dispatch prepare-story` checks out the story branch in the primary checkout. `dispatch merge-story` checks out the feature branch again before it merges.

The ledger records the way in its field `mode`, with the value `orchestrated` or `by-hand`. `dispatch` and the implementation agent read it. The git guardrail does not read it.

Each `dispatch` subcommand has its place on both ways.

| Subcommand                            | What it does                                                                             | Orchestrated                                        | By hand                                    |
| ------------------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------ |
| `init`                                | It cuts the feature branch, writes the ledger and checks the dependencies.               | implementation agent                                | implementation agent, after the human's go |
| `plan`                                | It writes the waves and dependencies into the ledger.                                    | implementation agent                                | implementation agent, after the human's go |
| `prepare-wave`                        | It creates a story branch and a worktree for each story of a wave.                       | implementation agent                                | not used                                   |
| `prepare-story`                       | It creates the story branch of one story.                                                | implementation agent                                | implementation agent, after the human's go |
| `mark-dispatching`, `mark-dispatched` | They record the spawn of the developer agent, so that the story reaches `dispatched`.    | implementation agent                                | implementation agent                       |
| `verify-story`                        | It checks that the story's commit exists on its branch and lies ahead of its base.       | implementation agent                                | implementation agent                       |
| `escalate`                            | It moves a story to the stronger model tier.                                             | implementation agent                                | implementation agent                       |
| `mark-failed`, `mark-blocked`         | They record a stopped story and its reason.                                              | implementation agent                                | implementation agent                       |
| `re-dispatch`                         | It moves a stopped story back to `prepared`, so that it runs again.                      | implementation agent, after the human's go          | implementation agent, after the human's go |
| `refresh-story`                       | It merges a feature branch that moved into the story branch.                             | implementation agent                                | not used                                   |
| `merge-story`                         | It runs the merge check, merges and sets `done` in the merge commit.                     | implementation agent                                | implementation agent, after the human's go |
| `close-wave`                          | It checks that the wave is finished and records the wave as closed.                      | implementation agent                                | implementation agent, after each story     |
| `add <finding-id>`                    | It adds a blocking finding to the ledger as a unit of work in a new wave.                | implementation agent                                | implementation agent, after the human's go |
| `return-story`                        | It sets a stopped story back to `pending` in the ledger and in the backlog.              | human                                               | human                                      |
| `close`                               | It removes the state of a finished run.                                                  | not settled (see [Open Questions](#open-questions)) | human                                      |
| `close --drop`                        | It returns every unfinished story to the backlog and removes the state of a dropped run. | human                                               | human                                      |
| `close --orphans`                     | It finds and removes leftovers that no run owns, as [Close](#close) describes.           | not settled (see [Open Questions](#open-questions)) | not settled                                |

`refresh-story` is not used by hand, because only one story runs at a time, so the feature branch does not move under it. Today `refresh-story` already loads only an orchestrated ledger (`dispatch`, `cmd_refresh_story`). The subcommand `mark-done` goes. It sets `done` in the ledger without a merge, and no agent definition, rulebook, playbook or skill calls it (checked with `grep` under `packages/factory/`).

### Guidance by hand

By hand, the human watches each step and can undo a wrong one. The implementation agent stops at four points: before a story starts, before it merges, when it stops, and before the merge into `dev`.

At each stop, the agent shows the output of `premerge-check`, the findings with their status, and the branch head. Before a story merges, `dispatch merge-story <id> --dry-run` gives that output. Then the agent names the next command and waits.

- **Before a start or a merge**, the human gives the go, and the agent runs `dispatch prepare-story` or `dispatch merge-story` itself.
- **When a story stops**, the human chooses one of two paths. The human fixes the cause and tells the agent to continue, and the agent runs `dispatch re-dispatch`. Or the agent prints `dispatch return-story <id>`, and the human runs it.
- **Before the merge into `dev`**, the agent runs `premerge-check dev <feature-branch>` and shows the result. The human runs `git merge`.

The human runs a command with the `!` prefix in Claude Code, or in a terminal of their own in the other tools. Afterwards, the agent reads the ledger to confirm that the step happened, and then it continues. A merge that went wrong can be undone: the human moves the feature branch back to the commit before the merge.

### The story workflow

Every unit of work goes through five steps on its story branch, before it merges.

1. **Development.** A developer agent writes the code test first and commits. It never sets `done`, and it never runs a gate script. The pre-commit hooks give it early feedback on each commit. When it finds drift between code and documents, it writes the story's spec-feedback report.
2. **Code review.** The code-review agent reviews the story's diff. It writes its report to `docs/reviews/code-review-<story-id>-YYYY-MM-DD.md` and files each finding with the story's ID in its `story` field.
3. **Review fixes.** A fresh developer agent fixes each open blocking finding of the story. A blocking finding is one that [finding-classification.md](../../../packages/factory/rulebooks/conventions/finding-classification.md#shared-severity-scale-and-blocking-rule) marks as blocking. A `minor` finding goes into a register file and never blocks.
4. **Gate-check step.** The implementation agent runs the gates, as [The gates](#the-gates) describes.
5. **Merge.** The implementation agent runs `dispatch merge-story <id>`. It runs the merge check, merges the story branch into the feature branch and writes `status: done` into the story file in the merge commit. For a finding, it writes `status: resolved` instead, as [Feature checks](#feature-checks) describes.

A second review of the same story on the same day writes `code-review-<story-id>-YYYY-MM-DD-2.md`. The review at the end of the feature writes `code-review-<feature-branch>-YYYY-MM-DD.md`, with the slash of the branch name replaced by a hyphen. For example, the feature review of `feature/login` writes `code-review-feature-login-YYYY-MM-DD.md`.

### The gates

The implementation agent runs the gates of a story from the story's checkout, on both ways. The gates are `dependency-check`, `test-design-verify`, `crap-score`, `mutation-testing` and a security scanner. `premerge-check` lists the conditions under which each of the first four runs (`premerge-check`, header comment). The security scanner runs when `docs/testing.yaml` enables one. A separate setup proposal defines that key, as [Scope](#scope) states.

When a gate fails, the implementation agent spawns a fresh developer agent with the gate's output. It counts the attempts in the ledger. Two keys in `docs/testing.yaml` set the limits.

| Key                        | Default | Meaning                                                                                                              |
| -------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------- |
| `gates.attempts`           | 3       | The story gets this many attempts on its own model tier: the first attempt and two retries.                          |
| `gates.attempts_escalated` | 3       | After `dispatch escalate`, the story gets this many attempts on the stronger tier. A value of 0 means no escalation. |

With the defaults, a story gets at most six attempts. Every story that uses up its attempts on its own tier may escalate. No limit applies per wave. After the last attempt fails, the implementation agent runs `dispatch mark-failed`. The test-strategy agent owns `docs/testing.yaml`, so it sets these counts next to the gate thresholds.

The OWASP review of the `security-review` skill stays with the QA agent at the feature level. It needs judgment, and the flaws it finds often show only when the stories fit together.

Mutation testing runs per story. `mutation-gate.md` plans a trial on five stories to measure its time per story. If the trial shows that it is too slow, mutation testing moves to the feature level, and the other steps stay as they are.

### Fast gates as pre-commit hooks

A pre-commit hook runs `dependency-check` on each commit. Without `docs/spec/dependency-rules.dsl`, the hook prints `dependency-check: no docs/spec/dependency-rules.dsl, skipped` and passes. The gate at the merge does the same. This is a change: today `dependency-check` exits with code 2 and `DSL file not found` when the file is missing. A project writes its rules file in the architecture phase, so a new project has none.

### Stopped stories

A story stops as `failed` or as `blocked`. `failed` means that the gates still fail after the last attempt. `blocked` means a merge conflict, or a test suite that fails after the merge. Both states wait for the human, and the human handles both in the same way.

- **The cause can be fixed.** The human fixes it and tells the implementation agent to continue. The agent runs `dispatch re-dispatch <id>`, and the story runs again in the same run.
- **The cause cannot be fixed.** The human runs `dispatch return-story <id>`. The story becomes `pending` in the ledger and in the backlog.

The ledger gains two transitions, from `failed` to `pending` and from `blocked` to `pending`. It gains no new state.

A story starts only when every dependency inside the run is `done` in the ledger. `prepare-wave` and `prepare-story` both check every dependency. Today `prepare-story` checks only the first one (`dispatch`, `cmd_prepare_story`, `entry.deps[0]`). During the run, both read only the ledger. `dispatch init` checked the dependencies outside the run at the start.

Stories that depend on a returned story stay `pending`, and the others continue. Take a run in which ST-9002 depends on ST-9001, and ST-9003 depends on ST-9002. The human returns ST-9001. ST-9002 never starts, so ST-9003 waits as well. A fourth story that depends on neither runs and merges. At the end, the three stories are `pending` and stay in the backlog. The feature can merge into `dev` without them.

When the test suite fails after a merge, `dispatch merge-story` moves the feature branch back to the commit before the merge. The story becomes `blocked`. A revert commit would make git treat the story's commits as merged, so a second merge of the story would bring in nothing. The feature branch is local, so nobody has built on the failed merge.

### Findings name their story or run

A finding names the unit of work it belongs to, so that the merge checks can find it.

- A finding from a story's review carries the story's ID in the field `story`. Register files already require `story`. Finding files gain the field.
- A finding from the feature review or from QA carries the feature branch in a new field `run`, for example `run: feature/login`.

`finding-format.md`, the finding template and `interface-contracts.md` change to describe both fields.

### Checks at the merge

`premerge-check` runs at two merges: a story into the feature branch, and the feature branch into `dev`.

At a story merge, `dispatch merge-story` calls `premerge-check`. It runs these checks in this order.

| Check               | The merge is refused when …                                                                                                                                                                                        |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Clean checkout      | A tracked file in the story's checkout differs from the branch head, staged or not. The output names those files.                                                                                                  |
| Review exists       | No file `docs/reviews/code-review-<story-id>-*.md` exists on the branch.                                                                                                                                           |
| No blocking finding | A finding file with status `open` names the story in `story` and is blocking.                                                                                                                                      |
| Gates pass          | A gate fails when it runs again at the branch head with its full command, tests included. `mutation-testing` is the exception: the check reads its stored result `.current-work/mutation-testing/<story-id>.json`. |
| Scope               | A changed file lies outside the story's paths.                                                                                                                                                                     |
| File count          | More files change than `--max-files` allows.                                                                                                                                                                       |

Before the gates run again, `premerge-check` puts the untracked files of the checkout into a stash named `premerge <story-id> <date>`. The gates then measure only what will merge. Afterwards, `premerge-check` puts the files back with `git stash pop`. If that fails, the stash stays, and the output names it. Files that `.gitignore` covers stay where they are.

For `crap-score`, the full command runs the tests, writes fresh coverage and then scores. A coverage file from an earlier test run would miss code that later commits added.

The story's paths are its declared outputs, its backlog file, its spec-feedback report and `INDEX.yaml`. They also include every file that belongs to the story. Such a file contains the story's ID in its name, or names the story in its `story` field. These files do not count toward `--max-files`. For example, the review report `code-review-ST-9001-YYYY-MM-DD.md` belongs to ST-9001.

`premerge-check` reads the ID from the branch name. Today it reads only the pattern `story/ST-NNNN` and prints `SKIP semantic-gates` for every other name (`premerge-check`, line 438). The pattern widens to finding IDs, such as `story/BUG-9001`.

At the feature merge, the implementation agent runs `premerge-check dev <feature-branch>`. It refuses the merge in these cases.

| Check          | The merge is refused when …                                                                                |
| -------------- | ---------------------------------------------------------------------------------------------------------- |
| Story states   | A story of the run is in a state other than `done` or `pending`.                                           |
| Waves          | A wave of the run is not recorded as closed.                                                               |
| Feature checks | The feature review or QA has not run.                                                                      |
| Open findings  | An open blocking finding names the feature branch in `run`, or names a unit of work of the run in `story`. |
| Tests          | The full test suite fails at the head of the feature branch.                                               |

The check counts no unrelated finding. Take an open finding FAGAN-9001 from an earlier review, with an empty `story` and no `run`. It lies in `docs/findings/` on the feature branch, and the check ignores it.

### Wave close

A wave closes after every story of the wave has stopped or merged. The implementation agent then starts the owner of each open row of the wave's spec-feedback reports, and after it a reviewer. For example, the domain-modeling agent owns a row that says the glossary lacks a term. These sessions commit on the feature branch.

When all of them have committed, the implementation agent runs `dispatch close-wave N`. `close-wave` refuses while a row is `open`, or `fixed` on a core or seam artifact as ADR-0029 defines them. On success, it records the wave as closed in the ledger. `prepare-wave` reads that record before it starts wave N+1.

The rows wait until the wave closes, so the owner sessions do not commit while the stories of their wave merge. Both stories of a wave start from the same head, so neither could use a fix from the other's row. By hand, each story is a wave, so its rows are handled right after the story merges.

### Feature checks

After the last wave closes, the code-review agent reviews the whole feature on the feature branch. It looks at how the stories fit together. Then the QA agent explores the feature and writes its Fagan, security and bug-hunt reports.

Each blocking finding of these reviews becomes a unit of work. Take BUG-9001, which QA files against the login form with `run: feature/login`.

1. `dispatch add BUG-9001` adds the finding to the ledger as a unit of work in a new wave. The command runs the same dependency check as `init`.
2. The finding runs through [the story workflow](#the-story-workflow) on the branch `story/BUG-9001`. A developer agent fixes it with a regression test, and the fix gets a review, the gates and the merge check.
3. `dispatch merge-story BUG-9001` writes `status: resolved` into the finding file in the merge commit. From then on, the feature merge check does not count it as open.

A finding has no model tier. The run uses a default tier for it, which [Open Questions](#open-questions) leaves open. The run treats a story and a finding in the same way, so it does not depend on where the backlog keeps its stories.

### Close

A run ends in one of two ways. It is finished after the human merges the feature branch into `dev`. Or the human drops it.

`dispatch close` refuses while a story of the run is in a state other than `done` or `pending`. When it runs, it removes all state of the run:

- the ledger;
- the worktrees of the run;
- the gate results under `.current-work/<gate>/`;
- the markers `premerge-check-ok` and `verify-base-ok`;
- the briefs and scratch files under `.current-work/<feature-branch>/`.

Before it removes a worktree, `dispatch close` puts the worktree's untracked files into a stash named `run <feature-branch> <story-id> <date>`. It does not put them back. Git keeps a stash in the repository, not in the folder, so the stash survives the removal.

`dispatch close` deletes each merged branch with `git branch -d`, which git allows only for a fully merged branch. It lists every unmerged branch and every stash it made. The human deletes the unmerged branches with `git branch -D` and decides which stashes to keep. The guardrail refuses agents `git branch -D` (`block-dangerous-git.sh`, line 154).

No tracked record of the run remains. The merge commits in `dev` and the status in each story file hold the outcome.

When the human drops a feature, the human runs `dispatch close --drop`. It returns every unfinished story to the backlog as `pending`, and then it removes the state of the run as `dispatch close` does.

`dispatch close --orphans` handles state that no run owns.

- It lists every worktree and branch without a ledger. It removes each such worktree whose branch has merged, and it leaves the others to the human.
- It also finds every ledger whose feature branch is gone, including a ledger nested inside a worktree. It removes such a ledger when every story in it is `done`, and it lists every other one.
- It does not read `mode`.

### The ledger

The ledger holds only fields that a command reads. Today the dispatch contract lists fields that the code never writes, such as `declared_base`, `premerge_check` and `merge_sha` (`dispatch-contract.md`, lines 254 to 273).

| Change                                        | Reason                                                                                                       |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `gate_results` goes from every story entry.   | The field always stays empty (`dispatch_lib.py`, `StoryEntry`), and the merge check reruns the gates.        |
| `closed` goes.                                | No code sets it, and an existing ledger already means that its run is active.                                |
| `mode` holds `orchestrated` or `by-hand`.     | `dispatch` and the implementation agent read it. Today its default value is `automated` (`dispatch_lib.py`). |
| `invocation_branch` becomes `feature_branch`. | The ledger uses the run's vocabulary.                                                                        |
| The wave records stay.                        | `prepare-wave` reads them before it starts the next wave.                                                    |

`commit_sha` keeps its behavior. After a merge, it holds the merge commit, and `prepare-story` reads it as the base of the next story in a serial chain. Before the merge, `verify-story` reads the story's own commit. A merge that stopped halfway resumes from the branch tip. So no command needs the story's own commit after the merge.

The dispatch contract describes exactly the fields that the code writes, under the code's names. The rule in `rules.md` that the ledger records gate results and the merge commit goes. `dispatch close` deletes the ledger, and git history holds the merges.

### The git guardrail

One script, `config/hooks/block-dangerous-git.sh`, checks the shell commands of agents in all five tools.

- Claude Code, Codex and Copilot call the script directly, as they do today (`init-factory`, `hooks/block-dangerous-git.json`).
- pi's `config/extensions/block-dangerous-git.ts` becomes a thin wrapper that hands each command to the script. `guard-human-fields.ts` already works this way.
- OpenCode's plugin `config/plugins/agent-factory.ts` calls the same script. Today OpenCode gets no git guardrail, so `git push` is not refused there either.

The script applies one set of checks in every session.

- The checks of today stay, the three worktree rules included. A branch is created only together with its worktree. A worktree lies under `.current-work/`. A commit in a linked worktree needs a `verify-base-ok` marker.
- The ST-0214 check reads only the ledger of the story branch's own feature branch.
- New: the script refuses agents `dispatch return-story` and `dispatch close --drop`. Both destroy work that a human cannot get back by watching.

pi's copy differs from the shell script today. It reads only `docs/charter/testing.yaml` (`block-dangerous-git.ts`, line 140), and it has no ledger check. With the wrapper, pi runs the same logic as the other four tools.

### Documents that change

Where a document and the code disagree and no design question lies behind it, the document changes to match the code.

| Document                                                                     | Change                                                                                                                       |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `docs/spec/areas/mechanized-dispatch.md`                                     | `dispatch plan` writes the waves into the ledger, and the area says so.                                                      |
| `docs/spec/areas/mechanized-dispatch.md`, `docs/spec/interface-contracts.md` | The test command comes from `docs/testing.yaml`, not from `config/project.json`.                                             |
| `docs/spec/areas/mechanized-dispatch.md`                                     | A failing test suite after a merge moves the feature branch back. The area says so instead of a revert.                      |
| `dispatch-contract.md`                                                       | `dispatch merge-story` copies `packages/factory` into `.agent-factory/factory`. The contract calls this a manual step today. |
| `branching-policy.md`                                                        | The branch root is the tip of the feature branch when `dispatch init` runs.                                                  |
| `implementation-agent.md`                                                    | One handoff line names the reconciliation agent directly. That line goes, and the order of `feature-addition.md` holds.      |

Other documents change because the design changes them.

| Document               | Change                                                                                                                                  |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `developer-agent.md`   | The developer agent never sets `done` and never runs a gate script, by hand included.                                                   |
| `rules.md`             | By hand, the human gives the go for each step that needs a person. The ledger audit rule goes.                                          |
| ADR-0012               | The attempt counts come from `docs/testing.yaml`. After the last failed attempt, the story becomes `failed`. No limit applies per wave. |
| ADR-0029               | The owner sessions of the spec-feedback rows run at the wave close, not after each merge.                                               |
| `feature-addition.md`  | The order becomes implementation, feature review, QA, merge into `dev`, and then reconciliation.                                        |
| `code-review-agent.md` | The report name carries the story ID or the feature branch.                                                                             |
| `finding-format.md`    | Finding files carry `story` and `run`.                                                                                                  |

ADR-0029 says that `prepare-wave N` refuses until the ledger records wave N-1 as closed (ADR-0029, lines 66 to 68). Today the code checks only that every story of the earlier wave has stopped or merged. The code changes to match ADR-0029.

## Scope

**In the first release:**

- The seven steps of [The run](#the-run), on both ways.
- The changes to `dispatch init`: no worktree by hand, the two cases of refusal, and the dependency check.
- The new subcommands `return-story`, `add`, `close`, `close --drop` and `close --orphans`, and the removal of `mark-done`.
- The dependency check of every dependency in `prepare-wave` and `prepare-story`.
- The attempt keys in `docs/testing.yaml`, and `dispatch escalate` without the limit per wave.
- The story workflow and the merge checks of [Checks at the merge](#checks-at-the-merge), including the stash at the rerun.
- The fields `story` and `run` on findings, and the wider branch pattern in `premerge-check`.
- The ledger changes of [The ledger](#the-ledger).
- One guardrail script for all five tools, the pi wrapper, the OpenCode plugin and the refusal of the two commands.
- The `dependency-check` hook and its skip without a rules file.
- The vocabulary rule and the document changes of [Documents that change](#documents-that-change).
- The cleanup of the six ledgers in this repository with `dispatch close` and `dispatch close --orphans`.

**Explicitly deferred (do NOT plan stories for these):**

- The security scanner's hook, its gate at the merge and its key in `docs/testing.yaml`. A separate setup proposal picks the tools per language, as `crap-gate-setup.md` does for `crap-score`.
- A backlog outside Markdown files, such as Jira. `jira-backlog-projection.md` defines that source. This proposal states only that the dependency check reads "the backlog" and that a return reaches "the backlog".
- Limits on repeat reviews, which `review-loop-cap.md` covers.
- Moving mutation testing to the feature level, which waits for the trial in `mutation-gate.md`.

## Design Details

- **Bypass.** The guardrail reads command text. An agent that builds a command from variables can get past it. `guard-human-fields` documents the same limit. By hand, the human watches each step. The guardrail's one new refusal covers the two commands that destroy work.
- **Review coverage.** `premerge-check` can show that a review report exists and that no blocking finding is open. It cannot judge the quality of the review.
- **Untracked files at the rerun.** By hand, the story runs in the primary checkout. The stash at the rerun then also takes the human's own untracked files, and puts them back afterwards. If `git stash pop` fails, those files stay in the named stash.
- **Interrupted merge.** `dispatch merge-story` resumes from the head of the story branch.
- **Installed copy.** In the Factory's own repository, `dispatch merge-story` copies `packages/factory` over `.agent-factory/factory` after each merge. With several runs active, every session then runs the scripts of the run that merged last. [Open Questions](#open-questions) holds the choice.
- **The leftovers in this repository.** Six ledgers lie under `.current-work/`, as [Motivation](#motivation) states.
  - `feature/brownfield-onboarding` and `feature/bug-hunt-fixes` have no branch left. `dispatch close --orphans` removes their ledgers if every story in them is `done`.
  - `feature/core-artifact-layout` has no branch left, and its ledger lists ST-0344 as `blocked`. `dispatch close --orphans` lists it and leaves it.
  - `feature/finding-classification` and `feature/counter-ids` still have their branches, so `dispatch close` handles them. [Open Questions](#open-questions) holds how it reads their `mode: automated`.
  - One ledger lies nested at `.current-work/feature/counter-ids-fitting/.current-work/feature/counter-ids-fitting/dispatch-ledger.yaml`. A lookup by branch does not find it.

## Open Questions

- **Who runs `dispatch close` in an orchestrated run, and who runs `dispatch close --orphans`.** By hand, the human runs `close`. For an orchestrated run, no source settles it. Take `feature/login`, orchestrated, just after the human merged it into `dev`. Option A: the implementation agent runs `dispatch close` once it sees the merge, and the human only deletes the listed branches and stashes. Option B: the human runs `dispatch close`, as by hand. I recommend option A, because `close` refuses unless every story is `done` or `pending`, and it destroys no unmerged work. `--orphans` removes only merged worktrees and ledgers whose stories are all `done`, so the same reason applies to it.

- **Which conditions of `dispatch escalate` stay.** Besides the limit per wave, `escalate` checks five more conditions (`dispatch`, `cmd_escalate`). One requires exactly one earlier implementation attempt in the ledger. Whether the fix attempts count toward it is unchecked. Take ST-9001 after three failed attempts on its tier. Option A: the five conditions stay as they are, and ST-9001 may fail that one. Option B: the tier, failure-class and branch checks stay, and the attempt condition reads `gates.attempts`. I recommend option B, because the attempt condition must match the new count.

- **Where the wave close sends open `QA` findings.** A `QA` finding records a mutant that the gate-check step could not kill (`finding-format.md`). Today the implementation agent routes it by its `owner` field (`implementation-agent.md`, step 6). A `planning-agent` finding waits for a story there. Take QA-9001 with `owner: planning-agent`. Option A: the routing by owner stays, and QA-9001 waits for a story. Option B: the wave close sends every `QA` finding to the test-strategy agent, and that agent gets a finding it cannot fix. I recommend option A, because the owner field already says who can act.

- **Whether a story's `quality-gates` field replaces or extends the gates of `docs/testing.yaml`.** Today the field replaces them. It accepts only `crap-score` and `mutation-testing` (`premerge-check`, header comment). Take a story with `quality-gates: [crap-score]` while `docs/testing.yaml` enables mutation testing. Option A: the field replaces the list, and mutation testing does not run. Option B: the field adds gates, and both run. I recommend option B, because a project setting should not vanish because one story names one gate.

- **How the copy into `.agent-factory/factory` behaves when several runs are active.** `dispatch merge-story` copies `packages/factory` over the installed copy after each merge (`dispatch`, `cmd_merge_story`). This happens only in the Factory's own repository. Take run A, which merges a story that breaks `block-dangerous-git.sh`, while run B works. Option A: the copy stays, and run B's agents lose the guardrail until run A repairs it. Option B: the tests read the scripts from `packages/factory`, and `dispatch merge-story` copies nothing. Today the tests import from the installed copy (`dispatch`, comment in `cmd_merge_story`), so option B changes the test setup. I recommend option A for the first release, with the limit stated in Design Details. The risk exists only in the Factory's own repository.

- **Whether the stash at the rerun may take the human's own untracked files.** By hand, the story runs in the primary checkout. This repository's primary checkout holds untracked handoffs, research notes and draft proposals (`git status`). Take a story merge in which `git stash pop` fails. Option A: the stash stays as designed, and those files wait in the named stash. Option B: the rerun runs in a temporary worktree of the branch head, and the primary checkout stays untouched. I recommend option A with a clear message, because the human watches every merge by hand and can apply the stash.

- **What the `dependency-check` hook needs.** `dependency-check` starts with `#!/usr/bin/env -S uv run --script`, so a project without `uv` fails the hook. It reads Python imports only (`dependency-check`, header comment). Take a TypeScript project without `uv`. Option A: `init-factory` installs the hook only where `uv` exists and the project has Python files. Option B: the hook always runs, and the project installs `uv`. I recommend option A, because a hook that cannot run teaches people to skip hooks.

- **How the glossary names a run.** `docs/spec/glossary.md` already uses "playbook run" for a wider idea, in the entry "In Use". Take a reader who meets "run" in this proposal and "playbook run" in the glossary. Option A: the glossary gains "run" as defined in [Terms](#terms), and "playbook run" keeps its meaning. Option B: "playbook run" changes its name. I recommend option A, because the two ideas differ, and the glossary can say how.

- **How ST-0344 leaves the old ledger.** The ledger of `feature/core-artifact-layout` lists ST-0344 as `blocked`, but `backlog/ST-0344.md` says `status: done`. A return would set a finished story to `pending`. Option A: the human removes that ledger by hand after `--orphans` lists it, and the story file stays `done`. Option B: `--orphans` removes a ledger when the backlog says `done` for each story. I recommend option A, because one ledger does not justify a rule that reads the backlog.

- **How `dispatch close` reads the old ledgers that still have a branch.** The ledgers of `feature/finding-classification` and `feature/counter-ids` carry `mode: automated`. The nested ledger of `feature/counter-ids-fitting` lies where a lookup by branch misses it. Option A: `close` reads `automated` as `orchestrated`, and `--orphans` also handles nested ledgers whose branch exists. Option B: the human removes these three ledgers by hand. I recommend option A, because other projects may hold the same leftovers.

- **Which model tier a finding gets as a unit of work.** A finding has no tier field. Take BUG-9001 from QA. Option A: the run uses the tier of the story the finding's `artifact` touches most. Option B: the run uses one fixed default tier, set in `docs/testing.yaml`. I recommend option B, because it is simple and visible.

- **How the feature merge check sees that the feature review and QA ran.** The feature review writes `code-review-<feature-branch>-YYYY-MM-DD.md`. No source names the QA reports in a form the check can find. Take `feature/login` after QA. Option A: QA's report names carry the feature branch, as the feature review's name does. Option B: the ledger records each feature check when it finishes. I recommend option A, because the review report already works this way.

- **How ADR-0012 and ADR-0029 change.** Both are accepted. The project replaces an ADR with a new one that supersedes it, for example ADR-0010 by ADR-0023. Take the attempt counts, which ADR-0012 sets in its text today. Option A: a new ADR states the counts from `docs/testing.yaml`, and ADR-0012 becomes `superseded`. Option B: ADR-0012 is edited and names the new keys. I recommend option A, because the project already works this way, and each ADR keeps its own words.

- **What happens to gate result files that nothing reads.** After the change, `premerge-check` reads only `.current-work/mutation-testing/<story-id>.json`. The other gate scripts still write their results. Take `crap-score`, which writes `.current-work/crap-score/<story-id>.json` on each run, and nothing reads that file. Option A: the other scripts stop writing them. Option B: they keep writing, and `dispatch close` removes them. I recommend option A, because the ledger already follows the rule that every field has a reader.

- **Where `status`, `clear-manifest` and `suggest-merge-args` belong.** No source places these three subcommands. `suggest-merge-args` prints a `--max-files` value for the merge into `dev`. Take a run by hand before that merge, in which the agent needs the value. Option A: the implementation agent runs all three on both ways. Option B: `suggest-merge-args` joins `premerge-check dev`, and the other two stay with the agent. I recommend option A for now, because none of them destroys work.

- **When mutation testing is too slow per story.** `mutation-gate.md` plans the trial, but this proposal sets no threshold. Take a trial in which one story's mutation run takes 20 minutes. Option A: the threshold comes from the trial's report. Option B: this proposal sets a fixed limit now. I recommend option A, because the trial measures the real cost first.

## Completion Criteria

Each criterion names a setup, an action and a result.

**Start and dependencies**

- Setup: no ledger exists for `feature/login`. Action: the implementation agent runs `dispatch init --stories ST-9001` for an orchestrated run. Result: the ledger has `mode: orchestrated`, and a worktree exists at `.current-work/feature/login/invocation`.
- Setup: no ledger exists for `feature/login`. Action: `dispatch init` runs for a run by hand. Result: the ledger has `mode: by-hand`, and no worktree exists for the feature branch.
- Setup: `feature/login` has a ledger. Action: `dispatch init` runs again for `feature/login`. Result: `init` refuses and names the existing ledger.
- Setup: an orchestrated run on `feature/login` is active. Action: `dispatch init` runs for an orchestrated run on `feature/search`. Result: the second run starts.
- Setup: a run by hand on `feature/login` is active. Action: `dispatch init` runs for a run by hand on `feature/search`. Result: `init` refuses and names the active run.
- Setup: ST-9010 depends on ST-9000, which is `pending` in the backlog and not in the run. Action: `dispatch init --stories ST-9010` runs. Result: `init` refuses and names ST-9010 and ST-9000.
- Setup: ST-9002 depends on ST-9001 and ST-9004 in the same run, and only ST-9001 is `done`. Action: `dispatch prepare-story ST-9002` runs. Result: the command refuses and names ST-9004.

**Two ways and guidance**

- Setup: a run by hand, with ST-9001 ready to start. Action: the implementation agent reaches the start. Result: it names `dispatch prepare-story ST-9001` and runs it only after the human's go.
- Setup: a run by hand, with ST-9001 past its gate-check step. Action: the agent reaches the merge. Result: it shows the `--dry-run` output, the findings with status and the branch head, and waits for the go.
- Setup: a run by hand, with ST-9001 in the ledger. Action: the implementation agent runs the start and the spawn. Result: the story reaches `dispatched`, and `dispatch merge-story ST-9001` accepts it.
- Setup: any run. Action: an agent runs `dispatch mark-done ST-9001`. Result: `dispatch` reports an unknown subcommand.
- Setup: a run by hand, with ST-9001 `blocked`. Action: the human runs the printed `dispatch return-story ST-9001` with `!`. Result: the agent reads `pending` in the ledger and continues with the next story.

**Story workflow and gates**

- Setup: the developer agent finishes ST-9001. Action: it commits. Result: the story file on the story branch does not say `done`, and no gate result file comes from that session.
- Setup: ST-9001 merges. Action: `dispatch merge-story ST-9001` runs. Result: the merge commit sets `status: done` in the story file.
- Setup: `docs/testing.yaml` holds no attempt keys, and `crap-score` fails on every attempt. Action: the gate-check step runs for ST-9001. Result: the ledger records three attempts on the story's tier, three on the stronger tier, and then `failed`.
- Setup: `gates.attempts_escalated: 0`. Action: ST-9001 uses up its attempts on its tier. Result: the story becomes `failed` without `dispatch escalate`.
- Setup: ST-9001 and ST-9002 in one wave both use up their attempts on their tier. Action: the implementation agent escalates both. Result: both get their escalated attempts.
- Setup: a project without `docs/spec/dependency-rules.dsl`. Action: a commit runs the pre-commit hooks. Result: the hook prints `dependency-check: no docs/spec/dependency-rules.dsl, skipped` and passes.
- Setup: two stories reviewed on the same day. Action: both merge. Result: their reports carry different names that contain each story's ID, and the second merge has no conflict.

**Stopped stories**

- Setup: ST-9001 is `blocked` by a merge conflict. Action: the human resolves the conflict and tells the agent to continue. Result: the agent runs `dispatch re-dispatch ST-9001`, and the story runs again in the same run.
- Setup: ST-9001 is `failed`. Action: the human runs `dispatch return-story ST-9001`. Result: the story is `pending` in the ledger and in its story file.
- Setup: ST-9002 depends on ST-9001, and ST-9003 on ST-9002. Action: the human returns ST-9001. Result: ST-9002 and ST-9003 never start, and a story independent of all three merges.
- Setup: ST-9002 merges, and the full test suite fails afterwards. Action: `dispatch merge-story` finishes. Result: the feature branch points to the commit before the merge, and ST-9002 is `blocked`.

**Checks at the merge**

- Setup: a tracked file in ST-9001's checkout differs from the branch head. Action: `premerge-check` runs. Result: it refuses and names the file.
- Setup: an untracked test file lies in ST-9001's checkout. Action: `premerge-check` runs. Result: the gates run without that file, and the file is back in the checkout afterwards.
- Setup: `git stash pop` fails after the rerun for ST-9001. Action: `premerge-check` finishes. Result: the stash `premerge ST-9001 <date>` remains, and the output names it.
- Setup: the coverage file in ST-9001's checkout is older than the last commit. Action: the merge check runs `crap-score`. Result: the tests run again, and the score uses fresh coverage.
- Setup: ST-9001 has an open `major` finding of category `defect` with `story: ST-9001`. Action: `premerge-check` runs. Result: it refuses and names the finding.
- Setup: ST-9001 has only an open `minor` finding in a register file. Action: `premerge-check` runs. Result: the finding does not block the merge.
- Setup: no review report for ST-9001 exists. Action: `premerge-check` runs. Result: it refuses because the review is missing.
- Setup: ST-9001's branch adds its review report and a finding file with `story: ST-9001`. Action: the scope check runs. Result: neither file counts as out of scope or toward `--max-files`.
- Setup: the branch `story/BUG-9001`. Action: `premerge-check` runs. Result: it runs the semantic gates and does not print `SKIP semantic-gates`.

**Wave close and feature checks**

- Setup: wave 1 has merged, and a spec-feedback row is `open`. Action: `dispatch prepare-wave 2` runs. Result: it refuses until `dispatch close-wave 1` succeeds.
- Setup: a spec-feedback row is `open` in wave 1. Action: the implementation agent runs `dispatch close-wave 1`. Result: `close-wave` refuses and names the row.
- Setup: QA files BUG-9001 with `run: feature/login`. Action: the implementation agent runs `dispatch add BUG-9001`. Result: the ledger holds BUG-9001 in a new wave.
- Setup: BUG-9001 passes its checks. Action: `dispatch merge-story BUG-9001` runs. Result: the merge commit sets `status: resolved` in `docs/findings/BUG-9001.md`.
- Setup: an open blocking FAGAN-9001 without `story` or `run` lies on `feature/login`. Action: `premerge-check dev feature/login` runs. Result: the finding does not block.
- Setup: an open blocking finding with `run: feature/login`. Action: `premerge-check dev feature/login` runs. Result: it refuses and names the finding.
- Setup: every story of `feature/login` is `done`, except a returned story that is `pending`. Action: `premerge-check dev feature/login` runs with the other checks passing. Result: it passes.
- Setup: a story of `feature/login` is `failed`. Action: `premerge-check dev feature/login` runs. Result: it refuses and names the story.

**Close**

- Setup: `feature/login` merged into `dev`, and every story is `done`. Action: `dispatch close` runs. Result: the ledger, the worktrees, the gate results, the markers and the briefs of the run are gone.
- Setup: a story worktree holds an untracked file. Action: `dispatch close` runs. Result: the file is in a stash named `run feature/login <story-id> <date>`, and the output lists that stash.
- Setup: a run with one unmerged branch. Action: `dispatch close` runs. Result: the merged branches are gone, and the output lists the unmerged branch.
- Setup: a story of the run is `blocked`. Action: `dispatch close` runs. Result: it refuses and names the story.
- Setup: the human drops `feature/login` with two unfinished stories. Action: the human runs `dispatch close --drop`. Result: both stories are `pending` in the backlog, and the run's state is gone.
- Setup: this repository's six ledgers. Action: `dispatch close --orphans` runs. Result: no ledger without a branch remains, except those the output lists.

**Ledger and guardrail**

- Setup: a new ledger. Action: `dispatch init` writes it. Result: it holds no `gate_results` and no `closed`, and it holds `feature_branch` instead of `invocation_branch`.
- Setup: each of the five agent tools runs an agent. Action: the agent runs `dispatch close --drop`. Result: the guardrail refuses it in each tool.
- Setup: each of the five agent tools runs an agent. Action: the agent runs `dispatch return-story ST-9001`. Result: the guardrail refuses it in each tool.
- Setup: pi runs an agent. Action: the agent runs `git checkout -b story/ST-9001`. Result: the refusal comes from `block-dangerous-git.sh`, which the wrapper called.
- Setup: a real OpenCode session, not a mock. Action: the agent runs `git push`. Result: the guardrail refuses it.
- Setup: a ledger exists only for another feature branch. Action: an agent commits on a story branch of `feature/login`. Result: the ST-0214 check refuses the commit.

**Playbook**

- Setup: `feature-addition.md` after the change. Action: a reader follows its steps. Result: QA comes before the merge into `dev`, and reconciliation comes after it.

**Vocabulary**

- Setup: the Markdown files under `packages/factory/` and `docs/spec/`, the ledger code and the error messages of `dispatch`. Action: a search for the seven old terms runs. Result: it finds them only in file names.

## Guiding Rule

Every run has an end, and both ways of driving it reach that end through the same checks.
