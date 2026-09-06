---
title: Markdown Formatting on Write
category: implementation
enforcement: pre-commit mdformat hook (backstop) + this rule (write-time, not deferred)
version: 1.0.0
---

# Markdown Formatting on Write

## Rule

Canonical statement: [rules.md § Markdown formatting](../rules.md#markdown-formatting).

**Why not just rely on the hook**: pre-commit only fires at commit time. A file can sit unformatted through several editing/review passes first, so a mid-session read of it — by a reviewer, by the author themselves, by the user — never shows a raggedly-formatted draft.

## Scope

Applies whenever a skill's own instructions include a "Save as ..." / "Write ..." step producing a `.md` file — reports, findings, specs, ADRs, backlog stories, docs/CONTEXT.md, arc42 chapters. Does not apply to skills that only *read* markdown (a review skill's input-reading steps, `spec-lint`/`arch-lint` invocations) — write side only.

## References

- Used by: every prose-driven skill listed in `INDEX.yaml` that writes a markdown artifact — each cites this rule at its own write step rather than restating the instruction.
- `scratchpad` is the one exception to "cited, not restated": it's an executable script, not agent-followed prose, so the rule is compiled directly into `factory/scripts/scratchpad` (calls `factory/scripts/mdformat` after every append) rather than cited in text.
