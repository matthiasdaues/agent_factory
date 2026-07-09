---
id: 0001
status: accepted
evaluation: none
---

# Split agent_factory from agent_hq as a fresh repo, without preserving git history

## Context

`agent_hq`'s orchestrator (the automation/dispatch layer) is still immature; the inert tooling — agents, skills, playbooks, rulebooks, deterministic gate scripts — is far more advanced and ready to share with the team now. Two options were on the table: keep drafting in place inside `agent_hq` and wait for a second real consumer project to justify a history-preserving `git subtree split`, or start fresh immediately. This was a binary call, not a weighted multi-criteria comparison — no Pugh Matrix applies.

- **Draft in place, subtree-split later** — the original plan (see this repo's own prior discussion): stay inside `agent_hq`, split only once a second real consumer needs the factory, preserving full history via `git subtree split` at that point. Rejected: the team needs a shareable artifact now, not once a hypothetical second consumer shows up.
- **Fresh repo now, no history** (chosen) — trades provenance for speed.

## Decision

Start `agent_factory` today as a fresh repo, copied from `agent_hq`'s current state, with no git history carried over.

## Consequences

Acceptable because most of the content is young (written this same week) — the loss is a convenience cost, not a knowledge-loss cost. `agent_hq` remains the repo of record for anything not yet ported. If provenance is ever needed for a specific file, it can still be found in `agent_hq`'s own history.
