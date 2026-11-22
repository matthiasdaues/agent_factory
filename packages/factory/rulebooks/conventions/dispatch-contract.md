---
title: Dispatch Contract
category: implementation
enforcement: dispatch-prompt clause (human/agent-authored discipline) — not mechanically gate-checked
version: 1.5.0
---

# Dispatch Contract

Governs how any agent that spawns its own sub-agents must address them, and how large a single dispatch is allowed to grow before it must be split and checkpointed. Distinct from [branching-policy.md](branching-policy.md): that rulebook governs branch/worktree mechanics for a dispatch; this one governs the dispatch's messaging contract and its size. Both are cited together from any agent's dispatch step.

## Project-Specific Rules

Canonical statements: [rules.md § Dispatch](../rules.md#dispatch).

### Research Assignment Contract

Research orchestration dispatches a logical Factory request, never a
vendor-specific tool call. Every assignment declares:

- `agent` — the Factory agent role that owns the task;
- `tier` — the Factory model tier (`economy`, `standard`, or `strong`);
- `task` — one bounded assignment with its inputs and completion conditions;
- `output` — the assignment's unique output path; and
- `independent_session` — whether the task must run under a distinct agent
  identity in a separate session.

Every concurrent assignment has a unique output path. A wave must not dispatch
two assignments that can write the same artifact.

Before dispatch, the orchestrator preflights the capabilities needed by the
research mode:

1. Required source access must be available in every mode. If it is
   unavailable, the research run blocks before planning or source gathering.
2. Falsification mode must be able to establish the independent agent
   identities required by the role-separation policy. If separate identities
   cannot be established, the run blocks; it must not collapse conflicting
   roles into one session.
3. Survey mode does not require independent sessions. If bounded parallel
   fan-out is unavailable, source gathering may fall back from a wave to
   sequential execution with the same assignments and unique outputs.

The active CLI maps the logical request to its installed invocation surface:

| CLI                | Separate session mechanism    | Bounded fan-out mechanism                 |
| ------------------ | ----------------------------- | ----------------------------------------- |
| Claude Code        | native subagent dispatch      | native concurrent subagent dispatch       |
| GitHub Copilot CLI | native custom-agent dispatch  | native concurrent custom-agent dispatch   |
| Codex              | generated native custom agent | parallel native-agent threads             |
| Pi                 | `run_agent` extension         | `dispatch_wave` for file-disjoint outputs |

The mechanism changes by CLI; the assignment fields, capability checks, output
ownership, and role-separation requirements do not.

### Sub-Agent Addressing

An agent that spawns its own sub-agents must give each one **a resolvable instance ID** to report back to — never its own agent *type* name. A type name (for example `reconciliation-agent`) names a role, not a routable recipient; a reply addressed to it cannot be delivered back to the specific instance that sent the sub-agent out; it strands, and surfaces to whatever session is listening instead, requiring a manual relay.

Every dispatch prompt that may itself spawn sub-agents carries this clause, verbatim:

> If you spawn sub-agents, give each one **your resolvable instance ID** as the address to report back to — never your agent *type* name. Include, verbatim, in each sub-agent's prompt: "Report your result to instance `<PARENT_INSTANCE_ID>`." Do not block indefinitely waiting on a sub-agent's reply: if a sub-agent declines out-of-scope work or does not respond, do the work yourself rather than waiting.

Motivating example: a reconciliation-agent instance in the 2026-07-12 session addressed its own sub-agents by type name; their replies stranded, surfaced to the orchestrating session for manual relay, and the parent blocked indefinitely on a reply that was never coming until told to stop waiting.

### Fresh Agent Or Inherited Context

A child agent either starts fresh, with only the task it is given, or it
inherits the parent's whole conversation. Inheriting costs more the later it
happens: in one measured session, early children that inherited the context
used about 80,000 tokens each, late ones 550,000 to 600,000. A child that
starts fresh costs the same at any point.

So the parent starts a fresh agent with a brief file by default. A child
inherits the context only when it needs the conversation itself: what the
user said, meant, or rejected, before anyone wrote it down. After a context
compaction, the parent always starts fresh agents, because a written brief
holds more than the summary.

How each CLI starts the two kinds:

| CLI            | Fresh agent                                                | Inherited context          |
| -------------- | ---------------------------------------------------------- | -------------------------- |
| Claude Code    | `Agent` tool with a named agent type, or `general-purpose` | `subagent_type: "fork"`    |
| OpenAI Codex   | a native custom agent from `.codex/agents/`                | none; every child is fresh |
| GitHub Copilot | `@agent-name`, default `general-purpose`                   | none; every child is fresh |
| Pi             | the `run_agent` tool, or `dispatch-wave` for a wave        | none; every child is fresh |

Where every child is fresh, the brief file is the only way to hand over what
the session knows.

### Brief File

Before the parent starts a fresh agent, it writes the brief to
`.current-work/<branch>/briefs/<task>.md` in the primary checkout, never to
`/tmp`, which the system can empty. The prompt says only: "Read
`<absolute brief path>` and follow it." Scratch files go to
`.current-work/<branch>/scratch/<agent-or-story>/` there, never into a
worktree.

A brief holds:

1. **Goal.** The observable result the child delivers.
2. **Ownership.** The one file or path the child may change, written as "You
   own ONLY `<path>`." Parallel children never own the same file.
3. **Decisions.** The path of the decision ledger or Decisions table that
   records what the session has settled. The parent keeps that record
   current before each round.
4. **Inputs.** The documents to read, with sections where a whole file is
   not needed. Factory files by absolute path under
   `<primary checkout>/.agent-factory/factory/`: a linked worktree has none.
5. **Output.** The report format, its length limit, and the instance ID to
   report to (see Sub-Agent Addressing).
6. **Stop conditions.** When the child stops and asks instead of deciding.

A dispatch packet or story file that already holds these points is the brief.
The parent then names that file instead of writing a second one.

### Dispatch Scope Cap And Checkpointing

A single dispatch that tries to cover an entire codebase in one pass ("relentless weeding of the whole codebase," "reconcile everything") is also the dispatch most likely to be reasoning against a stale base for the longest before anyone checks it, and the one an API spend limit is most likely to kill mid-run.

- **Cap the scope of a single dispatch.** Split a whole-codebase task into per-module or per-directory dispatches, each independently verifiable and mergeable via [branching-policy.md § Pre-Merge Diff Check](branching-policy.md#pre-merge-diff-check). A smaller dispatch fails cheaper, and its diff is easier to certify as in-scope.
- **Checkpoint long tasks with commits between rounds.** A dispatch that must stay large commits its work between rounds rather than holding everything uncommitted until the end — a spend-limit death mid-round then loses only that round's work on resume, not the whole dispatch.

Motivating example: the 2026-07-12 session's orchestrator-weeding and doc-reconciliation dispatches each hit the org API spend limit multiple times, at 300k–465k tokens per resume cycle; both were single, whole-codebase-scoped dispatches.

### Model Tier And Wave Size

A sub-agent **inherits the dispatching session's model unless the dispatch sets a tier explicitly**. A strong-tier session that fans out dozens of sub-agents without setting a tier pays the top rate on every one — the single largest avoidable cost in a large fan-out, and the fastest route to the org spend limit.

- **Set the tier per dispatch to the cheapest that fits the work.** Reserve the strong tier for the few genuinely hard sessions (deep synthesis, a decisive adversarial judgement). Route mechanical and structured sub-agents — evidence gathering, schema-bound authoring, protocol-driven review — to economy or standard. Do not let a fan-out inherit the strong tier by omission.
- **Cap a concurrent wave at a small number (default six).** The platform's concurrent-sub-agent limit (e.g. 20) is a *concurrency* ceiling, not a *spend* ceiling: a 20-wide wave can exhaust the monthly spend limit in a single burst, and a limit or infrastructure failure then lands mid-write, losing whole sessions at once. A wave of six degrades cheaply and its deaths cost at most six sessions to re-run.
- **Estimate before you launch.** Before a wave, state a rough pre-flight cost — sessions × tier × typical tokens — as a spend gate, and split the work across waves if it exceeds the headroom. Combine with the scope cap and inter-round checkpointing above so a resume loses only the last wave.

Motivating example: the binder-to-OCR research run dispatched ~60–80 research and review sub-agents that all inherited the strongest tier, in waves up to 20 wide; it hit the org monthly spend limit repeatedly, and several agents completed their analysis but died at the write step, forcing full re-runs. Routing the fan-out to standard or economy in waves of six would have cut the spend several-fold and made each failure cheap. See [agent-dispatch-token-efficiency.md](../../../../docs/proposals/implemented/agent-dispatch-token-efficiency.md) and [research-workflow-efficiency-and-atomicity.md](../../../../docs/proposals/implemented/research-workflow-efficiency-and-atomicity.md).

### Tier Rubric

The tier rubric is first-match-wins. Use this table as the single authoritative source for tier suggestions; other docs should cite it, not restate it.

| Order   | When                                                                                  | Suggested tier | Notes                                                                    |
| ------- | ------------------------------------------------------------------------------------- | -------------- | ------------------------------------------------------------------------ |
| 1       | Risk domains (in Constraints) include `security`, `privacy`, or `data_integrity`      | `strong`       | Closed risk domains override all weaker signals.                         |
| 2       | `touches` match any glob in `config/project.json`'s `safety_critical_paths` list      | `strong`       | An empty or absent list never fires this rule.                           |
| 3       | `touches` span two or more top-level directories, or `deps` has three or more entries | `standard`     | Structural breadth raises coordination cost but not enough for `strong`. |
| 4       | `touches` stay within one top-level directory                                         | `economy`      | Narrow-scope stories can stay cheap.                                     |
| default | No earlier rule matches                                                               | `standard`     | Use the middle tier when nothing stronger or cheaper applies.            |

### Verify Sub-Agent Reports Against State

A sub-agent's success report is a claim, not proof. Before treating a dispatched unit of work as done, verify it against observable state — the branch tip and `git log`, the actual test run, and the mechanical gates that the dispatch script owns — never the self-report alone.

For a mechanized implementation dispatch, the script-enforced checkpoints are:

1. `dispatch prepare-wave` / `dispatch prepare-story` record the declared base SHA and run `verify-base` **before** the developer-agent is spawned.
2. `dispatch verify-story <story-id> --sha <sha>` confirms the reported commit object exists and belongs to the expected story branch.
3. `dispatch merge-story <story-id>` runs `premerge-check <target> <branch> --scope ...` immediately before merge, then runs the post-merge test command.

`dispatch refresh-story <story-id>` merges the feature branch into the story branch inside the story's worktree. Run it when the feature branch has moved, for example after another story of the wave merged. It refuses a dirty worktree and a worktree on another branch. After an interrupted `merge-story` it refuses and points to a rerun of `merge-story`. On a conflict it aborts the merge and blocks the story. `merge-story` runs the same step before `premerge-check`.

Any failed checkpoint means the report is false or incomplete, or the work landed somewhere unexpected — investigate before merging or closing the story.

### Do Not Supersede A Running Agent

Do not launch a new agent for the same role while a prior instance of that role
is still running. The prior instance cannot be cancelled — it runs to completion
or failure, consuming tokens against stale state and producing output that will
be discarded. Wait for the prior instance to complete (or fail), then launch the
replacement.

Motivating example: the 2026-08-17 bausteinsicht spec review launched a
repeat-pass spec-review-agent while the first-pass instance was still running.
The first instance continued, hit the spend limit, recovered, and consumed
~217k tokens producing findings from pre-fix state that were never used.

### `run_agent` Envelope Error Is Not Proof Of Failure

A `run_agent`/`dispatch_wave` result reported as `child result envelope invalid` is a final-message *handshake* failure, not proof the child failed.
The child persists and commits its canonical artifacts *before* emitting its
final message, so the envelope-parse error can surface while the work is
already complete and committed (BUG-0008). Before re-dispatching after any
such error:

```bash
git log --oneline -5     # fresh commit from the child = work completed
.agent-factory/factory/scripts/verify-base <target> [--expect-base <sha>]
# check the child's declared artifact_paths exist
```

If the child committed its outputs, do **not** retry — treat the dispatch as
complete, review the committed artifacts, and only loop if the artifacts are
truly deficient. Retrying blindly wastes a full agent run and risks the
spend-limit death pattern above.

Motivating example: the 2026-08-06 session saw `run_agent` report this
envelope error on 8 of 9 reconciliation/planning dispatches, yet the child had
committed real work in each case (`50b307f`, `8abf5cd`, `04ba170`, `35229f2`).

Motivating example: in the 2026-07-21 session a developer-agent committed on a stale worktree base missing 144 commits and reported "7 passed"; `premerge-check` blocked the merge, and a direct git check exposed the false report.

### Wave Boundary As Hard Gate

File-disjoint stories fan out in parallel within a wave — that concurrency is the dispatcher's strength. The constraint is between waves, not within them: **the next wave launches only after the wave record exists**. `dispatch close-wave` writes it once every unit of work of the wave is `done`, `blocked`, `failed` and stopped, or `pending` and held back by a return, and once the wave's drift rows are handled. `dispatch prepare-wave` and `dispatch prepare-story` refuse until the previous wave has its record (BR-113).

This eliminates the drift pattern (wave N+1 dispatching against stale state) without sacrificing the throughput of parallel fan-out. The concurrent wave cap from [Model Tier And Wave Size](#model-tier-and-wave-size) (default six) still applies within each wave.

### Hard Checkpoint Per Story

Every story in a wave merges or stops before `dispatch close-wave` writes the wave record, and the next wave launches only after that record exists, as [Wave Boundary As Hard Gate](#wave-boundary-as-hard-gate) defines. A failed story with a retry left has not stopped, so it keeps its wave open (BR-062, BR-113). `prepared` is the required pre-spawn state: the story branch/worktree exists, the declared base SHA is recorded, the step manifest exists, and the dispatch script already ran `verify-base` successfully. A story has merged or stopped when:

1. The story reached `dispatched` only after the dispatcher marked the handoff around a real subagent spawn.
2. The story's reported commit SHA passed `dispatch verify-story`.
3. `dispatch merge-story` ran `premerge-check --scope ...`, the merge completed, and the post-merge tests passed, OR the story stopped as `blocked`, or as `failed` with no retry left, with a reason.
4. The story file's `status` field is updated in the same commit that delivers the implementation (for done) or in a dedicated status-update commit (for blocked/failed).

No new wave may launch while the prior wave has no wave record. This eliminates the drift pattern where later waves dispatch against progressively staler bases.

### Story Status Commit Rule

The story file's `status` field must be updated to `done` in the **same commit** that delivers the story's implementation — not in a separate housekeeping commit after the fact. For blocked or failed stories, the status update may be a dedicated commit, but it must happen before the next story is dispatched.

This ensures the backlog file is always consistent with the repository's actual state: if the commit is present, the status is `done`; if the status is `done`, the commit is present.

### Drift Rows At The Wave Close

The drift sessions run at the wave close, never after a merge. Once the last unit of work of a wave has merged or stopped, the implementation agent runs `dispatch close-wave <wave>`. `close-wave` reads the spec-feedback report of each story of the wave, `docs/spec/work/spec-feedback-<story-id>.md`. It refuses while a row is `open`, or `fixed` about an artifact on the core list `rulebooks/core-artifacts.yaml`, and lists each such row with its owner (BR-062). The implementation agent handles each listed row in two passes:

1. The implementation agent dispatches the owner of each `open` row. The owner is the agent in the row's Owner column. The owner changes the artifact and sets the row to `fixed`.
2. The implementation agent then dispatches the owner's reviewer for each `fixed` row. The reviewer is the `reviewed_by:` entry of the owner's declaration that matches the row's artifact. The reviewer sets the row to `confirmed` or `rejected`.

A row about an artifact without `reviewed_by:`, such as a QA strategy or an ADR, gets no reviewer and closes at `fixed` (DEC-35).

When the reviewer is the stakeholder, the implementation agent dispatches no reviewer. The owner presents the fix to the stakeholder in a session. The agent that ran the session sets the row to `confirmed` or `rejected` for the stakeholder. Until that session, the row stays `fixed`.

A reviewer sets `rejected` when the code breaks an accepted requirement. The reviewer that rejects the row files a `BUG` finding, `docs/findings/BUG-NNNN.md`, with `owner: developer-agent`. When the stakeholder rejects, the agent that ran the session files the `BUG` finding. A `rejected` row does not block the wave. The implementation agent states this rule in the brief of each owner and each reviewer.

Owners and reviewers commit each row status on the feature branch (ADR-0029). After every dispatch has returned, the implementation agent runs `close-wave` again, and repeats the two passes until it passes. It does not wait for the User's go, because the wave close starts, merges and destroys nothing.

### Run By Hand

A run by hand (`--manual`) keeps the same ledger, story workflow and checks as an orchestrated run, and it runs one story at a time in the primary checkout.

Each story is a wave of its own (BR-064), so the drift-row rule holds per story. After the story merges or stops, the implementation agent runs `dispatch close-wave <wave>` and handles each listed row as [Drift Rows At The Wave Close](#drift-rows-at-the-wave-close) describes. `close-wave` refuses while the story's report has an `open` row, or a `fixed` row about an artifact on the core list. The core list is `rulebooks/core-artifacts.yaml`. `dispatch prepare-story` refuses the next story until the wave has its record. The human closes no story, because `close-wave` checks the rows. At each story's wave close, the implementation agent routes the open `QA` findings, as step 6 of the orchestrated workflow does after `close-wave` (CAO-G31).

QA-in-Worktree Divergence does not apply in a run by hand, because the story runs in the primary checkout.

### Dispatch Ledger

Both ways of driving a run keep a ledger: an orchestrated run and a run by hand. `dispatch init --mode orchestrated|by-hand` writes it, and without `--mode` the run is orchestrated.

The dispatcher must maintain a machine-readable ledger at `.current-work/<feature-branch>/dispatch-ledger.yaml` tracking every story in the current dispatch. The ledger is **script-owned runtime state**: agents read it to resume and report, but only `.agent-factory/factory/scripts/dispatch` subcommands mutate it. The ledger is saved after each mechanically observable transition. It lives under the ignored `.current-work/` and is never committed. A ledger exists only while its run is active, so it has no field that marks the run closed.

Schema, with every field that `dispatch` writes:

```yaml
---
mode: orchestrated | by-hand
feature_branch: <branch-name>
branch_root: <40-char SHA>  # tip of the feature branch at init
branch_head: <40-char SHA>  # updated after each merge or wave closeout
stories:
  <story-id>:
    id: <story-id>
    wave: <wave-number or null>
    status: pending | prepared | dispatching | dispatched | done | blocked | failed
    deps: [<story-id>, ...]
    branch: <story branch or null>
    worktree: <worktree path or null>
    feature_branch: <branch-name or null>
    base_sha: <40-char SHA or null>
    tier: <economy | standard | strong or null>
    reason: <null or explanation for blocked/failed>  # or "escalate refused: verify-base" or "escalate refused: scope"
    # The fields below appear only once they hold a value.
    attempts: [<attempt record>, ...]
    escalation_granted: true
    attempt_grants: [{tier: <tier>, attempt_count: <number of attempts at the grant>}, ...]
    verify_base: <verify-base result>
    commit_sha: <40-char SHA>
    failure_class: <failure class>
    evidence: <evidence path>
    manifest_recoveries: [<recovery record>, ...]
    active_session: seam | impl
    active_tier: <economy | standard | strong>
    returned: true  # dispatch return-story set the entry back to pending
waves: [<wave closeout record>, ...]  # see Wave Closeout Record
```

Only the User runs `dispatch return-story <id>`, and the guardrail refuses it to agents. It sets a `failed` or `blocked` story to `pending`, sets `returned: true` in its entry, and sets `status: pending` in `backlog/<id>.md` of the current checkout. It refuses a story in any other state and commits nothing (BR-116).

`dispatch resume-gates <id>` sets a `blocked` story or finding with the reason `gate cannot measure: crap-score` back to `dispatched`. It keeps the attempts, the reason, the branch, and the worktree and writes no manifest, so the next step is the gate-check step. It refuses every other entry, and one without its story branch, with exit `1` and names why (BR-135, DEC-63). `re-dispatch` stays the way back when the code must change.

`dispatch` also reads a ledger with the old names `invocation_branch` and `mode: automated`. It reads them as `feature_branch` and `mode: orchestrated`, and its next write holds only the new names.

The ledger is the dispatcher's working memory across session boundaries — on resume, the dispatcher reads it to determine which stories completed, which failed, what is merely prepared, and what the current base SHA is, rather than reconstructing state from git log heuristics.

### Wave Closeout Record

At the end of each wave (even a single-story wave), the dispatcher calls `dispatch close-wave <wave>` so the script appends a brief closeout summary to the same ledger namespace:

1. Stories completed this wave, with merge SHAs.
2. Stories blocked or failed this wave, with reasons.
3. Next-ready stories (computed from the updated dependency graph).
4. Current branch head SHA.

This record is not a separate artifact — it is logged as a YAML list under the `waves:` key in the dispatch ledger, appended after each wave:

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

A run ends with `dispatch close`. Only the User runs it, and a run ends in one of two ways (BR-119):

| End      | Precondition                                                                                     | Command                 |
| -------- | ------------------------------------------------------------------------------------------------ | ----------------------- |
| Finished | The User has merged the feature branch into `dev`.                                               | `dispatch close`        |
| Dropped  | The User drops the feature and has returned every unfinished story with `dispatch return-story`. | `dispatch close --drop` |

### Refusals

Both forms refuse a run with a unit of work that is not `done` or `pending`. The message names each such unit of work and its state, such as `ST-0360 is failed`. BR-119 names `failed` and `blocked`. A unit of work in progress is refused too, because its worktree holds work that the close would remove. `dispatch close` without `--drop` also refuses a feature branch that is not merged into `dev`, and names `dispatch close --drop`. Both forms refuse a feature branch that `git check-ref-format --branch` rejects, such as `feature/../feature/other`, and a run folder with a symlink on the way to it, because either can lead to the folder of another run. A refusal exits `1` and changes nothing.

### What The Close Removes

The close acts only on what its ledger names and on the folder `.current-work/<feature-branch>/` of the primary checkout. It runs every git command on the primary checkout or on the worktree it removes, so the folder it is called from does not matter.

1. The worktrees of the run, in this order: the worktree of each story, each temporary worktree of `premerge-check` under `.current-work/<feature-branch>/premerge/`, and the worktree of the feature branch. A worktree counts only when `git worktree list` names it, it lies under `.current-work/` of the primary checkout, and it is not the primary checkout.
2. Before it removes a worktree, the close reads `git worktree list` again. When another registered worktree lies below the path, the close names it, stops with exit `1`, and keeps the ledger, because git would delete that worktree with the folder. The close checks for uncommitted work with `git status --porcelain --untracked-files=all`, so the git config of the User does not hide an untracked file. Before it removes a worktree with uncommitted work, the close runs `git stash push --include-untracked`. The stash holds the untracked files and the changes to tracked files, under a name such as `run feature/login ST-0350 2026-11-24`. The label is the story ID, `premerge/<id>` for a temporary worktree of `premerge-check`, and `feature` for the worktree of the feature branch. The close never applies or drops a stash. A clean worktree gets no stash. The close then runs `git worktree remove` without `--force`. When the stash, the removal, or a `git worktree list` fails, the close stops with exit `1` and keeps the ledger, so the User can fix the cause and run it again.
3. The ledger.
4. The markers of the run in the primary checkout: `.current-work/premerge-check-ok` when its `branch=` line names the feature branch or a story branch of the run, and `.current-work/verify-base-ok` for a run by hand. A marker inside a removed worktree goes with that worktree, and a marker of another run stays.
5. The gate result files `.current-work/<gate>/<id>.json` of each unit of work of the ledger.
6. The briefs and scratch files: the folder `.current-work/<feature-branch>/`. When a worktree that the ledger does not name is left in it, the close keeps the folder and names that worktree.
7. Each branch of the run, with `git branch -d`: the story branches of the ledger and the feature branch. Git refuses an unmerged branch, and the guardrail refuses agents a forced delete, so the User deletes it.

The output names each stash with `stash: <name>`, each deleted branch with `deleted branch: <branch>`, and each unmerged branch with `unmerged branch: <branch>`. A branch that git keeps for another reason, such as a checkout, appears as `kept branch: <branch>` with git's message. The last line is `dispatch close: closed the run on <feature-branch>`.

A stop on a critical finding allows `close` and `close --drop`, because they start and merge nothing (BR-091). The guardrail refuses `dispatch close --drop` to agents. The close reads a ledger with the old names `invocation_branch` and `mode: automated` like any other.

After the close, the record of the run is the merge commits in `dev` and the status `done` in each story file. The ledger held nothing that a later step reads.

## QA-in-Worktree Divergence

QA that runs inside a story worktree validates against `packages/factory/` (source), because the worktree shares the repository's source tree. Pre-commit hooks in the primary checkout, however, load scripts and tests from `factory/` (the installed copy). These are two different directory trees with independent content: `packages/factory/` is always current with the branch, while `factory/` reflects whichever version was last synced by `update-factory`.

When a dispatch touches files under `packages/factory/`, QA can pass in the worktree while the post-merge test suite fails in the primary checkout — the installed copy is stale.

**Mitigation.** Before the final `dispatch merge-story` of any wave that modified `packages/factory/` files, the dispatcher (or stakeholder) must run `.agent-factory/factory/scripts/update-factory` on the primary checkout to sync the installed copy from source. This is a manual step; no automated hook exists yet.

## Enforcement

Human/agent-authored discipline, not a git hook or lint gate — a sub-agent's addressing choice and a dispatcher's scope-splitting decision both happen inside the dispatching agent's own prompt-composition step, before any tool call a hook could intercept. On both ways, the `dispatch` script adds a stricter runtime rule: the ledger under `.current-work/` is script-owned, and the dispatcher must advance story state through `dispatch init`, `dispatch prepare-wave` / `prepare-story`, `dispatch mark-dispatching`, `dispatch mark-dispatched`, `dispatch verify-story`, `dispatch merge-story`, and `dispatch close-wave` instead of handwritten bookkeeping. A run by hand uses `prepare-story` and no `prepare-wave`, because each story is a wave of its own (BR-064). See [implementation-agent.md § Workflow — Orchestrated Run](../../agents/implementation-agent.md#workflow--orchestrated-run) and [§ Workflow — Run By Hand](../../agents/implementation-agent.md#workflow--run-by-hand) for the current concrete application.

## References

- [rules.md § Dispatch](../rules.md#dispatch)
- [branching-policy.md](branching-policy.md) — the branch/worktree half of the dispatch contract (Verify-Base Preamble, Declared Base SHA, Pre-Merge Diff Check)
- [implementation-agent.md § Workflow — Orchestrated Run](../../agents/implementation-agent.md#workflow--orchestrated-run) — the current dispatcher applying this contract
- [reconciliation-agent.md](../../agents/reconciliation-agent.md) — the agent whose incident motivated the Sub-Agent Addressing rule
- [docs/reviews/retro-2026-07-12.md](../../../../docs/reviews/retro-2026-07-12.md) — the session that motivated both rules
