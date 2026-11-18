# A1-SR-10: PostgreSQL 18 manual, text search indexes, limits and generated columns, with the index check in indexcmds.c

```json
{
  "source_identity": "PostgreSQL 18 manual 12.9 Preferred Index Types for Text Search (textsearch-indexes.html), 12.11 Limitations (textsearch-limitations.html), 5.4 Generated Columns (ddl-generated-columns.html), all under https://www.postgresql.org/docs/18/; PostgreSQL 19 manual 5.4 (same path under /docs/19/); src/backend/commands/indexcmds.c at commit e3b7f6156916c2ffefb51c12a0576d8b095d5c26 (REL_18_STABLE) and 1eb1e8b5f366b78d5a0e3821c3a197b7ab0f6ea4 (REL_19_STABLE)",
  "author_or_issuing_body": "PostgreSQL Global Development Group",
  "publisher": "PostgreSQL Global Development Group, postgresql.org and the git repository",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2025-09-25",
  "source_family": "Primary: the PostgreSQL manual and source code. Same manual lineage as A1-SR-06.",
  "precise_evidence_location": "12.9 all paragraphs; 12.11 list of limits; 5.4 first paragraph, the default-kind sentence and the restriction on generation expressions; indexcmds.c lines 1125-1146 (REL_18_STABLE) and 1132-1153 (REL_19_STABLE)",
  "method": "Project manual stating index types, limits and column kinds; source code for the error raised on indexes over virtual generated columns.",
  "limitations": "Same page dating as A1-SR-01. The 19 pages of 5.4, 12.9 and 12.11 are identical to 18 apart from the footer. The manual page on generated columns does not itself state that a virtual generated column cannot be indexed; the error text in indexcmds.c shows it.",
  "provenance": "Pages downloaded with curl on 2026-11-18. indexcmds.c read from raw.githubusercontent.com at both commits and searched for the words virtual generated. Re-verify at the URLs above."
}
```

## Evidence

- 12.9: "GIN indexes are the preferred text search index type."
- 12.9: "GIN indexes store only the words (lexemes) of tsvector values, and not their weight labels. Thus a table row recheck is needed when using a query that involves weights."
- 12.9: "A GiST index is lossy, meaning that the index might produce false matches, and it is necessary to check the actual table row to eliminate such false matches."
- 12.9: "The default signature length (when siglen is not specified) is 124 bytes, the maximum signature length is 2024 bytes."
- 12.9: "Partitioning of big collections and the proper use of GIN and GiST indexes allows the implementation of very fast searches with online update."
- 12.11 limits, verbatim items: "The length of each lexeme must be less than 2 kilobytes", "No more than 256 positions per lexeme", "Position values in tsvector must be greater than 0 and no more than 16,383", "The length of a tsvector's data (lexemes + positions) must be less than 1 megabyte"
- 5.4: "A stored generated column is computed when it is written (inserted or updated) and occupies storage as if it were a normal column. A virtual generated column occupies no storage and is computed when it is read."
- 5.4: "A generated column is by default of the virtual kind. Use the keywords VIRTUAL or STORED to make the choice explicit."
- 5.4: "The generation expression can only use immutable functions and cannot use subqueries or reference anything other than the current row in any way."
- 5.4: "the generation expression of a virtual generated column must not reference user-defined functions or types, that is, it can only use built-in functions or types."
- indexcmds.c raises the error `indexes on virtual generated columns are not supported`. Note: the code line holds C string quotation marks, so it is given as code, not as a quote.
- What the source shows: GIN suits text search and GiST is lossy. The 256-position cap and the 16,383 position limit bound what ranking and phrase search see in long documents. Since 18 a generated column defaults to virtual, and a virtual column cannot carry an index, so the 12.2.2 pattern (A1-SR-06) needs the keyword STORED. A stored generated tsvector is computed in the same statement that writes the row, so it commits and rolls back with the row (inferred from 5.4).
- What the source does not show: GIN behaviour under writes (A1-SR-11, A1-SR-12).
