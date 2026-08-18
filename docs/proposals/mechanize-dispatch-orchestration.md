---
schema_version: 2
title: Mechanize Dispatch Orchestration
status: open
owner: md@matthiasdaues.de
created: 2026-08-18
updated: 2026-08-18
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - factory/agents/implementation-agent.md
    - factory/rulebooks/conventions/dispatch-contract.md
    - factory/rulebooks/conventions/branching-policy.md
    - factory/scripts/premerge-check
    - factory/scripts/verify-base

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - compatibility

estimate:
  as_of: 2026-08-18
  basis: judgment
  confidence: low
  human_review_hours:
    min: 1.0
    max: 3.0
  normalized_tokens:
    min: 6000
    max: 12000
  estimated_consumption:
    min: 90000
    max: 300000
    overhead_multiplier: 25
    playbook: feature-addition
---

# Feature Request: Mechanize Dispatch Orchestration

## Summary

Extract the deterministic orchestration work from the implementation-agent into a `factory/scripts/dispatch` script that owns all git state management — branch creation, worktree setup, ledger maintenance, wave gating, merge ordering, and cleanup. The LLM dispatcher calls the script at each step and retains only the one job a script cannot do: spawning subagents.

## Motivation

The dispatch contract ([dispatch-contract.md](../../factory/rulebooks/conventions/dispatch-contract.md)) describes a meticulous stateful workflow: invocation branches, per-story worktrees, declared base SHAs, a YAML dispatch ledger, wave boundary gates, merge ordering by file overlap, and story-status-in-commit rules. Today the implementation-agent — an LLM — executes every step of this workflow by following prose instructions.

The charter dispatch (2026-08-18, ST-0074–ST-0085) exposed three failure modes:

1. **Branch contamination.** ST-0078's worktree accumulated commits from ST-0074, ST-0076, and ST-0079. The developer-agent implemented its story against a polluted workspace. `premerge-check` caught the problem at merge time — after the full subagent token budget was spent.

2. **verify-base never ran.** The dispatch ledger shows `verify_base: null` for ST-0078. The developer-agent was supposed to run `verify-base` as its first action. It did not. The early-detection gate existed in the instructions but was not enforced mechanically.

3. **Ledger drift.** ST-0075's commits appeared on the target branch, but the ledger still showed `status: dispatched`. The ledger was not the source of truth it was supposed to be — it was a record the LLM was supposed to maintain but did not.

All three failures share a root cause: the dispatch contract assigns deterministic orchestration work to a probabilistic executor. The LLM is reliable at creative implementation (writing code, skills, templates) and unreliable at procedural state management (branch operations, ledger writes, wave gating). The gates (`premerge-check`, `verify-base`) exist to catch mistakes, but they catch them too late — after the subagent has burned its full run.

The factory's foundational principle already separates these concerns: "agents create artifacts; mechanically triggered gates run scripts that validate against predefined, state-dependent criteria." The dispatch workflow has not applied this principle to itself.

## Core Principles

- The dispatch script owns all git state. The LLM never runs branch, worktree, merge, or ledger commands directly during a dispatch — it calls the script.
- Gates run before work, not after. `verify-base` runs when the script creates the worktree, before any subagent is spawned — not inside the subagent as a first-action instruction.
- The ledger is maintained by the script, not the LLM. Every state transition is a script call that atomically updates the ledger and commits it.
- The LLM dispatcher's remaining job is: read the plan, spawn subagents with the prepared worktrees, and call script commands in sequence. It cannot mess up branch management because it never touches branches directly.

## Design

### Script: `factory/scripts/dispatch`

A Python script (stdlib only, matching existing lint scripts) with subcommands that cover the full dispatch lifecycle. Each subcommand is atomic — it does its work, updates the ledger, and commits. The LLM calls them in order.

All git-mutating subcommands execute **in the invocation-branch worktree** (created by `dispatch init`), never in an arbitrary checkout. This matters mechanically: `premerge-check` writes its `premerge-check-ok` marker at the toplevel of the checkout it runs in, and [block-dangerous-git.sh](../../factory/config/hooks/block-dangerous-git.sh) denies any `git merge` whose marker does not match the branch's name and head in **that** checkout. Running merge-path subcommands anywhere else writes the marker where the hook never looks.

#### `dispatch plan --backlog-dir backlog --stories ST-0074,ST-0075,...`

Read the specified stories (or all pending stories if `--stories` is omitted), build the dependency graph, compute file-overlap sets, and output a wave plan as YAML to stdout. The plan includes:

- Wave assignments (which stories in which wave)
- Parallel-safe sets within each wave
- Serial chains within each wave (overlapping outputs)
- Model tier per story (from `tier` field, mapped via `config/model.conf`)
- Estimated cost per wave

Does not modify any state. The LLM reviews the plan and may adjust before proceeding.

#### `dispatch init --base <branch> --stories ST-0074,ST-0075,...`

Create the invocation branch and worktree from the specified base. Initialize the dispatch ledger at `.agent-factory/dispatch-ledger.yaml`. Record branch root. Commit the ledger. Verify the worktree mapping with `git worktree list --porcelain`. Check that all target directories implied by story outputs are git-tracked.

Untracked target directories are a precondition failure: `init` lists them and exits non-zero. Since the script owns all git state, the LLM cannot make the baseline commit by hand; instead, re-running `init` with `--baseline-commit` makes the script create an explicit baseline commit of those directories' current contents on the base branch, **before** the invocation branch is created — never as an improvised mid-dispatch fix.

Exit non-zero if any other precondition fails.

#### `dispatch prepare-wave <N>`

Read the ledger. Verify all stories in waves < N are terminal (done, blocked, or failed) — exit non-zero if not (this is the mechanical wave gate). For each story in wave N:

1. Create feature branch and worktree from the correct base (invocation branch tip for parallel-safe, previous story's merge commit for serial chains).
2. Verify the branch-to-worktree mapping with `git worktree list --porcelain` — one check per story, matching path and branch against what was requested — before considering the story prepared. This absorbs the [rules.md § Branching](../../factory/rulebooks/rules.md#branching) MUST that today relies on the LLM remembering to run it.
3. Run `factory/scripts/verify-base <invocation-branch> --expect-base <story's declared-base SHA>` in the new worktree — exit non-zero on failure, before the LLM spawns anything. The `--expect-base` argument is mandatory here: at creation time the not-behind-target check passes trivially, so the declared-base half is the one that catches a wrong-base dispatch.
4. Record the story as `prepared` in the ledger (new status between `pending` and `dispatched`), including `declared_base` and the `verify_base` result.
5. Commit the ledger.

Output the prepared worktree paths and a subagent prompt template for each story. The LLM reads this output and spawns subagents.

#### `dispatch mark-dispatched <story-id>`

Update the story's ledger entry from `prepared` to `dispatched`. Called by the LLM after it has spawned the subagent. Commit the ledger.

#### `dispatch verify-story <story-id> --sha <commit-sha>`

Run the SHA verification sequence for a completed story:

1. `git cat-file -e <sha>^{commit}` — SHA exists.
2. `git branch --contains <sha>` — SHA on expected branch.

Update the ledger entry with `commit_sha` and the verification result. Commit the ledger. Exit non-zero if any check fails — the LLM must not proceed to merge.

Note: `premerge-check` is deliberately **not** part of this subcommand. Its pass marker is one slot per checkout, keyed to the checked branch's current head, and each check must be immediately followed by that branch's own merge, one pair at a time ([branching-policy.md § Pre-Merge Diff Check](../../factory/rulebooks/conventions/branching-policy.md#pre-merge-diff-check)). A verify-all-then-merge-all sequence would overwrite the marker between check and merge, and the hook would deny the earlier merges. The check therefore lives inside `merge-story`, immediately before its own merge, so the pairing holds by construction instead of by dispatcher discipline.

#### `dispatch merge-story <story-id>`

Merge the story's feature branch into the invocation branch, in the invocation-branch worktree:

1. Read the story file's `outputs:` globs and run `factory/scripts/premerge-check <invocation-branch> <story-branch> --scope <output-glob> ...` — one repeated `--scope` per declared output path. The scope check is the mechanical detector for the proposal's own failure mode #1 (branch contamination): every changed file must fall under at least one declared output prefix. Omitting `--scope` would silently skip it, so the script derives scopes from the story file and never calls `premerge-check` without them. A non-zero exit blocks the merge and records `premerge_check: fail` in the ledger.
2. Immediately on pass — in the same subcommand invocation, so the one-slot `premerge-check-ok` marker still matches this branch's head — run `git merge <story-branch>`.
3. Update the story file's `status` to `done` in the same commit as the merge.
4. Run the full test suite after the merge, before any other story is merged. This is not optional: [rules.md § Branching](../../factory/rulebooks/rules.md#branching) states "**MUST** run the full test suite after every merge, before the next", and the current workflow already does this (inline, per merge). The script discovers the test command from a `test_command` key in the project config (`config/project.json` — the project-local config file that already exists alongside `config/model.conf`); if no command is declared there, it exits non-zero with a diagnostic rather than guessing. **Red-suite recovery:** the merge commit already exists when tests run, so a red suite cannot simply block the merge. The script records the story as `blocked` in the ledger with reason `post-merge test failure` (merge SHA noted), commits the ledger, and exits non-zero. The wave blocks; repairing the merged-but-broken invocation branch (fix-forward story or revert) is the dispatcher's call, exactly as [implementation-agent.md § Workflow, Step 4f](../../factory/agents/implementation-agent.md#workflow) treats a conflict or red suite today: resolve before continuing.
5. Update the ledger with `premerge_check`, `merge_sha`, and `status: done`. Clean up the worktree and delete the merged branch. Commit.

Exit non-zero on conflicts, premerge-check failure, or post-merge test failure. On a merge conflict the script runs `git merge --abort` before exiting, so the invocation worktree is never left in a MERGING state.

#### `dispatch mark-blocked <story-id> --reason <text>` / `dispatch mark-failed <story-id> --reason <text>`

Record a story that cannot reach `done` in this dispatch. Update the ledger entry (`status`, `reason`), update the story file's `status` field in a dedicated status-update commit per [dispatch-contract.md § Story Status Commit Rule](../../factory/rulebooks/conventions/dispatch-contract.md#story-status-commit-rule), and commit both.

Without these two subcommands the lifecycle cannot close: `prepare-wave` and `close-wave` exit non-zero unless every story is terminal, and the LLM is forbidden from writing the ledger directly — so a single failed story would deadlock the dispatch. Failed stories stay `pending` in the backlog (matching current workflow); the ledger status is `failed`, which is terminal for wave-gating purposes.

#### `dispatch close-wave <N>`

Verify all stories in wave N are terminal. Append the wave closeout record to the ledger (completed stories with merge SHAs, blocked/failed with reasons, next-ready stories, branch head SHA). Commit the ledger.

Exit non-zero if any story in wave N is not terminal — this prevents the LLM from moving to wave N+1.

#### `dispatch status`

Print the current ledger state as a human-readable table: story ID, wave, status, branch, commit SHA. Kept deliberately despite the ledger being readable YAML: it is the dispatcher's read-only pre-flight checkpoint, and it is the one place where "what does the ledger say right now" gets a compact, unambiguous answer before a wave launches. Cheap to implement, zero write paths.

### Failure behavior and idempotency

Every subcommand is idempotent: re-running it after success is a no-op that exits 0 (state detected from the ledger), and re-running it after a mid-command failure resumes or reports cleanly — never double-commits the ledger, never re-creates an existing branch or worktree, never starts a second merge while one is in progress. This is the prerequisite for the deferred retry model: the LLM retries by calling the same subcommand again, and the script decides from recorded state what that means.

Mid-merge conflict handling is specified above (`merge-story` aborts the merge, marks the story blocked, exits non-zero). A red post-merge suite is likewise specified above. For every other failure mode the rule is: ledger unchanged, non-zero exit, diagnosis on stderr.

### Implementation-agent changes

The implementation-agent's Workflow section is rewritten to call `dispatch` subcommands instead of performing git operations directly. The new workflow:

1. `dispatch plan` → review wave plan with user
2. `dispatch init` → create invocation branch (re-run with `--baseline-commit` if it reports untracked target directories)
3. For each wave N:
   a. `dispatch prepare-wave N` → get worktree paths and prompts
   b. Spawn developer-agent subagents (the one thing the script cannot do)
   c. `dispatch mark-dispatched` for each spawned story
   d. On completion: `dispatch verify-story` for each reported SHA
   e. For each verified story, in overlap-determined order: `dispatch merge-story` — one story fully merged (check, merge, status, tests) before the next merge begins
   f. On failure at any point: `dispatch mark-blocked` / `dispatch mark-failed` with a reason
   g. `dispatch close-wave N`
4. Handoff when all waves done

The agent prompt template for subagents no longer instructs them to run `verify-base` — the script already ran it before they were spawned.

The mechanized workflow does **not** absorb the remaining dispatch-contract clauses; they survive as LLM responsibilities, unchanged:

- Sub-agent addressing ([dispatch-contract.md § Sub-Agent Addressing](../../factory/rulebooks/conventions/dispatch-contract.md#sub-agent-addressing)) — instance IDs in prompts.
- The concurrent wave cap ([dispatch-contract.md § Model Tier And Wave Size](../../factory/rulebooks/conventions/dispatch-contract.md#model-tier-and-wave-size), default six) and pre-flight cost estimation.
- The envelope-error-is-not-failure check ([dispatch-contract.md § run_agent Envelope Error Is Not Proof Of Failure](../../factory/rulebooks/conventions/dispatch-contract.md#run_agent-envelope-error-is-not-proof-of-failure)) — verify the child's committed artifacts before retrying.

### Ledger status lifecycle

Current: `pending → dispatched → done | blocked | failed`

New: `pending → prepared → dispatched → done | blocked | failed`

The `prepared` status means the script has created the branch and worktree and verify-base has passed, but the LLM has not yet spawned the subagent. This eliminates the gap where a story is `dispatched` in the ledger but no subagent exists. `blocked` and `failed` are recorded by `mark-blocked` / `mark-failed`; `done` is recorded by `merge-story` only after the post-merge test suite passes.

### Dispatch contract updates

- dispatch-contract.md § Dispatch Ledger: document `prepared` status, note that the script owns all ledger writes.
- dispatch-contract.md § Verify Sub-Agent Reports: note that verify-base is now pre-spawn (script-owned), not in-agent.
- dispatch-contract.md § Hard Checkpoint Per Story: note that `premerge-check` runs inside `merge-story`, immediately before its own merge, with `--scope` derived from the story's `outputs:`.
- branching-policy.md § Verify-Base Preamble: update to note that verify-base is called by the dispatch script for dispatched stories; the developer-agent preamble instruction is a fallback for non-dispatched use.

## Scope

**In the first release:**

- `factory/scripts/dispatch` with subcommands: `plan`, `init`, `prepare-wave`, `mark-dispatched`, `verify-story`, `merge-story`, `mark-blocked`, `mark-failed`, `close-wave`, `status`
- `factory/agents/implementation-agent.md` rewritten to call script subcommands
- `factory/rulebooks/conventions/dispatch-contract.md` updated: `prepared` status, script-owned ledger, pre-spawn verify-base, premerge-check placement and `--scope` derivation
- `factory/rulebooks/conventions/branching-policy.md` updated: verify-base preamble notes script-owned path

**Explicitly deferred (do NOT plan stories for these):**

- Retry/resume logic within the dispatch script (the LLM handles retries by calling the same subcommands; idempotency makes this safe)
- Integration with CI/CD (the script is local-only, matching all other factory scripts)
- Parallelism within the script itself (the script is sequential; the LLM handles fan-out via the Agent tool)
- Migration of the research-orchestrator to use the dispatch script (different dispatch pattern)

## Open Questions

- Should the script support `--dry-run` on destructive subcommands (`init`, `merge-story`)? Genuinely unresolved; carry into planning.

## Completion Criteria

- `dispatch plan` produces a correct wave plan from a set of stories with dependencies and file overlaps
- `dispatch init` creates invocation branch, worktree, and ledger atomically; exits non-zero on untracked target directories unless `--baseline-commit` is given
- `dispatch prepare-wave` exits non-zero when prior wave has non-terminal stories (mechanical wave gate)
- `dispatch prepare-wave` runs `verify-base --expect-base <declared-base>` before spawning and exits non-zero on failure (pre-spawn gate)
- `dispatch prepare-wave` verifies each story's branch-to-worktree mapping with `git worktree list --porcelain`
- `dispatch verify-story` catches the SHA-level failures from the charter dispatch: missing SHA (`cat-file`), wrong branch (`branch --contains`)
- `dispatch merge-story` catches the contamination failure from the charter dispatch: it runs `premerge-check --scope <story outputs>` immediately before its own merge, in the invocation-branch worktree, so the `premerge-check-ok` marker pairing holds by construction
- `dispatch merge-story` updates story status to `done` in the same commit as the merge and runs the full test suite (command from the `test_command` key in `config/project.json`) after the merge, before the next merge
- `dispatch merge-story` records the story as `blocked` and exits non-zero on post-merge test failure, leaving no MERGING state
- `dispatch mark-blocked` / `dispatch mark-failed` close the ledger lifecycle for non-`done` stories (wave can close, next wave can start)
- `dispatch close-wave` exits non-zero when any story is non-terminal
- The ledger is never written by the LLM directly — only by the script
- Every subcommand is idempotent: re-running after success is a no-op; re-running after failure resumes from recorded state
- The implementation-agent workflow uses script subcommands, not raw git
- A dispatch of 3+ stories across 2+ waves completes with a clean ledger and no branch contamination

## Guiding Rule

Agents create; scripts orchestrate. The LLM decides what to build; the script decides where and how to put it.
