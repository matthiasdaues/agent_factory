---
title: "Story: Mermaid erDiagram"
---

# Story: Mermaid erDiagram

**Goal.** Find out whether Mermaid erDiagram can hold the [acid slice](../acid-slice.md),
check it, render it, and compare it with Gigacron's live schema.

**Why this is a candidate.** Gigacron's model is a Mermaid `erDiagram` today.
The baseline runs on the same slice as the challengers, so "better than what
we have" becomes a measured result ([survey-report.md](../survey-report.md)).

**What to build.** The slice as Mermaid, copied from the model, three broken models, an SVG, and the
comparison with the live schema. Run every tool through `docker run --rm`.

**Definition of Done.** The ten items of the
[proposal's Definition of Done](../proposal-data-model-dsl-technical-poc.md#per-story-definition-of-done).

**Output.** The comparison note [notes/mermaid.md](../notes/mermaid.md).
