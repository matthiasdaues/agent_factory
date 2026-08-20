---
title: Dispatch Contract
category: implementation
enforcement: dispatch-prompt clause (human/agent-authored discipline) — not mechanically gate-checked
version: 1.2.0
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

Motivating example: the binder-to-OCR research run dispatched ~60–80 research and review sub-agents that all inherited the strongest tier, in waves up to 20 wide; it hit the org monthly spend limit repeatedly, and several agents completed their analysis but died at the write step, forcing full re-runs. Routing the fan-out to standard or economy in waves of six would have cut the spend several-fold and made each failure cheap. See [agent-dispatch-token-efficiency.md](../../../docs/proposals/agent-dispatch-token-efficiency.md) and [research-workflow-efficiency-and-atomicity.md](../../../docs/proposals/implemented/research-workflow-efficiency-and-atomicity.md).

### Verify Sub-Agent Reports Against State

A sub-agent's success report is a claim, not proof. Before treating a dispatched unit of work as done, verify it against observable state — the branch tip and `git log`, the actual test run, and the mechanical gates ([verify-base](branching-policy.md#verify-base-preamble), [premerge-check](branching-policy.md#pre-merge-diff-check)) — never the self-report alone.

For every commit SHA a sub-agent reports, run both checks before proceeding:

```bash
git cat-file -e <sha>^{commit}       # SHA exists as a commit object
git branch --contains <sha>          # SHA lives on the expected branch
```

A SHA that fails either check means the sub-agent's report is false or the work landed somewhere unexpected — investigate before merging or closing the story.

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
factory/scripts/verify-base <target> [--expect-base <sha>]
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

File-disjoint stories fan out in parallel within a wave — that concurrency is the dispatcher's strength. The constraint is between waves, not within them: **every story in a wave must reach a terminal state before the next wave launches**. A terminal state is a verified merge or an explicit blocked/failed record in the dispatch ledger.

This eliminates the drift pattern (wave N+1 dispatching against stale state) without sacrificing the throughput of parallel fan-out. The concurrent wave cap from [Model Tier And Wave Size](#model-tier-and-wave-size) (default six) still applies within each wave.

### Hard Checkpoint Per Story

Every story in a wave must reach a terminal state — merged commit on the target branch, or an explicit blocked/failed record — before the next wave launches. "Terminal state" means:

1. The story's commit SHA is verified on the expected branch (see [Verify Sub-Agent Reports Against State](#verify-sub-agent-reports-against-state)).
2. `premerge-check` passed and the merge is complete, OR the story is recorded as blocked/failed with a reason.
3. The story file's `status` field is updated in the same commit that delivers the implementation (for done) or in a dedicated status-update commit (for blocked/failed).

No new wave may launch while any story from the prior wave is in an unresolved state. This eliminates the drift pattern where later waves dispatch against progressively staler bases.

### Story Status Commit Rule

The story file's `status` field must be updated to `done` in the **same commit** that delivers the story's implementation — not in a separate housekeeping commit after the fact. For blocked or failed stories, the status update may be a dedicated commit, but it must happen before the next story is dispatched.

This ensures the backlog file is always consistent with the repository's actual state: if the commit is present, the status is `done`; if the status is `done`, the commit is present.

### Dispatch Ledger

The dispatcher must maintain a machine-readable ledger at `.agent-factory/dispatch-ledger.yaml` tracking every story in the current dispatch. The ledger is committed after each story reaches its terminal state and serves as the authoritative record of what was dispatched, what succeeded, and what failed.

Schema:

```yaml
invocation_branch: <branch-name>
branch_root: <40-char SHA>
branch_head: <40-char SHA>  # updated after each merge
stories:
  - id: <story-id>
    branch: <feature-branch-name>
    worktree: <worktree-path>
    declared_base: <40-char SHA>
    verify_base: pass | fail
    premerge_check: pass | fail | pending
    commit_sha: <40-char SHA or null>
    merge_sha: <40-char SHA or null>
    status: dispatched | done | blocked | failed
    wave: <wave-number>
    reason: <null or explanation for blocked/failed>
```

The ledger is the dispatcher's working memory across session boundaries — on resume, the dispatcher reads the ledger to determine which stories completed, which failed, and what the current base SHA is, rather than reconstructing state from git log heuristics.

### Wave Closeout Record

At the end of each wave (even a single-story wave), the dispatcher produces a brief closeout summary committed alongside the ledger update:

1. Stories completed this wave, with merge SHAs.
2. Stories blocked or failed this wave, with reasons.
3. Next-ready stories (computed from the updated dependency graph).
4. Current branch head SHA.

This record is not a separate artifact — it is logged as a YAML list under the `waves:` key in the dispatch ledger, appended after each wave:

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

## Enforcement

Human/agent-authored discipline, not a git hook or lint gate — a sub-agent's addressing choice and a dispatcher's scope-splitting decision both happen inside the dispatching agent's own prompt-composition step, before any tool call a hook could intercept. Enforced by including the clauses above, verbatim, in every dispatch prompt that spawns sub-agents or covers more than one module/directory. See [implementation-agent.md § Workflow](../../agents/implementation-agent.md#workflow) for the current concrete application.

## References

- [rules.md § Dispatch](../rules.md#dispatch)
- [branching-policy.md](branching-policy.md) — the branch/worktree half of the dispatch contract (Verify-Base Preamble, Declared Base SHA, Pre-Merge Diff Check)
- [implementation-agent.md § Workflow](../../agents/implementation-agent.md#workflow) — the current dispatcher applying this contract
- [reconciliation-agent.md](../../agents/reconciliation-agent.md) — the agent whose incident motivated the Sub-Agent Addressing rule
- [docs/reviews/retro-2026-07-12.md](../../../docs/reviews/retro-2026-07-12.md) — the session that motivated both rules
