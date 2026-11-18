# Survey Report: Graph And Embeddings

This report answers [research-brief.json](research-brief.json) in survey mode. It uses only the 72 source records under [sources/](sources/), cited by record ID. It reports what the sources document. It gives no verdict on whether any concept or design holds; that verdict belongs to a later falsification study. Sections 1 to 5 recommend nothing. Section 6 draws conclusions and is marked as interpretation.

## 1. Answer

Current designs combine a graph with embeddings mostly by embedding text, not graph structure. The graph-based retrieval designs read here embed chunks, passages, phrases, or short keys, and use the graph for expansion, communities, or a PageRank walk (A1-SR-03 to A1-SR-07). One surveyed design, GRAG, embeds k-hop ego networks (A1-SR-08). Knowledge graph embeddings serve link prediction, not text retrieval (A1-SR-11, A1-SR-13). No record describes how a changed or deleted document reaches both the graph and the vectors (A1-SR-02, A1-SR-04, A1-SR-08).

Six store designs hold both. Five keep graph and vectors in one database: PostgreSQL with Apache AGE and pgvector, Neo4j, Memgraph, FalkorDB, and DuckDB with DuckPGQ and vss. The sixth puts a vector store beside a graph store. SQL/PGQ was reverted before PostgreSQL 19 (A2-SR-07). The documentation read for four stores names no feature that recomputes a vector when its text changes (A2-SR-01, A2-SR-08, A2-SR-11, A2-SR-13). AGE with pgvector and Neo4j document one query that matches a graph pattern and searches by vector distance. No record shows a similarity search followed by a traversal (A2-SR-05, A2-SR-09). Each single-database design carries a recorded risk (section 4).

Embedding similarity finds candidates. It misses negation, the direction of entailment, and domain shift, and the records offer cross-encoders and NLI models as second-stage checks (A3-SR-07, A3-SR-10, A3-SR-11, A3-SR-13). When the model changes, the records show two options: keep one model, or re-encode every vector (A3-SR-20, A3-SR-21).

Eleven concepts meet the entry rule for a hardened concept (section 3). The table there gives their rank.

## 2. State of the art by area

### 2.1 Architectures that combine graphs and embeddings

Retrieval-augmented generation (RAG) joins a language model to a dense vector index of 100-word text chunks (A1-SR-01). It updates its knowledge by replacing the whole index (A1-SR-01). Later papers call this design "vector RAG" (A1-SR-02).

Graph-based designs add a graph that an LLM or an extraction step builds from the same text. GraphRAG summarises communities of the graph in advance and answers global questions from the summaries, with no vector step on that path (A1-SR-02). HippoRAG embeds noun-phrase nodes, adds synonymy edges where two node vectors pass a cosine threshold, and ranks passages with Personalized PageRank (A1-SR-05). LightRAG embeds short keys of entities and relations, matches them in a vector database, and expands one hop in the graph (A1-SR-04). LazyGraphRAG ranks communities of a noun-phrase graph by text chunk similarity at query time (A1-SR-03). HippoRAG 2 adds passage nodes and seeds the walk with passage similarity (A1-SR-06). HybridRAG retrieves from a vector store and a graph separately and concatenates the two contexts (A1-SR-07).

None of these designs embeds graph structure with a knowledge graph embedding. The survey A1-SR-08 names GRAG, which converts k-hop ego networks into graph embeddings, and one design that reranks paths with a knowledge graph embedding score. Structure embeddings such as TransE and RotatE learn from triples alone (A1-SR-11, A1-SR-13). KG-BERT scores a triple from the text of its descriptions instead (A1-SR-14). Joining structure and text in one space is a named challenge (A1-SR-15).

Evaluations from 2025 compare graph-based RAG with vector RAG and reach different results. HippoRAG 2 reports that structure-augmented designs drop below standard RAG on factual memory tasks (A1-SR-06). A benchmark study finds "complementary behaviors rather than a consistent winner" between vector RAG and graph-based RAG (A1-SR-09). A second benchmark states that recent studies find that graph-based RAG frequently underperforms vanilla RAG, and quotes from the first study a figure of 13.4% lower accuracy on Natural Questions (A1-SR-10). The two benchmarks also report higher construction cost, latency, storage, and prompt tokens (A1-SR-09, A1-SR-10). For the knowledge-graph variant, KG-GraphRAG, the extracted graphs hold only about 65% of answer entities on two datasets (A1-SR-09).

The record on consistency is thin. GraphRAG describes no update procedure (A1-SR-02). LightRAG adds new documents by set union and describes no deletion (A1-SR-04). The survey A1-SR-08 names dynamic update as an open direction.

### 2.2 Stores that hold a graph and vectors

AGE stores vertices and edges in PostgreSQL tables per label and runs openCypher inside a SQL function call (A2-SR-04). pgvector adds a vector column type with HNSW and IVFFlat indexes (A2-SR-01). Since 2024, AGE can call functions of other extensions from Cypher, with a cast from AGE's own type through text to a vector (A2-SR-05). Since 2025, Cypher in AGE can also use PostgreSQL operators (A2-SR-05).

Neo4j stores the vector as a node or relationship property and indexes it with Lucene HNSW (A2-SR-08). Its `SEARCH` clause, introduced in 2026.01, runs a vector search inside a Cypher statement with filters in the index (A2-SR-09). Memgraph keeps the vector only in a USearch index and a reference in the property store (A2-SR-11). FalkorDB runs as a Redis module and keeps vector indexes in a RediSearch fork (A2-SR-13, A2-SR-14). DuckPGQ defines a property graph over DuckDB tables and queries it with SQL/PGQ (A2-SR-16), and vss adds an experimental HNSW index (A2-SR-15). Qdrant, read as the example of a separate vector store, acknowledges a write before it is searchable unless the client waits (A2-SR-17).

PostgreSQL carried SQL/PGQ on its development branch from March to September 2026. The Release Management Team named unresolved design issues, and PostgreSQL 19 ships without it (A2-SR-07).

Section 4 compares the designs.

### 2.3 Embedding similarity for the system's tasks

Raw BERT output scored worse than averaged GloVe vectors on semantic textual similarity (STS) (A3-SR-03). Sentence-BERT fine-tunes BERT so that cosine between sentence vectors works (A3-SR-03). Contextual representations occupy a narrow cone, so two random words can have a cosine near 1 (A3-SR-04). Later work names this anisotropy as a cause of poor sentence similarity (A3-SR-05). SimCSE trains with a contrastive objective and reports a more uniform space (A3-SR-06).

STS grades symmetric meaning similarity from 0 to 5 (A3-SR-02). MTEB states that STS correlates poorly with other uses and that no embedding method leads on all tasks (A3-SR-08). BEIR shows dense retrievers underperforming on datasets with a large domain shift, and names BM25 a robust baseline (A3-SR-07). The MTEB maintainers removed common training sets from a new version, and the rankings of small English models dropped (A3-SR-09).

Section 5 covers each task, the checks, and vector versioning.

### 2.4 Nearest-neighbour indexes and hybrid queries

Tree-based and partitioning indexes lose to a sequential scan above about ten dimensions (A4-SR-02). Locality-sensitive hashing (LSH) gave sub-linear query times (A4-SR-01). Product quantization with an inverted file (IVFADC) stores short codes and scans only lists near the query (A4-SR-03). Graph-based indexes became the leading family by 2021 (A4-SR-17). HNSW builds a layered proximity graph (A4-SR-04), and DiskANN serves a graph index from an SSD (A4-SR-05).

A hybrid query combines a vector search with a structured predicate. Pre-filtering is slow when many records pass, post-filtering must widen its search when few pass, and one index per label grows too expensive with many labels (A4-SR-09, A4-SR-10, A4-SR-11). Filtered-DiskANN builds the labels into the graph edges (A4-SR-10). ACORN builds a predicate-agnostic HNSW variant and applies the predicate at search time by traversing the subgraph that the predicate induces (A4-SR-11). An independent benchmark finds no single best method (A4-SR-12).

Keeping an index current costs work. The FreshDiskANN authors state that industry rebuilds indexes periodically and estimate 1.5 to 2 hours on 48 cores for 100 million points in HNSW (A4-SR-06). Simple graph update rules make graph indexes lose recall (A4-SR-06), and delete marks in HNSW leave points that no search reaches (A4-SR-07). IVF and PQ lose efficiency when the data distribution shifts (A4-SR-18).

## 3. Hardened concepts

The table below is the output of `concept-history-check --table`. Each history lives in [histories/](histories/).

| Rank | Concept                                         | Area                                                     | Rounds | Criticisms | Primary anchors | Criticism coverage | Records                                                    |
| ---- | ----------------------------------------------- | -------------------------------------------------------- | ------ | ---------- | --------------- | ------------------ | ---------------------------------------------------------- |
| 1    | Knowledge graph embedding, structure or text    | Area 1: architectures that combine graphs and embeddings | 4      | 4          | 100%            | 100%               | A1-SR-11, A1-SR-12, A1-SR-13, A1-SR-14                     |
| 2    | Combining graph results and vector results      | Area 1: architectures that combine graphs and embeddings | 3      | 2          | 100%            | 100%               | A1-SR-05, A1-SR-06, A1-SR-07                               |
| 3    | Filtered vector search                          | Area 4: nearest-neighbour indexes and hybrid queries     | 3      | 3          | 100%            | 100%               | A4-SR-09, A4-SR-10, A4-SR-11, A4-SR-12                     |
| 4    | Keeping a graph index current under updates     | Area 4: nearest-neighbour indexes and hybrid queries     | 3      | 2          | 100%            | 100%               | A4-SR-06, A4-SR-08                                         |
| 5    | The approximate nearest-neighbour index lineage | Area 4: nearest-neighbour indexes and hybrid queries     | 3      | 2          | 100%            | 100%               | A4-SR-01, A4-SR-03, A4-SR-05, A4-SR-04                     |
| 6    | The graph-based index                           | Area 4: nearest-neighbour indexes and hybrid queries     | 3      | 3          | 100%            | 100%               | A4-SR-04, A4-SR-05                                         |
| 7    | The nearest-neighbour benchmark                 | Area 4: nearest-neighbour indexes and hybrid queries     | 3      | 3          | 100%            | 100%               | A4-SR-13, A4-SR-15, A4-SR-16, A4-SR-12                     |
| 8    | pgvector index design                           | Area 2: stores that hold a graph and vectors             | 3      | 2          | 100%            | 100%               | A2-SR-03, A2-SR-02, A2-SR-01                               |
| 9    | Graph-based retrieval-augmented generation      | Area 1: architectures that combine graphs and embeddings | 5      | 4          | 100%            | 75%                | A1-SR-01, A1-SR-02, A1-SR-04, A1-SR-06, A1-SR-03, A1-SR-10 |
| 10   | The benchmark for embedding similarity          | Area 3: embedding similarity for the system's tasks      | 5      | 4          | 100%            | 75%                | A3-SR-02, A3-SR-08, A3-SR-07, A3-SR-09                     |
| 11   | The sentence embedding for similarity           | Area 3: embedding similarity for the system's tasks      | 5      | 4          | 100%            | 75%                | A3-SR-01, A3-SR-03, A3-SR-08, A3-SR-05, A3-SR-06           |

Below the entry rule (at least 3 formulations and 2 recorded criticisms):

| Rank | Concept                                         | Area                                                | Rounds | Criticisms | Primary anchors | Criticism coverage | Records                                          |
| ---- | ----------------------------------------------- | --------------------------------------------------- | ------ | ---------- | --------------- | ------------------ | ------------------------------------------------ |
| -    | Neo4j vector index                              | Area 2: stores that hold a graph and vectors        | 2      | 1          | 100%            | 100%               | A2-SR-08, A2-SR-09                               |
| -    | Anisotropy as an explanation of poor similarity | Area 3: embedding similarity for the system's tasks | 3      | 1          | 100%            | 50%                | A3-SR-04, A3-SR-05, A3-SR-06                     |
| -    | Near-duplicate detection by hashing             | Area 3: embedding similarity for the system's tasks | 5      | 0          | 100%            | 0%                 | A3-SR-15, A3-SR-16, A3-SR-17, A3-SR-18, A3-SR-19 |

The histories follow the stakeholder's frame of conjecture and criticism. Each step is a formulation, and each criticism is a recorded objection to it. The "Primary anchors" column reads the start of each record's `source_family`. Two records count as primary there although they are secondary for some steps: A4-SR-04 for the k-nearest-neighbour graph and navigable small world, and A3-SR-02 for the STS tasks of 2012 to 2016.

### 3.1 Knowledge graph embedding, structure or text

TransE models a relation as a translation between entity vectors (A1-SR-11). TransH criticises TransE on reflexive and many-to-many relations and moves the translation onto a hyperplane (A1-SR-12). RotatE states that no earlier model captures all relation patterns and models a relation as a rotation (A1-SR-13). KG-BERT criticises structure-only models for the sparseness of graphs and scores triples from their text (A1-SR-14). KG-BERT names its own cost at link prediction time as a limit (A1-SR-14). TransR, DistMult, and ComplEx are known here only through RotatE's summary (A1-SR-13).

### 3.2 Combining graph results and vector results

HippoRAG picks the seed nodes of its graph walk by cosine similarity (A1-SR-05). HybridRAG concatenates two independently retrieved contexts and reports lower context precision for the hybrid than for graph retrieval alone (A1-SR-07). HippoRAG 2 criticises its predecessor because it "simply aggregates scores" and moves passage similarity into the walk (A1-SR-06). No recorded criticism links one step to the next in date order; each criticism targets its own design.

### 3.3 Filtered vector search

AnalyticDB-V chooses among hybrid query plans by a cost model (A4-SR-09). Filtered-DiskANN states that current indexes, built without the label metadata, give high latency or low recall, and builds graph edges from geometry and labels (A4-SR-10). A4-SR-10 does not name AnalyticDB-V or its cost-based plans, so the history does not count this criticism as the cause of the next step. ACORN criticises Filtered-DiskANN for about 1,000 labels and equality predicates only, and traverses the subgraph that any predicate induces (A4-SR-11). An independent benchmark finds ACORN reliable but often outperformed (A4-SR-12). A4-SR-09 comes from the vendor of the system it describes.

### 3.4 Keeping a graph index current under updates

The FreshDiskANN authors call the periodic rebuild "a very expensive operation" and replace it with lazy deletion and batch consolidation (A4-SR-06). The same group then criticises batch consolidation and processes each insert and delete in place (A4-SR-08). Both records come from one group, and no independent replication of the last step is recorded.

### 3.5 The approximate nearest-neighbour index lineage

LSH hashes close points into the same bucket more often (A4-SR-01). Jégou and others criticise LSH on real data and on memory, and propose IVFADC (A4-SR-03). HNSW follows as a graph index (A4-SR-04). The DiskANN authors later report low recall for compressed inverted-file indexes at billion scale (A4-SR-05). That criticism came after HNSW, so it did not drive it. The original 1998 LSH paper was not read; A4-SR-01 is the 2012 journal version.

### 3.6 The graph-based index

The HNSW authors criticise the k-nearest-neighbour graph for power-law routing and navigable small world for polylogarithmic scaling, and add layers (A4-SR-04). The DiskANN authors criticise in-memory indexes for their cost and dataset limit (A4-SR-05). All three formulations rest on the HNSW paper. The NSW papers themselves were not read.

### 3.7 The nearest-neighbour benchmark

ANN-Benchmarks measures in-memory indexes in one thread (A4-SR-13). The 2021 challenge criticises million-point evaluations and tests at billion scale with hardware cost (A4-SR-15). The 2023 challenge adds filtered, out-of-distribution, sparse, and streaming tracks (A4-SR-16). A 2025 benchmark still finds too few realistic filtered datasets (A4-SR-12). A4-SR-15 and A4-SR-16 share organisers.

### 3.8 pgvector index design

The maintainer preferred product quantization over graph indexes in 2021 (A2-SR-03). Users called search too slow and asked for HNSW, and release 0.5.0 added it (A2-SR-03, A2-SR-02). The README states that filters run after the approximate index scan (A2-SR-01). Release 0.8.0 added iterative index scans, which continue until enough rows match (A2-SR-02, A2-SR-03). The history dates the last two steps 2026-11-18, the retrieval date of the changelog record. The changelog itself dates them 2023-08-28 and 2024-10-30 (A2-SR-02).

### 3.9 Graph-based retrieval-augmented generation

GraphRAG criticises vector RAG on global questions and summarises graph communities (A1-SR-02). LightRAG criticises the full regeneration of GraphRAG communities on new data and adds vector keys with additive updates (A1-SR-04). LazyGraphRAG moves the work to query time (A1-SR-03). HippoRAG 2 criticises structure-augmented designs for falling below standard RAG on factual tasks (A1-SR-06). A 2025 benchmark repeats that criticism for graph-based RAG in general (A1-SR-10). That benchmark is secondary for the figures it takes from A1-SR-09. LazyGraphRAG has no independent criticism on record, and its only source is the authors' blog (A1-SR-03).

### 3.10 The benchmark for embedding similarity

STS grades pairs for meaning equivalence, and the STS Benchmark joins the data of 2012 to 2017 (A3-SR-02). MTEB criticises STS-only evaluation (A3-SR-08). BEIR tests zero-shot retrieval and names a lexical bias in its own annotations (A3-SR-07). MMTEB criticises limited task diversity and drops common training sets (A3-SR-09). MMTEB names English leakage as its own limit (A3-SR-09). No independent audit of the leaderboards is recorded.

### 3.11 The sentence embedding for similarity

InferSent trains a sentence encoder on NLI labels (A3-SR-01). SBERT measures raw BERT output as worse than averaged GloVe and fine-tunes a siamese network (A3-SR-03). BERT-flow corrects anisotropy after training (A3-SR-05). SimCSE criticises post-processing because it only targets isotropy, and trains contrastively (A3-SR-06). MTEB criticises SBERT and SimCSE for evaluating only on STS and classification (A3-SR-08). The record holds no general embedding model after SimCSE.

### 3.12 Concepts below the entry rule

- **Neo4j vector index.** The records give reasons for the `SEARCH` clause only (A2-SR-09). The reasons for the beta, the general release, and the native vector type are gaps (A2-SR-08).
- **Anisotropy.** Only SimCSE's criticism of post-processing is recorded (A3-SR-06). The word-level finding names no fix, but no source criticises it in quoted words (A3-SR-04).
- **Near-duplicate hashing.** The records hold five formulations from 1997 to 2023 (A3-SR-15 to A3-SR-19). No recorded criticism targets one of these formulations. SemDeDup criticises datasets that are curated only by searches for exact duplicates (A3-SR-19). None of the five formulations is such a search, so the history attaches the criticism to no step. Charikar presents his sketch as an alternative, not as a fix of a fault (A3-SR-16).

The area indexes name five more sequences that are not entered as histories. Four of them fall short of the entry rule on formulations or criticisms. SQL/PGQ in PostgreSQL has one formulation and its revert (A2-SR-07). DuckDB vss filtering has two formulations (A2-SR-15). The Memgraph vector index has four formulations, but only one release note names a fault that a step removes (A2-SR-12). The area 1 sequence on graph and vector consistency has one recorded criticism in four steps (A1-SR-04). The fifth, AGE with pgvector, has three formulations, but two of its step dates match no date of its records (A2-SR-04, A2-SR-05).

## 4. The store comparison

Release counts cover 2024-11-18 to 2026-11-18. "Not found" means no record holds the fact.

| Design                           | Components                                                               | Query languages                                                                                      | Consistency boundaries                                                                           | Kept in sync by the application                                                               | Derived data rebuilt                                                                                | Release activity                                                                                                                                 | Project health                                                                                                                                                        |
| -------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PostgreSQL with AGE and pgvector | One server, two extensions (A2-SR-04, A2-SR-01)                          | Two: SQL, and openCypher inside a SQL function call (A2-SR-04)                                       | One PostgreSQL transaction (A2-SR-04, A2-SR-01)                                                  | Vector against its source text; the README names no recompute feature (A2-SR-01)              | Vector recompute: not found (A2-SR-01); index rebuild: not found                                    | AGE: 8 release-candidate tags, dated apart from the voted releases (A2-SR-06); pgvector: 7 patch releases, latest 0.8.7 of 2026-10-01 (A2-SR-02) | AGE: no release from 2024-03-19 to 2025-09-16, four missing board reports in 2026, chair changes in 2024 and 2026 (A2-SR-06); pgvector maintainer count: not found    |
| PostgreSQL with SQL/PGQ          | None released; reverted before PostgreSQL 19 (A2-SR-07)                  | SQL with SQL property graph queries, reverted (A2-SR-07)                                             | Not found                                                                                        | Not found                                                                                     | Not found                                                                                           | No release (A2-SR-07)                                                                                                                            | Not found                                                                                                                                                             |
| Neo4j                            | One server, Lucene inside (A2-SR-08)                                     | One: Cypher, in versions 5 and 25 (A2-SR-08, A2-SR-09)                                               | One transaction; the index does not see changes of the same transaction (A2-SR-08)               | Vector against its source text; no sync feature found (A2-SR-08)                              | A new index is built in the background (A2-SR-08); vector recompute: not found                      | 32 calendar-version tags plus a 5.26 line (A2-SR-10)                                                                                             | Community Edition under GPL-3.0, repository active (A2-SR-10); maintainer count: not found                                                                            |
| Memgraph                         | One server, USearch inside (A2-SR-11)                                    | Not found by name; the records show `CREATE VECTOR INDEX` and `CALL ... YIELD` statements (A2-SR-11) | The vector index reads uncommitted data; the rest keeps its isolation level (A2-SR-11)           | An embeddings module computes vectors only when called (A2-SR-11)                             | Dropping the index moves vectors back to the property store (A2-SR-11); vector recompute: not found | 29, latest v3.14.0 of 2026-10-21 (A2-SR-12)                                                                                                      | BSL 1.1 and Memgraph Enterprise License (A2-SR-12); maintainer count: not found                                                                                       |
| FalkorDB                         | Redis server, FalkorDB module, RediSearch fork (A2-SR-14)                | One: openCypher with extensions (A2-SR-14)                                                           | One query is atomic; several queries need Redis MULTI/EXEC (A2-SR-13)                            | A vector must be wrapped in `vecf32()` or the index skips it (A2-SR-13)                       | Not found                                                                                           | 78 on two lines, 4.x and 6.x (A2-SR-14)                                                                                                          | New Rust engine in September 2026; RedisGraph, treated as the predecessor by the researcher and not by a FalkorDB statement, is no longer maintained; SSPL (A2-SR-14) |
| DuckDB with DuckPGQ and vss      | DuckDB and two extensions (A2-SR-15, A2-SR-16); process model: not found | One: SQL with SQL/PGQ `GRAPH_TABLE` (A2-SR-16)                                                       | DuckDB transaction model: not found; vss filters through a transaction-visible bitmap (A2-SR-15) | Deleted rows are marked in the index and need compaction (A2-SR-15)                           | The whole index is written at each checkpoint; persistence is experimental (A2-SR-15)               | DuckDB: 20 (A2-SR-15); DuckPGQ: 12 registry updates from 2025-02-05 to 2026-10-14 (A2-SR-16)                                                     | vss experimental (A2-SR-15); DuckPGQ a research project with one main contributor (A2-SR-16)                                                                          |
| Neo4j beside Qdrant              | Two servers and a joining library (A2-SR-18)                             | Two: Cypher and the Qdrant API (A2-SR-17, A2-SR-18)                                                  | Two; a Qdrant write is eventually consistent unless the client waits (A2-SR-17)                  | Node identifier copied into the vector payload; the record shows no sync mechanism (A2-SR-18) | Not found                                                                                           | Qdrant: 34, latest v1.20.2 of 2026-11-16 (A2-SR-17)                                                                                              | Qdrant under Apache-2.0, repository active (A2-SR-17)                                                                                                                 |

The records state the licence names. Whether BSL 1.1 and SSPL count as open source is not assessed in any record (A2-SR-12, A2-SR-14).

### 4.1 One query with a graph pattern and a similarity search

No record, for any store, documents a query that starts from a similarity search and then traverses edges. The paragraphs below state what each store's records do show.

**PostgreSQL with AGE and pgvector.** A regression test, not a manual page, is the only source (A2-SR-05). Its Cypher query matches two node patterns with no edge between them and orders the result by a pgvector distance. An HNSW index on the label table serves it when the index expression matches the cast in the query (A2-SR-05). No record shows a query that starts from a similarity search and then traverses (A2-SR-05). Risks: no AGE manual page covers pgvector, and a committer confirms that none exists (A2-SR-05). The vector passes through a cast from AGE's type through text (A2-SR-05). pgvector applies filters after the approximate scan unless iterative scans are on (A2-SR-01). Releases 0.8.3 and 0.8.4 fixed HNSW vacuum faults (A2-SR-02). AGE's chair reported low organic activity and a release gap of more than 12 months (A2-SR-06).

**PostgreSQL with SQL/PGQ.** No released version exists, so no query is possible (A2-SR-07). Risk: no source gives a date for a new attempt (A2-SR-07).

**Neo4j.** One statement binds nodes with `MATCH` and searches with `SEARCH`. The documented example binds one movie by its title and then searches, with no hop (A2-SR-08, A2-SR-09). The pattern around `SEARCH` allows one bound variable and at most one hop; further traversal needs a following clause (A2-SR-09). No record shows a statement that searches first and then follows edges (A2-SR-08, A2-SR-09). Filters inside `SEARCH` run in the index, and only AND joins predicates (A2-SR-09). Risks: the index does not see changes of the same transaction, and no page states when the index catches up (A2-SR-08). Native VECTOR properties need block format, which only Enterprise Edition and Aura offer (A2-SR-08).

**Memgraph.** The search runs as a procedure call (A2-SR-11). No documented example combines it with a graph pattern (A2-SR-11). Risks: the vector index reads uncommitted data (A2-SR-11). Deleting vertices does not free the index memory (A2-SR-11).

**FalkorDB.** The search runs as a procedure call, `db.idx.vector.queryNodes` for nodes (A2-SR-13). The record holds no query that combines the procedure with a graph pattern (A2-SR-13). Risks: vector queries have no filter support (A2-SR-13). A plain list is stored without error but never found by the index (A2-SR-13). The engine was replaced in September 2026, and 4.x and 6.0 must not share a replica set (A2-SR-14).

**DuckDB with DuckPGQ and vss.** No source shows DuckPGQ and vss in one query (A2-SR-15, A2-SR-16). Risks: the documentation advises against persistent HNSW indexes in production (A2-SR-15). The index must fit in memory (A2-SR-15). One person makes most DuckPGQ commits (A2-SR-16).

**Neo4j beside Qdrant.** A query runs in two steps: a vector search in Qdrant, then a lookup of the node by its copied identifier (A2-SR-18). Risks: the two stores have separate write paths, and no record shows a way to commit both together (A2-SR-17). The record shows no mechanism that keeps the identifiers in sync when nodes change (A2-SR-18).

## 5. From similarity to edge

The settled design lets embeddings propose candidate relations, and an edge enters the graph only after a check or a person confirms it ([design-position.md](../knowledge-graph-with-provenance/design-position.md), context only). One recorded architecture does the opposite: HippoRAG adds a synonymy edge whenever two node vectors pass a cosine threshold (A1-SR-05).

**Paraphrase.** Similarity finds graded meaning similarity that correlates with human STS scores (A3-SR-02, A3-SR-03, A3-SR-06). It misses negation and word order: the STS systems of 2017 scored a sentence and its negation as nearly equivalent (A3-SR-02). Bi-encoders rank negated documents at or below random (A3-SR-10). Check: a cross-encoder handles negation best among the tested models, but the record notes that a large gap to human performance remains (A3-SR-10).

**Claim matching.** A cosine threshold of 0.71 reaches an F1 of 0.90 on English pairs (A3-SR-14). Lower-resource languages score F1 between 0.17 and 0.61, and claim matching does not always mean the same meaning (A3-SR-14). Domain shift lowers dense retrieval (A3-SR-07). Check: a cross-encoder generalises better across domains (A3-SR-07). An NLI model scores entailment from premise to hypothesis and beats an embedding-based metric on factual consistency (A3-SR-13). No record tests NLI as a filter on vector candidates.

**Text reuse.** Containment measures how much of one text lies in another, and substring matching finds partial copies (A3-SR-15, A3-SR-18). Broder calls his approach syntactic (A3-SR-15). No record measures reuse with rewording. Check: an exact substring match (A3-SR-18).

**Near-duplicate.** MinHash and SimHash find documents with high n-gram overlap at web scale (A3-SR-15 to A3-SR-18). SimHash reached precision and recall near 0.75 on a sample (A3-SR-17). SemDeDup targets pairs that are semantically similar but not exactly identical (A3-SR-19). No record measures how many such pairs the hashes miss. Check: a hash stage followed by an exact Jaccard and edit-similarity test (A3-SR-18).

**Same idea.** Embedding clusters with a cosine threshold remove semantic duplicates (A3-SR-19). The threshold slides from duplicate to related (A3-SR-19). Cosine is symmetric and cannot express the direction of entailment (A3-SR-11). Long texts cluster together (A3-SR-12). Check: an NLI model gives direction, but it degrades above 200 tokens (A3-SR-13). SemDeDup reports no precision against human labels (A3-SR-19).

**Cost of the checks.** A cross-encoder needs about 65 hours for all pairs of 10,000 sentences (A3-SR-03). So BEIR runs it on BM25 candidates (A3-SR-07). The near-duplicate pipeline also uses a cheap first stage, MinHash, before its exact check (A3-SR-18).

**Versioning and recomputing vectors.** An updated model is not guaranteed to produce vectors compatible with the old ones, though they can be moderately compatible by chance. The options are to keep one model for the life of the index or to re-encode the whole collection (A3-SR-20). One provider states that an upgrade between its two current models requires re-embedding all data (A3-SR-21). The only recorded strategy that avoids re-encoding addresses continued fine-tuning of one model (A3-SR-20). No record describes storing the model version with each vector (A3-SR-20, A3-SR-21). The pgvector, Neo4j, and Memgraph documentation names no feature that recomputes a vector when its text changes (A2-SR-01, A2-SR-08, A2-SR-11). The same record states that re-encoding and re-indexing all documents can be costly (A3-SR-20).

## 6. What this means for the knowledge system

This section is interpretation. Each point names the findings it rests on.

**Fewest moving parts for the settled design.** The settled design keeps provenance, knowledge, and decisions in one store. Read against section 4, four designs hold the graph and the vectors in one server: PostgreSQL with AGE and pgvector, Neo4j, Memgraph, and FalkorDB (A2-SR-14). Memgraph's vector index reads uncommitted data, so its single store does not give one consistency boundary (A2-SR-11). Neo4j has one server, one query language, and one transaction, the fewest parts among the designs with one boundary (A2-SR-08, A2-SR-09). AGE with pgvector has one server and one transaction but two languages and two extensions (A2-SR-04, A2-SR-05). It also keeps relational tables beside the graph in one storage, which may suit provenance rows (A2-SR-04). FalkorDB adds a module and a RediSearch fork to its Redis server, and DuckDB adds parts or carries experimental status (A2-SR-13 to A2-SR-16). The separate-store design has two boundaries by construction (A2-SR-17, A2-SR-18).

**Deletion and update across graph and vectors.** No architecture record describes how a changed or deleted document reaches both the graph and the vectors (A1-SR-02, A1-SR-04, A1-SR-08). The pgvector, Neo4j, and Memgraph documentation names no feature that recomputes a vector when its text changes (A2-SR-01, A2-SR-08, A2-SR-11). So the knowledge system has to own that step in every design. In a single transaction, the text, its vector, and its edges can change together, if the application computes the vector before the commit (A2-SR-04, A2-SR-01). Neo4j's index does not see changes of the same transaction, so a check inside that transaction cannot search the new vector (A2-SR-08). The separate-store design needs a second write and an identifier copy with no joint commit (A2-SR-17, A2-SR-18). Inside the index, deletes leave marks or unreachable points until compaction or repair (A2-SR-15, A4-SR-06, A4-SR-07). A model change can require re-encoding every vector (A3-SR-20, A3-SR-21). So each vector should carry its model version, a practice no record describes.

**Candidate edges need a check.** Similarity misses negation and direction (A3-SR-10, A3-SR-11), and a threshold slides from duplicate to related (A3-SR-19). That supports the settled rule that an edge enters only after a check. HippoRAG shows the risk of the opposite rule (A1-SR-05). A cross-encoder or NLI stage is the check the records offer (A3-SR-07, A3-SR-13). No record tests it on claim or idea candidates.

**Where the store choice is still open.** No record, for any store, shows a query that starts from a similarity search and then traverses edges (A2-SR-05, A2-SR-09). One test per store would settle that question, as section 7 lists. Three further questions remain.

- PostgreSQL with AGE and pgvector rests on a project with recorded health problems (A2-SR-06) and on undocumented interop (A2-SR-05). A count of active AGE contributors and a test of a traversal that starts from a similarity search would settle it.
- For Neo4j, the timing of index updates at commit is not documented (A2-SR-08). A test of read-after-commit search would settle it. The licence of Enterprise Edition is also not recorded (A2-SR-10).
- For SQL/PGQ, the next PostgreSQL attempt would remove AGE from the PostgreSQL design (A2-SR-07). A commit that survives into a released version would settle it.

## 7. Structured block

```json
{
  "findings": [
    {
      "title": "Graph-based retrieval designs mostly embed text, not graph structure",
      "summary": "The graph-based RAG designs read here embed chunks, passages, phrases, or short keys, and use the graph for expansion, communities, or a PageRank walk; GraphRAG answers global questions with no vector step. A survey names GRAG, which embeds k-hop ego networks, and one design that reranks paths with a knowledge graph embedding score.",
      "source_record_refs": ["A1-SR-02", "A1-SR-03", "A1-SR-04", "A1-SR-05", "A1-SR-06", "A1-SR-07", "A1-SR-08"]
    },
    {
      "title": "Knowledge graph embeddings serve link prediction",
      "summary": "TransE, TransH, and RotatE learn vectors from triples alone for link prediction. KG-BERT scores triples from their text. Joining structure and text in one space is a named challenge.",
      "source_record_refs": ["A1-SR-11", "A1-SR-12", "A1-SR-13", "A1-SR-14", "A1-SR-15"]
    },
    {
      "title": "Evaluations from 2025 report graph-based RAG below vector RAG on factual tasks, or no consistent winner",
      "summary": "HippoRAG 2 reports structure-augmented designs below standard RAG on factual memory tasks. One benchmark finds complementary behaviors rather than a consistent winner; a second states that graph-based RAG frequently underperforms vanilla RAG and takes its accuracy figure from the first. Both benchmarks report higher construction cost, latency, storage, or prompt tokens. Extracted graphs of KG-GraphRAG hold about 65% of answer entities on two datasets.",
      "source_record_refs": ["A1-SR-06", "A1-SR-09", "A1-SR-10"]
    },
    {
      "title": "No architecture record describes deletion across graph and vectors",
      "summary": "RAG replaces its whole index; GraphRAG describes no update; LightRAG adds documents by set union and describes no deletion; a survey names dynamic update as open.",
      "source_record_refs": ["A1-SR-01", "A1-SR-02", "A1-SR-04", "A1-SR-08"]
    },
    {
      "title": "Five single-database designs and one separate-store design",
      "summary": "PostgreSQL with AGE and pgvector, Neo4j, Memgraph, FalkorDB, and DuckDB with DuckPGQ and vss keep graph and vectors in one database; a graph store beside Qdrant needs two servers and two write paths. PostgreSQL 19 ships without SQL/PGQ.",
      "source_record_refs": ["A2-SR-01", "A2-SR-04", "A2-SR-05", "A2-SR-07", "A2-SR-08", "A2-SR-11", "A2-SR-13", "A2-SR-14", "A2-SR-15", "A2-SR-16", "A2-SR-17", "A2-SR-18"]
    },
    {
      "title": "Consistency boundaries differ between the store designs",
      "summary": "AGE with pgvector runs in one PostgreSQL transaction; Neo4j's vector index does not see changes of the same transaction; Memgraph's vector index reads uncommitted data; FalkorDB makes one query atomic; a Qdrant write is eventually consistent unless the client waits.",
      "source_record_refs": ["A2-SR-04", "A2-SR-01", "A2-SR-08", "A2-SR-11", "A2-SR-13", "A2-SR-17"]
    },
    {
      "title": "One query that matches a graph pattern and searches by vector distance is documented for AGE with pgvector and for Neo4j; no record shows a similarity search followed by a traversal",
      "summary": "An AGE regression test, the only source, runs one Cypher query that matches two node patterns with no edge and orders by a pgvector distance, served by an HNSW index whose expression matches the cast. Neo4j binds a node with MATCH and then runs SEARCH in one statement; the documented example has no hop, the pattern around SEARCH allows at most one hop, and further traversal needs a following clause. No record documents a query that starts from a similarity search and then traverses edges. Memgraph and FalkorDB document no combination with a graph pattern; DuckDB shows no combined DuckPGQ and vss query; the separate-store design runs two steps.",
      "source_record_refs": ["A2-SR-05", "A2-SR-09", "A2-SR-11", "A2-SR-13", "A2-SR-15", "A2-SR-16", "A2-SR-18"]
    },
    {
      "title": "Project health and maturity risks per store",
      "summary": "AGE had no release for about 18 months and missing board reports in 2026; FalkorDB replaced its engine in September 2026; vss is experimental and DuckPGQ has one main contributor; Memgraph is under BSL 1.1 and FalkorDB under SSPL.",
      "source_record_refs": ["A2-SR-06", "A2-SR-12", "A2-SR-14", "A2-SR-15", "A2-SR-16"]
    },
    {
      "title": "The pgvector, Neo4j, Memgraph, and FalkorDB documentation names no feature that recomputes a vector when its source text changes",
      "summary": "The pgvector, Neo4j, Memgraph, and FalkorDB documentation name no such feature; Memgraph's embeddings module runs only when a query calls it.",
      "source_record_refs": ["A2-SR-01", "A2-SR-08", "A2-SR-11", "A2-SR-13"]
    },
    {
      "title": "Similarity misses negation, entailment direction, domain shift, and length",
      "summary": "STS systems of 2017 and bi-encoders treat negated pairs as near equivalent; cosine is symmetric; dense retrievers underperform on datasets with a large domain shift; long texts cluster together; claim matching thresholds fail in lower-resource languages.",
      "source_record_refs": ["A3-SR-02", "A3-SR-07", "A3-SR-10", "A3-SR-11", "A3-SR-12", "A3-SR-14"]
    },
    {
      "title": "Second-stage checks for similarity candidates",
      "summary": "Cross-encoders generalise better across domains and handle negation best among tested models but cost about 65 hours for all pairs of 10,000 sentences; NLI models score directed entailment and degrade above 200 tokens; near-duplicate pipelines follow hashes with an exact Jaccard and edit-similarity check. No record tests NLI on vector candidates.",
      "source_record_refs": ["A3-SR-03", "A3-SR-07", "A3-SR-10", "A3-SR-13", "A3-SR-18"]
    },
    {
      "title": "A model change can mean re-encoding every vector",
      "summary": "An updated model is not guaranteed to produce compatible vectors, though they can be moderately compatible by chance; the options are one model for the life of the index or a full re-encode; the only recorded strategy that avoids re-encoding addresses continued fine-tuning of one model. One provider states that its upgrade requires re-embedding all data.",
      "source_record_refs": ["A3-SR-20", "A3-SR-21"]
    },
    {
      "title": "Filtered vector search has no single best method",
      "summary": "Pre-filtering, post-filtering, and per-label indexes each fail in a recorded case; Filtered-DiskANN builds labels into the graph edges, while ACORN applies the predicate at search time by traversing the subgraph it induces; an independent benchmark finds no universally best method.",
      "source_record_refs": ["A4-SR-09", "A4-SR-10", "A4-SR-11", "A4-SR-12"]
    },
    {
      "title": "Keeping a graph index current costs rebuilds or repair",
      "summary": "Periodic rebuilds are expensive; simple graph update rules lose recall and delete marks leave unreachable points; FreshDiskANN consolidates in batches and IP-DiskANN updates in place; IVF and PQ degrade under distribution shift.",
      "source_record_refs": ["A4-SR-06", "A4-SR-07", "A4-SR-08", "A4-SR-18"]
    },
    {
      "title": "Eleven concepts meet the entry rule for a hardened concept",
      "summary": "concept-history-check ranks eleven histories that have at least three formulations and two recorded criticisms; three further histories fall below the rule.",
      "source_record_refs": ["A1-SR-11", "A1-SR-05", "A4-SR-09", "A4-SR-06", "A4-SR-01", "A4-SR-04", "A4-SR-13", "A2-SR-03", "A1-SR-01", "A3-SR-02", "A3-SR-01"]
    }
  ],
  "uncertainties": [
    "The project health of Apache AGE rests on the chair's board reports, which are judgements, not counts of active contributors (A2-SR-06).",
    "The AGE and pgvector interop rests on a regression test with four-dimensional vectors and no manual page (A2-SR-05).",
    "Whether Neo4j and FalkorDB update the vector index at commit is not stated by any record (A2-SR-08, A2-SR-13).",
    "Two graph-based RAG evaluations re-implement the systems they compare (A1-SR-06, A1-SR-09). Only A1-SR-06 comes from authors of a competing design, HippoRAG 2. A1-SR-10 takes the accuracy figures of its introduction from other studies (A1-SR-10).",
    "The IP-DiskANN and FreshDiskANN results come from one research group without independent replication (A4-SR-06, A4-SR-08).",
    "The claim matching threshold of 0.71 is fitted on data from one fact-checking context (A3-SR-14)."
  ],
  "evidence_gaps": [
    "No record describes how a changed or deleted source document propagates to both graph and vectors.",
    "No record tests an NLI or cross-encoder check on vector candidates for claim matching or same-idea detection.",
    "No record describes storing the embedding model version with each vector.",
    "No record measures embedding similarity for reworded text reuse.",
    "DuckDB's transaction model, a combined DuckPGQ and vss query, and a Memgraph or FalkorDB query that combines vector search with a traversal were not found.",
    "Milvus and Weaviate were not read; Qdrant is the only separate vector store recorded.",
    "The licence of Neo4j Enterprise Edition and the maintainer counts of Neo4j, Memgraph, and pgvector were not recorded.",
    "No source gives a date for a new SQL/PGQ attempt in PostgreSQL.",
    "No general embedding model after SimCSE, such as E5, is recorded."
  ],
  "limitations": [
    "Vendor documentation is used for stated features and syntax only, never for performance or adoption.",
    "Several unreachable sources leave steps without their own record: Arora and others 2017, the NSW papers, the original 1998 LSH paper, Ruffinelli and others 2020, and the Jigsaw-LightRAG preprint.",
    "Some records rest on the abstract and introduction only, among them A3-SR-05, A3-SR-12, A4-SR-07, A4-SR-08, A4-SR-12, A4-SR-14, A4-SR-15, and A4-SR-17.",
    "Some history steps rest on a later paper's summary: the k-nearest-neighbour graph and NSW through A4-SR-04, TransR, DistMult, and ComplEx through A1-SR-13, and the STS tasks of 2012 to 2016 through A3-SR-02. The check counts A4-SR-04 and A3-SR-02 as primary.",
    "The history dates of two pgvector steps are the retrieval date of the changelog record, not the release dates.",
    "Store facts reflect documentation and release state on 2026-11-18."
  ],
  "candidates_for_deeper_falsification_study": [
    "PostgreSQL with AGE and pgvector: one transaction that changes a text node, its vector, and its edges leaves no state where a Cypher similarity query sees the new text with the old vector. Refuted if any concurrent read observes that mixed state.",
    "PostgreSQL with AGE and pgvector: one Cypher query that starts from a pgvector similarity search over one vertex label, keeps the top k vertices, and then follows edges two hops runs, and its plan uses the HNSW index. Refuted if the query is rejected, or if its plan falls back to a sequential scan for every supported cast.",
    "PostgreSQL with SQL/PGQ: in a released PostgreSQL version that holds SQL/PGQ, one SQL statement takes the top k vertices by pgvector distance and then follows edges two hops with GRAPH_TABLE. Precondition: such a version exists; PostgreSQL 19 does not hold SQL/PGQ. Refuted if the statement is rejected.",
    "Neo4j: a vector written and committed in one transaction is returned by SEARCH in the next transaction. Refuted if a committed vector is missing from SEARCH results for any measurable time.",
    "Memgraph: a similarity search never returns a vector from a transaction that later rolls back, under the documented READ_UNCOMMITTED vector index. Refuted if a rolled-back vector appears in any result.",
    "FalkorDB: one write query that creates a node with a vecf32 vector makes the node findable by the vector index once the query returns. Refuted if the node is missing from vector results after a successful write.",
    "DuckDB with DuckPGQ and vss: one SQL statement combines a GRAPH_TABLE traversal with an HNSW-served similarity ranking on a persistent database. Refuted if the statement fails or the index is not used.",
    "Neo4j beside Qdrant: a node deletion in Neo4j followed by a Qdrant delete leaves no window in which a vector search returns the identifier of a deleted node. Refuted if any search in that window returns it.",
    "Neo4j: one Cypher statement that runs SEARCH on a vector index and then follows two relationship hops from each result in a following MATCH clause returns the same nodes as the search and the traversal run as two separate statements. Refuted if the statement is rejected or the two results differ.",
    "Memgraph: one query that calls vector_search.search, yields the found nodes, and then matches a two-hop pattern from them returns the same nodes as the two steps run separately. Refuted if the query is rejected or the two results differ.",
    "FalkorDB: one query that calls db.idx.vector.queryNodes, yields the found nodes, and then matches a two-hop pattern from them returns the same nodes as the two steps run separately. Refuted if the query is rejected or the two results differ.",
    "DuckDB with DuckPGQ and vss: one SQL statement that takes the top k rows by an HNSW-served distance and then follows edges two hops with GRAPH_TABLE runs, and its plan uses the HNSW index. Refuted if the statement fails or the plan does not use the index.",
    "Neo4j beside Qdrant: a Qdrant similarity search followed by a two-hop Neo4j traversal from the copied node identifiers starts only from nodes that exist in Neo4j at query time: the Qdrant search returns no identifier of a node that no longer exists in Neo4j. Refuted if the Qdrant search returns an identifier that matches no Neo4j node.",
    "A cross-encoder or NLI check on cosine candidates rejects negated and reverse-entailment pairs that the cosine threshold accepts, on the system's own claim pairs. Refuted if the check accepts them at the same rate as the threshold."
  ]
}
```

## 8. Uncertainties, evidence gaps, and limitations

**Unreachable sources.** Several sources could not be read. Arora and others 2017 returned an HTML page instead of the PDF, so averaged word vectors have no record of their own. The NSW papers of 2012 to 2014 were not reached, so NSW is known only through the HNSW paper (A4-SR-04). The original 1998 LSH paper was not read; A4-SR-01 is the 2012 rewrite. The Jigsaw-LightRAG preprint on deletion returned "Access Denied". Ruffinelli and others 2020 also came back as HTML from OpenReview. The OpenAI page on embedding versions held only navigation. The PQ paper came from a third-party mirror (A4-SR-03).

**Abstract-only records.** Some records rest on the abstract and the introduction only. They are A3-SR-05, A3-SR-12, A4-SR-07, A4-SR-08, A4-SR-12, A4-SR-14, A4-SR-15 (abstract and conclusion), and A4-SR-17. Their findings may be narrower or wider in the full text.

**Secondary steps.** Some history steps rest on a later paper's summary. The k-nearest-neighbour graph and NSW come through A4-SR-04. TransR, DistMult, and ComplEx come through A1-SR-13. The STS tasks of 2012 to 2016 come through A3-SR-02. The check reads the first word of each record's `source_family`, so it counts A4-SR-04 and A3-SR-02 as primary for these steps.

**Quotes checked by eye only.** Several records took quotes from text extractions that scrambled columns or broke lines. The researchers checked these by eye against a crop or a layout extraction: A1-SR-15, A3-SR-01, A4-SR-02 (OCR scan), A4-SR-18, and A2-SR-07 (an archive page that dropped line breaks). `concept-history-check` checks that each history quote matches its record. It does not check the record against the source.

**Dates.** Many records date a living page by its retrieval date, 2026-11-18. So two pgvector history steps carry that date instead of their release dates (section 3.8). Several paper records set the day to the first of the month.

**Scope and freshness.** Store facts reflect the documentation and release state on 2026-11-18. Qdrant is the only separate vector store read. Vendor documentation is used only for stated features and syntax. No record was produced by installing or running a store.
