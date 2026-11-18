# Research Survey Plan — Postgres Text Search

The plan follows [research-brief.json](research-brief.json). It splits the survey by the two scope areas of the brief, so no two assignments research the same feature. Both assignments run in parallel as one wave.

The [postgres-and-qmd survey](../postgres-and-qmd/survey-report.md) found that [the proposed store](../knowledge-graph-with-provenance/design-position.md#the-proposed-store) has no answer for keyword queries or ranking. That survey recorded pgvector and qmd's search pipeline, but no source on PostgreSQL text search. This survey fills that gap.

## Research Questions

01. Area 1: What do `pg_trgm` similarity and word similarity, the `%` and `<->` operators, their thresholds, and the GIN and GiST trigram indexes do, and which queries can each index serve?
02. Area 1: What do the `fuzzystrmatch` functions Levenshtein, Soundex, Metaphone, Double Metaphone, and Daitch-Mokotoff compute, for which languages, and can an index serve them?
03. Area 1: How do `tsvector`, `tsquery`, text search configurations, dictionaries, and stemming work for German and English, and what do `unaccent`, phrase search, and `websearch_to_tsquery` add?
04. Area 1: What do `ts_rank` and `ts_rank_cd` compute, what do they use and ignore, and what do the sources say about their limits as a relevance ranking?
05. Area 1: How do GIN and GiST indexes behave under inserts and updates, including the GIN pending list, and does a query in the writing transaction see the new rows through the index?
06. Area 2: Which BM25 extensions for PostgreSQL exist as of November 2026, such as ParadeDB `pg_search`, `pg_textsearch`, and VectorChord-bm25, and how does each store, update, and query its index?
07. Area 2: Does each BM25 extension keep PostgreSQL transaction semantics, so its index commits and rolls back with the table and a transaction sees its own writes?
08. Area 2: How do keyword and vector results combine in one SQL statement, such as by reciprocal rank fusion, and which documented examples from pgvector or the extensions show it?
09. Both areas: How do the options compare on the simplicity facts: components, query languages, consistency boundaries, what must be kept in sync, rebuildable derived data, release activity, and project health?
10. Both areas: Which concepts went through several documented rounds of formulation, criticism, and reformulation, and what criticism drove each change?

## Search Angles

- The PostgreSQL 18 and 19 manual, for stated behaviour and syntax of the contrib modules, full-text search, and index types
- PostgreSQL source code, cited by file and commit, where the manual does not state a behaviour, such as the GIN pending list or the rank functions
- PostgreSQL release notes, mailing list threads, and commitfest entries, for the history of trigram matching, full-text search, and `websearch_to_tsquery`
- The repositories of each BM25 extension: README, documentation of stated features and syntax, changelog, release notes, issues, and source code
- Repository activity of each extension: release dates, commit history, open and closed issues, and maintainers
- The pgvector repository and the extension repositories, for documented examples that combine keyword and vector results
- The original papers on BM25 and on reciprocal rank fusion, and their later criticism, only for the history of the concepts
- Writing on search engines outside PostgreSQL, only where it holds a criticism of a PostgreSQL feature

## Source Targets

- PostgreSQL manual chapters on `pg_trgm`, `fuzzystrmatch`, and `unaccent`
- PostgreSQL manual chapter on full-text search: `tsvector` and `tsquery`, parsers, dictionaries, configurations, the `german` and `english` configurations, ranking, phrase search, and `websearch_to_tsquery`
- PostgreSQL manual chapters on GIN and GiST indexes, the `fastupdate` storage parameter, and `gin_pending_list_limit`
- PostgreSQL source files for the rank functions (`src/backend/utils/adt/tsrank.c`), the GIN pending list (`src/backend/access/gin/ginfast.c`), and `contrib/pg_trgm`, where the manual is silent
- PostgreSQL release notes for the features above, and the mailing list threads that proposed or criticised them
- The ParadeDB `pg_search` repository, its documentation of features and syntax, changelog, release notes, and issues on transactions and MVCC
- The `pg_textsearch` repository, its documentation, release notes, and issues
- The VectorChord-bm25 repository, its documentation, release notes, and issues, and any further BM25 extension that the repositories name
- The pgvector README section on hybrid search and the examples it names
- Robertson and colleagues on BM25 and the probabilistic relevance framework, and Cormack, Clarke, and Büttcher on reciprocal rank fusion

## Assignments

Each assignment declares agent, tier, independent session, a unique output, and a bounded task. The output is a record folder, an ID prefix, and one area index beside the folder, as [source-research](../../../packages/factory/skills/source-research/SKILL.md#record-file) defines. Every task carries the same eight requirements:

- Aim for 10 to 15 records.
- Put the source's own words in straight double quotes in the Evidence section, because `concept-history-check` anchors only on quoted words. When the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark.
- Write no relative markdown links copied from a source. Keep the link text only.
- Mark each source primary or secondary, and state what it shows and what it does not show.
- Cite source code by file and commit where the documentation is silent. Mark each behaviour that the record infers instead of reads.
- Record the simplicity facts for each option, and whether the option keeps one PostgreSQL transaction boundary.
- Take release activity and project health from repositories and release notes, never from vendor claims. Documentation counts only for stated features and syntax.
- Do not install, run, or benchmark any tool or store. Record only whether a component is open source.

Three boundaries keep the areas apart:

- Area 1 owns everything that ships with PostgreSQL, including the rank functions `ts_rank` and `ts_rank_cd`. Area 2 owns every extension outside the PostgreSQL distribution and every statement that combines keyword and vector results, even where the keyword side is built-in full-text search.
- The postgres-and-qmd survey already covers pgvector and qmd's pipeline. Both areas cite its records, such as A1-SR-10 and A2-SR-02, as context, and record their own sources only for the questions above.
- Area 2 cites the area 1 records for built-in ranking instead of recording the same manual pages again.

| ID  | Agent      | Tier     | Area                                                 | Output                                                                            | Independent Session |
| --- | ---------- | -------- | ---------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------- |
| A1  | researcher | standard | built-in and contrib text search                     | `sources/area-1/`, prefix `A1-SR-`, index `sources/area-1-builtin-text-search.md` | false               |
| A2  | researcher | standard | BM25 extensions and keyword with vector in one query | `sources/area-2/`, prefix `A2-SR-`, index `sources/area-2-ranking-hybrid.md`      | false               |

## Stop Conditions

- Each assignment has recorded sources for the main concepts of its area, and `source-record-check` exits 0 on its folder.
- Area 1 has a record for German and English configurations, or a recorded gap for each.
- Area 2 has, for each BM25 extension the brief names, a record from its repository, or a recorded gap stating that no repository was found.
- Both areas state, for each option, whether it keeps one PostgreSQL transaction boundary, backed by a record or marked not found.
- Area 2 has a record that shows keyword and vector results combined in one statement, or states in its index that no source shows it.
- Both areas have, for each simplicity fact of each option, a record-backed value or a recorded gap.
- Each area index names the concepts with a recorded sequence of formulations, with the criticism and a source for each step, or states that it found none.
- A secondary source is marked as secondary and used only where no primary source is reachable.
- An assignment stops searching when further sources are unlikely to change its findings, and records its failed searches as gaps in its area index.

## Structured Block

The block below is the plan in the shape of `research-survey-plan.schema.json`. The tasks in `assignments` are the full text each researcher receives.

```json
{
  "research_questions": [
    "Area 1: What do pg_trgm similarity and word similarity, the % and <-> operators, their thresholds, and the GIN and GiST trigram indexes do, and which queries can each index serve?",
    "Area 1: What do the fuzzystrmatch functions Levenshtein, Soundex, Metaphone, Double Metaphone, and Daitch-Mokotoff compute, for which languages, and can an index serve them?",
    "Area 1: How do tsvector, tsquery, text search configurations, dictionaries, and stemming work for German and English, and what do unaccent, phrase search, and websearch_to_tsquery add?",
    "Area 1: What do ts_rank and ts_rank_cd compute, what do they use and ignore, and what do the sources say about their limits as a relevance ranking?",
    "Area 1: How do GIN and GiST indexes behave under inserts and updates, including the GIN pending list, and does a query in the writing transaction see the new rows through the index?",
    "Area 2: Which BM25 extensions for PostgreSQL exist as of November 2026, such as ParadeDB pg_search, pg_textsearch, and VectorChord-bm25, and how does each store, update, and query its index?",
    "Area 2: Does each BM25 extension keep PostgreSQL transaction semantics, so its index commits and rolls back with the table and a transaction sees its own writes?",
    "Area 2: How do keyword and vector results combine in one SQL statement, such as by reciprocal rank fusion, and which documented examples from pgvector or the extensions show it?",
    "Both areas: How do the options compare on the simplicity facts: components, query languages, consistency boundaries, what must be kept in sync, rebuildable derived data, release activity, and project health?",
    "Both areas: Which concepts went through several documented rounds of formulation, criticism, and reformulation, and what criticism drove each change?"
  ],
  "search_angles": [
    "The PostgreSQL 18 and 19 manual, for stated behaviour and syntax of the contrib modules, full-text search, and index types",
    "PostgreSQL source code, cited by file and commit, where the manual does not state a behaviour, such as the GIN pending list or the rank functions",
    "PostgreSQL release notes, mailing list threads, and commitfest entries, for the history of trigram matching, full-text search, and websearch_to_tsquery",
    "The repositories of each BM25 extension: README, documentation of stated features and syntax, changelog, release notes, issues, and source code",
    "Repository activity of each extension: release dates, commit history, open and closed issues, and maintainers",
    "The pgvector repository and the extension repositories, for documented examples that combine keyword and vector results",
    "The original papers on BM25 and on reciprocal rank fusion, and their later criticism, only for the history of the concepts",
    "Writing on search engines outside PostgreSQL, only where it holds a criticism of a PostgreSQL feature"
  ],
  "source_targets": [
    "PostgreSQL manual chapters on pg_trgm, fuzzystrmatch, and unaccent",
    "PostgreSQL manual chapter on full-text search: tsvector and tsquery, parsers, dictionaries, configurations, the german and english configurations, ranking, phrase search, and websearch_to_tsquery",
    "PostgreSQL manual chapters on GIN and GiST indexes, the fastupdate storage parameter, and gin_pending_list_limit",
    "PostgreSQL source files for the rank functions (src/backend/utils/adt/tsrank.c), the GIN pending list (src/backend/access/gin/ginfast.c), and contrib/pg_trgm, where the manual is silent",
    "PostgreSQL release notes for the features above, and the mailing list threads that proposed or criticised them",
    "The ParadeDB pg_search repository, its documentation of features and syntax, changelog, release notes, and issues on transactions and MVCC",
    "The pg_textsearch repository, its documentation, release notes, and issues",
    "The VectorChord-bm25 repository, its documentation, release notes, and issues, and any further BM25 extension that the repositories name",
    "The pgvector README section on hybrid search and the examples it names",
    "Robertson and colleagues on BM25 and the probabilistic relevance framework, and Cormack, Clarke, and Büttcher on reciprocal rank fusion"
  ],
  "assignments": [
    "A1 | agent: researcher | tier: standard | independent_session: false | area: built-in and contrib text search | output: folder sources/area-1/, ID prefix A1-SR-, index sources/area-1-builtin-text-search.md | task: The text search features that ship with PostgreSQL. Cover pg_trgm: similarity and word similarity, the % and <-> operators, the threshold settings, and the GIN and GiST trigram indexes with the queries each can serve. Cover fuzzystrmatch: Levenshtein, Soundex, Metaphone, Double Metaphone, and Daitch-Mokotoff, the languages each suits, and whether an index can serve them. Cover unaccent. Cover full-text search: tsvector and tsquery, parsers, dictionaries, configurations, and stemming, with a record for the german and the english configuration each; phrase search; websearch_to_tsquery; and ts_rank and ts_rank_cd, including what they use and ignore and any source on their limits as a relevance ranking. Cover GIN and GiST index behaviour under inserts and updates, including the GIN pending list, the fastupdate parameter, and gin_pending_list_limit. Record whether a query in the writing transaction sees its new rows through each index, and whether each feature keeps one PostgreSQL transaction boundary. Record the simplicity facts for each feature: components, query languages, consistency boundaries, what must be kept in sync, rebuildable derived data, release activity, and project health. Use the PostgreSQL 18 and 19 manual and release state as of November 2026; use older sources only for the history of a concept, such as trigram matching or the rank functions. Cite source code by file and commit where the manual is silent, such as src/backend/utils/adt/tsrank.c or src/backend/access/gin/ginfast.c. Mark each behaviour the record infers instead of reads. Cite the postgres-and-qmd survey records, such as A1-SR-07 and A1-SR-10, as context instead of recording pgvector or MVCC again. Do not research extensions outside the PostgreSQL distribution or statements that combine keyword and vector results; area 2 owns them. For each concept in the area with a documented history, record the sequence of formulations and the criticism that drove each change, with a source for each step, or state in the area index that the sources show none. Aim for 10 to 15 records. Put the source's own words in straight double quotes in the Evidence section; when the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark. Write no relative markdown links copied from a source; keep the link text only. Mark each source primary or secondary. State for each source what it shows and what it does not show. Do not install, run, or benchmark any tool or store. Use search engines outside PostgreSQL only as context for a criticism. Record failed searches and gaps in the area index.",
    "A2 | agent: researcher | tier: standard | independent_session: false | area: BM25 extensions and keyword with vector in one query | output: folder sources/area-2/, ID prefix A2-SR-, index sources/area-2-ranking-hybrid.md | task: BM25 ranking extensions for PostgreSQL, and the combination of keyword and vector results in one SQL statement. First list the BM25 extensions that exist as of November 2026 from their repositories, starting with ParadeDB pg_search, pg_textsearch, and VectorChord-bm25. For a named extension without a repository, record a gap in the area index. For each extension, record how it stores, updates, and queries its index, its query syntax, and whether it is open source. Record whether each extension keeps PostgreSQL transaction semantics: whether its index commits and rolls back with the table, whether a transaction sees its own writes, and what lives outside the PostgreSQL write-ahead log or must be rebuilt. Read the extension issues on transactions, MVCC, replication, and crash recovery. Record how keyword and vector results combine in one SQL statement, such as reciprocal rank fusion, from documented examples in the pgvector repository or the extensions, with the statement text quoted. Where no source shows one statement, state that in the area index. Record the simplicity facts for each extension and for the combined statement: components, query languages, consistency boundaries, what must be kept in sync, rebuildable derived data, release activity, and project health. Take release activity and project health from repositories and release notes, never from vendor claims; vendor documentation counts only for stated features and syntax. Use the documentation, source, and release state as of November 2026; use older sources only for the history of a concept, such as BM25 or reciprocal rank fusion. Cite source code by file and commit where the documentation is silent. Mark each behaviour the record infers instead of reads. Cite the postgres-and-qmd survey records, such as A1-SR-10 for pgvector and A2-SR-02 and A2-SR-09 for qmd's fusion, as context instead of recording them again. Cite the area 1 records for ts_rank and ts_rank_cd instead of recording the PostgreSQL manual again. Do not research features that ship with PostgreSQL except as the keyword side of a combined statement; area 1 owns them. For each concept in the area with a documented history, such as BM25, reciprocal rank fusion, or an extension renamed or rebuilt after criticism, record the sequence of formulations and the criticism that drove each change, with a source for each step, or state in the area index that the sources show none. Aim for 10 to 15 records. Put the source's own words in straight double quotes in the Evidence section; when the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark. Write no relative markdown links copied from a source; keep the link text only. Mark each source primary or secondary. State for each source what it shows and what it does not show. Do not install, run, or benchmark any tool or store. Use search engines outside PostgreSQL only as context for a criticism. Record failed searches and gaps in the area index."
  ],
  "stop_conditions": [
    "Each assignment has recorded sources for the main concepts of its area, and source-record-check exits 0 on its folder.",
    "Area 1 has a record for German and English configurations, or a recorded gap for each.",
    "Area 2 has, for each BM25 extension the brief names, a record from its repository, or a recorded gap stating that no repository was found.",
    "Both areas state, for each option, whether it keeps one PostgreSQL transaction boundary, backed by a record or marked not found.",
    "Area 2 has a record that shows keyword and vector results combined in one statement, or states in its index that no source shows it.",
    "Both areas have, for each simplicity fact of each option, a record-backed value or a recorded gap.",
    "Each area index names the concepts with a recorded sequence of formulations, with the criticism and a source for each step, or states that it found none.",
    "A secondary source is marked as secondary and used only where no primary source is reachable.",
    "An assignment stops searching when further sources are unlikely to change its findings, and records its failed searches as gaps in its area index."
  ]
}
```
