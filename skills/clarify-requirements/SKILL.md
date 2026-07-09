---
name: clarify-requirements
description: Selects and runs the right requirements-clarification interview — Socratic (inline), grill-me (greenfield), or grill-with-docs (brownfield).
disable-model-invocation: true
---

# Clarify Requirements

Resolve ambiguity through an adversarial interview. This skill is a **branch selector** — pick the style, then run it.

## Select the branch

| Context                                   | Branch              | Action                                                       |
| ----------------------------------------- | ------------------- | ------------------------------------------------------------ |
| Small scope or quick pass                 | **Socratic**        | Run inline (below)                                           |
| Greenfield — no existing docs             | **Grill**           | Delegate to [`grill-me`](../grill-me/SKILL.md)               |
| Brownfield — existing `CONTEXT.md` / ADRs | **Grill with Docs** | Delegate to [`grill-with-docs`](../grill-with-docs/SKILL.md) |

If unsure: no `CONTEXT.md` / `docs/adr/` → `grill-me`; present → `grill-with-docs`. Announce the branch before starting.

## Branch: Socratic (inline)

Use the **Socratic Method** with **MECE**. Ask at most 3 questions at a time. Keep asking until no obvious gaps remain.

## Rules (all branches)

- Collect every open item in `docs/spec/todos.md`.
- Match `CONTEXT.md` domain vocabulary.
- Never accept "it should just work" — demand specifics.
- Every question gets a recommended answer, even lightweight ones.
