# Area 1: Built-in and Contrib Text Search

This index covers assignment A1 of the [survey plan](../research-survey-plan.md). The fifteen records sit in [area-1/](area-1/) under the prefix `A1-SR-`. They were gathered on 2026-11-18. All fifteen are primary. Records of the postgres-and-qmd survey are cited as context with the prefix "qmd", for example qmd A1-SR-07.

## State of the Art

PostgreSQL 18 is the current release, and 19 is at release candidate 2 (qmd A1-SR-09). For these features the 18 and 19 manuals match, except for the Snowball language list and the stemmer update in 19 (A1-SR-08, A1-SR-14).

Four features ship with PostgreSQL. Full-text search is in core. pg_trgm, fuzzystrmatch and unaccent are contrib modules, installed with `CREATE EXTENSION` (A1-SR-01, A1-SR-04, A1-SR-05).

- **Full-text search** turns a document into a `tsvector` of normalized lexemes with positions, and a query into a `tsquery`. The `@@` operator matches them (A1-SR-06). Four functions build a `tsquery`. Only `websearch_to_tsquery` accepts raw user input without raising syntax errors (A1-SR-06, A1-SR-15). Phrase search uses `<->` and `<N>` (A1-SR-06).
- **Configurations** chain a parser with dictionaries. German and English stemming ship as Snowball dictionaries. The German stemmer does not split compound words. Compound splitting needs an Ispell or Hunspell dictionary whose files the operator supplies (A1-SR-08, A1-SR-09).
- **Ranking**: `ts_rank` and `ts_rank_cd` score one document at a time from term counts, positions and weights. They use no collection statistics, and the manual calls them "only examples" (A1-SR-07).
- **pg_trgm** measures similarity by shared three-character groups. It offers three similarity functions with thresholds 0.3, 0.6 and 0.5. Its GIN and GiST indexes serve similarity, `LIKE`, `ILIKE`, regular expressions and equality. Only GiST serves ordering by distance (A1-SR-01).
- **fuzzystrmatch** computes Levenshtein distance and phonetic codes. Soundex, Metaphone and Double Metaphone do not work well with UTF-8. Only Daitch-Mokotoff has a documented index path, through GIN (A1-SR-04).
- **unaccent** removes diacritics, as a filtering dictionary or as a `STABLE` function. Its rules live in a file on the server's disk (A1-SR-05).
- **GIN** is the preferred text search index. GiST is lossy and needs row rechecks (A1-SR-10). With `fastupdate` on, the default, GIN puts new entries in a pending list that every search scans. Cleanup moves them into the main index during vacuum, autoanalyze, a call to `gin_clean_pending_list`, or in the foreground once the list passes `gin_pending_list_limit` (4 MB) (A1-SR-11, A1-SR-12).
- **Generated columns**: a stored generated `tsvector` column keeps the vector in step with its text. Since 18, generated columns are virtual by default, and a virtual column cannot be indexed. So the pattern needs `STORED` (A1-SR-06, A1-SR-10).

### Transaction Boundary

Every feature in this area runs inside the PostgreSQL server and keeps one transaction boundary. GIN and GiST indexes, including GIN pending-list pages, are written to the write-ahead log (A1-SR-12). The core, not the index, decides row visibility (qmd A1-SR-07). A GIN search reads all pending entries, so a later statement in the writing transaction finds its own new rows through the index. This is inferred from the scan code; no source states it in one sentence (A1-SR-12). A stored generated `tsvector` is computed in the statement that writes the row (A1-SR-10).

Two parts sit outside the tables, though not outside the transaction. These are the dictionary and rules files under `$SHAREDIR/tsearch_data`, and any word list built from `ts_stat` for spelling suggestions (A1-SR-01, A1-SR-05, A1-SR-08). With `fastupdate` on, a `SERIALIZABLE` scan locks the whole GIN index, which can cause extra serialization failures (A1-SR-12).

### Simplicity Facts

| Fact                     | Full-text search (core)                                                                                                                   | pg_trgm                                                          | fuzzystrmatch                                                   | unaccent                                                              |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------- |
| Components               | Types, functions, parser, dictionaries; optional Ispell or Hunspell files supplied by the operator (A1-SR-06, A1-SR-08)                   | One extension, version 1.6 (A1-SR-01)                            | One extension, version 1.2 (A1-SR-04)                           | One extension, version 1.1, and a rules file (A1-SR-05)               |
| Query languages          | SQL with the `tsquery` syntax, or the web syntax of `websearch_to_tsquery` (A1-SR-06)                                                     | SQL operators and functions (A1-SR-01)                           | SQL functions (A1-SR-04)                                        | SQL function or dictionary (A1-SR-05)                                 |
| Consistency boundary     | One PostgreSQL transaction (A1-SR-10, A1-SR-12)                                                                                           | Same; the spelling word table is refreshed by hand (A1-SR-01)    | Same (A1-SR-04)                                                 | Same; the rules file is outside the tables (A1-SR-05)                 |
| Kept in sync             | `tsvector` with its text, by a stored generated column or an expression index. A thesaurus change requires a reindex (A1-SR-06, A1-SR-08) | Word table for suggestions (A1-SR-01)                            | Code columns, if stored (A1-SR-04)                              | Derived vectors after a rules change (A1-SR-14)                       |
| Rebuildable derived data | `tsvector` columns and GIN or GiST indexes. Rebuild them after upgrades that change stems or character classes: 18 and 19 (A1-SR-14)      | Trigram indexes; reindex advised after 18 and 19 (A1-SR-14)      | Indexes on these functions; reindex advised after 19 (A1-SR-14) | Vectors built through it (A1-SR-14, inferred for later rules changes) |
| Release activity         | Text search or contrib text items in every major release from 9.6 to 19 (A1-SR-14)                                                        | Changes in 9.1, 9.3, 9.6, 11, 14, 18 and 19 (A1-SR-02, A1-SR-14) | Changes in 8.4, 9.1, 16 and 19 (A1-SR-14)                       | Changes in 9.5, 9.6, 11, 12 and 17 (A1-SR-14)                         |
| Project health           | Part of the PostgreSQL distribution and open source, as are the contrib modules. Not found: per-module maintainer counts.                 | As left                                                          | As left                                                         | As left                                                               |

## Concept: Text Search in PostgreSQL

1. **contrib/tsearch**, the type `txtidx` with a GiST index (2001-10-12, A1-SR-13). Criticism: its own README calls it a prototype "rather experiment with various approaches" and deprecates it in favour of tsearch2 (A1-SR-13; the README's date is not known).
2. **contrib/tsearch2**: `tsvector`, `tsquery`, table-driven configuration, and the functions `rank` and `rank_cd` (2003-07-21, A1-SR-13). Criticism leading to step 3: gap. No record states why the code moved into core.
3. **Core text search in 8.3**, with configuration by SQL commands and dictionary files in one directory "to forestall security problems" (commit 2007-08-21, release 2008-02-04, A1-SR-13, A1-SR-14).
4. **contrib/tsearch2 removed in 10**, as a compatibility layer no longer needed (A1-SR-14). Criticism after this step: gap.

The concept has four formulations and one recorded criticism.

## Concept: Trigram Word Similarity

1. **`similarity()` over whole strings** with a threshold set by `set_limit` (2004-05-31, A1-SR-02). Criticism leading to step 2: gap. The commit gives only the new concept, "similarity over string and just a word from another string".
2. **`word_similarity()`** in 9.6, and the threshold becomes a setting, because `set_limit` dated from before modules could define settings (2016-03-16, A1-SR-02). Criticism: a user reports that word_similarity matches trigrams across several words, against the documented meaning (2017-10-27, A1-SR-03).
3. **`strict_word_similarity()`** in 11, forcing extent boundaries to word boundaries (2018-03-21, A1-SR-02). Criticism after this step: gap.

The concept has three formulations and one recorded criticism, plus one stated reason for the setting change.

## Concept: Trigram Index Searches

1. **GiST trigram index for similarity** (2004, A1-SR-02), with a GIN operator class added in 8.3 (A1-SR-14). Criticism: B-tree `LIKE` serves only left-anchored patterns (2011-02-01, A1-SR-02).
2. **`LIKE` and `ILIKE` through trigram indexes** (2011-02-01, A1-SR-02). The commit names its own limit: a pattern with no trigrams degrades to a full scan.
3. **Regular expressions through trigram indexes**, at first for GIN only (2013-04-09, A1-SR-02). Criticism: the commit says that GiST is not yet supported. In 9.4 the choice of trigrams for regular expressions improved (A1-SR-14). The commit that added GiST support was not looked up.
4. **Equality lookups** through trigram indexes (14, A1-SR-14). Criticism after this step: gap.

The concept has four formulations and two recorded criticisms, both from commit messages.

## Concept: GIN Write Path

1. **GIN with retail inserts** (8.2, A1-SR-14). Criticism: one row can cause many index inserts, and bulk insertion is faster (2009-03-24, A1-SR-12).
2. **`fastupdate` pending list** in 8.4 (2009-03-24, A1-SR-12). Criticism: the list size was tied to `work_mem`, "which was awkward" (9.5 notes, A1-SR-14).
3. **`gin_pending_list_limit`** in 9.5, per index or global (commit 2014-11-13, A1-SR-12, A1-SR-14). Criticism leading to step 4: gap. The 9.6 note gives no reason for manual cleanup.
4. **`gin_clean_pending_list()`** in 9.6 (A1-SR-14). Criticism after this step: the current manual names slower searches and foreground cleanup as disadvantages (A1-SR-11).

The concept has four formulations and three recorded criticisms.

## Concept: Query Parsing for User Input

1. **`to_tsquery` and `plainto_tsquery`** in 8.3 (A1-SR-13, A1-SR-14), and **`phraseto_tsquery`** with phrase search in 9.6 (A1-SR-14). Criticism: to_tsquery needs every operator written out, and the plain functions "are not flexible enough" (2017-07-19, A1-SR-15).
2. **Proposed `queryto_tsquery`** with an `AROUND(N)` operator (2017-07-19, A1-SR-15). Criticism: reviewers ask for the operator in a separate patch, and ask whether the function can raise a syntax error (2018-03-22 and 2018-03-26, A1-SR-15).
3. **`websearch_to_tsquery`** without `AROUND(N)` and without syntax errors (2018-04-05, A1-SR-15). Criticism: misparsed discarded tokens, fixed in 14 (A1-SR-14).

The concept has three formulations and three recorded criticisms.

## Concept: Phonetic Name Matching

1. **Soundex in its own contrib, then Levenshtein and Metaphone in fuzzystrmatch** (2001-08-07, A1-SR-04). The commit asks whether to fold the soundex contrib into the new one. Criticism: Soundex "is not very useful for non-English names", and the phonetic functions fail with multibyte encodings (current manual, A1-SR-04).
2. **Daitch-Mokotoff Soundex** in 16, an array of codes that GIN can index (2023-04-07, A1-SR-04). Criticism leading to step 3: gap. The 19 note states the change, not its reason.
3. **ASCII-only letters for soundex, metaphone and difference** in 19 (A1-SR-14).

The concept has three formulations and one recorded criticism. The manual criticism is undated, so its order against step 2 rests on the 2023 commit text.

## Concept: Ranking

1. **`rank` and `rank_cd`** in tsearch2 (2003-07-21, A1-SR-13).
2. **`ts_rank` and `ts_rank_cd`** in 8.3. The manual itself calls them "only examples" without "any global information" (2008-02-04, A1-SR-07). A source comment asks for a correction of the weight handling (A1-SR-07).
3. No later reformulation in core. 9.4 fixed `ts_rank_cd` for stripped lexemes (A1-SR-14).

The concept has two formulations and one recorded criticism. BM25 extensions belong to area 2.

## Concept: English and German Stemming

1. **The Porter stemmer** for English (A1-SR-09; its date is not recorded). Criticism: Porter names "a deficiency in the Porter stemmer" (A1-SR-09).
2. **Porter2** as Snowball's english algorithm, revised up to September 2002 (A1-SR-09). For German, a separate german2 variant handled transliterated umlauts (A1-SR-09).
3. **Snowball 3.0.0**: german2 merges into german, and English gains new exceptions. PostgreSQL 19 ships these rules, so stems change (A1-SR-08, A1-SR-09, A1-SR-14). Criticism leading to step 3: gap. The pages list the changes but not the reports behind them.

The concept has three formulations and one recorded criticism.

## Gaps

- **Ranking criticism in core**: a search for a pgsql-hackers proposal to add collection statistics or IDF to `ts_rank` found none. A 2011 thread only asked how `ts_rank` works and was not recorded. Vendor posts that criticize ts_rank were excluded under the brief.
- **Clarke, Cormack and Tudhope (1999)**, the cover density paper that the manual cites, was not read.
- **The move of tsearch2 into core**: no record gives the reason. The OpenFTS and sai.msu.su pages were not read.
- **German compound words**: no source evaluates a Hunspell German dictionary with PostgreSQL. How the default parser splits hyphenated compounds was not traced.
- **The unaccent rules file** was not read, so the mapping of German umlauts is not recorded.
- **Own-writes visibility through GIN** is inferred from code, not stated (A1-SR-12).
- **The reasons for `gin_clean_pending_list` (9.6) and for the 19 fuzzystrmatch change** were not found.
- **GiST support for trigram regular-expression search**: the commit was not looked up.
- **The 8.2 release date** was not read from the page.
- **Project health per module** (maintainers, open bugs): not searched; the modules ship in the PostgreSQL distribution.
- **Unreachable pages**: `gin-implementation.html`, `gin-tips.html` and `gist-intro.html` under `/docs/18/` returned no content, because the GIN and GiST chapters are now single pages. `/docs/8.2/tsearch2.html` returned no content; the README from the repository took its place.
