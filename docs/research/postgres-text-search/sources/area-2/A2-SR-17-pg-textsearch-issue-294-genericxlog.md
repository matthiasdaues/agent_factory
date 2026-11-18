# A2-SR-17: pg_textsearch issue #294, Adopt GenericXLog for WAL-based crash atomicity and replication

```json
{
  "source_identity": "timescale/pg_textsearch issue #294 'Adopt GenericXLog for WAL-based crash atomicity and replication', opened 2026-03-21, closed 2026-04-14; https://github.com/timescale/pg_textsearch/issues/294",
  "author_or_issuing_body": "pg_textsearch maintainers (issue opened on the project tracker)",
  "publisher": "GitHub",
  "publication_date": "2026-03-21T02:43:15Z",
  "relevant_event_date": "2026-03-21",
  "source_family": "Primary: issue in the extension repository. Same lineage as A2-SR-01 and A2-SR-02.",
  "precise_evidence_location": "Issue body, sections Summary, Scope, Blocker",
  "method": "A design issue that describes the storage writes at the time and proposes WAL logging through PostgreSQL's generic WAL API.",
  "limitations": "The issue describes the code as of March 2026; the linked pull requests were not read. The closing date is from the API; the issue text does not say which release shipped the change. The author account was not checked against the maintainer list.",
  "provenance": "Read with `gh api repos/timescale/pg_textsearch/issues/294` on 2026-11-18; found with `gh api search/issues` on title keywords. Re-verify at the URL above."
}
```

## Evidence

- Summary: "pg_textsearch currently uses `MarkBufferDirty` + `FlushOneBuffer` for all buffer modifications, with no WAL logging."
- Summary, first consequence: "**No crash atomicity** for multi-buffer operations (e.g., docid chain extension writes two buffers with manual flush ordering)".
- Summary, second consequence: "**No physical replication** of index changes — replicas don't see buffer modifications since no WAL records are generated".
- Proposal: "Adopting Postgres's `GenericXLog` API would give us proper WAL-based crash atomicity and correct physical replication for free."
- Blocker: "Initial implementation found that `GenericXLogFinish` during `aminsert` (the `tp_add_docid_to_pages` single-docid-add path) causes a `BufferContent` LWLock self-deadlock on the second INSERT to any BM25 index."
- Not shown: the final design. A2-SR-01 shows that the current code uses `GenericXLog` and `log_newpage_buffer()`, and A2-SR-02 shows the custom WAL step in between.
