# A1-SR-06: PostgreSQL 18 manual, full text search: documents, matching, query parsing, highlighting

```json
{
  "source_identity": "PostgreSQL 18 manual, Chapter 12 Full Text Search: 12.1 Introduction (textsearch-intro.html), 12.2 Tables and Indexes (textsearch-tables.html), 12.3.1 Parsing Documents, 12.3.2 Parsing Queries and 12.3.4 Highlighting Results (textsearch-controls.html); all under https://www.postgresql.org/docs/18/",
  "author_or_issuing_body": "PostgreSQL Global Development Group",
  "publisher": "PostgreSQL Global Development Group, postgresql.org",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2025-09-25",
  "source_family": "Primary: the PostgreSQL manual for release 18. Same lineage as A1-SR-01, A1-SR-07, A1-SR-08, A1-SR-10 and A1-SR-11.",
  "precise_evidence_location": "12.1 opening paragraphs, 12.1.1, 12.1.2, 12.1.3; 12.2.1, 12.2.2; 12.3.1; 12.3.2 on to_tsquery, plainto_tsquery, phraseto_tsquery and websearch_to_tsquery; 12.3.4 including the XSS warning",
  "method": "Project manual stating types, functions and operators.",
  "limitations": "Same page dating as A1-SR-01. The 19 pages textsearch-intro.html, textsearch-tables.html and textsearch-controls.html are identical to 18 apart from the footer. Ranking (12.3.3) is recorded in A1-SR-07. Several manual sentences hold their own quotation marks and are paraphrased.",
  "provenance": "Pages downloaded with curl on 2026-11-18 and converted to text. Re-verify at the URLs above."
}
```

## Evidence

- 12.1: "Full Text Searching (or just text search) provides the capability to identify natural-language documents that satisfy a query, and optionally to sort them by relevance to the query."
- 12.1, on LIKE and regular expressions: "There is no linguistic support, even for English."
- 12.1: "A data type tsvector is provided for storing preprocessed documents, along with a type tsquery for representing processed queries"
- 12.1.1: "Searching and ranking are performed entirely on the tsvector representation of a document — the original text need only be retrieved when the document has been selected for display to a user."
- 12.1.2: "A tsquery contains search terms, which must be already-normalized lexemes, and may combine multiple terms using AND, OR, NOT, and FOLLOWED BY operators."
- 12.1.2, phrase search with the `<->` (FOLLOWED BY) operator: "which matches only if its arguments have matches that are adjacent and in the given order." Note: the quote starts after the operator sign, which the Markdown formatter would escape.
- 12.1.2: "The phraseto_tsquery function makes use of this operator to construct a tsquery that can match a multi-word phrase when some of the words are stop words."
- 12.1.3: "Text search configurations select a parser and a set of dictionaries to use to normalize the tokens produced by the parser."
- 12.1.3: "Text search parsers and templates are built from low-level C functions; therefore it requires C programming ability to develop new ones, and superuser privileges to install one into a database."
- 12.2.2: "Only text search functions that specify a configuration name can be used in expression indexes"
- 12.2.2: "This ensures that an index will be used only with the same configuration used to create the index entries."
- 12.2.2: "To keep this column automatically up to date with its source data, use a stored generated column."
- 12.2.2: "The expression-index approach is simpler to set up, however, and it requires less disk space since the tsvector representation is not stored explicitly."
- 12.3.1: "The function setweight can be used to label the entries of a tsvector with a given weight, where a weight is one of the letters A, B, C, or D."
- 12.3.2: "websearch_to_tsquery is a simplified version of to_tsquery with an alternative syntax, similar to the one used by web search engines."
- 12.3.2: "Moreover, this function will never raise syntax errors, which makes it possible to use raw user-supplied input for search."
- 12.3.2: quoted text becomes terms joined by `<->`, the word or becomes `|`, and a dash becomes `!`. Note: the manual's list holds its own quotation marks and is paraphrased.
- 12.3.2: "So like plainto_tsquery and phraseto_tsquery, the websearch_to_tsquery function will not recognize tsquery operators, weight labels, or prefix-match labels in its input."
- 12.3.4: "The output from ts_headline is not guaranteed to be safe for direct inclusion in web pages."
- 12.3.4: "ts_headline uses the original document, not a tsvector summary, so it can be slow and should be used with care."
- What the source shows: the types, the match operator, the four query parsers, phrase search, weights, highlighting, and the two ways to index (expression index or stored generated column), with their trade-offs.
- What the source does not show: ranking (A1-SR-07), language-specific stemming (A1-SR-08, A1-SR-09), or index behaviour under writes (A1-SR-11, A1-SR-12).
