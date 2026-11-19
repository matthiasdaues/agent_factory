# A2-SR-05: ParadeDB blog, renaming pg_bm25 to pg_search, 2023

```json
{
  "source_identity": "Ming Ying, 'pg_search: Elastic-Quality Full Text Search Inside Postgres', ParadeDB blog, 2023-11-15; https://www.paradedb.com/blog/introducing-search",
  "author_or_issuing_body": "Ming Ying, ParadeDB, Inc.",
  "publisher": "ParadeDB, Inc. (paradedb.com)",
  "publication_date": "2023-11-15T00:00:00Z",
  "relevant_event_date": "2023-11-15",
  "source_family": "Primary for the rename and the stated design of v0.6.0; vendor announcement. Same lineage as A2-SR-03 and A2-SR-04.",
  "precise_evidence_location": "Byline and first paragraph; paragraph on the inverted index",
  "method": "Vendor announcement of the v0.6.0 release.",
  "limitations": "Vendor blog post; the performance and quality claims in it are not used. The page does not say where the index files lived at the time or whether they were WAL-logged. Only the date is known, so the time is set to midnight UTC.",
  "provenance": "Raw HTML fetched with curl on 2026-11-18, tags stripped with a local Python script, passages read in the plain text. Re-verify at the URL above."
}
```

## Evidence

- Byline: "By Ming Ying on November 15, 2023".
- First paragraph: "With the release of v0.6.0 , which marks the first stable release of the ParadeDB full-text search extension, we have renamed pg_bm25 to pg_search ." The spaces before the commas come from the stripped HTML.
- Inverted index paragraph: "Rather than creating this inverted index externally, pg_search stores the index inside Postgres as a new, Postgres-native index type, which we now call the ParadeDB index. This is made possible through Postgres' index access method API."
- Not shown: the storage location of the index files before block storage (A2-SR-04, 0.14.0) and any WAL behaviour in 2023.
