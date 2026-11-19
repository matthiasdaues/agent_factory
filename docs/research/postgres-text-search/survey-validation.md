# Survey Validation: Postgres Text Search (Step 5)

## Verdict

The report passes the Step 5 gate. All four scripts exit 0, the ranking tables match the script output, and every record ID resolves to one file. No finding blocks the gate. The semantic review found ten minor defects and one suggestion. None changes what a reader concludes about the options or the transaction boundary. The writer can fix them in one pass, then rerun `concept-history-check` if a history quote changes.

The validator did not write any artifact of this survey. The inspection ran fresh over every history entry, every finding, every comparison cell, and both quoted statements, as [review-loop-discipline.md](../../../packages/factory/rulebooks/conventions/review-loop-discipline.md) requires. The playbook Step 5 and the brief agree on what must pass. No survey policy file exists, so the policy stage does not apply.

## Mechanical results

| Check                | Command or method                                                                          | Exit code    | Result                                                         |
| -------------------- | ------------------------------------------------------------------------------------------ | ------------ | -------------------------------------------------------------- |
| 1. Source records    | `packages/factory/scripts/source-record-check docs/research/postgres-text-search/sources`  | 0            | 33 records checked, 0 failures, 2 area indexes skipped by name |
| 2. Concept histories | `packages/factory/scripts/concept-history-check docs/research/postgres-text-search`        | 0            | `12 histories pass`                                            |
| 3. Report block      | `schema-validate` of the extracted json block against `research-survey-report.schema.json` | 0            | The block is valid                                             |
| 4. Ranking tables    | `concept-history-check --table docs/research/postgres-text-search`, then `diff`            | 0            | Both tables in section 3 equal the script output line for line |
| 5. Record IDs        | Every `A1-SR-n` and `A2-SR-n` in the report matched against `sources/**`                   | not a script | 33 distinct IDs, each resolves to exactly one file             |

A search of the report for "proven", "validated", "survived", "admitted", and "recommend" finds only the opening paragraph, which says that the report gives no verdict and that sections 1 to 5 recommend nothing.

## History results

The script settles quotes, dates, counts, the entry rule, and the rank. This review judged only three things per entry: whether the quote shows the formulation or criticism, whether the step is a new formulation, and whether each `drove_next: true` criticism is one the source presents as the cause of the next step.

The 12 histories hold 39 steps. Every step is a new formulation, and every `drove_next: true` criticism is one its source presents as leading to the next step. Five step quotes show only part of the formulation they stand for:

| History                       | Entry      | What the quote shows                                                    | What it does not show                                                                                                                                 |
| ----------------------------- | ---------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `english-and-german-stemming` | `steps[2]` | "Snowball 3.0.0: Handle ASCII transliterations of umlauts (merging the" | The quote stops before the word german2 and says nothing about English stems. Both are part of the formulation. The concept is below the entry rule.  |
| `gin-write-path`              | `steps[0]` | "Add GIN (Generalized Inverted iNdex)"                                  | That 8.2 inserted every key straight into the index. No record states it; it is read back from the 2009 `fastupdate` commit.                          |
| `paradedb-index-storage`      | `steps[1]` | "Postgres write-ahead log (WAL) integration" for Enterprise             | The move to block storage, which is the main part of the step. A2-SR-04 holds the quote "`pg_search` is now on Postgres block storage".               |
| `pg-textsearch-durability`    | `steps[1]` | v1.2.0: "proper support for physical replication"                       | The custom WAL entries that the formulation names. A2-SR-02 holds them only in the v1.3.0 sentence "v1.2.0 had introduced custom WAL entries".        |
| `trigram-word-similarity`     | `steps[0]` | The `show_limit` threshold for the `%` operator                         | That `similarity()` compares the trigram sets of whole strings. A1-SR-02 holds the README sentence on "similarity of text based on trigram matching". |

Two entries pass, but the stakeholder should know how they pass:

- `query-parsing-for-user-input`, `steps[1]`. `to_tsquery` and `plainto_tsquery` existed side by side, so the step order is not a time order. The step still counts, because the 2017 proposal presents the plain functions as the answer to the strict syntax: "In order to make it easier postgres has functions like plainto_tsquery". Section 3.2 of the report states the side-by-side origin.
- `pg-textsearch-durability`, `steps[0]`, `drove_next: true`. Issue #294 proposes `GenericXLog`, not the custom WAL entries of v1.2.0. The link to v1.2.0 holds because the v1.2.0 note calls replication "essentially broken in previous releases", which is the same criticism.

No disagreement with the ranking rule came up.

## Findings table

| No. | Finding                                                                              | Records opened                         | Verdict          | Reason                                                                                                                                                                   |
| --- | ------------------------------------------------------------------------------------ | -------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Built-in full-text search keeps one transaction boundary                             | A1-SR-06, A1-SR-10, A1-SR-11, A1-SR-12 | Supported        | The WAL-logged pending list, the stored generated column, and the whole-index lock are in the records. Own-write visibility is marked as inferred, as A1-SR-12 marks it. |
| 2   | German and English stemming ship as Snowball dictionaries without compound splitting | A1-SR-08, A1-SR-09, A1-SR-14           | Partly supported | The finding states that PostgreSQL 19 ships Snowball 3.0.0 rules. A1-SR-09 says this is inferred from the sync commit and the release note.                              |
| 3   | `ts_rank` and `ts_rank_cd` use no collection statistics                              | A1-SR-07                               | Supported        | The manual quote "do not use any global information" and the code reading support it.                                                                                    |
| 4   | pg_trgm and fuzzystrmatch give fuzzy matching inside the server                      | A1-SR-01, A1-SR-04                     | Partly supported | The finding says "three phonetic functions". The caution box names four functions: `soundex`, `metaphone`, `dmetaphone`, and `dmetaphone_alt`.                           |
| 5   | Upgrades to 18 and 19 change derived text search data                                | A1-SR-14                               | Supported        | Both reindex advices and the stemmer item are quoted in the record.                                                                                                      |
| 6   | Four BM25 extensions exist, each as an index access method                           | A2-SR-01, A2-SR-03, A2-SR-08, A2-SR-09 | Supported        | Each record shows an access method, an operator, and a commit in 2026.                                                                                                   |
| 7   | pg_search states ACID behaviour, and two open issues report gaps                     | A2-SR-03, A2-SR-06, A2-SR-18           | Supported        | The vendor statement, both open issues, and the edition split are in the records.                                                                                        |
| 8   | pg_textsearch states two exceptions to MVCC                                          | A2-SR-01, A2-SR-02                     | Supported        | Both exceptions and the `PREPARE TRANSACTION` limit are quoted.                                                                                                          |
| 9   | VectorChord-bm25 needs a second extension and a token column                         | A2-SR-08                               | Supported        | The WAL statement is marked as read from code, as the record marks it.                                                                                                   |
| 10  | pgx-bm25 states inherited WAL and replication but is one release old                 | A2-SR-09                               | Supported        | All parts are quoted or marked as the record's reading.                                                                                                                  |
| 11  | Keyword and vector results combine in one SQL statement by RRF                       | A2-SR-07, A2-SR-10, A2-SR-11           | Supported        | Both statements are in the records, and A2-SR-07 states that no score-based fusion in SQL is shown.                                                                      |
| 12  | Seven concepts meet the entry rule for a hardened concept                            | The 18 records the histories cite      | Supported        | The finding repeats the script output and adds no count of its own.                                                                                                      |

Ten findings are supported, two are partly supported, and none is unsupported.

Section 3 prose states no rank or order that the histories do not hold. Its two counts of record dates ("Three steps" in 3.6, "Two steps" in 3.8) match the histories. Five statements in sections 2 and 3 cite a record that does not hold them:

- Section 2.1 cites A1-SR-06 for the `<N>` operator. Only A1-SR-15 mentions it.
- Section 3.1 cites A2-SR-16 for the name BM1 and for "no term frequency or document length". A2-SR-14 holds both.
- Section 3.2 says that `to_tsquery` and `plainto_tsquery` "both arrived in 8.3" and cites A1-SR-14. That record says only that the tsearch2 features moved into core in 8.3.
- Section 3.4 says that GIN "arrived in 8.2 with direct inserts". A1-SR-14 shows only "Add GIN".
- Section 3.8 cites A1-SR-04 for "Daitch-Mokotoff in 16". A1-SR-14 holds the release number.

## Comparison results

The validator checked every cell of the table in section 4 against its cited record. Each transaction-boundary cell matches its record, and each inferred cell says "inferred". The project-health cells match the GitHub counts in A2-SR-02, A2-SR-08, A2-SR-09, and A2-SR-18. Issues #6007, #7093, and #124 were open on 2026-11-18, as their records state. No sentence in sections 1 to 5 recommends an option.

Four cells do not match their records exactly:

| Option           | Column                   | Cell says                                                                                                       | Record says                                                                                                                                                                                                              |
| ---------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| fuzzystrmatch    | Rebuildable derived data | "Daitch-Mokotoff GIN indexes and code columns; 19 changes the codes of non-ASCII letters, so a rebuild follows" | The 19 item in A1-SR-14 names `soundex`, `metaphone`, `difference`, `dmetaphone`, and `dmetaphone_alt`. It does not name `daitch_mokotoff`, so the Daitch-Mokotoff indexes are not the ones a rebuild would follow from. |
| Full-text search | Release activity         | "Items in every major release from 9.6 to 19"                                                                   | A1-SR-14 says each release has at least one item for text search, pg_trgm, fuzzystrmatch, or unaccent together. It shows no full-text item for 13 or 15.                                                                 |
| pg_trgm          | Release activity         | "Changes in 9.1, 9.3, 9.6, 11, 14, 18, 19"                                                                      | A1-SR-14 also lists pg_trgm items in 8.3, 8.4, and 9.4. The releases 9.3 and 9.6 are read from commit dates in A1-SR-02 and are not marked as inferred.                                                                  |
| pg_textsearch    | Replication and pg_dump  | "Logical and pg_dump: not stated (A2-SR-01)"                                                                    | A2-SR-02 records "Add physical and logical replication tests (#263)" in v0.6.1. The test result itself is not recorded.                                                                                                  |

Section 8 places VectorChord-bm25 issue #124 under "Open issues that contradict documentation". No VectorChord-bm25 document states anything about `REINDEX`, so the issue contradicts nothing.

## Fusion results

Both quoted statements in section 5 equal their records character for character. The `diff` of the pgvector statement against A2-SR-10 and of the ParadeDB statement against A2-SR-07 is empty. The three short quotes also match: "fixed during a pilot investigation" (A2-SR-11), "Each branch contributes `weight / (k + rank)`" (A2-SR-07), and "pgvector's vector types, but not its HNSW or IVF indexes" (A2-SR-07).

| Fusion method       | Source cited | Original source?                                                                                                                                                                         |
| ------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RRF                 | A2-SR-11     | Yes, Cormack, Clarke, and Büttcher 2009.                                                                                                                                                 |
| CombSUM and CombMNZ | A2-SR-12     | Yes, Fox and Shaw at TREC-2.                                                                                                                                                             |
| Convex combination  | A2-SR-13     | No. Bruch and colleagues cite an earlier study of the convex combination, Chen et al. 2022, which was not read. The formula line does not say so; only the evidence gaps list the paper. |
| Weighted RRF        | A2-SR-07     | No original was located. The line says that the page cites no source for the weights, but not that no original was found or read.                                                        |

Section 5 also says that the pgvector cross-encoder example "reranks in Python, outside SQL". A2-SR-10 states this from the file name only and marks the file as not read. The report drops that mark.

## Completion criteria

| Criterion from `research-brief.json`                                       | Met | Where                                                   |
| -------------------------------------------------------------------------- | --- | ------------------------------------------------------- |
| Each scope area has findings backed by recorded sources                    | Yes | Findings 1 to 5 for area 1, findings 6 to 11 for area 2 |
| The comparison covers the simplicity facts, each backed or "not found"     | Yes | Section 4, with the four cells above to correct         |
| The report states which options keep one transaction boundary              | Yes | Section 1 and the column "Transaction boundary"         |
| The report shows how keyword and vector results combine, or that none does | Yes | Section 5, including "What no record shows"             |
| Candidates for falsification are testable design claims                    | Yes | Nine claims, each with a refutation condition           |
| The report claims no concept survived refutation                           | Yes | No falsification-only status language found             |

Section 6 is marked as interpretation. Each of its four points names the section or records it rests on, and each record it names supports a finding in sections 1 to 5.

## Required corrections

All corrections use the document class of [finding-classification.md](../../../packages/factory/rulebooks/conventions/finding-classification.md). The report is in use by no story or code, so `harms_downstream` is "no" for each one. A reader reaches the right conclusion about every option in each case, so `fails_purpose` is "no" and none blocks.

| No. | Correction                                                                                                                                                                                                                                                                                                                                          | Class            | Why this severity                                                                                                                     |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | In the fuzzystrmatch derived-data cell, name the stored codes of `soundex`, `metaphone`, `dmetaphone`, and `dmetaphone_alt` as the data the 19 change affects, not the Daitch-Mokotoff GIN indexes.                                                                                                                                                 | defect, minor    | No to fails_purpose: the cell is marked inferred and affects upgrade work only. A reader would rebuild the wrong index.               |
| 2   | Mark the full-text release-activity cell as covering text search, pg_trgm, fuzzystrmatch, and unaccent together. Add 8.3, 8.4, and 9.4 to the pg_trgm cell, and mark 9.3 and 9.6 as inferred from commit dates.                                                                                                                                     | defect, minor    | No to fails_purpose: the health picture of a core feature does not change. A reader checking the cells finds gaps.                    |
| 3   | In the pg_textsearch replication cell, state that v0.6.1 added logical replication tests (A2-SR-02) and that the logical behaviour itself is not stated.                                                                                                                                                                                            | defect, minor    | No to fails_purpose: the cell says "not stated" and a record of this survey says more.                                                |
| 4   | In finding 2 and in the `current_formulation` of `english-and-german-stemming`, mark "PostgreSQL 19 ships Snowball 3.0.0 rules" as inferred, as A1-SR-09 does.                                                                                                                                                                                      | defect, minor    | No to fails_purpose: the stem change in 19 is stated by A1-SR-14 either way.                                                          |
| 5   | In finding 4, write "four phonetic functions" and name them.                                                                                                                                                                                                                                                                                        | defect, minor    | No to fails_purpose: the count is wrong, but the conclusion on UTF-8 holds.                                                           |
| 6   | In section 5, say at the convex combination line that its earlier source, Chen et al. 2022, was not read. Say at the weighted RRF line that no original source was found.                                                                                                                                                                           | defect, minor    | No to fails_purpose: the brief asks for this mark, and the evidence gaps already name Chen et al. 2022.                               |
| 7   | In section 5, mark the cross-encoder statement as taken from the file name, not from reading the file, as A2-SR-10 does.                                                                                                                                                                                                                            | defect, minor    | No to fails_purpose: the statement is context for a gap, not a finding.                                                               |
| 8   | Fix the five citations listed under the findings table: `<N>` to A1-SR-15, BM1 to A2-SR-14, release 16 to A1-SR-14, and either cite or drop "both arrived in 8.3" and "with direct inserts".                                                                                                                                                        | defect, minor    | No to fails_purpose: each fact except the last two is in a record of this survey. A reader who follows the citation does not find it. |
| 9   | Replace the three step quotes that have a fuller quote in their record (`paradedb-index-storage` `steps[1]`, `pg-textsearch-durability` `steps[1]`, `trigram-word-similarity` `steps[0]`). Narrow the formulation of the two that have none (`english-and-german-stemming` `steps[2]`, `gin-write-path` `steps[0]`). Rerun `concept-history-check`. | defect, minor    | No to fails_purpose: no step changes the count or rank. A reader who checks a quote cannot see the step in it.                        |
| 10  | In section 8, move VectorChord-bm25 issue #124 out of "Open issues that contradict documentation", because no document states `REINDEX` behaviour.                                                                                                                                                                                                  | defect, minor    | No to fails_purpose: the issue is correctly reported. Only its heading is wrong.                                                      |
| 11  | In `pg-textsearch-durability` `steps[0]`, consider citing the v1.2.0 sentence "essentially broken in previous releases" beside the issue, since issue #294 proposes `GenericXLog`, not custom WAL.                                                                                                                                                  | suggestion, note | The link holds as recorded. Nothing needs to change.                                                                                  |
