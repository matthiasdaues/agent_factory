# A1-SR-09: PostgreSQL release state and SQL/PGQ, commit and revert, 2026

```json
{
  "source_identity": "PostgreSQL commits 2f094e7ac691abc9d2fe0f4dcf0feac4a6ce1d9c 'SQL Property Graph Queries (SQL/PGQ)' (2026-03-16) and b1f106c80cbeb18d3a0219994d98a51a6eca8ede 'Revert SQL Property Graph Queries (SQL/PGQ)' (2026-09-07); branch contents of master and REL_19_STABLE; PostgreSQL versioning page https://www.postgresql.org/support/versioning/ and front page news of 2026-11-12",
  "author_or_issuing_body": "Peter Eisentraut and Ashutosh Bapat (feature); Peter Eisentraut (revert); PostgreSQL Global Development Group (versioning page and news)",
  "publisher": "PostgreSQL Global Development Group (git repository mirrored at github.com/postgres/postgres; postgresql.org)",
  "publication_date": "2026-09-07T19:00:55Z",
  "relevant_event_date": "2026-03-16",
  "source_family": "Primary: the PostgreSQL source repository and the project's own release pages. The same commits are recorded as context in the graph-and-embeddings survey, record A2-SR-07, which also quotes the Release Management Team message behind the revert.",
  "precise_evidence_location": "Commit message of 2f094e7ac691; commit message of b1f106c80cbe; directory listing of src/backend/rewrite on master and REL_19_STABLE; tag list; versioning page, first paragraph and release table; front page news item of 2026-11-12",
  "method": "Commit records and branch contents read through the GitHub API; release pages downloaded.",
  "limitations": "The mailing list discussion of the revert was not re-read; A2-SR-07 of the graph-and-embeddings survey holds it. A tag REL_19_0 exists in the repository on 2026-11-18, but postgresql.org still announces 19 as release candidate 2 and marks 18 as current; the record treats 19.0 as not yet announced. No source gives a date for a new SQL/PGQ attempt.",
  "provenance": "Commits read with gh api repos/postgres/postgres/commits/<sha> on 2026-11-18. Branch listings read with gh api repos/postgres/postgres/contents/src/backend/rewrite?ref=master and ref=REL_19_STABLE; no file name contains 'graph'. Master commits since 2026-09-08 searched for 'PGQ' and 'property graph' with no match. Versioning page and front page downloaded with curl on 2026-11-18."
}
```

## Evidence

- Commit 2f094e7ac691: "Implementation of SQL property graph queries, according to SQL/PGQ standard (ISO/IEC 9075-16:2023)."
- Commit 2f094e7ac691: "A property graph is a relation with a new relkind RELKIND_PROPGRAPH. It acts like a view in many ways. It is rewritten to a standard relational query in the rewriter."
- Commit b1f106c80cbe: "Revert SQL Property Graph Queries (SQL/PGQ)"
- Versioning page: "The PostgreSQL Global Development Group releases a new major version containing new features about once a year."
- Versioning page, release table: 18, current minor 18.7, first release September 25, 2025, final release November 14, 2030.
- Front page: "November 12, 2026: PostgreSQL 18.7, 17.12, 16.16, 15.20, 14.25, and 19 RC 2 Released!"
- Statement S11: the March 2026 commit declared a property graph over existing tables, like a view, so no data moved. That supports the condition of S11. But the feature was reverted, and on 2026-11-18 neither master nor REL_19_STABLE holds it. S11 stays conditional on a release that no source schedules.
- What the source shows: how PostgreSQL's SQL/PGQ worked while it existed, its removal from release 19, and the release rhythm of PostgreSQL.
- What the source does not show: whether a later SQL/PGQ would keep the view-like design.
