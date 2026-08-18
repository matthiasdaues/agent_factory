---
id: SPEC-008
source: spec-review
severity: major
category: defect
artifact: docs/proposals/mechanize-dispatch-orchestration.md#design
status: resolved
traces: []
---

# No subcommand records a blocked or failed story — the ledger lifecycle cannot close

**What is wrong:** The proposed subcommand set (`plan`, `init`, `prepare-wave`, `mark-dispatched`, `verify-story`, `merge-story`, `close-wave`, `status`) has no way to transition a story to `blocked` or `failed`. Yet the current workflow records blocked/failed stories in the ledger and story file with a reason ([implementation-agent.md § Workflow, Step 4f](../../factory/agents/implementation-agent.md#workflow)), and both `prepare-wave` and `close-wave` exit non-zero unless every story is terminal. Combined with the proposal's own completion criterion "the ledger is never written by the LLM directly — only by the script", any failed story deadlocks the dispatch: the wave can never close and the next wave can never start. The subcommand set does not cover the full workflow it replaces, and it does not close failure modes whose stories end anywhere but `done`.

**Fix:** Add a `dispatch mark-blocked <story-id> --reason <text>` / `dispatch mark-failed <story-id> --reason <text>` subcommand (or one `mark-terminal` with a status argument) that updates the ledger entry, updates the story file's `status` field in a dedicated status-update commit per [dispatch-contract.md § Hard Checkpoint Per Story](../../factory/rulebooks/conventions/dispatch-contract.md#hard-checkpoint-per-story), and commits both.

**Resolution (2026-08-18, repeat pass):** Fixed in commit c1507a1. The proposal adds `dispatch mark-blocked <story-id> --reason <text>` and `dispatch mark-failed <story-id> --reason <text>`, which update the ledger entry, update the story file's `status` in a dedicated status-update commit per the Story Status Commit Rule, and commit both. The deadlock rationale is stated explicitly, and both subcommands appear in Scope and the Completion Criteria. Verified against the current proposal text.
