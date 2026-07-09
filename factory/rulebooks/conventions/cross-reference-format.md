---
title: Cross-Reference Format
category: implementation
enforcement: none — human/agent-authored convention, not mechanically gate-checked
version: 1.0.0
---

# Cross-Reference Format

## Rule

Canonical statement: [rules.md § Cross-references](../rules.md#cross-references).

Every reference from one artifact to another — ADR, finding, todo entry, rulebook, convention, skill, agent, spec document — is a full markdown link: `[label](relative/path.md#anchor)`. Never a bare ID (`ADR-0001`), a code span (`` `docs/spec/todo.md#T-0001` ``), or a parenthetical citation with no href.

## Anchor to the section, not just the file

Where the target artifact has distinct sections or entries — a heading, a `## T-NNNN` todo entry, an ADR's `## Consequences` — the link's anchor MUST point at that section, not just the top of the file. Land the reader exactly where the cited content is; don't make them scroll to find it. Only omit the anchor when the target genuinely has no internal structure to point at (a single-purpose file with one subject throughout).

## Scope

Applies to prose/body content. Does **not** apply to structured frontmatter fields (`traces: [NFR-01]`, `id: SPEC-0001`) — those are data, not rendered markdown, and a link there would be meaningless.

## Examples

Wrong: `See the QA Agent for how findings hand off downstream.`

Right: `See the [QA Agent § Handoff](../../agents/qa-agent.md#handoff) for how findings hand off downstream.`

Wrong: `Tracked in docs/spec/todo.md#T-0001.`

Right: `Tracked in [T-0001](../../../docs/spec/todo.md#t-0001-cursor-mdc-adapter-for-configagentsmd).`

## Why

A bare ID or file path forces the reader to go find the file themselves. A link is one click to the same information — cheap to write, meaningfully better to read.
