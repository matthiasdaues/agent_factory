---
id: RECON-0002
source: reconcile-spec
severity: minor
category: defect
artifact: factory/agents/*.md (8 files; in-range additions at implementation-agent.md#L50,L55)
status: resolved
traces: []
---

# Broken `../factory/rulebooks/...` relative links across factory/agents/, propagated further by ST-0005/ST-0008

**What is wrong:** This is a pre-existing, repo-wide bug, not one this integration range introduced — but two of this range's own edits made it worse in one file, which is why it surfaces here. Every `.md` file under `factory/agents/` (`qa-agent.md`, `spec-review-agent.md`, `implementation-agent.md`, `requirements-agent.md`, `reconciliation-agent.md`, `architecture-review-agent.md`, `developer-agent.md`, `architecture-agent.md` — 8 files, confirmed by `grep -rln '\.\./factory/rulebooks' factory/agents/`) links to rulebook conventions as `[label](../factory/rulebooks/conventions/<file>.md)`. Resolved from these files' real location (`factory/agents/`), that path is `factory/factory/rulebooks/conventions/<file>.md`, which does not exist anywhere; the correct relative path is `../rulebooks/conventions/<file>.md`. This predates the branch (line 46 of `implementation-agent.md` already had it at `e8a8565`). In this range specifically, ST-0008 and ST-0005 each added a new sentence to `implementation-agent.md` (lines 50 and 55) citing the same broken `../factory/rulebooks/conventions/branching-policy.md` pattern instead of catching and fixing the pre-existing bug — so the in-range contribution is 2 more broken links in an already-broken file, not the root cause.

**Fix:** Mechanical, repo-wide, one pass: in every file under `factory/agents/`, replace `../factory/rulebooks/conventions/` with `../rulebooks/conventions/`. Confirm afterward with the same grep that no `../factory/rulebooks/` occurrences remain.
