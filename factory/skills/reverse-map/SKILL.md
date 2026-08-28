---
name: reverse-map
description: Forensic scope-map population from code, tests, and unstructured sources. Sweeps tests first as primary evidence, then code entry points, then accepts additional sources. Presents results in batches by domain area for stakeholder confirmation. Writes docs/spec/scope-map.md and seeds docs/CONTEXT.md.
category: requirements
---

# Reverse-Map

Build `docs/spec/scope-map.md` from whatever sources exist — code, tests, docs, wiki pages, API specs, or stakeholder knowledge. The skill replaces the need for `derive-spec` artifacts before the first scope map.

## How the user experiences it

Open with plain language:

> "I'm going to look through your codebase to understand what this system does. I'll start with tests and code, then you can point me at anything else — docs, wiki pages, API specs, whatever you have. I'll show you what I find as I go."

Present results in short batches by domain area. After each batch:

> "Does this match what you know?"

The user confirms, corrects, or adds missing behaviors. The skill incorporates corrections and moves to the next domain area.

After sweeping code and tests:

> "That's what I found in the code. Got anything else — wiki pages, API docs, a README someone wrote last year? I can cross-check."

The user feeds additional sources or says "that's enough." The skill writes the scope map and summarises:

> "Here's your inventory — N behaviors, M backed by tests, K in code only, J from docs I couldn't match to code. You can start building from here. The inventory grows as you add features."

## Order of operations

### Step 1 — Find the tests

Tests are the map someone already drew. Read test files as the highest-confidence evidence.

- Match test function names to behavioral claims.
- A behavioral claim is one test function asserting one observable outcome.
- Record each finding with confidence "verified" (passing tests) or "flagged" (failing or skipped tests).

### Step 2 — Find the entry points

HTTP routes, CLI commands, queue consumers, cron jobs. These are the system's external surface.

- Record each finding with confidence "high."
- Match entry points to test coverage where possible — an entry point with a matching test upgrades to "verified."

### Step 3 — Triangulate

Match tests to entry points to docs. The truth is in the overlap; contradictions are the most valuable findings.

- Infer domain areas from top-level module or package boundaries.
- Confirm domain-area grouping with the stakeholder before presenting results.

### Step 4 — Present in batches

Group results by domain area. Each batch shows:

- The behavior (one sentence)
- Test count and implementing code paths
- Discrepancies surfaced as questions, not findings

The stakeholder confirms, corrects, or adds missing behaviors after each batch.

### Step 5 — Accept additional sources

Offer to accept additional sources: wiki pages, API specs, README files, Postman collections, Jira exports, or verbal stakeholder knowledge.

- Cross-check additional sources against existing findings.
- Record the source type and confidence level for each new finding.

### Step 6 — Write the scope map

The stakeholder says "that's enough." Write `docs/spec/scope-map.md` in the 5-column format:

| Rule | Status | Confidence | Sources | Feature Link |
| ---- | ------ | ---------- | ------- | ------------ |

- Rows backed by passing tests have confidence "verified."
- Rows from docs alone have confidence "claimed."
- The Sources column names the specific test files, code files, or documents that evidence the rule.
- Feature Link is left empty — filled later by the reconciliation-agent when code is implemented.
- Status is "implemented" for all rows (the code exists).

Summarise the inventory count at the end.

## Seed docs/CONTEXT.md

During the code sweep (Steps 1-3), extract domain vocabulary from type names, class names, and module names. Write these to `docs/CONTEXT.md` using the [CONTEXT.md template](../../rulebooks/templates/context.md). This seed is the early form of arc42 chapter 12 (Glossary).

## Evidence hierarchy

The confidence level for each scope-map row follows this hierarchy:

| Source type                      | Confidence  | Why                                                    |
| -------------------------------- | ----------- | ------------------------------------------------------ |
| Passing test                     | verified    | Mechanically proven behavioral claim                   |
| Failing or skipped test          | flagged     | Documents intent, known broken or deferred             |
| Code entry point                 | high        | Exists and executes, but not test-verified             |
| Test fixture or factory          | medium-high | Reveals entity model and relationships                 |
| API spec (OpenAPI, Postman)      | medium      | Declared contract, may not match code                  |
| Repo docs (README, comments)     | medium-low  | Close to code, but often stale                         |
| External docs (Confluence, wiki) | low         | Furthest from code, most likely to drift               |
| Stakeholder verbal claim         | lowest      | Tribal knowledge, unfindable elsewhere                 |
| Document-only (no code match)    | claimed     | Asserted in documentation, not verifiable against code |

## Boundaries

- The skill reads code and presents information to the stakeholder. It writes only `docs/spec/scope-map.md` and `docs/CONTEXT.md`.
- Discrepancies are surfaced as questions to the stakeholder, not filed as findings.
- The stakeholder controls depth — "that's enough" is always valid.
- The skill does not modify code, tests, or any implementation artifact.

## UX principles

- Progressive results batched by domain — not one giant list at the end.
- Plain language throughout — no "populating scope-map rows from test evidence."
- The user controls depth.
- Additional sources are offered, not required.
- The output is readable in two minutes.
