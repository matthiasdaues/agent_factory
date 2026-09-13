# Agent & Skill Audit — Frontier Model Impact

**Date:** 2026-09-12 (updated same day — second pass after pipeline changes)
**Scope:** `agent_factory/packages/factory/agents/` (18 agents) and `agent_factory/packages/factory/skills/` (66 skills, 4 supplementary reference files)
**Method:** Full read of every file, per-item analysis of token cost, prescriptive vs. declarative style, overlap with native model capabilities, and overlap with sibling items. Token estimates are line-count approximations (lines × ~4), not exact tokenizer counts.

______________________________________________________________________

## Summary

| Metric           | Value                         |
| ---------------- | ----------------------------- |
| Total items      | 84 (18 agents, 66 skills)     |
| Total token load | ~38,500                       |
| Recoverable      | ~8,500 (≈22%)                 |
| Well-designed    | 35 (keep as-is or minor trim) |

**Core finding:** The collection encodes genuine domain methodology — research epistemology, Structurizr DSL workflows, formal specification methods — that a frontier model would not produce unprompted. However, roughly a fifth of the total token budget is spent re-teaching methods the model already knows (TDD mechanics, Cockburn use cases, Vue best practices, OWASP), scripting steps it would derive from goals, or duplicating instructions across sibling skills.

**Update note:** The backlog pipeline expanded from 4 to 8 phases since the initial pass. A new parent skill (`create-backlog`) centralizes composition rules and quality gates — partially addressing the DRY violations flagged below. Two new phase skills (`make-concrete`, `slice-story`) and an expanded `grilling` skill with story-target mode were added. The story template grew to v2.1.0 with new frontmatter fields. These changes are factored into the findings and totals.

______________________________________________________________________

## Priority Actions

### Tier 1 — Immediate Wins

#### Agent boilerplate duplication (~1,200 tokens) ▸ Extract

The "Phase entry / Child return / Phase exit" block is copy-pasted verbatim into 10 of 18 agents. Move to a single convention file referenced once.

#### `implementation-agent` (3,254 → ~800 tokens) ▸ Trim

Largest agent. Encodes wave planning, branching model, gate-check loops, tier escalation, and prompt templates — dispatch protocol that belongs in scripts, not in the agent definition. The model spends capacity tracking branch management rules instead of making implementation decisions. Target: "resolve dependency graph, dispatch stories, verify completion."

#### `developer-agent` (1,964 → ~600 tokens) ▸ Trim

Heavy conditional branching on TDD mechanics (Red-Green-Refactor sub-conditions, `.feature` workflow). Frontier models do TDD natively. Replace with "implement using TDD per the story's test design" and let the model handle mechanics.

#### `derive-spec` (432 tokens) ▸ Remove

Explicitly superseded by `derive-feature`. Dead weight whenever the skill index loads.

#### `update-context` (96 tokens) ▸ Remove

Deprecation notice that does nothing. Handle the redirect elsewhere.

#### `scope-map-migration` (376 tokens) ▸ Remove

One-time migration skill. If it has been used, it is dead weight going forward.

______________________________________________________________________

### Tier 2 — Native-Knowledge Overlap

These items spend tokens re-teaching methods the model already knows from training data.

#### `derive-feature` (1,104 → ~600 tokens) ▸ Trim

~500 tokens re-teach Cockburn reasoning. Keep the project-specific output format and lifecycle rules; replace methodology pedagogy with "apply Cockburn reasoning to derive actor-goal pairs."

#### `qa-strategy-from-spec` (1,624 → ~800 tokens) ▸ Trim

Largest skill. The 15-item quality checklist restates constraints already embedded in its own template. The embedded markdown template (~120 lines) should be a separate reference file loaded on demand.

#### `vue-best-practices` (560 → ~60 tokens) ▸ Trim

Restates Vue 3 Composition API knowledge the model already has. Keep only project-specific deviations from standard practice.

#### `comic-relief` (324 → ~60 tokens) ▸ Trim

324 tokens prescribing when and how to tell jokes, including a "humor quadrangle" with Dilbert/XKCD/South Park/Hornblower vertices. A frontier model calibrates humor from a single sentence.

#### `create-backlog-stories` (~496 tokens) ▸ Trim (revised assessment)

Now 12 instructions (was 11) and references the parent `create-backlog` for composition rules — a DRY improvement. However, it still embeds its own copy of the Agent-Answerability and International Readability gate tables (~100 tokens) instead of referencing the parent where they are now canonically defined. The backward-compatibility heuristic for old-model test-design sections (~80 tokens) should be removed once old-format EPICs are migrated.

#### `security-review` (172 tokens) ▸ Trim

May actively interfere with the model's native security review capabilities. The OWASP-10 checklist approach is less sophisticated than what the model does unprompted. Only the "minimize false positives" line adds value.

#### `explain-concept` (320 → ~80 tokens) ▸ Trim

The Sandman/Lucien persona, self-check step, and audience-calibration rubric are native model behavior. The search-path routing (guide → INDEX → rulebooks → README) is the only high-value part.

______________________________________________________________________

### Tier 3 — Consolidation Targets

#### `grill-me` + `grill-with-docs` + `grilling` (3 skills → 1) ▸ Merge (still open)

`grilling` was expanded with a story-target mode (using `Resolve Before Implementation` as agenda) — a good addition. But `grill-me` and `grill-with-docs` still exist as separate redirect files. Consolidate them into `grilling` with a mode parameter.

#### `code-review-agent` ↔ `qa-agent` ▸ Clarify boundary

Both invoke `fagan-review` and both trigger on "code review." Sharpen the boundary: code-review = pre-merge diff only, QA = post-merge full codebase + security + bug hunt. Also evaluate against Claude Code's built-in `/code-review`.

#### `research-report-writer` ↔ `research-synthesizer` (2 agents) ▸ Merge

Nearly identical structure. Could merge with a mode parameter or share a base definition.

#### DRY violations in backlog skills (~250 duplicated tokens) ▸ Extract (partially addressed)

The new parent `create-backlog` skill now centralizes composition rules, quality gates (Agent-Answerability, International Readability), and the done check. Phase skills reference the parent — a significant DRY improvement. Remaining duplication: `create-backlog-stories` still embeds its own copy of both gate tables instead of referencing the parent's. The "international team" instruction also appears independently in `draft-proposal`.

#### `testability-probe` ↔ `test-design` (~100 duplicated tokens) ▸ Extract

Shared prerequisite guard is copy-pasted verbatim. Extract to a shared guard or a one-liner: "requires `testing.yaml` with `testing_strategy` and `suites`."

______________________________________________________________________

### New and Revised Skills (second-pass additions)

#### `create-backlog` parent skill (~560 tokens) ▸ Keep — well-designed

New canonical parent for the 8-phase backlog pipeline. Centralizes composition rules (4 rules), quality gates, operational sequence table, story file format reference, and done check. Phase skills reference this document instead of restating shared definitions. Good refactoring that addresses several DRY violations from the initial audit. The pipeline now runs: EPICs → write EPICs → testability probe → story slices → write stories → grilling → make concrete → slice story.

#### `create-backlog-make-concrete` (~572 tokens) ▸ Keep — well-designed

Phase 6: works grilled answers into their home sections in the story body. The answer-type → home-section mapping table (entity lifecycle → Domain Rule, HTTP method → Required API Behavior, etc.) is genuinely additive — the model would not reliably route resolved answers to correct sections without it. The "do not touch Resolve Before Implementation" instruction is important and non-obvious — it preserves the decision record. Quality gate references parent correctly.

#### `create-backlog-slice-story` (~684 tokens) ▸ Keep — well-designed

Phase 7: cuts concrete stories into implementation stories along hard boundaries. The split-decision criteria (6 boundary types: backend/frontend, schema/behavior, generated types/consumers, etc.) are genuinely useful for consistent slicing. The "do not split" escape hatch for narrow stories prevents over-decomposition. Dependency chaining rules and inheritance semantics are necessarily prescriptive for a high-stakes artifact transformation.

#### `grilling` revised (~236 tokens, was ~168) ▸ Keep — improved

Now handles both proposal targets and story targets. The story-target mode uses `Resolve Before Implementation` as the grilling agenda — a clean interface between planning and implementation. The blockquote format for resolved answers with dates is a convention the model would not standardize on its own. Well-integrated with the new pipeline phases.

#### Story template v2.1.0 (~816 tokens) ▸ Trim reference documentation

Major expansion. Added frontmatter fields: `concerns`, `quality-gates`, `tests`, `test-design-pass`, `risk_level`. Added body sections: `Resolve Before Implementation`, `Suggested Agent Plan`, `Required Behavior` (optional). The template body is well-structured. However, ~400 tokens of field documentation at the bottom (`### risk_level`, `### touches`, `### concerns`, etc.) is reference material that a model reads once and retains — it should be a separate reference file rather than part of the template loaded every time a story is written. The `touches` hygiene rule is also embedded in the body template itself; it belongs in the parent skill or a conventions document.

______________________________________________________________________

### Tier 4 — Moderate Trimming

| Item                      | Current | Target | Note                                                                                                                                                 |
| ------------------------- | ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mutation-testing`        | ~600    | ~300   | Tutorial content re-read every invocation. Split into runtime skill + referenced methodology doc.                                                    |
| `model-structurizr-slice` | ~824    | ~500   | Inline DSL examples and 11-point checklist → reference files. Watch drift against `maintain-architecture`.                                           |
| `implement-issue`         | ~320    | ~180   | TDD pedagogy (London vs. Chicago) the model knows. Three gates where two suffice. Keep file-path routing.                                            |
| `research-reporting`      | ~464    | ~300   | "Forbidden Content" is ~80% redundant with "Key Principles." Preferred-wording list micro-manages prose.                                             |
| `virgil`                  | ~1,969  | ~1,969 | Behavioral anchors (~120 tokens) are author's stamp — functionally inert on frontier models but do not conflict with operational instructions. Keep. |
| `testability-probe`       | ~1,060  | ~800   | "What this skill does NOT do" is design commentary, not operational instruction. Prerequisite guard duplicated.                                      |
| `process-transcript`      | ~728    | ~500   | RFC 2119 formalism and extraction-method table are reference data, not per-invocation instructions.                                                  |
| `run-step`                | ~260    | ~200   | "What this deliberately does not do (yet)" is design commentary. Decision table is good.                                                             |
| `reverse-map`             | ~480    | ~350   | Scripted dialogue lines ("I'm going to look through your codebase...") — let the model handle UX naturally.                                          |

______________________________________________________________________

## What Works Well

These items demonstrate good skill design for frontier models: declarative goals, genuine domain methodology, project-specific contracts the model cannot derive, and lean token budgets.

### Agents

| Agent                   | Tokens | Why it works                                                       |
| ----------------------- | ------ | ------------------------------------------------------------------ |
| `claim-reviewer`        | ~417   | Lean, boundary-focused, genuinely additive constraints             |
| `proposal-review-agent` | ~1,240 | 8-check adversarial review adds real value not produced unprompted |
| `coaching-agent`        | ~286   | Minimal, skill-dispatching, does not over-prescribe                |
| `researcher`            | ~310   | Lean, well-bounded, declarative                                    |
| `research-orchestrator` | ~844   | Clean role separation with permitted/forbidden action lists        |

### Skills

| Skill                          | Tokens | Why it works                                                                                            |
| ------------------------------ | ------ | ------------------------------------------------------------------------------------------------------- |
| `pugh-matrix`                  | ~140   | Model exemplar. Declarative format, no scripted steps                                                   |
| `scratchpad`                   | ~124   | Exemplary brevity. Delegates all logic to the script                                                    |
| `write-adr`                    | ~248   | Judgment criteria gate ("offer only when all three hold") — declarative                                 |
| `write-prd`                    | ~160   | Brief, clear, well-bounded                                                                              |
| `handoff`                      | ~280   | Fills a real gap. Justified prescription for high-stakes contracts                                      |
| `inspect-spec`                 | ~212   | Deterministic lint + LLM semantic review — strong two-pass pattern                                      |
| `init-factory`                 | ~272   | Clean wrapper. "This skill exists only for conversational trigger."                                     |
| `maintain-architecture`        | ~464   | Necessarily detailed DSL workflow. Token cost justified by complexity                                   |
| `refutation-design`            | ~316   | Declarative principles, lets the model reason about application                                         |
| `claim-formulation`            | ~256   | Domain-specific methodology. Model would not produce this unprompted                                    |
| `crap-score`                   | ~356   | Reference card for a deterministic tool — correct role for a skill                                      |
| `dependency-check`             | ~360   | Same pattern as crap-score. Tool documentation, not reasoning                                           |
| `clarify-requirements`         | ~156   | Clean router. Delegates to specialized skills rather than cramming                                      |
| `source-research`              | ~124   | Lean. Delegates to schema                                                                               |
| `research-synthesis`           | ~160   | Lean. Delegates to schema                                                                               |
| `research-planning`            | ~224   | Lean. Delegates to schemas and templates                                                                |
| `reconcile-spec`               | ~236   | Clean classification table — declarative, lets model reason                                             |
| `spec-feedback`                | ~168   | Well-differentiated from reconcile-spec. Lean                                                           |
| `validate`                     | ~196   | Gate table — good reference data, useful context                                                        |
| `scaffold-arc42`               | ~656   | Necessary reference with STRUCTURIZR.md. Well-scoped                                                    |
| `newcomer-tour`                | ~316   | Framework-specific onboarding. No native overlap                                                        |
| `atam-review`                  | ~232   | Procedural discipline matches the formal method                                                         |
| `bug-hunt`                     | ~176   | Compact, declarative focus + prescriptive fix loop                                                      |
| `domain-modeling`              | ~176   | Good behavioral anchoring. Inline-update discipline prevents failure modes                              |
| `create-backlog`               | ~560   | Canonical parent centralizing composition rules, quality gates, done check. Good DRY refactoring        |
| `create-backlog-make-concrete` | ~572   | Answer-type → home-section mapping is genuinely additive. Decision-record preservation is non-obvious   |
| `create-backlog-slice-story`   | ~684   | Hard-boundary split criteria and dependency chaining rules are necessarily prescriptive                 |
| `grilling` (revised)           | ~236   | Story-target mode with Resolve Before Implementation as agenda. Clean planning↔implementation interface |

______________________________________________________________________

## Overlap Map

Skills and agents that claim overlapping territory. Each cluster risks contradictory instructions when multiple members fire in one session.

### Code review

**Members:** `code-review-agent` · `qa-agent` · Claude Code built-in `/code-review`

All three trigger on "code review." The custom agent's three "review gates" (international team, junior clarity, senior respect) are style instructions, not review methodology. Run 5 representative diffs through the built-in and the custom agent — if quality matches, retire the custom one.

### Spec vs. code comparison

**Members:** `reconcile-spec` · `spec-feedback` · `qa-strategy-from-spec` · `reverse-map`

Four skills touch "compare code to spec" from different angles. Well-differentiated today (per-issue / per-phase / strategy / brownfield), but the contract-ownership concept is defined slightly differently in three of them.

### Test ownership and risk

**Members:** `testability-probe` · `test-design` · `qa-strategy-from-spec`

Three skills touching the same contract-ownership concept with slightly different rules. The prerequisite guard is copy-pasted between `testability-probe` and `test-design`. Risk-class definitions in `test-design` are duplicated from `testing-strategy.md`.

### Scope map authorship

**Members:** `reverse-map` · `scope-map-migration`

Both write `scope-map.md`. If the migration has been performed, the migration skill is dead weight.

### Backlog pipeline quality gates

**Members:** `create-backlog` (parent) · `create-backlog-stories` · `create-backlog-make-concrete` · `create-backlog-slice-story`

The parent skill now canonically defines Agent-Answerability (9 checks) and International Readability (6 checks). `make-concrete` and `slice-story` correctly reference the parent. `create-backlog-stories` still embeds its own copy of both tables — these will drift if the parent's definitions change. The "Junior Clarity / Senior Acceptance" framing in `create-backlog-stories` is not present in the parent's gate definitions, creating a dual standard.

### Structurizr DSL → docs

**Members:** `model-structurizr-slice` · `maintain-architecture`

Both describe how to update docs from DSL with different levels of detail. Risk of drift if conventions change in one but not the other.

______________________________________________________________________

## Design Principles Emerging from the Good Skills

The well-designed items share a pattern worth codifying for future skill authoring.

### Declarative over prescriptive

State the goal and constraints. Let the model determine the steps. `pugh-matrix`, `refutation-design`, and `write-adr` do this well. `developer-agent` and `implementation-agent` do not.

### Delegate to schemas and reference files

The research cluster (`source-research`, `research-synthesis`, `research-planning`) defines output contracts by reference, not inline. Every invocation loads only the routing logic. Heavy templates and checklists should be separate files loaded on demand.

### Prescribe only what the model would not do

The `research-report-writer`'s "forbidden phrasing" list is genuinely additive — a model would naturally use "is true" without this constraint. The `explain-concept`'s "self-check completeness" step is not — the model does this already.

### Tool wrappers, not reasoning replacements

`crap-score` and `dependency-check` document deterministic tools the model needs to call. They do not attempt to replace or guide the model's reasoning about the results. This is the correct role for a skill paired with a script.
