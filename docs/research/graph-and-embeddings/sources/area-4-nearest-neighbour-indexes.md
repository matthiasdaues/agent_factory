# Area 4: Nearest-Neighbour Indexes and Hybrid Queries

This index covers assignment A4 of the survey. It lists 18 source records in `sources/area-4/`. Each record marks its source as primary or secondary and states what the source shows and what it does not show. The index reports what the sources document and forms no claims.

## Records

| ID       | Source                                                                 | Year | Family    |
| -------- | ---------------------------------------------------------------------- | ---- | --------- |
| A4-SR-01 | Har-Peled, Indyk, Motwani: locality-sensitive hashing, journal version | 2012 | Primary   |
| A4-SR-02 | Weber, Schek, Blott: similarity search in high-dimensional spaces      | 1998 | Primary   |
| A4-SR-03 | Jégou, Douze, Schmid: product quantization and IVFADC                  | 2011 | Primary   |
| A4-SR-04 | Malkov, Yashunin: HNSW                                                 | 2016 | Primary   |
| A4-SR-05 | Subramanya et al.: DiskANN and Vamana                                  | 2019 | Primary   |
| A4-SR-06 | Singh et al.: FreshDiskANN                                             | 2021 | Primary   |
| A4-SR-07 | Xiao et al.: unreachable points in HNSW under updates                  | 2024 | Primary   |
| A4-SR-08 | Xu et al.: IP-DiskANN, in-place updates                                | 2025 | Primary   |
| A4-SR-09 | Wei et al.: AnalyticDB-V hybrid query plans                            | 2020 | Primary   |
| A4-SR-10 | Gollapudi et al.: Filtered-DiskANN                                     | 2023 | Primary   |
| A4-SR-11 | Patel et al.: ACORN                                                    | 2024 | Primary   |
| A4-SR-12 | Iff et al.: benchmark of filtered search methods                       | 2025 | Primary   |
| A4-SR-13 | Aumüller, Bernhardsson, Faithfull: ANN-Benchmarks                      | 2018 | Primary   |
| A4-SR-14 | Aumüller, Ceccarello: local intrinsic dimensionality in benchmarks     | 2019 | Primary   |
| A4-SR-15 | Simhadri et al.: NeurIPS 2021 billion-scale challenge                  | 2022 | Primary   |
| A4-SR-16 | Simhadri et al.: Big ANN NeurIPS 2023                                  | 2024 | Primary   |
| A4-SR-17 | Wang et al.: survey and comparison of graph-based indexes              | 2021 | Secondary |
| A4-SR-18 | Douze et al.: the Faiss library                                        | 2024 | Primary   |

Several records come from one research group at Microsoft: A4-SR-05, A4-SR-06, A4-SR-08, A4-SR-10, A4-SR-15, and A4-SR-16. They are not independent of each other. A4-SR-07, A4-SR-11, A4-SR-12, A4-SR-14, and A4-SR-17 come from other groups.

## State of the art

An approximate nearest-neighbour index trades exact answers for speed, because exact methods fail in high dimensions. Tree-based and partitioning indexes lose to a plain sequential scan above about ten dimensions (A4-SR-02). Locality-sensitive hashing (LSH) gave query times sub-linear in the dataset size, with space polynomial in size and dimension (A4-SR-01).

Product quantization stores each vector as a short code. An inverted file then limits the search to the lists of the nearest coarse centroids. This combination is called IVFADC (A4-SR-03). It answered two criticisms of LSH: high memory use and weaker quality on real data (A4-SR-03).

Graph-based indexes became the leading family by 2021 (A4-SR-17). HNSW builds a layered proximity graph and searches it greedily from the top layer (A4-SR-04). DiskANN moves a graph index to an SSD, so a billion vectors fit on one machine (A4-SR-05). The DiskANN authors report that compressed inverted-file indexes reach a 1-recall@1 of only about 0.5 at that scale (A4-SR-05).

A hybrid query combines a vector search with a structured predicate, such as a price range or a label. Three plain methods exist (A4-SR-09, A4-SR-10, A4-SR-11, A4-SR-18):

- Pre-filtering applies the predicate first and then compares the query with the remaining vectors by brute force.
- Post-filtering searches the vector index first and then drops results that fail the predicate.
- A per-label index builds one index for each filter value.

The sources criticise each method. Pre-filtering is slow when many records pass. Post-filtering must widen its search when few records pass. Per-label indexes grow too expensive when there are many labels (A4-SR-10, A4-SR-11). Two responses build the predicate into the graph: Filtered-DiskANN uses labels at build time (A4-SR-10), and ACORN changes the traversal for any predicate (A4-SR-11). An independent 2025 benchmark finds no single best method (A4-SR-12).

An index must also stay current as vectors are inserted, updated, and deleted. The common practice was a periodic full rebuild. The FreshDiskANN authors estimate that rebuild at 1.5 to 2 hours on 48 cores for 100 million points in HNSW (A4-SR-06). Simple delete rules make graph indexes lose recall over time (A4-SR-06, A4-SR-07). Indexes trained on the data distribution, such as IVF and PQ, lose efficiency when that distribution shifts (A4-SR-18).

Benchmarks moved from in-memory, single-thread, million-scale tests (A4-SR-13) to billion-scale tests that count hardware cost (A4-SR-15). In 2023 they added filtered search, streaming updates, and out-of-distribution queries (A4-SR-16).

## Hardened concepts

The area holds four concepts with a recorded sequence of formulations and criticism. Each step names the formulation, its date, the criticism that led to the next step, and the records.

### 1. The approximate nearest-neighbour index lineage

1. **Tree-based and partitioning indexes for exact search** (before 1998). Criticism: above about ten dimensions they are outperformed on average by a sequential scan (1998, A4-SR-02; restated 2011, A4-SR-03). The tree papers themselves were not read.
2. **Locality-sensitive hashing** (STOC 1998, read in the 2012 journal version). It hashes points so that close points collide more often than distant ones (A4-SR-01). Criticism: on real data it loses to methods that exploit the data distribution, and its memory use can exceed that of the original vectors (2011, A4-SR-03).
3. **Product quantization with an inverted file (IVFADC)** (technical report 2009, journal 2011, A4-SR-03). It uses short codes and scans only the inverted lists near the query. Criticism: lossy compression gives low recall at billion scale (2019, A4-SR-05). Codebooks trained on the data degrade when the distribution shifts under updates (2024, A4-SR-18).
4. **Graph-based indexes** (from 2016, A4-SR-04). By 2021 graph indexes were the leading family (A4-SR-17). Concept 2 traces how this family changed.

### 2. The graph-based index

1. **k-nearest-neighbour graph** (before 2016). The source for this step is HNSW's own summary (A4-SR-04), which makes this record secondary for the step. Criticism: the number of routing steps grows by a power law with the dataset size, and the graph can lose global connectivity on clustered data (A4-SR-04).
2. **Navigable small world (NSW)** (2012 to 2014). It inserts points in random order and links each new point to its closest neighbours (described in A4-SR-04). The NSW papers were not read, so this step is a gap for a primary source. Criticism: polylogarithmic scaling leaves NSW prone to severe slowdowns on low-dimensional data (A4-SR-04).
3. **HNSW** (arXiv 2016, A4-SR-04). It adds layers with an exponentially decaying chance of membership and starts the search from the top layer, so the search scales logarithmically. Criticism from the authors themselves: no support for updates and removal, and no distributed search (A4-SR-04). Criticism from others: the index must sit in main memory, which limits dataset size (2019, A4-SR-05). Other surveyed graph indexes are criticised for index size (2021, A4-SR-17).
4. **DiskANN with the Vamana graph** (NeurIPS 2019, A4-SR-05). It serves a graph index from an SSD. Criticism: the index is static, and simple update rules degrade HNSW, NSG, and Vamana under update streams (2021, A4-SR-06).
5. **FreshDiskANN** (2021, A4-SR-06). Concept 4 continues this step for updates.

### 3. Filtered vector search

1. **Post-filtering and pre-filtering** (no single first source; described in 2020 to 2024 by A4-SR-09, A4-SR-10, A4-SR-11). Criticism: post-filtering performs poorly when the filter matches few points (2023, A4-SR-10) and must widen its search (2024, A4-SR-11). Pre-filtering with brute force works only when few points pass, and its time grows linearly with their number (2020, A4-SR-09; 2024, A4-SR-11). A source that first named these two methods was not found; this is a gap.
2. **Cost-based choice between plans** (2020, A4-SR-09). A query optimiser picks brute force after the filter, a scan of compressed codes through a filter bitmap, or other plans, by estimated cost and accuracy. A similar rule picks vector-first or metadata-first by estimated subset size (2023 to 2024, A4-SR-16, A4-SR-18). Criticism: indexes that ignore the labels at build time still give high latency or low recall for filtered queries (2023, A4-SR-10).
3. **Label-aware graph indexes: Filtered-DiskANN** (WWW 2023, A4-SR-10). Graph edges depend on both vector geometry and label sets. Criticism: the label set is limited to about 1,000 values and to equality predicates (2024, A4-SR-11). It fails on a large dataset of transformer embeddings (2025, A4-SR-12).
4. **Predicate-agnostic traversal: ACORN** (2024, A4-SR-11). It extends HNSW and traverses the subgraph that the predicate induces. Criticism: an independent benchmark finds it reliable across scales but often outperformed by more specialised methods. The same benchmark finds no universally best method and too few realistic datasets (2025, A4-SR-12). No later formulation that answers this criticism was found.

### 4. Keeping an index current under updates

1. **Periodic full rebuild** (industry practice, stated in 2021 by A4-SR-06). Criticism: it is very expensive, about 1.5 to 2 hours on 48 cores for 100 million points in HNSW, by the authors' estimate (A4-SR-06). No primary source for the practice itself was read; this is a gap.
2. **Simple in-graph update rules and delete marks** (HNSW and NSG implementations, before 2021). Criticism: recall drops over cycles of deletes and re-inserts because the graph becomes sparse (2021, A4-SR-06). Delete marks and replaced updates in HNSW leave points that no search reaches (2024, A4-SR-07). For IVF and PQ, distribution shift lowers efficiency (A4-SR-18).
3. **Lazy deletion with batch consolidation: FreshDiskANN** (2021, A4-SR-06). Deleted points go to a delete list and stay usable for navigation until a later batch repair. Criticism: the batch consolidation exists only because a directed graph has no fast way to find the in-neighbours of a deleted vertex (2025, A4-SR-08).
4. **In-place updates: IP-DiskANN** (2025, A4-SR-08). It processes each insert and delete in place. No independent criticism or replication was found; it comes from the same group as step 3.

### Benchmark lineage

The benchmarks show a shorter sequence:

- ANN-Benchmarks measures in-memory indexes in a single thread on datasets of millions of points (2018, A4-SR-13).
- Its own co-author showed that common real-world datasets are not diverse (2019, A4-SR-14).
- The 2021 challenge criticised the focus on million-point evaluations and moved to billion scale with hardware cost (A4-SR-15).
- The 2023 challenge added filtered, streaming, sparse, and out-of-distribution tracks (A4-SR-16).
- The 2025 filtered benchmark still found too few realistic filtered datasets (A4-SR-12).

The read passages of A4-SR-15 cite ANN-Benchmarks but not A4-SR-14, so the link between those two criticisms is not documented.

## Gaps

- **Indyk and Motwani, STOC 1998.** The original paper was not read. A4-SR-01 is the authors' 2012 journal rewrite, so the 1998 wording is not recorded.
- **NSW, 2012 to 2014.** The Information Systems paper by Malkov, Ponomarenko, Logvinov, and Krylov was not reached. The HSE mirror found by search returned no file to curl. NSW is recorded only through A4-SR-04.
- **Tree-based indexes.** The KD-tree, R-tree, and cover tree papers were not read. Their criticism is recorded (A4-SR-02, A4-SR-03), but the formulations are not.
- **Inverted file origin.** Sivic and Zisserman, Video Google (2003), was not read. It is cited by A4-SR-03.
- **Product quantization, HAL copy.** The HAL server answered with a bot check, so A4-SR-03 came from a third-party mirror of the HAL postprint.
- **NSG and other graph indexes.** The NSG paper was not read. It appears only in A4-SR-06, A4-SR-17, and A4-SR-18.
- **First source for pre-filtering and post-filtering.** No paper that first formulated these terms was found.
- **Second filtered benchmark.** Shi et al., arXiv:2509.07789 (2025), was found by search but not read.
- **IVF-family updates.** No paper on updating IVF or quantization indexes, such as SPFresh, was read. Only the general statement in A4-SR-18 is recorded.
- **Filtered search under updates.** No source covering both was found, apart from the separate filtered and streaming tracks in A4-SR-16.
- **Boundary with area 2.** Records A4-SR-09, A4-SR-10, A4-SR-11, and A4-SR-18 mention products such as Faiss, Milvus, Weaviate, Pinecone, and AnalyticDB-V. This index uses only their algorithm statements. Product facts stay with area 2.
