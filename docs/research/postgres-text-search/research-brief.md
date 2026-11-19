# Research Brief: Postgres Text Search

This brief is the readable copy of [research-brief.json](research-brief.json).
The JSON file is authoritative and passes `research-brief.schema.json`.

The survey fills the gap the [postgres-and-qmd](../postgres-and-qmd/survey-report.md)
survey found: the store sketch in the
[design position](../knowledge-graph-with-provenance/design-position.md#the-proposed-store)
has no answer for keyword queries or ranking.

The survey covers two areas:

1. Built-in and contrib features: `pg_trgm`, `fuzzystrmatch`, `unaccent`, and
   full-text search with German and English configurations.
2. Ranking extensions such as BM25 for PostgreSQL, and how keyword and vector
   results combine in one SQL statement.

As before, the survey reports what sources document. A verdict that a concept
survived refutation belongs to a later falsification study.
