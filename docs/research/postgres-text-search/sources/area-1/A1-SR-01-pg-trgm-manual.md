# A1-SR-01: PostgreSQL 18 and 19 manual, pg_trgm

```json
{
  "source_identity": "PostgreSQL 18 manual F.35 pg_trgm (https://www.postgresql.org/docs/18/pgtrgm.html); PostgreSQL 19 manual F.37 pg_trgm (https://www.postgresql.org/docs/19/pgtrgm.html)",
  "author_or_issuing_body": "PostgreSQL Global Development Group; module authors named in F.35.7: Oleg Bartunov, Teodor Sigaev, Alexander Korotkov",
  "publisher": "PostgreSQL Global Development Group, postgresql.org",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2025-09-25",
  "source_family": "Primary: the PostgreSQL manual for release 18 and the release 19 candidate. Same lineage as A1-SR-04 to A1-SR-08, A1-SR-10, A1-SR-11 and A1-SR-14.",
  "precise_evidence_location": "F.35.1 Trigram Concepts; F.35.2 Table F.26 (functions) and Table F.27 (operators); F.35.3 GUC Parameters; F.35.4 Index Support; F.35.5 Text Search Integration. In the 19 manual the same text is F.37 with Tables F.27 and F.28.",
  "method": "Project manual that states the functions, operators, settings and index support of the contrib module.",
  "limitations": "The pages carry no date. publication_date is the day of the 18.7 and 19 RC 2 releases (2026-11-12), the latest date the pages can stand for; relevant_event_date is the first release of 18. A diff of the 18 and 19 pages shows only renumbered sections and tables. The manual does not give the pg_trgm extension version (1.6 in contrib/pg_trgm/pg_trgm.control on REL_19_STABLE) or any cost figure. It does not state transaction behaviour; that comes from the general index rules (postgres-and-qmd survey, A1-SR-07).",
  "provenance": "Pages downloaded with curl on 2026-11-18 and converted to text with a local HTML-to-text script. pg_trgm.control read from raw.githubusercontent.com at commit 1eb1e8b5f366b78d5a0e3821c3a197b7ab0f6ea4 of REL_19_STABLE. Re-verify at the URLs above."
}
```

## Evidence

- F.35.1: "A trigram is a group of three consecutive characters taken from a string. We can measure the similarity of two strings by counting the number of trigrams they share."
- F.35.1 note: "pg_trgm ignores non-word characters (non-alphanumerics) when extracting trigrams from a string."
- Table F.26, similarity: "The range of the result is zero (indicating that the two strings are completely dissimilar) to one (indicating that the two strings are identical)."
- Table F.26, word_similarity: "Returns a number that indicates the greatest similarity between the set of trigrams in the first string and any continuous extent of an ordered set of trigrams in the second string."
- Table F.26, strict_word_similarity: "Same as word_similarity, but forces extent boundaries to match word boundaries."
- Table F.26, set_limit: "(Deprecated; instead use SET pg_trgm.similarity_threshold.)"
- F.35.2: "Thus, the strict_word_similarity function is useful for finding the similarity to whole words, while word_similarity is more suitable for finding the similarity for parts of words."
- Table F.27, the % operator: "Returns true if its arguments have a similarity that is greater than the current similarity threshold set by pg_trgm.similarity_threshold."
- Table F.27 also defines `<%` and `%>` against `pg_trgm.word_similarity_threshold`, `<<%` and `%>>` against `pg_trgm.strict_word_similarity_threshold`, and the distance operators `<->`, `<<->`, `<->>`, `<<<->` and `<->>>`. The distance is one minus the matching similarity value. Note: the operator descriptions hold their own quotation marks, so they are paraphrased here.
- F.35.3 defaults: "The threshold must be between 0 and 1 (default is 0.3)." for `pg_trgm.similarity_threshold`; "(default is 0.6)" for the word similarity threshold; "(default is 0.5)" for the strict word similarity threshold.
- F.35.4: "These index types support the above-described similarity operators, and additionally support trigram-based index searches for LIKE, ILIKE," and the sentence goes on to list the operators `~`, `~*` and `=`. Note: the quote stops before the operator signs, which the Markdown formatter would escape.
- F.35.4: "The similarity comparisons are case-insensitive in a default build of pg_trgm. Inequality operators are not supported."
- F.35.4, GiST signature: "gist_trgm_ops GiST opclass approximates a set of trigrams as a bitmap signature." The default signature length is 12 bytes, valid values 1 to 2024.
- F.35.4, nearest-neighbour ordering by `<->`: "This can be implemented quite efficiently by GiST indexes, but not by GIN indexes."
- F.35.4: "Unlike B-tree based searches, the search string need not be left-anchored."
- F.35.4: "For both LIKE and regular-expression searches, keep in mind that a pattern with no extractable trigrams will degenerate to a full-index scan."
- F.35.5: "Trigram matching is a very useful tool when used in conjunction with a full text index. In particular it can help to recognize misspelled input words that will not be matched directly by the full text search mechanism."
- F.35.5 note: "Since the words table has been generated as a separate, static table, it will need to be periodically regenerated so that it remains reasonably up-to-date with the document collection."
- What the source shows: the functions, operators, thresholds and their defaults; that GIN and GiST trigram indexes serve similarity, LIKE, ILIKE, regular expressions and equality; that only GiST serves distance ordering; and that the spelling-suggestion pattern needs a separate word table kept in sync by hand.
- What the source does not show: how the index behaves under concurrent writes (A1-SR-11, A1-SR-12), how pg_trgm classifies characters per locale (A1-SR-14 for the 18 and 19 changes), or any measured cost.
