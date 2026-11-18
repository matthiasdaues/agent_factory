# A1-SR-07: PostgreSQL 18 manual on MVCC, isolation, the index access method interface, and SQL functions and procedures

```json
{
  "source_identity": "PostgreSQL 18 manual: 13.1 Introduction (mvcc-intro.html), 13.2 Transaction Isolation (transaction-iso.html), 63.3 Index Scanning (index-scanning.html), 63.4 Index Locking Considerations (index-locking.html), 36.5 Query Language (SQL) Functions (xfunc-sql.html), CREATE PROCEDURE (sql-createprocedure.html); all under https://www.postgresql.org/docs/current/",
  "author_or_issuing_body": "PostgreSQL Global Development Group",
  "publisher": "PostgreSQL Global Development Group, postgresql.org",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2025-09-25",
  "source_family": "Primary: the PostgreSQL manual for the current release. Same lineage as A1-SR-05, A1-SR-06 and A1-SR-08.",
  "precise_evidence_location": "13.1, first two paragraphs; 13.2.1 Read Committed, first paragraph; 13.2.2 Repeatable Read, first paragraph; 63.3, first paragraph and paragraph on index-only scans; 63.4, paragraphs on MVCC-compliant snapshots; 36.5, opening paragraphs; 36.5 example on procedures versus void functions",
  "method": "Project manual that states behaviour and the interface between the core and index extensions.",
  "limitations": "Same dating as A1-SR-05. The manual states the general rule for every index access method; it does not name pgvector. The step from this rule to pgvector's HNSW index is inferred in A1-SR-10.",
  "provenance": "Pages downloaded with curl on 2026-11-18 and converted to text with pandoc. Re-verify at the URLs above or at /docs/18/."
}
```

## Evidence

- 13.1: "This means that each SQL statement sees a snapshot of data (a database version) as it was some time ago, regardless of the current state of the underlying data."
- 13.2.1: "However, SELECT does see the effects of previous updates executed within its own transaction, even though they are not yet committed."
- 13.2.2: "(However, each query does see the effects of previous updates executed within its own transaction, even though they are not yet committed.)"
- 63.3: "The access method is not involved in actually fetching those tuples from the index's parent table, nor in determining whether they pass the scan's visibility test or other conditions."
- 63.4: "When using an MVCC-compliant snapshot, there is no problem because the new occupant of the slot is certain to be too new to pass the snapshot test."
- 36.5: "Any collection of commands in the SQL language can be packaged together and defined as a function."
- 36.5: "(You cannot use transaction control commands, e.g., COMMIT, SAVEPOINT, and some utility commands, e.g., VACUUM, in SQL functions.)"
- 36.5: "However, procedures offer additional functionality such as transaction control that is not available in functions."
- 36.5: "Alternatively, an SQL function can be declared to return a set (that is, multiple rows) by specifying the function's return type as SETOF sometype, or equivalently by declaring it as RETURNS TABLE(columns)."
- Statement S6: an SQL function that returns a table can hold a query with WITH RECURSIVE, so a caller names the function. The manual states the packaging; the combination with a recursive query is inferred.
- Statement S7: the visibility rule is general. A later statement in the same transaction sees the earlier statement's rows, and the core, not the index, decides visibility. A1-SR-10 applies this to HNSW.
- What the source shows: the own-writes rule at Read Committed and Repeatable Read, and that index extensions leave visibility to the core.
- What the source does not show: anything about approximate indexes, which can return fewer rows than asked for (A1-SR-10).
