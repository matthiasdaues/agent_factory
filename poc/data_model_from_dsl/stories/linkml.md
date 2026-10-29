---
title: "Story: LinkML"
---

# Story: LinkML

**Goal.** Find out whether LinkML can hold the [acid slice](../acid-slice.md),
check it, render it, and compare it with Gigacron's live schema.

**Why this is a candidate.** The factory's T-0006 names LinkML. It is the only
candidate with first-party Pydantic and SQLAlchemy generators. The survey could
not confirm that composite keys, JSON columns, and CHECK constraints survive
generation ([survey-report.md](../survey-report.md)).

**What to build.** The slice as a LinkML schema, three broken models, an SVG, and the
comparison with the live schema. Run every tool through `docker run --rm`.

**Definition of Done.** The ten items of the
[proposal's Definition of Done](../proposal-data-model-dsl-technical-poc.md#per-story-definition-of-done).

**Output.** The comparison note [notes/linkml.md](../notes/linkml.md).
