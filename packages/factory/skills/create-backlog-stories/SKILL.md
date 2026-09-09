---
name: create-backlog-stories
description: "Read confirmed slice tables, write backlog/ST-NNNN.md story files with MoSCoW priorities, dependencies, and quality gates. Phase 4 of 4 in the create-backlog sequence."
category: planning
inputs:
  - docs/testing.yaml
disable-model-invocation: false
---

# Create Backlog — Phase 4: Write Stories

Write story files from confirmed slice tables, validate, and present the final backlog. This is phase 4 of the [create-backlog sequence](../create-backlog/SKILL.md#operational-sequence). Story format, composition rules, and the done check live in the [parent skill](../create-backlog/SKILL.md).

Write for an international Team whose members have English as a common, but not as a native language.

**Prerequisite:** story-level slice tables have been confirmed by the user (output of [`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md)).

## Step 2 — Break EPICs into User Stories

For each EPIC, create `backlog/ST-NNNN.md` stories meeting **INVEST** — particularly: Independent (dependencies explicit in `deps`), Small (one implementation session), Testable (acceptance criteria as falsifiable invariants).

Apply the [story composition rules](../create-backlog/SKILL.md#story-composition-rules): write the Goal statement first, then the Demo (Rule 1), build Inputs and Affected Paths forward from Status Quo (Rule 2), write acceptance criteria as invariants (Rule 3), gather constraints as boundaries (Rule 4). Every story is a vertical slice that crosses all system boundaries its capability requires. A story that touches only one boundary (only schema, only service, only UI) and delivers nothing a person can demonstrate is not a story — fold it into the first story that needs it as a line item.

Each story records in `traces`: the scope-map Rule(s) it implements, the arc42 component(s) it touches, and any constraining ADR(s).

Judge each story's `tier` (`economy | standard | strong`) — the model strength its work needs, same vocabulary as agent frontmatter's `tier`.

For each story, fill the 13-section body using these 11 instructions:

01. **Goal derivation.** Write Goal from the EPIC's actor goals + the story's scope-map rules. One paragraph, plain language describing what capability the story enables.

02. **Domain Rule extraction.** Read domain concerns from `docs/agent-context.md`, follow `Read:` paths to supplementary specs and glossary. Extract entity lifecycle rules and invariants relevant to this story — the constraints the implementation must honor.

03. **Demo as numbered steps.** Write the Demo section as a numbered step list with concrete values, not 2–4 sentence paragraphs. Each step should name the actor, the action, and the expected observable result.

04. **Affected Paths from codebase survey.** Extend the current Status Quo section survey. For each system layer (schema, backend, frontend, deployment, etc.), list specific files that exist and will change, and new files to create. Reference actual files in the codebase, not spec abstractions.

05. **Inputs as reading manifest.** List the deliverables from depended-on stories, relevant spec rules, architecture references (arc42 sections, ADRs), and current implementation files the developer-agent needs to read. When `backlog/epics.md` contains ownership assignments (from testability-probe output), record them here: "contract X owned by this story" informs the agent which contracts it is responsible for testing. If the EPIC has a `### Ownership Resolution` table, read it and record assignments for contracts owned by this story.

06. **Outputs with behavioral detail.** For each system layer, state what the system does in observable terms after the story ships. This is a concrete description of behavior, not scope deltas — the developer-agent must think through the implementation shape concretely. Include user-visible changes (UI, API, CLI), state changes (database, files, cache), and side effects (logs, metrics, network calls).

07. **Required Behavior from spec rules (conditional).** Derive from the governing scenarios and acceptance criteria. Write in the vocabulary of the story's primary delivery mechanism (API, CLI, UI). Include this section only when the behavior is not fully captured in Outputs — omit for small stories where Outputs already covers everything.

08. **Constraints from ADRs + conventions.** Gather must-nots from traces, agent-context technical concerns, and `testing.yaml`. Constraints are non-negotiable rules: architectural boundaries the story must respect, forbidden patterns, required naming conventions, and must-not-touch modules.

09. **Suggested Agent Plan.** Write a numbered step sequence in implementation order, referencing Affected Paths and Outputs. Each step names a file to create or modify and describes the concrete change in terms the developer-agent can execute directly (e.g. "Add test_foo_filter in test_model.py; add FooFilter class to model.py").

10. **Verification from testing.yaml.** List exact shell commands per test suite from the testing regime. For each suite in `testing.yaml` (at `docs/testing.yaml`), note the suite's name, its `root` directory, its `pattern`, and the command to run tests in that suite. Scan the suite's root for files matching the pattern and compare against acceptance criteria — record paths of pre-existing tests by filename, and identify target suite names for new tests. Read the document referenced by `testing_strategy:` in `testing.yaml` to determine cluster assignment and test budget for the story.

11. **Agent Stop Conditions from risk and ambiguity.** Identify situations where the developer-agent should halt and ask for clarification. List spec ambiguities (missing detail, conflicting rules), conflicting codebase patterns (inconsistent naming, competing architectures), and missing infrastructure (test fixtures not yet wired, deployment targets not yet configured). Scale the list by the story's `risk_level` (higher risk → more stop conditions).

**Backward compatibility — when `backlog/epics.md` contains old-model test-design sections** (produced by the former test-design skill), carry them into the story files as before:

- If the story's epic building-block entry has a `tests:` key, record those test file paths in the story's Inputs section (overriding any cross-referenced test discovery).
- If the entry contains a `#### Failure scenarios` section, write it verbatim into the story body immediately after the Acceptance Criteria section.
- If the entry contains a `#### Prior Tests` section, write it verbatim into the story body immediately after the Failure scenarios section (or after Acceptance Criteria if no Failure scenarios section exists).

**Detection heuristic:** if the EPIC has an `### Ownership Resolution` table, it is probe output — carry ownership assignments into the Inputs section. If it has `#### Failure scenarios` subsections under story entries, it is old-model test-design output — carry those sections. If neither is present, the cross-referencing behavior above continues unchanged.

See the [story template](../../rulebooks/templates/story.md) for the complete 13-section structure. Reference the [parent skill composition rules](../create-backlog/SKILL.md#story-composition-rules) for section-ordering and depth guidance.

Format each story file via `factory/scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Step 3 — Prioritise with MoSCoW

Record each story's **MoSCoW** priority in its body: `**Priority:** must-have | should-have | could-have | wont-have`.

## Step 4 — Mark dependencies

List blocking stories in `deps` (by `ST-NNNN` id). Run `factory/scripts/backlog-lint --backlog-dir backlog` — it checks acyclicity — and fix any errors.

## Quality gate

Review every story through two lenses:

**Junior Clarity:** Read the story as a junior developer. Can you start working right now — do you know which file to open first, what the first test asserts, and what "done" looks like? If not, the story is underspecified.

**Senior Acceptance:** Read the story as a senior grooming the backlog. Would you hand this to your team without a follow-up conversation — is the scope bounded, the demo concrete, every criterion testable, and nothing left to interpret? If not, the story is not ready.

**Agent-Answerability Checks:** A story fails this gate if any check cannot be answered from the story alone:

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

**International Readability:** Six concrete sentence-level checks for Goal, Domain Rule, Demo Scenario, Constraints, and Agent Stop Conditions:

- No idioms, slang, or culture-specific metaphors.
- No ambiguous pronouns across sentence boundaries. Repeat the noun.
- Short sentences (under 25 words). One idea per sentence.
- Active voice.
- Domain terms are used consistently — one term per concept, never alternated with synonyms for variety.
- Abbreviations are spelled out on first use within the story, even when the spec already defined them.

If any sentence fails, rewrite it before the story leaves the gate.

## Plain-language pass

Before presenting the backlog, reread the Goal, Domain Rule, and Demo Scenario sections for understandability. Can a developer unfamiliar with the epic understand what the story delivers and why it matters? Does the demo feel concrete and achievable in one session? If not, revise.

Present the complete backlog to the user. Ask:

- _"Are the MoSCoW priorities correct?"_
- _"Any missing stories?"_
- _"Should any dependencies be reordered?"_

## This skill ends here

The backlog is written and validated. Run the [done check](../create-backlog/SKILL.md#done-check) to verify completeness. The user confirms the backlog, then the planning agent commits to `dev` and hands off to the implementation agent.
