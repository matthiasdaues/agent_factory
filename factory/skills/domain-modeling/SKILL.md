---
name: domain-modeling
description: Build and sharpen a project's domain model — challenge terminology, record architecture decisions, update docs/CONTEXT.md and docs/adr/ inline as decisions crystallise. Use when pinning down domain vocabulary or a ubiquitous language, recording an architectural decision, or when another skill needs to maintain the domain model.
category: utility
source: https://github.com/mattpocock/skills/
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. Merely *reading* `docs/CONTEXT.md` for vocabulary is not this skill; that's a one-line habit any skill can do. This skill is for *changing* the model, not just consuming it.

## Domain awareness

During codebase exploration, also look for existing documentation. See [context-format.md](../../rulebooks/conventions/context-format.md) for the single-context vs multi-context file layout. Create `docs/CONTEXT.md` and `docs/adr/` lazily — only when the first term or ADR is actually needed.

## During the session

### Challenge against the glossary

When a term conflicts with `docs/CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When a vague or overloaded term appears, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios that probe edge cases and force precision about the boundaries between concepts.

### Cross-reference with code

When someone states how something works, check whether the code agrees. If you find a contradiction, surface it: "The code cancels entire Orders, but partial cancellation was just described — which is right?"

### Update docs/CONTEXT.md inline

When a term is resolved, update `docs/CONTEXT.md` right there — don't batch. Use the format in [context-format.md](../../rulebooks/conventions/context-format.md). Format via `scripts/mdformat --number docs/CONTEXT.md` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

`docs/CONTEXT.md` is a glossary only — no implementation details, no spec content, no scratch notes.

### Offer ADRs sparingly

When a decision is hard to reverse, surprising without context, and the result of a real trade-off — all three — invoke `write-adr`. It owns the format; this skill carries no ADR-writing logic of its own.
