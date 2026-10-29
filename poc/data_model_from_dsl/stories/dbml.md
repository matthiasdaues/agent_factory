---
title: "Story: DBML"
---

# Story: DBML

**Goal.** Find out whether DBML can hold the [acid slice](../acid-slice.md),
check it, render it, and compare it with Gigacron's live schema.

**Why this is a candidate.** DBML expresses the most constructs of any
candidate in the survey and has a named-view construct, `DiagramView`. The
survey read the `dbml2sql` source and found no non-zero exit code
([survey-report.md](../survey-report.md)).

**What to build.** The slice in DBML, three broken models, an SVG, and the
comparison with the live schema. Run every tool through `docker run --rm`.

**Definition of Done.** The ten items of the
[proposal's Definition of Done](../proposal-data-model-dsl-technical-poc.md#per-story-definition-of-done).

**Output.** The comparison note [notes/dbml.md](../notes/dbml.md).
