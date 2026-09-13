---
title: Cockburn Reasoning
version: 1.0.0
---

# Cockburn Reasoning

Alistair Cockburn's use-case reasoning sequence for deriving structured
specifications from unstructured requirements.

## Sequence

1. **Identify actors.** Enumerate who interacts with the feature: users,
   systems, external services.
2. **Goal-level test.** For each actor, ask: does the actor achieve a
   satisfying outcome when this goal completes? If yes, the goal is a
   **User Goal**. If no, it is a **Subfunction** — include only when
   reused across multiple use cases.
3. **Build the actor-goal matrix.** One row per actor-goal pair.
4. **Derive scenarios per goal.** Main success path first, then
   extensions, then failure modes.

## Application in this factory

The `derive-feature` skill uses this sequence as an internal working
discipline to produce Rule-per-actor-goal Gherkin `.feature` files. The
matrix is held in working context and appears in the gaps report as
completeness evidence — it is not committed as a separate artifact.
