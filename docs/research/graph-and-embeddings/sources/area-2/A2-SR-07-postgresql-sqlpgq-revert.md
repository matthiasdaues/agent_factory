# A2-SR-07: SQL/PGQ in PostgreSQL, commit and revert

```json
{
  "source_identity": "PostgreSQL commits 2f094e7ac691 'SQL Property Graph Queries (SQL/PGQ)' (2026-03-16) and b1f106c80cbe 'Revert SQL Property Graph Queries (SQL/PGQ)' (2026-09-07); pgsql-hackers message 'Re: PGQ catalog representation and pg_dump support' by Melanie Plageman, 2026-09-02, https://www.postgresql.org/message-id/CAAKRu_bEtjWYWhYxSo0o_t3DaZYRQd5PkC0abA0g9Mp4%2BovH0w%40mail.gmail.com",
  "author_or_issuing_body": "Peter Eisentraut and Ashutosh Bapat (authors of the feature); Peter Eisentraut (committer of the revert); Melanie Plageman for the PostgreSQL 19 Release Management Team",
  "publisher": "PostgreSQL Global Development Group (git repository, mirrored at github.com/postgres/postgres; pgsql-hackers archive)",
  "publication_date": "2026-09-07T19:00:55Z",
  "relevant_event_date": "2026-03-16",
  "source_family": "Primary: the PostgreSQL source repository and the developers' mailing list.",
  "precise_evidence_location": "Commit message of 2f094e7ac691; commit message of b1f106c80cbe; body of the mailing list message of 2026-09-02 19:29:06; file listings of src/backend/rewrite on master and REL_19_STABLE; tag REL_19_0",
  "method": "Commit records and a Release Management Team message read directly; branch contents checked through the GitHub mirror.",
  "limitations": "The mailing list thread has more than thirty messages; only the Release Management Team message was read in full. Whether SQL/PGQ will return in PostgreSQL 20 is not settled by any source found. The standards status of SQL/PGQ is out of scope for this area. The GitHub mirror was used, not git.postgresql.org itself.",
  "provenance": "Commits read with gh api repos/postgres/postgres/commits/<sha> and found with the GitHub commit search on 2026-11-18. Message downloaded with curl on 2026-11-18. Branch contents read with gh api repos/postgres/postgres/contents/src/backend/rewrite?ref=master and ref=REL_19_STABLE; tag REL_19_0 points to a commit of 2026-11-16."
}
```

## Evidence

- Commit 2f094e7ac691: "Implementation of SQL property graph queries, according to SQL/PGQ standard (ISO/IEC 9075-16:2023)."
- Commit 2f094e7ac691: "A property graph is a relation with a new relkind RELKIND_PROPGRAPH. It acts like a view in many ways. It is rewritten to a standard relational query in the rewriter."
- Release Management Team message of 2026-09-02: "The RMT has been spending time looking at the current state of PGQ given the release time, and we have some serious concerns about the number of design issues with either recently posted patches or without consensus on behavior."
- Same message: "These show up as phantom entries in information_schema views, can cause later legitimate alterations of the property graph to fail, and can render the graph undumpable/unrestorable."
- Same message: "As such, unless we are misunderstanding something about the discussion, we feel it would be better to revert this in 19."
- Commit b1f106c80cbe: "Revert SQL Property Graph Queries (SQL/PGQ)". The message lists 49 reverted commits, starting with 2f094e7ac69.
- On 2026-11-18, neither master nor REL_19_STABLE holds the file src/backend/rewrite/rewriteGraphTable.c, and the tag REL_19_0 exists.
- Note: the archive page removes some line breaks, so a few words run together in the raw text; the quotes above restore the spaces only.
- What the source shows: PostgreSQL had a SQL/PGQ implementation on its development branch from March to September 2026, and PostgreSQL 19 ships without it.
- What the source does not show: any vector feature in SQL/PGQ, or a date for a new attempt.
