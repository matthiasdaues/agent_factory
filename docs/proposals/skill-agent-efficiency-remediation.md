---
scope: global
schema_version: 2
status: implemented
owner: Matthias Daues
created: 2026-09-12
updated: 2026-09-13
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - packages/factory/agents/
    - packages/factory/skills/
    - packages/factory/rulebooks/templates/story.md
    - packages/factory/rulebooks/conventions/

governance:
  assurance: elevated
  risk_domains:
    - compatibility
    - reliability

estimate:
  as_of: 2026-09-12
  basis: decomposition
  confidence: medium
  human_review_hours:
    min: 2.0
    max: 4.0
  normalized_tokens:
    min: 8000
    max: 15000
  estimated_consumption:
    min: 80000
    max: 150000
    overhead_multiplier: 10
    playbook: feature-addition
---

# Feature Request: Skill & Agent Efficiency Remediation

## Summary

Remove inefficiencies and detractors from the 84-item skill and agent
collection, recovering approximately 7,000 tokens (18% of the total load)
while preserving the genuine domain methodology that makes the collection
valuable. The work is organized as six streams executed in a defined order:
structural optimization first (convention extraction, reference extraction,
consolidation), instruction trimming last.

The proposal answers one question: which parts of the collection help a
frontier model produce better work than it would unassisted, and which parts
consume context without improving — or actively degrading — output quality?

## Motivation

An [audit](../reviews/skill-agent-audit-2026-09-12.md) of the full collection
(18 agents, 66 skills, 4 supplementary files, 1 story template) found that
roughly a fifth of the total token budget is spent on three categories of
waste:

1. **Native-knowledge re-teaching.** Skills that re-explain methods the model
   already knows from training — TDD mechanics, Cockburn use cases, Vue best
   practices, OWASP checklists. These instructions do not improve output; they
   consume context the model could use for the actual task and, in some cases,
   cap the model's judgment by scripting steps it would handle more flexibly on
   its own.

2. **Duplication.** Identical instruction blocks copy-pasted across sibling
   skills and agents — quality gate tables, boilerplate lifecycle blocks,
   prerequisite guards. These create drift risk: when the canonical definition
   changes, copies become contradictory.

3. **Dead weight.** Superseded skills, one-time migration utilities kept after
   use, and deprecation stubs that do nothing.

The collection also contains 35 well-designed items that demonstrate a clear
pattern: declarative goals, genuine domain methodology, project-specific
contracts the model cannot derive, and lean token budgets. The remediation
preserves and extends this pattern.

## Core Principles

- **Trim, do not gut.** The collection's value is in its domain methodology.
  Remove only what duplicates the model's native capabilities or what is
  demonstrably dead. Every trim must preserve the project-specific contracts
  and conventions that the model would not produce unprompted.

- **Declarative over prescriptive.** Replace step-by-step scripts with goal
  statements and constraints wherever the model can derive the steps. Prescribe
  only what the model would not do on its own — forbidden phrasings, routing
  tables, file-path conventions, output format contracts.

- **Single source of truth.** Shared definitions (quality gates, composition
  rules, boilerplate protocols) live in one canonical location. Phase skills
  and agents reference them by path, never by copy.

- **Reference on demand.** Heavy reference material (templates, checklists,
  code examples, field documentation) lives in separate files loaded when
  needed, not embedded in runtime skill bodies that are loaded on every
  invocation.

- **Structural optimization first, instruction trimming last.** Extract
  shared conventions, deduplicate reference material, and consolidate
  overlapping items before trimming any instruction text. This ensures
  that trims are applied to already-cleaned skills, making them smaller,
  better scoped, and independently revertible.

- **Verify by contract checks and revert commitment.** Each changed item
  must still meet its own stated output contract (file format, required
  sections, routing decisions, forbidden patterns). Pipeline smoke tests
  confirm no regression in end-to-end workflows. Semantic quality —
  whether prose is as clear, actionable, and concrete as before — cannot
  be automated; it is monitored through normal use. If a trimmed item
  produces noticeably worse output in practice, the trim is reverted.
  All changes are version-controlled; reverting is one `git checkout`.

## Design

The work is organized into six streams. Each stream has a clear scope, a
list of affected items, and an expected token recovery.

**Execution order (decided 2026-09-13):** Structural optimization precedes
instruction trimming. All convention extraction, reference extraction,
consolidation, and codification must complete before any native-knowledge
trimming begins. This ensures trims are applied to already-cleaned items
and are independently revertible.

| Phase | Stream | Work                              | Status |
| ----- | ------ | --------------------------------- | ------ |
| 1     | 1      | Remove dead items                 | done   |
| 2     | 2      | Extract shared conventions        |        |
| 2     | 5      | Extract reference material        |        |
| 2     | 4      | Consolidate overlapping items     |        |
| 3     | 6      | Codify skill authoring principles |        |
| 4     | 3      | Trim native-knowledge overlap     |        |

Phase 2 streams have no dependencies on each other and may execute in
parallel. Stream 3 (phase 4) requires phases 2 and 3 to be complete.

### Stream 1: Remove Dead Items ✓ DONE

Removed skills that were superseded, deprecated, or single-use-completed.

| Item                  | Tokens | Reason                                    |
| --------------------- | ------ | ----------------------------------------- |
| `derive-spec`         | ~432   | Explicitly superseded by `derive-feature` |
| `update-context`      | ~96    | Deprecation stub; does nothing            |
| `scope-map-migration` | ~376   | One-time migration; already performed     |

**Recovered:** ~904 tokens.

### Stream 2: Extract Shared Conventions

Move duplicated instruction blocks into canonical convention files. Replace
inline copies with single-line references.

#### 2a. Agent lifecycle boilerplate (~1,200 tokens)

The "Phase entry / Child return / Phase exit" block appears verbatim in 10
of 18 agents. Extract to
`packages/factory/rulebooks/conventions/agent-lifecycle-protocol.md`.
Replace the inline block in each agent with:

> Follow the agent lifecycle protocol.

Replace the "agent lifecycle protocol" text with a working link when the referenced file exists.

**Affected agents:** `architecture-agent`, `architecture-review-agent`,
`code-review-agent`, `developer-agent`, `implementation-agent`,
`proposal-review-agent`, `qa-agent`, `reconciliation-agent`,
`requirements-agent`, `spec-review-agent`.

#### 2b. Writing quality gates → standalone convention

**Decision (2026-09-13):** The "Junior Clarity / Senior Acceptance" framing
has proven, high-impact influence on output quality — text becomes more
understandable, actionable, and concrete. It is **not** retired and **not**
buried inside a parent skill. Instead, it becomes a first-class, standalone
convention that applies universally to all written output.

Extract to `packages/factory/rulebooks/conventions/writing-quality-gates.md`
containing:

- **Junior Clarity / Senior Acceptance** gate — the primary quality lever.
- **International Readability** gate (currently in `create-backlog`).
- **Agent-Answerability** gate (currently in `create-backlog`).

This file is independently versioned and evolvable. Every skill and agent
that produces written output references it with a single line:

> Apply the writing quality gates.

Replace "writing quality gates" with a working link once the referenced file exists.

**Inclusion rule:** any agent or skill whose primary output includes
persistent prose artifacts (markdown documents, reports, findings, specs,
stories, proposals, ADRs, handoffs). Items producing only code, config,
JSON gate reports, or ephemeral conversational output are excluded.

**Affected agents (16):** `architecture-agent`, `architecture-review-agent`,
`claim-reviewer`, `coaching-agent`, `code-review-agent`,
`implementation-agent`, `planning-agent`, `proposal-review-agent`,
`qa-agent`, `reconciliation-agent`, `requirements-agent`,
`research-orchestrator`, `research-report-writer`, `research-synthesizer`,
`researcher`, `spec-review-agent`.

**Affected skills (37):** `adversarial-review`, `atam-review`, `bug-hunt`,
`capture-context`, `capture-vision`, `claim-formulation`,
`clarify-requirements`, `create-backlog`, `create-backlog-epics`,
`create-backlog-make-concrete`, `create-backlog-slice-story`,
`create-backlog-stories`, `create-backlog-story-slices`,
`create-backlog-write-epics`, `derive-feature`, `domain-modeling`,
`draft-proposal`, `fagan-review`, `handoff`, `inspect-spec`,
`maintain-architecture`, `model-structurizr-slice`, `process-transcript`,
`pugh-matrix`, `qa-strategy-from-spec`, `reconcile-spec`,
`research-planning`, `research-reporting`, `research-synthesis`,
`retrospective`, `reverse-map`, `scaffold-arc42`, `source-research`,
`spec-feedback`, `testability-probe`, `write-adr`, `write-prd`.

**Excluded (not prose-producing):** `developer-agent`, `virgil`,
`caveman`, `comic-relief`, `commit`, `crap-score`, `dependency-check`,
`detect-test-regime`, `explain-concept`, `grilling`, `grill-me`,
`grill-with-docs`, `guided-tour`, `newcomer-tour`, `implement-issue`,
`init-factory`, `mutation-testing`, `refutation-design`, `run-step`,
`scratchpad`, `security-review`, `test-design`, `validate`,
`vue-best-practices`.

Inline copies of any of these gates in individual items are removed and
replaced with the single reference. Future items meeting the inclusion
rule must add the reference at authoring time (enforced by the
skill-authoring principles in Stream 6).

#### 2c. Prerequisite guards (~100 tokens)

`testability-probe` and `test-design` share a verbatim prerequisite guard
for `testing.yaml`. Extract to a one-liner convention or a shared guard
snippet:

> Requires `docs/testing.yaml` with `testing_strategy` and `suites` sections.

**Recovery:** ~1,984 tokens across 2a–2c (includes ~434 tokens previously
double-counted in Stream 3 for `code-review-agent` gate extraction and
`create-backlog-stories` gate table dedup).

### Stream 3: Trim Native-Knowledge Overlap

Replace methodology pedagogy with method-name references and keep only
project-specific conventions. For each item, the "keep" column names the
genuinely additive content; everything else is trimmed.

**Principle references for sub-frontier models (decided 2026-09-13):**
Where a trim replaces pedagogy with a method-name reference (e.g. "apply
Cockburn reasoning"), extract the removed explanation into a lean principle
file under `packages/factory/rulebooks/principles/` (~50–100 tokens each).
The trimmed skill includes a flipped-default conditional:

> Apply Cockburn reasoning to derive actor-goal pairs. Read
> `rulebooks/principles/cockburn-reasoning.md` before proceeding. Skip
> only if you can state the core principle without reading.

Frontier models skip the file (they already know the principle). Weaker
models default to reading — the safe direction. No model-matrix lookup,
no router changes, no duplicate skill variants. Fails safe: the only
failure mode is a weak model reading a file it could have skipped.

Candidate principle files:

| File                        | Extracted from       |
| --------------------------- | -------------------- |
| `cockburn-reasoning.md`     | `derive-feature`     |
| `tdd-red-green-refactor.md` | `developer-agent`    |
| `vue3-composition-api.md`   | `vue-best-practices` |
| `owasp-top-10.md`           | `security-review`    |

| Item                         | Current | Target | Keep                                                                                                                                                      | Trim                                                                                                                                                                                                                                                                                                                  |
| ---------------------------- | ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `implementation-agent`       | ~3,254  | ~2,400 | Full dispatch protocol: mode resolution (without hardcoded default), workflow steps, prompt templates, gate-check loop, escalation — all project-specific | Lifecycle boilerplate (→ Stream 2a convention), branching prose (restates linked policy docs), hardcoded `autonomous` default (mode default belongs in project config, not agent). Remaining kept content edited for conciseness: tighter prose, remove explanatory asides, compress to command + constraint per step |
| `developer-agent`            | ~1,964  | ~600   | Story-file contract, skill routing                                                                                                                        | TDD conditional branching, Red-Green-Refactor sub-conditions, `.feature` re-explanation                                                                                                                                                                                                                               |
| `derive-feature`             | ~1,104  | ~600   | Output format, lifecycle rules, @-references, scope-map integration                                                                                       | Cockburn reasoning pedagogy (Steps 3–5) — replace with "apply Cockburn reasoning to derive actor-goal pairs"                                                                                                                                                                                                          |
| `vue-best-practices`         | ~560    | ~60    | Project-specific deviations only                                                                                                                          | Generic Vue 3 Composition API knowledge                                                                                                                                                                                                                                                                               |
| `comic-relief`               | ~324    | ~60    | Tone constraint, target rule (process not person)                                                                                                         | Humor quadrangle, timing rules, example categories                                                                                                                                                                                                                                                                    |
| `explain-concept`            | ~320    | ~80    | Search-path routing (guide → INDEX → rulebooks)                                                                                                           | Lucien persona, self-check step, audience rubric                                                                                                                                                                                                                                                                      |
| `security-review`            | ~172    | ~40    | "Minimize false positives" constraint                                                                                                                     | OWASP-10 checklist (model does this natively and more thoroughly)                                                                                                                                                                                                                                                     |
| **Recovery:** ~2,800 tokens. |         |        |                                                                                                                                                           |                                                                                                                                                                                                                                                                                                                       |

**Moved to other streams (no longer counted here):**

- `code-review-agent` (834→500): entire recovery is writing-quality gate
  extraction → Stream 2b.
- `create-backlog-stories` (496→350): gate table dedup → Stream 2b (~100
  tokens); backward-compatibility heuristic removal → deferred. No
  native-knowledge content to trim in Stream 3.

### Stream 4: Consolidate Overlapping Items

#### 4a. Grilling triplicate (3 → 1)

`grilling` already handles proposal and story targets. `grill-me` is a pure
redirect. `grill-with-docs` adds domain-modeling context.

**Action:** Add `grill-with-docs` mode as a parameter or trigger in
`grilling` (load `domain-modeling` context when the target has domain
concerns). Delete `grill-me/SKILL.md` and `grill-with-docs/SKILL.md`.
Update INDEX.yaml aliases.

#### 4b. Research output agents (2 → 1)

`research-report-writer` and `research-synthesizer` have nearly identical
structure. Merge into one agent with a mode parameter (survey report vs.
synthesis).

#### 4c. Code review boundary clarification

`code-review-agent` and `qa-agent` both trigger on "code review" and both
invoke `fagan-review`. Sharpen boundary:

- `code-review-agent`: pre-merge diff review only.
- `qa-agent`: post-merge full-codebase review, security, bug hunt.

Remove "code review" from `qa-agent` triggers.

**Decision (2026-09-13):** Retiring `code-review-agent` in favor of Claude
Code's built-in `/code-review` is **architecturally invalid**. The factory
is a multi-CLI system (Claude Code, Copilot, Pi, Codex). The built-in
`/code-review` is Claude Code only — retiring the custom agent would break
every other CLI. The comparison test is therefore not applicable.

**Recovery:** reduced confusion cost from clearer trigger boundaries
(unquantifiable but real).

### Stream 5: Extract Reference Material

Move heavy reference content from runtime skill bodies into separate files
loaded on demand. The skill retains its routing logic and procedure; the
reference file holds templates, checklists, code examples, and field
documentation.

| Item                      | Extract what                                                                                                         | From                           | To                                                                                     |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------ | -------------------------------------------------------------------------------------- |
| Story template v2.1.0     | Field documentation (~400 tokens): `risk_level`, `touches`, `concerns`, `quality-gates`, `tests`, `test-design-pass` | `rulebooks/templates/story.md` | `rulebooks/references/story-frontmatter-fields.md`                                     |
| Story template v2.1.0     | `touches` hygiene rule                                                                                               | Template body                  | Parent `create-backlog` skill or `conventions/touches-hygiene.md`                      |
| `qa-strategy-from-spec`   | Embedded markdown template (~480 tokens) and 15-item quality checklist                                               | Skill body                     | `rulebooks/templates/qa-strategy.md` + `rulebooks/references/qa-strategy-checklist.md` |
| `mutation-testing`        | Setup/tutorial content (~300 tokens)                                                                                 | Skill body                     | `rulebooks/references/mutation-testing-methodology.md`                                 |
| `model-structurizr-slice` | Inline DSL code examples (~200 tokens) and 11-point behavior checklist                                               | Skill body                     | `rulebooks/references/structurizr-behavior-checklist.md`                               |

**Recovery:** ~1,380 tokens from runtime skill bodies. The reference files
still exist and are still loadable — the saving is that they are not loaded on
every invocation.

### Stream 6: Codify Skill Authoring Principles

Write `packages/factory/rulebooks/conventions/skill-authoring.md` — a short
document codifying the design principles that emerged from the audit. This
prevents future skills from re-introducing the patterns this remediation
removes.

The document covers four principles:

1. **Declarative over prescriptive.** State the goal and constraints; let the
   model determine the steps. Prescribe only what the model would not do
   unprompted — forbidden phrasings, routing tables, file-path conventions,
   output contracts.

2. **Delegate to schemas and reference files.** Define output contracts by
   reference, not inline. Heavy templates and checklists are separate files
   loaded on demand.

3. **Prescribe only the non-obvious.** A constraint the model already follows
   (self-check completeness, audience calibration, active voice) wastes
   tokens. A constraint the model would violate without instruction (forbidden
   phrasing, file-path routing, decision-record preservation) earns its
   tokens.

4. **Tool wrappers, not reasoning replacements.** A skill paired with a
   deterministic script documents how to call the tool — it does not replace or
   guide the model's reasoning about the results.

Each principle includes a positive exemplar (a skill from the collection that
does it well) and a negative exemplar (a skill that does not, with the specific
lines that fail the principle).

## Scope

**In the first release:**

- Streams 1, 2, 4, 5 executed and verified by contract checks and pipeline
  smoke tests.
- Stream 6 skill-authoring document written and referenced from factory guide.
- Stream 3 (instruction trimming) executed last, after all structural
  optimization is complete. Verified by contract checks; semantic quality
  monitored in normal use with revert commitment.
- All INDEX.yaml references updated.
- All agent `skills:` lists updated.
- No behavioral changes to the backlog pipeline, research pipeline, or
  architecture workflow — only the instruction text that drives them.

**Explicitly deferred (do NOT plan stories for these):**

- Rewriting `implementation-agent` dispatch protocol as executable scripts.
  Stream 3 trims the agent definition; moving the protocol to scripts is a
  separate architectural change.
- Removing the backward-compatibility heuristic from `create-backlog-stories`.
  Requires confirming all EPICs have been migrated from the old format.
- Automated token-budget tracking for skills (e.g., a lint rule that flags
  skills exceeding a threshold). Worth considering but not part of this
  remediation.

## Open Questions

- ~~Should "Junior Clarity / Senior Acceptance" framing move into the parent
  `create-backlog` quality gates, or be retired entirely?~~ **Resolved
  (2026-09-13):** Promoted to standalone convention file
  (`conventions/writing-quality-gates.md`) with universal scope across all
  written output. See Stream 2b.
- ~~Is the `code-review-agent` vs. built-in `/code-review` comparison test
  worth doing now, or should it wait?~~ **Resolved (2026-09-13):** Not
  applicable. The factory is multi-CLI; retiring the custom agent in favor
  of a Claude Code-only built-in would break Copilot, Pi, and Codex. See
  Stream 4c.
- Should the `touches` hygiene rule live in the parent `create-backlog` skill
  or in a standalone conventions document? It applies to story authoring
  broadly, not just backlog creation.

### Model-capability dependence

**Decision (2026-09-13):** Flipped-default principle references.

The guiding rule — "a skill earns its tokens when it makes the model do
something it would not do unprompted" — is a function of the consumer model,
not a constant. The proposal's trims are calibrated for frontier models
(Opus, Sonnet). On Haiku or locally run models (Llama, Mistral, Qwen under
~30B), several assumptions weaken:

- **Stream 3 trims are capability-dependent.** "Apply Cockburn reasoning" is
  a sufficient instruction for a frontier model that knows Cockburn from
  training. A 13B local model may not know Cockburn at all.

- **Cross-file references require self-directed loading.** Streams 2 and 5
  replace inline instructions with file references. Smaller models may
  skip the reference and produce output from (incomplete) memory.

- **Mode-switching in merged agents.** Stream 4b merges two research output
  agents into one with a mode parameter. Smaller models may conflate modes.

**Mitigation:** Stream 3 extracts removed pedagogy into lean principle
files under `rulebooks/principles/` (~50–100 tokens each). Each trimmed
skill includes a flipped-default conditional reference: "Read X before
proceeding. Skip only if you can state the core principle without reading."
Frontier models skip; weaker models default to reading. No model-matrix
infrastructure, no duplicate variants, no router logic. See Stream 3
for the candidate principle files.

The cross-file reference risk (Streams 2 and 5) is accepted. File
references are standard agent behavior for the factory's supported CLIs;
models that cannot follow a file reference are below the factory's minimum
capability floor.

## Completion Criteria

- [x] Three dead skills removed; no dangling references in INDEX.yaml or agent files
- [ ] Agent lifecycle boilerplate extracted; 10 agents reference the convention file
- [ ] Writing quality gates extracted to standalone convention file; all prose-producing skills and agents reference it; no inline copies remain
- [ ] Seven items trimmed per Stream 3 table; each meets its stated output contract (file format, required sections, routing, forbidden patterns); semantic quality monitored in use with revert commitment
- [ ] Grilling consolidated to one skill; `grill-me` and `grill-with-docs` deleted
- [ ] Research output agents merged or share a base definition
- [ ] Code review boundary clarified; `qa-agent` no longer triggers on "code review"; `code-review-agent` retained as multi-CLI asset
- [ ] Five reference extractions completed; runtime skill bodies reduced
- [ ] Skill-authoring principles document written and referenced from factory guide
- [ ] Total token load reduced by ≥7,000 tokens from pre-remediation baseline
- [ ] Pipeline smoke tests pass: backlog creation, research, and architecture workflows produce structurally valid output after each phase completes
- [ ] No Stream 3 trim reverted due to observed semantic quality degradation within 30 days of completion

## Guiding Rule

A skill earns its tokens when it makes the model do something it would not do
unprompted. Everything else is overhead.

## Review — 2026-09-13

Reviewer: proposal-review-agent
Reviewed commit: fa5dd94bf49bb12fa238d48144f2e11d2bff5b09
Disposition: findings

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------- | -------- | ----- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-01 | blocking | 01    | open   | **Ablation testing undefined.** The proposal's primary verification method — "ablation testing" — appears in five locations (Core Principles, Summary, Stream 3, Completion Criteria) but is never operationally defined. No metric for "output quality," no method for selecting "representative tasks," no pass/fail threshold, no evaluator role. The completion criterion "output quality matches or exceeds pre-trim baseline on 3 representative tasks" cannot be tested without these definitions.                                                                                                    |
| PROP-02 | blocking | 02    | open   | **Stream 1 marked DONE but incomplete.** INDEX.yaml still contains entries for `derive-spec`, `scope-map-migration`, and `update-context` pointing to deleted skill paths. The completion criterion for Stream 1 explicitly requires "no dangling references in INDEX.yaml or agent files." Additionally, `reconciliation-agent.md` references `scope-map-migration` (line about skip-migration-rows for old-format entries). Stream 1 cannot be marked done until these references are cleaned.                                                                                                             |
| PROP-03 | major    | 02    | open   | **Stream 3 vs. deferred scope contradiction for implementation-agent.** Stream 3 trims `implementation-agent` from 3,254 to ~800 tokens. The "Trim" column says "wave planning, branching prose, prompt templates, gate-check loop — move to dispatch scripts." But the Scope section explicitly defers "Rewriting `implementation-agent` dispatch protocol as executable scripts." If the script destination is deferred, the trimmed content has no place to land. The proposal must specify: is the content deleted outright, or is the trim blocked on the script work? Either answer changes planning.  |
| PROP-04 | major    | 02    | open   | **Stream 4c contradicts scope deferral.** The Stream 4c design says "Run 5 representative diffs... If quality matches, retire the custom agent and redirect to the built-in." But the Scope says retiring `code-review-agent` is explicitly deferred, requiring "the 5-diff comparison test first." Open Question 2 then asks whether this comparison test should even happen now. Three locations give three different answers about the same work. A planner cannot determine what stories to write.                                                                                                       |
| PROP-05 | major    | 06    | open   | **Model-capability strategy is unresolved and shapes three streams.** The Model-capability dependence section identifies a critical decision ("which strategy to adopt before stories are written") with three options. The decision directly affects Stream 3 story scope (trim-only vs. trim-plus-variant), Stream 2 and 5 implementation (inline-to-reference vs. inline-to-reference-with-fallback), and the ablation protocol (single-tier vs. cross-tier). This is not an open question that can be resolved during planning — it must be resolved before the proposal can be decomposed into stories. |
| PROP-06 | major    | 01    | open   | **"All prose-producing" items unbounded in Stream 2b.** The affected-items list uses "including but not limited to." Without a definitive, closed list of items that must reference the writing-quality-gates convention file, a planner cannot write complete stories and the completion criterion ("all prose-producing skills and agents reference it; no inline copies remain") cannot be mechanically verified. Enumerate the full list or define a mechanical rule for inclusion.                                                                                                                      |
| PROP-07 | major    | 03    | open   | **Token recovery double-counting between Stream 2b and Stream 3.** The Stream 3 table includes `code-review-agent` (834 → 500, recovery 334 tokens) with the trim action described as "replace with single reference to `conventions/writing-quality-gates.md` (Stream 2b)." This is a Stream 2b action listed in Stream 3's table. Similarly, `create-backlog-stories` attributes ~100 tokens to "reference parent" which overlaps Stream 2b gate extraction. The ~4,834 claimed Stream 3 recovery includes tokens that belong to Stream 2. The aggregate ~8,500 total may overcount.                       |
| PROP-08 | minor    | 08    | open   | **Overhead multiplier below template guidance.** The estimate uses 10x, but the proposal template's own documented range for feature-addition with review loops is 15-25x. This remediation adds ablation testing (running representative tasks multiple times across 9+ items), which further inflates overhead. Even if ablation testing is light, 10x is optimistic for a cross-component change touching 30+ files.                                                                                                                                                                                      |
| PROP-09 | minor    | 02    | open   | **Tier 4 audit items neither included nor deferred.** The audit identifies recoverable tokens in `implement-issue` (320 → 180), `research-reporting` (464 → 300), `process-transcript` (728 → 500), `run-step` (260 → 200), and `reverse-map` (480 → 350) — totaling ~658 potential tokens. These items appear in neither the "In" scope list nor the "Explicitly deferred" list. The scope boundary is not a clean partition of the audit's findings.                                                                                                                                                       |
| PROP-10 | minor    | 03    | open   | **Research agent merge may not reduce tokens.** `research-report-writer` and `research-synthesizer` serve fundamentally different research modes (falsification vs. survey) with different inputs, schemas, forbidden actions, and completion criteria. A merged definition with mode-switching logic may be *larger* than the two current definitions combined. The proposal claims only ~90 tokens total from Stream 4, none from this specific merge. The value is unclear and the merge risks capability regression.                                                                                     |
| PROP-11 | minor    | 02    | open   | **qa-strategy-from-spec partially addressed.** The audit identifies this as the largest skill (1,624 tokens) and recommends trimming to ~800 tokens by removing the quality checklist that "restates constraints already embedded in its own template." The proposal addresses only the reference extraction in Stream 5 (~480 tokens) but omits the native-knowledge overlap identified in the audit. ~344 tokens of potential recovery are dropped without explanation.                                                                                                                                    |
| PROP-12 | minor    | 06    | open   | **Open Question 2 contradicts Stream 4c design.** The open question asks "Is the code-review-agent vs. built-in `/code-review` comparison test worth doing now, or should it wait?" But Stream 4c's design includes this comparison as active work. Either the question should be resolved (and 4c updated) or 4c should note the question's dependency. Currently the proposal gives contradictory signals. (See also PROP-04.)                                                                                                                                                                             |
| PROP-13 | note     | 08    | open   | **Token estimation methodology adds uncertainty.** The audit acknowledges "line-count approximations (lines × ~4)." Spot-checking against byte counts: `derive-feature` is 10,241 bytes (~2,560 tokens at 4 chars/token) but estimated at 1,104 tokens; `create-backlog-stories` is 11,537 bytes (~2,884 tokens) but estimated at 496 tokens. Systematic undercount by 2-6x suggests the ~38,500 total load and per-item estimates carry wide error bars. The ≥7,000 target may be easier or harder to hit than it appears.                                                                                  |
| PROP-14 | note     | 01    | open   | **Completion criterion uses "or" for research agents.** "Research output agents merged or share a base definition" accepts either outcome. This is technically testable but weakens the criterion into a non-commitment — the planner does not know which to implement, and either alternative could be declared "done."                                                                                                                                                                                                                                                                                     |
| PROP-15 | note     | 01    | open   | **"No regression" criterion not operationally testable.** The criterion "No regression in factory pipeline behavior (backlog creation, research, architecture workflows produce equivalent output)" has the same undefined-quality problem as PROP-01. "Equivalent output" needs a definition — token-for-token identical? Structurally equivalent? Same acceptance-criteria pass rate? Without this, the criterion is aspirational.                                                                                                                                                                         |

### Summary

The proposal identifies a genuine and well-motivated problem — roughly a fifth of the skill and agent collection's context budget consumed by waste. The six-stream design is sound in concept and most items are well-scoped. However, three categories of issues prevent this proposal from being planned in its current form.

First, the primary verification method ("ablation testing") is invoked throughout but never defined. Without a measurable pass/fail criterion, the eight completion criteria that depend on it are aspirational rather than testable. Second, three scope contradictions — Stream 3's implementation-agent trim versus the deferred script rewrite, Stream 4c's retirement clause versus the deferred list, and the unresolved model-capability strategy — create ambiguities that a planner cannot resolve. Third, Stream 2b's unbounded "all prose-producing" scope and the double-counting between Streams 2b and 3 mean the token recovery numbers are soft.

Recommended path: resolve the five major findings (PROP-03 through PROP-07), define ablation testing operationally (PROP-01), and fix the Stream 1 completion claim (PROP-02) before returning for a repeat review.

## Repeat Review — 2026-09-13

Reviewer: proposal-review-agent
Reviewed commit: 034b845e326da3c0075134d0b84ad9f92b95712b
Disposition: findings

### Prior Finding Resolutions

| ID      | Prior Severity | Status             | Resolution                                                                                                                                                                                                                                                           |
| ------- | -------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | blocking       | resolved           | "Ablation testing" replaced with contract checks and revert commitment. Verification is now operationally defined: each item must meet its stated output contract; semantic quality is monitored in normal use with a revert commitment; 30-day window is concrete.  |
| PROP-02 | blocking       | resolved           | No dangling INDEX.yaml or agent-file references to `derive-spec`, `scope-map-migration`, or `update-context` remain at the reviewed commit. `reconciliation-agent` reference also cleaned.                                                                           |
| PROP-03 | major          | resolved           | Target revised from ~800 to ~2,400. Dispatch protocol recognized as project-specific. Kept content identified; lifecycle boilerplate attributed to Stream 2a. Hardcoded `autonomous` default removed. Deferred script rewrite cleanly excluded.                      |
| PROP-04 | major          | resolved           | Stream 4c reduced to boundary clarification only. Retirement declared architecturally invalid (multi-CLI factory). Open Question 2 resolved. All three previously contradictory locations now agree.                                                                 |
| PROP-05 | major          | resolved           | Flipped-default principle references with candidate principle files. No model-matrix infrastructure, no duplicate variants, no router logic. Fails safe.                                                                                                             |
| PROP-06 | major          | partially resolved | Closed list of 14 agents + 34 skills replaces "including but not limited to." Mechanical inclusion rule defined. However, the enumeration is incomplete — see PROP-18.                                                                                               |
| PROP-07 | major          | partially resolved | `code-review-agent` and `create-backlog-stories` moved from Stream 3 to Stream 2b. Double-counting eliminated. However, the Summary's ~8,500 total no longer matches the revised stream totals — see PROP-17.                                                        |
| PROP-08 | minor          | open (carried)     | Overhead multiplier still 10x. Template guidance for feature-addition with review loops is 15–25x. Verification method is now lighter (no ablation testing), but 10x remains below guidance for a cross-component change touching 30+ files.                         |
| PROP-09 | minor          | open (carried)     | Tier 4 audit items (`implement-issue`, `research-reporting`, `process-transcript`, `run-step`, `reverse-map`) still neither included in scope nor explicitly deferred. The scope boundary is not a clean partition of the audit's findings.                          |
| PROP-10 | minor          | open (carried)     | Research agent merge value unchanged. `research-report-writer` (2,852 bytes) and `research-synthesizer` (2,054 bytes) serve different research modes with different schemas and forbidden actions. A mode-switched merge may be larger than the two separate agents. |
| PROP-11 | minor          | open (carried)     | `qa-strategy-from-spec` native-knowledge overlap (identified in audit, ~344 tokens) still not addressed. Stream 5 handles reference extraction but omits the native-knowledge trim.                                                                                  |
| PROP-12 | minor          | resolved           | Open Question 2 resolved; Stream 4c reduced to boundary clarification. The contradiction between the open question and the stream design is eliminated as a side effect of the PROP-04 fix.                                                                          |
| PROP-13 | note           | open (carried)     | Token estimation methodology unchanged. Byte-count spot checks show systematic undercount: `implementation-agent` is 18,873 bytes (~4,718 tokens at 4 chars/token) vs. proposal's ~3,254; `derive-feature` is 10,241 bytes (~2,560 tokens) vs. ~1,104.               |
| PROP-14 | note           | open (carried)     | Completion criterion still uses "merged or share a base definition" — accepts either outcome without committing to one, leaving the planner to decide which to implement.                                                                                            |
| PROP-15 | note           | resolved           | Criterion now says "structurally valid output" instead of "equivalent output." Operationally testable via output format validation.                                                                                                                                  |

### New Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------- | -------- | ----- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-16 | minor    | 01    | open   | **Completion criterion count mismatch.** Line 465 says "Nine items trimmed per Stream 3 table" but the Stream 3 table now contains seven items after `code-review-agent` and `create-backlog-stories` were moved to Stream 2b. The criterion must say "Seven."                                                                                                                                                                                                                                                        |
| PROP-17 | minor    | 03    | open   | **Summary token total exceeds stream totals.** The Summary claims "approximately 8,500 tokens (22%)" but stream recovery figures add to ~7,068 (Stream 1: 904 + Stream 2: 1,984 + Stream 3: 2,800 + Stream 5: 1,380). Stream 4a deletions (grill-me ~118 tokens + grill-with-docs ~168 tokens) narrow the gap to ~1,146 but do not close it. The binding completion criterion (≥7,000) is reachable from the stream totals; the Summary overstates.                                                                   |
| PROP-18 | major    | 01    | open   | **Stream 2b closed list incomplete.** Five items are missing from both the included and excluded enumerations: agents — `requirements-agent`, `spec-review-agent`; skills — `clarify-requirements`, `create-backlog-make-concrete`, `create-backlog-slice-story`. All five produce persistent prose artifacts and meet the stated mechanical inclusion rule. The 14+34 count does not partition the full 18-agent, 59-skill inventory. A planner writing Stream 2b stories from this list would miss five work items. |

### Eight-Check Results

| Check | Name                             | Result   | Notes                                                                                                                                                                                                              |
| ----- | -------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 01    | Completion criteria testable     | findings | PROP-16: count says nine, table has seven. PROP-18: closed list is incomplete — the "all prose-producing" criterion cannot be verified against the proposal's own enumeration.                                     |
| 02    | Scope boundary sharp             | finding  | PROP-09 (carried): five Tier 4 audit items are neither in scope nor deferred. The scope section does not partition the audit's full findings.                                                                      |
| 03    | Design decomposable              | finding  | PROP-17: Summary's ~8,500 cannot be derived from the stream totals. The binding criterion (≥7,000) is consistent. Stream 3 per-item deltas span multiple streams but "Trim" column partitions the work adequately. |
| 04    | Impact classification consistent | pass     | `scope: cross_component` fits. `architecture_change: false` is defensible — Stream 4b merges agents but preserves their interfaces; the change is organizational, not architectural.                               |
| 05    | Boundary references exist        | pass     | All four paths resolve at the reviewed commit: `packages/factory/agents/`, `packages/factory/skills/`, `packages/factory/rulebooks/templates/story.md`, `packages/factory/rulebooks/conventions/`.                 |
| 06    | Open questions genuine           | pass     | One remaining open question ("touches hygiene rule" location) is a genuine design decision. Two resolved questions are clearly marked. Model-capability section resolved with decision.                            |
| 07    | Motivation justifies timing      | pass     | The audit provides concrete evidence: ~20% of context budget on waste across three named categories. Motivation distinguishes this from backlog.                                                                   |
| 08    | Estimate plausible               | finding  | PROP-08 (carried): 10x multiplier below 15–25x template guidance. PROP-13 (carried): per-item token estimates systematically undercount by 2–4x vs. byte-derived estimates.                                        |

### Summary

The edits since the first review resolved both blocking findings and five of seven major findings. The verification method is now operationally defined, the three scope contradictions are eliminated, and the model-capability strategy is decided. The proposal is substantially improved.

Three categories of remaining issues prevent a clean disposition. First, the Stream 2b closed list — the fix for PROP-06 — is itself incomplete: five items that meet the stated inclusion rule are missing from both the included and excluded enumerations (PROP-18, major). A planner cannot write complete Stream 2b stories from the current list. Second, two quantitative inconsistencies: the Summary's ~8,500 token claim exceeds what the stream totals support (~7,068, PROP-17), and the completion criterion references nine Stream 3 items where the table now has seven (PROP-16). Third, four minor and two note findings carried from the first review remain open — none blocking individually, but the Tier 4 scope gap (PROP-09) and the multiplier (PROP-08) affect planning accuracy.

Recommended path: complete the Stream 2b enumeration (add the five missing items or explicitly exclude them with rationale), correct the "nine" to "seven" in the completion criterion, and reconcile the Summary token figure with the stream totals. The four carried minor findings and two notes are addressable during planning and do not require another review pass.
