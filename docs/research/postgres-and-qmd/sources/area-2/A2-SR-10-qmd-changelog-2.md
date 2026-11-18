# A2-SR-10: qmd CHANGELOG.md, releases 2.0.0 to 2.9.0

```json
{
  "source_identity": "CHANGELOG.md of tobi/qmd at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514, sections 2.0.0 (2026-03-10) to 2.9.0 (2026-11-17)",
  "author_or_issuing_body": "Tobi Lütke and contributors",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-11-17",
  "source_family": "Primary: release notes of tobi/qmd. Same lineage as A2-SR-01 to A2-SR-09, A2-SR-11 and A2-SR-12.",
  "precise_evidence_location": "CHANGELOG.md lines 5-60 and 130-214 (2.9.0), 274-282 and 584-590 (2.8.3, #785, entry printed twice), 508-517 (2.8.3, #791 #803), 795-845 (2.5.0, #591), 980-993 (2.0.0)",
  "method": "Read the sections in the clone at the stated commit.",
  "limitations": "The 2.8.3 section repeats the #785 entry at lines 274-282 and 584-590. Section 2.6.3 has no tag, release, or npm version. The changelog speaks of an ANN candidate pool at line 513 and of a brute-force scan at line 207; the two wordings conflict and the sqlite-vec documentation does not settle them (A2-SR-13). Performance figures are the project's own.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18 at aa247d0ee2e5dc3b83e1270714c0f06ca94e2514. Re-verify with git show aa247d0ee2e5dc3b83e1270714c0f06ca94e2514:CHANGELOG.md."
}
```

## Evidence

- 2.0.0, lines 982-983: "QMD 2.0 declares a stable library API. The SDK is now the primary interface — the MCP server is a clean consumer of it"
- 2.5.0, line 842: "Hybrid search: weight RRF lists by query type so original FTS and original vector evidence get the intended 2x boost, instead of accidentally boosting the first lexical expansion. #591"
- 2.8.3, lines 512-517: "`vsearch -c <collection>` no longer returns empty results for small collections crowded out of the global ANN candidate pool." The fix exact-scans a collection within 20k rows: "sqlite-vec caps `k` at 4096 so a larger multiplier alone is not enough".
- 2.8.3, lines 277-281: "A fallback there means the file moved or was deleted since the last index, so `search`, `query`, `get` and `multi-get` now print a notice to stderr naming how many results fell back and suggesting `qmd update`; stdout stays machine-readable."
- 2.9.0, lines 167-172: repeated expansions are dropped: "one reported query ran 23 expansions where 9 were distinct, and each copy ran its own search."
- 2.9.0, lines 183-187: "The vector index is partitioned by collection." and a collection-scoped query "scans only that collection's vectors instead of pre-filtering the whole index, and a small collection is never crowded out of the results by a large one."
- 2.9.0, lines 205-208: "vec0 fills the first free slot of its newest chunk and reclaims a chunk only once it is empty, so re-embeds and orphan removal leave holes in older chunks that every brute-force scan still reads"
- 2.9.0, lines 34-44: config writes are serialised and published atomically; a collection rename writes a pending marker so an interrupted rename is finished by repeating the command.
- 2.9.0 also adds metadata filtering (line 97), processors, and remote embedding and reranking options (lines 78-81).
- Shows: the later formulations of fusion weighting, vector partitioning, and consistency between YAML config and SQLite. Does not show: independent measurement of the stated speed-ups.
