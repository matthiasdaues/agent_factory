---
title: "Story: Atlas HCL"
---

# Story: Atlas HCL

**Goal.** Find out whether Atlas HCL can hold the [acid slice](../acid-slice.md),
check it, render it, and compare it with Gigacron's live schema.

**Why this is a candidate.** Atlas validates a model by applying it to a real
database and has a first-party `schema diff`. The survey could not settle
whether validation needs a live database and which features need a paid
licence ([survey-report.md](../survey-report.md)).

**What to build.** The slice in HCL, three broken models, an SVG, and the
comparison with the live schema. Run every tool through `docker run --rm`.

**Definition of Done.** The ten items of the
[proposal's Definition of Done](../proposal-data-model-dsl-technical-poc.md#per-story-definition-of-done).

**Output.** The comparison note [notes/atlas.md](../notes/atlas.md).
