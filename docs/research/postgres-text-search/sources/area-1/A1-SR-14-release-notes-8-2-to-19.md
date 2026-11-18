# A1-SR-14: PostgreSQL release notes 8.2 to 19 on text search, trigrams, fuzzy matching and GIN

```json
{
  "source_identity": "PostgreSQL release notes, sections E.x Release 8.2, 8.3, 8.4, 9.1, 9.3, 9.4, 9.5, 9.6, 10, 11, 12, 13, 14, 16, 17, 18 and 19; https://www.postgresql.org/docs/<version>/release-<version>.html, for example /docs/19/release-19.html",
  "author_or_issuing_body": "PostgreSQL Global Development Group",
  "publisher": "PostgreSQL Global Development Group, postgresql.org",
  "publication_date": "2026-10-09T00:00:00Z",
  "relevant_event_date": "2008-02-04",
  "source_family": "Primary: the project's release notes. They summarise the commits recorded in A1-SR-02, A1-SR-04, A1-SR-12, A1-SR-13 and A1-SR-15.",
  "precise_evidence_location": "8.3 Overview and Migration; 8.4 GIN and Full Text Indexes items; 9.5 gin_pending_list_limit item; 9.6 phrase search, unaccent, pg_trgm and gin_clean_pending_list items; 10 tsearch2 removal; 11 websearch_to_tsquery and strict_word_similarity; 12 Snowball and unaccent; 14 websearch_to_tsquery fixes and pg_trgm equality; 16 Daitch-Mokotoff; 17 unaccent rules syntax; 18 collation provider and parallel GIN build; 19 locale provider, fuzzystrmatch, stemmers",
  "method": "Release notes compiled by the project for each major release.",
  "limitations": "publication_date is the AS OF date printed in the 19 notes (Release date: 2026-??-??, AS OF 2026-10-09); 19 was at release candidate 2 on 2026-11-12 (postgres-and-qmd survey, A1-SR-09), so the 19 notes may still change. relevant_event_date is the 8.3 release. Older notes were searched with a keyword filter, so an item worded without the keywords may be missing. Release notes summarise and do not give reasons except where quoted.",
  "provenance": "Pages downloaded with curl on 2026-11-18, converted to text and searched for the terms tsearch, text search, pg_trgm, trigram, fuzzystrmatch, unaccent, ts_rank, tsvector, tsquery, websearch, GIN, pending, fastupdate, snowball, stemmer and phrase. Re-verify at the URLs above."
}
```

## Evidence

- 8.2: "Add GIN (Generalized Inverted iNdex)" (release 2006).
- 8.3 (2008-02-04): "Full text search features from contrib/tsearch2 have been moved into the core server, with some minor syntax changes"
- 8.3: "Add GIN support for contrib/pg_trgm (Guillaume Smet," and the line names further authors.
- 8.4: "Implement fast update option for GIN indexes" and "Allow prefix matching in full text searches" and "Add support for multibyte encodings to contrib/pg_trgm (Teodor)"
- 8.4: "In contrib/fuzzystrmatch," the notes add a version of the Levenshtein function (line wrap in source).
- 9.1: "Add nearest-neighbor search support to contrib/pg_trgm and contrib/btree_gist" and "Add levenshtein_less_equal() function to contrib/fuzzystrmatch, which is" optimised for small distances (line wrap in source).
- 9.4: "Fix ts_rank_cd() to ignore stripped lexemes (Alex Hill)"
- 9.4: "Improve pg_trgm's choice of trigrams for indexed regular expression searches (Alexander Korotkov)"
- 9.5: "Add configuration parameter gin_pending_list_limit to control the size of GIN pending lists (Fujii Masao)"
- 9.5: "Previously the pending-list size was controlled by work_mem, which was awkward because appropriate values for work_mem are often much too large for this purpose."
- 9.6: "Improve full-text search to support searching for phrases, that is, lexemes appearing adjacent to each other in a specific order, or with a specified distance between them (Teodor Sigaev, Oleg Bartunov, Dmitry Ivanov)"
- 9.6: "Add gin_clean_pending_list() function to allow manual invocation of pending-list cleanup for a GIN index (Jeff Janes)"
- 9.6: "Installations that use this rules file may wish to rebuild tsvector columns and indexes that depend on the result." (unaccent rules extended to all Unicode diacritics)
- 10: "Remove contrib/tsearch2 module (Robert Haas)" and "This module provided compatibility with the version of full text search that shipped in pre-8.3 PostgreSQL releases."
- 11: "Add text search function websearch_to_tsquery() that supports a query syntax similar to that used by web search engines (Victor Drobny, Dmitry Ivanov)"
- 11: "Add pg_trgm function strict_word_similarity() to compute the similarity of whole words (Alexander Korotkov)"
- 11: "Add predicate locking for hash, GiST and GIN indexes (Shubham Barai)"
- 12: "This adds word stemming support for Arabic, Indonesian, Irish, Lithuanian, Nepali, and Tamil to full text search."
- 14: "Fix websearch_to_tsquery() to properly parse multiple adjacent discarded tokens in quotes (Alexander Korotkov)" and "Allow GiST/GIN pg_trgm indexes to do equality lookups (Julien Rouhaud)"
- 16: "Add support for Daitch-Mokotoff Soundex to fuzzystrmatch (Dag Lem)"
- 17: "Allow unaccent character translation rules to contain whitespace and quotes (Michael Paquier)"
- 18: "When upgrading such clusters using pg_upgrade, it is recommended to reindex all indexes related to full-text search and pg_trgm after the upgrade." and "Allow GIN indexes to be created in parallel (Tomas Vondra, Matthias van de Meent)"
- 19: "Change full text search and pg_trgm to use the database's locale provider for character classification when parsing text (Jeff Davis)"
- 19: "When upgrading such databases using pg_upgrade, it is recommended to reindex all indexes which use full text search and pg_trgm after the upgrade, and to recompute any stored tsvector values."
- 19: "dmetaphone() and dmetaphone_alt() now upper-case their input using the database's default collation rather than always using libc, and soundex(), metaphone(), and difference() now treat only ASCII letters as letters."
- 19: "The English, French, German, Lithuanian, Norwegian, Spanish, Swedish, and Turkish stemmers have also been updated and produce different stems for some words."
- What the source shows: the release of each feature, and that four upgrades (9.6, 18, 19, and the 19 stemmer change) change derived text search data. After such an upgrade, stored tsvector columns and indexes must be rebuilt. Release activity: each major release from 9.6 to 19 has at least one text search, pg_trgm, fuzzystrmatch or unaccent item.
- What the source does not show: whether the 19 stemmer change carries its own reindex advice; the stemmer item gives none, while the locale item does. The 8.2 release date was not read from the page.
