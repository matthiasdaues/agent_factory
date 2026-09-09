---
schema_version: 2
title: Agent-Ready Story Format
status: open
owner: md@matthiasdaues.de
created: 2026-09-09
updated: 2026-09-09
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - factory/rulebooks/templates/story.md
    - factory/skills/create-backlog/SKILL.md
    - factory/skills/create-backlog-stories/SKILL.md
    - factory/skills/create-backlog-write-epics/SKILL.md
    - factory/skills/create-backlog-story-slices/SKILL.md

governance:
  assurance: elevated
  risk_domains:
    - reliability

estimate:
  as_of: 2026-09-09
  basis: judgment
  confidence: medium
  human_review_hours:
    min: 1.0
    max: 2.0
  normalized_tokens:
    min: 8000
    max: 15000
  estimated_consumption:
    min: 80000
    max: 225000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Agent-Ready Story Format

## Summary

Redesign the backlog writing skills so stories and epics come out agent-ready in
a single pass — concrete enough for a coding agent to start implementation
without rereading the full planning context. The current story template is
planning-oriented (traces, invariants, scope deltas); the target format is
implementation-oriented (explicit files, behavioral outputs, verification
commands, stop conditions). This eliminates the need for a post-hoc rewrite
step.

## Motivation

A production rewrite skill (the "dorthe" format, developed for the Gigacron
project) demonstrated that stories produced by the current `create-backlog-stories`
skill require a second pass before a developer-agent can execute them
efficiently. The rewrite adds Goal, Domain Rule, Affected Paths, Inputs,
Outputs, Required Behavior, Constraints, Suggested Agent Plan, Verification, and
Agent Stop Conditions — sections the planning agent already has the information
to produce but the current template does not ask for.

The two-pass approach doubles token spend per story, creates two artifacts to
maintain, and drifts when the codebase changes between planning and rewrite. A
single-pass approach folds the rewrite's quality bar into the existing skill
sequence and Junior Clarity / Senior Acceptance gates.

## Core Principles

- **One story, one file, one pass.** The planning agent produces the final
  implementable story. No rewrite phase.
- **Agent-answerable.** Every story answers eight questions without external
  context: what behavior exists after? which files change? which domain rule
  owns it? what existing state matters? what should tests prove? what commands
  verify? what is out of scope? when should the agent stop and ask?
- **Plain language over architecture-speak.** Domain terms are used and defined
  in context; architectural identifiers appear only where they name real code.
- **Preserve planning rigor.** Traces, acceptance-criteria-as-invariants,
  vertical-slice gates, and backlog-lint validation remain unchanged.

## Design

### New story template structure

The template (`factory/rulebooks/templates/story.md`) changes from the current
seven-section body to a thirteen-section body. Sections marked (required) must
appear in every story; sections marked (conditional) appear when they apply.

**Frontmatter** — unchanged, plus one optional field:

```yaml
risk_level: low          # low | medium | high (optional; drives Agent Stop
                         # Conditions depth and review attention)
```

**Body sections, in order:**

| #   | Section               | Replaces / extends             | Required    |
| --- | --------------------- | ------------------------------ | ----------- |
| 1   | Goal                  | intro paragraph                | required    |
| 2   | Domain Rule           | Terminology                    | required    |
| 3   | Demo Scenario         | Demo                           | required    |
| 4   | Affected Paths        | new (extends `touches`)        | required    |
| 5   | Inputs                | new (reading manifest)         | required    |
| 6   | Outputs               | Scope → Delivers               | required    |
| 7   | Required Behavior     | new (API / CLI / UI specifics) | conditional |
| 8   | Constraints           | new (must-not list)            | required    |
| 9   | Suggested Agent Plan  | new (numbered implementation)  | required    |
| 10  | Acceptance Criteria   | same (checkboxes, invariants)  | required    |
| 11  | Verification          | new (exact commands)           | required    |
| 12  | Out of Scope          | Scope → Out of scope           | required    |
| 13  | Agent Stop Conditions | new (halt triggers)            | required    |

**Sections removed:**

- **Terminology** — folds into Domain Rule. Terms are defined where they are
  used, not in a separate glossary appendix.
- **Notes for the Implementer** — content distributes: pre-existing tests →
  Inputs; suggested approach → Suggested Agent Plan; risk domains → Agent Stop
  Conditions; gate exclusion justifications → Constraints.
- **Scope (three-part)** — the Status quo / Delivers / Out of scope block
  splits: Status quo content moves to Inputs (what already exists); Delivers
  moves to Outputs (per-layer behavioral detail); Out of scope becomes its own
  top-level section.

### Section definitions

**Goal.** One paragraph. What user-visible or API-visible behavior must exist
after this story ships. Plain domain language. No architecture identifiers
unless they name real code the agent will touch.

**Domain Rule.** Bullet list. The mental model the agent needs: what entities
mean, what invariants hold, what must never happen. Written as "use this wording"
guidance. Sources definitions from the spec, glossary, and ADRs referenced in
`traces`. Defines every project term the agent would not know from general
programming.

**Demo Scenario.** Numbered step list (not a paragraph). Each step is an
observable action or system response with concrete values. A junior can walk the
steps as a manual test.

**Affected Paths.** Explicit file listing grouped by layer (backend, frontend,
generated, tests, or whatever layers the project uses). Each entry is either
an existing file that changes or a new file to create, marked accordingly.
`touches` (frontmatter) remains as the coarse-grained dispatcher input for
overlap detection; Affected Paths is the fine-grained implementation guide.

**Inputs.** What the agent reads before starting. Lists: dependencies' delivered
state (from `deps`), spec rules (from `traces`), architecture references,
current implementation files the story extends. This is a reading manifest — not
an exhaustive codebase survey, but the minimum set of documents and files the
agent needs to understand the starting point.

**Outputs.** Concrete deliverables per layer with behavioral detail. Not "adds
update route" but "API can update an existing TaskDraft via partial PATCH; only
provided fields change." Each output states what the system does in observable
terms.

**Required Behavior** (conditional). The story's primary delivery mechanism
described concretely. For an API story: operations, request/response shapes,
status codes, semantics. For a CLI story: commands, flags, exit codes. For a UI
story: interactions, state transitions, visual feedback. Omit when the Outputs
section already captures the behavior fully (small stories often need no
separate section).

**Constraints.** Explicit must-not list gathered from: ADRs in `traces`, project
conventions from `docs/agent-context.md` technical concerns, testing regime from
`docs/testing.yaml`, and scope exclusions. Includes project-specific command
conventions (e.g. "prefix shell commands with `rtk`", "do not run tests with
plain `pytest`"). Every constraint states what the agent must not do and, where
non-obvious, why.

**Suggested Agent Plan.** Numbered implementation steps in dependency order.
Backend-first, frontend-first, or interleaved depending on the story's shape.
The developer-agent follows or adapts; the plan is guidance, not a contract.
Steps reference files from Affected Paths and outputs from Outputs.

**Acceptance Criteria.** Checkbox list of falsifiable invariants, unchanged from
the current format. Each criterion traces to a scope-map rule parenthetically.
Checkboxes replace dash-prefixed bullets.

**Verification.** Exact shell commands grouped by suite, derived from
`docs/testing.yaml`. Plus any generation, lint, or format commands relevant to
the story's outputs. After verification, record the actual test modules touched
and any implementation-record metadata (e.g.
`test-design-pass: skipped-feature-governed`).

**Out of Scope.** Dash-prefixed list of explicit exclusions. Each item names
what is excluded with enough context to prevent confusion about why. Moved from
a subsection of Scope to top-level because agents scan section headings.

**Agent Stop Conditions.** Dash-prefixed list of situations where the
developer-agent should halt and ask for clarification rather than guess.
Derived from: ambiguity points in the spec, conflicting implementation
patterns in the codebase, missing infrastructure the story assumes, and
the story's `risk_level`. Higher risk → more stop conditions.

### Changes to create-backlog-stories (Phase 4)

The skill's Step 2 (Break EPICs into User Stories) gains instructions for
filling each new section. The analytical work the skill already does —
codebase survey, spec reading, testing.yaml cross-reference — feeds directly
into the new sections rather than being compressed into a three-part Scope
block and a Notes section.

Specific additions to the skill:

01. **Goal derivation.** Write Goal from the EPIC's actor goals + the story's
    scope-map rules. One paragraph, plain language.
02. **Domain Rule extraction.** Read domain concerns from `docs/agent-context.md`,
    follow `Read:` paths to supplementary specs and glossary. Extract entity
    lifecycle rules and invariants relevant to this story.
03. **Demo as numbered steps.** Change from "2–4 sentences" to "numbered step
    list with concrete values."
04. **Affected Paths from codebase survey.** Extend the current Status Quo
    survey. For each layer, list specific files that exist and will change, and
    new files to create.
05. **Inputs as reading manifest.** List the deps deliverables, spec rules,
    architecture references, and current implementation files the agent needs.
06. **Outputs with behavioral detail.** For each layer, state what the system
    does in observable terms after the story ships. This is the biggest change —
    the planning agent must think through the implementation shape concretely
    rather than stating scope deltas.
07. **Required Behavior from spec rules.** Derive from the governing scenarios
    and acceptance criteria. Write in the vocabulary of the story's primary
    delivery mechanism (API, CLI, UI).
08. **Constraints from ADRs + conventions.** Gather must-nots from traces,
    agent-context technical concerns, and testing.yaml.
09. **Suggested Agent Plan.** Write a numbered step sequence in implementation
    order, referencing Affected Paths and Outputs.
10. **Verification from testing.yaml.** List exact commands per suite from the
    testing regime.
11. **Agent Stop Conditions from risk and ambiguity.** Identify where the
    spec is ambiguous, where codebase patterns conflict, and where missing
    infrastructure would block the agent.

The existing testing.yaml cross-reference (steps 1–6 in current skill) folds
into the Verification and Inputs sections rather than producing a separate
Notes for the Implementer subsection.

### Changes to create-backlog-write-epics (Phase 2)

Minor adjustments:

- The building-block inventory gains a **Goal** column: one sentence of concrete
  behavior per anticipated story. This seeds the story's Goal section in
  Phase 4.
- Add a **Domain Rules** subsection per EPIC listing the invariants that
  govern the EPIC's stories. This seeds each story's Domain Rule section.
- Demo format is already numbered steps — no change.

### Changes to create-backlog-story-slices (Phase 3)

The story-level slice table gains one column:

| #   | Capability | Goal (one sentence) | Boundaries crossed | Demo sentence |
| --- | ---------- | ------------------- | ------------------ | ------------- |

The Goal column forces the planning agent to articulate what each story
delivers in plain language before writing the full story file.

### Changes to create-backlog parent skill

Story composition rules update:

- **Rule 1** becomes "Goal First, then Demo" — write the Goal statement first
  (what behavior must exist), then the Demo Scenario (how a person shows it).
  If you cannot write the Goal, the story is not deliverable.
- **Rule 2** (Forward from Status Quo) stays but the output shape changes:
  Status Quo content feeds Inputs + Affected Paths instead of a three-part
  Scope block.
- **Rule 3** (Criteria Are Invariants) stays unchanged.
- **New Rule 4: Constraints Are Boundaries.** Every must-not from ADRs,
  conventions, testing regime, and scope exclusions goes in Constraints. A
  must-not buried in prose is a must-not the agent will miss.

### Quality gate changes

The existing Junior Clarity / Senior Acceptance gates absorb the dorthe quality
bar as eight concrete checks:

| Check                                | Answered by           |
| ------------------------------------ | --------------------- |
| What behavior must exist after?      | Goal                  |
| Which files change?                  | Affected Paths        |
| Which domain rule owns the behavior? | Domain Rule           |
| What existing state matters?         | Inputs                |
| What should tests prove?             | Acceptance Criteria   |
| What commands verify completion?     | Verification          |
| What is explicitly out of scope?     | Out of Scope          |
| When should the agent stop and ask?  | Agent Stop Conditions |

If any check cannot be answered from the story alone, the story fails the gate.

A third gate runs alongside Junior Clarity and Senior Acceptance:

**International Readability.** The story is written for a team whose members
share English as a working language but none are native speakers. For every
sentence in Goal, Domain Rule, Demo Scenario, Constraints, and Agent Stop
Conditions:

- No idioms, slang, or culture-specific metaphors. "The service rejects the
  request" beats "the service kicks back."
- No ambiguous pronouns across sentence boundaries. Repeat the noun.
- Short sentences (under 25 words). One idea per sentence.
- Active voice. "The agent validates the draft" beats "the draft is validated."
- Domain terms are used consistently — one term per concept, never alternated
  with synonyms for variety.
- Abbreviations are spelled out on first use within the story, even when the
  spec already defined them.

If any sentence fails, rewrite it before the story leaves the gate.

### Plain-Language Pass

After drafting each story, the planning agent rereads it once for
understandability. For every sentence in Goal, Domain Rule, and Demo
Scenario:

- Could a coding agent name the concrete code or behavior this points to?
- Would a newcomer understand the sentence without knowing the planning history?
- Does a domain term either name a real project concept or get explained nearby?

If no, rewrite the sentence in plainer words while preserving the domain term
when it is important.

### backlog-lint changes

The linter validates the new required sections exist (by heading match) and
that checkboxes are used for Acceptance Criteria. The `risk_level` field is
validated as an enum when present.

## Scope

**In the first release:**

- Redesigned `factory/rulebooks/templates/story.md` with new section structure.
- Updated `factory/skills/create-backlog-stories/SKILL.md` to fill new sections.
- Updated `factory/skills/create-backlog-write-epics/SKILL.md` with Goal column
  and Domain Rules subsection.
- Updated `factory/skills/create-backlog-story-slices/SKILL.md` with Goal column
  in slice table.
- Updated `factory/skills/create-backlog/SKILL.md` with revised composition
  rules and quality gate.
- Updated `factory/scripts/backlog-lint` to validate new sections and
  `risk_level`.

**Explicitly deferred (do NOT plan stories for these):**

- Migration of existing backlogs to the new format.
- A standalone rewrite skill in the factory (the dorthe skill's function is
  absorbed; the original remains project-specific in Gigacron).
- Changes to the test-design skill (its output feeds into stories as before).
- Changes to the developer-agent (it already reads story files; the new
  sections give it more to work with, no protocol change needed).
- Project-specific command conventions (e.g. `rtk` prefixes) — these remain
  in project-level agent-context or house-rules, not in the factory template.

## Open Questions

- Should Required Behavior be required rather than conditional? Every story
  has some primary behavior, but very small stories might duplicate Outputs.
- Should Suggested Agent Plan carry a disclaimer that the developer-agent may
  deviate, or is the "guidance, not a contract" framing in the skill sufficient?
- The `risk_level` field overlaps with `governance.risk_domains` on the
  proposal. Should it derive from the EPIC's risk classification instead of
  being set per story?

## Completion Criteria

- Stories produced by `create-backlog-stories` match the new template structure
  without manual editing.
- `backlog-lint` validates the new required sections and rejects stories missing
  them.
- A developer-agent can answer all eight quality-bar questions from the story
  file alone — verified by running one story through implementation.
- The dorthe rewrite skill produces no changes when run against a story already
  written in the new format (the rewrite is a no-op).

## Guiding Rule

A story is done when the developer-agent can start implementing from the story
file alone, without rereading the spec, the architecture, or the planning
context.
