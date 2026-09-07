---
title: CONTEXT.md Format
category: domain-modeling
enforcement: domain-modeling skill (written by), most other skills (read by) — not mechanically gate-checked
version: 1.0.0
---

# CONTEXT.md Format

## Structure

Skeleton: [context.md template](../templates/context.md).

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS, not what it does.
- **Only project-specific terms.** General programming concepts (timeouts, error types, utility patterns) don't belong even if heavily used. Ask: unique to this context, or general programming? Only the former belongs.
- **Group under subheadings** when natural clusters emerge; a flat list is fine otherwise.

## Single vs multi-context repos

**Single context (most repos):** one `docs/arc42/CONTEXT.md`.

**Multiple contexts:** a `docs/arc42/CONTEXT-MAP.md` lists the contexts, where they live, and how they relate. Skeleton: [context-map.md template](../templates/context-map.md).

Infer the structure: `docs/arc42/CONTEXT-MAP.md` exists → read it for contexts; only `docs/arc42/CONTEXT.md` exists → single context; neither exists → create `docs/arc42/CONTEXT.md` lazily when the first term is resolved.

When multiple contexts exist, infer which one the current topic relates to; ask if unclear.

## Referenced from

- [domain-modeling § Domain awareness](../../skills/domain-modeling/SKILL.md#domain-awareness)
