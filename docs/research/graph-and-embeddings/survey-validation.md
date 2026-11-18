# Survey Validation: Graph And Embeddings

This file records Step 5 of [research-survey.md](../../../packages/factory/playbooks/research-survey.md) for [survey-report.md](survey-report.md). The research orchestrator ran the mechanical checks. Four independent reviewers, one per area, read every record, every history, and the named report text. The orchestrator checked each defect claim against the records before it entered this file.

## 1. Verdict

**Fail.** One defect changes what a reader concludes and blocks release. Finding 7 in the JSON block states that one query with a graph traversal and a similarity search is documented for PostgreSQL with AGE and pgvector and for Neo4j. Neither record shows a traversal. The report must be corrected and validated again from schema validation onward.

All mechanical checks pass. Ten further defects do not change a reader's conclusion and do not block. They are listed in section 7 with the suggestions.

## 2. Mechanical checks

| Check                                                                                      | Result                                                                                | Exit code |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- | --------- |
| `source-record-check sources/`                                                             | 72 records checked, 0 failures; the four area index files are skipped by name         | 0         |
| `concept-history-check` on the survey root                                                 | 14 histories pass                                                                     | 0         |
| `schema-validate` of the JSON block against the survey report schema                       | Valid                                                                                 | 0         |
| Section 3 tables against `concept-history-check --table <survey-root>`                     | Both tables equal the script output line for line                                     | 0         |
| Every record ID in the report resolves to exactly one file in `sources/`                   | 72 distinct IDs cited, each resolves to one file; every record of the survey is cited | -         |
| Falsification-only status words ("proven", "validated", "survived refutation", "admitted") | None as whole words; "proven" occurs only inside "provenance"                         | -         |

## 3. History results

The script settled quotes, dates, counts, the entry rule, and the rank. This section judges only whether each quote shows its step, whether each step is a new formulation, and whether each `drove_next: true` criticism is one the source presents as leading to the next step.

Twelve of the 14 histories have no defect. Four of them have no finding at all: `ann-index-lineage`, `anisotropy`, `graph-based-rag`, and `neo4j-vector-index`. Two histories carry a defect, and eight carry only suggestions.

| History                     | Entry | Problem                                                                                                                                                                                                                        | Class      |
| --------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- |
| `filtered-vector-search`    | 0     | The criticism from A4-SR-10 ("current indices have high search latency or low recall") does not target the cost-based plan choice of A4-SR-09. A4-SR-10 never names AnalyticDB-V, plans, or cost. `drove_next: true` is wrong. | defect     |
| `near-duplicate-hashing`    | 3     | The A3-SR-19 criticism targets "searches for exact duplicates". Step 3 is approximate MinHash matching (A3-SR-18), so the criticism is attached to the wrong step. Section 3.12 repeats the pairing.                           | defect     |
| `graph-based-index`         | 0, 2  | Entry 0 quotes the drawback of the k-NN graph, not its formulation. Entry 2 claims "exponentially decaying membership", which the quote does not show.                                                                         | suggestion |
| `index-updates`             | 1     | The quote shows lazy deletion but not the batch consolidation that the formulation also names.                                                                                                                                 | suggestion |
| `ann-benchmark`             | 1     | The A4-SR-16 quote is a contrast with earlier challenges, not an objection.                                                                                                                                                    | suggestion |
| `knowledge-graph-embedding` | 2     | The A1-SR-14 criticism covers structure-only models in general and does not name RotatE.                                                                                                                                       | suggestion |
| `graph-vector-fusion`       | 0, 2  | Each quote shows half of its formulation. The other half ("scores combined afterwards", the reset probability) rests on A1-SR-06.                                                                                              | suggestion |
| `sentence-embedding`        | 3     | SimCSE makes its point on post-processing as a contrast after its method, not as the motivation for it (A3-SR-06).                                                                                                             | suggestion |
| `embedding-benchmark`       | 2, 3  | Entry 2 quotes a BEIR result, not the formulation. Entry 3 quotes MTEB's problem statement, not its formulation.                                                                                                               | suggestion |
| `pgvector-index-design`     | 1, 2  | Entry 1 names IVFFlat, which A2-SR-03 never names. Entry 2 cites a README feature statement as the criticism; the causal statement is in A2-SR-03, pull request #259.                                                          | suggestion |

The fix of `filtered-vector-search` entry 0 lowers its criticism count from 3 to 2. The concept still meets the entry rule, but its rank may change. So the author reruns `concept-history-check --table` and copies the new table into section 3.

## 4. Findings

Each reviewer opened every cited record of each finding.

| #   | Finding                                                                                          | Verdict          | Reason, where not supported                                                                                                                                                                                                                                                                      |
| --- | ------------------------------------------------------------------------------------------------ | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Graph-based retrieval designs embed text, not graph structure                                    | partly supported | A1-SR-08 names GRAG, which converts "k-hop ego networks into graph embeddings, thereby better preserving structural information". Section 1 says "mostly"; the title does not. A1-SR-02 embeds nothing on its global query path.                                                                 |
| 2   | Knowledge graph embeddings serve link prediction                                                 | supported        |                                                                                                                                                                                                                                                                                                  |
| 3   | Graph-based RAG often falls behind vector RAG on factual questions                               | partly supported | The A1-SR-09 record states "complementary behaviors rather than a consistent winner" and holds no "falls behind" statement. Its 13.4% figure reaches the records only through A1-SR-10. The 65% figure applies to KG-GraphRAG only.                                                              |
| 4   | No architecture record describes deletion across graph and vectors                               | supported        |                                                                                                                                                                                                                                                                                                  |
| 5   | Five single-database designs and one separate-store design                                       | supported        |                                                                                                                                                                                                                                                                                                  |
| 6   | Consistency boundaries differ between the single-database designs                                | supported        | The title says "single-database", but the summary includes Qdrant.                                                                                                                                                                                                                               |
| 7   | One query with traversal and similarity search is documented for AGE with pgvector and for Neo4j | partly supported | Blocking. The AGE query in A2-SR-05 is `MATCH (m:Movie), (search:Movie {...}) ... ORDER BY ... <=>`: two node patterns and no edge. The Neo4j example in A2-SR-08 and A2-SR-09 binds a node and searches, with no hop. AGE has no manual page on pgvector; the only source is a regression test. |
| 8   | Project health and maturity risks per store                                                      | supported        | No record calls a licence a health risk.                                                                                                                                                                                                                                                         |
| 9   | No store recomputes a vector when its source text changes                                        | partly supported | The summary is exact. The title covers all stores, but the records cover four documentation pages, not DuckDB vss or Qdrant.                                                                                                                                                                     |
| 10  | Similarity misses negation, entailment direction, domain shift, and length                       | partly supported | A3-SR-07 says dense retrievers "underperform on datasets with a large domain shift"; only its abstract mentions BM25, as "a robust baseline".                                                                                                                                                    |
| 11  | Second-stage checks for similarity candidates                                                    | supported        |                                                                                                                                                                                                                                                                                                  |
| 12  | A model change means re-encoding every vector                                                    | partly supported | A3-SR-20 says vectors are "not guaranteed to be compatible ... (though they can be moderately compatible by chance)", and A3-SR-20 is itself an update that avoids re-encoding through continued fine-tuning.                                                                                    |
| 13  | Filtered vector search has no single best method                                                 | partly supported | "Filtered-DiskANN and ACORN build predicates into the graph" holds for Filtered-DiskANN only. A4-SR-11 calls ACORN a "predicate-agnostic HNSW variant" that uses "predicate subgraph traversal" at search time.                                                                                  |
| 14  | Keeping a graph index current costs rebuilds or repair                                           | supported        | A4-SR-06 speaks of "simple graph update rules", not delete rules alone.                                                                                                                                                                                                                          |
| 15  | Eleven concepts meet the entry rule for a hardened concept                                       | supported        | The script output holds the count.                                                                                                                                                                                                                                                               |

Counts: 8 supported, 7 partly supported, 0 unsupported.

## 5. Store comparison

No sentence in sections 1 to 5 ranks or recommends a store. Each project-health statement matches its record: the AGE release gap and board reports (A2-SR-06), the pgvector vacuum fixes (A2-SR-02), the replaced FalkorDB engine and replica-set rule (A2-SR-14), the experimental vss persistence (A2-SR-15), and the single main DuckPGQ contributor (A2-SR-16). Every risk sentence of section 4.1 matches its record.

These cells and sentences do not match their records:

| Place                                          | Problem                                                                                                                                     | Class      |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Memgraph, "Query languages"                    | No record names Cypher; `grep -ic cypher` gives 0 for A2-SR-11 and A2-SR-12. The cell should say "not found" or cite a record.              | defect     |
| DuckDB, "Components"                           | No record says "embedded".                                                                                                                  | defect     |
| DuckDB, "Release activity"                     | "DuckPGQ follows each DuckDB release" goes beyond A2-SR-16, whose registry lists 12 updates against 20 DuckDB releases.                     | defect     |
| SQL/PGQ, "Query languages"                     | The cell says "Not found", but A2-SR-07 names "SQL property graph queries".                                                                 | defect     |
| Section 2.2, AGE interop                       | "Since 2024, AGE can call functions and operators": functions came with #2088 on 2024-09-11, operators with #2172 on 2025-07-09 (A2-SR-05). | defect     |
| AGE, "Kept in sync" and "Derived data rebuilt" | The cast rule is a query constraint, not data kept in sync. Creating an index on an empty table is not a rebuild.                           | suggestion |
| AGE, "Release activity"                        | The 8 tags are release-candidate tags, whose dates differ from the voted release dates (A2-SR-06).                                          | suggestion |
| FalkorDB, "Project health"                     | The RedisGraph lineage is the researcher's inference; the record says it rests on no FalkorDB statement read.                               | suggestion |
| Section 4.1, FalkorDB                          | "No example combines it with a traversal" is in the area index, not in A2-SR-13.                                                            | suggestion |
| Section 4.1, Neo4j beside Qdrant               | "Nothing keeps the identifiers in sync" is stronger than A2-SR-18, which "does not show any mechanism".                                     | suggestion |

Section 4.1 itself describes the queries correctly. It says that no AGE record starts from a similarity search and then traverses, and that further Neo4j traversal needs a following clause. Only finding 7 overstates them.

## 6. Similarity results

Section 5 passes on every statement of what similarity finds or misses, with the qualifications below. The three stated gaps hold across all four areas: no record tests NLI as a filter on vector candidates, no record measures reworded text reuse, and no record describes storing the model version with each vector. The orchestrator confirmed the last gap: A3-SR-20 lists it under "Does not show".

| Place                               | Problem                                                                                                                                                                                                                               | Class      |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Versioning paragraph                | "Update strategies that avoid re-encoding exist only for continued fine-tuning" overstates A3-SR-20, whose researcher read backward-compatible training (Shen et al. 2020) but did not record it. Write "the only recorded strategy". | defect     |
| Versioning paragraph                | "Vectors from different models live in unrelated spaces" drops "moderately compatible by chance" (A3-SR-20).                                                                                                                          | suggestion |
| Versioning paragraph, last sentence | A4-SR-18 shows efficiency loss under distribution shift, not a rebuild cost; the link to a model change is an inference.                                                                                                              | suggestion |
| Cost of the checks                  | "it" is the cross-encoder, but A3-SR-18 pairs MinHash with Jaccard and edit similarity, not with a cross-encoder.                                                                                                                     | suggestion |
| Paraphrase                          | The negation result of A3-SR-02 concerns the 2017 systems, and A3-SR-10 adds that "a large gap remains" after the cross-encoder.                                                                                                      | suggestion |
| Text reuse, near-duplicate          | Only Broder says "syntactic" (A3-SR-15). A3-SR-16 does not evaluate detection. Neither A3-SR-18 nor A3-SR-19 states that hashes miss semantic duplicates.                                                                             | suggestion |

## 7. Required corrections

Classes follow [finding-classification.md](../../../packages/factory/rulebooks/conventions/finding-classification.md), document class. A defect is blocking only when a reader who follows the statement reaches a wrong conclusion.

| #   | Correction                                                                                                                                          | Class      | Blocks |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------ |
| 1   | Finding 7: claim a pattern match ordered by similarity, not a traversal, and say that the AGE source is a regression test.                          | defect     | yes    |
| 2   | `filtered-vector-search` entry 0: set `drove_next: false` or cite a criticism of cost-based plans; rerun `--table` and copy it into section 3.      | defect     | no     |
| 3   | `near-duplicate-hashing` entry 3 and section 3.12: attach the exact-duplicate criticism to no MinHash step, or find one that targets MinHash.       | defect     | no     |
| 4   | Finding 3 and section 2.1: cite A1-SR-09 for "complementary behaviors rather than a consistent winner", not for "falls behind".                     | defect     | no     |
| 5   | Uncertainty on graph-based RAG evaluations: only A1-SR-06 comes from authors of a competing design, and A1-SR-10 does not re-implement the systems. | defect     | no     |
| 6   | Finding 1 title: add "mostly" or name GRAG from A1-SR-08.                                                                                           | defect     | no     |
| 7   | Finding 13 and section 2.4: ACORN applies the predicate at search time; only Filtered-DiskANN builds labels into the graph.                         | defect     | no     |
| 8   | Section 4 cells for Memgraph query languages, DuckDB components, DuckPGQ releases, and SQL/PGQ query languages: cite a record or say "not found".   | defect     | no     |
| 9   | Section 2.2: date operator support in AGE to 2025.                                                                                                  | defect     | no     |
| 10  | Section 5: "the only recorded strategy" in place of "exist only".                                                                                   | defect     | no     |
| 11  | Section 3.12: the area indexes name five more sequences, not four, and three of them fall short on criticisms or formulations, not on dates.        | defect     | no     |
| 12  | The suggestions in sections 3, 4, 5, and 6 of this file.                                                                                            | suggestion | no     |

Section 6 of the report ties each point to a finding. Every completion criterion of [research-brief.json](research-brief.json) is met, apart from the store comparison, which needs corrections 1 and 8. Each of the seven store designs has at least one falsification candidate.

Next, the report writer applies correction 1, and ideally corrections 2 to 11, and the survey returns to Step 5.
