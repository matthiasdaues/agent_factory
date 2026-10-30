---
title: "Story: Named Views"
---

# Story: Named Views

**Goal.** Find out whether DBML and LinkML can render one named subset of the
model to its own SVG, the way `structurizr export-svg` renders each view of
`architecture.dsl`.

**Why this is a comparison case.** Under the criteria of the
architecture.dsl pattern, the views cell decides between DBML and LinkML.
DBML has a `DiagramView` construct in the language, but no tool in the DBML
story drew it. LinkML has no view construct, but `gen-erdiagram` takes a list
of classes.

**What to build.** One view, `runtime`, with `task_instance`, `attempt`, and
`outbox`, in both languages. Run every tool through `docker run --rm`.

**Definition of Done.**

1. The plain renderer runs on the DBML model with the view, and the exit code
   is recorded.
2. A thin wrapper renders the DBML view to SVG, if the plain renderer cannot.
3. `gen-erdiagram` renders the same three LinkML classes, and `mmdc` turns
   the result into SVG.
4. The note compares what each SVG shows.

**Output.** The comparison note [notes/views.md](../notes/views.md).
