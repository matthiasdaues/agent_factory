# A2-SR-04: qmd re-index logic in src/store.ts

```json
{
  "source_identity": "src/store.ts of tobi/qmd at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514, functions reindexCollection, deactivateDocument, deleteInactiveDocuments, cleanupOrphanedContent",
  "author_or_issuing_body": "Tobi Lütke and contributors",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-11-17",
  "source_family": "Primary: source code of tobi/qmd. Same lineage as A2-SR-01 to A2-SR-03 and A2-SR-05 to A2-SR-12.",
  "precise_evidence_location": "src/store.ts lines 2125-2135 (doc comment), 2280-2405 (reindexCollection loop), 3618-3640 (deleteInactiveDocuments, cleanupOrphanedContent), 4189-4192 (deactivateDocument)",
  "method": "Read the functions in the clone at the stated commit. A grep for watch, fs.watch, and chokidar in src/ found no file watcher.",
  "limitations": "Rename handling is inferred: no code detects a file rename. The record reads the code path for a new path and a vanished path and infers the rename outcome from them. Processor collections follow a different path (A2-SR-07) that was not traced. publication_date is the commit date.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18 at aa247d0ee2e5dc3b83e1270714c0f06ca94e2514. Re-verify with git show aa247d0ee2e5dc3b83e1270714c0f06ca94e2514:src/store.ts."
}
```

## Evidence

- Lines 2127-2133: "Uses mtime+size fast-path (file_sync_state) to avoid re-reading unchanged files." and "If mtime changed but content hash identical, only mtime cache is updated."
- Lines 2350-2358: a file whose hash changed gets a new content row and an updated documents row; a path not yet in documents gets a new documents row.
- Line 2318: "// Empty file — if previously indexed, deactivate it (treat as removed)"
- Line 2389: "// Deactivate documents that no longer exist + cleanup sync_state"
- Line 4190: deactivation is an UPDATE: "UPDATE documents SET active = 0 WHERE collection = ? AND path = ? AND active = 1"
- Lines 3631-3632: "Inactive documents are soft-deleted tombstones, so their content rows must remain referenced until deleteInactiveDocuments() hard-deletes them."
- Line 3625: hard delete is "DELETE FROM documents WHERE active = 0".
- Inferred for a renamed file: the old path is deactivated and the new path is inserted as a new document. The content row and its vectors are keyed by hash, so they are shared and need no new embedding if the content is unchanged.
- Changes reach the index only when qmd update runs; no watcher exists (grep result above).
- Shows: change, delete, and inferred rename handling. Does not show: any record of the old path for a renamed file, or any history of earlier content versions once orphaned content is cleaned.
