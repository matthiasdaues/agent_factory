---
name: domain-modeling
description: Build and sharpen a project's domain model — challenge terminology, record settled terms and architecture decisions in docs/adr/ inline as decisions crystallise. A settled term goes into docs/spec/glossary.md when the domain-modeling agent runs the skill, and into docs/spec/work/term-candidates.md otherwise. Use when pinning down domain vocabulary or a ubiquitous language, recording an architectural decision, or when another skill needs to maintain the domain model.
category: utility
source: https://github.com/mattpocock/skills/
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. Merely *reading* `docs/spec/glossary.md` for vocabulary is not this skill; that's a one-line habit any skill can do. This skill is for *changing* the model, not just consuming it.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

## Domain awareness

During codebase exploration, also look for existing documentation. See [context-format.md](../../rulebooks/conventions/context-format.md) for the glossary format and for the domain concerns in `docs/agent-context.md` that name the bounded contexts. Create `docs/adr/` lazily, only when the first ADR is needed. With `--write-glossary`, the skill also creates `docs/spec/glossary.md` on every run, even when the file holds no term yet.

Once you identify the repository as multi-context, prompt the user immediately with a single checklist covering all artifact classes the split affects: docs/, backlog/, the domain concerns in `docs/agent-context.md`, the sections of `docs/spec/glossary.md`, README, and `docs/adr/`. Do this in one pass rather than surfacing each artifact class as a separate follow-up round. Refer to [context-format.md](../../rulebooks/conventions/context-format.md) for the file layout structure.

## Where a settled term goes

The glossary has one producer, the domain-modeling agent. Only the domain-modeling agent passes `--write-glossary`. So the argument decides where a term goes once the stakeholder settles it in the session:

- **With `--write-glossary`:** write the term into `docs/spec/glossary.md`, as [Update docs/spec/glossary.md inline](#update-docsspecglossarymd-inline) describes.
- **Without the argument:** write the term right there as a row of `docs/spec/work/term-candidates.md` with status `confirmed`. Put the settled definition into Proposed definition, the scope-map area into Domain area, and the session into Source, such as `grilling on docs/proposals/payouts.md`. When the term already has a row, update that row. `docs/spec/glossary.md` stays unchanged.

The work file holds one table with the columns Term, Domain area, Source, Proposed definition, Status, and Note. When the file is missing, create it with that table header. The domain-modeling agent later moves each `confirmed` row into the glossary without asking the stakeholder again.

## During the session

### Challenge against the glossary

When a term conflicts with `docs/spec/glossary.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When a vague or overloaded term appears, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios that probe edge cases and force precision about the boundaries between concepts.

### Cross-reference with code

When someone states how something works, check whether the code agrees. If you find a contradiction, surface it: "The code cancels entire Orders, but partial cancellation was just described — which is right?"

### Update docs/spec/glossary.md inline

Only with `--write-glossary`: when a term is settled, write it to `docs/spec/glossary.md` right there — don't batch. The term goes in as one table row with the columns Term, Definition, and Avoid, in the section of its context. Use the [glossary template](../../rulebooks/templates/glossary.md).

- Find the section named after the term's context. The domain concerns in `docs/agent-context.md` name the contexts; ask if the context is unclear.
- When the section is missing, the skill creates the section with its table header.
- When the term already has a row in that section, the skill updates the existing row. It never adds a second row for the same term in one section.
- Format via `scripts/mdformat --number docs/spec/glossary.md` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

`docs/spec/glossary.md` holds terms only — no implementation details, no spec content, no scratch notes.

### State machine step

The domain-modeling agent runs this step for each entity with a lifecycle. Write the state machine in `docs/spec/state-machines.md` per [state-machine-notation.md](../../rulebooks/conventions/state-machine-notation.md), using the [state machine template](../../rulebooks/templates/state-machine.md).

- Write the pseudocode first. Derive the Mermaid `stateDiagram-v2` diagram from it, one edge per `ChangeState(X)`.
- Run `.agent-factory/factory/scripts/statemachine-lint docs/spec/state-machines.md`. Fix the pseudocode or the diagram until the check passes.
- When no entity has a lifecycle, write no `state-machines.md`.

### Schema step

The domain-modeling agent runs this step for each payload column with inner structure in `docs/spec/entity-model.md`, such as a JSON column.

- Write one JSON Schema file per column: `docs/spec/schemas/<entity>-<column>.json`, in lowercase kebab case.
- Link the schema file from the column's row in the entity model.
- When no column has inner structure, write no `docs/spec/schemas/` folder.

### Offer ADRs sparingly

When a decision is hard to reverse, surprising without context, and the result of a real trade-off — all three — invoke `write-adr`. It owns the format; this skill carries no ADR-writing logic of its own.
