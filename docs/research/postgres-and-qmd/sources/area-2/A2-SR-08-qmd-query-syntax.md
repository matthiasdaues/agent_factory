# A2-SR-08: qmd query syntax, docs/SYNTAX.md

```json
{
  "source_identity": "docs/SYNTAX.md of tobi/qmd at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514",
  "author_or_issuing_body": "Tobi Lütke and contributors",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-02-20",
  "source_family": "Primary: documentation of tobi/qmd. Same lineage as A2-SR-01 to A2-SR-07 and A2-SR-09 to A2-SR-12.",
  "precise_evidence_location": "docs/SYNTAX.md lines 1-60 (grammar, query types, default behaviour, lex syntax)",
  "method": "Read the file in the clone at the stated commit.",
  "limitations": "Lines 61-196 (examples and MCP usage) were skimmed, not read in full. relevant_event_date is the 1.1.0 release that introduced query documents (A2-SR-09). publication_date is the commit date.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18 at aa247d0ee2e5dc3b83e1270714c0f06ca94e2514. Re-verify with git show aa247d0ee2e5dc3b83e1270714c0f06ca94e2514:docs/SYNTAX.md."
}
```

## Evidence

- Line 3: "QMD queries are structured documents with typed sub-queries. Each line specifies a search type and query text."
- Grammar (lines 7-19): a query is an expand query or a query document of an optional intent line and typed lines of type lex, vec, or hyde.
- Line 30: "Any single-line query with no prefix is treated as an expand query and passed to the expansion model, which emits lex, vec, and hyde variants automatically."
- Lex syntax: prefix match per word, quoted phrase, and negation with a leading minus.
- Shows: the user-facing query language: one line-typed format plus a JSON filter AST for metadata (A2-SR-02 lines 1084-1110). Does not show: any graph traversal, join, or SQL access through the public interfaces. SQL exists only inside the SQLite file.
