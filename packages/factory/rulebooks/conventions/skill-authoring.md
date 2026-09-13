---
title: Skill Authoring Principles
version: 1.0.0
---

# Skill Authoring Principles

Design principles for writing and maintaining Factory skills. Skills that
follow these principles stay small, stay useful across model tiers, and
resist the token bloat this convention was created to prevent.

Apply the [writing quality gates](writing-quality-gates.md).

## 1. Declarative over prescriptive

State the goal and constraints. Let the model determine the steps.

Prescribe only what the model would not do unprompted: forbidden phrasings,
routing tables, file-path conventions, output contracts. If you are writing
"Step 1 … Step 2 … Step 3" for reasoning the model already performs, those
steps waste tokens.

**Positive exemplar — `crap-score` (Change Risk Anti-Patterns).**
States the formula, threshold, CLI interface, and report contract. Never
tells the model *how* to reason about the results. Every line earns its
tokens.

**Anti-pattern: prescribed reasoning chains.**
A skill that scripts "Step 1: locate the concept, Step 2: gauge the
audience, Step 3: explain, Step 4: check completeness" is narrating what
any frontier model already does. Persona names and self-check reminders
add atmosphere with no behavioral effect.

## 2. Delegate to schemas and reference files

Define output contracts, templates, and checklists by reference — not
inline. Heavy content lives in separate files under `rulebooks/references/`
or `rulebooks/templates/` and is loaded on demand.

A skill that inlines a 40-line template or a 15-item checklist forces
every invocation to load that content. A `Read:` reference lets the model
load the content once, when the content matters.

**Positive exemplar — `qa-strategy-from-spec`.**
References `rulebooks/templates/qa-strategy.md` for the output skeleton
and `rulebooks/references/qa-strategy-checklist.md` for the quality check.
The skill itself stays focused on procedure and judgment.

**Anti-pattern: inlined heavy content.**
A skill that embeds a 90-line output template and a 15-item quality
checklist directly in its body forces every invocation to load ~2,000
tokens of content the model reads once and never revisits.

## 3. Prescribe only the non-obvious

A constraint the model already follows wastes tokens. A constraint the
model would violate without instruction earns its tokens.

Test each line against: "Would the model do something wrong if this line
were absent?" If the answer is no, the line wastes tokens.

Examples of constraints that earn their tokens:

- File-path routing (`backlog/epics.md`, not `docs/epics.md`)
- Forbidden output patterns ("never emit a full test suite in the probe")
- Domain-specific decision tables (risk-level → test-layer mapping)
- Cross-reference mandates ("trace every boundary case to a Scenario or
  a named gap")

Examples of constraints that waste tokens:

- "Write clearly and concisely" (model default)
- "Check your work for completeness" (model default)
- "Consider the audience" (model default)
- Active-voice and grammar instructions (covered by writing-quality-gates)

**Positive exemplar — `testability-probe`.**
Every constraint is project-specific: which file to write, what sections
to add, what ownership table shape to produce, what *not* to include
(no failure scenarios, no risk classifications). Zero generic advice.

**Anti-pattern: generic advice burying the real constraints.**
A skill devotes ~250 tokens to example outputs, timing heuristics, and
style tables. The two constraints that earn their tokens — "target the
process, never the user" and "keep it to two sentences" — sit buried
among them.

## 4. Tool wrappers, not reasoning replacements

When a skill wraps a deterministic script, document how to call the tool
and how to interpret its output. Do not replace or guide the model's
reasoning about the results.

The script owns the computation. The model owns the judgment. The skill
connects the two.

**Positive exemplar — `crap-score`.**
Documents the CLI, its arguments, its JSON report contract, and its
threshold semantics. Says nothing about what the model should *think*
when a function fails. The model already knows how to reason about
complexity and coverage.

**Anti-pattern: reasoning scripts around tool output.**
A skill wraps a linter and then prescribes how to categorize findings,
when to suppress, and how to prioritize. That reasoning is the model's
job. The skill should state the suppression policy (if one exists) and
stop.

## Applying these principles

When writing a new skill or reviewing an existing one:

1. Delete every line that describes reasoning the model already performs.
2. Extract any inline template, checklist, or example block longer than
   ~20 lines into a reference or template file.
3. Verify that every surviving line fails the removal test: "Would the
   model produce a wrong result if this line were absent?"
4. If the skill wraps a script, confirm that the skill documents the
   interface and the model supplies the judgment — not the reverse.
