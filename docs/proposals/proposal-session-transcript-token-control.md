---
schema_version: 2
title: Session-transcript token control — phase-gating, cache hygiene, and agent-result compression
status: accepted
owner: matthias
created: 2026-08-03
updated: 2026-08-04
supersedes:

impact:
  scope: cross_project
  architecture_change: false
  external_contract_change: true
  boundaries:
    - factory/skills/handoff/SKILL.md
    - factory/scripts/handoff-lint
    - factory/rulebooks/conventions/handoff-format.md
    - factory/rulebooks/conventions/report-format.md
    - factory/rulebooks/conventions/cache-hygiene.md
    - factory/playbooks/greenfield-development.md
    - factory/playbooks/feature-addition.md
    - factory/scripts/usage-capture
    - factory/skills/retrospective/SKILL.md
    - factory/agents/requirements-agent.md
    - factory/agents/architecture-agent.md
    - factory/agents/spec-review-agent.md
    - factory/agents/architecture-review-agent.md
    - factory/agents/qa-agent.md
    - factory/agents/reconciliation-agent.md
    - factory/agents/implementation-agent.md
    - factory/agents/developer-agent.md

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - operations

estimate:
  as_of: 2026-08-03
  basis: analogous_change
  confidence: medium
  human_review_hours:
    min: 3.0
    max: 6.0
  normalized_tokens:
    min: 20000
    max: 50000
---

# Feature Request: Session-transcript token control — phase-gating, cache hygiene, and agent-result compression

## Summary

Token spend in a long multi-phase agent session is dominated by re-reading a growing transcript, not by task complexity or by output. This proposal adds four factory-level mechanisms: hard phase boundaries backed by a Factory-owned `handoff` skill and deterministic validator, agent-result injection as a bounded summary-plus-file-path envelope, on-demand chunked reads, and retrospective usage signals. The one question it answers that the factory cannot answer today: *how does a long agent session keep its per-turn input cost bounded, instead of growing monotonically with transcript length?*

## Motivation

A retrospective on a measured 189-turn, 7-phase session (requirements → spec review → PRD → architecture dispatch → architecture review → architecture remedies → retrospective) measured the cost structure directly from the session log:

| Metric                            | Value                                       |
| --------------------------------- | ------------------------------------------- |
| Total tokens billed               | 26,228,761                                  |
| Total cost                        | €7.55                                       |
| Input : output ratio              | 33 : 1                                      |
| Input share of cost               | 99.4%                                       |
| Cache-hit rate                    | 79.3%                                       |
| Cache-miss turns (11% of turns)   | 62% of full-rate input spend (3.32M tokens) |
| Phase-9 (turns 144–161) avg input | 11.3× phase-1                               |
| Top turn input                    | 273,510 tokens                              |

Three structural facts emerge from the data, none of which the factory currently addresses:

1. **Input is 99.4% of cost; output is 0.6%.** Any optimisation that targets output (terse replies, caveman compression) is optimising 0.6% of the budget. The lever is input.
2. **Input per turn tracks transcript length, not task complexity.** Phase-9 turns doing similar work to phase-1 turns cost 11× more, solely because the conversation was longer. The transcript only grows; nothing in the factory's workflow compacts or truncates it between phases.
3. **Cache misses are the single largest waste.** 21 of 189 turns had no cache hit and carried 3.32M full-rate input tokens. The session log establishes the cost but not one universal cause. The controlled follow-up experiment found different behavior for same-process tool continuations and process resumes, so cache findings must retain CLI/provider/lifecycle context.

The factory already has a `token-usage-tracking` proposal (implemented) for *capturing* usage and an `agent-dispatch-token-efficiency` proposal (open) for *dispatch-side* waste (stale bases, stranded replies). Neither addresses *in-session transcript-driven waste*. This proposal fills that gap. It is complementary, not overlapping: dispatch efficiency prevents wasted *child runs*; this proposal prevents wasted *parent-session turns*.

**Why now.** The retrospective that produced this data was itself the session that paid the cost. The mechanisms proposed here are not speculative — every one is evidenced by a specific turn or phase in the measured session. The cost will recur on every future multi-phase session until the factory adopts them.

## Core Principles

- **Input is the budget; output is noise.** Every mechanism here targets input-token reduction. Output compression is not in scope — it optimises \<1% of cost.
- **Phase boundaries are the natural truncation points.** A session that runs requirements → architecture → review → remedies does not need the requirements transcript to do the remedies; the artifacts are on disk. Phase-gating is context truncation by session boundary, with no information loss.
- **The factory owns phase-gating, not the model.** Whether and when to phase-gate is a workflow decision encoded in agents and rulebooks, not a model-context-window feature the CLI provides. The factory cannot control the window, but it can control when a session ends and a new one begins.
- **Cache behavior is measured, not guessed.** Large files are read in chunks and only on demand. Cache signals retain CLI/provider identity, and no workflow ritual is adopted without evidence that it improves that implementation.
- **Agent results are files, not transcript content.** A `run_agent` result injected verbatim becomes a permanent per-turn read cost. Writing it to a file and injecting a summary plus path turns a recurring cost into a one-time write.

## Design

### 1. Phase-gated sessions with `handoff` at every boundary

**Mechanism.** Every factory playbook and every long-running agent workflow ends a phase by invoking a Factory-owned, CLI-agnostic `handoff` skill and begins the next phase in a fresh session that reads only on-disk artifacts. The transcript does not cross a phase boundary. Crossing a phase boundary in the same session is a workflow defect; single-phase work is exempt.

**Where the rule lives.** A new `factory/rulebooks/conventions/handoff-format.md` (extending the existing `handoff-format` rulebook if it has content, or creating it) defines:

- The phase boundary set: requirements → review, review → architecture, architecture → review, review → remedies, remedies → planning, planning → implementation. Every arrow is a `handoff`.
- The handoff document's required contents: the phase's on-disk artifact list (with paths), the open findings/decisions carried forward, the next phase's entry point, and a one-paragraph "what was decided, what is open" summary. No transcript replay.
- The receiving session's first action: read the handoff document and the referenced artifacts, not the prior session's history.
- The compression invariant: prose is dense but unambiguous; compression removes wording, never informational detail. Every decision, open item, artifact path, exact 40-character SHA, branch state, gate result, and next action survives intact.

`factory/scripts/handoff-lint` validates the required sections, referenced artifact paths, exact SHA shape, branch/upstream fields, verification evidence, open decisions, and next action before the phase may close. Semantic review remains responsible for detecting omitted information that structural validation cannot infer.

**Playbook and agent updates.** Each factory agent that participates in a multi-phase workflow (`requirements-agent`, `architecture-agent`, `spec-review-agent`, `architecture-review-agent`, `qa-agent`, `reconciliation-agent`, `implementation-agent`, `developer-agent`) gains a "Phase boundary: invoke `handoff`" step in its workflow, and a "Phase entry: read the handoff document and named artifacts" step at its start. The greenfield-development and feature-addition playbooks mark every phase transition as a `handoff` point.

**What does not change.** Short sessions (a single review, a single implementation story) do not phase-gate — there is nothing to truncate. The rule applies only when a session crosses a phase boundary.

### 2. Agent-result injection as summary + file path

**Mechanism.** Before a child agent run by `run_agent`, `dispatch_wave`, or a native sub-agent mechanism returns, it persists its complete result in canonical tracked report and finding artifacts. Its parent-facing response is a bounded result envelope: disposition, finding counts by severity, the complete artifact-path list, and the next action. The full text is read on demand, not on every subsequent turn.

**Where the rule lives.** `factory/rulebooks/conventions/report-format.md` gains a section: "Agent results injected into the orchestrating transcript are a summary plus a file path, never the verbatim result. The full result lives in a tracked file; the transcript carries only the summary." The agents that consume `run_agent` results (`implementation-agent` as dispatcher; any orchestrating role) reference this rule.

**What the summary contains.** The disposition (pass/fail), the count of findings by severity, the file paths of the full report and any finding files, and the one- to three-sentence "what to do next" the result implies. Nothing more. The verbatim finding text, the full reasoning, the per-finding detail — all in the file, none in the transcript.

**What does not change.** The agent's own session writes its full output as before. The compression is only at the *injection* boundary, where the result enters the parent transcript.

### 3. On-demand, chunked large-file reads

**Mechanism.** When a `read` would inject a large file (tens of thousands of tokens), the agent reads in `offset`/`limit` chunks. The first chunk establishes the working context; further chunks are read only if needed.

**Where the rule lives.** A short `factory/rulebooks/conventions/cache-hygiene.md` (new) records the discipline. Every skill that includes a potentially large `read` step (`inspect-spec`, `atam-review`, `fagan-review`, `reconcile-spec`, `derive-spec`, `scaffold-arc42`, etc.) cites it at that step.

**What does not change.** The CLI's prompt-caching mechanism is not modified. Chunking is advisory because a static gate cannot determine which parts of a file the task requires.

**Rejected remediation.** A 2026-08-04 experiment resumed and forked the measured Pi session, read a 66 KB file, and measured the immediate continuation and next same-process probe. The continuation recorded 13,443 full-rate input tokens and 242,176 cached-read tokens; the ordinary probe, without an extra prose turn, recorded 17,759 full-rate input tokens and 242,176 cached-read tokens. The large read did not destroy the prior prefix. A process resume did cause a near-total miss despite a preceding short response. Therefore a mandatory prose-only "restabilisation turn" is not adopted.

### 4. A factory-level usage-pattern signal (optional, low cost)

**Mechanism.** The existing `usage-capture` already records per-turn usage. At session end, capture the cache-miss turn count, cache-miss input-token total, late-phase vs early-phase input-token ratio, and the CLI/provider identity needed to interpret those figures. This is a one-time write to the session log, not a new artifact. The signals are retrospective inputs only in the first release; they are not exposed as live controls to the running agent.

**Where the rule lives.** `factory/scripts/usage-capture` (or its lifecycle script) computes and stores the three derived numbers. `factory/skills/retrospective/SKILL.md` reads them when mining the session for friction.

## Scope

**In the first release:**

- `factory/rulebooks/conventions/handoff-format.md` (new or extended) defines the phase-boundary `handoff` rule, the boundary set, and the handoff-document contents.
- `factory/skills/handoff/SKILL.md` provides the Factory-owned, CLI-agnostic handoff operation and is generated to every supported CLI.
- `factory/scripts/handoff-lint` mechanically validates every phase handoff.
- `factory/rulebooks/conventions/report-format.md` gains the "agent results injected as summary + file path" section.
- `factory/rulebooks/conventions/cache-hygiene.md` (new) records on-demand chunked reads and the measurement-first cache rule.
- Every multi-phase factory agent (`requirements-agent`, `architecture-agent`, `spec-review-agent`, `architecture-review-agent`, `qa-agent`, `reconciliation-agent`, `implementation-agent`, `developer-agent`) gains the "Phase boundary: invoke `handoff`" and "Phase entry: read handoff + artifacts" steps.
- The `greenfield-development` and `feature-addition` playbooks mark every phase transition as a `handoff` point.
- `factory/scripts/usage-capture` (or its lifecycle) adds the three derived usage signals at session end.
- `factory/skills/retrospective/SKILL.md` reads the derived signals when mining a session.
- Proposal-path contracts are updated from `factory/docs/proposals/` to the repository-root `docs/proposals/` location before feature intake proceeds.

**Explicitly deferred (do NOT plan stories for these):**

- A CLI-level or skill-level "context compaction" that summarises the transcript in-place without ending the session. Phase-gating achieves the same effect at lower complexity; in-place compaction loses information and is a model-quality risk.
- An automated cache-miss detector that interrupts a session when the cache breaks. Detection requires session-log access the running agent does not have; the discipline-based approach is sufficient for the first release.
- A prose-only cache-restabilisation turn. The controlled Pi experiment did not show a benefit, and cache behavior is CLI/provider-specific.
- A token-budget gate that hard-stops a session at N tokens. Budgets are project- and phase-dependent; a hard gate would false-stop legitimate long sessions. Retrospective measurement (this proposal's mechanism 4) is the right intervention point.
- A unified cross-CLI transcript format. Each CLI's transcript is its own; the factory's lever is the *workflow* (when sessions end), not the transcript format.
- An ADR for "phase-gating as a token-control measure." This proposal is the input; an ADR would be authored by the `architecture-agent` when the proposal is accepted, not by this proposal.

## Design Details

### What "phase" means here

A phase is a factory workflow phase as already named in `INDEX.yaml` (Requirements, Architecture, Planning, Implementation, Quality, Research) and in the playbooks (`greenfield-development`, `feature-addition`). The phase boundary set is not invented; it is the existing factory phase taxonomy. This proposal only adds the rule that crossing a boundary ends the session.

### Interaction with the `handoff` skill

The first release adds a Factory-owned `handoff` skill because repository inspection found no project-local implementation for any supported CLI. The skill compacts the current phase into a dense, unambiguous restart contract without reducing informational detail. Its generated CLI copies share `handoff-format.md` and `handoff-lint` as their contract.

### Interaction with `agent-dispatch-token-efficiency`

That proposal addresses wasted *child runs* (stale bases, stranded replies, late catches). This proposal addresses wasted *parent-session turns*. They compose: a dispatch-efficient factory still wastes parent-session tokens on transcript growth; a phase-gated factory still wastes child runs on stale bases. Both are needed.

### Interaction with `token-usage-tracking`

That proposal (implemented) captures per-turn usage. This proposal's mechanism 4 adds three derived signals at session end, computed from the captured data — a small extension, not a parallel system.

### What the summary-plus-path rule does not change

Agents that consume `run_agent` results still read the full result file when they need the detail (e.g. `architecture-agent` reading `spec-review-agent`'s findings to remedy them). The compression is only at the *injection* boundary; once the orchestrating session decides to act on a result, it reads the file deliberately, paying the cost once instead of every turn.

### Cost of the phase-gating rule

Ending a session and starting a new one has a small cost: the new session reads the handoff document and the on-disk artifacts (a few thousand tokens), where the prior session would have re-read the full transcript (hundreds of thousands of tokens by late phase). The crossover is reached within a few turns of the new phase. For sessions that stay within one phase, there is no cost — the rule does not apply.

## Open Questions

None. Phase gating is a hard workflow contract; the first release owns a cross-CLI handoff skill and validator; the prose-only cache remedy is rejected by experiment; and derived usage signals are retrospective-only.

## Completion Criteria

- `factory/rulebooks/conventions/handoff-format.md` defines the phase-boundary set, the handoff-document contents, and the mandatory-invoke rule.
- The Factory-owned `handoff` skill is generated for every supported CLI and produces dense, unambiguous handoffs without dropping informational detail.
- `factory/scripts/handoff-lint` blocks phase closure when required structure, paths, exact SHAs, state, evidence, decisions, or next action are absent or malformed.
- `factory/rulebooks/conventions/report-format.md` documents the agent-result summary-plus-path injection rule.
- `factory/rulebooks/conventions/cache-hygiene.md` records on-demand chunked reads, provider-qualified measurement, and no unsupported prose-restabilisation ritual.
- Every multi-phase factory agent listed in `boundaries` has a "Phase boundary: invoke `handoff`" step and a "Phase entry: read handoff + artifacts" step.
- The `greenfield-development` and `feature-addition` playbooks mark every phase transition as a `handoff` point.
- `factory/scripts/usage-capture` (or its lifecycle) writes the three derived usage signals plus CLI/provider identity at session end.
- `factory/skills/retrospective/SKILL.md` reads the three derived signals and uses them in the "Caused Friction" category.
- A retrospective on a session that uses the phase-gating rule shows a lower late-phase vs early-phase input ratio than the 11.3× measured in the session that motivated this proposal.

## Guiding Rule

A long agent session's per-turn input cost should track the work being done, not the length of the conversation that preceded it — and the factory's workflow, not the model's context window, is what keeps it that way.
