# Research Brief: Postgres And qmd

This brief is the readable copy of [research-brief.json](research-brief.json).
The JSON file is authoritative and passes `research-brief.schema.json`.

The survey checks the proposed store sketch in the
[design position](../knowledge-graph-with-provenance/design-position.md#the-proposed-store)
against the documentation, and compares it with qmd, a local search tool for
markdown documents. It follows the
[graph-and-embeddings](../graph-and-embeddings/survey-report.md) survey and uses
the same simplicity facts.

The survey covers two areas:

1. Plain PostgreSQL with pgvector as a graph and vector store: recursive
   queries, triggers, append-only tables, pgvector under transactions,
   filtered search, `LISTEN` and `NOTIFY`, the outbox pattern, and the client
   layer.
2. qmd: what it is, how it stores and searches, and what it would need to hold
   edges, decisions, and append-only history.

As before, the survey reports what sources document. A verdict that a concept
survived refutation belongs to a later falsification study.
