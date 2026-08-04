---
title: Cache Hygiene
category: implementation
enforcement: workflow guidance
version: 1.0.0
---

# Cache Hygiene

## Bounded reads

Read a potentially large artifact through a bounded initial chunk. Request
further chunks only on demand when the current task requires them; do not load
the rest merely because it exists.

## Provider-qualified evidence

Treat cache behavior as measured provider evidence, qualified by the CLI and
provider that reported it. Do not infer a cache hit or miss from normalized
token estimates, another provider's behavior, or an absent native field.

## No restabilisation ritual

Do not add a prose-only cache-restabilisation turn after a large read. The
controlled evidence did not show that ritual improving cache behavior, so an
ordinary task continuation should follow the bounded read.

Cache-miss and early/late input signals are derived once at session end for
retrospective use. They are never a live token budget or session-control gate.
