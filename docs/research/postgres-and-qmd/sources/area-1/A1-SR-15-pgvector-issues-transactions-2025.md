# A1-SR-15: pgvector issues 824 and 1055, HNSW under transactions and SERIALIZABLE

```json
{
  "source_identity": "pgvector GitHub issues #824 'Is the HNSW Index in pgvector Fully ACID Compliant, Including Under Crash Recovery and Concurrent Updates?' (2025-04-20) and #1055 'HNSW under SERIALIZABLE: two concurrent check-then-insert transactions can both commit' (2026-11-02); https://github.com/pgvector/pgvector/issues/824 and /1055",
  "author_or_issuing_body": "Issue authors Hannibal96 (#824) and anonymous-ai-researcher (#1055); replies by Jonathan Katz (jkatz, pgvector contributor) and the maintainer Andrew Kane (ankane)",
  "publisher": "GitHub, repository pgvector/pgvector",
  "publication_date": "2025-04-20T15:19:14Z",
  "relevant_event_date": "2026-11-02",
  "source_family": "Primary: issue threads of the pgvector project with replies by a contributor and the maintainer. Same lineage as A1-SR-10 to A1-SR-14.",
  "precise_evidence_location": "#824 replies of 2025-04-21 (jkatz), 2025-05-19 (jkatz) and 2025-05-27 (ankane); #1055 issue body of 2026-11-02 and maintainer reply of 2026-11-02T03:19:34Z",
  "method": "Questions and a bug report in the issue tracker, with replies.",
  "limitations": "The #824 answers are short and point to the PostgreSQL manual; they do not address own-write visibility in the same transaction. The #1055 report is a user's analysis with a reproduction under a debugger; it was not run. Both issues are closed. The #1055 author name is a handle.",
  "provenance": "Read with gh api repos/pgvector/pgvector/issues/<n> and repos/pgvector/pgvector/issues/<n>/comments on 2026-11-18; found with the GitHub search API for 'uncommitted' and 'same transaction' in the repository."
}
```

## Evidence

- #824, question 1: "If a transaction that inserts vectors is rolled back (either manually or due to a crash), will the HNSW index also roll back?" Reply by jkatz of 2025-04-21: "Yes."
- #824, reply by jkatz: "pgvector follows the same update semantics as PostgreSQL, i.e., the tuple being updated is removed and a new tuple is inserted."
- #824, reply by jkatz: "The PostgreSQL default is `READ COMMITTED`, which disallows dirty reads."
- #824, maintainer reply of 2025-05-27: "One thing to add (to the initial question) is approximate results are not guaranteed to be the same between multiple executions of the same query"
- #1055, issue body: "HNSW doesn't do its own predicate locking, so PostgreSQL falls back to a lock on the whole index."
- #1055, issue body: "One side of the conflict goes unrecorded, SSI doesn't see a dangerous pattern, and both transactions commit."
- #1055, maintainer reply: "It'd be best to report this to core since it isn't specific to pgvector"
- Statement S7: the threads support that pgvector indexes follow PostgreSQL MVCC for rollback and visibility. They do not state that a transaction sees its own new vectors through HNSW; that remains inferred in A1-SR-10. The #1055 report shows one open edge: a check-then-insert under SERIALIZABLE can commit twice.
- What the source shows: the project's answer on rollback and visibility, and a reported race under SERIALIZABLE.
- What the source does not show: a fix for #1055, or a PostgreSQL core response.
