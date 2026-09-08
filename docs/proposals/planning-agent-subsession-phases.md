---
schema_version: 2
title: Planning Agent Subsession Phases
status: draft
owner: Matthias Daues
created: 2026-09-08
updated: 2026-09-08
supersedes:

impact:
  scope: factory_internal
  architecture_change: false
  external_contract_change: false
  boundaries:
    - factory/agents/planning-agent.md
    - factory/skills/create-backlog/SKILL.md
    - factory/skills/create-backlog-epics/SKILL.md
    - factory/skills/create-backlog-write-epics/SKILL.md
    - factory/skills/create-backlog-story-slices/SKILL.md
    - factory/skills/create-backlog-stories/SKILL.md

governance:
  assurance: routine
  risk_domains:
    - operations

estimate:
  as_of: 2026-09-08
  basis: judgment
  confidence: low
  human_review_hours:
    min: 0.5
    max: 1.0
  normalized_tokens:
    min: 3000
    max: 8000
  estimated_consumption:
    min: 45000
    max: 120000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Planning Agent Subsession Phases

## Summary

Split the planning agent's single long-running session into three sequential interactive
subsessions — epic slicing, test-design enrichment, and story slicing/writing — each
starting with a clean context window and handing off state exclusively through files on
disk. A thin dispatcher sequences the phases and manages user gates between them.

## Motivation

The planning agent accumulates tool output (file reads, diffs, discussion history) across
five skill invocations in a single session. By the story-writing phase, context may reach
250–400K tokens, most of it stale output from earlier phases. Auto-compaction reclaims
some of this, but the boundary and retention are unpredictable.

The agent already uses file-mediated state — each phase reads its inputs from disk and
writes its outputs to disk. The conversation context carries redundant copies of what the
filesystem already holds.

## Proposed Design

### Three subsession phases

| Phase | Subsession              | Input (disk)                               | Output (disk)              | Interactive |
| ----- | ----------------------- | ------------------------------------------ | -------------------------- | ----------- |
| 1     | Epic slicing            | scope map, `.feature` files, agent-context | `backlog/epics.md`         | yes         |
| 2     | Test-design enrichment  | `backlog/epics.md`, testing.yaml           | updated `backlog/epics.md` | yes         |
| 3     | Story slicing + writing | `backlog/epics.md`                         | `backlog/ST-NNNN.md` files | yes         |

Each subsession is a full interactive loop: the user discusses, iterates, approves, and
the subsession writes the result to disk before terminating. No conversational state
crosses subsession boundaries — only files.

### Dispatcher

A thin sequencer that:

1. Runs the testing-regime pre-flight check (no subsession needed).
2. Launches phase 1 subsession; waits for completion.
3. Launches phase 2 subsession; waits for completion.
4. Launches phase 3 subsession; waits for completion.
5. Commits all indexed artifacts to `dev`.

The user interacts directly with each subsession (model B — no relay layer).

### Token economics (medium project, ~4 EPICs / 15 stories)

| Approach                    | Estimated total input tokens |
| --------------------------- | ---------------------------- |
| Single session (current)    | 250–400K                     |
| Single session + compaction | 100–180K                     |
| Three subsessions           | 80–140K                      |

Subsessions save ~30–50% over compaction alone, more on larger projects. The saving comes
from phase 3 (the heaviest) starting with a clean ~6.5K base instead of a compacted
residual of 20–50K.

## Current Decision

**Parked.** Auto-compaction captures the majority of the token savings for zero
architecture work and preserves the simpler single-session user experience. The
subsession split becomes worth revisiting if:

- Late-phase quality degrades because compaction loses important context from earlier
  phases (predictability problem, not cost problem).
- Project sizes grow large enough that compacted residual still dominates phase 3 context.
- The dispatcher pattern is needed elsewhere and the infrastructure cost is already paid.

## Open Questions

- If the user needs to revise epic boundaries during phase 3, the current model requires
  restarting from phase 1. Acceptable, or does this need a "go back" mechanism?
- Should the dispatcher be a skill, a modified planning-agent, or a standalone agent?

## Alternatives Considered

| Alternative                              | Verdict           | Rationale                                                                                                |
| ---------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------- |
| Five subsessions (each skill = one call) | Rejected          | Test-design and story-writing are too thin to justify standalone subsessions; three is the natural grain |
| Auto-compaction only (status quo)        | Preferred for now | ~60–70% of the savings, zero architecture cost                                                           |
| Workflow-based orchestration             | Not evaluated     | Overkill for sequential gated phases; workflows shine on parallel fan-out                                |
