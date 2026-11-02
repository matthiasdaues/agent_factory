---
title: Glossary and Domain Concern Format
category: domain-modeling
enforcement: domain-modeling skill (written by), most other skills (read by) — not mechanically gate-checked
version: 2.0.0
---

# Glossary and Domain Concern Format

A project keeps its domain vocabulary in two places. `docs/spec/glossary.md` holds the terms. The domain concerns of `docs/agent-context.md` say which bounded contexts exist and where each one's files live.

## Structure

`docs/spec/glossary.md` is a core file. Skeleton: [glossary.md template](../templates/glossary.md).

- One `##` section per bounded context or per topic, such as acronyms.
- One table per section, with the columns Term, Definition, and Avoid, in this order.
- A term appears at most once inside one section. A settled term updates its existing row; it never adds a second one. A term may appear in more than one section.
- Avoid lists the words not to use for the term. It may be empty.

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others under Avoid.
- **Keep definitions tight.** One or two sentences max. Define what it IS, not what it does.
- **Only project-specific terms.** General programming concepts (timeouts, error types, utility patterns) don't belong even if heavily used. Ask: unique to this context, or general programming? Only the former belongs.
- **No other content.** The glossary holds terms only — no implementation details, no spec content, no scratch notes.

## Bounded contexts

Which bounded contexts exist is a routing fact. `docs/agent-context.md` holds it: each bounded context is one domain concern under `## Domain concerns`, with its description and its `Read:` paths. A domain concern routes to `docs/spec/glossary.md` for its terms.

The glossary section of a context carries the same name as its domain concern. A project with one context needs no domain concern for it; its terms go into one section.

When the current topic belongs to one of several contexts, infer which one from the domain concerns; ask if unclear. When `docs/spec/glossary.md` does not exist, create it when the first term is settled.

## Referenced from

- [domain-modeling § Domain awareness](../../skills/domain-modeling/SKILL.md#domain-awareness)
