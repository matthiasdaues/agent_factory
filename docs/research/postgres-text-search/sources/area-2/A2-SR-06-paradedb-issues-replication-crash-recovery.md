# A2-SR-06: ParadeDB issues #6007 and #7093 on physical replication and crash recovery

```json
{
  "source_identity": "paradedb/paradedb issue #6007 'Community ParadeDB index creation stops all PostgreSQL physical replication' (opened 2026-08-20, open) and issue #7093 'pg_search 0.26.0: BM25 index keeps documents with no heap tuple after crash recovery (verify_index heap_references_valid = false)' (opened 2026-10-29, open); https://github.com/paradedb/paradedb/issues/6007 and https://github.com/paradedb/paradedb/issues/7093",
  "author_or_issuing_body": "Issue reporters on the paradedb/paradedb tracker",
  "publisher": "GitHub",
  "publication_date": "2026-10-29T16:47:38Z",
  "relevant_event_date": "2026-08-20",
  "source_family": "Primary: issue reports in the extension repository, written by reporters, not by the vendor's documentation team. Independent of the vendor claims in A2-SR-03.",
  "precise_evidence_location": "Issue #6007 body, sections Problem, Reproduction steps 4 to 6, Expected behavior; issue #7093 body, sections Setup, Result, Questions",
  "method": "Reporters describe reproductions: #6007 with the project's own replication integration test on v0.25.2 and PostgreSQL 18; #7093 with repeated kill -9 and crash recovery on v0.26.0 and PostgreSQL 17.11.",
  "limitations": "Both issues were open on 2026-11-18 with no maintainer resolution read; the behaviour may change. I did not reproduce either report. The search for issues used the GitHub search API with title keywords (rollback, replication, standby, visibility, crash recovery, pg_dump) and may miss reports with other titles.",
  "provenance": "Read with `gh api repos/paradedb/paradedb/issues/6007` and `gh api repos/paradedb/paradedb/issues/7093` on 2026-11-18; found with `gh api search/issues`. Re-verify at the URLs above."
}
```

## Evidence

- #6007, Problem: "ParadeDB Community currently stops the entire PostgreSQL physical standby when WAL replay reaches the creation of a ParadeDB index. This prevents replication not only for the unsupported ParadeDB index, but also for every ordinary PostgreSQL relation in the cluster."
- #6007, Reproduction step 4: "`ambuild` emits the custom WAL `INIT_INDEX` record using resource manager ID 137." Step 6: "Recovery terminates and the standby becomes unavailable. Ordinary heap-table WAL can no longer replay either."
- #6007, Expected behavior: "Installing Community in an existing PostgreSQL cluster should not disable native physical replication for regular PostgreSQL tables and indexes."
- #6007 shows that ParadeDB uses a custom WAL resource manager, while pg_textsearch states it has none (A2-SR-01).
- #7093, Result: after crash-recovery cycles, `pdb.verify_index` reported "14 of 270994 indexed ctids missing from heap". The reporter notes the heap holds only whole committed batches.
- #7093, Questions: "Is it expected that crash recovery leaves index documents for heap tuples that never became durable?"
- #7093 also reports that `REINDEX` cleared the state on one clone. The ParadeDB index is derived data that a `REINDEX` rebuilds from the table.
- Not shown: a maintainer answer, a fix, or whether query results were wrong in the crash runs.
