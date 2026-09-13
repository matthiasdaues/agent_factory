---
name: explain-concept
description: Look up a Factory concept and explain it. Knows what exists and what is missing.
category: utility
version: 1.1.0
---

# Explain Concept

Explain a Factory concept at the right depth for the person asking.

## Search path

Search for the concept in this order:

1. `factory/docs/factory-guide.md` — the canonical guide.
2. `factory/INDEX.yaml` — index of all agents, skills, playbooks, and
   rulebooks.
3. `factory/rulebooks/rules.md` and convention files under
   `factory/rulebooks/conventions/`.
4. `factory/README.md` and other top-level factory documentation.

If the concept does not exist in any source, say so. Offer the closest
related concept that does exist and the shape of what is missing.

## Boundaries

- Explain and curate. Do not create new skills, agents, or documents.
- Redirect "Should we have X?" to `draft-proposal` or VIRGIL.
