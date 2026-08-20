---
id: SPEC-011
source: spec-review
severity: major
category: defect
artifact: docs/proposals/mechanize-dispatch-orchestration.md#dispatch-prepare-wave-n
status: resolved
traces: []
---

# prepare-wave cannot create serial-chain branches — their declared base does not exist yet

**What is wrong:** `dispatch prepare-wave <N>` prepares **every** story in wave N upfront, creating each branch and worktree "from the correct base (invocation branch tip for parallel-safe, previous story's merge commit for serial chains)". For a serial chain A→B inside wave N, story B's declared base is A's merge commit — which cannot exist while `prepare-wave N` runs, because A has not been merged (it may not even have been dispatched: spawning happens after `prepare-wave` returns). The rewritten workflow then has the LLM spawn subagents for all prepared stories. As specified, the script must either fail on any wave containing a serial chain, or silently cut B from the wrong base — reintroducing exactly the wrong-base/contamination failure modes the proposal exists to close. The current workflow this replaces gets the ordering right: [implementation-agent.md § Workflow, Step 3](../../factory/agents/implementation-agent.md#workflow) creates each serial-chain branch "off the previous one's *already-merged* state, dispatching one at a time", and [branching-policy.md § Merge Order Is Overlap-Aware](../../factory/rulebooks/conventions/branching-policy.md#merge-order-is-overlap-aware) merges overlapping branches one at a time in dependency order. Overlap-aware serial chains are a core feature of the dispatch design, not an edge case — a mechanized replacement that cannot execute them is a significant regression.

**Resolution (pass 3, verified 2026-08-18 against c49f5890ef9f2270869a9067dca63b9745179f17):** Fixed via option (a) — `prepare-wave` now prepares only base-available stories (parallel-safe stories and chain heads, cut from the invocation branch tip) while chain links stay `pending`, and a new `dispatch prepare-story <story-id>` subcommand lazily prepares each link from its predecessor's merge commit after that predecessor's `merge-story` succeeds, with mandatory `verify-base --expect-base <predecessor's merge SHA>`. The workflow sketch gained step f (prepare-story → spawn → mark-dispatched → verify-story → merge-story, one link at a time), and completion criteria now cover both halves. Verified in [spec-review-2026-08-18-pass3.md](../reviews/spec-review-2026-08-18-pass3.md).

**Fix:** Make chain-link preparation lazy instead of upfront. Either (a) restrict `prepare-wave` to the wave's parallel-safe stories and add a per-story `dispatch prepare-story <story-id>` subcommand that the LLM calls for each serial-chain link only after its predecessor's `merge-story` has succeeded — at which point the predecessor's merge commit exists and can serve as the declared base; or (b) have `prepare-wave` prepare only chain heads and record remaining links as `pending-preparation`, with `merge-story` (or a follow-up call) preparing the next link after a successful merge. Update the workflow sketch and completion criteria to match whichever option is chosen, and keep the mandatory `--expect-base` check pointed at the freshly recorded merge-commit SHA.
