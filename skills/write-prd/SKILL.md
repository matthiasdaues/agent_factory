---
name: write-prd
description: Synthesise a Product Requirements Document from clarified requirements.
disable-model-invocation: true
---

# Write PRD

Formalise the clarified requirements into a PRD. Do not interview the user — synthesise what the conversation has already established. Reference `docs/spec/todos.md` for pending decisions.

Read `CONTEXT.md` if it exists — use the project's domain vocabulary throughout.

## Step 1 — Draft the PRD

Write `docs/spec/prd.md` covering:

1. **Problem Statement** — the problem from the user's perspective
2. **Goals and Non-Goals** — what this project achieves and what it explicitly excludes
3. **Target Users** — who will use the system and what they need from it
4. **Functional Requirements** — what the system does, grouped by capability
5. **Non-Functional Requirements** — performance, security, reliability, operability
6. **Constraints and Assumptions** — technology, timeline, organisational, regulatory
7. **Open Questions** — each referencing an entry in `docs/spec/todos.md`

**Completion**: `docs/spec/prd.md` exists with all seven sections filled — no placeholder text, no silently assumed decisions.

## Step 2 — Verify completeness

Check the PRD against the conversation history — confirm every topic discussed during clarification appears. List and add any omissions.

Ask: _"Does this PRD capture everything we discussed? Anything missing or misrepresented?"_

**Completion**: the user confirms the PRD or corrections are applied.

## Completion criterion

A colleague unfamiliar with the project can read `docs/spec/prd.md` and understand what needs to be built, what is out of scope, and what is still undecided.
