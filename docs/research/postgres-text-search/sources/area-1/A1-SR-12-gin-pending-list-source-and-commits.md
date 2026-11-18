# A1-SR-12: GIN pending list in the PostgreSQL source, and the fastupdate and gin_pending_list_limit commits

```json
{
  "source_identity": "src/backend/access/gin/ginfast.c, src/backend/access/gin/ginget.c and src/backend/access/gin/README at commit e3b7f6156916c2ffefb51c12a0576d8b095d5c26 of REL_18_STABLE; commits ff301d6e690bb5581502ea3d8591a1600fd87acc (2009-03-24, fastupdate) and c291503b1c8250c7ba6ca900b7ba2f85a64b1eb6 (2014-11-13, rename to gin_pending_list_limit); github.com/postgres/postgres",
  "author_or_issuing_body": "PostgreSQL Global Development Group; Teodor Sigaev (fastupdate patch, committed by Tom Lane); Fujii Masao (rename commit, per the 9.5 release note in A1-SR-14)",
  "publisher": "PostgreSQL Global Development Group (git repository mirrored at github.com/postgres/postgres)",
  "publication_date": "2026-11-18T18:57:40Z",
  "relevant_event_date": "2009-03-24",
  "source_family": "Primary: the PostgreSQL source code and commit records. The manual description of the same mechanism is A1-SR-11.",
  "precise_evidence_location": "ginfast.c header comment (lines 1-8) and XLogInsert calls at lines 130, 436 and 652; ginget.c scanPendingInsert, lines 1834-1860; gin/README, paragraph on list pages (lines 95-105) and the predicate locking section (lines 480-508); commit messages of ff301d6e69 and c291503b1c",
  "method": "Source code and commit messages read directly.",
  "limitations": "publication_date is the committer date of the REL_18_STABLE head read; the REL_19_STABLE copy of ginfast.c differs only in the copyright year and allocation macros in the lines compared. That a transaction sees its own pending entries is inferred: the scan reads every pending page into the result bitmap, and visibility is then decided by the core against the heap (postgres-and-qmd survey, A1-SR-07). No source states this in one sentence. The code was read, not run. Quotes from C comments leave out the leading asterisk of each comment line.",
  "provenance": "Files read from raw.githubusercontent.com at the commit above on 2026-11-18; commits read with gh api repos/postgres/postgres/commits/<sha>. Re-verify at the same commit."
}
```

## Evidence

- ginfast.c header: "Pending entries are stored in linear list of pages. Later on (typically during VACUUM), ginInsertCleanup() will be invoked to transfer pending entries into the regular index structure. This wins because bulk insertion is much more efficient than retail."
- ginfast.c line 130: "recptr = XLogInsert(RM_GIN_ID, XLOG_GIN_INSERT_LISTPAGE);" and line 436: "recptr = XLogInsert(RM_GIN_ID, XLOG_GIN_UPDATE_META_PAGE);"
- ginget.c, scanPendingInsert: "Collect all matched rows from pending list into bitmap."
- ginget.c: "Acquire predicate lock on the metapage, to conflict with any fastupdate insertions."
- gin/README: "The list pages have to be scanned linearly when doing a search, so the pending entries should be merged into the main btree before there get to be too many of them."
- gin/README: "The interlock for fastupdate pending lists means that with fastupdate=on, we effectively always grab a full-index lock, so you could get a lot of false positives."
- Commit ff301d6 (2009): "This helps because bulk insert is (usually) significantly faster than retail insert for GIN."
- Commit ff301d6: "This patch also removes GIN support for amgettuple-style index scans."
- Commit c291503 (2014): "Since this parameter is only for GIN index, it's better to add" and the message goes on to say the name gains the prefix gin. Note: the setting was first called pending_list_cleanup_size during the 9.5 cycle.
- What the source shows: pending entries live in index pages inside the server and are written to the write-ahead log, so they commit, roll back and recover with the table. Every GIN scan reads the whole pending list. Under SERIALIZABLE, fastupdate makes every scan lock the whole index for conflict checks, which can cause extra serialization failures.
- What the source does not show: any measurement of the false-positive rate or of search slowdown.
