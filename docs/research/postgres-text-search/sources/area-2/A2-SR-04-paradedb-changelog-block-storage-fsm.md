# A2-SR-04: ParadeDB changelog entries 0.14.0 and 0.17.0

```json
{
  "source_identity": "paradedb/paradedb, docs/project/changelog/0.14.0.mdx and 0.17.0.mdx at commit c0ffb135a234efc5e1cf67f68b9ca5c0e6a51723; GitHub releases v0.14.0 (2025-01-12) and v0.17.0 (2025-07-17); https://github.com/paradedb/paradedb/releases",
  "author_or_issuing_body": "ParadeDB, Inc.",
  "publisher": "GitHub (changelog also published at paradedb.com/docs/project/changelog)",
  "publication_date": "2025-07-17T13:50:56Z",
  "relevant_event_date": "2025-01-12",
  "source_family": "Primary: vendor changelog and release metadata in the extension repository. Same lineage as A2-SR-03, A2-SR-05, A2-SR-07, A2-SR-18.",
  "precise_evidence_location": "0.14.0.mdx section Introducing Block Storage; 0.17.0.mdx section Custom Free Space Map; release dates from the GitHub releases API",
  "method": "Vendor release notes.",
  "limitations": "The changelog files carry no date; dates come from the matching GitHub releases. publication_date is v0.17.0 and relevant_event_date is v0.14.0. The notes do not say whether Community index buffers were WAL-logged after 0.14.0; the 0.24.0 entry in A2-SR-18 suggests they were not (my inference). The notes do not say where the index lived before 0.14.0.",
  "provenance": "Sparse shallow clone of https://github.com/paradedb/paradedb on 2026-11-18; dates from `gh api repos/paradedb/paradedb/releases/tags/<tag>`. Re-verify at the URLs above."
}
```

## Evidence

- 0.14.0 (released 2025-01-12): "`pg_search` is now on Postgres block storage 🎉"
- 0.14.0, for ParadeDB Community: speed gains and "Integration with Postgres' buffer cache".
- 0.14.0, for ParadeDB Enterprise: "Postgres write-ahead log (WAL) integration", "Physical replication support", and "Crash and point-in-time recovery".
- 0.14.0: "Because this is a breaking change, upgrade scripts to `0.14.0` are not provided." The upgrade steps drop all existing pg_search indexes and the extension and recreate them.
- 0.17.0 (released 2025-07-17), Custom Free Space Map: "Prior to this release, the BM25 index relied on the built-in Postgres free space map (FSM) to reclaim space during compaction. However, the Postgres FSM is not write-ahead logged. This means that if the instance terminates (i.e. during a failover), the FSM can get lost, preventing dead space in the index from being reclaimed by future writes." (link text kept.)
- 0.17.0: "To solve this, we implemented our own, write-ahead logged free space map that lives alongside the BM25 index."
- Not shown: any test of crash recovery, and the Community WAL state.
