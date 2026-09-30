---
title: Foundational Principles
category: implementation
enforcement: none — human/agent-authored discipline, not mechanically gate-checked
version: 1.0.0
---

# Foundational Principles

Canonical statements: [rules.md § Foundational principles](../rules.md#foundational-principles).

## Eichhorst's Principle

Keep each skill/agent transmission short and independently verifiable. An LLM is a noisy channel: short, checked transmissions (compiler → tests → review) beat one long, unchecked one.

## Agentic Creation, Deterministic Validation

**Creation is agentic** — agents and humans write specs, code, architecture, tests, and ADRs. **Validation is deterministic** — mechanically triggered gates run scripts that check artifacts against predefined criteria. Agents create; gates validate. No agent self-validation, no trust-based checking. Tests run through Factory test gates, not bare agent commands. Git safety is enforced by `PreToolUse` hooks and `block-dangerous-git.sh`, not agent judgment. You can explicitly bypass client-side Git hooks with `--no-verify`; organization-wide enforcement requires server-side controls. This separation of concerns is the foundation of reliable AI-assisted output: agentic creation paired with mechanical validation produces artifacts you can ship.

## YAGNI

Build only what the specification requires, in the smallest verified step it allows. Anything built ahead of a verified requirement is unverified surface nobody asked for.

## Referenced from

- [rules.md § Foundational principles](../rules.md#foundational-principles)
