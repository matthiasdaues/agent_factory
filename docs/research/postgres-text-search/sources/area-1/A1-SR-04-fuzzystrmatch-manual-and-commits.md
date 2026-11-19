# A1-SR-04: PostgreSQL 18 and 19 manual, fuzzystrmatch, with its first and Daitch-Mokotoff commits

```json
{
  "source_identity": "PostgreSQL 18 manual F.16 fuzzystrmatch (https://www.postgresql.org/docs/18/fuzzystrmatch.html); PostgreSQL 19 manual, same page under /docs/19/; commits d8783c512e3c90c705ce61a225df39f962db9ab3 (2001-08-07) and a290378a3752f787cdc2252889ba513f6fb393db (2023-04-07) in github.com/postgres/postgres",
  "author_or_issuing_body": "PostgreSQL Global Development Group (manual); Joe Conway, committed by Bruce Momjian (2001); Dag Lem, committed by Tom Lane (Daitch-Mokotoff)",
  "publisher": "PostgreSQL Global Development Group, postgresql.org and the git repository",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2023-04-07",
  "source_family": "Primary: the PostgreSQL manual and source repository. The 19 release note on the non-ASCII change is recorded in A1-SR-14.",
  "precise_evidence_location": "F.16 Caution box; F.16.1 Soundex; F.16.2 Daitch-Mokotoff Soundex, including the GIN and full-text examples; F.16.3 Levenshtein; F.16.4 Metaphone; F.16.5 Double Metaphone. Commit messages of d8783c512e and a290378a37.",
  "method": "Project manual stating functions and limits; commit messages stating intent.",
  "limitations": "Same page dating as A1-SR-01. The 18 and 19 pages are identical apart from the footer. The manual does not state for which languages Metaphone suits beyond the multibyte caution. The 2001 patch author is taken from the message signature; the commit metadata names Bruce Momjian. The module version is 1.2 (fuzzystrmatch.control on REL_19_STABLE).",
  "provenance": "Pages downloaded with curl on 2026-11-18 and converted to text; commits read with gh api on 2026-11-18. Re-verify at the URLs above."
}
```

## Evidence

- Caution box: "At present, the soundex, metaphone, dmetaphone, and dmetaphone_alt functions do not work well with multibyte encodings (such as UTF-8). Use daitch_mokotoff or levenshtein with such data."
- F.16.1: "The Soundex system is a method of matching similar-sounding names by converting them to the same code. It was initially used by the United States Census in 1880, 1900, and 1910. Note that Soundex is not very useful for non-English names."
- F.16.2: "However, Daitch-Mokotoff Soundex is significantly more useful for non-English names than the original system."
- F.16.2: "The result may contain one or more codes depending on how many plausible pronunciations there are, so it is represented as an array."
- F.16.2: "For matching of single names, returned text arrays can be matched directly using the && operator: any overlap can be considered a match. A GIN index may be used for efficiency"
- F.16.2 example: `CREATE INDEX ix_s_dm ON s USING gin (daitch_mokotoff(nm)) WITH (fastupdate = off);` and a second example that wraps the codes in a `tsvector` and indexes them with GIN.
- F.16.2: "If it is desired to avoid recalculation of soundex codes during index rechecks, an index on a separate column can be used instead of an index on an expression. A stored generated column can be used for this"
- F.16.3: "Both source and target can be any non-null string, with a maximum of 255 characters."
- F.16.3: "levenshtein_less_equal is an accelerated version of the Levenshtein function for use when only small distances are of interest. If the actual distance is less than or equal to max_d, then levenshtein_less_equal returns the correct distance; otherwise it returns some value greater than max_d."
- F.16.4: "source has to be a non-null string with a maximum of 255 characters."
- F.16.5: "There is no length limit on the input strings." The section also states that the primary and alternate codes can differ for non-English names; that sentence holds its own quotation marks and is paraphrased here.
- Commit d8783c5 (2001): "Per this discussion, here's a patch to implement both levenshtein() and metaphone() in a contrib."
- Commit d8783c5: "Does it make sense to fold the soundex contrib together with this one?"
- Commit d8783c5: "I was debating trying to add multibyte support to levenshtein (it would make no sense at all for metaphone)"
- Commit a290378 (2023): "This modernized version of Soundex works significantly better than the original, particularly for non-English names."
- What the source shows: what each function computes, its input limits, the languages and encodings it suits, and that only Daitch-Mokotoff codes get a documented index path (GIN on the code array or on a tsvector). Levenshtein, Soundex, Metaphone and Double Metaphone get no index in the manual, so a query compares row by row unless another filter narrows the rows (inferred from the absence of any index example).
- What the source does not show: any combination of fuzzystrmatch with pg_trgm indexes, or any figure for speed.
