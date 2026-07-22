---
id: RECON-0009
source: reconcile-spec
severity: major
category: defect
artifact: factory/config/extensions/pi-usage.ts
status: resolved
traces: [ST-0044, ADR-0007]
---

# Pi nested usage can be deleted with a dispatched worktree

**What is wrong:** `capturePiStream()` writes beneath the Pi process's current
project directory. A Pi agent launched by `dispatch_wave` runs inside a
disposable worktree, so any `run_agent` or nested `dispatch_wave` call made by
that agent persists its descendant usage inside the worktree. A successful
outer dispatch removes the worktree after merge and therefore deletes those
descendant records. Existing installed-path tests stop at depth one and use
`merge: false`, so they cannot detect the loss. This violates the requirement
to retain total usage across the complete spend tree.

**Fix:** Establish one canonical usage root outside disposable worktrees and
propagate it through every Pi subprocess. Make human, `run_agent`, and
`dispatch_wave` capture write to that root regardless of the child's working
directory. Add an installed-path regression test in which a dispatched agent
creates a nested child, the outer branch merges and its worktree is removed,
and every root/child/descendant record remains available with correct parent
and depth context.

**Resolution:** Pi now derives the primary checkout from Git's shared common
directory, validates any inherited root against that independently derived
checkout and the Factory installation, and propagates the canonical root to
every subprocess. The capture executable is resolved from the installed
extension source rather than from environment-selected data paths.

The installed-path regression executes a depth-one `dispatch_wave` child that
invokes a depth-two `run_agent`, merges the outer branch, confirms the dispatch
worktree was removed, and verifies that both records and transcripts remain in
the primary checkout with the lineage `human -> depth 1 -> depth 2`. Separate
coverage proves linked-worktree human capture and rejection of an untrusted
inherited root.
