---
name: create-backlog-stories
description: "Read confirmed slice tables, write backlog/ST-NNNN.md story files with MoSCoW priorities, dependencies, and quality gates. Phase 4 of 4 in the create-backlog sequence."
category: planning
inputs:
  context:
    - docs/testing.yaml
---

# Create Backlog — Phase 4: Write Stories

Write story files from confirmed slice tables, validate, and present the final backlog. This is phase 4 of the [create-backlog sequence](../create-backlog/SKILL.md#operational-sequence). Story format, composition rules, and the done check live in the [parent skill](../create-backlog/SKILL.md).

Read [writing-quality-gates.md](../../rulebooks/conventions/writing-quality-gates.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates. Do not write first and check later.

**Prerequisite:** story-level slice tables have been confirmed by the user (output of [`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md)).

## Step 2 — Break EPICs into User Stories

For each EPIC, create `backlog/ST-NNNN.md` stories (or `ST-NNNNA.md`, `ST-NNNNB.md`, … when splitting an existing story) meeting **INVEST** — particularly: Independent (dependencies explicit in `deps`), Small (one implementation session), Testable (evidence as falsifiable invariants).

Apply the [story composition rules](../create-backlog/SKILL.md#story-composition-rules): write the Goal statement first, then the Demo (Rule 1), build Inputs and Affected Paths forward from Status Quo (Rule 2), write evidence as invariants (Rule 3), gather constraints as boundaries (Rule 4). Every story is a vertical slice that crosses all system boundaries its capability requires. A story that touches only one boundary (only schema, only service, only UI) and delivers nothing a person can demonstrate is not a story — fold it into the first story that needs it as a line item.

Each story records in `traces`: the scope-map Rule(s) it implements, the arc42 component(s) it touches, and any constraining ADR(s).

Judge each story's `tier` (`economy | standard | strong`) — the model strength its work needs, same vocabulary as agent frontmatter's `tier`.

### Section ownership

Give every fact one home. Each section answers one question. A fact stated in its home section is referenced elsewhere, never restated. Before writing a sentence, ask which section owns it; if another section owns it, write a reference instead.

| Section        | Owns                                        | Never contains                              |
| -------------- | ------------------------------------------- | ------------------------------------------- |
| Goal           | the observable outcome                      | how it is verified or built                 |
| Contract       | input→outcome cases, persistence effects    | narrative behavior or invariants            |
| Domain Rule    | invariants and must-nevers, domain language | status codes, request shapes, API mechanics |
| Demo Scenario  | the ordered walkthrough with literal values | deliverables                                |
| Demo Data      | the seeded rows                             | behavior                                    |
| Boundaries     | architectural constraints, no-side-effects  | deliverables or verification methods        |
| Affected Paths | where the work lands                        | what the work does                          |
| Evidence       | falsifiable checks                          | restatements of each other                  |

The common failures are a deliverable named in Affected Paths, the Contract, and Evidence; and a verification method stated in the Goal. Both are redundancy, not emphasis.

### Story body instructions

For each story, compose the body using these instructions:

01. **Goal.** Write from the EPIC's actor goals and the story's scope-map rules. At most three sentences describing what capability the story enables and its deliberately narrow scope. Do not state how it is verified or built.

02. **Contract or Domain Rule.** Choose one:

    - **Contract table** — when the story's behavior reduces to a finite set of input→outcome cases, write a `## Contract` table (columns: Operation, Input state, Outcome, Persistence) in place of separate Domain Rule, Outputs, and Required Behavior sections. The contract table is the normative core.

    - **Domain Rule + Outputs** — when the behavior is narrative or has more than a handful of input classes, keep separate sections. Extract entity lifecycle rules and invariants from `docs/agent-context.md` and supplementary specs for Domain Rule. Write Outputs as observable behavioral detail per system layer — what the system does after the story ships, not scope deltas.

    Do not write both a Contract table and separate Domain Rule/Outputs sections. If you chose Contract, the Domain Rule and Outputs content lives in the table.

03. **Demo Scenario as numbered steps.** Write the Demo section as a numbered step list with concrete values, not 2–4 sentence paragraphs. Each step names the actor, the action, and the expected observable result. The demo must use the shipped interface — the command, menu option, API, or trigger the actor would use in production. Tests verify a story; test output is not the capability the story delivers. If the demo cannot be performed without reading source code or running a test suite, the story is not a vertical slice — recut it. Every identifier in the Demo Scenario must resolve to a row in a Demo Data table — in this story or a predecessor. Never invent demo names inline.

04. **Demo Data.** When the story seeds rows, write a table — one row per seeded record, one column per field, literal values. State which seeding script is extended, whether the story extends an existing row or adds a new one, which rows must be written directly through the model because no API delivers them yet, and what the script's idempotency guard and existing output must preserve. When the story seeds nothing, say so and name the predecessor story whose seed set it depends on, plus the specific rows and states the flow needs. When no seeded data is involved at all, state "None."

05. **Boundaries.** Gather invariants and must-nots from traces, ADRs, agent-context technical concerns, and `testing.yaml`. Boundaries are non-negotiable rules: architectural constraints the story must respect, forbidden patterns, required naming conventions, must-not-touch modules, and no-side-effect rules.

06. **Affected Paths at coarsest honest granularity.** Name a file only when that exact file already exists and the story changes it. For work that creates new files, name the directory that will hold them and say what is added.

    - `src/module/service.py` — existing file, extend ✅ (the file exists)
    - `src/module/` — new `dtos.py`, `errors.py` ✅ (directory plus intent)
    - `src/module/dtos.py` — new file to create ❌ (a path guessed at planning time)

    A path invented at planning time ages badly and constrains the developer agent for no benefit.

07. **Inputs as reading manifest.** List the deliverables from depended-on stories, relevant spec rules, architecture references (arc42 sections, ADRs), and current implementation files the developer-agent needs to read. Link rather than repeat their contents. When `backlog/epics.md` contains ownership assignments (from testability-probe output), record them here: "contract X owned by this story" informs the agent which contracts it is responsible for testing. If the EPIC has a `### Ownership Resolution` table, read it and record assignments for contracts owned by this story.

08. **Evidence.** Independent, observable acceptance checks. When the story uses a Contract table, Evidence proves the contract without restating it. When the story uses Domain Rule + Outputs, Evidence replaces what was previously called Acceptance Criteria — falsifiable invariants traced to scope-map rules. Each check must be independently verifiable.

09. **Verification from testing.yaml.** List exact shell commands per test suite from the testing regime. For each suite in `testing.yaml` (at `docs/testing.yaml`), note the suite's name, its `root` directory, its `pattern`, and the command to run tests in that suite. Scan the suite's root for files matching the pattern and compare against evidence — record paths of pre-existing tests by filename, and identify target suite names for new tests. Read the document referenced by `testing_strategy:` in `testing.yaml` to determine cluster assignment and test budget for the story.

10. **Out of Scope.** Make scope exclusions explicit, especially when a broad business rule is implemented only at one operation or lifecycle stage.

11. **Stop Conditions as checkable predicates.** Each stop condition names a predicate the developer-agent evaluates before starting work, not a vague risk category. Scale the list by the story's `risk_level` (higher risk → more stop conditions). Include at least one specification-drift stop condition: "Code and the referenced specification disagree on [specific aspect] — report the conflicting files and the decision needed; do not add a workaround."

12. **Resolve Before Implementation.** Contract-level decisions the planning agent cannot resolve from spec, architecture, and codebase: transport formats, mutability boundaries, validation scope and timing, operation granularity, rejection behavior, cross-story side effects, computed vs. stored fields. Numbered list of concrete questions. "None" when fully specified. This section is the grilling entrypoint.

**Suggested Agent Plan — omit by default.** Include it only when implementation ordering is itself a requirement — a migration that must run before a service change, a generated-types step that gates downstream consumers. When ordering is obvious from the dependency chain and affected paths, the plan adds tokens without adding information.

**Fill `quality-gates` frontmatter.** Read the `gates` section of `testing.yaml`. For each gate where `enabled` is `true`, add its key (hyphenated form: `crap_score` → `crap-score`, `mutation_testing` → `mutation-testing`) to the story's `quality-gates` list. If no gate is enabled, or the story is prose-only (no production code), leave the list empty (`quality-gates: []`). If excluding a gate that is enabled in `testing.yaml`, justify in the story's Boundaries section.

**Backward compatibility — when `backlog/epics.md` contains old-model test-design sections** (produced by the former test-design skill), carry them into the story files as before:

- If the story's epic building-block entry has a `tests:` key, record those test file paths in the story's Inputs section (overriding any cross-referenced test discovery).
- If the entry contains a `#### Failure scenarios` section, write it verbatim into the story body immediately after the Evidence section.
- If the entry contains a `#### Prior Tests` section, write it verbatim into the story body immediately after the Failure scenarios section (or after Evidence if no Failure scenarios section exists).

**Detection heuristic:** if the EPIC has an `### Ownership Resolution` table, it is probe output — carry ownership assignments into the Inputs section. If it has `#### Failure scenarios` subsections under story entries, it is old-model test-design output — carry those sections. If neither is present, the cross-referencing behavior above continues unchanged.

See the [story template](../../rulebooks/templates/story.md) for the complete story structure. Reference the [parent skill composition rules](../create-backlog/SKILL.md#story-composition-rules) for section-ordering and depth guidance.

Format each story file via `.agent-factory/factory/scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Step 3 — Prioritise with MoSCoW

Record each story's **MoSCoW** priority in its body: `**Priority:** must-have | should-have | could-have | wont-have`.

## Step 4 — Mark dependencies

List blocking stories in `deps` (by `ST-NNNN` id). Run `.agent-factory/factory/scripts/backlog-lint --backlog-dir backlog` — it checks acyclicity — and fix any errors.

## Quality gate

Compose every story with the writing quality gates active. Every sentence passes all four gates while you write it, not after.

## Agent-readability check

Before presenting the backlog, verify that a coding agent can quickly identify: the one observable change, permitted and refused cases, data side effects, public boundaries, test evidence, verification commands, excluded work, and when to stop. Remove prose that does not answer one of those questions.

Reread the Goal and Demo Scenario sections for understandability. Can a developer unfamiliar with the epic understand what the story delivers and why it matters? Does the demo feel concrete and achievable in one session? If not, revise.

Present the complete backlog to the user. Ask:

- _"Are the MoSCoW priorities correct?"_
- _"Any missing stories?"_
- _"Should any dependencies be reordered?"_

## This skill ends here

The backlog is written and validated. Run the [done check](../create-backlog/SKILL.md#done-check) to verify completeness. The user confirms the backlog, then the planning agent commits to `dev` and hands off to the implementation agent.
