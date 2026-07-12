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

## Eichhorst's Principle

Keep each skill/agent transmission short and independently verifiable. An LLM is a noisy channel: short, checked transmissions (compiler → tests → review) beat one long, unchecked one.

## Agentic Creation, Deterministic Validation

**Creation is agentic** — agents and humans write specs, code, architecture, tests, and ADRs. **Validation is deterministic** — unavoidable hooks trigger scripts that check artifacts against predefined, state-dependent criteria. Agents create; hooks validate. No agent self-validation, no trust-based checking. Tests run via `script_exit_zero` gate conditions, not agent commands. Commits block via `transition-lint` pre-commit hooks, not agent restraint. Git safety enforced by `PreToolUse` hooks, not agent judgment. This separation of concerns is the foundation of reliable AI-assisted output: agentic creation paired with mechanical validation produces artifacts you can ship.

## YAGNI

Build only what the specification requires, in the smallest verified step it allows. Anything built ahead of a verified requirement is unverified surface nobody asked for.

## Referenced from

- [rules.md § Foundational principles](../rules.md#foundational-principles)
