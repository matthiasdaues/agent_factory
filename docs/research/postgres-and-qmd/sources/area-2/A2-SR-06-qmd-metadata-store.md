# A2-SR-06: qmd metadata tables in src/metadata-store.ts

```json
{
  "source_identity": "src/metadata-store.ts of tobi/qmd at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514, function initializeMetadataSchema",
  "author_or_issuing_body": "Tobi Lütke and contributors",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-11-17",
  "source_family": "Primary: source code of tobi/qmd. Same lineage as A2-SR-01 to A2-SR-05 and A2-SR-07 to A2-SR-12.",
  "precise_evidence_location": "src/metadata-store.ts lines 40-90",
  "method": "Read the DDL in the clone at the stated commit, and the matching README section (A2-SR-02 lines 1060-1130).",
  "limitations": "The filter evaluator in src/metadata-filter.ts was not read in full. The feature is new in 2.9.0 (A2-SR-10), so its behaviour has had one release of use. publication_date is the commit date.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18 at aa247d0ee2e5dc3b83e1270714c0f06ca94e2514. Re-verify with git show aa247d0ee2e5dc3b83e1270714c0f06ca94e2514:src/metadata-store.ts."
}
```

## Evidence

- Table document_metadata(document_id INTEGER PRIMARY KEY, metadata_json, extraction_version, extraction_error, extracted_at, FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE).
- Table document_metadata_values(document_id, key, ordinal, value_type, text_value, number_value, boolean_value, PRIMARY KEY (document_id, key, ordinal)) with "CHECK (value_type IN ('string', 'number', 'boolean'))".
- Three lookup indexes, one per value type (lines 76-90).
- Metadata is read from a frontmatter block named qmd.metadata (A2-SR-02 line 1082 holds the accepted value types).
- Shows: the only typed key-value store attached to documents. Inferred: a string value can name another document, so a document could list targets of a relation as an array of strings. The store does not resolve such a value to a document, check that the target exists, or type the relation beyond its key name. Does not show: any edge between chunks, or any history of metadata values; rows cascade-delete with their document.
