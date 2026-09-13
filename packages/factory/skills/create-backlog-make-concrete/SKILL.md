---
name: make-concrete
description: "Incorporate grilling results into a backlog story: fill resolved contract decisions into their home sections, write concrete Required API Behavior, and prepare the story for slicing. Phase 6 of the create-backlog sequence."
category: planning
disable-model-invocation: false
---

# Create Backlog — Phase 6: Make Concrete

Take a grilled backlog story and make it concrete. Read the resolved answers in
the story's `## Resolve Before Implementation` section and work each answer into
its home section — Domain Rule, Outputs, Required Behavior, Acceptance Criteria,
or Constraints. The resolved blockquotes stay in place as the decision record.
When this skill finishes, the story is ready for slicing into implementation
stories.

The original story is a design record, not a dispatch unit. It carries the full
design context from planning and grilling. The implementation stories sliced from
it are what the dispatcher sends to developer agents.

This is Phase 6 of the
[create-backlog sequence](../create-backlog/SKILL.md#operational-sequence), after
the grilling session (Phase 5). Story format, composition rules, and quality gates
live in the [parent skill](../create-backlog/SKILL.md).

## Prerequisite

The story's `## Resolve Before Implementation` section has been grilled. Each
numbered question carries a resolved answer as a blockquote, or
deferral with rationale. If unresolved questions remain without deferral
rationale, do not proceed — send the story back to grilling.

## Procedure

### 1. Read the grilled story

Read the story file and its resolved questions. For each resolv
which body section it belongs in:

| Answer type                    | Home section           |
| ------------------------------ | ---------------------- |
| Entity lifecycle rule          | Domain Rule            |
| Field storage/transport format | Domain Rule or Outputs |
| Mutability boundary            | Domain Rule            |
| HTTP method, status code       | Required API Behavior  |
| DTO shape, field spec          | Required API Behavior  |
| Validation scope or timing     | Required API Behavior  |
| Rejection behavior             | Required API Behavior  |
| Cross-story side effect        | Outputs or Constraints |
| Computed vs. stored            | Outputs                |
| New must-not                   | Constraints            |
| New falsifiable invariant      | Acceptance Criteria    |

### 2. Write the concrete detail into home sections

For each resolved answer:

- Add the concrete detail to the appropriate section.
- Use the project's domain language, not the grilling's convers
- When a resolved answer is a new invariant, add a checkbox acceptance criterion.
- When a resolved answer narrows an existing criterion, sharpen

**Do not touch the Resolve Before Implementation section.** The
blockquotes stay as the decision record. They document what was decided and when.

**Required API Behavior.** If the story's Required Behavior section was empty or
optional before grilling, and the resolved answers include HTTP
codes, DTO shapes, validation rules, or rejection behavior, rename the section
to `Required API Behavior` and write the full contract:

- HTTP method and expected status code for each operation.
- Request and response field names and types.
- Field storage representation vs. API transport representation
- Which fields are mutable at each lifecycle state.
- Whether invalid input is saved, rejected, or both.
- Whether detail GET recomputes or returns stored state.
- What side effects must not happen.

Use concrete examples (JSON fragments, field specs with ranges
they reduce ambiguity. Do not add examples for ceremony.

**Domain Rule.** Add new bullet items for resolved lifecycle rules, mutability
boundaries, and format decisions. Keep the "Use this wording as
framing when the existing section uses it.

**Demo Scenario.** If the grilling surfaced a rejection or edge-case path that
the demo does not cover, add a demo step showing the rejection
stored state. Every lifecycle constraint the story enforces should be visible in
the demo.

**Deferred questions.** Move deferred questions (those with exp
rationale instead of a resolved answer) to `docs/spec/todo.md` per the
[todo format](../../rulebooks/conventions/todo-format.md). Reco
and deferral rationale. The deferred item stays in the Resolve Before
Implementation section with its deferral blockquote — it is not

### 3. Plain-language pass

Reread Goal, Domain Rule, Demo Scenario, Required API Behavior,
Criteria for understandability.

For every sentence, check:

- Could a developer unfamiliar with the grilling understand what to build?
- Does a domain term name a real project concept, or is it left
  architecture-speak from the planning phase?
- Is the sentence under 25 words? One idea per sentence?
- Active voice?

Rewrite sentences that fail. Preserve domain terms when they are important;
replace architectural jargon when plain language is clearer.

### 4. Quality gate

Run the Agent-Answerability Checks from
[create-backlog](../create-backlog/SKILL.md#agent-answerability-checks). Every
check must be answerable from the story alone.

Run the International Readability checks on Goal, Domain Rule,
Required API Behavior, Constraints, and Agent Stop Conditions.

A story that fails either gate is revised before it leaves this skill.

### 5. Format

Format the story via `factory/scripts/mdformat --number <path>` per
\[markdown-formatting.md\](../../rulebooks/conventions/markdown-f

## Output

The operationalised story file, in place. No new files created.

Present the story to the user. Ask:

- \_"Does the Required API Behavior match your intent from the g
- _"Any acceptance criteria missing?"_
- _"Ready to slice, or does anything need another pass?"_

## This skill ends here

The story is concrete — grilled, detailed, with a decision reco
for slicing into implementation stories (Phase 7). The original story is not
dispatched; it stays as the design record. When slicing is comp
original story's `status` to `closed`.
