---
schema_version: 2
title: Newcomer Onboarding and Incremental Brownfield
status: accepted
owner: md@matthiasdaues.de
created: 2026-08-28
updated: 2026-08-28
accepted: 2026-08-28
supersedes:

impact:
  scope: cross_component
  architecture_change: false  # manual override — no boundary change despite entity-model additions
  external_contract_change: false
  boundaries:
    - docs/arc42/beginner-intro.md
    - factory/playbooks/brownfield-onboarding.md
    - factory/playbooks/feature-addition.md
    - factory/agents/chat-agent.md
    - factory/agents/kit-manager.md
    - factory/agents/coaching-agent.md
    - factory/config/AGENTS.md
    - factory/playbooks/greenfield-development.md

governance:
  assurance: elevated
  risk_domains:
    - compatibility

estimate:
  as_of: 2026-08-28
  basis: judgment
  confidence: low
  human_review_hours:
    min: 2
    max: 4
  normalized_tokens:
    min: 8000
    max: 20000
  estimated_consumption:
    min: 120000
    max: 300000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Newcomer Onboarding and Incremental Brownfield

## Summary

The factory is built for rigour but presents that rigour as a wall, not a
ramp. A newcomer encounters insider vocabulary, a multi-branch menu, and a
heavyweight brownfield pipeline before they have done anything. This
proposal introduces a guided-tour entry path, changes how in-session agents
are assumed, and splits brownfield onboarding into a lightweight "enough to
work" phase and an incremental deepening pulled by feature work. The scope
boundary of the first release is the CLI orientation file, the brownfield
playbook, and the beginner introduction.

## Motivation

Agent Factory is a solo project. A second user stepping into it today feels
like wearing someone else's harness: the arms move in patterns that made
sense for the person who built it, not for a newcomer learning to control
them. Enterprise adoption depends on the brownfield-then-feature-addition
path, which is the universal enterprise story ("I inherited a codebase, I
need to understand it, then I need to change it"). The current brownfield
playbook produces 20+ files before the user can make a single change. The
current feature-addition playbook applies full ceremony regardless of change
size. Both block adoption by front-loading cost before delivering value.

Three specific UX patterns are violated:

- **Progressive disclosure.** The session entrypoint dumps the full factory
  topology on someone who does not know what an agent is.
- **Sensible defaults.** There is no default path for a newcomer; every
  path requires a classification decision in factory vocabulary.
- **Escape hatches.** Once a playbook starts, there is no documented
  "good enough" exit before the terminal condition.

## Core Principles

- The factory is a power multiplier you wear, not a process you follow.
  Onboarding teaches you to move one arm before handing you four.
- Knowledge about a codebase grows in three anchor files
  (`architecture.dsl`, `scope-map.md`, `CONTEXT.md`), not in a scatter
  of dozens. Each change produces a small, reviewable diff.
- Full rigour is the destination, not the starting point. Ceremony scales
  with the size and risk of the change.

## Design

### 1. Session entrypoint revision

Replace the current A/B/C menu with A/B/C/D:

```
What do you want to do?

A — I'm new here — show me around
B — I want to start something (prove an idea, research, build)
C — I want to run an agent or playbook directly
D — I just want to talk something through
```

**Option A — Guided tour.** Read `docs/arc42/beginner-intro.md` and walk
the user through it conversationally, one section at a time, pausing for
questions. Cover: the one idea (you approve each step), the four words
(agent, skill, playbook, gate), the two modes (manual first), and "your
first session." Offer to run `poc-spike` at the end. Before starting, check
for signs the user has been here before (a completed poc-spike, a charter,
prior playbook outputs). If found, acknowledge what they have done and
offer to skip ahead or start fresh.

**Option D — Talk.** Read the `chat-agent` definition (resolve path from
INDEX.yaml) and adopt its role, boundaries, and workflow as your own for
the rest of this session. Do not delegate to a subagent. Open with "What's
on your mind?"

### 2. Adopt pattern for in-session agents

Three agents are documented as "runs in the current session":
`chat-agent`, `kit-manager`, `coaching-agent`. Wherever the entrypoint or a
playbook step calls one of these, the instruction changes from "spawn" to:

> Read the `<agent>` definition (resolve path from INDEX.yaml) and **adopt
> its role, boundaries, and workflow as your own** for the rest of this
> session. Do not delegate to a subagent — you are the `<agent>` now.

This eliminates the relay problem (subagent cannot have a conversation with
the stakeholder) and removes a layer of indirection that confuses newcomers.

### 3. Brownfield-lite: "enough to work" exit

Split the current brownfield-onboarding playbook into two stages with a
documented exit point between them.

**Stage 1 — Enough to work** (new default stopping point):

- `docs/arc42/architecture.dsl` with system context and container views.
- `docs/spec/scope-map.md` populated with existing Rules, all marked
  `implemented`. Populated by the `reverse-map` skill (Design Section 4).
- `CONTEXT.md` seeded with domain vocabulary extracted from type names,
  class names, and module names during the same code-reading pass that
  builds the DSL. This seed is the early form of what becomes arc42
  chapter 12 (Glossary) when the project deepens into full architecture
  documentation. The architecture-agent already reads `CONTEXT.md` as
  input when writing arc42 chapters; seeding it at Stage 1 means the
  derivation path to chapter 12 is live from the start, not deferred
  until a full spec extraction.
- Structurizr validation passes.

Three files. The user understands the structural shape (what containers
exist, how they connect), the functional inventory (what the system does,
rule by rule), and the domain language (what terms mean). Grilling and
domain-modeling skills work from day one. They can make a change now.

**Stage 2 — Full reverse engineering** (opt-in deepening):

The current Phases 3-6 of brownfield onboarding: specification extraction,
component-resolution pass, ATAM review, reconciliation. Available when the
user or the change warrants it, but not required before the first
feature-addition.

The playbook presents the Stage 1 exit explicitly:

> "You now have the structural shape and the functional inventory. You can
> start feature work from here. Want to go deeper, or start building?"

### 4. New skill: `reverse-map`

A new skill that builds the scope map from whatever sources exist —
code, tests, docs, wiki pages, Postman collections, Jira exports, or
verbal stakeholder knowledge. Replaces the open question about how
brownfield-lite populates the scope map without derive-spec artifacts.

**How the user experiences it:**

The skill opens with plain language:

> "I'm going to look through your codebase to understand what this
> system does. I'll start with tests and code, then you can point me at
> anything else — docs, wiki pages, API specs, whatever you have. I'll
> show you what I find as I go."

It works in short passes, presenting results in batches organised by
domain area:

> "Here's what I found in the payments area:"
>
> - Accepts a payment (3 tests, main API endpoint)
> - Processes partial refunds (2 tests)
> - Retries failed webhooks (1 test, retry handler)
> - *No tests found for batch settlement, but there's a
>   `settlement_batch.py` with no callers — dead code?*
>
> "Does this match what you know?"

The user confirms, corrects, or adds ("you're missing the subscription
billing — that's the big one"). The skill incorporates corrections and
moves to the next domain area.

After sweeping code and tests:

> "That's what I found in the code. Got anything else — wiki pages, API
> docs, a README someone wrote last year? I can cross-check."

The user feeds additional sources or says "that's enough." The skill
writes the scope map and summarises:

> "Here's your inventory — 34 behaviors, 28 backed by tests, 4 in code
> only, 2 from docs I couldn't match to code. You can start building
> from here. The inventory grows as you add features."

**UX principles:**

- Progressive results batched by domain — not one giant list at the
  end.
- Plain language throughout — no "populating scope-map rows from test
  evidence."
- The user controls depth — "that's enough" is always valid.
- Additional sources are offered, not required.
- Discrepancies are surfaced as questions, not findings.
- The output is readable in two minutes.

**Technical approach (behind the curtain):**

The skill follows a forensic evidence hierarchy. Tests are the most
reliable source because they are mechanically verified behavioral
claims. The hierarchy determines the confidence level for each
scope-map row:

| Source type                      | Confidence          | Why                                        |
| -------------------------------- | ------------------- | ------------------------------------------ |
| Passing test                     | Verified            | Mechanically proven behavioral claim       |
| Failing/skipped test             | Flagged             | Documents intent, known broken or deferred |
| Code entry point                 | High                | Exists and executes, but not test-verified |
| Test fixture/factory             | Medium-high         | Reveals entity model and relationships     |
| API spec (OpenAPI, Postman)      | Medium              | Declared contract, may not match code      |
| Repo docs (README, comments)     | Medium-low          | Close to code, but often stale             |
| External docs (Confluence, wiki) | Low                 | Furthest from code, most likely to drift   |
| Stakeholder verbal claim         | Lowest (but unique) | Tribal knowledge, unfindable elsewhere     |

The scope-map output carries provenance:

| Rule                | Status      | Confidence | Sources                                        |
| ------------------- | ----------- | ---------- | ---------------------------------------------- |
| Process payment     | implemented | verified   | `test_pay.py`, `src/pay.py`                    |
| Send refund webhook | implemented | verified   | `test_refund.py`, `src/refund.py`              |
| Batch settlement    | implemented | claimed    | Confluence/settlement (no test, no code match) |

Rows backed by passing tests are facts. Rows from docs alone are
claims that may be stale. The user sees both, and the Sources column
tells them why.

**Order of operations:**

1. Find the tests. Tests are the map someone already drew.
2. Find the entry points. HTTP routes, CLI commands, queue consumers,
   cron jobs.
3. Triangulate: match tests to entry points to docs. The truth is in
   the overlap; contradictions are the most valuable findings.
4. Present in batches by domain area, confirm with stakeholder.
5. Accept additional sources (URLs, files, pasted text), cross-check
   against existing findings.
6. Write the scope map. The user calls when it is good enough.

### 5. Feature-addition as incremental deepening

Each feature-addition run naturally deepens the three anchor files:

- A new Rule in `scope-map.md` for what the feature adds.
- Component detail in `architecture.dsl` if the structural shape changes.
- New domain terms in `CONTEXT.md` as the grilling and domain-modeling
  skills surface them during requirements clarification. As the vocabulary
  accumulates, `CONTEXT.md` matures into the source from which arc42
  chapter 12 (Glossary) is derived — the same derivation path that exists
  today, just fed earlier and grown incrementally instead of produced in
  one pass.

The detailed prose (arc42 chapters, supplementary specs) grows as a
side effect of feature work, not as a front-loaded investment. Over time,
repeated feature-additions produce the same completeness that the full
brownfield pipeline would have — but incrementally, with each step justified
by a real change, and each diff small enough for an enterprise PR review.

## Scope

**In the first release:**

- Revised session entrypoint in the CLI orientation file (CLAUDE.md and
  equivalents) with the four-option menu and guided tour instructions.
- Adopt-pattern wording for chat-agent, kit-manager, and coaching-agent in
  the entrypoint and in any playbook step that invokes them.
- Brownfield-onboarding playbook split into Stage 1 (enough to work) and
  Stage 2 (full reverse engineering) with an explicit exit between them.
- Feature-addition playbook prerequisites relaxed: "existing project with
  spec and architecture" softened to "architecture.dsl, scope-map.md, and
  CONTEXT.md exist." Full specification artifacts become optional inputs
  that deepen the process when present.
- Beginner-intro revised to align with the new entrypoint and the
  incremental framing. No new document; edit the existing one.
- New `reverse-map` skill: forensic scope-map population from code,
  tests, and unstructured sources (docs, wikis, API specs, stakeholder
  knowledge). Conversational UX with progressive batched results and
  stakeholder confirmation. Replaces the need for derive-spec artifacts
  before the first scope map.

**Explicitly deferred (do NOT plan stories for these):**

- Automatic newcomer detection (checking for artifacts to offer the tour
  proactively). The tour is offered as a menu choice; detection is a later
  refinement.
- Feature-addition ceremony scaling by change size. The incremental
  deepening is a natural consequence of running feature-addition on a
  brownfield-lite baseline, not a ceremony reduction.
- User profiles or cross-project memory of who has used the factory before.
- Changes to the orchestrator or automatic mode.

## Open Questions

- ~~Should the guided tour be a standalone skill (invocable as
  `/guided-tour`) or only reachable through the entrypoint menu?~~
  **Resolved:** standalone skill at `factory/skills/guided-tour/SKILL.md`.
  The tour covers reorientation on demand ("where am I", "what do I do",
  "what's next"), not just first-time onboarding.
- ~~Does the Stage 1 / Stage 2 split need a gate marker (a file that
  records "Stage 1 complete, user chose to stop here") for downstream
  playbooks to detect, or is the presence of `architecture.dsl` +
  `scope-map.md` without full spec artifacts sufficient signal?~~
  **Resolved:** no gate marker. The presence of the three anchor files
  (`architecture.dsl`, `scope-map.md`, `CONTEXT.md`) is the signal.
  Brownfield depth is a continuum — each feature-addition deepens it.
  Gates discretize and destroy the flow.
- ~~Scope-map population without derive-spec artifacts.~~ **Resolved:**
  the `reverse-map` skill (Design Section 4) populates the scope map from
  code, tests, and unstructured sources. `scope-map-migration` remains
  unchanged for projects that already have derive-spec artifacts.

## Completion Criteria

- A user who has never seen Agent Factory can pick option A, walk through
  the tour, and run a poc-spike without encountering undefined vocabulary
  or needing to leave the session for documentation.
- Picking option D adopts the chat-agent role in the current session; no
  subagent is spawned; the conversation is direct.
- Brownfield onboarding can exit after Stage 1 with a valid
  `architecture.dsl`, `scope-map.md`, and `CONTEXT.md`. The user can
  immediately start a feature-addition from that baseline.
- A feature-addition run against a brownfield-lite baseline adds a Rule to
  the scope map without requiring the full Stage 2 reverse engineering.
  If the feature changes the structural shape, the architecture-agent
  updates `architecture.dsl` in the same run.

## Guiding Rule

The factory should feel like putting on a harness that extends your reach,
not like reading someone else's manual before you are allowed to move.

## Review — 2026-08-28

Reviewer: proposal-review-agent
Reviewed commit: e8c9c4a93e6ab7d1b8118e6f905dd72b71ff198a
Disposition: findings

### Findings

| ID                                    | Severity | Check | Status   | Finding                                                                                                                                                                                             |
| ------------------------------------- | -------- | ----- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [PROP-0013](../findings/PROP-0013.md) | major    | 01    | resolved | CC-3 omits CONTEXT.md from brownfield-lite exit condition; contradicts Scope section which lists it as a prerequisite for feature-addition.                                                         |
| [PROP-0014](../findings/PROP-0014.md) | major    | 03    | resolved | Design Section 3 (Stage 1) says scope-map.md is "populated with existing Rules" but does not state that Stage 1 invokes the reverse-map skill (Section 4). Planning must re-derive this dependency. |
| [PROP-0015](../findings/PROP-0015.md) | minor    | 06    | resolved | Open Question 3 is stale — resolved by Design Section 4 (reverse-map skill).                                                                                                                        |
| [PROP-0016](../findings/PROP-0016.md) | minor    | 05    | resolved | `.claude/CLAUDE.md` affected by entrypoint revision but not listed in impact.boundaries.                                                                                                            |
| [PROP-0017](../findings/PROP-0017.md) | minor    | 08    | resolved | estimated_consumption.min of 80,000 inconsistent with normalized_tokens.min (8,000) x overhead_multiplier (15) = 120,000.                                                                           |
| [PROP-0018](../findings/PROP-0018.md) | minor    | 01    | resolved | CC-4 "optionally deepens the DSL" is not testable — no criterion distinguishes success from failure on deepening.                                                                                   |
| [PROP-0019](../findings/PROP-0019.md) | minor    | 03    | resolved | Factory glossary stub has no output path; Planning needs a file location.                                                                                                                           |

### Check Results

1. **Completion criteria testable?** FAIL — CC-3 omits CONTEXT.md (PROP-0013); CC-4 "optionally deepens" untestable (PROP-0018).
2. **Scope boundary sharp?** PASS — In/Deferred partition is clean; "proactive detection" (deferred) is distinct from "reactive check" (in scope).
3. **Design decomposable?** FAIL — Stage 1 does not reference reverse-map as its scope-map mechanism (PROP-0014); glossary has no output path (PROP-0019).
4. **Impact classification consistent?** PASS — scope, architecture_change, and external_contract_change match the design.
5. **Boundary references exist?** FAIL — `.claude/CLAUDE.md` is affected but unlisted (PROP-0016); all six listed boundaries resolve.
6. **Open questions genuine?** FAIL — OQ-3 is stale, already resolved by Design Section 4 (PROP-0015); OQ-1 and OQ-2 are genuine but undecided despite accepted status.
7. **Motivation justifies timing?** PASS — concrete adoption blocker with three specific UX violations.
8. **Estimate plausible?** FAIL — arithmetic inconsistency in consumption floor (PROP-0017); ranges and multiplier are otherwise reasonable.

### Summary

The proposal's motivation, scope boundaries, and most of the design are strong
and planning-ready. Two major findings block planning readiness: the
brownfield-lite completion criterion omits CONTEXT.md (contradicting the Scope
section), and the reverse-map skill is not wired to Stage 1 as its scope-map
population mechanism, forcing planning to re-derive the dependency. Five minor
findings cover a stale open question, a missing boundary reference, an
arithmetic error, an untestable criterion, and an unspecified output path.
Address the two majors and the proposal is ready to plan from.

## Review — 2026-08-28 (repeat pass)

Reviewer: proposal-review-agent
Reviewed commit: e8c9c4a93e6ab7d1b8118e6f905dd72b71ff198a
Disposition: findings

### Prior Findings

All seven findings from the initial review have been verified as resolved:

- **PROP-0013** (major, Check 01): CC-3 now includes CONTEXT.md in the brownfield-lite exit condition.
- **PROP-0014** (major, Check 03): Stage 1 scope-map line now cross-references the reverse-map skill with "Populated by the `reverse-map` skill (Design Section 4)."
- **PROP-0015** (minor, Check 06): OQ-3 struck through and marked "Resolved" with explanation referencing Design Section 4.
- **PROP-0016** (minor, Check 05): `factory/config/AGENTS.md` added to boundaries (canonical file; `.claude/CLAUDE.md` is a symlink to it). `factory/playbooks/greenfield-development.md` also added as a coaching-agent invocation site.
- **PROP-0017** (minor, Check 08): `estimated_consumption.min` corrected from 80,000 to 120,000; arithmetic now consistent (8,000 x 15 = 120,000).
- **PROP-0018** (minor, Check 01): CC-4 rewritten with concrete testable condition: "If the feature changes the structural shape, the architecture-agent updates `architecture.dsl` in the same run."
- **PROP-0019** (minor, Check 03): Factory glossary stub removed entirely. CONTEXT.md serves as the vocabulary collector with explicit derivation path to arc42 chapter 12.

### Findings

| ID                                    | Severity | Check | Status | Finding                                                                                                                                                                                               |
| ------------------------------------- | -------- | ----- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [PROP-0020](../findings/PROP-0020.md) | minor    | 05    | open   | `factory/skills/reverse-map/SKILL.md` listed in `impact.boundaries` but does not exist at the reviewed commit. The skill is a new artifact created by this proposal, not an existing file to inspect. |

### Check Results

1. **Completion criteria testable?** PASS — All four criteria are verifiable without asking the author; CC-3 now includes CONTEXT.md, CC-4 now has a concrete trigger condition.
2. **Scope boundary sharp?** PASS — In/Deferred partition is clean and mechanically separable.
3. **Design decomposable?** PASS — All five design sections provide enough specificity for Planning to write INVEST stories without re-deriving the design.
4. **Impact classification consistent?** PASS — scope, architecture_change, and external_contract_change match the design.
5. **Boundary references exist?** FAIL — Eight of nine boundaries resolve. `factory/skills/reverse-map/SKILL.md` does not exist at the reviewed commit (PROP-0020). It is a new artifact this proposal creates, fully described in the Design section.
6. **Open questions genuine?** PASS — OQ-1 and OQ-2 are genuine with stated trade-offs; OQ-3 is properly resolved and marked.
7. **Motivation justifies timing?** PASS — Concrete adoption blocker with three specific UX violations.
8. **Estimate plausible?** PASS — Arithmetic correct (120,000 = 8,000 x 15; 300,000 = 20,000 x 15); multiplier of 15 is at the low end of the typical 15-25x range but defensible for a process/documentation change; confidence: low and basis: judgment are honest.

### Summary

All seven prior findings are resolved. The two major findings (CONTEXT.md omitted from CC-3, reverse-map not wired to Stage 1) are fixed cleanly. One new minor finding remains: the reverse-map skill file is listed as a boundary but does not exist because it is a new artifact. Seven of eight checks pass; the boundary-reference check fails on this single non-existent path. The proposal is ready to plan from once this minor listing error is corrected.
