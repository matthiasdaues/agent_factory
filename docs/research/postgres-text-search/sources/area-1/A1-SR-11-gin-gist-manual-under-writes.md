# A1-SR-11: PostgreSQL 18 manual, GIN and GiST under inserts and updates, fastupdate and gin_pending_list_limit

```json
{
  "source_identity": "PostgreSQL 18 manual 65.4 GIN Indexes (gin.html), 65.2 GiST Indexes (gist.html), CREATE INDEX (sql-createindex.html), 19.11 Client Connection Defaults (runtime-config-client.html); all under https://www.postgresql.org/docs/18/",
  "author_or_issuing_body": "PostgreSQL Global Development Group; 65.4.1 names Teodor Sigaev and Oleg Bartunov as the main GIN maintainers",
  "publisher": "PostgreSQL Global Development Group, postgresql.org",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2025-09-25",
  "source_family": "Primary: the PostgreSQL manual for release 18. The source code behind the same mechanism is recorded in A1-SR-12.",
  "precise_evidence_location": "65.4.1 Introduction; 65.4.4.1 GIN Fast Update Technique; 65.4.5 GIN Tips and Tricks, items Create vs. insert, gin_pending_list_limit and gin_fuzzy_search_limit; 65.2.4.1 GiST build methods; CREATE INDEX storage parameters fastupdate and gin_pending_list_limit and the note on ALTER INDEX; runtime-config-client entry gin_pending_list_limit",
  "method": "Project manual stating index behaviour and settings.",
  "limitations": "Same page dating as A1-SR-01. The 19 GIN page (gin.html) differs from 18 only in one sentence on the comparePartial support function. The manual states the pending list and cleanup, but not whether a search in the writing transaction finds its own new entries; A1-SR-12 and the postgres-and-qmd survey record A1-SR-07 cover that.",
  "provenance": "Pages downloaded with curl on 2026-11-18 and converted to text. Re-verify at the URLs above."
}
```

## Evidence

- 65.4.1: "A GIN index stores a set of (key, posting list) pairs, where a posting list is a set of row IDs in which the key occurs."
- 65.4.4.1: "Updating a GIN index tends to be slow because of the intrinsic nature of inverted indexes: inserting or updating one heap row can cause many inserts into the index (one for each key extracted from the indexed item)."
- 65.4.4.1: "GIN is capable of postponing much of this work by inserting new tuples into a temporary, unsorted list of pending entries."
- 65.4.4.1: "When the table is vacuumed or autoanalyzed, or when gin_clean_pending_list function is called, or if the pending list becomes larger than gin_pending_list_limit, the entries are moved to the main GIN data structure using the same bulk insert techniques used during initial index creation."
- 65.4.4.1: "The main disadvantage of this approach is that searches must scan the list of pending entries in addition to searching the regular index, and so a large list of pending entries will slow searches significantly."
- 65.4.4.1: "If consistent response time is more important than update speed, use of pending entries can be disabled by turning off the fastupdate storage parameter for a GIN index."
- 65.4.5: "So, for bulk insertions into a table it is advisable to drop the GIN index and recreate it after finishing bulk insertion."
- 65.4.5: "To avoid fluctuations in observed response time, it's desirable to have pending-list cleanup occur in the background (i.e., via autovacuum)."
- 65.4.5: "If a non-zero limit is set, then the returned set is a subset of the whole result set, chosen at random." (gin_fuzzy_search_limit, default 0)
- CREATE INDEX, fastupdate: "ON enables fast update, OFF disables it. The default is ON."
- CREATE INDEX note: "Turning fastupdate off via ALTER INDEX prevents future insertions from going into the list of pending index entries, but does not in itself flush existing entries."
- runtime-config-client: "The default is four megabytes (4MB). This setting can be overridden for individual GIN indexes by changing index storage parameters."
- 65.2.4.1: "The simplest way to build a GiST index is just to insert all the entries, one by one." GiST inserts each new entry into the tree at once, using the penalty function; the manual describes no pending list for GiST.
- What the source shows: GIN with fastupdate on defers index work to a pending list that every search also scans. Cleanup runs in vacuum, autoanalyze, on a call, or in the foreground when the list passes 4 MB. GiST has no such list.
- What the source does not show: that pending entries are WAL-logged and visible to the writing transaction (A1-SR-12), and any figure for the slowdown.
