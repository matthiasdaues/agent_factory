# Survey Report: Postgres Text Search

This report answers [research-brief.json](research-brief.json) in survey mode. It uses only the 39 source records under [sources/](sources/), cited by record ID. It reports what the sources document and gives no verdict on whether any design holds; that verdict belongs to a later falsification study. Sections 1 to 5 recommend nothing. Section 6 draws conclusions and is marked as interpretation.

The report serves [the proposed store](../knowledge-graph-with-provenance/design-position.md#the-proposed-store): one PostgreSQL server with pgvector, one transaction boundary, and SQL as the only query language. So for each option the deciding fact is whether it keeps that one boundary. Records of the earlier [postgres-and-qmd survey](../postgres-and-qmd/survey-report.md) appear only as context, named in words, so that their IDs do not clash with the IDs of this survey.

## 1. Answer

Three features that ship with PostgreSQL give the store keyword, fuzzy, and ranked search: full-text search in core, and the contrib modules pg_trgm and fuzzystrmatch (A1-SR-06, A1-SR-01, A1-SR-04). They run inside the server, and their GIN index writes go to the write-ahead log (WAL) (A1-SR-12). Their ranking functions, `ts_rank` and `ts_rank_cd`, use no collection statistics, so they do not compute BM25 (A1-SR-07).

Four BM25 extensions have public repositories: ParadeDB pg_search, pg_textsearch, VectorChord-bm25, and pgx-bm25 (A2-SR-03, A2-SR-01, A2-SR-08, A2-SR-09). Each adds an index access method and needs no server outside PostgreSQL. They differ on the transaction boundary. pg_search states ACID behaviour, but an open issue reports index entries without table rows after crash recovery, and its Community edition has no physical replication (A2-SR-03, A2-SR-06). In pg_textsearch, compaction output survives a rollback, and corpus statistics ignore MVCC (A2-SR-01). pgx-bm25 states that it inherits WAL and replication from core, and it has one release (A2-SR-09). For VectorChord-bm25 the records show no transaction behaviour (A2-SR-08).

Four documented examples combine keyword and vector results in one SQL statement by reciprocal rank fusion (RRF). pgvector fuses built-in `ts_rank_cd` with a vector distance, and ParadeDB fuses its BM25 branch with a vector branch and weights per branch (A2-SR-10, A2-SR-07). A Tiger Cloud page fuses pg_textsearch with a pgvector HNSW branch, and a Tiger tutorial fuses it with a pgvectorscale `diskann` branch (A2-SR-19, A2-SR-23). No record shows a score-based fusion in SQL. Section 4 compares the costs.

## 2. State of the art by area

### 2.1 Built-in and contrib text search

**Full-text search** turns a document into a `tsvector` of normalised words (lexemes) with positions, and a query into a `tsquery`; the `@@` operator matches them (A1-SR-06). Four functions build a `tsquery`. Only `websearch_to_tsquery` takes raw user input, because it never raises a syntax error (A1-SR-06). Phrase search uses the operators `<->` and `<N>` (A1-SR-06, A1-SR-15). A configuration selects a parser and a list of dictionaries, and an expression index works only with a function call that names its configuration (A1-SR-06). The `tsvector` limits bound long documents: at most 256 positions per lexeme, and positions up to 16,383 (A1-SR-10).

**German and English stemming** ship as Snowball dictionaries (A1-SR-08). The German stemmer does not split compound words, because "To split up compound words cannot be done without a dictionary" (A1-SR-09). Compound splitting needs an Ispell or Hunspell dictionary. PostgreSQL ships no such files, so the operator places them on the server's disk (A1-SR-08). The stemmer lower-cases words first, which loses the capital letter of German nouns (A1-SR-09). PostgreSQL 19 syncs with a Snowball commit of 2025-12-15, and its English and German stemmers "produce different stems for some words" (A1-SR-08, A1-SR-14).

**unaccent** removes diacritics, either as a filtering dictionary inside a configuration or as a function (A1-SR-05). The install script declares the function `STABLE`, so it cannot appear directly in an index expression. That consequence is inferred from the general rule for index expressions (A1-SR-05). The rules file lives in `$SHAREDIR/tsearch_data/`, outside the tables (A1-SR-05). The record does not show how it maps German umlauts.

**Ranking.** `ts_rank` counts matching lexemes, and `ts_rank_cd` also weighs their proximity (A1-SR-07). Both read one document's `tsvector` and no collection statistics. The manual calls them "only examples" and says they "do not use any global information" (A1-SR-07). The default normalisation ignores document length (A1-SR-07). Ranking reads the `tsvector` of every matching row, which "can be I/O bound and therefore slow" (A1-SR-07).

**pg_trgm** measures similarity by shared three-character groups (trigrams). It has three similarity functions with default thresholds of 0.3, 0.6, and 0.5 (A1-SR-01). GIN and GiST trigram indexes serve similarity, `LIKE`, `ILIKE`, regular expressions, and equality, and the search string need not be left-anchored (A1-SR-01). Only GiST serves ordering by distance with `<->` (A1-SR-01). The manual's spelling-suggestion pattern keeps a separate word table that "will need to be periodically regenerated" (A1-SR-01).

**fuzzystrmatch** computes Levenshtein distance and phonetic codes (A1-SR-04). Soundex, Metaphone, and Double Metaphone "do not work well with multibyte encodings (such as UTF-8)" (A1-SR-04). Only Daitch-Mokotoff codes have a documented index path, through GIN (A1-SR-04). For the other functions the manual gives no index, so a query compares row by row (inferred, A1-SR-04).

**GIN and GiST under writes.** GIN is the preferred text search index, and GiST is lossy and rechecks table rows (A1-SR-10). With `fastupdate` on, the default, GIN puts new entries in a pending list that every search scans (A1-SR-11). Vacuum, autoanalyze, a call to `gin_clean_pending_list`, or a list larger than `gin_pending_list_limit` (4 MB by default) moves them into the main index (A1-SR-11). The pending-list pages are written to the WAL (A1-SR-12). A GIN scan reads the whole pending list, so a later statement in the writing transaction finds its own new rows through the index. That is inferred from the scan code; no source states it in one sentence (A1-SR-12). Under `SERIALIZABLE`, `fastupdate` makes a scan lock the whole index, which "could get a lot of false positives" (A1-SR-12). GiST inserts each entry at once and has no pending list (A1-SR-11).

**Generated columns.** A stored generated `tsvector` column is computed when the row is written (A1-SR-10). Since 18 a generated column is virtual by default, and an index on a virtual generated column raises an error, so the pattern needs `STORED` (A1-SR-10).

**Upgrades change derived data.** The 18 and 19 release notes advise a reindex of all full-text and pg_trgm indexes after `pg_upgrade`, and 19 also advises recomputing stored `tsvector` values (A1-SR-14).

### 2.2 BM25 extensions and keyword with vector in one query

Four BM25 extensions have commits in 2026 (A2-SR-02, A2-SR-08, A2-SR-09, A2-SR-18). All four add an index access method and a scoring operator (A2-SR-01, A2-SR-03, A2-SR-08, A2-SR-09).

**ParadeDB pg_search** builds LSM segments with the Tantivy library inside PostgreSQL block storage (A2-SR-03, A2-SR-04). It uses its own tokenizers and operators (A2-SR-03). The vendor states that writes "go through Postgres’ transaction engine" and are atomic (A2-SR-03). Two open issues report otherwise in edge cases. In the Community edition, creating an index stops a physical standby for every relation, because the index writes a custom WAL record (A2-SR-06, issue #6007). After crash recovery, the index can hold documents with no table row (A2-SR-06, issue #7093). Physical replication is an Enterprise feature; Community supports logical replication on PostgreSQL 17 and later (A2-SR-03, A2-SR-18).

**pg_textsearch** keeps an LSM memtable and segments in index pages and tokenizes with PostgreSQL text search configurations (A2-SR-01). It writes through generic WAL and has no custom resource manager (A2-SR-01). Two exceptions to MVCC are stated. Compaction output is "not undone by `ROLLBACK`", and the corpus statistics are "not MVCC-filtered" (A2-SR-01). Standbys need `hot_standby_feedback = on`, and `PREPARE TRANSACTION` is not supported after creating an index (A2-SR-01). The extension must be preloaded, which needs a server restart (A2-SR-01).

A Tiger Cloud page documents the older v1.1.0 (A2-SR-19). It creates "one partial index per language", each with its own `text_config`. The implicit `<@>` form skips partial indexes, so queries on them name the index with `to_bm25query()`. The implicit form also does not run inside PL/pgSQL functions, procedures, or `DO` blocks. The page states that phrase search is missing and that inserts fail above a memory cap (A2-SR-19).

**VectorChord-bm25** indexes a separate `bm25vector` column, which the second extension pg_tokenizer fills (A2-SR-08). A trigger or an `UPDATE` keeps that column in step with the text (A2-SR-08). Index pages go through generic WAL, read from the source code (A2-SR-08). The README states nothing about rollback, replication, or `pg_dump`, and says "We currently have only tested against English" (A2-SR-08).

**pgx-bm25** (extension `bm25_native`) keeps a pending list and sealed segments in its own index pages, and states that it "inherits WAL, crash recovery, and physical replication from core" (A2-SR-09). Its tokenizer uses PostgreSQL text search dictionaries (A2-SR-09). A ranked scan that reads past its top-k limit can score rows "under the new corpus statistics", even under `REPEATABLE READ` (A2-SR-09). `pg_dump` emits `CREATE INDEX`, so a restore rebuilds the index (A2-SR-09). Development happens in a private repository (A2-SR-09).

**Keyword and vector in one statement.** Two records quote a full statement, and section 5 holds both (A2-SR-10, A2-SR-07). Two vendor pages add a pg_textsearch statement, which section 5 describes (A2-SR-19, A2-SR-23). All are plain SQL with common table expressions and need no fusion function from an extension.

**pgvectorscale** adds a `diskann` vector index on top of pgvector; it is not a BM25 extension (A2-SR-20, A2-SR-21). It needs a superuser to install and builds for PostgreSQL 14 to 18 (A2-SR-21). Index writes use generic WAL, read from code (A2-SR-21). Label filters use a `smallint[]` column in the index (A2-SR-20), and the scan reads only the first `&&` condition (inferred from code, A2-SR-21). The maintainers call it "still at an early stage" (A2-SR-20).

## 3. Hardened concepts

The table below is the output of `concept-history-check --table`. Each history lives in [histories/](histories/).

| Rank | Concept                                  | Area                                                         | Rounds | Criticisms | Primary anchors | Criticism coverage | Records                                |
| ---- | ---------------------------------------- | ------------------------------------------------------------ | ------ | ---------- | --------------- | ------------------ | -------------------------------------- |
| 1    | BM25 term weighting                      | Area 2: BM25 extensions and keyword with vector in one query | 3      | 3          | 100%            | 100%               | A2-SR-16, A2-SR-14, A2-SR-15           |
| 2    | Query parsing for user input             | Area 1: built-in and contrib text search                     | 3      | 3          | 100%            | 100%               | A1-SR-15, A1-SR-14                     |
| 3    | pg_textsearch durability and replication | Area 2: BM25 extensions and keyword with vector in one query | 3      | 2          | 100%            | 100%               | A2-SR-17, A2-SR-02                     |
| 4    | GIN write path                           | Area 1: built-in and contrib text search                     | 4      | 3          | 100%            | 67%                | A1-SR-14, A1-SR-12, A1-SR-11           |
| 5    | Rank fusion                              | Area 2: BM25 extensions and keyword with vector in one query | 4      | 2          | 100%            | 67%                | A2-SR-12, A2-SR-11, A2-SR-13, A2-SR-07 |
| 6    | Trigram index searches                   | Area 1: built-in and contrib text search                     | 4      | 2          | 100%            | 67%                | A1-SR-02, A1-SR-14                     |
| 7    | ParadeDB index storage and WAL           | Area 2: BM25 extensions and keyword with vector in one query | 3      | 2          | 100%            | 50%                | A2-SR-05, A2-SR-04, A2-SR-18, A2-SR-06 |

Below the entry rule (at least 3 formulations and 2 recorded criticisms):

| Rank | Concept                          | Area                                     | Rounds | Criticisms | Primary anchors | Criticism coverage | Records            |
| ---- | -------------------------------- | ---------------------------------------- | ------ | ---------- | --------------- | ------------------ | ------------------ |
| -    | English and German stemming      | Area 1: built-in and contrib text search | 3      | 1          | 100%            | 50%                | A1-SR-09           |
| -    | Phonetic name matching           | Area 1: built-in and contrib text search | 3      | 1          | 100%            | 50%                | A1-SR-04, A1-SR-14 |
| -    | Trigram word similarity          | Area 1: built-in and contrib text search | 3      | 1          | 100%            | 50%                | A1-SR-02, A1-SR-03 |
| -    | Text search in PostgreSQL        | Area 1: built-in and contrib text search | 4      | 1          | 100%            | 33%                | A1-SR-13, A1-SR-14 |
| -    | Ranking in core full-text search | Area 1: built-in and contrib text search | 2      | 1          | 100%            | 0%                 | A1-SR-13, A1-SR-07 |

The histories follow the stakeholder's frame of conjecture and criticism. Each step is a formulation, and each criticism is a recorded objection to it. The "Primary anchors" column reads the start of each record's `source_family`. The check requires each date to equal the record's `publication_date` or `relevant_event_date`. Several records bundle events of many years, so some history dates are record dates, not event dates. The sections below give the event dates the records state.

### 3.1 BM25 term weighting

At TREC-1 the Okapi team used the Robertson-Sparck Jones weight, called BM1, with no term frequency or document length (A2-SR-14). The TREC-3 paper later notes that this scheme "tends to favour long documents" (A2-SR-14). At TREC-2 the team defined BM11 and BM15 from the 2-Poisson model, and wrote that the argument is "not by any stretch of the imagination a strong quantitative argument" (A2-SR-16). At TREC-3 the authors combined BM11 and BM15 into BM25 through the parameter b, because BM11's length model "might be expected to exaggerate the document length effect" (A2-SR-14). In 2009, Robertson and Zaragoza wrote that the model "provides no guidance" on setting k1 and b (A2-SR-15). BM25F is known here only from a paraphrase in A2-SR-15, so it is not a step. All anchors come from one team.

### 3.2 Query parsing for user input

`to_tsquery` needs every operator written out, and `plainto_tsquery` and `phraseto_tsquery` accept no operators. A 2017 proposal criticised both and called the plain functions "not flexible enough" (A1-SR-15). The proposal led to `websearch_to_tsquery` in release 11 (A1-SR-15, A1-SR-14). In review, the `AROUND(N)` operator went to a separate patch, and the function stopped raising syntax errors (A1-SR-15). The review messages are not steps, because their dates are not record dates. Release 14 fixed a parsing error in the function (A1-SR-14). The history lists `to_tsquery` and the plain functions as two steps, while the area index groups them as one. The 2017 proposal names both as functions that already exist, so the two steps stand side by side, not in time order (A1-SR-15). Phrase search arrived in 9.6 (A1-SR-14).

### 3.3 pg_textsearch durability and replication

In March 2026 an issue stated that index buffers were written with no WAL, so "replicas don't see buffer modifications" (A2-SR-17). Release v1.2.0 added custom WAL entries for physical replication, which its note calls "essentially broken in previous releases" (A2-SR-02). The v1.3.0 note says those entries do not suit the stateless WAL redo of Aurora, AlloyDB, Neon, and HorizonDB, and replaces them with a paged memtable on generic WAL (A2-SR-02). The current files describe that design (A2-SR-01). All criticism comes from the project itself.

### 3.4 GIN write path

GIN arrived in 8.2 (A1-SR-14). The `fastupdate` commit of 2009 says bulk insert is "significantly faster than retail insert" and adds the pending list (A1-SR-12). Release 9.5 replaced the `work_mem` bound on the list, "which was awkward", with `gin_pending_list_limit` (A1-SR-14). Release 9.6 added `gin_clean_pending_list()`, and no record states why (A1-SR-14). The current manual names slower searches as "the main disadvantage" of the list (A1-SR-11). The history dates the 9.5 and 9.6 steps 2026-10-09, the date of the release-notes record.

### 3.5 Rank fusion

Fox and Shaw summed the scores of several runs as CombSUM and CombMNZ at TREC-2 (A2-SR-12). Cormack and colleagues defined RRF in 2009 with k = 60, and noted that CombMNZ sums "uncalibrated scores" (A2-SR-11). The RRF paper presents RRF as a baseline, not as an answer to CombMNZ, so the history does not count that criticism as the cause of RRF. Bruch and colleagues argued in 2023 that RRF "discards useful information" and found a convex combination of normalised scores better on their datasets (A2-SR-13). Two of those authors work for a vector database vendor (A2-SR-13). ParadeDB's current page adds a weight per branch to RRF and cites no paper (A2-SR-07). The pgvector example of 2024 applies plain RRF, so it is an application, not a step (A2-SR-10).

### 3.6 Trigram index searches

The 2004 module offered index classes for similarity (A1-SR-02). A 2011 commit added `LIKE` and `ILIKE`, and named its own limit: a pattern with no trigrams "degrades to a full-table scan" (A1-SR-02). A 2013 commit added regular expressions for GIN only (A1-SR-02). The current manual lists both index types for regular expressions; the commit that added GiST was not read (A1-SR-01). Release 14 added equality lookups (A1-SR-14). Three steps carry the date of the commit-history record, 2004-05-31.

### 3.7 ParadeDB index storage and WAL

Version 0.6.0 renamed pg_bm25 to pg_search and stored the index as a PostgreSQL index type (A2-SR-05). Release 0.14.0 moved the index to block storage and gave Enterprise WAL, replication, and recovery (A2-SR-04). Release 0.17.0 replaced the PostgreSQL free space map, because it "is not write-ahead logged" (A2-SR-04). Release 0.24.0 made Community write WAL for crash recovery (A2-SR-18). Issues #6007 and #7093 followed, and both were open on 2026-11-18 (A2-SR-06). No record states the criticism that led to block storage.

### 3.8 Concepts below the entry rule

- **English and German stemming.** Porter2 replaced the Porter stemmer for English after "twenty years of use" (A1-SR-09). Snowball 3.0.0 merged german2 into german (A1-SR-09). No record states the criticism behind 3.0.0.
- **Phonetic name matching.** Levenshtein and Metaphone arrived in 2001 (A1-SR-04), and Daitch-Mokotoff in 16 (A1-SR-14). In 19 the older functions treat only ASCII letters as letters (A1-SR-14). The only criticism is the manual's note on non-English names (A1-SR-04). Two steps carry the record date 2023-04-07.
- **Trigram word similarity.** A 2017 bug report found that `word_similarity` matched across words, and `strict_word_similarity` followed in 11 (A1-SR-03, A1-SR-02). The `word_similarity` commit is of 2016-03-16; the history dates it 2004-05-31, the record date.
- **Text search in PostgreSQL.** contrib/tsearch (2001) gave way to tsearch2 (2003), then to core in 8.3, and release 10 removed tsearch2 (A1-SR-13, A1-SR-14). No record states why the code moved into core.
- **Ranking in core full-text search.** `rank` and `rank_cd` became `ts_rank` and `ts_rank_cd` in 8.3, and no reformulation followed (A1-SR-13, A1-SR-07).

## 4. The comparison

"Inferred" marks a fact that a record reads from code or derives from a general rule. "Not found" means the survey found no record for the fact. The column "Consistency boundary" names the boundary the option's data lives in. The column "Transaction boundary" says whether the option keeps the store's one PostgreSQL transaction. pgvectorscale, a vector index, has no row; section 2.2 lists its facts.

| Option                          | Components                                                                                                                                           | Query languages                                                                         | Consistency boundary                                                                                                          | Kept in sync                                                                                                                                      | Rebuildable derived data                                                                                                                                            | Transaction boundary                                                                                                                                                                           | Replication and pg_dump                                                                                                                                                                                              | PostgreSQL versions                                                            | Licence                                                    | Release activity                                                                                                                       | Project health                                                                                 |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| pg_trgm                         | One contrib extension, version 1.6 (A1-SR-01)                                                                                                        | SQL functions and operators such as `%` and `<->` (A1-SR-01)                            | The PostgreSQL transaction (A1-SR-12 for GIN; inferred for GiST)                                                              | A word table for spelling suggestions, regenerated by hand (A1-SR-01)                                                                             | Trigram indexes; reindex advised after upgrades to 18 and 19 (A1-SR-14)                                                                                             | Kept: GIN pages are WAL-logged (A1-SR-12). GiST: not found                                                                                                                                     | GIN changes travel in the WAL, so physical replication follows (inferred, A1-SR-12). pg_dump: not found                                                                                                              | Ships with PostgreSQL; 18 and 19 pages match (A1-SR-01)                        | Not found; ships in the PostgreSQL distribution (A1-SR-01) | Changes in 8.3, 8.4, 9.1, 9.4, 11, 14, 18, 19 (A1-SR-14); 9.3 and 9.6 inferred from commit dates (A1-SR-02)                            | Module authors named (A1-SR-01); maintainer counts not found                                   |
| fuzzystrmatch                   | One contrib extension, version 1.2 (A1-SR-04)                                                                                                        | SQL functions (A1-SR-04)                                                                | The PostgreSQL transaction (inferred, A1-SR-04)                                                                               | Stored code columns, if used (A1-SR-04)                                                                                                           | Stored codes of `soundex`, `metaphone`, `dmetaphone`, and `dmetaphone_alt`; 19 changes how these functions treat letters, so a rebuild follows (inferred, A1-SR-14) | Kept (inferred: server functions; the GIN index as in A1-SR-12)                                                                                                                                | Not found                                                                                                                                                                                                            | Ships with PostgreSQL; 18 and 19 pages match (A1-SR-04)                        | Not found; ships in the PostgreSQL distribution (A1-SR-04) | Changes in 8.4, 9.1, 16, 19 (A1-SR-14)                                                                                                 | Not found                                                                                      |
| Full-text search with `ts_rank` | Core types, parser, and dictionaries; operator-supplied Ispell or Hunspell files; optional unaccent with a rules file (A1-SR-06, A1-SR-08, A1-SR-05) | SQL with `tsquery` syntax, or web syntax through `websearch_to_tsquery` (A1-SR-06)      | The PostgreSQL transaction; dictionary and rules files on the server's disk (A1-SR-05, A1-SR-08, A1-SR-12)                    | `tsvector` with its text, by a stored generated column or an expression index (A1-SR-06, A1-SR-10); a thesaurus change needs a reindex (A1-SR-08) | `tsvector` columns and GIN or GiST indexes; recompute after upgrades to 18 and 19 (A1-SR-14)                                                                        | Kept: stored `tsvector` computed in the writing statement (inferred, A1-SR-10); pending list WAL-logged, own rows found (inferred, A1-SR-12); whole-index lock under `SERIALIZABLE` (A1-SR-12) | Physical replication follows from the WAL (inferred, A1-SR-12). pg_dump: not found                                                                                                                                   | Core since 8.3 (A1-SR-13); 18 and 19 match except the Snowball list (A1-SR-08) | Not found; part of the core server (A1-SR-13)              | At least one item in each major release from 9.6 to 19, counting text search, pg_trgm, fuzzystrmatch, and unaccent together (A1-SR-14) | GIN maintainers named (A1-SR-11); counts not found                                             |
| ParadeDB pg_search              | One extension built on pgrx, Tantivy, and DataFusion; pgvector for vector types; Enterprise edition for physical replication (A2-SR-03, A2-SR-07)    | SQL with its own operators `\|\|\|`, `###`, `@@@`, and `pdb.score` (A2-SR-03, A2-SR-07) | The PostgreSQL transaction, as the vendor states (A2-SR-03)                                                                   | Index updated within the transaction (A2-SR-03); own WAL-logged free space map (A2-SR-04)                                                         | Index, rebuilt by `REINDEX` (A2-SR-06); the 0.14.0 upgrade dropped and recreated every index (A2-SR-04)                                                             | Stated kept (A2-SR-03); open issue #7093 reports index entries without table rows after crash recovery (A2-SR-06)                                                                              | Community: logical only, PostgreSQL 17 and later; index creation stops a physical standby (A2-SR-18, A2-SR-06). Enterprise: physical (A2-SR-03). pg_dump: advised for loading data; index dump not stated (A2-SR-03) | 15 to 18 (A2-SR-03)                                                            | AGPL-3.0; Enterprise commercial (A2-SR-03)                 | 153 releases from 2024-11-18 to 2026-11-18; v0.26.8 on 2026-11-18 (A2-SR-18)                                                           | 161 contributors; 2,714 commits since 2024-11-18; 261 open issues and pull requests (A2-SR-18) |
| pg_textsearch                   | One extension, preloaded with a server restart; pg_durable only for background compaction (A2-SR-01)                                                 | SQL with `<@>`, `to_bm25query()`, and the `@@` `tsquery` filter (A2-SR-01, A2-SR-19)    | The PostgreSQL transaction, except compaction output and corpus statistics (A2-SR-01)                                         | Nothing outside the index stated; standbys need `hot_standby_feedback` (A2-SR-01)                                                                 | Index, rebuilt by `REINDEX`; memtable cache rebuilt from the page chain (A2-SR-01)                                                                                  | Partly: rollback test suite (A2-SR-02); compaction survives `ROLLBACK`, statistics not MVCC-filtered, no `PREPARE TRANSACTION` (A2-SR-01); own-write visibility not found                      | Physical since v1.2.0, generic WAL since v1.3.0 (A2-SR-02, A2-SR-01). Logical: v0.6.1 added replication tests, but the logical behaviour itself is not stated (A2-SR-02). pg_dump: not stated (A2-SR-01, A2-SR-19)   | 17, 18, 19 RC2 (A2-SR-01); 17 and 18 on the v1.1.0 page (A2-SR-19)             | PostgreSQL (A2-SR-01)                                      | 23 releases from 2025-10-14 to 2026-10-02 (A2-SR-02)                                                                                   | 17 contributors; 364 commits since 2024-11-18; first general release 2026-03-27 (A2-SR-02)     |
| VectorChord-bm25                | Two extensions, vchord_bm25 and pg_tokenizer, and a token column (A2-SR-08)                                                                          | SQL with `<&>`, `bm25query`, and `tokenize`; the README may lag a new API (A2-SR-08)    | Not found; index pages on generic WAL (inferred from code, A2-SR-08)                                                          | Token column with its text, by trigger or `UPDATE` (A2-SR-08)                                                                                     | Token column and index (inferred, A2-SR-08); open issue #124: a session cannot `REINDEX` after churn (A2-SR-08)                                                     | Not found                                                                                                                                                                                      | Not found                                                                                                                                                                                                            | 14 to 18 (A2-SR-08)                                                            | AGPLv3 or Elastic License v2 (A2-SR-08)                    | 6 releases; last 0.3.0 on 2025-12-15; last commit 2026-04-28 (A2-SR-08)                                                                | 9 contributors; repository moved organisation, reason not stated (A2-SR-08)                    |
| pgx-bm25                        | One extension in C; no separate runtime (A2-SR-09)                                                                                                   | SQL with `@@@` and `&@@` (A2-SR-09)                                                     | The PostgreSQL transaction for index pages, as stated; corpus statistics not bound to the snapshot in ranked scans (A2-SR-09) | Nothing outside the index stated; pending list sealed by size and `VACUUM` (A2-SR-09)                                                             | Index, rebuilt on restore from `CREATE INDEX` (A2-SR-09)                                                                                                            | Partly: WAL and crash recovery stated; rows can be rescored within one statement; rollback not stated (A2-SR-09)                                                                               | Physical replication stated as inherited; pg_dump emits `CREATE INDEX` (A2-SR-09)                                                                                                                                    | 17, 18, 19 (A2-SR-09)                                                          | PostgreSQL (A2-SR-09)                                      | 1 release, v1.0.0 on 2026-10-06 (A2-SR-09)                                                                                             | 1 public account; private development; 14 stars (A2-SR-09)                                     |

## 5. Keyword and vector in one statement

**The pgvector example** fuses a pgvector ranking with built-in `ts_rank_cd` (A2-SR-10). The statement, as the record quotes it:

```sql
WITH semantic_search AS (
    SELECT id, RANK () OVER (ORDER BY embedding <=> %(embedding)s) AS rank
    FROM documents
    ORDER BY embedding <=> %(embedding)s
    LIMIT 20
),
keyword_search AS (
    SELECT id, RANK () OVER (ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC)
    FROM documents, plainto_tsquery('english', %(query)s) query
    WHERE to_tsvector('english', content) @@ query
    ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC
    LIMIT 20
)
SELECT
    COALESCE(semantic_search.id, keyword_search.id) AS id,
    COALESCE(1.0 / (%(k)s + semantic_search.rank), 0.0) +
    COALESCE(1.0 / (%(k)s + keyword_search.rank), 0.0) AS score
FROM semantic_search
FULL OUTER JOIN keyword_search ON semantic_search.id = keyword_search.id
ORDER BY score DESC
LIMIT 5
```

The example sets k = 60 (A2-SR-10). It needs one table `documents` with `id`, `content`, and a pgvector column `embedding`, plus a GIN index on `to_tsvector('english', content)` (A2-SR-10). The `FULL OUTER JOIN` with `COALESCE` scores a row that only one branch found (A2-SR-10). The expression index stores no `tsvector`, so the ranking computes `to_tsvector` again for each matching row (inferred, A1-SR-06, A1-SR-07).

**The ParadeDB example** fuses its BM25 branch and a vector branch with weights (A2-SR-07):

```sql
WITH text AS (
    SELECT id, RANK() OVER (ORDER BY pdb.score(id) DESC, id) AS rank
    FROM mock_items
    WHERE description ||| 'running shoes'
    ORDER BY pdb.score(id) DESC, id
    LIMIT 20
),
vector AS (
    SELECT id, RANK() OVER (ORDER BY embedding <=> '[1,2,3,4,5,6,7,8]', id) AS rank
    FROM mock_items
    WHERE id @@@ pdb.all()
    ORDER BY embedding <=> '[1,2,3,4,5,6,7,8]', id
    LIMIT 20
),
fused AS (
    SELECT id, sum(weight) AS score
    FROM (
        SELECT id, 1.0 / (60 + rank) AS weight FROM text
        UNION ALL
        SELECT id, 0.7 / (60 + rank) AS weight FROM vector
    ) u
    GROUP BY id
)
SELECT m.id, m.description, f.score
FROM fused f
JOIN mock_items m USING (id)
ORDER BY f.score DESC, m.id
LIMIT 5;
```

It needs a table with `id`, `description`, and a pgvector-typed `embedding`, a ParadeDB index, and ParadeDB's vector search, a beta feature from 0.25.0 (A2-SR-07). ParadeDB uses "pgvector's vector types, but not its HNSW or IVF indexes" (A2-SR-07). So the store's HNSW index on `embedding` would not serve this vector branch (inferred, A2-SR-07). The record does not quote the index definition.

**The Tiger Cloud example** fuses a pg_textsearch branch with a pgvector HNSW branch, and the record quotes it in parts (A2-SR-19). Each branch ranks with `ROW_NUMBER()` and `LIMIT 20`. A `LEFT JOIN` to the base table scores "COALESCE(1.0 / (60 + v.rank), 0.0) + COALESCE(1.0 / (60 + k.rank), 0.0)". A weighted variant gives the vector term 0.7 (A2-SR-19). The table needs `content`, `embedding`, an `hnsw` index, and a `bm25` index `WITH (text_config='english')` (A2-SR-19). The page installs `vectorscale`, but the statement uses no pgvectorscale feature (inferred, A2-SR-19, A2-SR-24).

**The Tiger tutorial** runs the same form on a pgvectorscale `diskann` index, with no filter in the vector branch (A2-SR-23).

**The fusion formulas and their sources.**

- RRF: the score of a document is the sum over the rankings of 1 / (k + rank), with k = 60 "fixed during a pilot investigation" (A2-SR-11). No SQL example cites the paper (A2-SR-07, A2-SR-10, A2-SR-19, A2-SR-23).
- Weighted RRF: "Each branch contributes `weight / (k + rank)`" (A2-SR-07). The example weights the text branch 1.0 and the vector branch 0.7. The Tiger Cloud page also weights the vector branch 0.7 (A2-SR-19). Neither page cites a source for the weights, and the survey found no original source for weighted RRF (A2-SR-07, A2-SR-19).
- CombSUM and CombMNZ add raw similarity scores; CombMNZ multiplies the sum by the number of runs that found the document (A2-SR-12).
- Convex combination: α times the semantic score plus (1 − α) times the lexical score, after min-max normalisation (A2-SR-13). The authors tuned α to 0.8 on their datasets (A2-SR-13). The paper credits an earlier study of the convex combination, Chen et al. 2022, which the survey did not read (A2-SR-13).

**What no record shows.** No record shows a convex combination or any score-based fusion written in SQL. No record shows a fused statement for VectorChord-bm25 or pgx-bm25. The pg_textsearch statements come from vendor pages and were not run (A2-SR-19, A2-SR-23). No record shows a fused statement whose vector branch filters rows, for example by embedding model. No record states that a fused statement reads one snapshot; that follows from single-statement semantics (inferred, A2-SR-07). No record runs a fused statement in the same transaction as the writes it should find. No record evaluates the weights or k for any corpus of the store's kind. The pgvector README names a cross-encoder as a second option (A2-SR-10). The record says that example reranks in Python, outside SQL, but it takes this from the file name and did not read the file (A2-SR-10).

## 6. What this means for the store sketch

*This section is interpretation. Each point names the findings it rests on.*

**One transaction boundary.** Built-in full-text search, pg_trgm, and fuzzystrmatch keep the sketch's single boundary and add no server and no query language beyond SQL (section 2.1, A1-SR-12). The keyword index and the stored `tsvector` commit and roll back with the text row. A statement later in the writing transaction should find the new row through GIN, but that rests on reading code (A1-SR-12). Among the BM25 extensions, pgx-bm25 states the closest fit, but it has one release, one public account, and statistics that can shift inside a statement (A2-SR-09). pg_textsearch keeps the boundary for rows and states two exceptions: compaction and corpus statistics (A2-SR-01). pg_search's Community edition conflicts with the brief's cost of error. It stops a physical standby when an index is created, and an open issue reports index entries without table rows after a crash (A2-SR-06). For VectorChord-bm25 the boundary is not documented, and it adds a second extension and a column to keep in sync (A2-SR-08). A `diskann` branch would add pgvectorscale, whose WAL behaviour rests on code reading (A2-SR-21). The pilot filters by embedding model with pgvector's `hnsw.iterative_scan` alone (context, not a record).

**A German and English corpus.** The built-in `german` and `english` configurations stem both languages but do not split German compounds (A1-SR-08, A1-SR-09). Compound splitting needs Hunspell files on the server's disk, outside the tables (A1-SR-08). An expression index is fixed to one configuration (A1-SR-06). So a mixed corpus needs a language column and a stored generated `tsvector` that picks the configuration per row, or one index per language. pg_textsearch documents the per-language form, with queries that name the index (A2-SR-19). No record tests either design with German text. pg_textsearch and pgx-bm25 reuse PostgreSQL configurations and dictionaries, so they would inherit the same German behaviour (A2-SR-01, A2-SR-09). VectorChord-bm25 has been tested only on English (A2-SR-08), and the records do not show German support in pg_search. The upgrade to 19 changes German and English stems, so stored vectors need a recompute (A1-SR-14).

**qmd's ideas.** The postgres-and-qmd survey records that qmd runs BM25 over SQLite FTS5, fuses with RRF weighted by query type, and reranks. In the store, keyword search maps to full-text search, or to BM25 through an extension. Fusion maps to the pgvector RRF statement, which needs no extension beyond pgvector (A2-SR-10). BM25 fusion maps to the Tiger Cloud statement for pg_textsearch (A2-SR-19). Weighting maps to the weighted forms of ParadeDB and Tiger Cloud (A2-SR-07, A2-SR-19). Both fusion steps are plain SQL, so either would work with a built-in keyword branch (inferred, A2-SR-07). qmd's BM25 corpus statistics have no built-in counterpart, because `ts_rank` uses none (A1-SR-07). No record covers reranking inside SQL (A2-SR-10).

**Pilot tests that follow.** They extend the sketch's first pilot test.

1. An RRF statement that fuses `ts_rank_cd` and pgvector HNSW finds a row inserted earlier in the same transaction, in both branches (A1-SR-12, A2-SR-10).
2. After `ROLLBACK`, no keyword or vector query finds the rolled-back row (A1-SR-10, A1-SR-12).
3. Under `SERIALIZABLE`, compare the serialization failures with `fastupdate` on and off (A1-SR-12).
4. A German sample corpus shows which compound queries miss without Hunspell (A1-SR-09).
5. A `pg_upgrade` from 18 to 19 shows which stored vectors change (A1-SR-14).
6. If the pilot needs BM25 statistics, run tests 1 and 2 and a crash and standby test against pgx-bm25 and pg_textsearch, with the Tiger Cloud statement for pg_textsearch (A2-SR-01, A2-SR-09, A2-SR-19).

## 7. Structured block

```json
{
  "findings": [
    {
      "title": "Built-in full-text search keeps one transaction boundary",
      "summary": "Full-text search runs in the core server. GIN pending-list pages are written to the WAL, and a stored generated tsvector is computed in the statement that writes the row. That a later statement in the writing transaction finds its own rows through GIN is inferred from the scan code. With fastupdate on, a SERIALIZABLE scan locks the whole GIN index.",
      "source_record_refs": ["A1-SR-06", "A1-SR-10", "A1-SR-11", "A1-SR-12"]
    },
    {
      "title": "German and English stemming ship as Snowball dictionaries without compound splitting",
      "summary": "The german and english configurations use Snowball stemmers. The German stemmer does not split compounds; that needs operator-supplied Ispell or Hunspell files on the server's disk. That PostgreSQL 19 ships Snowball 3.0.0 rules is inferred from the sync commit and the release note; the 19 release note states that some stems change.",
      "source_record_refs": ["A1-SR-08", "A1-SR-09", "A1-SR-14"]
    },
    {
      "title": "ts_rank and ts_rank_cd use no collection statistics",
      "summary": "Both functions score one document from its own tsvector: term counts, positions, and weight labels. The manual calls them only examples that use no global information. They do not compute BM25 or TF-IDF.",
      "source_record_refs": ["A1-SR-07"]
    },
    {
      "title": "pg_trgm and fuzzystrmatch give fuzzy matching inside the server",
      "summary": "pg_trgm GIN and GiST indexes serve similarity, LIKE, ILIKE, regular expressions, and equality; only GiST serves distance ordering. fuzzystrmatch computes Levenshtein distance and phonetic codes; only Daitch-Mokotoff has a documented GIN index path, and four phonetic functions, soundex, metaphone, dmetaphone, and dmetaphone_alt, do not work well with UTF-8.",
      "source_record_refs": ["A1-SR-01", "A1-SR-04"]
    },
    {
      "title": "Upgrades to 18 and 19 change derived text search data",
      "summary": "The release notes advise reindexing full-text and pg_trgm indexes after pg_upgrade to 18 and 19, and recomputing stored tsvector values for 19. The 19 stemmer update changes stems for English and German.",
      "source_record_refs": ["A1-SR-14"]
    },
    {
      "title": "Four BM25 extensions exist, each as an index access method",
      "summary": "ParadeDB pg_search, pg_textsearch, VectorChord-bm25, and pgx-bm25 have public repositories with commits in 2026. Each adds an index access method and a scoring operator and needs no server outside PostgreSQL.",
      "source_record_refs": ["A2-SR-01", "A2-SR-03", "A2-SR-08", "A2-SR-09"]
    },
    {
      "title": "pg_search states ACID behaviour, and two open issues report gaps",
      "summary": "The vendor states that index changes are atomic and follow PostgreSQL isolation. Open issue #7093 reports index documents without heap rows after crash recovery, and open issue #6007 reports that creating an index in Community stops a physical standby. Physical replication is an Enterprise feature.",
      "source_record_refs": ["A2-SR-03", "A2-SR-06", "A2-SR-18"]
    },
    {
      "title": "pg_textsearch states two exceptions to MVCC",
      "summary": "pg_textsearch writes through generic WAL and supports physical replication since v1.2.0. Compaction output is not undone by ROLLBACK, corpus statistics are not MVCC-filtered, and PREPARE TRANSACTION is not supported after creating an index. A Tiger Cloud page for v1.1.0 documents one partial index per language with its own text_config, states that the implicit <@> form does not run inside PL/pgSQL functions, and states that there is no phrase search.",
      "source_record_refs": ["A2-SR-01", "A2-SR-02", "A2-SR-19"]
    },
    {
      "title": "VectorChord-bm25 needs a second extension and a token column",
      "summary": "The index covers a bm25vector column that pg_tokenizer fills and a trigger or UPDATE keeps in sync. Index pages use generic WAL, read from code. No document states rollback, replication, or pg_dump behaviour, and only English has been tested.",
      "source_record_refs": ["A2-SR-08"]
    },
    {
      "title": "pgx-bm25 states inherited WAL and replication but is one release old",
      "summary": "pgx-bm25 keeps its index in its own pages and states that it inherits WAL, crash recovery, and physical replication; pg_dump emits CREATE INDEX. A ranked scan can rescore rows under new corpus statistics within one statement. It has one release and private development.",
      "source_record_refs": ["A2-SR-09"]
    },
    {
      "title": "Keyword and vector results combine in one SQL statement by RRF",
      "summary": "The pgvector example fuses ts_rank_cd and a pgvector distance with RRF, k = 60, FULL OUTER JOIN and COALESCE. ParadeDB fuses its BM25 branch and a vector branch with UNION ALL, GROUP BY, and weights per branch. Two Tiger Data pages fuse a pg_textsearch BM25 branch with RRF, k = 60, and LEFT JOIN, one with a pgvector HNSW branch and one with a pgvectorscale diskann branch. All are plain SQL, and the survey ran none of them. No record shows score-based fusion in SQL.",
      "source_record_refs": ["A2-SR-07", "A2-SR-10", "A2-SR-11", "A2-SR-19", "A2-SR-23"]
    },
    {
      "title": "pgvectorscale adds a diskann vector index on top of pgvector",
      "summary": "pgvectorscale requires pgvector, needs a superuser to install, and builds for PostgreSQL 14 to 18; support for 19 exists only as an open user issue. Index writes use generic WAL, read from the code and not tested. No record states its replication, rollback, or pg_dump behaviour. Label filters use a smallint[] column in the index, and the scan reads only the first && condition, inferred from code. The fused pg_textsearch statement with a pgvector HNSW branch does not need it, inferred from the statement.",
      "source_record_refs": ["A2-SR-19", "A2-SR-20", "A2-SR-21", "A2-SR-22", "A2-SR-23", "A2-SR-24"]
    },
    {
      "title": "Seven concepts meet the entry rule for a hardened concept",
      "summary": "concept-history-check ranks BM25 term weighting, query parsing for user input, pg_textsearch durability and replication, the GIN write path, rank fusion, trigram index searches, and ParadeDB index storage and WAL. Five more histories fall below the entry rule.",
      "source_record_refs": ["A1-SR-02", "A1-SR-11", "A1-SR-12", "A1-SR-14", "A1-SR-15", "A2-SR-02", "A2-SR-04", "A2-SR-05", "A2-SR-06", "A2-SR-07", "A2-SR-11", "A2-SR-12", "A2-SR-13", "A2-SR-14", "A2-SR-15", "A2-SR-16", "A2-SR-17", "A2-SR-18"]
    }
  ],
  "uncertainties": [
    "Own-write visibility through GIN is inferred from ginget.c, not stated by any source (A1-SR-12).",
    "Physical replication of built-in text indexes is inferred from GIN WAL logging (A1-SR-12); GiST WAL behaviour is not recorded.",
    "VectorChord-bm25 WAL behaviour is read from one source file, and its README may lag the API (A2-SR-08).",
    "That a fused statement reads one snapshot is inferred from single-statement semantics (A2-SR-07).",
    "The transaction statements of pg_search, pg_textsearch, and pgx-bm25 are project documentation, and ParadeDB issues #6007 and #7093 contradict parts of it (A2-SR-03, A2-SR-06).",
    "Some concept history dates are record dates, not event dates, because the check requires record dates.",
    "pgvectorscale WAL behaviour and its use of only the first label condition in a scan are read from code, not tested (A2-SR-21).",
    "The Tiger Cloud page on pg_textsearch describes v1.1.0, and its version list and crash recovery disagree with the current README (A2-SR-19, A2-SR-01)."
  ],
  "evidence_gaps": [
    "No record shows a score-based fusion, such as a convex combination, in SQL.",
    "No record shows a fused keyword-and-vector statement for VectorChord-bm25 or pgx-bm25. The pg_textsearch fused statements are vendor examples that the survey did not run (A2-SR-19, A2-SR-23).",
    "No record shows a fused statement whose vector branch filters rows, for example by embedding model.",
    "No record tests pgvectorscale crash recovery, standby replay, ROLLBACK, pg_dump, or a partial diskann index with a WHERE clause.",
    "pg_dump behaviour is not recorded for the built-in features, pg_textsearch, VectorChord-bm25, or pgvectorscale.",
    "Rollback and own-write visibility are not stated for VectorChord-bm25 or pgx-bm25, and own-write visibility is not stated for pg_textsearch.",
    "No source evaluates a Hunspell German dictionary with PostgreSQL, and the unaccent mapping of German umlauts was not read.",
    "No record states why tsearch2 moved into core, why gin_clean_pending_list was added, or what criticism led ParadeDB to block storage.",
    "The cover density paper, the TREC-1 Okapi paper, the 2004 BM25F paper, Chen et al. 2022, Lv and Zhai 2011, and ParadeDB issue #2195 were not read.",
    "No record measures retrieval quality of ts_rank, BM25, or any fusion on a corpus like the store's."
  ],
  "limitations": [
    "The survey installed, ran, and benchmarked nothing; all behaviour comes from documentation, code reading, issues, and papers.",
    "All records were gathered on 2026-11-18, except A2-SR-19 to A2-SR-24 on 2026-11-19; release and contributor counts change over time.",
    "PostgreSQL 19 was at release candidate 2, so its release notes may still change.",
    "Issue searches used GitHub title keywords only, so reports with other titles may be missing.",
    "Vendor documentation counts only for stated features and syntax; performance figures on the Tiger Data pages and in the pgvectorscale README are vendor statements without a recorded method; no independent test of any extension is recorded."
  ],
  "candidates_for_deeper_falsification_study": [
    "Claim: one RRF statement that fuses ts_rank_cd over a GIN index with pgvector HNSW finds a row inserted earlier in the same transaction in both branches. Refuted if either branch misses a row that a plain SELECT in that transaction returns.",
    "Claim: after ROLLBACK of a transaction that inserted text with a stored generated tsvector, no keyword or vector query finds the rolled-back row. Refuted if any later query returns it.",
    "Claim: under SERIALIZABLE, concurrent transactions that write and search one GIN index fail more often with fastupdate on than off. Refuted if the failure rates do not differ under the same load.",
    "Claim: the german Snowball configuration does not match a compound part, so a query for Fabrik misses Schokoladenfabrik without a Hunspell dictionary. Refuted if the query matches.",
    "Claim: RRF over ts_rank_cd and pgvector gives top-5 results as good as RRF over a BM25 extension on a judged German and English sample of the store's corpus. Refuted if the BM25 variant scores clearly higher on nDCG.",
    "Claim: pg_textsearch BM25 scores inside one REPEATABLE READ snapshot change when another session commits new rows. Refuted if the scores stay equal.",
    "Claim: pgx-bm25 returns the same results on a physical standby as on the primary, and after crash recovery holds no entry without a table row. Refuted if results differ or an orphan entry appears.",
    "Claim: ParadeDB Community 0.26 leaves index documents without heap rows after repeated kill -9 crash recovery, as issue #7093 reports. Refuted if repeated runs of the reported procedure show every indexed row in the heap.",
    "Claim: after pg_upgrade from 18 to 19, some stored german and english tsvectors differ from a fresh to_tsvector of the same text. Refuted if no stored vector differs on the corpus.",
    "Claim: the Tiger Cloud RRF statement over pg_textsearch and pgvector HNSW finds a row inserted earlier in the same transaction in both branches, and no longer finds it after ROLLBACK. Refuted if either branch misses the row before ROLLBACK or returns it after.",
    "Claim: a pgvectorscale diskann index on a physical standby returns the same nearest neighbours as on the primary after a burst of inserts. Refuted if the result lists differ once the standby has replayed the WAL."
  ]
}
```

## 8. Uncertainties, evidence gaps, and limitations

**Inferred behaviour.** Four facts that matter to the store rest on inference, not on a source sentence. The first is that a transaction finds its own new rows through GIN, read from the scan code (A1-SR-12). The second is that the GIN WAL gives physical replication of built-in text indexes (A1-SR-12). The third is that VectorChord-bm25 writes WAL, read from one source file (A2-SR-08). The fourth is that a fused statement reads one snapshot (A2-SR-07). pgvectorscale WAL and its label scan are also read from code (A2-SR-21). GiST WAL behaviour and `pg_dump` behaviour for the built-in features were not recorded. The area index lists a reindex advice for fuzzystrmatch after 19, but the release-notes record states that advice only for full-text search and pg_trgm (A1-SR-14). So the table marks the fuzzystrmatch rebuild as inferred.

**Open issues that contradict documentation.** ParadeDB documents atomic, MVCC-consistent index changes (A2-SR-03). Issue #7093 reports index documents without table rows after crash recovery, and issue #6007 reports a stopped physical standby (A2-SR-06). Both were open on 2026-11-18. The VectorChord-bm25 README may lag commits that changed the API after release 0.3.0 (A2-SR-08). The Tiger Cloud page on pg_textsearch still describes v1.1.0: PostgreSQL 17 and 18, crash recovery from the heap, and no background compaction (A2-SR-19). The README and release notes describe the newer design, so the report follows them (A2-SR-01, A2-SR-02).

**Vendor and project statements.** The transaction and replication statements of pg_search, pg_textsearch, and pgx-bm25 come from the projects' own documentation (A2-SR-01, A2-SR-03, A2-SR-09). No independent test of any of them is recorded. pgx-bm25's public repository shows one squashed commit per release, so its activity is not visible (A2-SR-09). VectorChord-bm25 issue #124 reports a session that cannot `REINDEX` after delete churn. No VectorChord-bm25 document states `REINDEX` behaviour, so the issue contradicts no document (A2-SR-08). The Tiger Data pages and pgvectorscale files come from the company behind pg_textsearch, and their performance figures have no recorded method (A2-SR-19, A2-SR-20). The BM25 history rests on one team, and two authors of the 2023 fusion analysis work for a vector database vendor (A2-SR-14, A2-SR-15, A2-SR-16, A2-SR-13).

**Dates.** Some history dates are record dates, not event dates, as section 3 states. The release counts and contributor counts were taken on 2026-11-18 and 2026-11-19 and will change (A2-SR-02, A2-SR-18, A2-SR-22). PostgreSQL 19 was at release candidate 2, so its notes may still change (A1-SR-14).

**Unread sources.** The area 1 index lists the cover density paper behind `ts_rank_cd`, the unaccent rules file, and the reason for moving tsearch2 into core as not read. The area 2 index lists the TREC-1 Okapi paper, the 2004 BM25F paper, Chen and colleagues 2022, Lv and Zhai 2011, and ParadeDB issue #2195 on `pg_dump` as not read. A web search summary claimed that Neon deprecated pg_search, and two Neon pages did not confirm it, so the survey records nothing on it. The Azure page and the pgvectorscale benchmark post were not read (A2-SR-19, A2-SR-20). The issue searches used GitHub title keywords, so reports with other titles may be missing (A2-SR-06, A2-SR-22).

**Method limits.** The survey installed, ran, and measured nothing. No fused statement in section 5 was run. No record measures retrieval quality for `ts_rank`, BM25, or any fusion on a corpus like the store's. All records were gathered on 2026-11-18 and 2026-11-19.
