# Feature Request: Run Lifecycle

## Summary

This proposal defines one lifecycle for a run. A run is everything the
Factory does for one feature branch, from `dispatch init` to `dispatch close`.
The lifecycle is the same on both ways of driving a run. In an orchestrated
run, the implementation agent starts stories in waves. In a run by hand, a
person gives the go for each story. The first release covers the whole lifecycle
of a run, from its start to its cleanup. It also clears the old runs in this
repository and sets one vocabulary for all living Factory documents.

## Motivation

Today a run has a start and no end. `dispatch init` writes a ledger, the file
that tracks the stories of a run, and no command removes it. The command that
would close a run is T-0014, and it has never been built. The ledger has a
`closed` field, and no code sets it to true. So every check that asks "is a
run active?" sees old runs as live.

This repository shows the result. `.current-work/` holds 36,109 files. Six
ledgers remain from features that have merged. Thirteen worktrees besides the
primary checkout still exist, and sixteen `story/` and `feature/` branches
remain.

Three more gaps sit in the same process:

- Nobody owns the merge of the feature branch into `dev`. One line in the
  branching policy states it, and no agent step carries it out.
- A run by hand is a different process today. It has no story branches, no
  ledger and no merge step, so `premerge-check` cannot run there. The gate
  results it writes are read by nobody.
- Documents and code disagree in about fifteen places. Three sources name
  three different owners for setting `done`. At the attempt limit, ADR-0012
  marks a story `blocked`, while the implementation agent marks it `failed`.
  ADR-0012 says the developer agent never runs a gate, and the developer
  agent's instructions tell it to run the gates by hand. The spec says a red
  suite after a merge reverts the merge commit, and the code resets the
  branch.

The story workflow proposal answered some of these questions for one part of
the process. Its open points all lead back to the run as a whole. So this
proposal defines the whole run, and the story workflow is one of its
sections.

## Core Principles

- One frame for both ways. A run by hand has the same feature branch, ledger,
  story branches, merge command and end as an orchestrated run.
- The merge decides `done`. A story is `done` when it has merged into the
  feature branch, and only `dispatch merge-story` sets that status.
- No stored result decides a merge, with one stated exception for mutation
  testing. The merge check runs the gates again at the branch head.
- Every piece of state has a reader. A ledger field that no command reads
  does not exist.
- A run ends. It ends finished or dropped. Afterwards, only unmerged branches
  and named stashes of untracked files remain, and the person handles both.
- A person decides at the points that need a person. By hand, the person
  watches each step and can undo a wrong one. The git guardrail refuses only
  the commands that destroy work.
- Every mechanism works in all five agent tools: Claude Code, Codex, Copilot,
  pi and OpenCode.

## Design

### The run

A run belongs to one feature branch, such as `feature/login`, cut from `dev`.
Its ledger lies at `.current-work/<feature-branch>/dispatch-ledger.yaml` and
is ignored by git. A run is active while its feature branch has a ledger.
Every check that asks whether a run is active reads only the ledger of the
branch it works on.

A run moves through these steps:

1. **Start.** `dispatch init` checks the stories of the run and writes the
   ledger. See [Starting a run](#starting-a-run).
2. **Waves of stories.** Each story runs the
   [story workflow](#the-story-workflow) on its own story branch,
   `story/<id>`, cut from the feature branch. It ends with
   `dispatch merge-story`.
3. **Wave close.** After each wave, `dispatch close-wave` handles the drift
   between code and documents. The next wave starts only after that close.
   See [Wave close](#wave-close).
4. **Feature checks.** After the last wave, the code-review agent reviews the
   whole feature, and then the QA agent explores it. Each blocking finding
   from those reviews becomes a unit of work in a new wave.
5. **Merge into `dev`.** A person merges the feature branch into `dev` after
   `premerge-check dev <feature-branch>` passes. See
   [Feature checks and the merge into dev](#feature-checks-and-the-merge-into-dev).
6. **Reconciliation.** The reconciliation agent runs on `dev`, one feature at
   a time, outside the run.
7. **Close.** `dispatch close` removes the state of the run. See
   [Close](#close).

Several runs may be active at the same time, one per feature branch. An
orchestrated run works in its own worktrees. A run by hand works in the
primary checkout, so only one run by hand can be active at a time.

Reconciliation sits outside the run for a reason. It edits shared documents
such as the scope map, the glossary and the arc42 chapters. Two parallel runs
that each reconciled on their own feature branch would conflict over those
files at the merge into `dev`. On `dev`, reconciliation also sees all merged
code, not only one feature.

### Two ways to drive it

The two ways share every step above. They differ in three points:

| Point                         | Orchestrated                                | By hand                                    |
| ----------------------------- | ------------------------------------------- | ------------------------------------------ |
| How stories run               | in parallel waves, each in its own worktree | one at a time, in the primary checkout     |
| When a story starts or merges | when the implementation agent is ready      | after the person gives the go              |
| What a wave holds             | the stories the wave plan assigns           | exactly one story, closed after that story |

The ledger field `mode` records the way, as `orchestrated` or `by-hand`.
`dispatch` and the implementation agent read it.

By hand, the story branch and the feature branch share the primary checkout.
So `dispatch prepare-story` checks out the story branch, and
`dispatch merge-story` checks out the feature branch before it merges.

Each `dispatch` subcommand has one place on each way:

| Subcommand                                | Orchestrated         | By hand                                         |
| ----------------------------------------- | -------------------- | ----------------------------------------------- |
| `init`                                    | implementation agent | implementation agent, after the go              |
| `plan`, `prepare-wave`                    | implementation agent | see Open Questions                              |
| `prepare-story`                           | implementation agent | implementation agent, after the go              |
| `mark-dispatching`, `mark-dispatched`     | implementation agent | implementation agent                            |
| `verify-story`                            | implementation agent | implementation agent                            |
| `escalate`, `mark-failed`, `mark-blocked` | implementation agent | implementation agent                            |
| `re-dispatch`                             | implementation agent | implementation agent, after the person's prompt |
| `refresh-story`                           | implementation agent | not used                                        |
| `merge-story`                             | implementation agent | implementation agent, after the go              |
| `close-wave`                              | implementation agent | implementation agent, after each story          |
| `add`                                     | implementation agent | implementation agent, after the go              |
| `return-story`                            | person               | person                                          |
| `close`                                   | see Open Questions   | person                                          |
| `close --drop`                            | person               | person                                          |

`refresh-story` merges the feature branch into a story branch when the
feature branch moved while the story ran. By hand, only one story runs at a
time, so the feature branch does not move under it.

`dispatch` has no `mark-done` subcommand. Only the merge sets `done`.

The merge of the feature branch into `dev` is not a `dispatch` subcommand. A
person runs `git merge` on both ways.

### Guidance by hand

A person who drives a run by hand needs to know what to decide and when. So
the implementation agent stops at each point where a person decides:

- before a story starts;
- before a story merges;
- when a story stops as `failed` or `blocked`;
- before the merge into `dev`.

At each stop, the agent shows the output of `premerge-check`, the findings of
the story with their status, and the head of the branch. It names the command
it will run and waits for the go. On the go, it runs the command itself and
reports the result.

Only the person runs three commands: `dispatch return-story`,
`dispatch close` and `dispatch close --drop`. The person also runs the
`git merge` into `dev`. In Claude Code, the person types the command with
`!`. In the other tools, the person runs it in a terminal.

A run by hand relies on the person watching. If an agent merges a story too
early, the person sees it and moves the branch back. The git guardrail does
not stop an agent from starting or merging a story. It refuses only the two
commands that destroy work; see [The git guardrail](#the-git-guardrail).

### Starting a run

`dispatch init --stories <ids>` starts a run on both ways. `--stories` is
required, because the dependency check needs the list.

`init` checks the dependency tree once, against the backlog. It refuses a
story whose dependency outside the run is not done, and it names that
dependency. Take ST-0360, which depends on ST-0300 from an earlier feature.
If ST-0300 is not done, `init` refuses ST-0360. The person then finishes
ST-0300 first or leaves ST-0360 out of the run. If ST-0300 is done, ST-0360
joins the run.

During the run, `dispatch` reads only the ledger for dependencies. A story
starts only when every dependency inside the run is `done`. `prepare-wave`
and `prepare-story` both check every dependency. A dependency outside the run
was checked at the start and does not count again. So nothing in the middle
of a run needs to know where stories are stored. A Jira backlog changes only
the check at the start; `docs/proposals/jira-backlog-projection.md` defines
that source.

In an orchestrated run, `init` creates the feature branch with a worktree at
`.current-work/<feature-branch>/invocation`. By hand, `init` creates the
feature branch without a worktree, because the run works in the primary
checkout.

`init` refuses in two cases only:

- the same feature branch already has a ledger;
- the person starts a run by hand while another run by hand is active.

Two orchestrated runs on `feature/login` and `feature/search` can then both
start.

### The story workflow

Each story runs these steps on its story branch, on both ways. Take ST-0350
on `feature/login`.

1. **Start.** The implementation agent runs `dispatch prepare-story ST-0350`
   or `dispatch prepare-wave`. The command cuts `story/ST-0350` from the
   feature branch.
2. **Development.** A developer agent implements the story test first and
   commits `feat: … (ST-0350)`. It does not set `done`, and it runs no gate
   script. The pre-commit hooks give it early feedback on every commit.
3. **Code review.** The code-review agent reviews the diff of the story. It
   writes `docs/reviews/code-review-ST-0350-2026-11-20.md` and files each
   finding with `story: ST-0350`. A fresh developer agent fixes every
   blocking finding before the gates run.
4. **Gate-check step.** The implementation agent runs the gates in the
   story's checkout. For each failure, it spawns a fresh developer agent with
   the gate output. See [Attempts and stops](#attempts-and-stops).
5. **Merge.** The implementation agent runs `dispatch merge-story ST-0350`.
   The command runs `premerge-check`, merges with `--no-ff`, and sets
   `status: done` in the story file in the merge commit. It then copies
   `packages/factory` into `.agent-factory/factory` and runs the test
   command. On a merge conflict, it aborts and sets the story to `blocked`.

A blocking finding follows the rule in
[finding-classification.md, "Shared severity scale and blocking rule"](../../../packages/factory/rulebooks/conventions/finding-classification.md#shared-severity-scale-and-blocking-rule).
A finding blocks when its category is `defect` or `risk` and its severity is
`critical` or `major`. A `minor` finding lives in a register file and never
blocks.

The code-review report carries the story ID in its name, so two stories
reviewed on the same day write two different files. A second review of the
same story on the same day adds `-2` to the name. The review at the end of
the feature carries the feature branch name, with the slash replaced by a
hyphen: `docs/reviews/code-review-feature-login-2026-11-24.md`.

The full test suite can fail after a merge. Then `dispatch merge-story`
moves the feature branch back to the commit before the merge, and the story
becomes `blocked`. Take ST-0350 and ST-0351 in one wave. Both pass on their own, and
a test that uses both fails after ST-0351 merges. The merge of ST-0351 then
does not appear in the history. A revert commit would cause trouble here.
After a revert, git treats the commits of ST-0351 as merged, so a second
merge attempt would bring in nothing. The feature branch is local, so nobody
has built on the failed merge.

### The gates

The gates of a story are the checks that `premerge-check` runs before its
merge:

- `dependency-check`, always;
- `test-design-verify`, when the story has a Test Design or Prior Tests
  heading;
- `crap-score` and `mutation-testing`, as the story's `quality-gates` field
  or the `gates` section of `docs/testing.yaml` picks them;
- a security scanner, when `docs/testing.yaml` enables one.

The security scan is a deterministic gate per story, and each project
chooses whether to enable it and which scanners to run. It finds known
patterns, such as an SQL query built from user input or a leaked key. The
OWASP review of the `security-review` skill finds what needs judgment, such
as a broken permission check. It stays in QA at the feature level. The key in
`docs/testing.yaml` and the setup skill that picks the tools belong to a
separate proposal; see [Scope](#scope). `premerge-check` reruns every gate
that `docs/testing.yaml` enables, so a scanner gate runs at the merge without
a change in this proposal.

Mutation testing runs per story. The trial in `docs/proposals/mutation-gate.md`
measures how long a run takes. If it is too slow per story, it moves to the
feature level, and the rest of the run stays the same.

### Pre-commit hooks

The fast gates also run as pre-commit hooks, so the developer agent gets
feedback before the gate-check step. `dependency-check` runs as a hook when a
commit stages a source file.

`dependency-check` reads its rules from `docs/spec/dependency-rules.dsl`. A
new project has no rules file until its architecture phase writes one. In
that case, the hook prints
`dependency-check: no docs/spec/dependency-rules.dsl, skipped` and passes.
The gate at the merge does the same. A failing hook would only push people
towards `--no-verify`, and the notice keeps the gap visible on every commit.

### Attempts and stops

A story gets a fixed number of attempts to pass its gates. The first attempt
is the implementation itself. Each later attempt is a fresh developer agent
that gets the gate output. Two keys in `docs/testing.yaml` set the numbers:

| Key                        | Meaning                                  | Default |
| -------------------------- | ---------------------------------------- | ------- |
| `gates.attempts`           | attempts on the story's model tier       | 3       |
| `gates.attempts_escalated` | attempts on the stronger tier after that | 3       |

With the defaults, a story gets the first attempt and two retries on its own
tier. Then it gets three attempts on the stronger tier, six in all.

The counts live in `docs/testing.yaml` for three reasons. The file is
tracked, so the counts reach the whole team. `dispatch` and `premerge-check`
already read it. It also holds the thresholds that these attempts try to
meet. The test-strategy agent owns the file.

Every story that uses up its attempts on its own tier escalates. Two stories
in the same wave can both escalate.

A story stops in one of two states:

- `failed`: the gates still fail after the last attempt.
- `blocked`: the merge hit a conflict, the test suite failed after the merge,
  or `refresh-story` hit a conflict.

The two names tell the person why the story stopped. Both states are handled
the same way. The story waits for the person, and the implementation agent
stops and reports.

### Returning a story

The person looks at a stopped story and chooses one of two paths:

- **The root cause can be fixed.** The person fixes it and tells the agent
  to continue. The agent runs `dispatch re-dispatch`, and the story continues
  in the same run. Take ST-0350, blocked by a conflict in one file. The person
  resolves the conflict in a few minutes, and the story runs again.
- **The root cause cannot be fixed.** The person runs
  `dispatch return-story ST-0350`. The story goes back to `pending`, in the
  ledger and in the backlog.

No story that depends on a returned story may start. Only work that is
independent of it continues. The rule carries through a chain. Say ST-0351
depends on ST-0350, and ST-0352 depends on ST-0351. The person returns
ST-0350, so ST-0351 never starts, and ST-0352 waits too. A story that depends
on neither runs and merges.

At the end of the run, the returned story and the stories that wait on it are
`pending`. `dispatch close` and the feature merge check accept them, and they
stay in the backlog. Both refuse while a story is `failed` or `blocked`,
because a decision is still open.

The ledger state machine has a transition from `failed` to `pending` and one
from `blocked` to `pending`. It has no separate state for a returned story.

### Checks at the story merge

`dispatch merge-story` calls `premerge-check <feature-branch> story/<id>`.
The check runs in the story's checkout, at the head of the story branch. It
refuses the merge unless every row below passes.

| Check               | Passes when                                                                                                 |
| ------------------- | ----------------------------------------------------------------------------------------------------------- |
| Clean tracked files | no tracked file differs from the branch head, staged or not; the check names each changed file              |
| Review ran          | a code-review report for the story exists                                                                   |
| No blocking finding | no open blocking finding names the story in its `story` field                                               |
| Gates pass          | every gate passes when run again in full at the branch head; `mutation-testing` is the exception, see below |
| Scope               | every changed file lies in the scope of the story, and the number of changed files stays under the limit    |
| Existing checks     | the conflict and file-count checks of `premerge-check` pass, as today                                       |

**Gates run again in full.** The check runs each gate's full measuring
command, tests included. Take ST-0350. Its last fix commit adds an untested
function, and the coverage file dates from the gate-check step before that
commit. The measuring command of `crap-score` runs the tests again, writes
fresh coverage and scores the new function. So the merge is refused. A
second test run per story is the cost. Mutation testing is the exception. The
check reads its stored result in `.current-work/mutation-testing/<id>.json`,
because a second mutation run per story is expensive.

**Untracked files.** The gates measure the files in the folder, and the merge
takes the commits. An untracked file can make the two differ. Say a fix agent
writes `tests/test_login.py` and does not commit it. The tests would find
that file, and the merge would take a branch head without it. So before the
gates run, the check runs `git stash push --include-untracked` with a name
such as `premerge ST-0350 2026-11-20`. It runs the gates and then puts the
files back with `git stash pop`. Files that `.gitignore` covers, such as
coverage output, stay in place. If the files cannot be put back, the stash
stays, and the output names it.

**Scope.** The scope of a story holds its declared outputs, its backlog file,
its spec-feedback report and `INDEX.yaml`. It also holds the story's own
review reports, finding files and register files. A file counts as the
story's own when its name contains the story ID, or when its `story` field
names the story. These own files do not count towards the file limit. Any
other finding file is outside the scope.

**Branch names.** The check recognizes a story branch by its name. It accepts
`story/ST-NNNN` and the branch of a finding, such as `story/BUG-0090`.
Without that, a fix branch would skip the gates with `SKIP semantic-gates`.

On a pass, `premerge-check` writes `.current-work/premerge-check-ok`, keyed to
the branch head, as today.

### Wave close

`dispatch close-wave N` closes wave N. The next wave starts only after that
close succeeds.

A story's spec-feedback report lists the drift between its code and the
documents, one row per drift. For example, a row says "the glossary lacks the
term *session token*". The rows of a wave are handled at its close, not after
each merge. The implementation agent spawns the owner of each open row, such
as the domain-modeling agent, and after it a reviewer. These drift sessions
commit on the feature branch. `close-wave` refuses while any row is open, and
then it writes the wave record into the ledger.

Handling the rows at the close avoids a story merge and a drift session
committing on the same branch at once. The delay loses nothing. Both stories
of a wave start from the same base, so neither could use a fix from the
other's report. The next wave starts after the close, so it sees the fixed
documents.

By hand, each story is a wave of its own. Its rows are handled right after
the story merges, and the next story starts after that.

The wave close also routes the open `QA` findings of the wave. A `QA` finding
records what the gate-check step could not fix, such as a surviving mutant.
Where each one goes is an open question; see [Open Questions](#open-questions).

### Feature checks and the merge into dev

After the last wave closes, two steps work on the whole feature, on the
feature branch:

1. The code-review agent reviews how the stories fit together.
2. The QA agent explores the feature. It writes its Fagan, security and
   bug-hunt reports.

A finding filed at the feature level names no single story. So it carries the
field `run` with the feature branch, such as `run: feature/login`.

Each blocking finding from these two steps becomes a unit of work in the
same run. A unit of work is a story or a finding. Take BUG-0090, filed by QA
against the login form:

- `dispatch add BUG-0090` adds the open finding to the ledger as a new wave.
- The finding runs through the story workflow on `story/BUG-0090`: a fix with
  a regression test, review, gates and the merge check.
- `dispatch merge-story` sets `status: resolved` in the finding file, in the
  merge commit.

A finding already holds what the run needs from a story. Its body says what
is wrong, `artifact` says where, and `status: resolved` says when it is
finished. A finding has no dependencies, which a fix inside the run does not
need.

Before the merge into `dev`, the implementation agent runs
`premerge-check dev <feature-branch>` and shows the result. The check passes
only when all of these hold:

- every unit of work in the ledger is `done` or `pending`;
- every wave is closed;
- the review of the whole feature and the QA reports exist;
- no open blocking finding has `run` set to the feature branch or `story` set
  to a unit of work of the run;
- the full test suite passes.

Take `feature/login`. BUG-0090 carries `run: feature/login` and counts. An
open FAGAN-0071 from an unrelated earlier review also sits in
`docs/findings/`. It names neither the branch nor a story of the run, so the
check ignores it.

A person merges the feature branch into `dev` with `git merge`, on both ways.
This is the point where a feature leaves the run and joins everyone's work,
so a person stands behind it.

### Close

A run ends in one of two ways.

**Finished.** The feature branch has merged into `dev`. `dispatch close`
checks that merge, and then it:

- stashes the untracked files of each worktree before it removes that
  worktree, with a name such as `run feature/login ST-0350 2026-11-24`, and
  does not put them back;
- removes the worktrees, the ledger, the gate results, the markers and the
  briefs for agents;
- deletes each merged branch with `git branch -d`, which git allows only for a
  fully merged branch;
- lists each unmerged branch and each stash it made.

The person deletes the listed branches with `git branch -D` and decides which
stashes to keep. Git keeps stashes in the repository, not in the worktree, so
a stash survives the removal of its worktree.

**Dropped.** The person drops the feature with `dispatch close --drop`. Every
unit of work that is not `done` returns to the backlog as `pending`. The
command then removes the run's state as above.

After either close, the record of the run is the merge commits in `dev` and
the status in each story file. No other record of the run is kept. Nothing
reads a ledger after its run ends.

**Old runs.** `dispatch close --orphans` handles what earlier runs left
behind. It works the same way in every project that uses the Factory:

- It lists worktrees and branches that have no ledger. It removes the
  worktrees whose branch is merged and leaves the unmerged ones for the
  person.
- It finds ledgers whose feature branch is gone, nested ledgers
  included. It removes such a ledger when every story in it is `done`, and it
  lists every other one and leaves it.
- It ignores the `mode` field, so the old value `automated` needs no reading.

An old run whose feature branch exists closes with `dispatch close`,
like a new run.

### The ledger

Every ledger field has a command that reads it. The ledger holds:

- `mode`, as `orchestrated` or `by-hand`;
- `feature_branch`, `branch_root` and `branch_head`;
- per unit of work: its state, wave, dependencies, branch, worktree,
  `base_sha`, tier, attempts and `commit_sha`;
- the wave records, which `prepare-wave` reads to check that the previous
  wave closed.

`branch_root` is the tip of the feature branch at `init`. After a merge,
`commit_sha` holds the merge commit, and `prepare-story` reads it as the base
of the next story in a serial chain. No command needs the story's own commit
after the merge.

The ledger has no `gate_results` field, because the merge check runs the
gates again. It has no `closed` field, because a run is active exactly while
its ledger exists. The dispatch contract describes these fields under the
names the code uses.

### The git guardrail

The git guardrail checks every shell command that an agent runs, in every
session. It has one list of checks for every session. That list keeps the
checks of today, including the three worktree rules:

- a branch is created only together with a worktree;
- worktrees lie under `.current-work/`;
- a commit in a linked worktree needs the `verify-base-ok` marker.

The list also refuses agents `dispatch return-story` and
`dispatch close --drop` in every run. Both commands destroy work, and seeing
them run does not bring the work back. A wrong merge, by contrast, can be
undone.

One script, `config/hooks/block-dangerous-git.sh`, holds the checks. All five
agent tools call it, as they call `guard-human-fields` today:

- Claude Code, Codex and Copilot call the script through their hook
  configuration.
- pi's `config/extensions/block-dangerous-git.ts` is a thin wrapper that
  passes each command to the script.
- OpenCode's plugin `config/plugins/agent-factory.ts` calls the same script,
  so OpenCode gets the git guardrail.

The guardrail matches command text. An agent that builds a command from
variables can get past it. `guard-human-fields` has the same limit. The guard
stops mistakes, not a determined attempt to get around it.

### One vocabulary

The living Factory documents use these terms:

| Term                 | Meaning                                                                    |
| -------------------- | -------------------------------------------------------------------------- |
| run                  | everything from `dispatch init` to `dispatch close` for one feature branch |
| orchestrated         | the implementation agent starts stories in waves                           |
| by hand              | a person gives the go for each story                                       |
| feature branch       | the branch of a run, cut from `dev`                                        |
| story branch         | `story/<id>`, cut from the feature branch                                  |
| gate-check step      | running the gates and fixing what they report                              |
| spawn                | starting one agent                                                         |
| spec-feedback report | a story's report of drift between code and documents                       |
| primary checkout     | the repository's main folder                                               |

The word "dispatch" names only the script `dispatch`. Seven old terms do not
appear in the living documents: automated mode, manual mode, mechanized
dispatch, invocation branch, gate-check loop, drift report and main checkout.

The living documents are the Markdown files under `packages/factory/` and
`docs/spec/`. Code identifiers and error messages follow the same vocabulary.
The ledger field `invocation_branch` is `feature_branch`, the mode value is
`orchestrated`, and the error messages say "feature branch". Accepted ADRs,
superseded proposals and file names such as
`docs/spec/areas/mechanized-dispatch.md` keep their wording.

### Documents that change

A document can disagree with the code without a design question behind the
difference. In that case, the document changes to match the code. The table lists each
document and what it states afterwards.

| Document                  | What it states                                                                                                                                                 |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dispatch-contract.md`    | the ledger fields of [The ledger](#the-ledger); `dispatch close` and `--drop` as the two ends; `dispatch merge-story` copies the installed folder              |
| `branching-policy.md`     | the feature branch is cut from `dev`; `branch_root` is the feature branch tip at `init`                                                                        |
| `rules.md`                | the ledger carries no gate results and no merge record; the implementation agent runs the gates by hand too                                                    |
| `implementation-agent.md` | the subcommand table, the guidance by hand, the stops, and the order of the playbook after the run                                                             |
| `developer-agent.md`      | the developer agent never sets `done` and never runs a gate script                                                                                             |
| `code-review-agent.md`    | the report names with story ID or feature branch                                                                                                               |
| `finding-format.md`       | the field `run`, and `status: resolved` set by the merge for a finding that runs as a unit of work                                                             |
| ADR-0012                  | three attempts per tier with the defaults; a story that uses up its attempts is `failed`                                                                       |
| ADR-0029                  | drift sessions run at the wave close; `merge-story` waits for none                                                                                             |
| `mechanized-dispatch.md`  | a red suite resets the feature branch; `plan` writes waves into the ledger; the test command comes from `docs/testing.yaml`; `init` refuses per feature branch |
| `interface-contracts.md`  | the test command comes from `docs/testing.yaml`                                                                                                                |
| `state-machines.md`       | the transitions from `failed` and `blocked` to `pending`                                                                                                       |
| `crap-gate-setup.md`      | every story merges through `dispatch merge-story`, and the implementation agent runs `crap-score` on both ways                                                 |

`premerge-check` keeps its marker and the guardrail keeps its marker check
for `git merge`.

## Scope

**In the first release:**

- One frame for both ways, with the `mode` field in the ledger.
- `dispatch init` with the dependency check and the refusal per feature
  branch; no worktree for the feature branch by hand.
- The subcommand table, with `return-story`, `add`, `close`, `close --drop`
  and `close --orphans` as new subcommands, and without `mark-done`.
- `prepare-story` checking every dependency inside the run.
- The guidance by hand in the implementation agent.
- The story workflow, with review reports named by story ID.
- The merge checks of a story: clean tracked files, a review, no blocking
  finding and a full gate rerun.
- The stash of untracked files, the wider scope and the branch pattern for
  findings at the story merge.
- The keys `gates.attempts` and `gates.attempts_escalated` in
  `docs/testing.yaml`, with escalation for every story that needs it.
- Drift sessions at the wave close, and the wave close as the condition for
  the next wave.
- Feature findings with the field `run`, run as units of work.
- `premerge-check dev <feature-branch>`.
- `dispatch close`, with stashes for untracked files.
- `dispatch close --orphans`, and its run over the old runs of this
  repository.
- The `dependency-check` pre-commit hook, with the skip notice.
- The guardrail refusal of `return-story` and `close --drop`, in one script
  that all five agent tools call.
- The vocabulary, in living documents, code identifiers and error messages.
- The document changes in [Documents that change](#documents-that-change).

**Explicitly deferred (do NOT plan stories for these):**

- The security scanner hook and its key in `docs/testing.yaml`.
- The setup skill that picks the scanners per language.
  It belongs to a separate setup proposal, like `crap-gate-setup.md`, and the
  hook and the key go with it.
- Limits on repeat reviews; `docs/proposals/review-loop-cap.md` covers them.
- A Jira backlog as the source of stories;
  `docs/proposals/jira-backlog-projection.md` covers it.
- Moving mutation testing to the feature level, which waits for the trial in
  `docs/proposals/mutation-gate.md`.
- Renaming files and rewriting accepted ADRs or superseded proposals for the
  vocabulary.

## Design Details

- **Review coverage.** `premerge-check` can show that a review report exists
  and that no blocking finding is open. It cannot judge how good the review
  was.
- **The leftovers of this repository.** Six ledgers remain:
  - `brownfield-onboarding` and `bug-hunt-fixes` have no feature branch left,
    and all their stories are `done`. `--orphans` removes both.
  - `core-artifact-layout` has no feature branch left and lists ST-0344 as
    `blocked`. `--orphans` lists it. The person returns ST-0344 to the backlog
    on `dev` and then removes the ledger.
  - `finding-classification` and `counter-ids` close with `dispatch close`.
    Their feature branches exist and have merged into `dev`.
  - One ledger lies nested inside the `counter-ids-fitting` worktree, at
    `.current-work/feature/counter-ids-fitting/.current-work/feature/counter-ids-fitting/`.
    `--orphans` finds it.
  - The worktrees without a ledger, such as the six story worktrees of
    `data-model-dsl-poc`, and stray branches such as `feature/my-work` go
    through `--orphans` as well.

## Open Questions

01. **Who runs the finished close in an orchestrated run.** Take
    `feature/login`, orchestrated, just after the person merged it into
    `dev`. If the implementation agent may run `dispatch close`, the worktrees
    go at once, and untracked files land in listed stashes. If only the person
    may run it, the state stays until the person acts, as by hand. I recommend
    that the agent may run it, because the close checks the merge first and
    destroys no unmerged work. The answer settles the `close` row of the
    subcommand table.

02. **Whether `close --drop` deletes unmerged branches.** Take
    `feature/export`, dropped with ST-0370 unmerged. If `--drop` only lists
    the branch, the person deletes it with `git branch -D`. If `--drop`
    deletes it, the work of ST-0370 is gone when the command ends. The
    sources describe both. I recommend listing, because it gives the person a
    last look before work is lost. The answer settles [Close](#close).

03. **The stash in the primary checkout.** By hand, the stash at the merge
    check takes every untracked file of the primary checkout. In this
    repository, those are 15 paths, among them `poc/findings-board/` and draft
    proposals. If `git stash pop` fails, they stay in a stash named
    `premerge ST-0350 …`. Either the rule stays and the guidance warns the
    person, or the stash takes only paths the story could touch. I recommend
    the warning, because the narrower stash needs a rule for which paths
    count. The answer settles
    [Checks at the story merge](#checks-at-the-story-merge).

04. **Where the wave close sends `QA` findings.** Today the implementation
    agent routes each finding by its `owner`. A finding with
    `owner: planning-agent` waits for a story. The other reading sends every
    `QA` finding to the test-strategy agent, which then receives findings
    that belong to the planning agent. I recommend routing by owner, because
    the code works that way. The answer settles [Wave close](#wave-close) and
    the row for `implementation-agent.md`.

05. **How often the implementation agent runs `close-wave`.** `close-wave` is a
    script and cannot spawn an agent. Take wave 1 with one open row in the
    report of ST-0350. One reading is that the first run of `close-wave`
    refuses and prints the open rows. The agent then spawns the owners and runs
    `close-wave` again. The sources do not settle this reading. I recommend that reading, because it keeps
    the spawns with the agent. The answer settles [Wave close](#wave-close).

06. **What the `quality-gates` field of a story does.** In `premerge-check`,
    the field replaces the pick from `docs/testing.yaml` and accepts only
    `crap-score` and `mutation-testing`. Take a story with
    `quality-gates: [crap-score]` while `docs/testing.yaml` enables mutation
    testing. If the field replaces the pick, mutation testing does not run. If
    it adds to the pick, both run. I recommend adding, because a story should
    not switch off a gate the project enabled. The answer settles
    [The gates](#the-gates).

07. **Which conditions of `dispatch escalate` stay.** Every story may escalate,
    so no limit per wave applies. The command also requires
    exactly one prior implementation attempt, a qualifying failure class, a
    passing `verify-base` and no scope violation. The sources do not say
    whether these stay, or whether `gates.attempts_escalated: 0` turns
    escalation off. I recommend keeping the other conditions and reading `0`
    as no escalation, because both match the meaning of the keys. The answer
    settles [Attempts and stops](#attempts-and-stops).

08. **The model tier of a finding.** A finding has no model tier. So a finding
    that runs as a unit of work needs a default tier, and the sources do not
    name it.
    Take BUG-0090. If the default is the economy tier, its first attempts are
    cheap and escalation covers the hard cases. I recommend the economy tier
    for that reason, matching the fallback of `dispatch escalate` today. The
    answer settles
    [Feature checks and the merge into dev](#feature-checks-and-the-merge-into-dev).

09. **The installed copy with several runs.** `dispatch merge-story` copies
    `packages/factory` into `.agent-factory/factory`. With two runs active,
    the guardrail and scripts of every session become the code of the run that
    merged last. Run A can merge a broken `block-dangerous-git.sh`, and the
    agents of run B lose the guardrail. This happens only in the Factory
    repository. I recommend copying only on `dev`, because a feature is not
    finished before its merge. The answer settles the row for
    `dispatch-contract.md`.

10. **The `dependency-check` hook in other projects.** The script starts with
    `#!/usr/bin/env -S uv run --script`, so a project without `uv` fails the
    hook. The script reads Python imports only, and "a commit stages a source
    file" has no definition. I recommend running the hook only on staged
    Python files and naming `uv` as a prerequisite. The answer settles
    [Pre-commit hooks](#pre-commit-hooks).

11. **"Run" and "playbook run".** The glossary uses "playbook run" in its
    entry "In Use", and this proposal's "run" is narrower. Either the glossary
    gets "run" as its own entry next to "playbook run", or one term covers
    both. I recommend two entries, because a playbook run spans more than one
    feature branch's work. The answer settles [One vocabulary](#one-vocabulary)
    and the glossary.

12. **Gate result files without a reader.** The gate scripts write
    `.current-work/<gate>/<id>.json` on every commit. Only the result of
    `mutation-testing` keeps a reader. Either the other gates stop writing
    these files, or the principle that every piece of state has a reader
    names them as an exception. I recommend that they stop writing them,
    because the principle then holds without an exception. The answer settles
    [Core Principles](#core-principles) and [The gates](#the-gates).

13. **Waves in a run by hand.** By hand, each story is a wave of its own, and
    `close-wave N` needs a wave number. Take ST-0350 and ST-0351, driven by
    hand. Either `dispatch plan` gives each story its own wave at the start,
    or `prepare-story` gives a story the next wave number when it starts. I
    recommend `prepare-story`, because the person may choose the order of
    stories during the run. The answer settles the `plan` row of the
    subcommand table.

## Completion Criteria

- `dispatch init` by hand creates the feature branch without a worktree. In an
  orchestrated run it creates the worktree at
  `.current-work/<feature-branch>/invocation`.
- `dispatch init` refuses a second run on the same feature branch and a second
  run by hand. Two orchestrated runs on different feature branches both
  start.
- `dispatch init` refuses a story whose dependency outside the run is not
  done, and it names that dependency.
- `prepare-story` refuses a story when any of its dependencies inside the run
  is not `done`, not only the first one.
- By hand, a story reaches `dispatched` through `mark-dispatching` and
  `mark-dispatched`, run by the implementation agent, and then merges.
- `dispatch` has no `mark-done` subcommand.
- By hand, the implementation agent stops before each start, each merge, each
  stopped story and the merge into `dev`. It shows the `premerge-check`
  output, the findings with status and the branch head, names the command,
  and waits for the go.
- A developer agent never sets `done` and never runs a gate script.
  `dispatch merge-story` sets `status: done` in the merge commit.
- A red test suite after a story merge leaves the feature branch at the
  commit before the merge, and the story is `blocked`.
- With the defaults, a story that keeps failing its gates gets three
  attempts on its tier and three on the stronger tier. Then it is `failed`. Two stories
  of one wave can both escalate.
- `gates.attempts` and `gates.attempts_escalated` in `docs/testing.yaml`
  change these counts.
- `dispatch return-story` sets a `failed` or `blocked` story to `pending` in
  the ledger and in the backlog. In the chain ST-0350, ST-0351, ST-0352, a
  return of ST-0350 keeps ST-0351 and ST-0352 `pending`, and an independent
  story still merges.
- `dispatch close` and `premerge-check dev` accept `done` and `pending`, and
  refuse `failed` and `blocked`.
- `premerge-check` refuses a story checkout with a changed tracked file,
  staged or not, and names the file.
- An untracked test file does not take part in the gate rerun and is back in
  the checkout afterwards.
- The gate rerun runs each gate's full measuring command at the branch head.
  An untested function added in the last fix commit fails `crap-score` at the
  merge.
- A story without a code-review report does not merge. A story with an open
  blocking finding does not merge. A story with only an open `minor` finding
  merges.
- The story's own review reports, finding files and register files pass the
  scope check and do not count towards the file limit.
- Two stories reviewed on the same day write two review reports with
  different names.
- `premerge-check` runs the gates on `story/BUG-0090` and does not print
  `SKIP semantic-gates`.
- `prepare-wave N+1` refuses until `close-wave N` has succeeded.
  `merge-story` does not wait for drift sessions.
- `dispatch add BUG-0090` adds the finding as a new wave, and its merge sets
  `status: resolved` in the finding file.
- `premerge-check dev feature/login` counts an open blocking finding with
  `run: feature/login` and ignores an unrelated open finding such as
  FAGAN-0071.
- After `dispatch close`, the run has no ledger, worktree, gate result,
  marker or brief. Merged branches are deleted, and unmerged branches are
  listed.
- After `dispatch close`, an untracked file from a story worktree is in a
  named stash that the close listed.
- After `dispatch close --orphans` in this repository, no ledger without a
  feature branch remains except the ones it listed.
- The ledger has a `mode` field with `orchestrated` or `by-hand`, a
  `feature_branch` field, and no `gate_results` or `closed` field.
- In all five agent tools, an agent's `dispatch return-story` and
  `dispatch close --drop` are refused.
- pi's `block-dangerous-git.ts` passes each command to
  `config/hooks/block-dangerous-git.sh` and holds no checks of its own.
- In a real OpenCode session, not a mock, the plugin refuses an agent's
  `git push`.
- In a project without `docs/spec/dependency-rules.dsl`, the
  `dependency-check` hook prints the skip notice and passes.
- No Markdown file under `packages/factory/` or `docs/spec/` uses the seven
  old terms. No code identifier or error message in `dispatch` uses
  "invocation branch" or the mode value `automated`.

## Guiding Rule

Both ways of driving a run pass the same steps and checks. Every run ends,
and only what a person chose to keep remains.
