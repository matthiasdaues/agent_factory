---
title: Foundational Principles
category: implementation
enforcement: none — human/agent-authored discipline, not mechanically gate-checked
version: 1.0.0
---

# Foundational Principles

Canonical statements: [rules.md § Foundational principles](../rules.md#foundational-principles).

## Plain Prose (Strunk & White / Wolf Schneider)

Write short, precise prose. English: plain English after Strunk & White's *The Elements of Style*. German: *Gutes Deutsch* after Wolf Schneider. Cut every word that doesn't carry weight. State the claim, then the qualification — not the reverse. This applies to deliverable prose — specs, ADRs, reviews, READMEs — not to chat or code comments, which follow their own conventions.

Apply this from the first draft, not as a later cleanup pass. A second pass whose only job is cutting padding out of compound, em-dash-linked sentences is a sign the first draft skipped this principle, not the normal workflow — writing to the rule once costs less than writing loosely and editing down.

## Eichhorst's Principle

Keep each skill/agent transmission short and independently verifiable. An LLM is a noisy channel: short, checked transmissions (compiler → tests → review) beat one long, unchecked one.

## Agentic Creation, Deterministic Validation

**Creation is agentic** — agents and humans write specs, code, architecture, tests, and ADRs. **Validation is deterministic** — mechanically triggered gates run scripts that check artifacts against predefined, state-dependent criteria. Agents create; gates validate. No agent self-validation, no trust-based checking. Tests run through Factory test gates, not bare agent commands. Commits block via `transition-lint` pre-commit hooks, not agent restraint. Git safety is enforced by `PreToolUse` hooks, not agent judgment. Human operators can explicitly bypass client-side Git hooks with `--no-verify`; organization-wide enforcement requires server-side controls. This separation of concerns is the foundation of reliable AI-assisted output: agentic creation paired with mechanical validation produces artifacts you can ship.

## YAGNI

Build only what the specification requires, in the smallest verified step it allows. Anything built ahead of a verified requirement is unverified surface nobody asked for.

## Referenced from

- [rules.md § Foundational principles](../rules.md#foundational-principles)
