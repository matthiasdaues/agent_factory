---
title: Dispatch Contract
category: implementation
enforcement: dispatch-prompt clause (human/agent-authored discipline) — not mechanically gate-checked
version: 1.5.0
---

# Dispatch Contract

This file sets two things for any agent that starts its own sub-agents: how it tells them where to send their reports, and how large one dispatch may get before the agent must split it and commit between steps. [branching-policy.md](branching-policy.md) covers a different part: the branches and worktrees that a dispatch uses. This file covers the messages between agents and the size of a dispatch. The dispatch step of any agent cites both files together.

## Project-Specific Rules

The short versions of these rules are in [rules.md § Dispatch](../rules.md#dispatch).

### What A Research Assignment Contains

Research orchestration sends a Factory request, never a tool call written for
one vendor's CLI. Every assignment states:

- `agent` — the Factory agent role that is responsible for the task;
- `tier` — the Factory model tier (`economy`, `standard`, or `strong`);
- `task` — one assignment with clear limits, its inputs, and the conditions
  under which it is finished;
- `output` — the output path that belongs to this assignment alone; and
- `independent_session` — whether the task must run as a separate agent
  identity in a separate session.

Each assignment that runs at the same time as others has its own output path.
A wave must not dispatch two assignments that can write the same file.

Before dispatch, the orchestrator checks that the CLI can do what the research
mode needs:

1. Every mode needs access to the required sources. If that access is
   missing, the research run stops before planning or source gathering.
2. Falsification mode must be able to set up the separate agent identities
   that the role-separation policy requires. If it cannot set them up, the run
   stops. It must not merge conflicting roles into one session.
3. Survey mode does not need separate sessions. If the CLI cannot run a
   limited number of agents in parallel, source gathering may run the same
   assignments one after another instead of as a wave, each with its own output.

The active CLI turns the request into the command it has installed:

| CLI                | How it starts a separate session | How it runs a limited parallel batch      |
| ------------------ | -------------------------------- | ----------------------------------------- |
| Claude Code        | native subagent dispatch         | native concurrent subagent dispatch       |
| GitHub Copilot CLI | native custom-agent dispatch     | native concurrent custom-agent dispatch   |
| Codex              | generated native custom agent    | parallel native-agent threads             |
| Pi                 | `run_agent` extension            | `dispatch_wave` for file-disjoint outputs |

The command differs from one CLI to the next. The assignment fields, the
capability checks, the rule that each output has one owner, and the
role-separation rules stay the same.

### Where Sub-Agents Send Their Reports

An agent that starts its own sub-agents must give each one **an instance ID that the system can resolve** as the address for its report. It must never give its own agent *type* name. A type name (for example `reconciliation-agent`) names a role, not a recipient that the system can route a message to. A reply sent to a type name cannot reach the specific instance that started the sub-agent. The reply gets lost and shows up in whatever session is listening, and someone has to pass it on by hand.

Every dispatch prompt for an agent that may start sub-agents contains this clause, word for word:

> If you start sub-agents, give each one **your resolvable instance ID** as the address for its report. Never give your agent *type* name. Put this sentence, word for word, in each sub-agent's prompt: "Report your result to instance `<PARENT_INSTANCE_ID>`." Do not wait forever for a sub-agent's reply. If a sub-agent refuses work outside its scope or does not answer, do the work yourself instead of waiting.

The case behind this rule: in the 2026-07-12 session, a reconciliation-agent instance addressed its own sub-agents by type name. Their replies got lost and showed up in the orchestrating session, where someone passed them on by hand. The parent waited without end for a reply that was never going to come, until someone told it to stop waiting.

### Fresh Agent Or Inherited Context

A child agent either starts fresh, with only the task it is given, or it
receives the parent's whole conversation. Passing on the conversation costs
more the later it happens: in one measured session, early children that
received the conversation used about 80,000 tokens each, late ones 550,000 to
600,000. A child that starts fresh costs the same at any point.

So by default the parent starts a fresh agent and gives it a brief file. A
child receives the conversation only when it needs the conversation itself:
what the user said, meant, or rejected, before anyone wrote it down. After a
context compaction, the parent always starts fresh agents, because a written
brief holds more than the compaction summary.

How each CLI starts the two kinds:

| CLI            | Fresh agent                                                | Inherited context          |
| -------------- | ---------------------------------------------------------- | -------------------------- |
| Claude Code    | `Agent` tool with a named agent type, or `general-purpose` | `subagent_type: "fork"`    |
| OpenAI Codex   | a native custom agent from `.codex/agents/`                | none; every child is fresh |
| GitHub Copilot | `@agent-name`, default `general-purpose`                   | none; every child is fresh |
| Pi             | the `run_agent` tool, or `dispatch-wave` for a wave        | none; every child is fresh |

Where every child starts fresh, the brief file is the only way to pass on what
the session knows.

### Brief File

Before the parent starts a fresh agent, it writes the brief to
`.current-work/<branch>/briefs/<task>.md` in the main checkout. It never writes
the brief to `/tmp`, because the system can empty that folder. The prompt says
only: "Read `<absolute brief path>` and follow it." Scratch files go to
`.current-work/<branch>/scratch/<agent-or-story>/` in the main checkout, never
into a worktree.

A brief contains:

1. **Goal.** The result the child delivers, in a form someone can check.
2. **Ownership.** The one file or path the child may change, written as "You
   own ONLY `<path>`." Two children that run in parallel never own the same file.
3. **Decisions.** The path of the decision ledger or Decisions table that
   records what the session has already decided. The parent updates that
   record before each round.
4. **Inputs.** The documents to read, with the sections to read where the
   whole file is not needed. Factory files go by absolute path under
   `<main checkout>/.agent-factory/factory/`, because a linked worktree has none.
5. **Output.** The report format, its length limit, and the instance ID to
   report to (see Where Sub-Agents Send Their Reports).
6. **Stop conditions.** When the child stops and asks instead of deciding.

If a dispatch packet or story file already contains these points, it is the
brief. The parent then names that file instead of writing a second one.

### Limit The Size Of A Dispatch And Commit Between Rounds

A single dispatch that tries to cover the whole codebase in one pass ("relentless weeding of the whole codebase," "reconcile everything") is also the dispatch most likely to work from an outdated base for the longest time before anyone checks it. It is also the one most likely to be stopped mid-run by an API spend limit.

- **Limit the scope of one dispatch.** Split a task that covers the whole codebase into one dispatch per module or per directory. Each of these can be checked and merged on its own through [branching-policy.md § Pre-Merge Diff Check](branching-policy.md#pre-merge-diff-check). A smaller dispatch costs less when it fails, and it is easier to confirm that its diff stays in scope.
- **Commit long tasks between rounds.** A dispatch that must stay large commits its work after each round instead of keeping everything uncommitted until the end. If the spend limit stops the dispatch mid-round, the resume loses only that round's work, not the whole dispatch.

The case behind this rule: in the 2026-07-12 session, the orchestrator-weeding dispatch and the doc-reconciliation dispatch each hit the org API spend limit several times, at 300k–465k tokens per resume cycle. Both were single dispatches that covered the whole codebase.

### Model Tier And Wave Size

A sub-agent **uses the model of the session that dispatched it, unless the dispatch sets a tier explicitly**. A strong-tier session that starts dozens of sub-agents without setting a tier pays the highest rate for every one of them. That is the largest cost you can avoid when you start many sub-agents, and the quickest way to reach the org spend limit.

- **Set the tier for each dispatch to the cheapest one that can do the work.** Keep the strong tier for the few sessions that are really hard (deep synthesis, a deciding adversarial judgement). Send mechanical and structured sub-agents — evidence gathering, writing to a fixed schema, review that follows a set protocol — to economy or standard. Do not let a large batch of sub-agents get the strong tier because nobody set a tier.
- **Limit a wave of parallel sub-agents to a small number (default six).** The platform's limit on parallel sub-agents (e.g. 20) caps how many run at once, not how much they spend. A wave of 20 can use up the monthly spend limit in one go. A spend limit or an infrastructure failure then hits while agents are writing, and whole sessions are lost at once. A wave of six fails cheaply, and its failures cost at most six sessions to run again.
- **Estimate the cost before you start.** Before a wave, state a rough cost — sessions × tier × typical tokens — and check it against the remaining budget. If it is more than the budget allows, split the work across waves. Combine this with the scope limit and the commits between rounds described above, so that a resume loses only the last wave.

The case behind this rule: the binder-to-OCR research run dispatched ~60–80 research and review sub-agents. All of them used the strongest tier, in waves of up to 20. The run hit the org monthly spend limit again and again. Several agents finished their analysis but were stopped at the write step, so the work had to be run again from the start. Sending these sub-agents to standard or economy in waves of six would have cut the spend several times over and made each failure cheap. See [agent-dispatch-token-efficiency.md](../../../../docs/proposals/implemented/agent-dispatch-token-efficiency.md) and [research-workflow-efficiency-and-atomicity.md](../../../../docs/proposals/implemented/research-workflow-efficiency-and-atomicity.md).

### Tier Rubric

The tier table applies the first rule that matches. This table is the one source for tier suggestions. Other docs should link to it, not repeat it.

| Order   | When                                                                                  | Suggested tier | Notes                                                                |
| ------- | ------------------------------------------------------------------------------------- | -------------- | -------------------------------------------------------------------- |
| 1       | Risk domains (in Constraints) include `security`, `privacy`, or `data_integrity`      | `strong`       | Risk domains from the fixed list win over every weaker rule.         |
| 2       | `touches` match any glob in `config/project.json`'s `safety_critical_paths` list      | `strong`       | An empty or missing list never triggers this rule.                   |
| 3       | `touches` span two or more top-level directories, or `deps` has three or more entries | `standard`     | Wider scope adds coordination cost, but not enough to need `strong`. |
| 4       | `touches` stay within one top-level directory                                         | `economy`      | Stories with a narrow scope can stay cheap.                          |
| default | No earlier rule matches                                                               | `standard`     | Use the middle tier when no stronger or cheaper rule applies.        |

### Check Sub-Agent Reports Against The Repository

A sub-agent's success report is a claim, not proof. Before you treat a dispatched piece of work as done, check it against what you can see in the repository — the branch tip and `git log`, the actual test run, and the automated checks that the dispatch script runs. Never rely on the sub-agent's own report alone.

For an automated implementation dispatch, the script runs these checks:

1. `dispatch prepare-wave` / `dispatch prepare-story` record the declared base SHA and run `verify-base` **before** the developer-agent is started.
2. `dispatch verify-story <story-id> --sha <sha>` confirms that the reported commit object exists and belongs to the expected story branch.
3. `dispatch merge-story <story-id>` runs `premerge-check <target> <branch> --scope ...` right before the merge, then runs the post-merge test command.

`dispatch refresh-story <story-id>` merges the invocation branch into the story branch inside the story's worktree. Run it when the invocation branch has moved, for example after another story of the wave merged. It refuses a worktree with uncommitted changes and a worktree on another branch. After an interrupted `merge-story` it refuses and tells you to run `merge-story` again. On a conflict it aborts the merge and blocks the story. `merge-story` runs the same step before `premerge-check`.

If any of these checks fails, the report is false or incomplete, or the work ended up somewhere you did not expect. Find out why before you merge or close the story.

### Do Not Start A Second Agent While The First Still Runs

Do not start a new agent for a role while an earlier instance of that role is
still running. The earlier instance cannot be cancelled. It runs until it
finishes or fails, uses tokens against an outdated state, and produces output
that will be thrown away. Wait for the earlier instance to finish (or fail),
then start the new one.

The case behind this rule: the 2026-08-17 bausteinsicht spec review started a
second-pass spec-review-agent while the first-pass instance was still running.
The first instance kept going, hit the spend limit, recovered, and used
~217k tokens to produce findings from the state before the fixes. Nobody used them.

### A `run_agent` Envelope Error Does Not Prove The Child Failed

A `run_agent`/`dispatch_wave` result reported as `child result envelope invalid` means the parent could not read the child's final message. It does not prove that the child failed.
The child saves and commits its main artifacts *before* it sends its final
message. So the error can appear while the work is already done and committed
(BUG-0008). Before you dispatch again after such an error, run:

```bash
git log --oneline -5     # fresh commit from the child = work completed
.agent-factory/factory/scripts/verify-base <target> [--expect-base <sha>]
# check the child's declared artifact_paths exist
```

If the child committed its outputs, do **not** retry. Treat the dispatch as
complete, review the committed artifacts, and dispatch again only if the
artifacts really fall short. A blind retry wastes a full agent run and risks
the spend-limit failures described above.

The case behind this rule: in the 2026-08-06 session, `run_agent` reported this
error on 8 of 9 reconciliation and planning dispatches, yet the child had
committed real work every time (`50b307f`, `8abf5cd`, `04ba170`, `35229f2`).

The case behind this rule: in the 2026-07-21 session a developer-agent committed on an outdated worktree base that was missing 144 commits and reported "7 passed". `premerge-check` blocked the merge, and a direct git check showed that the report was false.

### Finish Every Wave Before The Next One Starts

Stories that touch different files run in parallel within a wave. That parallel work is what makes the dispatcher fast. The rule applies between waves, not within them: **every story in a wave must reach a final state before the next wave starts**. A final state is a verified merge or an explicit blocked or failed record in the dispatch ledger.

This stops wave N+1 from being dispatched against an outdated state, and the waves still run their stories in parallel. The wave size limit from [Model Tier And Wave Size](#model-tier-and-wave-size) (default six) still applies within each wave.

### What Each Story Must Reach Before The Next Wave

Every story in a wave must reach a final state — a merged commit on the target branch, or an explicit blocked or failed record — before the next wave starts. `prepared` is the state a story must have before its agent is started: the story branch and worktree exist, the declared base SHA is recorded, the step manifest exists, and the dispatch script has already run `verify-base` successfully. "Final state" means:

1. The story reached `dispatched` only after the dispatcher recorded the handoff around the actual start of a subagent.
2. The commit SHA that the story reported passed `dispatch verify-story`.
3. `dispatch merge-story` ran `premerge-check --scope ...`, the merge finished, and the post-merge tests passed, OR the story was recorded as blocked or failed with a reason.
4. The story file's `status` field is updated in the same commit that delivers the implementation (for done) or in a separate commit only for the status change (for blocked or failed).

No new wave may start while any story from the previous wave has no final state. This stops later waves from being dispatched against bases that grow more and more outdated.

### Story Status Commit Rule

The story file's `status` field must be set to `done` in the **same commit** that delivers the story's implementation, not in a separate cleanup commit later. For blocked or failed stories, the status change may go in a separate commit, but that commit must happen before the next story is dispatched.

This keeps the backlog file in line with the repository: if the commit is there, the status is `done`; if the status is `done`, the commit is there.

### Spec-Feedback Rows After A Merge

After a story merges, the implementation agent handles each row of the story's spec-feedback report, `docs/spec/work/spec-feedback-<story-id>.md`. It does this in two passes:

1. The implementation agent dispatches the owner of each `open` row. The owner is the agent in the row's Owner column. The owner changes the artifact and sets the row to `fixed`.
2. The implementation agent then dispatches the owner's reviewer for each `fixed` row. The reviewer is the `reviewed_by:` entry in the owner's declaration that matches the row's artifact. The reviewer sets the row to `confirmed` or `rejected`.

A row about an artifact without `reviewed_by:`, such as a QA strategy or an ADR, gets no reviewer and closes at `fixed` (DEC-35).

When the reviewer is the stakeholder, the implementation agent dispatches no reviewer. The owner shows the fix to the stakeholder in a session. The agent that ran the session sets the row to `confirmed` or `rejected` on the stakeholder's behalf. Until that session, the row stays `fixed`.

A reviewer sets `rejected` when the code breaks an accepted requirement. The reviewer that rejects the row files a `BUG` finding, `docs/findings/BUG-NNNN.md`, with `owner: developer-agent`. When the stakeholder rejects, the agent that ran the session files the `BUG` finding. A `rejected` row does not block the wave. The implementation agent states this rule in the brief of each owner and each reviewer.

### Manual Mode

Manual mode (`--manual`) turns off all automated dispatch tooling. No dispatch scripts, no ledger, no automated SHA checks, no waves. The implementation-agent dispatches stories one at a time to developer-agents with `--no-stage --no-commit`. The human reviews, commits, and pushes. A code-review-agent reviews each committed story before the next dispatch. When the review finds defects, the implementation-agent dispatches a fresh developer-agent with the findings to fix them. The human commits the fixes.

Manual mode has no waves, so the spec-feedback row rule applies to each story. After the human commits a story, the implementation agent handles the story's report as [Spec-Feedback Rows After A Merge](#spec-feedback-rows-after-a-merge) describes. The human does not close a story while its report has an `open` row, or a `fixed` row about an artifact on the core list. The core list is `rulebooks/core-artifacts.yaml`. When each story closes, the implementation agent routes the open `QA` findings, as step 6 of the automated workflow does after `close-wave` (CAO-G31).

The following sections do not apply in manual mode: Dispatch Ledger, Finish Every Wave Before The Next One Starts, What Each Story Must Reach Before The Next Wave, Wave Closeout Record, Story Status Commit Rule, QA In A Worktree Checks A Different Copy.

### Dispatch Ledger

The dispatch ledger applies to **automated mode only**.

The dispatcher must keep a machine-readable ledger at `.current-work/<feature-branch>/dispatch-ledger.yaml` that tracks every story in the current dispatch. **Only scripts write the ledger**: agents read it to resume and to report, but only `.agent-factory/factory/scripts/dispatch` subcommands change it. The ledger is saved after each state change that the script can observe. It lives under the git-ignored `.current-work/` and is never committed.

Schema:

```yaml
---
mode: automated
closed: false | true
invocation_branch: <branch-name>
branch_root: <40-char SHA>
branch_head: <40-char SHA>  # updated after each merge or wave closeout
stories:
  - id: <story-id>
    branch: <feature-branch-name>
    worktree: <worktree-path>
    declared_base: <40-char SHA>
    verify_base: pass | fail | pending
    premerge_check: pass | fail | pending
    commit_sha: <40-char SHA or null>
    merge_sha: <40-char SHA or null>
    status: pending | prepared | dispatching | dispatched | done | blocked | failed
    wave: <wave-number>
    reason: <null or explanation for blocked/failed>
```

The ledger keeps the dispatcher's state from one session to the next. On resume, the dispatcher reads it to find out which stories finished, which failed, which are only prepared, and what the current base SHA is. It does not guess the state from `git log`.

### Wave Closeout Record

At the end of each wave (even a wave with one story), the dispatcher calls `dispatch close-wave <wave>`. The script then adds a short summary of the wave to the same ledger:

1. Stories finished in this wave, with merge SHAs.
2. Stories blocked or failed in this wave, with reasons.
3. Stories that are ready next (computed from the updated dependency graph).
4. Current branch head SHA.

This record is not a separate file. It is a YAML list under the `waves:` key in the dispatch ledger, with one entry added after each wave:

<!-- yaml-excerpt -->

```yaml
waves:
  - number: 1
    completed:
      - id: ST-0101
        merge_sha: <40-char SHA>
    blocked: []
    failed: []
    next_ready:
      - ST-0102
      - ST-0103
    branch_head: <40-char SHA>
```

## Close

A dispatch that starts but never ends leaves things behind. Every dispatch must end as either completed or abandoned, with its worktrees removed, its branches handled according to their final state, and the ledger saved.

### Completed Close

The dispatch finished successfully: all stories in the wave reached a final state (merged, or blocked with a recorded reason). To close a completed dispatch:

1. Check that every story in the dispatch has a final status in the ledger — `done` (merged), `blocked`, or `failed`.
2. Run `git worktree prune` to remove references to worktrees that no longer exist.
3. For each worktree that belongs to the dispatch:
   - If the story's branch was merged into the target: run `git worktree remove` and `git branch -d` on the story branch (safe delete — the commit is already on the target branch).
   - If the story's branch is blocked: record the reason in the ledger and leave the branch and worktree for a person to resolve. The developer responsible for the block decides whether to resume or abandon it.
4. Save the final state of the ledger.

The main point: **merged branches are safe to delete** (the work is on the target branch), **blocked branches stay where they are** (the developer may resume), and the ledger keeps the reason for later.

### Abandoned Close

The dispatch was abandoned before it finished, and the work is not being merged. To close an abandoned dispatch:

1. Record the reason in the ledger: add an entry under `abandonment:` with the reason (e.g., "deprioritized", "replaced by alternative approach", "blocked by external dependency"). If no ledger exists, create one with all stories set to `abandoned` and the reason.
2. For each worktree that belongs to the dispatch: run `git worktree remove --force` and `git branch -D` (force-delete the branches, because the work is abandoned and nobody will resolve it by hand).
3. Save the ledger.

## QA In A Worktree Checks A Different Copy

QA that runs inside a story worktree tests against `packages/factory/` (source), because the worktree shares the repository's source tree. Pre-commit hooks in the main checkout, however, load scripts and tests from `factory/` (the installed copy). These are two separate directory trees, and their content can differ: `packages/factory/` always matches the branch, while `factory/` holds whatever version `update-factory` last copied there.

When a dispatch changes files under `packages/factory/`, QA can pass in the worktree while the post-merge test suite fails in the main checkout, because the installed copy is out of date.

**What to do.** Before the last `dispatch merge-story` of any wave that changed files under `packages/factory/`, the dispatcher (or stakeholder) must run `.agent-factory/factory/scripts/update-factory` on the main checkout to copy the source into the installed copy. This is a manual step; no automated hook does it yet.

## Enforcement

People and agents follow these rules themselves; no git hook or lint check enforces them. An agent chooses how to address a sub-agent, and a dispatcher decides how to split the scope, while it writes its own prompt, before any tool call that a hook could catch. In automated mode, the automated implementation dispatch adds a stricter rule at run time: only scripts write the ledger under `.current-work/`, and the dispatcher must move a story from state to state through `dispatch init`, `dispatch prepare-wave` / `prepare-story`, `dispatch mark-dispatching`, `dispatch mark-dispatched`, `dispatch verify-story`, `dispatch merge-story`, and `dispatch close-wave` instead of recording the state by hand. In manual mode, none of these script commands apply. See [implementation-agent.md § Workflow — Automated Mode](../../agents/implementation-agent.md#workflow--automated-mode) for how this works today.

## References

- [rules.md § Dispatch](../rules.md#dispatch)
- [branching-policy.md](branching-policy.md) — the branch and worktree part of the dispatch contract (Verify-Base Preamble, Declared Base SHA, Pre-Merge Diff Check)
- [implementation-agent.md § Workflow — Automated Mode](../../agents/implementation-agent.md#workflow--automated-mode) — the dispatcher that applies this contract today
- [reconciliation-agent.md](../../agents/reconciliation-agent.md) — the agent whose incident led to the rule in Where Sub-Agents Send Their Reports
- [docs/reviews/retro-2026-07-12.md](../../../../docs/reviews/retro-2026-07-12.md) — the session that led to both rules
