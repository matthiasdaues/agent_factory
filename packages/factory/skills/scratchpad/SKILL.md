---
name: scratchpad
description: Append a quick note to session-scratchpad.md, sectioned by date. Use when the user says "note this down:", "make a note of this:", or invokes "/scratchpad" or "/scratch".
category: utility
disable-model-invocation: true
---

# Scratchpad

Capture a short note verbatim into `session-scratchpad.md` at the project root — a running, date-sectioned scratch pad, not a formal artifact. Not `docs/CONTEXT.md`, not a finding, not an ADR — those have their own skills. This is for todos and ideas that don't belong anywhere else yet.

## Triggers

- "note this down: {text}"
- "make a note of this: {text}"
- `/scratchpad {text}`
- `/scratch {text}`

## Step 1 — Capture verbatim

Take the note text as-is — no rewriting, no summarizing, no correcting. This is a scratch pad, not an edited artifact.

## Step 2 — Pipe to the script

```bash
echo "{note text}" | factory/scripts/scratchpad
```

The script handles everything: creates the file if it doesn't exist, starts a new date section if the most recent one isn't today, appends the note as a bullet, and formats the file via `factory/scripts/mdformat` per [markdown-formatting.md](../../factory/rulebooks/conventions/markdown-formatting.md). Never construct the file/heading structure by hand, and never edit `session-scratchpad.md` directly — always go through the script, so the date-sectioning and formatting stay consistent.

**Completion**: script exits 0, note appended.
