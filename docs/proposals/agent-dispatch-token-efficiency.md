---
schema_version: 2
title: "Agent Dispatch Token Efficiency"
status: accepted
owner: agent-factory
created: 2026-07-12
updated: 2026-08-04
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - factory/rulebooks/conventions/dispatch-contract.md
    - factory/rulebooks/conventions/branching-policy.md
    - factory/rulebooks/rules.md
    - factory/agents/implementation-agent.md
    - factory/agents/reconciliation-agent.md
    - factory/scripts/verify-base
    - factory/scripts/premerge-check
    - factory/scripts/trigger
    - factory/config/hooks/block-dangerous-git.sh
    - factory/config/extensions/dispatch-wave.ts
    - orchestrator/tests/

governance:
  assurance: high
  risk_domains:
    - reliability
    - data_integrity

estimate:
  as_of: 2026-08-04
  basis: decomposition
  confidence: medium
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Agent Dispatch Token Efficiency

## Summary

Prevent token spend on child-agent runs that are doomed by stale bases, contaminated diffs, stranded replies, over-broad permissions, or oversized dispatch scope. Repository inspection on 2026-08-04 found that the intended safeguards are already substantially implemented; existing behavior is the baseline, and planning covers only verified gaps, missing tests, and proposal/status reconciliation.

## Motivation

A dispatch of a worktree-isolated background subagent can burn a full agent run's worth of tokens before anyone notices the run was doomed. The 2026-07-12 session lost work three ways, all avoidable:

- **Stale base.** Worktree isolation did not reliably resolve its base to the current tip of the target branch. An agent branched from a commit predating recent merges, did real work against code that no longer existed on `dev`, and produced a diff that was pure noise. This recurred across three phases; twice it cost a full run. The 2026-07-10 retro flagged the same class of failure and its fix (a declared base SHA) went unadopted.
- **Late catch.** The base problem surfaced only when the orchestrating session remembered to diff the finished branch against `dev`. The catch was reliable but manual, and it fired after the wasted work was already paid for.
- **Stranded replies.** An agent that spawned its own sub-agents addressed them by agent *type*, not a resolvable instance ID, so their replies could not route back. The parent blocked indefinitely on a reply that never came.

The fix is to make base-verification, reply-addressing, and pre-merge diffing **mechanical and required**, not habits the orchestrating session must remember.

## Existing implementation baseline

| Mechanism                               | Existing evidence                                                                                | Planning disposition                                         |
| --------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| Verify base before work                 | `factory/scripts/verify-base`, `branching-policy.md`, commit-blocking hooks, dispatcher preamble | Preserve; audit negative-path coverage                       |
| Declared base SHA                       | `verify-base --expect-base`, dispatch-wave prompt, implementation-agent workflow                 | Preserve; audit full-SHA enforcement                         |
| Resolvable sub-agent addressing         | `dispatch-contract.md`, reconciliation-agent workflow                                            | Preserve; add contract coverage where absent                 |
| Pre-merge diff against target           | `factory/scripts/premerge-check`, merge-blocking hooks, dispatch-wave integration                | Preserve; audit file-blowout, scope, and revert coverage     |
| Evidence-derived unattended permissions | Scoped Claude/Copilot background allowlists in `factory/scripts/trigger`                         | Preserve; add direct argv/deny-list regression tests         |
| Dispatch scope cap and checkpoints      | `dispatch-contract.md`, `rules.md`, implementation-agent workflow                                | Preserve; add enforceable acceptance coverage where feasible |

The baseline audit must not create retrospective implementation stories merely to relabel delivered behavior.

## Design

### 1. A verify-base preamble, required as the agent's first action

Every worktree-isolated dispatch prompt carries a fixed preamble. The agent must run it as its first tool call and must halt if it fails — before reading a single source file. Proposed wording, verbatim, to paste into the dispatch prompt:

> **Before any other work, verify your worktree base.** Run:
>
> ```bash
> git merge-base --is-ancestor <TARGET_BRANCH> HEAD && echo BASE_OK || echo BASE_STALE
> git rev-list --left-right --count <TARGET_BRANCH>...HEAD
> ```
>
> If the first line prints `BASE_STALE`, or the left number of the second line is not `0`, your worktree is behind `<TARGET_BRANCH>`. **Stop. Do not read files, do not edit, do not commit.** Report the two command outputs to the dispatcher and wait for instruction.

`<TARGET_BRANCH>` is filled in by the dispatcher (normally `dev`). The `merge-base --is-ancestor` check proves the target is fully contained in HEAD; the `rev-list --left-right --count` left number is how many target commits HEAD is missing. Either failing means the base is stale. This is the exact check the orchestrating session ran by hand this session to certify its own retro branch as safe — the proposal is only to move it from the end of the process to the start, and from the human to the agent.

The implemented form is `factory/scripts/verify-base <target> [--expect-base <SHA>]`, which exits non-zero and prints the diagnosis.

### 2. A declared base SHA in the dispatch contract

The dispatcher records the exact SHA the worktree is expected to be branched from, and the preamble in §1 asserts against it:

```bash
test "$(git merge-base HEAD <EXPECTED_BASE_SHA>)" = "<EXPECTED_BASE_SHA>" && echo BASE_OK || echo BASE_WRONG
```

`BASE_WRONG` means the worktree was not cut from the commit the dispatcher intended, independent of how far `dev` has since moved. This is the 2026-07-10 retro's still-open action item #1 (phase-branch with a recorded `--base`/`--head` SHA pair), narrowed to the one assertion that catches the failure. Adopting §1 and §2 together turns every stale-base incident this session hit into an immediate halt on the agent's first tool call, instead of a discarded run.

### 3. A sub-agent-addressing clause

When a dispatched agent may spawn its own sub-agents, its prompt must carry this clause:

> If you spawn sub-agents, give each one **your resolvable instance ID** as the address to report back to — never your agent *type* name. A type name (for example `reconciliation-agent`) is not a routable recipient, and replies sent to it are lost. Include, verbatim in each sub-agent's prompt: "Report your result to instance `<PARENT_INSTANCE_ID>`." Do not block indefinitely waiting on a sub-agent reply: if a sub-agent declines out-of-scope work or does not respond, do the work yourself rather than waiting.

This addresses two distinct failures from the reconciliation agent: replies addressed to an unroutable type name (which surfaced to the orchestrating session and had to be relayed by hand), and the parent hanging on a reply that was never coming.

### 4. A required pre-merge diff-against-target check

Diffing a finished branch against its target before merge caught both contaminated diffs this session. It must stop being a thing the orchestrating session remembers and become a scripted, non-optional step: `factory/scripts/premerge-check <target> <branch>`.

It runs the diff the orchestrating session ran by hand and flags, deterministically:

- **File-count blowout** — `git diff --name-only <target>...<branch>` returns far more files than the dispatch's stated scope (a configurable threshold, or simply surfaced for confirmation). The Phase 3 diff was 165 files against an intended handful; a blowout is the signature of a stale base.
- **Out-of-scope paths** — changed files outside the directories the dispatch declared it would touch.
- **Reverts of merged work** — the diff deletes or reverts lines that exist on `<target>` but not on the branch's own base, the tell of a stale-base diff undoing already-merged commits.

Its output is a report; a blowout or a revert blocks the merge through the pre-merge marker and hook contract. A contaminated diff cannot proceed without explicit investigation.

### 5. Permission allowlists derived from repository evidence

Unattended dispatch needs a scoped permission allowlist. Two rules, both learned from a classifier block this session:

1. **No blanket bypass.** Never `--dangerously-skip-permissions` or `--allow-all-tools` for an unattended run.
2. **No bare interpreter wildcards.** `Bash(python3 *)`, `Bash(uv *)`, `Bash(uvx *)` scope nothing — a wildcarded interpreter runs arbitrary code. Scope to specific scripts and subcommands instead.

The allowlist is **derived, not imagined**: grep the repository — playbooks, skills, agents, rulebooks, and both pre-commit configs — for the commands actually invoked, and allow those. This is the process that produced a correct allowlist on the third pass this session, after two imagined drafts were blocked.

### 6. Cap single-dispatch scope; checkpoint long tasks

The two largest dispatches this session — orchestrator weeding and doc reconciliation — each hit the org API spend limit multiple times, at 300k–465k tokens per resume cycle. A dispatch that large is also the one most likely to be reasoning against a stale base for the longest before anyone checks. Two mitigations:

- **Cap the scope of a single dispatch.** Split a "relentless weeding of the whole codebase" task into per-module dispatches, each independently verifiable and mergeable. A smaller dispatch fails cheaper and its diff is easier to certify.
- **Checkpoint long tasks with commits between rounds.** The agents that died between rounds recovered cleanly on resume because their work was committed; the risk is a death mid-write. Frequent checkpoint commits bound the loss from a spend-limit death to one round.

## Scope

**In the first release:**

- Build a traceability audit from each of the six mechanisms to its shipped rule, runtime implementation, and automated tests.
- Add regression tests for verified gaps, especially background permission argv/deny lists, pre-merge failure modes, exact declared-base handling, and dispatch prompt contracts.
- Amend stale documentation only where it contradicts observable behavior.
- Close the proposal as implemented only when every completion criterion is evidenced.

**Explicitly deferred (do NOT plan stories for these):**

- Reimplementing safeguards that the baseline audit proves are already delivered.
- New dispatch optimizations not motivated by one of the six recorded mechanisms.
- Live token-budget enforcement; session-level measurement belongs to the companion session-transcript proposal.

## Open Questions

None. Existing behavior is the implementation baseline; only verified gaps are planned.

## Completion Criteria

- Each of the six mechanisms maps to a shipped contract, implementation point, and passing automated evidence, or to a backlog story that supplies the missing element.
- Worktree dispatch halts before source reads or writes when the target or declared base is wrong, using full 40-character SHAs in machine-consumed state.
- A merge is mechanically blocked for stale, out-of-scope, file-count-blowout, or target-reverting diffs.
- Nested dispatch instructions require a resolvable parent instance ID and prohibit indefinite waiting on an unreachable child.
- Unattended Claude and Copilot launch paths use repository-derived scoped permissions, no blanket bypass, and no bare-interpreter wildcard.
- Oversized dispatches are split or checkpointed according to the dispatch contract.
- The proposal status and references reflect the audited delivered state without inventing retrospective implementation work.

## Referenced from

- [`docs/reviews/retro-2026-07-12.md`](../reviews/retro-2026-07-12.md) — the session that motivated every mechanism here.
- [`docs/reviews/retro-2026-07-10.md`](../reviews/retro-2026-07-10.md) — action item #1 (phase-branch with declared base SHA), which §2 narrows and revives.
