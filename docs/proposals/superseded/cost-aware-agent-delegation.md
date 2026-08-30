---
schema_version: 2
title: Cost-Aware Agent Delegation
status: superseded
owner: md@matthiasdaues.de
created: 2026-08-19
updated: 2026-08-19
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - factory/agents/implementation-agent.md
    - factory/agents/developer-agent.md
    - factory/agents/planning-agent.md
    - factory/rulebooks/conventions/dispatch-contract.md
    - factory/scripts/backlog-lint
    - factory/rulebooks/templates/story.md
    - factory/skills/create-backlog/SKILL.md
    - factory/scripts/dispatch
    - config/model.conf

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - operations
    - compatibility

estimate:
  as_of: 2026-08-19
  basis: analogous_change
  confidence: medium
  human_review_hours:
    min: 2.0
    max: 5.0
  normalized_tokens:
    min: 8000
    max: 16000
  estimated_consumption:
    min: 160000
    max: 320000
    overhead_multiplier: 20
    playbook: feature-addition
---

# Feature Request: Cost-Aware Agent Delegation

## Summary

Give the implementation dispatcher a decision procedure for *which model tier
runs which story*, *what a subagent is told*, and *what happens when a story
fails*. Today the dispatcher reads a `tier` field written by the planner,
sends a two-line prompt, and marks a failure `blocked` for a human to resolve.
This feature adds a task-shape tier rubric, a script-generated subagent
handoff contract under a hard token budget, an evidence-gated escalation
predicate with a closed failure-class vocabulary, and an optional
seams-then-implement split that moves implementation work down a tier. The
first release changes decision procedure and prompt composition only; it adds
no new agent role.

## Motivation

The Factory already holds the *principle* of cheap delegation.
[dispatch-contract.md § Model Tier And Wave Size](../../../factory/rulebooks/conventions/dispatch-contract.md#model-tier-and-wave-size)
tells a dispatcher to set the cheapest tier that fits, cap waves at six, and
estimate spend before launching. That guidance arrived through
[agent-dispatch-token-efficiency.md](../implemented/agent-dispatch-token-efficiency.md)
after a research run exhausted the monthly spend limit. What the Factory lacks
is the *procedure* that turns the principle into repeatable decisions:

1. **No rubric.** `tier` is authored by the planning agent from unstated
   judgment. Nothing records how a story's shape maps to a tier, and the
   dispatcher cannot disagree with the planner on the record.

2. **A two-line handoff.** The subagent prompt in
   [implementation-agent.md § Workflow](../../../factory/agents/implementation-agent.md#workflow)
   names a story path and a branch. It states no allowed write paths, no
   forbidden actions, no stop conditions, and no return schema. The dispatcher
   then verifies the result against git and the gates because the report
   cannot be trusted — a verification cost the contract itself could reduce.

3. **No escalation, and no policy against the wrong escalation.** A failed
   story becomes `blocked` and waits for a human. When a human does intervene,
   the tempting move is a stronger model, which is frequently the wrong answer:
   a subagent that lacked an input needs a better handoff, not deeper
   reasoning. Nothing in the Factory says so, and nothing prevents a retry
   from silently costing a second full session.

4. **A cost lever left unused.** [developer-agent.md § Workflow](../../../factory/agents/developer-agent.md#workflow)
   already skips the Red phase when a story carries a non-empty `tests:`
   field, reading those tests as its specification. Nobody authors those tests
   on purpose. The most expensive part of a story — deciding the seams — is
   never separated from the cheapest part, making them green.

The reference implementation that prompted this proposal is the
`cost-aware-subagent-orchestrator` skill in the LSF-Fliegerlager-Webapp
repository. Its contribution over current Factory practice is precisely the
four items above; its wave-sizing, disjoint-write-scope, and no-double-assign
rules are already Factory law.

## Core Principles

- **Deterministic where the decision is mechanical.** A tier suggestion, a
  prompt budget, and an escalation predicate are computable from recorded
  state. They belong in `factory/scripts/dispatch`, not in dispatcher
  judgment — per [foundational-principles.md § Agentic Creation, Deterministic Validation](../../../factory/rulebooks/conventions/foundational-principles.md#agentic-creation-deterministic-validation).
- **Missing context is a handoff defect, not a capability defect.** Only two
  failure classes may raise the tier. Every other class re-dispatches at the
  same tier with an amended handoff.
- **The handoff contract is substitutive, not additive.** Every clause added
  to the dispatch prompt is removed from static agent prose or dropped as
  inapplicable. Growth is bounded by a measured budget, because a diluted
  prompt degrades compliance — per [foundational-principles.md § Eichhorst's Principle](../../../factory/rulebooks/conventions/foundational-principles.md#eichhorsts-principle).
- **The planner's tier stands unless overridden on the record.** The rubric
  advises; it never silently rewrites a story.
- **One escalation per story, ever.** A second failure after escalation is
  terminal and belongs to a human.

## Design

This feature layers on the accepted
[mechanize-dispatch-orchestration.md](mechanize-dispatch-orchestration.md),
which moves deterministic orchestration into `factory/scripts/dispatch`. That
script already computes a wave plan with per-story tiers, and already emits a
subagent prompt template from `dispatch prepare-wave` and
`dispatch prepare-story`. Those two outputs are the insertion points for
everything below. Where this proposal specifies script behaviour, it extends
subcommands that proposal defines.

**Sequencing.** These stories are blocked on
[mechanize-dispatch-orchestration.md](mechanize-dispatch-orchestration.md)
being implemented; `factory/scripts/dispatch` does not exist yet. One
amendment to that proposal is made now rather than after the fact: its
`dispatch mark-failed <story-id> --reason <text>` becomes
`dispatch mark-failed <story-id> --class <class> --evidence <path>`, so the
subcommand is built once against its final signature instead of being shipped
and then replaced. The amendment touches an unimplemented subcommand only, and
the owner has ruled it immaterial: that proposal keeps `status: accepted`.

### Axis 1 — Task-shape tier rubric

`dispatch plan` computes a *suggested* tier for every story from fields the
story file already declares, and reports it beside the declared `tier`. The
rubric never rewrites a story. It disposes of a mismatch asymmetrically:

- **Under-tiering against a `strong` suggestion blocks.** Where the rubric
  suggests `strong` and the story declares `standard` or `economy`,
  `dispatch init` exits non-zero until the mismatch is resolved. The `strong`
  row fires only on high-blast-radius write paths, and there an under-tiered
  agent does damage the gates catch late or not at all.
- **Every other mismatch warns.** Over-tiering costs money and nothing else. A
  crude rubric will disagree often, and blocking on the cheap direction buys
  friction without safety.

Either way the dispatcher resolves the mismatch with the user before
`dispatch init` succeeds, and the resolution is recorded in the ledger.

Signals are drawn only from validated frontmatter — `outputs`, `tests`,
`deps`, `epic`, and one new field — so the rubric stays computable without
reading story prose. Stories gain:

```yaml
risk_domains: [security]   # optional; security | privacy | data_integrity |
                           # compatibility | reliability | operations
```

**Risk is a property of the change, not of the feature it belongs to.** The
field is authored per story and is never inherited from the originating
proposal's `governance.risk_domains`. Recolouring a hover highlight and
repointing an identity-provider URL can belong to one proposal, and
inheritance would tier them identically. Write paths are no better a proxy:
both changes may land in the same directory while differing entirely in what a
mistake costs.

`security`, `privacy`, and `data_integrity` raise the suggestion to `strong`.
`compatibility`, `reliability`, and `operations` do not on their own — nearly
every story touches one of them, so treating them as escalation signals would
make the rubric suggest `strong` for almost everything and mean nothing.

`backlog-lint` validates the field against the closed six-value enum and
rejects any other value. The field is optional; an absent `risk_domains` is
an empty list, and the rubric falls through to its remaining rows.

| Condition, evaluated top to bottom, first match wins                                                                                                                        | Suggested tier |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| `risk_domains` includes `security`, `privacy`, or `data_integrity`; or `outputs` touches `factory/scripts/`, `factory/rulebooks/`, a git hook, or `.pre-commit-config.yaml` | `strong`       |
| `outputs` spans two or more top-level directories, or `deps` has three or more entries                                                                                      | `standard`     |
| `tests` is non-empty and `outputs` stays within one top-level directory                                                                                                     | `economy`      |
| `outputs` stays within one top-level directory and `tests` is absent                                                                                                        | `standard`     |
| otherwise                                                                                                                                                                   | `standard`     |

The rubric is deliberately crude. Its purpose is to make the planner's
implicit reasoning visible and arguable, not to be right unaided. It is
recorded in [dispatch-contract.md](../../../factory/rulebooks/conventions/dispatch-contract.md)
as a new section and cited from
[planning-agent.md](../../../factory/agents/planning-agent.md), so the planner
assigns tiers from the same table the dispatcher checks them against.

### Axis 2 — Subagent handoff contract

`dispatch prepare-wave` and `dispatch prepare-story` generate the full
subagent prompt from the story file and the prepared worktree, replacing the
prose template in
[implementation-agent.md § Workflow](../../../factory/agents/implementation-agent.md#workflow).
The generated prompt carries exactly seven parts:

| Part              | Source                           | Content                                                                                                                       |
| ----------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Outcome           | story file                       | Story ID, title, and the path to its acceptance criteria — referenced, never inlined                                          |
| Workspace         | script                           | Worktree path and feature branch                                                                                              |
| Allowed writes    | story `outputs`                  | The declared globs, verbatim; nothing else may be written                                                                     |
| Forbidden actions | fixed                            | Merge, push, branch or worktree creation, ledger writes, edits to other story files, any hook bypass                          |
| Required checks   | `config/project.json` and script | The project `test_command`, then `factory/scripts/validate`                                                                   |
| Stop conditions   | fixed                            | Ambiguous acceptance criterion; a required input absent; a needed write outside `outputs`; a test the agent believes is wrong |
| Return envelope   | fixed schema                     | `status`, `commit_sha`, `files_changed`, `checks`, `blockers`, `failure_class`                                                |

Three clauses are *removed* in the same change, which is what keeps the budget:

- The `verify-base` preamble, already made redundant by
  [mechanize-dispatch-orchestration.md](mechanize-dispatch-orchestration.md),
  which runs the check before the subagent is spawned.
- The verbatim sub-agent addressing clause from
  [dispatch-contract.md § Sub-Agent Addressing](../../../factory/rulebooks/conventions/dispatch-contract.md#sub-agent-addressing).
  A developer agent spawns no sub-agents; the clause is inapplicable and is
  emitted only for dispatches whose target role may fan out.
- The narrative workflow restatement, which duplicates
  [developer-agent.md § Workflow](../../../factory/agents/developer-agent.md#workflow)
  and the `implement-issue` skill the agent already loads.

The script measures the assembled prompt with the fixed cross-CLI tokenizer of
[ADR-0007](../../adr/0007-normalize-runtime-usage-through-cli-adapters.md) and
refuses to emit a prompt above the budget declared in Completion Criteria.
The budget is a mechanical gate, not an aspiration.

### Axis 3 — Evidence-gated escalation

Escalation is a script decision over recorded ledger state, not a judgment
call. It rests on a closed failure-class vocabulary supplied when a story is
marked failed.

`dispatch mark-failed <story-id> --class <class> --evidence <path>` accepts
only these classes:

| Class                    | Meaning                                                                                             | Disposition                                                                            |
| ------------------------ | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `context_missing`        | The subagent reported it lacked an input that exists in the repository                              | Re-dispatch, **same tier**, handoff amended with the path                              |
| `contract_violation`     | Wrote outside `outputs`, skipped a required check, or committed without the story ID                | Re-dispatch, **same tier**, contract restated; a second occurrence is terminal         |
| `environment`            | Worktree, base, tooling, or test-harness failure unrelated to the story                             | Fix the environment, re-dispatch, **same tier**                                        |
| `spend_death`            | The session died at a spend or infrastructure limit                                                 | Re-dispatch, **same tier**                                                             |
| `seam_defect`            | The implementer stopped because a pre-authored test in `tests` is wrong                             | Re-dispatch the **seam session**, same tier; not charged to the implementation session |
| `acceptance_unmet`       | Inputs present, contract honoured, session ran to completion, acceptance criteria still unsatisfied | **Escalate one tier**                                                                  |
| `contradictory_evidence` | The subagent reported success and a gate falsified it                                               | **Escalate one tier**                                                                  |

`dispatch escalate <story-id>` exits non-zero unless every one of these holds:

1. The ledger records exactly one prior attempt for this story with
   `status: failed` and `session: impl`. Attempts recorded against
   `session: seam` are not counted — a seam author's bad test is not the
   implementer's failure and must not consume the story's one escalation.
2. That attempt's recorded class is `acceptance_unmet` or
   `contradictory_evidence`.
3. That attempt's `verify_base` passed and its `premerge_check` did not fail
   on a scope violation — a scope violation is a contract failure, not a
   capability failure.
4. The story's effective tier is not already `strong`.
5. The recorded evidence names the specific unmet acceptance criterion and
   the artifact demonstrating it.
6. No other story in the current wave has already escalated.

On success the script writes a new attempt entry at tier + 1 and re-prepares
the story. A failure after escalation is terminal: the story is marked
`blocked` and returned to the user. There is no second escalation.

Condition 6 is the wave-level cap. A second `acceptance_unmet` in the same
wave is evidence of systematic under-tiering — a planning fault — rather than
six independent capability faults, and blocking forces that diagnosis instead
of paying for it story by story. It also bounds the worst case: one extra
session per wave rather than one per story, which on the figures in
[Cost Analysis](#cost-analysis) is the difference between roughly 1.7 million
and 10 million tokens.

The ledger schema in
[dispatch-contract.md § Dispatch Ledger](../../../factory/rulebooks/conventions/dispatch-contract.md#dispatch-ledger)
gains an `attempts` list per story, each entry recording `session`
(`seam` or `impl`), `tier`, `failure_class`, `evidence`, `commit_sha`, and
`normalized_total` from the usage record. Without the attempt history the
predicate has nothing to evaluate.

### Axis 4 — Seams-then-implement split

An optional per-story strategy that separates the expensive decision from the
cheap execution. Stories gain one optional frontmatter field:

```yaml
strategy: direct | seams-first    # default: direct
```

`seams-first` runs two sessions in place of one:

1. **Seam session**, at the story's declared `tier`. It writes only test files
   and commits them, populating the story's `tests:` field. Its allowed writes
   are the story's test paths alone, enforced mechanically by
   `premerge-check --scope` rather than by instruction.
2. **Implementation session**, at one tier below the declared tier, floored at
   `economy`. It reads the committed tests as its specification and goes
   straight to Green — the path
   [developer-agent.md § Workflow](../../../factory/agents/developer-agent.md#workflow)
   already defines for a non-empty `tests:` field. It may not modify the test
   files. An implementer that believes a test is wrong stops and reports
   `failure_class: seam_defect`, which returns the work to the seam session
   rather than escalating the implementer.

Each session records its own `attempts` entry, tagged `session: seam` or
`session: impl`. Only `impl` entries count toward the escalation predicate, so
a story may cycle through a corrected seam session without spending the one
escalation its implementation session is allowed.

`backlog-lint` validates the new field against the enum, and rejects
`seams-first` on a story whose `tests` paths fall outside its declared
`outputs`.

Automatic selection of `strategy` is out of scope. The planner sets it; the
`dispatch plan` output shows it; the user confirms it.

## Cost Analysis

The obvious objection to Axis 2 is that a longer prompt costs input tokens on
every iteration. Measured against this repository's own captured usage, that
cost is real and third-order.

### Method and caveat

Aggregated from 91 sessions in `.agent-factory/usage/*.jsonl`, produced by
`factory/scripts/usage-capture`. The `reported_*` fields in those records are
**cumulative per session**, not per turn; the figures below take the last
record of each session. Summing every record inflates the total roughly
eleven-fold and is the error to avoid when this measurement is repeated.

### Observed

| Measure                                             | Value                                   |
| --------------------------------------------------- | --------------------------------------- |
| Sessions captured                                   | 91                                      |
| Total billed tokens                                 | 805,760,228                             |
| Fresh input share of input-side tokens              | 26.2%                                   |
| Cache-write share                                   | 2.4%                                    |
| Cache-read share                                    | 71.5%                                   |
| Standalone developer-agent sessions                 | 294,924 · 504,298 · 910,742 · 1,738,884 |
| Combined dispatcher and developer session, 48 turns | 25,235,519                              |

The cache-read share decides the question. A prompt prefix is written to cache
once and read at roughly a tenth of the write rate on every later turn.

### Cost of the handoff contract

For an added 800 prompt tokens over a thirty-turn session, the billed cost is
one cache write plus thirty cache reads: `800 × 1.25 + 800 × 0.1 × 30`, about
**3,400 token-equivalents**. Against a 500,000-token developer session that is
**0.68%**; against the observed 25,235,519-token combined session, **0.015%**.
Were caching absent entirely, the same 800 tokens across thirty turns would
cost 24,000, about **5%**.

Break-even therefore requires the contract to prevent one wasted developer
session per **150 dispatches** under caching, or per **20** in the worst case
without it. The charter dispatch ST-0074 through ST-0085 lost one story of
twelve to a full wasted subagent run — a rework rate near **8%**, which clears
the cached threshold by roughly twelvefold. On tokens alone the contract is
very likely to pay for itself.

### Where the token risk actually sits

| Axis                  | Cost per use                               | Rank           |
| --------------------- | ------------------------------------------ | -------------- |
| Escalation, per retry | One full session, 300,000–1,700,000 tokens | 1              |
| Seams-then-implement  | Negative: moves implementation down a tier | 1, as a saving |
| Tier rubric           | Zero subagent tokens                       | 3              |
| Handoff contract      | About 3,400 token-equivalents              | 3              |

A single unnecessary escalation costs about as much as 150 dispatches of
handoff-contract overhead. This is why the escalation predicate, not the
prompt budget, is the tightly specified part of this proposal, and why only
two of seven failure classes may raise a tier.

### The real risk is dilution

The measurable risk of Axis 2 is not spend but compliance. The same charter
dispatch recorded `verify_base: null` for ST-0078: the instruction was present
in the prompt and the subagent did not follow it. Adding text to a prompt that
is already being partially ignored can make adherence worse, which is why the
contract is specified as substitutive and capped by a mechanical budget rather
than left to grow.

### Making it measurable

`usage-capture` already attributes tokens per session with an `agent` field,
so the claim above is testable rather than arguable. The first wave dispatched
after this feature lands runs as an A/B: half its stories with the generated
contract, half with the current template, comparing `normalized_total` per
**merged** story and the count of stories needing rework. The result is
recorded and the budget adjusted from it.

## Scope

**In the first release:**

- The tier rubric table, recorded in `dispatch-contract.md`, cited from
  `planning-agent.md`, and computed as a suggestion by `dispatch plan`.
- The story-level `risk_domains` field: added to
  [story.md](../../../factory/rulebooks/templates/story.md), authored by the
  planner via [create-backlog](../../../factory/skills/create-backlog/SKILL.md),
  and validated by `backlog-lint` against the six-value enum.
- Asymmetric mismatch disposition: a `strong` suggestion against a lower
  declared tier blocks `dispatch init`; every other mismatch warns. Both are
  resolved with the user and recorded in the ledger.
- Script-generated seven-part subagent handoff contract from
  `dispatch prepare-wave` and `dispatch prepare-story`, with the three
  removals that keep it substitutive.
- A measured prompt-token budget enforced by the script.
- The closed failure-class vocabulary on `dispatch mark-failed`.
- `dispatch escalate` with the six-condition predicate: one escalation per
  story, and one escalation per wave.
- The ledger `attempts` list, with per-entry `session` attribution.
- The `strategy: direct | seams-first` story field, its `backlog-lint`
  validation, and the two-session dispatch it implies.
- The A/B measurement on the first wave after landing.

**Explicitly deferred (do NOT plan stories for these):**

- Automatic selection of `strategy` by the planner or the script.
- Any tier rubric that reads story prose rather than frontmatter.
- Inheriting `risk_domains` from a proposal's `governance.risk_domains`. The
  vocabularies match, but risk is scoped to the story, not to the feature.
- Escalation beyond one tier, or a second escalation for the same story.
- A per-wave escalation budget expressed in tokens.
- Cost-aware behaviour for any dispatcher other than the implementation agent
  — the research orchestrator keeps its current assignment contract.
- Delegating gate execution or CI monitoring to cheap agents. Determinism
  beats a cheap agent, and
  [mechanize-dispatch-orchestration.md](mechanize-dispatch-orchestration.md)
  already moves that work into a script.
- Changing `config/model.conf` tier definitions or the set of tiers.

## Design Details

**Ledger compatibility.** The `attempts` list is additive. A ledger written
before this feature has no `attempts` key; `dispatch escalate` treats its
absence as zero recorded attempts and therefore refuses to escalate, which is
the safe default.

**Attempt accounting.** An attempt entry is written for every dispatched
session, including successful ones, so `normalized_total` accumulates for the
A/B measurement. The escalation predicate reads only entries with
`status: failed` and `session: impl`; every other entry is history.

**Risk vocabulary.** Story `risk_domains` reuses the six values of
`governance.risk_domains` from
[proposal.md](../../../factory/rulebooks/templates/proposal.md) so the two read
as one vocabulary. Sharing the terms is deliberate; sharing the values between
a proposal and its stories is not, and nothing derives one from the other.

**Budget provenance.** The 800-token figure is derived from the assembled
seven-part contract, whose parts total roughly 420 tokens before framing, and
from the cost analysis showing 800 tokens to be about 0.7% of a developer
session. It is a recorded assumption, not a measurement. The A/B result
revises it; the revision path is defined, so the figure ships as a hard gate
rather than a warning.

**Tier arithmetic.** Tier + 1 and tier − 1 are defined over the ordered triple
`economy < standard < strong` from
[config/model.conf](../../../config/model.conf). `strong + 1` and `economy − 1`
are not errors; they saturate, and saturation at `strong` is condition 4 of
the escalation predicate.

**Evidence paths.** `--evidence` takes a path to a tracked artifact — a
finding file, a test output committed to the branch, or the story file section
recording the unmet criterion. A free-text reason is not evidence and does not
satisfy condition 5.

**Budget measurement point.** The budget covers the generated prompt only, not
the agent definition or the skills the subagent loads. Those are already
counted in `.claude/INDEX.yaml` as `total_tokens` per agent and are unchanged
by this feature.

## Open Questions

None. The clarification interview of 2026-08-19 resolved every question this
proposal opened. Two resolutions are worth naming, because each overturned the
draft: `risk_domains` is authored per story and never inherited from a
proposal, and the `mark-failed` signature amendment leaves
[mechanize-dispatch-orchestration.md](mechanize-dispatch-orchestration.md)
`accepted`. The remaining resolutions are recorded in Design, Design Details,
and Completion Criteria.

## Completion Criteria

- `dispatch plan` reports a suggested tier per story from the rubric table,
  and flags every mismatch against the declared `tier`.
- `dispatch init` exits non-zero when the rubric suggests `strong` and the
  story declares a lower tier, and exits zero with a warning for every other
  mismatch. A test covers both directions.
- `backlog-lint` accepts the six enumerated `risk_domains` values, rejects any
  other, and accepts a story with the field absent.
- A story declaring `risk_domains: [security]` draws a `strong` suggestion
  from the rubric whatever its `outputs` are, and a story declaring
  `risk_domains: [reliability]` does not.
- The rubric table is recorded in `dispatch-contract.md` and cited from
  `planning-agent.md`; both cite the same table, with no second copy.
- `dispatch prepare-wave` and `dispatch prepare-story` emit the seven-part
  contract, and the `verify-base` preamble, the sub-agent addressing clause,
  and the workflow restatement no longer appear in a developer-agent dispatch
  prompt.
- The generated prompt measures no more than **800 normalized tokens** under
  the [ADR-0007](../../adr/0007-normalize-runtime-usage-through-cli-adapters.md)
  tokenizer; the script exits non-zero above that figure.
- `dispatch mark-failed` rejects any `--class` outside the seven-value
  vocabulary and any invocation without `--evidence`.
- `dispatch escalate` exits non-zero when any of its six conditions fails,
  and a test exists for each condition failing in isolation.
- No story reaches a second escalation, and no wave reaches a second
  escalation: the script refuses both, and a test proves each refusal.
- A `seam_defect` attempt does not consume the story's escalation: a test
  dispatches a seam failure followed by an `acceptance_unmet` failure and
  proves the escalation is still granted.
- The ledger records an `attempts` entry per dispatch attempt, carrying
  `session`, `tier`, `failure_class`, `evidence`, `commit_sha`, and
  `normalized_total`.
- `backlog-lint` validates `strategy` against its enum and rejects
  `seams-first` when the story's `tests` paths fall outside its `outputs`.
- A `seams-first` story runs two sessions, the seam session writes only test
  files, and the implementation session runs at one tier below the declared
  tier.
- The first wave dispatched after landing records an A/B result comparing
  `normalized_total` per merged story and rework count, with and without the
  generated contract.

## Guiding Rule

Spend reasoning where the decision is genuinely hard, and spend nothing
anywhere else; when a subagent fails, first ask what it was not told, and only
then ask whether it could not think.
